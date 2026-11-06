#!/usr/bin/env python3
"""
TESTING SCRIPT: Verify Model Info Setup
Run this to check if everything is configured correctly.
"""

import os
import sys
import json
from pathlib import Path

def test_json_file():
    """Test 1: Check model_evaluation.json exists and is valid"""
    print("\n[TEST 1] Checking model_evaluation.json...")
    json_path = Path(__file__).resolve().parent / 'models' / 'model_evaluation.json'
    
    if not json_path.exists():
        print(f"  ERROR: File not found at {json_path}")
        return False
    
    print(f"  OK: File exists")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  OK: JSON is valid")
    except json.JSONDecodeError as e:
        print(f"  ERROR: JSON decode error - {e}")
        return False
    
    return data

def test_data_structure(data):
    """Test 2: Check required data structure"""
    print("\n[TEST 2] Checking data structure...")
    
    required_keys = [
        'model_evaluation',
        'training_info',
        'model_artifacts',
        'hyperparameters',
        'feature_importance'
    ]
    
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"  ERROR: Missing keys: {missing}")
        return False
    
    print(f"  OK: All required keys present")
    return True

def test_model_artifacts(data):
    """Test 3: Check model_artifacts structure"""
    print("\n[TEST 3] Checking model_artifacts...")
    
    ma = data.get('model_artifacts', {})
    if 'outputs' not in ma:
        print(f"  ERROR: model_artifacts.outputs missing")
        return False
    
    outputs = ma['outputs']
    required_models = ['bbu', 'tbu', 'bbtb']
    missing = [m for m in required_models if m not in outputs]
    if missing:
        print(f"  ERROR: Missing models: {missing}")
        return False
    
    for model_key, model_data in outputs.items():
        if 'total_params' not in model_data:
            print(f"  ERROR: {model_key} missing total_params")
            return False
        print(f"  OK: {model_key} = {model_data['total_params']} parameters")
    
    return True

def test_training_info(data):
    """Test 4: Check training_info structure"""
    print("\n[TEST 4] Checking training_info...")
    
    ti = data.get('training_info', {})
    if 'epochs_completed' not in ti:
        print(f"  ERROR: training_info.epochs_completed missing")
        return False
    
    epochs = ti['epochs_completed']
    for model, epoch_count in epochs.items():
        print(f"  OK: {model} completed {epoch_count} epochs")
    
    return True

def test_model_evaluation(data):
    """Test 5: Check model_evaluation metrics"""
    print("\n[TEST 5] Checking model_evaluation metrics...")
    
    me = data.get('model_evaluation', {})
    for model_key, model_eval in me.items():
        if 'testing' not in model_eval:
            print(f"  ERROR: {model_key} missing testing metrics")
            return False
        
        test_metrics = model_eval['testing']
        acc = test_metrics.get('accuracy', 0)
        print(f"  OK: {model_key} testing accuracy = {acc:.2%}")
    
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("MODEL INFO SETUP VERIFICATION")
    print("="*60)
    
    # Test 1
    data = test_json_file()
    if not data:
        print("\n[RESULT] FAILED - JSON file problem")
        return False
    
    # Test 2
    if not test_data_structure(data):
        print("\n[RESULT] FAILED - Data structure problem")
        return False
    
    # Test 3
    if not test_model_artifacts(data):
        print("\n[RESULT] FAILED - Model artifacts problem")
        return False
    
    # Test 4
    if not test_training_info(data):
        print("\n[RESULT] FAILED - Training info problem")
        return False
    
    # Test 5
    if not test_model_evaluation(data):
        print("\n[RESULT] FAILED - Model evaluation problem")
        return False
    
    # All passed
    print("\n" + "="*60)
    print("[RESULT] SUCCESS - All checks passed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Restart Flask: python app.py")
    print("2. Hard refresh browser: Ctrl+F5")
    print("3. Login and open 'Informasi Model AI' menu")
    print("4. Open DevTools (F12) Console to see debug logs")
    print("\nExpected logs:")
    print("  [model_info.js] modelData assigned")
    print("  [renderOverviewTab] Starting render...")
    print("  [renderOverviewTab] chartParams created")
    print("  [renderOverviewTab] chartEpochs created")
    print("  [renderOverviewTab] chartAvgMetrics created")
    print("  [renderOverviewTab] Render complete")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
