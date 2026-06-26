---
module_id: KE-2955
status: active
title: tests/integration/test_integration_contracts.py
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# tests/integration/test_integration_contracts.py

tests/integration/test_integration_contracts.py
import pytest

class TestIntegrationContract:
    """每个CT-*契约的通用验证模板"""

    CONTRACT_ID: str  # 子类覆写

    def test_producer_side_exists(self):
        """生产方实现文件存在"""
        ...

    def test_consumer_side_exists(self):
        """消费方实现文件存在"""
        ...

    def test_contract_payload_schema_matches(self):
        """payload字段与契约YAML声明一致"""
        ...

    def test_circuit_breaker_fires_on_threshold(self):
        """熔断在failure_threshold触发"""
        ...

    def test_circuit_breaker_recovers_after_timeout(self):
        """熔断在recovery_after_seconds恢复"""
        ...
```
