# backend/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from .graph_agent import agent  # compiled agent from your LangGraph setup

# -------------------- FastAPI App --------------------
app = FastAPI(
    title="MindFlow Wellness API",
    docs_url="/Newdocs",      # Swagger UI
    redoc_url="/Newredoc"     # ReDoc
)

# -------------------- Pydantic Model --------------------
class WellnessInput(BaseModel):
    mood: str
    stress: int
    sleep: float
    habits: list[str]

# -------------------- API Endpoint --------------------
@app.post("/analyze")
def analyze(data: WellnessInput):
    state = data.model_dump()  # converts Pydantic model to dict
    result = agent.invoke(state)  # run LangGraph agent
    return {
        "guidance": result.get("guidance"),
        "analysis_text": result.get("analysis"),
        "stress_analysis": result.get("stress_analysis"),
        "sleep_analysis": result.get("sleep_analysis"),
        "habit_analysis": result.get("habit_analysis")
    }

# -------------------- Root Endpoint --------------------
@app.get("/")
def root():
    return {
        "message": "✅ MindFlow Wellness API is running! Visit /Newdocs for Swagger UI or /Newredoc for ReDoc."
    }
