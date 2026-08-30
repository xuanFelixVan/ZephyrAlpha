# [BLUEPRINT] MOD-NLP-SENT-PIPE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 7
# [MODULE] zephyr.nlp.sentiment_pipeline
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.nlp.nlp_inference; zephyr.nlp.sentiment_aggregator
# [CONSUMERS] scripts/ml/run_sentiment_batch.py（CLI 壳，后续接入位）; .runtime 跑批驱动（离线批量 smoke）; regime S2 bad_news_flat（Phase 7 negative_count 源）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 离线批量端到端接线：news dict → infer_batch → aggregate_daily → daily_sink；chat/daily_sink 全注入（LLM/网络可 mock）；空输入→空 outcome 且 sink 不调用；单条推理失败降级 neutral 计入 n_degraded 不阻断；chat=None→NLPInferenceError 契约传播
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 7
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——空/退化输入返回空 outcome；chat=None 抛 nlp_inference.NLPInferenceError（ZA-NLP-0001，契约违反传播）
# [TESTS] tests/nlp/test_sentiment_pipeline.py
# [A_module] module_id=MOD-NLP-SENT-PIPE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-NLP-PIPELINE-001 Phase 7
# [ALGO_FLOW]
# I1: news dict 序列（news_id/title/content/source/publish_time）
# F1: infer_batch（chat 注入，单条失败降级 neutral）
# F2: SentimentResult+news → SourceSentiment（publish_date 日键提取）
# F3: aggregate_daily（跨源一致性投票 + 日级聚合）
# A1: daily_sink 注入推送（可选；空产物不调用）
# O1: PipelineOutcome（n_input/n_inferred/n_degraded/n_daily/elapsed_s/daily）
# [/ALGO_FLOW]
"""
MOD-NLP-SENT-PIPE SentimentPipeline — 离线批量端到端接线件（NLP Phase 7）。

设计依据：
- 13 号 §3.1.6 管道架构：news_data → 采集 → NLP 推理 → 情感聚合 → 指标。
- 13 号 §3.1.11 步骤 9/10：情感聚合层 + 离线批量推理（回测用）。
- 13 号 §3.1.13 H 单一推理源原则：推理后端走 ChatBackend 协议注入
  （OllamaChat / DeepSeekChat / FakeChat 均满足），训练轨产物 GGUF 回灌后
  经同一协议消费，禁止独立推理服务。

定位：把「推理 → 聚合 → 产物下沉」三环节编成**可注入、可测试**的 src 层接线件，
补 scripts/ml/run_sentiment_batch.py（CLI 壳：断点续作/DB 采集/Ollama 守卫）
与 sentiment_aggregator（纯聚合）之间的管道断点——离线批量模式下 LLM/网络
全 mock 即可端到端跑通并产出验收指标（PipelineOutcome）。

落库口径：13 号 Phase 7 离线批量产物=日级聚合 JSONL 落盘（回测/S2 消费）；
``write_daily_jsonl`` 为默认产物下沉件，``daily_sink`` 注入位支持未来 DB 下沉
（intelligence 域 news_sentiment_window 为另一独立管道，非本链路）。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 7
SSoT: #ARCH-NLP-PIPELINE-001
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: news 参数
#   fields: 参数 news，类型注解 dict[str, Any]
#   code: sentiment_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: news_items 参数
#   fields: 参数 news_items，类型注解 list[dict[str, Any]]
#   code: sentiment_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: chat 参数
#   fields: 参数 chat（无注解）
#   code: sentiment_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: daily_sink 参数
#   fields: 参数 daily_sink（无注解）
#   code: sentiment_pipeline.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① publish_date_of
#   name_en: publish_date_of
#   intro: 从新闻记录提取日键 'YYYY-MM-DD'（兼容 datetime/字符串 publish_time）。
#   desc: 从新闻记录提取日键 'YYYY-MM-DD'（兼容 datetime/字符串 publish_time）。；源码 L150-L153
#   inputs: news
#   outputs: str
# - id: A2
#   name_zh: ② run_offline_pipeline
#   name_en: run_offline_pipeline
#   intro: 离线批量端到端管道：推理 → 日级聚合 → 产物下沉。
#   desc: 离线批量端到端管道：推理 → 日级聚合 → 产物下沉。 Parameters ---------- news_items : 新闻 dict 列表（需含 ``title``；``…；源码 L164-L207
#   inputs: news_items chat daily_sink config
#   outputs: PipelineOutcome
# - id: A3
#   name_zh: ③ write_daily_jsonl
#   name_en: write_daily_jsonl
#   intro: 日级聚合产物 JSONL 落盘（13 号 Phase 7 默认下沉口径，父目录自动创建）。
#   desc: 日级聚合产物 JSONL 落盘（13 号 Phase 7 默认下沉口径，父目录自动创建）。 产物字段含 ``negative_count``（S2 bad_news_flat 入…；源码 L210-L219
#   inputs: daily out_path
#   outputs: 返回值
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: scripts/ml/run_sentiment_batch.py（CLI 壳，后续接入位）; .runtime 跑批驱动（离线批量 smoke）; regi…
# - id: O2
#   name_zh: PipelineOutcome
#   name_en: PipelineOutcome
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: scripts/ml/run_sentiment_batch.py（CLI 壳，后续接入位）; .runtime 跑批驱动（离线批量 smoke）; regi…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Final, Sequence

from zephyr.nlp.nlp_inference import ChatBackend, InferConfig, SentimentResult, infer_batch
from zephyr.nlp.sentiment_aggregator import DailySentiment, SourceSentiment, aggregate_daily

#: 日级聚合产物下沉回调（接收聚合结果列表；空产物不触发）
DailySink = Callable[[Sequence[DailySentiment]], None]


@dataclass(frozen=True, slots=True)
class PipelineOutcome:
    """离线批量管道运行指标（验收汇总输入）。

    Attributes
    ----------
    n_input : 输入新闻条数。
    n_inferred : 完成推理条数（含降级）。
    n_degraded : 推理失败降级 neutral 条数（SentimentResult.error 非空）。
    n_daily : 聚合产出天数。
    elapsed_s : 管道耗时（秒）。
    daily : 日级聚合产物（与 daily_sink 接收内容一致）。
    """

    n_input: int
    n_inferred: int
    n_degraded: int
    n_daily: int
    elapsed_s: float
    daily: tuple[DailySentiment, ...] = ()


def publish_date_of(news: dict[str, Any]) -> str:
    """从新闻记录提取日键 'YYYY-MM-DD'（兼容 datetime/字符串 publish_time）。"""
    ts = news.get("publish_time") or news.get("publish_date") or ""
    return str(ts)[:10]


def _to_source_sentiment(news: dict[str, Any], result: SentimentResult) -> SourceSentiment:
    return SourceSentiment(
        source=str(news.get("source", "") or "unknown"),
        polarity=result.polarity,
        publish_date=publish_date_of(news),
    )


def run_offline_pipeline(
    news_items: list[dict[str, Any]],
    *,
    chat: ChatBackend,
    daily_sink: DailySink | None = None,
    config: InferConfig | None = None,
) -> PipelineOutcome:
    """离线批量端到端管道：推理 → 日级聚合 → 产物下沉。

    Parameters
    ----------
    news_items : 新闻 dict 列表（需含 ``title``；``content``/``news_id``/``source``/
        ``publish_time`` 可选）。
    chat : 推理后端（ChatBackend 协议；mock 可注入，禁真调 LLM 的测试/跑批场景
        用 fake 实现即可端到端跑通）。
    daily_sink : 日级聚合产物下沉回调（可选；空产物不调用）。
    config : 推理配置（``None`` 用 ``InferConfig()`` 默认值）。

    Returns
    -------
    PipelineOutcome —— 空输入返回全零空 outcome（不抛异常）。

    Raises
    ------
    NLPInferenceError
        chat 为 None（契约违反，由 nlp_inference 传播）。
    """
    t0 = time.time()
    if not news_items:
        return PipelineOutcome(0, 0, 0, 0, time.time() - t0, ())

    results = infer_batch(news_items, chat=chat, config=config)
    items = [_to_source_sentiment(n, r) for n, r in zip(news_items, results, strict=True)]
    daily = aggregate_daily(items)
    if daily_sink is not None and daily:
        daily_sink(daily)
    return PipelineOutcome(
        n_input=len(news_items),
        n_inferred=len(results),
        n_degraded=sum(1 for r in results if r.error),
        n_daily=len(daily),
        elapsed_s=time.time() - t0,
        daily=tuple(daily),
    )


def write_daily_jsonl(daily: Sequence[DailySentiment], out_path: Path) -> None:
    """日级聚合产物 JSONL 落盘（13 号 Phase 7 默认下沉口径，父目录自动创建）。

    产物字段含 ``negative_count``（S2 bad_news_flat 入参）与
    ``vote_score``/``vote_strength``（跨源一致性），对齐验收检查项 3。
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for d in daily:
            f.write(json.dumps(asdict(d), ensure_ascii=False) + "\n")


__all__: Final = [
    "DailySink",
    "PipelineOutcome",
    "publish_date_of",
    "run_offline_pipeline",
    "write_daily_jsonl",
]
