import json

from openai import OpenAI

from app.core.config import settings
from app.tools.registry import TOOL_SCHEMAS, execute_tool


client = OpenAI(api_key=settings.openai_api_key)


def generate_response(user_message: str, chat_history: list[dict] | None = None) -> dict:
    """
    Sends the user message and optional chat history to the LLM.

    The LLM can answer directly or request a tool call.
    Tool schemas and execution are handled by app.tools.registry.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI agent. "
                "Answer clearly and professionally. "
                "When a user asks for a calculation, use the calculator tool. "
                "When a user asks about a general knowledge topic, person, technology, organization, "
                "or historical event, use the wikipedia_search tool to get context first. "
                "Use previous conversation history when it is relevant."
            ),
        }
    ]

    if chat_history:
        messages.extend(chat_history)

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    try:
        first_response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )

        assistant_message = first_response.choices[0].message

        if not assistant_message.tool_calls:
            return {
                "answer": assistant_message.content,
                "tool_used": None,
                "tool_input": None,
                "tool_output": None,
                "tool_error": None,
            }

        tool_call = assistant_message.tool_calls[0]
        tool_name = tool_call.function.name

        try:
            tool_arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            tool_arguments = {}

        tool_result = execute_tool(
            tool_name=tool_name,
            tool_arguments=tool_arguments,
        )

        if tool_result["tool_error"]:
            return {
                "answer": (
                    f"I tried to use the {tool_result['tool_used']} tool, "
                    f"but it failed: {tool_result['tool_error']}"
                ),
                "tool_used": tool_result["tool_used"],
                "tool_input": tool_result["tool_input"],
                "tool_output": tool_result["tool_output"],
                "tool_error": tool_result["tool_error"],
            }

        messages.append(assistant_message)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result["tool_output"],
            }
        )

        final_response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
        )

        final_answer = final_response.choices[0].message.content

        return {
            "answer": final_answer,
            "tool_used": tool_result["tool_used"],
            "tool_input": tool_result["tool_input"],
            "tool_output": tool_result["tool_output"],
            "tool_error": None,
        }

    except Exception as error:
        return {
            "answer": (
                "Sorry, something went wrong while generating the response. "
                "Please check the server logs or try again."
            ),
            "tool_used": None,
            "tool_input": None,
            "tool_output": None,
            "tool_error": str(error),
        }