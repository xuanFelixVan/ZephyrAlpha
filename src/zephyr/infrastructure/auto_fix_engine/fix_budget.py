# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §5
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_budget
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;llm_fix_adapter.py;batch_fixer.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FixBudget daily≤50;monthly≤500;LLM tokens≤500000;FixStormGuard MUST检测风暴
# [MODIFY-GUARD] blueprint.md §5;auto_fix_config.yaml budget段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FixBudgetExceededError;FixStormDetectedError
# [TESTS] tests/auto-fix-engine/test_fix_budget.py
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: fix_budget.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: db_path 参数
#   fields: 参数 db_path（无注解）
#   code: fix_budget.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FixBudget
#   name_en: FixBudget
#   intro: class FixBudget 源码 L97-L254
#   desc: 公共方法（定义序）: daily_limit, monthly_limit, llm_token_limit, check, consume, get_info；源码 L97-L254
#   inputs: config db_path
#   outputs: 返回值
# - id: A2
#   name_zh: ② DriftBudgetLink
#   name_en: DriftBudgetLink
#   intro: class DriftBudgetLink 源码 L257-L293
#   desc: 公共方法（定义序）: drift_fix_limit, drift_fix_count, evaluate_drift_budget, record_drift_fix；源码 L257-L293
#   inputs: fix_budget
#   outputs: 返回值
# - id: A3
#   name_zh: ③ FixStormGuard
#   name_en: FixStormGuard
#   intro: class FixStormGuard 源码 L296-L350
#   desc: 公共方法（定义序）: short_window, short_threshold, long_window, long_threshold, record, check, is_active；源码 L296-L350
#   inputs: config
#   outputs: 返回值
# - id: A4
#   name_zh: ④ LLMCostEstimator
#   name_en: LLMCostEstimator
#   intro: class LLMCostEstimator 源码 L353-L381
#   desc: 公共方法（定义序）: cost_per_1k_input, cost_per_1k_output, estimate, estimate_for_fix；源码 L353-L381
#   inputs: cost_per_1k_input cost_per_1k_output
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: FixBudget, DriftBudgetLink, FixStormGuard, LLMCostEstimator
#   downstream: engine.py;llm_fix_adapter.py;batch_fixer.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
import os
import sqlite3
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import BudgetDecision, BudgetInfo, FixLevel
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.sqlite_factory import get_db_connection

logger = logging.getLogger(__name__)

_DB_PATH = DB_PATH


