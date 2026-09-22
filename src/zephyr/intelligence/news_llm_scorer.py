# [BLUEPRINT] MOD-INT-NEWS-LLM-SCORER | docs/_working/emotion_line/gap_list_and_construction_proposal.md §5-S5
# [MODULE] zephyr.intelligence.news_llm_scorer
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.nlp.nlp_inference (infer_sentiment/SentimentResult); zephyr.integration.local_model.ollama_chat (OllamaChat, LSG 经 lsg_gate 内置)
# [CONSUMERS] zephyr.intelligence.nightly_sentiment_window (run_nightly_sentiment_batch: analyzer 注入位)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] factory-off：旗标文件 data/runtime/nightly_sentiment_llm.enabled 不存在→返回 None
#              （=规则法不变，零行为变更）；启=创建标记文件（全资产净零：零新配置件零新计划任务）；
#              polarity 契约对齐（P0-1 修复：传 polarity 有向极性，禁误用 score 强度）；
#              LSG 链=OllamaChat 内置 lsg_gate（本件不绕不重复建）；S5 双轨对照期：C6 成分仍消费
#              rule 值，LLM 行 data_source='llm' 落库仅供对照，对照期结论交 Owner 后再定切换。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] make_llm_scorer 零抛出（构造失败→log warning 返回 None 降级规则法）；
#                  单条打分异常由 analyzer 分支捕获落 llm_fallback（既有契约）。
# [TESTS] tests/intelligence/test_news_llm_scorer.py
# [A_module] module_id=MOD-INT-NEWS-LLM-SCORER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""news_llm_scorer — 夜间新闻情绪 LLM 打分器构造入口（S5，factory-off）。

接线三件套（全部既有件，本件只做组装）：
    nlp_inference.infer_sentiment（LLM 推理+解析+缓存键）
    × OllamaChat（本地推理后端，LSG 经内置 lsg_gate）
    → analyzer 级 LLMSentimentScorer 协议 (title, content) -> SentimentResult(polarity)

启用语义（宪法 §5.2：flag 出厂翻转=Owner 门位）：
    出厂默认关（规则法零变更）；Owner 创建 data/runtime/nightly_sentiment_llm.enabled
    即启用；删除标记即回退。启用后 analyzer 打分 method='llm'（异常行 'llm_fallback'），
    C6 成分对照期仍消费 rule 值——切换须待对照期结论+Owner 批。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 新闻标题/正文 + 旗标文件 data/runtime/nightly_sentiment_llm.enabled
# 层: 算法
# - id: A1
#   name_zh: LLM 打分器组装（旗标关→None=规则法零变更）
#   name_en: make_llm_scorer
#   intro: infer_sentiment × OllamaChat（LSG 经内置 lsg_gate）→ analyzer 级打分闭包
#   inputs: I1
#   outputs: 打分闭包（polarity 有向极性契约）
#   invariant: 构造失败降级 None 不阻断夜间批；单条异常→llm_fallback（既有契约）
# 层: 输出
# - id: O1
#   name: c1_market.news_sentiment_window 行 data_source='llm'（对照期，C6 仍消费 rule 值）
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from zephyr.nlp.nlp_inference import SentimentResult as _NLPResult
from zephyr.shared.io.paths import REPO_ROOT

if TYPE_CHECKING:
    from zephyr.integration.local_model.ollama_chat import OllamaChat

log = logging.getLogger(__name__)

__all__: list[str] = ["make_llm_scorer", "LLM_SCORER_FLAG"]

LLM_SCORER_FLAG = REPO_ROOT / "data" / "runtime" / "nightly_sentiment_llm.enabled"


def make_llm_scorer(
    flag_path: Path | None = None, backend: OllamaChat | None = None
) -> Callable[[str, str], _NLPResult] | None:
    """构造 analyzer 级 LLM 打分器（LLMSentimentScorer 协议）。

    Returns:
        旗标关闭（默认）→ None（调用方 analyzer=None 同款：规则法零变更）；
        旗标开启 → (title, content) -> nlp_inference.SentimentResult 闭包。
        构造异常 → log warning 返回 None（降级规则法，不阻断夜间批）。
    """
    flag = flag_path or LLM_SCORER_FLAG
    if not flag.exists():
        return None
    try:
        from zephyr.integration.local_model.ollama_chat import OllamaChat
        from zephyr.nlp.nlp_inference import infer_sentiment

        chat = backend if backend is not None else OllamaChat()
    except Exception as e:  # noqa: BLE001 — 降级契约：构造失败不阻断夜间批
        log.warning("news_llm_scorer 构造失败降级规则法: %s: %s", type(e).__name__, e)
        return None

    def _score(title: str, content: str = "") -> _NLPResult:
        return infer_sentiment(title, content, chat=chat)

    log.info("news_llm_scorer 已启用（旗标 %s）——夜间情绪 LLM 打分生效", flag.name)
    return _score
