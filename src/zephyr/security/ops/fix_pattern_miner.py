# [BLUEPRINT] MOD-INF-055 | docs/03_modules/MOD-INF-055/
# [MODULE] zephyr.security.ops.fix_pattern_miner
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.ops.incident_pipeline; zephyr.shared.io.paths; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] event_driven
# [MATURITY] testing
# [INVARIANTS] 只产建议不落策略库（A-L2封顶，采纳human_gated）;挖掘报告append-only;命中率只观测不设目标值
# [MODIFY-GUARD] 16_ai_security_ops.md §4.4 P2-1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FixPatternMinerError(ZA-SC-0038)
# [TESTS] tests/security/ops/test_fix_pattern_miner.py
# [A_module] module_id=MOD-INF-055 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
修复模式挖掘器——Learn 回写闭环（16号文 §4.4 P2-1，MOD-INF-055 一部分）。

闭环定位：Detect（security_event_bus）→ Diagnose（failure_matcher）→
Remediate（auto_fix_engine 三通道）→ **Learn（本件）**。修复记录由
``incident_pipeline.FixPatternStore`` 以「记录优先」写入
``data/fix_patterns/pattern_index.yaml``；本件周期性挖掘这些记录：

1. **挖掘 → 修复策略库更新建议**：按 (fault_class, action_type) 聚簇统计
   频率/成功率——高频高成功率簇产 ``PROMOTE_PATTERN`` 建议（固化为模板化
   策略候选），高频低成功率簇产 ``REVIEW_PATTERN`` 建议（人工复核通道），
   Diagnose 未覆盖类别的高频簇产 ``ENRICH_DIAGNOSIS`` 建议（补诊断模式，
   让下次 Diagnose 直接命中）。**只产建议不落库**——A-L2 封顶（16号文
   §4.4 P2-2 / ops_maturity），采纳与写库走 human_gated，本件 MUST NOT
   自动改 pattern_index.yaml。
2. **Diagnose 匹配命中率统计**：记录类别被策略库 ``patterns`` 节覆盖即记
   Diagnose 命中，输出总体命中率 + 按 fault_class 分解。**指标只观测不设
   目标值**（P2-1 验收口径原文）。
3. **留痕**：每次挖掘产 ``MiningReport`` append-only 落盘
   ``.runtime/security_ops/pattern_mining_reports.jsonl``（命中率可观测的
   载体；仪表板消费该文件）。

与既有 ``auto_fix_engine/fix_pattern_miner.py``（MOD-INF-031，SQLite
fix_actions 表挖掘）数据源不同——本件挖 16号文知识库 YAML 记录，是安全
运维闭环的 Learn 件；两者互补不替代。周期调度属外部（Windows 任务计划），
本件提供 ``run_once()`` 单次挖掘入口；LLM/DB/网络不在本模块。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: records 参数
#   fields: 参数 records，类型注解 Sequence[Any]
#   code: fix_pattern_miner.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: patterns 参数
#   fields: 参数 patterns（无注解）
#   code: fix_pattern_miner.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: fix_pattern_miner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① mine_records
#   name_en: mine_records
#   intro: 纯内存挖掘：修复记录 + 模式库覆盖 → 命中率统计 + 策略库更新建议。
#   desc: 纯内存挖掘：修复记录 + 模式库覆盖 → 命中率统计 + 策略库更新建议。 - 非 mapping 记录跳过并计数（``skipped_records``，fail-visibl…；源码 L195-L303
#   inputs: records patterns config
#   outputs: MiningReport
# - id: A2
#   name_zh: ② FixPatternMiner
#   name_en: FixPatternMiner
#   intro: Learn 回写闭环挖掘器：读知识库记录 → 挖掘 → 报告 append-only 落盘。
#   desc: Learn 回写闭环挖掘器：读知识库记录 → 挖掘 → 报告 append-only 落盘。 不变量：只产建议不落策略库（A-L2 封顶，采纳 human_gated）；挖掘报告…；公共方法（定义序）: config,…
#   inputs: config
#   outputs: 返回值
#   （注：A2 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: MiningReport
#   name_en: MiningReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Final

from zephyr.security.ops.incident_pipeline import FixPatternStore
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_MIN_FREQUENCY",
    "DEFAULT_PROMOTE_SUCCESS_RATE",
    "DEFAULT_REVIEW_SUCCESS_RATE",
    "DiagnoseHitStats",
    "FixPatternMiner",
    "FixPatternMinerError",
    "MinerConfig",
    "MiningReport",
    "StrategySuggestion",
    "SuggestionKind",
    "mine_records",
]

