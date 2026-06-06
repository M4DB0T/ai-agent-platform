# AI Agent Platform

AI Agent Platform is a FastAPI-based AI engineering portfolio project with a simple frontend UI. It demonstrates OpenAI tool calling, session-based memory, SQLite logging, tool execution history, Docker support, and `uv`-based dependency management.

This project is backend-focused, but it also includes a lightweight frontend built with plain HTML, CSS, and JavaScript so the system can be tested through a simple local chat interface.

## Repository Description

AI Agent Platform built with FastAPI, OpenAI tool calling, session memory, SQLite logging, calculator and Wikipedia tools, frontend UI, uv, and Docker.

## Problem It Solves

Many AI demos only show a single prompt and response. This project demonstrates the backend engineering needed for a more practical AI agent service.

It includes:

- Structured API contracts
- Session continuity
- Tool execution
- Persistent chat and tool logs
- Error capture
- A simple frontend for local testing
- Docker-based reproducible setup

The goal is to show how an AI assistant can do more than just answer text. It can use tools, remember session context, store logs, and expose useful backend APIs.

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
- `uv` for dependency management

## Tech Stack

- Python 3.12
- FastAPI
- OpenAI Python SDK
- SQLAlchemy
- SQLite
- Pydantic
- uv
- Docker
- Docker Compose
- HTML
- CSS
- JavaScript

## Architecture Overview

The application is organized as a backend-first FastAPI service.

```text
User
  |
  v
Frontend UI / Swagger / API Client
  |
  v
FastAPI API Layer
  |
  v
Agent Layer
  |
  v
LLM Layer
  |
  +--------------------+
  |                    |
  v                    v
OpenAI Model       Tool Registry
                       |
                       +--> Calculator Tool
                       |
                       +--> Wikipedia Tool
  |
  v
SQLite Logging and Session Memory
```

Main project modules:

- `app/main.py` creates the FastAPI app, initializes database tables, includes API routes, and serves the static frontend.
- `app/api/chat.py` defines the chat, log, and session endpoints.
- `app/agents/agent.py` coordinates agent execution.
- `app/core/llm.py` communicates with OpenAI and handles tool-call decisions.
- `app/tools/registry.py` defines available tools and dispatches tool execution.
- `app/tools/calculator.py` contains the calculator tool.
- `app/tools/wikipedia.py` contains the Wikipedia summary tool.
- `app/db/` contains SQLAlchemy database setup and chat log models.
- `app/schemas/` contains Pydantic API schemas.
- `app/static/` contains the local frontend UI.

## Agent Flow

The main chat flow works like this:

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

Tool calling is handled through OpenAI function tools.

The available tool schemas are registered in:

```text
app/tools/registry.py
```

When the model decides that a tool is useful, the backend:

1. Parses the requested tool name.
2. Parses the tool arguments.
3. Executes the matching local Python function.
4. Captures the tool result or error.
5. Sends the result back to the model.
6. Stores the tool metadata in SQLite.

Tool execution metadata is saved with each chat log:

- `tool_used`
- `tool_input`
- `tool_output`
- `tool_error`

This makes tool behavior visible through both the API and frontend.

## Available Tools

### calculator

The calculator tool safely evaluates arithmetic expressions.

It is useful for:

- Addition
- Subtraction
- Multiplication
- Division
- Percentages
- Powers
- Basic numeric calculations

Example user message:

```text
What is 25 * 1840 / 100?
```

Expected tool metadata:

```json
{
  "tool_used": "calculator",
  "tool_input": "25 * 1840 / 100",
  "tool_output": "460.0",
  "tool_error": null
}
```

### wikipedia_search

The Wikipedia tool searches Wikipedia for a topic and returns a short summary.

It is useful for general knowledge questions about:

- People
- Concepts
- Technologies
- Organizations
- Historical events

Example user message:

```text
Who was Alan Turing?
```

Expected tool metadata:

```json
{
  "tool_used": "wikipedia_search",
  "tool_input": "Alan Turing",
  "tool_error": null
}
```

Note: The Wikipedia tool uses Wikipedia summaries and is intended for general background context. It is not a real-time web search engine.

## Session Memory

The API supports session-based memory using `session_id`.

If the client sends no `session_id`, the backend creates one automatically.

If the client sends an existing `session_id`, the backend loads recent messages from that session and passes them to the model as conversation history.

This allows the assistant to answer with context from previous messages in the same session.

Session-related endpoints:

- `GET /api/sessions` returns session summaries.
- `GET /api/sessions/{session_id}` returns full message history for one session.

## Logging and Observability

