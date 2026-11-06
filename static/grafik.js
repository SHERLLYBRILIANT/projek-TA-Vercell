/**
 * Grafik Pertumbuhan Anak
 * Chart.js untuk visualisasi berat badan & tinggi badan per umur
 */

let chartBB = null;   // Chart instance untuk berat badan
let chartTB = null;   // Chart instance untuk tinggi badan
let chartBBTB = null; // Chart instance untuk BB/TB
let currentBalita = null; // identity info from API

// Element references
const selectBalita = document.getElementById('selectBalita');
const btnRiwayat = document.getElementById('btnRiwayat');
const btnExportPdf = document.getElementById('btnExportPdf');
const chartBBContainer = document.getElementById('chartBBContainer');
const chartTBContainer = document.getElementById('chartTBContainer');
const chartBBTBContainer = document.getElementById('chartBBTBContainer');
const emptyBB = document.getElementById('emptyBB');
const emptyTB = document.getElementById('emptyTB');
const emptyBBTB = document.getElementById('emptyBBTB');
const tabelRiwayatContainer = document.getElementById('tabelRiwayatContainer');
const tabelRiwayatBody = document.getElementById('tabelRiwayatBody');

// Event Listeners
if (selectBalita) selectBalita.addEventListener('change', handleBalitaChange);
if (btnRiwayat) btnRiwayat.addEventListener('click', toggleTabelRiwayat);
if (btnExportPdf) btnExportPdf.addEventListener('click', exportPdf);

/**
 * Handle perubahan pilihan anak
 */
async function handleBalitaChange() {
  if (!selectBalita) return;
  const balitaId = selectBalita.value;
  console.log('[handleBalitaChange] Balita ID selected:', balitaId);
  
  if (!balitaId) {
    console.log('[handleBalitaChange] No balita selected, resetting');
    resetCharts();
    return;
  }

  try {
    const url = `/api/grafik_data/${balitaId}`;
    console.log('[handleBalitaChange] Fetching from:', url);
    const response = await fetch(url);
    console.log('[handleBalitaChange] Response status:', response.status);
    const result = await response.json();
    console.log('[handleBalitaChange] Response JSON:', result);

    if (!response.ok || !result.success || !result.data || result.data.length === 0) {
      console.warn('[handleBalitaChange] No valid data - resetting charts');
      if (window.Swal) {
        Swal.fire({
          icon: 'warning',
          title: 'Data belum tersedia',
          text: 'Riwayat pemeriksaan untuk anak ini belum ada.',
          confirmButtonText: 'OK'
        });
      } else {
        alert('Riwayat pemeriksaan untuk anak ini belum ada.');
      }
      resetCharts();
      return;
    }

    // store balita identity info for PDF header
    currentBalita = result.balita || null;
    renderCharts(result.data);
    populateTabelRiwayat(result.data);
    if (btnRiwayat) btnRiwayat.disabled = false;
    if (tabelRiwayatContainer) tabelRiwayatContainer.style.display = 'none';
  } catch (error) {
    console.error('[handleBalitaChange] Error:', error);
    resetCharts();
  }
}

/**
 * Reset chart dan UI
 */
function resetCharts() {
  if (chartBB) chartBB.destroy();
  if (chartTB) chartTB.destroy();
  if (chartBBTB) chartBBTB.destroy();
  
  chartBB = null;
  chartTB = null;
  chartBBTB = null;
  
  if (chartBBContainer) chartBBContainer.style.display = 'none';
  if (chartTBContainer) chartTBContainer.style.display = 'none';
  if (chartBBTBContainer) chartBBTBContainer.style.display = 'none';
  if (emptyBB) emptyBB.style.display = 'block';
  if (emptyTB) emptyTB.style.display = 'block';
  if (emptyBBTB) emptyBBTB.style.display = 'block';
  if (tabelRiwayatContainer) tabelRiwayatContainer.style.display = 'none';
  if (btnRiwayat) btnRiwayat.disabled = true;
  if (tabelRiwayatBody) tabelRiwayatBody.innerHTML = '';
}

/**
 * Render chart menggunakan Chart.js
 * @param {Array} data - Array of riwayat pemeriksaan
 */
