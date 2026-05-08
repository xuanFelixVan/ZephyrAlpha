from __future__ import annotations
from dataclasses import dataclass

NTP_SERVER: str = "pool.ntp.org"
NTP_SYNC_INTERVAL_SECONDS: int = 60
MAX_CLOCK_DRIFT_MS: int = 50
TIMESTAMP_FORMAT: str = "ISO8601"

@dataclass(frozen=True)
class TimeSource:
    level: int
    name: str
    max_jitter_ms: int

TIME_HIERARCHY: list[TimeSource] = [
    TimeSource(1, "硬件NTP pool.ntp.org", 10),
    TimeSource(2, "系统时间 w32tm/timedatectl", 50),
    TimeSource(3, "业务应用BusinessTs UTC+8 1ms", 1),
]
