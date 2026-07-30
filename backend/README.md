# Headcanon — Backend

FastAPI backend for the Headcanon multimedia story-generation platform.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) or pip

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # fill in your credentials
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Health Check

```
GET /health  →  {"status": "ok"}
```
