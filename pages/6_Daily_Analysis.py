import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Daily Analysis — ER Optimizer",
    page_icon="📅",
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

st.title("📅 Daily Analysis — Day by Day Breakdown")
st.markdown("**Data Period:** April 2023 – October 2024 | **Total Patients:** 9,216 | **Total Days:** 548 days of ER data")
st.divider()

# ── DAILY AGGREGATION ──────────────────────────────────────────────
daily = df.groupby(df['Check_In_Time'].dt.date).agg(
    Total_Patients  =('Patient_ID',    'count'),
    Avg_Wait_Mins   =('Wait_Minutes',  'mean'),
    Max_Wait_Mins   =('Wait_Minutes',  'max'),
    Min_Wait_Mins   =('Wait_Minutes',  'min'),
    Critical_Cases  =('Triage_Score',  lambda x: (x==1).sum()),
    Peak_Hour       =('Hour_Of_Day',   lambda x: x.mode()[0])
).reset_index()

daily.columns = [
    'Date', 'Total Patients', 'Avg Wait (mins)',
    'Max Wait (mins)', 'Min Wait (mins)',
    'Critical Cases', 'Peak Hour'
]
daily['Date']          = pd.to_datetime(daily['Date'])
daily['Avg Wait (mins)'] = daily['Avg Wait (mins)'].round(1)
daily['Max Wait (mins)'] = daily['Max Wait (mins)'].round(1)
daily['Min Wait (mins)'] = daily['Min Wait (mins)'].round(1)
daily['Day of Week']   = daily['Date'].dt.day_name()
daily['Month']         = daily['Date'].dt.strftime('%B %Y')
daily['Peak Hour']     = daily['Peak Hour'].apply(
    lambda x: f"{x}:00 {'AM' if x < 12 else 'PM'}"
)

# ── KEY DAILY STATS ────────────────────────────────────────────────
st.markdown("### 📊 Daily Summary — Key Stats Across All 548 Days")
st.caption("April 2023 – October 2024 · Based on 9,216 patient records across 548 days")

worst_day  = daily.loc[daily['Avg Wait (mins)'].idxmax()]
best_day   = daily.loc[daily['Avg Wait (mins)'].idxmin()]
busiest    = daily.loc[daily['Total Patients'].idxmax()]
quietest   = daily.loc[daily['Total Patients'].idxmin()]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(
    "📊 Avg Patients/Day",
    "17.1",
    help="9,216 patients ÷ 548 days = 17.1 patients per day on average"
)
c2.metric(
    "📈 Busiest Day Ever",
    f"{int(busiest['Total Patients'])} patients",
    help=f"{busiest['Date'].strftime('%B %d, %Y')} — {busiest['Day of Week']}"
)
c3.metric(
    "📉 Quietest Day Ever",
    f"{int(quietest['Total Patients'])} patients",
    help=f"{quietest['Date'].strftime('%B %d, %Y')} — {quietest['Day of Week']}"
)
c4.metric(
    "🔴 Worst Day Avg Wait",
    f"{worst_day['Avg Wait (mins)']} mins",
    help=f"{worst_day['Date'].strftime('%B %d, %Y')} — {worst_day['Day of Week']}"
)
c5.metric(
    "🟢 Best Day Avg Wait",
    f"{best_day['Avg Wait (mins)']} mins",
    help=f"{best_day['Date'].strftime('%B %d, %Y')} — {best_day['Day of Week']}"
)

st.divider()

# ── SPECIFIC DAY CALLOUTS ──────────────────────────────────────────
st.markdown("### 🔍 Most Notable Days in 18 Months")
st.caption("Specific dates with the most significant findings")

col_a, col_b = st.columns(2, gap="large")
with col_a:
    st.error(f"""
    🚨 **Worst Day — {worst_day['Date'].strftime('%B %d, %Y')} ({worst_day['Day of Week']})**

    • Avg wait time: **{worst_day['Avg Wait (mins)']} minutes**
    • Total patients that day: **{int(worst_day['Total Patients'])}**
    • Max wait recorded: **{worst_day['Max Wait (mins)']} minutes**
    • Critical cases: **{int(worst_day['Critical Cases'])}**
    • Peak hour: **{worst_day['Peak Hour']}**
    """)
    st.error(f"""
    📈 **Busiest Day — {busiest['Date'].strftime('%B %d, %Y')} ({busiest['Day of Week']})**

    • Total patients: **{int(busiest['Total Patients'])}** (vs avg of 17.1/day)
    • Avg wait that day: **{busiest['Avg Wait (mins)']} minutes**
    • Max wait recorded: **{busiest['Max Wait (mins)']} minutes**
    • Critical cases: **{int(busiest['Critical Cases'])}**
    • Peak hour: **{busiest['Peak Hour']}**
    """)
with col_b:
    st.success(f"""
    ✅ **Best Day — {best_day['Date'].strftime('%B %d, %Y')} ({best_day['Day of Week']})**

    • Avg wait time: **{best_day['Avg Wait (mins)']} minutes**
    • Total patients that day: **{int(best_day['Total Patients'])}**
    • Max wait recorded: **{best_day['Max Wait (mins)']} minutes**
    • Critical cases: **{int(best_day['Critical Cases'])}**
    • Peak hour: **{best_day['Peak Hour']}**
    """)
    st.success(f"""
    📉 **Quietest Day — {quietest['Date'].strftime('%B %d, %Y')} ({quietest['Day of Week']})**

    • Total patients: **{int(quietest['Total Patients'])}** (vs avg of 17.1/day)
    • Avg wait that day: **{quietest['Avg Wait (mins)']} minutes**
    • Max wait recorded: **{quietest['Max Wait (mins)']} minutes**
    • Critical cases: **{int(quietest['Critical Cases'])}**
    • Peak hour: **{quietest['Peak Hour']}**
    """)

