import os

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'pemeriksaan.html')

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: HTML input - change min="30" to min="35" and update placeholder
content = content.replace(
    'placeholder="0.0" step="0.1" min="30" max="130" required/>',
    'placeholder="35.0" step="0.1" min="35" max="130" required/>'
)

# Verify change was made
assert 'min="35" max="130"' in content, "Fix 1 failed: HTML min attribute not changed"

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML input fix applied successfully")

# Now fix app.py backend validation
app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.py')

with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Add server-side validation for tinggi_badan in api_prediksi
old_block = """        tinggi_badan = float(data['tinggi_badan'])
        catatan      = data.get('catatan', '')

        cur = mysql.connection.cursor()"""

new_block = """        tinggi_badan = float(data['tinggi_badan'])
        catatan      = data.get('catatan', '')

        # Validasi rentang tinggi badan wajar untuk balita (35-130 cm)
        if tinggi_badan < 35 or tinggi_badan > 130:
            return jsonify({'success': False, 'message': 'Tinggi badan di luar rentang wajar (35–130 cm)'}), 400

        cur = mysql.connection.cursor()"""

app_content = app_content.replace(old_block, new_block)

assert 'tinggi_badan < 35 or tinggi_badan > 130' in app_content, "Fix 2 failed: Backend validation not added"

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Backend validation fix applied successfully")
print("All fixes applied!")

