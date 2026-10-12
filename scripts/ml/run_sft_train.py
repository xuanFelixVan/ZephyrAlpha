#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/03_modules/_domain_machine_learning_train/blueprint.md | §3.1.9
# [MODULE] scripts.ml.run_sft_train
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.implementations.sentiment_sft_trainer; datasets; torch
# [CONSUMERS] (CLI 训练脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 默认加载 data/sft/{train,eval}.jsonl → build_sft_dataset 转 messages → SentimentSFTTrainer 训练 → validate 算 F1；支持 --smoke 快速验证管道；validate 成功后 metrics JSON 落盘（默认 data/eval/sft_metrics.json，Phase 8 验收检查项 1 生产者）；--gold-path 合并多本金标时按 news_id 去重且异标同 id 即 fail-loud，训练侧与评估侧 id 交集非空即 fail-loud（防泄漏＝禁边训边改卷的执行面）
# [MODIFY-GUARD] 13_regime_phase3_engineering_plan.md §3.1.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 训练失败 exit 1；金标/泄漏契约违反 exit 2（训练不启动）；评估失败记录但不阻断（已训练 adapter 保留）
# [TESTS] tests/meta/scripts/test_ml_run_sft_train.py
# [TTL] permanent
"""run_sft_train.py — P1-E3 Phase 4: 执行 LoRA SFT 训练 + F1 评估。

流程:
  1. 加载 ``data/sft/{train,eval}.jsonl``（build_sft_dataset.py 产物；--train-path/--eval-path 可换源）
  2. 经 ``build_sft_dataset()`` 转 messages 格式 datasets.Dataset
  3. ``SentimentSFTTrainer.train()`` QLoRA 4bit 训练
  4. ``SentimentSFTTrainer.validate()`` 在金标集算 Macro-F1（默认 ``data/eval/news_sentiment_200.jsonl``；
     ``--gold-path`` 可给多本金标，逐本合并）
  5. LoRA adapter 持久化 ``models/qwen25-7b-sft-v1/``

用法:
    # smoke test（50 条快速验证管道）
    python scripts/ml/run_sft_train.py --smoke
    # 全量训练
    python scripts/ml/run_sft_train.py --epochs 3 --batch-size 4
    # GPU-03B 蒸馏线：训练读蒸馏池，评分只认冻结金标 v1（200＋351），及格线 0.767
    python scripts/ml/run_sft_train.py \\
        --train-path data/sft_distill/train.jsonl --eval-path data/sft_distill/eval_split.jsonl \\
        --gold-path data/eval/news_sentiment_200.jsonl data/eval/gold_expansion_v1.jsonl \\
        --pass-line 0.767

依据: docs/03_modules/_domain_machine_learning_train/blueprint.md §3.1.9
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
GOLD_EXPANSION_V1_PATH = ROOT / "data" / "eval" / "gold_expansion_v1.jsonl"
OUTPUT_DIR = ROOT / "models" / "qwen25-7b-sft-v1"
DEFAULT_METRICS_PATH = ROOT / "data" / "eval" / "sft_metrics.json"
DEFAULT_PASS_LINE = 0.75


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


def _die_contract(msg: str) -> None:
    """数据面契约违反：fail-loud 且不启动训练（exit 2，与训练失败 exit 1 分档）。"""
    log.error("金标/泄漏契约违反: %s", msg)
    sys.exit(2)


def merge_gold_rows(paths: list[Path], *, labels: list[str] | None = None) -> tuple[list[dict], dict]:
    """把金标册合成一个评估面。

    金标扩充集用 ``human_label``（教师预标经裁定采信／Owner 改判），原 200 集用 ``sentiment``——
    两本真源字段名不同但词表相同，这里只改键名不改值，绝不就地造标签。

    去重只发生在**跨册**之间（同 id 且标签与正文全等＝折叠并计数；标签不同＝exit 2）。
    **册内**重复一律原样保留并只登记进 report（实测原 200 集内有一对逐字重复题）：
    默认单册口径下 n 必须与改造前相等，否则就是悄悄改了现产线的分母。
    缺标签／标签不在词表／无 news_id＝契约违反（exit 2），不静默择一。
    """
    kept: dict[str, dict] = {}
    merged: list[dict] = []
    per_source: list[dict] = []
    collapsed = 0
    intra_dup_ids: list[str] = []
    for path in paths:
        rows = load_jsonl(path)
        if not rows:
            _die_contract(f"金标册 {path} 读不到任何行")
        in_file: dict[str, dict] = {}
        added = 0
        for row in rows:
            gid = str(row.get("news_id") or "").strip()
            if not gid:
                _die_contract(f"{path} 存在无 news_id 的行，无法做训练/评估隔离判定")
            label = row.get("sentiment") or row.get("human_label")
            if not label:
                _die_contract(f"{path} 行 {gid} 既无 sentiment 也无 human_label（评估面禁空白标签）")
            if labels is not None and label not in labels:
                _die_contract(f"{path} 行 {gid} 标签 {label!r} 不在词表 {labels}")
            norm = {
                "news_id": gid,
                "title": row.get("title", ""),
                "content": row.get("content", ""),
                "sentiment": label,
                "stratum": row.get("stratum", ""),
                "label_source": row.get("label_source", "gold_200"),
            }
            same_file = in_file.get(gid)
            if same_file is not None:
                if same_file["sentiment"] != label:
                    _die_contract(f"{path} 册内同 news_id 标签打架：{gid} {same_file['sentiment']} vs {label}")
                if gid not in intra_dup_ids:
                    intra_dup_ids.append(gid)
            # 跨册比对只看"前面别的册"，册内重复不参与折叠
            other = kept.get(gid)
            if other is not None:
                if other["sentiment"] == label and other["content"] == norm["content"]:
                    collapsed += 1
                    continue
                _die_contract(
                    f"跨册同 news_id 标签打架：{gid} {other['sentiment']} vs {label}（金标必须唯一真源，禁在此择一）"
                )
            merged.append(norm)
            in_file[gid] = norm
            added += 1
        per_source.append({"path": str(path), "rows_read": len(rows), "rows_kept": added})
        kept.update(in_file)
    report = {
        "gold_sources": per_source,
        "gold_rows": len(merged),
        "gold_rows_read": sum(s["rows_read"] for s in per_source),
        "collapsed_cross_source": collapsed,
        "intra_file_duplicate_ids": intra_dup_ids,
    }
    return merged, report


def assert_no_gold_leakage(train_rows: list[dict], gold_rows: list[dict]) -> None:
    """训练面与评估面 id 交集必须为空（裁定①④"训练只认冻结版"的执行面守卫）。"""
    train_ids = {str(r.get("news_id") or "") for r in train_rows} - {""}
    gold_ids = {str(r.get("news_id") or "") for r in gold_rows}
    overlap = sorted(train_ids & gold_ids)
    if overlap:
        _die_contract(f"训练面含 {len(overlap)} 条金标题（样例 {overlap[:5]}）——考卷混进作业本，F1 不可信")


def write_metrics_json(metrics: dict, out_path: Path) -> None:
    """validate 指标 JSON 落盘（Phase 8 验收检查项 1 生产者：macro_f1 必填）。

    附带 generated_at 留痕；父目录自动创建。
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(metrics)
    payload["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA SFT 训练 + F1 评估")
    parser.add_argument("--smoke", action="store_true", help="快速验证管道（50 条）")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--no-validate", action="store_true", help="跳过最终 F1 评估")
    parser.add_argument(
        "--train-path",
        type=Path,
        default=SFT_TRAIN_PATH,
        help="训练 jsonl 源（默认 data/sft/train.jsonl，现产线不变）",
    )
    parser.add_argument(
        "--eval-path",
        type=Path,
        default=SFT_EVAL_PATH,
        help="训练中验证集 jsonl 源（默认 data/sft/eval.jsonl）",
    )
    parser.add_argument(
        "--gold-path",
        type=Path,
        nargs="+",
        default=[EVAL_200_PATH],
        help="算 Macro-F1 的金标册，可给多本（默认仅 data/eval/news_sentiment_200.jsonl）",
    )
    parser.add_argument(
        "--pass-line",
        type=float,
        default=DEFAULT_PASS_LINE,
        help="及格线（默认 0.75＝Phase 8 现产线口径；GPU-03B 蒸馏线显式传 0.767）",
    )
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=DEFAULT_METRICS_PATH,
        help="validate 指标 JSON 落盘路径（Phase 8 验收检查项 1 产物）",
    )
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

    train_items = load_jsonl(args.train_path)
    eval_items = load_jsonl(args.eval_path)
    log.info(
        "加载训练数据: train=%d eval=%d (train_path=%s eval_path=%s)",
        len(train_items),
        len(eval_items),
        args.train_path,
        args.eval_path,
    )
    if not train_items:
        log.error("无训练数据（先运行 build_sft_dataset.py，或检查 --train-path）")
        sys.exit(1)

    # 1.5 金标面在训练**之前**校验：考卷有问题就不必烧三小时 GPU（exit 2 早退）
    gold_report: dict = {}
    gold_items: list[dict] = []
    if not args.no_validate:
        from zephyr.ml_train.implementations.sentiment_sft_trainer import LABELS

        gold_items, gold_report = merge_gold_rows(list(args.gold_path), labels=LABELS)
        assert_no_gold_leakage(train_items, gold_items)
        log.info(
            "金标面: 读 %d 行→评估面 %d 条（跨册折叠 %d 条；册内重复题 %s）标签分布=%s",
            gold_report["gold_rows_read"],
            gold_report["gold_rows"],
            gold_report["collapsed_cross_source"],
            gold_report["intra_file_duplicate_ids"] or "无",
            {lb: sum(1 for g in gold_items if g["sentiment"] == lb) for lb in LABELS},
        )

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

    # 4. 评估 F1（金标面已在 1.5 校验并加载）
    if args.no_validate:
        log.info("跳过最终 F1 评估（--no-validate）")
        return

    if not gold_items:
        log.warning("评估集 %s 不存在，跳过 F1 评估", args.gold_path)
        return

    log.info("=== F1 评估（%d 条独立金标）===", len(gold_items))
    try:
        val_metrics = trainer.validate(features={"eval_items": gold_items}, target=None)
    except Exception as exc:  # noqa: BLE001 — 评估失败不丢已训练 adapter
        log.error("F1 评估失败（adapter 已保存）: %s", exc, exc_info=True)
        return

    f1 = val_metrics.get("macro_f1", 0.0)
    acc = val_metrics.get("accuracy", 0.0)
    n = int(val_metrics.get("n", 0))
    verdict = f"✅ 达标 ≥{args.pass_line:.2%}" if f1 >= args.pass_line else f"❌ 未达 {args.pass_line:.2%}"
    print("\n" + "=" * 60)
    print(f"SFT 训练完成（{time.time() - t0:.0f}s）")
    print(f"训练 loss: {metrics.get('train_loss', 0):.4f}")
    print(f"Macro-F1: {f1:.4f}  {verdict}")
    print(f"Accuracy: {acc:.4f}  (n={n})")
    print(f"LoRA adapter: {OUTPUT_DIR}")
    print("=" * 60)

    # 5. metrics JSON 落盘（Phase 8 验收检查项 1 产物：macro_f1/accuracy/n + train_loss）
    write_metrics_json(
        {
            **val_metrics,
            "train_loss": metrics.get("train_loss", 0.0),
            "model": OUTPUT_DIR.name,
            "pass_line": args.pass_line,
            "passed": bool(f1 >= args.pass_line),
            "gold": gold_report,
        },
        args.metrics_out,
    )
    log.info("metrics 已写入 %s", args.metrics_out)


if __name__ == "__main__":
    main()
