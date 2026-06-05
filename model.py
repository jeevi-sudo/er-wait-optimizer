# FILE 3: model.py
# PURPOSE: Train ML model to predict wait times + risk levels
# HOW TO RUN: python model.py

import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import pickle

# ── STEP 1: Load data ──────────────────────────────────────────────
conn = sqlite3.connect('er_admissions.db')
df = pd.read_sql_query("SELECT * FROM er_admissions", conn)
conn.close()
print("✅ Data loaded! Records:", len(df))

# ── STEP 2: Prepare features ───────────────────────────────────────
# Features we use to predict wait time
features = ['Hour_Of_Day', 'Day_Num', 'Triage_Score', 'Age']
target   = 'Wait_Minutes'

# Drop rows with missing values in these columns
df = df.dropna(subset=features + [target])

X = df[features]
y = df[target]

print("✅ Features prepared!")

# ── STEP 3: Train Linear Regression (predict wait time) ────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

y_pred = lr_model.predict(X_test)
mae    = mean_absolute_error(y_test, y_pred)

print(f"✅ Linear Regression trained! MAE: {mae:.1f} minutes")

# ── STEP 4: Train Risk Classifier (HIGH/LOW risk hours) ────────────
# HIGH RISK = wait time above average
avg_wait         = df['Wait_Minutes'].mean()
df['Risk_Level'] = (df['Wait_Minutes'] > avg_wait).astype(int)
# 1 = HIGH RISK, 0 = LOW RISK

y_risk = df['Risk_Level']
X_risk = df[features]

Xr_train, Xr_test, yr_train, yr_test = train_test_split(
    X_risk, y_risk, test_size=0.2, random_state=42
)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(Xr_train, yr_train)

yr_pred   = rf_model.predict(Xr_test)
accuracy  = accuracy_score(yr_test, yr_pred)

print(f"✅ Risk Classifier trained! Accuracy: {accuracy*100:.1f}%")

# ── STEP 5: Save models for app to use ────────────────────────────
pickle.dump(lr_model, open('wait_model.pkl', 'wb'))
pickle.dump(rf_model, open('risk_model.pkl', 'wb'))

print("✅ Models saved!")

# ── STEP 6: Show what model learned ───────────────────────────────
print("\n📊 Average wait time in dataset:", round(avg_wait, 1), "mins")
print("📊 HIGH RISK threshold:", round(avg_wait, 1), "mins")

# Test prediction example
sample = pd.DataFrame([[22, 4, 2, 45]], columns=features)
predicted_wait = lr_model.predict(sample)[0]
risk           = rf_model.predict(sample)[0]
risk_label     = "🔴 HIGH RISK" if risk == 1 else "🟢 LOW RISK"

print(f"\n🧪 Test: Friday 10PM, Triage 2, Age 45")
print(f"   Predicted wait : {predicted_wait:.1f} mins")
print(f"   Risk level     : {risk_label}")

print("\n🎉 FILE 3 COMPLETE! ML models ready!")