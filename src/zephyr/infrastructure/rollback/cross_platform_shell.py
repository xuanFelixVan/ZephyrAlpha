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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DEPRECATED] legacy trio retirement (audit P2-13 / P2-20).
#   Replacement: no direct replacement; the rollback core path
#   (RollbackExecutor + RollbackVerifier) remains the supported API.
#   Scheduled for removal in a future release.

"""
CrossPlatformShell — 跨平台 Shell 脚本双输出。

依据: 蓝图 MOD-INF-021 §6.12 B67

对每个回滚操作自动生成 Linux (.sh) 和 Windows (.ps1) 双平台可执行脚本。
.sh: bash shebang + chmod +x + git revert --gpg-sign
.ps1: #Requires -Version 5.1 + Set-ExecutionPolicy 保护

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: cross_platform_shell.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CrossPlatformShell
#   name_en: CrossPlatformShell
#   intro: class CrossPlatformShell 源码 L83-L175
#   desc: 公共方法（定义序）: output_dir, project_root, generate；源码 L83-L175
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CrossPlatformShell
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

warnings.warn(
    "zephyr.infrastructure.rollback.cross_platform_shell is deprecated (legacy "
    "trio retirement, audit P2-13/P2-20). No direct replacement; use the "
    "rollback core path (RollbackExecutor/RollbackVerifier).",
    DeprecationWarning,
    stacklevel=2,
)


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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def output_dir(self):
        """只读：output_dir（Stage 4 公共化）。"""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        """写入：output_dir（Stage 4 公共化）。"""
        self._output_dir = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

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
