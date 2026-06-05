import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(
    page_title="Heatmap — ER Optimizer",
    page_icon="🔥",
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

df = load_data()
DAY_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

st.title("🔥 Heatmap — When Is The ER Most Dangerous?")
st.markdown("**Data Period:** April 2023 – October 2024 | **Total Patients:** 9,216 | Each cell = 18-month average wait time for that specific hour and day")
st.divider()

# ── TOP STATS ──────────────────────────────────────────────────────
heatmap_df = df.groupby(
    ['Day_Of_Week','Day_Num','Hour_Of_Day']
)['Wait_Minutes'].mean().reset_index()

worst = heatmap_df.loc[heatmap_df['Wait_Minutes'].idxmax()]
best  = heatmap_df.loc[heatmap_df['Wait_Minutes'].idxmin()]
worst_hour_val = df.groupby('Hour_Of_Day')['Wait_Minutes'].mean().max()
worst_hour_num = df.groupby('Hour_Of_Day')['Wait_Minutes'].mean().idxmax()

st.markdown("### 📊 Key Wait Time Stats — 18-Month Summary")
st.caption("All figures are 18-month averages (April 2023 – October 2024) across 9,216 patients")

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "🔴 Worst Slot",
    f"{worst['Wait_Minutes']:.1f} mins",
    help=f"{worst['Day_Of_Week']} at {int(worst['Hour_Of_Day'])}:00 — 18-month average wait for this specific hour"
)
c2.metric(
    "🟢 Best Slot",
    f"{best['Wait_Minutes']:.1f} mins",
    help=f"{best['Day_Of_Week']} at {int(best['Hour_Of_Day'])}:00 — 18-month average wait for this specific hour"
)
c3.metric(
    "⏰ Worst Hour Overall",
    f"{worst_hour_val:.1f} mins",
    help=f"{worst_hour_num}:00 — averaged across all days over 18 months"
)
c4.metric(
    "📊 Overall Average",
    "35.3 mins",
    help="Average wait time across all 9,216 patients over 18 months"
)

st.divider()

# ── HEATMAP ────────────────────────────────────────────────────────
st.markdown("### 🗓️ Wait Time Heatmap — Hour of Day vs Day of Week")
st.caption("🔴 Red = long waits (danger zone) · 🟢 Green = short waits (safe) | Each cell = 18-month average wait time for that hour | 0 = Midnight · 12 = Noon · 23 = 11PM")

pivot = heatmap_df.pivot_table(
    index='Day_Of_Week',
    columns='Hour_Of_Day',
    values='Wait_Minutes'
).reindex(DAY_ORDER)

fig = px.imshow(
    pivot,
    labels=dict(
        x="Hour of Day (0=Midnight · 6=6AM · 12=Noon · 18=6PM · 23=11PM)",
        y="Day of Week",
        color="Avg Wait Time (mins) — 18-month average"
    ),
    color_continuous_scale="RdYlGn_r",
    aspect="auto",
    title="Average Patient Wait Time (mins) by Hour & Day | Each cell = 18-month average | Based on 9,216 patients | April 2023 – October 2024"
)
fig.update_layout(
    height=500,
    margin=dict(t=60, b=20),
    paper_bgcolor='white',
    font=dict(size=13)
)
fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
st.plotly_chart(fig, use_container_width=True)

col_w, col_b = st.columns(2, gap="large")
with col_w:
    st.error(f"🚨 **Worst Slot:** {worst['Day_Of_Week']} at {int(worst['Hour_Of_Day'])}:00 — Average wait of **{worst['Wait_Minutes']:.1f} minutes** — This is the 18-month average for this specific hour across all {worst['Day_Of_Week']}s in the dataset")
with col_b:
    st.success(f"✅ **Best Slot:** {best['Day_Of_Week']} at {int(best['Hour_Of_Day'])}:00 — Average wait of only **{best['Wait_Minutes']:.1f} minutes** — This is the 18-month average for this specific hour across all {best['Day_Of_Week']}s in the dataset")

st.divider()

