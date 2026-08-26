# [BLUEPRINT] MOD-INF-091 | docs/03_modules/_domain_infrastructure_operations/config_center/blueprint.md
# [MODULE] zephyr.infrastructure.config.config_center
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] 无（纯内存注册表；audit_sink/guard/clock 全注入）
# [CONSUMERS] 运行时装配批（配置注册与热更新装配 / 审计路由 / 热更新守卫钩子绑定）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] key 唯一注册; 每次 set/rollback version 严格递增+快照留存; set/rollback 前 guard 校验拒绝即 Fail-Closed; 变更审计逐条留痕; list_versions 确定性升序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/config_center/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ConfigCenterError(占位 ZA-INF-UNREGISTERED-CONFIG-CENTER)——空key/重复注册/未知key/未知版本/守卫拒绝时抛
# [TESTS] tests/infrastructure/test_config_center.py
# [A_module] module_id=MOD-INF-091 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ConfigCenter — 统一配置中心（MOD-INF-091）。

B1-00203（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRASTR-001，C2）：统
一配置注册表（内存后端）+ 参数版本快照（每次变更 version 递增 + 快照
留存）+ 变更审计日志（注入 audit_sink 回调）+ 回滚 API（按版本回退，
回滚本身亦生成新版本）+ 热更新守卫语义（set/rollback 前经注入 guard
钩子校验，拒绝即 Fail-Closed）。Nacos/Apollo 单机化，不触网。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ConfigCenter",
    "ConfigCenterError",
    "ConfigChange",
    "ConfigVersion",
]


class ConfigCenterError(Exception):
    """配置中心输入/守卫非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-CONFIG-CENTER。
    """


@dataclass(frozen=True)
class ConfigVersion:
    """单 key 单版本快照（frozen）。"""

    key: str
    version: int
    value: Any
    meta: dict
    at: datetime.datetime


@dataclass(frozen=True)
class ConfigChange:
    """变更审计载荷（frozen）。"""

    key: str
    kind: str  # "register" | "set" | "rollback"
    from_version: int | None
    to_version: int
    at: datetime.datetime
    meta: dict = field(default_factory=dict)


class ConfigCenter:
    """统一配置中心件（注册表 + 版本快照 + 审计 + 回滚 + 守卫）。"""

    def __init__(
        self,
        *,
        audit_sink: Callable[[ConfigChange], None] | None = None,
        guard: Callable[[str, Any, Any], bool] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._audit_sink = audit_sink
        self._guard = guard
        self._clock = clock or datetime.datetime.now
        self._history: dict[str, dict[int, ConfigVersion]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_key(self, key: str) -> None:
        if not key:
            raise ConfigCenterError("key 为空")

    def _require_registered(self, key: str) -> dict[int, ConfigVersion]:
        versions = self._history.get(key)
        if versions is None:
            raise ConfigCenterError(f"未知 key: {key!r}（未注册）")
        return versions

    def _check_guard(self, key: str, old_value: Any, new_value: Any) -> None:
        if self._guard is None:
            return
        try:
            ok = bool(self._guard(key, old_value, new_value))
        except Exception as exc:  # noqa: BLE001 — 守卫异常按拒绝处理
            _log.exception("guard 校验异常: %s", key)
            raise ConfigCenterError(f"guard 校验异常（Fail-Closed）: {key!r}") from exc
        if not ok:
            raise ConfigCenterError(f"guard 拒绝变更（Fail-Closed）: {key!r}")

    def _commit(self, key: str, value: Any, meta: Mapping | None, kind: str) -> int:
        versions = self._history.setdefault(key, {})
        next_version = (max(versions) + 1) if versions else 1
        snap = ConfigVersion(
            key=key,
            version=next_version,
            value=value,
            meta=dict(meta or {}),
            at=self._clock(),
        )
        versions[next_version] = snap
        change = ConfigChange(
            key=key,
            kind=kind,
            from_version=(next_version - 1) if next_version > 1 else None,
            to_version=next_version,
            at=snap.at,
            meta=dict(meta or {}),
        )
        _log.info("配置变更: %s %s -> v%d", key, kind, next_version)
        if self._audit_sink is not None:
            try:
                self._audit_sink(change)
            except Exception:  # noqa: BLE001 — 审计回调不阻断主路
                _log.exception("audit_sink 留痕失败")
        return next_version

    # ── 注册与变更 ────────────────────────────────────────────────────────

    def register(self, key: str, value: Any, meta: Mapping | None = None) -> int:
        """注册 key（版本 1）：重复注册 → Fail-Closed。"""
        self._require_key(key)
        if key in self._history:
            raise ConfigCenterError(f"key 重复注册: {key!r}")
        return self._commit(key, value, meta, "register")

    def set(self, key: str, value: Any, meta: Mapping | None = None) -> int:
        """变更：未知 key → Fail-Closed；guard 拒绝 → Fail-Closed；版本递增。"""
        self._require_key(key)
        versions = self._require_registered(key)
        old_value = versions[max(versions)].value
        self._check_guard(key, old_value, value)
        return self._commit(key, value, meta, "set")

    # ── 回滚 ─────────────────────────────────────────────────────────────

    def rollback(self, key: str, to_version: int) -> int:
        """按版本回退：回滚亦生成新版本（守卫同 set 校验）。"""
        self._require_key(key)
        versions = self._require_registered(key)
        target = versions.get(to_version)
        if target is None:
            raise ConfigCenterError(f"未知版本: {key!r} v{to_version}")
        old_value = versions[max(versions)].value
        self._check_guard(key, old_value, target.value)
        return self._commit(key, target.value, target.meta, "rollback")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get(self, key: str) -> Any:
        """当前值（未知 key → Fail-Closed）。"""
        versions = self._require_registered(key)
        return versions[max(versions)].value

    def version_of(self, key: str) -> int:
        """当前版本号（未知 key → Fail-Closed）。"""
        versions = self._require_registered(key)
        return max(versions)

    def list_versions(self, key: str) -> tuple[int, ...]:
        """版本序列（确定性升序）。"""
        versions = self._require_registered(key)
        return tuple(sorted(versions))

    def snapshot_of(self, key: str, version: int) -> ConfigVersion:
        """单版本快照（未知 key/版本 → Fail-Closed）。"""
        versions = self._require_registered(key)
        snap = versions.get(version)
        if snap is None:
            raise ConfigCenterError(f"未知版本: {key!r} v{version}")
        return snap
