"""
Sistem Prediksi Status Gizi Balita
Backend: Flask + MySQL
Model: TabNet (pytorch-tabnet)
Author: Sistem Prediksi Gizi Balita
"""

import os
import io
import json
import warnings
import traceback
from datetime import datetime, timedelta
from functools import wraps
from xml.sax.saxutils import escape
from dotenv import load_dotenv
import os.path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load environment variables
# Prioritas: .env.local (development lokal) > .env (default)
env_local_path = os.path.join(BASE_DIR, '.env.local')
env_path = os.path.join(BASE_DIR, '.env')

if os.path.isfile(env_local_path):
    load_dotenv(env_local_path, override=True)
load_dotenv(env_path, override=False)

warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, send_file, Response, Request
)
from flask_mysqldb import MySQL
import bcrypt
from werkzeug.utils import secure_filename

# Export
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, LongTable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# ─── Konfigurasi ────────────────────────────────────────────────────────────
app.secret_key = os.environ.get('SECRET_KEY', 'gizi-balita-secret-key-2024')
app.config['MYSQL_HOST']     = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT']     = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_USER']     = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB']       = os.environ.get('MYSQL_DB', 'gizi_balita')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Debug: Log configuration (hapus di production)
if os.environ.get('DEBUG'):
    print(f"[DEBUG] MySQL Config:")
    print(f"  Host: {app.config['MYSQL_HOST']}")
    print(f"  Port: {app.config['MYSQL_PORT']}")
    print(f"  User: {app.config['MYSQL_USER']}")
    print(f"  Password: {'*' * len(app.config['MYSQL_PASSWORD'])}")
    print(f"  Database: {app.config['MYSQL_DB']}")

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
Request.max_form_memory_size = 50 * 1024 * 1024      # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mysql = MySQL(app)

# ─── Load Model TabNet ───────────────────────────────────────────────────────
from utils.predictor import GiziPredictor
predictor = GiziPredictor()

# ─── Decorator Login ─────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'petugas_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def is_admin_jabatan(jabatan):
    jabatan_lower = (jabatan or '').lower()
    return 'admin' in jabatan_lower or 'kepala kesehatan' in jabatan_lower


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Akses ditolak. Hanya Admin yang dapat mengakses fitur ini.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ════════════════════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if 'petugas_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    show_manage = False
    if 'petugas_id' in session:
        show_manage = session.get('is_admin') and request.args.get('manage') == '1'
        if not show_manage:
            return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM petugas WHERE username = %s", (username,))
        petugas = cur.fetchone()
        cur.close()
        if petugas and bcrypt.checkpw(password.encode('utf-8'), petugas['password'].encode('utf-8')):
            session['petugas_id']   = petugas['id']
            session['petugas_nama'] = petugas['nama']
            session['petugas_jabatan'] = petugas['jabatan']
            session['is_admin'] = is_admin_jabatan(petugas.get('jabatan'))
            flash(f'Selamat datang, {petugas["nama"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah.', 'danger')
    return render_template('login.html', show_manage=show_manage, is_admin=session.get('is_admin', False))

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM balita")
    total_balita = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM pemeriksaan")
    total_pemeriksaan = cur.fetchone()['total']

    cur.execute("""
        SELECT COUNT(*) AS total FROM hasil_klasifikasi
        WHERE tbu_label = 'Stunted'
    """)
    total_stunted = cur.fetchone()['total']

    cur.execute("""
        SELECT COUNT(*) AS total FROM hasil_klasifikasi
        WHERE bbu_label = 'Malnutrition'
    """)
    total_malnutrisi = cur.fetchone()['total']

    # Distribusi BB/U
    cur.execute("""
        SELECT bbu_label AS label, COUNT(*) AS jumlah
        FROM hasil_klasifikasi
        GROUP BY bbu_label
    """)
    dist_bbu = cur.fetchall()

    # Distribusi TB/U
    cur.execute("""
        SELECT tbu_label AS label, COUNT(*) AS jumlah
        FROM hasil_klasifikasi
        GROUP BY tbu_label
    """)
    dist_tbu = cur.fetchall()

    # Distribusi BB/TB
    cur.execute("""
        SELECT bbtb_label AS label, COUNT(*) AS jumlah
        FROM hasil_klasifikasi
        GROUP BY bbtb_label
    """)
    dist_bbtb = cur.fetchall()

    # Riwayat terbaru
    cur.execute("""
        SELECT p.id, b.nama AS nama_balita, b.jenis_kelamin,
               p.umur_bulan, p.berat_badan, p.tinggi_badan,
               p.tanggal_periksa,
               h.bbu_label, h.tbu_label, h.bbtb_label
        FROM pemeriksaan p
        JOIN balita b ON p.balita_id = b.id
        LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
        ORDER BY p.tanggal_periksa DESC
        LIMIT 5
    """)
    riwayat_terbaru = cur.fetchall()
    cur.close()

    return render_template('dashboard.html',
        total_balita=total_balita,
        total_pemeriksaan=total_pemeriksaan,
        total_stunted=total_stunted,
        total_malnutrisi=total_malnutrisi,
        dist_bbu=json.dumps(dist_bbu),
        dist_tbu=json.dumps(dist_tbu),
        dist_bbtb=json.dumps(dist_bbtb),
        riwayat_terbaru=riwayat_terbaru
    )

# ════════════════════════════════════════════════════════════════════════════
# INPUT & PREDIKSI
# ════════════════════════════════════════════════════════════════════════════

@app.route('/pemeriksaan', methods=['GET', 'POST'])
@login_required
def pemeriksaan():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama, jenis_kelamin FROM balita ORDER BY nama")
    list_balita = cur.fetchall()
    cur.close()
    return render_template('pemeriksaan.html', list_balita=list_balita)

