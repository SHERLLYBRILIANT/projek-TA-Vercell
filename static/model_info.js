/**
 * Model Info Charts
 * Visualisasi metrik, performa, dan feature importance model TabNet
 */

let chartPerformance = null;
let chartParams = null;
let chartEpochs = null;
let chartAvgMetrics = null;
let modelData = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
  console.log('[model_info.js] DOMContentLoaded fired');
  loadModelData();
  
  // Setup tab listeners - mereka akan trigger render saat tab diklik
  document.getElementById('metrics-tab')?.addEventListener('shown.bs.tab', function() {
    console.log('[model_info.js] metrics-tab shown');
    renderMetricsTab();
  });
  
  document.getElementById('performance-tab')?.addEventListener('shown.bs.tab', function() {
    console.log('[model_info.js] performance-tab shown');
    if (!chartPerformance && modelData) {
      renderPerformanceChart();
    }
  });
  
  document.getElementById('features-tab')?.addEventListener('shown.bs.tab', function() {
    console.log('[model_info.js] features-tab shown');
    renderFeaturesTab();
  });
});

/**
 * Load model evaluation data dari API
 */
async function loadModelData() {
  try {
    console.log('[model_info.js] fetchingdata from /api/model_info');
    const response = await fetch('/api/model_info');
    console.log('[model_info.js] Fetch response status:', response.status);
    
    if (!response.ok) {
      const text = await response.text();
      console.error('[model_info.js] HTTP error response:', text.substring(0, 500));
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log('[model_info.js] Response JSON parsed, keys:', Object.keys(result));
    
    if (result.success && result.data) {
      modelData = result.data;
      console.log('[model_info.js] modelData assigned, keys:', Object.keys(modelData));
      
      // Render immediately - overview tab is shown by default
      console.log('[model_info.js] Calling renderOverviewTab() and renderMetricsTab()');
      renderOverviewTab();
      renderMetricsTab();
      console.log('[model_info.js] Initial render complete');
    } else {
      console.error('[model_info.js] API returned success=false or no data');
      alert('Gagal memuat data model: ' + (result.message || 'Unknown error'));
    }
  } catch (error) {
    console.error('[model_info.js] Error loading model data:', error.message, error.stack);
    alert('Gagal memuat data model: ' + error.message);
  }
}

/**
 * Helpers
 */
function toPct(x, digits = 2) {
  return (x * 100).toFixed(digits);
}

function calcOverallAvgTesting(evalData) {
  const keys = Object.keys(evalData);
  const sum = { accuracy: 0, precision: 0, recall: 0, f1_score: 0 };

  keys.forEach((k) => {
    const t = evalData[k].testing;
    sum.accuracy += t.accuracy;
    sum.precision += t.precision;
    sum.recall += t.recall;
    sum.f1_score += t.f1_score;
  });

  const n = keys.length || 1;
  return {
    accuracy: sum.accuracy / n,
    precision: sum.precision / n,
    recall: sum.recall / n,
    f1_score: sum.f1_score / n,
  };
}

function shortKeyName(key) {
  return key === 'bbu' ? 'BB/U' : key === 'tbu' ? 'TB/U' : 'BB/TB';
}

/**
 * Render Overview Tab - Ringkasan + Visualisasi
 */
function renderOverviewTab() {
  if (!modelData) {
    console.warn('[renderOverviewTab] modelData is null/undefined');
    return;
  }

  console.log('[renderOverviewTab] Starting render with modelData keys:', Object.keys(modelData));
  
  const evalData = modelData.model_evaluation;
  const artifacts = modelData.model_artifacts;
  const training = modelData.training_info;
  
  if (!evalData || !artifacts || !training) {
    console.error('[renderOverviewTab] Missing critical data:', {
      evalData: !!evalData,
      artifacts: !!artifacts,
      training: !!training
    });
    return;
  }

  const overall = calcOverallAvgTesting(evalData);

  // Ringkasan teks
  const trials = modelData.hyperparameters?.n_trials ?? 30;
  const sampler = modelData.hyperparameters?.sampler ?? 'Optuna';
  const es = artifacts?.training_setup?.early_stopping;

  const summaryEl = document.getElementById('overviewSummary');
  if (summaryEl) {
    summaryEl.innerHTML = `
      <strong>Multi-Output:</strong> 3 output sekaligus (BB/U, TB/U, BB/TB).<br>
      <strong>Optimizer:</strong> Adam (learning rate berbeda per output).<br>
      <strong>Bayesian Optimization:</strong> Optuna ${sampler} dengan ${trials} trials untuk tuning hyperparameter.<br>
      <strong>Early Stopping:</strong> aktif untuk mencegah overfitting (patience tuning ${es?.patience_tuning ?? '-'} / final ${es?.patience_final ?? '-'}).
    `;
    console.log('[renderOverviewTab] Summary updated');
  } else {
    console.warn('[renderOverviewTab] Element overviewSummary not found');
  }

  // Kartu metrik rata-rata
  const avgEl = document.getElementById('overviewAvgMetrics');
  if (avgEl) {
    avgEl.innerHTML = `
      <div class="metric-card">
        <div class="label">Avg Accuracy (Test)</div>
        <div class="value">${toPct(overall.accuracy)}%</div>
      </div>
      <div class="metric-card">
        <div class="label">Avg Precision (Test)</div>
        <div class="value">${toPct(overall.precision)}%</div>
      </div>
      <div class="metric-card">
        <div class="label">Avg Recall (Test)</div>
        <div class="value">${toPct(overall.recall)}%</div>
      </div>
      <div class="metric-card">
        <div class="label">Avg F1-Score (Test)</div>
        <div class="value">${toPct(overall.f1_score)}%</div>
      </div>
    `;
    console.log('[renderOverviewTab] Metric cards updated');
  } else {
    console.warn('[renderOverviewTab] Element overviewAvgMetrics not found');
  }

  // Chart: jumlah parameter
  const paramsCanvas = document.getElementById('chartParams');
  if (paramsCanvas && artifacts?.outputs) {
    try {
      const labels = Object.keys(artifacts.outputs).map(shortKeyName);
      const values = Object.keys(artifacts.outputs).map((k) => artifacts.outputs[k].total_params);

      if (chartParams) chartParams.destroy();
      chartParams = new Chart(paramsCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Total Parameter',
            data: values,
            backgroundColor: ['#FCE0E9', '#E6F5F7', '#FFFBDD'],
            borderColor: ['#CA6180', '#9ED3DC', '#B59B1E'],
            borderWidth: 2,
            borderRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.parsed.y.toLocaleString('id-ID')} params`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (v) => v >= 1000 ? (v / 1000) + 'k' : v
              },
              title: { display: true, text: 'Jumlah parameter' }
            }
          }
        }
      });
      console.log('[renderOverviewTab] chartParams created');
    } catch (e) {
      console.error('[renderOverviewTab] Error creating chartParams:', e);
    }
  } else {
    console.warn('[renderOverviewTab] chartParams element or artifacts.outputs not found');
  }

  // Chart: epoch completed (indikasi early stopping)
  const epochsCanvas = document.getElementById('chartEpochs');
  if (epochsCanvas && training?.epochs_completed) {
    try {
      const keys = Object.keys(training.epochs_completed);
      const labels = keys.map(shortKeyName);
      const values = keys.map((k) => training.epochs_completed[k]);

      if (chartEpochs) chartEpochs.destroy();
      chartEpochs = new Chart(epochsCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Epoch hingga berhenti',
            data: values,
            backgroundColor: '#FEFD99',
            borderColor: '#B59B1E',
            borderWidth: 2,
            borderRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Epoch' }
            }
          }
        }
      });
      console.log('[renderOverviewTab] chartEpochs created');
    } catch (e) {
      console.error('[renderOverviewTab] Error creating chartEpochs:', e);
    }
  } else {
    console.warn('[renderOverviewTab] chartEpochs element or training.epochs_completed not found');
  }

  // Chart: radar rata-rata metrik testing
  const avgCanvas = document.getElementById('chartAvgMetrics');
  if (avgCanvas) {
    try {
      if (chartAvgMetrics) chartAvgMetrics.destroy();
      chartAvgMetrics = new Chart(avgCanvas.getContext('2d'), {
        type: 'radar',
        data: {
          labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
          datasets: [{
            label: 'Rata-rata (Testing)',
            data: [overall.accuracy, overall.precision, overall.recall, overall.f1_score],
            borderColor: '#CA6180',
            backgroundColor: 'rgba(202, 97, 128, 0.15)',
            pointBackgroundColor: '#CA6180',
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              beginAtZero: true,
              suggestedMin: 0.8,
              suggestedMax: 1.0,
              ticks: {
                callback: (v) => (v * 100).toFixed(0) + '%'
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.label}: ${toPct(ctx.raw)}%`
              }
            }
          }
        }
      });
      console.log('[renderOverviewTab] chartAvgMetrics created');
    } catch (e) {
      console.error('[renderOverviewTab] Error creating chartAvgMetrics:', e);
    }
  } else {
    console.warn('[renderOverviewTab] chartAvgMetrics element not found');
  }

  console.log('[renderOverviewTab] Render complete');
}

