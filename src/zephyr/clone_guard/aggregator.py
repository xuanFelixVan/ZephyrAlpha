# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.5
# [MODULE] zephyr.clone_guard.aggregator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); hashlib; math; logging
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 聚合器是多引擎结果合并的统一入口；按克隆对去重 + 多数表决 + 严重性就高；降级引擎排除出表决；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] aggregate() 永不抛异常——空输入/全降级返回空 AggregationResult
# [TESTS] tests/clone_guard/test_aggregator.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
FindingAggregator — 多引擎结果聚合器（Phase B）。

将多个引擎（Echo-Guard、reDUP、ast-grep）的检测结果合并为统一的、去重的 finding 列表。
核心算法：按克隆对分组 → 多数表决 + 严重性就高 → 返回 AggregatedFinding 列表。

核心概念
--------
- **去重键**: (source_file, source_function, existing_file, existing_function) 归一化路径后组合。
  同一克隆对被多引擎报告时自动合并为一个 AggregatedFinding。
- **多数表决**: 报告同一克隆对的引擎数 >= ceil(active_count / 2) 时为 "majority"，
  全体一致为 "unanimous"，仅 1 引擎为 "single"（少数派）。
- **严重性就高**: extract(3) > review(2) > acknowledged(1)。任一引擎判 extract → 最终 extract。
- **相似度取最大**: 各引擎相似度的最大值（最悲观估计）。
- **降级引擎排除**: degraded=True 的引擎完全排除出表决（不计入 active_count）。

Usage::

    from zephyr.clone_guard.aggregator import FindingAggregator

    aggregator = FindingAggregator()
    result = aggregator.aggregate({
        "echo_guard": ([finding1, finding2], False),
        "redup": ([finding1, finding3], False),
        "ast_grep": ([], True),  # degraded
    })
    # result.findings = [AggregatedFinding(finding1 合并后), AggregatedFinding(finding2), AggregatedFinding(finding3)]
    # finding1 被 echo_guard + redup 同时报告 → consensus="majority"
    # finding2 仅 echo_guard → consensus="single"（2 引擎活跃，1/2 < ceil(2/2)=1... 实际 1>=1 → majority）
    # finding3 仅 redup → 同上

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: aggregator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FindingAggregator
#   name_en: FindingAggregator
#   intro: 多引擎结果聚合器。
#   desc: 多引擎结果聚合器。 核心算法： 1. 过滤降级引擎 2. 按克隆对 (source, existing) 分组去重 3. 多数表决 + 严重性就高 4. 返回去重后的 Aggre…；公共方法（定义序）: aggrega…
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: FindingAggregator
#   downstream: zephyr.clone_guard.orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__: Final = ["AggregatedFinding", "AggregationResult", "FindingAggregator"]

# 严重性优先级映射——数字越大越严重
_SEVERITY_ORDER: dict[str, int] = {"extract": 3, "review": 2, "acknowledged": 1}


@dataclass(frozen=True)
class AggregatedFinding:
    """跨引擎聚合后的统一 Finding。

    在 Finding 基础上增加引擎共识元数据，用于判断 finding 的可信度。
    """

    # ── 基础字段（同 Finding）──
    finding_id: str  # 聚合后新 ID（"AGG-{short_hash}"）
    severity: str  # 最终严重性（多数表决 + 就高）
    clone_type: str
    similarity: float  # 各引擎相似度最大值
    source_file: str
    source_function: str
    source_lineno: int
    existing_file: str
    existing_function: str
    existing_lineno: int
    import_suggestion: str | None

    # ── 聚合元数据 ──
    engines: tuple[str, ...]  # 报告此 finding 的引擎列表
    engine_severities: dict[str, str]  # 各引擎独立判定的严重性
    engine_similarities: dict[str, float]  # 各引擎独立相似度
    consensus: str  # "unanimous" | "majority" | "single"
    vote_count: int  # 投票引擎数
    active_engine_count: int  # 参与表决的活跃引擎总数


@dataclass(frozen=True)
class AggregationResult:
    """聚合结果。"""

    findings: list[AggregatedFinding] = field(default_factory=list)
    degraded_engines: list[str] = field(default_factory=list)
    active_engine_count: int = 0
    total_raw_findings: int = 0  # 聚合前原始 finding 总数
    deduplicated_count: int = 0  # 去重后数量


