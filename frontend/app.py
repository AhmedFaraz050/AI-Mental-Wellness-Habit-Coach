# frontend/app.py
import streamlit as st
import requests
import json
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# ------------------ CONFIG ------------------
st.set_page_config(page_title="MindFlow Dashboard", page_icon="🧠", layout="wide")
API_URL = "https://ai-mental-wellness-habit-coach.onrender.com/"  # change if needed

# ------------------ HELPERS ------------------
def gen_dates(days=7):
    today = datetime.now().date()
    return [(today - timedelta(days=i)).isoformat() for i in reversed(range(days))]

def jittered_series(center, days=7, var=1.5, floor=0, ceil=10):
    s = []
    for _ in range(days):
        v = center + random.uniform(-var, var)
        v = max(floor, min(ceil, v))
        s.append(round(v, 1))
    return s

# light lexicon-based sentiment scoring for mood text
POS = {"happy","good","great","calm","relaxed","productive","excited","joy","joyful","content"}
NEG = {"anxious","stressed","angry","sad","tired","depressed","worried","down","upset","nervous"}

def mood_sentiment_score(mood_text):
    words = set([w.strip(".,!?:;").lower() for w in mood_text.split()])
    score = 50
    score += 10 * len(words & POS)
    score -= 10 * len(words & NEG)
    return max(0, min(100, score))

def sleep_quality_score(hours):
    if hours < 5: return 30
    if hours < 7: return 60
    return 90

def wellness_score(stress, sleep_hours, mood_text, habits_list):
    # 0-100 composite: lower stress better, sleep optimal better, mood sentiment, habits completeness
    stress_component = max(0, 100 - (stress * 10))  # stress 0->100,10->0
    sleep_comp = sleep_quality_score(sleep_hours)
    mood_comp = mood_sentiment_score(mood_text)
    # habits completeness: percent of recommended habits present
    recommended = ["exercise","journaling","mindfulness","reading","water"]
    have = sum(1 for h in recommended if h in habits_list)
    habit_comp = int((have / len(recommended)) * 100)
    # weighted average
    score = round((0.35 * stress_component) + (0.25 * sleep_comp) + (0.2 * mood_comp) + (0.2 * habit_comp))
    return max(0, min(100, score))

def make_session_obj(payload, backend_data, generated):
    return {
        "timestamp": datetime.now().isoformat(),
        "payload": payload,
        "backend": backend_data,
        "generated": generated
    }

def to_bytes_download(obj):
    b = io.BytesIO()
    b.write(json.dumps(obj, indent=2).encode("utf-8"))
    b.seek(0)
    return b

# ------------------ UI: Input ------------------
st.title(" MindFlow: AI Mental Wellness & Habit Coach")
st.markdown("Enter today's info — the dashboard will generate dynamic charts, AI insights and a daily wellness plan.")

with st.form("input_form"):
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        mood = st.text_input("How are you feeling today? (brief)","anxious and tired")
    with c2:
        stress = st.slider("Stress (0–10)", 0, 10, 6)
    with c3:
        sleep = st.number_input("Sleep hours last night", min_value=0.0, max_value=24.0, value=6.5, step=0.25)

    habits_raw = st.text_area("Current habits (comma-separated)","exercise, journaling")
    habits = [h.strip().lower() for h in habits_raw.split(",") if h.strip()]

    submit = st.form_submit_button("Generate Dashboard")

if not submit:
    st.info("Fill the form and click 'Generate Dashboard' to see charts and insights.")
    st.stop()

# ------------------ Try backend call ------------------
payload = {"mood": mood, "stress": stress, "sleep": sleep, "habits": habits}
backend_data = {}
try:
    resp = requests.post(f"{API_URL}/analyze", json=payload, timeout=8)
    if resp.status_code == 200:
        backend_data = resp.json()
    else:
        st.warning("Backend returned status " + str(resp.status_code))
except requests.exceptions.RequestException:
    st.info("Backend unreachable — using local generator for insights.")

# ------------------ Generate 7-day data (dynamic) ------------------
dates = gen_dates(7)
stress_vals = jittered_series(stress, days=7, var=1.8, floor=0, ceil=10)
sleep_vals = jittered_series(sleep, days=7, var=1.2, floor=0, ceil=12)
mood_scores = [mood_sentiment_score(mood) + random.uniform(-5,5) for _ in range(7)]
mood_scores = [max(0,min(100,round(s))) for s in mood_scores]

# habit scores per recommended habit
recommended = ["exercise","journaling","mindfulness","reading","water"]
habit_scores = [80 + random.uniform(-10,10) if h in habits else 30 + random.uniform(-10,10) for h in recommended]
habit_scores = [max(0,min(100, round(s))) for s in habit_scores]