@app.route('/api/prediksi', methods=['POST'])
@login_required
def api_prediksi():
    """Endpoint AJAX: terima data, simpan ke DB, kembalikan hasil prediksi"""
    try:
        data = request.get_json()
        balita_id    = int(data['balita_id'])
        umur_bulan   = int(data['umur_bulan'])
        berat_badan  = float(data['berat_badan'])
        tinggi_badan = float(data['tinggi_badan'])
        catatan      = data.get('catatan', '')

        # Validasi rentang berat badan wajar untuk balita (2-30 kg)
        if berat_badan < 2 or berat_badan > 30:
            return jsonify({'success': False, 'message': 'Berat badan di luar rentang wajar (2–30 kg)'}), 400

        # Validasi rentang tinggi badan wajar untuk balita (35-130 cm)
        if tinggi_badan < 35 or tinggi_badan > 130:
            return jsonify({'success': False, 'message': 'Tinggi badan di luar rentang wajar (35–130 cm)'}), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM balita WHERE id = %s", (balita_id,))
        balita = cur.fetchone()
        if not balita:
            return jsonify({'success': False, 'message': 'Balita tidak ditemukan'}), 404

        gender_code = 1 if balita['jenis_kelamin'] == 'L' else 0

        # Prediksi TabNet
        hasil = predictor.predict_single(gender_code, umur_bulan, berat_badan, tinggi_badan)

        # Simpan pemeriksaan
        cur.execute("""
            INSERT INTO pemeriksaan (balita_id, petugas_id, umur_bulan, berat_badan, tinggi_badan, catatan)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (balita_id, session['petugas_id'], umur_bulan, berat_badan, tinggi_badan, catatan))
        pemeriksaan_id = cur.lastrowid

        # Simpan hasil klasifikasi
        cur.execute("""
            INSERT INTO hasil_klasifikasi
                (pemeriksaan_id, bbu_label, tbu_label, bbtb_label, bbu_kode, tbu_kode, bbtb_kode, model_digunakan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'TabNet')
        """, (
            pemeriksaan_id,
            hasil['bbu']['label'], hasil['tbu']['label'], hasil['bbtb']['label'],
            hasil['bbu']['kode'],  hasil['tbu']['kode'],  hasil['bbtb']['kode']
        ))
        mysql.connection.commit()
        cur.close()

        return jsonify({
            'success': True,
            'pemeriksaan_id': pemeriksaan_id,
            'balita': {
                'nama': balita['nama'],
                'jenis_kelamin': balita['jenis_kelamin'],
                'umur_bulan': umur_bulan,
                'berat_badan': berat_badan,
                'tinggi_badan': tinggi_badan
            },
            'hasil': hasil
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/balita/tambah', methods=['POST'])
@login_required
def api_tambah_balita():
    """Tambah balita baru via AJAX"""
    try:
        data = request.get_json()
        
        tgl_lahir = data.get('tanggal_lahir')
        if not tgl_lahir:
            return jsonify({'success': False, 'message': 'Tanggal lahir wajib diisi'}), 400
            
        try:
            from datetime import datetime, date
            tgl_obj = datetime.strptime(tgl_lahir, '%Y-%m-%d').date()
            today = date.today()
            try:
                tgl_min = today.replace(year=today.year - 5)
            except ValueError:
                # Handle leap year (Feb 29)
                tgl_min = today.replace(year=today.year - 5, day=28)
            tgl_max = today
            
            if tgl_obj < tgl_min or tgl_obj > tgl_max:
                return jsonify({'success': False, 'message': f'Tanggal lahir harus antara {tgl_min.strftime("%d-%m-%Y")} hingga {tgl_max.strftime("%d-%m-%Y")}'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Format tanggal lahir tidak valid'}), 400
            
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO balita (nama, nik, jenis_kelamin, tanggal_lahir, nama_ibu, alamat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['nama'], data.get('nik',''), data['jenis_kelamin'],
            data['tanggal_lahir'], data.get('nama_ibu',''), data.get('alamat','')
        ))
        mysql.connection.commit()
        balita_id = cur.lastrowid
        cur.close()
        return jsonify({'success': True, 'balita_id': balita_id, 'nama': data['nama']})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/balita/list', methods=['GET'])
@login_required
def api_list_balita():
    """Ambil daftar balita untuk refresh dropdown tanpa reload halaman."""
    try:
        cur = mysql.connection.cursor()
        # Return balita plus latest pemeriksaan (if any) for quick table display
        cur.execute("""
            SELECT b.id, b.nama, b.jenis_kelamin, b.nama_ibu,
                   b.nik,
                   DATE_FORMAT(b.tanggal_lahir, %s) AS tanggal_lahir,
                   b.alamat,
                   p.umur_bulan, p.berat_badan, p.tinggi_badan
            FROM balita b
            LEFT JOIN pemeriksaan p ON p.id = (
                SELECT id FROM pemeriksaan WHERE balita_id = b.id ORDER BY tanggal_periksa DESC LIMIT 1
            )
            ORDER BY b.nama
        """, ('%Y-%m-%d',))
        list_balita = cur.fetchall()
        cur.close()
        return jsonify({'success': True, 'balita': list_balita})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/balita/hapus/<int:balita_id>', methods=['DELETE'])
@login_required
def api_hapus_balita(balita_id):
    """Hapus data balita terpilih beserta riwayat terkait (cascade FK)."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nama FROM balita WHERE id = %s", (balita_id,))
        balita = cur.fetchone()
        if not balita:
            cur.close()
            return jsonify({'success': False, 'message': 'Balita tidak ditemukan'}), 404

        cur.execute("DELETE FROM balita WHERE id = %s", (balita_id,))
        mysql.connection.commit()
        cur.close()

        return jsonify({
            'success': True,
            'balita_id': balita_id,
            'nama': balita['nama']
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ════════════════════════════════════════════════════════════════════════════
# MANAJEMEN PETUGAS (ADMIN ONLY)
# ════════════════════════════════════════════════════════════════════════════

@app.route('/petugas')
@login_required
@admin_required
def petugas():
    return render_template('petugas.html', is_admin=session.get('is_admin', False))


@app.route('/api/petugas/list')
@login_required
@admin_required
def api_petugas_list():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, nama, username, jabatan, puskesmas,
                   DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS created_at
            FROM petugas
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return jsonify({'success': True, 'petugas': rows})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/petugas/tambah', methods=['POST'])
@login_required
@admin_required
def api_petugas_tambah():
    try:
        data = request.get_json() or {}
        nama = (data.get('nama') or '').strip()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        jabatan = (data.get('jabatan') or 'Petugas').strip()
        puskesmas = (data.get('puskesmas') or '').strip()

        if 'kepala kesehatan' in jabatan.lower():
            return jsonify({'success': False, 'message': 'Jabatan Kepala Kesehatan hanya boleh ada 1 orang dan tidak dapat ditambahkan'}), 400

        if not nama or not username or not password:
            return jsonify({'success': False, 'message': 'Nama, username, dan password wajib diisi'}), 400

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO petugas (nama, username, password, jabatan, puskesmas)
            VALUES (%s, %s, %s, %s, %s)
        """, (nama, username, hashed, jabatan, puskesmas))
        mysql.connection.commit()
        new_id = cur.lastrowid
        cur.close()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/petugas/ubah/<int:petugas_id>', methods=['PUT'])
@login_required
@admin_required
def api_petugas_ubah(petugas_id):
    try:
        data = request.get_json() or {}
        nama = (data.get('nama') or '').strip()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        jabatan = (data.get('jabatan') or 'Petugas Gizi').strip()
        puskesmas = (data.get('puskesmas') or '').strip()

        # Get current jabatan
        cur = mysql.connection.cursor()
        cur.execute("SELECT jabatan FROM petugas WHERE id = %s", (petugas_id,))
        current = cur.fetchone()
        if not current:
            return jsonify({'success': False, 'message': 'Data petugas tidak ditemukan'}), 404
        
        current_jabatan = current['jabatan'] or ''
        is_kepala_kesehatan = 'kepala kesehatan' in current_jabatan.lower()
        
        # Jika Kepala Kesehatan, hanya boleh ubah password dan puskesmas
        if is_kepala_kesehatan:
            if not data.get('password_only'):
                return jsonify({'success': False, 'message': 'Kepala Kesehatan hanya dapat mengubah password dan puskesmas'}), 400
            
            # Update password jika ada
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("UPDATE petugas SET password = %s, puskesmas = %s WHERE id = %s", (hashed, puskesmas, petugas_id))
            else:
                cur.execute("UPDATE petugas SET puskesmas = %s WHERE id = %s", (puskesmas, petugas_id))
        else:
            # Untuk petugas lain, boleh ubah semua field
            if 'kepala kesehatan' in jabatan.lower():
                return jsonify({'success': False, 'message': 'Tidak dapat mengubah jabatan menjadi Kepala Kesehatan, hanya boleh ada 1 orang'}), 400

            if not nama or not username:
                return jsonify({'success': False, 'message': 'Nama dan username wajib diisi'}), 400

            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    UPDATE petugas
                    SET nama = %s, username = %s, password = %s, jabatan = %s, puskesmas = %s
                    WHERE id = %s
                """, (nama, username, hashed, jabatan, puskesmas, petugas_id))
            else:
                cur.execute("""
                    UPDATE petugas
                    SET nama = %s, username = %s, jabatan = %s, puskesmas = %s
                    WHERE id = %s
                """, (nama, username, jabatan, puskesmas, petugas_id))
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/petugas/hapus/<int:petugas_id>', methods=['DELETE'])
@login_required
@admin_required
def api_petugas_hapus(petugas_id):
    try:
        if petugas_id == session.get('petugas_id'):
            return jsonify({'success': False, 'message': 'Tidak dapat menghapus akun yang sedang aktif'}), 400

        # Cegah penghapusan Kepala Kesehatan
        cur = mysql.connection.cursor()
        cur.execute("SELECT jabatan FROM petugas WHERE id = %s", (petugas_id,))
        result = cur.fetchone()
        if result:
            jabatan = result['jabatan'] or ''
            if 'kepala kesehatan' in jabatan.lower():
                return jsonify({'success': False, 'message': 'Kepala Kesehatan tidak dapat dihapus'}), 400
        
        cur.execute("DELETE FROM petugas WHERE id = %s", (petugas_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ════════════════════════════════════════════════════════════════════════════
# HASIL PREDIKSI (detail halaman)
# ════════════════════════════════════════════════════════════════════════════

@app.route('/hasil/<int:pemeriksaan_id>')
@login_required
def hasil(pemeriksaan_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, b.nama AS nama_balita, b.jenis_kelamin, b.tanggal_lahir,
               b.nama_ibu, b.alamat,
               h.bbu_label, h.tbu_label, h.bbtb_label,
               h.model_digunakan, h.created_at AS tgl_hasil,
               pt.nama AS nama_petugas, pt.puskesmas
        FROM pemeriksaan p
        JOIN balita b ON p.balita_id = b.id
        LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
        LEFT JOIN petugas pt ON p.petugas_id = pt.id
        WHERE p.id = %s
    """, (pemeriksaan_id,))
    data = cur.fetchone()
    cur.close()
    if not data:
        flash('Data pemeriksaan tidak ditemukan.', 'danger')
        return redirect(url_for('riwayat'))
    return render_template('hasil.html', data=data)

# ════════════════════════════════════════════════════════════════════════════
# BATCH UPLOAD
# ════════════════════════════════════════════════════════════════════════════

@app.route('/batch')
@login_required
def batch():
    return render_template('batch.html')

@app.route('/api/batch/upload', methods=['POST'])
@login_required
def api_batch_upload():
    """Upload dan prediksi batch CSV/Excel"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Tidak ada file yang diunggah'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Format file tidak valid (gunakan CSV atau Excel)'}), 400
    try:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Validasi kolom
        required_cols = {'jenis_kelamin', 'umur_bulan', 'berat_badan', 'tinggi_badan'}
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        missing = required_cols - set(df.columns)
        if missing:
            return jsonify({'success': False,
                            'message': f'Kolom wajib tidak ditemukan: {", ".join(missing)}'}), 400

        results = []
        for idx, row in df.iterrows():
            try:
                gender = row['jenis_kelamin']
                gender_code = 1 if str(gender).upper() in ['L', '1', 'LAKI', 'LAKI-LAKI'] else 0
                umur   = int(row['umur_bulan'])
                bb     = float(row['berat_badan'])
                tb     = float(row['tinggi_badan'])
                nama   = row.get('nama', f'Balita {idx+1}')

                hasil  = predictor.predict_single(gender_code, umur, bb, tb)
                results.append({
                    'no': idx + 1,
                    'nama': str(nama),
                    'jenis_kelamin': 'L' if gender_code == 1 else 'P',
                    'umur_bulan': umur,
                    'berat_badan': bb,
                    'tinggi_badan': tb,
                    'bbu': hasil['bbu']['label'],
                    'tbu': hasil['tbu']['label'],
                    'bbtb': hasil['bbtb']['label'],
                })
            except Exception as e:
                results.append({
                    'no': idx + 1,
                    'nama': str(row.get('nama', f'Baris {idx+1}')),
                    'error': str(e)
                })

        return jsonify({'success': True, 'total': len(results), 'results': results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# ════════════════════════════════════════════════════════════════════════════
# RIWAYAT
# ════════════════════════════════════════════════════════════════════════════

@app.route('/riwayat')
@login_required
def riwayat():
    page      = int(request.args.get('page', 1))
    per_page  = 15
    offset    = (page - 1) * per_page
    search    = request.args.get('search', '').strip()

    cur = mysql.connection.cursor()
    where = "WHERE 1=1"
    params = []
    if search:
        where += " AND b.nama LIKE %s"
        params.append(f'%{search}%')

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM pemeriksaan p
        JOIN balita b ON p.balita_id = b.id
        LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
        {where}
    """, params)
    total = cur.fetchone()['total']

    cur.execute(f"""
        SELECT p.id, b.nama AS nama_balita, b.jenis_kelamin,
               p.umur_bulan, p.berat_badan, p.tinggi_badan,
               p.tanggal_periksa,
               h.bbu_label, h.tbu_label, h.bbtb_label,
               pt.nama AS nama_petugas
        FROM pemeriksaan p
        JOIN balita b ON p.balita_id = b.id
        LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
        LEFT JOIN petugas pt ON p.petugas_id = pt.id
        {where}
        ORDER BY p.tanggal_periksa DESC
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])
    rows = cur.fetchall()
    cur.close()

    total_pages = (total + per_page - 1) // per_page
    return render_template('riwayat.html',
        rows=rows, page=page, total_pages=total_pages,
        total=total, search=search
    )

# ════════════════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════════════════

@app.route('/export/excel')
@login_required
def export_excel():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT b.nama AS 'Nama Balita', b.jenis_kelamin AS 'JK',
               p.umur_bulan AS 'Umur (bulan)', p.berat_badan AS 'BB (kg)',
               p.tinggi_badan AS 'TB (cm)', p.tanggal_periksa AS 'Tgl Periksa',
               h.bbu_label AS 'BB/U', h.tbu_label AS 'TB/U', h.bbtb_label AS 'BB/TB',
               pt.nama AS 'Petugas'
        FROM pemeriksaan p
        JOIN balita b ON p.balita_id = b.id
        LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
        LEFT JOIN petugas pt ON p.petugas_id = pt.id
        ORDER BY p.tanggal_periksa DESC
    """)
    rows = cur.fetchall()
    cur.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Riwayat Pemeriksaan"

    # Header style
    header_fill = PatternFill("solid", fgColor="1E3A5F")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    center = Alignment(horizontal='center', vertical='center')
    thin = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # Title
    ws.merge_cells('A1:K1')
    ws['A1'] = 'RIWAYAT PEMERIKSAAN STATUS GIZI BALITA'
    ws['A1'].font = Font(bold=True, size=13, color="1E3A5F")
    ws['A1'].alignment = center
    ws['A2'] = f'Diekspor: {datetime.now().strftime("%d/%m/%Y")}'
    ws['A2'].alignment = center
    ws.merge_cells('A2:K2')

    # Header row
    headers = ['Nama Balita', 'JK', 'Umur (bulan)', 'BB (kg)', 'TB (cm)', 'Tgl Periksa', 'BB/U', 'TB/U', 'BB/TB', 'Petugas', 'Saran Sistem']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center
        cell.border = thin

    # Data
    if rows:
        alt_fill = PatternFill("solid", fgColor="EBF5FB")
        for row_idx, row in enumerate(rows, 5):
            tgl = row['Tgl Periksa']
            tgl_str = tgl.strftime('%d/%m/%Y') if (tgl and hasattr(tgl, 'strftime')) else str(tgl or '-')
            saran_detail = _build_saran_kombinasi(row['BB/U'], row['TB/U'], row['BB/TB'])
            saran_text = saran_detail['saran']
            
            vals = [
                row['Nama Balita'],
                row['JK'],
                row['Umur (bulan)'],
                row['BB (kg)'],
                row['TB (cm)'],
                tgl_str,
                row['BB/U'],
                row['TB/U'],
                row['BB/TB'],
                row['Petugas'],
                saran_text
            ]
            for col_idx, val in enumerate(vals, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin
                if row_idx % 2 == 0:
                    cell.fill = alt_fill

        # Auto width (skip MergedCell)
        from openpyxl.cell.cell import MergedCell
        for col in ws.columns:
            max_len = 0
            col_letter = None
            for c in col:
                if isinstance(c, MergedCell):
                    continue
                col_letter = c.column_letter
                try:
                    max_len = max(max_len, len(str(c.value)) if c.value else 0)
                except:
                    pass
            if col_letter:
                ws.column_dimensions[col_letter].width = min(max_len + 4, 30)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=f'riwayat_gizi_{datetime.now().strftime("%Y%m%d")}.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def _format_pdf_datetime(value, fmt='%d/%m/%Y'):
    if not value:
        return '-'
    if isinstance(value, str):
        return value
    return value.strftime(fmt)


def _pdf_text(value):
    if value is None or value == '':
        return '-'
    return escape(str(value)).replace('\n', '<br/>')


def _build_saran_kombinasi(bbu_label, tbu_label, bbtb_label):
    """Return detail rekomendasi berbasis kombinasi 3 label status gizi."""
    bbu   = (bbu_label or '').strip()
    tbu   = (tbu_label or '').strip()
    bbtb  = (bbtb_label or '').strip()

    is_stunting    = tbu == 'Stunted'
    is_thin        = bbtb in ('Very Thin', 'Thin')
    is_obese       = bbtb == 'Obese'
    is_overweight_age = bbu == 'Overnutrition'
    is_underweight = bbu in ('Malnutrition', 'Underfed')

    kombinasi = f'BB/U: {bbu or "-"} | TB/U: {tbu or "-"} | BB/TB: {bbtb or "-"}'

    # 1. Pengecekan Kombinasi Tidak Valid (Kesalahan Pengukuran)
    is_error_1 = tbu in ('Normal', 'Not Stunted') and is_obese and is_underweight
    is_error_2 = is_thin and is_overweight_age
    if is_error_1 or is_error_2:
        return {
            'judul': '⚠ Hasil Tidak Valid: Indikator Bertentangan',
            'analisis': f'{kombinasi}. Kombinasi hasil ini secara fisik tidak mungkin (misal: kurus tapi berat badan berlebih, atau tinggi normal obesitas tapi berat kurang).',
            'saran': 'Terdapat indikasi kesalahan pengukuran. Harap ulangi pengukuran berat dan tinggi badan dengan alat yang sudah dikalibrasi.',
            'warna': '#FEFD99',
        }

    # 2. Normal
    if bbu == 'Normal' and tbu in ('Normal', 'Not Stunted') and bbtb == 'Normal':
        return {
            'judul': '✓ Status Gizi Normal & Proporsional',
            'analisis': f'{kombinasi}. Ketiga indikator selaras dan tidak menunjukkan tanda risiko utama saat ini.',
            'saran': 'Pertahankan pola makan bergizi seimbang, variasikan sumber protein, dan lanjutkan pemantauan rutin di Posyandu.',
            'warna': '#9ED3DC',
        }

    # 3. Kritis: Stunting & Kurus / Sangat Kurus
    if is_stunting and is_thin:
        return {
            'judul': '⚠ Kondisi Kritis: Stunting & Kurus',
            'analisis': f'{kombinasi}. Pertumbuhan tinggi terhambat (stunting) disertai berat badan sangat kurang untuk tingginya (kurus/sangat kurus).',
            'saran': 'Segera rujuk ke dokter anak atau puskesmas untuk evaluasi medis, penanganan gizi terapeutik, dan pemeriksaan infeksi penyerta.',
            'warna': '#FCB7C7',
        }

    # 4. Beban Ganda: Stunting & Obesitas
    if is_stunting and is_obese:
        return {
            'judul': '⚠ Beban Ganda: Stunting & Obesitas',
            'analisis': f'{kombinasi}. Anak pendek menurut usia (stunting) namun memiliki berat badan berlebih untuk tingginya (obesitas).',
            'saran': 'JANGAN melakukan diet penurunan berat badan ekstrem. Fokus perbaikan kualitas makanan (tinggi protein, kaya mikronutrien), batasi gula/makanan manis, dan tingkatkan aktivitas fisik ringan sampai sedang.',
            'warna': '#FCB7C7',
        }

    # 5. Stunting & Underweight (BB/U rendah, BB/TB Normal)
    if is_stunting and is_underweight:
        return {
            'judul': '⚠ Risiko Gizi Kurang Kronis: Stunting & Berat Kurang',
            'analisis': f'{kombinasi}. Tinggi dan berat badan kurang menurut usia, namun proporsi berat terhadap tinggi (BB/TB) masih dalam batas proporsional.',
            'saran': 'Tingkatkan asupan energi dan protein (terutama hewani) secara bertahap. Pantau rutin pertumbuhan bersama tenaga kesehatan.',
            'warna': '#FCB7C7',
        }

    # 6. Hanya Stunting
    if is_stunting:
        return {
            'judul': '⚠ Peringatan: Indikasi Stunting',
            'analisis': f'{kombinasi}. Tinggi badan berada di bawah standar usia, tetapi proporsi berat badan terhadap tinggi masih normal.',
            'saran': 'Perbaiki kualitas diet dengan protein hewani, zat besi, dan seng. Konsultasikan ke faskes bila tinggi tidak bertambah dalam beberapa bulan.',
            'warna': '#FCB7C7',
        }

    # 7. Kurus / Sangat Kurus (Tidak Stunting)
    if is_thin:
        return {
            'judul': '⚠ Peringatan: Kurus / Sangat Kurus (Risiko Gizi Akut)',
            'analisis': f'{kombinasi}. Proporsi berat terhadap tinggi di bawah normal (kurus), menandakan kekurangan asupan atau infeksi relatif baru.',
            'saran': 'Naikkan asupan energi dan protein dengan porsi kecil namun sering, dan periksa kemungkinan infeksi atau gangguan pencernaan ke faskes.',
            'warna': '#FCB7C7',
        }

    # 8. Obesitas / Kelebihan Gizi (Tidak Stunting)
    if is_obese or is_overweight_age:
        return {
            'judul': '🔴 Perhatian: Risiko Obesitas / Kelebihan Gizi',
            'analisis': f'{kombinasi}. Berat badan relatif tinggi (obesitas atau kelebihan gizi) tanpa disertai stunting.',
            'saran': 'Batasi minuman manis dan makanan olahan (ultra-proses). Perbanyak sayur, buah, dan aktivitas fisik. Hindari diet ketat tanpa pengawasan.',
            'warna': '#FEFD99',
        }

    # 9. Underweight / Berat Kurang (Tidak Stunting, BB/TB Normal)
    if is_underweight:
        return {
            'judul': '🟠 Pantau Ketat: Berat Badan Kurang',
            'analisis': f'{kombinasi}. Berat badan di bawah kurva normal seusianya, meski tinggi dan proporsi tubuh (BB/TB) masih wajar.',
            'saran': 'Evaluasi nafsu makan dan asupan harian. Tingkatkan frekuensi makan atau kalori secara bertahap, pantau kenaikan berat bulan depan.',
            'warna': '#FEFD99',
        }

    # 10. Fallback
    return {
        'judul': 'ℹ Informasi Status Gizi Terpadu',
        'analisis': f'{kombinasi}. Kombinasi ini memerlukan observasi lebih lanjut melihat tren pertumbuhan di KMS/Buku KIA.',
        'saran': 'Lanjutkan pola makan gizi seimbang, ulang pemantauan pertumbuhan secara berkala, dan evaluasi ke tenaga kesehatan bila tren tidak wajar.',
        'warna': '#9ED3DC',
    }


def _get_saran_pdf(bbu_label, tbu_label, bbtb_label):
    """Return (judul, isi, warna_hex) saran sistem berdasarkan label klasifikasi."""
    detail = _build_saran_kombinasi(bbu_label, tbu_label, bbtb_label)
    return detail['judul'], detail['saran'], detail['warna']


@app.route('/export/pdf', defaults={'pemeriksaan_id': None})
@app.route('/export/pdf/<int:pemeriksaan_id>')
@login_required
def export_pdf(pemeriksaan_id):
    cur = mysql.connection.cursor()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'pdf_title',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#1E3A5F'),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'pdf_subtitle',
        parent=styles['Normal'],
        alignment=1,
        fontSize=9,
        textColor=colors.HexColor('#64748B'),
    )
    section_style = ParagraphStyle(
        'pdf_section',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#1E3A5F'),
        spaceBefore=8,
        spaceAfter=6,
    )
    label_style = ParagraphStyle(
        'pdf_label',
        parent=styles['BodyText'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#4B5563'),
    )
    value_style = ParagraphStyle(
        'pdf_value',
        parent=styles['BodyText'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#111827'),
    )
    cell_style = ParagraphStyle(
        'pdf_cell',
        parent=styles['BodyText'],
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#111827'),
    )

    def build_profile_table(profile):
        table_data = [
            [Paragraph('Nama Balita', label_style), Paragraph(_pdf_text(profile.get('nama_balita')), value_style)],
            [Paragraph('NIK', label_style), Paragraph(_pdf_text(profile.get('nik')), value_style)],
            [Paragraph('Jenis Kelamin', label_style), Paragraph(_pdf_text('Laki-laki' if profile.get('jenis_kelamin') == 'L' else 'Perempuan'), value_style)],
            [Paragraph('Tanggal Lahir', label_style), Paragraph(_pdf_text(_format_pdf_datetime(profile.get('tanggal_lahir'), '%d/%m/%Y')), value_style)],
            [Paragraph('Nama Ibu', label_style), Paragraph(_pdf_text(profile.get('nama_ibu')), value_style)],
            [Paragraph('Alamat', label_style), Paragraph(_pdf_text(profile.get('alamat')), value_style)],
        ]
        table = Table(table_data, colWidths=[4.0*cm, 11.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        return table

    def build_history_table(history_rows, selected_id=None):
        headers = ['No', 'Tanggal', 'Umur', 'BB', 'TB', 'BB/U', 'TB/U', 'BB/TB', 'Petugas', 'Saran Sistem']
        table_data = [headers]
        for idx, row in enumerate(history_rows, 1):
            _, saran_isi, _ = _get_saran_pdf(
                row.get('bbu_label'), row.get('tbu_label'), row.get('bbtb_label')
            )
            table_data.append([
                idx,
                Paragraph(_pdf_text(_format_pdf_datetime(row.get('tanggal_periksa'))), cell_style),
                Paragraph(_pdf_text(row.get('umur_bulan')), cell_style),
                Paragraph(_pdf_text(row.get('berat_badan')), cell_style),
                Paragraph(_pdf_text(row.get('tinggi_badan')), cell_style),
                Paragraph(_pdf_text(row.get('bbu_label')), cell_style),
                Paragraph(_pdf_text(row.get('tbu_label')), cell_style),
                Paragraph(_pdf_text(row.get('bbtb_label')), cell_style),
                Paragraph(_pdf_text(row.get('nama_petugas') or '-'), cell_style),
                Paragraph(_pdf_text(saran_isi), cell_style),
            ])

        table = LongTable(
            table_data,
            repeatRows=1,
            colWidths=[0.65*cm, 2.2*cm, 1.1*cm, 1.1*cm, 1.1*cm, 1.7*cm, 1.7*cm, 1.7*cm, 2.3*cm, 4.25*cm]
        )
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]
        if selected_id is not None:
            for row_idx, row in enumerate(history_rows, 1):
                if row.get('id') == selected_id:
                    style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#FEFD99')))
                    style_commands.append(('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'))
        table.setStyle(TableStyle(style_commands))
        return table

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.3*cm
    )
    story = []
    story.append(Paragraph('RIWAYAT PEMERIKSAAN STATUS GIZI BALITA', title_style))
    story.append(Paragraph(f'Diekspor: {datetime.now().strftime("%d/%m/%Y")}', subtitle_style))
    story.append(Spacer(1, 0.45*cm))

    if pemeriksaan_id is None:
        cur.execute("""
            SELECT p.id, b.nama AS nama_balita, b.jenis_kelamin,
                   p.umur_bulan, p.berat_badan, p.tinggi_badan,
                   p.tanggal_periksa,
                   h.bbu_label, h.tbu_label, h.bbtb_label,
                   pt.nama AS nama_petugas
            FROM pemeriksaan p
            JOIN balita b ON p.balita_id = b.id
            LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
            LEFT JOIN petugas pt ON p.petugas_id = pt.id
            ORDER BY p.tanggal_periksa DESC
            LIMIT 500
        """)
        rows = cur.fetchall()
        cur.close()

        story.append(Paragraph('Laporan Semua Riwayat Pemeriksaan', section_style))
        story.append(build_history_table(rows))
    else:
        cur.execute("""
            SELECT p.id, p.balita_id, p.umur_bulan, p.berat_badan, p.tinggi_badan,
                   p.tanggal_periksa,
                   b.nama AS nama_balita, b.nik, b.jenis_kelamin, b.tanggal_lahir,
                   b.nama_ibu, b.alamat,
                   h.bbu_label, h.tbu_label, h.bbtb_label, h.model_digunakan,
                   pt.nama AS nama_petugas, pt.puskesmas
            FROM pemeriksaan p
            JOIN balita b ON p.balita_id = b.id
            LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
            LEFT JOIN petugas pt ON p.petugas_id = pt.id
            WHERE p.id = %s
        """, (pemeriksaan_id,))
        current = cur.fetchone()
        if not current:
            cur.close()
            flash('Data pemeriksaan tidak ditemukan.', 'danger')
            return redirect(url_for('riwayat'))

        cur.execute("""
            SELECT p.id, p.umur_bulan, p.berat_badan, p.tinggi_badan,
                   p.tanggal_periksa,
                   h.bbu_label, h.tbu_label, h.bbtb_label,
                   pt.nama AS nama_petugas
            FROM pemeriksaan p
            LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
            LEFT JOIN petugas pt ON p.petugas_id = pt.id
            WHERE p.balita_id = %s
            ORDER BY p.tanggal_periksa DESC
        """, (current['balita_id'],))
        history_rows = cur.fetchall()
        cur.close()

        story.append(Paragraph('Profil Balita', section_style))
        story.append(build_profile_table(current))
        story.append(Spacer(1, 0.35*cm))

        story.append(Paragraph('Ringkasan Pemeriksaan Terpilih', section_style))
        saran_ringkas_judul, saran_ringkas_isi, _ = _get_saran_pdf(
            current.get('bbu_label'), current.get('tbu_label'), current.get('bbtb_label')
        )
        summary_rows = [
            ['Tanggal Pemeriksaan', _format_pdf_datetime(current.get('tanggal_periksa'))],
            ['Umur', f"{current.get('umur_bulan', '-')} bulan"],
            ['Berat Badan', f"{current.get('berat_badan', '-')} kg"],
            ['Tinggi Badan', f"{current.get('tinggi_badan', '-')} cm"],
            ['BB/U', current.get('bbu_label') or '-'],
            ['TB/U', current.get('tbu_label') or '-'],
            ['BB/TB', current.get('bbtb_label') or '-'],
            ['Petugas', current.get('nama_petugas') or '-'],
            ['Puskesmas', current.get('puskesmas') or '-'],
            ['Model AI', current.get('model_digunakan') or '-'],
            ['Saran Sistem', saran_ringkas_isi],
        ]
        summary_table = Table(
            [[Paragraph(_pdf_text(label), label_style), Paragraph(_pdf_text(value), value_style)] for label, value in summary_rows],
            colWidths=[4.0*cm, 11.5*cm]
        )
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.35*cm))

        story.append(Paragraph('Riwayat Pemeriksaan Lengkap', section_style))
        story.append(build_history_table(history_rows, selected_id=pemeriksaan_id))
        story.append(Spacer(1, 0.45*cm))

    doc.build(story)
    buf.seek(0)
    if pemeriksaan_id is None:
        download_name = f'riwayat_gizi_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    else:
        safe_name = secure_filename((current.get('nama_balita') or 'balita').replace(' ', '_'))
        download_name = f'riwayat_{safe_name}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    return send_file(buf, as_attachment=True, download_name=download_name, mimetype='application/pdf')


@app.route('/export/grafik/pdf/<int:balita_id>')
@login_required
def export_grafik_pdf(balita_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, nama, nik, jenis_kelamin,
               tanggal_lahir, nama_ibu, alamat
        FROM balita
        WHERE id = %s
    """, (balita_id,))
    balita = cur.fetchone()
    if not balita:
        cur.close()
        flash('Data balita tidak ditemukan.', 'danger')
        return redirect(url_for('grafik_pertumbuhan'))

    cur.execute("""
        SELECT p.id, p.umur_bulan, p.berat_badan, p.tinggi_badan,
               p.tanggal_periksa,
               h.bbu_label, h.tbu_label, h.bbtb_label,
               pt.nama AS nama_petugas, p.catatan
        FROM pemeriksaan p
        LEFT JOIN hasil_klasifikasi h ON h.pemeriksaan_id = p.id
        LEFT JOIN petugas pt ON p.petugas_id = pt.id
        WHERE p.balita_id = %s
        ORDER BY p.tanggal_periksa ASC
    """, (balita_id,))
    riwayat = cur.fetchall()
    cur.close()

    if not riwayat:
        flash('Belum ada riwayat pemeriksaan untuk balita ini.', 'warning')
        return redirect(url_for('grafik_pertumbuhan'))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.3*cm
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'grafik_title',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#1E3A5F')
    )
    subtitle_style = ParagraphStyle(
        'grafik_sub',
        parent=styles['Normal'],
        alignment=1,
        fontSize=9,
        textColor=colors.HexColor('#64748B')
    )
    section_style = ParagraphStyle(
        'grafik_section',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#1E3A5F'),
        spaceBefore=8,
        spaceAfter=6
    )
    label_style = ParagraphStyle(
        'grafik_label',
        parent=styles['BodyText'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#4B5563')
    )
    value_style = ParagraphStyle(
        'grafik_value',
        parent=styles['BodyText'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#111827')
    )
    cell_style = ParagraphStyle(
        'grafik_cell',
        parent=styles['BodyText'],
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#111827')
    )

    def build_line_chart(title, points, x_label, y_label, line_color, width=16.9 * cm, height=6.2 * cm):
        if not points:
            return Paragraph('Tidak ada data untuk menampilkan grafik.', value_style)

        x_values = [point[0] for point in points]
        y_values = [point[1] for point in points]
        x_min = min(x_values)
        x_max = max(x_values)
        y_min = min(y_values)
        y_max = max(y_values)

        if x_min == x_max:
            x_min -= 1
            x_max += 1
        if y_min == y_max:
            y_min -= 1
            y_max += 1

        x_padding = max((x_max - x_min) * 0.12, 1)
        y_padding = max((y_max - y_min) * 0.18, 1)

        drawing = Drawing(width, height)
        plot = LinePlot()
        plot.x = 42
        plot.y = 28
        plot.width = width - 62
        plot.height = height - 60
        plot.data = [points]
        plot.lines[0].strokeColor = line_color
        plot.lines[0].strokeWidth = 2.4
        plot.lines[0].symbol = makeMarker('FilledCircle')
        plot.lines[0].symbol.size = 5
        plot.lines[0].symbol.fillColor = line_color
        plot.lines[0].symbol.strokeColor = colors.white
        plot.lines[0].symbol.strokeWidth = 1
        plot.xValueAxis.valueMin = x_min - x_padding
        plot.xValueAxis.valueMax = x_max + x_padding
        plot.xValueAxis.valueStep = max(1, round((x_max - x_min) / 4) or 1)
        plot.xValueAxis.labelTextFormat = lambda value: f'{value:g}'
        plot.xValueAxis.labels.fontName = 'Helvetica'
        plot.xValueAxis.labels.fontSize = 7
        plot.xValueAxis.labels.fillColor = colors.HexColor('#475569')
        plot.yValueAxis.valueMin = max(0, y_min - y_padding)
        plot.yValueAxis.valueMax = y_max + y_padding
        plot.yValueAxis.valueStep = max(1, round((y_max - y_min) / 4) or 1)
        plot.yValueAxis.labelTextFormat = lambda value: f'{value:g}'
        plot.yValueAxis.labels.fontName = 'Helvetica'
        plot.yValueAxis.labels.fontSize = 7
        plot.yValueAxis.labels.fillColor = colors.HexColor('#475569')
        plot.strokeColor = colors.HexColor('#CBD5E1')
        plot.fillColor = colors.white
        drawing.add(plot)
        return drawing

    def chart_points_from_rows(x_key, y_key):
        points = []
        for row in riwayat:
            try:
                x_value = float(row.get(x_key))
                y_value = float(row.get(y_key))
            except (TypeError, ValueError):
                continue
            points.append((x_value, y_value))
        return points

    def profile_table():
        data = [
            [Paragraph('Nama Balita', label_style), Paragraph(_pdf_text(balita.get('nama')), value_style)],
            [Paragraph('NIK', label_style), Paragraph(_pdf_text(balita.get('nik')), value_style)],
            [Paragraph('Jenis Kelamin', label_style), Paragraph(_pdf_text('Laki-laki' if balita.get('jenis_kelamin') == 'L' else 'Perempuan'), value_style)],
            [Paragraph('Tanggal Lahir', label_style), Paragraph(_pdf_text(_format_pdf_datetime(balita.get('tanggal_lahir'), '%d/%m/%Y')), value_style)],
            [Paragraph('Nama Ibu', label_style), Paragraph(_pdf_text(balita.get('nama_ibu')), value_style)],
            [Paragraph('Alamat', label_style), Paragraph(_pdf_text(balita.get('alamat')), value_style)],
        ]
        table = Table(data, colWidths=[4.0*cm, 11.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        return table

    def history_table():
        headers = ['No', 'Tanggal', 'Umur', 'BB', 'TB', 'BB/U', 'TB/U', 'BB/TB', 'Petugas', 'Saran Sistem']
        data = [headers]
        for idx, row in enumerate(riwayat, 1):
            _, saran_isi, _ = _get_saran_pdf(
                row.get('bbu_label'), row.get('tbu_label'), row.get('bbtb_label')
            )
            data.append([
                idx,
                Paragraph(_pdf_text(_format_pdf_datetime(row.get('tanggal_periksa'))), cell_style),
                Paragraph(_pdf_text(row.get('umur_bulan')), cell_style),
                Paragraph(_pdf_text(row.get('berat_badan')), cell_style),
                Paragraph(_pdf_text(row.get('tinggi_badan')), cell_style),
                Paragraph(_pdf_text(row.get('bbu_label')), cell_style),
                Paragraph(_pdf_text(row.get('tbu_label')), cell_style),
                Paragraph(_pdf_text(row.get('bbtb_label')), cell_style),
                Paragraph(_pdf_text(row.get('nama_petugas')), cell_style),
                Paragraph(_pdf_text(saran_isi), cell_style),
            ])

        table = LongTable(
            data,
            repeatRows=1,
            colWidths=[0.65*cm, 2.2*cm, 1.1*cm, 1.1*cm, 1.1*cm, 1.7*cm, 1.7*cm, 1.7*cm, 2.3*cm, 4.25*cm]
        )
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        return table

    latest = riwayat[-1]
    summary_rows = [
        ['Tanggal Pemeriksaan Terakhir', _pdf_text(_format_pdf_datetime(latest.get('tanggal_periksa')))],
        ['Umur Terakhir', f"{latest.get('umur_bulan', '-')} bulan"],
        ['Berat Badan Terakhir', f"{latest.get('berat_badan', '-')} kg"],
        ['Tinggi Badan Terakhir', f"{latest.get('tinggi_badan', '-')} cm"],
        ['BB/U Terakhir', latest.get('bbu_label') or '-'],
        ['TB/U Terakhir', latest.get('tbu_label') or '-'],
        ['BB/TB Terakhir', latest.get('bbtb_label') or '-'],
    ]
    summary_table = Table(
        [[Paragraph(_pdf_text(label), label_style), Paragraph(_pdf_text(value), value_style)] for label, value in summary_rows],
        colWidths=[4.0*cm, 11.5*cm]
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(Paragraph('LAPORAN GRAFIK PERTUMBUHAN ANAK', title_style))
    story.append(Paragraph(f'Diekspor: {datetime.now().strftime("%d/%m/%Y")}', subtitle_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph('Profil Balita', section_style))
    story.append(profile_table())
    story.append(Spacer(1, 0.35*cm))
    story.append(Paragraph('Tiga Grafik Pertumbuhan', section_style))
    story.append(Spacer(1, 0.12*cm))
    story.append(Paragraph('1. Kurva Berat Badan Menurut Umur (BB/U)', label_style))
    story.append(build_line_chart('BB/U', chart_points_from_rows('umur_bulan', 'berat_badan'), 'Umur (bulan)', 'Berat Badan (kg)', colors.HexColor('#9ED3DC')))
    story.append(Spacer(1, 0.22*cm))
    story.append(Paragraph('2. Kurva Tinggi Badan Menurut Umur (TB/U)', label_style))
    story.append(build_line_chart('TB/U', chart_points_from_rows('umur_bulan', 'tinggi_badan'), 'Umur (bulan)', 'Tinggi Badan (cm)', colors.HexColor('#CA6180')))
    story.append(Spacer(1, 0.22*cm))
    story.append(Paragraph('3. Kurva Berat Badan Menurut Tinggi Badan (BB/TB)', label_style))
    story.append(build_line_chart('BB/TB', chart_points_from_rows('tinggi_badan', 'berat_badan'), 'Tinggi Badan (cm)', 'Berat Badan (kg)', colors.HexColor('#D4AF37')))
    story.append(Spacer(1, 0.35*cm))
    story.append(Paragraph('Riwayat Pemeriksaan Lengkap', section_style))
    story.append(history_table())
    story.append(Spacer(1, 0.45*cm))

    doc.build(story)
    buf.seek(0)
    safe_name = secure_filename((balita.get('nama') or 'balita').replace(' ', '_'))
    return send_file(
        buf,
        as_attachment=True,
        download_name=f'grafik_pertumbuhan_{safe_name}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
        mimetype='application/pdf'
    )

@app.route('/export/batch/excel', methods=['POST'])
@login_required
def export_batch_excel():
    import json
    results_raw = request.form.get('results')
    if not results_raw:
        flash('Tidak ada data batch untuk diekspor.', 'warning')
        return redirect(url_for('batch'))
    try:
        results = json.loads(results_raw)
    except Exception as e:
        flash('Data ekspor tidak valid.', 'danger')
        return redirect(url_for('batch'))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hasil Prediksi Batch"
    header_fill = PatternFill("solid", fgColor="1E3A5F")
    header_font = Font(bold=True, color="FFFFFF")
    thin = Border(left=Side(style='thin'), right=Side(style='thin'),
                  top=Side(style='thin'), bottom=Side(style='thin'))
    center = Alignment(horizontal='center', vertical='center')

    headers = ['No','Nama','JK','Umur (bulan)','BB (kg)','TB (cm)','BB/U','TB/U','BB/TB','Saran Sistem']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center
        cell.border = thin

    for r in results:
        if r.get('error'):
            row = [r.get('no'), r.get('nama'), '', '', '', '', '', '', '', f"Error: {r.get('error')}"]
        else:
            saran_detail = _build_saran_kombinasi(r.get('bbu'), r.get('tbu'), r.get('bbtb'))
            saran_text = saran_detail['saran']
            row = [r.get('no'), r.get('nama'), r.get('jenis_kelamin'),
                   r.get('umur_bulan'), r.get('berat_badan'), r.get('tinggi_badan'),
                   r.get('bbu','-'), r.get('tbu','-'), r.get('bbtb','-'),
                   saran_text]
        ws.append(row)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=f'prediksi_batch_{datetime.now().strftime("%Y%m%d")}.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ════════════════════════════════════════════════════════════════════════════
# INFORMASI MODEL AI
# ════════════════════════════════════════════════════════════════════════════

@app.route('/informasi_model')
@login_required
def informasi_model():
    """Halaman informasi model TabNet dan hasil evaluasinya"""
    return render_template('informasi_model.html')

@app.route('/api/model_info')
@login_required
def api_model_info():
    """API endpoint: kembalikan data evaluasi model"""
    try:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        eval_path = os.path.join(model_dir, 'model_evaluation.json')
        
        with open(eval_path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        
        return jsonify({'success': True, 'data': model_data})
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'model_evaluation.json not found'}), 404
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'message': f'JSON decode error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Test route (tanpa login requirement untuk debugging)
@app.route('/api/model_info_test')
def api_model_info_test():
    """Test endpoint tanpa login - gunakan untuk debugging"""
    try:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        eval_path = os.path.join(model_dir, 'model_evaluation.json')
        
        with open(eval_path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        
        return jsonify({'success': True, 'data': model_data})
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'model_evaluation.json not found'}), 404
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'message': f'JSON decode error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ════════════════════════════════════════════════════════════════════════════
# GRAFIK PERTUMBUHAN
# ════════════════════════════════════════════════════════════════════════════

@app.route('/grafik_pertumbuhan')
@login_required
def grafik_pertumbuhan():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama, jenis_kelamin FROM balita ORDER BY nama")
    list_balita = cur.fetchall()
    cur.close()
    return render_template('grafik_pertumbuhan.html', list_balita=list_balita)

@app.route('/api/grafik_data/<int:balita_id>')
@login_required
def api_grafik_data(balita_id):
    """Endpoint AJAX: ambil riwayat pertumbuhan anak untuk grafik"""
    try:
        # Use DictCursor to return rows as dictionaries
        cur = mysql.connection.cursor()
        
        # Debug: Log the query execution
        query = """
            SELECT p.umur_bulan, p.berat_badan, p.tinggi_badan,
                   DATE_FORMAT(p.tanggal_periksa, '%%d/%%m/%%Y') AS tgl_format,
                   p.tanggal_periksa
            FROM pemeriksaan p
            WHERE p.balita_id = %s
            ORDER BY p.tanggal_periksa ASC
        """
        print(f"[API] Executing query for balita_id={balita_id}")
        print(f"[API] Query: {query}")
        
        cur.execute(query, (balita_id,))
        riwayat = cur.fetchall()
        # Fetch balita identity information
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT id, nama, nama_ibu, jenis_kelamin, DATE_FORMAT(tanggal_lahir, '%%d/%%m/%%Y') AS tanggal_lahir, alamat FROM balita WHERE id = %s", (balita_id,))
        balita_info = cur2.fetchone()
        cur2.close()
        cur.close()
        
        print(f"[API] Query returned {len(riwayat)} records")
        if riwayat:
            print(f"[API] First record: {riwayat[0]}")
            print(f"[API] First record type: {type(riwayat[0])}")
            print(f"[API] First record keys: {list(riwayat[0].keys()) if isinstance(riwayat[0], dict) else 'Not a dict!'}")
        
        if not riwayat:
            print(f"[API] No data found for balita_id={balita_id}")
            return jsonify({'success': False, 'message': 'Tidak ada data pemeriksaan'}), 404
        
        response_data = {
            'success': True,
            'data': riwayat,
            'count': len(riwayat),
            'balita': balita_info,
            'debug': {
                'balita_id': balita_id,
                'record_count': len(riwayat),
                'sample_record': riwayat[0] if riwayat else None
            }
        }
        
        print(f"[API] Returning {len(riwayat)} records successfully")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        print(f"[API] ERROR: {error_msg}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': error_msg}), 500

# ════════════════════════════════════════════════════════════════════════════
# HAPUS DATA
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/pemeriksaan/hapus/<int:id>', methods=['DELETE'])
@login_required
def hapus_pemeriksaan(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM pemeriksaan WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True})


@app.route('/api/pemeriksaan/hapus_semua', methods=['DELETE'])
@login_required
def hapus_semua_pemeriksaan():
    """Hapus seluruh data pemeriksaan beserta hasil klasifikasinya."""
    try:
        cur = mysql.connection.cursor()
        # Hapus tabel hasil_klasifikasi terlebih dahulu jika ada relasi FK
        cur.execute("DELETE FROM hasil_klasifikasi")
        cur.execute("DELETE FROM pemeriksaan")
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
