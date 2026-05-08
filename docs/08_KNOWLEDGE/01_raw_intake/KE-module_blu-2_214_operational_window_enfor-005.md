---
module_id: KE-module_blu-2_214_operational_window_enfor-005
title: 2.214 Operational Window Enforcer - operational_window_enforcer.py (🆕 v0.20.0 -
category: module_blueprint
---

# 2.214 Operational Window Enforcer - operational_window_enforcer.py (🆕 v0.20.0 -

2.214 Operational Window Enforcer - operational_window_enforcer.py (🆕 v0.20.0 - 盲点264 — 运维窗口感知的动作权限控制)

**致命问题**：FLE不能在任何时间做任何事——在市场交易时段做SCHEMA_MIGRATION=灾难，在午夜无人时做NOTIFY_OWNER=噪音，在月末结算窗口做DR_DRILL=不可接受的风险。但现有market_calendar只提供"是否交易日"的布尔判断，不提供**per-action-type的窗口权限矩阵**。
**对标**：ITIL Change Management Calendar + AWS Maintenance Window + ServiceNow Change Blackout Periods

```python
@dataclass
class OperationalWindow:
    window_name: str
    days_of_week: list[int]  # 0=Mon, 6=Sun
    hours_of_day: tuple[int, int]  # (start_hour, end_hour) UTC
    permitted_actions: list[str]   # ["NOTIFY_OWNER", "ADJUST_THRESHOLD", ...]
    prohibited_actions: list[str]  # 即使permitted list包含，也强制禁止的
    priority: int  # 1=最高（窗口匹配→直接用此窗口规则）

class OperationalWindowEnforcer:
    WINDOWS: list[OperationalWindow] = [
        OperationalWindow("market_hours_mon_fri", [0,1,2,3,4], (13, 20),
            permitted_actions=["NOTIFY_OWNER", "ADJUST_THRESHOLD", "REBALANCE"],
            prohibited_actions=["SCHEMA_MIGRATION", "DR_DRILL", "SELF_UPGRADE",
                                 "SECRET_ROTATION", "DEPLOY_ROLLBACK"],
            priority=1),  # 市场时段最高优先级
        OperationalWindow("end_of_day_settlement", [0,1,2,3,4], (20, 22),
            permitted_actions=["NOTIFY_OWNER"],
            prohibited_actions=["*"],  # 任何改变性动作都禁止
            priority=1),
        OperationalWindow("weekend_maintenance", [5,6], (0, 23),
            permitted_actions=["SCHEMA_MIGRATION", "SELF_UPGRADE", "DR_DRILL",
                               "SECRET_ROTATION", "DEPLOY_ROLLBACK", "KB_COMPACT"],
            prohibited_actions=["NOTIFY_OWNER", "REBALANCE"],
            priority=2),  # 周末窗口→安心做大变更
        OperationalWindow("default", [0,1,2,3,4,5,6], (0, 23),
            permitted_actions=["*"],
            prohibited_actions=[],
            priority=99),  # 最低优先级兜底
    ]

    async def check_action_permission(self, action: FLEAction) -> WindowPermission:
        now = datetime.utcnow()
        matched_window = None
        for window in sorted(self.WINDOWS, key=lambda w: w.priority):
            if now.weekday() in window.days_of_week and \
               window.hours_of_day[0] <= now.hour <= window.hours_of_day[1]:
                matched_window = window
                break  # 已按priority排好序，第一个匹配的就是最高优先级
        if not matched_window:
            return WindowPermission(permitted=True)  # 默认允许
        if action.action_type in matched_window.prohibited_actions or \
           "*" in matched_window.prohibited_actions:
            self.FLE.log_deferral("WINDOW_PROHIBITED",
                f"Action {action.action_type} prohibited in window '{matched_window.window_name}'. "
                f"Scheduled for next permitted window: "
                f"{self._find_next_permitted_window(action.action_type)}")
            return WindowPermission(permitted=False, window=matched_window,
                next_permitted=self._find_next_permitted_window(action.action_type))
        return WindowPermission(pe
