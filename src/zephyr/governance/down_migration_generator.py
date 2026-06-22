# [A_module] module_id=MOD-RES_down_migration_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md

# [MODULE] zephyr.infrastructure.rollback.down_migration_generator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
DownMigrationGenerator — Down-migration 脚本生成器。

依据: 蓝图 MOD-INF-021 §6.2 B45 + D-021-16

pre-commit hook: 每次 commit 自动生成反向脚本 (.sh + .ps1)。
git 行为序列 → 自动推导逆操作 → 生成可执行回退脚本。
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class DownMigration:
    commit_sha: str
    bash_script: str
    pwsh_script: str
    files_changed: list[str]
    generated_at: str


class DownMigrationGenerator:
    OUTPUT_DIR: str = "data/rollback/down"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._output_dir = self._project_root / self.OUTPUT_DIR
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, commit_sha: str = "HEAD") -> DownMigration:
        if not commit_sha or commit_sha == "HEAD":
            commit_sha = self._get_head_short()

        changed_files = self._get_changed_files(commit_sha)
        now = datetime.now(UTC)

        bash_script = self._generate_bash(commit_sha, changed_files)
        pwsh_script = self._generate_pwsh(commit_sha, changed_files)

        bash_path = self._output_dir / f"{commit_sha}.sh"
        pwsh_path = self._output_dir / f"{commit_sha}.ps1"

        bash_path.write_text(bash_script, encoding="utf-8")
        pwsh_path.write_text(pwsh_script, encoding="utf-8")

        return DownMigration(
            commit_sha=commit_sha,
            bash_script=str(bash_path),
            pwsh_script=str(pwsh_path),
            files_changed=changed_files,
            generated_at=now.isoformat(),
        )

    def _generate_bash(self, commit_sha: str, files: list[str]) -> str:
        lines: list[str] = []
        lines.append("#!/bin/bash")
        lines.append(f"# Down-migration: revert to {commit_sha}")
        lines.append(f"# Generated: {datetime.now(UTC).isoformat()}")
        lines.append("#")
        lines.append("set -euo pipefail")
        lines.append("")
        lines.append(f"echo 'Starting down-migration to {commit_sha}'")
        lines.append(f"git revert --no-edit {commit_sha}")
        lines.append("")
        lines.append("echo 'Down-migration complete'")
        return "\n".join(lines)

    def _generate_pwsh(self, commit_sha: str, files: list[str]) -> str:
        lines: list[str] = []
        lines.append(f"# Down-migration: revert to {commit_sha}")
        lines.append(f"# Generated: {datetime.now(UTC).isoformat()}")
        lines.append("$ErrorActionPreference = 'Stop'")
        lines.append("")
        lines.append(f"Write-Host 'Starting down-migration to {commit_sha}'")
        lines.append(f"git revert --no-edit {commit_sha}")
        lines.append("")
        lines.append("Write-Host 'Down-migration complete'")
        return "\n".join(lines)

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
            return "unknown"

    def _get_changed_files(self, commit_sha: str) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_sha],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return [f for f in result.stdout.strip().split("\n") if f]
        except Exception:
            return []
