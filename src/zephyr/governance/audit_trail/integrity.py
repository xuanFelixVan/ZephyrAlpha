# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.integrity
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.agent_signer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit-trail.integrity — MOD-INF-020 · 密码学完整性验证器
===========================================================
蓝图 §5 · 哈希链验证 + HMAC验证 + Agent签名验证 + Merkle树聚合 (§2.2)

算法
----
  - 链式验证: 逐条验证 prev_entry_hash == SHA-256(上一条事件)
  - HMAC 验证: 验证 HMAC-SHA256 系统级签名
  - Ed25519 验证: 验证 Agent 私钥签名
  - Merkle 树聚合: 按批次(batch_id)构建 Merkle 树，产出 merkle_root
  - 批量验证: 一次性验证整个 event log 的完整性
  - 报告: 返回被篡改/中断的 entry_id 列表
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import hashlib
import hmac
import json
import logging
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)


class MerkleAggregator:
    """Merkle 树构建器——蓝图 §2.2 cryptographic_integrity.merkle_aggregation。

    将一批审计事件的 entry_hash 作为叶子节点，构建 Merkle 树并返回 root。
    使用 SHA-256 作为哈希函数，每对兄弟节点拼接后哈希。

    使用方式:
        aggregator = MerkleAggregator()
        root = aggregator.build(entry_hashes)
    """

    @staticmethod
    def build(leaves: list[str]) -> str:
        """构建 Merkle 树——返回根哈希。

        Args:
            leaves: entry_hash 列表（叶子节点）

        Returns:
            merkle_root 的十六进制字符串。空列表返回空字符串。
        """
        if not leaves:
            return ""

        hashes = [bytes.fromhex(h) for h in leaves if h]

        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])

            next_level: list[bytes] = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_level.append(hashlib.sha256(combined).digest())
            hashes = next_level

        return hashes[0].hex() if hashes else ""

    @staticmethod
    def verify(leaves: list[str], claimed_root: str) -> bool:
        """验证 Merkle root 是否匹配。

        Args:
            leaves: 叶子节点的 entry_hash 列表
            claimed_root: 声称的 Merkle root

        Returns:
            True 如果重建的 root 与 claimed_root 一致
        """
        actual_root = MerkleAggregator.build(leaves)
        return hmac.compare_digest(actual_root.encode(), claimed_root.encode())


class IntegrityVerifier:
    def __init__(
        self,
        event_log_path: Path | str = Path.cwd() / "data" / "audit-trail" / "events.jsonl",
        hmac_key: str = "",
    ) -> None:
        self._event_log_path = Path(event_log_path)
        # 修复：原使用 AUDIT_HMAC_KEY 与 writer.py 的 ZEPHYR_AUDIT_HMAC_SECRET 不一致，
        # 导致验证方永远使用空密钥=不验证。统一为 ZEPHYR_AUDIT_HMAC_SECRET。
        if not hmac_key:
            import os
            hmac_key = os.environ.get("ZEPHYR_AUDIT_HMAC_SECRET", "")
        self._hmac_key = hmac_key.encode("utf-8") if hmac_key else b""

    def verify_chain(self) -> dict[str, Any]:
        if not self._event_log_path.exists():
            return {"status": "no_data", "events_checked": 0, "issues": []}

        issues: list[str] = []
        prev_hash = ""
        event_count = 0

        with open(self._event_log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event_count += 1
                event = json.loads(line)

                stored_prev = event.get("prev_entry_hash", event.get("prev_hash", ""))
                if stored_prev != prev_hash:
                    issues.append(
                        f"event #{event_count}: prev_entry_hash mismatch "
                        f"(expected={prev_hash[:16]}..., got={stored_prev[:16]}...)"
                    )

                verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
                event_str = dumps(verify_event, ensure_ascii=False, sort_keys=True)
                prev_hash = hashlib.sha256(event_str.encode("utf-8")).hexdigest()

                if self._hmac_key:
                    stored_hmac = event.get("hmac_signature", "")
                    if stored_hmac:
                        verify_event = {k: v for k, v in event.items() if k not in ("hmac_signature", "entry_hash")}
                        verify_str = dumps(verify_event, ensure_ascii=False, sort_keys=True)
                        expected_hmac = hmac.new(
                            self._hmac_key,
                            verify_str.encode("utf-8"),
                            hashlib.sha256,
                        ).hexdigest()
                        if not hmac.compare_digest(expected_hmac, stored_hmac):
                            issues.append(f"event #{event_count}: HMAC signature mismatch")

                stored_agent_sig = event.get("signature", "")
                if stored_agent_sig:
                    entry_hash = event.get("entry_hash", "")
                    if entry_hash:
                        v = self._verify_agent_signature_inline(event, stored_agent_sig)
                        if v is False:
                            issues.append(f"event #{event_count}: Agent signature invalid")

        status = "valid" if not issues else "compromised"
        return {"status": status, "events_checked": event_count, "issues": issues}

    def verify_single(self, event_index: int) -> dict[str, Any]:
        if not self._event_log_path.exists():
            return {"status": "no_data", "valid": False}

        with open(self._event_log_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i == event_index - 1:
                    event = json.loads(line.strip())
                    # 5.37.13 修复：统一哈希逻辑——排除 entry_hash 和 hmac_signature，
                    # 与 verify_chain() 保持一致，避免两种验证方法结果矛盾。
                    verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
                    calc_hash = hashlib.sha256(
                        dumps(verify_event, ensure_ascii=False, sort_keys=True).encode("utf-8")
                    ).hexdigest()
                    result: dict[str, Any] = {
                        "status": "found",
                        "event_index": event_index,
                        "valid": True,
                        "chain_hash": calc_hash,
                    }
                    if self._hmac_key:
                        stored_hmac = event.get("hmac_signature", "")
                        if stored_hmac:
                            # 修复：HMAC 验证 entry_hash 字符串，与 writer.py 写入方一致。
                            entry_hash_str = event.get("entry_hash", "")
                            expected_hmac = hmac.new(
                                self._hmac_key,
                                entry_hash_str.encode("utf-8"),
                                hashlib.sha256,
                            ).hexdigest()
                            result["hmac_valid"] = hmac.compare_digest(expected_hmac, stored_hmac)
                    return result
        return {"status": "not_found", "valid": False}

    def _verify_agent_signature_inline(self, event: dict[str, Any], signature_hex: str) -> bool | None:
        try:
            from zephyr.governance.audit_trail.agent_signer import AgentSigner

            entry_hash = event.get("entry_hash", "")
            if not entry_hash:
                return None
            public_key_hex = event.get("metadata", {}).get("agent_public_key", "")
            if not public_key_hex:
                return None
            return AgentSigner.verify(event, public_key_hex, signature_hex)
        except ImportError:
            return None
        except Exception:
            return False