class FixBudget:
    def __init__(self, config: dict[str, Any] | None = None, db_path: str | None = None) -> None:
        config = config or {}
        self._daily_limit: int = config.get("daily_limit", 50)
        self._monthly_limit: int = config.get("monthly_limit", 500)
        self._llm_token_limit: int = config.get("llm_token_limit", 500000)
        self._l1_cost: int = config.get("l1_cost_per_fix", 1)
        self._l2_cost: int = config.get("l2_cost_per_fix", 5)
        self._l3_cost: int = config.get("l3_cost_per_fix", 10)
        # db_path resolution: explicit param > config['db_path'] (test isolation seam) > DB_PATH SSoT
        self._db_path = db_path or config.get("db_path") or str(_DB_PATH)
        self._lock = threading.Lock()
        self._daily_consumed: int = 0
        self._monthly_consumed: int = 0
        self._llm_tokens_consumed: int = 0
        self._last_daily_reset: str = datetime.now(UTC).strftime("%Y-%m-%d")
        self._last_monthly_reset: str = datetime.now(UTC).strftime("%Y-%m")
        self._ensure_db()
        self._load_from_db()

    # Stage 4 公共化：limit 属性公共只读（primary），私有属性向后兼容。
    @property
    def daily_limit(self) -> int:
        return self._daily_limit

    @property
    def monthly_limit(self) -> int:
        return self._monthly_limit

    @property
    def llm_token_limit(self) -> int:
        return self._llm_token_limit

    def _ensure_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        conn = get_db_connection(self._db_path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS fix_budget_consumption "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, operation_id TEXT, level TEXT, "
                "cost INTEGER DEFAULT 1, tokens INTEGER DEFAULT 0, timestamp TEXT, session_id TEXT)"
            )
            conn.commit()
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            conn.close()

    def _load_from_db(self) -> None:
        conn = None
        try:
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            this_month = datetime.now(UTC).strftime("%Y-%m")
            conn = get_db_connection(self._db_path)
            row = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM fix_budget_consumption WHERE timestamp LIKE ?",
                (today + "%",),
            ).fetchone()
            self._daily_consumed = row[0] if row else 0
            row = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM fix_budget_consumption WHERE timestamp LIKE ?",
                (this_month + "%",),
            ).fetchone()
            self._monthly_consumed = row[0] if row else 0
            row = conn.execute(
                "SELECT COALESCE(SUM(tokens), 0) FROM fix_budget_consumption WHERE timestamp LIKE ?",
                (this_month + "%",),
            ).fetchone()
            self._llm_tokens_consumed = row[0] if row else 0
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in fix_budget", exc_info=True)
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()

    def _check_reset(self) -> None:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        this_month = datetime.now(UTC).strftime("%Y-%m")
        if today != self._last_daily_reset:
            self._daily_consumed = 0
            self._last_daily_reset = today
        if this_month != self._last_monthly_reset:
            self._monthly_consumed = 0
            self._llm_tokens_consumed = 0
            self._last_monthly_reset = this_month

    def check(self, level: FixLevel = FixLevel.L1_RULE, tokens: int = 0) -> BudgetDecision:
        with self._lock:
            self._check_reset()
            cost = self._cost_for_level(level)
            daily_remaining = self._daily_limit - self._daily_consumed
            monthly_remaining = self._monthly_limit - self._monthly_consumed
            if daily_remaining < cost:
                return BudgetDecision(
                    allowed=False,
                    reason=f"Daily budget exhausted: {daily_remaining} remaining, need {cost}",
                    remaining_daily=daily_remaining,
                    remaining_monthly=monthly_remaining,
                )
            if monthly_remaining < cost:
                return BudgetDecision(
                    allowed=False,
                    reason=f"Monthly budget exhausted: {monthly_remaining} remaining, need {cost}",
                    remaining_daily=daily_remaining,
                    remaining_monthly=monthly_remaining,
                )
            if tokens > 0 and level in (FixLevel.L2_LLM, FixLevel.L3_AGENT):
                llm_remaining = self._llm_token_limit - self._llm_tokens_consumed
                if llm_remaining < tokens:
                    return BudgetDecision(
                        allowed=False,
                        reason=f"LLM token budget exhausted: {llm_remaining} remaining, need {tokens}",
                        remaining_daily=daily_remaining,
                        remaining_monthly=monthly_remaining,
                    )
            return BudgetDecision(
                allowed=True,
                reason="Budget check passed",
                remaining_daily=daily_remaining,
                remaining_monthly=monthly_remaining,
            )

    def consume(self, level: FixLevel = FixLevel.L1_RULE, tokens: int = 0, operation_id: str = "") -> None:
        with self._lock:
            self._check_reset()
            cost = self._cost_for_level(level)
            self._daily_consumed += cost
            self._monthly_consumed += cost
            if tokens > 0 and level in (FixLevel.L2_LLM, FixLevel.L3_AGENT):
                self._llm_tokens_consumed += tokens
            conn = None
            try:
                conn = get_db_connection(self._db_path)
                conn.execute(
                    "INSERT INTO fix_budget_consumption (operation_id, level, cost, tokens, timestamp, session_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (operation_id, level.value, cost, tokens, datetime.now(UTC).isoformat(), ""),
                )
                conn.commit()
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("Failed to persist budget consumption: %s", exc, exc_info=True)
            # 5.49.2 修复：异常路径确保连接归还
            finally:
                if conn is not None:
                    conn.close()

    def get_info(self) -> BudgetInfo:
        with self._lock:
            self._check_reset()
            return BudgetInfo(
                daily_remaining=max(0, self._daily_limit - self._daily_consumed),
                monthly_remaining=max(0, self._monthly_limit - self._monthly_consumed),
                llm_tokens_remaining=max(0, self._llm_token_limit - self._llm_tokens_consumed),
            )

    def _cost_for_level(self, level: FixLevel) -> int:
        return {FixLevel.L1_RULE: self._l1_cost, FixLevel.L2_LLM: self._l2_cost, FixLevel.L3_AGENT: self._l3_cost}.get(
            level, self._l1_cost
        )


