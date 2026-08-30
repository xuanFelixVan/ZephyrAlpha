# [BLUEPRINT] MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.3
# [MODULE] zephyr.autonomy_core.drift_semantic_reviewer
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] 无仓内硬依赖（嵌入模型经 EmbeddingProvider 协议注入，禁真调模型）
# [CONSUMERS] tests/autonomy_core/test_drift_semantic_reviewer.py；外部跑批编排（日/周频调度）
# [STARTUP] event_driven
# [MATURITY] testing
# [INVARIANTS] 嵌入模型仅经注入接口调用（本模块永不自调真实模型/网络/GPU）; 复核产出=报告人审（status=pending_human_review，不自动处置）; 跑批避开交易时段与 GPU 高峰（约束二，由外部编排保证）; 错误消息禁含 session_id
# [MODIFY-GUARD] Owner approval required; 阈值口径变更须同步 15号文 §4.2 S1.3 与 Q2 关联记录
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SemanticReviewError（裸异常——ZA-AU 前缀未在 error_code_registry 声明，沿域先例 MOD-AU-002 同款，禁自创前缀）; run_batch 落盘 IO 失败不阻断报告回传
# [TESTS] tests/autonomy_core/test_drift_semantic_reviewer.py
# [A_module] module_id=MOD-AU-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
# [ALGO_FLOW]
# I1: Sequence[SessionChainReview]（原始任务意图 + 当前动作链摘要）；I2: EmbeddingProvider（注入）
# F1: 批量嵌入（意图 vs 动作链摘要成对）→ F2: 余弦相似度 < threshold 判疑似意图偏差 → F3: 汇总复核报告
# O1: SemanticReviewReport（pending_human_review）；O2: drift_semantic_review-<report_id>.json 落盘
# [/ALGO_FLOW]
"""


DriftSemanticReviewer — Agentic Drift 深度语义复核批量件（MOD-AU-003，15号文 §4.2 S1.3）.

设计真源：15号文（15_autonomy_boundary_risk.md）§3.2 / §4.2-S1.3：
- 意图偏差度的语义维度（双维度阈值第二维）走批量档：日频/周频对会话操作链做嵌入相似度
  复核（当前动作链 vs 原始任务意图），避开交易时段与 GPU 高峰（约束二——单机不与交易/
  回测抢显存；实时档只做操作链内联检查，见 agentic_drift_guard.py）。
- 产出漂移报告落盘人审（status=pending_human_review），误报率阈值人定（15号文 Q2 关联）。
- 嵌入模型为接口位注入（EmbeddingProvider 协议），测试注入 mock，本模块永不自调真实模型。

跑批骨架：外部编排（日/周频调度器）收集会话操作链摘要 → 调 run_batch/review_sessions →
报告 JSON 落盘 → 人审抽样评估误报率。本模块只提供复核核与报告结构，不含调度器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: a 参数
#   fields: 参数 a，类型注解 Sequence[float]
#   code: drift_semantic_reviewer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: b 参数
#   fields: 参数 b，类型注解 Sequence[float]
#   code: drift_semantic_reviewer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: sessions 参数
#   fields: 参数 sessions，类型注解 Sequence[SessionChainReview]
#   code: drift_semantic_reviewer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: embedder 参数
#   fields: 参数 embedder，类型注解 EmbeddingProvider
#   code: drift_semantic_reviewer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EmbeddingProvider
#   name_en: EmbeddingProvider
#   intro: 嵌入模型注入协议（实现方：真实模型适配器 / 测试 mock；本模块不自带实现）。
#   desc: 嵌入模型注入协议（实现方：真实模型适配器 / 测试 mock；本模块不自带实现）。；公共方法（定义序）: embed；源码 L154-L159
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SemanticReviewConfig
#   name_en: SemanticReviewConfig
#   intro: 复核参数（similarity_threshold 人定，15号文 Q2 关联；frequency=daily/wee…
#   desc: 复核参数（similarity_threshold 人定，15号文 Q2 关联；frequency=daily/weekly）。；公共方法（定义序）: validate；源码 L172-L185
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ SemanticReviewReport
#   name_en: SemanticReviewReport
#   intro: 日/周频复核报告（人审载体，不自动处置）。
#   desc: 日/周频复核报告（人审载体，不自动处置）。；公共方法（定义序）: to_dict；源码 L198-L227
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ cosine_similarity
#   name_en: cosine_similarity
#   intro: 余弦相似度；零向量 → 0.0（fail-safe，不放大为相似）。
#   desc: 余弦相似度；零向量 → 0.0（fail-safe，不放大为相似）。；源码 L230-L237
#   inputs: a b
#   outputs: float
# - id: A5
#   name_zh: ⑤ review_sessions
#   name_en: review_sessions
#   intro: S1.3 复核核：批量嵌入 + 成对余弦相似度比对（当前动作链 vs 原始任务意图）。
#   desc: S1.3 复核核：批量嵌入 + 成对余弦相似度比对（当前动作链 vs 原始任务意图）。 相似度 < similarity_threshold → 疑似意图偏差，收入 flagge…；源码 L244-L300
#   inputs: sessions embedder config
#   outputs: SemanticReviewReport
# - id: A6
#   name_zh: ⑥ run_batch
#   name_en: run_batch
#   intro: 日/周频跑批骨架：复核 + 报告 JSON 落盘，返回 (报告, 文件名)。
#   desc: 日/周频跑批骨架：复核 + 报告 JSON 落盘，返回 (报告, 文件名)。 调度（日/周频、避开交易时段与 GPU 高峰）由外部编排负责；本函数不含调度逻辑。 落盘 IO 失败…；源码 L303-L323
#   inputs: sessions embedder report_dir config
#   outputs: tuple[SemanticReviewReport, str]
# - id: A7
#   name_zh: ⑦ SemanticReviewer
#   name_en: SemanticReviewer
#   intro: S1.3 类封装：注入 embedder + report_dir 的复核器（等价函数入口的持有型形态）。
#   desc: S1.3 类封装：注入 embedder + report_dir 的复核器（等价函数入口的持有型形态）。；公共方法（定义序）: review, run_batch；源码 L326-L345
#   inputs: embedder report_dir config
#   outputs: 返回值
#   （注：A7 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy_core/test_drift_semantic_reviewer.py；外部跑批编排（日/周频调度）
# - id: O2
#   name_zh: SemanticReviewReport
#   name_en: SemanticReviewReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy_core/test_drift_semantic_reviewer.py；外部跑批编排（日/周频调度）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import json
import logging
import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Protocol, Sequence, runtime_checkable

logger = logging.getLogger(__name__)

SCHEMA_VERSION: Final[str] = "1.0"
_EPS: Final[float] = 1e-12


class SemanticReviewError(Exception):
    """配置/输入/嵌入向量非法（裸异常——ZA-AU 前缀未声明，沿 MOD-AU-002 域先例）。消息禁含 session_id。"""


@runtime_checkable
class EmbeddingProvider(Protocol):
    """嵌入模型注入协议（实现方：真实模型适配器 / 测试 mock；本模块不自带实现）。"""

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """批量嵌入：len(返回) 须等于 len(texts)，且全部向量同维。"""
        ...


@dataclass(frozen=True)
class SessionChainReview:
    """单会话复核输入（原始任务意图 + 当前动作链摘要文本）。"""

    session_ref: str
    original_intent: str
    action_summary: str


@dataclass(frozen=True)
class SemanticReviewConfig:
    """复核参数（similarity_threshold 人定，15号文 Q2 关联；frequency=daily/weekly）。"""

    similarity_threshold: float = 0.6
    frequency: str = "weekly"
    max_text_chars: int = 4000

    def validate(self) -> None:
        if not 0.0 < self.similarity_threshold < 1.0:
            raise SemanticReviewError(f"similarity_threshold 须落在 (0,1): {self.similarity_threshold}")
        if self.frequency not in ("daily", "weekly"):
            raise SemanticReviewError(f"frequency 须为 daily/weekly: {self.frequency}")
        if self.max_text_chars < 16:
            raise SemanticReviewError(f"max_text_chars 须 >= 16: {self.max_text_chars}")


@dataclass(frozen=True)
class FlaggedSession:
    """疑似意图偏差会话（相似度低于阈值，待人审裁定误报与否）。"""

    session_ref: str
    similarity: float
    reason: str


@dataclass(frozen=True)
class SemanticReviewReport:
    """日/周频复核报告（人审载体，不自动处置）。"""

    report_id: str
    frequency: str
    generated_at: str
    n_sessions: int
    similarity_threshold: float
    flagged: tuple[FlaggedSession, ...]
    status: str = "pending_human_review"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "report_id": self.report_id,
            "report_type": "agentic_drift_semantic_review",
            "frequency": self.frequency,
            "generated_at": self.generated_at,
            "n_sessions": self.n_sessions,
            "similarity_threshold": self.similarity_threshold,
            "status": self.status,
            "flagged": [
                {
                    "session_ref": f.session_ref,
                    "similarity": f.similarity,
                    "reason": f.reason,
                }
                for f in self.flagged
            ],
        }


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """余弦相似度；零向量 → 0.0（fail-safe，不放大为相似）。"""
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a < _EPS or norm_b < _EPS:
        return 0.0
    return dot / (norm_a * norm_b)


def _truncate(text: str, max_chars: int) -> str:
    return text[:max_chars]


def review_sessions(
    sessions: Sequence[SessionChainReview],
    embedder: EmbeddingProvider,
    config: SemanticReviewConfig | None = None,
) -> SemanticReviewReport:
    """S1.3 复核核：批量嵌入 + 成对余弦相似度比对（当前动作链 vs 原始任务意图）。

    相似度 < similarity_threshold → 疑似意图偏差，收入 flagged 待人审。
    嵌入模型仅经 embedder 注入接口调用；向量维度不齐/数量不符 → SemanticReviewError。
    """
    cfg = config or SemanticReviewConfig()
    cfg.validate()
    if not sessions:
        return SemanticReviewReport(
            report_id=uuid.uuid4().hex[:12],
            frequency=cfg.frequency,
            generated_at=datetime.now(UTC).isoformat(),
            n_sessions=0,
            similarity_threshold=cfg.similarity_threshold,
            flagged=(),
        )

    texts: list[str] = []
    for s in sessions:
        texts.append(_truncate(s.original_intent, cfg.max_text_chars))
        texts.append(_truncate(s.action_summary, cfg.max_text_chars))
    vectors = embedder.embed(texts)
    if len(vectors) != len(texts):
        raise SemanticReviewError(f"嵌入向量数量 {len(vectors)} 与输入文本数量 {len(texts)} 不符")
    dims = {len(v) for v in vectors}
    if len(dims) != 1:
        raise SemanticReviewError("嵌入向量维度不齐（全部向量须同维）")

    flagged: list[FlaggedSession] = []
    for i, s in enumerate(sessions):
        similarity = cosine_similarity(vectors[2 * i], vectors[2 * i + 1])
        if similarity < cfg.similarity_threshold:
            flagged.append(
                FlaggedSession(
                    session_ref=s.session_ref,
                    similarity=similarity,
                    reason=(
                        f"动作链与原始意图嵌入相似度={similarity:.3f} < "
                        f"{cfg.similarity_threshold}（疑似意图偏差，待人审）"
                    ),
                )
            )
    if flagged:
        logger.warning("S1.3 语义复核疑似漂移 %d/%d 会话（待人审）", len(flagged), len(sessions))
    return SemanticReviewReport(
        report_id=uuid.uuid4().hex[:12],
        frequency=cfg.frequency,
        generated_at=datetime.now(UTC).isoformat(),
        n_sessions=len(sessions),
        similarity_threshold=cfg.similarity_threshold,
        flagged=tuple(flagged),
    )


def run_batch(
    sessions: Sequence[SessionChainReview],
    embedder: EmbeddingProvider,
    report_dir: str | Path,
    config: SemanticReviewConfig | None = None,
) -> tuple[SemanticReviewReport, str]:
    """日/周频跑批骨架：复核 + 报告 JSON 落盘，返回 (报告, 文件名)。

    调度（日/周频、避开交易时段与 GPU 高峰）由外部编排负责；本函数不含调度逻辑。
    落盘 IO 失败不阻断报告回传（文件名返回空串，仅 logger.warning）。
    """
    report = review_sessions(sessions, embedder, config)
    name = f"drift_semantic_review-{report.report_id}.json"
    try:
        out_dir = Path(report_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / name).write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.warning("S1.3 复核报告落盘失败（报告仍回传）: %r", exc)
        return report, ""
    return report, name


class SemanticReviewer:
    """S1.3 类封装：注入 embedder + report_dir 的复核器（等价函数入口的持有型形态）。"""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        report_dir: str | Path,
        config: SemanticReviewConfig | None = None,
    ) -> None:
        self._embedder = embedder
        self._report_dir = Path(report_dir)
        self._config = config or SemanticReviewConfig()

    def review(self, sessions: Sequence[SessionChainReview]) -> SemanticReviewReport:
        """只复核不落盘。"""
        return review_sessions(sessions, self._embedder, self._config)

    def run_batch(self, sessions: Sequence[SessionChainReview]) -> tuple[SemanticReviewReport, str]:
        """复核 + 报告落盘（report_dir 为初始化注入）。"""
        return run_batch(sessions, self._embedder, self._report_dir, self._config)


__all__: Final = [
    "SCHEMA_VERSION",
    "EmbeddingProvider",
    "FlaggedSession",
    "SemanticReviewConfig",
    "SemanticReviewError",
    "SemanticReviewReport",
    "SemanticReviewer",
    "SessionChainReview",
    "cosine_similarity",
    "review_sessions",
    "run_batch",
]
