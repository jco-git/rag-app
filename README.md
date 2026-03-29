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

## Example prompts

The assistant works best when questions are specific and grounded in what your docs cover. The current `docs/` folder contains user permissions and best practices documentation, so the prompts below are good starting points.

### Factual lookups
Ask directly for a specific piece of information:
- *"What permissions does the editor role have?"*
- *"What approval is required to assign the admin role?"*
- *"How do I revoke a role via the API?"*

### Procedural / how-to
Ask for step-by-step guidance:
- *"Walk me through assigning a role to a user via the admin panel."*
- *"How do I bulk update roles for multiple users at once?"*
- *"What's the process for offboarding a user who has left the company?"*

### Comparisons (triggers a markdown table)
Ask the assistant to compare or summarize multiple items — it will format the result as a table:
- *"Compare all available roles and their access levels."*
- *"Show me a table of all feature flag best practices."*

### Policy and rules
Ask about constraints, requirements, or guidelines:
- *"What are the rules around feature flag rollouts in production?"*
- *"How often should API tokens be rotated?"*
- *"What should I do first when investigating a production incident?"*

### Multi-turn follow-ups
The assistant remembers the conversation, so you can ask follow-up questions naturally:
1. *"What roles are available?"*
2. *"Which one should I assign to someone who only needs to read dashboards?"*
3. *"How do I assign that via the API?"*

### Tips for better results
- **Be specific** — "How do I assign the viewer role via the API?" gets a better answer than "How do roles work?"
- **Reference the docs** — If you know the topic is covered, mention it: *"According to the best practices doc, how should I handle feature flag rollouts?"*
- **Ask follow-ups** — If an answer is incomplete, ask the assistant to expand or clarify rather than rephrasing the original question from scratch.
