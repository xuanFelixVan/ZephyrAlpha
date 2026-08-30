# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_recycling
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md;src/zephyr/governance/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_recycling.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextRecycling
#   name_en: ContextRecycling
#   intro: class ContextRecycling 源码 L76-L152
#   desc: 公共方法（定义序）: compress, restore, store, purge, list_sessions, stats, export_json, import_json；源码 L76-L152
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextRecycling
#   downstream: MOD-INF-020;MOD-INF-018;MOD-INF-027
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import logging
import zlib
from datetime import UTC, datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CompressedContext(BaseModel):
    session_id: str
    compressed_at: str
    origin_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    key_topics: list[str] = Field(default_factory=list)
    summary_text: str = ""
    data: str = ""

    @property
    def is_valid(self) -> bool:
        return bool(self.data) and self.compression_ratio < 1.0


class ContextRecycling:
    def __init__(self) -> None:
        self._store: dict[str, CompressedContext] = {}

    def compress(
        self,
        session_id: str,
        content: str,
        key_topics: list[str] | None = None,
    ) -> CompressedContext:
        raw_bytes = content.encode("utf-8")
        compressed = zlib.compress(raw_bytes, level=9)
        ratio = len(compressed) / max(len(raw_bytes), 1)

        ctx = CompressedContext(
            session_id=session_id,
            compressed_at=datetime.now(UTC).isoformat(),
            origin_size_bytes=len(raw_bytes),
            compressed_size_bytes=len(compressed),
            compression_ratio=round(ratio, 4),
            key_topics=key_topics or [],
            summary_text=content[:200] if len(content) > 200 else content,
            data=compressed.hex(),
        )
        self._store[session_id] = ctx
        logger.info(
            "ContextRecycling: session=%s ratio=%.2f%% topics=%s",
            session_id,
            ratio * 100,
            key_topics,
        )
        return ctx

    def restore(self, session_id: str) -> str | None:
        ctx = self._store.get(session_id)
        if ctx is None or not ctx.data:
            logger.warning("ContextRecycling: no data for session=%s", session_id)
            return None
        try:
            decompressed = zlib.decompress(bytes.fromhex(ctx.data))
            return decompressed.decode("utf-8")
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("ContextRecycling restore failed for %s: %s", session_id, exc, exc_info=True)
            return None

    def store(self, session_id: str) -> CompressedContext | None:
        return self._store.get(session_id)

    def purge(self, session_id: str) -> bool:
        return self._store.pop(session_id, None) is not None

    def list_sessions(self) -> list[str]:
        return sorted(self._store.keys())

    def stats(self) -> dict[str, object]:
        total_orig = sum(c.origin_size_bytes for c in self._store.values())
        total_comp = sum(c.compressed_size_bytes for c in self._store.values())
        return {
            "session_count": len(self._store),
            "total_origin_bytes": total_orig,
            "total_compressed_bytes": total_comp,
            "overall_ratio": round(total_comp / max(total_orig, 1), 4),
        }

    def export_json(self, file_path: str) -> None:
        data = {sid: ctx.model_dump() for sid, ctx in self._store.items()}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_json(self, file_path: str) -> int:
        with open(file_path, encoding="utf-8") as f:
            raw = json.load(f)
        count = 0
        for sid, d in raw.items():
            self._store[sid] = CompressedContext(**d)
            count += 1
        return count
