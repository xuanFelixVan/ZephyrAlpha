# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] zephyr.clone_guard.orchestrator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig, load_config); zephyr.clone_guard.engines.echo_guard_adapter (EchoGuardAdapter, Finding)
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.capability_overlap_gate; zephyr.clone_guard (re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 统一调度入口——Phase A 仅调度 Echo-Guard；check() 永不抛异常；degraded 时按 fail_closed 配置决定阻断或放行；extract 级硬阻断=必须合并
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() 永不抛异常——适配器失败时 degraded=True + 按 fail_closed 决定 passed
# [TESTS] tests/clone_guard/test_orchestrator.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CloneGuard 统一编排器——Phase A MVP（仅调度 Echo-Guard）。

统一调度入口，对 CAPABILITY-OVERLAP 门禁暴露 check() 方法。
Phase B 起在此层添加多引擎并发调度（asyncio.gather）+ 结果聚合。

Usage::

    from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator

    orch = CloneGuardOrchestrator(repo_root=Path("/repo"))
    result = orch.check(staged_files=["src/foo.py", "scripts/bar.py"])
    if not result.passed:
        # extract 级克隆发现——硬阻断
        for f in result.findings:
            print(f"  {f.severity}: {f.source_function} 重复 {f.existing_function}")
"""

from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig, load_config
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter, Finding

logger = logging.getLogger(__name__)

__all__ = ["CheckResult", "CloneGuardOrchestrator", "Finding"]


@dataclass
class CheckResult:
    """CloneGuard check 结果。

    Attributes:
        passed: True=放行, False=硬阻断（extract 级克隆发现）
        findings: 检测到的克隆 Finding 列表
        degraded: True=echo-guard 不可用/超时/崩溃（降级模式）
        error: 错误描述（None=无错误）
        checked_files: 实际被检测的文件数
    """

    passed: bool
    findings: list[Finding] = field(default_factory=list)
    degraded: bool = False
    error: str | None = None
    checked_files: int = 0


class CloneGuardOrchestrator:
    """CloneGuard 统一编排器。

    Phase A: 仅调度 Echo-Guard
    Phase B: + ast-grep + reDUP 并发
    Phase C: + mcrit + Vendetect + relate
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or load_config(self._repo_root)
        self._echo_guard = EchoGuardAdapter(self._repo_root, self._config)

    def check(self, staged_files: list[str]) -> CheckResult:
        """检测 staged 文件中的代码克隆。

        Args:
            staged_files: staged 文件路径列表（相对路径）。

        Returns:
            CheckResult: passed=False 表示发现 extract 级克隆（硬阻断）。
        """
        # 1. 筛选 .py 文件（排除测试文件和忽略路径）
        py_files = self._filter_files(staged_files)
        if not py_files:
            return CheckResult(passed=True, checked_files=0)

        # 2. 调用 Echo-Guard 检测
        findings, degraded = self._echo_guard.detect(py_files, self._config.pre_commit_timeout_sec)

        # 3. 降级处理
        if degraded:
            if self._config.fail_closed:
                return CheckResult(
                    passed=False,
                    degraded=True,
                    error="echo-guard 不可用且 fail_closed=True——阻断提交（守铁律）",
                    checked_files=len(py_files),
                )
            logger.warning(
                "CloneGuard degraded: echo-guard 不可用，降级为 warn-only（不阻断）"
            )
            return CheckResult(passed=True, degraded=True, checked_files=len(py_files))

        # 4. 严重性判定
        block_findings = [f for f in findings if f.severity in self._config.block_severities]
        review_findings = [f for f in findings if f.severity == "review"]

        if review_findings:
            for f in review_findings:
                logger.warning(
                    "CloneGuard review: %s 与 %s:%d 的 %s 相似度 %.1f%%（建议精简）",
                    f.source_file,
                    f.existing_file,
                    f.existing_lineno,
                    f.existing_function,
                    f.similarity * 100,
                )

        if block_findings:
            return CheckResult(
                passed=False,
                findings=block_findings,
                checked_files=len(py_files),
            )

        return CheckResult(passed=True, findings=findings, checked_files=len(py_files))

    def _filter_files(self, files: list[str]) -> list[str]:
        """筛选需要检测的 .py 文件（排除测试、忽略路径）。"""
        result: list[str] = []
        for f in files:
            # 只检测 .py 文件
            if not f.endswith(".py"):
                continue
            # 统一路径分隔符后做前缀/模式匹配
            rel = f.replace("\\", "/")
            # 排除测试文件（路径开头或中间包含 test_/tests/conftest）
            if (
                "/test_" in rel
                or rel.startswith("test_")
                or rel.startswith("tests/")
                or "/tests/" in rel
                or "/conftest.py" in rel
            ):
                continue
            # 排除忽略路径——目录前缀模式（以 / 结尾）做 startsWith，其余用 fnmatch
            if any(
                rel.startswith(pat) if pat.endswith("/") else fnmatch.fnmatch(rel, pat)
                for pat in self._config.ignore_paths
            ):
                continue
            result.append(f)
        return result
