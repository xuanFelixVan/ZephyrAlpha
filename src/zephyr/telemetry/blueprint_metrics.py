"""
blueprint_metrics — 蓝图使用追踪 instrumentation
==================================================
Task ID  : T-V2-011（Phase 1e — 量化追踪 P2-1）
关联蓝图 : MOD-INF-015 §4（metrics 子系统, SLI 新增）
关联决策 : R92（量化追踪 + 强制合规 + Retrospective 三件套）

职责
----
提供轻量级 instrumentation hook，记录每次蓝图被 AI 读取的事件：
- ``record_blueprint_read(blueprint_id, session_id, task_id)``
- 输出到 JSONL 日志（供 Telemetry 和 FLE 事后消费）

设计约束
--------
- 零外部依赖——只依赖标准库 json + datetime
- fail-closed——写入失败静默跳过，不阻塞主流程
- 每行一个 JSON 事件，可被 Telemetry logs 子系统聚合

对标
----
Codified Context (arXiv 2602.20478) §5.2 Maintenance Cost:
  "codified context infrastructure itself has maintenance cost—
   tracking usage patterns enables informed refactoring decisions"
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

__all__ = ["record_blueprint_read", "BlueprintReadEvent", "METRICS_FILE"]

_logger = logging.getLogger(__name__)
_UTC = timezone.utc

_FILE = Path(__file__).resolve()
REPO_ROOT = _FILE.parents[3]
METRICS_FILE = REPO_ROOT / "data" / "telemetry" / "blueprint_reads.jsonl"


class BlueprintReadEvent:
    """单次蓝图读取事件。"""

    def __init__(
        self,
        blueprint_id: str,
        session_id: str = "",
        task_id: str = "",
        agent_model: str = "",
    ) -> None:
        self.blueprint_id = blueprint_id
        self.session_id = session_id
        self.task_id = task_id
        self.agent_model = agent_model
        self.timestamp = datetime.now(_UTC).isoformat()


def record_blueprint_read(
    blueprint_id: str,
    session_id: str = "",
    task_id: str = "",
    agent_model: str = "",
) -> bool:
    """记录一次蓝图被 AI 读取的事件。

    写入 ``data/telemetry/blueprint_reads.jsonl``——每行一个 JSON 事件。
    写入失败时静默降级，不抛出异常（fail-closed）。

    Returns
    -------
    bool
        True 写入成功，False 静默跳过。
    """
    try:
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        _logger.warning("cannot create telemetry dir, skipping record", exc_info=True)
        return False

    event = BlueprintReadEvent(
        blueprint_id=blueprint_id,
        session_id=session_id,
        task_id=task_id,
        agent_model=agent_model,
    )

    record = {
        "event": "blueprint_read",
        "blueprint_id": event.blueprint_id,
        "session_id": event.session_id,
        "task_id": event.task_id,
        "agent_model": event.agent_model,
        "timestamp": event.timestamp,
    }

    try:
        with open(METRICS_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except OSError:
        _logger.warning("cannot write blueprint_read event, skipping", exc_info=True)
        return False
