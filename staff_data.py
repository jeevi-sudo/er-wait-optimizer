# FILE: staff_data.py
# PURPOSE: Generate realistic staff data and save to database
# HOW TO RUN: python staff_data.py

import sqlite3
import pandas as pd
import numpy as np

# ── STEP 1: Define realistic staff counts by hour ─────────────────
# Based on real hospital shift patterns
# Night=least staff, Evening=most staff, Weekends=reduced

def get_staff_count(hour, day_num):
    # Base staff by hour (shift patterns)
    if 0 <= hour < 6:      # Night shift
        base = 2
    elif 6 <= hour < 14:   # Morning shift
        base = 6
    elif 14 <= hour < 22:  # Evening shift
        base = 7
    else:                   # Late night
        base = 3

    # Weekends have less staff
    if day_num >= 5:        # Saturday=5, Sunday=6
        base = max(1, base - 2)

    # Add small random variation (realistic)
    variation = np.random.choice([-1, 0, 0, 1])
    return max(1, base + variation)

# ── STEP 2: Generate staff table for all hours and days ───────────
days = ['Monday','Tuesday','Wednesday',
        'Thursday','Friday','Saturday','Sunday']

staff_records = []
for day_num, day_name in enumerate(days):
    for hour in range(24):
        staff_count = get_staff_count(hour, day_num)
        staff_records.append({
            'Day_Of_Week'  : day_name,
            'Day_Num'      : day_num,
            'Hour_Of_Day'  : hour,
            'Doctor_Count' : staff_count,
            'Shift'        : (
                'Night'   if 0  <= hour < 6  else
                'Morning' if 6  <= hour < 14 else
                'Evening' if 14 <= hour < 22 else
                'Late Night'
            )
        })

staff_df = pd.DataFrame(staff_records)
print("✅ Staff data generated!")
print(staff_df.head(10))

# ── STEP 3: Load patient data to calculate patients per hour ───────
conn = sqlite3.connect('er_admissions.db')
patient_df = pd.read_sql_query("""
    SELECT 
        Day_Of_Week,
        Day_Num,
        Hour_Of_Day,
        COUNT(*) as Total_Patients,
        ROUND(AVG(Wait_Minutes), 1) as Avg_Wait
    FROM er_admissions
    GROUP BY Day_Of_Week, Day_Num, Hour_Of_Day
""", conn)

# ── STEP 4: Merge staff + patients ────────────────────────────────
merged = pd.merge(
    staff_df, patient_df,
    on=['Day_Of_Week', 'Day_Num', 'Hour_Of_Day'],
    how='left'
)

# Fill any missing patient counts with 0
merged['Total_Patients'] = merged['Total_Patients'].fillna(0)
merged['Avg_Wait']       = merged['Avg_Wait'].fillna(0)

# ── STEP 5: Calculate patients per doctor (workload) ──────────────
merged['Patients_Per_Doctor'] = (
    merged['Total_Patients'] / merged['Doctor_Count']
).round(1)

# ── STEP 6: Flag shortage zones ───────────────────────────────────
# SHORTAGE = more than 8 patients per doctor in that hour
# OR less than 3 doctors during peak hours (>15 patients)
def flag_shortage(row):
    if row['Patients_Per_Doctor'] > 8:
        return '🔴 Critical Shortage'
    elif row['Patients_Per_Doctor'] > 5:
        return '🟠 Understaffed'
    elif row['Patients_Per_Doctor'] > 3:
        return '🟡 Slightly Stretched'
    else:
        return '🟢 Adequate'

merged['Staffing_Status'] = merged.apply(flag_shortage, axis=1)

print("✅ Staff vs Patient analysis done!")
print("\nStaffing Status breakdown:")
print(merged['Staffing_Status'].value_counts())

# ── STEP 7: Save to database ───────────────────────────────────────
merged.to_sql('staff_data', conn, if_exists='replace', index=False)
conn.close()

print("\n✅ Staff data saved to database!")
print("🎉 STAFF FILE COMPLETE!")
print("\nSample — worst shortage slots:")
print(
    merged[merged['Staffing_Status']=='🔴 Critical Shortage']
    [['Day_Of_Week','Hour_Of_Day','Doctor_Count',
      'Total_Patients','Patients_Per_Doctor']]
    .head(5)
)