# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.observability.metrics_server
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.observability.metrics; http.server(标准库)
# [CONSUMERS] zephyr.data.tick_subscriber
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] /metrics端点输出Prometheus文本; 端口默认9925; 独立daemon线程; 不阻塞主流程; 静默访问日志
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 端口冲突->log warning+返回None; 正常请求->200+Prometheus文本; 未知路径->404
# [TESTS] tests/zephyr/shared/observability/test_metrics_server.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Prometheus /metrics HTTP 端点（P1-5 可观测性改造）。

启动 daemon 线程提供 /metrics 和 /health 端点，
输出 MetricsRegistry 的 Prometheus 兼容文本。

用法::

    from zephyr.shared.observability.metrics_server import start_metrics_server
    start_metrics_server(port=9925)

验证::

    curl http://localhost:9925/metrics
    curl http://localhost:9925/health
"""
from __future__ import annotations

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from zephyr.shared.observability.metrics import get_registry

log = logging.getLogger(__name__)

_METRICS_PORT = 9925


class _MetricsHandler(BaseHTTPRequestHandler):
    """Prometheus /metrics 端点请求处理器。"""

    def do_GET(self) -> None:
        if self.path == "/metrics":
            text = get_registry().prometheus_text()
            body = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args) -> None:
        pass  # 静默访问日志


def start_metrics_server(port: int = _METRICS_PORT) -> HTTPServer | None:
    """启动 /metrics HTTP 服务（daemon 线程）。

    Args:
        port: 监听端口（默认 9925）

    Returns:
        HTTPServer 实例（端口冲突时返回 None）
    """
    try:
        server = HTTPServer(("0.0.0.0", port), _MetricsHandler)
        thread = Thread(target=server.serve_forever, daemon=True, name="metrics-server")
        thread.start()
        log.info("metrics_server 已启动: port=%d (/metrics, /health)", port)
        return server
    except OSError as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.warning("metrics_server 启动失败 (port=%d): %s", port, e)
        return None
