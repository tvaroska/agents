### `EvalSet` File Description

An `EvalSet` file is a JSON document that contains a collection of test cases, known as "eval cases." These are used to evaluate the performance of your agent. Each case represents a recorded conversation, including user inputs and the agent's corresponding responses.

The basic structure is as follows:

*   **Top-Level Object:**
    *   `eval_set_id`: A unique string to identify this entire set of tests.
    *   `name`: A human-readable name for the test set.
    *   `eval_cases`: An array `[]` containing one or more `eval_case` objects.

*   **`eval_case` Object (A single test conversation):**
    *   `eval_id`: A unique string to identify this specific test case.
    *   `conversation`: An array `[]` of turn-by-turn interactions between the user and the model.
    *   `session_input`: Contains metadata like the `app_name` being tested.

*   **`conversation` Turn Object (A single user message and model reply):**
    *   `user_content`: An object containing the user's input text.
    *   `final_response`: An object containing the expected or recorded response from the model.

### How to Create an `EvalSet` File

1.  **Create a new `.json` file.** For example, `my_agent_evals.json`.
2.  **Use the template below** and paste it into your new file.
3.  **Populate the `eval_cases`:** For each test scenario, create a new `eval_case` object.
4.  **Fill in the `conversation`:**
    *   For each turn in the conversation, add an object to the `conversation` array.
    *   In the `user_content` part, enter the text of the user's message.
    *   In the `final_response` part, enter the text of the desired model response for that user message. You can have multiple turns in a single conversation to test how the agent handles follow-up questions.

---

### `EvalSet` Template

You can use this template as a starting point. It includes one test case with a two-turn conversation.

```json
{
  "eval_set_id": "your_unique_eval_set_id",
  "name": "Name of Your Eval Set",
  "eval_cases": [
    {
      "eval_id": "your_first_case_id",
      "conversation": [
        {
          "user_content": {
            "parts": [
              {
                "text": "This is the first user message."
              }
            ]
          },
          "final_response": {
            "parts": [
              {
                "text": "This is the model's expected response to the first message."
              }
            ]
          }
        },
        {
          "user_content": {
            "parts": [
              {
                "text": "This is a follow-up user message."
              }
            ]
          },
          "final_response": {
            "parts": [
              {
                "text": "This is the model's expected response to the follow-up."
              }
            ]
          }
        }
      ],
      "session_input": {
        "app_name": "name_of_your_agent"
      }
    }
  ]
}
```
