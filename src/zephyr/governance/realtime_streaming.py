from __future__ import annotations
from enum import Enum

class PipelineMode(str, Enum):
    BATCH = "Batch"
    STREAM = "Stream"

CONNECTION_POOL_MIN: int = 10
FIFO_MAX_DEPTH: int = 1000
DISCONNECT_ALERT_SECONDS: int = 120
BACKPRESSURE_THRESHOLD: int = 1000