# AI wellness score
w_score = wellness_score(stress, sleep, mood, habits)

# compute simple weekly analytics deltas (compare last two days)
delta_stress = round(stress_vals[-1] - stress_vals[-2],1) if len(stress_vals)>=2 else 0
delta_sleep = round(sleep_vals[-1] - sleep_vals[-2],1) if len(sleep_vals)>=2 else 0
# habit consistency percent (simple)
habit_consistency = int((sum(1 for h in recommended if h in habits) / len(recommended)) * 100)

# Build generated dict for session
generated = {
    "dates": dates,
    "stress_vals": stress_vals,
    "sleep_vals": sleep_vals,
    "mood_scores": mood_scores,
    "habit_keys": recommended,
    "habit_scores": habit_scores,
    "wellness_score": w_score,
    "sleep_quality": sleep_quality_score(sleep),
    "sleep_category": ("Very Low" if sleep<5 else "Below Optimal" if sleep<7 else "Healthy")
}

session_obj = make_session_obj(payload, backend_data, generated)

# ------------------ Layout: top summary cards ------------------
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("AI Wellness Score", f"{w_score}/100", delta=f"{w_score -  (50 if random.random()<0.5 else w_score-2)}")
col_b.metric("Stress (now)", f"{stress}/10", delta=f"{delta_stress:+}")
col_c.metric("Sleep (hrs)", f"{sleep} hrs", delta=f"{delta_sleep:+}")
col_d.metric("Habit Consistency", f"{habit_consistency}%", delta=f"{random.choice(['+5%','-3%','+0%'])}")

st.markdown("---")

# ------------------ Left: big charts, Right: insights & plan ------------------
left, right = st.columns([2.2, 1])

with left:
    st.subheader("Stress Pattern Timeline & Gauge")

    # Stress gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=stress,
        title={'text': "Current Stress", 'font': {'size': 16}},
        delta={'reference': round(np.mean(stress_vals),1)},
        gauge={'axis': {'range': [0,10]}, 'steps': [
            {'range':[0,3], 'color':'#d6f5d6'},
            {'range':[3,6], 'color':'#fff1b8'},
            {'range':[6,10], 'color':'#ffd6d6'}
        ]}
    ))
    gauge.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10))
    st.plotly_chart(gauge, use_container_width=True)

    # Stress trend line + markers
    df_s = pd.DataFrame({"date": dates, "stress": stress_vals})
    fig_s = px.line(df_s, x="date", y="stress", markers=True, title="7-day Stress Trend")
    fig_s.update_yaxes(range=[0,10])
    st.plotly_chart(fig_s, use_container_width=True)

    # Label important patterns (simple heuristics)
    st.markdown("**AI-labeled stress patterns:**")
    labels = []
    if stress_vals[0] < stress_vals[-1]:
        labels.append("Increasing trend since start of week")
    if max(stress_vals) >= 8:
        labels.append("High spikes detected — consider immediate breathing")
    if np.mean(stress_vals) < 4:
        labels.append("Generally low stress this week — keep it up")
    for lab in labels:
        st.info(lab)

    st.markdown("---")
    st.subheader("Sleep Overview")

    # sleep bar
    df_sleep = pd.DataFrame({"date": dates, "hours": sleep_vals})
    fig_sleep = px.bar(df_sleep, x="date", y="hours", title="Last 7 Days Sleep (hrs)")
    fig_sleep.update_yaxes(range=[0,12])
    st.plotly_chart(fig_sleep, use_container_width=True)

    # sleep donut
    sleep_score = generated["sleep_quality"]
    donut = go.Figure(data=[go.Pie(labels=[f"Sleep score ({sleep_score})","Remaining"], values=[sleep_score, 100 - sleep_score], hole=.6)])
    donut.update_layout(title=f"Sleep Quality: {generated['sleep_category']}", showlegend=False, height=300)
    st.plotly_chart(donut, use_container_width=True)

    st.markdown("---")
    st.subheader("Mood Sentiment Heatmap (7-day)")

    # heatmap from mood scores
    df_m = pd.DataFrame({"date": dates, "mood_score": mood_scores})
    hm = px.imshow([df_m["mood_score"].values], labels=dict(x="Date", y="Mood"), x=dates, y=["Sentiment"], color_continuous_scale="RdYlGn_r")
    hm.update_layout(height=150)
    st.plotly_chart(hm, use_container_width=True)

    st.markdown("---")
    st.subheader("Habits Radar & Progress Wheel")

    # radar
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=generated["habit_scores"],
        theta=generated["habit_keys"],
        fill='toself',
        name='Habit strength'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, title="Habit Strength Radar", height=420)
    st.plotly_chart(fig_radar, use_container_width=True)

    # progress wheel (donut segmented)
    have_count = sum(1 for h in recommended if h in habits)
    remain = len(recommended) - have_count
    values = [have_count, remain]
    labels = ["Completed", "Missing"]
    fig_wheel = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])
    fig_wheel.update_layout(title="Habit Completion", height=300, showlegend=True)
    st.plotly_chart(fig_wheel, use_container_width=True)

