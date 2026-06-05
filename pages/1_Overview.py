import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Overview — ER Optimizer",
    page_icon="📊",
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
    df['Check_In_Time'] = pd.to_datetime(df['Check_In_Time'])
    return df

df = load_data()
MONTHS = 18

st.title("📊 Overview — 18 Months of ER Data")
st.markdown("**Data Period:** April 2023 – October 2024 | **Total Patients:** 9,216 | **Source:** Kaggle Hospital Emergency Dataset")
st.divider()

# ── STATS ──────────────────────────────────────────────────────────
st.markdown("### 📈 Patient Volume — 18-Month Summary")
st.caption("All averages calculated across 18 months (April 2023 – October 2024)")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🏥 Total Patients", "9,216",
    help="Total ER visits — Apr 2023 to Oct 2024")
c2.metric("📆 Per Month (avg)", "512",
    help="Average patients per calendar month over 18 months")
c3.metric("📅 Per Week (avg)", "128",
    help="Average patients per week over 18 months")
c4.metric("🗓️ Per Day (avg)", "17.1",
    help="Average patients per day over 18 months")
c5.metric("🚨 Critical Total", "624",
    help="Triage Score 1 (life-threatening) — total over 18 months = 34.7/month = 1.2/day")

st.divider()

# ── MONTHLY TREND ──────────────────────────────────────────────────
st.markdown("### 📅 Monthly Patient Volume & Average Wait Time")
st.caption("Each bar = total patients that calendar month | Red line = avg wait time that month | April 2023 – October 2024")

df['Month'] = df['Check_In_Time'].dt.to_period('M').astype(str)
monthly = df.groupby('Month').agg(
    Avg_Wait=('Wait_Minutes', 'mean'),
    Patient_Count=('Patient_ID', 'count')
).reset_index()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly['Month'],
    y=monthly['Patient_Count'],
    name='Total Patients That Month',
    marker_color='#93c5fd',
    yaxis='y2',
    hovertemplate='<b>%{x}</b><br>Patients that month: %{y}<extra></extra>'
))
fig.add_trace(go.Scatter(
    x=monthly['Month'],
    y=monthly['Avg_Wait'].round(1),
    name='Avg Wait Time (mins)',
    line=dict(color='#ef4444', width=3),
    mode='lines+markers',
    marker=dict(size=7),
    hovertemplate='<b>%{x}</b><br>Avg wait that month: %{y} mins<extra></extra>'
))
fig.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(title='Month (Apr 2023 – Oct 2024)', showgrid=False),
    yaxis=dict(title='Avg Wait Time (mins)', side='left',
               showgrid=True, gridcolor='#f3f4f6'),
    yaxis2=dict(title='Total Patients That Month',
                overlaying='y', side='right', showgrid=False),
    height=420, hovermode='x unified',
    legend=dict(x=0.01, y=0.99),
    margin=dict(t=20, b=40)
)
st.plotly_chart(fig, use_container_width=True)

st.info("📌 **How to read:** Blue bars = total patients that month (right axis). Red line = average wait time that month (left axis). When red line spikes while bars stay high = most strained month.")

st.divider()

# ── TRIAGE ─────────────────────────────────────────────────────────
st.markdown("### ⚠️ Patient Severity — Triage Score Analysis")
st.caption("Triage Score 1 = Life-threatening · Score 5 = Non-urgent | 18-month totals and daily averages across all 9,216 patients")

triage = df.groupby('Triage_Score').agg(
    Avg_Wait=('Wait_Minutes', 'mean'),
    Total=('Patient_ID', 'count')
).reset_index()
triage['Per_Day']   = (triage['Total'] / (MONTHS * 30)).round(1)
triage['Per_Month'] = (triage['Total'] / MONTHS).round(0).astype(int)
triage['Label'] = triage['Triage_Score'].map({
    1: 'Score 1\nLife-Threatening',
    2: 'Score 2\nVery Urgent',
    3: 'Score 3\nUrgent',
    4: 'Score 4\nMinor',
    5: 'Score 5\nNon-Urgent'
})

col1, col2 = st.columns(2, gap="large")
with col1:
    fig1 = px.bar(
        triage, x='Label', y='Avg_Wait',
        color='Avg_Wait',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Wait',
        title="Avg Wait Time per Severity Level — 18-month average across 9,216 patients",
        labels={'Avg_Wait': 'Avg Wait (mins)', 'Label': 'Triage Severity'}
    )
    fig1.update_traces(
        texttemplate='%{text:.1f} mins',
        textposition='outside'
    )
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=420, showlegend=False,
        margin=dict(t=60, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
                   title='Avg Wait Time (mins)')
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        triage, x='Label', y='Per_Day',
        color='Per_Day',
        color_continuous_scale='Blues',
        text='Per_Day',
        title="Avg Patients Per Day per Severity — 18-month average (9,216 patients ÷ 540 days)",
        labels={'Per_Day': 'Avg Patients/Day', 'Label': 'Triage Severity'}
    )
    fig2.update_traces(
        texttemplate='%{text} pts/day',
        textposition='outside'
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=420, showlegend=False,
        margin=dict(t=60, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
                   title='Avg Patients Per Day')
    )
    st.plotly_chart(fig2, use_container_width=True)

crit = triage[triage['Triage_Score'] == 1].iloc[0]
st.error(f"🚨 **Critical Finding:** Life-threatening patients (Triage Score 1) wait an average of **{crit['Avg_Wait']:.1f} minutes** before seeing a doctor. There are **{crit['Per_Day']} such patients every day** on average — **{int(crit['Per_Month'])} per month** — **624 total over 18 months.** Every minute of delay increases mortality risk.")

st.divider()

# ── WAIT DISTRIBUTION ──────────────────────────────────────────────
st.markdown("### 📊 Wait Time Distribution — All 9,216 Patients")
st.caption("How wait times are spread across all patients | Min: 10 mins · Avg: 35.3 mins · Max: 60 mins | April 2023 – October 2024")

fig3 = px.histogram(
    df, x='Wait_Minutes', nbins=30,
    color_discrete_sequence=['#60a5fa'],
    title="Distribution of Wait Times — All 9,216 patients · April 2023 – October 2024",
    labels={'Wait_Minutes': 'Wait Time (minutes)', 'count': 'Number of Patients'}
)
fig3.add_vline(
    x=35.3, line_dash="dash",
    line_color="#ef4444", line_width=2,
    annotation_text="18-month avg: 35.3 mins",
    annotation_position="top right",
    annotation_font_color="#ef4444"
)
fig3.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    height=380, showlegend=False,
    margin=dict(t=50, b=20),
    xaxis=dict(showgrid=False, title='Wait Time (minutes)'),
    yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
               title='Number of Patients')
)
st.plotly_chart(fig3, use_container_width=True)
st.info("📌 **How to read:** Each bar = number of patients who waited that long. Red dashed line = 18-month average of 35.3 mins. Patients to the RIGHT of the line waited longer than average — these are the cases of concern.")

st.divider()
st.caption("📊 Overview · ER Wait Time Optimizer · Kaggle Hospital Emergency Dataset · Apr 2023 – Oct 2024 · 9,216 patient records")