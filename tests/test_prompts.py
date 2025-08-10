from src.agents.rag_graph import PROMPTS, PROMPT_FILE

def test_prompt_file_exists():
    assert PROMPT_FILE.exists()

def test_has_blocks():
    assert "SYNTH" in PROMPTS and "CONDENSE" in PROMPTS
    assert "{a1}" in PROMPTS["SYNTH"]
