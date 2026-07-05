# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.agent_signer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_agent_signer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit-trail.agent_signer — MOD-INF-020 · Agent Ed25519 签名器
===============================================================
蓝图 §7 · 每条审计记录的不可否认性约束

流程
----
  1. Agent 私钥签名(sha256(event_json))
  2. 签名追加到 event.signature 字段
  3. Notary 公钥可验证签名
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

_logger = logging.getLogger(__name__)


class AgentSigner:
    @staticmethod
    def generate_key_pair() -> tuple[str, str]:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        private_key = Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes_raw()
        public_bytes = private_key.public_key().public_bytes_raw()
        return private_bytes.hex(), public_bytes.hex()

    @staticmethod
    def sign(event: dict[str, Any], private_key_hex: str) -> str:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        event_copy = {k: v for k, v in event.items() if k != "signature"}
        event_json = json.dumps(event_copy, ensure_ascii=False, sort_keys=True, default=str)
        event_hash = hashlib.sha256(event_json.encode("utf-8")).digest()

        private_key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
        signature = private_key.sign(event_hash)
        return signature.hex()

    @staticmethod
    def verify(event: dict[str, Any], public_key_hex: str, signature_hex: str) -> bool:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        event_copy = {k: v for k, v in event.items() if k != "signature"}
        event_json = json.dumps(event_copy, ensure_ascii=False, sort_keys=True, default=str)
        event_hash = hashlib.sha256(event_json.encode("utf-8")).digest()

        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        try:
            public_key.verify(bytes.fromhex(signature_hex), event_hash)
            return True
        except InvalidSignature:
            return False
