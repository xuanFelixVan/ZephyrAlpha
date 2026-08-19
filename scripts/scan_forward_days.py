#!/usr/bin/env python
# [BLUEPRINT] MOD-REGIME-P2-E8 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §4.2
# [MODULE] scripts.scan_forward_days
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.validation.phase2.b1_probability_calibration; pandas
# [CONSUMERS] (CLI 扫描脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 扫描 B1 验证器 forward_days∈{5,10,20,40,60,120} 找 ECE 最小预测周期；单候选失败不阻断整体（记 degraded 行续扫）；全候选 degraded → best=None；输入文件缺失 exit 1
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md §4.2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入缺失/格式非法→exit 1；单候选 B1ValidationError→degraded 行不阻断
# [TESTS] tests/scripts/test_scan_forward_days.py
# [TTL] permanent
"""scan_forward_days.py — P2-E8: forward_days 参数扫描（13 号 §4.2）。

扫描 B1 验证器的 ``forward_days`` 参数，找校准误差（ECE）最小的预测周期::

    for forward_days in [5, 10, 20, 40, 60, 120]:
        b1_report = b1_validator.validate(detect_records, close, forward_days)
        # 记录校准误差，选最优

学术参考（13 号 §4.2.3）：QLoRA Benchmark（arXiv:2608.04200）显示短期收益
预测力本身就弱——若扫描后所有周期误差都高，可能不是 forward_days 的问题，
而是 regime 状态和收益的因果关系本身就弱（报告 degraded/全 FAIL 时应如此解读）。

用法:
    python scripts/scan_forward_days.py \
        --detect-records data/regime/detect_records.jsonl \
        --close-csv data/regime/close.csv \
        [--out data/regime/forward_days_scan.json]

输入格式:
  - detect-records JSONL：{"timestamp": "YYYY-MM-DD", "confidence": 0.8, "dominant_regime": "r3"}
  - close CSV：含 date,close 两列（header 行）

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md §4.2
SSoT: 13_regime_phase3_engineering_plan P2-E8（依赖 P0-E2 校准器 B1ProbabilityCalibration）
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.regime.validation.phase2.b1_probability_calibration import (  # noqa: E402
    B1ProbabilityCalibration,
    B1ValidationError,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# P2-E8 扫描候选（13 号 §4.2.2 裁定值）
FORWARD_DAYS_CANDIDATES: Final[list[int]] = [5, 10, 20, 40, 60, 120]
CURRENT_DEFAULT_FORWARD_DAYS: Final[int] = 20  # B1 DEFAULT_FORWARD_DAYS（P0-E2 落地值）


@dataclass(frozen=True, slots=True)
class ForwardDaysScanRow:
    """单候选扫描结果。"""

    forward_days: int
    ece: float           # 样本加权校准误差（B1 weighted_calibration_error）
    verdict: str
    total_samples: int
    degraded: bool
    note: str = ""


@dataclass(frozen=True, slots=True)
class ForwardDaysScanReport:
    """扫描报告。best=None 表示全部候选 degraded（无法选优，§4.2.3 解读）。"""

    rows: list[ForwardDaysScanRow]
    best_forward_days: int | None
    best_ece: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": [asdict(r) for r in self.rows],
            "best_forward_days": self.best_forward_days,
            "best_ece": self.best_ece,
        }


def scan_forward_days(
    detect_records: list[dict[str, Any]],
    close: pd.Series,
    candidates: Sequence[int] | None = None,
) -> ForwardDaysScanReport:
    """扫描 forward_days 候选，按 ECE 选最优（13 号 §4.2.2 施工化）。

    单候选 B1 失败（数据不足/参数非法）记 degraded 行续扫，不阻断整体。
    最优选择：非 degraded 候选中 ECE 最小者；并列取候选序列先者（稳定序）。
    """
    validator = B1ProbabilityCalibration()
    rows: list[ForwardDaysScanRow] = []
    for fd in candidates or FORWARD_DAYS_CANDIDATES:
        try:
            report = validator.validate(detect_records, close, forward_days=fd)
            rows.append(
                ForwardDaysScanRow(
                    forward_days=fd,
                    ece=report.weighted_calibration_error,
                    verdict=report.verdict.value,
                    total_samples=report.total_samples,
                    degraded=report.degraded,
                    note=report.summary,
                )
            )
        except B1ValidationError as exc:
            log.warning("forward_days=%d 验证失败（degraded 续扫）: %s", fd, exc)
            rows.append(
                ForwardDaysScanRow(fd, 1.0, "FAIL", 0, True, note=f"B1ValidationError: {exc}"),
            )

    valid = [r for r in rows if not r.degraded]
    best = min(valid, key=lambda r: r.ece) if valid else None
    return ForwardDaysScanReport(
        rows=rows,
        best_forward_days=best.forward_days if best else None,
        best_ece=round(best.ece, 4) if best else None,
    )


def load_detect_records(path: Path) -> list[dict[str, Any]]:
    """加载 detect_records JSONL（timestamp 解析为 pd.Timestamp）。"""
    records: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(
                {
                    "timestamp": pd.Timestamp(obj["timestamp"]),
                    "confidence": float(obj["confidence"]),
                    "dominant_regime": str(obj["dominant_regime"]),
                }
            )
    return records


def load_close(path: Path) -> pd.Series:
    """加载 close CSV（date,close 两列，DatetimeIndex 升序）。"""
    df = pd.read_csv(path)
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError(f"close CSV 须含 date,close 两列: {path}")
    s = pd.Series(df["close"].astype(float).to_numpy(), index=pd.to_datetime(df["date"]))
    return s.sort_index()


def print_report(report: ForwardDaysScanReport) -> None:
    print("=" * 72)
    print("P2-E8 forward_days 参数扫描（B1 ECE 最小化）")
    print("=" * 72)
    print(f"  {'forward_days':>12}  {'ECE':>8}  {'verdict':>7}  {'samples':>7}  degraded")
    for r in report.rows:
        marker = " ← 当前默认" if r.forward_days == CURRENT_DEFAULT_FORWARD_DAYS else ""
        print(f"  {r.forward_days:>12}  {r.ece:>8.4f}  {r.verdict:>7}  {r.total_samples:>7}  {r.degraded}{marker}")
    print("-" * 72)
    if report.best_forward_days is None:
        print("最优: 无（全部候选 degraded——按 §4.2.3 解读：可能 regime-收益因果本身弱）")
    else:
        print(f"最优: forward_days={report.best_forward_days}（ECE={report.best_ece:.4f}）")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P2-E8 forward_days 参数扫描")
    parser.add_argument("--detect-records", type=Path, required=True, help="detect_records JSONL")
    parser.add_argument("--close-csv", type=Path, required=True, help="close CSV（date,close）")
    parser.add_argument("--out", type=Path, default=None, help="扫描报告 JSON 输出路径（可选）")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.detect_records.exists():
        log.error("detect_records 文件不存在: %s", args.detect_records)
        sys.exit(1)
    if not args.close_csv.exists():
        log.error("close CSV 文件不存在: %s", args.close_csv)
        sys.exit(1)

    detect_records = load_detect_records(args.detect_records)
    close = load_close(args.close_csv)
    log.info("输入：detect_records %d 条，close %d 点", len(detect_records), len(close))

    report = scan_forward_days(detect_records, close)
    print_report(report)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("报告已写入 %s", args.out)


if __name__ == "__main__":
    main()
