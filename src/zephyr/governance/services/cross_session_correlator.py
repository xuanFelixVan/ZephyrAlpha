# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.services.cross_session_correlator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 跨会话关联必须执行;异常必须触发告警
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cross-Session Correlator — v0.9.0 跨会话Coreset关联器: 多session行为模式+异常跨session模式检测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cross_session_correlator.py
# 层: 算法
# - id: A1
#   name_zh: ① CrossSessionCorrelator
#   name_en: CrossSessionCorrelator
#   intro: class CrossSessionCorrelator 源码 L51-L77
#   desc: 公共方法（定义序）: sessions, register_session, detect_anomalous_session；源码 L51-L77
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CrossSessionCorrelator
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class CrossSessionCorrelator:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def sessions(self) -> dict[str, dict]:
        """只读：sessions（Stage 4 公共化）。"""
        return self._sessions

    @sessions.setter
    def sessions(self, value):
        """写入：sessions（Stage 4 公共化）。"""
        self._sessions = value

    def register_session(self, session_id: str, metrics: dict):
        self._sessions[session_id] = metrics

    def detect_anomalous_session(self, metrics: dict, std_dev_threshold: float = 2.0) -> bool:
        if len(self._sessions) < 3:
            return False
        means = {k: sum(s[k] for s in self._sessions.values()) / len(self._sessions) for k in metrics}
        for k, v in metrics.items():
            mean = means.get(k, 0)
            if mean > 0 and abs(v - mean) / mean > std_dev_threshold:
                return True
        return False
