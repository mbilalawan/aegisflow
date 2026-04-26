import pandas as pd

# 1. Calculate Success Rate
metrics = pd.read_csv('system_metrics.csv')
success_rate = (metrics['Status'] == 'Success').mean() * 100

# 2. Analyze Drift Categories
history = pd.read_csv('change_history.csv')
drift_summary = history['Category'].value_counts()

# 3. Measure Evolution Cycles
unique_repairs = history['Session_ID'].nunique()

print(f"Success Rate: {success_rate:.2f}%")
print(f"Total Adaptations: {unique_repairs}")
print("Drift Breakdown:\n", drift_summary)