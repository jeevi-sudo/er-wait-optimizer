import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Staff Simulator — ER Optimizer",
    page_icon="🎛️",
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

AVG_WAIT    = 35.3
AVG_PER_DAY = 17.1
AVG_PER_WEEK= 128

st.title("🎛️ Staff Simulator — What If We Add More Doctors?")
st.markdown("**Based on:** 18-month average wait of 35.3 mins across 9,216 patients | **Model:** Queuing theory — wait reduces proportionally as staff increases")
st.divider()

# ── HOW IT WORKS ───────────────────────────────────────────────────
st.markdown("### 📖 How The Simulator Works")
st.caption("The logic behind the staff simulation")

st.info("""
**Queuing Theory Model:** Wait time reduces proportionally when more doctors are added.

Formula: `New Wait Time = Current Avg Wait × (Current Staff ÷ Total Staff)`

**Based on real data:**
- 18-month average wait: **35.3 mins** across 9,216 patients
- Average patients per day: **17.1** (Apr 2023 – Oct 2024)
- Average patients per week: **128** (18-month average)
""")

st.divider()

# ── SIMULATOR ──────────────────────────────────────────────────────
st.markdown("### 🎛️ Adjust Staff Levels — See Impact in Real Time")
st.caption("Move the sliders to simulate different staffing scenarios based on 18-month ER data")

col_sl, col_res = st.columns([1, 2], gap="large")

with col_sl:
    st.markdown("**Current Staffing**")
    current_staff = st.slider(
        "Doctors currently on this shift",
        min_value=1, max_value=20, value=5,
        help="How many doctors are currently on duty for this shift"
    )

    st.markdown("**Add Extra Doctors**")
    added_staff = st.slider(
        "Additional doctors to add",
        min_value=0, max_value=15, value=2,
        help="How many extra doctors you want to simulate adding"
    )

    total_staff  = current_staff + added_staff
    new_wait     = round(AVG_WAIT * (current_staff / total_staff), 1)
    saved_mins   = round(AVG_WAIT - new_wait, 1)
    saved_hrs_wk = round(saved_mins * AVG_PER_WEEK / 60, 1)
    saved_hrs_mo = round(saved_mins * AVG_PER_DAY * 30 / 60, 1)
    pct_better   = round((saved_mins / AVG_WAIT) * 100, 1)

    st.divider()
    st.markdown("**📊 Simulation Results**")
    st.metric(
        "👨‍⚕️ Total Doctors on Shift",
        f"{total_staff}",
        help=f"{current_staff} current + {added_staff} added"
    )
    st.metric(
        "⏱️ New Avg Wait Time",
        f"{new_wait} mins",
        delta=f"-{saved_mins} mins (was {AVG_WAIT} mins)",
        delta_color="inverse",
        help="Based on 18-month average of 35.3 mins across 9,216 patients"
    )
    st.metric(
        "📉 Wait Time Reduction",
        f"{pct_better}%",
        help=f"From {AVG_WAIT} mins down to {new_wait} mins"
    )
    st.metric(
        "💰 Patient-Hours Saved/Week",
        f"{saved_hrs_wk} hrs",
        help=f"Based on avg {AVG_PER_WEEK} patients/week over 18 months"
    )
    st.metric(
        "📅 Patient-Hours Saved/Month",
        f"{saved_hrs_mo} hrs",
        help=f"Based on avg {AVG_PER_DAY} patients/day × 30 days"
    )

with col_res:
    # Before vs After chart
    sim_df = pd.DataFrame({
        'Scenario': [
            f'Current\n({current_staff} doctors)',
            f'With {added_staff} Extra\n({total_staff} doctors)'
        ],
        'Avg Wait (mins)': [AVG_WAIT, new_wait],
        'Color': ['Current', 'Improved']
    })

    fig = px.bar(
        sim_df, x='Scenario', y='Avg Wait (mins)',
        color='Color',
        color_discrete_map={
            'Current' : '#ef4444',
            'Improved': '#22c55e'
        },
        text='Avg Wait (mins)',
        title=f"Wait Time Before vs After Adding {added_staff} Doctor(s) | Based on 18-month avg of 35.3 mins across 9,216 patients",
    )
    fig.update_traces(
        texttemplate='%{text} mins',
        textposition='outside',
        width=0.4
    )
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=420, showlegend=False,
        margin=dict(t=60, b=20),
        xaxis=dict(showgrid=False, title=''),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6',
                   range=[0, AVG_WAIT + 10],
                   title='Avg Wait Time (mins)')
    )
    st.plotly_chart(fig, use_container_width=True)

    if added_staff > 0:
        st.success(f"✅ Adding **{added_staff} doctor(s)** to a shift of {current_staff} reduces average wait from **{AVG_WAIT} mins → {new_wait} mins** — saving **{saved_mins} mins per patient** — **{saved_hrs_wk} patient-hours every week** — **{saved_hrs_mo} patient-hours every month**")
    else:
        st.info("👆 Move the 'Add Extra Doctors' slider above to simulate the impact of adding staff")

st.divider()

# ── SHIFT SCENARIOS ────────────────────────────────────────────────
st.markdown("### 📋 Pre-Built Scenarios — Most Critical Shifts")
st.caption("Based on real shortage data found in 18 months of ER records | These are the shifts that need attention most urgently")

scenarios = [
    {"shift": "Saturday 2AM (worst slot)", "current": 1, "patients": 63,
     "recommended": 3, "reason": "1 doctor handling 63 patients — most critical gap found"},
    {"shift": "Saturday 1AM", "current": 1, "patients": 60,
     "recommended": 3, "reason": "1 doctor handling 60 patients — second worst slot"},
    {"shift": "Monday Midnight", "current": 2, "patients": 66,
     "recommended": 4, "reason": "2 doctors handling 66 patients — 33 per doctor"},
    {"shift": "Night Shift (12AM–6AM avg)", "current": 2, "patients": 55,
     "recommended": 4, "reason": "Avg 1.6 doctors across all nights — most vulnerable shift"},
]

for s in scenarios:
    new_w = round(AVG_WAIT * (s['current'] / s['recommended']), 1)
    saved = round(AVG_WAIT - new_w, 1)
    with st.expander(f"📍 {s['shift']} — Currently {s['current']} doctor(s) for ~{s['patients']} patients"):
        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Current Doctors", s['current'])
        ec2.metric("Recommended Doctors", s['recommended'])
        ec3.metric("Wait Time Reduction", f"-{saved} mins",
                   delta=f"{AVG_WAIT} → {new_w} mins", delta_color="inverse")
        st.error(f"⚠️ **Why critical:** {s['reason']}")
        st.success(f"✅ **Fix:** Add {s['recommended'] - s['current']} doctor(s) → reduces avg wait from {AVG_WAIT} to {new_w} mins — saving {saved} mins per patient")

st.divider()
st.caption("🎛️ Staff Simulator · ER Wait Time Optimizer · Based on 18-month avg of 35.3 mins · 9,216 patient records · Apr 2023 – Oct 2024")