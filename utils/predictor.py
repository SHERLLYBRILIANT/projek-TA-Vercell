"""
utils/predictor.py
──────────────────
Modul prediksi status gizi menggunakan TabNet
Features: Gender (0/1), Age (Month), Weight (kg), Height (cm)
Targets:
  - Weight for Age  (BB/U): 0=Underfed, 1=Normal, 2=Malnutrition, 3=Overnutrition
  - Height for Age  (TB/U): 0=Not Stunted, 1=Stunted
  - Weight for Height(BB/TB):0=Very Thin, 1=Thin, 2=Normal, 3=Obese
"""

import os
import warnings
import numpy as np

warnings.filterwarnings('ignore')

# ─── Label Maps ──────────────────────────────────────────────────────────────
ENCODING_MAP = {
    'Weight for Age': {
        0: 'Underfed',
        1: 'Normal',
        2: 'Malnutrition',
        3: 'Overnutrition'
    },
    'Height for Age': {
        0: 'Not Stunted',
        1: 'Stunted'
    },
    'Weight for Height': {
        0: 'Very Thin',
        1: 'Thin',
        2: 'Normal',
        3: 'Obese'
    }
}

# Warna badge untuk setiap label (Bootstrap)
LABEL_COLOR = {
    # BB/U
    'Underfed':      'warning',
    'Normal':        'success',
    'Malnutrition':  'danger',
    'Overnutrition': 'info',
    # TB/U
    'Not Stunted':   'success',
    'Stunted':       'danger',
    # BB/TB
    'Very Thin':     'danger',
    'Thin':          'warning',
    'Obese':         'info',
}

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# ─── Scaler parameters (StandardScaler dari notebook)
# Nilai ini harus disesuaikan dengan nilai scaler yang digunakan saat training.
# Jika Anda menyimpan scaler.joblib, load dari sana.
# Default: placeholder mean/std yang umum untuk data balita Indonesia.
SCALER_PARAMS = {
    'mean': np.array([0.48, 24.5, 9.2, 78.5]),   # Gender, Age, Weight, Height
    'std':  np.array([0.50,  14.2, 2.8, 11.3])
}


