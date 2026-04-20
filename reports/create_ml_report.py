import pandas as pd
import json
from sklearn.metrics import classification_report
import joblib
from pathlib import Path

# Load dataset
df = pd.read_csv('dataset.csv')

# Load SmartBugs stats
with open('smartbugs-curated/vulnerabilities.json') as f:
    smartbugs = json.load(f)

vulns_count = {}
for entry in smartbugs:
    for v in entry['vulnerabilities']:
        cat = v['category']
        vulns_count[cat] = vulns_count.get(cat, 0) + 1

smartbugs_df = pd.DataFrame([vulns_count]).T.reset_index()
smartbugs_df.columns = ['Category', 'Count']

# Load model
model = joblib.load('model.pkl')

# Model summary
feature_importance = pd.DataFrame({
    'feature': model.feature_names_in_,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

# Excel with tabs
with pd.ExcelWriter('reports/ml_cumulative_report.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Dataset (10 contracts)', index=False)
    smartbugs_df.to_excel(writer, sheet_name='SmartBugs Stats (143 contracts)')
    feature_importance.head(10).to_excel(writer, sheet_name='Top Features', index=False)

print("Cumulative Excel report saved: reports/ml_cumulative_report.xlsx")
print(f"Dataset shape: {df.shape}")
print(f"Model classes: {model.classes_}")
print(df['label'].value_counts())
print("\nReady for production retrain with SmartBugs!")
