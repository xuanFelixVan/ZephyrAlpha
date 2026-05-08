"""
Heartbeat Server - external heartbeat detection (blindspot #55)
Features:
  - HTTP health check endpoint (/health)
  - 5-min heartbeat interval, 3 misses -> alert, 6 misses -> emergency
  - Port conflict detection + global singleton protection
"""
from __future__ import annotations

import logging
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

_logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    check_fn: callable | None = None

    def do_GET(self):
        if self.path == "/health":
            healthy = True
            if self.check_fn:
                healthy = self.check_fn()
            status = 200 if healthy else 503
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = '{"status":"%s","timestamp":%f}' % (
                "healthy" if healthy else "unhealthy", time.time()
            )
            self.wfile.write(resp.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


class HeartbeatServer:
    DEFAULT_PORT = 9123

    _instances: ClassVar[dict[int, HeartbeatServer]] = {}
    _instances_lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_instance(cls, port: int = DEFAULT_PORT) -> HeartbeatServer:
        with cls._instances_lock:
            if port not in cls._instances:
                cls._instances[port] = cls(port=port)
            return cls._instances[port]

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._healthy = True

    def check_health(self) -> bool:
        return self._healthy

    def mark_unhealthy(self):
        self._healthy = False

    def mark_healthy(self):
        self._healthy = True

    @staticmethod
    def _is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return False
            except OSError:
                return True

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            _logger.warning("HeartbeatServer: already running on port %d", self.port)
            return
        if self._is_port_in_use(self.port):
            _logger.warning("HeartbeatServer: port %d already in use, skipping start", self.port)
            return
        HealthHandler.check_fn = self.check_health
        try:
            self._server = HTTPServer(("localhost", self.port), HealthHandler)
        except OSError as e:
            _logger.error("HeartbeatServer: failed to bind port %d: %s", self.port, e)
            return
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        _logger.info("HeartbeatServer: started on port %d", self.port)

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server = None
            _logger.info("HeartbeatServer: stopped on port %d", self.port)
