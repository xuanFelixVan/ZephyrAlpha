# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.gov_audit.trust_ring_manager
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: trust_ring_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① TrustRingManager
#   name_en: TrustRingManager
#   intro: class TrustRingManager 源码 L97-L181
#   desc: 公共方法（定义序）: register_identity, can, grant, revoke, get_ring, verify, recent_grants, active_identities；源码 L97-L…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TrustRingManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path


class RingLevel:
    R0_OWNER = 0
    R1_ADMIN = 1
    R2_AGENT = 2
    R3_OBSERVER = 3


RING_LABELS: dict[int, str] = {
    RingLevel.R0_OWNER: "owner",
    RingLevel.R1_ADMIN: "admin",
    RingLevel.R2_AGENT: "agent",
    RingLevel.R3_OBSERVER: "observer",
}


@dataclass
class TrustSignature:
    ring: int
    identity: str
    action: str
    payload_hash: str
    signed_at: float = field(default_factory=time.time)


PREMISSION_MAP: dict[int, set[str]] = {
    RingLevel.R0_OWNER: {
        "modify_budget",
        "add_model",
        "disable_gate",
        "grant_trust",
        "revoke_trust",
        "view_all",
        "audit_all",
        "execute",
    },
    RingLevel.R1_ADMIN: {"modify_budget", "add_model", "view_all", "audit_all", "execute"},
    RingLevel.R2_AGENT: {"view_own", "use_model", "execute"},
    RingLevel.R3_OBSERVER: {"view_summary"},
}


class TrustRingManager:
    _KEY_FILE = ".zephyr_secure/trust_keys.json"

    def __init__(self):
        self._keys: dict[str, dict] = {}
        self._trust_grants: list[TrustSignature] = []
        self._active_ring: dict[str, int] = {}
        self._load_keys()

    def _load_keys(self) -> None:
        kf = Path(self._KEY_FILE)
        if kf.exists():
            with open(kf, encoding="utf-8") as f:
                self._keys = json.load(f)

    def _save_keys(self) -> None:
        kf = Path(self._KEY_FILE)
        kf.parent.mkdir(parents=True, exist_ok=True)
        with open(kf, "w", encoding="utf-8") as f:
            json.dump(self._keys, f, indent=2)

    def register_identity(self, identity: str, ring: int) -> str:
        key_hash = hashlib.sha256(f"{identity}:{time.time()}:{os.urandom(16).hex()}".encode()).hexdigest()
        self._keys[identity] = {"ring": ring, "key_hash": key_hash, "registered_at": time.time()}
        self._active_ring[identity] = ring
        self._save_keys()
        return key_hash

    def can(self, identity: str, action: str) -> bool:
        ring = self._active_ring.get(identity, RingLevel.R3_OBSERVER)
        allowed = PREMISSION_MAP.get(ring, set())
        if action in allowed:
            return True
        for r in range(ring, -1, -1):
            if action in PREMISSION_MAP.get(r, set()):
                return True
        return False

    def grant(self, granter: str, grantee: str, target_ring: int) -> TrustSignature | None:
        if not self.can(granter, "grant_trust"):
            return None
        if target_ring <= self._active_ring.get(granter, RingLevel.R3_OBSERVER):
            return None

        self._active_ring[grantee] = target_ring
        sig = TrustSignature(
            ring=target_ring,
            identity=grantee,
            action=f"trust_granted_by_{granter}",
            payload_hash=hashlib.sha256(f"{grantee}:{target_ring}".encode()).hexdigest()[:16],
        )
        self._trust_grants.append(sig)
        self._save_keys()
        return sig

    def revoke(self, revoker: str, target: str) -> bool:
        if not self.can(revoker, "revoke_trust"):
            return False
        if target == "owner":
            return False
        self._active_ring[target] = RingLevel.R3_OBSERVER
        self._save_keys()
        return True

    def get_ring(self, identity: str) -> int:
        return self._active_ring.get(identity, RingLevel.R3_OBSERVER)

    def verify(self, identity: str, action: str) -> TrustSignature | None:
        if not action:
            return None
        ring = self._active_ring.get(identity, RingLevel.R3_OBSERVER)
        sig = TrustSignature(
            ring=ring,
            identity=identity,
            action=action,
            payload_hash=hashlib.sha256(f"{identity}:{action}:{time.time()}".encode()).hexdigest()[:16],
        )
        self._trust_grants.append(sig)
        return sig

    def recent_grants(self, n: int = 20) -> list[TrustSignature]:
        return self._trust_grants[-n:]

    def active_identities(self) -> dict[str, int]:
        return dict(self._active_ring)
