# Copilot Instructions

## What this project does

A Retrieval-Augmented Generation (RAG) app using OpenAI's file search (vector store) and GPT-4.1. It indexes local markdown and JSON docs from `docs/` into an OpenAI vector store, then serves a FastAPI chat interface that answers questions about those docs with conversation context.

## Architecture

Two distinct components:

- **`main.py`** — Indexing script. Creates an OpenAI vector store, uploads all `docs/**/*.md` and `docs/**/*.json` files, and prints the `VECTOR_STORE_ID` to add to `.env`. Run this once before starting the server, or with `--resync` to re-upload after doc changes.
- **`app.py`** — FastAPI server with two routes:
  - `GET /` — Serves a self-contained HTML/JS chat UI (inlined as a string in the route handler)
  - `POST /chat` — Accepts `{"messages": [...]}` (full conversation history) and calls the OpenAI Responses API with `file_search` against the vector store

**Critical detail:** The app uses `client.responses.create()` (OpenAI Responses API), **not** `client.chat.completions.create()`. Conversation history is maintained entirely client-side — the frontend sends the full message array on every request.

## Running the app

```bash
# Install dependencies
pip install openai fastapi uvicorn python-dotenv pydantic

# Step 1: Index docs and get a vector store ID
python main.py
# Copy the printed VECTOR_STORE_ID into .env

# Step 2: Start the server
uvicorn app:app --reload

# Re-upload docs after changes
python main.py --resync
```

## Environment variables

| Variable | Required | Default |
|---|---|---|
| `OPENAI_API_KEY` | Yes | — |
| `VECTOR_STORE_ID` | Yes (after indexing) | — |
| `MODEL` | No | `gpt-4.1` |

## Key conventions

- **Adding docs**: Drop `.md` or `.json` files anywhere under `docs/`, then run `python main.py --resync`. The `DOC_GLOBS` list in `main.py` controls which file types are indexed.
- **Changing the assistant's behavior**: Edit `SYSTEM_PROMPT` in `app.py`. The prompt currently instructs the assistant to use markdown tables for data comparisons and stay concise.
- **The UI is inlined**: The entire frontend HTML/CSS/JS lives inside the `index()` route handler in `app.py` as a string — there is no separate template or static file.
- **`--resync` behavior**: Deletes all existing files from the vector store before re-uploading. It does not create a new store; it reuses the `VECTOR_STORE_ID` from `.env`.
