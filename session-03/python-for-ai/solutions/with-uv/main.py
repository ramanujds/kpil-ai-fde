from fastapi import FastAPI, HTTPException

app = FastAPI(title="Site Status API")

SITE_STATUS = {
    "kpil-01": {"name": "Ring Road Flyover", "status": "on-track"},
    "kpil-02": {"name": "Metro Package 3", "status": "delayed"},
    "kpil-03": {"name": "Bridge Widening", "status": "on-hold"},
}


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    site = SITE_STATUS.get(site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"No site found with id '{site_id}'")
    return site