# ── WORST HOURS + DAYS ─────────────────────────────────────────────
st.markdown("### 📈 Bottleneck Breakdown — Worst Hours & Days Ranked")
st.caption("18-month averages | April 2023 – October 2024 | All figures based on 9,216 patient records")

col_a, col_b = st.columns(2, gap="large")
with col_a:
    st.markdown("#### ⏰ Top 5 Worst Hours of the Day")
    st.caption("Avg wait time per hour · All 7 days combined · 18-month average")

    worst_h = df.groupby('Hour_Of_Day').agg(
        Avg_Wait=('Wait_Minutes','mean'),
        Total=('Patient_ID','count')
    ).reset_index()
    worst_h['Avg_Per_Day'] = (worst_h['Total'] / (18*30)).round(1)
    worst_h = worst_h.nlargest(5, 'Avg_Wait')
    worst_h['Hour_Label'] = worst_h['Hour_Of_Day'].apply(
        lambda x: f"{x}:00 ({'AM' if x < 12 else 'PM'})"
    )

    fig_h = px.bar(
        worst_h, x='Hour_Label', y='Avg_Wait',
        color='Avg_Wait',
        color_continuous_scale='Reds',
        text='Avg_Wait',
        title="Top 5 Hours — Longest Avg Wait | 18-month average across all days",
        labels={'Avg_Wait':'Avg Wait (mins)','Hour_Label':'Hour of Day'},
        hover_data={'Avg_Per_Day': True, 'Total': True}
    )
    fig_h.update_traces(
        texttemplate='%{text:.1f} mins',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Avg Wait: %{y:.1f} mins<br>Avg Patients/Day: %{customdata[0]}<br>Total Patients (18mo): %{customdata[1]}<extra></extra>'
    )
    fig_h.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=420, showlegend=False,
        margin=dict(t=60, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
                   range=[0, worst_h['Avg_Wait'].max()+5])
    )
    st.plotly_chart(fig_h, use_container_width=True)

    top = worst_h.iloc[0]
    st.error(f"🚨 **{top['Hour_Label']}** is the worst hour — **{top['Avg_Wait']:.1f} min** avg wait · **{top['Avg_Per_Day']} patients/day** on avg · **{int(top['Total'])} total patients** over 18 months")

with col_b:
    st.markdown("#### 📅 Wait Time by Day of Week")
    st.caption("Avg wait time per day · All 24 hours combined · 18-month average")

    by_day = df.groupby('Day_Of_Week').agg(
        Avg_Wait=('Wait_Minutes','mean'),
        Total=('Patient_ID','count')
    ).reset_index()
    by_day['Avg_Per_Day'] = (by_day['Total'] / (18*4)).round(1)
    by_day = by_day.set_index('Day_Of_Week').reindex(DAY_ORDER).reset_index()
    by_day.columns = ['Day','Avg_Wait','Total','Avg_Per_Day']

    fig_d = px.bar(
        by_day, x='Day', y='Avg_Wait',
        color='Avg_Wait',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Wait',
        title="Avg Wait Time by Day | 18-month average · All hours combined",
        labels={'Avg_Wait':'Avg Wait (mins)','Day':'Day of Week'},
        hover_data={'Avg_Per_Day': True, 'Total': True}
    )
    fig_d.update_traces(
        texttemplate='%{text:.1f} mins',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Avg Wait: %{y:.1f} mins<br>Avg Patients/Day: %{customdata[0]}<br>Total Patients (18mo): %{customdata[1]}<extra></extra>'
    )
    fig_d.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=420, showlegend=False,
        margin=dict(t=60, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
                   range=[0, by_day['Avg_Wait'].max()+5])
    )
    st.plotly_chart(fig_d, use_container_width=True)

    wd = by_day.loc[by_day['Avg_Wait'].idxmax()]
    st.error(f"🚨 **{wd['Day']}** has the longest waits — **{wd['Avg_Wait']:.1f} min** avg · **{wd['Avg_Per_Day']} patients/day** on avg · **{int(wd['Total'])} total patients** over 18 months")

st.divider()
st.caption("🔥 Heatmap Analysis · ER Wait Time Optimizer · Apr 2023 – Oct 2024 · 9,216 records")