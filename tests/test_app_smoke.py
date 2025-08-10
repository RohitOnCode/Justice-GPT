def test_home_page(app_client):
    resp = app_client.get("/")
    assert resp.status_code == 200

def test_chat_endpoint_mocked(app_client, monkeypatch):
    from src.agents import rag_graph as rg
    def fake_invoke(state): return {"final": "Hello from test."}
    monkeypatch.setattr(rg.rag_pipeline, "invoke", fake_invoke)
    resp = app_client.post("/chat", json={"message":"Hi"})
    assert resp.status_code == 200
    assert "Hello from test." in resp.get_json()["answer"]
