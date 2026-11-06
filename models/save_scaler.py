"""
save_scaler.py
─────────────────────────────
Jalankan script ini di lingkungan training Anda (Google Colab/Jupyter)
untuk menyimpan StandardScaler yang digunakan saat preprocessing.

Kemudian salin file scaler.joblib ke folder models/ project ini.
"""

# ── Di notebook training Anda, jalankan ini setelah preprocessing ─────────
# from sklearn.preprocessing import StandardScaler
# import joblib, numpy as np
#
# FEATURE_COLS = ['Gender', 'Age (Month)', 'Weight', 'Height']
# X_raw = df_original[FEATURE_COLS].values.astype(np.float32)
#
# scaler = StandardScaler()
# scaler.fit(X_raw)
# joblib.dump(scaler, 'scaler.joblib')
# print("Scaler disimpan: scaler.joblib")
# print("Mean:", scaler.mean_)
# print("Std :", scaler.scale_)
#
# ─────────────────────────────────────────────────────────────────────────
# Lalu salin file hasil training ke folder models/:
#   models/tabnet_weight_for_age.zip
#   models/tabnet_height_for_age.zip
#   models/tabnet_weight_for_height.zip
#   models/scaler.joblib
# ─────────────────────────────────────────────────────────────────────────

print("Baca komentar di dalam file ini untuk petunjuk menyimpan scaler.")
