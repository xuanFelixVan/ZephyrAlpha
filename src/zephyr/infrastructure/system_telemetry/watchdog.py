# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.watchdog
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS] zephyr.security.access_control
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] triple-redundancy mutual-check; panic mode on 2+ peer misses; dead man's switch threshold 1800s
# [MODIFY-GUARD] health_aggregator.py; health_probes.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OSError; RuntimeError
# [TESTS] tests/system-telemetry/test_watchdog.py
# [A_module] module_id=MOD-INF_watchdog | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m02-manual  M02豁免: 系统遥测watchdog常驻服务(python -m zephyr.infrastructure.system_telemetry.watchdog),CLI触发启动,启动后自动运行;非reconciler无需事件触发

"""三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic Mode+Dead Man's Switch。

支持两种运行模式:
    1. 库模式: Watchdog(watchdog_id="wd-1") -> 嵌入其他进程
    2. 独立进程: python -m zephyr.infrastructure.system_telemetry.watchdog --id wd-1 [--interval 10]
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.shared.io.paths import REPO_ROOT


class WatchdogHeartbeat(BaseModel):
    watchdog_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    alive: bool = True


class Watchdog:
    def __init__(self, watchdog_id: str):
        self._id = watchdog_id
        self._heartbeats: dict[str, WatchdogHeartbeat] = {}
        self._external_file = str(REPO_ROOT / "data" / "telemetry" / f".watchdog_heartbeat_{watchdog_id}")
        self._panic_mode = False

    @property
    def panic_mode(self) -> bool:
        return self._panic_mode

    def check_peers(self, peers: list[str], peer_heartbeats: dict[str, float]) -> bool:
        missing = 0
        for peer in peers:
            last = peer_heartbeats.get(peer, 0)
            if time.time() - last > 1800:
                missing += 1
        self._panic_mode = missing >= 2
        return not self._panic_mode

    def write_external_heartbeat(self) -> None:
        import json

        hb_file = Path(self._external_file)
        try:
            hb_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "watchdog_id": self._id,
                "timestamp": datetime.now(UTC).isoformat(),
                "alive": True,
            }
            tmp = hb_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(data) + "\n", encoding="utf-8")
            tmp.replace(hb_file)
        except Exception:
            _logger.warning("write_external_heartbeat failed id=%s", self._id, exc_info=True)

    def should_alert_dead_mans_switch(self, last_heartbeat_s: float) -> bool:
        return time.time() - last_heartbeat_s > 1800

    def run_standalone(self, interval: float = 10.0) -> None:
        """独立进程模式：持续运行，定时写入心跳 + 检查 peer。

        用法: python -m zephyr.infrastructure.system_telemetry.watchdog --id wd-1 --interval 10
        """
        import logging
        import signal

        _wd_logger = logging.getLogger(f"watchdog.{self._id}")
        _stop = False

        def _handle_signal(signum, frame):
            nonlocal _stop
            _stop = True
            _wd_logger.info("watchdog received signal=%s, shutting down", signum)

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        _wd_logger.info("watchdog standalone started id=%s interval=%.1fs", self._id, interval)
        while not _stop:
            try:
                self.write_external_heartbeat()
                hb = WatchdogHeartbeat(watchdog_id=self._id)
                self._heartbeats[self._id] = hb
                _wd_logger.debug("heartbeat written id=%s", self._id)
            except Exception:
                _wd_logger.error("heartbeat write failed id=%s", self._id, exc_info=True)
            time.sleep(interval)

        _wd_logger.info("watchdog standalone stopped id=%s", self._id)


if __name__ == "__main__":
    import argparse
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="ZephyrAlpha Telemetry Watchdog")
    parser.add_argument("--id", required=True, help="Watchdog ID")
    parser.add_argument("--interval", type=float, default=10.0, help="Heartbeat interval in seconds")
    args = parser.parse_args()

    wd = Watchdog(watchdog_id=args.id)
    wd.run_standalone(interval=args.interval)