Each chat interaction is stored in SQLite.

Stored fields include:

- User message
- Assistant answer
- Session ID
- Tool used
- Tool input
- Tool output
- Tool error
- Timestamp

The endpoint below exposes stored chat logs:

```text
GET /api/logs
```

This is useful for:

- Debugging
- Reviewing tool calls
- Checking errors
- Understanding agent behavior
- Observability during local development

## Frontend UI

The project includes a simple frontend built with plain HTML, CSS, and JavaScript.

No frontend framework is required.

The UI includes:

- Left sidebar with previous sessions from `GET /api/sessions`
- Main chat area for user and assistant messages
- Message input connected to `POST /api/chat`
- Automatic reuse of returned `session_id`
- Session history loading from `GET /api/sessions/{session_id}`
- Assistant tool metadata display when available
- New chat flow
- Loading state while waiting for a response

After running the server, open:

```text
http://localhost:8000/app/
```

If your project serves the frontend at `/ui`, open:

```text
http://localhost:8000/ui
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a message to the AI agent. |
| `GET` | `/api/logs` | Return all stored chat logs. |
| `GET` | `/api/sessions` | Return session summaries ordered by recent activity. |
| `GET` | `/api/sessions/{session_id}` | Return full message history for one session. |

## Setup With uv

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-platform.git
cd ai-agent-platform
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Create an environment file

On Linux/macOS:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 4. Add your OpenAI API key to `.env`

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./agent_platform.db
```

### 5. Run the app

```bash
uv run python run.py
```

### 6. Open local URLs

API root:

```text
http://localhost:8000/
```

Frontend UI:

```text
http://localhost:8000/app/
```

Swagger API docs:

```text
http://localhost:8000/docs
```

## Setup With Docker

### 1. Create `.env`

Create `.env` from `.env.example` and add your OpenAI API key.

### 2. Build and run

```bash
docker compose up --build
```

If your Docker Compose file maps port `8001:8000`, open:

```text
http://localhost:8001/
```

Frontend UI:

```text
http://localhost:8001/app/
```

Swagger API docs:

```text
http://localhost:8001/docs
```

If your Docker Compose file maps port `8000:8000`, use:

```text
http://localhost:8000/
```

### 3. Stop the container

```bash
docker compose down
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key used by the backend. |
| `OPENAI_MODEL` | No | OpenAI model name. Defaults to `gpt-4o-mini`. |
| `DATABASE_URL` | No | SQLAlchemy database URL. Defaults to SQLite. |

Safe `.env.example`:

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
|   |   `-- wikipedia.py
|   `-- main.py
|-- data/
|-- docker-compose.yml
|-- Dockerfile
|-- pyproject.toml
|-- README.md
|-- run.py
|-- uv.lock
`-- .env.example
```

Note: `data/`, local database files, `.env`, and `.venv/` should not be committed to GitHub.

## What I Learned

This project demonstrates practical backend AI engineering concepts:

- Designing an AI agent API with FastAPI
- Integrating OpenAI tool calling
- Defining local tools through structured schemas
- Executing model-selected tools in the backend
- Storing chat history and tool metadata in SQLite
- Building session-based memory
- Exposing logs for observability
- Managing Python dependencies with `uv`
- Packaging the app with Docker
- Adding a lightweight frontend without turning the project into a frontend-focused app

## Future Improvements

Possible next improvements:

- Add authentication for protected logs and sessions
- Add pagination for logs and long session histories
- Add automated tests for API endpoints and tool execution
- Add streaming responses for the chat endpoint
- Add more tools, such as web search, file analysis, or database lookup
- Add production-ready migrations with Alembic
- Add rate limiting
- Add better frontend screenshots and demo GIF
- Add deployment instructions for a cloud platform
- Add multi-user support

## Portfolio and Interview Explanation

AI Agent Platform is a backend-focused AI portfolio project. It shows how to build more than a simple chatbot by combining a FastAPI service, OpenAI tool calling, structured tool execution, session memory, persistent SQLite logs, Docker support, and a small local frontend.

In an interview, this project can be used to discuss:

- How tool calling works from model decision to backend execution
- How session memory is stored and reused
- How tool errors are captured without crashing the API
- How database logs improve debugging and observability
- How the project separates API, agent, LLM, tool, schema, and database layers
- How Docker and `uv` make local setup more reproducible

## Important Notes

This project is intended as a portfolio and learning project. It is not presented as a full production SaaS product.

Before using it in production, improvements such as authentication, authorization, migrations, tests, rate limiting, monitoring, and deployment hardening would be needed.

## License

This project is for portfolio and educational purposes.