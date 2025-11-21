from fastapi import FastAPI
from pydantic import BaseModel
from .graph_agent import agent  # import compiled agent

# -------------------- FastAPI App --------------------
app = FastAPI(
    title="MindFlow Wellness API",
    docs_url="/newdocs",      # Swagger UI
    redoc_url="/newredoc"     # ReDoc
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
    state = data.model_dump()  # convert to dict
    result = agent.invoke(state)
    return {
        "guidance": result.get("guidance"),
        "stress_analysis": result.get("stress_analysis"),
        "sleep_analysis": result.get("sleep_analysis"),
        "habit_analysis": result.get("habit_analysis"),
        "analysis_text": result.get("analysis")
    }

# -------------------- Root --------------------
@app.get("/")
def root():
    return {"message": "✅ MindFlow Wellness API is running! Visit /Newdocs for Swagger UI."}
