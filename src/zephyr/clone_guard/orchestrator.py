# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] zephyr.clone_guard.orchestrator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig, load_config); zephyr.clone_guard.engines.echo_guard_adapter (EchoGuardAdapter, Finding); zephyr.clone_guard.engines.ast_grep_adapter (AstGrepAdapter); zephyr.clone_guard.aggregator (FindingAggregator, AggregatedFinding, AggregationResult); asyncio; concurrent.futures; fnmatch; logging
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.capability_overlap_gate; zephyr.clone_guard (re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 统一调度入口——Phase B 并发调度 Echo-Guard + ast-grep（asyncio.gather + run_in_executor 桥接同步适配器）；check() 永不抛异常；全引擎降级时按 fail_closed 决定阻断或放行；部分降级 warn+继续；extract 级硬阻断=必须合并；结果经 FindingAggregator 去重+多数表决+严重性就高
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() 永不抛异常——适配器异常被 run_in_executor 捕获并归一为 ([], degraded=True)；全降级按 fail_closed 决定 passed；asyncio.run 在已有事件循环时回退顺序执行
# [TESTS] tests/clone_guard/test_orchestrator.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CloneGuard 统一编排器——Phase B（多引擎并发 + 结果聚合）。

统一调度入口，对 CAPABILITY-OVERLAP 门禁暴露 check() 方法。
Phase B 起：asyncio.gather 并发调度 Echo-Guard + ast-grep，结果经
FindingAggregator 去重 + 多数表决 + 严重性就高，输出 AggregatedFinding 列表。

并发模型
--------
适配器 detect() 是同步阻塞调用（subprocess.run），通过
``loop.run_in_executor`` 提交到线程池实现真并发（subprocess 等待是 I/O 阻塞，
线程模型足够）。``asyncio.gather(return_exceptions=True)`` 保证单引擎异常不
影响其他引擎——异常被归一为 ``([], degraded=True)`` 交给聚合器。

降级策略（守 blueprint §5.2）
-----------------------------
- 单引擎降级：标记 degraded_engines，其他引擎结果照常聚合（warn-only）
- 全引擎降级：fail_closed=True→阻断（守铁律）；fail_closed=False→warn-only 放行

Usage::

    from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator

    orch = CloneGuardOrchestrator(repo_root=Path("/repo"))
    result = orch.check(staged_files=["src/foo.py", "scripts/bar.py"])
    if not result.passed:
        # extract 级克隆发现——硬阻断
        for f in result.findings:
            print(f"  {f.severity} [{f.consensus}]: {f.source_function} 重复 {f.existing_function}")
"""

from __future__ import annotations

import asyncio
import fnmatch
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.clone_guard.aggregator import (
    AggregatedFinding,
    AggregationResult,
    FindingAggregator,
)
from zephyr.clone_guard.config import CloneGuardConfig, load_config
from zephyr.clone_guard.engines.ast_grep_adapter import AstGrepAdapter
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter, Finding

logger = logging.getLogger(__name__)

__all__ = ["AggregatedFinding", "CheckResult", "CloneGuardOrchestrator", "Finding"]


@dataclass
class CheckResult:
    """CloneGuard check 结果。

    Attributes:
        passed: True=放行, False=硬阻断（extract 级克隆发现）
        findings: 聚合后的 AggregatedFinding 列表（passed=False 时仅含阻断级）
        degraded: True=有引擎降级（部分或全部）
        degraded_engines: 降级引擎名列表（供诊断）
        consensus_summary: {consensus_level: count} 共识分布（unanimous/majority/single）
        error: 错误描述（None=无错误）
        checked_files: 实际被检测的文件数
    """

    passed: bool
    findings: list[AggregatedFinding] = field(default_factory=list)
    degraded: bool = False
    degraded_engines: list[str] = field(default_factory=list)
    consensus_summary: dict[str, int] = field(default_factory=dict)
    error: str | None = None
    checked_files: int = 0


class CloneGuardOrchestrator:
    """CloneGuard 统一编排器。

    Phase A: 仅调度 Echo-Guard
    Phase B: + ast-grep 并发 + FindingAggregator 聚合（当前）
    Phase C: + mcrit + Vendetect + relate
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or load_config(self._repo_root)
        self._echo_guard = EchoGuardAdapter(self._repo_root, self._config)
        self._ast_grep = AstGrepAdapter(self._repo_root, self._config)
        self._aggregator = FindingAggregator(self._config)

    def check(self, staged_files: list[str]) -> CheckResult:
        """检测 staged 文件中的代码克隆（多引擎并发 + 聚合）。

        Args:
            staged_files: staged 文件路径列表（相对路径）。

        Returns:
            CheckResult: passed=False 表示发现 extract 级克隆（硬阻断）。
        """
        # 1. 筛选 .py 文件（排除测试文件和忽略路径）
        py_files = self._filter_files(staged_files)
        if not py_files:
            return CheckResult(passed=True, checked_files=0)

        # 2. 并发调度多引擎
        engine_results = self._run_engines_concurrent(py_files)

        # 3. 聚合（去重 + 多数表决 + 严重性就高）
        agg_result = self._aggregator.aggregate(engine_results)

        # 4. 全引擎降级 → fail_closed 决定
        if agg_result.active_engine_count == 0:
            return self._handle_total_degradation(
                len(py_files), agg_result.degraded_engines
            )

        # 5. 部分降级 → warn + 继续（用活跃引擎结果）
        if agg_result.degraded_engines:
            logger.warning(
                "CloneGuard: 引擎 %s 降级，仅用 %d 个活跃引擎结果聚合",
                agg_result.degraded_engines,
                agg_result.active_engine_count,
            )

        # 6. 严重性判定
        block_findings = [
            f for f in agg_result.findings if f.severity in self._config.block_severities
        ]
        review_findings = [f for f in agg_result.findings if f.severity == "review"]

        for f in review_findings:
            logger.warning(
                "CloneGuard review: %s 与 %s:%d 的 %s 相似度 %.1f%%（共识=%s, 引擎=%s）",
                f.source_file,
                f.existing_file,
                f.existing_lineno,
                f.existing_function,
                f.similarity * 100,
                f.consensus,
                ",".join(f.engines),
            )

        consensus_summary = self._build_consensus_summary(agg_result)
        degraded = bool(agg_result.degraded_engines)

        if block_findings:
            return CheckResult(
                passed=False,
                findings=block_findings,
                degraded=degraded,
                degraded_engines=agg_result.degraded_engines,
                consensus_summary=consensus_summary,
                checked_files=len(py_files),
            )

        return CheckResult(
            passed=True,
            findings=agg_result.findings,
            degraded=degraded,
            degraded_engines=agg_result.degraded_engines,
            consensus_summary=consensus_summary,
            checked_files=len(py_files),
        )

    # ------------------------------------------------------------------
    # 并发调度
    # ------------------------------------------------------------------

    def _run_engines_concurrent(
        self, py_files: list[str]
    ) -> dict[str, tuple[list[Finding], bool]]:
        """asyncio.gather 并发调度所有启用引擎（守 blueprint §5.1）。

        适配器 detect() 是同步阻塞调用，通过 run_in_executor 提交线程池
        实现真并发。return_exceptions=True 保证单引擎异常被捕获归一为
        ([], degraded=True)，不影响其他引擎。

        Returns:
            {engine_name: (findings, degraded)} 字典。
        """
        timeout = self._config.pre_commit_timeout_sec

        async def _gather_all(executor: ThreadPoolExecutor):
            loop = asyncio.get_running_loop()
            tasks = {
                "echo_guard": loop.run_in_executor(
                    executor, self._echo_guard.detect, py_files, timeout
                ),
                "ast_grep": loop.run_in_executor(
                    executor, self._ast_grep.detect, py_files, timeout
                ),
            }
            raw = await asyncio.gather(*tasks.values(), return_exceptions=True)
            return dict(zip(tasks.keys(), raw))

        try:
            raw_results = asyncio.run(
                _gather_all(
                    ThreadPoolExecutor(
                        max_workers=4, thread_name_prefix="clone-guard"
                    )
                )
            )
        except RuntimeError:
            # 已有事件循环在跑（如嵌套 async 上下文）——回退顺序执行
            logger.debug("CloneGuard: 检测到已有事件循环，回退顺序执行引擎")
            raw_results = self._run_engines_sequential(py_files, timeout)

        # 归一化异常 → ([], degraded=True)
        engine_results: dict[str, tuple[list[Finding], bool]] = {}
        for name, res in raw_results.items():
            if isinstance(res, BaseException):
                logger.warning(
                    "CloneGuard: 引擎 %s 异常(%s: %s)，标记降级",
                    name,
                    type(res).__name__,
                    res,
                )
                engine_results[name] = ([], True)
            else:
                engine_results[name] = res
        return engine_results

    def _run_engines_sequential(
        self, py_files: list[str], timeout: int
    ) -> dict[str, tuple[list[Finding], bool] | BaseException]:
        """顺序执行引擎（asyncio 不可用时的兜底）。"""
        results: dict[str, tuple[list[Finding], bool] | BaseException] = {}
        try:
            results["echo_guard"] = self._echo_guard.detect(py_files, timeout)
        except Exception as e:  # noqa: BLE001
            results["echo_guard"] = e
        try:
            results["ast_grep"] = self._ast_grep.detect(py_files, timeout)
        except Exception as e:  # noqa: BLE001
            results["ast_grep"] = e
        return results

    # ------------------------------------------------------------------
    # 降级处理
    # ------------------------------------------------------------------

    def _handle_total_degradation(
        self, checked_files: int, degraded_engines: list[str]
    ) -> CheckResult:
        """全引擎降级——按 fail_closed 决定阻断或放行（守 blueprint §5.2）。"""
        if self._config.fail_closed:
            logger.error(
                "CloneGuard: 全引擎降级(%s)且 fail_closed=True——阻断提交（守铁律）",
                degraded_engines,
            )
            return CheckResult(
                passed=False,
                degraded=True,
                degraded_engines=degraded_engines,
                error=f"全引擎降级({degraded_engines})且 fail_closed=True——阻断提交",
                checked_files=checked_files,
            )
        logger.warning(
            "CloneGuard: 全引擎降级(%s)，fail_closed=False——降级为 warn-only（不阻断）",
            degraded_engines,
        )
        return CheckResult(
            passed=True,
            degraded=True,
            degraded_engines=degraded_engines,
            error=f"全引擎降级({degraded_engines})——warn-only 兜底",
            checked_files=checked_files,
        )

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    @staticmethod
    def _build_consensus_summary(agg_result: AggregationResult) -> dict[str, int]:
        """统计聚合结果的共识分布。"""
        summary: dict[str, int] = {"unanimous": 0, "majority": 0, "single": 0}
        for f in agg_result.findings:
            if f.consensus in summary:
                summary[f.consensus] += 1
            else:
                summary[f.consensus] = 1
        return {k: v for k, v in summary.items() if v > 0}

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
