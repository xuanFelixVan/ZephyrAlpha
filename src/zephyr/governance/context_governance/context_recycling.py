# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_recycling
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_context_recycling | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
        except Exception as exc:
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