function renderCharts(data) {
  console.log('[renderCharts] Starting render with', data.length, 'records');
  if (!data || data.length === 0) { resetCharts(); return; }

  const requiredFields = ['umur_bulan', 'berat_badan', 'tinggi_badan', 'tgl_format'];
  const firstRecord = data[0];
  for (const field of requiredFields) {
    if (!(field in firstRecord)) { console.error('[renderCharts] Missing field', field); resetCharts(); return; }
  }

  try {
    const labels = data.map(d => `${d.umur_bulan}bln`);
    const beratBadanData = data.map(d => parseFloat(d.berat_badan));
    const tinggiBadanData = data.map(d => parseFloat(d.tinggi_badan));
    const tanggalData = data.map(d => d.tgl_format);

    const colorBB = '#9ED3DC';
    const colorTB = '#CA6180';
    const bgColorBB = 'rgba(158, 211, 220, 0.12)';
    const bgColorTB = 'rgba(202, 97, 128, 0.12)';

    if (chartBB) chartBB.destroy();
    if (chartTB) chartTB.destroy();
    if (chartBBTB) chartBBTB.destroy();

    if (chartBBContainer) chartBBContainer.style.display = 'block';
    if (chartTBContainer) chartTBContainer.style.display = 'block';
    if (chartBBTBContainer) chartBBTBContainer.style.display = 'block';
    if (emptyBB) emptyBB.style.display = 'none';
    if (emptyTB) emptyTB.style.display = 'none';
    if (emptyBBTB) emptyBBTB.style.display = 'none';

    // CHART BB/U
    const ctxBB = document.getElementById('chartBB').getContext('2d');
    chartBB = new Chart(ctxBB, {
      type: 'line',
      data: { labels, datasets: [{ label: 'Berat Badan (kg)', data: beratBadanData, borderColor: colorBB, backgroundColor: bgColorBB, fill: true, tension: 0.4, pointRadius: 6, pointBackgroundColor: colorBB, pointBorderColor: '#fff', pointBorderWidth: 2, pointHoverRadius: 8, borderWidth: 2.5 }]},
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: true, position: 'top' }, tooltip: { callbacks: { afterTitle: ctx => `Tanggal: ${tanggalData[ctx[0].dataIndex]}`, label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} kg` } } },
        scales: { y: { title: { display: true, text: 'Berat Badan (kg)' } }, x: { title: { display: true, text: 'Umur' } } }
      }
    });

    // CHART TB/U
    const ctxTB = document.getElementById('chartTB').getContext('2d');
    chartTB = new Chart(ctxTB, {
      type: 'line',
      data: { labels, datasets: [{ label: 'Tinggi Badan (cm)', data: tinggiBadanData, borderColor: colorTB, backgroundColor: bgColorTB, fill: true, tension: 0.4, pointRadius: 6, pointBackgroundColor: colorTB, pointBorderColor: '#fff', pointBorderWidth: 2, pointHoverRadius: 8, borderWidth: 2.5 }]},
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, position: 'top' } }, scales: { y: { title: { display: true, text: 'Tinggi Badan (cm)' } }, x: { title: { display: true, text: 'Umur' } } } }
    });

    // CHART BB/TB (scatter)
    const ctxBBTB = document.getElementById('chartBBTB').getContext('2d');
    const bbtbData = data.map(d => ({ x: parseFloat(d.tinggi_badan), y: parseFloat(d.berat_badan) }));
    chartBBTB = new Chart(ctxBBTB, {
      type: 'scatter',
      data: { datasets: [{ label: 'Berat Badan vs Tinggi Badan', data: bbtbData, borderColor: '#D4AF37', backgroundColor: 'rgba(212, 175, 55, 0.12)', fill: true, tension: 0.4, showLine: true, pointRadius: 6, pointBackgroundColor: '#D4AF37', pointBorderColor: '#fff', pointBorderWidth: 2, pointHoverRadius: 8, borderWidth: 2.5 }]},
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, position: 'top' } }, scales: { x: { title: { display: true, text: 'Tinggi Badan (cm)' } }, y: { title: { display: true, text: 'Berat Badan (kg)' } } } }
    });

    console.log('[renderCharts] ✓ All 3 charts created successfully');
  } catch (error) {
    console.error('[renderCharts] Error rendering charts:', error);
    resetCharts();
  }
}

/**
 * Populate tabel riwayat
 */
function populateTabelRiwayat(data) {
  if (!tabelRiwayatBody) return;
  tabelRiwayatBody.innerHTML = '';
  data.forEach((item, idx) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${idx + 1}</td>
      <td>${item.tgl_format}</td>
      <td>${item.umur_bulan}</td>
      <td>${parseFloat(item.berat_badan).toFixed(2)}</td>
      <td>${parseFloat(item.tinggi_badan).toFixed(2)}</td>
    `;
    tabelRiwayatBody.appendChild(row);
  });
}

/**
 * Toggle tampilan tabel riwayat
 */
function toggleTabelRiwayat() {
  if (!btnRiwayat || !tabelRiwayatContainer) return;
  if (tabelRiwayatContainer.style.display === 'none') {
    tabelRiwayatContainer.style.display = 'block';
    btnRiwayat.classList.add('active');
  } else {
    tabelRiwayatContainer.style.display = 'none';
    btnRiwayat.classList.remove('active');
  }
}

/**
 * Unduh laporan grafik berbasis data server untuk balita yang dipilih
 */
function exportPdf() {
  const balitaId = selectBalita ? selectBalita.value : '';
  if (!balitaId) {
    if (window.Swal) {
      Swal.fire({ icon: 'info', title: 'Belum ada data dipilih', text: 'Pilih anak terlebih dahulu sebelum mencetak dokumen grafik.' });
    } else {
      alert('Pilih anak terlebih dahulu sebelum mencetak dokumen grafik.');
    }
    return;
  }
  const selectedLabel = currentBalita && currentBalita.nama ? currentBalita.nama : (selectBalita.options[selectBalita.selectedIndex] ? selectBalita.options[selectBalita.selectedIndex].text : 'balita');
  const pdfUrl = `/export/grafik/pdf/${balitaId}`;

  if (window.Swal) {
    Swal.fire({
      icon: 'question',
      title: 'Cetak Dokumen Grafik?',
      text: `Dokumen akan berisi data diri dan riwayat pemeriksaan lengkap untuk ${selectedLabel}.`,
      showCancelButton: true,
      confirmButtonText: 'Ya, Cetak',
      cancelButtonText: 'Batal',
      confirmButtonColor: '#D4AF37',
      cancelButtonColor: '#9ED3DC'
    }).then((result) => {
      if (result.isConfirmed) {
        window.location.href = pdfUrl;
      }
    });
    return;
  }

  window.location.href = pdfUrl;
}
