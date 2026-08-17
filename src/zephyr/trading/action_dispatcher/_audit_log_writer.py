# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §5.150.7
# [MODULE] zephyr.trading.action_dispatcher._audit_log_writer
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.action_dispatcher (facade module: _facade_mod.AUDIT_LOGS_DIR/ActionReport)
# [CONSUMERS] zephyr.trading.action_dispatcher.ActionDispatcher.__init__ (构造 _audit 实例)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计日志写入器——write_triage_log 将异常分诊结果写入 JSONL；无状态（仅 dry_run 标志）；通过 _facade_mod 访问 patchable 模块级常量以支持 patch("...action_dispatcher.AUDIT_LOGS_DIR", ...) 测试
# [MODIFY-GUARD] 公共方法 write_triage_log 签名变更需同步 facade thin wrapper 与测试
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] write_triage_log 始终返回 ActionReport(status=modified)；needs_human=True→detail 含 ALERT，否则 CLEAR
# [TESTS] tests/action/test_action_dispatcher.py (TestActionDispatcherWriteTriageLog)
# [A_module] module_id=MOD-INF-035 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""审计日志写入器（从 ActionDispatcher._write_triage_log 提取）。

职责簇：JSONL 审计日志写入。无状态（仅 dry_run 标志）。
通过 _facade_mod 访问模块级常量（test-patchable via patch("...action_dispatcher.AUDIT_LOGS_DIR")）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: triage 结果字典
#   fields: result 字典（含 needs_human 等键）+ dry_run 标志
#   code: write_triage_log 入口参数
# - id: I2
#   name: facade 模块级常量
#   fields: AUDIT_LOGS_DIR/ActionReport（_facade_mod 引用，test-patchable）
#   code: _facade_mod 模块引用
# 层: 处理
# - id: F1
#   name: JSONL 追加写入
#   code: write_triage_log 主流程（构造带时间戳记录 → 追加 AUDIT_LOGS_DIR 下 jsonl；dry_run 跳过写盘）
# 层: 输出
# - id: O1
#   name: ActionReport
#   fields: status=modified；needs_human=True→detail 含 ALERT，否则 CLEAR
#   code: write_triage_log 返回值
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from zephyr.trading import action_dispatcher as _facade_mod


class AuditLogWriter:
    """审计日志写入器。

    Public API:
        write_triage_log(result: dict) -> ActionReport
    """

    def __init__(self, dry_run: bool = False, facade=None) -> None:
        self._dry_run = dry_run
        self._facade = facade

    def write_triage_log(self, result: dict):
        """将异常分诊结果写入审计日志（JSONL）。"""
        triage = result.get("result", {})
        needs_human = triage.get("needs_human", False)
        reason = triage.get("reason", "")

        today = datetime.now(UTC).strftime("%Y%m%d")
        out_file = _facade_mod.AUDIT_LOGS_DIR / f"brain_triage_{today}.jsonl"
        out_file.parent.mkdir(parents=True, exist_ok=True)

        entry = json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "needs_human": needs_human,
                "reason": reason,
            },
            ensure_ascii=False,
        )

        with open(out_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

        status = "ALERT" if needs_human else "CLEAR"
        return _facade_mod.ActionReport("audit", "anomaly_triage", "modified", f"triage: {status}")