DEFAULT_STORE_DIR: Final[Path] = REPO_ROOT / "data" / "fix_patterns"
DEFAULT_RUNTIME_DIR: Final[Path] = REPO_ROOT / ".runtime" / "security_ops"
REPORTS_FILENAME: Final[str] = "pattern_mining_reports.jsonl"
DEFAULT_MIN_FREQUENCY: Final[int] = 3
DEFAULT_PROMOTE_SUCCESS_RATE: Final[float] = 0.8
DEFAULT_REVIEW_SUCCESS_RATE: Final[float] = 0.5
SUCCESS_STATUS: Final[str] = "completed"


class FixPatternMinerError(Exception):
    """ZA-SC-0038: 修复模式挖掘操作非法（知识库不可读/记录集非法）。"""

    error_code = "ZA-SC-0038"


class SuggestionKind(str, Enum):
    """修复策略库更新建议类别（只产建议，采纳 human_gated）。"""

    PROMOTE_PATTERN = "promote_pattern"
    REVIEW_PATTERN = "review_pattern"
    ENRICH_DIAGNOSIS = "enrich_diagnosis"


@dataclass(frozen=True)
class MinerConfig:
    """挖掘配置（参数收敛 dataclass，默认路径 = 生产落点）。"""

    store_dir: Path = DEFAULT_STORE_DIR
    runtime_dir: Path = DEFAULT_RUNTIME_DIR
    min_frequency: int = DEFAULT_MIN_FREQUENCY
    promote_success_rate: float = DEFAULT_PROMOTE_SUCCESS_RATE
    review_success_rate: float = DEFAULT_REVIEW_SUCCESS_RATE
    reports_filename: str = REPORTS_FILENAME


@dataclass(frozen=True)
class StrategySuggestion:
    """单条修复策略库更新建议（建议态，不落库）。"""

    kind: SuggestionKind
    cluster_key: str
    frequency: int
    success_rate: float
    rationale: str
    sample_targets: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DiagnoseHitStats:
    """Diagnose 匹配命中率统计（只观测不设目标值）。"""

    total_records: int
    matched_records: int
    hit_rate: float
    by_fault_class: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class MiningReport:
    """单次挖掘产出（append-only 落盘的可观测载体）。"""

    report_id: str
    ts: str
    total_records: int
    skipped_records: int
    diagnose: DiagnoseHitStats
    suggestions: tuple[StrategySuggestion, ...] = field(default_factory=tuple)


def _cluster_key(record: Mapping[str, Any]) -> str:
    return f"{record.get('fault_class', '')}|{record.get('action_type', '')}"


