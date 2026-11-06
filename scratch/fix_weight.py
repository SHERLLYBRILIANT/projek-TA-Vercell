import os

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'pemeriksaan.html')

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: HTML input - change min="1" to min="2" and update placeholder
content = content.replace(
    'placeholder="0.0" step="0.1" min="1" max="30" required/>',
    'placeholder="2.0" step="0.1" min="2" max="30" required/>'
)
assert 'min="2" max="30"' in content, "Fix 1 failed"

# Fix 2: JavaScript validation - change beratNum <= 0 to beratNum < 2 and max to 30
content = content.replace(
    "(beratNum <= 0 || beratNum > 50)) errors.push('Berat Badan di luar rentang wajar (0\u201350 kg)')",
    "(beratNum < 2 || beratNum > 30)) errors.push('Berat Badan di luar rentang wajar (2\u201330 kg)')"
)
assert "beratNum < 2 || beratNum > 30" in content, "Fix 2 failed"

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Frontend fixes applied")

# Fix 3: Backend validation in app.py
app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.py')

with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Add berat badan validation right before tinggi badan validation
old = "        # Validasi rentang tinggi badan wajar untuk balita (35-130 cm)"
new = """        # Validasi rentang berat badan wajar untuk balita (2-30 kg)
        if berat_badan < 2 or berat_badan > 30:
            return jsonify({'success': False, 'message': 'Berat badan di luar rentang wajar (2\u201330 kg)'}), 400

        # Validasi rentang tinggi badan wajar untuk balita (35-130 cm)"""

app_content = app_content.replace(old, new)
assert "berat_badan < 2 or berat_badan > 30" in app_content, "Fix 3 failed"

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
print("Backend fix applied")
print("All fixes done!")

