# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] zephyr.clone_guard.orchestrator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig, load_config); zephyr.clone_guard.engines.echo_guard_adapter (EchoGuardAdapter, Finding); zephyr.clone_guard.engines.ast_grep_adapter (AstGrepAdapter); zephyr.clone_guard.engines.redup_adapter (RedupAdapter); zephyr.clone_guard.aggregator (FindingAggregator, AggregatedFinding, AggregationResult); asyncio; concurrent.futures; fnmatch; logging
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.capability_overlap_gate; zephyr.clone_guard (re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 统一调度入口——Phase B 并发调度 Echo-Guard + ast-grep + reDUP（asyncio.gather + run_in_executor 桥接同步适配器）；check() 永不抛异常；全引擎降级时按 fail_closed 决定阻断或放行；部分降级 warn+继续；extract 级硬阻断=必须合并；结果经 FindingAggregator 去重+多数表决+严重性就高
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() 永不抛异常——适配器异常被 run_in_executor 捕获并归一为 ([], degraded=True)；全降级按 fail_closed 决定 passed；asyncio.run 在已有事件循环时回退顺序执行
# [TESTS] tests/clone_guard/test_orchestrator.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CloneGuard 统一编排器——Phase B（多引擎并发 + 结果聚合）。

统一调度入口，对 CAPABILITY-OVERLAP 门禁暴露 check() 方法。
Phase B 起：asyncio.gather 并发调度 Echo-Guard + ast-grep + reDUP，结果经
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: orchestrator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CloneGuardOrchestrator
#   name_en: CloneGuardOrchestrator
#   intro: CloneGuard 统一编排器。
#   desc: CloneGuard 统一编排器。 Phase A: 仅调度 Echo-Guard Phase B: + ast-grep + reDUP 并发 + FindingAggrega…；公共方法（定义序）: check…
#   inputs: repo_root config
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: CloneGuardOrchestrator
#   downstream: zephyr.gov_enforcement.commit_gates.capability_overlap_gate; zephyr.clone_guard…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import asyncio
import fnmatch
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from zephyr.clone_guard.aggregator import (
    AggregatedFinding,
    AggregationResult,
    FindingAggregator,
)
from zephyr.clone_guard.config import CloneGuardConfig, load_config
from zephyr.clone_guard.engines.ast_grep_adapter import AstGrepAdapter
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter, Finding
from zephyr.clone_guard.engines.mcrit_adapter import McritAdapter
from zephyr.clone_guard.engines.redup_adapter import RedupAdapter
from zephyr.clone_guard.engines.relate_adapter import RelateAdapter
from zephyr.clone_guard.engines.vendetect_adapter import VendetectAdapter

logger = logging.getLogger(__name__)

__all__ = [
    "AggregatedFinding",
    "AuditResult",
    "CheckResult",
    "CloneGuardOrchestrator",
    "CompareResult",
    "Finding",
]


@runtime_checkable
class _EngineAdapter(Protocol):
    """引擎适配器统一接口（detect/health_check）。"""

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]: ...

    def health_check(self) -> bool: ...


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


@dataclass
class AuditResult:
    """L2 周期审计结果（架构裁定：可运行核心闭环）。

    不写 depgraph、不新增 reconciler、不用 cron（守裁定）。
    结果持久化到 .runtime/clone_guard_audit/audit_<ts>.json（派生产物）。

    Attributes:
        findings: 聚合后的 AggregatedFinding 列表（全量，含 review/acknowledged）
        degraded_engines: 降级引擎名列表
        active_engine_count: 参与表决的活跃引擎数
        health_score: A-F 评分（A=无债，F=extract 级债严重）
        refactoring_plan: 重构建议列表（基于 extract 级 findings 生成）
        checked_files: 实际被检测的文件数
        timestamp: 审计时间戳（ISO 格式）
        persisted_path: 持久化 JSON 路径（None=未持久化）
    """

    findings: list[AggregatedFinding] = field(default_factory=list)
    degraded_engines: list[str] = field(default_factory=list)
    active_engine_count: int = 0
    health_score: str = "A"
    refactoring_plan: list[str] = field(default_factory=list)
    checked_files: int = 0
    timestamp: str = ""
    persisted_path: str | None = None


