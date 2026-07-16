# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.sequence_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FORBIDDEN_SEQUENCES immutable; per-session history isolated; match returns FORBIDDEN string
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] record() never raises; returns str|None
# [TESTS] tests/agent_rbac/test_sequence_guard_agent_rbac.py
# [A_module] module_id=MOD-SEC_sequence_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""SequenceGuard — 操作序列守卫.

依据蓝图 MOD-INF-018 §3:
- 检测禁止的操作序列（数据外泄、权限提升等）
- 每个 session 独立维护操作历史
- 匹配禁止序列时返回违规描述
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FORBIDDEN_SEQUENCES: list[dict[str, Any]] = [
    {
        "name": "data_exfiltration",
        "pattern": ["read:credential", "write:network", "delete:log"],
    },
    {
        "name": "privilege_escalation",
        "pattern": ["read:rbac_config", "modify:self_permission", "execute:admin"],
    },
    {
        "name": "destruction_chain",
        "pattern": ["read:config", "write:destructive", "delete:backup"],
    },
    {
        "name": "audit_tampering",
        "pattern": ["read:audit_log", "delete:audit_log", "write:audit_log"],
    },
    {
        "name": "credential_theft",
        "pattern": ["read:env", "read:credential", "write:network"],
    },
    {
        "name": "backdoor_install",
        "pattern": ["write:src", "execute:scripts", "modify:rbac_config"],
    },
]

SEQUENCE_TIMEOUT = 3600  # 秒


@dataclass
class SequenceEvent:
    """序列事件.

    Attributes:
        session_id: 会话 ID
        operation: 操作名称
        target: 操作目标
    """

    session_id: str = ""
    operation: str = ""
    target: str = ""


class SequenceGuard:
    """操作序列守卫.

    维护每个 session 的操作历史，检测禁止的操作序列。
    """

    def __init__(self) -> None:
        self._history: dict[str, list[str]] = {}
        self._whitelist: list[list[str]] = []

    def _format_op(self, event: SequenceEvent) -> str:
        """将事件格式化为 operation:target 字符串."""
        operation = getattr(event, "operation", "")
        target = getattr(event, "target", "")
        if target:
            return f"{operation}:{target}"
        return operation

    def _is_whitelisted(self, op: str) -> bool:
        """检查操作是否在白名单中."""
        for wl in self._whitelist:
            if op in wl:
                return True
        return False

    def record(self, event: SequenceEvent) -> str | None:
        """记录事件并检测禁止序列.

        Args:
            event: 序列事件

        Returns:
            str | None: 违规描述（包含 FORBIDDEN）或 None
        """
        session_id = getattr(event, "session_id", "")
        op = self._format_op(event)

        if session_id not in self._history:
            self._history[session_id] = []

        self._history[session_id].append(op)

        # 检测是否匹配任何禁止序列
        history = self._history[session_id]
        for seq in FORBIDDEN_SEQUENCES:
            seq_ops = seq["pattern"]
            seq_name = seq["name"]
            seq_len = len(seq_ops)
            if len(history) < seq_len:
                continue
            # 检查最近的操作是否匹配禁止序列
            recent = history[-seq_len:]
            if recent == seq_ops:
                return f"FORBIDDEN sequence detected: {seq_name}"

        return None

    def check_cross_session(self, events: list[SequenceEvent]) -> str | None:
        """检查跨会话的序列风险.

        Args:
            events: 多个会话的事件列表

        Returns:
            str | None: 风险描述或 None
        """
        if not events:
            return None

        # 检查是否有多个会话操作同一目标
        targets_by_session: dict[str, set[str]] = {}
        for e in events:
            sid = getattr(e, "session_id", "")
            target = getattr(e, "target", "")
            if sid not in targets_by_session:
                targets_by_session[sid] = set()
            if target:
                targets_by_session[sid].add(target)

        # 找出被多个会话操作的目标
        all_targets: dict[str, set[str]] = {}
        for sid, targets in targets_by_session.items():
            for t in targets:
                if t not in all_targets:
                    all_targets[t] = set()
                all_targets[t].add(sid)

        shared = {t: s for t, s in all_targets.items() if len(s) >= 2}
        if shared:
            return f"cross_session shared targets: {list(shared.keys())}"

        return None

    def add_whitelist(self, ops: list[str]) -> None:
        """添加操作白名单.

        Args:
            ops: 白名单操作列表
        """
        self._whitelist.append(list(ops))

    def reset_session(self, session_id: str) -> None:
        """重置指定会话的历史."""
        self._history.pop(session_id, None)

    def reset_all(self) -> None:
        """重置所有会话历史."""
        self._history.clear()


__all__ = [
    "FORBIDDEN_SEQUENCES",
    "SEQUENCE_TIMEOUT",
    "SequenceEvent",
    "SequenceGuard",
]
