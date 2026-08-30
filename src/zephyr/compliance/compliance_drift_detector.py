# [BLUEPRINT] MOD-CMP-016 | docs/03_modules/_domain_compliance/compliance_drift_detector/blueprint.md
# [MODULE] zephyr.compliance.compliance_drift_detector
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] 无（协议核心纯内存；clock/alert_sink/evidence_sink/时段判定 全注入；仅 stdlib）
# [CONSUMERS] 运行时装配批（基线由配置中心装配 / AL-P3 告警接 alert 路由 / 整改任务入人工队列）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 仅非交易时段运行(注入判定,交易时段Fail-Closed); 基线须先登记方可比对; diff键确定性排序(声明缺失/值漂移/未申报生效三类); 漂移→AL-P3告警+证据快照+整改任务三联动; 整改任务按漂移键序确定性生成; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/compliance_drift_detector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ComplianceDriftError(占位 ZA-CMP-UNREGISTERED-COMPLIANCE-DRIFT)——基线未登记/空基线/运行时快照非法/交易时段运行时抛
# [TESTS] tests/compliance/test_compliance_drift_detector.py
# [A_module] module_id=MOD-CMP-016 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



ComplianceDriftDetector — 合规漂移检测器（MOD-CMP-016）。

B14-04656（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-007，A9 M66-NEW-03；
canonical 承接 CAND-CMP-004 归并语义）：合规规则声明与运行时生效参数/代码
路径**定期比对**（基线快照 + diff）+ 漂移 → **AL-P3 告警** + **证据快照**
（差异清单）+ **整改任务生成** + **仅非交易时段运行**（时段判定注入）。

设计要点：
- **纯内存/DI**：时钟、告警汇、证据汇、非交易时段判定全部注入；运行时
  快照由调用方经 provider 注入（不读配置中心不触网）。
- **三联动**：检出漂移 ⇒ (1) AL-P3 告警 (2) 证据快照（差异清单 frozen）
  (3) 逐项整改任务（确定性 task_id 与建议文案）。
- **Fail-Closed**：基线未登记/空基线/provider 返回非 Mapping/交易时段
  调用一律抛 ComplianceDriftError，绝不静默跳过比对。
- **确定性**：diff 按键排序（声明缺失 / 值漂移 / 未申报生效三类同键序）；
  同输入必同输出。

查重分工：gov_drift/config_consistency=治理域配置一致性族（无合规 AL-P3
联动与整改任务语义）；配置中心 MOD-INF-091=基线供方（本件只消费注入基线，
不重建配置中心）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: compliance_drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: compliance_drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: evidence_sink 参数
#   fields: 参数 evidence_sink（无注解）
#   code: compliance_drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: is_non_trading_time 参数
#   fields: 参数 is_non_trading_time（无注解）
#   code: compliance_drift_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ComplianceDriftDetector
#   name_en: ComplianceDriftDetector
#   intro: 合规漂移检测器（基线 diff + AL-P3 告警 + 证据快照 + 整改任务）。
#   desc: 合规漂移检测器（基线 diff + AL-P3 告警 + 证据快照 + 整改任务）。 Args: clock: 时钟注入。 alert_sink: AL-P3 告警汇注入；Non…；公共方法（定义序）: set_bas…
#   inputs: clock alert_sink evidence_sink is_non_trading_time
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: ComplianceDriftDetector
#   downstream: 运行时装配批（基线由配置中心装配 / AL-P3 告警接 alert 路由 / 整改任务入人工队列）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AlertLevel",
    "ComplianceDriftDetector",
    "ComplianceDriftError",
    "DriftAlert",
    "DriftEvidence",
    "DriftItem",
    "DriftReport",
    "RemediationTask",
]


class ComplianceDriftError(Exception):
    """合规漂移检测输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-CMP-UNREGISTERED-COMPLIANCE-DRIFT。
    """


class AlertLevel(str, Enum):
    """告警级别（词表闭合）。"""

    AL_P3 = "AL-P3"


@dataclass(frozen=True)
class DriftItem:
    """单项漂移（键确定性；declared/actual 原样留痕）。"""

    key: str
    declared: object  # 基线声明值；未申报生效时为 "<UNDECLARED>"
    actual: object  # 运行时生效值；声明缺失时为 "<MISSING>"


@dataclass(frozen=True)
class DriftAlert:
    """AL-P3 告警载荷。"""

    level: AlertLevel
    keys: tuple[str, ...]
    raised_at: datetime.datetime


@dataclass(frozen=True)
class DriftEvidence:
    """证据快照（差异清单，frozen）。"""

    items: tuple[DriftItem, ...]
    taken_at: datetime.datetime


@dataclass(frozen=True)
class RemediationTask:
    """整改任务（人工处置队列条目）。"""

    task_id: str
    key: str
    declared: object
    actual: object
    suggestion: str
    created_at: datetime.datetime


@dataclass(frozen=True)
class DriftReport:
    """单次比对报告（frozen）。"""

    drifted: bool
    items: tuple[DriftItem, ...]
    tasks: tuple[RemediationTask, ...]
    checked_at: datetime.datetime


_MISSING: Final[str] = "<MISSING>"
_UNDECLARED: Final[str] = "<UNDECLARED>"


