from app.core.llm import generate_response


def run_agent(user_message: str, chat_history: list[dict] | None = None) -> dict:
    """
    Runs the AI agent.

    The agent sends the message and previous chat history to the LLM.
    The LLM can answer directly or call a tool.
    """

    result = generate_response(
        user_message=user_message,
        chat_history=chat_history,
    )

    return {
        "answer": result["answer"],
        "tool_used": result["tool_used"],
        "tool_input": result["tool_input"],
        "tool_output": result["tool_output"],
        "tool_error": result["tool_error"],
    }