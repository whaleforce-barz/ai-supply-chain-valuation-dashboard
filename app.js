const PAGE_CONFIG = {
  US: {
    title: "美國 AI 供應鏈估值",
    eyebrow: "US AI Supply Chain",
    benchmark: "SOXX / QQQ",
    csv: "./data/us_valuation_screen.csv",
    validation: "./data/us_historical_validation.csv",
    reversion: "./data/us_mean_reversion_results.csv",
    note: "美股 current screen 已完整保留；歷史驗證待累積 point-in-time 月度估值快照。",
  },
  TW: {
    title: "臺灣 AI 供應鏈估值",
    eyebrow: "Taiwan AI Supply Chain",
    benchmark: "0050 / TAIEX",
    csv: "./data/tw_valuation_screen.csv",
    validation: "./data/tw_historical_validation.csv",
    reversion: "./data/tw_mean_reversion_results.csv",
    note: "臺灣頁接入既有 CMoney / MOPS 回測輸出，並保留 sealed-test 與 overfit 警示。",
  },
};

const LABELS = [
  "未充分反映",
  "合理反映",
  "偏熱",
  "過熱",
  "極度過熱 / priced for perfection",
  "資料不足",
];

const LABEL_META = {
  "未充分反映": { className: "cool", score: 1, short: "未充分反映" },
  "合理反映": { className: "fair", score: 2, short: "合理" },
  "偏熱": { className: "warm", score: 3, short: "偏熱" },
  "過熱": { className: "hot", score: 4, short: "過熱" },
  "極度過熱 / priced for perfection": { className: "extreme", score: 5, short: "極度過熱" },
  "資料不足": { className: "missing", score: 0, short: "資料不足" },
};

const SORT_LABELS = {
  severity: "風險",
  ticker: "Ticker",
  company: "公司",
  category: "類型",
  valuation_label: "標籤",
  price: "價格",
  marketCap: "市值",
  trailingPE: "TTM PE",
  forwardPE: "Fwd PE",
  evToEbitda: "EV/EBITDA",
  ps: "PS",
  pb: "PB",
  revenueGrowth: "營收成長",
  grossMargins: "毛利率",
  profitMargins: "淨利率",
  valuation_gap_pct: "估值 gap",
  six_month_return: "半年報酬",
};

const RANGE_META = {
  marketCap: { label: "市值", unit: "B", scale: 1_000_000_000 },
  forwardPE: { label: "Fwd PE", unit: "", scale: 1 },
  trailingPE: { label: "TTM PE", unit: "", scale: 1 },
  pb: { label: "PB", unit: "", scale: 1 },
  ps: { label: "PS", unit: "", scale: 1 },
  revenueGrowth: { label: "營收成長", unit: "%", scale: 0.01 },
  valuation_gap_pct: { label: "估值 gap", unit: "%", scale: 0.01 },
  six_month_return: { label: "半年報酬", unit: "%", scale: 0.01 },
};

const NUMERIC_KEYS = new Set([
  "price",
  "marketCap",
  "trailingPE",
  "forwardPE",
  "evToEbitda",
  "ps",
  "pb",
  "revenueGrowth",
  "grossMargins",
  "ebitdaMargins",
  "profitMargins",
  "six_month_return",
  "benchmark_return",
  "signal_count",
  "six_month_horizon_days",
  "excess_return",
  "convergence_rate",
  "hit_rate",
  "max_drawdown",
  "turnover",
  "current_multiple",
  "own_history_mid",
  "peer_history_mid",
  "fair_mid",
  "fair_low",
  "fair_high",
  "valuation_gap_pct",
  "history_months",
]);

const state = {
  config: null,
  rows: [],
  validation: [],
  reversion: [],
  filtered: [],
  activeLabels: new Set(LABELS),
  sortKey: "severity",
  sortDirection: "desc",
  search: "",
  category: "",
  purity: "",
  ranges: {},
};