/**
 * Render Metrics Tab - Metrik Evaluasi
 */
function renderMetricsTab() {
  if (!modelData) {
    console.warn('[renderMetricsTab] modelData is null/undefined');
    return;
  }
  
  console.log('[renderMetricsTab] Starting render');
  
  const eval_data = modelData.model_evaluation;
  if (!eval_data) {
    console.error('[renderMetricsTab] model_evaluation not found in modelData');
    return;
  }

  let html = '';
  
  Object.entries(eval_data).forEach(([key, item]) => {
    const train = item.training;
    const test = item.testing;
    const gap = ((train.accuracy - test.accuracy) * 100).toFixed(2);
    
    html += `
      <div class="col-lg-4 mb-3">
        <div class="card">
          <div class="card-header bg-light">
            <strong>${item.name}</strong>
          </div>
          <div class="card-body">
            <h6 class="mb-2">📚 Training Data</h6>
            <table class="comparison-table">
              <tr>
                <td class="label-col">Accuracy</td>
                <td><span class="badge-train">${(train.accuracy * 100).toFixed(2)}%</span></td>
              </tr>
              <tr>
                <td class="label-col">Precision</td>
                <td><span class="badge-train">${(train.precision * 100).toFixed(2)}%</span></td>
              </tr>
              <tr>
                <td class="label-col">Recall</td>
                <td><span class="badge-train">${(train.recall * 100).toFixed(2)}%</span></td>
              </tr>
              <tr>
                <td class="label-col">F1-Score</td>
                <td><span class="badge-train">${(train.f1_score * 100).toFixed(2)}%</span></td>
              </tr>
            </table>
            
            <h6 class="mb-2 mt-4">🧪 Testing Data</h6>
            <table class="comparison-table">
              <tr>
                <td class="label-col">Accuracy</td>
                <td><span class="badge-test">${(test.accuracy * 100).toFixed(2)}%</span></td>
              </tr>
              <tr>
                <td class="label-col">Precision</td>
                <td><span class="badge-test">${(test.precision * 100).toFixed(2)}%</span></td>
              </tr>
              <tr>
                <td class="label-col">Recall</td>
                <td><span class="badge-test">${(test.recall * 100).toFixed(2)}%</span></td>
              </tr>
              <tr>
                <td class="label-col">F1-Score</td>
                <td><span class="badge-test">${(test.f1_score * 100).toFixed(2)}%</span></td>
              </tr>
            </table>
            
            <div style="margin-top: 12px; padding: 10px; background: #F0F4F8; border-radius: 4px; font-size: 0.8rem;">
              <strong>Gap Train-Test:</strong> ${gap}% 
              <span style="color: ${gap > 5 ? '#9B4864' : '#4EA9B7'};">
                ${gap > 5 ? '⚠️ Perhatikan overfitting' : '✓ Stabil'}
              </span>
            </div>
          </div>
        </div>
      </div>
    `;
  });
  
  const metricsEl = document.getElementById('metricsContent');
  if (metricsEl) {
    metricsEl.innerHTML = html;
    console.log('[renderMetricsTab] Metrics content updated');
  } else {
    console.warn('[renderMetricsTab] Element metricsContent not found');
  }
}

