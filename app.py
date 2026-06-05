import streamlit as st

st.set_page_config(
    page_title="ER Wait Time Optimizer",
    page_icon="🏥",
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
    st.metric("Total Patients", "9,216", help="Over 18 months")
    st.metric("Avg Wait Time", "35.3 mins", help="Check-in to doctor")
    st.metric("Critical Cases/Day", "1.2", help="Triage Score 1 avg per day")
    st.metric("Shortage Slots", "137", help="Critically understaffed hours")
    st.divider()
    st.caption("Use the menu above to navigate pages")

st.title("🏥 ER Wait Time Optimizer")
st.markdown("### AI-Powered Emergency Room Bottleneck Detection & Staff Simulator")
st.info("📅 **Data Period:** April 2023 – October 2024 (18 months) | 👥 **Total Records:** 9,216 patients | 📦 **Source:** Kaggle Hospital Emergency Dataset")

st.divider()

# ── THE PROBLEM ────────────────────────────────────────────────────
col_p, col_s = st.columns(2, gap="large")
with col_p:
    st.error("""
    **❗ The Problem**

    Emergency Rooms face unpredictable surges.
    Without data, hospitals react to crises
    instead of preventing them.

    Our data shows **1.2 life-critical patients
    arrive every single day** — they cannot wait.
    Yet staffing decisions are made without
    knowing when and where pressure builds.
    """)
with col_s:
    st.success("""
    **✅ What We Built**

    We analysed **9,216 ER visits over 18 months**
    using SQL, Python, and Machine Learning to map
    exactly when bottlenecks occur.

    Our dashboard gives hospital managers a clear
    picture of staffing gaps — and an interactive
    simulator to explore solutions **before
    decisions need to be made.**
    """)

st.divider()

# ── KEY STATS ──────────────────────────────────────────────────────
st.markdown("## 📊 18-Month Summary — April 2023 to October 2024")
st.caption("All figures calculated from 9,216 real patient records over 18 months")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(
    label="🏥 Total ER Visits",
    value="9,216",
    help="Total patients who visited ER — April 2023 to October 2024 (18 months)"
)
c2.metric(
    label="📆 Avg Visits / Month",
    value="512",
    help="Average number of patients per calendar month over 18 months"
)
c3.metric(
    label="📅 Avg Visits / Day",
    value="17.1",
    help="Average patients per day over 18 months (9,216 ÷ 540 days)"
)
c4.metric(
    label="⏱️ Avg Wait Time",
    value="35.3 mins",
    help="Average time from patient check-in to doctor assignment — 18-month average"
)
c5.metric(
    label="🚨 Critical Cases / Day",
    value="1.2",
    help="Triage Score 1 (life-threatening) patients per day on average. 624 total over 18 months"
)

st.divider()

# ── KEY FINDINGS ───────────────────────────────────────────────────
st.markdown("## 🔍 Key Findings From 18 Months of Data")
st.caption("Discovered through SQL analysis and ML on 9,216 patient records")

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.warning("""
    **🌙 Night Shift Crisis**

    Midnight – 6AM:
    Only **1–2 doctors** on duty

    Handling up to **39 patients
    per doctor** per shift

    Most dangerous staffing gap
    """)
with f2:
    st.warning("""
    **📅 Saturday Night**

    Saturday 1–2AM is the
    single worst slot found:

    **1 doctor handling
    60–63 patients**

    Immediately actionable gap
    """)
with f3:
    st.warning("""
    **⏰ 3AM Danger Zone**

    3:00 AM averages
    **37.2 minute wait**

    Highest of any hour
    across 18 months

    Staffing lowest when
    pressure is highest
    """)
with f4:
    st.success("""
    **🤖 ML Prediction**

    Model trained on
    all 9,216 records

    Predicts wait time for
    any hour + day +
    age + severity

    Proactive staffing
    """)

st.divider()

# ── NAVIGATE ───────────────────────────────────────────────────────
st.markdown("## 🗺️ Dashboard Pages")
st.caption("Click any page in the sidebar to explore")

n1, n2, n3, n4, n5 = st.columns(5)
with n1:
    st.info("""
    **📊 Page 1**
    **Overview**

    Monthly trends
    Triage breakdown
    Wait distribution

    *512 patients/month*
    """)
with n2:
    st.info("""
    **🔥 Page 2**
    **Heatmap**

    Hour vs Day grid
    Danger zones
    Best/worst slots

    *Worst: 3AM 37.2 mins*
    """)
with n3:
    st.info("""
    **👨‍⚕️ Page 3**
    **Staff Analysis**

    Doctor counts
    Patient vs staff
    Shortage map

    *137 critical slots*
    """)
with n4:
    st.info("""
    **🎛️ Page 4**
    **Simulator**

    Add doctors
    See wait drop
    Hours saved/week

    *Interactive slider*
    """)
with n5:
    st.info("""
    **🤖 Page 5**
    **ML Predictor**

    Any scenario
    Predict wait time
    Risk level label

    *9,216 records trained*
    """)

st.divider()

st.markdown("## 🛠️ Tech Stack")
st.caption("End-to-end data science pipeline")
tc1, tc2, tc3, tc4, tc5, tc6, tc7, tc8 = st.columns(8)
tc1.success("🐍\n\nPython")
tc2.success("🗄️\n\nSQLite")
tc3.success("🐼\n\nPandas")
tc4.success("🤖\n\nScikit-learn")
tc5.success("📊\n\nStreamlit")
tc6.success("📈\n\nPlotly")
tc7.success("🔢\n\nNumPy")
tc8.success("📦\n\nKaggle")

st.divider()
st.caption("🏥 ER Wait Time Optimizer · Pragyan AI Hackathon · Kaggle Hospital Emergency Dataset (Apr 2023 – Oct 2024) · 9,216 patient records over 18 months")