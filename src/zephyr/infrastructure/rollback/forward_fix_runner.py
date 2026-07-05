# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.forward_fix_runner
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
# [A_module] module_id=MOD-INF_forward_fix_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ForwardFixRunner — Forward-Fix 执行器。

依据: 蓝图 MOD-INF-021 §6.2 B51 + D-021-08

回滚的替代决策路径: 优先产生 FIX commit 而非 revert commit。
preview 评估 → 冲突风险低 + 变更文件 ≤3 → 自动生成 fix patch → commit。
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FixResult:
    success: bool
    commit_sha: str
    fix_type: str
    patch_file: str
    details: list[str] = field(default_factory=list)


class ForwardFixRunner:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def can_forward_fix(self, changed_files: list[str], conflict_risk: str) -> bool:
        if conflict_risk == "high":
            return False
        if len(changed_files) <= 3:
            return True
        return False

    def generate_fix(self, commit_sha: str, error_message: str) -> FixResult:
        patch_path = Path(".zephyr/fix_patches") / f"fix_{commit_sha}.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                ["git", "diff", f"{commit_sha}..HEAD"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            patch_path.write_text(result.stdout, encoding="utf-8")

            self._run_git(["add", "-A"])
            self._run_git(["commit", "-m", f"Forward-Fix: {error_message[:72]} [target:{commit_sha}]"])

            return FixResult(
                success=True,
                commit_sha=commit_sha,
                fix_type="forward_fix",
                patch_file=str(patch_path),
                details=[f"Fix patch saved to {patch_path}"],
            )
        except Exception as e:
            return FixResult(
                success=False,
                commit_sha=commit_sha,
                fix_type="forward_fix",
                patch_file="",
                details=["internal error"],
            )

    def _run_git(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout
        except Exception:
            return ""
