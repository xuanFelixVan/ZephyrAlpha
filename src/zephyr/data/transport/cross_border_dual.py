# [MODULE] zephyr.data.transport.cross_border_dual
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（骨架期零外部依赖）
# [CONSUMERS] 装配层（CAND-CRYPTO-002 行情 WS / CAND-CRYPTO-005 执行回传 注入）
# [STARTUP] imported
# [MATURITY] skeleton
# [INVARIANTS] 切备=失败+吞吐下降+积压超阈值三感知同时成立（5 秒桶）; 切回=纯时间驱动 60s 探测; 积压计数器饱和递减最低到零
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §7.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知状态→ValueError; probe 回调异常视为探测失败（保持备线路）
# [TESTS] tests/zephyr/data/transport/test_cross_border_dual.py
# [A_module] module_id=CAND-CRYPTO-009 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""跨境网络双活传输层（CAND-CRYPTO-009 / 94号 §7.2）。

境内基建↔境外交易所双线路：
- 主线路（PRIMARY）=HTTPS 直连（Caddy TLS 终结+DNS-01 证书+来源 IP 白名单）
- 备用线路（BACKUP）=Cloudflare Tunnel（Access Service Token 鉴权、cloudflared
  隧道、不暴露源站）

热切换三条纪律（外部实战血泪教训，94号 §7.2）：
1. 切备必须三感知同时成立——连接失败 + 吞吐下降 + 积压超阈值（5 秒桶），
   不能只看连接存活（"活着但跟不上"的主线路要主动绕开）；
2. 切回用纯时间驱动 60 秒探测，不依赖"积压=0"等发送中永远达不到的静态条件；
3. 积压计数器饱和递减（最低到零），防无符号下溢误判天文数字积压。

Usage::

    cfg = DualPathConfig(baseline_throughput_bps=1_000_000)
    dual = CrossBorderDualTransport(cfg, probe=probe_primary_https)
    event = dual.record_bucket(BucketStats(
        connection_failed=True, throughput_bps=100_000, backlog=30,
    ))
    # ... 60 秒后
    event = dual.maybe_probe_primary()
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Optional

log = logging.getLogger(__name__)

_DEFAULT_BUCKET_SECONDS: Final = 5.0
_DEFAULT_PROBE_INTERVAL_SECONDS: Final = 60.0
_DEFAULT_THROUGHPUT_DROP_RATIO: Final = 0.5
_DEFAULT_BACKLOG_THRESHOLD: Final = 24  # 5s 桶积压 ~24 个≈2 分钟数据量（94号 §7.2）


class TransportPath(Enum):
    """双线路路径标识。"""

    PRIMARY = "primary_https_direct"
    BACKUP = "backup_cloudflare_tunnel"


@dataclass(frozen=True)
class CloudflareTunnelSpec:
    """Cloudflare Tunnel 配置输入（cloudflared tunnel config YAML 生成参数）。

    Attributes:
        tunnel_id: cloudflared tunnel UUID。
        credentials_file: 隧道凭据 JSON 路径（cert 签发后由 cloudflared 落地）。
        hostname: 对外服务域名（CF Access Service Token 鉴权挂在此 hostname）。
        service: 隧道回源的本地服务地址（如 https://127.0.0.1:8443）。
        warp_routing: 是否启用 WARP 路由（默认关——数据面仅降级时走 CF，控成本）。
    """

    tunnel_id: str
    credentials_file: str
    hostname: str
    service: str
    warp_routing: bool = False


def render_cloudflared_config(spec: CloudflareTunnelSpec) -> str:
    """生成 cloudflared tunnel 配置 YAML 文本。

    Args:
        spec: 隧道配置输入。

    Returns:
        cloudflared config.yml 内容（UTF-8 文本）。
    """
    warp = "true" if spec.warp_routing else "false"
    return (
        f"tunnel: {spec.tunnel_id}\n"
        f"credentials-file: {spec.credentials_file}\n"
        f"warp-routing:\n"
        f"  enabled: {warp}\n"
        f"ingress:\n"
        f"  - hostname: {spec.hostname}\n"
        f"    service: {spec.service}\n"
        f"  - service: http_status:404\n"
    )


@dataclass(frozen=True)
class DualPathConfig:
    """双线路热切换配置。

    Attributes:
        baseline_throughput_bps: 主线路健康吞吐基线（字节/秒），吞吐下降判定基准。
        bucket_seconds: 统计桶宽（秒），默认 5 秒。
        throughput_drop_ratio: 吞吐下降阈值——桶吞吐 < 基线×ratio 判定为下降。
        backlog_threshold: 积压阈值（条数/字节数，按注入方口径）。
        probe_interval_seconds: 切回探测间隔（秒），纯时间驱动，默认 60。
    """

    baseline_throughput_bps: float
    bucket_seconds: float = _DEFAULT_BUCKET_SECONDS
    throughput_drop_ratio: float = _DEFAULT_THROUGHPUT_DROP_RATIO
    backlog_threshold: int = _DEFAULT_BACKLOG_THRESHOLD
    probe_interval_seconds: float = _DEFAULT_PROBE_INTERVAL_SECONDS


