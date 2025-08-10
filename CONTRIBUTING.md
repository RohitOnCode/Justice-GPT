# Contributing

Thanks for your interest! Please:
1. Open an issue describing the change.
2. Follow the existing code style.
3. Add/adjust tests for your change.
4. Open a PR targeting `main`.

## Dev
```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add keys
pytest -q
python app.py
```