st.divider()

# ── DAILY TREND CHART ──────────────────────────────────────────────
st.markdown("### 📈 Daily Patient Volume — All 548 Days")
st.caption("Each point = one day · Red line = 18-month daily average of 17.1 patients · April 2023 – October 2024")

fig1 = px.line(
    daily, x='Date', y='Total Patients',
    title="Daily Patient Count — Every Day from April 2023 to October 2024",
    labels={'Total Patients': 'Patients That Day', 'Date': 'Date'},
    color_discrete_sequence=['#3b82f6']
)
fig1.add_hline(
    y=17.1, line_dash="dash",
    line_color="#ef4444", line_width=2,
    annotation_text="18-month daily avg: 17.1 patients",
    annotation_position="top right",
    annotation_font_color="#ef4444"
)
fig1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    height=380, margin=dict(t=50, b=40),
    xaxis=dict(showgrid=False, title='Date (Apr 2023 – Oct 2024)'),
    yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
               title='Total Patients That Day')
)
st.plotly_chart(fig1, use_container_width=True)
st.info("📌 Days above the red line had more patients than average. Clusters of high bars indicate surge periods that needed more staff.")

st.divider()

# ── DAILY WAIT TIME TREND ──────────────────────────────────────────
st.markdown("### ⏱️ Daily Average Wait Time — All 548 Days")
st.caption("Each point = avg wait time on that specific day · Red line = 18-month avg of 35.3 mins · April 2023 – October 2024")

fig2 = px.line(
    daily, x='Date', y='Avg Wait (mins)',
    title="Daily Average Wait Time — Every Day from April 2023 to October 2024",
    labels={'Avg Wait (mins)': 'Avg Wait That Day (mins)', 'Date': 'Date'},
    color_discrete_sequence=['#f59e0b']
)
fig2.add_hline(
    y=35.3, line_dash="dash",
    line_color="#ef4444", line_width=2,
    annotation_text="18-month avg: 35.3 mins",
    annotation_position="top right",
    annotation_font_color="#ef4444"
)
fig2.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    height=380, margin=dict(t=50, b=40),
    xaxis=dict(showgrid=False, title='Date (Apr 2023 – Oct 2024)'),
    yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
               title='Avg Wait Time (mins)')
)
st.plotly_chart(fig2, use_container_width=True)
st.info("📌 Days above the red line had longer-than-average waits. These are the days where staffing was most stretched.")

st.divider()

# ── WORST 10 DAYS ──────────────────────────────────────────────────
st.markdown("### 🚨 Top 10 Worst Days — Longest Average Wait Times")
st.caption("The 10 specific days with the longest average patient wait times | April 2023 – October 2024")

worst10 = daily.nlargest(10, 'Avg Wait (mins)')[
    ['Date','Day of Week','Month','Total Patients',
     'Avg Wait (mins)','Max Wait (mins)',
     'Critical Cases','Peak Hour']
].reset_index(drop=True)
worst10['Date'] = worst10['Date'].dt.strftime('%B %d, %Y')
worst10.index  += 1

st.dataframe(
    worst10.style.background_gradient(
        subset=['Avg Wait (mins)'], cmap='Reds'
    ).format({
        'Avg Wait (mins)': '{:.1f} mins',
        'Max Wait (mins)': '{:.1f} mins',
    }),
    use_container_width=True
)

st.divider()

# ── BEST 10 DAYS ───────────────────────────────────────────────────
st.markdown("### ✅ Top 10 Best Days — Shortest Average Wait Times")
st.caption("The 10 specific days with the shortest average patient wait times | April 2023 – October 2024")

best10 = daily.nsmallest(10, 'Avg Wait (mins)')[
    ['Date','Day of Week','Month','Total Patients',
     'Avg Wait (mins)','Max Wait (mins)',
     'Critical Cases','Peak Hour']
].reset_index(drop=True)
best10['Date'] = best10['Date'].dt.strftime('%B %d, %Y')
best10.index  += 1

st.dataframe(
    best10.style.background_gradient(
        subset=['Avg Wait (mins)'], cmap='Greens_r'
    ).format({
        'Avg Wait (mins)': '{:.1f} mins',
        'Max Wait (mins)': '{:.1f} mins',
    }),
    use_container_width=True
)

st.divider()

# ── FULL DAILY TABLE ───────────────────────────────────────────────
st.markdown("### 📋 Complete Daily Log — All 548 Days")
st.caption("Every single day from April 2023 to October 2024 | Sortable by any column")

show_daily = daily[[
    'Date','Day of Week','Month','Total Patients',
    'Avg Wait (mins)','Max Wait (mins)',
    'Min Wait (mins)','Critical Cases','Peak Hour'
]].copy()
show_daily['Date'] = show_daily['Date'].dt.strftime('%B %d, %Y')
show_daily = show_daily.reset_index(drop=True)
show_daily.index += 1

st.dataframe(
    show_daily.style.background_gradient(
        subset=['Avg Wait (mins)'], cmap='RdYlGn_r'
    ).format({
        'Avg Wait (mins)': '{:.1f} mins',
        'Max Wait (mins)': '{:.1f} mins',
        'Min Wait (mins)': '{:.1f} mins',
    }),
    use_container_width=True,
    height=400
)

st.divider()
st.caption("📅 Daily Analysis · ER Wait Time Optimizer · Apr 2023 – Oct 2024 · 9,216 records · 548 days")