const els = {
  status: document.querySelector("#dataStatus"),
  pageTitle: document.querySelector("#pageTitle"),
  pageEyebrow: document.querySelector("#pageEyebrow"),
  pageNote: document.querySelector("#pageNote"),
  benchmark: document.querySelector("#benchmark"),
  csvLink: document.querySelector("#csvLink"),
  validationLink: document.querySelector("#validationLink"),
  reversionLink: document.querySelector("#reversionLink"),
  search: document.querySelector("#searchInput"),
  category: document.querySelector("#categoryFilter"),
  purity: document.querySelector("#purityFilter"),
  labelFilters: document.querySelector("#labelFilters"),
  sortSelect: document.querySelector("#sortSelect"),
  sortDir: document.querySelector("#sortDir"),
  rangeInputs: document.querySelectorAll("[data-range]"),
  clearFilters: document.querySelector("#clearFilters"),
  kpiGrid: document.querySelector("#kpiGrid"),
  filteredCount: document.querySelector("#filteredCount"),
  labelChart: document.querySelector("#labelChart"),
  categoryChart: document.querySelector("#categoryChart"),
  validationSummary: document.querySelector("#validationSummary"),
  reversionSummary: document.querySelector("#reversionSummary"),
  riskList: document.querySelector("#riskList"),
  reasonableList: document.querySelector("#reasonableList"),
  stockTable: document.querySelector("#stockTable"),
  tableMeta: document.querySelector("#tableMeta"),
  activeFilters: document.querySelector("#activeFilters"),
  detailDialog: document.querySelector("#detailDialog"),
  detailContent: document.querySelector("#detailContent"),
  methodAudit: document.querySelector("#methodAudit"),
};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let value = "";
  let quoted = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (quoted) {
      if (char === '"' && next === '"') {
        value += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        value += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(value);
      value = "";
    } else if (char === "\n") {
      row.push(value);
      rows.push(row);
      row = [];
      value = "";
    } else if (char !== "\r") {
      value += char;
    }
  }

  if (value || row.length) {
    row.push(value);
    rows.push(row);
  }

  const headers = rows.shift() || [];
  return rows
    .filter((r) => r.length === headers.length)
    .map((r) => Object.fromEntries(headers.map((header, index) => [header, normalizeCell(header, r[index])])));
}

