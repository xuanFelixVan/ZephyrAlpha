# [BLUEPRINT] MOD-INF-044 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] zephyr.shared.observability.metrics_server
# [DOMAIN] D_SHARED
# [A_module] module_id=MOD-TEST_METRICS_SERVER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""metrics_server 单元测试（P1-5 Prometheus /metrics 端点）。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

import urllib.error
import urllib.request

from zephyr.shared.observability.metrics import get_registry
from zephyr.shared.observability.metrics_server import start_metrics_server


def _fetch(server, path: str) -> tuple[int, bytes]:
    """向 metrics_server 发 GET 请求，返回 (status_code, body)。"""
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


class TestMetricsServer:
    def setup_method(self):
        get_registry().reset()

    def teardown_method(self):
        get_registry().reset()

    def test_start_returns_server(self):
        """start_metrics_server 返回 HTTPServer 实例"""
        server = start_metrics_server(port=0)
        assert server is not None
        try:
            assert server.server_address[1] > 0
        finally:
            server.shutdown()
            server.server_close()

    def test_metrics_endpoint_returns_prometheus_text(self):
        """/metrics 返回 200 + Prometheus 文本，包含已注册的 counter"""
        server = start_metrics_server(port=0)
        assert server is not None
        try:
            get_registry().inc("zephyr_tick_received_total")
            status, body = _fetch(server, "/metrics")
            assert status == 200
            text = body.decode("utf-8")
            assert "zephyr_tick_received_total" in text
        finally:
            server.shutdown()
            server.server_close()

    def test_metrics_endpoint_content_type(self):
        """/metrics 响应头 Content-Type 含 text/plain"""
        server = start_metrics_server(port=0)
        assert server is not None
        try:
            port = server.server_address[1]
            url = f"http://127.0.0.1:{port}/metrics"
            with urllib.request.urlopen(url, timeout=2) as resp:
                ct = resp.headers.get("Content-Type", "")
                assert "text/plain" in ct
        finally:
            server.shutdown()
            server.server_close()

    def test_health_endpoint_returns_ok(self):
        """/health 返回 200 + 契约 JSON {"status","uptime_seconds"}（CAND-OBS-001 §3.4 升级）"""
        import json as _json

        server = start_metrics_server(port=0)
        assert server is not None
        try:
            status, body = _fetch(server, "/health")
            assert status == 200
            payload = _json.loads(body.decode("utf-8"))
            assert payload["status"] == "ok"
            assert payload["uptime_seconds"] >= 0.0
        finally:
            server.shutdown()
            server.server_close()

    def test_unknown_path_returns_404(self):
        """未知路径返回 404"""
        server = start_metrics_server(port=0)
        assert server is not None
        try:
            status, _ = _fetch(server, "/unknown")
            assert status == 404
        finally:
            server.shutdown()
            server.server_close()

    def test_port_conflict_returns_none(self, monkeypatch):
        """端口被占用时（HTTPServer 抛 OSError）返回 None"""
        from zephyr.shared.observability import metrics_server

        def _raise_oserror(*args, **kwargs):
            raise OSError("Address already in use")

        monkeypatch.setattr(metrics_server, "HTTPServer", _raise_oserror)
        result = start_metrics_server(port=0)
        assert result is None

    def test_metrics_reflects_gauge(self):
        """/metrics 输出反映 set_gauge 设置的值"""
        server = start_metrics_server(port=0)
        assert server is not None
        try:
            get_registry().set_gauge("zephyr_tick_queue_size", 42)
            status, body = _fetch(server, "/metrics")
            assert status == 200
            text = body.decode("utf-8")
            assert "zephyr_tick_queue_size 42" in text
        finally:
            server.shutdown()
            server.server_close()

    def test_metrics_reflects_batch_inc(self):
        """inc(n=5) 批量计数在 /metrics 中正确反映"""
        server = start_metrics_server(port=0)
        assert server is not None
        try:
            get_registry().inc("zephyr_tick_written_total", n=5)
            status, body = _fetch(server, "/metrics")
            assert status == 200
            text = body.decode("utf-8")
            assert "zephyr_tick_written_total{} 5" in text
        finally:
            server.shutdown()
            server.server_close()
