import json

data = {
    "train": {
        "BBU": {
            "title": "Weight for Age",
            "acc": 0.9678,
            "f1_w": 0.9677,
            "f1_m": 0.9688,
            "rows": [
                ["Underfed", 0.95, 0.94, 0.95, 23064],
                ["Normal", 0.98, 0.98, 0.98, 32035],
                ["Malnutrition", 0.97, 0.95, 0.96, 19220],
                ["Overnutrition", 0.98, 0.99, 0.99, 11532]
            ],
            "macro": [0.97, 0.97, 0.97, 85851],
            "weighted": [0.97, 0.97, 0.97, 85851]
        },
        "TBU": {
            "title": "Height for Age",
            "acc": 0.9721,
            "f1_w": 0.9721,
            "f1_m": 0.9710,
            "rows": [
                ["Not Stunted", 0.98, 0.98, 0.98, 51255],
                ["Stunted", 0.96, 0.97, 0.97, 34596]
            ],
            "macro": [0.97, 0.97, 0.97, 85851],
            "weighted": [0.97, 0.97, 0.97, 85851]
        },
        "BBTB": {
            "title": "Weight for Height",
            "acc": 0.9748,
            "f1_w": 0.9748,
            "f1_m": 0.9731,
            "rows": [
                ["Very Thin", 0.99, 0.94, 0.97, 15376],
                ["Thin", 0.93, 0.97, 0.95, 19220],
                ["Normal", 0.98, 0.98, 0.98, 32035],
                ["Obese", 1.00, 1.00, 1.00, 19220]
            ],
            "macro": [0.98, 0.97, 0.97, 85851],
            "weighted": [0.98, 0.97, 0.97, 85851]
        }
    },
    "test": {
        "BBU": {
            "title": "Weight for Age",
            "acc": 0.9646,
            "f1_w": 0.9649,
            "f1_m": 0.8875,
            "rows": [
                ["Underfed", 0.91, 0.88, 0.90, 1663],
                ["Normal", 0.98, 0.98, 0.98, 8539],
                ["Malnutrition", 0.84, 0.95, 0.89, 401],
                ["Overnutrition", 0.67, 0.93, 0.78, 59]
            ],
            "macro": [0.85, 0.94, 0.89, 10662],
            "weighted": [0.97, 0.96, 0.96, 10662]
        },
        "TBU": {
            "title": "Height for Age",
            "acc": 0.9588,
            "f1_w": 0.9586,
            "f1_m": 0.9540,
            "rows": [
                ["Not Stunted", 0.96, 0.98, 0.97, 6972],
                ["Stunted", 0.96, 0.92, 0.94, 3690]
            ],
            "macro": [0.96, 0.95, 0.95, 10662],
            "weighted": [0.96, 0.96, 0.96, 10662]
        },
        "BBTB": {
            "title": "Weight for Height",
            "acc": 0.9811,
            "f1_w": 0.9816,
            "f1_m": 0.8922,
            "rows": [
                ["Very Thin", 0.87, 0.82, 0.84, 88],
                ["Thin", 0.80, 0.92, 0.86, 540],
                ["Normal", 1.00, 0.99, 0.99, 9905],
                ["Obese", 0.83, 0.94, 0.88, 129]
            ],
            "macro": [0.87, 0.92, 0.89, 10662],
            "weighted": [0.98, 0.98, 0.98, 10662]
        }
    }
}

html = []

for split in ["train", "test"]:
    html.append(f'<div class="accordion accordion-flush border rounded-3" id="acc{split.capitalize()}">')
    for key, d in data[split].items():
        acc_pct = f"{d['acc']*100:.2f}%"
        html.append(f'''
  <div class="accordion-item rounded-3 mb-2 border">
    <h2 class="accordion-header">
      <button class="accordion-button collapsed fw-bold rounded-3" type="button" data-bs-toggle="collapse" data-bs-target="#{split}-{key}">
        <span class="text-primary me-2">[{d['title']}]</span> Accuracy: {acc_pct}
      </button>
    </h2>
    <div id="{split}-{key}" class="accordion-collapse collapse" data-bs-parent="#acc{split.capitalize()}">
      <div class="accordion-body p-0">
        <div class="p-3 bg-light border-bottom d-flex gap-4 small text-muted">
          <span><strong>Accuracy:</strong> {d['acc']:.4f}</span>
          <span><strong>F1 Weighted:</strong> {d['f1_w']:.4f}</span>
          <span><strong>F1 Macro:</strong> {d['f1_m']:.4f}</span>
        </div>
        <div class="table-responsive">
          <table class="table table-hover table-borderless text-center mb-0 small">
            <thead class="table-light text-muted border-bottom">
              <tr>
                <th class="text-start ps-4 w-25">Label</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th class="pe-4">Support</th>
              </tr>
            </thead>
            <tbody>''')
        for r in d['rows']:
            html.append(f'''              <tr>
                <td class="text-start ps-4 fw-medium text-dark">{r[0]}</td>
                <td>{r[1]:.2f}</td>
                <td>{r[2]:.2f}</td>
                <td>{r[3]:.2f}</td>
                <td class="pe-4">{r[4]}</td>
              </tr>''')
        html.append(f'''              <tr class="border-top">
                <td class="text-start ps-4 text-muted">accuracy</td>
                <td></td>
                <td></td>
                <td class="fw-bold">{d['acc']:.2f}</td>
                <td class="pe-4">{d['weighted'][3]}</td>
              </tr>
              <tr>
                <td class="text-start ps-4 text-muted">macro avg</td>
                <td>{d['macro'][0]:.2f}</td>
                <td>{d['macro'][1]:.2f}</td>
                <td>{d['macro'][2]:.2f}</td>
                <td class="pe-4">{d['macro'][3]}</td>
              </tr>
              <tr class="table-light">
                <td class="text-start ps-4 fw-bold text-dark">weighted avg</td>
                <td class="fw-bold">{d['weighted'][0]:.2f}</td>
                <td class="fw-bold">{d['weighted'][1]:.2f}</td>
                <td class="fw-bold">{d['weighted'][2]:.2f}</td>
                <td class="pe-4 fw-bold">{d['weighted'][3]}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>''')
    html.append("</div>")

with open('scratch/tables.html', 'w') as f:
    f.write('\n'.join(html))
