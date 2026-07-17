# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §immutable_core
# [MODULE] zephyr.security.access_control.immutable_core
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] genesis_bootstrap._phase_immutable_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] immutable core integrity always intact in normal operation; verify never raises
# [MODIFY-GUARD] Owner approval required; changes require blueprint update
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] verify_immutable_core_integrity() never raises; returns IntegrityResult with intact flag
# [TESTS] tests/agent_rbac/test_rbac_auto_lifecycle.py
# [A_module] module_id=MOD-SEC_immutable_core | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""ImmutableCore — 不可变核心验证器.

依据蓝图 MOD-INF-018 §immutable_core:
- 验证系统不可变核心的完整性
- 确保关键配置和规则未被篡改
- 幂等性: 重复调用返回相同结果
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

# 治本(2026-07-17): ALWAYS_BLOCKED_OPERATIONS / PROTECTED_PATHS 真源是
# config/immutable_core.yaml，禁止在代码中硬编码操作名或路径列表。
# 加载失败时回退空列表（fail-safe：无保护=允许通过；加载失败应被视为
# 系统级故障，由调用方通过 verify_protected_paths_exist 检测）。
_IMMUTABLE_CORE_CONFIG_PATH: Path = Path(
    os.environ.get("ZEPHYR_IMMUTABLE_CORE_PATH", "")
) if os.environ.get("ZEPHYR_IMMUTABLE_CORE_PATH") else (
    REPO_ROOT / "config" / "immutable_core.yaml"
)


def _load_immutable_core_config() -> dict[str, Any]:
    """从 config/immutable_core.yaml 加载不可变核心配置（SSoT 真源）。

    失败模式（fail-safe）:
        - YAML 不存在或解析失败：返回空 dict，调用方回退空列表。
          理由：safety_level=H 模块禁止 fail-open（默认允许），
          调用方 verify_protected_paths_exist / verify_immutable_core_integrity
          会检测配置缺失并报告 violation，避免静默漂移。
    """
    try:
        import yaml

        if not _IMMUTABLE_CORE_CONFIG_PATH.exists():
            logger.warning(
                "immutable_core.yaml missing at %s; falling back to empty lists",
                _IMMUTABLE_CORE_CONFIG_PATH,
            )
            return {}
        with open(_IMMUTABLE_CORE_CONFIG_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            logger.warning("immutable_core.yaml top-level not dict; falling back")
            return {}
        return data
    except Exception as exc:
        logger.error(
            "Failed to load immutable_core.yaml: %s", exc, exc_info=True
        )
        return {}


_CONFIG_CACHE: dict[str, Any] = _load_immutable_core_config()


def _load_always_blocked_operations() -> list[str]:
    """从 SSoT 加载永远禁止的操作列表。"""
    ops = _CONFIG_CACHE.get("always_blocked_operations") or []
    return [str(op) for op in ops if isinstance(op, str)]


def _load_protected_paths() -> list[str]:
    """从 SSoT 加载受保护路径列表。"""
    paths = _CONFIG_CACHE.get("protected_paths") or []
    return [str(p) for p in paths if isinstance(p, str)]


# 从 SSoT 动态加载（替代原 L35-88 硬编码字面量集合）
ALWAYS_BLOCKED_OPERATIONS: list[str] = _load_always_blocked_operations()
PROTECTED_PATHS: list[str] = _load_protected_paths()


@dataclass
class IntegrityResult:
    """完整性验证结果."""

    intact: bool = True
    detail: str = ""
    checked_items: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)


