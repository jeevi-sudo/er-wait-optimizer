# FILE 2: analysis.py
# PURPOSE: Run SQL queries to find bottlenecks by hour and day
# HOW TO RUN: python analysis.py

import sqlite3
import pandas as pd

# ── STEP 1: Connect to database ────────────────────────────────────
conn = sqlite3.connect('er_admissions.db')
print("✅ Connected to database!")

# ── STEP 2: Average wait time by HOUR and DAY (for heatmap) ───────
heatmap_query = """
    SELECT 
        Day_Of_Week,
        Day_Num,
        Hour_Of_Day,
        ROUND(AVG(Wait_Minutes), 1) AS Avg_Wait,
        COUNT(*) AS Patient_Count
    FROM er_admissions
    GROUP BY Day_Of_Week, Hour_Of_Day
    ORDER BY Day_Num, Hour_Of_Day
"""

heatmap_df = pd.read_sql_query(heatmap_query, conn)
print("✅ Heatmap data ready!")
print(heatmap_df.head(10))

# ── STEP 3: Worst hours overall ────────────────────────────────────
worst_hours_query = """
    SELECT 
        Hour_Of_Day,
        ROUND(AVG(Wait_Minutes), 1) AS Avg_Wait,
        COUNT(*) AS Patient_Count
    FROM er_admissions
    GROUP BY Hour_Of_Day
    ORDER BY Avg_Wait DESC
    LIMIT 5
"""

worst_hours = pd.read_sql_query(worst_hours_query, conn)
print("\n✅ Top 5 WORST hours:")
print(worst_hours)

# ── STEP 4: Worst days overall ─────────────────────────────────────
worst_days_query = """
    SELECT 
        Day_Of_Week,
        ROUND(AVG(Wait_Minutes), 1) AS Avg_Wait,
        COUNT(*) AS Patient_Count
    FROM er_admissions
    GROUP BY Day_Of_Week
    ORDER BY Avg_Wait DESC
"""

worst_days = pd.read_sql_query(worst_days_query, conn)
print("\n✅ Worst days ranked:")
print(worst_days)

# ── STEP 5: Critical patients waiting too long ─────────────────────
critical_query = """
    SELECT 
        Triage_Score,
        ROUND(AVG(Wait_Minutes), 1) AS Avg_Wait,
        COUNT(*) AS Patient_Count
    FROM er_admissions
    GROUP BY Triage_Score
    ORDER BY Triage_Score
"""

critical_df = pd.read_sql_query(critical_query, conn)
print("\n✅ Wait time by Triage Score:")
print(critical_df)

# ── STEP 6: Save results for app to use ───────────────────────────
heatmap_df.to_csv('heatmap_data.csv', index=False)
worst_hours.to_csv('worst_hours.csv', index=False)
worst_days.to_csv('worst_days.csv', index=False)
critical_df.to_csv('critical_data.csv', index=False)

conn.close()
print("\n🎉 FILE 2 COMPLETE! All analysis saved!")