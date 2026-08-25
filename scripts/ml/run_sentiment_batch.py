#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 7
# [MODULE] scripts.ml.run_sentiment_batch
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.nlp.nlp_inference; zephyr.nlp.sentiment_aggregator; zephyr.data.news_collector（db 源，lazy）; zephyr.integration.local_model.ollama_chat（运行态，lazy）
# [CONSUMERS] (CLI 批量脚本，无模块消费者；产物供回测/regime S2 消费)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 断点续作追加写入（news_id 去重）；单条推理失败降级 neutral 不阻断批量；Ollama 不可达 exit 1；输入文件不存在 exit 1；聚合产物含 negative_count（S2 bad_news_flat 入参）与 vote_score（跨源一致性）；批次结束写 benchmark.json（items/elapsed_s，验收检查项 2 生产者）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 7
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入缺失/Ollama 不可达→exit 1；逐条推理异常降级不阻断
# [TESTS] tests/scripts/test_ml_run_sentiment_batch.py
# [TTL] permanent
"""run_sentiment_batch.py — P1-E3 Phase 7: 离线批量情感推理 + 日级聚合。

端到端管道（13 号 Phase 7）：news_data → nlp_inference 批量推理 →
sentiment_aggregator 跨源一致性投票 + 按日聚合 → 产物落盘（回测用）。
默认范围 2010-2026 全历史（可 --start-date/--end-date 裁剪）。

产物（--out-dir 下）:
  - predictions.jsonl     逐条预测（news_id/sentiment/score/polarity/cached/error）
  - daily_sentiment.jsonl 日级聚合（negative_count/vote_score/vote_strength 等）
  - benchmark.json        推理速度产物（items/elapsed_s，Phase 8 验收检查项 2）

用法:
    # JSONL 输入（离线/测试）
    python scripts/ml/run_sentiment_batch.py --source jsonl --input data/eval/news_sentiment_200.jsonl --limit 50
    # ClickHouse fund_news_data 全历史（Ollama 须就绪）
    python scripts/ml/run_sentiment_batch.py --source db --start-date 2010-01-01

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 7
SSoT: #ARCH-NLP-PIPELINE-001
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.nlp.nlp_inference import (  # noqa: E402
    PROMPT_VERSION,
    InferConfig,
    SentimentResult,
    infer_sentiment,
)
from zephyr.nlp.sentiment_aggregator import (  # noqa: E402
    DailySentiment,
    SourceSentiment,
    aggregate_daily,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DEFAULT_OUT_DIR = ROOT / "data" / "sentiment_batch"
PRED_FILENAME = "predictions.jsonl"
DAILY_FILENAME = "daily_sentiment.jsonl"
BENCH_FILENAME = "benchmark.json"


def load_news_jsonl(path: Path) -> list[dict[str, Any]]:
    """加载 JSONL 新闻输入（news_id/title/content/source/publish_time）。"""
    items: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def load_db_news(start_date: str, end_date: str, limit: int = 0) -> list[dict[str, Any]]:
    """从 fund_news_data 采集（lazy import，db 源运行态才触达 ClickHouse）。"""
    from zephyr.data.news_collector import collect_news

    df = collect_news(start_date, end_date, limit=limit)
    return df.to_dict(orient="records")


def load_done_ids(pred_path: Path) -> set[str]:
    """断点续作：已预测的 news_id 集合。"""
    if not pred_path.exists():
        return set()
    done: set[str] = set()
    with open(pred_path, encoding="utf-8") as f:
        for line in f:
            try:
                done.add(json.loads(line)["news_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def publish_date_of(news: dict[str, Any]) -> str:
    """从新闻记录提取日键 'YYYY-MM-DD'（兼容 datetime/字符串 publish_time）。"""
    ts = news.get("publish_time") or news.get("publish_date") or ""
    return str(ts)[:10]


def run_batch(
    news_items: list[dict[str, Any]],
    *,
    chat: Any,
    pred_path: Path,
    config: InferConfig | None = None,
    resume: bool = True,
    cache: Any = None,
) -> list[SentimentResult]:
    """批量推理 + 逐条追加写入 predictions.jsonl（断点续作）。

    逐条推理逐条落盘——进程中途被杀仅损失当前一条，已写部分下次
    运行经 news_id 去重跳过（2026-08-25 修复：原先全量推完才落盘，
    12 万条批次中途被杀即全部白算）。单条失败由 infer_sentiment
    内部降级 neutral 不阻断。返回本次新推理结果（不含断点续作跳过的部分）。
    """
    done = load_done_ids(pred_path) if resume else set()
    todo = [n for n in news_items if str(n.get("news_id", "")) not in done]
    log.info("待推理 %d 条（跳过已预测 %d 条）", len(todo), len(news_items) - len(todo))
    if not todo:
        return []

    mode = "a" if resume and pred_path.exists() else "w"
    results: list[SentimentResult] = []
    t0 = time.time()
    with open(pred_path, mode, encoding="utf-8") as f:
        for news in todo:
            r = infer_sentiment(
                title=str(news.get("title", "")),
                content=str(news.get("content", "")),
                chat=chat,
                news_id=str(news.get("news_id", "")),
                cache=cache,
                config=config,
            )
            results.append(r)
            f.write(
                json.dumps(
                    {
                        "news_id": str(news.get("news_id", "")),
                        "source": news.get("source", ""),
                        "publish_date": publish_date_of(news),
                        "prompt": PROMPT_VERSION,
                        "sentiment": r.sentiment,
                        "score": r.score,
                        "polarity": r.polarity,
                        "cached": r.cached,
                        "error": r.error,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            f.flush()
            if len(results) % 100 == 0:
                elapsed = time.time() - t0
                rate = len(results) / elapsed if elapsed > 0 else 0.0
                log.info("进度 %d/%d  %.1f 条/秒", len(results), len(todo), rate)
    return results


def aggregate_from_predictions(pred_path: Path) -> list[DailySentiment]:
    """从 predictions.jsonl 全量聚合（断点续作安全：含历史已预测部分）。"""
    items: list[SourceSentiment] = []
    if not pred_path.exists():
        return []
    with open(pred_path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            items.append(
                SourceSentiment(
                    source=str(obj.get("source", "") or "unknown"),
                    polarity=float(obj.get("polarity", 0.0)),
                    publish_date=str(obj.get("publish_date", "")),
                )
            )
    return aggregate_daily(items)


def write_daily(daily: list[DailySentiment], out_path: Path) -> None:
    """日级聚合产物写 JSONL。"""
    with open(out_path, "w", encoding="utf-8") as f:
        for d in daily:
            f.write(json.dumps(asdict(d), ensure_ascii=False) + "\n")


def write_benchmark(items: int, elapsed_s: float, out_path: Path) -> None:
    """推理速度 benchmark 产物落盘（验收检查项 2 生产者：{"items", "elapsed_s"}）。

    items=本次新推理条数（断点续作跳过部分不计）；父目录自动创建。
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"items": int(items), "elapsed_s": float(elapsed_s)}, ensure_ascii=False),
        encoding="utf-8",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="离线批量情感推理 + 日级聚合（Phase 7）")
    parser.add_argument("--source", choices=["db", "jsonl"], default="jsonl")
    parser.add_argument("--input", type=Path, default=None, help="jsonl 源输入文件")
    parser.add_argument("--start-date", default="2010-01-01")
    parser.add_argument("--end-date", default=time.strftime("%Y-%m-%d"))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", default="qwen3:8b", help="Ollama 模型名")
    parser.add_argument("--limit", type=int, default=0, help="限制推理条数（0=全部）")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # 1. 输入
    if args.source == "jsonl":
        if args.input is None or not args.input.exists():
            log.error("jsonl 源须指定存在的 --input 文件（实际 %s）", args.input)
            sys.exit(1)
        news_items = load_news_jsonl(args.input)
    else:
        news_items = load_db_news(args.start_date, args.end_date)
    if args.limit > 0:
        news_items = news_items[: args.limit]
    log.info("输入新闻 %d 条（source=%s）", len(news_items), args.source)

    # 2. 推理后端（Ollama 单一推理源，13 号 §3.1.13 H）+ 查询缓存（重复标题去重）
    from zephyr.integration.local_model.cache_layer import CacheLayer
    from zephyr.integration.local_model.ollama_chat import OllamaChat

    if not OllamaChat.quick_alive():
        log.error("Ollama 不可达（localhost:11434），请先启动 Ollama")
        sys.exit(1)
    chat = OllamaChat(model=args.model, timeout_s=args.timeout)
    cache = CacheLayer()

    # 3. 批量推理（断点续作，逐条落盘）
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = args.out_dir / PRED_FILENAME
    cfg = InferConfig(model_version=args.model)
    t_batch = time.time()
    results = run_batch(
        news_items, chat=chat, pred_path=pred_path, config=cfg, resume=args.resume, cache=cache
    )
    batch_elapsed = time.time() - t_batch

    # 4. 日级聚合（跨源一致性投票，26 号 §2.7；从 predictions 全量聚合 resume 安全）
    daily = aggregate_from_predictions(pred_path)
    daily_path = args.out_dir / DAILY_FILENAME
    write_daily(daily, daily_path)

    # 5. benchmark 产物（验收检查项 2：1000 条 < 300s；items=本次新推理条数）
    bench_path = args.out_dir / BENCH_FILENAME
    write_benchmark(len(results), batch_elapsed, bench_path)
    log.info(
        "完成：预测 %d 条 → %s；日级聚合 %d 天 → %s；benchmark → %s",
        len(results),
        pred_path,
        len(daily),
        daily_path,
        bench_path,
    )


if __name__ == "__main__":
    main()
