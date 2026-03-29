import os
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

# load env vars
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VECTOR_STORE_ID = os.environ.get("VECTOR_STORE_ID")
MODEL = os.environ.get("MODEL", "gpt-4.1")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY env var.")
if not VECTOR_STORE_ID:
    raise RuntimeError("Missing VECTOR_STORE_ID env var (your hosted vector store id).")

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI(title="Config Assist Demo")

class ChatRequest(BaseModel):
    # Send the full conversation so the assistant has context
    messages: List[Dict[str, Any]]  # [{"role": "user"|"assistant", "content": "..."}]

class ChatResponse(BaseModel):
    answer: str
    # Optional: raw response for debugging (set include_debug=True in request if you add that later)
    sources: Optional[List[Dict[str, Any]]] = None

SYSTEM_PROMPT = """You are an internal documentation assistant.
You MUST always call the file_search tool before answering any question.
Answer ONLY using information retrieved from the file_search tool. Do not use your training knowledge or any external information.
If the retrieved documentation does not contain the answer, say so explicitly and ask a clarifying question or suggest where to look. Do not attempt to answer from memory.
When the user asks to analyze data, compare values, or requests a table, always format the results as a markdown table.
Keep answers concise and actionable.
"""


@app.get("/", response_class=HTMLResponse)
def index():
    # Single-file HTML UI
    return HTMLResponse(
        """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Config Assist Demo</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    body { font-family: system-ui, Arial; max-width: 900px; margin: 24px auto; }
    #chat { border: 1px solid #ddd; padding: 12px; height: 60vh; overflow-y: auto; background: #fafafa; }
    .msg { margin: 10px 0; }
    .user { font-weight: 600; white-space: pre-wrap; }
    .assistant { }
    .assistant table { border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 13px; }
    .assistant th, .assistant td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
    .assistant th { background: #f0f0f0; font-weight: 600; }
    .assistant tr:nth-child(even) td { background: #f9f9f9; }
    .meta { color: #666; font-size: 12px; margin-top: 2px; }
    #row { display: flex; gap: 8px; margin-top: 12px; }
    #q { flex: 1; padding: 10px; }
    button { padding: 10px 14px; }
  </style>
</head>
<body>
  <h2>Config Assist Demo</h2>
  <div id="chat"></div>

  <div id="row">
    <input id="q" placeholder="Ask a question about the docs..." />
    <button onclick="send()">Send</button>
  </div>

<script>
  const chatEl = document.getElementById("chat");
  const inputEl = document.getElementById("q");

  const messages = []; // conversation memory

  function addMsg(role, text) {
    const div = document.createElement("div");
    div.className = "msg " + role;
    const label = document.createElement("div");
    label.className = role;
    label.textContent = (role === "user" ? "You" : "Assistant") + ": ";
    if (role === "assistant") {
      const body = document.createElement("div");
      body.className = "assistant";
      body.innerHTML = marked.parse(text);
      div.appendChild(label);
      div.appendChild(body);
    } else {
      label.textContent += text;
      div.appendChild(label);
    }
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  async function send() {
    const q = inputEl.value.trim();
    if (!q) return;

    messages.push({ role: "user", content: q });
    addMsg("user", q);
    inputEl.value = "";
    inputEl.focus();

    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages })
    });

    const data = await res.json();
    messages.push({ role: "assistant", content: data.answer });
    addMsg("assistant", data.answer);
  }

  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") send();
  });

  addMsg("assistant", "Ask me something about the documentation.");
</script>
</body>
</html>
        """
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        input_messages = []
        for m in req.messages:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                input_messages.append({"role": role, "content": content})

        resp = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=input_messages,
            tools=[{"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]}],
        )

        answer = resp.output_text
        return ChatResponse(answer=answer, sources=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))