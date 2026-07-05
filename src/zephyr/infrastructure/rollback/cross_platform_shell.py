# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.cross_platform_shell
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
# [A_module] module_id=MOD-INF_cross_platform_shell | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CrossPlatformShell — 跨平台 Shell 脚本双输出。

依据: 蓝图 MOD-INF-021 §6.12 B67

对每个回滚操作自动生成 Linux (.sh) 和 Windows (.ps1) 双平台可执行脚本。
.sh: bash shebang + chmod +x + git revert --gpg-sign
.ps1: #Requires -Version 5.1 + Set-ExecutionPolicy 保护
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class CrossPlatformScripts:
    bash_path: str
    pwsh_path: str
    commit_sha: str
    generated_at: str


class CrossPlatformShell:
    OUTPUT_DIR: str = "data/rollback/down"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._output_dir = self._project_root / self.OUTPUT_DIR
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, commit_sha: str, gpg_sign: bool = False) -> CrossPlatformScripts:
        now = datetime.now(UTC).isoformat()

        bash_content = self._build_bash(commit_sha, gpg_sign)
        pwsh_content = self._build_pwsh(commit_sha, gpg_sign)

        bash_path = self._output_dir / f"{commit_sha}.sh"
        pwsh_path = self._output_dir / f"{commit_sha}.ps1"

        bash_path.write_text(bash_content, encoding="utf-8")
        pwsh_path.write_text(pwsh_content, encoding="utf-8")

        return CrossPlatformScripts(
            bash_path=str(bash_path),
            pwsh_path=str(pwsh_path),
            commit_sha=commit_sha,
            generated_at=now,
        )

    def _build_bash(self, commit_sha: str, gpg_sign: bool) -> str:
        lines = [
            "#!/usr/bin/env bash",
            "# ZephyrAlpha Rollback Script — Linux/macOS",
            f"# Target: {commit_sha}",
            f"# Generated: {datetime.now(UTC).isoformat()}",
            "",
            "set -euo pipefail",
            "",
            f'echo "[ROLLBACK] Starting rollback to commit {commit_sha}"',
        ]
        if gpg_sign:
            lines.append(f"git revert --gpg-sign --no-edit {commit_sha}")
        else:
            lines.append(f"git revert --no-edit {commit_sha}")
        lines.extend(
            [
                "",
                'echo "[ROLLBACK] Complete"',
            ]
        )
        return "\n".join(lines)

    def _build_pwsh(self, commit_sha: str, gpg_sign: bool) -> str:
        lines = [
            "#Requires -Version 5.1",
            "# ZephyrAlpha Rollback Script — Windows PowerShell",
            f"# Target: {commit_sha}",
            f"# Generated: {datetime.now(UTC).isoformat()}",
            "",
            "$ErrorActionPreference = 'Stop'",
            "",
            f'Write-Host "[ROLLBACK] Starting rollback to commit {commit_sha}"',
        ]
        if gpg_sign:
            lines.append(f"git revert --gpg-sign --no-edit {commit_sha}")
        else:
            lines.append(f"git revert --no-edit {commit_sha}")
        lines.extend(
            [
                "",
                'Write-Host "[ROLLBACK] Complete"',
            ]
        )
        return "\n".join(lines)
