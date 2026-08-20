#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 8
# [MODULE] scripts.ml.accept_nlp_pipeline
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（纯产物文件检查）
# [CONSUMERS] (CLI 验收脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 产物驱动验收（不跑真实推理）；必需项全 PASS 才 exit 0，任一 FAIL→exit 1；WARN 不阻塞；检查项与 13 号 §3.1.12 验收清单一一对应
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 8
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 产物缺失/指标不达标→对应项 FAIL，汇总 exit 1
# [TESTS] tests/scripts/test_ml_accept_nlp_pipeline.py
# [TTL] permanent
"""accept_nlp_pipeline.py — P1-E3 Phase 8: NLP 管道验收检查清单自动化。

对应 13 号 §3.1.12 验收标准（产物驱动，不跑真实推理）:

  | # | 检查项 | 门槛 | 产物 |
  |---|--------|------|------|
  | 1 | SFT Macro-F1 | ≥ 0.75 | metrics JSON {"macro_f1": ...} |
  | 2 | 推理速度 | 1000 条 < 300 秒 | benchmark JSON {"items": N, "elapsed_s": X} |
  | 3 | 端到端管道 | daily 产物含 negative_count/vote_score | daily_sentiment.jsonl |
  | 4 | 离线批量覆盖 | 最早聚合日 ≤ --start-date | daily_sentiment.jsonl |
  | 5 | SFT 权重持久化 | adapter_model.safetensors 存在 | models/qwen25-7b-sft-v1/ |
  | 6 | RLSP 权重持久化 | （可选，缺失 WARN 不 FAIL） | models/qwen25-7b-rlsp-v1/ |

用法:
    python scripts/ml/accept_nlp_pipeline.py [--metrics data/eval/sft_metrics.json]
        [--benchmark data/sentiment_batch/benchmark.json]
        [--daily data/sentiment_batch/daily_sentiment.jsonl]
        [--adapter-dir models/qwen25-7b-sft-v1] [--rlsp-dir models/qwen25-7b-rlsp-v1]

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 8
SSoT: #ARCH-NLP-PIPELINE-001
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Final

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── 验收门槛（13 号 §3.1.12/§3.1.10）──
SFT_F1_THRESHOLD: Final[float] = 0.75  # SFT 后 Macro-F1 ≥ 75%
SPEED_MIN_ITEMS: Final[int] = 1000  # 推理速度样本量
SPEED_MAX_SECONDS: Final[float] = 300.0  # 1000 条 < 5 分钟（RTX 3090）
DEFAULT_START_DATE: Final[str] = "2010-01-01"  # 离线批量全历史起点

STATUS_PASS: Final[str] = "PASS"
STATUS_FAIL: Final[str] = "FAIL"
STATUS_WARN: Final[str] = "WARN"


@dataclass(frozen=True, slots=True)
class CheckItem:
    """单项验收结果。required=False 的项缺失降级 WARN 不阻塞总验收。"""

    name: str
    status: str
    detail: str
    required: bool = True


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def check_sft_f1(metrics_path: Path, threshold: float = SFT_F1_THRESHOLD) -> CheckItem:
    """检查项 1：SFT Macro-F1 ≥ 75%（13 号 §3.1.12）。"""
    obj = _read_json(metrics_path)
    if obj is None or "macro_f1" not in obj:
        return CheckItem("sft_f1", STATUS_FAIL, f"metrics 缺失或无 macro_f1 字段: {metrics_path}")
    f1 = float(obj["macro_f1"])
    ok = f1 >= threshold
    return CheckItem(
        "sft_f1",
        STATUS_PASS if ok else STATUS_FAIL,
        f"Macro-F1={f1:.4f}（门槛 {threshold:.2f}）",
    )


def check_inference_speed(
    benchmark_path: Path,
    min_items: int = SPEED_MIN_ITEMS,
    max_seconds: float = SPEED_MAX_SECONDS,
) -> CheckItem:
    """检查项 2：推理速度 1000 条 < 5 分钟（13 号 §3.1.10，Phase 6 GGUF 回灌后测）。"""
    obj = _read_json(benchmark_path)
    if obj is None or "items" not in obj or "elapsed_s" not in obj:
        return CheckItem("inference_speed", STATUS_FAIL, f"benchmark 缺失或字段不全: {benchmark_path}")
    items = int(obj["items"])
    elapsed = float(obj["elapsed_s"])
    if items < min_items:
        return CheckItem("inference_speed", STATUS_FAIL, f"样本量不足 {items} < {min_items}")
    ok = elapsed < max_seconds
    return CheckItem(
        "inference_speed",
        STATUS_PASS if ok else STATUS_FAIL,
        f"{items} 条耗时 {elapsed:.1f}s（门槛 <{max_seconds:.0f}s）",
    )


def check_e2e_pipeline(daily_path: Path) -> CheckItem:
    """检查项 3：端到端管道 news_data → 日级聚合（含 bad_news_flat 入参 negative_count）。"""
    rows = _read_jsonl(daily_path)
    if not rows:
        return CheckItem("e2e_pipeline", STATUS_FAIL, f"daily 产物缺失或为空: {daily_path}")
    required = {"negative_count", "vote_score", "vote_strength"}
    missing = required - set(rows[0])
    if missing:
        return CheckItem("e2e_pipeline", STATUS_FAIL, f"daily 产物缺字段 {sorted(missing)}")
    return CheckItem("e2e_pipeline", STATUS_PASS, f"日级聚合 {len(rows)} 天，字段齐备")


def check_batch_coverage(
    daily_path: Path,
    start_date: str = DEFAULT_START_DATE,
    tolerance_days: int = 10,
) -> CheckItem:
    """检查项 4：离线批量推理覆盖（最早聚合日 ≤ start_date + 容差，默认 2010-01-01 全历史）。

    容差理由：start_date 未必是交易日（2010 首个交易日为 01-04），
    要求最早聚合日严格 ≤ start_date 会误伤全历史完备的批次。
    """
    rows = _read_jsonl(daily_path)
    if not rows:
        return CheckItem("batch_coverage", STATUS_FAIL, f"daily 产物缺失或为空: {daily_path}")
    days = sorted(str(r.get("day", "")) for r in rows)
    min_day, max_day = days[0], days[-1]
    threshold = (date.fromisoformat(start_date) + timedelta(days=tolerance_days)).isoformat()
    ok = min_day <= threshold
    return CheckItem(
        "batch_coverage",
        STATUS_PASS if ok else STATUS_FAIL,
        f"覆盖 {min_day} ~ {max_day}（要求起点 ≤ {start_date}+{tolerance_days}d 容差）",
    )


def check_weights_persisted(adapter_dir: Path) -> CheckItem:
    """检查项 5：SFT 权重持久化（adapter_model.safetensors 存在）。"""
    target = adapter_dir / "adapter_model.safetensors"
    if target.exists():
        return CheckItem("sft_weights", STATUS_PASS, f"{target}")
    return CheckItem("sft_weights", STATUS_FAIL, f"adapter 权重缺失: {target}")


def check_rlsp_weights(rlsp_dir: Path) -> CheckItem:
    """检查项 6：RLSP 权重持久化（可选——Phase 5 未施工时 WARN 不阻塞）。"""
    target = rlsp_dir / "adapter_model.safetensors"
    if target.exists():
        return CheckItem("rlsp_weights", STATUS_PASS, f"{target}", required=False)
    return CheckItem("rlsp_weights", STATUS_WARN, f"RLSP adapter 未持久化（Phase 5 待施工）: {target}", required=False)


def run_acceptance(
    metrics_path: Path,
    benchmark_path: Path,
    daily_path: Path,
    adapter_dir: Path,
    rlsp_dir: Path,
    start_date: str = DEFAULT_START_DATE,
) -> list[CheckItem]:
    """执行全部检查项（纯函数，测试直调）。"""
    return [
        check_sft_f1(metrics_path),
        check_inference_speed(benchmark_path),
        check_e2e_pipeline(daily_path),
        check_batch_coverage(daily_path, start_date),
        check_weights_persisted(adapter_dir),
        check_rlsp_weights(rlsp_dir),
    ]


def summarize(items: list[CheckItem]) -> bool:
    """汇总：必需项全 PASS → True（WARN 不阻塞）。"""
    return all(it.status == STATUS_PASS for it in items if it.required)


def print_report(items: list[CheckItem]) -> None:
    print("=" * 60)
    print("NLP 管道验收清单（13 号 §3.1.12 / Phase 8）")
    print("=" * 60)
    for it in items:
        req = "" if it.required else "（可选）"
        print(f"  [{it.status:4s}] {it.name}{req}: {it.detail}")
    verdict = "通过" if summarize(items) else "未通过"
    print("-" * 60)
    print(f"总验收: {verdict}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NLP 管道验收检查清单（Phase 8）")
    parser.add_argument("--metrics", type=Path, default=ROOT / "data" / "eval" / "sft_metrics.json")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "data" / "sentiment_batch" / "benchmark.json")
    parser.add_argument("--daily", type=Path, default=ROOT / "data" / "sentiment_batch" / "daily_sentiment.jsonl")
    parser.add_argument("--adapter-dir", type=Path, default=ROOT / "models" / "qwen25-7b-sft-v1")
    parser.add_argument("--rlsp-dir", type=Path, default=ROOT / "models" / "qwen25-7b-rlsp-v1")
    parser.add_argument("--start-date", default=DEFAULT_START_DATE)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    items = run_acceptance(
        metrics_path=args.metrics,
        benchmark_path=args.benchmark,
        daily_path=args.daily,
        adapter_dir=args.adapter_dir,
        rlsp_dir=args.rlsp_dir,
        start_date=args.start_date,
    )
    print_report(items)
    sys.exit(0 if summarize(items) else 1)


if __name__ == "__main__":
    main()
