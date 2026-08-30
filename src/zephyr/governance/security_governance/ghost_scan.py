# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.ghost_scan
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 幽灵进程检测不可禁用;内核级验证不可绕过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Ghost Scan — v0.8.0 幽灵进程检测: lingering process扫描+资源泄漏检测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ghost_scan.py
# 层: 算法
# - id: A1
#   name_zh: ① GhostScanner
#   name_en: GhostScanner
#   intro: class GhostScanner 源码 L51-L74
#   desc: 公共方法（定义序）: registered_pids, register, detect_ghosts, cleanup；源码 L51-L74
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: GhostScanner
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class GhostScanner:
    def __init__(self):
        self._registered_pids: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def registered_pids(self) -> set[str]:
        """只读：registered_pids（Stage 4 公共化）。"""
        return self._registered_pids

    @registered_pids.setter
    def registered_pids(self, value):
        """写入：registered_pids（Stage 4 公共化）。"""
        self._registered_pids = value

    def register(self, pid: str):
        self._registered_pids.add(pid)

    def detect_ghosts(self, active_pids: set[str]) -> list[str]:
        return list(self._registered_pids - active_pids)

    def cleanup(self, pid: str) -> bool:
        self._registered_pids.discard(pid)
        return True
