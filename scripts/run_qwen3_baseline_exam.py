# [BLUEPRINT] MOD-INF-060 | 待统筹登记（10号文 implementation_plans/10_llm_infrastructure.md §4 Phase 2.4 + aiarch 清单 3.4）| §3
# [MODULE] scripts.run_qwen3_baseline_exam
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.integration.local_model.ollama_chat(OllamaChat); zephyr.intelligence.model_profiling.exam_orchestrator(ExamOrchestrator.run_quick_exam); zephyr.intelligence.model_profiling.capability_passport(QuickProfile)
# [CONSUMERS] 人工/调度触发（基线考试跑批）; tests/model/test_qwen3_baseline_profile.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 产物格式与 results_writer._profile_to_dict 键集兼容（ModelRouter.load_benchmark_from_disk 直接可读）；原子写入（tmp+os.replace，同 results_writer 先例）；折算产物必须带 baseline_provenance 标注；只写 data/model_profiles/（目录契约仅允许 .jsonl）
# [MODIFY-GUARD] 产物键集变更须同步 results_writer 与 ModelRouter 消费口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=PASS, exit 1=FAIL（考试/转换失败）, exit 2=ERROR（参数/环境错误，如 Ollama 不可达）
# [TESTS] tests/model/test_qwen3_baseline_profile.py
# [A_module] module_id=MOD-INF-060 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""run_qwen3_baseline_exam.py — qwen3:8b 本地推理质量基线考试（10号文 §4 Phase 2.4）。

验收口径：基线成绩入库 data/model_profiles/（ModelRouter.load_benchmark_from_disk
默认消费目录）。两种模式：

1. 真实考试（默认）：
       python scripts/run_qwen3_baseline_exam.py
   经 OllamaChat(qwen3:8b) + ExamOrchestrator.run_quick_exam() 跑 39 次推断
   （~6-8 分钟），QuickProfile 存档 data/brain/quick_profiles/ 并折算为
   benchmark 记录落 data/model_profiles/。
2. 既有结果折算（--from-existing）：
       python scripts/run_qwen3_baseline_exam.py --from-existing data/brain/quick_profiles/qwen3_8b.json
   不触网不调模型，把既有 quick_profile 折算为基准记录。折算产物带
   baseline_provenance 标注「首版由既有 quick_profile 折算，待真实 exam 链路复跑校准」。

折算口径（quick_profile → results_writer._profile_to_dict 兼容记录）：
  - average_score  <- overall_score（综合分）
  - category_scores <- capability_scores（逐能力原始分）
  - total_tests     <- 能力数；passed_tests <- 评级 != "F" 的能力数
  - hallucination_rate <- 九维幻觉率均值（quick 模式无聚合 overall_rate，取均值代理）
  - refusal_rate    <- hallucination.refusal
  - latency/throughput <- 0.0（quick profile 不记速轴，待真实复跑回填）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

EXIT_PASS: Final = 0
EXIT_FAIL: Final = 1
EXIT_ERROR: Final = 2

DEFAULT_MODEL: Final[str] = "qwen3:8b"
DEFAULT_OUTPUT_DIR: Final[str] = "data/model_profiles"

_BASELINE_NOTE: Final[str] = "首版由既有 quick_profile 折算，待真实 exam 链路复跑校准"

_HALLU_DIMS: Final[tuple[str, ...]] = (
    "fabrication",
    "inconsistency",
    "refusal",
    "overclaim",
    "context_drift",
    "source_confusion",
    "instruction_drift",
    "format_hallucination",
    "quantity_hallucination",
)


