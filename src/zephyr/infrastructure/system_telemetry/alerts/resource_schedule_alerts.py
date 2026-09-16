# [BLUEPRINT] MOD-RESCHED-ALERT | docs/03_modules/_cross_layer/resource_schedule_alerts/blueprint.md | §
# [MODULE] zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed（唯一出口，本模块不另起炉灶）;
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate（findings 真源）
# [CONSUMERS] src/zephyr/frontend/dashboard/api_server.py（/api/ops-notifications 探针段——既有，零改动）;
#   promotion 页横幅（既有消费方）; 晨审（notifications.jsonl 机器可读板）;
#   tests/infrastructure/test_resource_schedule_alerts.py
# [STARTUP] imported（无独立线程/无 cron——发布由闸/视图生成器在检测时点事件触发调用）
# [MATURITY] testing
# [INVARIANTS] 唯一出口纪律——只经 OpsAlertFeed.publish 落板（飞书/SMTP 已裁撤，禁另起通道）;
#   同 key 静默窗口去重照抄 OpsAlertFeed 语义（refresh 不重复）;
#   板目录可注入（测试隔离禁写生产 .runtime）;
#   告警失败不抛出（发布失败降级记日志——告警线自身不得成为故障源）;
#   block 级 finding → severity=critical；warn 级 → severity=warning
# [MODIFY-GUARD] config/alert_rules.yaml（只读引用规则命名风格，不改规则）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ops 板写入失败=记日志不抛；findings 空表=幂等 resolve 既有告警
# [TESTS] tests/infrastructure/test_resource_schedule_alerts.py
# [A_module] module_id=MOD-RESCHED-ALERT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
#
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> O1
# A2 --> O1
"""resource_schedule_alerts — 排班冲突告警桥（MOD-RESCHED-ALERT，B4）。

资源排班全景四件套的告警接线：把闸（MOD-RESCHED-GATE）的 findings 送进项目唯一
通知出口 OpsAlertFeed（MOD-INF-OPS-ALERT-FEED，治理线已收口——本模块零通道自建、
不碰飞书/SMTP 已裁撤通道、不改 ops_alert_feed 模块本体）。

映射规则：
- block 级 finding（sched_overlap_group/sched_mem_ceiling/sched_e0_block/
  sched_gate_absent）→ severity=critical，key=`<reason_code>:<排序 task_ids>`（同冲突去重）；
- warn 级（sched_truth_drift/sched_view_stale 等）→ severity=warning；
- 本轮未再触发的既有活动告警 → resolve()（灰显解除，滞回语义照抄供给线）。

多发布方纪律（2026-09-17 P0）：解除联动按 module_id 划界，各发布方只解除自己的
key——闸/视图发布方用缺省 `resource-schedule-gate`，注册表再生自检发布方传
`resource-schedule-regen`。混用同一 id 会让两臂互删对方告警（视图日更臂不含
健康码，跑一次就把再生臂的闸缺席告警 resolve 掉）。

静默窗口：同 key 30 分钟内只刷新 count/last_seen 不重复（OpsAlertFeed.publish
内建语义，本模块只传窗口参数）。

晨审挂接：通知板=``.runtime/ops_notifications/notifications.jsonl``（机器可读
JSONL），晨审/AI 会话冷启动直接读板或经 ``GET /api/ops-notifications``——本模块
零额外接口。
# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/resource_schedule_alerts.yaml
"""

from __future__ import annotations

import logging
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final = ["ResourceScheduleAlerts", "publish_findings"]

# 静默窗口（同 key 去重照抄 OpsAlertFeed 语义；30min 防扫描轮询刷板）
DEFAULT_SILENCE_WINDOW_S: Final = 1800.0

