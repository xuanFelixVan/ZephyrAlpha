# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §8
# [MODULE] zephyr.gov_audit.merkle_audit
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.integrity
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SSoT=zephyr.gov_audit(MOD-INF-020);本文件为兼容别名
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] record()->str;get_root()->str
# [TESTS]
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.gov_audit (MOD-INF-020).

原内存Merkle树已被MOD-INF-020的MerkleAggregator+HourlyMerkleAggregator超集覆盖。
本模块保留API兼容性，内部委托至SSoT。
"""

from __future__ import annotations

from zephyr.gov_audit.integrity import MerkleAggregator as _MerkleAggregator


class MerkleTree:
    def __init__(self):
        self._leaves: list[str] = []
        self._aggregator = _MerkleAggregator

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def leaves(self) -> list[str]:
        """只读：leaves（Stage 4 公共化）。"""
        return self._leaves

    @leaves.setter
    def leaves(self, value):
        """写入：leaves（Stage 4 公共化）。"""
        self._leaves = value


    def add_event(self, event: dict) -> None:
        import hashlib
        import json

        self._leaves.append(hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest())

    def root_hash(self) -> str:
        if not self._leaves:
            return "empty"
        return self._aggregator.build(self._leaves)


class MerkleAudit:
    def __init__(self):
        self._tree = MerkleTree()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def tree(self):
        """只读：tree（Stage 4 公共化）。"""
        return self._tree

    @tree.setter
    def tree(self, value):
        """写入：tree（Stage 4 公共化）。"""
        self._tree = value


    def record(self, escalation_event: dict) -> str:
        self._tree.add_event(escalation_event)
        return self._tree.root_hash()

    def get_root(self) -> str:
        return self._tree.root_hash()