class FindingAggregator:
    """多引擎结果聚合器。

    核心算法：
      1. 过滤降级引擎
      2. 按克隆对 (source, existing) 分组去重
      3. 多数表决 + 严重性就高
      4. 返回去重后的 AggregatedFinding 列表
    """

    def __init__(self, config: CloneGuardConfig | None = None):
        self._config = config or CloneGuardConfig()

    def aggregate(
        self,
        engine_results: dict[str, tuple[list[Finding], bool]],
    ) -> AggregationResult:
        """聚合多引擎检测结果。

        Args:
            engine_results: {engine_name: (findings, degraded)} 字典。
                - findings: Finding 列表
                - degraded: True 表示该引擎降级（不可用/超时/崩溃）

        Returns:
            AggregationResult: 去重 + 表决后的 findings + 降级引擎列表。
        """
        if not engine_results:
            return AggregationResult()

        # ── Step 1: 分离活跃引擎和降级引擎 ──
        active: dict[str, list[Finding]] = {}
        degraded_engines: list[str] = []
        total_raw = 0

        for engine, (findings, degraded) in engine_results.items():
            total_raw += len(findings)
            if degraded:
                degraded_engines.append(engine)
                logger.debug("聚合器: 引擎 %s 降级，排除出表决", engine)
            else:
                active[engine] = findings

        active_count = len(active)

        # 边界：全部降级 → 返回空（orchestrator 按 fail_closed 决定阻断或放行）
        if active_count == 0:
            logger.warning("聚合器: 全部引擎降级(%s)，返回空结果", degraded_engines)
            return AggregationResult(
                degraded_engines=degraded_engines,
                total_raw_findings=total_raw,
            )

        # ── Step 2: 按克隆对分组（去重）──
        # 键 = (source_file, source_function, existing_file, existing_function) 归一化路径
        groups: dict[tuple[str, str, str, str], list[tuple[str, Finding]]] = defaultdict(list)
        for engine, findings in active.items():
            for f in findings:
                key = _make_dedup_key(f)
                groups[key].append((engine, f))

        # ── Step 3: 每组多数表决 + 严重性就高 ──
        # 多数表决阈值：ceil(active_count / 2)
        majority_threshold = math.ceil(active_count / 2)

        aggregated: list[AggregatedFinding] = []
        for key, engine_findings in groups.items():
            aggregated_finding = _build_aggregated_finding(key, engine_findings, active_count, majority_threshold)
            aggregated.append(aggregated_finding)

        # ── Step 4: 过滤少数派（配置控制）──
        if self._config.filter_minority:
            before = len(aggregated)
            aggregated = [f for f in aggregated if f.consensus != "single"]
            filtered = before - len(aggregated)
            if filtered > 0:
                logger.info("聚合器: 过滤 %d 个少数派 findings（filter_minority=True）", filtered)

        logger.debug(
            "聚合器: %d 引擎活跃, %d 原始 findings → %d 去重后 → %d 最终",
            active_count,
            total_raw,
            len(groups),
            len(aggregated),
        )

        return AggregationResult(
            findings=aggregated,
            degraded_engines=degraded_engines,
            active_engine_count=active_count,
            total_raw_findings=total_raw,
            deduplicated_count=len(aggregated),
        )


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _normalize_path(path: str) -> str:
    """归一化路径——统一为正斜杠，去除前后空白。"""
    return path.strip().replace("\\", "/")


def _make_dedup_key(f: Finding) -> tuple[str, str, str, str]:
    """构造去重键——同一克隆对被多引擎报告时自动合并。

    键 = (source_file, source_function, existing_file, existing_function) 归一化后组合。
    ast-grep 的 existing_file 是规则文件，天然不会与克隆对冲突。
    """
    return (
        _normalize_path(f.source_file),
        f.source_function.strip(),
        _normalize_path(f.existing_file),
        f.existing_function.strip(),
    )


def _build_aggregated_finding(
    key: tuple[str, str, str, str],
    engine_findings: list[tuple[str, Finding]],
    active_count: int,
    majority_threshold: int,
) -> AggregatedFinding:
    """对单个克隆组进行多数表决 + 严重性就高，构造 AggregatedFinding。"""
    engines = tuple(e for e, _ in engine_findings)
    vote_count = len(engines)

    # ── 共识判定 ──
    if vote_count == active_count:
        consensus = "unanimous"  # 全体一致
    elif vote_count >= majority_threshold:
        consensus = "majority"  # 多数同意
    else:
        consensus = "single"  # 少数派（仅 1 引擎报告，或未达多数阈值）

    # ── 严重性就高：extract(3) > review(2) > acknowledged(1) ──
    engine_severities: dict[str, str] = {e: f.severity for e, f in engine_findings}
    final_severity = max(
        engine_severities.values(),
        key=lambda s: _SEVERITY_ORDER.get(s, 0),
    )

    # ── 相似度取最大值（最悲观估计）──
    engine_similarities: dict[str, float] = {e: f.similarity for e, f in engine_findings}
    final_similarity = max(engine_similarities.values())

    # ── 取第一个 finding 的基础字段（同组内应一致）──
    base = engine_findings[0][1]

    # ── 生成稳定 ID ──
    key_str = "|".join(key)
    short_hash = hashlib.sha256(key_str.encode("utf-8")).hexdigest()[:8]
    finding_id = f"AGG-{short_hash}"

    return AggregatedFinding(
        finding_id=finding_id,
        severity=final_severity,
        clone_type=base.clone_type,
        similarity=final_similarity,
        source_file=base.source_file,
        source_function=base.source_function,
        source_lineno=base.source_lineno,
        existing_file=base.existing_file,
        existing_function=base.existing_function,
        existing_lineno=base.existing_lineno,
        import_suggestion=base.import_suggestion,
        engines=engines,
        engine_severities=engine_severities,
        engine_similarities=engine_similarities,
        consensus=consensus,
        vote_count=vote_count,
        active_engine_count=active_count,
    )
