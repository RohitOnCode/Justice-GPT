# JusticeGPT — IPC Legal Copilot

JusticeGPT is a Retrieval-Augmented Generation (RAG) chatbot for the **Indian Penal Code (IPC)**.  
It uses **two retrieval agents** over a single corpus split in half:
- Agent 1 → **Chroma** (first half)
- Agent 2 → **FAISS** (second half)

Both agents share **one conversation memory** and their answers are **synthesized** into a single, clear response.  
The app provides a simple **Flask** UI with a **Thinking… spinner** while answers are generated.

---

## Features

- ⚖️ Legal RAG on the IPC (PDF auto-downloaded on first run)
- 🧠 **Single shared memory** (`ConversationBufferMemory`) across both agents
- 🔎 Dual vector stores: **Chroma** + **FAISS**
- 🧩 **Answer synthesizer** merges both agent answers into one
- 🌀 **Spinner/Thinking UI** during LLM calls
- 📦 Vector stores **auto-build once** (skip if already persisted)
- 🧰 Prompts externalized in `prompts/promt.txt`
- ✅ Modern imports: `langchain-openai`, `langchain-chroma` (no deprecation noise)
- 🐍 Python 3.13 compatible; LangGraph 0.5 with state schema & `.invoke()`

---

## Project Structure

```
justicegpt_ipc_legal_copilot/
├─ .env.example
├─ requirements.txt
├─ README.md
├─ app.py
├─ prompts/
│  └─ promt.txt
├─ chroma_db/        # empty; built on first run
├─ faiss_db/         # empty; built on first run
├─ docs/             # empty; IPC PDF saved here on first run
├─ templates/
│  └─ index.html
├─ static/
│  └─ style.css
└─ src/
   ├─ agents/
   │  └─ rag_graph.py
   ├─ loaders/
   │  └─ ipc_loader.py
   ├─ memory/
   │  └─ chat_memory.py
   └─ vectorstores/
      └─ auto_build.py
```

---

## Quickstart

```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python app.py          # first run builds vectors, later runs skip
# open http://localhost:7070
```

> **Note:** The first run will download the IPC PDF and build the Chroma + FAISS indexes.  
> Subsequent runs will reuse the persisted stores and skip the build.

---

## Config

Edit `.env`:
- `OPENAI_API_KEY`: your OpenAI key
- `OPENAI_CHAT_MODEL`: e.g., `gpt-4o`
- `OPENAI_EMBED_MODEL`: e.g., `text-embedding-3-small`
- `CHROMA_TELEMETRY=FALSE`: silences Chroma telemetry logs

---

## Troubleshooting

- **NumPy errors (`np.float_ removed`)**: We pin `numpy<2.0` in `requirements.txt`.
- **FAISS load error about pickle**: We enable `allow_dangerous_deserialization=True` for loading *your own* local FAISS index. Do **not** do this for untrusted files.
- **Deprecation warnings**: All imports updated to `langchain-openai` & `langchain-chroma`.
- **Chroma telemetry warnings**: Set `CHROMA_TELEMETRY=FALSE` in `.env`.

---

## Customize

- Edit prompts in `prompts/promt.txt` (merge/synthesis & condense templates).
- Switch memory to Redis (persistent) by changing the memory builder in `src/memory/chat_memory.py`.
- Add streaming token-by-token responses (SSE/WebSockets) if desired.

MIT-style use permitted (add your own LICENSE if needed).