def quick_profile_to_benchmark_record(
    qp: dict[str, Any],
    *,
    provenance: str,
) -> dict[str, Any]:
    """把 QuickProfile（dict 形态）折算为 results_writer._profile_to_dict 兼容记录。

    键集与 results_writer 落盘记录逐键对齐，保证 ModelRouter.load_benchmark_from_disk /
    load_benchmark_history / load_latest_benchmark_results 三消费口径直接可读。
    """
    model_id = str(qp.get("model_id", ""))
    if not model_id:
        raise ValueError("quick_profile 缺 model_id")
    scores = qp.get("capability_scores") or {}
    grades = qp.get("capability_grades") or {}
    hallu = qp.get("hallucination") or {}

    hallu_vals = [float(hallu.get(d, 0.0)) for d in _HALLU_DIMS]
    hallu_rate = round(sum(hallu_vals) / len(hallu_vals), 4) if hallu_vals else 0.0

    recommendations = qp.get("recommendations") or []
    top_job = ""
    if recommendations and isinstance(recommendations[0], dict):
        top_job = str(recommendations[0].get("job_title", ""))

    return {
        "model_name": model_id,
        "source": "ollama",
        "benchmark_date": str(qp.get("exam_timestamp", "")),
        "total_tests": len(scores),
        "passed_tests": sum(1 for g in grades.values() if g != "F"),
        "average_score": float(qp.get("overall_score", 0.0)),
        "latency_p50_ms": 0.0,
        "latency_p95_ms": 0.0,
        "latency_p99_ms": 0.0,
        "throughput_tokens_per_sec": 0.0,
        "total_tokens": 0,
        "total_time_ms": float(qp.get("exam_duration_seconds", 0.0)) * 1000.0,
        "category_scores": {str(k): float(v) for k, v in scores.items()},
        "hallucination_rate": hallu_rate,
        "refusal_rate": float(hallu.get("refusal", 0.0)),
        "json_validity_rate": 0.0,
        "code_validity_rate": 0.0,
        "recommendation": (f"overall_grade={qp.get('overall_grade', '?')} top_job={top_job}".strip()),
        "rank": 0,
        "available": True,
        "error": "",
        # 折算标注（非 results_writer 标准键，消费方按 model_name 取记录不受影响）
        "baseline_provenance": provenance,
        "exam_mode": str(qp.get("exam_mode", "quick")),
        "overall_grade": str(qp.get("overall_grade", "")),
    }


def write_baseline_jsonl(
    records: list[dict[str, Any]],
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    meta: dict[str, Any],
) -> Path:
    """原子写入 benchmark_<UTCts>.jsonl（首行 _meta 头注，消费方按 model_name 过滤自动跳过）。"""
    if not records:
        raise ValueError("records 为空，拒绝落盘（同 ARCH-BENCH-LEAK-001 口径）")
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filepath = base / f"benchmark_{ts}.jsonl"

    lines = [json.dumps({"_meta": meta}, ensure_ascii=False)]
    lines += [json.dumps(r, ensure_ascii=False) for r in records]
    payload = "\n".join(lines) + "\n"

    tmp_path = str(filepath) + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(filepath))
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
    return filepath


def _run_real_exam(model: str) -> dict[str, Any]:
    """真实考试链路：OllamaChat + ExamOrchestrator.run_quick_exam。"""
    from zephyr.integration.local_model.ollama_chat import OllamaChat
    from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator

    chat = OllamaChat(model=model)
    if hasattr(chat, "health_check") and not chat.health_check():
        raise RuntimeError(f"Ollama 不可达或模型未拉取: {model}")
    orch = ExamOrchestrator(chat, model_id=model)
    profile = orch.run_quick_exam()
    profile.save()  # QuickProfile.save() -> data/brain/quick_profiles/
    return asdict(profile)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="qwen3:8b 本地推理质量基线考试（10号文 Phase 2.4）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama 模型名（默认 qwen3:8b）")
    parser.add_argument(
        "--from-existing",
        default="",
        help="既有 quick_profile JSON 路径（折算模式，不调模型）",
    )
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    try:
        if args.from_existing:
            src = Path(args.from_existing)
            if not src.exists():
                print(f"[ERROR] quick_profile 不存在: {src}", file=sys.stderr)
                return EXIT_ERROR
            qp = json.loads(src.read_text(encoding="utf-8"))
            record = quick_profile_to_benchmark_record(qp, provenance=_BASELINE_NOTE)
            meta = {
                "note": _BASELINE_NOTE,
                "generated_by": "scripts/run_qwen3_baseline_exam.py --from-existing",
                "source_file": str(src),
                "generated_at_utc": datetime.now(UTC).isoformat(),
            }
        else:
            qp = _run_real_exam(args.model)
            record = quick_profile_to_benchmark_record(qp, provenance="真实 exam 链路（run_quick_exam）产出")
            meta = {
                "note": "真实 exam 链路产出",
                "generated_by": "scripts/run_qwen3_baseline_exam.py",
                "generated_at_utc": datetime.now(UTC).isoformat(),
            }

        out = write_baseline_jsonl([record], output_dir=args.output_dir, meta=meta)
    except (ValueError, RuntimeError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return EXIT_FAIL
    except Exception as exc:  # noqa: BLE001 — CLI 兜底，错误打印+退出码
        print(f"[ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    print(
        f"[PASS] baseline 落盘: {out} | model={record['model_name']} "
        f"score={record['average_score']} grade={record['overall_grade']}"
    )
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
