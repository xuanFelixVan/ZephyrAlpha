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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ForwardFixRunner — Forward-Fix 执行器。

依据: 蓝图 MOD-INF-021 §6.2 B51 + D-021-08

回滚的替代决策路径: 优先产生 FIX commit 而非 revert commit。
preview 评估 -> 冲突风险低 + 变更文件 ≤3 -> 自动生成 fix patch -> commit。

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/rollback/forward_fix_runner.yaml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.io.paths import REPO_ROOT


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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def can_forward_fix(self, changed_files: list[str], conflict_risk: str) -> bool:
        if conflict_risk == "high":
            return False
        if len(changed_files) <= 3:
            return True
        return False

    def _own_target_paths(self, target_files: list[str] | None, patch_path: Path) -> list[str]:
        """本次 forward-fix 唯一有权提交的文件集（仓库相对 POSIX 路径）。

        来源必须可追溯到 runner 自家产物：① 调用方显式传入的清单（= 它要提交的修复面）；
        ② 缺省回落到它刚刚自己写出的 fix patch 文件本身。绝不返回"全部脏文件"。
        """
        own: list[str] = []
        for f in target_files or []:
            rel = Path(str(f)).as_posix()
            if str(f):
                try:
                    if Path(str(f)).is_absolute():
                        rel = Path(str(f)).relative_to(self._project_root).as_posix()
                except (ValueError, OSError):
                    continue  # 仓外路径无提交权可言
            if rel and rel not in own:
                own.append(rel)
        if own:
            return own
        # 自家产物兜底：runner 自己写出的 patch 文件（在仓内才谈得上提交）
        try:
            rel = patch_path.resolve().relative_to(self._project_root.resolve()).as_posix()
            return [rel]
        except (ValueError, OSError):
            return []

    def generate_fix(self, commit_sha: str, error_message: str, target_files: list[str] | None = None) -> FixResult:
        patch_path = (REPO_ROOT / ".zephyr" / "fix_patches") / f"fix_{commit_sha}.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = run_subprocess_hidden(
                ["git", "diff", f"{commit_sha}..HEAD"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            patch_path.write_text(result.stdout, encoding="utf-8")

            # 脸三 pathspec 收紧（maint2 2026-10-11 任务书 C 项）：禁 `git add -A`——
            # 共享暂存池是多会话混合池，`add -A`＝把他人条目装进我的 commit＝归属篡改；
            # 只 add/commit 自家目标集（调用方清单，缺省＝自己刚写出的 patch）。
            # 自家集为空时 fail-closed：宁可什么都不提交，也不做无 pathspec 全量 commit。
            own = self._own_target_paths(target_files, patch_path)
            if not own:
                return FixResult(
                    success=False,
                    commit_sha=commit_sha,
                    fix_type="forward_fix",
                    patch_file=str(patch_path),
                    details=["no_own_target_files: fail-closed，跳过 commit（禁吸他人条目）"],
                )
            self.run_git(["add", "--"] + own)
            self.run_git(["commit", "-m", f"Forward-Fix: {error_message[:72]} [target:{commit_sha}]"] + ["--"] + own)

            return FixResult(
                success=True,
                commit_sha=commit_sha,
                fix_type="forward_fix",
                patch_file=str(patch_path),
                details=[f"Fix patch saved to {patch_path}"],
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return FixResult(
                success=False,
                commit_sha=commit_sha,
                fix_type="forward_fix",
                patch_file="",
                details=["internal error"],
            )

    def run_git(self, args: list[str]) -> str:
        try:
            result = run_subprocess_hidden(
                ["git"] + args,
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return ""

    def _run_git(self, args: list[str]) -> str:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_git(args)
