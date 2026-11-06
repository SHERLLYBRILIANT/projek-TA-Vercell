import re

with open('scratch/tables.html', 'r') as f:
    tables_html = f.read()

train_tables = tables_html.split('<div class="accordion accordion-flush border rounded-3" id="accTest">')[0]
test_tables = '<div class="accordion accordion-flush border rounded-3" id="accTest">' + tables_html.split('<div class="accordion accordion-flush border rounded-3" id="accTest">')[1]

new_content = f"""
          <hr class="my-5" style="border-top: 2px dashed #eee; opacity: 1;">

          <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
            <h5 class="fw-bold text-dark mb-0"><i class="bi bi-file-earmark-bar-graph-fill me-2 text-primary"></i>Laporan Evaluasi Metrik (Classification Report)</h5>
            <button class="btn btn-sm btn-outline-info d-flex align-items-center" data-bs-toggle="modal" data-bs-target="#modalManualMetrics">
              <i class="bi bi-calculator me-2"></i> Simulasi Perhitungan Manual
            </button>
          </div>

          <!-- Nav Pills -->
          <ul class="nav nav-pills mb-4 gap-2" id="evalPills" role="tablist">
            <li class="nav-item" role="presentation">
              <button class="nav-link active rounded-pill px-4 border border-primary border-opacity-25" id="eval-train-tab" data-bs-toggle="pill" data-bs-target="#eval-train" type="button" role="tab" style="font-weight: 500;">Evaluasi Data Training</button>
            </li>
            <li class="nav-item" role="presentation">
              <button class="nav-link rounded-pill px-4 border border-primary border-opacity-25" id="eval-test-tab" data-bs-toggle="pill" data-bs-target="#eval-test" type="button" role="tab" style="font-weight: 500;">Evaluasi Data Testing</button>
            </li>
            <li class="nav-item" role="presentation">
              <button class="nav-link rounded-pill px-4 border border-primary border-opacity-25" id="eval-summary-tab" data-bs-toggle="pill" data-bs-target="#eval-summary" type="button" role="tab" style="font-weight: 500;">Ringkasan (Train vs Test)</button>
            </li>
          </ul>

          <!-- Tab Content -->
          <div class="tab-content" id="evalPillsContent">
            <!-- Evaluasi Training -->
            <div class="tab-pane fade show active" id="eval-train" role="tabpanel">
               <p class="text-muted small mb-3">Evaluasi model menggunakan data yang <strong>sama</strong> dengan yang dipelajari selama proses pelatihan (Train Data). Digunakan untuk mengukur seberapa baik model menghafal dan mengenali pola dasar.</p>
               {train_tables}
            </div>

            <!-- Evaluasi Testing -->
            <div class="tab-pane fade" id="eval-test" role="tabpanel">
               <p class="text-muted small mb-3">Evaluasi model menggunakan data yang <strong>belum pernah dilihat</strong> sebelumnya (Test Data). Ini adalah metrik terpenting untuk mengukur kemampuan model dalam menghadapi kasus dunia nyata (Generalisasi).</p>
               {test_tables}
            </div>

            <!-- Ringkasan -->
            <div class="tab-pane fade" id="eval-summary" role="tabpanel">
              <div class="table-responsive rounded-3 border">
                <table class="table table-hover table-borderless text-center mb-0">
                  <thead class="table-light text-muted border-bottom">
                    <tr>
                      <th class="text-start ps-4">Target Label</th>
                      <th>Acc Train</th>
                      <th>Acc Test</th>
                      <th>F1-W Train</th>
                      <th>F1-W Test</th>
                      <th class="pe-4">Status</th>
                    </tr>
                  </thead>
                  <tbody class="small">
                    <tr>
                      <td class="text-start ps-4 fw-medium">Weight for Age</td>
                      <td>0.9678</td>
                      <td>0.9646</td>
                      <td>0.9677</td>
                      <td>0.9649</td>
                      <td class="pe-4"><span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill"><i class="bi bi-check-circle-fill me-1"></i>Good Fit</span></td>
                    </tr>
                    <tr>
                      <td class="text-start ps-4 fw-medium">Height for Age</td>
                      <td>0.9721</td>
                      <td>0.9588</td>
                      <td>0.9721</td>
                      <td>0.9586</td>
                      <td class="pe-4"><span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill"><i class="bi bi-check-circle-fill me-1"></i>Good Fit</span></td>
                    </tr>
                    <tr>
                      <td class="text-start ps-4 fw-medium">Weight for Height</td>
                      <td>0.9748</td>
                      <td>0.9811</td>
                      <td>0.9748</td>
                      <td>0.9816</td>
                      <td class="pe-4"><span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill"><i class="bi bi-check-circle-fill me-1"></i>Good Fit</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="alert mt-4 mb-0" style="background-color: #f8f9fa; border: 1px solid #e2e8f0; border-left: 4px solid #ff9800; border-radius: 8px;">
            <h6 class="fw-bold text-dark mb-2"><i class="bi bi-journal-text me-2" style="color: #ff9800;"></i>Cara Membaca Metrik Evaluasi</h6>
            <div class="row g-3">
              <div class="col-md-6">
                <ul class="mb-0 ps-3 text-muted small lh-base">
                  <li class="mb-1"><strong>Precision:</strong> Seberapa presisi tebakan model? Jika model menebak "Stunting", berapa persen yang benar-benar Stunting di dunia nyata. (Menghindari <em>False Positive</em>).</li>
                  <li class="mb-1"><strong>Recall (Sensitivity):</strong> Dari seluruh anak yang aslinya "Stunting", berapa persen yang berhasil dideteksi oleh model? (Menghindari <em>False Negative</em>).</li>
                  <li><strong>F1-Score:</strong> Nilai rata-rata harmonis antara Precision dan Recall. Jika F1-Score tinggi, berarti model presisi dan juga teliti (tidak banyak kasus terlewat).</li>
                </ul>
              </div>
              <div class="col-md-6">
                <ul class="mb-0 ps-3 text-muted small lh-base">
                  <li class="mb-1"><strong>Accuracy:</strong> Persentase total tebakan benar (semua kelas) dibagi total keseluruhan data.</li>
                  <li class="mb-1"><strong>Support:</strong> Jumlah data asli yang tersedia untuk masing-masing kelas label tersebut.</li>
                  <li><strong>Weighted Avg:</strong> Rata-rata dari skor metrik yang memperhitungkan jumlah sampel (support) pada masing-masing kelas. Cocok digunakan pada data yang <em>imbalance</em> (tidak seimbang).</li>
                </ul>
              </div>
            </div>
          </div>
"""

