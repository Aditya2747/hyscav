import pandas as pd
import json
from pathlib import Path
import glob

# Load SmartBugs labels
with open('smartbugs-curated/vulnerabilities.json') as f:
    smartbugs = json.load(f)

vulns_summary = {}
total_contracts = len(smartbugs)
total_vulns = 0

high_vulns = ['reentrancy', 'arithmetic', 'unchecked_low_level_calls', 'access_control']
med_vulns = ['denial_of_service', 'front_running', 'bad_randomness']

high_count = 0
med_count = 0
low_count = 0

category_counts = {}

for entry in smartbugs:
    categories = [v['category'] for v in entry['vulnerabilities']]
    total_vulns += len(categories)
    
    for cat in categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if cat in high_vulns:
            high_count += 1
            break
    else:
        if any(cat in med_vulns for cat in categories):
            med_count += 1
        else:
            low_count += 1

print(f"SmartBugs Dataset Summary:")
print(f"Total contracts: {total_contracts}")
print(f"Total vulnerabilities: {total_vulns}")
print(f"HIGH risk: {high_count}")
print(f"MEDIUM risk: {med_count}")
print(f"LOW risk: {low_count}")

# Summary table
summary_df = pd.DataFrame({
    'Dataset': ['SmartBugs Curated'],
    'Contracts': [total_contracts],
    'Vulns': [total_vulns],
    'HIGH': [high_count],
    'MEDIUM': [med_count],
    'LOW': [low_count]
})

# Category counts
cat_df = pd.DataFrame(list(category_counts.items()), columns=['Category', 'Count']).sort_values('Count', ascending=False)

# Cumulative Excel
with pd.ExcelWriter('reports/smartbugs_cumulative_report.xlsx', engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    cat_df.to_excel(writer, sheet_name='Vuln Categories', index=False)
    pd.read_csv('dataset.csv').to_excel(writer, sheet_name='POC Dataset', index=False)

print("Cumulative Excel saved: reports/smartbugs_cumulative_report.xlsx")
print("\nTop categories:")
print(cat_df.head(10).to_markdown(index=False))
