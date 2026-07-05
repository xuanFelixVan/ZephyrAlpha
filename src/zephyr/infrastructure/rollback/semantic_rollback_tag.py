# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.semantic_rollback_tag
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_semantic_rollback_tag | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SemanticRollbackTag — 语义化 Rollback Tag 管理器。

依据: 蓝图 MOD-INF-021 §6.12 B62

TASK/refactor/migration 边界自动 git tag:
    rollback/task-{task_id}:before / :after
    rollback/refactor/{module}:before / :after
    rollback/migration/{migration_id}:before / :after

Tag 作为语义化回滚目标: zephyr rollback --to rollback/refactor/auth:before
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path


class TagType(str, Enum):
    TASK = "task"
    REFACTOR = "refactor"
    MIGRATION = "migration"


@dataclass
class RollbackTag:
    tag_name: str
    tag_type: TagType
    target_id: str
    phase: str
    commit_sha: str
    created_at: str


class SemanticRollbackTag:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def tag_task(self, task_id: str, phase: str) -> RollbackTag | None:
        sha = self._get_head_short()
        if not sha:
            return None
        tag = RollbackTag(
            tag_name=f"rollback/task-{task_id}:{phase}",
            tag_type=TagType.TASK,
            target_id=task_id,
            phase=phase,
            commit_sha=sha,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._create_git_tag(tag.tag_name, sha)
        return tag

    def tag_refactor(self, module: str, phase: str) -> RollbackTag | None:
        sha = self._get_head_short()
        if not sha:
            return None
        tag = RollbackTag(
            tag_name=f"rollback/refactor/{module}:{phase}",
            tag_type=TagType.REFACTOR,
            target_id=module,
            phase=phase,
            commit_sha=sha,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._create_git_tag(tag.tag_name, sha)
        return tag

    def tag_migration(self, migration_id: str, phase: str) -> RollbackTag | None:
        sha = self._get_head_short()
        if not sha:
            return None
        tag = RollbackTag(
            tag_name=f"rollback/migration/{migration_id}:{phase}",
            tag_type=TagType.MIGRATION,
            target_id=migration_id,
            phase=phase,
            commit_sha=sha,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._create_git_tag(tag.tag_name, sha)
        return tag

    def list_tags(self, tag_type: TagType | None = None) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "tag", "-l", "rollback/*"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            tags = [t for t in result.stdout.strip().split("\n") if t]
            if tag_type:
                prefix = f"rollback/{tag_type.value}/"
                tags = [t for t in tags if t.startswith(prefix)]
            return tags
        except Exception:
            return []

    def resolve_tag(self, tag_name: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "rev-list", "-1", tag_name],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning("suppressed error in semantic_rollback_tag", exc_info=True)
        return None

    def delete_tag_safe(self, tag_name: str) -> bool:
        try:
            subprocess.run(
                ["git", "tag", "-d", tag_name],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            return True
        except Exception:
            return False

    def find_task_tags(self, task_id: str) -> list[str]:
        return [t for t in self.list_tags(TagType.TASK) if task_id in t]

    def _create_git_tag(self, tag_name: str, commit_sha: str) -> None:
        subprocess.run(
            ["git", "tag", "-f", tag_name, commit_sha],
            cwd=str(self._project_root),
            capture_output=True,
            text=True,
            timeout=5,
        )

    def _get_head_short(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception:
            return ""
