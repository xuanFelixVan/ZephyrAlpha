# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 7
# [MODULE] zephyr.nlp.research_rating
# [DOMAIN] D_DATA
# [DEPENDENCIES] (纯函数零依赖)
# [CONSUMERS] scripts.ml.run_research_rating_batch
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 规则优先——评级/机构/行业从 summary 结构化字段提取（覆盖率实证 92.1%/100%）；评级映射表唯一真源在本模块；LLM 补位（目标价/盈利修正细节）属后续阶段；未知评级 score=None 不猜值
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常——解析失败字段为空/None，不抛
# [TESTS] tests/nlp/test_research_rating.py
# [TTL] permanent
"""research_rating — 研报结构化评级提取（CAND-NLP-006）。

研报的机构级信号不在通用情感分（卖方多头偏见：实证 买入69%+增持22%=91%），
而在结构化字段（朝阳永续/Wind 一致预期口径）：

- **评级本身**：summary ``评级:X`` → 静态立场分（``RATING_SCORE`` 唯一真源）
- **评级变动**：标题关键词（首次覆盖/上调/下调/维持）→ 边际信息（最强信号）
- **目标价**：标题/内容 ``目标价 X 元`` → 预期幅度锚（覆盖率低，可选字段）

Version: 0.1.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

# ── 评级 → 立场分（唯一真源；未知评级不在表内 → score=None 不猜值）──
RATING_SCORE: Final[dict[str, float]] = {
    "买入": 1.0,
    "强烈推荐": 1.0,
    "推荐": 0.8,
    "增持": 0.6,
    "谨慎推荐": 0.5,
    "持有": 0.2,
    "中性": 0.0,
    "减持": -0.6,
    "卖出": -1.0,
    "回避": -1.0,
}

# ── summary 结构化字段（"机构:X | 评级:Y | 行业:Z"，akshare_provider 写入口径）──
_FIELD_RE = re.compile(r"(机构|评级|行业):([^|]+)")

# ── 标题评级变动模式（顺序敏感：先判首次覆盖/下调/上调，再判维持）──
_INITIATION_RE = re.compile(r"首次覆盖|首次给予|首覆")
_DOWNGRADE_RE = re.compile(r"下调")
_UPGRADE_RE = re.compile(r"上调")
_MAINTAIN_RE = re.compile(r"维持")
_TARGET_PRICE_RE = re.compile(r"目标价[：:至为]?\s*(\d+(?:\.\d+)?)\s*元")

REVISION_INITIATION: Final[str] = "initiation"  # 首次覆盖
REVISION_UPGRADE: Final[str] = "upgrade"  # 上调（评级/目标价/盈利预测）
REVISION_DOWNGRADE: Final[str] = "downgrade"  # 下调
REVISION_MAINTAIN: Final[str] = "maintain"  # 维持
REVISION_NONE: Final[str] = "none"  # 无显式标记


@dataclass(frozen=True, slots=True)
class ReportRating:
    """单篇研报的结构化评级提取结果。

    org          : 机构名（summary 机构字段，空串=缺失）
    industry     : 行业名（summary 行业字段）
    rating       : 评级原文（买入/增持/...，空串=缺失）
    score        : 立场分（RATING_SCORE 映射；未知/缺失=None）
    revision     : initiation/upgrade/downgrade/maintain/none（标题判定）
    revision_detail : 变动细节原文片段（如"下调盈利预测及目标价"截取，调试用）
    target_price : 目标价（元；未提取到=None）
    """

    org: str
    industry: str
    rating: str
    score: float | None
    revision: str
    revision_detail: str
    target_price: float | None


def parse_summary_fields(summary: str) -> dict[str, str]:
    """解析 summary 的 机构/评级/行业 三个结构化字段（缺失则键不存在）。"""
    return {m.group(1): m.group(2).strip() for m in _FIELD_RE.finditer(summary or "")}


def rating_score(rating: str) -> float | None:
    """评级原文 → 立场分；未知/缺失 → None（不猜值）。"""
    return RATING_SCORE.get((rating or "").strip())


def detect_revision(title: str) -> tuple[str, str]:
    """标题 → (变动类型, 细节片段)。

    顺序敏感：首次覆盖 > 下调 > 上调 > 维持 > none。
    细节片段=命中关键词起最多 20 字（如"下调盈利预测及目标价"），调试用。
    """
    t = title or ""
    for rev, rex in (
        (REVISION_INITIATION, _INITIATION_RE),
        (REVISION_DOWNGRADE, _DOWNGRADE_RE),
        (REVISION_UPGRADE, _UPGRADE_RE),
        (REVISION_MAINTAIN, _MAINTAIN_RE),
    ):
        m = rex.search(t)
        if m:
            return rev, t[m.start() : m.start() + 20]
    return REVISION_NONE, ""


def extract_target_price(text: str) -> float | None:
    """标题/内容提取目标价（"目标价 58.5 元"形态；未命中 → None）。"""
    m = _TARGET_PRICE_RE.search(text or "")
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def analyze_report(title: str, summary: str) -> ReportRating:
    """单篇研报全字段提取（组合 parse_summary_fields/detect_revision/extract_target_price）。"""
    fields = parse_summary_fields(summary)
    rating = fields.get("评级", "")
    revision, detail = detect_revision(title)
    return ReportRating(
        org=fields.get("机构", ""),
        industry=fields.get("行业", ""),
        rating=rating,
        score=rating_score(rating),
        revision=revision,
        revision_detail=detail,
        target_price=extract_target_price(f"{title} {summary}"),
    )


__all__: Final = [
    "RATING_SCORE",
    "REVISION_DOWNGRADE",
    "REVISION_INITIATION",
    "REVISION_MAINTAIN",
    "REVISION_NONE",
    "REVISION_UPGRADE",
    "ReportRating",
    "analyze_report",
    "detect_revision",
    "extract_target_price",
    "parse_summary_fields",
    "rating_score",
]
