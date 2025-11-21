import streamlit as st
import requests

# ------------------ Config ------------------
st.set_page_config(page_title="💆 MindFlow Wellness Coach", page_icon="🧠", layout="wide")
API_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

# ------------------ Header ------------------
st.title("💆 MindFlow Mental Wellness Coach")
st.markdown("### 🌱 Get personalized mental wellness guidance based on your mood, stress, sleep, and habits.")

# ------------------ User Input ------------------
st.subheader("📝 Your Daily Info")
mood = st.text_input("Mood (e.g., happy, stressed, anxious)")
stress = st.slider("Stress Level (0-10)", min_value=0, max_value=10, value=5)
sleep = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, value=7.0)
habits = st.text_area("Current Habits (comma-separated)").split(",")

# ------------------ Analyze Button ------------------
if st.button("✨ Get Guidance"):
    if not mood or stress is None or sleep is None or not habits:
        st.warning("⚠️ Please fill out all fields.")
    else:
        payload = {
            "mood": mood,
            "stress": stress,
            "sleep": sleep,
            "habits": [h.strip().lower() for h in habits if h.strip()]
        }
        try:
            with st.spinner("🔍 Analyzing your wellness profile..."):
                response = requests.post(f"{API_URL}/analyze", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    # ------------------ Display ------------------
                    st.subheader("🧠 Analysis")
                    st.write(data.get("analysis_text"))

                    st.subheader("💡 Guidance")
                    st.success(data.get("guidance"))

                    st.subheader("📊 Tools Analysis")
                    st.markdown("**Stress:**")
                    st.write(data.get("stress_analysis"))
                    st.markdown("**Sleep:**")
                    st.write(data.get("sleep_analysis"))
                    st.markdown("**Habits:**")
                    st.write(data.get("habit_analysis"))
                else:
                    st.error(f"❌ API Error: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ Something went wrong: {e}")