class GiziPredictor:
    """
    Wrapper untuk 3 model TabNet (BB/U, TB/U, BB/TB).
    Jika model tidak ditemukan, menggunakan rule-based fallback (WHO standards).
    """

    def __init__(self):
        self.models = {}
        self.model_loaded = False
        self._load_models()

    def _load_models(self):
        """Load TabNet models dari folder models/"""
        try:
            from pytorch_tabnet.tab_model import TabNetClassifier

            target_files = {
                'Weight for Age':   'tabnet_weight_for_age.zip',
                'Height for Age':   'tabnet_height_for_age.zip',
                'Weight for Height':'tabnet_weight_for_height.zip',
            }

            loaded = 0
            for target, fname in target_files.items():
                model_path = os.path.join(MODEL_DIR, fname.replace('.zip', ''))
                zip_path   = os.path.join(MODEL_DIR, fname)

                # TabNet load_model menerima path tanpa .zip
                if os.path.exists(zip_path):
                    clf = TabNetClassifier()
                    clf.load_model(zip_path)
                    self.models[target] = clf
                    loaded += 1
                    print(f'  ✅ Model loaded: {fname}')
                else:
                    print(f'  ⚠️  Model tidak ditemukan: {zip_path}')

            # Load scaler jika ada
            scaler_path = os.path.join(MODEL_DIR, 'standard_scaler.joblib')
            if os.path.exists(scaler_path):
                import joblib
                scaler = joblib.load(scaler_path)
                # Jika scaler hanya punya 3 fitur (Age, Weight, Height), tambahkan dummy untuk Gender agar tidak ikut di-scale
                if len(scaler.mean_) == 3:
                    import numpy as np
                    SCALER_PARAMS['mean'] = np.array([0.0] + list(scaler.mean_))
                    SCALER_PARAMS['std']  = np.array([1.0] + list(scaler.scale_))
                else:
                    SCALER_PARAMS['mean'] = scaler.mean_
                    SCALER_PARAMS['std']  = scaler.scale_
                print('  ✅ Scaler loaded dari standard_scaler.joblib')

            if loaded == 3:
                self.model_loaded = True
                print('✅ Semua model TabNet berhasil dimuat!')
            elif loaded > 0:
                self.model_loaded = True
                print(f'⚠️  {loaded}/3 model dimuat. Model sisanya gunakan fallback.')
            else:
                print('⚠️  Tidak ada model TabNet ditemukan. Menggunakan rule-based fallback.')

        except ImportError:
            print('⚠️  pytorch-tabnet belum terinstall. Gunakan: pip install pytorch-tabnet')
        except Exception as e:
            print(f'⚠️  Gagal memuat model: {e}')

    def _scale(self, X: np.ndarray) -> np.ndarray:
        """StandardScaler transform"""
        return (X - SCALER_PARAMS['mean']) / SCALER_PARAMS['std']

    def _predict_with_model(self, target: str, X_scaled: np.ndarray) -> int:
        """Prediksi dengan model TabNet"""
        model = self.models[target]
        pred  = model.predict(X_scaled)
        return int(pred[0])

    def _rule_based_fallback(self, gender: int, age_months: int,
                             weight: float, height: float) -> dict:
        """
        Fallback berbasis aturan WHO Child Growth Standards
        Digunakan jika model TabNet belum di-load.
        """
        # BB/U (Weight for Age) — z-score sederhana
        # Referensi median BB/U anak Indonesia (approx)
        ref_weight = {
            'L': {3:6.0,6:7.9,9:9.2,12:10.2,18:11.5,24:12.5,36:14.3,48:16.3,60:18.3},
            'P': {3:5.4,6:7.3,9:8.5,12:9.5,18:10.8,24:11.8,36:13.9,48:15.9,60:18.2}
        }
        # BB/TB
        bmi = weight / ((height/100)**2)

        gender_key = 'L' if gender == 1 else 'P'
        nearest_age = min(ref_weight[gender_key].keys(), key=lambda x: abs(x-age_months))
        ref_w = ref_weight[gender_key][nearest_age]
        weight_ratio = weight / ref_w

        # BB/U kode
        if weight_ratio < 0.70:
            bbu_kode = 2  # Malnutrition
        elif weight_ratio < 0.85:
            bbu_kode = 0  # Underfed
        elif weight_ratio > 1.25:
            bbu_kode = 3  # Overnutrition
        else:
            bbu_kode = 1  # Normal

        # TB/U — stunting jika tinggi < 2 SD
        ref_height = {
            'L': {12:75.7,24:87.1,36:96.1,48:103.3,60:110.0},
            'P': {12:74.0,24:85.7,36:95.1,48:102.7,60:109.4}
        }
        nearest_h = min(ref_height[gender_key].keys(), key=lambda x: abs(x-age_months))
        ref_h = ref_height[gender_key][nearest_h]
        tbu_kode = 1 if height < ref_h * 0.9 else 0

        # BB/TB (BMI-based)
        if bmi < 14.0:
            bbtb_kode = 0  # Very Thin
        elif bmi < 16.5:
            bbtb_kode = 1  # Thin
        elif bmi > 22.0:
            bbtb_kode = 3  # Obese
        else:
            bbtb_kode = 2  # Normal

        return {'bbu': bbu_kode, 'tbu': tbu_kode, 'bbtb': bbtb_kode}

    def predict_single(self, gender: int, age_months: int,
                       weight: float, height: float) -> dict:
        """
        Prediksi status gizi satu balita.
        Returns dict dengan label dan kode untuk setiap indikator.
        """
        X = np.array([[gender, age_months, weight, height]], dtype=np.float32)
        X_scaled = self._scale(X)

        hasil_kode = {}

        # Coba gunakan model TabNet
        targets = ['Weight for Age', 'Height for Age', 'Weight for Height']
        keys    = ['bbu', 'tbu', 'bbtb']

        all_ok = True
        for target, key in zip(targets, keys):
            if target in self.models:
                try:
                    hasil_kode[key] = self._predict_with_model(target, X_scaled)
                except Exception as e:
                    print(f'Error prediksi {target}: {e}')
                    all_ok = False
                    break
            else:
                all_ok = False
                break

        if not all_ok or not self.models:
            # Fallback rule-based
            hasil_kode = self._rule_based_fallback(gender, age_months, weight, height)

        # Map kode → label
        bbu_label  = ENCODING_MAP['Weight for Age'].get(hasil_kode['bbu'],  'Unknown')
        tbu_label  = ENCODING_MAP['Height for Age'].get(hasil_kode['tbu'],  'Unknown')
        bbtb_label = ENCODING_MAP['Weight for Height'].get(hasil_kode['bbtb'], 'Unknown')

        return {
            'bbu': {
                'kode':  hasil_kode['bbu'],
                'label': bbu_label,
                'color': LABEL_COLOR.get(bbu_label, 'secondary'),
                'desc':  'Berat Badan menurut Umur (BB/U)'
            },
            'tbu': {
                'kode':  hasil_kode['tbu'],
                'label': tbu_label,
                'color': LABEL_COLOR.get(tbu_label, 'secondary'),
                'desc':  'Tinggi Badan menurut Umur (TB/U)'
            },
            'bbtb': {
                'kode':  hasil_kode['bbtb'],
                'label': bbtb_label,
                'color': LABEL_COLOR.get(bbtb_label, 'secondary'),
                'desc':  'Berat Badan menurut Tinggi Badan (BB/TB)'
            },
            'model_used': 'TabNet' if self.model_loaded else 'Rule-Based (WHO Standards)'
        }
