# FILE 1: create_db.py
# PURPOSE: Load Kaggle CSV, clean it, add missing columns, save as database
# HOW TO RUN: python create_db.py

import pandas as pd
import sqlite3
from datetime import timedelta
import numpy as np

# ── STEP 1: Load your CSV ──────────────────────────────────────────
# Put your downloaded CSV file in the same folder as this file
# Rename your CSV file to:  hospital_data.csv

df = pd.read_csv('hospital_data.csv')

print("✅ CSV loaded! Shape:", df.shape)
print("Columns found:", df.columns.tolist())

# ── STEP 2: Rename columns to match problem statement ──────────────

df = df.rename(columns={
    'Patient Id'                 : 'Patient_ID',
    'Patient Admission Date'     : 'Check_In_Time',
    'Patient Waittime'           : 'Wait_Minutes',
    'Patient Satisfaction Score' : 'Satisfaction_Score',
    'Department Referral'        : 'Department',
    'Patient Age'                : 'Age',
    'Patient Gender'             : 'Gender',
    'Patient Race'               : 'Race',
    'Patient Admission Flag'     : 'Admitted',
    'Patients CM'                : 'Case_Manager'
})

print("✅ Columns renamed!")

# ── STEP 3: Clean the data ─────────────────────────────────────────

# Convert Check_In_Time to proper datetime format
df['Check_In_Time'] = pd.to_datetime(df['Check_In_Time'])

# Remove rows where wait time is missing or negative
df = df.dropna(subset=['Wait_Minutes'])
df = df[df['Wait_Minutes'] >= 0]

# Fill any missing satisfaction scores with average
df['Satisfaction_Score'] = df['Satisfaction_Score'].fillna(
    df['Satisfaction_Score'].mean()
)

print("✅ Data cleaned!")

# ── STEP 4: Derive TRIAGE SCORE from Age + Wait Time ──────────────
# Logic: older patients + longer waits = more critical (lower score)
# Score 1 = most critical, Score 5 = least critical

def assign_triage(row):
    age  = row['Age']
    wait = row['Wait_Minutes']
    if age > 60 and wait > 45:
        return 1   # Critical
    elif age > 60 or wait > 45:
        return 2   # Urgent
    elif age > 40 and wait > 30:
        return 3   # Less urgent
    elif wait > 20:
        return 4   # Minor
    else:
        return 5   # Non-urgent

df['Triage_Score'] = df.apply(assign_triage, axis=1)

print("✅ Triage scores derived!")

# ── STEP 5: Derive PHYSICIAN ASSIGNED TIME ────────────────────────
# Logic: Doctor sees patient AFTER wait time is over
# Physician_Assigned_Time = Check_In_Time + Wait_Minutes

df['Physician_Assigned_Time'] = df['Check_In_Time'] + \
    pd.to_timedelta(df['Wait_Minutes'], unit='m')

print("✅ Physician assigned times calculated!")

# ── STEP 6: Add hour and day columns (needed for heatmap) ─────────

df['Hour_Of_Day']    = df['Check_In_Time'].dt.hour
df['Day_Of_Week']    = df['Check_In_Time'].dt.day_name()
df['Day_Num']        = df['Check_In_Time'].dt.dayofweek

print("✅ Hour and day columns added!")

# ── STEP 7: Save as SQLite database ───────────────────────────────

conn = sqlite3.connect('er_admissions.db')
df.to_sql('er_admissions', conn, if_exists='replace', index=False)
conn.close()

print("✅ Database saved as er_admissions.db!")
print("🎉 FILE 1 COMPLETE! Total records:", len(df))
print("\nSample data:")
print(df[['Patient_ID','Triage_Score','Check_In_Time',
          'Physician_Assigned_Time','Wait_Minutes']].head())