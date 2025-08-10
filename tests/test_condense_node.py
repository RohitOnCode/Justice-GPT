from src.agents import rag_graph as rg

def test_condense_uses_history_and_returns_standalone(dummy_llm, monkeypatch):
    rg.shared_memory.chat_memory.add_user_message("What does Section 420 say?")
    rg.shared_memory.chat_memory.add_ai_message("Cheating and dishonestly inducing delivery of property.")
    out = rg.condense({"query":"Is it bailable?"})
    assert "standalone_query" in out
    assert isinstance(out["standalone_query"], str)
    assert out["standalone_query"]