def mine_records(
    records: Sequence[Any],
    *,
    patterns: Sequence[Mapping[str, Any]] = (),
    config: MinerConfig | None = None,
) -> MiningReport:
    """纯内存挖掘：修复记录 + 模式库覆盖 → 命中率统计 + 策略库更新建议。

    - 非 mapping 记录跳过并计数（``skipped_records``，fail-visible 不静默吞）；
    - 成功口径：``action_status == "completed"``（incident_pipeline 落库口径）；
    - Diagnose 命中口径：记录 ``category`` 非空且被 ``patterns`` 节某条
      ``category`` 覆盖（FailureMatcher 冷启动模式携带 category 字段）；
    - 建议阈值：频率 ≥ ``min_frequency`` 才产建议；成功率 ≥ promote 阈值产
      PROMOTE，< review 阈值产 REVIEW，中间带（观察区）不产建议；类别未被
      模式库覆盖的高频簇产 ENRICH_DIAGNOSIS。
    """
    cfg = config or MinerConfig()
    covered_categories = {str(pat.get("category", "")) for pat in patterns if isinstance(pat, Mapping)} - {""}

    valid: list[Mapping[str, Any]] = []
    skipped = 0
    for rec in records:
        if isinstance(rec, Mapping):
            valid.append(rec)
        else:
            skipped += 1

    matched = sum(1 for rec in valid if str(rec.get("category", "")) in covered_categories)
    total = len(valid)
    hit_rate = matched / total if total else 0.0

    by_class_total: dict[str, int] = {}
    by_class_matched: dict[str, int] = {}
    for rec in valid:
        fault_class = str(rec.get("fault_class", ""))
        by_class_total[fault_class] = by_class_total.get(fault_class, 0) + 1
        if str(rec.get("category", "")) in covered_categories:
            by_class_matched[fault_class] = by_class_matched.get(fault_class, 0) + 1
    by_fault_class = {fc: by_class_matched.get(fc, 0) / count for fc, count in sorted(by_class_total.items())}

    clusters: dict[str, list[Mapping[str, Any]]] = {}
    for rec in valid:
        clusters.setdefault(_cluster_key(rec), []).append(rec)

    suggestions: list[StrategySuggestion] = []
    for key, cluster in sorted(clusters.items()):
        frequency = len(cluster)
        if frequency < cfg.min_frequency:
            continue
        succeeded = sum(1 for rec in cluster if rec.get("action_status") == SUCCESS_STATUS)
        success_rate = succeeded / frequency
        sample_targets = tuple(str(rec.get("target", "")) for rec in cluster[:5])
        category = str(cluster[0].get("category", ""))
        if success_rate >= cfg.promote_success_rate:
            suggestions.append(
                StrategySuggestion(
                    kind=SuggestionKind.PROMOTE_PATTERN,
                    cluster_key=key,
                    frequency=frequency,
                    success_rate=success_rate,
                    rationale=(
                        f"高频（{frequency} 次）高成功率（{success_rate:.0%}）修复簇——"
                        "建议固化为模板化策略候选（人工采纳后入库）"
                    ),
                    sample_targets=sample_targets,
                )
            )
        elif success_rate < cfg.review_success_rate:
            suggestions.append(
                StrategySuggestion(
                    kind=SuggestionKind.REVIEW_PATTERN,
                    cluster_key=key,
                    frequency=frequency,
                    success_rate=success_rate,
                    rationale=(
                        f"高频（{frequency} 次）低成功率（{success_rate:.0%}）修复簇——"
                        "建议人工复核该修复通道（模板失效/输入漂移）"
                    ),
                    sample_targets=sample_targets,
                )
            )
        if category and category not in covered_categories:
            suggestions.append(
                StrategySuggestion(
                    kind=SuggestionKind.ENRICH_DIAGNOSIS,
                    cluster_key=f"category:{category}",
                    frequency=frequency,
                    success_rate=success_rate,
                    rationale=(
                        f"类别 {category!r} 高频（{frequency} 次）但未被诊断模式库覆盖——"
                        "建议补充诊断模式，让下次 Diagnose 直接命中"
                    ),
                    sample_targets=sample_targets,
                )
            )

    return MiningReport(
        report_id=uuid.uuid4().hex[:12],
        ts=now_iso(),
        total_records=total,
        skipped_records=skipped,
        diagnose=DiagnoseHitStats(
            total_records=total,
            matched_records=matched,
            hit_rate=hit_rate,
            by_fault_class=by_fault_class,
        ),
        suggestions=tuple(suggestions),
    )


def _report_to_dict(report: MiningReport) -> dict[str, Any]:
    blob = asdict(report)
    blob["diagnose"] = asdict(report.diagnose)
    blob["suggestions"] = [{**asdict(sug), "kind": sug.kind.value} for sug in report.suggestions]
    return blob


class FixPatternMiner:
    """Learn 回写闭环挖掘器：读知识库记录 → 挖掘 → 报告 append-only 落盘。

    不变量：只产建议不落策略库（A-L2 封顶，采纳 human_gated）；挖掘报告
    append-only；命中率只观测不设目标值。周期调度属外部，本件提供
    ``run_once()`` 单次挖掘入口。
    """

    def __init__(self, config: MinerConfig) -> None:
        self._config = config
        self._store = FixPatternStore(config.store_dir)

    @property
    def config(self) -> MinerConfig:
        return self._config

    def load_kb(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """读取知识库（records + patterns 两节；schema 经 FixPatternStore 校验）。"""
        try:
            index = self._store.read_pattern_index()
        except Exception as exc:
            raise FixPatternMinerError(f"修复策略知识库不可读: {exc}") from exc
        records = index.get("records") or []
        patterns = index.get("patterns") or []
        return list(records), list(patterns)

    def mine(
        self,
        records: Sequence[Any] | None = None,
        *,
        patterns: Sequence[Mapping[str, Any]] | None = None,
    ) -> MiningReport:
        """挖掘一轮：records/patterns 缺省时从知识库加载。"""
        if records is None or patterns is None:
            kb_records, kb_patterns = self.load_kb()
            if records is None:
                records = kb_records
            if patterns is None:
                patterns = kb_patterns
        return mine_records(records, patterns=patterns, config=self._config)

    def run_once(self) -> MiningReport:
        """单次挖掘入口（周期任务调用）：挖掘 + 报告 append-only 落盘。"""
        report = self.mine()
        self._config.runtime_dir.mkdir(parents=True, exist_ok=True)
        path = self._config.runtime_dir / self._config.reports_filename
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(_report_to_dict(report), ensure_ascii=False, separators=(",", ":")) + "\n")
        logger.info(
            "修复模式挖掘完成: report_id=%s records=%d hit_rate=%.2f suggestions=%d → %s",
            report.report_id,
            report.total_records,
            report.diagnose.hit_rate,
            len(report.suggestions),
            path,
        )
        return report
