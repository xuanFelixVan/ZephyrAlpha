# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] zephyr.ai_layer.intake.kpi
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.alerts.threshold_loader (load_alert_thresholds); zephyr.ai_layer.intake.intake_events (IntakeJournal); zephyr.ai_layer.intake.card_store (CardStore); zephyr.infrastructure.database_service (get_db_service)
# [CONSUMERS] zephyr.ai_layer.intake.intake_events (intake_kpi_alert 消费体 handle_alert); 周巡检 CLI（后续接线批）
# [STARTUP] event_driven
# [MATURITY] evolving
# [INVARIANTS] 阈值真源=alert_threshold_registry.yaml（fail-closed 统读，禁码内第二真源）；DB 视图 V3 只产出数值不存阈值（规则=YAML、架构=DB 的 SSOT 分界）；
#              健康区间 v0=5%–30%（入考率=每百卡 funnel_stage>=E2 占比）；
#              <下界连续 2 周→贫矿降级（该域/源 daily_quota 减半）；连续 4 周→移长尾（quota=1，禁清零=多样性保底）；
#              >上界→收紧判据建议 + 附当周被 E2 拒样本清单；动作只经事件（intake_kpi_alert），禁定时器
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.7
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 阈值缺条目/畸形→AlertThresholdConfigError 上抛（fail-closed，绝不退回硬编码默认值）；
#                  样本不足（周数<窗口）→不告警且留 reason=insufficient_weeks（防冷启动假贫矿）；
#                  quota 更新用 GREATEST(1, quota/2) 保证永不清零；DB 不可达→异常上抛
# [TESTS] tests/ai_layer/intake/（★ 在册缺口：本模块测试 test_kpi.py 未建，处方见 lanes/aibase_relay.md §6）
# [TTL] permanent
"""kpi — L2 淘汰率 KPI：读 V3 视图 + 阈值判定 + intake_kpi_alert 事件（DESIGN §2.7）。

判据分层：``evaluate_series()`` 是**纯函数**（输入周序列 + 阈值，输出告警清单，零 DB 可全枚举单测）；
``IntakeKpi`` 只负责取数（V3 视图）与派事件；``handle_alert()`` 是事件消费体（执行降级/收紧动作）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from zephyr.ai_layer.intake.card_store import CardStore
from zephyr.ai_layer.intake.intake_events import IntakeJournal
from zephyr.shared.alerts.threshold_loader import load_alert_thresholds

log = logging.getLogger(__name__)

__all__: Final = [
    "IntakeKpi",
    "KpiAlert",
    "KpiThresholds",
    "evaluate_series",
    "handle_alert",
    "load_kpi_thresholds",
]

THD_LOWER: Final = "THD-INTAKE-001"
THD_UPPER: Final = "THD-INTAKE-002"
THD_DEMOTE_WEEKS: Final = "THD-INTAKE-003"
THD_LONGTAIL_WEEKS: Final = "THD-INTAKE-004"
ACTION_DEMOTE: Final = "demote"
ACTION_LONGTAIL: Final = "longtail"
ACTION_TIGHTEN: Final = "tighten"

SQL_WEEKLY_DOMAIN = """
SELECT week_start, domain_id, cards_total, cards_to_exam, exam_pass_rate_pct
FROM {s}.ai_intake_kpi_weekly ORDER BY week_start DESC LIMIT %s
"""
SQL_DEMOTE_QUOTA = """
UPDATE {s}.ai_intake_source_quota
SET daily_quota = GREATEST(1, daily_quota / 2), note = %s, updated_at = now()
WHERE source_slug = %s
"""
SQL_LONGTAIL_QUOTA = """
UPDATE {s}.ai_intake_source_quota
SET daily_quota = 1, note = %s, updated_at = now()
WHERE source_slug = %s
"""
SQL_RECENT_REJECTED = """
SELECT card_id, domain_id, rejection_reason FROM {s}.ai_intake_negative
ORDER BY stage_changed_at DESC NULLS LAST LIMIT %s
"""


@dataclass(frozen=True)
class KpiThresholds:
    """阈值快照（全部来自 alert_threshold_registry，fail-closed 统读）。"""

    lower_pct: float
    upper_pct: float
    demote_weeks: int
    longtail_weeks: int


@dataclass(frozen=True)
class KpiAlert:
    """一条 KPI 告警结论（可直接做 intake_kpi_alert 的 payload）。"""

    scope: str
    key: str
    pass_rate: float
    window_weeks: int
    action: str
    reason: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "key": self.key,
            "pass_rate": self.pass_rate,
            "window_weeks": self.window_weeks,
            "action": self.action,
            "reason": self.reason,
        }


def load_kpi_thresholds(registry_path: Path | None = None) -> KpiThresholds:
    """从告警阈值注册表统读四条 intake KPI 阈值（缺条目即报错，不退回硬编码）。"""
    values = load_alert_thresholds(
        {
            THD_LOWER: "lower_pct",
            THD_UPPER: "upper_pct",
            THD_DEMOTE_WEEKS: "demote_weeks",
            THD_LONGTAIL_WEEKS: "longtail_weeks",
        },
        registry_path=registry_path,
        cast="float",
    )
    return KpiThresholds(
        lower_pct=float(values["lower_pct"]),
        upper_pct=float(values["upper_pct"]),
        demote_weeks=int(values["demote_weeks"]),
        longtail_weeks=int(values["longtail_weeks"]),
    )


def evaluate_series(rates: list[float | None], thresholds: KpiThresholds, *, key: str,
                    scope: str = "domain") -> list[KpiAlert]:
    """纯判据：周入考率序列（新→旧）→ 告警清单。

    规则：①最近 longtail_weeks 周全部 < 下界 → longtail（移长尾 quota=1）；
          ②否则最近 demote_weeks 周全部 < 下界 → demote（quota 减半）；
          ③最近一周 > 上界 → tighten（收紧判据建议）；
          ④样本不足窗口 → 静默（冷启动不判贫矿）。
    """
    known = [r for r in rates if r is not None]
    if not known:
        return []
    out: list[KpiAlert] = []
    latest = float(known[0])
    if latest > thresholds.upper_pct:
        out.append(
            KpiAlert(scope=scope, key=key, pass_rate=latest, window_weeks=1,
                     action=ACTION_TIGHTEN, reason=f"above_upper:{thresholds.upper_pct}")
        )
    if len(known) >= thresholds.longtail_weeks and all(
        float(r) < thresholds.lower_pct for r in known[: thresholds.longtail_weeks]
    ):
        out.append(
            KpiAlert(scope=scope, key=key, pass_rate=latest, window_weeks=thresholds.longtail_weeks,
                     action=ACTION_LONGTAIL, reason=f"below_lower:{thresholds.lower_pct}")
        )
        return out
    if len(known) >= thresholds.demote_weeks and all(
        float(r) < thresholds.lower_pct for r in known[: thresholds.demote_weeks]
    ):
        out.append(
            KpiAlert(scope=scope, key=key, pass_rate=latest, window_weeks=thresholds.demote_weeks,
                     action=ACTION_DEMOTE, reason=f"below_lower:{thresholds.lower_pct}")
        )
    return out


class IntakeKpi:
    """KPI 取数 + 判定 + 派事件（阈值 YAML 真源，数值只从 V3 视图出）。"""

    def __init__(self, schema: str = "ai_intake", service: Any | None = None,
                 journal: IntakeJournal | None = None, registry_path: Path | None = None) -> None:
        self._store = CardStore(schema=schema, service=service)
        self.schema: Final = schema
        self._journal = journal or IntakeJournal()
        self._registry_path = registry_path

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    def weekly_rows(self, limit: int = 52) -> list[dict[str, Any]]:
        """读 V3 视图（周×域），新→旧排序。"""
        cur = self._store._conn(reader=True).cursor()  # noqa: SLF001——同包复用只读连接口径
        cur.execute(self._sql(SQL_WEEKLY_DOMAIN), (int(limit),))
        return [dict(r) for r in cur.fetchall()]

    def rates_by_domain(self, limit: int = 52) -> dict[str, list[float | None]]:
        """把周×域行折叠成 {domain_id: [rate 新→旧]}。"""
        out: dict[str, list[float | None]] = {}
        for row in self.weekly_rows(limit):
            domain = str(row.get("domain_id") or "unknown")
            rate = row.get("exam_pass_rate_pct")
            out.setdefault(domain, []).append(None if rate is None else float(rate))
        return out

    def evaluate(self, limit: int = 52) -> list[KpiAlert]:
        """全域评估（阈值 fail-closed 统读）。"""
        thresholds = load_kpi_thresholds(self._registry_path)
        alerts: list[KpiAlert] = []
        for domain, rates in sorted(self.rates_by_domain(limit).items()):
            alerts.extend(evaluate_series(rates, thresholds, key=domain, scope="domain"))
        return alerts

    def run(self, limit: int = 52) -> dict[str, Any]:
        """评估 → 派 intake_kpi_alert 事件（动作在消费体侧执行，保持事件触发单向）。"""
        alerts = self.evaluate(limit)
        emitted = [self._journal.emit("intake_kpi_alert", a.payload()).id for a in alerts]
        return {"alerts": [a.payload() for a in alerts], "emitted": emitted}

    def rejected_samples(self, limit: int = 20) -> list[dict[str, Any]]:
        """收紧路附带的当周被拒样本清单（供 rubric 复盘，DESIGN §2.7）。"""
        cur = self._store._conn(reader=True).cursor()  # noqa: SLF001
        cur.execute(self._sql(SQL_RECENT_REJECTED), (int(limit),))
        return [dict(r) for r in cur.fetchall()]


def handle_alert(payload: dict[str, Any]) -> dict[str, Any]:
    """intake_kpi_alert 消费体：demote/longtail 改配额，tighten 出建议+样本清单。"""
    action = str(payload.get("action") or "")
    key = str(payload.get("key") or "")
    journal_scope = str(payload.get("scope") or "domain")
    if action == ACTION_TIGHTEN:
        samples = IntakeKpi().rejected_samples(20)
        log.warning("intake KPI 收紧建议：域 %s 入考率 %s 超上界，附拒样 %d 条",
                    key, payload.get("pass_rate"), len(samples))
        return {"action": action, "key": key, "advice": "tighten_L1_rubric", "samples": len(samples)}
    if action in (ACTION_DEMOTE, ACTION_LONGTAIL):
        sql = SQL_DEMOTE_QUOTA if action == ACTION_DEMOTE else SQL_LONGTAIL_QUOTA
        store = CardStore()
        conn = store.write_conn()
        note = f"intake_kpi:{action}:{journal_scope}:{key}"
        try:
            cur = conn.cursor()
            cur.execute(store._sql(sql), (note, key))  # noqa: SLF001
            touched = cur.rowcount
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return {"action": action, "key": key, "quota_rows_updated": int(touched or 0)}
    raise ValueError(f"unknown_kpi_action:{action}")
