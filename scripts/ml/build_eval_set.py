#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 1
# [MODULE] scripts.ml.build_eval_set
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.news_collector
# [CONSUMERS] (CLI 脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 分层抽样构建评估集；关键词规则标注（DeepSeek/Ollama backend 预留未实现）；断点续作追加写入
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse 不可达→collect_news 抛异常传播；keyword_label 纯规则无异常；空结果写入空文件不 exit
# [TESTS] (CLI 脚本，无单元测试)
# [TTL] permanent
"""build_eval_set.py — P1-E3 Phase 1: 构建 200 条新闻情感评估集。

分层抽样（危机期/复苏期/常态期）从 ClickHouse 采集新闻，
当前实现关键词规则标注（DeepSeek/Ollama backend 预留未实现）。

用法:
    python scripts/ml/build_eval_set.py [--backend keyword|deepseek|ollama] [--resume]

输出:
    data/eval/news_sentiment_200.jsonl  （200 条标注新闻，断点续作用）

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 1
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

from zephyr.data.news_collector import collect_news  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

OUTPUT_PATH = ROOT / "data" / "eval" / "news_sentiment_200.jsonl"

# ── 分层抽样配置（200 条）──
STRATA = [
    # 危机期 100 条
    ("crisis_2015", "2015-06-15", "2015-09-15", 35),
    ("crisis_2020", "2020-02-01", "2020-04-15", 35),
    ("crisis_2024", "2024-06-01", "2024-09-30", 30),
    # 复苏期 50 条
    ("recovery_2015", "2015-10-01", "2016-02-28", 18),
    ("recovery_2020", "2020-05-01", "2020-08-31", 17),
    ("recovery_2024", "2024-10-01", "2025-03-31", 15),
    # 常态期 50 条
    ("normal_2017", "2017-01-01", "2017-12-31", 17),
    ("normal_2019", "2019-01-01", "2019-12-31", 17),
    ("normal_2022", "2022-01-01", "2022-12-31", 16),
]

# ── 关键词规则标注（降级方案）──
_KW_POSITIVE = [
    "降准",
    "降息",
    "减税",
    "利好",
    "增长",
    "盈利",
    "回购",
    "增持",
    "重组",
    "并购",
    "改革",
    "投资",
    "基建",
    "补贴",
    "扶持",
    "刺激",
    "支持",
    "上涨",
    "突破",
    "回暖",
    "复苏",
    "企稳",
    "反弹",
]
_KW_NEGATIVE = [
    "跌停",
    "暴跌",
    "下跌",
    "利空",
    "亏损",
    "减持",
    "违规",
    "处罚",
    "退市",
    "爆雷",
    "违约",
    "下修",
    "下调",
    "风险",
    "警告",
    "监管",
    "限售",
    "解禁",
    "商誉减值",
    "业绩变脸",
    "诉讼",
    "熔断",
    "跳水",
    "崩盘",
    "恐慌",
    "抛售",
]


def keyword_label(news: dict) -> dict:
    """关键词规则标注——按正/负面关键词计数判定情感。

    降级方案：DeepSeek API 余额不足或 Ollama 超时时使用。
    """
    text = f"{news['title']} {news['content']}"
    pos_count = sum(1 for kw in _KW_POSITIVE if kw in text)
    neg_count = sum(1 for kw in _KW_NEGATIVE if kw in text)
    total = pos_count + neg_count
    if total == 0:
        sentiment, score = "neutral", 0.5
    elif pos_count > neg_count:
        sentiment = "positive"
        score = 0.5 + 0.5 * (pos_count / total)  # 0.5~1.0
    elif neg_count > pos_count:
        sentiment = "negative"
        score = 0.5 + 0.5 * (neg_count / total)  # 0.5~1.0
    else:
        sentiment, score = "neutral", 0.5
    return {**news, "sentiment": sentiment, "score": round(score, 3)}


def _sample_stratum(name: str, start: str, end: str, n: int) -> list[dict]:
    """从单个分层抽样 n 条新闻。"""
    df = collect_news(start, end, limit=n * 3)  # 多取以备筛选
    if df.empty:
        log.warning("分层 %s (%s~%s) 无新闻数据", name, start, end)
        return []
    rows: list[dict] = []
    for _, row in df.head(n).iterrows():
        rows.append(
            {
                "news_id": str(row.get("news_id", "")),
                "publish_time": str(row.get("publish_time", "")),
                "title": str(row.get("title", "")),
                "content": str(row.get("content", ""))[:500],
                "source": str(row.get("source", "")),
                "stratum": name,
            }
        )
    log.info("分层 %s: 采集 %d 条", name, len(rows))
    return rows


def _load_done(path: Path) -> set[str]:
    """断点续作：已标注的 news_id。"""
    if not path.exists():
        return set()
    done: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                done.add(json.loads(line)["news_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def _print_distribution(items: list[dict]) -> None:
    """打印情感分布统计。"""
    from collections import Counter

    dist = Counter(item.get("sentiment", "?") for item in items)
    total = len(items)
    print("\n=== 情感分布 ===")
    for label in ("positive", "negative", "neutral"):
        count = dist.get(label, 0)
        print(f"  {label:10s}: {count:4d} ({100 * count / total:.1f}%)")
    print(f"  {'total':10s}: {total:4d}")


def _parse_args() -> argparse.Namespace:
    """解析 CLI 参数。"""
    parser = argparse.ArgumentParser(description="构建新闻情感评估集")
    parser.add_argument(
        "--backend", default="keyword", choices=["keyword", "deepseek", "ollama"], help="标注后端（默认 keyword 规则）"
    )
    parser.add_argument("--resume", action="store_true", default=True, help="断点续作")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    return parser.parse_args()


def _collect_all_news() -> list[dict]:
    """分层抽样采集全部新闻。"""
    all_news: list[dict] = []
    for name, start, end, n in STRATA:
        rows = _sample_stratum(name, start, end, n)
        all_news.extend(rows)
    log.info("总计采集 %d 条新闻", len(all_news))
    return all_news


def main() -> None:
    args = _parse_args()

    # 1. 分层抽样采集
    all_news = _collect_all_news()

    # 2. 断点续作
    done_ids = _load_done(OUTPUT_PATH) if args.resume else set()
    todo = [n for n in all_news if n.get("news_id") not in done_ids]
    log.info("待标注: %d 条（跳过已标注 %d 条）", len(todo), len(all_news) - len(todo))

    # 3. 标注
    mode = "a" if args.resume and OUTPUT_PATH.exists() else "w"
    labeled: list[dict] = []
    with open(OUTPUT_PATH, mode, encoding="utf-8") as f:
        for i, news in enumerate(todo):
            result = keyword_label(news)
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
            f.flush()
            labeled.append(result)
            if (i + 1) % 20 == 0:
                log.info("进度: %d/%d", i + 1, len(todo))

    # 4. 汇总全部（含断点续作旧记录）
    all_items: list[dict] = []
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    all_items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # 5. 分布统计
    _print_distribution(all_items)
    log.info("评估集写入: %s (%d 条)", OUTPUT_PATH, len(all_items))


if __name__ == "__main__":
    main()
