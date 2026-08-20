#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 2
# [MODULE] scripts.ml.eval_sentiment
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.nlp.nlp_inference; zephyr.integration.local_model.ollama_chat; zephyr.integration.local_model.cache_layer; sklearn.metrics
# [CONSUMERS] (CLI 评估脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 零样本情感分类 F1 评估；断点续作追加写入；Ollama 不可达 exit 1；评估集不存在 exit 1
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Ollama 不可达 exit 1；评估集不存在 exit 1；逐条推理异常降级 neutral 不阻断
# [TESTS] (CLI 评估脚本，无单元测试)
# [TTL] permanent
"""eval_sentiment.py — P1-E3 Phase 2: 零样本情感分类 F1 评估。

对 ``data/eval/news_sentiment_200.jsonl`` 评估集跑零样本推理（Ollama qwen3:8b），
计算 Macro-F1 / Accuracy / per-class metrics，目标 F1 ≥ 65%。

用法:
    python scripts/ml/eval_sentiment.py [--model qwen3:8b] [--limit N] [--resume]

输出:
    - data/eval/zero_shot_predictions.jsonl  （逐条预测，断点续作用）
    - stdout: Macro-F1 / Accuracy / classification_report

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 2
SSoT: #ARCH-NLP-PIPELINE-001
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# ── 项目路径 ──
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    classification_report,
    f1_score,
)

from zephyr.integration.local_model.cache_layer import CacheLayer  # noqa: E402
from zephyr.integration.local_model.ollama_chat import OllamaChat  # noqa: E402
from zephyr.nlp.nlp_inference import InferConfig, infer_sentiment  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

EVAL_PATH = ROOT / "data" / "eval" / "news_sentiment_200.jsonl"
PRED_PATH = ROOT / "data" / "eval" / "zero_shot_predictions.jsonl"

LABELS = ["positive", "negative", "neutral"]


def load_eval_set(path: Path) -> list[dict]:
    """加载评估集（ground truth）。"""
    if not path.exists():
        log.error("评估集不存在: %s（先运行 build_eval_set.py）", path)
        sys.exit(1)
    items: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    log.info("加载评估集: %d 条", len(items))
    return items


def load_done(path: Path) -> set[str]:
    """断点续作：已预测的 news_id。"""
    if not path.exists():
        return set()
    done: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                done.add(json.loads(line)["news_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    log.info("断点续作: 已预测 %d 条", len(done))
    return done


def _parse_args() -> argparse.Namespace:
    """解析 CLI 参数。"""
    parser = argparse.ArgumentParser(description="零样本情感分类 F1 评估")
    parser.add_argument("--model", default="qwen3:8b", help="Ollama 模型名")
    parser.add_argument("--limit", type=int, default=0, help="限制评估数量（0=全部）")
    parser.add_argument("--resume", action="store_true", default=True, help="断点续作（默认开启）")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--timeout", type=float, default=120.0, help="Ollama 超时秒数")
    return parser.parse_args()


def _run_inference(
    todo: list[dict],
    chat: OllamaChat,
    cache: CacheLayer,
    model: str,
    resume: bool,
) -> None:
    """逐条推理，追加写入预测文件（支持断点续作）。"""
    mode = "a" if resume and PRED_PATH.exists() else "w"
    t0 = time.time()
    cfg = InferConfig(model_version=model)
    with open(PRED_PATH, mode, encoding="utf-8") as f:
        for i, news in enumerate(todo):
            r = infer_sentiment(
                title=news.get("title", ""),
                content=news.get("content", ""),
                chat=chat,
                news_id=news.get("news_id", ""),
                cache=cache,
                config=cfg,
            )
            f.write(
                json.dumps(
                    {
                        "news_id": news.get("news_id", ""),
                        "stratum": news.get("stratum", ""),
                        "y_true": news.get("sentiment", "neutral"),
                        "y_pred": r.sentiment,
                        "pred_score": r.score,
                        "polarity": r.polarity,
                        "cached": r.cached,
                        "error": r.error,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            f.flush()
            if (i + 1) % 10 == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                log.info(
                    "进度: %d/%d (%.0f%%) %.1f 条/秒",
                    i + 1,
                    len(todo),
                    100 * (i + 1) / max(len(todo), 1),
                    rate,
                )


def _collect_predictions(pred_path: Path) -> tuple[list[str], list[str]]:
    """从预测文件汇总 (y_true, y_pred)。"""
    y_true: list[str] = []
    y_pred: list[str] = []
    with open(pred_path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                y_true.append(obj["y_true"])
                y_pred.append(obj["y_pred"])
            except (json.JSONDecodeError, KeyError):
                continue
    return y_true, y_pred


def _print_metrics(y_true: list[str], y_pred: list[str], model: str) -> None:
    """打印 Macro-F1 / Accuracy / classification_report。"""
    macro_f1 = f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, labels=LABELS, zero_division=0)
    print("\n" + "=" * 60)
    print(f"模型: {model}")
    print(f"样本数: {len(y_true)}")
    print(f"Macro-F1: {macro_f1:.4f}  {'✅ ≥65%' if macro_f1 >= 0.65 else '❌ <65%'}")
    print(f"Accuracy: {acc:.4f}")
    print("-" * 60)
    print(report)
    print("=" * 60)


def _print_strata_f1(pred_path: Path) -> None:
    """按 stratum 分组打印分层 Macro-F1。"""
    strata: dict[str, list[tuple[str, str]]] = {}
    with open(pred_path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                s = obj.get("stratum", "?")
                strata.setdefault(s, []).append((obj["y_true"], obj["y_pred"]))
            except (json.JSONDecodeError, KeyError):
                continue
    print("\n分层 Macro-F1:")
    for s in sorted(strata):
        yt = [x[0] for x in strata[s]]
        yp = [x[1] for x in strata[s]]
        f1s = f1_score(yt, yp, labels=LABELS, average="macro", zero_division=0)
        print(f"  {s:20s} n={len(yt):3d}  F1={f1s:.4f}")


def main() -> None:
    args = _parse_args()

    # 1. 加载评估集 + 断点续作
    eval_items = load_eval_set(EVAL_PATH)
    if args.limit > 0:
        eval_items = eval_items[: args.limit]
    done_ids = load_done(PRED_PATH) if args.resume else set()
    todo = [n for n in eval_items if n.get("news_id") not in done_ids]
    log.info("待推理: %d 条（跳过已预测 %d 条）", len(todo), len(eval_items) - len(todo))

    # 2. 推理后端 + 缓存
    if not OllamaChat.quick_alive():
        log.error("Ollama 不可达（localhost:11434），请先启动 Ollama")
        sys.exit(1)
    chat = OllamaChat(model=args.model, timeout_s=args.timeout)
    cache = CacheLayer()

    # 3. 逐条推理
    _run_inference(todo, chat, cache, args.model, args.resume)

    # 4. 汇总 + 指标
    y_true, y_pred = _collect_predictions(PRED_PATH)
    _print_metrics(y_true, y_pred, args.model)

    # 5. 分层 F1
    _print_strata_f1(PRED_PATH)


if __name__ == "__main__":
    main()