/**
 * Render Performance Tab - Performa Training vs Testing
 */
function renderPerformanceChart() {
  const eval_data = modelData.model_evaluation;
  
  const labels = [];
  const trainAccuracy = [];
  const testAccuracy = [];
  
  Object.entries(eval_data).forEach(([key, item]) => {
    const shortName = key === 'bbu' ? 'BB/U' : key === 'tbu' ? 'TB/U' : 'BB/TB';
    labels.push(shortName);
    trainAccuracy.push((item.training.accuracy * 100).toFixed(2));
    testAccuracy.push((item.testing.accuracy * 100).toFixed(2));
  });
  
  const ctx = document.getElementById('chartPerformance').getContext('2d');
  chartPerformance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Training Accuracy',
          data: trainAccuracy,
          backgroundColor: '#E6F5F7',
          borderColor: '#9ED3DC',
          borderWidth: 2,
          borderRadius: 4,
        },
        {
          label: 'Testing Accuracy',
          data: testAccuracy,
          backgroundColor: '#FCE0E9',
          borderColor: '#CA6180',
          borderWidth: 2,
          borderRadius: 4,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { boxWidth: 12, font: { size: 11, weight: '600' } }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 10,
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(v) { return v + '%'; }
          },
          title: {
            display: true,
            text: 'Accuracy (%)'
          }
        }
      }
    }
  });
  
  // Render performance info
  let infoHtml = '<div class="col-12"><div class="info-box">';
  infoHtml += '<div class="title">📈 Analisis Performa</div>';
  infoHtml += '<div class="desc">';
  infoHtml += '<strong>Model Performance Summary:</strong><br>';
  infoHtml += '✓ Ketiga model menunjukkan akurasi tinggi di atas 94% pada data testing<br>';
  infoHtml += '✓ Model BB/TB memiliki performa terbaik (95.72% testing accuracy)<br>';
  infoHtml += '✓ Gap antara training dan testing relatif kecil (<2%), menunjukkan generalisasi baik<br>';
  infoHtml += '✓ Early stopping berhasil mencegah overfitting<br>';
  infoHtml += '</div></div></div>';
  
  document.getElementById('performanceInfo').innerHTML = infoHtml;
}

