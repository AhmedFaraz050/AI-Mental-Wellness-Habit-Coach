# 💡 MindFlow: AI Mental Wellness & Habit Coach

A context-aware AI agent that provides personalized wellness guidance, stress analysis, sleep insights, and habit recommendations using **Gemini LLM**, **LangGraph**, **FastAPI**, and **Streamlit**.

---

## 🌟 Features

* Analyze user mood, stress level, sleep hours, and current habits.
* Provide warm, actionable mental wellness guidance.
* MCP-style tools for:

  * Stress evaluation
  * Sleep quality assessment
  * Habit recommendations
* Interactive **Streamlit frontend** to input user data and view insights.
* **FastAPI backend** serving the LangGraph agent.
* Deployable on free cloud platforms (Render, Streamlit Cloud, or Vercel).

---

## 🏗️ Tech Stack

| Component           | Technology / Library                         |
| ------------------- | -------------------------------------------- |
| LLM                 | Google Gemini (via `langchain_google_genai`) |
| Agent Orchestration | LangGraph                                    |
| Backend             | FastAPI + Pydantic                           |
| Frontend            | Streamlit                                    |
| Deployment          | Render / Streamlit Cloud                     |
| Environment         | Python 3.10+, `.env` for API keys            |

---

## 📁 Project Structure

```
AI-Mental-Wellness-Habit-Coach/
│
├─ backend/
│   ├─ api.py           # FastAPI server & endpoints
│   └─ graph_agent.py   # LangGraph agent definition & MCP tools
│
├─ frontend/
│   └─ app.py    # Streamlit UI to interact with agent
│
├─ .env                # Environment variables (Gemini API key)
├─ requirements.txt    # Python dependencies
└─ README.md           # Project documentation
```

---

## ⚡ Setup & Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Mental-Wellness-Habit-Coach.git
cd AI-Mental-Wellness-Habit-Coach
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run FastAPI backend

```bash
uvicorn backend.api:app --reload
```

* API docs: [http://127.0.0.1:8000/newdocs](http://127.0.0.1:8000/newdocs)

### 6. Run Streamlit frontend

```bash
streamlit run frontend/app.py
```

* Streamlit UI: [http://localhost:8501](http://localhost:8501)

---

## 🛠️ Usage

1. Open the Streamlit app.
2. Enter your mood, stress level (1-10), sleep hours, and habits.
3. Click **Analyze**.
4. View:

   * AI-generated wellness guidance
   * Stress, sleep, and habit analysis
   * Recommendations for improving mental wellness

---

## 📦 Deployment

* Deploy backend on **Render** (free tier) or any FastAPI-friendly host.
* Deploy frontend on **Streamlit Cloud**.
* Update `FASTAPI_URL` in `dstreamlit.py` to point to your deployed backend.

---

## 🔑 Environment Secrets

* Keep your **Gemini API key** private in `.env`.
* Never commit `.env` to GitHub (included in `.gitignore`).

---

## ✨ Optional Enhancements

* Add speech input/output using Whisper & Coqui TTS.
* Add Google/Firebase login to save user sessions.
* Include caching with Redis or in-memory for repeated queries.
* Perform stress testing for multiple concurrent users.

---

## 💻 Demo

![Demo GIF](demo.gif) *(Replace with your own GIF)*

---

## 📝 License

MIT License © Ahmed Faraz

.

Do you want me to make that version too?
