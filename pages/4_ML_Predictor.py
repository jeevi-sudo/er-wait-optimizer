import streamlit as st
import pandas as pd
import sqlite3
import pickle
import plotly.express as px

st.set_page_config(
    page_title="ML Predictor — ER Optimizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("🏥 ER Optimizer")
    st.caption("Pragyan AI Hackathon")
    st.divider()
    st.markdown("**📅 Data Period**")
    st.info("April 2023 – October 2024\n\n18 months of ER records")
    st.divider()
    st.markdown("**📊 Quick Stats**")
    st.metric("Total Patients", "9,216")
    st.metric("Avg Wait Time", "35.3 mins")
    st.metric("Critical Cases/Day", "1.2")
    st.metric("Shortage Slots", "137")
    st.divider()
    st.caption("Use the menu above to navigate pages")

@st.cache_data
def load_data():
    conn = sqlite3.connect('er_admissions.db')
    df = pd.read_sql_query("SELECT * FROM er_admissions", conn)
    conn.close()
    return df

@st.cache_resource
def load_models():
    lr = pickle.load(open('wait_model.pkl', 'rb'))
    rf = pickle.load(open('risk_model.pkl', 'rb'))
    return lr, rf

df = load_data()
lr_model, rf_model = load_models()
AVG_WAIT = 35.3

st.title("🤖 ML Predictor — Predict Wait Time For Any Scenario")
st.markdown("**Model:** Linear Regression + Risk Classifier | **Trained on:** 9,216 patient records | **Period:** April 2023 – October 2024")
st.divider()

# ── MODEL INFO ─────────────────────────────────────────────────────
st.markdown("### 🧠 About The Model")
st.caption("How our ML model works and what it was trained on")

m1, m2, m3, m4 = st.columns(4)
m1.info("**Model Type**\n\nLinear Regression\n\nPredicts wait time\nin minutes")
m2.info("**Training Data**\n\n9,216 patient\nrecords\n\nApr 2023 – Oct 2024")
m3.info("**Input Features**\n\nHour of day\nDay of week\nTriage score\nPatient age")
m4.info("**Output**\n\nPredicted wait\ntime (mins)\n\n+ HIGH/LOW\nrisk label")

st.divider()

# ── PREDICTOR ──────────────────────────────────────────────────────
st.markdown("### 🔮 Try The Predictor — Select Any Scenario")
st.caption("Select a specific hour, day, triage severity, and patient age to predict expected wait time and risk level")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    pred_hour = st.selectbox(
        "🕐 Hour of Day",
        list(range(24)),
        format_func=lambda x: f"{x}:00 {'AM' if x < 12 else 'PM'} {'(Midnight)' if x==0 else '(Noon)' if x==12 else ''}",
        index=22
    )
with col_m2:
    pred_day = st.selectbox(
        "📅 Day of Week",
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
        index=4
    )
    day_map = {'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,
               'Friday':4,'Saturday':5,'Sunday':6}
    pred_day_num = day_map[pred_day]
with col_m3:
    pred_triage = st.selectbox(
        "⚠️ Triage Severity",
        [1,2,3,4,5],
        format_func=lambda x: {
            1:'Score 1 — Life-Threatening',
            2:'Score 2 — Very Urgent',
            3:'Score 3 — Urgent',
            4:'Score 4 — Minor',
            5:'Score 5 — Non-Urgent'
        }[x]
    )
with col_m4:
    pred_age = st.slider("👤 Patient Age", 1, 100, 45)

sample = pd.DataFrame(
    [[pred_hour, pred_day_num, pred_triage, pred_age]],
    columns=['Hour_Of_Day','Day_Num','Triage_Score','Age']
)
pred_wait = max(0, lr_model.predict(sample)[0])
pred_risk = rf_model.predict(sample)[0]
diff      = pred_wait - AVG_WAIT

st.divider()
st.markdown("### 📊 Prediction Result")
st.caption(f"Scenario: {pred_day} at {pred_hour}:00 {'AM' if pred_hour < 12 else 'PM'} · Triage Score {pred_triage} · Age {pred_age}")

r1, r2, r3, r4 = st.columns(4)
r1.metric(
    "⏱️ Predicted Wait Time",
    f"{pred_wait:.1f} mins",
    help="Predicted time from check-in to doctor assignment for this scenario"
)
r2.metric(
    "📊 vs 18-Month Average",
    f"{pred_wait:.1f} mins",
    delta=f"{diff:+.1f} mins vs avg of 35.3 mins",
    delta_color="inverse"
)
r3.metric(
    "⚠️ Triage Severity",
    f"Score {pred_triage}",
    help={1:'Life-Threatening',2:'Very Urgent',3:'Urgent',4:'Minor',5:'Non-Urgent'}[pred_triage]
)
r4.metric(
    "🔴 Risk Level",
    "HIGH RISK" if pred_risk == 1 else "LOW RISK",
    help="HIGH = wait above 18-month average | LOW = wait within acceptable range"
)

if pred_risk == 1:
    st.error(f"🔴 **HIGH RISK** — {pred_day} at {pred_hour}:00 {'AM' if pred_hour < 12 else 'PM'} with a Triage Score {pred_triage} patient aged {pred_age} is predicted to wait **{pred_wait:.1f} minutes** — **{abs(diff):.1f} mins ABOVE** the 18-month average of 35.3 mins. Immediate staffing attention recommended.")
else:
    st.success(f"🟢 **LOW RISK** — {pred_day} at {pred_hour}:00 {'AM' if pred_hour < 12 else 'PM'} with a Triage Score {pred_triage} patient aged {pred_age} is predicted to wait **{pred_wait:.1f} minutes** — **{abs(diff):.1f} mins {'ABOVE' if diff > 0 else 'BELOW'}** the 18-month average of 35.3 mins.")

st.divider()

# ── HOURLY PREDICTION CHART ────────────────────────────────────────
st.markdown("### 📈 Predicted Wait Time — All Hours of the Day")
st.caption(f"Showing predicted wait time for every hour on {pred_day} · Triage Score {pred_triage} · Age {pred_age} · Based on ML model trained on 9,216 records")

hours = list(range(24))
predictions = []
for h in hours:
    s = pd.DataFrame([[h, pred_day_num, pred_triage, pred_age]],
                     columns=['Hour_Of_Day','Day_Num','Triage_Score','Age'])
    predictions.append(max(0, lr_model.predict(s)[0]))

pred_df = pd.DataFrame({
    'Hour': [f"{h}:00" for h in hours],
    'Predicted_Wait': predictions,
    'Hour_Num': hours
})

fig = px.line(
    pred_df, x='Hour', y='Predicted_Wait',
    markers=True,
    title=f"Predicted Wait Time for Every Hour — {pred_day} · Triage Score {pred_triage} · Age {pred_age}",
    labels={'Predicted_Wait': 'Predicted Wait (mins)', 'Hour': 'Hour of Day'}
)
fig.add_hline(
    y=AVG_WAIT, line_dash="dash",
    line_color="red", line_width=2,
    annotation_text="18-month avg: 35.3 mins",
    annotation_position="top right"
)
fig.add_scatter(
    x=[f"{pred_hour}:00"],
    y=[pred_wait],
    mode='markers',
    marker=dict(size=14, color='red', symbol='star'),
    name=f'Your scenario ({pred_hour}:00)',
    hovertemplate=f'Selected: {pred_hour}:00<br>Predicted: {pred_wait:.1f} mins<extra></extra>'
)
fig.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    height=400,
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
    margin=dict(t=60, b=40)
)
st.plotly_chart(fig, use_container_width=True)
st.info("📌 Red dashed line = 18-month average (35.3 mins). Hours above the line = predicted to exceed average wait time. Red star = your selected scenario.")

st.divider()
st.caption("🤖 ML Predictor · ER Wait Time Optimizer · Apr 2023 – Oct 2024 · 9,216 records · Linear Regression + Risk Classifier")