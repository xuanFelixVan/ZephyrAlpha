# [BLUEPRINT] MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.3
# [MODULE] zephyr.autonomy_core.embedding_provider_adapter
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.drift_semantic_reviewer; zephyr.integration.local_model.embedding_router（仅 CLI 实跑懒加载）; zephyr.intelligence.reflexion.batch_runner（is_intraday 盘中守卫口径复用，CLI 懒加载）
# [CONSUMERS] tests/autonomy/test_embedding_provider_adapter.py；手动 CLI（python -m zephyr.autonomy_core.embedding_provider_adapter）
# [STARTUP] manual（批量档 CLI/调度手动触发；适配器类本体 imported，可被外部跑批编排注入）
# [MATURITY] testing
# [INVARIANTS] 适配器仅转发嵌入调用不自带模型/网络/GPU; 批量 CLI 盘中零调用（工作日 09:30-15:00 CST 拒跑，复用 reflexion is_intraday 口径）; 复核产出=报告人审（status=pending_human_review，不自动处置）; 错误消息禁含 session_id
# [MODIFY-GUARD] Owner approval required; 集合/阈值口径变更须同步 15号文 §4.2 S1.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 输入/配置非法 → SemanticReviewError（复用 drift_semantic_reviewer 裸异常，禁自创前缀）; 嵌入后端异常不吞（fail-fast 交调用方）
# [TESTS] tests/autonomy/test_embedding_provider_adapter.py
# [A_module] module_id=MOD-AU-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



EmbeddingRouterAdapter — S1.3 语义复核嵌入设施桥接 + 批量档手动 CLI（15号文 §4.2 S1.3）.

设计真源：15号文 §3.2 / §4.2-S1.3：
- 深度语义复核走批量档（日/周频），嵌入模型不新造——本适配器把既有
  EmbeddingRouter（MOD-INF-042，双嵌入维度路由 + LSG 输入闸门 + in_memory 降级链）
  桥接为 drift_semantic_reviewer 的 EmbeddingProvider 注入协议。
- 集合口径：默认 decisions（BGE-M3 高维模型，意图/动作链语义对齐场景）；
  路由与降级链全部委托 EmbeddingRouter，本适配器零自有模型逻辑。
- 批量档手动 CLI：盘中零调用（复用 reflexion batch_runner 的 is_intraday 口径，
  工作日 09:30-15:00 CST 拒绝执行，返回码 3），调度挂点由外部编排负责。

用法::

    python -m zephyr.autonomy_core.embedding_provider_adapter         --sessions .runtime/drift_review/sessions.json         --report-dir .runtime/drift_review/reports --frequency weekly

sessions JSON 格式：[{"session_ref", "original_intent", "action_summary"}, ...]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: argv 参数
#   fields: 参数 argv，类型注解 list[str] | None
#   code: embedding_provider_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: at 参数
#   fields: 参数 at（无注解）
#   code: embedding_provider_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: provider 参数
#   fields: 参数 provider（无注解）
#   code: embedding_provider_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EmbeddingRouterAdapter
#   name_en: EmbeddingRouterAdapter
#   intro: EmbeddingProvider 协议适配器：把 EmbeddingRouter（MOD-INF-042）桥接给 S…
#   desc: EmbeddingProvider 协议适配器：把 EmbeddingRouter（MOD-INF-042）桥接给 S1.3 复核核. 首次嵌入调用时按需 warmup 一次（a…；公共方法（定义序）: collect…
#   inputs: router collection_name auto_warmup
#   outputs: 返回值
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: S1.3 批量档手动 CLI 入口。
#   desc: S1.3 批量档手动 CLI 入口。返回码：0 成功；2 输入/配置非法；3 盘中时段拒绝执行. Args: argv: CLI 参数（None → sys.argv）。 at:…；源码 L185-L244
#   inputs: argv at provider
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_embedding_provider_adapter.py；手动 CLI（python -m zephyr.auton…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Sequence

from zephyr.autonomy_core.drift_semantic_reviewer import (
    EmbeddingProvider,
    SemanticReviewConfig,
    SemanticReviewError,
    SessionChainReview,
    run_batch,
)

if TYPE_CHECKING:
    from zephyr.integration.local_model.embedding_router import EmbeddingRouterProtocol

logger = logging.getLogger(__name__)

#: S1.3 复核默认嵌入集合（BGE-M3 路由——意图/动作链语义对齐用高维模型）
DEFAULT_COLLECTION: Final[str] = "decisions"

_SESSION_FIELDS: Final = ("session_ref", "original_intent", "action_summary")