/**
 * Render Features Tab - Feature Importance
 */
function renderFeaturesTab() {
  if (!modelData) return;
  
  const features = modelData.feature_importance;
  let html = '';
  
  Object.entries(features).forEach(([key, importances]) => {
    const modelName = key === 'bbu' ? 'BB/U (Berat Badan per Umur)' 
                    : key === 'tbu' ? 'TB/U (Tinggi Badan per Umur)'
                    : 'BB/TB (Berat Badan per Tinggi Badan)';
    
    let featuresHtml = '';
    
    // Sort by importance descending
    importances.sort((a, b) => b.importance - a.importance);
    
    importances.forEach((item, idx) => {
      const percent = (item.importance * 100).toFixed(1);
      const colors = ['#CA6180', '#B75371', '#9ED3DC', '#7AC4CC'];
      
      featuresHtml += `
        <div class="feature-bar">
          <div class="label">${item.feature}</div>
          <div class="bar">
            <div class="bar-fill" style="width: ${percent}%; background: ${colors[idx % colors.length]};"></div>
          </div>
          <div class="value">${percent}%</div>
        </div>
      `;
    });
    
    html += `
      <div class="col-lg-6 mb-3">
        <div class="card">
          <div class="card-header">
            <i class="bi bi-lightning me-1"></i> ${modelName}
          </div>
          <div class="card-body">
            ${featuresHtml}
          </div>
        </div>
      </div>
    `;
  });
  
  html += `
    <div class="col-12">
      <div class="info-box">
        <div class="title">💡 Interpretasi Feature Importance</div>
        <div class="desc">
          <strong>Apa artinya?</strong><br>
          Feature Importance menunjukkan seberapa penting setiap input untuk membuat prediksi. 
          Semakin tinggi persentase, semakin penting feature tersebut untuk model.
          <br><br>
          <strong>Insight Utama:</strong><br>
          • <strong>BB/U:</strong> Berat badan adalah faktor paling penting (45%), dikombinasikan dengan tinggi badan dan umur<br>
          • <strong>TB/U:</strong> Tinggi badan dominan (52%) karena langsung mengukur pertumbuhan vertikal<br>
          • <strong>BB/TB:</strong> Keseimbangan berat dan tinggi sama-sama penting untuk deteksi gizi buruk
        </div>
      </div>
    </div>
  `;
  
  document.getElementById('featureContent').innerHTML = html;
}
