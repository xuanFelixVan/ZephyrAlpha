# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.rate_limiter
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.infra.limiter
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
# [A_module] module_id=MOD-INF-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: acquire()的while True+time.sleep是TokenBucket阻塞等待token可用,非周期触发(类似锁等待循环)

"""MCP Gateway 同步速率限制器（MOD-INF-013 §12 Step 3）。

设计基线：
- 继承 shared/infra/limiter.py 的 SyncTokenBucketLimiter（canonical SSoT）
- Token Bucket 算法 + 线程安全（threading.Lock）
- 按 tool_name 粒度独立 bucket（对标 R98）
- 可配置：10 req/s default, 30 burst（从 config/mcp.json 加载）

盲点关闭：B10（缺限流 -> 无 DoS 防护）。
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from zephyr.shared.infra.limiter import SyncTokenBucketLimiter

__all__ = [
    "DEFAULT_BURST",
    "DEFAULT_MAX_WAIT",
    "DEFAULT_QPS",
    "RATE_LIMITED_KEY",
    "RateLimiter",
    "RateLimiterStats",
]

RATE_LIMITED_KEY: Final[str] = "RATE_LIMITED"
DEFAULT_QPS: Final[float] = 10.0
DEFAULT_BURST: Final[float] = 30.0
DEFAULT_MAX_WAIT: Final[float] = 30.0


@dataclass
class RateLimiterStats:
    permits_per_second: float
    available_tokens: float
    total_acquired: int = 0
    total_rejected: int = 0
    total_waited: int = 0


class RateLimiter(SyncTokenBucketLimiter):
    """MCP Gateway 同步速率限制器（继承 SyncTokenBucketLimiter）。

    Usage::

        rl = RateLimiter(permits_per_second=10.0, burst_size=30.0)
        if not rl.try_acquire():
            raise RateLimitExceeded("rate limited")
    """

    def __init__(
        self,
        permits_per_second: float = DEFAULT_QPS,
        *,
        burst_size: float | None = None,
        max_wait_seconds: float = DEFAULT_MAX_WAIT,
    ) -> None:
        super().__init__(
            permits_per_second,
            burst_size=burst_size,
            max_wait_seconds=max_wait_seconds,
        )


class RateLimitExceeded(Exception):
    """速率限制超出。"""


def _load_mcp_rate_limits() -> dict[str, tuple[float, float]]:
    """从 config/mcp.json 加载 per-server rate_limit 配置。

    返回 {tool_prefix: (qps, burst)} 映射，如 {"blueprint_search.": (30.0, 60.0)}。
    加载失败返回空 dict（fail-open，使用默认值）。
    """
    try:
        # file: src/zephyr/integration/mcp/rate_limiter.py
        # parents[4] = project root (D:\ZephyrAlpha)
        config_path = Path(__file__).resolve().parents[4] / "config" / "mcp.json"
        if not config_path.exists():
            return {}
        with config_path.open(encoding="utf-8") as f:
            cfg = json.load(f)
        result: dict[str, tuple[float, float]] = {}
        servers = cfg.get("mcpServers", cfg.get("servers", {}))
        for _server_id, server_cfg in servers.items():
            rl = server_cfg.get("rate_limit")
            if not rl:
                continue
            qps = float(rl.get("default_qps", DEFAULT_QPS))
            burst = float(rl.get("burst", DEFAULT_BURST))
            tool_prefix = server_cfg.get("tool_prefix", f"{server_cfg.get('server_id', '')}.")
            if tool_prefix:
                result[tool_prefix] = (qps, burst)
        return result
    except Exception:  # noqa: BLE001 — fail-open
        return {}


def _resolve_tool_rate(
    tool_name: str,
    per_server: dict[str, tuple[float, float]],
    default_qps: float,
    default_burst: float,
) -> tuple[float, float]:
    """根据 tool_name 前缀匹配 per-server 配置，返回 (qps, burst)。"""
    for prefix, (qps, burst) in per_server.items():
        if tool_name.startswith(prefix):
            return qps, burst
    return default_qps, default_burst


class PerToolRateLimiter:
    """按 tool_name 粒度管理多个 TokenBucket。

    5.36.2: 支持 (client_id, tool_name) 复合键分桶，跨客户端隔离。
    5.36.6: 默认配额与 per-server 覆盖从 mcp.json 加载。
    5.36.7: 限流拒绝响应携带 retry_after_seconds（受 config.rate_limit.retry_after_header 控制）。

    默认 10QPS per tool；可在 config/mcp.json 覆盖。
    """

    def __init__(
        self,
        default_qps: float | None = None,
        default_burst: float | None = None,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        explicit = default_qps is not None
        if default_qps is None:
            default_qps = DEFAULT_QPS
        if default_burst is None:
            default_burst = DEFAULT_BURST
        self._default_qps = float(default_qps)
        self._default_burst = float(default_burst)
        self._buckets: dict[str, RateLimiter] = {}
        self._lock = threading.Lock()
        self._config = config or {}
        # 仅在无显式参数时从 mcp.json 加载 per-server 配置
        self._per_server: dict[str, tuple[float, float]] = {} if explicit else _load_mcp_rate_limits()

    @property
    def default_qps(self):
        """只读：default_qps（Stage 4 公共化）。"""
        return self._default_qps

    @default_qps.setter
    def default_qps(self, value):
        """写入：default_qps（Stage 4 公共化）。"""
        self._default_qps = value

    @property
    def default_burst(self):
        """只读：default_burst（Stage 4 公共化）。"""
        return self._default_burst

    @default_burst.setter
    def default_burst(self, value):
        """写入：default_burst（Stage 4 公共化）。"""
        self._default_burst = value

    def _make_key(self, tool_name: str, client_id: str | None = None) -> str:
        if client_id is None:
            return tool_name
        return f"{client_id}|{tool_name}"

    def get_or_create(
        self,
        tool_name: str,
        qps: float | None = None,
        burst: float | None = None,
        client_id: str | None = None,
    ) -> RateLimiter:
        key = self._make_key(tool_name, client_id)
        with self._lock:
            if key not in self._buckets:
                if qps is None or burst is None:
                    resolved_qps, resolved_burst = _resolve_tool_rate(
                        tool_name, self._per_server, self._default_qps, self._default_burst
                    )
                    qps = qps if qps is not None else resolved_qps
                    burst = burst if burst is not None else resolved_burst
                self._buckets[key] = RateLimiter(
                    qps,
                    burst_size=burst,
                )
            return self._buckets[key]

    def try_acquire(self, tool_name: str, client_id: str | None = None) -> bool:
        return self.get_or_create(tool_name, client_id=client_id).try_acquire()

    def retry_after(self, tool_name: str, client_id: str | None = None) -> float:
        """返回 tool 的 retry_after 秒数。受 config.rate_limit.retry_after_header 控制。"""
        rl_cfg = self._config.get("rate_limit", {}) if self._config else {}
        if not rl_cfg.get("retry_after_header", False):
            return 0.0
        key = self._make_key(tool_name, client_id)
        with self._lock:
            bucket = self._buckets.get(key)
        if bucket is None:
            return 0.0
        return bucket.retry_after_seconds()

    def stats(self) -> dict[str, RateLimiterStats]:
        with self._lock:
            return {k: v.stats() for k, v in self._buckets.items()}
