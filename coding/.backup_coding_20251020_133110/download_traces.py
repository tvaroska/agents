#!/usr/bin/env python3
"""
Download traces from GCP Cloud Trace for the last hour using the Trace API.
Convert traces to EvalSet format for agent evaluation.
"""

import json
from datetime import datetime, timedelta, timezone
from google.cloud import trace_v1
from typing import List, Dict, Any


def download_traces(project_id: str, output_file: str = "traces.json"):
    """
    Download traces from GCP Cloud Trace for the last hour.

    Args:
        project_id: GCP project ID
        output_file: Output file path for saving traces (default: traces.json)
    """
    # Create a client (v1 API supports listing traces)
    client = trace_v1.TraceServiceClient()

    # Calculate time range (last 1 hour)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    print(f"Fetching traces from {start_time.isoformat()} to {end_time.isoformat()}")
    print(f"Project: {project_id}")

    # Prepare the request
    project_path = f"projects/{project_id}"

    traces = []
    trace_count = 0

    try:
        # List traces using v1 API
        request = trace_v1.ListTracesRequest(
            project_id=project_id,
            start_time=start_time,
            end_time=end_time,
        )

        # Iterate through pages of results
        page_result = client.list_traces(request=request)

        for trace in page_result:
            trace_count += 1

            # Get the full trace with spans using get_trace
            full_trace = client.get_trace(
                project_id=project_id,
                trace_id=trace.trace_id
            )

            trace_dict = {
                "project_id": full_trace.project_id,
                "trace_id": full_trace.trace_id,
                "spans": []
            }

            # Get spans for this trace - capture ALL available data
            for span in full_trace.spans:
                span_dict = {
                    "span_id": str(span.span_id),
                    "name": span.name,
                    "parent_span_id": str(span.parent_span_id) if span.parent_span_id else None,
                    "start_time": span.start_time.isoformat() if span.start_time else None,
                    "end_time": span.end_time.isoformat() if span.end_time else None,
                    "kind": str(span.kind),
                }

                # Extract labels/attributes
                if span.labels:
                    span_dict["labels"] = dict(span.labels)
                else:
                    span_dict["labels"] = {}

                trace_dict["spans"].append(span_dict)

            traces.append(trace_dict)

            if trace_count % 10 == 0:
                print(f"Downloaded {trace_count} traces...")

        print(f"\nTotal traces downloaded: {trace_count}")

        # Save to file
        with open(output_file, 'w') as f:
            json.dump(traces, f, indent=2)

        print(f"Traces saved to {output_file}")

    except Exception as e:
        print(f"Error downloading traces: {e}")
        raise


