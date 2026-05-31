const CSV_PATH = "./ai_supply_chain_valuation_screen.csv";

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
};

const RANGE_META = {
  marketCap: { label: "市值", unit: "B", scale: 1_000_000_000 },
  forwardPE: { label: "Fwd PE", unit: "", scale: 1 },
  evToEbitda: { label: "EV/EBITDA", unit: "", scale: 1 },
  ps: { label: "PS", unit: "", scale: 1 },
  revenueGrowth: { label: "營收成長", unit: "%", scale: 0.01 },
  grossMargins: { label: "毛利率", unit: "%", scale: 0.01 },
  profitMargins: { label: "淨利率", unit: "%", scale: 0.01 },
};

const state = {
  rows: [],
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
  riskList: document.querySelector("#riskList"),
  reasonableList: document.querySelector("#reasonableList"),
  stockTable: document.querySelector("#stockTable"),
  tableMeta: document.querySelector("#tableMeta"),
  activeFilters: document.querySelector("#activeFilters"),
  detailDialog: document.querySelector("#detailDialog"),
  detailContent: document.querySelector("#detailContent"),
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

  const headers = rows.shift();
  return rows
    .filter((r) => r.length === headers.length)
    .map((r) => Object.fromEntries(headers.map((header, index) => [header, normalizeCell(header, r[index])])));
}

function normalizeCell(key, value) {
  const numericKeys = new Set([
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
  ]);
  if (!numericKeys.has(key)) return value || "";
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

  els.stockTable.addEventListener("click", (event) => {
    const row = event.target.closest("[data-ticker]");
    if (row) openDetail(row.dataset.ticker);
  });

  els.riskList.addEventListener("click", (event) => {
    const row = event.target.closest("[data-ticker]");
    if (row) openDetail(row.dataset.ticker);
  });

  els.reasonableList.addEventListener("click", (event) => {
    const row = event.target.closest("[data-ticker]");
    if (row) openDetail(row.dataset.ticker);
  });
}

function optionValues() {
  return {
    severity: true,
    ticker: true,
    company: true,
    price: true,
    marketCap: true,
    trailingPE: true,
    forwardPE: true,
    evToEbitda: true,
    ps: true,
    pb: true,
    revenueGrowth: true,
    grossMargins: true,
    profitMargins: true,
  };
}

function render() {
  state.filtered = state.rows.filter(matchesFilters).sort(compareRows);
  renderKpis();
  renderCharts();
  renderWatchLists();
  renderActiveFilters();
  renderTable();
  renderSortIndicators();
}

