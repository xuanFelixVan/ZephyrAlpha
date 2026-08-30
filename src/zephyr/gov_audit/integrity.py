# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.integrity
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.agent_signer
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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event_log_path 参数
#   fields: 参数 event_log_path（无注解）
#   code: integrity.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: hmac_key 参数
#   fields: 参数 hmac_key（无注解）
#   code: integrity.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MerkleAggregator
#   name_en: MerkleAggregator
#   intro: Merkle 树构建器——蓝图 §2.2 cryptographic_integrity.merkle_aggrega…
#   desc: Merkle 树构建器——蓝图 §2.2 cryptographic_integrity.merkle_aggregation。 将一批审计事件的 entry_hash 作为叶子…；公共方法（定义序）: build,…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② IntegrityVerifier
#   name_en: IntegrityVerifier
#   intro: class IntegrityVerifier 源码 L143-L371
#   desc: 公共方法（定义序）: event_log_path, hmac_key, verify_chain, verify_single；源码 L143-L371
#   inputs: event_log_path hmac_key
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: MerkleAggregator, IntegrityVerifier
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import AUDIT_DATA_DIR  # 路径真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.io.serialization import dumps

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
        event_log_path: Path | str | None = None,
        hmac_key: str | None = None,
    ) -> None:
        # 治本（裁定#6 路径SSoT）：默认路径必须为绝对路径（项目硬约束"禁止相对路径"），
        # 真源为 zephyr.shared.io.paths.AUDIT_DATA_DIR。
        if event_log_path is None:
            self._event_log_path = AUDIT_DATA_DIR / "events.jsonl"
        else:
            self._event_log_path = Path(event_log_path)
        # 5.62.2 治本：未显式传 hmac_key（None）时经 SecretProvider 统一密钥源解析
        # （与 writer.py 签名方同一密钥源 ZEPHYR_AUDIT_HMAC_SECRET），禁止裸 os.environ。
        # 显式传 "" 表示禁用 HMAC（测试 SSoT：_hmac_key 应为 b""）。
        if hmac_key is None:
            from zephyr.gov_audit.writer import resolve_audit_hmac_secret

            hmac_key = resolve_audit_hmac_secret()
        if not hmac_key:
            _logger.warning("ZEPHYR_AUDIT_HMAC_SECRET 未设置，HMAC 验证明确降级为跳过（不验证签名）")
        self._hmac_key = hmac_key.encode("utf-8") if hmac_key else b""

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def event_log_path(self):
        """只读：event_log_path（Stage 4 公共化）。"""
        return self._event_log_path

    @event_log_path.setter
    def event_log_path(self, value):
        """写入：event_log_path（Stage 4 公共化）。"""
        self._event_log_path = value

    @property
    def hmac_key(self):
        """只读：hmac_key（Stage 4 公共化）。"""
        return self._hmac_key

    @hmac_key.setter
    def hmac_key(self, value):
        """写入：hmac_key（Stage 4 公共化）。"""
        self._hmac_key = value

    def verify_chain(self) -> dict[str, Any]:
        if not self._event_log_path.exists():
            return {"status": "no_data", "events_checked": 0, "issues": []}

        issues: list[str] = []
        # 治本（裁定#10 双契约并存）：首条事件的 prev 字段接受 "" 或 "0"*64 两种约定。
        # - writer 生产约定: prev_hash="0"*64 + HMAC(entry_hash)
        # - legacy 单元约定: prev_entry_hash="" + HMAC(canonical(event \ {entry_hash, hmac_signature}))
        # 两者安全等价：攻击者无 key 无法伪造任一形式；创世值不承载完整性保证
        #   （真正的保护来自后续事件的哈希链接）。
        prev_hash = ""
        genesis_seen = False
        event_count = 0

        with open(self._event_log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event_count += 1
                event = json.loads(line)

                stored_prev = event.get("prev_entry_hash", event.get("prev_hash", ""))
                if not genesis_seen:
                    # 创世哨兵：首条事件允许 "" 或 "0"*64 两种约定
                    if stored_prev not in ("", "0" * 64):
                        issues.append(
                            f"event #{event_count}: genesis prev_hash must be '' or '0'*64, got={stored_prev[:16]}..."
                        )
                    genesis_seen = True
                elif stored_prev != prev_hash:
                    issues.append(
                        f"event #{event_count}: prev_entry_hash mismatch "
                        f"(expected={prev_hash[:16]}..., got={stored_prev[:16]}...)"
                    )

                verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
                event_str = dumps(verify_event, ensure_ascii=False, sort_keys=True)
                prev_hash = hashlib.sha256(event_str.encode("utf-8")).hexdigest()

                # 治本（AI-AUDIT12 审计链自一致性）：校验 stored entry_hash == 内容重算哈希。
                # 原实现仅做链式 prev 链接 + HMAC-over-entry_hash：篡改"最后一条"事件内容
                # （保留 entry_hash/hmac_signature 不变）时，无后续事件暴露断链，HMAC 也只
                # 证明 entry_hash 未被替换而非内容未被篡改——末事件篡改不可检测。
                # canonical 口径（全部既有测试契约实测并存）：
                # - production 事件（writer 写入，标记=prev_hash 字段存在）：payload 含 prev_hash
                # - legacy 事件：两种历史变体并存（含/不含 prev_entry_hash），任一匹配即通过
                #   （SHA-256 抗原像，接受两个确定性 canonical 不削弱篡改检测）。
                is_production_format = "prev_hash" in event
                stored_entry_hash = event.get("entry_hash", "")
                if is_production_format and not stored_entry_hash:
                    issues.append(f"event #{event_count}: production event missing entry_hash (possible strip tamper)")
                if stored_entry_hash:
                    entry_candidates = [verify_event]
                    if not is_production_format and "prev_entry_hash" in verify_event:
                        entry_candidates.append({k: v for k, v in verify_event.items() if k != "prev_entry_hash"})
                    if not any(
                        hmac.compare_digest(
                            hashlib.sha256(dumps(c, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
                            stored_entry_hash,
                        )
                        for c in entry_candidates
                    ):
                        issues.append(f"event #{event_count}: entry_hash mismatch (content tampered or hash stripped)")
                if is_production_format and self._hmac_key and not event.get("hmac_signature", ""):
                    issues.append(
                        f"event #{event_count}: production event missing hmac_signature (possible strip tamper)"
                    )

                if self._hmac_key:
                    stored_hmac = event.get("hmac_signature", "")
                    if stored_hmac and not self._hmac_matches(event):
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

    def _hmac_matches(self, event: dict[str, Any]) -> bool:
        r"""验证 HMAC 签名——治本（裁定#10 双契约并存）：同时支持两种安全等价的签名约定。

        1. writer 生产约定: HMAC-SHA256(key, entry_hash 字符串)
        2. legacy 单元约定: HMAC-SHA256(key, canonical(event \ {entry_hash, hmac_signature}))

        攻击者无 key 无法伪造任一形式；任一形式通过即视为验证通过。
        """
        stored_hmac = event.get("hmac_signature", "")
        if not stored_hmac:
            return True
        # 尝试 writer 生产约定：HMAC over entry_hash 字符串
        entry_hash_str = event.get("entry_hash", "")
        if entry_hash_str:
            expected_over_hash = hmac.new(self._hmac_key, entry_hash_str.encode("utf-8"), hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected_over_hash, stored_hmac):
                return True
        # 回退 legacy 单元约定：HMAC over canonical(event \ {entry_hash, hmac_signature})
        verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
        canonical_str = dumps(verify_event, ensure_ascii=False, sort_keys=True)
        expected_over_event = hmac.new(self._hmac_key, canonical_str.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_over_event, stored_hmac)

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
                    # 治本（AI-AUDIT12 审计链自一致性）：valid 不再恒 True——stored entry_hash
                    # 存在时必须与内容重算哈希一致（canonical 口径同 verify_chain：production
                    # 含 prev_hash；legacy 含/不含 prev_entry_hash 两变体任一匹配）；否则视为
                    # 内容篡改 valid=False。
                    stored_entry_hash = event.get("entry_hash", "")
                    is_production_format = "prev_hash" in event
                    entry_hash_valid = True
                    if stored_entry_hash:
                        single_candidates = [verify_event]
                        if not is_production_format and "prev_entry_hash" in verify_event:
                            single_candidates.append({k: v for k, v in verify_event.items() if k != "prev_entry_hash"})
                        entry_hash_valid = any(
                            hmac.compare_digest(
                                hashlib.sha256(
                                    dumps(c, ensure_ascii=False, sort_keys=True).encode("utf-8")
                                ).hexdigest(),
                                stored_entry_hash,
                            )
                            for c in single_candidates
                        )
                    result: dict[str, Any] = {
                        "status": "found",
                        "event_index": event_index,
                        "valid": entry_hash_valid,
                        "chain_hash": calc_hash,
                    }
                    if not entry_hash_valid:
                        result["issue"] = "entry_hash mismatch (content tampered or hash stripped)"
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
                        elif is_production_format:
                            # 治本（AI-AUDIT12）：production 事件必有 hmac_signature（writer
                            # 恒签名）——缺失即剥离篡改，显式判 invalid（原静默跳过）。
                            result["hmac_valid"] = False
                            result["valid"] = False
                            result.setdefault("issue", "production event missing hmac_signature")
                    return result
        return {"status": "not_found", "valid": False}

    def _verify_agent_signature_inline(self, event: dict[str, Any], signature_hex: str) -> bool | None:
        try:
            from zephyr.gov_audit.agent_signer import AgentSigner

            entry_hash = event.get("entry_hash", "")
            if not entry_hash:
                return None
            public_key_hex = event.get("metadata", {}).get("agent_public_key", "")
            if not public_key_hex:
                return None
            return AgentSigner.verify(event, public_key_hex, signature_hex)
        except ImportError:
            return None
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False
