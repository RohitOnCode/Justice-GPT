import pytest

class DummyResp:
    def __init__(self, content): self.content = content

@pytest.fixture
def dummy_llm(monkeypatch):
    from src.agents import rag_graph as rg
    def fake_invoke(prompt):
        return DummyResp("standalone: ok")
    monkeypatch.setattr(rg.llm, "invoke", fake_invoke)
    return rg.llm

@pytest.fixture
def app_client():
    from app import app
    app.testing = True
    with app.test_client() as c:
        yield c
