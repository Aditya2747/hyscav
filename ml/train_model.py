"""ML Model Training for HySCAV Risk Assessment.

Run Slither on contracts/, extract features, heuristic labels, train RandomForestClassifier.
Saves ml/model.pkl and ml/dataset.csv.
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Add root for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.slither_runner import run_slither
from controller.feature_extractor import extract_slither_features

def get_heuristic_label(features: Dict[str, Any]) -> int:
    """Heuristic risk label: 0=LOW, 1=MEDIUM, 2=HIGH."""
    high = features.get('high', 0)
    medium = features.get('medium', 0)
    if high >= 1 or features.get('has_reentrancy', False) or features.get('has_overflow', False) or features.get('has_delegatecall', False):
        return 2
    if medium >= 2 or features.get('has_tx_origin', False) or features.get('has_unchecked_call', False):
        return 1
    return 0

print("Generating dataset from contracts...")

data = []

# 1. Real contracts
contracts_dir = 'contracts'
for filename in os.listdir(contracts_dir):
    if filename.endswith('.sol'):
        contract_path = os.path.join(contracts_dir, filename)
        print(f"Analyzing {filename}...")
        slither_data = run_slither(contract_path)
        if slither_data:
            features = extract_slither_features(slither_data)
            label = get_heuristic_label(features)
            data.append(features | {'label': label, 'contract': filename})
        else:
            print(f"Skipped {filename} (Slither failed)")

# 2. Test samples from tests (boost dataset)
test_samples = [
    # Reentrancy HIGH
    {'total_issues': 1, 'high': 1, 'medium': 0, 'low': 0, 'high_risk_categories': 1, 'medium_risk_categories': 0, 'unique_vuln_types': 1, 'contract_complexity': 4, 'has_reentrancy': True, 'has_overflow': False, 'has_unchecked_call': False, 'has_access_control': False, 'has_tx_origin': False, 'has_delegatecall': False, 'has_timestamp': False, 'has_weak_randomness': False, 'label': 2, 'contract': 'test_reentrancy'},
    # Overflow HIGH
    {'total_issues': 1, 'high': 1, 'medium': 0, 'low': 0, 'high_risk_categories': 1, 'medium_risk_categories': 0, 'unique_vuln_types': 1, 'contract_complexity': 4, 'has_reentrancy': False, 'has_overflow': True, 'has_unchecked_call': False, 'has_access_control': False, 'has_tx_origin': False, 'has_delegatecall': False, 'has_timestamp': False, 'has_weak_randomness': False, 'label': 2, 'contract': 'test_overflow'},
    # TxOrigin MEDIUM
    {'total_issues': 1, 'high': 0, 'medium': 1, 'low': 0, 'high_risk_categories': 0, 'medium_risk_categories': 1, 'unique_vuln_types': 1, 'contract_complexity': 3, 'has_reentrancy': False, 'has_overflow': False, 'has_unchecked_call': False, 'has_access_control': False, 'has_tx_origin': True, 'has_delegatecall': False, 'has_timestamp': False, 'has_weak_randomness': False, 'label': 1, 'contract': 'test_txorigin'},
    # Clean LOW
    {'total_issues': 0, 'high': 0, 'medium': 0, 'low': 0, 'high_risk_categories': 0, 'medium_risk_categories': 0, 'unique_vuln_types': 0, 'contract_complexity': 0, 'has_reentrancy': False, 'has_overflow': False, 'has_unchecked_call': False, 'has_access_control': False, 'has_tx_origin': False, 'has_delegatecall': False, 'has_timestamp': False, 'has_weak_randomness': False, 'label': 0, 'contract': 'test_clean'},
    # Multiple medium LOW
    {'total_issues': 3, 'high': 0, 'medium': 1, 'low': 2, 'high_risk_categories': 0, 'medium_risk_categories': 1, 'unique_vuln_types': 2, 'contract_complexity': 5, 'has_reentrancy': False, 'has_overflow': False, 'has_unchecked_call': False, 'has_access_control': True, 'has_tx_origin': False, 'has_delegatecall': False, 'has_timestamp': False, 'has_weak_randomness': False, 'label': 0, 'contract': 'test_low'},
]
data.extend(test_samples)

df = pd.DataFrame(data)
if len(df) < 5:
    print("ERROR: Too few samples. Check Slither installation.")
    sys.exit(1)

print(f"Dataset: {len(df)} samples")
print(df[['contract', 'label', 'high', 'has_reentrancy']].head())

# Features: all numeric + has_*
feature_cols = ['total_issues', 'high', 'medium', 'low', 'high_risk_categories', 'medium_risk_categories', 'unique_vuln_types', 'contract_complexity', 'external_calls', 'state_variables']
for col in df.columns:
    if col.startswith('has_'):
        feature_cols.append(col)

X = df[feature_cols].fillna(0).astype(float)
y = df['label']

print(f"Features shape: {X.shape}")
print(f"Labels distribution: {np.bincount(y)}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
train_acc = accuracy_score(y_train, model.predict(X_train))
test_acc = accuracy_score(y_test, model.predict(X_test))
print(f"Train accuracy: {train_acc:.2f}")
print(f"Test accuracy: {test_acc:.2f}")
print("\nClassification report:")
print(classification_report(y_test, model.predict(X_test)))

# Save
joblib.dump(model, 'model.pkl')
df.to_csv('dataset.csv', index=False)
print("\nSaved ml/model.pkl and ml/dataset.csv")
print("Training complete! Update risk_model.py to use the trained model.")
