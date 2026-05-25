from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from api.job_radar import JobRadar

# ── Rutas dinámicas con pathlib (nunca absolutas) ──────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Career Booster AI 2.0")

# ── CORS: solo orígenes conocidos ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://careerboosterai.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Career Booster AI 2.0 — operational"}

# ── PROXY: el backend llama a Remotive, el frontend no sabe que existe ──────
@app.get("/api/jobs")
def get_jobs(
    q: str | None = Query(None),
    location: str | None = Query(None),
):
    try:
        import requests
        search = f"{q or 'fintech sales manager'} {location or 'latam mexico remote'}"
        response = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": search, "limit": 20},
            timeout=10,
        )
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
        
        return [
            {
                "company": j.get("company_name", "N/A"),
                "title": j.get("title", "N/A"),
                "url": j.get("url", "#"),
                "location": j.get("candidate_required_location", "Remote"),
                "salary": j.get("salary"),
                "tags": j.get("tags", [])[:4],
                "source": "api"
            }
            for j in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudieron obtener los empleos: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
