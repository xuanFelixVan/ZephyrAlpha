#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §3.1.9
# [MODULE] scripts.ml.build_sft_dataset
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.news_collector; scripts.ml.build_eval_set(keyword_label); urllib; pandas
# [CONSUMERS] scripts/ml/run_sft_train.py; P1-E3 NLP 管道 Phase 4
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 中文新闻关键词规则标注+平衡采样；排除评估集 200 条防数据泄露；FPB 英文异源增强；train/eval 9:1 划分
# [MODIFY-GUARD] 13_regime_phase3_engineering_plan.md §3.1.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse 不可达或 FPB 下载失败时降级（仅用可用数据）不 exit
# [TESTS] (CLI 脚本，无单元测试)
# [TTL] permanent
"""build_sft_dataset.py — P1-E3 Phase 4: 构建 LoRA SFT 训练数据集。

数据组成（MVP，零成本，§Phase 4 裁定）：
  1. 中文新闻（ClickHouse fund_news_data）—— 关键词规则标注 + 平衡采样
     - 多时间段采集（危机期关键词密集，pos/neg 样本充足）
     - 排除 ``data/eval/news_sentiment_200.jsonl`` 的 200 条 news_id（防数据泄露）
     - 复用 ``build_eval_set.keyword_label``（避免代码克隆，单一真源）
     - 平衡采样：pos/neg 全留（少数类宝贵），neutral 控制到与 pos/neg 均衡
  2. Financial PhraseBank 英文（AllAgree 2264 句，人工标注，异源增强）
     - 教模型金融情感语义理解（高质量人工标注，与中文关键词规则评估集异源）
     - urllib 从 GitHub raw 下载，失败则跳过（降级）

输出 ``data/sft/{train,eval}.jsonl``（每行 title/content/sentiment/score/source），
训练时经 ``build_sft_dataset()`` 转 messages 格式。

⚠ 同源循环风险（Phase 4 MVP）：中文训练数据标签与评估集 ground truth 同为关键词规则。
   后续 DeepSeek API 充值后，用 DeepSeek 蒸馏训练数据去循环（治本演化）。

用法:
    python scripts/ml/build_sft_dataset.py [--target-per-class 1200] [--no-fpb]

依据: 13_regime_phase3_engineering_plan.md §3.1.9
SSoT: #ARCH-NLP-PIPELINE-001
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import urllib.request
from pathlib import Path

# ── 项目路径 ──
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "ml"))  # 复用 build_eval_set.keyword_label

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = ROOT / "data" / "sft"
EVAL_SET_PATH = ROOT / "data" / "eval" / "news_sentiment_200.jsonl"

# ── 中文新闻采集时间段（危机期关键词密集）──
PERIODS = [
    ("2015-06-15", "2015-09-15", 2500),  # 股灾 1.0
    ("2015-12-01", "2016-02-29", 2500),  # 股灾 2.0/3.0 + 熔断
    ("2018-06-01", "2019-01-31", 2500),  # 贸易战
    ("2020-02-01", "2020-04-30", 2500),  # 疫情
    ("2022-01-01", "2022-05-31", 2500),  # 美联储加息
    ("2024-01-01", "2024-09-30", 2500),  # 近期波动
    ("2017-03-01", "2017-09-30", 1500),  # 常态
    ("2023-01-01", "2023-09-30", 1500),  # 常态
]

FPB_URL = "https://raw.githubusercontent.com/AnonZamura/financial-phrasebank/master/Data/Sentences_AllAgree.txt"

LABELS = ("positive", "negative", "neutral")


def load_eval_ids() -> set[str]:
    """加载评估集 news_id（采集时排除，防数据泄露）。"""
    ids: set[str] = set()
    if not EVAL_SET_PATH.exists():
        return ids
    with open(EVAL_SET_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                ids.add(str(json.loads(line).get("news_id", "")))
            except json.JSONDecodeError:
                continue
    log.info("评估集 news_id 排除列表: %d 条", len(ids))
    return ids


def collect_chinese_news(eval_ids: set[str]) -> list[dict]:
    """多时间段采集中文新闻，排除评估集。"""
    from zephyr.data.news_collector import collect_news

    all_news: list[dict] = []
    seen: set[str] = set()
    for start, end, limit in PERIODS:
        try:
            df = collect_news(start, end, limit=limit)
        except Exception as exc:  # noqa: BLE001 — 单段失败不阻断
            log.warning("采集 %s~%s 失败: %s", start, end, exc)
            continue
        added = 0
        for _, row in df.iterrows():
            nid = str(row.get("news_id", ""))
            if not nid or nid in eval_ids or nid in seen:
                continue
            seen.add(nid)
            all_news.append(
                {
                    "news_id": nid,
                    "title": str(row.get("title", "")).strip(),
                    "content": str(row.get("content", ""))[:500],
                    "source": str(row.get("source", "")),
                    "publish_time": str(row.get("publish_time", "")),
                    "lang": "zh",
                }
            )
            added += 1
        log.info("采集 %s~%s: +%d（累计 %d）", start, end, added, len(all_news))
    return all_news


def label_with_keywords(news_list: list[dict]) -> list[dict]:
    """复用 build_eval_set.keyword_label 标注（单一真源，避免克隆）。"""
    from build_eval_set import keyword_label  # type: ignore[import-not-found]

    labeled: list[dict] = []
    for news in news_list:
        result = keyword_label(news)
        result["source"] = "ch_news_kw"
        labeled.append(result)
    return labeled


def balance_sample(labeled: list[dict], *, target_per_class: int, seed: int = 42) -> list[dict]:
    """平衡采样：每类采样到 target_per_class（不够全留），实现三类均衡。

    关键词规则下 positive 天然偏多（利好词命中率高）、negative 偏少。
    若 positive 全留会致 67% 失衡 → 模型偏向 positive，评估集（neutral 71%）
    上 pos/neg F1 崩塌。故每类都裁到 target_per_class，使 pos≈neg≈neutral。
    """
    rnd = random.Random(seed)
    by_label: dict[str, list[dict]] = {l: [] for l in LABELS}
    for item in labeled:
        s = str(item.get("sentiment", "neutral")).strip().lower()
        if s in by_label:
            by_label[s].append(item)

    pos_n, neg_n, neu_n = len(by_label["positive"]), len(by_label["negative"]), len(by_label["neutral"])
    log.info("平衡前分布: pos=%d neg=%d neutral=%d", pos_n, neg_n, neu_n)

    # 每类采样到 target_per_class（不够全留）——实现三类均衡
    for label in LABELS:
        pool = by_label[label]
        if len(pool) > target_per_class:
            by_label[label] = rnd.sample(pool, target_per_class)
            log.info("%s 采样 %d→%d", label, len(pool), target_per_class)

    balanced = by_label["positive"] + by_label["negative"] + by_label["neutral"]
    rnd.shuffle(balanced)
    log.info(
        "平衡后: pos=%d neg=%d neutral=%d 总计=%d",
        len(by_label["positive"]),
        len(by_label["negative"]),
        len(by_label["neutral"]),
        len(balanced),
    )
    return balanced


def fetch_fpb_english() -> list[dict]:
    """加载 Financial PhraseBank（AllAgree）英文数据（HF datasets parquet）。失败返回空。

    尝试多个 HF repo（parquet 版本），任一成功即用。FPB label 可能是 int
    (0=negative,1=neutral,2=positive) 或 str，统一映射。
    """
    samples: list[dict] = []
    # 候选 repo（parquet 版本优先，避免 loading script 不兼容 datasets 4.x）
    candidates = [
        ("takala/financial_phrasebank", "sentences_allagree"),
        ("mteb/financial_phrasebank", None),
    ]
    from datasets import load_dataset

    for repo, config in candidates:
        try:
            log.info("加载 FPB: %s (config=%s)", repo, config)
            ds = load_dataset(repo, config, split="train") if config else load_dataset(repo, split="train")
            break
        except Exception as exc:  # noqa: BLE001 — 单 repo 失败试下一个
            log.warning("FPB %s 加载失败: %s", repo, str(exc)[:120])
            ds = None
    else:
        log.warning("FPB 全部候选 repo 失败（跳过英文增强）")
        return samples

    if ds is None:
        return samples

    _INT_MAP = {0: "negative", 1: "neutral", 2: "positive"}
    for row in ds:
        sentence = str(row.get("sentence", row.get("text", ""))).strip()
        raw_label = row.get("label", row.get("sentiment", ""))
        if isinstance(raw_label, int) or (isinstance(raw_label, str) and raw_label.isdigit()):
            sent = _INT_MAP.get(int(raw_label), "neutral")
        else:
            sent = str(raw_label).strip().lower()
        if sent not in LABELS or not sentence:
            continue
        score = 0.8 if sent != "neutral" else 0.5
        samples.append(
            {
                "title": sentence[:100],
                "content": sentence,
                "sentiment": sent,
                "score": score,
                "source": "fpb_allagree",
                "lang": "en",
            }
        )
    log.info("FPB 加载: %d 条英文样本", len(samples))
    return samples


def write_jsonl(items: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    log.info("写入 %s: %d 条", path, len(items))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="构建 LoRA SFT 训练数据集")
    parser.add_argument("--target-per-class", type=int, default=1200, help="每类目标样本数（neutral 上限）")
    parser.add_argument("--no-fpb", action="store_true", help="跳过 FPB 英文增强")
    parser.add_argument("--eval-ratio", type=float, default=0.1, help="训练监控 eval 划分比例")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    rnd = random.Random(args.seed)

    # 1. 加载评估集排除列表
    eval_ids = load_eval_ids()

    # 2. 采集中文新闻
    log.info("=== 采集中文新闻 ===")
    cn_news = collect_chinese_news(eval_ids)
    log.info("中文新闻采集完成: %d 条", len(cn_news))

    # 3. 关键词规则标注
    cn_labeled = label_with_keywords(cn_news) if cn_news else []

    # 4. 平衡采样
    cn_balanced = (
        balance_sample(cn_labeled, target_per_class=args.target_per_class, seed=args.seed) if cn_labeled else []
    )

    # 5. FPB 英文增强
    en_samples: list[dict] = []
    if not args.no_fpb:
        log.info("=== 下载 Financial PhraseBank ===")
        en_samples = fetch_fpb_english()

    # 6. 合并
    all_samples = cn_balanced + en_samples
    rnd.shuffle(all_samples)
    log.info("=== 合并总计: %d 条（中文 %d + 英文 %d）===", len(all_samples), len(cn_balanced), len(en_samples))

    if not all_samples:
        log.error("无训练数据，退出")
        sys.exit(1)

    # 7. 分布统计
    from collections import Counter

    dist = Counter(s.get("sentiment") for s in all_samples)
    log.info("最终分布: %s", dict(dist))

    # 8. 划分 train / eval_split（训练监控用，非最终评估）
    n_eval = max(1, int(len(all_samples) * args.eval_ratio))
    eval_split = all_samples[:n_eval]
    train_split = all_samples[n_eval:]
    log.info("划分: train=%d eval_split=%d", len(train_split), len(eval_split))

    # 9. 写入
    write_jsonl(train_split, OUTPUT_DIR / "train.jsonl")
    write_jsonl(eval_split, OUTPUT_DIR / "eval.jsonl")
    log.info("SFT 数据集构建完成: %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
