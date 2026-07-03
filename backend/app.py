from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_research_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agent-forge-delta-five.vercel.app",
        "https://agent-forge-qwfpreimv-deekshitha44.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.post("/research")
def research(data: dict):

    topic = data["topic"]

    result = run_research_pipeline(topic)

    # Pipeline may return an error-only payload (e.g., quota/auth issues).
    if "error" in result:
        return {"error": result["error"]}

    return {
        "search_results": result.get("search_results", ""),
        "scraped_content": result.get("scraped_content", ""),
        "report": result.get("report", ""),
        "critique": result.get("feedback", result.get("critique", ""))
    }