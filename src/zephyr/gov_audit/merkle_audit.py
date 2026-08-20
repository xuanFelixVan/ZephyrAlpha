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

"""

Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.gov_audit (MOD-INF-020).

原内存Merkle树已被MOD-INF-020的MerkleAggregator+HourlyMerkleAggregator超集覆盖。
本模块保留API兼容性，内部委托至SSoT。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 升级事件 字典
#   fields: escalation_event（任意可 JSON 序列化的事件字典）
#   code: MerkleAudit.record(escalation_event) L74
# 层: 算法
# - id: A1
#   name_zh: ① 事件哈希入叶
#   name_en: MerkleTree.add_event
#   intro: 把事件字典序列化后算 SHA-256 当一片叶子存起来
#   desc: json.dumps(event, sort_keys=True).encode() → hashlib.sha256 → hexdigest 追加到 _leaves
#   inputs: I1
#   outputs: 叶子哈希列表 _leaves
# - id: A2
#   name_zh: ② Merkle 根计算
#   name_en: MerkleTree.root_hash
#   intro: 把所有叶子委托给 SSoT 聚合器算出 Merkle 根
#   desc: 空树返回 "empty"；否则 _MerkleAggregator.build(self._leaves)（zephyr.gov_audit.integrity）
#   inputs: A1
#   outputs: Merkle 根哈希
#   invariant: SSoT=zephyr.gov_audit(MOD-INF-020)，本文件仅为兼容别名
# - id: A3
#   name_zh: ③ 记录并取根
#   name_en: MerkleAudit.record/get_root
#   intro: 对外门面：record 先加事件再返回最新根，get_root 只查不记
#   desc: record()=add_event+root_hash 返回 str；get_root()=root_hash
#   inputs: A1 A2
#   outputs: 根哈希 str
# 层: 输出
# - id: O1
#   name_zh: Merkle 根哈希
#   name_en: merkle root hash str
#   intro: 升级事件序列的完整性指纹，可用于审计对账
#   invariant: 空树返回 "empty"
#   downstream: zephyr.governance.__init__（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
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
