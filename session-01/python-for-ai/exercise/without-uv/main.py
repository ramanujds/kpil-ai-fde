"""Site Status API -- Day 1, Block 3: Python for AI.

A minimal FastAPI app: two routes, one small piece of synthetic data.
Fill in the TODOs, then run it -- see exercise-walkthrough/README.md
for the exact commands.
"""

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Kalpataru Site Status API")

# Synthetic, in-memory data only -- never real project data.
SITE_STATUS = {
    "site-a": "On Track",
    "site-b": "Delayed",
    "site-c": "On Track",
}


@app.get("/")
def root():
    # TODO: return a dict with a "message" key.
    pass


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    # TODO: look up site_id.lower() in SITE_STATUS.
    # TODO: if it is not there, raise HTTPException(status_code=404, detail=...).
    # TODO: otherwise return {"site_id": site_id, "status": status}.
    pass
