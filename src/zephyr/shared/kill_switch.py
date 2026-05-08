"""
Re-export wrapper — canonical implementation at zephyr.rollback.kill_switch.

TD-SHARED-001: 发散副本统一为 re-export wrapper，消除代码漂移。
shared/ 版本原为独立实现（KillSwitchMode/KillSwitchState），与 rollback/ 版本（L1/L2/L3 三级 KillSwitchManager）功能重叠。
rollback/ 版本为 canonical（被 agent_rbac、governance、pipeline 等实际消费）。
"""
from zephyr.rollback.kill_switch import *  # noqa: F401,F403
from zephyr.rollback.kill_switch import KillLevel, KillSwitchEntry, KillSwitchStatus, KillSwitchManager  # noqa: F401
