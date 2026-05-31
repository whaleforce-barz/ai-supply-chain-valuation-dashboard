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
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean_cell(row.get(field)) for field in fields})


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


def normalize_us_rows(workspace: Path) -> list[dict[str, object]]:
    rows = read_csv(workspace / "ai_supply_chain_valuation_screen.csv")
    normalized = []
    for row in rows:
        industry = row.get("industry_class", "")
        stage = row.get("stage", "")
        label = row.get("valuation_label") or "資料不足"
        data_status = "complete" if not row.get("fetch_error") else "資料不足"
        ticker = row.get("ticker", "")
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
                "valuation_label": label if label in LABEL_SCORE else "資料不足",
                "data_status": data_status,
                "six_month_return": "",
                "benchmark_return": "",
                "source_url": row.get("source_url") or f"https://finance.yahoo.com/quote/{ticker}",
            }
        )
    return normalized


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


def build_method_audit(us_rows: list[dict[str, object]], tw_rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shared_labels": LABELS,
        "horizon_trading_days": 126,
        "benchmarks": {
            "US": {"primary": "SOXX", "secondary": "QQQ"},
            "TW": {"primary": "0050", "secondary": "TAIEX", "note": "0050 split adjustment retained in existing Taiwan backtest outputs."},
        },
        "method": [
            "同一 industry_model_class 對應同一 valuation_basis。",
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
    _latest, tw_signals, _universe = latest_tw_rows(workspace)

    write_csv(out / "us_valuation_screen.csv", us_rows, SCREEN_FIELDS)
    write_csv(out / "tw_valuation_screen.csv", tw_rows, SCREEN_FIELDS)
    write_csv(out / "us_historical_validation.csv", build_us_validation(), VALIDATION_FIELDS)
    write_csv(out / "tw_historical_validation.csv", build_tw_validation(workspace), VALIDATION_FIELDS)
    write_csv(out / "us_mean_reversion_results.csv", build_mean_reversion("US", us_rows), MEAN_REVERSION_FIELDS)
    write_csv(out / "tw_mean_reversion_results.csv", build_mean_reversion("TW", tw_rows, tw_signals), MEAN_REVERSION_FIELDS)
    (out / "method_audit.json").write_text(
        json.dumps(build_method_audit(us_rows, tw_rows), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
