from __future__ import annotations
from enum import Enum

class OpsPhase(str, Enum):
    P1_PRE_OPEN = "08:00-09:30 盘前"
    P2_CORE = "09:30-16:00 主交易"
    P3_CLOSE = "16:00-16:30 收市核实"
    P4_MAINTENANCE = "16:30-17:30 盘后维护"
    P5_SUMMARY = "17:30-18:00 日终总结"

class QuickCommand(str, Enum):
    CRISIS = "/crisis"
    STATUS = "/status"
    NOTES = "/notes"
    PUBLISH = "/publish"

QUICK_COMMANDS: dict[QuickCommand, str] = {
    QuickCommand.CRISIS: "立即Pause所有策略仅Emergency defense·内存Only",
    QuickCommand.STATUS: "实时关键指标clean dashboard",
    QuickCommand.NOTES: "所有今天关键事件→markdown→daily_notes.md",
    QuickCommand.PUBLISH: "将今天稳定变更发布到MOD-MASTER-001+bump版本号",
}
