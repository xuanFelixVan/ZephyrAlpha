# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.hooks_integrity_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Hooks自编辑防护不可禁用;外部hash必须验证
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Hooks Integrity Guard — v0.11.0 Hooks自编辑防护器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: hooks_integrity_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① HooksIntegrityGuard
#   name_en: HooksIntegrityGuard
#   intro: class HooksIntegrityGuard 源码 L51-L71
#   desc: 公共方法（定义序）: hooks_hashes, register, verify；源码 L51-L71
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: HooksIntegrityGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class HooksIntegrityGuard:
    def __init__(self):
        self._hooks_hashes: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def hooks_hashes(self) -> dict[str, str]:
        """只读：hooks_hashes（Stage 4 公共化）。"""
        return self._hooks_hashes

    @hooks_hashes.setter
    def hooks_hashes(self, value):
        """写入：hooks_hashes（Stage 4 公共化）。"""
        self._hooks_hashes = value

    def register(self, hook_path: str, hash_value: str):
        self._hooks_hashes[hook_path] = hash_value

    def verify(self, hook_path: str, current_hash: str) -> bool:
        expected = self._hooks_hashes.get(hook_path)
        return expected is None or expected == current_hash
