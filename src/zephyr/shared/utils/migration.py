# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.migration
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SHR_migration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
migration.py —— ZephyrAlpha Schema 版本化迁移系统

Phase 5 新增（盲点 B4）——解决 schemas.py Task 模型变更后
旧 SQLite 记录无法自动升级的问题。

设计原则：
  - 零外部依赖——纯 Python dict 操作，不需要 Alembic/SQLAlchemy
  - 双向迁移——支持 upgrade 和 downgrade（用于回滚场景）
  - 版本链——从任意旧版本逐步迁移到最新版本
  - 幂等——同一版本多次调用无副作用
  - 可发现——所有迁移注册到 `MIGRATIONS` 字典，AI 可直接遍历

对标：
  - Alembic (SQLAlchemy): revision-based migration chain
  - Django migrations: auto-detected + dependency graph
  - flyway: versioned SQL scripts

SSoT: MOD-INF-016 §2.12 shared-migration
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final
from collections.abc import Callable
from typing import Any

__all__ = [
    "MIGRATIONS",
    "Migration",
    "MigrationError",
    "downgrade_task",
    "latest_schema_version",
    "migrate_task",
]


class MigrationError(Exception):
    """迁移失败异常。"""
    error_code = "ZA-SH-0048"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


Migration = Callable[[dict[str, Any]], dict[str, Any]]

MIGRATIONS: Final[dict[str, dict[str, Migration]]] = {}
"""
迁移注册表——按 `{from_version: {to_version: migration_fn}}` 组织。

格式:
    MIGRATIONS = {
        "1.0.0": {
            "1.1.0": upgrade_1_0_0_to_1_1_0,
        },
        "1.1.0": {
            "1.0.0": downgrade_1_1_0_to_1_0_0,
            "2.0.0": upgrade_1_1_0_to_2_0_0,
        },
    }

AI 添加新迁移时:
  1. 将 `_register_*` 函数取消注释
  2. 实现 migration 函数
  3. 注册到 MIGRATIONS
  4. 更新 `latest_schema_version` 返回值
"""


def _register_bidirectional(
    from_ver: str,
    to_ver: str,
    upgrade_fn: Migration,
    downgrade_fn: Migration,
) -> None:
    """注册双向迁移——upgrade 和 downgrade 同时登记。"""
    MIGRATIONS.setdefault(from_ver, {})[to_ver] = upgrade_fn
    MIGRATIONS.setdefault(to_ver, {})[from_ver] = downgrade_fn


# 5.136.2 修复: 原 Phase 5 占位示例注释代码块已删除, 后续实际 Schema 变更时
# 应在 docs 中编写示例, 而非在源码中保留注释代码。


LATEST_VERSION: Final[str] = "1.0.0"


def latest_schema_version() -> str:
    """返回当前最新 Schema 版本。

    每次新增字段且实现了升级迁移后，MUST 更新此返回值。
    """
    return LATEST_VERSION


def _find_path(from_ver: str, to_ver: str) -> list[str]:
    """BFS 寻找从 from_ver 到 to_ver 的最短迁移路径。"""
    if from_ver == to_ver:
        return []

    visited: set[str] = {from_ver}
    queue: list[tuple[str, list[str]]] = [(from_ver, [])]

    while queue:
        current, path = queue.pop(0)
        neighbors = MIGRATIONS.get(current, {})
        for neighbor in neighbors:
            if neighbor == to_ver:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []


def migrate_task(data: dict[str, Any], to_version: str | None = None) -> dict[str, Any]:
    """将一个 Task dict 从当前版本迁移到目标版本。

    Args:
        data: Task 数据的 dict 表示
        to_version: 目标版本号。None = 自动迁移到最新版本

    Returns:
        迁移后的 dict（新副本，不修改原 dict）

    Raises:
        MigrationError: 迁移路径不存在

    用法:
        from zephyr.shared.utils.migration import migrate_task

        old_task = {"task_id": "T-001", "schema_version": "1.0.0", ...}
        migrated = migrate_task(old_task)  # 自动到最新

        migrated = migrate_task(old_task, to_version="1.1.0")  # 到指定版本
    """
    target = to_version or latest_schema_version()
    data = dict(data)

    current_version = data.get("schema_version", "1.0.0")

    if current_version == target:
        data["schema_version"] = target
        return data

    path = _find_path(current_version, target)
    if not path:
        raise MigrationError(
            f"找不到从 {current_version} 到 {target} 的迁移路径。\n"
            f"  已注册的版本: {sorted(MIGRATIONS.keys())}\n"
            f"  当前最新版本: {latest_schema_version()}"
        )

    for next_ver in path:
        current = data.get("schema_version", current_version)
        migration_fn = MIGRATIONS.get(current, {}).get(next_ver)
        if migration_fn is None:
            raise MigrationError(f"迁移 {current} -> {next_ver} 未注册")
        data = migration_fn(data)
        data["schema_version"] = next_ver

    data["schema_version"] = target
    return data


def downgrade_task(data: dict[str, Any], to_version: str) -> dict[str, Any]:
    """将 Task dict 从当前版本降级到旧版本。

    用于回滚场景。路径自动反向查找。

    Args:
        data: Task dict
        to_version: 目标旧版本号

    Returns:
        降级后的 dict
    """
    return migrate_task(data, to_version=to_version)
