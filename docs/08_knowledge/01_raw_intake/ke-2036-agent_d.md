---
module_id: KE-1945-----------------d-02-000
status: active
title: 2.8 Agent 级数字签名——不可否认性（决策 D-020-14）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.8 Agent 级数字签名——不可否认性（决策 D-020-14）

2.8 Agent 级数字签名——不可否认性（决策 D-020-14）

> **决策 D-020-14**（新增）：HMAC 只能证明"数据来自知道 secret 的系统"，不能证明"具体是哪个 Agent 操作的"。引入 Agent 级 Ed25519 数字签名实现不可否认性（non-repudiation）。每个 Agent 拥有独立的 Ed25519 密钥对，操作时用私钥对 `entry_hash` 签名，审计条目携带 `agent_signature` + `agent_did` + 公钥 PEM。任何第三方可以离线验证签名，不需要知道 HMAC secret。

```yaml
agent_signing:
  algorithm: "Ed25519"
  key_generation:
    trigger: "Agent 身份创建时（MOD-INF-018 AgentIdentity 初始化）"
    storage: "Agent 私钥存储在密钥库（非审计系统），公钥写入 AgentIdentity 元数据"
    rotation: "每 90 天或 Agent 权限升级时重新生成"

  signing:
    description: "Agent 私钥签名(entry_hash) → agent_signature 写入审计条目"
    verification: "公钥验证(entry_hash, agent_signature)——任何第三方可离线验证"

  did:
    format: "did:zephyr:{sha256(Ed25519_public_key)[:16]}"
    example: "did:zephyr:a1b2c3d4e5f6g7h8"
    binding: "DID 绑定到 Ed25519 公钥——不可伪造"

  non_repudiation_chain:
    description: "HMAC（系统级）证明'来自本系统' + Ed25519（Agent 级）证明'来自 Agent X' —— 双重保障"
    hmac_only: "完整性 + 来源验证（弱——不区分 Agent）"
    ed25519: "完整性 + 来源验证 + 不可否认性（强——区分 Agent，法庭可采信）"
```

```python
class AgentSigner:
    """Agent 级 Ed25519 签名器"""

    def __init__(self, agent_did: str, private_key_pem: str) -> None:
        self._did = agent_did
        self._private_key = Ed25519PrivateKey.from_pem(private_key_pem)
        self._public_key_pem = self._private_key.public_key().to_pem()

    def sign(self, entry_hash: str) -> str:
        """对 entry_hash 签名——返回 base64 签名"""
        return base64.b64encode(self._private_key.sign(entry_hash.encode())).decode()

    @staticmethod
    def verify(entry_hash: str, signature: str, public_key_pem: str) -> bool:
        """离线验证签名——无需任何 secret"""
        key = Ed25519PublicKey.from_pem(public_key_pem)
        try:
            key.verify(base64.b64decode(signature), entry_hash.encode())
            return True
        except Exception:
            return False

class DIDRegistry:
    """DID → 公钥映射注册表"""
    def register(self, did: str, public_key_pem: str, agent_metadata: dict) -> None: ...
    def resolve(self, did: str) -> str | None: ...  # 返回公钥 PEM
    def revoke(self, did: str, reason: str) -> None: ...
```
