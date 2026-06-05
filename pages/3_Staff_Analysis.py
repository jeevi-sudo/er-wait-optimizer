import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Staff Analysis — ER Optimizer",
    page_icon="👨‍⚕️",
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
    df   = pd.read_sql_query("SELECT * FROM er_admissions", conn)
    staff= pd.read_sql_query("SELECT * FROM staff_data", conn)
    conn.close()
    return df, staff

df, staff_df = load_data()
DAY_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

st.title("👨‍⚕️ Staff Analysis — Where Are The Gaps?")
st.markdown("**Data Period:** April 2023 – October 2024 | **Total Patients:** 9,216 | Staff counts modeled on published hospital shift patterns")
st.divider()

# ── SUMMARY METRICS ────────────────────────────────────────────────
st.markdown("### 📊 Staffing Summary — All Shifts")
st.caption("Staff shortage defined as: more than 8 patients per doctor in any given hour")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🔴 Critical Shortage Hours", "137",
    help="Hours where doctors handle >8 patients each — dangerously overwhelmed")
c2.metric("🟠 Understaffed Hours", "30",
    help="Hours where doctors handle 5–8 patients each — stretched thin")
c3.metric("🌙 Night Shift Avg Doctors", "1.6",
    help="Average doctors on duty midnight to 6AM — lowest of any shift")
c4.metric("🌅 Evening Shift Avg Doctors", "6.3",
    help="Average doctors on duty 2PM to 10PM — highest of any shift")
c5.metric("📊 Worst Ratio Found", "63 pts/doctor",
    help="Saturday 2AM — 1 doctor handling 63 patients in a single hour slot")

st.divider()

# ── PATIENTS VS DOCTORS ────────────────────────────────────────────
st.markdown("### ⚖️ Patient Volume vs Doctor Availability — By Hour of Day")
st.caption("Red bars = total patients over 18 months for that hour | Blue line = avg doctors on duty | Gap between them = staffing shortage | April 2023 – October 2024")

hourly = staff_df.groupby('Hour_Of_Day').agg(
    Avg_Doctors=('Doctor_Count','mean'),
    Total_Patients=('Total_Patients','sum'),
).reset_index()

fig_vs = go.Figure()
fig_vs.add_trace(go.Bar(
    x=hourly['Hour_Of_Day'],
    y=hourly['Total_Patients'],
    name='Total Patients (18 months)',
    marker_color='#fca5a5',
    yaxis='y',
    hovertemplate='Hour %{x}:00<br>Total patients over 18 months: %{y}<extra></extra>'
))
fig_vs.add_trace(go.Scatter(
    x=hourly['Hour_Of_Day'],
    y=hourly['Avg_Doctors'].round(1),
    name='Avg Doctors on Duty',
    marker_color='#3b82f6',
    mode='lines+markers',
    line=dict(width=3),
    marker=dict(size=8),
    yaxis='y2',
    hovertemplate='Hour %{x}:00<br>Avg doctors on duty: %{y}<extra></extra>'
))
fig_vs.update_layout(
    title="Total Patients (18 months) vs Avg Doctors on Duty — by Hour of Day | 0=Midnight · 12=Noon",
    plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(title='Hour of Day (0=Midnight · 6=6AM · 12=Noon · 18=6PM)',
               tickmode='linear', showgrid=False),
    yaxis=dict(title='Total Patients (18 months)', side='left',
               showgrid=True, gridcolor='#f3f4f6'),
    yaxis2=dict(title='Avg Doctors on Duty', overlaying='y',
                side='right', showgrid=False),
    height=440, hovermode='x unified',
    legend=dict(x=0.01, y=0.99),
    margin=dict(t=60, b=40)
)
st.plotly_chart(fig_vs, use_container_width=True)
st.warning("📌 **How to read:** Where red bars are TALL but the blue line is LOW = danger zone. These are the hours where patient volume far exceeds doctor availability.")

st.divider()

# ── DOCTOR COUNT HEATMAP ───────────────────────────────────────────
st.markdown("### 🗓️ Doctor Count Heatmap — By Hour & Day")
st.caption("Number of doctors available at each hour | Darker blue = more doctors | Based on standard hospital shift patterns")

doc_pivot = staff_df.pivot_table(
    index='Day_Of_Week',
    columns='Hour_Of_Day',
    values='Doctor_Count'
).reindex(DAY_ORDER)

