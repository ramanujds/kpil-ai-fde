# Site Status API — without uv

A minimal two-route FastAPI app, set up the traditional way with `venv` and `pip`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/docs`.

## Routes

| Route | Returns |
|---|---|
| `GET /` | A welcome message |
| `GET /sites/{site_id}/status` | Status of a synthetic site, or a 404 if the id is unknown |

Try `GET /sites/kpil-01/status` and `GET /sites/kpil-99/status` to see the 404 path.
