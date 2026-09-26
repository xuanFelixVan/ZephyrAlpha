# [TTL] permanent
"""tests/frontend 收集期 _ModuleLock 死锁防御（st-chief5-20260927）。

病根：test_api_server_heartbeat 等先收集文件 import api_server 时拉起后台导入线程，
与主线程收集 test_dashboard_feeds（import 链经 zephyr.risk.core 包 __init__ 到
daily_auditor）在同一模块锁上相撞——py3.12 importlib 判死锁，整目录 531 条测试
无法收集（HEAD 态同样复现，两文件最小复现实证）。

治本：conftest 先于全部测试模块在主线程预导入争用终端模块，后台线程后续导入
变为已完成模块的零锁查找。新增争用模块若再现同族死锁，在此追加预导入即可。
"""

from zephyr.risk.core.daily_auditor import AuditRequest, DailyAuditor  # noqa: F401

__all__ = ["AuditRequest", "DailyAuditor"]