fig_doc = px.imshow(
    doc_pivot,
    labels=dict(x="Hour of Day", y="Day of Week", color="Doctor Count"),
    color_continuous_scale="Blues",
    aspect="auto",
    title="Number of Doctors on Duty — by Hour & Day | Lighter = fewer doctors = more risk"
)
fig_doc.update_layout(height=420, margin=dict(t=50, b=20), paper_bgcolor='white')
fig_doc.update_xaxes(tickmode='linear', tick0=0, dtick=1)
st.plotly_chart(fig_doc, use_container_width=True)

st.divider()

# ── SHORTAGE HEATMAP ───────────────────────────────────────────────
st.markdown("### 🚨 Staffing Shortage Map — Patients Per Doctor")
st.caption("Higher number = more patients per doctor = more overloaded | 🔴 Red = critical overload | 🟢 Green = manageable | April 2023 – October 2024")

shortage_pivot = staff_df.pivot_table(
    index='Day_Of_Week',
    columns='Hour_Of_Day',
    values='Patients_Per_Doctor'
).reindex(DAY_ORDER)

fig_sh = px.imshow(
    shortage_pivot,
    labels=dict(x="Hour of Day", y="Day of Week",
                color="Patients Per Doctor"),
    color_continuous_scale="RdYlGn_r",
    aspect="auto",
    title="Patients Per Doctor — by Hour & Day | Higher = More Overloaded | Red = Critical Shortage"
)
fig_sh.update_layout(height=420, margin=dict(t=50, b=20), paper_bgcolor='white')
fig_sh.update_xaxes(tickmode='linear', tick0=0, dtick=1)
st.plotly_chart(fig_sh, use_container_width=True)

st.divider()

# ── TOP 5 WORST ────────────────────────────────────────────────────
st.markdown("### 🚨 Top 5 Most Critical Staffing Gaps Found")
st.caption("The specific hour-day combinations most urgently needing additional staff | April 2023 – October 2024")

worst5 = staff_df.nlargest(5, 'Patients_Per_Doctor')[
    ['Day_Of_Week','Hour_Of_Day','Doctor_Count',
     'Total_Patients','Patients_Per_Doctor']
].reset_index(drop=True)

for i, row in worst5.iterrows():
    ratio = row['Patients_Per_Doctor']
    if ratio > 20:
        status = "🔴 Critical Shortage"
    elif ratio > 10:
        status = "🟠 Understaffed"
    else:
        status = "🟡 Stretched"

    st.error(
        f"**#{i+1} — {row['Day_Of_Week']} at {int(row['Hour_Of_Day'])}:00** | "
        f"**{int(row['Doctor_Count'])} doctor(s)** on duty | "
        f"**{int(row['Total_Patients'])} total patients** over 18 months | "
        f"= **{row['Patients_Per_Doctor']:.1f} patients per doctor** | "
        f"Status: {status}"
    )

st.divider()

# ── SHIFT SUMMARY ──────────────────────────────────────────────────
st.markdown("### 📋 Staffing Summary by Shift — 18-Month Average")
st.caption("Average staffing levels and patient load per shift | Night = 12AM–6AM · Morning = 6AM–2PM · Evening = 2PM–10PM · Late Night = 10PM–12AM")

shift_df = staff_df.groupby('Shift').agg(
    Avg_Doctors=('Doctor_Count','mean'),
    Avg_Patients_Per_Hour=('Total_Patients','mean'),
    Patients_Per_Doctor=('Patients_Per_Doctor','mean'),
    Avg_Wait_Mins=('Avg_Wait','mean')
).round(1).reset_index()

shift_df.columns = [
    'Shift', 'Avg Doctors on Duty',
    'Avg Patients/Hour (18mo avg)',
    'Patients Per Doctor',
    'Avg Wait Time (mins)'
]

st.dataframe(
    shift_df.style.background_gradient(
        subset=['Patients Per Doctor'], cmap='RdYlGn_r'
    ).format({
        'Avg Doctors on Duty': '{:.1f}',
        'Avg Patients/Hour (18mo avg)': '{:.1f}',
        'Patients Per Doctor': '{:.1f}',
        'Avg Wait Time (mins)': '{:.1f}'
    }),
    use_container_width=True,
    hide_index=True
)

st.divider()
st.caption("👨‍⚕️ Staff Analysis · ER Wait Time Optimizer · Apr 2023 – Oct 2024 · 9,216 records")