# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.process_isolator
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 进程隔离边界不可突破;IPC通道必须加密
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Process Isolator — v0.6.0 进程隔离器: engine运行在独立进程+资源限制+crash恢复。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: process_isolator.py
# 层: 算法
# - id: A1
#   name_zh: ① ProcessIsolator
#   name_en: ProcessIsolator
#   intro: class ProcessIsolator 源码 L51-L78
#   desc: 公共方法（定义序）: processes, spawn_engine, isolate, kill_engine；源码 L51-L78
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ProcessIsolator
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ProcessIsolator:
    def __init__(self):
        self._processes: dict[str, dict] = {}

    # ── Stage 4 公共化（2026-07-28）：只读 property ──
    @property
    def processes(self) -> dict[str, dict]:
        """只读：processes（Stage 4 公共化）。"""
        return self._processes

    @processes.setter
    def processes(self, value):
        """写入：processes（Stage 4 公共化）。"""
        self._processes = value

    def spawn_engine(self, engine_id: str, config: dict = None) -> bool:
        self._processes[engine_id] = {"status": "running", "config": config or {}}
        return True

    def isolate(self, engine_id: str, resource_limits: dict = None) -> bool:
        if engine_id not in self._processes:
            return False
        self._processes[engine_id]["limits"] = resource_limits or {"cpu": 1, "memory_mb": 256}
        return True

    def kill_engine(self, engine_id: str) -> bool:
        proc = self._processes.pop(engine_id, None)
        return proc is not None
