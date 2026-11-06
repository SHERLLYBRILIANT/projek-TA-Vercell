#!/usr/bin/env python3
"""
Test script: cek apakah /api/model_info berfungsi
"""

import json
import os
import sys

# Test 1: JSON file exists and can be read
json_path = os.path.join(os.path.dirname(__file__), 'models', 'model_evaluation.json')
print(f"[TEST 1] Checking {json_path}")
if os.path.exists(json_path):
    print("✓ File exists")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ JSON valid - keys: {list(data.keys())}")
        print(f"✓ Has 'model_artifacts': {'model_artifacts' in data}")
        print(f"✓ Has 'training_info': {'training_info' in data}")
        print(f"✓ Has 'model_evaluation': {'model_evaluation' in data}")
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error: {e}")
        sys.exit(1)
else:
    print(f"✗ File not found")
    sys.exit(1)

# Test 2: Simulate Flask response
print("\n[TEST 2] Simulating Flask API response")
response_payload = {
    'success': True,
    'data': data
}
print(f"✓ Response would be: {len(json.dumps(response_payload))} bytes")
print(f"✓ Response keys: {list(response_payload['data'].keys())}")

# Test 3: Check critical elements for JS rendering
print("\n[TEST 3] Checking data structure for JS rendering")
try:
    ma = data['model_artifacts']
    print(f"✓ model_artifacts.outputs keys: {list(ma['outputs'].keys())}")
    for k, v in ma['outputs'].items():
        print(f"  - {k}: {v['total_params']} params")
    
    ti = data['training_info']
    print(f"✓ training_info.epochs_completed: {ti['epochs_completed']}")
    
    me = data['model_evaluation']
    for k, v in me.items():
        acc = v['testing']['accuracy']
        print(f"✓ {k} testing accuracy: {acc:.2%}")
    
    hp = data['hyperparameters']
    print(f"✓ hyperparameters.n_trials: {hp['n_trials']}")
    print(f"✓ hyperparameters.sampler: {hp.get('sampler', 'N/A')}")
    
except (KeyError, TypeError) as e:
    print(f"✗ Data structure error: {e}")
    sys.exit(1)

print("\n✓✓✓ All checks passed! API should work correctly.")
