# AI Agent Platform

AI Agent Platform is a FastAPI-based backend-focused AI engineering portfolio project with a simple frontend UI. It demonstrates OpenAI tool calling, session-based memory, SQLite logging, tool execution history, Docker, and uv-based dependency management.

Suggested repository description:

```text
AI Agent Platform built with FastAPI, OpenAI tool calling, session memory, SQLite logging, calculator and Wikipedia tools, frontend UI, uv, and Docker.
```

## Problem It Solves

Many AI demos only show a single prompt and response. This project shows the backend engineering needed for a practical AI agent service: structured API contracts, session continuity, tool execution, persistent logs, error capture, and a simple UI for testing real conversations locally.

## Main Features

- FastAPI backend
- OpenAI integration
- OpenAI tool calling
- Calculator tool
- Wikipedia search and summary tool
- Tool registry
- SQLite chat and tool-call logging
- Session-based chat history
- Automatic `session_id` generation
- Session list endpoint
- Single session history endpoint
- Error handling with `tool_error`
- Pydantic request and response schemas
- Simple frontend UI
- Dockerfile and Docker Compose
- uv for dependency management

## Tech Stack

- Python 3.12
- FastAPI
- OpenAI Python SDK
- SQLAlchemy
- SQLite
- Pydantic
- uv
- Docker and Docker Compose
- Plain HTML, CSS, and JavaScript

## Architecture Overview

The application is organized as a backend-first FastAPI service:

- `app/main.py` creates the FastAPI app, initializes database tables, includes API routes, and serves the static frontend.
- `app/api/chat.py` defines the chat, log, and session endpoints.
- `app/agents/agent.py` coordinates agent execution.
- `app/core/llm.py` communicates with OpenAI and handles tool-call decisions.
- `app/tools/registry.py` defines available tools and dispatches tool execution.
- `app/db/` contains SQLAlchemy database setup and chat log models.
- `app/schemas/` contains Pydantic API schemas.
- `app/static/` contains the local frontend UI.

## Agent Flow

1. A user sends a message to `POST /api/chat`.
2. If no `session_id` is provided, the API automatically creates one.
3. The backend loads recent messages from the same session.
4. The agent sends the user message and relevant history to the OpenAI model.
5. The model either answers directly or requests a tool call.
6. If a tool is requested, the backend executes it through the tool registry.
7. The tool result is sent back to the model so it can produce a final answer.
8. The user message, assistant answer, tool details, and error details are stored in SQLite.
9. The API returns the answer, `session_id`, and tool metadata.

## Tool Calling

Tool calling is handled through OpenAI function tools. The available tool schemas are registered in `app/tools/registry.py`. When the model decides a tool is useful, the backend parses the tool arguments, executes the matching local function, captures the result, and returns that result to the model for the final response.

Tool execution metadata is saved with each chat log:

- `tool_used`
- `tool_input`
- `tool_output`
- `tool_error`

This makes tool behavior visible through both the API and the frontend.

## Available Tools

### calculator

Safely evaluates arithmetic expressions such as multiplication, division, percentages, powers, and other numeric calculations.

Example use:

```text
What is 25 * 1840 / 100?
```

### wikipedia_search

Searches Wikipedia for a topic and returns a short summary. It is intended for general knowledge questions about people, concepts, technologies, organizations, and historical events.

Example use:

```text
Who was Alan Turing?
```

## Session Memory

The API supports session-based memory using `session_id`.

- If the client sends no `session_id`, the backend creates one automatically.
- If the client sends an existing `session_id`, the backend loads recent messages from that session.
- The agent receives relevant previous messages so it can answer with conversation context.
- Session summaries are available through `GET /api/sessions`.
- Full session history is available through `GET /api/sessions/{session_id}`.

## Logging and Observability

Each chat interaction is stored in SQLite with:

- user message
- assistant answer
- session ID
- tool used
- tool input
- tool output
- tool error
- timestamp

The `GET /api/logs` endpoint exposes stored chat logs for debugging, review, and observability.

## Frontend UI

The project includes a simple frontend built with plain HTML, CSS, and JavaScript. It works locally without React, Vue, Next.js, or another frontend framework.

The UI includes:

- left sidebar with previous sessions from `GET /api/sessions`
- main chat area for user and assistant messages
- message input connected to `POST /api/chat`
- automatic reuse of returned `session_id`
- session history loading from `GET /api/sessions/{session_id}`
- assistant tool metadata display when available

After running the server, open:

```text
http://localhost:8000/app/
```

or:

```text
http://localhost:8000/ui
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/chat` | Send a message to the AI agent. |
| `GET` | `/api/logs` | Return all stored chat logs. |
| `GET` | `/api/sessions` | Return session summaries ordered by recent activity. |
| `GET` | `/api/sessions/{session_id}` | Return full message history for one session. |

## Setup With uv

Install dependencies:

```bash
uv sync
```

