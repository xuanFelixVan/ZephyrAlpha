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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: forward_fix_runner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ForwardFixRunner
#   name_en: ForwardFixRunner
#   intro: class ForwardFixRunner 源码 L72-L142
#   desc: 公共方法（定义序）: project_root, can_forward_fix, generate_fix, run_git；源码 L72-L142
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ForwardFixRunner
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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

    def generate_fix(self, commit_sha: str, error_message: str) -> FixResult:
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

            self.run_git(["add", "-A"])
            self.run_git(["commit", "-m", f"Forward-Fix: {error_message[:72]} [target:{commit_sha}]"])

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
