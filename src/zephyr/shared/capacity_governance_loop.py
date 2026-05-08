"""
Capacity Governance Loop — 容量治理闭环引擎 (M-19)
职责：读取 capacity_metrics → EMA 评估 → 五级响应触发。

设计：
  - evaluate(): 从 DB 读取最近指标 → 计算 EMA → 判定级别
  - act(): 根据 Error Budget 级别触发 L0~L4 响应
  - 采样间隔 300s（环境变量 CAPACITY_GOVERNANCE_INTERVAL_SECONDS 可配）
"""
import os
import sqlite3
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class GovernanceLevel(IntEnum):
    L0_HEALTHY = 0
    L1_WARNING = 1
    L2_CAUTION = 2
    L3_CRITICAL = 3
    L4_EMERGENCY = 4


LEVEL_DESCRIPTIONS = {
    GovernanceLevel.L0_HEALTHY: "所有指标正常，Error Budget 充足",
    GovernanceLevel.L1_WARNING: "个别指标接近阈值，需关注",
    GovernanceLevel.L2_CAUTION: "Error Budget 快速消耗，启动限流",
    GovernanceLevel.L3_CRITICAL: "多项指标超阈值，触发自动降级",
    GovernanceLevel.L4_EMERGENCY: "系统濒临崩溃，触发 Kill Switch",
}


@dataclass
class GovernanceState:
    level: GovernanceLevel
    sli_values: dict[str, float]
    error_budget_remaining: float
    burn_rate: float
    timestamp: str
    description: str = ""


class CapacityGovernanceLoop:
    """
    容量治理闭环 (M-19)

    EMA 算法：
      alpha = 2 / (span + 1)，span 默认 5（约 25 分钟窗口）
      EMA_t = alpha * value_t + (1 - alpha) * EMA_{t-1}
    """

    DEFAULT_INTERVAL_SECONDS = 300
    DEFAULT_EMA_SPAN = 5

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self._default_db_path()
        self._interval = int(os.environ.get(
            "CAPACITY_GOVERNANCE_INTERVAL_SECONDS", str(self.DEFAULT_INTERVAL_SECONDS)
        ))
        self._ema_values: dict[str, float] = {}
        self._ema_alpha = 2.0 / (self.DEFAULT_EMA_SPAN + 1)
        self._last_eval_time: float = 0
        self._state_history: list[GovernanceState] = []

    def _default_db_path(self) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "capacity.db"
        )

    def evaluate(self) -> GovernanceState:
        now = time.time()
        if now - self._last_eval_time < self._interval:
            if self._state_history:
                return self._state_history[-1]

        self._last_eval_time = now

        sli_values = self._read_recent_metrics()

        for sli_id, value in sli_values.items():
            if sli_id in self._ema_values:
                self._ema_values[sli_id] = (
                    self._ema_alpha * value + (1 - self._ema_alpha) * self._ema_values[sli_id]
                )
            else:
                self._ema_values[sli_id] = value

        level = self._compute_level(self._ema_values)
        burn_rate = self._estimate_burn_rate()
        error_budget_remaining = self._read_error_budget_remaining()

        state = GovernanceState(
            level=level,
            sli_values=dict(self._ema_values),
            error_budget_remaining=error_budget_remaining,
            burn_rate=burn_rate,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            description=LEVEL_DESCRIPTIONS.get(level, "Unknown"),
        )
        self._state_history.append(state)
        if len(self._state_history) > 100:
            self._state_history = self._state_history[-100:]

        return state

    def _read_recent_metrics(self) -> dict[str, float]:
        try:
            conn = sqlite3.connect(self.db_path)
            cutoff = f"datetime('now', '-{self._interval * 2} seconds')"
            rows = conn.execute(
                f"SELECT sli_id, AVG(value) FROM capacity_metrics WHERE ts > {cutoff} GROUP BY sli_id"
            ).fetchall()
            conn.close()
            return {r[0]: r[1] for r in rows if r[1] is not None}
        except Exception:
            return {}

    def _read_error_budget_remaining(self) -> float:
        try:
            conn = sqlite3.connect(self.db_path)
            row = conn.execute(
                "SELECT budget_remaining FROM error_budget ORDER BY last_updated DESC LIMIT 1"
            ).fetchone()
            conn.close()
            return row[0] if row else 1.0
        except Exception:
            return 1.0

    def _estimate_burn_rate(self) -> float:
        try:
            conn = sqlite3.connect(self.db_path)
            rows = conn.execute(
                "SELECT budget_consumed FROM error_budget "
                "WHERE window_start > datetime('now', '-1 hour') ORDER BY window_start"
            ).fetchall()
            conn.close()
            if len(rows) < 2:
                return 0.0
            return (rows[-1][0] - rows[0][0]) / max(len(rows) - 1, 1)
        except Exception:
            return 0.0

    def _compute_level(self, ema_values: dict[str, float]) -> GovernanceLevel:
        if not ema_values:
            return GovernanceLevel.L0_HEALTHY

        violations = 0
        for sli_id, value in ema_values.items():
            threshold = self._get_threshold(sli_id)
            if threshold and value > threshold:
                violations += 1

        if violations == 0:
            return GovernanceLevel.L0_HEALTHY
        if violations <= 1:
            return GovernanceLevel.L1_WARNING
        if violations <= 2:
            return GovernanceLevel.L2_CAUTION
        if violations <= 3:
            return GovernanceLevel.L3_CRITICAL
        return GovernanceLevel.L4_EMERGENCY

    def _get_threshold(self, sli_id: str) -> Optional[float]:
        thresholds = {
            "CAP-003-error-rate": 0.001,
            "CAP-004-memory-saturation": 0.8,
            "CAP-005-cpu-saturation": 0.7,
            "CAP-006-queue-depth-saturation": 500,
        }
        return thresholds.get(sli_id)

    def act(self, state: GovernanceState) -> list[str]:
        actions: list[str] = []

        if state.level >= GovernanceLevel.L2_CAUTION:
            actions.append("RATE_LIMIT: 启用 Token Budget 消耗加速限制")

        if state.level >= GovernanceLevel.L3_CRITICAL:
            actions.append("DEGRADE: 触发 Graceful Degradation 降级链")
            actions.append("THROTTLE: 非关键模块延迟调度")

        if state.level >= GovernanceLevel.L4_EMERGENCY:
            actions.append("KILL_SWITCH: 建议触发全局 Kill Switch")
            actions.append("NOTIFY: 飞书告警 → Owner 即时通知")

        return actions

    def report(self, state: GovernanceState) -> str:
        lines = [
            "=" * 50,
            f"  容量治理报告 — {state.timestamp}",
            "=" * 50,
            f"  级别: {state.level.name} — {state.description}",
            f"  Error Budget 剩余: {state.error_budget_remaining:.4%}",
            f"  Burn Rate: {state.burn_rate:.6f}/s",
            f"  EMA 指标数: {len(state.sli_values)}",
        ]

        for sli_id, value in state.sli_values.items():
            lines.append(f"    {sli_id}: {value:.6f}")

        actions = self.act(state)
        if actions:
            lines.append("  触发动作:")
            for action in actions:
                lines.append(f"    → {action}")

        lines.append("=" * 50)
        return "\n".join(lines)


_loop: Optional[CapacityGovernanceLoop] = None


def get_governance_loop() -> CapacityGovernanceLoop:
    global _loop
    if _loop is None:
        _loop = CapacityGovernanceLoop()
    return _loop
