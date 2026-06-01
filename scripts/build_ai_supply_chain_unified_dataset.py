#!/usr/bin/env python3
"""Build unified US/Taiwan AI supply-chain valuation dashboard data.

The site is static, so this script normalizes the local research outputs into
CSV/JSON files that are loaded by the browser. The valuation framework is shared
across regions; only the data adapters differ.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


LABELS = [
    "未充分反映",
    "合理反映",
    "偏熱",
    "過熱",
    "極度過熱 / priced for perfection",
    "資料不足",
]

LABEL_SCORE = {
    "資料不足": 0,
    "未充分反映": 1,
    "合理反映": 2,
    "偏熱": 3,
    "過熱": 4,
    "極度過熱 / priced for perfection": 5,
}

SCREEN_FIELDS = [
    "region",
    "ticker",
    "display_ticker",
    "company",
    "exchange",
    "currency",
    "category",
    "supply_chain_category",
    "role",
    "industry_class",
    "industry_model_class",
    "stage",
    "lifecycle_stage",
    "revenue_purity",
    "valuation_models",
    "valuation_basis",
    "selected_model",
    "fallback_model",
    "model_confidence",
    "coverage_status",
    "model_validation_signal_count",
    "model_validation_convergence_rate",
    "model_validation_hit_rate",
    "model_validation_note",
    "valuation_label",
    "model_read",
    "data_status",
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
    "source_url",
]

VALIDATION_FIELDS = [
    "region",
    "section",
    "scenario",
    "label",
    "signal_count",
    "six_month_horizon_days",
    "six_month_return",
    "benchmark_return",
    "excess_return",
    "convergence_rate",
    "hit_rate",
    "max_drawdown",
    "turnover",
    "transaction_cost_case",
    "passed",
    "note",
]

MEAN_REVERSION_FIELDS = [
    "region",
    "ticker",
    "display_ticker",
    "company",
    "industry_model_class",
    "valuation_basis",
    "current_multiple",
    "own_history_mid",
    "peer_history_mid",
    "fair_mid",
    "fair_low",
    "fair_high",
    "valuation_gap_pct",
    "history_months",
    "data_status",
    "note",
]

STOCK_POOL_FIELDS = [
    "region",
    "ticker",
    "display_ticker",
    "company",
    "exchange",
    "currency",
    "category",
    "industry_model_class",
    "stage",
    "revenue_purity",
    "role",
]

SNAPSHOT_FIELDS = [
    "region",
    "signal_date",
    "future_date",
    "ticker",
    "display_ticker",
    "company",
    "industry_model_class",
    "lifecycle_stage",
    "label",
    "close",
    "future_close",
    "future_return",
    "peer_return",
    "benchmark_return",
    "ttm_pe",
    "forward_pe",
    "ev_to_ebitda",
    "ps",
    "pb",
    "implied_cagr",
    "current_cagr",
    "revenue_growth",
    "data_status",
    "note",
]

MODEL_VALIDATION_FIELDS = [
    "region",
    "industry_model_class",
    "lifecycle_stage",
    "candidate_model",
    "candidate_rank",
    "is_selected",
    "fallback_model",
    "signal_count",
    "coverage_ratio",
    "convergence_rate",
    "hit_rate",
    "median_excess_return",
    "label_calibration_score",
    "model_score",
    "model_confidence",
    "coverage_status",
    "method_status",
    "reason",
]

MODEL_REGISTRY = {
    "software_platform": {
        "patterns": ["軟體", "平台", "IP"],
        "candidates": ["PS", "Forward PE", "Peer Relative Z", "Own History Percentile"],
        "fallback": "PS",
        "why": "平台型公司常有高毛利與折舊差異，PS/FCF margin 比單一 PE 更穩定。",
        "gaps": "FCF margin, gross profit, Rule of 40, AI revenue purity",
    },
    "high_margin_equipment": {
        "patterns": ["半導體設備", "ASIC", "測試", "交換機", "光通訊"],
        "candidates": ["Forward PE", "EV/EBITDA", "PEG/implied CAGR", "Peer Relative Z", "Own History Percentile"],
        "fallback": "Forward PE",
        "why": "高毛利成長股優先測試 forward earnings 與 implied CAGR 是否能解釋估值。",
        "gaps": "forward estimate history, backlog, gross margin, customer concentration",
    },
    "capital_intensive": {
        "patterns": ["Foundry", "封測", "代工", "資本密集", "晶圓"],
        "candidates": ["EV/EBITDA", "Forward PE", "PB", "Own History Percentile", "Peer Relative Z"],
        "fallback": "EV/EBITDA",
        "why": "資本密集產業需要同時看 EBITDA、折舊、利用率與 ROIC。",
        "gaps": "utilization, capex後FCF, ROIC, depreciation cycle",
    },
    "odm_ems": {
        "patterns": ["ODM", "EMS", "Rack", "server", "Server"],
        "candidates": ["EV/EBITDA", "Forward PE", "Peer Relative Z", "Own History Percentile"],
        "fallback": "EV/EBITDA",
        "why": "低毛利代工不適合高 PS，應看 EBIT/EBITDA 與現金轉換。",
        "gaps": "EBIT margin, FCF conversion, working capital, pass-through revenue",
    },
    "components_power_cooling": {
        "patterns": ["零組件", "電源", "供電", "散熱", "液冷", "連接器"],
        "candidates": ["Forward PE", "EV/EBITDA", "PB", "Peer Relative Z", "Own History Percentile"],
        "fallback": "Forward PE",
        "why": "元件、電力與散熱供應鏈通常以 earnings multiple 搭配 margin stability 驗證。",
        "gaps": "gross margin stability, backlog, customer qualification, ASP trend",
    },
    "materials_cyclical": {
        "patterns": ["材料", "PCB", "CCL", "載板", "銅箔"],
        "candidates": ["PB", "EV/EBITDA", "Forward PE", "Own History Percentile", "Peer Relative Z"],
        "fallback": "PB",
        "why": "材料與循環股需避免用高峰 EPS 判斷便宜，PB 與 normalized EBITDA 更保守。",
        "gaps": "mid-cycle margin, inventory cycle, commodity spread, ROIC",
    },
    "utilities_power": {
        "patterns": ["公用事業", "電力", "工程服務", "備援電力"],
        "candidates": ["PB", "EV/EBITDA", "Forward PE", "Peer Relative Z"],
        "fallback": "PB",
        "why": "資產型與電力基礎設施需看 book value、regulated return 與專案現金流。",
        "gaps": "regulated ROE, load growth, project cash flow, financing cost",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd().parent)
    parser.add_argument("--out", type=Path, default=Path.cwd() / "data")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean_cell(row.get(field)) for field in fields})


def write_stock_pool_md(path: Path, title: str, rows: list[dict[str, object]]) -> None:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("category") or "未分類")].append(row)

    lines = [
        f"# {title}",
        "",
        "此檔案只列股票池，不混入另一個市場。估值資料請看同市場的 valuation screen CSV。",
        "",
        f"- 股票數：{len(rows)}",
        f"- 更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    for category in sorted(grouped, key=lambda value: re.sub(r"^\d+\.\s*", "", value)):
        items = sorted(grouped[category], key=lambda row: str(row.get("display_ticker") or row.get("ticker")))
        lines.extend([f"## {category}", "", "|Ticker|公司|交易所|產業模型|階段|AI 純度|角色|", "|---|---|---|---|---|---|---|"])
        for row in items:
            lines.append(
                "|"
                + "|".join(
                    md_cell(row.get(field, ""))
                    for field in ["display_ticker", "company", "exchange", "industry_model_class", "stage", "revenue_purity", "role"]
                )
                + "|"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def clean_cell(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    return value


def safe_float(value: object) -> float | None:
    try:
        if value in ("", None, "nan", "None"):
            return None
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except (TypeError, ValueError):
        return None


def median(values: list[float]) -> float | None:
    clean = sorted(v for v in values if v is not None and math.isfinite(v) and v > 0)
    if not clean:
        return None
    mid = len(clean) // 2
    if len(clean) % 2:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2


def percentile(values: list[float], pct: float) -> float | None:
    clean = sorted(v for v in values if v is not None and math.isfinite(v) and v > 0)
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    idx = (len(clean) - 1) * pct
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return clean[int(idx)]
    return clean[lo] + (clean[hi] - clean[lo]) * (idx - lo)


def fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def detect_exchange_map(md_path: Path) -> dict[str, str]:
    if not md_path.exists():
        return {}
    text = md_path.read_text(encoding="utf-8")
    exchange = {}
    for ticker, suffix in re.findall(r"(\d{4})\.(TW|TWO)", text):
        exchange[ticker] = suffix
    return exchange


def valuation_basis_for(model_class: str, source: str = "") -> str:
    text = f"{model_class} {source}".lower()
    if any(term in text for term in ["odm", "ems", "rack", "server"]):
        return "EV/EBITDA, EV/EBIT, FCF conversion"
    if any(term in text for term in ["foundry", "封測", "測試", "osat", "capital", "晶圓"]):
        return "EV/EBITDA, normalized PE, utilization/ROIC"
    if any(term in text for term in ["asic", "ip", "software", "平台", "design"]):
        return "Forward PE, PEG/implied CAGR, EV/EBITDA"
    if any(term in text for term in ["power", "電源", "供電", "cooling", "散熱", "liquid"]):
        return "PE, EV/EBITDA, margin stability"
    if any(term in text for term in ["memory", "dram", "nand", "material", "材料", "pcb", "ccl"]):
        return "Mid-cycle PB, normalized EBITDA"
    return "PE, PB, EV/EBITDA peer/history blend"


def registry_entry_for(model_class: str) -> dict[str, object]:
    text = model_class.lower()
    for entry in MODEL_REGISTRY.values():
        if any(pattern.lower() in text for pattern in entry["patterns"]):
            return entry
    return {
        "patterns": [],
        "candidates": ["Forward PE", "EV/EBITDA", "PB", "Peer Relative Z"],
        "fallback": "Forward PE",
        "why": "一般成熟公司先以 earnings / EBITDA / book value 的 peer/history blend 測試。",
        "gaps": "forward estimates, peer range, own history",
    }


def candidate_value(row: dict[str, object], model: str) -> float | None:
    if model == "Forward PE":
        return safe_float(row.get("forwardPE")) or safe_float(row.get("forward_pe")) or safe_float(row.get("ttm_pe")) or safe_float(row.get("trailingPE"))
    if model == "EV/EBITDA":
        return safe_float(row.get("evToEbitda")) or safe_float(row.get("ev_to_ebitda"))
    if model == "PB":
        return safe_float(row.get("pb"))
    if model == "PS":
        return safe_float(row.get("ps"))
    if model == "PEG/implied CAGR":
        return safe_float(row.get("implied_cagr"))
    if model in {"Peer Relative Z", "Own History Percentile"}:
        return safe_float(row.get("ttm_pe")) or safe_float(row.get("trailingPE")) or safe_float(row.get("pb"))
    return None


def confidence_from_metrics(signal_count: int, coverage: float | None, convergence: float | None, hit_rate: float | None) -> tuple[str, str]:
    coverage = coverage or 0
    convergence = convergence or 0
    hit_rate = hit_rate or 0
    if signal_count >= 30 and coverage >= 0.55 and convergence >= 0.5 and hit_rate >= 0.45:
        return "high", "validated"
    if signal_count >= 12 and coverage >= 0.35:
        return "medium", "partial_history"
    if signal_count > 0:
        return "low", "low_sample_fallback"
    return "none", "coverage_gap"


def metric_gap(value: float | None, own_mid: float | None, peer_mid: float | None) -> float | None:
    fair = blend_mid(own_mid, peer_mid)
    if value is None or fair is None or fair <= 0:
        return None
    return (value - fair) / fair


def label_calibration_score(items: list[dict[str, float]]) -> float | None:
    clean = [item for item in items if item.get("gap") is not None and item.get("future_return") is not None]
    if len(clean) < 6:
        return None
    clean.sort(key=lambda item: item["gap"])
    third = max(1, len(clean) // 3)
    cheap = clean[:third]
    expensive = clean[-third:]
    cheap_ret = sum(item["future_return"] for item in cheap) / len(cheap)
    expensive_ret = sum(item["future_return"] for item in expensive) / len(expensive)
    return 1.0 if cheap_ret >= expensive_ret else 0.0


def normalize_us_rows(workspace: Path) -> list[dict[str, object]]:
    rows = read_csv(workspace / "ai_supply_chain_valuation_screen.csv")
    normalized = []
    for row in rows:
        ticker = row.get("ticker", "")
        if "." in ticker:
            continue
        industry = row.get("industry_class", "")
        stage = row.get("stage", "")
        label, read = normalize_us_label(row)
        data_status = "complete" if not row.get("fetch_error") else "資料不足"
        normalized.append(
            {
                **row,
                "region": "US",
                "display_ticker": ticker,
                "exchange": "US",
                "supply_chain_category": row.get("category", ""),
                "industry_model_class": industry,
                "lifecycle_stage": stage,
                "valuation_basis": valuation_basis_for(industry, row.get("valuation_models", "")),
                "selected_model": "",
                "fallback_model": "",
                "model_confidence": "",
                "coverage_status": "",
                "model_validation_signal_count": "",
                "model_validation_convergence_rate": "",
                "model_validation_hit_rate": "",
                "model_validation_note": "",
                "valuation_label": label,
                "model_read": read,
                "data_status": data_status,
                "six_month_return": "",
                "benchmark_return": "",
                "source_url": row.get("source_url") or f"https://finance.yahoo.com/quote/{ticker}",
            }
        )
    return normalized


def normalize_us_label(row: dict[str, str]) -> tuple[str, str]:
    original = row.get("valuation_label") or "資料不足"
    original_read = row.get("model_read") or ""
    if original != "資料不足":
        return original if original in LABEL_SCORE else "資料不足", original_read

    industry = row.get("industry_class", "")
    pe = safe_float(row.get("forwardPE")) or safe_float(row.get("trailingPE"))
    ev = safe_float(row.get("evToEbitda"))
    ps = safe_float(row.get("ps"))
    pb = safe_float(row.get("pb"))
    margin = safe_float(row.get("profitMargins"))
    growth = safe_float(row.get("revenueGrowth"))
    has_multiple = any(value is not None and value > 0 for value in [pe, ev, ps, pb])
    if not has_multiple:
        return "資料不足", original_read or "缺少可用的 PE / EV/EBITDA / PS / PB 基礎"

    suffix = "；provisional label，仍需補完整週期/現金流資料覆核"

    if "封測" in industry:
        if ev is not None and ev > 25:
            return "過熱", "資本密集公司 EV/EBITDA > 25x，估值要求高利用率多年維持" + suffix
        if pe is not None and pe > 35:
            return "過熱", "資本密集公司 PE > 35x，需要 capex 後 ROIC 明確改善" + suffix
        if pe is not None and pe > 24:
            return "偏熱", "資本密集公司 PE 已高於保守區間，需用 utilization / FCF 驗證" + suffix
        if ev is not None and ev <= 18 or pe is not None:
            return "合理反映", "已有 PE/EV 倍數可初步判斷，估值未明顯脫離資本密集模型" + suffix

    if "材料" in industry:
        if ev is not None and ev > 15 or pb is not None and pb > 4:
            return "偏熱", "材料/循環股倍數偏高，需要 mid-cycle EBITDA / ROIC 支撐" + suffix
        if pe is not None and pe <= 18 or ev is not None and ev <= 13:
            return "合理反映", "以可得 PE/EV/EBITDA 看未明顯過熱，但仍需 mid-cycle 覆核" + suffix
        return "偏熱", "材料/循環股缺 mid-cycle 邊際資料，先以可得倍數標為偏熱覆核" + suffix

    if "ODM" in industry:
        if ps is not None and ps > 3 or ev is not None and ev > 18:
            return "偏熱", "低毛利代工估值需要 EBIT margin 與現金轉換支持" + suffix
        if pe is not None and pe <= 20:
            return "合理反映", "低毛利代工以 forward PE / EV/EBITDA 看尚可解釋" + suffix
        return "偏熱", "低毛利代工估值已要求 AI server margin 改善" + suffix

    if "公用事業" in industry:
        if ps is None and (pe is None or pe < 0) and (pb is not None and pb > 3):
            return "過熱", "早期能源/核能標的缺穩定營收與 earnings，價格已反映遠期情境" + suffix
        if pe is not None and pe > 30:
            return "過熱", "資本密集能源/公用事業 PE > 30x，需負載成長與監管支持" + suffix
        return "合理反映", "以可得資產/盈餘倍數初步可解釋，仍需專案現金流覆核" + suffix

    if (margin is not None and margin < 0) or pe is not None and pe < 0:
        if ps is not None and ps > 5 or ev is not None and ev > 40:
            return "過熱", "虧損或轉機型標的估值已要求明確轉盈" + suffix
        if pe is not None and pe > 0 and pe <= 30:
            return "偏熱", "forward PE 可用但當期仍虧損，需 breakeven / cash burn 覆核" + suffix
        return "資料不足", original_read or "虧損公司缺 breakeven revenue / cash burn 資料"

    if pe is not None and pe <= 20 and (growth is None or growth >= 0):
        return "合理反映", "可得 PE 顯示估值未明顯過熱" + suffix
    if pe is not None and pe <= 35:
        return "偏熱", "可得 PE 已偏高但仍可給出初步標籤" + suffix
    if pe is not None:
        return "過熱", "可得 PE 已高，需成長與現金流兌現" + suffix
    return "資料不足", original_read or "缺少可用估值基礎"


def latest_tw_rows(workspace: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, dict[str, str]]]:
    out = workspace / "outputs/taiwan-ai-valuation-threeway-revenue-2025-05-to-2026-05"
    signals = read_csv(out / "monthly_signals.csv")
    universe = {row["ticker"]: row for row in read_csv(out / "universe_split.csv")}
    latest_date = max(row["signal_date"] for row in signals)
    return [row for row in signals if row["signal_date"] == latest_date], signals, universe


def normalize_tw_rows(workspace: Path) -> list[dict[str, object]]:
    latest, _signals, universe = latest_tw_rows(workspace)
    exchanges = detect_exchange_map(workspace / "research/taiwan-ai-supply-chain-map.md")
    normalized = []
    for row in latest:
        ticker = row["ticker"]
        suffix = exchanges.get(ticker, "TW")
        display = f"{ticker}.{suffix}"
        model_class = row.get("model_class", "")
        meta = universe.get(ticker, {})
        market_cap_b = safe_float(row.get("market_cap_b"))
        revenue_growth = safe_float(row.get("revenue_3m_yoy_avg"))
        model_read = (
            f"TTM PE {row.get('ttm_pe') or 'NA'} / PB {row.get('pb') or 'NA'}；"
            f"隱含CAGR {pct_text(safe_float(row.get('implied_cagr')))}，"
            f"目前CAGR {pct_text(safe_float(row.get('current_cagr')))}。"
            "臺股頁保留 sealed-test 與 overfit 警示。"
        )
        normalized.append(
            {
                "region": "TW",
                "ticker": ticker,
                "display_ticker": display,
                "company": row.get("company", ""),
                "exchange": suffix,
                "currency": "TWD",
                "category": model_class,
                "supply_chain_category": model_class,
                "role": meta.get("roles", ""),
                "industry_class": model_class,
                "industry_model_class": model_class,
                "stage": meta.get("stage", ""),
                "lifecycle_stage": meta.get("stage", ""),
                "revenue_purity": infer_tw_purity(model_class, meta.get("roles", "")),
                "valuation_models": valuation_basis_for(model_class),
                "valuation_basis": valuation_basis_for(model_class),
                "selected_model": "",
                "fallback_model": "",
                "model_confidence": "",
                "coverage_status": "",
                "model_validation_signal_count": "",
                "model_validation_convergence_rate": "",
                "model_validation_hit_rate": "",
                "model_validation_note": "",
                "valuation_label": row.get("label") if row.get("label") in LABEL_SCORE else "資料不足",
                "model_read": model_read,
                "data_status": row.get("data_status") or "complete",
                "price": row.get("close", ""),
                "marketCap": fmt_float(market_cap_b * 100_000_000 if market_cap_b is not None else None),
                "trailingPE": row.get("ttm_pe", ""),
                "forwardPE": "",
                "evToEbitda": "",
                "ps": "",
                "pb": row.get("pb", ""),
                "revenueGrowth": fmt_float(revenue_growth / 100 if revenue_growth is not None else None),
                "grossMargins": "",
                "ebitdaMargins": "",
                "profitMargins": "",
                "six_month_return": fmt_float(safe_float(row.get("momentum_6m"))),
                "benchmark_return": fmt_float(
                    (safe_float(row.get("momentum_6m")) or 0) - (safe_float(row.get("relative_momentum_6m")) or 0)
                    if row.get("momentum_6m") and row.get("relative_momentum_6m")
                    else None
                ),
                "source_url": f"https://www.wantgoo.com/stock/{ticker}",
            }
        )
    return normalized


def pct_text(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value * 100:.1f}%"


def infer_tw_purity(model_class: str, role: str) -> str:
    text = f"{model_class} {role}"
    if any(term in text for term in ["AI server", "Rack", "ASIC", "散熱", "液冷", "交換機", "光通訊"]):
        return "高"
    if any(term in text for term in ["Foundry", "封測", "電源", "PCB", "CCL", "連接器"]):
        return "中高"
    return "中"


def build_mean_reversion(region: str, rows: list[dict[str, object]], signals: list[dict[str, str]] | None = None) -> list[dict[str, object]]:
    result = []
    if region == "TW" and signals:
        by_ticker: dict[str, list[dict[str, str]]] = defaultdict(list)
        by_class: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in signals:
            by_ticker[row["ticker"]].append(row)
            by_class[row["model_class"]].append(row)
        for row in rows:
            ticker = str(row["ticker"])
            model_class = str(row["industry_model_class"])
            basis = "PE" if safe_float(row.get("trailingPE")) else "PB"
            key = "ttm_pe" if basis == "PE" else "pb"
            current = safe_float(row.get("trailingPE" if basis == "PE" else "pb"))
            own_vals = [safe_float(item.get(key)) for item in by_ticker.get(ticker, [])]
            peer_vals = [safe_float(item.get(key)) for item in by_class.get(model_class, [])]
            own_mid = median([v for v in own_vals if v is not None])
            peer_mid = median([v for v in peer_vals if v is not None])
            fair_mid = blend_mid(own_mid, peer_mid)
            low = percentile([v for v in own_vals if v is not None], 0.25) or fair_mid
            high = percentile([v for v in own_vals if v is not None], 0.75) or fair_mid
            status = "complete" if len([v for v in own_vals if v is not None]) >= 6 else "歷史不足"
            result.append(mean_row(region, row, basis, current, own_mid, peer_mid, fair_mid, low, high, len(own_vals), status))
        return result

    by_class_current: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        basis_key = "forwardPE" if safe_float(row.get("forwardPE")) else "trailingPE"
        if safe_float(row.get(basis_key)) is None:
            basis_key = "pb"
        value = safe_float(row.get(basis_key))
        if value is not None:
            by_class_current[str(row["industry_model_class"])].append(value)
    for row in rows:
        basis_key = "forwardPE" if safe_float(row.get("forwardPE")) else "trailingPE"
        basis = "Forward PE" if basis_key == "forwardPE" else "PE"
        if safe_float(row.get(basis_key)) is None:
            basis_key = "pb"
            basis = "PB"
        current = safe_float(row.get(basis_key))
        peer_mid = median(by_class_current.get(str(row["industry_model_class"]), []))
        fair_mid = peer_mid
        low = percentile(by_class_current.get(str(row["industry_model_class"]), []), 0.25) or fair_mid
        high = percentile(by_class_current.get(str(row["industry_model_class"]), []), 0.75) or fair_mid
        result.append(mean_row(region, row, basis, current, None, peer_mid, fair_mid, low, high, 0, "歷史不足"))
    return result


def blend_mid(own_mid: float | None, peer_mid: float | None) -> float | None:
    if own_mid is not None and peer_mid is not None:
        return (own_mid + peer_mid) / 2
    return own_mid if own_mid is not None else peer_mid


def mean_row(
    region: str,
    row: dict[str, object],
    basis: str,
    current: float | None,
    own_mid: float | None,
    peer_mid: float | None,
    fair_mid: float | None,
    low: float | None,
    high: float | None,
    history_months: int,
    status: str,
) -> dict[str, object]:
    gap = (current - fair_mid) / fair_mid if current is not None and fair_mid and fair_mid > 0 else None
    note = "50%自身歷史 + 50%同業分布" if status == "complete" else "自身歷史不足，先以同業/目前分布做 fallback"
    return {
        "region": region,
        "ticker": row.get("ticker", ""),
        "display_ticker": row.get("display_ticker", row.get("ticker", "")),
        "company": row.get("company", ""),
        "industry_model_class": row.get("industry_model_class", ""),
        "valuation_basis": basis,
        "current_multiple": fmt_float(current),
        "own_history_mid": fmt_float(own_mid),
        "peer_history_mid": fmt_float(peer_mid),
        "fair_mid": fmt_float(fair_mid),
        "fair_low": fmt_float(low),
        "fair_high": fmt_float(high),
        "valuation_gap_pct": fmt_float(gap),
        "history_months": history_months,
        "data_status": status,
        "note": note,
    }


def build_tw_validation(workspace: Path) -> list[dict[str, object]]:
    out = workspace / "outputs/taiwan-ai-valuation-threeway-revenue-2025-05-to-2026-05"
    signals = read_csv(out / "monthly_signals.csv")
    rows = []
    rows.extend(validation_gate_rows("TW", read_csv(out / "validation_gates.csv")))
    rows.extend(validation_gate_rows("TW", read_csv(out / "post_test_audit.csv"), section="sealed_test"))
    rows.extend(metrics_rows("TW", read_csv(out / "metrics.csv")))
    rows.extend(label_calibration_rows("TW", signals))
    return rows


def validation_gate_rows(region: str, gates: list[dict[str, str]], section: str = "validation_gate") -> list[dict[str, object]]:
    rows = []
    for gate in gates:
        rows.append(
            {
                "region": region,
                "section": section,
                "scenario": gate.get("gate", ""),
                "label": "",
                "signal_count": "",
                "six_month_horizon_days": 126,
                "six_month_return": "",
                "benchmark_return": "",
                "excess_return": gate.get("excess_return", ""),
                "convergence_rate": "",
                "hit_rate": "",
                "max_drawdown": "",
                "turnover": "",
                "transaction_cost_case": gate.get("cost_case", ""),
                "passed": gate.get("passed", ""),
                "note": gate.get("description", ""),
            }
        )
    return rows


def metrics_rows(region: str, metrics: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for row in metrics:
        if not row.get("total_return") and not row.get("excess_return"):
            continue
        rows.append(
            {
                "region": region,
                "section": "portfolio_backtest",
                "scenario": row.get("scenario", ""),
                "label": "",
                "signal_count": row.get("periods", ""),
                "six_month_horizon_days": 126,
                "six_month_return": row.get("total_return", ""),
                "benchmark_return": row.get("benchmark_total_return", ""),
                "excess_return": row.get("excess_return", ""),
                "convergence_rate": "",
                "hit_rate": row.get("hit_rate", ""),
                "max_drawdown": row.get("max_drawdown", ""),
                "turnover": row.get("avg_turnover", ""),
                "transaction_cost_case": row.get("cost_case", ""),
                "passed": "",
                "note": "臺灣既有三段式 revenue_acceleration_value 回測輸出；sealed test 不用於調參。",
            }
        )
    return rows


def label_calibration_rows(region: str, signals: list[dict[str, str]]) -> list[dict[str, object]]:
    by_ticker = defaultdict(list)
    for row in signals:
        by_ticker[row["ticker"]].append(row)
    for ticker in by_ticker:
        by_ticker[ticker].sort(key=lambda item: item["signal_date"])

    buckets: dict[str, list[tuple[float, bool]]] = defaultdict(list)
    for ticker, items in by_ticker.items():
        for row in items:
            start_date = datetime.fromisoformat(row["signal_date"])
            target = start_date + timedelta(days=182)
            future = next((item for item in items if datetime.fromisoformat(item["signal_date"]) >= target), None)
            if not future:
                continue
            close = safe_float(row.get("close"))
            future_close = safe_float(future.get("close"))
            if not close or not future_close:
                continue
            label = row.get("label", "資料不足")
            start_distance = abs(LABEL_SCORE.get(label, 0) - 2)
            future_distance = abs(LABEL_SCORE.get(future.get("label", "資料不足"), 0) - 2)
            buckets[label].append(((future_close / close) - 1, future_distance < start_distance))

    rows = []
    for label in LABELS:
        values = buckets.get(label, [])
        returns = [item[0] for item in values]
        convergence = [item[1] for item in values]
        rows.append(
            {
                "region": region,
                "section": "label_calibration",
                "scenario": "six_month_mean_reversion",
                "label": label,
                "signal_count": len(values),
                "six_month_horizon_days": 126,
                "six_month_return": fmt_float(sum(returns) / len(returns) if returns else None),
                "benchmark_return": "",
                "excess_return": "",
                "convergence_rate": fmt_float(sum(1 for flag in convergence if flag) / len(convergence) if convergence else None),
                "hit_rate": fmt_float(sum(1 for value in returns if value > 0) / len(returns) if returns else None),
                "max_drawdown": "",
                "turnover": "",
                "transaction_cost_case": "",
                "passed": "",
                "note": "以既有月度 signal 近似半年後標籤是否往合理區間收斂。",
            }
        )
    return rows


def build_us_validation() -> list[dict[str, object]]:
    return [
        {
            "region": "US",
            "section": "method_status",
            "scenario": "historical_validation_pending",
            "label": "",
            "signal_count": "",
            "six_month_horizon_days": 126,
            "six_month_return": "",
            "benchmark_return": "",
            "excess_return": "",
            "convergence_rate": "",
            "hit_rate": "",
            "max_drawdown": "",
            "turnover": "",
            "transaction_cost_case": "",
            "passed": "",
            "note": "美股目前保留 current valuation screen；待累積 point-in-time 月度估值快照後，使用與臺股相同的半年收斂與 sealed-test 流程。",
        }
    ]


def build_us_historical_snapshots(us_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in us_rows:
        rows.append(
            {
                "region": "US",
                "signal_date": datetime.now().strftime("%Y-%m-%d"),
                "future_date": "",
                "ticker": row.get("ticker", ""),
                "display_ticker": row.get("display_ticker", row.get("ticker", "")),
                "company": row.get("company", ""),
                "industry_model_class": row.get("industry_model_class", ""),
                "lifecycle_stage": row.get("lifecycle_stage", ""),
                "label": row.get("valuation_label", ""),
                "close": row.get("price", ""),
                "future_close": "",
                "future_return": "",
                "peer_return": "",
                "benchmark_return": "",
                "ttm_pe": row.get("trailingPE", ""),
                "forward_pe": row.get("forwardPE", ""),
                "ev_to_ebitda": row.get("evToEbitda", ""),
                "ps": row.get("ps", ""),
                "pb": row.get("pb", ""),
                "implied_cagr": "",
                "current_cagr": "",
                "revenue_growth": row.get("revenueGrowth", ""),
                "data_status": "coverage_gap",
                "note": "美股目前只有 current screen；尚未建立 point-in-time 月度 fundamental snapshots。",
            }
        )
    return rows


def build_tw_historical_snapshots(signals: list[dict[str, str]], universe: dict[str, dict[str, str]], exchanges: dict[str, str]) -> list[dict[str, object]]:
    by_ticker = defaultdict(list)
    for row in signals:
        by_ticker[row["ticker"]].append(row)
    for rows in by_ticker.values():
        rows.sort(key=lambda item: item["signal_date"])

    snapshots = []
    for ticker, rows in by_ticker.items():
        for row in rows:
            signal_date = datetime.fromisoformat(row["signal_date"])
            target = signal_date + timedelta(days=182)
            future = next((item for item in rows if datetime.fromisoformat(item["signal_date"]) >= target), None)
            close = safe_float(row.get("close"))
            future_close = safe_float(future.get("close")) if future else None
            future_return = (future_close / close - 1) if close and future_close else None
            suffix = exchanges.get(ticker, "TW")
            snapshots.append(
                {
                    "region": "TW",
                    "signal_date": row.get("signal_date", ""),
                    "future_date": future.get("signal_date", "") if future else "",
                    "ticker": ticker,
                    "display_ticker": f"{ticker}.{suffix}",
                    "company": row.get("company", ""),
                    "industry_model_class": row.get("model_class", ""),
                    "lifecycle_stage": universe.get(ticker, {}).get("stage", ""),
                    "label": row.get("label", ""),
                    "close": row.get("close", ""),
                    "future_close": fmt_float(future_close),
                    "future_return": fmt_float(future_return),
                    "peer_return": "",
                    "benchmark_return": "",
                    "ttm_pe": row.get("ttm_pe", ""),
                    "forward_pe": "",
                    "ev_to_ebitda": "",
                    "ps": "",
                    "pb": row.get("pb", ""),
                    "implied_cagr": row.get("implied_cagr", ""),
                    "current_cagr": row.get("current_cagr", ""),
                    "revenue_growth": fmt_float((safe_float(row.get("revenue_3m_yoy_avg")) or 0) / 100) if row.get("revenue_3m_yoy_avg") else "",
                    "data_status": "complete" if future else "future_window_pending",
                    "note": "point-in-time signal；future fields only used as validation outcome。",
                }
            )

    peer_returns = defaultdict(list)
    for row in snapshots:
        future_return = safe_float(row.get("future_return"))
        if future_return is not None:
            peer_returns[(row["signal_date"], row["industry_model_class"])].append(future_return)
    for row in snapshots:
        row["peer_return"] = fmt_float(median(peer_returns.get((row["signal_date"], row["industry_model_class"]), [])))
        future_return = safe_float(row.get("future_return"))
        peer_return = safe_float(row.get("peer_return"))
        row["benchmark_return"] = fmt_float((future_return - peer_return) if future_return is not None and peer_return is not None else None)
    return snapshots


def build_us_model_validation(us_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    combos = sorted({(str(row.get("industry_model_class", "")), str(row.get("lifecycle_stage", ""))) for row in us_rows})
    for industry, stage in combos:
        entry = registry_entry_for(industry)
        candidates = list(entry["candidates"])
        for idx, model in enumerate(candidates, 1):
            rows.append(
                {
                    "region": "US",
                    "industry_model_class": industry,
                    "lifecycle_stage": stage,
                    "candidate_model": model,
                    "candidate_rank": idx,
                    "is_selected": "true" if idx == 1 else "false",
                    "fallback_model": entry["fallback"],
                    "signal_count": 0,
                    "coverage_ratio": "",
                    "convergence_rate": "",
                    "hit_rate": "",
                    "median_excess_return": "",
                    "label_calibration_score": "",
                    "model_score": "",
                    "model_confidence": "none",
                    "coverage_status": "coverage_gap",
                    "method_status": "pending_history",
                    "reason": "美股尚未建立 point-in-time 月度 fundamental snapshots；先使用 registry fallback，不宣稱已驗證。",
                }
            )
    return rows


def build_tw_model_validation(snapshots: list[dict[str, object]]) -> list[dict[str, object]]:
    by_ticker = defaultdict(list)
    by_combo = defaultdict(list)
    by_combo_date = defaultdict(list)
    for row in snapshots:
        by_ticker[row["ticker"]].append(row)
        combo = (row["industry_model_class"], row["lifecycle_stage"])
        by_combo[combo].append(row)
        by_combo_date[(combo, row["signal_date"])].append(row)
    for rows in by_ticker.values():
        rows.sort(key=lambda item: item["signal_date"])

    validation_rows = []
    for combo, combo_rows in sorted(by_combo.items()):
        industry, stage = combo
        entry = registry_entry_for(industry)
        candidates = list(entry["candidates"])
        total_with_future = sum(1 for row in combo_rows if safe_float(row.get("future_return")) is not None)
        scored = []
        for model in candidates:
            observations = []
            for row in combo_rows:
                current_value = candidate_value(row, model)
                future_return = safe_float(row.get("future_return"))
                if current_value is None or future_return is None:
                    continue

                own_prior = [
                    candidate_value(item, model)
                    for item in by_ticker[row["ticker"]]
                    if item["signal_date"] <= row["signal_date"] and candidate_value(item, model) is not None
                ]
                peer_now = [
                    candidate_value(item, model)
                    for item in by_combo_date[(combo, row["signal_date"])]
                    if candidate_value(item, model) is not None
                ]
                current_gap = metric_gap(current_value, median(own_prior), median(peer_now))
                future_row = next(
                    (item for item in by_ticker[row["ticker"]] if item["signal_date"] == row.get("future_date")),
                    None,
                )
                future_gap = None
                if future_row:
                    future_value = candidate_value(future_row, model)
                    future_own = [
                        candidate_value(item, model)
                        for item in by_ticker[row["ticker"]]
                        if item["signal_date"] <= future_row["signal_date"] and candidate_value(item, model) is not None
                    ]
                    future_peer = [
                        candidate_value(item, model)
                        for item in by_combo_date[(combo, future_row["signal_date"])]
                        if candidate_value(item, model) is not None
                    ]
                    future_gap = metric_gap(future_value, median(future_own), median(future_peer))
                peer_return = safe_float(row.get("peer_return"))
                excess = future_return - peer_return if peer_return is not None else None
                hit = None
                if current_gap is not None and peer_return is not None:
                    hit = future_return >= peer_return if current_gap < 0 else future_return <= peer_return
                convergence = None
                if current_gap is not None and future_gap is not None:
                    convergence = abs(future_gap) < abs(current_gap)
                observations.append(
                    {
                        "gap": current_gap,
                        "future_return": future_return,
                        "excess": excess,
                        "hit": hit,
                        "convergence": convergence,
                    }
                )

            signal_count = len(observations)
            coverage = signal_count / total_with_future if total_with_future else 0
            convergence_values = [item["convergence"] for item in observations if item["convergence"] is not None]
            hit_values = [item["hit"] for item in observations if item["hit"] is not None]
            excess_values = [item["excess"] for item in observations if item["excess"] is not None]
            convergence_rate = sum(1 for item in convergence_values if item) / len(convergence_values) if convergence_values else None
            hit_rate = sum(1 for item in hit_values if item) / len(hit_values) if hit_values else None
            calibration = label_calibration_score(observations)
            confidence, coverage_status = confidence_from_metrics(signal_count, coverage, convergence_rate, hit_rate)
            score = (
                (convergence_rate or 0.0) * 0.45
                + (hit_rate or 0.0) * 0.25
                + coverage * 0.20
                + (calibration if calibration is not None else 0.5) * 0.10
            )
            scored.append(
                {
                    "model": model,
                    "signal_count": signal_count,
                    "coverage": coverage,
                    "convergence_rate": convergence_rate,
                    "hit_rate": hit_rate,
                    "median_excess_return": median(excess_values),
                    "label_calibration_score": calibration,
                    "model_score": score,
                    "model_confidence": confidence,
                    "coverage_status": coverage_status,
                }
            )
        scored.sort(key=lambda item: (item["model_score"], item["signal_count"]), reverse=True)
        fallback = scored[1]["model"] if len(scored) > 1 else entry["fallback"]
        for idx, item in enumerate(scored, 1):
            method_status = "research-only" if item["model_confidence"] in {"low", "none"} else "validated"
            validation_rows.append(
                {
                    "region": "TW",
                    "industry_model_class": industry,
                    "lifecycle_stage": stage,
                    "candidate_model": item["model"],
                    "candidate_rank": idx,
                    "is_selected": "true" if idx == 1 else "false",
                    "fallback_model": fallback,
                    "signal_count": item["signal_count"],
                    "coverage_ratio": fmt_float(item["coverage"]),
                    "convergence_rate": fmt_float(item["convergence_rate"]),
                    "hit_rate": fmt_float(item["hit_rate"]),
                    "median_excess_return": fmt_float(item["median_excess_return"]),
                    "label_calibration_score": fmt_float(item["label_calibration_score"]),
                    "model_score": fmt_float(item["model_score"]),
                    "model_confidence": item["model_confidence"],
                    "coverage_status": item["coverage_status"],
                    "method_status": method_status,
                    "reason": "以臺股月度 point-in-time signal 測試 126 trading day 估值 gap 收斂與 peer-relative hit rate。",
                }
            )
    return validation_rows


def enrich_rows_with_model_selection(rows: list[dict[str, object]], validation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = {
        (row["industry_model_class"], row["lifecycle_stage"]): row
        for row in validation_rows
        if str(row.get("is_selected")).lower() == "true"
    }
    fallback_by_industry = {}
    for row in validation_rows:
        if str(row.get("is_selected")).lower() == "true":
            fallback_by_industry[row["industry_model_class"]] = row
    for row in rows:
        match = selected.get((row.get("industry_model_class", ""), row.get("lifecycle_stage", ""))) or fallback_by_industry.get(
            row.get("industry_model_class", "")
        )
        if not match:
            continue
        row["selected_model"] = match.get("candidate_model", "")
        row["fallback_model"] = match.get("fallback_model", "")
        row["model_confidence"] = match.get("model_confidence", "")
        row["coverage_status"] = match.get("coverage_status", "")
        row["model_validation_signal_count"] = match.get("signal_count", "")
        row["model_validation_convergence_rate"] = match.get("convergence_rate", "")
        row["model_validation_hit_rate"] = match.get("hit_rate", "")
        row["model_validation_note"] = match.get("reason", "")
    return rows


def model_matrix(validation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "region": row["region"],
            "industry_model_class": row["industry_model_class"],
            "lifecycle_stage": row["lifecycle_stage"],
            "primary_model": row["candidate_model"],
            "fallback_model": row["fallback_model"],
            "model_confidence": row["model_confidence"],
            "coverage_status": row["coverage_status"],
            "signal_count": row["signal_count"],
            "convergence_rate": row["convergence_rate"],
            "hit_rate": row["hit_rate"],
            "method_status": row["method_status"],
        }
        for row in validation_rows
        if str(row.get("is_selected")).lower() == "true"
    ]


def build_registry_payload() -> dict[str, object]:
    return {
        key: {
            "patterns": value["patterns"],
            "candidates": value["candidates"],
            "fallback": value["fallback"],
            "why": value["why"],
            "gaps": value["gaps"],
        }
        for key, value in MODEL_REGISTRY.items()
    }


def build_method_audit(
    us_rows: list[dict[str, object]],
    tw_rows: list[dict[str, object]],
    us_model_validation: list[dict[str, object]],
    tw_model_validation: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shared_labels": LABELS,
        "horizon_trading_days": 126,
        "model_registry": build_registry_payload(),
        "model_matrix": model_matrix(us_model_validation + tw_model_validation),
        "benchmarks": {
            "US": {"primary": "SOXX", "secondary": "QQQ"},
            "TW": {"primary": "0050", "secondary": "TAIEX", "note": "0050 split adjustment retained in existing Taiwan backtest outputs."},
        },
        "method": [
            "以 industry_model_class × lifecycle_stage 建立候選估值模型 registry。",
            "每個候選模型用半年 valuation gap 收斂率、peer-relative hit rate、coverage ratio 與 label calibration 評分。",
            "同一 industry_model_class 對應同一 valuation_basis，但 primary model 由歷史驗證結果選出。",
            "合理估值區間採自身歷史與同業分布 50/50；歷史不足時標示 fallback。",
            "歷史驗證使用月度 signal date 與約 126 交易日半年觀察期。",
            "sealed test 不可用於反向調參，失敗結果必須顯示。",
        ],
        "data_status": {
            "US": {
                "screen_rows": len(us_rows),
                "historical_validation": "pending_point_in_time_snapshots",
                "warning": "美股 current screen 已完整保留；歷史驗證需後續產生月度估值快照。",
            },
            "TW": {
                "screen_rows": len(tw_rows),
                "historical_validation": "available_from_existing_outputs",
                "warning": "validation robust gate 通過，但 sealed company/deployment test 失敗，判定有 overfit 風險。",
            },
        },
    }


def main() -> None:
    args = parse_args()
    workspace = args.workspace.resolve()
    out = args.out.resolve()
    us_rows = normalize_us_rows(workspace)
    tw_rows = normalize_tw_rows(workspace)
    _latest, tw_signals, tw_universe = latest_tw_rows(workspace)
    exchanges = detect_exchange_map(workspace / "research/taiwan-ai-supply-chain-map.md")
    us_snapshots = build_us_historical_snapshots(us_rows)
    tw_snapshots = build_tw_historical_snapshots(tw_signals, tw_universe, exchanges)
    us_model_validation = build_us_model_validation(us_rows)
    tw_model_validation = build_tw_model_validation(tw_snapshots)
    us_rows = enrich_rows_with_model_selection(us_rows, us_model_validation)
    tw_rows = enrich_rows_with_model_selection(tw_rows, tw_model_validation)

    write_csv(out / "us_valuation_screen.csv", us_rows, SCREEN_FIELDS)
    write_csv(out / "tw_valuation_screen.csv", tw_rows, SCREEN_FIELDS)
    write_csv(out / "us_stock_pool.csv", us_rows, STOCK_POOL_FIELDS)
    write_csv(out / "tw_stock_pool.csv", tw_rows, STOCK_POOL_FIELDS)
    write_stock_pool_md(out / "us_stock_pool.md", "美國 AI 供應鏈股票池", us_rows)
    write_stock_pool_md(out / "tw_stock_pool.md", "臺灣 AI 供應鏈股票池", tw_rows)
    write_csv(out / "us_historical_validation.csv", build_us_validation(), VALIDATION_FIELDS)
    write_csv(out / "tw_historical_validation.csv", build_tw_validation(workspace), VALIDATION_FIELDS)
    write_csv(out / "us_historical_snapshots.csv", us_snapshots, SNAPSHOT_FIELDS)
    write_csv(out / "tw_historical_snapshots.csv", tw_snapshots, SNAPSHOT_FIELDS)
    write_csv(out / "us_model_validation.csv", us_model_validation, MODEL_VALIDATION_FIELDS)
    write_csv(out / "tw_model_validation.csv", tw_model_validation, MODEL_VALIDATION_FIELDS)
    write_csv(out / "us_mean_reversion_results.csv", build_mean_reversion("US", us_rows), MEAN_REVERSION_FIELDS)
    write_csv(out / "tw_mean_reversion_results.csv", build_mean_reversion("TW", tw_rows, tw_signals), MEAN_REVERSION_FIELDS)
    (out / "valuation_model_registry.json").write_text(
        json.dumps(build_registry_payload(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "method_audit.json").write_text(
        json.dumps(build_method_audit(us_rows, tw_rows, us_model_validation, tw_model_validation), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