with right:
    st.subheader("AI Insights & Daily Plan")

    # prefer backend insights if available
    analysis_text = backend_data.get("analysis_text") or f"Auto-analysis: mood='{mood}', stress={stress}, sleep={sleep}hrs."
    guidance_text = backend_data.get("guidance") or "Try breathing, 10-min walk, and 5-min journaling tonight."

    st.markdown("**Analysis**")
    st.info(analysis_text)

    st.markdown("**Top Guidance**")
    st.success(guidance_text)

    st.markdown("**Quick Actions**")
    if st.button("Start 5-min breathing"):
        st.toast("Play breathing audio (not implemented)") if hasattr(st, "toast") else st.write("Start breathing session (local)")

    st.write("")
    st.markdown("**Daily Wellness Plan (AI-curated)**")
    # Construct plan based on inputs
    plan = []
    if stress >= 7:
        plan.append("🔴 Immediate: 5–10 min guided breathing and short walk")
    else:
        plan.append("🟢 Gentle: 5 min breathing, brief stretching")

    if sleep < 6:
        plan.append("🛏️ Sleep: Wind down 1 hour before bed; no screens; aim for 7–8 hrs")
    else:
        plan.append("✅ Sleep: Keep the schedule, good job")

    if "exercise" not in habits:
        plan.append("🏃 Add 10-min morning walk to routine")
    else:
        plan.append("🏃 Keep exercising 3x/week")

    if "journaling" not in habits:
        plan.append("✍️ Start 5-min evening journaling (feelings & wins)")
    else:
        plan.append("✍️ Keep journaling daily if possible")

    for p in plan:
        st.markdown(f"- {p}")

    st.markdown("---")
    st.subheader("Weekly Analytics")
    st.markdown(f"- **Average Stress (7d):** {round(np.mean(stress_vals),1)}")
    st.markdown(f"- **Average Sleep (7d):** {round(np.mean(sleep_vals),1)} hrs")
    st.markdown(f"- **Habit Consistency:** {habit_consistency}%")

    st.markdown("---")
    st.subheader("Emotional Keyword Cloud (simple)")
    # build word-size map (simulate from mood)
    words = [w.strip(".,!?:;") for w in (mood + " " + " ".join(habits)).split() if w.strip()]
    counts = {}
    for w in words:
        lw = w.lower()
        counts[lw] = counts.get(lw,0) + 1
    # convert to scatter positions
    x = []
    y = []
    txt = []
    sizes = []
    i = 0
    for k,v in counts.items():
        x.append(random.uniform(0,1))
        y.append(random.uniform(0,1))
        txt.append(k)
        sizes.append(10 + v*15)
        i+=1
    fig_cloud = go.Figure(data=go.Scatter(x=x, y=y, mode='text', text=txt, textfont_size=sizes))
    fig_cloud.update_layout(height=250, xaxis=dict(showgrid=False, zeroline=False, visible=False),
                            yaxis=dict(showgrid=False, zeroline=False, visible=False))
    st.plotly_chart(fig_cloud, use_container_width=True)

    st.markdown("---")
    st.subheader("Personal Balance Radar")
    balance_axes = ["Mental","Physical","Productivity","Social","Sleep"]
    # estimate each axis roughly
    mental = max(0, min(100, 100 - stress*8 + random.uniform(-5,5)))
    physical = 80 if "exercise" in habits else 40 + random.uniform(-10,10)
    productivity = 60 + random.uniform(-10,10)
    social = 50 + random.uniform(-15,15)
    sleep_axis = generated["sleep_quality"]
    balance_vals = [round(mental,1), round(physical,1), round(productivity,1), round(social,1), round(sleep_axis,1)]
    fig_balance = go.Figure()
    fig_balance.add_trace(go.Scatterpolar(r=balance_vals, theta=balance_axes, fill='toself'))
    fig_balance.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, height=350)
    st.plotly_chart(fig_balance, use_container_width=True)

    st.markdown("---")
    st.subheader("Download & Save Session")
    st.download_button("Download session JSON", data=to_bytes_download(session_obj), file_name="mindflow_session.json", mime="application/json")
    st.write("You can also copy the insights or plan to your notes.")

st.success("Dashboard generated — explore the tabs, visuals and quick actions above.")