function matchesFilters(row) {
  const haystack = `${row.ticker} ${row.company} ${row.role} ${row.model_read} ${row.category}`.toLowerCase();
  const searchOk = !state.search || haystack.includes(state.search);
  const categoryOk = !state.category || row.category === state.category;
  const purityOk = !state.purity || row.revenue_purity === state.purity;
  const labelOk = state.activeLabels.has(row.valuation_label);
  const rangeOk = matchesRanges(row);
  return searchOk && categoryOk && purityOk && labelOk && rangeOk;
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
  let av;
  let bv;
  if (state.sortKey === "severity") {
    av = score(a);
    bv = score(b);
  } else {
    av = a[state.sortKey];
    bv = b[state.sortKey];
  }

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
  const warm = rows.filter((row) => row.valuation_label === "偏熱").length;
  const fair = rows.filter((row) => row.valuation_label === "合理反映").length;
  const cool = rows.filter((row) => row.valuation_label === "未充分反映").length;
  const missing = rows.filter((row) => row.valuation_label === "資料不足").length;
  const avgGrowth = average(rows.map((row) => row.revenueGrowth).filter((v) => v !== null));

  const cards = [
    ["股票數", rows.length, "目前篩選"],
    ["過熱以上", hot, "高風險"],
    ["偏熱", warm, "估值已高"],
    ["合理", fair, "大致合理"],
    ["未充分反映", cool, "相對低估"],
    ["平均營收成長", formatPct(avgGrowth), "可得資料"],
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
  void missing;
}

function renderCharts() {
  renderBarChart(els.labelChart, LABELS.map((label) => [label, countMatching(state.filtered, "valuation_label", label)]));

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

function renderWatchLists() {
  const risk = [...state.filtered]
    .filter((row) => score(row) >= 4)
    .sort((a, b) => score(b) - score(a) || (b.forwardPE || 0) - (a.forwardPE || 0))
    .slice(0, 8);
  const reasonable = [...state.filtered]
    .filter((row) => ["未充分反映", "合理反映"].includes(row.valuation_label))
    .sort((a, b) => score(a) - score(b) || (b.revenueGrowth || 0) - (a.revenueGrowth || 0))
    .slice(0, 8);

  els.riskList.innerHTML = risk.map(watchItem).join("") || `<div class="empty">無符合項目</div>`;
  els.reasonableList.innerHTML = reasonable.map(watchItem).join("") || `<div class="empty">無符合項目</div>`;
}

function watchItem(row) {
  return `
    <div class="watch-item" data-ticker="${escapeAttr(row.ticker)}">
      <div>
        <div class="ticker">${row.ticker}</div>
        <div class="company">${row.company}</div>
      </div>
      <div class="company">${cleanCategory(row.category)}</div>
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
          <td><strong>${row.ticker}</strong></td>
          <td>${row.company}</td>
          <td>${cleanCategory(row.category)}</td>
          <td>${labelTag(row.valuation_label)}</td>
          <td class="numeric">${formatNumber(row.price, 2)} ${row.currency || ""}</td>
          <td class="numeric">${formatNumber(row.marketCap)}</td>
          <td class="numeric">${formatNumber(row.trailingPE, 1)}</td>
          <td class="numeric">${formatNumber(row.forwardPE, 1)}</td>
          <td class="numeric">${formatNumber(row.evToEbitda, 1)}</td>
          <td class="numeric">${formatNumber(row.ps, 1)}</td>
          <td class="numeric">${formatNumber(row.pb, 1)}</td>
          <td class="numeric">${formatPct(row.revenueGrowth)}</td>
          <td class="numeric">${formatPct(row.grossMargins)}</td>
          <td class="numeric">${formatPct(row.profitMargins)}</td>
          <td class="read-cell">${row.model_read || "-"}</td>
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
  if (state.sortKey in optionValues()) {
    els.sortSelect.value = state.sortKey;
  } else {
    els.sortSelect.value = "severity";
  }
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
  const row = state.rows.find((item) => item.ticker === ticker);
  if (!row) return;
  els.detailContent.innerHTML = `
    <section class="detail">
      <h2>${row.ticker} · ${row.company}</h2>
      <p>${row.role}</p>
      <div>${labelTag(row.valuation_label)}</div>
      <div class="detail-grid">
        ${detailStat("價格", `${formatNumber(row.price, 2)} ${row.currency || ""}`)}
        ${detailStat("市值", formatNumber(row.marketCap))}
        ${detailStat("AI 純度", row.revenue_purity || "-")}
        ${detailStat("Fwd PE", formatNumber(row.forwardPE, 1))}
        ${detailStat("EV/EBITDA", formatNumber(row.evToEbitda, 1))}
        ${detailStat("PS", formatNumber(row.ps, 1))}
        ${detailStat("營收成長", formatPct(row.revenueGrowth))}
        ${detailStat("毛利率", formatPct(row.grossMargins))}
        ${detailStat("淨利率", formatPct(row.profitMargins))}
      </div>
      <p><strong>供應鏈類型：</strong>${cleanCategory(row.category)}</p>
      <p><strong>估值模型：</strong>${row.valuation_models || "-"}</p>
      <p><strong>判讀：</strong>${row.model_read || "-"}</p>
      <p><a href="${row.source_url}" target="_blank" rel="noreferrer">Yahoo Finance</a></p>
    </section>
  `;
  els.detailDialog.showModal();
}

function detailStat(label, value) {
  return `<div class="detail-stat"><span>${label}</span><strong>${value || "-"}</strong></div>`;
}

function countBy(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "資料不足";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function countMatching(rows, key, value) {
  return rows.filter((row) => row[key] === value).length;
}

function average(values) {
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function escapeAttr(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function init() {
  try {
    const response = await fetch(CSV_PATH);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const text = await response.text();
    state.rows = parseCsv(text);
    els.status.textContent = `已載入 ${state.rows.length} 檔`;
    setupFilters();
    bindEvents();
    render();
  } catch (error) {
    els.status.textContent = "資料載入失敗";
    document.querySelector(".content").innerHTML = `
      <section class="panel">
        <h2>資料載入失敗</h2>
        <p>請從工作目錄啟動本地 HTTP server，再開啟此頁。</p>
        <p>${escapeAttr(error.message)}</p>
      </section>
    `;
  }
}

init();
