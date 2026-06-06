import json

from app.tools.calculator import calculate
from app.tools.wikipedia import search_wikipedia


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Safely calculate a mathematical expression. "
                "Use this for arithmetic, percentages, multiplication, division, powers, and numeric calculations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to calculate. Example: '25 * 1840 / 100'",
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wikipedia_search",
            "description": (
                "Search Wikipedia for background context about a topic and return a short summary. "
                "Use this when the user asks about a person, concept, technology, historical event, "
                "organization, or general knowledge topic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The Wikipedia topic to search. "
                            "Example: 'Artificial intelligence', 'Alan Turing', or 'Python programming language'."
                        ),
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
]


def execute_tool(tool_name: str, tool_arguments: dict) -> dict:
    """
    Executes a tool by name and returns a standard tool result dictionary.

    This function catches tool-level errors so the whole API does not crash.
    """

    try:
        if tool_name == "calculator":
            expression = tool_arguments.get("expression")

            if not expression:
                raise ValueError("Missing required argument: expression")

            result = calculate(expression)

            return {
                "tool_used": "calculator",
                "tool_input": expression,
                "tool_output": str(result),
                "tool_error": None,
            }

        if tool_name == "wikipedia_search":
            query = tool_arguments.get("query")

            if not query:
                raise ValueError("Missing required argument: query")

            result = search_wikipedia(query)

            return {
                "tool_used": "wikipedia_search",
                "tool_input": query,
                "tool_output": json.dumps(result),
                "tool_error": None,
            }

        return {
            "tool_used": tool_name,
            "tool_input": json.dumps(tool_arguments),
            "tool_output": None,
            "tool_error": "The requested tool is not available.",
        }

    except Exception as error:
        return {
            "tool_used": tool_name,
            "tool_input": json.dumps(tool_arguments),
            "tool_output": None,
            "tool_error": str(error),
        }