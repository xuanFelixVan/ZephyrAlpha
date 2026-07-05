# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.cache_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/data_layer/test_cache_manager.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_cache_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Stage 0: 函数缓存管理器 — 增量扫描的加速核心.

职责：
  - 加载/保存 function-cache.json
  - 原子写入（.tmp → os.replace）防止写入中断损坏
  - _integrity SHA256 自检——加载时校验→损坏→自动全量重建
  - 增量更新：仅更新变更文件的函数条目
  - 全量重建：重新扫描所有源文件生成缓存
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class FunctionCacheEntry(BaseModel):
    id: str
    file: str
    name: str
    signature_fingerprint: str = ""
    ast_fingerprint: str = ""
    token_minhash: list[int] = Field(default_factory=list)
    loc_start: int = 0
    loc_end: int = 0
    loc_count: int = 0
    last_modified: str = ""
    intentional_duplicate: bool = False
    known_shared_equivalent: str = ""
    decorator_count: int = 0
    complexity: int = 0
    caller_count: int = 0
    category: str = ""


class CacheMetadata(BaseModel):
    generated_at: str = ""
    total_functions: int = 0
    last_full_scan: str = ""
    version: str = "1.0.0"
    _integrity: str = ""


class FunctionCache(BaseModel):
    cache_metadata: CacheMetadata = Field(default_factory=CacheMetadata)
    functions: list[FunctionCacheEntry] = Field(default_factory=list)


class CacheManager:
    """函数缓存管理器."""

    def __init__(self, cache_path: str | Path | None = None) -> None:
        if cache_path is None:
            cache_path = Path("data/cache/function-cache.json")
        self._cache_path = Path(cache_path)
        self._cache: FunctionCache | None = None
        self._index: dict[str, FunctionCacheEntry] = {}
        self._signature_index: dict[str, list[FunctionCacheEntry]] = {}

    # ── 公共 API ──────────────────────────────────────────────

    def load(self) -> FunctionCache:
        """加载缓存——含 _integrity 验证."""
        if not self._cache_path.exists():
            return self._rebuild_from_scratch()

        try:
            raw = self._cache_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, OSError):
            return self._rebuild_from_scratch()

        meta = data.get("cache_metadata", {})
        stored_hash = meta.get("_integrity", "")

        computed = self._compute_integrity(data)
        if stored_hash and stored_hash != computed:
            return self._rebuild_from_scratch()

        self._cache = FunctionCache(**data)
        self._rebuild_indices()
        return self._cache

    def save(self, cache: FunctionCache | None = None) -> str:
        """原子写入——先写 .tmp 再 os.replace."""
        if cache is not None:
            self._cache = cache
        if self._cache is None:
            return ""

        data = self._cache.model_dump()
        data["cache_metadata"]["_integrity"] = self._compute_integrity(data)
        data["cache_metadata"]["generated_at"] = datetime.now(UTC).isoformat()

        json_text = json.dumps(data, ensure_ascii=False, indent=2)

        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            suffix=".json",
            prefix="function_cache_",
            dir=str(self._cache_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json_text)
            tmp = Path(tmp_path)
            os.replace(str(tmp), str(self._cache_path))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        self._rebuild_indices()
        return data["cache_metadata"]["_integrity"]

    def incremental_update(
        self,
        added: list[FunctionCacheEntry],
        removed_ids: list[str] | None = None,
    ) -> None:
        """增量更新——添加新条目、移除过期条目."""
        if self._cache is None:
            self.load()
        if self._cache is None:
            self._cache = FunctionCache()

        removed = set(removed_ids or [])
        self._cache.functions = [f for f in self._cache.functions if f.id not in removed]
        for entry in added:
            self._cache.functions = [f for f in self._cache.functions if f.id != entry.id]
            self._cache.functions.append(entry)

        self._cache.cache_metadata.total_functions = len(self._cache.functions)
        self.save()

    def full_rebuild(self, entries: list[FunctionCacheEntry]) -> FunctionCache:
        """全量重建缓存."""
        self._cache = FunctionCache(
            cache_metadata=CacheMetadata(
                generated_at=datetime.now(UTC).isoformat(),
                total_functions=len(entries),
                last_full_scan=datetime.now(UTC).isoformat(),
                version="1.0.0",
            ),
            functions=entries,
        )
        self.save()
        return self._cache

    # ── 索引查询 ─────────────────────────────────────────────

    def get_by_id(self, func_id: str) -> FunctionCacheEntry | None:
        return self._index.get(func_id)

    def get_by_signature(self, fingerprint: str) -> list[FunctionCacheEntry]:
        return self._signature_index.get(fingerprint, [])

    @property
    def cache(self) -> FunctionCache | None:
        return self._cache

    # ── 内部方法 ─────────────────────────────────────────────

    def _rebuild_indices(self) -> None:
        self._index.clear()
        self._signature_index.clear()
        if self._cache is None:
            return
        for func in self._cache.functions:
            self._index[func.id] = func
            if func.signature_fingerprint:
                self._signature_index.setdefault(func.signature_fingerprint, []).append(func)

    def _rebuild_from_scratch(self) -> FunctionCache:
        """缓存损坏或不存在→返回空缓存（外部负责全量扫描填充）."""
        self._cache = FunctionCache(
            cache_metadata=CacheMetadata(
                generated_at=datetime.now(UTC).isoformat(),
                total_functions=0,
                last_full_scan="",
                version="1.0.0",
            ),
            functions=[],
        )
        self._index.clear()
        self._signature_index.clear()
        return self._cache

    @staticmethod
    def _compute_integrity(data: dict[str, Any]) -> str:
        stripped = {k: v for k, v in data.items() if k != "cache_metadata"}
        payload = json.dumps(stripped, ensure_ascii=False, sort_keys=True)
        return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"
