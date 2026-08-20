#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §3.1.9
# [MODULE] scripts.ml.run_sft_train
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.implementations.sentiment_sft_trainer; datasets; torch
# [CONSUMERS] (CLI 训练脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 加载 data/sft/{train,eval}.jsonl → build_sft_dataset 转 messages → SentimentSFTTrainer 训练 → validate 算 F1；支持 --smoke 快速验证管道
# [MODIFY-GUARD] 13_regime_phase3_engineering_plan.md §3.1.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 训练失败 exit 1；评估失败记录但不阻断（已训练 adapter 保留）
# [TESTS] (CLI 训练脚本，无单元测试)
# [TTL] permanent
"""run_sft_train.py — P1-E3 Phase 4: 执行 LoRA SFT 训练 + F1 评估。

流程:
  1. 加载 ``data/sft/{train,eval}.jsonl``（build_sft_dataset.py 产物）
  2. 经 ``build_sft_dataset()`` 转 messages 格式 datasets.Dataset
  3. ``SentimentSFTTrainer.train()`` QLoRA 4bit 训练
  4. ``SentimentSFTTrainer.validate()`` 在 ``data/eval/news_sentiment_200.jsonl`` 算 Macro-F1
  5. LoRA adapter 持久化 ``models/qwen25-7b-sft-v1/``

用法:
    # smoke test（50 条快速验证管道）
    python scripts/ml/run_sft_train.py --smoke
    # 全量训练
    python scripts/ml/run_sft_train.py --epochs 3 --batch-size 4

依据: 13_regime_phase3_engineering_plan.md §3.1.9
SSoT: #ARCH-NLP-PIPELINE-001
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SFT_TRAIN_PATH = ROOT / "data" / "sft" / "train.jsonl"
SFT_EVAL_PATH = ROOT / "data" / "sft" / "eval.jsonl"
EVAL_200_PATH = ROOT / "data" / "eval" / "news_sentiment_200.jsonl"
OUTPUT_DIR = ROOT / "models" / "qwen25-7b-sft-v1"


def load_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    if not path.exists():
        return items
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA SFT 训练 + F1 评估")
    parser.add_argument("--smoke", action="store_true", help="快速验证管道（50 条）")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--no-validate", action="store_true", help="跳过最终 F1 评估")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    t0 = time.time()

    # 1. 加载数据
    from zephyr.ml_train.implementations.sentiment_sft_trainer import (
        SentimentSFTTrainer,
        SFTTrainConfig,
        build_sft_dataset,
    )

    train_items = load_jsonl(SFT_TRAIN_PATH)
    eval_items = load_jsonl(SFT_EVAL_PATH)
    log.info("加载训练数据: train=%d eval=%d", len(train_items), len(eval_items))
    if not train_items:
        log.error("无训练数据（先运行 build_sft_dataset.py）")
        sys.exit(1)

    if args.smoke:
        train_items = train_items[:50]
        eval_items = eval_items[:10]
        log.info("SMOKE 模式: 截断到 train=%d eval=%d", len(train_items), len(eval_items))

    train_ds = build_sft_dataset(train_items)
    eval_ds = build_sft_dataset(eval_items) if eval_items else None
    log.info("messages Dataset: train=%d eval=%s", len(train_ds), len(eval_ds) if eval_ds else "None")

    # 2. 配置 + 训练器
    epochs = 1.0 if args.smoke else args.epochs
    cfg = SFTTrainConfig(
        epochs=epochs,
        batch_size=2 if args.smoke else args.batch_size,
        grad_accum=2 if args.smoke else args.grad_accum,
        lr=args.lr,
        max_seq_length=args.max_seq_length,
        output_dir=str(OUTPUT_DIR),
        logging_steps=5 if args.smoke else 10,
        eval_steps=10 if args.smoke else 50,
        save_steps=50 if args.smoke else 100,
    )
    trainer = SentimentSFTTrainer(cfg)
    log.info("训练器: model_id=%s epochs=%s batch=%s", trainer.__model_id__, cfg.epochs, cfg.batch_size)

    # 3. 训练
    log.info("=== SFT 训练开始 ===")
    metrics = trainer.train(
        features={"train_dataset": train_ds, "eval_dataset": eval_ds},
        target=None,
        idempotency_key="sft-v1-" + time.strftime("%Y%m%d%H%M"),
    )
    log.info("训练指标: %s", metrics)

    # 4. 评估 F1（独立评估集 200 条）
    if args.no_validate:
        log.info("跳过最终 F1 评估（--no-validate）")
        return

    eval_200 = load_jsonl(EVAL_200_PATH)
    if not eval_200:
        log.warning("评估集 %s 不存在，跳过 F1 评估", EVAL_200_PATH)
        return

    log.info("=== F1 评估（%d 条独立评估集）===", len(eval_200))
    try:
        val_metrics = trainer.validate(features={"eval_items": eval_200}, target=None)
    except Exception as exc:  # noqa: BLE001 — 评估失败不丢已训练 adapter
        log.error("F1 评估失败（adapter 已保存）: %s", exc, exc_info=True)
        return

    f1 = val_metrics.get("macro_f1", 0.0)
    acc = val_metrics.get("accuracy", 0.0)
    n = int(val_metrics.get("n", 0))
    verdict = "✅ 达标 ≥75%" if f1 >= 0.75 else "❌ 未达 75%"
    print("\n" + "=" * 60)
    print(f"SFT 训练完成（{time.time() - t0:.0f}s）")
    print(f"训练 loss: {metrics.get('train_loss', 0):.4f}")
    print(f"Macro-F1: {f1:.4f}  {verdict}")
    print(f"Accuracy: {acc:.4f}  (n={n})")
    print(f"LoRA adapter: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
