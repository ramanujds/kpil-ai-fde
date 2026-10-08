# Site Status API — with uv

The same two-route FastAPI app as the without-uv version, set up with `uv` instead of
`venv` + `pip`.

## Setup and run

```bash
uv sync
uv run uvicorn main:app --reload
```

`uv sync` reads `pyproject.toml`, creates a `.venv` automatically, and installs the
dependencies — no separate activate step, no `requirements.txt`.

Visit `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/docs`.

## Routes

| Route | Returns |
|---|---|
| `GET /` | A welcome message |
| `GET /sites/{site_id}/status` | Status of a synthetic site, or a 404 if the id is unknown |

Try `GET /sites/kpil-01/status` and `GET /sites/kpil-99/status` to see the 404 path.
