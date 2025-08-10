# JusticeGPT — IPC Legal Copilot

A Retrieval-Augmented Generation (RAG) chatbot designed to assist with queries on the **Indian Penal Code (IPC)** by retrieving relevant sections, interpreting them, and answering legal questions in plain language.

## Overview

JusticeGPT combines:
- Two retrieval agents (Chroma + FAISS) over split IPC corpus
- A single shared conversation memory
- A condense step that rewrites follow-ups into standalone queries
- An LLM synthesizer to merge both agent outputs
- Automatic first-run PDF download and vector-store build
- A Flask-based UI with a live "Thinking..." status indicator

It is intended for quick and context-aware legal reference, not legal advice.

## Target Audience

- Law students and educators  
- Legal researchers  
- Citizens seeking a quick understanding of IPC sections  
- Developers interested in multi-agent RAG architectures  

## Prerequisites

- Python 3.11–3.13 (recommended: 3.13)  
- OpenAI API key  
- Internet access on first run to fetch the IPC PDF  
- Basic familiarity with Python and command-line usage  

## Installation

```bash
git clone <repo_url> justicegpt_ipc_legal_copilot
cd justicegpt_ipc_legal_copilot
python3.13 -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Setup

```bash
cp .env.example .env
# Edit .env with your API key:
# OPENAI_API_KEY=sk-...
```

## Usage

Start the app:
```bash
python app.py
```
Then open [http://localhost:7070](http://localhost:7070) in your browser.

On first run:
- Downloads IPC PDF into `docs/`
- Splits into two halves
- Builds vector stores in `chroma_db/` and `faiss_db/`

Subsequent runs skip rebuilding.

## Data Requirements

- The IPC corpus (auto-downloaded from `https://www.indiacode.nic.in/bitstream/...`)  
- The app splits it into two halves for separate retrieval  

## Testing

Run:
```bash
pytest -q
```
Covers:
- Prompt template presence  
- Condense step functionality  
- Flask route smoke tests  

## Configuration

Set in `.env`:
- `OPENAI_API_KEY`: **Required** — your OpenAI key  
- `OPENAI_CHAT_MODEL`: Defaults to `gpt-4o`  
- `OPENAI_EMBED_MODEL`: Defaults to `text-embedding-3-small`  
- `CHROMA_TELEMETRY`: Defaults to `FALSE`  

## Methodology

JusticeGPT uses:
1. **Condense Node** — rewrites follow-ups into standalone queries using shared history  
2. **Agent 1** — Chroma vector store over part 1 of IPC  
3. **Agent 2** — FAISS vector store over part 2 of IPC  
4. **Synthesis Node** — merges results into a unified answer  

All prompts are stored in `prompts/prompt.txt`.

## Performance

- First run: ~20–30 seconds (PDF download + index build)  
- Subsequent runs: near-instant query response (depends on OpenAI API latency)  

## License

MIT License — see `LICENSE`.

## Contributing

1. Fork the repo  
2. Create a feature branch  
3. Submit a pull request  

See `CONTRIBUTING.md` for full guidelines.

## Changelog

See `CHANGELOG.md` for version history.

## Citation

If used in research:
```
@misc{justicegpt2025,
  author = {JusticeGPT Team},
  title = {JusticeGPT — IPC Legal Copilot},
  year = {2025},
  howpublished = {\url{https://github.com/...}}
}
```

## Contact

Maintainers:  
Email: rchopra424@gmail.com 
GitHub Issues: rchopra424@gmail.com 