with open('templates/informasi_model.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Target for injection: right after the Cara Membaca Grafik Akurasi alert
target = """          <div class="alert mt-4 mb-0" style="background-color: #f8f9fa; border: 1px solid #e2e8f0; border-left: 4px solid #CA6180; border-radius: 8px;">
            <h6 class="fw-bold text-dark mb-2"><i class="bi bi-info-circle-fill me-2" style="color: #CA6180;"></i>Cara Membaca Grafik Akurasi</h6>
            <ul class="mb-0 ps-3 text-muted small lh-base">
              <li class="mb-1"><strong>Garis Biru (Train Accuracy):</strong> Menunjukkan tingkat akurasi model dalam mengenali pola data yang sedang dipelajari (data latih). Nilainya cenderung naik secara progresif.</li>
              <li class="mb-1"><strong>Garis Putus-putus Merah (Test Accuracy):</strong> Menunjukkan performa model saat diuji menggunakan sekumpulan data baru yang disembunyikan sebelumnya. Garis ini menjadi indikator vital apakah model bisa beroperasi optimal di dunia nyata (Generalisasi).</li>
              <li><strong>Garis Vertikal Hijau (Best Epoch):</strong> Menandai momen siklus terbaik (misal: Epoch 26 untuk BB/U) di mana model berhasil mencapai titik keseimbangan paling sempurna antara skor Train dan Test tertingginya, tepat sebelum terjadinya penurunan kualitas akurasi akibat <em>overfitting</em> (terlalu menghafal data).</li>
            </ul>
          </div>"""

content = content.replace(target, target + new_content)

modal_content = """

  <!-- Modal Simulasi Perhitungan Manual Metrik -->
  <div class="modal fade" id="modalManualMetrics" tabindex="-1" aria-labelledby="modalManualMetricsLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg" style="border-radius: 12px;">
        <div class="modal-header border-bottom-0 pb-0 pt-4 px-4">
          <h5 class="modal-title fw-bold text-dark" id="modalManualMetricsLabel"><i class="bi bi-calculator-fill text-info me-2"></i>Simulasi Perhitungan Manual Metrik Evaluasi</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body p-4">
          <p class="text-muted small mb-4">Mari kita hitung bagaimana angka <strong>Accuracy</strong>, <strong>Precision</strong>, dan <strong>Recall</strong> didapatkan, menggunakan ilustrasi sederhana berupa <em>Confusion Matrix</em> untuk mendeteksi label <strong>"Stunted"</strong> vs <strong>"Not Stunted"</strong>.</p>

          <div class="table-responsive mb-4">
            <table class="table table-bordered text-center align-middle small mb-0">
              <thead class="table-light">
                <tr>
                  <th rowspan="2" colspan="2" class="border-0 bg-transparent"></th>
                  <th colspan="2">Tebakan Model (Prediction)</th>
                </tr>
                <tr>
                  <th class="text-danger">Stunted (Positif)</th>
                  <th class="text-success">Not Stunted (Negatif)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th rowspan="2" class="align-middle table-light" style="width: 20px;"><div style="writing-mode: vertical-rl; transform: rotate(180deg);">Data Asli (Actual)</div></th>
                  <th class="text-danger text-start px-3">Stunted (Positif)</th>
                  <td><div class="fw-bold fs-6">3,394</div><span class="text-muted" style="font-size: 0.7rem;">True Positive (TP)</span></td>
                  <td><div class="fw-bold fs-6">296</div><span class="text-muted" style="font-size: 0.7rem;">False Negative (FN)</span></td>
                </tr>
                <tr>
                  <th class="text-success text-start px-3">Not Stunted (Negatif)</th>
                  <td><div class="fw-bold fs-6">278</div><span class="text-muted" style="font-size: 0.7rem;">False Positive (FP)</span></td>
                  <td><div class="fw-bold fs-6">6,694</div><span class="text-muted" style="font-size: 0.7rem;">True Negative (TN)</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="row g-4">
            <div class="col-md-12">
              <div class="card shadow-none border rounded-3 h-100 bg-light">
                <div class="card-body">
                  <h6 class="fw-bold text-dark mb-3">1. Perhitungan Accuracy</h6>
                  <p class="small text-muted mb-2">Total tebakan yang benar (TP + TN) dibagi Total seluruh data.</p>
                  <div class="bg-white p-2 rounded border font-monospace text-center small mb-2">
                    Accuracy = (TP + TN) / (TP + TN + FP + FN)<br>
                    Accuracy = (3,394 + 6,694) / 10,662<br>
                    Accuracy = 10,088 / 10,662 = <span class="fw-bold text-dark">0.9461 (94.61%)</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card shadow-none border rounded-3 h-100 bg-light">
                <div class="card-body">
                  <h6 class="fw-bold text-dark mb-3">2. Perhitungan Precision (untuk "Stunted")</h6>
                  <p class="small text-muted mb-2">Dari semua yang ditebak "Stunted", berapa banyak yang benar-benar "Stunted"?</p>
                  <div class="bg-white p-2 rounded border font-monospace text-center small mb-2">
                    Precision = TP / (TP + FP)<br>
                    Precision = 3,394 / (3,394 + 278)<br>
                    Precision = 3,394 / 3,672 = <span class="fw-bold text-dark">0.9242</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card shadow-none border rounded-3 h-100 bg-light">
                <div class="card-body">
                  <h6 class="fw-bold text-dark mb-3">3. Perhitungan Recall (untuk "Stunted")</h6>
                  <p class="small text-muted mb-2">Dari semua anak yang aslinya "Stunted", berapa persen yang berhasil ditemukan model?</p>
                  <div class="bg-white p-2 rounded border font-monospace text-center small mb-2">
                    Recall = TP / (TP + FN)<br>
                    Recall = 3,394 / (3,394 + 296)<br>
                    Recall = 3,394 / 3,690 = <span class="fw-bold text-dark">0.9197</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-12">
              <div class="card shadow-none border rounded-3 h-100 bg-light">
                <div class="card-body">
                  <h6 class="fw-bold text-dark mb-3">4. Perhitungan F1-Score (untuk "Stunted")</h6>
                  <p class="small text-muted mb-2">Rata-rata harmonis antara Precision dan Recall.</p>
                  <div class="bg-white p-2 rounded border font-monospace text-center small mb-2">
                    F1-Score = 2 × (Precision × Recall) / (Precision + Recall)<br>
                    F1-Score = 2 × (0.9242 × 0.9197) / (0.9242 + 0.9197)<br>
                    F1-Score = 2 × 0.8500 / 1.8439 = <span class="fw-bold text-dark">0.9219</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
"""

# Insert modal before final block containing </div>\n</div>\n\n<script>
content = content.replace('  </div>\n</div>\n\n<script>', modal_content + '  </div>\n</div>\n\n<script>')

with open('templates/informasi_model.html', 'w', encoding='utf-8') as f:
    f.write(content)