class ComplianceDriftDetector:
    """合规漂移检测器（基线 diff + AL-P3 告警 + 证据快照 + 整改任务）。

    Args:
        clock: 时钟注入。
        alert_sink: AL-P3 告警汇注入；None 时仅留日志。
        evidence_sink: 证据快照汇注入；None 时仅留日志。
        is_non_trading_time: 非交易时段判定注入；None 时视为恒可运行
            （测试/离线场景），注入 False 判定即门禁运行。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[DriftAlert], None] | None = None,
        evidence_sink: Callable[[DriftEvidence], None] | None = None,
        is_non_trading_time: Callable[[], bool] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._evidence_sink = evidence_sink
        self._is_non_trading_time = is_non_trading_time or (lambda: True)
        self._baseline: dict[str, object] | None = None
        self._tasks: list[RemediationTask] = []
        self._task_seq = 0

    # ── 基线登记 ──────────────────────────────────────────────────────────

    def set_baseline(self, baseline: Mapping[str, object]) -> None:
        """登记基线快照（规则声明参数/代码路径的扁平键值表）。"""
        if not isinstance(baseline, Mapping):
            raise ComplianceDriftError("基线须为 Mapping")
        if not baseline:
            raise ComplianceDriftError("基线为空（无声明可比对的合规参数）")
        for key in baseline:
            if not isinstance(key, str) or not key:
                raise ComplianceDriftError(f"基线键非法: {key!r}")
        self._baseline = dict(baseline)
        _log.info("基线登记: %d 键", len(baseline))

    # ── diff 比对 ─────────────────────────────────────────────────────────

    def _diff(self, current: Mapping[str, object]) -> tuple[DriftItem, ...]:
        assert self._baseline is not None  # 调用方已 Fail-Closed 校验
        items: list[DriftItem] = []
        for key in self._baseline:
            if key not in current:
                items.append(DriftItem(key=key, declared=self._baseline[key], actual=_MISSING))
            elif current[key] != self._baseline[key]:
                items.append(DriftItem(key=key, declared=self._baseline[key], actual=current[key]))
        for key in current:
            if key not in self._baseline:
                items.append(DriftItem(key=key, declared=_UNDECLARED, actual=current[key]))
        items.sort(key=lambda it: it.key)
        return tuple(items)

    # ── 运行（仅非交易时段）────────────────────────────────────────────────

    def run_check(self, current_provider: Mapping[str, object] | Callable[[], Mapping[str, object]]) -> DriftReport:
        """比对基线与运行时快照：漂移 → AL-P3 告警 + 证据快照 + 整改任务。"""
        if not self._is_non_trading_time():
            raise ComplianceDriftError("当前为交易时段（漂移比对仅限非交易时段运行）")
        if self._baseline is None:
            raise ComplianceDriftError("基线未登记（先 set_baseline 方可比对，Fail-Closed）")
        current = current_provider() if callable(current_provider) else current_provider
        if not isinstance(current, Mapping):
            raise ComplianceDriftError("运行时快照非法（provider 须返回 Mapping）")
        for key in current:
            if not isinstance(key, str) or not key:
                raise ComplianceDriftError(f"运行时快照键非法: {key!r}")

        items = self._diff(current)
        tasks: tuple[RemediationTask, ...] = ()
        if items:
            now = self._clock()
            keys = tuple(it.key for it in items)
            self._emit_alert(DriftAlert(level=AlertLevel.AL_P3, keys=keys, raised_at=now))
            self._emit_evidence(DriftEvidence(items=items, taken_at=now))
            tasks = self._make_tasks(items, now)
            _log.warning("合规漂移: %d 键 %s", len(items), keys)
        else:
            _log.info("合规漂移比对: 无漂移（%d 键）", len(self._baseline))
        return DriftReport(drifted=bool(items), items=items, tasks=tasks, checked_at=self._clock())

    # ── 三联动 ────────────────────────────────────────────────────────────

    def _emit_alert(self, alert: DriftAlert) -> None:
        if self._alert_sink is not None:
            try:
                self._alert_sink(alert)
            except Exception:  # noqa: BLE001 — 告警不阻断比对（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _emit_evidence(self, evidence: DriftEvidence) -> None:
        if self._evidence_sink is not None:
            try:
                self._evidence_sink(evidence)
            except Exception:  # noqa: BLE001 — 证据汇异常不阻断比对
                _log.exception("evidence_sink 留证失败")

    def _make_tasks(self, items: tuple[DriftItem, ...], now: datetime.datetime) -> tuple[RemediationTask, ...]:
        out: list[RemediationTask] = []
        for item in items:
            self._task_seq += 1
            task = RemediationTask(
                task_id=f"REM-{self._task_seq:04d}",
                key=item.key,
                declared=item.declared,
                actual=item.actual,
                suggestion=f"对齐 {item.key}: 声明 {item.declared!r} / 生效 {item.actual!r}",
                created_at=now,
            )
            self._tasks.append(task)
            out.append(task)
        return tuple(out)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def remediation_tasks(self) -> list[RemediationTask]:
        """整改任务全量（按 task_id 确定性排序）。"""
        return sorted(self._tasks, key=lambda t: t.task_id)
