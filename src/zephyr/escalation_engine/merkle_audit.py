# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §8

# [MODULE] zephyr.escalation_engine.merkle_audit

# [INVARIANTS] SSoT=zephyr.audit_trail(MOD-INF-020);本文件为兼容别名

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine.__init__

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] record()->str;get_root()->str

# [TESTS]

"""Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.audit_trail (MOD-INF-020).

原内存Merkle树已被MOD-INF-020的MerkleAggregator+HourlyMerkleAggregator超集覆盖。
本模块保留API兼容性，内部委托至SSoT。
"""
from __future__ import annotations

from zephyr.audit_trail.integrity import MerkleAggregator as _MerkleAggregator


class MerkleTree:
    def __init__(self):
        self._leaves: list[str] = []
        self._aggregator = _MerkleAggregator

    def add_event(self, event: dict) -> None:
        import hashlib, json
        self._leaves.append(hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest())

    def root_hash(self) -> str:
        if not self._leaves:
            return "empty"
        return self._aggregator.build(self._leaves)


class MerkleAudit:
    def __init__(self):
        self._tree = MerkleTree()

    def record(self, escalation_event: dict) -> str:
        self._tree.add_event(escalation_event)
        return self._tree.root_hash()

    def get_root(self) -> str:
        return self._tree.root_hash()
