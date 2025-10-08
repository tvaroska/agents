import {
  CopilotRuntime, // Main runtime that manages agent communication
  ExperimentalEmptyAdapter, // Service adapter for agent-only setups
  copilotRuntimeNextJSAppRouterEndpoint, // Next.js App Router endpoint handler
} from "@copilotkit/runtime";
// Import AG-UI client for connecting to ADK agents
import { HttpAgent } from "@ag-ui/client";
// Import Next.js types for request handling
import { NextRequest } from "next/server";

// Create a service adapter for the CopilotKit runtime
const serviceAdapter = new ExperimentalEmptyAdapter();

// Create the main CopilotRuntime instance that manages communication between the frontend and backend agents
const runtime = new CopilotRuntime({
  // Define the agents that will be available to the frontend
  // agents is a Record<string, AbstractAgent> where the key is the agent name
  agents: {
    // Agent name must match the name used in useCoAgent hook
    ProverbsAgent: new HttpAgent({
      // URL of your ADK agent backend (update this to match your backend URL)
      url: process.env.NEXT_PUBLIC_AGENT_URL || "http://localhost:8000",
    }),
  },
  // Enable agent lock mode to use EmptyAdapter
  delegateAgentProcessingToServiceAdapter: false,
});

// Export the POST handler for the Next.js App Router
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
