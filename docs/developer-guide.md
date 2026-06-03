# Developer Guide

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m sql_engine.seed
uvicorn app.main:app --reload
```

Run the UI:

```bash
streamlit run frontend/streamlit_app.py
```

Run tests:

```bash
pytest -q
```

## Adding A New Data Domain

1. Add a table definition to `sql_engine/schema.py`.
2. Add sample rows to `sql_engine/seed.py`.
3. Extend deterministic SQL patterns in `agents/sql_generation.py`.
4. Add role policies in `sql_engine/validator.py`.
5. Add tests for validation and workflow behavior.

## LLM Integration

Set `ENABLE_LLM=true` and `GEMINI_API_KEY` to enable Gemini-compatible generation. The deterministic SQL generator remains as a fallback for offline demos and CI.