def convert_traces_to_evalset(
    traces_file: str,
    output_file: str = "evalset.json",
    app_name: str = "agent",
    eval_set_id: str = None,
    eval_set_name: str = None,
    include_metadata: bool = False
):
    """
    Convert traces to EvalSet format for agent evaluation.

    Args:
        traces_file: Path to traces JSON file
        output_file: Output file path for EvalSet (default: evalset.json)
        app_name: Name of the agent being tested
        eval_set_id: ID for the eval set (default: generated from timestamp)
        eval_set_name: Name for the eval set (default: based on traces file)
        include_metadata: Include trace metadata in eval cases (default: False)
    """
    # Load traces
    with open(traces_file, 'r') as f:
        traces = json.load(f)

    # Generate defaults if not provided
    if eval_set_id is None:
        eval_set_id = f"evalset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if eval_set_name is None:
        eval_set_name = f"Eval Set from {traces_file}"

    eval_cases = []

    for trace in traces:
        trace_id = trace.get("trace_id", "unknown")
        spans = trace.get("spans", [])

        # Extract conversation from LLM call spans
        conversation = []

        # Find all call_llm spans in chronological order
        llm_spans = [s for s in spans if "call_llm" in s.get("name", "")]
        llm_spans.sort(key=lambda x: x.get("start_time", ""))

        # Track agent context
        agent_name = app_name

        for llm_span in llm_spans:
            labels = llm_span.get("labels", {})

            # Try to get agent name from parent span
            parent_id = llm_span.get("parent_span_id")
            if parent_id:
                parent_span = next((s for s in spans if s["span_id"] == parent_id), None)
                if parent_span:
                    parent_labels = parent_span.get("labels", {})
                    agent_name = parent_labels.get("gen_ai.agent.name", agent_name)

            # Extract LLM request and response from labels
            llm_request_str = labels.get("gcp.vertex.agent.llm_request", "")
            llm_response_str = labels.get("gcp.vertex.agent.llm_response", "")

            # Try to parse the JSON strings (they may be truncated)
            try:
                # Attempt to parse, handling potential truncation
                request_data = {}
                response_data = {}

                if llm_request_str:
                    try:
                        request_data = json.loads(llm_request_str)
                    except json.JSONDecodeError:
                        # Try to extract partial JSON
                        pass

                if llm_response_str:
                    try:
                        response_data = json.loads(llm_response_str)
                    except json.JSONDecodeError:
                        # Try to extract partial information from truncated JSON
                        # Look for function_call pattern
                        if '"function_call"' in llm_response_str:
                            import re
                            # Try to extract function name
                            name_match = re.search(r'"name":"([^"]+)"', llm_response_str)
                            if name_match:
                                response_data = {
                                    "content": {
                                        "parts": [{
                                            "function_call": {
                                                "name": name_match.group(1),
                                                "args": {} # Truncated
                                            }
                                        }]
                                    },
                                    "_truncated": True
                                }
                        # Look for text response pattern
                        elif '"text"' in llm_response_str:
                            import re
                            text_match = re.search(r'"text":"([^"]*)', llm_response_str)
                            if text_match:
                                response_data = {
                                    "content": {
                                        "parts": [{
                                            "text": text_match.group(1) + "... [truncated]"
                                        }]
                                    },
                                    "_truncated": True
                                }

                # Extract user content - use a synthetic message based on trace
                # Since actual user inputs may not be in the trace, we create a placeholder
                user_text = f"[Trace {trace_id[:8]}] Request to {agent_name}"

                # Try to extract system instruction as context
                if "system_instruction" in request_data:
                    system_inst = request_data.get("system_instruction", "")
                    if system_inst:
                        user_text = system_inst

                # Extract model response
                model_text = ""
                if "content" in response_data:
                    content = response_data["content"]
                    if "parts" in content:
                        parts = content["parts"]
                        if parts and isinstance(parts, list):
                            # Extract text from parts
                            for part in parts:
                                if "text" in part:
                                    model_text = part["text"]
                                    break
                                elif "function_call" in part:
                                    # For function calls, represent as text
                                    fc = part["function_call"]
                                    model_text = f"Function call: {fc.get('name', 'unknown')} with args {json.dumps(fc.get('args', {}))}"
                                    break

                # Also check finish reason and usage metadata
                finish_reason = response_data.get("finish_reason", "")
                usage = response_data.get("usage_metadata", {})
                is_truncated = response_data.get("_truncated", False)

                # Add metadata if requested
                metadata = {}
                if include_metadata:
                    metadata = {
                        "agent_name": agent_name,
                        "model": request_data.get("model", ""),
                        "finish_reason": finish_reason,
                        "usage": usage,
                        "span_id": llm_span.get("span_id"),
                        "start_time": llm_span.get("start_time"),
                        "end_time": llm_span.get("end_time"),
                        "truncated": is_truncated
                    }

                # Create conversation turn
                turn = {
                    "user_content": {
                        "parts": [{"text": user_text}]
                    },
                    "final_response": {
                        "parts": [{"text": model_text if model_text else f"[No text response - finish_reason: {finish_reason}]"}]
                    }
                }

                if include_metadata and metadata:
                    turn["metadata"] = metadata

                conversation.append(turn)

            except Exception as e:
                print(f"Warning: Error processing LLM span: {e}")
                continue

        # Only create eval case if we have conversation turns
        if conversation:
            eval_case = {
                "eval_id": f"trace_{trace_id}",
                "conversation": conversation,
                "session_input": {
                    "app_name": app_name
                }
            }

            if include_metadata:
                eval_case["trace_metadata"] = {
                    "trace_id": trace_id,
                    "project_id": trace.get("project_id"),
                    "total_spans": len(spans)
                }

            eval_cases.append(eval_case)

    # Create EvalSet structure
    evalset = {
        "eval_set_id": eval_set_id,
        "name": eval_set_name,
        "eval_cases": eval_cases
    }

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(evalset, f, indent=2)

    print(f"Converted {len(eval_cases)} traces to EvalSet format")
    print(f"Total conversation turns: {sum(len(ec['conversation']) for ec in eval_cases)}")
    print(f"EvalSet saved to {output_file}")

    return evalset


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download traces from GCP Cloud Trace and convert to EvalSet format"
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="GCP project ID"
    )
    parser.add_argument(
        "--output",
        default="evalset.json",
        help="Output file path for EvalSet (default: evalset.json)"
    )
    parser.add_argument(
        "--raw-output",
        help="Optional: Save raw traces to this file"
    )
    parser.add_argument(
        "--app-name",
        default="agent",
        help="Name of the agent being tested (default: agent)"
    )
    parser.add_argument(
        "--eval-set-id",
        help="ID for the eval set (default: auto-generated)"
    )
    parser.add_argument(
        "--eval-set-name",
        help="Name for the eval set (default: auto-generated)"
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include trace metadata in eval cases"
    )

    args = parser.parse_args()

    # Download traces to a temporary file or the specified raw output
    import tempfile
    import os

    if args.raw_output:
        # Save raw traces to specified file
        traces_file = args.raw_output
        download_traces(args.project_id, traces_file)
    else:
        # Use a temporary file for raw traces
        temp_fd, traces_file = tempfile.mkstemp(suffix='.json', prefix='traces_')
        os.close(temp_fd)
        try:
            download_traces(args.project_id, traces_file)
        except Exception as e:
            os.unlink(traces_file)
            raise

    # Convert traces to EvalSet
    try:
        convert_traces_to_evalset(
            traces_file=traces_file,
            output_file=args.output,
            app_name=args.app_name,
            eval_set_id=args.eval_set_id,
            eval_set_name=args.eval_set_name,
            include_metadata=args.include_metadata
        )
    finally:
        # Clean up temporary file if used
        if not args.raw_output and os.path.exists(traces_file):
            os.unlink(traces_file)