function normalizeCell(key, value) {
  if (!NUMERIC_KEYS.has(key)) return value || "";
  if (value === "" || value === "nan") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function cleanCategory(category) {
  return String(category || "").replace(/^\d+\.\s*/, "");
}

function formatNumber(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  const abs = Math.abs(value);
  if (abs >= 1_000_000_000_000) return `${(value / 1_000_000_000_000).toFixed(digits)}T`;
  if (abs >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(digits)}B`;
  if (abs >= 1_000_000) return `${(value / 1_000_000).toFixed(digits)}M`;
  return value.toFixed(digits);
}

function formatPct(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return `${(value * 100).toFixed(1)}%`;
}

function labelTag(label) {
  const meta = LABEL_META[label] || LABEL_META["資料不足"];
  return `<span class="tag ${meta.className}">${meta.short}</span>`;
}

function score(row) {
  return LABEL_META[row.valuation_label]?.score ?? 0;
}

function escapeAttr(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function countBy(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "資料不足";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function average(values) {
  const clean = values.filter((v) => v !== null && v !== undefined && !Number.isNaN(v));
  if (!clean.length) return null;
  return clean.reduce((sum, value) => sum + value, 0) / clean.length;
}

function median(values) {
  const clean = values.filter((v) => v !== null && v !== undefined && !Number.isNaN(v)).sort((a, b) => a - b);
  if (!clean.length) return null;
  const mid = Math.floor(clean.length / 2);
  return clean.length % 2 ? clean[mid] : (clean[mid - 1] + clean[mid]) / 2;
}

async function fetchCsv(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return parseCsv(await response.text());
}

async function initDashboard(region) {
  state.config = PAGE_CONFIG[region];
  if (!state.config) return;

  els.pageTitle.textContent = state.config.title;
  els.pageEyebrow.textContent = state.config.eyebrow;
  els.pageNote.textContent = state.config.note;
  els.benchmark.textContent = state.config.benchmark;
  els.csvLink.href = state.config.csv;
  els.validationLink.href = state.config.validation;
  els.reversionLink.href = state.config.reversion;

  try {
    const [rows, validation, reversion] = await Promise.all([
      fetchCsv(state.config.csv),
      fetchCsv(state.config.validation),
      fetchCsv(state.config.reversion),
    ]);
    const reversionByTicker = new Map(reversion.map((row) => [String(row.ticker), row]));
    state.rows = rows.map((row) => ({ ...row, ...(reversionByTicker.get(String(row.ticker)) || {}) }));
    state.validation = validation;
    state.reversion = reversion;
    els.status.textContent = `已載入 ${state.rows.length} 檔`;
    setupFilters();
    bindEvents();
    render();
  } catch (error) {
    els.status.textContent = "資料載入失敗";
    document.querySelector(".content").innerHTML = `
      <section class="panel">
        <h2>資料載入失敗</h2>
        <p>請確認 GitHub Pages 或本地 HTTP server 可讀取 data 目錄。</p>
        <p>${escapeAttr(error.message)}</p>
      </section>
    `;
  }
}

async function initMethod() {
  if (!els.methodAudit) return;
  try {
    const response = await fetch("./data/method_audit.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const audit = await response.json();
    els.methodAudit.innerHTML = renderMethodAudit(audit);
  } catch (error) {
    els.methodAudit.innerHTML = `<div class="panel"><h2>方法資料載入失敗</h2><p>${escapeAttr(error.message)}</p></div>`;
  }
}

function setupFilters() {
  const categories = [...new Set(state.rows.map((row) => row.category))].sort((a, b) =>
    cleanCategory(a).localeCompare(cleanCategory(b), "zh-Hant"),
  );
  els.category.innerHTML = `<option value="">全部</option>${categories
    .map((category) => `<option value="${escapeAttr(category)}">${cleanCategory(category)}</option>`)
    .join("")}`;

  const counts = countBy(state.rows, "valuation_label");
  els.labelFilters.innerHTML = LABELS.map(
    (label) => `
      <button class="label-toggle active" type="button" data-label="${escapeAttr(label)}">
        <span>${labelTag(label)}</span>
        <span class="count">${counts[label] || 0}</span>
      </button>
    `,
  ).join("");
}

function bindEvents() {
  els.search.addEventListener("input", (event) => {
    state.search = event.target.value.trim().toLowerCase();
    render();
  });

  els.category.addEventListener("change", (event) => {
    state.category = event.target.value;
    render();
  });

  els.purity.addEventListener("change", (event) => {
    state.purity = event.target.value;
    render();
  });

  els.labelFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-label]");
    if (!button) return;
    const label = button.dataset.label;
    if (state.activeLabels.has(label)) {
      state.activeLabels.delete(label);
      button.classList.remove("active");
    } else {
      state.activeLabels.add(label);
      button.classList.add("active");
    }
    render();
  });

  els.sortSelect.addEventListener("change", (event) => {
    state.sortKey = event.target.value;
    syncSortControls();
    render();
  });

  els.sortDir.addEventListener("click", () => {
    state.sortDirection = state.sortDirection === "desc" ? "asc" : "desc";
    syncSortControls();
    render();
  });

  els.rangeInputs.forEach((input) => {
    input.addEventListener("input", (event) => {
      const { range, bound } = event.target.dataset;
      const raw = event.target.value.trim();
      state.ranges[range] = state.ranges[range] || {};
      if (raw === "") {
        delete state.ranges[range][bound];
      } else {
        state.ranges[range][bound] = Number(raw);
      }
      if (!Object.keys(state.ranges[range]).length) delete state.ranges[range];
      render();
    });
  });

  els.clearFilters.addEventListener("click", () => {
    resetFilters();
    render();
  });

  document.querySelector("thead").addEventListener("click", (event) => {
    const th = event.target.closest("[data-sort]");
    if (!th) return;
    const next = th.dataset.sort === "valuation_label" ? "severity" : th.dataset.sort;
    if (state.sortKey === next) {
      state.sortDirection = state.sortDirection === "desc" ? "asc" : "desc";
    } else {
      state.sortKey = next;
      state.sortDirection = typeof state.rows[0]?.[next] === "string" ? "asc" : "desc";
    }
    syncSortControls();
    render();
  });

  [els.stockTable, els.riskList, els.reasonableList].forEach((container) => {
    container.addEventListener("click", (event) => {
      const row = event.target.closest("[data-ticker]");
      if (row) openDetail(row.dataset.ticker);
    });
  });
}

function render() {
  state.filtered = state.rows.filter(matchesFilters).sort(compareRows);
  renderKpis();
  renderCharts();
  renderValidation();
  renderReversion();
  renderWatchLists();
  renderActiveFilters();
  renderTable();
  renderSortIndicators();
}

function matchesFilters(row) {
  const haystack = `${row.display_ticker || row.ticker} ${row.company} ${row.role} ${row.model_read} ${row.category}`.toLowerCase();
  const searchOk = !state.search || haystack.includes(state.search);
  const categoryOk = !state.category || row.category === state.category;
  const purityOk = !state.purity || row.revenue_purity === state.purity;
  const labelOk = state.activeLabels.has(row.valuation_label);
  return searchOk && categoryOk && purityOk && labelOk && matchesRanges(row);
}

function matchesRanges(row) {
  return Object.entries(state.ranges).every(([key, bounds]) => {
    const meta = RANGE_META[key];
    const value = row[key];
    if (!meta || value === null || value === undefined || Number.isNaN(value)) return false;
    const displayValue = value / meta.scale;
    const minOk = bounds.min === undefined || displayValue >= bounds.min;
    const maxOk = bounds.max === undefined || displayValue <= bounds.max;
    return minOk && maxOk;
  });
}

function compareRows(a, b) {
  let av = state.sortKey === "severity" ? score(a) : a[state.sortKey];
  let bv = state.sortKey === "severity" ? score(b) : b[state.sortKey];
  if (typeof av === "string" || typeof bv === "string") {
    const result = String(av || "").localeCompare(String(bv || ""), "zh-Hant");
    return state.sortDirection === "desc" ? -result : result;
  }
  av = av ?? -Infinity;
  bv = bv ?? -Infinity;
  const result = av === bv ? String(a.ticker).localeCompare(String(b.ticker)) : av - bv;
  return state.sortDirection === "desc" ? -result : result;
}

function renderKpis() {
  const rows = state.filtered;
  const hot = rows.filter((row) => score(row) >= 4).length;
  const fair = rows.filter((row) => row.valuation_label === "合理反映").length;
  const cool = rows.filter((row) => row.valuation_label === "未充分反映").length;
  const avgGrowth = average(rows.map((row) => row.revenueGrowth));
  const avgGap = average(rows.map((row) => row.valuation_gap_pct));
  const avgSixMonth = average(rows.map((row) => row.six_month_return));

  const cards = [
    ["股票數", rows.length, "目前篩選"],
    ["過熱以上", hot, "高風險"],
    ["合理", fair, "大致合理"],
    ["未充分反映", cool, "相對低估"],
    ["平均營收成長", formatPct(avgGrowth), "可得資料"],
    ["估值 gap 中位", formatPct(median(rows.map((row) => row.valuation_gap_pct))), "均值回歸"],
    ["半年動能", formatPct(avgSixMonth), "可得資料"],
    ["Benchmark", state.config.benchmark, "驗證基準"],
  ];

  els.kpiGrid.innerHTML = cards
    .map(
      ([label, value, note]) => `
        <div class="kpi">
          <span class="value">${value}</span>
          <span class="label">${label} · ${note}</span>
        </div>
      `,
    )
    .join("");
  els.filteredCount.textContent = `${rows.length} / ${state.rows.length}`;
  void avgGap;
}

function renderCharts() {
  renderBarChart(els.labelChart, LABELS.map((label) => [label, state.filtered.filter((row) => row.valuation_label === label).length]));
  const categories = Object.entries(countBy(state.filtered, "category"))
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([category, count]) => [cleanCategory(category), count]);
  renderBarChart(els.categoryChart, categories);
}

function renderBarChart(container, items) {
  const max = Math.max(1, ...items.map(([, count]) => count));
  container.innerHTML = items
    .map(([label, count]) => {
      const pct = (count / max) * 100;
      const meta = LABEL_META[label];
      const colorClass = meta ? meta.className : "";
      return `
        <div class="bar-row">
          <div class="bar-label" title="${escapeAttr(label)}">${label}</div>
          <div class="bar-track"><div class="bar-fill ${colorClass}" style="width:${pct}%"></div></div>
          <div class="metric">${count}</div>
        </div>
      `;
    })
    .join("");
}

function renderValidation() {
  const gates = state.validation.filter((row) => ["validation_gate", "sealed_test", "method_status"].includes(row.section));
  const calibration = state.validation.filter((row) => row.section === "label_calibration" && row.signal_count);
  els.validationSummary.innerHTML = `
    <div class="summary-list">
      ${gates
        .slice(0, 6)
        .map(
          (row) => `
            <div class="summary-item ${row.passed === "False" ? "danger" : row.passed === "True" ? "ok" : ""}">
              <strong>${escapeAttr(row.scenario)}</strong>
              <span>${row.excess_return !== null ? formatPct(row.excess_return) : "-"}</span>
              <p>${escapeAttr(row.note || "等待月度估值快照累積。")}</p>
            </div>
          `,
        )
        .join("")}
    </div>
    <div class="mini-table">
      <table>
        <thead><tr><th>Label</th><th>Signals</th><th>半年報酬</th><th>收斂率</th><th>Hit rate</th></tr></thead>
        <tbody>
          ${calibration
            .map(
              (row) => `
                <tr>
                  <td>${labelTag(row.label)}</td>
                  <td class="numeric">${row.signal_count || "-"}</td>
                  <td class="numeric">${formatPct(row.six_month_return)}</td>
                  <td class="numeric">${formatPct(row.convergence_rate)}</td>
                  <td class="numeric">${formatPct(row.hit_rate)}</td>
                </tr>
              `,
            )
            .join("") || `<tr><td colspan="5">尚未有可驗證的歷史 label calibration。</td></tr>`}
        </tbody>
      </table>
    </div>
  `;
}

function renderReversion() {
  const sorted = [...state.reversion].sort((a, b) => Math.abs(b.valuation_gap_pct || 0) - Math.abs(a.valuation_gap_pct || 0)).slice(0, 8);
  els.reversionSummary.innerHTML = `
    <div class="mini-table">
      <table>
        <thead><tr><th>Ticker</th><th>公司</th><th>Basis</th><th>目前</th><th>合理中位</th><th>Gap</th><th>狀態</th></tr></thead>
        <tbody>
          ${sorted
            .map(
              (row) => `
                <tr>
                  <td><strong>${escapeAttr(row.display_ticker || row.ticker)}</strong></td>
                  <td>${escapeAttr(row.company)}</td>
                  <td>${escapeAttr(row.valuation_basis)}</td>
                  <td class="numeric">${formatNumber(row.current_multiple, 1)}</td>
                  <td class="numeric">${formatNumber(row.fair_mid, 1)}</td>
                  <td class="numeric">${formatPct(row.valuation_gap_pct)}</td>
                  <td>${escapeAttr(row.data_status)}</td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderWatchLists() {
  const risk = [...state.filtered]
    .filter((row) => score(row) >= 4)
    .sort((a, b) => score(b) - score(a) || (b.valuation_gap_pct || 0) - (a.valuation_gap_pct || 0))
    .slice(0, 8);
  const reasonable = [...state.filtered]
    .filter((row) => ["未充分反映", "合理反映"].includes(row.valuation_label))
    .sort((a, b) => score(a) - score(b) || (a.valuation_gap_pct || 0) - (b.valuation_gap_pct || 0))
    .slice(0, 8);
  els.riskList.innerHTML = risk.map(watchItem).join("") || `<div class="empty">無符合項目</div>`;
  els.reasonableList.innerHTML = reasonable.map(watchItem).join("") || `<div class="empty">無符合項目</div>`;
}

function watchItem(row) {
  return `
    <div class="watch-item" data-ticker="${escapeAttr(row.ticker)}">
      <div>
        <div class="ticker">${escapeAttr(row.display_ticker || row.ticker)}</div>
        <div class="company">${escapeAttr(row.company)}</div>
      </div>
      <div class="company">${escapeAttr(cleanCategory(row.category))}</div>
      <div>${labelTag(row.valuation_label)}</div>
    </div>
  `;
}

function renderTable() {
  const rows = state.filtered;
  const arrow = state.sortDirection === "desc" ? "↓" : "↑";
  els.tableMeta.textContent = `${rows.length} rows · ${SORT_LABELS[state.sortKey] || state.sortKey} ${arrow}`;
  els.stockTable.innerHTML = rows
    .map(
      (row) => `
        <tr data-ticker="${escapeAttr(row.ticker)}">
          <td><strong>${escapeAttr(row.display_ticker || row.ticker)}</strong></td>
          <td>${escapeAttr(row.company)}</td>
          <td>${escapeAttr(cleanCategory(row.category))}</td>
          <td>${labelTag(row.valuation_label)}</td>
          <td class="numeric">${formatNumber(row.price, 2)} ${row.currency || ""}</td>
          <td class="numeric">${formatNumber(row.marketCap)}</td>
          <td class="numeric">${formatNumber(row.trailingPE, 1)}</td>
          <td class="numeric">${formatNumber(row.forwardPE, 1)}</td>
          <td class="numeric">${formatNumber(row.evToEbitda, 1)}</td>
          <td class="numeric">${formatNumber(row.ps, 1)}</td>
          <td class="numeric">${formatNumber(row.pb, 1)}</td>
          <td class="numeric">${formatPct(row.revenueGrowth)}</td>
          <td class="numeric">${formatPct(row.valuation_gap_pct)}</td>
          <td class="numeric">${formatPct(row.six_month_return)}</td>
          <td class="read-cell">${escapeAttr(row.model_read || "-")}</td>
        </tr>
      `,
    )
    .join("");
}

function renderActiveFilters() {
  const chips = [];
  if (state.search) chips.push(`搜尋: ${state.search}`);
  if (state.category) chips.push(`類型: ${cleanCategory(state.category)}`);
  if (state.purity) chips.push(`AI 純度: ${state.purity}`);
  if (state.activeLabels.size !== LABELS.length) {
    const active = [...state.activeLabels].map((label) => LABEL_META[label].short).join(", ") || "無";
    chips.push(`標籤: ${active}`);
  }
  for (const [key, bounds] of Object.entries(state.ranges)) {
    const meta = RANGE_META[key];
    if (!meta) continue;
    const min = bounds.min === undefined ? "-∞" : bounds.min;
    const max = bounds.max === undefined ? "∞" : bounds.max;
    chips.push(`${meta.label}: ${min} ~ ${max}${meta.unit}`);
  }
  els.activeFilters.innerHTML = chips.length
    ? chips.map((chip) => `<span class="filter-chip">${escapeAttr(chip)}</span>`).join("")
    : `<span class="filter-chip muted">無進階篩選</span>`;
}

function renderSortIndicators() {
  document.querySelectorAll(".sort-head[data-sort]").forEach((button) => {
    const key = button.dataset.sort === "valuation_label" ? "severity" : button.dataset.sort;
    button.classList.toggle("sorted", key === state.sortKey);
    button.dataset.direction = key === state.sortKey ? state.sortDirection : "";
  });
}

function syncSortControls() {
  const values = [...els.sortSelect.options].map((option) => option.value);
  els.sortSelect.value = values.includes(state.sortKey) ? state.sortKey : "severity";
  els.sortDir.textContent = state.sortDirection === "desc" ? "↓" : "↑";
}

function resetFilters() {
  state.search = "";
  state.category = "";
  state.purity = "";
  state.ranges = {};
  state.activeLabels = new Set(LABELS);
  state.sortKey = "severity";
  state.sortDirection = "desc";
  els.search.value = "";
  els.category.value = "";
  els.purity.value = "";
  els.rangeInputs.forEach((input) => {
    input.value = "";
  });
  document.querySelectorAll("[data-label]").forEach((button) => button.classList.add("active"));
  syncSortControls();
}

function openDetail(ticker) {
  const row = state.rows.find((item) => String(item.ticker) === String(ticker));
  if (!row) return;
  els.detailContent.innerHTML = `
    <section class="detail">
      <h2>${escapeAttr(row.display_ticker || row.ticker)} · ${escapeAttr(row.company)}</h2>
      <p>${escapeAttr(row.role)}</p>
      <div>${labelTag(row.valuation_label)}</div>
      <div class="detail-grid">
        ${detailStat("價格", `${formatNumber(row.price, 2)} ${row.currency || ""}`)}
        ${detailStat("市值", formatNumber(row.marketCap))}
        ${detailStat("AI 純度", row.revenue_purity || "-")}
        ${detailStat("估值 basis", row.valuation_basis || "-")}
        ${detailStat("目前倍數", `${row.valuation_basis || ""} ${formatNumber(row.current_multiple, 1)}`)}
        ${detailStat("合理中位", formatNumber(row.fair_mid, 1))}
        ${detailStat("估值 gap", formatPct(row.valuation_gap_pct))}
        ${detailStat("半年動能", formatPct(row.six_month_return))}
        ${detailStat("資料狀態", row.data_status || "-")}
      </div>
      <p><strong>供應鏈類型：</strong>${escapeAttr(cleanCategory(row.category))}</p>
      <p><strong>估值模型：</strong>${escapeAttr(row.valuation_models || "-")}</p>
      <p><strong>判讀：</strong>${escapeAttr(row.model_read || "-")}</p>
      <p><a href="${escapeAttr(row.source_url)}" target="_blank" rel="noreferrer">外部資料頁</a></p>
    </section>
  `;
  els.detailDialog.showModal();
}

function detailStat(label, value) {
  return `<div class="detail-stat"><span>${escapeAttr(label)}</span><strong>${escapeAttr(value || "-")}</strong></div>`;
}

function renderMethodAudit(audit) {
  return `
    <section class="method-grid">
      <div class="panel">
        <div class="panel-head"><h2>共同估值邏輯</h2><span>${escapeAttr(audit.updated_at || "")}</span></div>
        <ul class="method-list">
          ${(audit.method || []).map((item) => `<li>${escapeAttr(item)}</li>`).join("")}
        </ul>
      </div>
      <div class="panel">
        <div class="panel-head"><h2>Benchmark</h2><span>region-specific</span></div>
        <div class="summary-list">
          ${Object.entries(audit.benchmarks || {})
            .map(
              ([region, item]) => `
                <div class="summary-item">
                  <strong>${region}</strong>
                  <span>${escapeAttr(item.primary)} / ${escapeAttr(item.secondary)}</span>
                  <p>${escapeAttr(item.note || "")}</p>
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
      <div class="panel">
        <div class="panel-head"><h2>資料狀態</h2><span>audit</span></div>
        <div class="summary-list">
          ${Object.entries(audit.data_status || {})
            .map(
              ([region, item]) => `
                <div class="summary-item ${region === "TW" ? "danger" : ""}">
                  <strong>${region} · ${item.screen_rows} 檔</strong>
                  <span>${escapeAttr(item.historical_validation)}</span>
                  <p>${escapeAttr(item.warning)}</p>
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
      <div class="panel">
        <div class="panel-head"><h2>標籤定義</h2><span>${audit.horizon_trading_days} trading days</span></div>
        <div class="label-filters static-labels">
          ${(audit.shared_labels || LABELS).map((label) => `<div class="label-toggle active">${labelTag(label)}</div>`).join("")}
        </div>
      </div>
    </section>
  `;
}

const page = document.body.dataset.page;
if (page === "method") {
  initMethod();
} else if (page in PAGE_CONFIG) {
  initDashboard(page);
}
