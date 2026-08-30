# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §novel_attack_guard
# [MODULE] zephyr.security.access_control.guards.novel_attack_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_novel_attack.py; tests/agent_rbac/test_vibe_coding.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] normal actions never increment score; suspicious keywords always increment
# [MODIFY-GUARD] blueprint.md §novel_attack_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] profile_action never raises; returns dict with suspicious/suspicion_score
# [TESTS] tests/agent_rbac/test_novel_attack.py; tests/agent_rbac/test_vibe_coding.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
NovelAttackGuard — 新型攻击行为画像.

依据蓝图 MOD-INF-018 §novel_attack_guard:
- 为每个 agent 建立行为画像
- 检测偏离正常行为模式的新型攻击
- 累积可疑分数

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: novel_attack_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① NovelAttackGuard
#   name_en: NovelAttackGuard
#   intro: 新型攻击行为画像守卫.
#   desc: 新型攻击行为画像守卫.；公共方法（定义序）: profile_action；源码 L96-L137
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: NovelAttackGuard
#   downstream: tests/agent_rbac/test_novel_attack.py; tests/agent_rbac/test_vibe_coding.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field

_SUSPICIOUS_KEYWORDS = {
    "sudo",
    "meltdown",
    "bypass",
    "killswitch",
    "direct_memory",
    "raw_socket",
    "override",
    "hack",
    "exploit",
    "inject",
    "rm_rf",
    "fork_bomb",
    "privilege_escalat",
}

_NORMAL_ACTIONS = {"read", "write", "query", "list", "execute", "check", "verify"}

_SUSPICION_INCREMENT = 0.5
_SUSPICIOUS_THRESHOLD = 1.0


@dataclass
class BehaviorProfile:
    """Agent 行为画像.

    Attributes:
        agent_id: agent ID
        normal_count: 正常操作计数
        suspicious_count: 可疑操作计数
        suspicion_score: 累积可疑分数
    """

    agent_id: str = ""
    normal_count: int = 0
    suspicious_count: int = 0
    suspicion_score: float = 0.0


class NovelAttackGuard:
    """新型攻击行为画像守卫."""

    def __init__(self) -> None:
        self._profiles: dict[str, BehaviorProfile] = {}

    def _get_profile(self, agent_id: str) -> BehaviorProfile:
        if agent_id not in self._profiles:
            self._profiles[agent_id] = BehaviorProfile(agent_id=agent_id)
        return self._profiles[agent_id]

    def _is_suspicious(self, action: str) -> bool:
        if action in _NORMAL_ACTIONS:
            return False
        action_lower = action.lower()
        for keyword in _SUSPICIOUS_KEYWORDS:
            if keyword in action_lower:
                return True
        return False

    def profile_action(self, agent_id: str, action: str) -> dict:
        """记录 agent 行为并更新画像.

        Args:
            agent_id: agent ID
            action: 操作名称

        Returns:
            dict 包含 suspicious (bool) 和 suspicion_score (float)
        """
        profile = self._get_profile(agent_id)
        if self._is_suspicious(action):
            profile.suspicious_count += 1
            profile.suspicion_score += _SUSPICION_INCREMENT
        else:
            profile.normal_count += 1
        return {
            "suspicious": profile.suspicion_score >= _SUSPICIOUS_THRESHOLD,
            "suspicion_score": profile.suspicion_score,
            "normal_count": profile.normal_count,
            "suspicious_count": profile.suspicious_count,
        }


__all__ = [
    "BehaviorProfile",
    "NovelAttackGuard",
]