class EmbeddingRouterAdapter:
    """EmbeddingProvider 协议适配器：把 EmbeddingRouter（MOD-INF-042）桥接给 S1.3 复核核.

    首次嵌入调用时按需 warmup 一次（auto_warmup=True）；双模型均不可用时经
    EmbeddingRouter 既有降级链进入 in_memory 零向量兜底——复核核余弦 fail-safe
    为 0.0，全部会话 flagged 人审（宁多报人审不放过，与复核核零向量口径一致）。
    """

    def __init__(
        self,
        router: EmbeddingRouterProtocol,
        *,
        collection_name: str = DEFAULT_COLLECTION,
        auto_warmup: bool = True,
    ) -> None:
        if not collection_name.strip():
            raise SemanticReviewError("collection_name 禁空")
        self._router = router
        self._collection_name = collection_name.strip()
        self._auto_warmup = auto_warmup
        self._warmed = False

    @property
    def collection_name(self) -> str:
        """嵌入路由集合名（只读）。"""
        return self._collection_name

    def _ensure_warmup(self) -> None:
        """按需预热一次：双模型均未就绪且未进 in_memory 降级时调 router.warmup()。"""
        if self._warmed or not self._auto_warmup:
            return
        self._warmed = True
        if (
            not self._router.bge_m3_available
            and not self._router.bge_small_available
            and self._router.fallback_mode != "in_memory"
        ):
            self._router.warmup()

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """EmbeddingProvider 协议实现：批量文本 → list[list[float]]（全部同维）。"""
        items = [str(t) for t in texts]
        if not items:
            return []
        self._ensure_warmup()
        matrix = self._router.embed_batch(items, self._collection_name)
        rows = matrix.tolist() if hasattr(matrix, "tolist") else matrix
        return [[float(x) for x in row] for row in rows]


def _load_sessions(path: Path) -> list[SessionChainReview]:
    """加载会话复核清单 JSON（[{session_ref, original_intent, action_summary}]）。"""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SemanticReviewError(f"会话清单读取/解析失败: {exc!r}") from exc
    if not isinstance(raw, list):
        raise SemanticReviewError("会话清单须为 JSON 数组")
    sessions: list[SessionChainReview] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict) or not all(
            isinstance(item.get(k), str) and item.get(k).strip() for k in _SESSION_FIELDS
        ):
            raise SemanticReviewError(f"会话清单第 {i} 项非法（须含非空字符串字段 {'/'.join(_SESSION_FIELDS)}）")
        sessions.append(
            SessionChainReview(
                session_ref=item["session_ref"].strip(),
                original_intent=item["original_intent"],
                action_summary=item["action_summary"],
            )
        )
    return sessions


def main(
    argv: list[str] | None = None,
    *,
    at: datetime | None = None,
    provider: EmbeddingProvider | None = None,
) -> int:
    """S1.3 批量档手动 CLI 入口。返回码：0 成功；2 输入/配置非法；3 盘中时段拒绝执行.

    Args:
        argv: CLI 参数（None → sys.argv）。
        at: 执行时刻注入（测试用；None → 当前时刻，交 is_intraday 自取）。
        provider: 嵌入提供者注入（测试/外部编排用；None → 实装 EmbeddingRouter 适配器）。
    """
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.autonomy_core.embedding_provider_adapter",
        description="S1.3 Agentic Drift 深度语义复核批量档（盘中 09:30-15:00 CST 拒绝执行）",
    )
    parser.add_argument(
        "--sessions",
        required=True,
        help="会话复核清单 JSON（[{session_ref, original_intent, action_summary}]）",
    )
    parser.add_argument("--report-dir", required=True, help="复核报告落盘目录")
    parser.add_argument("--frequency", choices=("daily", "weekly"), default="weekly")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="嵌入路由集合名")
    parser.add_argument("--similarity-threshold", type=float, default=0.6)
    parser.add_argument("--backend", choices=("ollama", "local"), default="ollama")
    args = parser.parse_args(argv)

    # 盘中零调用守卫（15号文约束二：批量复核避开交易时段与 GPU 高峰）——
    # 口径复用 zephyr.intelligence.reflexion.batch_runner.is_intraday，不另造。
    from zephyr.intelligence.reflexion.batch_runner import is_intraday

    if is_intraday(at):
        print(
            "[盘中禁跑] S1.3 语义复核为日/周频批量档，工作日 09:30-15:00 CST 拒绝执行（15号文 §3.2/约束二）",
            file=sys.stderr,
        )
        return 3

    try:
        sessions = _load_sessions(Path(args.sessions))
        config = SemanticReviewConfig(similarity_threshold=args.similarity_threshold, frequency=args.frequency)
        config.validate()
    except SemanticReviewError as exc:
        print(f"[输入非法] {exc}", file=sys.stderr)
        return 2

    embedder: Any = provider
    if embedder is None:
        from zephyr.integration.local_model.embedding_router import EmbeddingRouter

        embedder = EmbeddingRouterAdapter(EmbeddingRouter(backend=args.backend), collection_name=args.collection)

    report, name = run_batch(sessions, embedder, args.report_dir, config)
    print(
        f"[S1.3] 复核完成：{report.n_sessions} 会话，疑似漂移 {len(report.flagged)} "
        f"（status={report.status}）→ {name or '(落盘失败，报告仅内存回传)'}"
    )
    return 0


__all__: Final = [
    "DEFAULT_COLLECTION",
    "EmbeddingRouterAdapter",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