# 理由码 → 通知标题（人类可读；理由码真源在 resource_schedule_gate）
_TITLES: dict[str, str] = {
    "sched_overlap_group": "排班冲突：互斥组时间窗交叠",
    "sched_mem_ceiling": "排班冲突：内存天花板超限",
    "sched_e0_block": "排班冲突：交易时段未过 E0 闸",
    "sched_truth_drift": "排班真源漂移（window_expr 与真源不一致）",
    # 排产链健康码（2026-09-17 P0，v2 方案 C-5/C-10；产出方=注册表生成器 --check 臂）
    "sched_gate_absent": "排班闸缺席：E0/冲突闸/闸注册不可解析（日历守卫静默失效）",
    "sched_view_stale": "排班视图过期：rw-data.js 内嵌指纹与注册表现盘不一致",
}


class ResourceScheduleAlerts:
    """闸 findings → OpsAlertFeed 唯一通道桥（板目录可注入，测试隔离）。"""

    def __init__(self, board_dir: str | None = None, module_id: str = "resource-schedule-gate", silence_window_s: float = DEFAULT_SILENCE_WINDOW_S):
        self._board_dir = board_dir
        self._module_id = module_id
        self._silence = float(silence_window_s)

    def _feed(self):
        from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

        return OpsAlertFeed(board_dir=self._board_dir, module_id=self._module_id)

    def publish_findings(self, findings: list) -> dict:
        """发布 findings（block→critical/warn→warning）并解除已消失告警。返回操作摘要。

        fail-safe：单条发布失败记日志继续（告警线自身不得成为故障源）。
        """
        feed = self._feed()
        ops: list[dict] = []
        active_keys: list[str] = []
        for f in findings or []:
            try:
                key = self.key_of(f)
                active_keys.append(key)
                severity = "critical" if getattr(f, "severity", "warn") == "block" else "warning"
                title = _TITLES.get(getattr(f, "reason_code", ""), str(getattr(f, "reason_code", "sched_finding")))
                detail = str(getattr(f, "detail", ""))
                at = getattr(f, "at", None)
                message = f"{detail}" + (f"（冲突时刻 {at}）" if at else "")
                r = feed.publish(
                    key=key,
                    severity=severity,
                    title=title,
                    message=message,
                    source=self._module_id,
                    labels={"reason_code": getattr(f, "reason_code", ""), "task_ids": getattr(f, "task_ids", [])},
                    silence_window_s=self._silence,
                )
                ops.append(r)
            except Exception as exc:  # noqa: BLE001 — INVARIANTS：发布失败降级不抛
                logger.warning("resource_schedule_alerts publish failed: %s", exc)
                ops.append({"op": "failed", "reason": str(exc)[:120]})
        # 解除联动：活动板里属于本闸、但本轮未再触发的 key → resolve
        try:
            board_keys = {e.get("key") for e in feed.list_active() if e.get("module_id") == self._module_id and not e.get("resolved_at")}
            for k in sorted(board_keys - set(active_keys)):
                n = feed.resolve(str(k))
                if n:
                    ops.append({"op": "resolved", "key": k, "count": n})
        except Exception as exc:  # noqa: BLE001 — 解除联动失败不抛
            logger.warning("resource_schedule_alerts resolve failed: %s", exc)
        return {"ops": ops, "active_keys": active_keys}

    @staticmethod
    def key_of(finding) -> str:
        """finding → dedup key（理由码+排序 task_ids；同冲突稳定去重）。"""
        reason = str(getattr(finding, "reason_code", "sched_finding"))
        tids = ",".join(sorted(getattr(finding, "task_ids", []) or [])) or "unknown"
        return f"{reason}:{tids}"


# 模块级便捷函数（视图生成器/闸扫描后的单行动接）
def publish_findings(findings: list, board_dir: str | None = None, module_id: str | None = None) -> dict:
    """便捷入口：ResourceScheduleAlerts(board_dir, module_id).publish_findings(findings)。

    module_id 省略=缺省发布方 `resource-schedule-gate`；再生自检臂传
    `resource-schedule-regen`（多发布方纪律，见模块头）。
    """
    kw: dict = {"board_dir": board_dir}
    if module_id:
        kw["module_id"] = module_id
    return ResourceScheduleAlerts(**kw).publish_findings(findings)