@dataclass
class CompareResult:
    """L3 跨边界审计结果。

    Attributes:
        findings: 跨仓库聚合后的 AggregatedFinding 列表
        cross_repo_findings: clone_type=vendored 的跨仓库 findings（合规风险子集）
        degraded_engines: 降级引擎名列表
        active_engine_count: 参与表决的活跃引擎数
        remote_url: 比对远程仓库 URL
        checked_files: 实际被检测的文件数
    """

    findings: list[AggregatedFinding] = field(default_factory=list)
    cross_repo_findings: list[AggregatedFinding] = field(default_factory=list)
    degraded_engines: list[str] = field(default_factory=list)
    active_engine_count: int = 0
    remote_url: str = ""
    checked_files: int = 0


class CloneGuardOrchestrator:
    """CloneGuard 统一编排器。

    Phase A: 仅调度 Echo-Guard
    Phase B: + ast-grep + reDUP 并发 + FindingAggregator 聚合（当前）
    Phase C: + mcrit + Vendetect + relate（audit/compare 方法）
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or load_config(self._repo_root)
        # L1 引擎（pre-commit 拦截）
        self._echo_guard = EchoGuardAdapter(self._repo_root, self._config)
        self._ast_grep = AstGrepAdapter(self._repo_root, self._config)
        self._redup = RedupAdapter(self._repo_root, self._config)
        # L2/L3 引擎（Phase C；按 config.*_enabled 过滤参与调度）
        self._mcrit = McritAdapter(self._repo_root, self._config)
        self._vendetect = VendetectAdapter(self._repo_root, self._config)
        self._relate = RelateAdapter(self._repo_root, self._config)
        self._aggregator = FindingAggregator(self._config)

    # ------------------------------------------------------------------
    # 引擎集构造（按 config.*_enabled 过滤）
    # ------------------------------------------------------------------

    def _build_l1_engines(self) -> dict[str, _EngineAdapter]:
        """构造 L1 pre-commit 引擎集（Echo-Guard + ast-grep + reDUP）。

        守 blueprint §5.1：仅快速引擎参与 L1，按 config.*_enabled 过滤。
        reDUP 在 L1 用 changed-only 增量模式（config.redup_mode="changed-only"）。
        """
        engines: dict[str, _EngineAdapter] = {}
        if self._config.echo_guard_enabled:
            engines["echo_guard"] = self._echo_guard
        if self._config.ast_grep_enabled:
            engines["ast_grep"] = self._ast_grep
        if self._config.redup_enabled:
            engines["redup"] = self._redup
        return engines

    def _build_l2_engines(self) -> dict[str, _EngineAdapter]:
        """构造 L2 周期审计引擎集（mcrit + echo_guard + redup + ast_grep）。

        守 blueprint §6.1：L2 全量审计，用重引擎精检。mcrit 默认 disabled，
        启用后作为索引底座加速；echo_guard/redup/ast_grep 复用 L1 引擎做精检。
        """
        engines: dict[str, _EngineAdapter] = {}
        if self._config.mcrit_enabled:
            engines["mcrit"] = self._mcrit
        if self._config.echo_guard_enabled:
            engines["echo_guard"] = self._echo_guard
        if self._config.redup_enabled:
            engines["redup"] = self._redup
        if self._config.ast_grep_enabled:
            engines["ast_grep"] = self._ast_grep
        return engines

    def _build_l3_engines(self) -> dict[str, _EngineAdapter]:
        """构造 L3 跨边界审计引擎集（redup + vendetect + relate）。

        守 blueprint §6.1：L3 跨仓库合规审计。vendetect 检测 vendored 代码 +
        许可证合规；relate 快速预筛加速；redup 语义克隆精检。
        """
        engines: dict[str, _EngineAdapter] = {}
        if self._config.redup_enabled:
            engines["redup"] = self._redup
        if self._config.vendetect_enabled:
            engines["vendetect"] = self._vendetect
        if self._config.relate_enabled:
            engines["relate"] = self._relate
        return engines

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

        # 2. 构造 L1 引擎集（按 config 过滤）
        engines = self._build_l1_engines()
        if not engines:
            logger.warning("CloneGuard: 无启用引擎（全在 config 中禁用），放行")
            return CheckResult(passed=True, checked_files=len(py_files))

        # 3. 并发调度多引擎
        engine_results = self._run_engines_concurrent(engines, py_files)

        # 4. 聚合（去重 + 多数表决 + 严重性就高）
        agg_result = self._aggregator.aggregate(engine_results)

        # 5. 全引擎降级 → fail_closed 决定
        if agg_result.active_engine_count == 0:
            return self._handle_total_degradation(len(py_files), agg_result.degraded_engines)

        # 6. 部分降级 → warn + 继续（用活跃引擎结果）
        if agg_result.degraded_engines:
            logger.warning(
                "CloneGuard: 引擎 %s 降级，仅用 %d 个活跃引擎结果聚合",
                agg_result.degraded_engines,
                agg_result.active_engine_count,
            )

        # 7. 严重性判定
        block_findings = [f for f in agg_result.findings if f.severity in self._config.block_severities]
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
    # L2 周期审计 + L3 跨边界审计（Phase C，架构裁定：可运行核心闭环）
    # ------------------------------------------------------------------

    def audit(self, files: list[str]) -> AuditResult:
        """L2 周期审计——全量检测代码克隆累积债（架构裁定实现）。

        调度 L2 引擎集（mcrit + echo_guard + redup + ast_grep），聚合后生成
        health_score（A-F）+ refactoring_plan，结果持久化到
        .runtime/clone_guard_audit/audit_<ts>.json（派生产物，不入 git）。

        L2 扫描模式（守蓝图 §3.4 阶段2）：use_scan=True 经 _invoke_engine 对
        echo_guard 调 ``echo-guard scan``（全仓库冗余扫描，无文件参数，规避
        Windows CreateProcess 命令行上限）；ast-grep 仍走 detect()（已用
        ``_chunk_files`` 分批兜底）；redup/mcrit 回退 detect()。

        守裁定：不写 depgraph、不新增 reconciler、不用 cron（事件触发）。
        AI 冷启动可通过 MCP 工具 clone_guard.audit_status 查询上次结果。

        Args:
            files: 待审计文件路径列表（相对路径，通常为全量 src/）。

        Returns:
            AuditResult: 含 findings + health_score + refactoring_plan + 持久化路径。
        """
        py_files = self._filter_files(files)
        timestamp = datetime.now().isoformat(timespec="seconds")

        if not py_files:
            return AuditResult(timestamp=timestamp, checked_files=0)

        engines = self._build_l2_engines()
        if not engines:
            logger.warning("CloneGuard.audit: 无启用 L2 引擎，返回空审计")
            return AuditResult(timestamp=timestamp, checked_files=len(py_files))

        engine_results = self._run_engines_concurrent(
            engines, py_files, timeout=self._config.audit_timeout_sec, use_scan=True
        )
        agg_result = self._aggregator.aggregate(engine_results)

        health_score = self._compute_health_score(agg_result)
        refactoring_plan = self._build_refactoring_plan(agg_result.findings)

        result = AuditResult(
            findings=agg_result.findings,
            degraded_engines=agg_result.degraded_engines,
            active_engine_count=agg_result.active_engine_count,
            health_score=health_score,
            refactoring_plan=refactoring_plan,
            checked_files=len(py_files),
            timestamp=timestamp,
        )

        # 持久化（派生产物，I-GOV-1 离库铁律：写 .runtime/ 已 gitignore）
        result.persisted_path = self._persist_audit_result(result)
        return result

    def compare(self, files: list[str], remote_url: str | None = None) -> CompareResult:
        """L3 跨边界审计——检测跨仓库 vendored 代码 + 许可证合规。

        调度 L3 引擎集（redup + vendetect + relate），分离 cross_repo_findings
        （clone_type=vendored 的合规风险子集）。vendetect 检测 AGPL 等高风险
        许可证 → extract 级硬阻断信号（由调用方决定是否阻断）。

        Args:
            files: 待检测文件路径列表（相对路径）。
            remote_url: 比对远程仓库 URL（None 时用 config.vendetect_remote_url）。

        Returns:
            CompareResult: 含 findings + cross_repo_findings（合规子集）。
        """
        py_files = self._filter_files(files)
        url = remote_url or self._config.vendetect_remote_url or ""

        if not py_files:
            return CompareResult(remote_url=url, checked_files=0)

        engines = self._build_l3_engines()
        if not engines:
            logger.warning("CloneGuard.compare: 无启用 L3 引擎，返回空比对")
            return CompareResult(remote_url=url, checked_files=len(py_files))

        engine_results = self._run_engines_concurrent(engines, py_files, timeout=self._config.compare_timeout_sec)
        agg_result = self._aggregator.aggregate(engine_results)

        # 分离跨仓库合规风险子集（vendetect 的 clone_type=vendored）
        cross_repo = [f for f in agg_result.findings if f.clone_type == "vendored"]

        return CompareResult(
            findings=agg_result.findings,
            cross_repo_findings=cross_repo,
            degraded_engines=agg_result.degraded_engines,
            active_engine_count=agg_result.active_engine_count,
            remote_url=url,
            checked_files=len(py_files),
        )

    @staticmethod
    def _compute_health_score(agg_result: AggregationResult) -> str:
        """health_score A-F 评分（基于 extract/review 数量映射）。

        - A: 无 findings
        - B: 仅 acknowledged/review 且 review < 5
        - C: review >= 5 或有 1 个 extract
        - D: 2-4 个 extract
        - F: >= 5 个 extract（债严重）
        """
        if not agg_result.findings:
            return "A"
        extract_count = sum(1 for f in agg_result.findings if f.severity == "extract")
        review_count = sum(1 for f in agg_result.findings if f.severity == "review")
        if extract_count == 0 and review_count < 5:
            return "B"
        if extract_count <= 1:
            return "C"
        if extract_count < 5:
            return "D"
        return "F"

    @staticmethod
    def _build_refactoring_plan(findings: list[AggregatedFinding]) -> list[str]:
        """基于 extract 级 findings 生成重构建议（供 AI 冷启动看见技术债）。"""
        plan: list[str] = []
        extract_findings = [f for f in findings if f.severity == "extract"]
        for f in extract_findings:
            suggestion = f.import_suggestion or f.existing_function
            plan.append(
                f"[{f.consensus}] {f.source_file}:{f.source_function} → "
                f"复用 {f.existing_file}:{f.existing_function}" + (f" (suggestion: {suggestion})" if suggestion else "")
            )
        return plan

    def _persist_audit_result(self, result: AuditResult) -> str | None:
        """持久化审计结果到 .runtime/clone_guard_audit/（派生产物，已 gitignore）。

        守 I-GOV-1（派生产物离库铁律）：写入 .runtime/ 目录，不入 git。
        返回写入的文件路径；失败时返回 None（不阻断审计）。
        """
        audit_dir = self._repo_root / ".runtime" / "clone_guard_audit"
        try:
            audit_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning("CloneGuard: 创建审计目录失败(%s)，跳过持久化", e)
            return None

        # 文件名：audit_YYYYMMDD_HHMMSS.json（可排序）
        ts_slug = result.timestamp.replace(":", "").replace("-", "")[:15]
        path = audit_dir / f"audit_{ts_slug}.json"

        payload = {
            "timestamp": result.timestamp,
            "checked_files": result.checked_files,
            "active_engine_count": result.active_engine_count,
            "degraded_engines": result.degraded_engines,
            "health_score": result.health_score,
            "refactoring_plan": result.refactoring_plan,
            "findings_count": len(result.findings),
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "severity": f.severity,
                    "clone_type": f.clone_type,
                    "similarity": f.similarity,
                    "source_file": f.source_file,
                    "source_function": f.source_function,
                    "source_lineno": f.source_lineno,
                    "existing_file": f.existing_file,
                    "existing_function": f.existing_function,
                    "existing_lineno": f.existing_lineno,
                    "engines": list(f.engines),
                    "consensus": f.consensus,
                    "vote_count": f.vote_count,
                }
                for f in result.findings
            ],
        }
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.debug("CloneGuard: 审计结果已持久化到 %s", path)
            return str(path.relative_to(self._repo_root)).replace("\\", "/")
        except OSError as e:
            logger.warning("CloneGuard: 持久化审计结果失败(%s)", e)
            return None

    def load_latest_audit(self) -> dict | None:
        """读取最近一次审计结果（供 MCP audit_status 工具复用，6层闭环·可达性）。

        返回最新 audit_*.json 的解析字典；无历史记录时返回 None。
        """
        audit_dir = self._repo_root / ".runtime" / "clone_guard_audit"
        if not audit_dir.exists():
            return None
        audit_files = sorted(audit_dir.glob("audit_*.json"))
        if not audit_files:
            return None
        try:
            return json.loads(audit_files[-1].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("CloneGuard: 读取最近审计结果失败(%s)", e)
            return None

    # ------------------------------------------------------------------
    # 并发调度（通用——接受 engines 字典，供 check()/audit()/compare() 复用）
    # ------------------------------------------------------------------

    @staticmethod
    def _invoke_engine(
        adapter: _EngineAdapter,
        py_files: list[str],
        timeout: int,
        use_scan: bool,
    ) -> tuple[list[Finding], bool]:
        """调度单个引擎——L2 审计时优先 scan()（全仓库扫描，规避命令行长度上限）。

        use_scan=True 且适配器实现了 scan()（当前仅 EchoGuardAdapter）时调用
        ``scan(timeout)`` 而非 ``detect(py_files, timeout)``。无 scan() 的引擎
        （ast-grep 已用 ``_chunk_files`` 内部分批；redup/mcrit）回退 detect()。

        守 L2 改造裁定（蓝图 §3.4 阶段2）：echo-guard L2 用 ``scan`` 命令治本——
        全仓库冗余扫描不取文件参数，规避 Windows CreateProcess 32767 字符上限；
        ast-grep 用 ``_chunk_files`` 兜底（commit 5d7161ea）。L1 check() 传
        use_scan=False（staged 文件少，无上限问题，走 detect 快速路径）。

        Args:
            adapter: 引擎适配器实例。
            py_files: 待检测文件列表（use_scan=True 时仅传给回退 detect 的引擎）。
            timeout: 超时秒数。
            use_scan: True=优先 scan()（L2 审计），False=统一 detect()（L1/L3）。

        Returns:
            (findings, degraded) 元组。
        """
        if use_scan:
            scan_fn = getattr(adapter, "scan", None)
            if callable(scan_fn):
                return scan_fn(timeout=timeout)
        return adapter.detect(py_files, timeout)

    def _run_engines_concurrent(
        self,
        engines: dict[str, _EngineAdapter],
        py_files: list[str],
        timeout: int | None = None,
        use_scan: bool = False,
    ) -> dict[str, tuple[list[Finding], bool]]:
        """asyncio.gather 并发调度给定引擎集（守 blueprint §5.1）。

        适配器调用是同步阻塞（subprocess.run），通过 run_in_executor 提交线程池
        实现真并发。return_exceptions=True 保证单引擎异常被捕获归一为
        ([], degraded=True)，不影响其他引擎。use_scan=True 时经 _invoke_engine
        对实现了 scan() 的引擎（echo_guard）走全仓库扫描路径（L2 治本）。

        Args:
            engines: {engine_name: adapter} 字典（已按 config 过滤）。
            py_files: 待检测文件列表。
            timeout: 超时秒数（None 时用 config.pre_commit_timeout_sec）。
            use_scan: True=L2 审计模式（echo_guard 走 scan，其余回退 detect）。

        Returns:
            {engine_name: (findings, degraded)} 字典。
        """
        if not engines:
            return {}
        timeout_sec = timeout or self._config.pre_commit_timeout_sec

        async def _gather_all(executor: ThreadPoolExecutor):
            loop = asyncio.get_running_loop()
            tasks = {
                name: loop.run_in_executor(executor, self._invoke_engine, adapter, py_files, timeout_sec, use_scan)
                for name, adapter in engines.items()
            }
            raw = await asyncio.gather(*tasks.values(), return_exceptions=True)
            return dict(zip(tasks.keys(), raw, strict=True))

        try:
            raw_results = asyncio.run(
                _gather_all(ThreadPoolExecutor(max_workers=max(4, len(engines)), thread_name_prefix="clone-guard"))
            )
        except RuntimeError:
            # 已有事件循环在跑（如嵌套 async 上下文）——回退顺序执行
            logger.debug("CloneGuard: 检测到已有事件循环，回退顺序执行引擎")
            raw_results = self._run_engines_sequential(engines, py_files, timeout_sec, use_scan)

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

    @staticmethod
    def _run_engines_sequential(
        engines: dict[str, _EngineAdapter],
        py_files: list[str],
        timeout: int,
        use_scan: bool = False,
    ) -> dict[str, tuple[list[Finding], bool] | BaseException]:
        """顺序执行引擎（asyncio 不可用时的兜底，保留 use_scan 语义与并发路径一致）。"""
        results: dict[str, tuple[list[Finding], bool] | BaseException] = {}
        for name, adapter in engines.items():
            try:
                results[name] = CloneGuardOrchestrator._invoke_engine(adapter, py_files, timeout, use_scan)
            except Exception as e:  # noqa: BLE001
                results[name] = e
        return results

    # ------------------------------------------------------------------
    # 降级处理
    # ------------------------------------------------------------------

    def _handle_total_degradation(self, checked_files: int, degraded_engines: list[str]) -> CheckResult:
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
