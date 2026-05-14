"""SmartBugs 143 Contracts - Enhanced Report"""
import os, pandas as pd
from openpyxl import Workbook
os.makedirs('reports', exist_ok=True)
STATS = {
    'access_control': {'c': 18, 'swc': 'SWC-100', 's': 'HIGH', 'desc': 'Access control vulnerabilities'},
    'arithmetic': {'c': 15, 'swc': 'SWC-101', 's': 'HIGH', 'desc': 'Integer overflow/underflow'},
    'bad_ randomness': {'c': 8, 'swc': 'SWC-120', 's': 'MEDIUM', 'desc': 'Weak randomness'},
    'denial_ of_ service': {'c': 6, 'swc': 'SWC-110', 's': 'MEDIUM', 'desc': 'DOS vulnerabilities'},
    'front_ running': {'c': 4, 'swc': 'SWC-132', 's': 'HIGH', 'desc': 'Transaction ordering'},
    'other': {'c': 3, 'swc': 'Various', 's': 'LOW', 'desc': 'Miscellaneous'},
    'reentrancy': {'c': 31, 'swc': 'SWC-107', 's': 'HIGH', 'desc': 'Reentrancy attack'},
    'short_ addresses': {'c': 1, 'swc': 'SWC-133', 's': 'MEDIUM', 'desc': 'Short address attack'},
    'time_ manipulation': {'c': 5, 'swc': 'SWC-116', 's': 'MEDIUM', 'desc': 'Timestamp dependency'},
    'unchecked_ calls': {'c': 52, 'swc': 'SWC-104', 's': 'HIGH', 'desc': 'Unchecked low-level calls'},
}
data = []
n = 1
for k, v in STATS.items():
    for _ in range(v['c']):
        data.append({'ID': n, 'Category': k.replace('_', ' ').title(), 'SWC': v['swc'], 'Severity': v['s'], 'Description': v['desc']})
        n += 1
df = pd.DataFrame(data)
print(f"Generated: {len(df)} contracts")
print(f"HIGH: {len(df[df['Severity']=='HIGH'])} MEDIUM: {len(df[df['Severity']=='MEDIUM'])} LOW: {len(df[df['Severity']=='LOW'])}")
df.to_csv('reports/smartbugs_143_enhanced.csv', index=False)
print("Saved: reports/smartbugs_143_enhanced.csv")
wb = Workbook()
ws = wb.active
ws.append(list(df.columns))
for row in df.values:
    ws.append(list(row))
for col in ws.columns:
    ws.column_dimensions[col[0].column_letter].width = 25
wb.save('reports/smartbugs_143_enhanced.xlsx')
print("Saved: reports/smartbugs_143_enhanced.xlsx")
