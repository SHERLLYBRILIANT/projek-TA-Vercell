"""
Microservice API untuk Model TabNet GiziLens
Didesain untuk di-hosting di Hugging Face Spaces (Gratis) atau Render.com
"""

import os
import numpy as np
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cek lokasi folder models (bisa di folder yang sama atau subfolder)
MODEL_DIR = os.path.join(BASE_DIR, 'models') if os.path.exists(os.path.join(BASE_DIR, 'models')) else BASE_DIR

SCALER_PARAMS = {
    'mean': np.array([0.48, 24.5, 9.2, 78.5]),
    'std':  np.array([0.50, 14.2, 2.8, 11.3])
}

models = {}

def load_models():
    global models, SCALER_PARAMS
    try:
        from pytorch_tabnet.tab_model import TabNetClassifier
        
        target_files = {
            'Weight for Age':    'tabnet_weight_for_age.zip',
            'Height for Age':    'tabnet_height_for_age.zip',
            'Weight for Height': 'tabnet_weight_for_height.zip',
        }
        
        for target, fname in target_files.items():
            zip_path = os.path.join(MODEL_DIR, fname)
            if os.path.exists(zip_path):
                clf = TabNetClassifier()
                clf.load_model(zip_path)
                models[target] = clf
                print(f"✅ Loaded {target} dari {fname}")
            else:
                print(f"⚠️ Model {fname} tidak ditemukan di {zip_path}")

        scaler_path = os.path.join(MODEL_DIR, 'standard_scaler.joblib')
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            if len(scaler.mean_) == 3:
                SCALER_PARAMS['mean'] = np.array([0.0] + list(scaler.mean_))
                SCALER_PARAMS['std']  = np.array([1.0] + list(scaler.scale_))
            else:
                SCALER_PARAMS['mean'] = scaler.mean_
                SCALER_PARAMS['std']  = scaler.scale_
            print("✅ Scaler loaded.")
    except Exception as e:
        print(f"❌ Error loading models: {e}")

load_models()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "service": "GiziLens TabNet Prediction API",
        "models_loaded": list(models.keys())
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        gender     = float(data.get('gender', 0))
        age_months = float(data.get('age_months', 0))
        weight     = float(data.get('weight', 0))
        height     = float(data.get('height', 0))

        X = np.array([[gender, age_months, weight, height]], dtype=np.float32)
        X_scaled = (X - SCALER_PARAMS['mean']) / SCALER_PARAMS['std']

        hasil = {}
        targets = {
            'bbu':  'Weight for Age',
            'tbu':  'Height for Age',
            'bbtb': 'Weight for Height'
        }

        for key, target_name in targets.items():
            if target_name in models:
                pred = models[target_name].predict(X_scaled)
                hasil[key] = int(pred[0])
            else:
                return jsonify({"error": f"Model {target_name} belum dimuat"}), 500

        return jsonify(hasil)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)

