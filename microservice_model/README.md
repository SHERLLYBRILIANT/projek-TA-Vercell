# Panduan Hosting Model TabNet di Hugging Face Spaces (Gratis)

Hugging Face Spaces menyediakan hosting gratis dengan CPU & RAM besar yang mendukung PyTorch tanpa batasan 250 MB seperti Vercel.

### Cara Setup di Hugging Face Spaces (Hanya 2 Menit):
1. Buka [https://huggingface.co/spaces](https://huggingface.co/spaces) dan login/daftar.
2. Klik tombol **"Create new Space"**.
3. Isi data:
   * **Space name**: `gizilens-model` (atau nama lain)
   * **License**: `mit` / `apache-2.0`
   * **Select the Space SDK**: Pilih **Docker** (atau **Blank** lalu pilih Dockerfile)
   * **Space hardware**: `CPU Basic (Free)`
4. Upload file-file berikut ke Space tersebut:
   * `microservice_model/app.py`
   * `microservice_model/requirements.txt`
   * `microservice_model/Dockerfile`
   * File-file model dari folder `models/`:
     - `tabnet_height_for_age.zip`
     - `tabnet_weight_for_age.zip`
     - `tabnet_weight_for_height.zip`
     - `standard_scaler.joblib`
5. Setelah status Space berubah menjadi **Running**:
   * Dapatkan URL Space Anda, misalnya: `https://username-gizilens-model.hf.space`
6. Masukkan URL tersebut ke **Environment Variables** di Vercel:
   * Variable Name: `PREDICTOR_API_URL`
   * Value: `https://username-gizilens-model.hf.space`

