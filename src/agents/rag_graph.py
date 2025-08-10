# src/agents/rag_graph.py
from __future__ import annotations
import os, pathlib, dotenv
from typing import TypedDict, NotRequired

from langgraph.graph import StateGraph, END
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

from src.memory.chat_memory import build_shared_memory
from src.vectorstores.auto_build import ensure_vectorstores

dotenv.load_dotenv()

ROOT = pathlib.Path(__file__).parents[2]
CHROMA_DIR = ROOT / "chroma_db"
FAISS_DIR  = ROOT / "faiss_db"
PROMPT_FILE = ROOT / "prompts" / "prompt.txt"

# ---------- load prompts ----------
def _load_prompts(path: pathlib.Path) -> dict[str, str]:
    text = path.read_text()
    blocks, current, buf = {}, None, []
    for line in text.splitlines():
        ls = line.strip()
        if ls.startswith("--") and ls.endswith("--"):
            tag = ls.strip("-").upper()
            if tag in {"SYNTH", "CONDENSE"}:
                if current and buf:
                    blocks[current] = "\n".join(buf).strip()
                    buf = []
                current = tag
            elif ls == "--END--":
                if current is not None:
                    blocks[current] = "\n".join(buf).strip()
                    buf, current = [], None
            continue
        buf.append(line)
    if current and buf:
        blocks[current] = "\n".join(buf).strip()
    return blocks

PROMPTS = _load_prompts(PROMPT_FILE)

# ---------- llm + embeddings + shared memory ----------
emb = OpenAIEmbeddings()
llm = ChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o"), temperature=0)
shared_memory = build_shared_memory()  # ONE shared memory for all agents

# ---------- retrieval agents ----------
def build_agent1():
    retriever = Chroma(
        collection_name="ipc_part1",
        persist_directory=str(CHROMA_DIR / "ipc_part1"),
        embedding_function=emb,
    ).as_retriever(search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, memory=shared_memory
    )

def build_agent2():
    vs = FAISS.load_local(
        str(FAISS_DIR / "ipc_part2"),
        embeddings=emb,
        index_name="index",
        allow_dangerous_deserialization=True,
    )
    retriever = vs.as_retriever(search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, memory=shared_memory
    )

agent1 = build_agent1()
agent2 = build_agent2()

# ---------- helpers ----------
def _history_text() -> str:
    """Render shared chat history as plain text for the condense prompt."""
    msgs = getattr(shared_memory, "chat_memory", None)
    if not msgs or not getattr(msgs, "messages", None):
        return ""
    lines = []
    for m in msgs.messages:
        # robust role detection across versions
        role = getattr(m, "role", None) or getattr(m, "type", "")
        who = "User" if role in ("user", "human") else ("Assistant" if role in ("ai", "assistant") else "System")
        content = getattr(m, "content", "") or ""
        if content:
            lines.append(f"{who}: {content}")
    return "\n".join(lines)

# ---------- node fns ----------
def condense(state: dict) -> dict:
    """Rewrite follow-up into a standalone query using history + CONDENSE prompt."""
    followup = state["query"]
    tmpl = PROMPTS.get("CONDENSE", "Rewrite as standalone: {followup}")
    prompt = tmpl.format(history=_history_text(), followup=followup)
    try:
        standalone = llm.invoke(prompt).content.strip()
        if not standalone:
            standalone = followup
    except Exception:
        standalone = followup
    return {"standalone_query": standalone}

def run_agent1(state: dict) -> dict:
    q = state.get("standalone_query") or state["query"]
    return {"ans1": agent1.invoke(q)["result"]}

def run_agent2(state: dict) -> dict:
    q = state.get("standalone_query") or state["query"]
    return {"ans2": agent2.invoke(q)["result"]}

def synthesize(state: dict) -> dict:
    synth_tmpl = PROMPTS.get("SYNTH", "Merge A and B.\nA:{a1}\nB:{a2}\nFinal:")
    prompt = synth_tmpl.format(
        question=state.get("standalone_query") or state.get("query", ""),
        a1=state.get("ans1", ""),
        a2=state.get("ans2", ""),
    )
    final = llm.invoke(prompt)
    final = final.content

    # IMPORTANT: update shared memory with this turn
    try:
        shared_memory.chat_memory.add_user_message(state["query"])
        shared_memory.chat_memory.add_ai_message(final)
    except Exception:
        pass

    return {"final": final}

# ---------- state schema ----------
class ChatState(TypedDict):
    query: str
    standalone_query: NotRequired[str]
    ans1: NotRequired[str]
    ans2: NotRequired[str]
    final: NotRequired[str]

# ---------- graph ----------
def build_graph():
    ensure_vectorstores()
    sg = StateGraph(ChatState, name="ipc_rag_graph")
    sg.add_node("condense", condense)
    sg.add_node("agent1", run_agent1)
    sg.add_node("agent2", run_agent2)
    sg.add_node("synth",  synthesize)

    sg.set_entry_point("condense")
    sg.add_edge("condense", "agent1")
    sg.add_edge("agent1", "agent2")
    sg.add_edge("agent2", "synth")
    sg.add_edge("synth", END)
    return sg.compile()

rag_pipeline = build_graph()
