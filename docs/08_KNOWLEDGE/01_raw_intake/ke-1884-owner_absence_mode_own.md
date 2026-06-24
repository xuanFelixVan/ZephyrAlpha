---
module_id: KE-1793---own-000
status: active
title: 2.218 Owner Absence Mode - owner_absence_mode.py (🆕 v0.20.0 - 盲点268 — Owner假期/应急
category: module_blueprint
---

# 2.218 Owner Absence Mode - owner_absence_mode.py (🆕 v0.20.0 - 盲点268 — Owner假期/应急

2.218 Owner Absence Mode - owner_absence_mode.py (🆕 v0.20.0 - 盲点268 — Owner假期/应急/不可用场景的自治策略)

**致命问题**：1人维护者的"1人"是会res休假、生病、出差的。现有CognitiveLoadAdaptiveEscalator处理"Owner疲劳"，但处理的是"Owner在线但过载"的场景，不处理"Owner离线数天"的场景。Owner去度假2周→FLE应该自动切换到保守自治模式：不做高风险动作、不频繁通知、定期发送日报摘要、紧急问题升级到备用联系人。
**对标**：PagerDuty Vacation Overrides + OpsGenie Scheduled Override + Slack Vacation Responder

```python
@dataclass
class AbsenceProfile:
    mode: str                     # "VACATION"|"CONFERENCE"|"SICK"|"SLEEPING"
    start_time: datetime
    end_time: datetime
    autonomy_policy: dict[str, str]  # action_type → "ALLOW"|"DEFER"|"ESCALATE"
    escalation_contact: str | None   # "wife@example.com" 或 None(无人)
    report_frequency: str          # "DAILY"|"TWICE_DAILY"|"NONE"

class OwnerAbsenceMode:
    ABSENCE_POLICIES: dict[str, dict] = {
        "VACATION": {
            "max_autonomy": "STAGE_3",          # 不允许大变
            "max_severity_for_auto": "MEDIUM",   # 中等以上→defer到Owner回来
            "report_frequency": "DAILY",          # 每天一份摘要
            "permitted_actions": ["ADJUST_THRESHOLD", "NOTIFY_OWNER_SILENT"],
        },
        "EMERGENCY_UNREACHABLE": {
            "max_autonomy": "STAGE_1",           # 最低自治
            "max_severity_for_auto": "NONE",      # 不做任何自主修复
            "report_frequency": "NONE",            # 不发送报告（省资源、Owner收不到）
            "permitted_actions": [],                # OBSERVE_ONLY
            "escalation": "ESCALATE_TO_BACKUP",     # 紧急→通知备用联系人
        },
    }

    async def enter_absence_mode(self, profile: AbsenceProfile):
        policy = self.ABSENCE_POLICIES.get(profile.mode,
            self.ABSENCE_POLICIES["EMERGENCY_UNREACHABLE"])
        self.FLE.set_autonomy_cap(policy["max_autonomy"])
        self.FLE.set_severity_cap(policy["max_severity_for_auto"])
        self.FLE.set_report_frequency(policy["report_frequency"])
        self.current_absence = profile
        if profile.escalation_contact:
            await self._notify_escalation_contact(profile)
        self.FLE.log_info("ABSENCE_MODE_ACTIVATED",
            f"Owner absence mode: {profile.mode}, until {profile.end_time}. "
            f"Autonomy capped at {policy['max_autonomy']}, "
            f"severity cap={policy['max_severity_for_auto']}.")

    async def check_absence_expiry(self):
        if self.current_absence and datetime.now() > self.current_absence.end_time:
            await self._exit_absence_mode()
            self.FLE.notify_owner("WELCOME_BACK",
                f"Owner absence ({self.current_absence.mode}) ended. "
                f"During your absence: {self._absence_summary()}. "
                f"FLE restoring full autonomy.")
```