Create an environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./agent_platform.db
```

Run the app:

```bash
uv run python run.py
```

Local URLs:

- API root: `http://localhost:8000/`
- Frontend UI: `http://localhost:8000/app/`
- API docs: `http://localhost:8000/docs`

## Setup With Docker

Create `.env` from `.env.example` and add your OpenAI API key.

Build and run:

```bash
docker compose up --build
```

The Docker Compose configuration maps the app to:

```text
http://localhost:8001/
```

Frontend UI:

```text
http://localhost:8001/app/
```

Stop the container:

```bash
docker compose down
```

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | OpenAI API key used by the backend. |
| `OPENAI_MODEL` | No | OpenAI model name. Defaults to `gpt-4o-mini`. |
| `DATABASE_URL` | No | SQLAlchemy database URL. Defaults to SQLite. |

Safe example:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./agent_platform.db
```

## Example API Requests and Responses

### Send a new chat message

Request:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"What is 25 * 1840 / 100?\"}"
```

Response:

```json
{
  "answer": "25 * 1840 / 100 is 460.",
  "session_id": "generated-session-id",
  "tool_used": "calculator",
  "tool_input": "25 * 1840 / 100",
  "tool_output": "460.0",
  "tool_error": null
}
```

### Continue an existing session

Request:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Explain that result briefly.\",\"session_id\":\"generated-session-id\"}"
```

Response:

```json
{
  "answer": "The calculation multiplies 25 by 1840 and then divides by 100, which gives 460.",
  "session_id": "generated-session-id",
  "tool_used": null,
  "tool_input": null,
  "tool_output": null,
  "tool_error": null
}
```

### List sessions

Request:

```bash
curl http://localhost:8000/api/sessions
```

Response:

```json
[
  {
    "session_id": "generated-session-id",
    "last_user_message": "Explain that result briefly.",
    "last_ai_answer": "The calculation multiplies 25 by 1840 and then divides by 100, which gives 460.",
    "message_count": 2,
    "last_activity": "2026-06-06T12:00:00"
  }
]
```

### Get one session history

Request:

```bash
curl http://localhost:8000/api/sessions/generated-session-id
```

Response:

```json
{
  "session_id": "generated-session-id",
  "messages": [
    {
      "role": "user",
      "content": "What is 25 * 1840 / 100?",
      "created_at": "2026-06-06T12:00:00",
      "tool_used": null,
      "tool_input": null,
      "tool_output": null,
      "tool_error": null
    },
    {
      "role": "assistant",
      "content": "25 * 1840 / 100 is 460.",
      "created_at": "2026-06-06T12:00:01",
      "tool_used": "calculator",
      "tool_input": "25 * 1840 / 100",
      "tool_output": "460.0",
      "tool_error": null
    }
  ]
}
```

## Project Structure

```text
ai-agent-platform/
|-- app/
|   |-- agents/
|   |   `-- agent.py
|   |-- api/
|   |   `-- chat.py
|   |-- core/
|   |   |-- config.py
|   |   `-- llm.py
|   |-- db/
|   |   |-- database.py
|   |   `-- models.py
|   |-- schemas/
|   |   `-- chat.py
|   |-- static/
|   |   |-- app.js
|   |   |-- index.html
|   |   `-- styles.css
|   |-- tools/
|   |   |-- calculator.py
|   |   |-- registry.py
|   |   |-- text_tools.py
|   |   `-- wikipedia.py
|   `-- main.py
|-- data/
|-- docker-compose.yml
|-- Dockerfile
|-- pyproject.toml
|-- README.md
|-- requirements.txt
|-- run.py
|-- uv.lock
`-- .env.example
```

## What I Learned

This project demonstrates practical backend AI engineering concepts:

- designing an AI agent API with FastAPI
- integrating OpenAI tool calling
- defining local tools through structured schemas
- storing chat history and tool metadata in SQLite
- building session-based memory
- exposing logs for observability
- managing Python dependencies with uv
- packaging the app with Docker
- adding a lightweight frontend without changing backend behavior

## Future Improvements

- Add authentication for protected logs and sessions.
- Add pagination for logs and long session histories.
- Add automated tests for API endpoints and tool execution.
- Add streaming responses for the chat endpoint.
- Add more tools, such as web search, file analysis, or database lookup.
- Add production-ready migrations with Alembic.
- Add deployment instructions for a cloud platform.

## Portfolio and Interview Explanation

AI Agent Platform is a backend-focused AI portfolio project. It shows how to build more than a simple chatbot by combining a FastAPI service, OpenAI tool calling, structured tool execution, session memory, persistent SQLite logs, Docker support, and a small local frontend.

In an interview, this project can be used to discuss:

- how tool calling works from model decision to backend execution
- how session memory is stored and reused
- how tool errors are captured without crashing the API
- how database logs improve debugging and observability
- how to structure a maintainable AI backend project
- how Docker and uv make local setup more reproducible