@dataclass(frozen=True)
class BucketStats:
    """单个 5 秒桶的线路观测。

    Attributes:
        connection_failed: 桶内是否发生连接失败。
        throughput_bps: 桶内实测吞吐（字节/秒）。
        backlog: 桶末发送积压（条数/字节数，口径与阈值一致）。
    """

    connection_failed: bool
    throughput_bps: float
    backlog: int


@dataclass(frozen=True)
class SwitchEvent:
    """切换事件记录。"""

    ts: float
    from_path: TransportPath
    to_path: TransportPath
    reason: str


class CrossBorderDualTransport:
    """双线路热切换状态机（PRIMARY ⇄ BACKUP）。

    - record_bucket(): 主线路活跃期喂入 5 秒桶观测；三感知同时成立即切备。
    - maybe_probe_primary(): 备线路活跃期纯时间驱动探测；距上次探测满
      probe_interval_seconds 且探测成功即切回，失败则顺延下一周期。
    - decr_backlog(): 饱和递减（最低到零），防无符号下溢。
    """

    def __init__(
        self,
        config: DualPathConfig,
        probe: Callable[[], bool],
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._cfg = config
        self._probe = probe
        self._clock = clock
        self._path = TransportPath.PRIMARY
        self._backlog = 0
        self._switched_at: Optional[float] = None
        self._last_probe_at: Optional[float] = None
        self._events: list[SwitchEvent] = []

    @property
    def active_path(self) -> TransportPath:
        """当前活跃线路。"""
        return self._path

    @property
    def backlog(self) -> int:
        """当前发送积压计数。"""
        return self._backlog

    @property
    def events(self) -> tuple[SwitchEvent, ...]:
        """历史切换事件。"""
        return tuple(self._events)

    def add_backlog(self, n: int) -> None:
        """积压计数 +n。"""
        if n > 0:
            self._backlog += n

    def decr_backlog(self, n: int) -> int:
        """积压计数饱和递减（纪律③：最低到零，防无符号下溢）。

        Args:
            n: 递减量（负数按 0 处理）。

        Returns:
            递减后的积压值。
        """
        if n > 0:
            self._backlog = max(0, self._backlog - n)
        return self._backlog

    def record_bucket(self, stats: BucketStats) -> Optional[SwitchEvent]:
        """喂入一个 5 秒桶观测；主线路期三感知同时成立即切备。

        Args:
            stats: 桶观测。

        Returns:
            发生切换时返回 SwitchEvent，否则 None。
        """
        self._backlog = max(0, stats.backlog)
        if self._path is not TransportPath.PRIMARY:
            return None
        throughput_dropped = (
            stats.throughput_bps < self._cfg.baseline_throughput_bps * self._cfg.throughput_drop_ratio
        )
        if not (stats.connection_failed and throughput_dropped and stats.backlog > self._cfg.backlog_threshold):
            return None
        reason = (
            f"三感知命中: connection_failed={stats.connection_failed} "
            f"throughput_bps={stats.throughput_bps:.0f}<{self._cfg.baseline_throughput_bps * self._cfg.throughput_drop_ratio:.0f} "
            f"backlog={stats.backlog}>{self._cfg.backlog_threshold}"
        )
        return self._switch(TransportPath.BACKUP, reason)

    def maybe_probe_primary(self) -> Optional[SwitchEvent]:
        """备线路期纯时间驱动探测切回（纪律②：不依赖积压=0 等静态条件）。

        距切备/上次探测满 probe_interval_seconds 才发起探测；探测成功切回
        主线路，失败保持备线路并顺延下一探测周期。

        Returns:
            切回成功时返回 SwitchEvent，否则 None。
        """
        if self._path is not TransportPath.BACKUP:
            return None
        now = self._clock()
        anchor = self._last_probe_at if self._last_probe_at is not None else self._switched_at
        if anchor is not None and now - anchor < self._cfg.probe_interval_seconds:
            return None
        self._last_probe_at = now
        try:
            ok = bool(self._probe())
        except Exception:  # noqa: BLE001 探测回调异常=探测失败，保持备线路
            log.warning("cross_border_dual probe raised, stay on backup", exc_info=True)
            ok = False
        if not ok:
            log.info("cross_border_dual probe failed, stay on backup (next probe in %.0fs)", self._cfg.probe_interval_seconds)
            return None
        return self._switch(TransportPath.PRIMARY, f"时间驱动探测成功（{self._cfg.probe_interval_seconds:.0f}s 周期）")

    def _switch(self, to_path: TransportPath, reason: str) -> SwitchEvent:
        event = SwitchEvent(ts=self._clock(), from_path=self._path, to_path=to_path, reason=reason)
        log.warning("cross_border_dual switch %s -> %s: %s", self._path.value, to_path.value, reason)
        self._path = to_path
        if to_path is TransportPath.BACKUP:
            self._switched_at = event.ts
            self._last_probe_at = None
        else:
            self._switched_at = None
            self._last_probe_at = None
        self._events.append(event)
        return event
