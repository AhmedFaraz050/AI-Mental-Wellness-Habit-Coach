from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, List
import os
from dotenv import load_dotenv

load_dotenv()

# ----------------- Gemini LLM -----------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# ----------------- State Schema -----------------
class WellnessState(TypedDict):
    mood: str
    stress: int
    sleep: float
    habits: List[str]
    analysis: str
    stress_analysis: dict
    sleep_analysis: dict
    habit_analysis: dict
    guidance: str

# ----------------- MCP-Style Tools -----------------
def stress_tool(stress: int):
    if stress <= 3:
        return {"status": "Low Stress", "tips": ["Keep journaling", "Maintain routine"]}
    elif stress <= 6:
        return {"status": "Moderate Stress", "tips": ["Try deep breathing", "Walk 10 minutes"]}
    else:
        return {"status": "High Stress", "tips": ["Mindfulness exercise", "Talk to a friend"]}

def sleep_tool(hours: float):
    if hours < 5:
        return {"status": "Very Low Sleep", "tips": ["Avoid screens", "Short nap if possible"]}
    elif hours < 7:
        return {"status": "Below Optimal Sleep", "tips": ["Go to bed earlier", "Relaxing tea"]}
    else:
        return {"status": "Healthy Sleep", "tips": ["Keep routine", "Good energy"]}

def habit_tool(habits: List[str]):
    recommendations = []
    if "exercise" not in habits:
        recommendations.append("Add 10-min morning walk")
    if "journaling" not in habits:
        recommendations.append("Start 5-min nightly journaling")
    if not recommendations:
        recommendations.append("Great habit consistency!")
    return {"status": "Habit Analysis", "tips": recommendations}

# ----------------- LangGraph Nodes -----------------
def analyze_node(state: WellnessState):
    prompt = ChatPromptTemplate.from_template("""
You are a mental wellness coach.
User Mood: {mood}
Stress Level: {stress}/10
Sleep Hours: {sleep}
Current Habits: {habits}

Provide a warm, short supportive analysis.
""")
    chain = prompt | llm
    state["analysis"] = chain.invoke(state).content
    return state

def tools_node(state: WellnessState):
    state["stress_analysis"] = stress_tool(state["stress"])
    state["sleep_analysis"] = sleep_tool(state["sleep"])
    state["habit_analysis"] = habit_tool(state["habits"])
    return state

def final_node(state: WellnessState):
    prompt = ChatPromptTemplate.from_template("""
Based on the analysis:
{analysis}

Stress Analysis: {stress_analysis}
Sleep Analysis: {sleep_analysis}
Habit Analysis: {habit_analysis}

Provide a concise, friendly wellness guidance message.
""")
    chain = prompt | llm
    state["guidance"] = chain.invoke(state).content
    return state

# ----------------- Build Graph -----------------
def build_graph():
    graph = StateGraph(WellnessState)
    graph.add_node("analyze", analyze_node)
    graph.add_node("tools", tools_node)
    graph.add_node("final", final_node)

    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "tools")
    graph.add_edge("tools", "final")
    graph.add_edge("final", END)

    return graph.compile()

# ----------------- Export agent -----------------
agent = build_graph()
