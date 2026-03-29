# RAG App

A simple Retrieval-Augmented Generation (RAG) app using OpenAI's file search (vector store) and GPT-4.1.

## What it does

- Indexes local markdown and JSON docs into an OpenAI vector store
- Exposes a FastAPI chat interface that answers questions about those docs
- Maintains conversation context across turns

## Setup

```bash
pip install openai fastapi uvicorn python-dotenv pydantic
```

Create a `.env` file:

```
OPENAI_API_KEY=your-key-here
VECTOR_STORE_ID=          # filled in after running main.py
```

## Usage

**1. Index your docs** (creates the vector store and uploads files from `docs/`):

```bash
python main.py
```

Copy the printed `VECTOR_STORE_ID` into your `.env`, then:

**2. Start the chat server:**

```bash
uvicorn app:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

To re-upload docs after changes:

```bash
python main.py --resync
```