class DriftBudgetLink:
    def __init__(self, fix_budget: FixBudget) -> None:
        self._fix_budget = fix_budget
        self._drift_fix_count: int = 0
        self._drift_fix_limit: int = 20

    # Stage 4 公共化：drift 预算属性公共读写（primary），私有属性向后兼容。
    @property
    def drift_fix_limit(self) -> int:
        return self._drift_fix_limit

    @drift_fix_limit.setter
    def drift_fix_limit(self, value: int) -> None:
        self._drift_fix_limit = value

    @property
    def drift_fix_count(self) -> int:
        return self._drift_fix_count

    def evaluate_drift_budget(self) -> BudgetDecision:
        if self._drift_fix_count >= self._drift_fix_limit:
            return BudgetDecision(
                allowed=False, reason=f"Drift fix budget exhausted: {self._drift_fix_count}/{self._drift_fix_limit}"
            )
        base = self._fix_budget.check(FixLevel.L1_RULE)
        if not base.allowed:
            return base
        return BudgetDecision(
            allowed=True,
            reason="Drift budget OK",
            remaining_daily=base.remaining_daily,
            remaining_monthly=base.remaining_monthly,
        )

    def record_drift_fix(self) -> None:
        self._drift_fix_count += 1
        self._fix_budget.consume(FixLevel.L1_RULE, operation_id=f"drift_fix_{self._drift_fix_count}")


class FixStormGuard:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        cfg = config or {}
        self._short_window: int = cfg.get("short_window_sec", 60)
        self._short_threshold: int = cfg.get("short_threshold", 30)
        self._long_window: int = cfg.get("long_window_sec", 300)
        self._long_threshold: int = cfg.get("long_threshold", 100)
        self._cooldown: int = cfg.get("cooldown_sec", 900)
        self._events: list[float] = []
        self._frozen_until: float = 0.0
        self._lock = threading.Lock()

    # Stage 4 公共化：窗口/阈值属性公共只读（primary），私有属性向后兼容。
    @property
    def short_window(self) -> int:
        return self._short_window

    @property
    def short_threshold(self) -> int:
        return self._short_threshold

    @property
    def long_window(self) -> int:
        return self._long_window

    @property
    def long_threshold(self) -> int:
        return self._long_threshold

    def record(self) -> None:
        with self._lock:
            self._events.append(time.time())

    def check(self) -> tuple[bool, str]:
        with self._lock:
            now = time.time()
            if now < self._frozen_until:
                return (
                    False,
                    f"Fix storm guard active until {datetime.fromtimestamp(self._frozen_until, tz=UTC).isoformat()}",
                )
            self._events = [t for t in self._events if now - t < self._long_window]
            short_count = len([t for t in self._events if now - t < self._short_window])
            if short_count >= self._short_threshold:
                self._frozen_until = now + self._cooldown
                return False, f"Short-window storm detected: {short_count} fixes in {self._short_window}s"
            if len(self._events) >= self._long_threshold:
                self._frozen_until = now + self._cooldown
                return False, f"Long-window storm detected: {len(self._events)} fixes in {self._long_window}s"
            return True, ""

    @property
    def is_active(self) -> bool:
        with self._lock:
            return time.time() < self._frozen_until


class LLMCostEstimator:
    def __init__(self, cost_per_1k_input: float = 0.001, cost_per_1k_output: float = 0.002) -> None:
        self._cost_per_1k_input = cost_per_1k_input
        self._cost_per_1k_output = cost_per_1k_output

    # Stage 4 公共化：成本属性公共只读（primary），私有属性向后兼容。
    @property
    def cost_per_1k_input(self) -> float:
        return self._cost_per_1k_input

    @property
    def cost_per_1k_output(self) -> float:
        return self._cost_per_1k_output

    def estimate(self, input_tokens: int, output_tokens: int = 0) -> dict[str, float]:
        input_cost = (input_tokens / 1000) * self._cost_per_1k_input
        output_cost = (output_tokens / 1000) * self._cost_per_1k_output
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": input_cost + output_cost,
        }

    def estimate_for_fix(self, target_lines: int, complexity: str = "medium") -> dict[str, int]:
        multipliers = {"simple": 1.0, "medium": 2.0, "complex": 4.0}
        m = multipliers.get(complexity, 2.0)
        input_tokens = int(target_lines * 15 * m)
        output_tokens = int(target_lines * 5 * m)
        return {"input_tokens": input_tokens, "output_tokens": output_tokens}
