# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint_qmt_bridge_health.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-L28-QMTBH | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.frontend.test_qmt_bridge_health
# [TESTS] src/zephyr/frontend/dashboard/components/qmt_bridge_health.py
"""MOD-L28-QMTBH 单元测试：qmt_bridge_health 文件桥健康监控面板。

蓝图验收（§8 测试策略）：
fetch fail-closed（None/异常→assembled=False）+ 字段映射正确 +
render dict 可序列化 + 三级 level 映射预期颜色键。
数据源全部内存构造（mock assembly），不连真实文件桥。
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

pytest.importorskip(
    "zephyr.frontend.dashboard.components.qmt_bridge_health",
    reason="qmt_bridge_health not importable",
)

from zephyr.frontend.dashboard.components.qmt_bridge_health import (
    ComponentHealth,
    QmtBridgeHealthData,
    fetch_qmt_bridge_health,
    render_qmt_bridge_health,
)


def _mock_assembly(level: str = "ok") -> MagicMock:
    """构造返回聚合 dict 的 mock assembly"""
    assembly = MagicMock()
    assembly.health_check.return_value = {
        "component": "qmt_file_bridge_assembly",
        "type": "assembly",
        "ok": level == "ok",
        "level": level,
        "components": {
            "qmt_sim": {
                "type": "broker",
                "level": "ok",
                "connected": True,
                "sync_thread_alive": True,
                "export_age_seconds": {"Order.csv": 2.1},
                "counter": {"pending_orders": 1, "positions": 1, "available_cash": "9998116.60"},
            },
            "quote_qmt_sim": {
                "type": "quote_provider",
                "level": "ok",
                "file_age_seconds": 1.2,
                "fresh": True,
            },
            "queue_qmt_sim": {
                "type": "order_queue",
                "level": "degraded",
                "running": True,
                "pending": 2,
                "sent": 8,
                "failed": 1,
                "detail": "1 笔发送失败待重试",
            },
        },
    }
    return assembly


class TestFetchQmtBridgeHealth:
    """fetch_qmt_bridge_health 测试"""

    def test_assembly_none_fail_closed(self):
        """assembly None → assembled=False（fail-closed）"""
        data = fetch_qmt_bridge_health(None)
        assert data.assembled is False
        assert data.overall_level == "down"
        assert data.components == []
        assert data.checked_at != ""

    def test_assembly_exception_fail_closed(self):
        """assembly 抛异常 → assembled=False（fail-closed）"""
        assembly = MagicMock()
        assembly.health_check.side_effect = RuntimeError("boom")
        data = fetch_qmt_bridge_health(assembly)
        assert data.assembled is False
        assert data.components == []

    def test_field_mapping(self):
        """聚合 dict → ComponentHealth 字段映射正确"""
        data = fetch_qmt_bridge_health(_mock_assembly())
        assert data.assembled is True
        assert data.overall_level == "ok"
        assert len(data.components) == 3

        broker = next(c for c in data.components if c.name == "qmt_sim")
        assert broker.type == "broker"
        assert broker.level == "ok"
        assert broker.metrics["在途挂单"] == 1
        assert broker.metrics["可用资金"] == "9998116.60"

        quote = next(c for c in data.components if c.name == "quote_qmt_sim")
        assert quote.type == "quote_provider"
        assert quote.metrics["新鲜"] is True

        queue = next(c for c in data.components if c.name == "queue_qmt_sim")
        assert queue.type == "order_queue"
        assert queue.level == "degraded"
        assert queue.detail == "1 笔发送失败待重试"
        assert queue.metrics["待发"] == 2

    def test_non_dict_return_fail_closed(self):
        """health_check 返回非 dict → assembled=False"""
        assembly = MagicMock()
        assembly.health_check.return_value = "not-a-dict"
        data = fetch_qmt_bridge_health(assembly)
        assert data.assembled is False


class TestRenderQmtBridgeHealth:
    """render_qmt_bridge_health 测试"""

    def test_render_dict_payload_serializable(self):
        """dict payload 可 JSON 序列化（无 panel 环境）"""
        data = fetch_qmt_bridge_health(_mock_assembly())
        payload = render_qmt_bridge_health(data)
        # 剔除 _layout（panel 对象不可序列化）
        payload.pop("_layout", None)
        json.dumps(payload, ensure_ascii=False)
        assert payload["assembled"] is True
        assert payload["overall_level"] == "ok"
        assert len(payload["components"]) == 3

    def test_render_unassembled(self):
        """未装配 → payload assembled=False"""
        data = QmtBridgeHealthData(assembled=False, overall_level="down", checked_at="12:00:00")
        payload = render_qmt_bridge_health(data)
        assert payload["assembled"] is False
        assert payload["components"] == []

    def test_level_visual_mapping(self):
        """三级 level 在 payload 中原样透传（视觉映射在 _layout 层）"""
        data = fetch_qmt_bridge_health(_mock_assembly(level="degraded"))
        payload = render_qmt_bridge_health(data)
        assert payload["overall_level"] == "degraded"
        levels = {c["name"]: c["level"] for c in payload["components"]}
        assert levels["qmt_sim"] == "ok"
        assert levels["queue_qmt_sim"] == "degraded"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
