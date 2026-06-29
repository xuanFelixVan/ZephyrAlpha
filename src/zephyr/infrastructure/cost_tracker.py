# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain-infra_runtime/runtime-integration/blueprint.md
# [MODULE] zephyr.infrastructure.cost_tracker
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF_cost_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
RI-15 CostTracker — 成本追踪器
===============================
职责：追踪 AI Agent 执行成本——Token消耗、API调用次数、费用预估与告警。
对标：AWS Cost Explorer + OpenAI Usage API
使用方式：
    tracker = CostTracker()  # 默认使用 DB_PATH (governance.db)
    tracker.record_usage(model="deepseek-chat", tokens_in=2500, tokens_out=1200)
    report = tracker.daily_report()
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "COST_TRACKER_SCHEMA",
    "CostReport",
    "CostTracker",
    "UsageRecord",
]

_MODEL_PRICING: dict[str, dict[str, float]] = {
    "deepseek-chat": {"prompt_per_1k": 0.00014, "completion_per_1k": 0.00028},
    "deepseek-reasoner": {"prompt_per_1k": 0.00055, "completion_per_1k": 0.00219},
    "claude-sonnet-4-20250514": {"prompt_per_1k": 0.003, "completion_per_1k": 0.015},
    "claude-opus-4-20250514": {"prompt_per_1k": 0.015, "completion_per_1k": 0.075},
    "glm-4": {"prompt_per_1k": 0.0005, "completion_per_1k": 0.0005},
}

COST_TRACKER_SCHEMA = """
CREATE TABLE IF NOT EXISTS usage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    model TEXT NOT NULL DEFAULT '',
    component TEXT NOT NULL DEFAULT '',
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    tokens_total INTEGER NOT NULL DEFAULT 0,
    estimated_cost TEXT NOT NULL DEFAULT '0.0',
    metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_usage_date ON usage_records(date DESC);
CREATE INDEX IF NOT EXISTS idx_usage_model ON usage_records(model);
CREATE INDEX IF NOT EXISTS idx_usage_record_id ON usage_records(record_id);
"""


@dataclass
class UsageRecord:
    record_id: str
    model: str = "unknown"
    component: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def tokens_total(self) -> int:
        return self.tokens_in + self.tokens_out

    @property
    def estimated_cost(self) -> float:
        pricing = _MODEL_PRICING.get(self.model)
        if not pricing:
            pricing = {"prompt_per_1k": 0.001, "completion_per_1k": 0.002}
        cost = (self.tokens_in / 1000) * pricing["prompt_per_1k"] + (self.tokens_out / 1000) * pricing[
            "completion_per_1k"
        ]
        return round(cost, 8)


@dataclass
class CostReport:
    report_date: str
    total_tokens: int = 0
    total_cost: float = 0.0
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_component: dict[str, dict[str, Any]] = field(default_factory=dict)
    record_count: int = 0


class CostTracker:
    """成本追踪器——Token/API调用成本实时监控

    特性：
    - 多模型定价支持
    - 按组件/日期聚合
    - 成本超限告警
    """

    def __init__(
        self,
        db_path: str | Path = DB_PATH,
        daily_budget_usd: float = 10.0,
        auto_init: bool = True,
    ):
        self._db_path = Path(db_path)
        self._daily_budget = daily_budget_usd
        self._lock = threading.Lock()

        if auto_init:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                conn.executescript(COST_TRACKER_SCHEMA)
                conn.commit()
            finally:
                conn.close()

    def record_usage(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        component: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> UsageRecord:
        record = UsageRecord(
            record_id=f"UR-{uuid.uuid4().hex[:16]}",
            model=model,
            component=component,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            metadata=metadata or {},
        )
        now = datetime.now(UTC)
        today = now.strftime("%Y-%m-%d")

        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute(
                    "INSERT INTO usage_records (record_id,timestamp,date,model,component,tokens_in,tokens_out,tokens_total,estimated_cost,metadata) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        record.record_id,
                        record.timestamp,
                        today,
                        record.model,
                        record.component,
                        record.tokens_in,
                        record.tokens_out,
                        record.tokens_total,
                        str(record.estimated_cost),
                        json.dumps(record.metadata, ensure_ascii=False),
                    ),
                )
                conn.commit()
            finally:
                conn.close()

        return record

    def daily_report(self, report_date: str | None = None) -> CostReport:
        date_str = report_date or datetime.now(UTC).strftime("%Y-%m-%d")
        report = CostReport(report_date=date_str)

        with self._lock:
            conn = self._get_conn()
            try:
                rows = conn.execute("SELECT * FROM usage_records WHERE date = ?", (date_str,)).fetchall()

                report.record_count = len(rows)
                for row in rows:
                    r = dict(row)
                    report.total_tokens += int(r.get("tokens_total", 0))
                    report.total_cost += float(r.get("estimated_cost", 0))

                    model = r.get("model", "unknown")
                    if model not in report.by_model:
                        report.by_model[model] = {"tokens": 0, "cost": 0.0, "calls": 0}
                    report.by_model[model]["tokens"] += int(r.get("tokens_total", 0))
                    report.by_model[model]["cost"] += float(r.get("estimated_cost", 0))
                    report.by_model[model]["calls"] += 1

                    comp = r.get("component", "unknown")
                    if comp not in report.by_component:
                        report.by_component[comp] = {"tokens": 0, "cost": 0.0, "calls": 0}
                    report.by_component[comp]["tokens"] += int(r.get("tokens_total", 0))
                    report.by_component[comp]["cost"] += float(r.get("estimated_cost", 0))
                    report.by_component[comp]["calls"] += 1

                report.total_cost = round(report.total_cost, 6)
            finally:
                conn.close()

        return report

    def check_budget(self) -> dict[str, Any]:
        report = self.daily_report()
        remaining = round(self._daily_budget - report.total_cost, 6)
        pct_used = round(report.total_cost / self._daily_budget * 100, 1) if self._daily_budget > 0 else 0

        alerts: list[str] = []
        if pct_used > 90:
            alerts.append(f"COST_ALERT: 已使用日预算 {pct_used}% (${report.total_cost}/${self._daily_budget})")
        if remaining < 0:
            alerts.append(f"COST_OVER: 超出日预算 ${abs(remaining)}!")

        return {
            "daily_budget": self._daily_budget,
            "spent": report.total_cost,
            "remaining": remaining,
            "pct_used": pct_used,
            "alerts": alerts,
            "date": report.report_date,
        }

    def close(self) -> None:
        pass
