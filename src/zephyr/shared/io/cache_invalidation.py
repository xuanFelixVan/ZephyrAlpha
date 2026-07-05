# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.io.cache_invalidation
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_cache_invalidation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""cache_invalidation.py — 缓存一致性 (DD113, TASK-020)"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

UTC = UTC


@dataclass
class CacheVersion:
    key: str
    version: int
    invalidated_at: str


class CacheInvalidationManager:
    """Mem/Redis 缓存 + event-driven KE update → cache invalidation (DD113).

    提供：
    - 自动失效：set_version 时自动调用已注册的失效回调
    - 回调注册：register_invalidation_handler 供数据更新组件订阅失效事件
    - 持久化：版本数据持久化到 JSON 文件，重启后恢复
    """

    def __init__(self, persistence_path: str | Path | None = None) -> None:
        self._versions: dict[str, CacheVersion] = {}
        self._handlers: dict[str, list[Callable[[str, int], None]]] = {}
        self._persistence_path = Path(persistence_path) if persistence_path else None
        if self._persistence_path and self._persistence_path.exists():
            self._load_from_disk()

    def set_version(self, key: str, version: int) -> CacheVersion:
        cv = CacheVersion(key=key, version=version, invalidated_at=datetime.now(UTC).isoformat())
        self._versions[key] = cv
        self._persist()
        self._notify_handlers(key, version)
        return cv

    def bump_version(self, key: str) -> CacheVersion:
        """自动递增版本号——数据更新组件调用此方法触发自动失效."""
        current = self._versions.get(key)
        next_version = (current.version + 1) if current else 1
        return self.set_version(key, next_version)

    def check_staleness(self, key: str, client_version: int) -> bool:
        cv = self._versions.get(key)
        return cv is not None and cv.version > client_version

    def register_invalidation_handler(
        self, key: str, handler: Callable[[str, int], None]
    ) -> None:
        """注册失效回调——当 key 的版本被更新（set_version/bump_version）时自动调用。

        允许数据更新组件订阅缓存失效事件，实现数据更新→缓存自动失效。
        """
        self._handlers.setdefault(key, []).append(handler)

    # ── 内部方法 ─────────────────────────────────────────────

    def _notify_handlers(self, key: str, version: int) -> None:
        for handler in self._handlers.get(key, []):
            try:
                handler(key, version)
            except Exception:
                # 回调失败不应影响版本更新主流程
                pass

    def _load_from_disk(self) -> None:
        """从 JSON 文件恢复版本数据，重启后保持一致性."""
        try:
            data = json.loads(self._persistence_path.read_text(encoding="utf-8"))
            for key, entry in data.items():
                self._versions[key] = CacheVersion(
                    key=key,
                    version=entry.get("version", 0),
                    invalidated_at=entry.get("invalidated_at", ""),
                )
        except (json.JSONDecodeError, OSError):
            pass

    def _persist(self) -> None:
        """持久化版本数据到 JSON 文件."""
        if self._persistence_path is None:
            return
        data = {
            k: {"version": v.version, "invalidated_at": v.invalidated_at}
            for k, v in self._versions.items()
        }
        try:
            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            self._persistence_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError:
            pass
