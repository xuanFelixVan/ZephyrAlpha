---
module_id: KE-2601
status: active
title: Crypto-Shredding
category: module_blueprint
ttl: permanent
---

# Crypto-Shredding

Crypto-Shredding

```python
class CryptoShredding:
    """RI-13 EventStore GDPR 兼容——用 per-stream AES 密钥加密敏感字段
    删除权 = 销毁该 stream 的 AES 密钥 → 所有历史事件不可解密 = 逻辑删除
    """
    _stream_keys: dict[str, bytes] = {}  # stream_id → AES-256 key

    async def anonymize_stream(self, stream_id: str) -> None:
        """删除加密密钥 = 该 stream 的所有历史事件永久不可读"""
        del self._stream_keys[stream_id]
        audit.record(f"CRYPTO_SHRED: stream={stream_id}")
```