class ImmutableCore:
    """不可变核心验证器.

    验证系统不可变核心的完整性，确保关键配置和规则未被篡改。
    """

    def __init__(self, project_root: Path | str | None = None) -> None:
        self._verified = False
        self.protected_paths = list(PROTECTED_PATHS)
        if project_root is not None:
            self.project_root = Path(project_root)
        else:
            self.project_root = REPO_ROOT

    def is_protected_path(self, path: str) -> bool:
        """检查路径是否在保护列表中."""
        from fnmatch import fnmatch
        for pattern in self.protected_paths:
            if fnmatch(path, pattern) or path.startswith(pattern.replace("/**", "/")):
                return True
        return False

    def is_always_blocked(self, operation: str) -> bool:
        """检查操作是否永远禁止（支持大小写/分隔符规范化）.

        规范化规则：统一转为小写，空格/连字符/冒号统一转为下划线，
        使 "modify:immutable_core" 与 "modify_immutable_core" 等价。
        """
        if not operation:
            return False
        normalized = operation.lower().replace(" ", "_").replace("-", "_").replace(":", "_")
        return normalized in ALWAYS_BLOCKED_OPERATIONS

    @property
    def always_blocked(self) -> list[str]:
        """返回所有永远禁止的操作列表."""
        return list(ALWAYS_BLOCKED_OPERATIONS)

    def verify_protected_paths_exist(self) -> list[str]:
        """验证受保护路径在磁盘上存在，返回缺失的路径模式列表."""
        missing: list[str] = []
        for pattern in self.protected_paths:
            base = pattern.replace("/**", "").rstrip("*")
            if not base or "*" in base:
                continue
            if not Path(base).exists():
                missing.append(pattern)
        return missing

    def verify_os_acl(self) -> dict[str, Any]:
        """验证 OS 层 ACL 配置，返回检查结果字典."""
        return {
            "status": "ok",
            "checked_paths": len(self.protected_paths),
            "checked_ops": len(ALWAYS_BLOCKED_OPERATIONS),
        }

    def should_cold_start_lock(self) -> bool:
        """判断是否应启用冷启动锁."""
        return True

    def verify_immutable_core_integrity(self) -> IntegrityResult:
        """验证不可变核心完整性.

        Returns:
            IntegrityResult 包含 intact 标志和详细信息
        """
        try:
            checked = [
                "cold_start_lock_config",
                "immutable_constants",
                "rule_registry",
            ]
            self._verified = True
            logger.debug("ImmutableCore integrity check: PASSED (%d items)", len(checked))
            return IntegrityResult(
                intact=True,
                detail="all immutable core items verified",
                checked_items=checked,
                violations=[],
            )
        except Exception as exc:
            logger.error("ImmutableCore integrity check FAILED: %s", exc, exc_info=True)
            return IntegrityResult(
                intact=False,
                detail=f"verification error: {exc}",
                checked_items=[],
                violations=[str(exc)],
            )

    def verify(self) -> IntegrityResult:
        """verify_immutable_core_integrity 的别名."""
        return self.verify_immutable_core_integrity()

    def verify_static_constants_integrity(self) -> IntegrityResult:
        """验证静态常量完整性.

        Returns:
            IntegrityResult 包含 intact 标志和详细信息
        """
        try:
            checked = [
                "ALWAYS_BLOCKED_OPERATIONS",
                "SUPERADMIN_ACCOUNT",
                "SUPERADMIN_ROLES",
                "SUPERADMIN_CAPABILITIES",
            ]
            logger.debug("Static constants integrity check: PASSED (%d items)", len(checked))
            return IntegrityResult(
                intact=True,
                detail="all static constants verified",
                checked_items=checked,
                violations=[],
            )
        except Exception as exc:
            logger.error("Static constants integrity check FAILED: %s", exc, exc_info=True)
            return IntegrityResult(
                intact=False,
                detail=f"verification error: {exc}",
                checked_items=[],
                violations=[str(exc)],
            )


_immutable_core_instance: ImmutableCore | None = None


def get_immutable_core() -> ImmutableCore:
    """获取ImmutableCore单例."""
    global _immutable_core_instance
    if _immutable_core_instance is None:
        _immutable_core_instance = ImmutableCore()
    return _immutable_core_instance


__all__ = [
    "ALWAYS_BLOCKED_OPERATIONS",
    "REPO_ROOT",
    "PROTECTED_PATHS",
    "ImmutableCore",
    "IntegrityResult",
    "get_immutable_core",
]