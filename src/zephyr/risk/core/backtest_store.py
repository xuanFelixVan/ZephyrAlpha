# [BLUEPRINT] MOD-RK-20B | (36号 §3.4/§3.13/§3.18 持久化门面) | §
# [TTL] permanent
# [MODULE] zephyr.risk.core.backtest_store
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.state_store(原语注入)
# [CONSUMERS] daily_auditor(日终持久化); RiskLayerOrchestrator(盘前加载); 35号 §3.15/§3.16(entry_var 配对消费)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 命名空间纯名字(date后缀禁路径分隔符); cvar≥var(盘前基线写入守卫,§3.18阶段0); entry_var≥0; 读损坏→StateCorruptError上抛(fail-closed,不静默兜底); 历史加载缺日记None不补0(数据缺口即缺口)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidBacktestStoreError; StateCorruptError(读取损坏上抛)
# [TESTS] tests/risk/test_backtest_store.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: JsonStateStore 同接口 store(save/load 单记录原语, 双后端经 make_state_store 工厂)
# I2: trade_date + 各类载荷(回测报告/双轨P&L/盘中重算日志/盘前基线/entry_var)
# A1: save_*(写入守卫: 有限值/cvar≥var/entry_var≥0 → 命名空间单记录原子写)
# A2: load_*(读取: None=冷启动 / dict=记录 / StateCorruptError=损坏上抛; 历史按显式日期序列逐日加载)
# O1: 持久化记录 → §3.19 盘前初始化 / §3.9 回测历史 clean P&L / 35号 §3.16 回撤归因
# [/ALGO_FLOW]
"""

Backtest Store — VaR 回测/基线/双轨 P&L/entry_var 持久化门面 (36号 §3.4/§3.13/§3.18)

JsonStateStore 单记录原语 → 业务命名空间方法的薄门面 (只编排不重造)。

命名空间规约 (日频记录 date 后缀; 最新快照 latest 单记录):
    var_backtest_report_YYYY-MM-DD   §3.18 阶段 6 回测报告 (供 §3.10 校准决策)
    var_pnl_dual_YYYY-MM-DD          §3.18 阶段 4 clean/dirty P&L 双轨 (§3.13)
    var_intraday_recalc_YYYY-MM-DD   §3.18 阶段 3 盘中重算日志 (§3.12)
    var_premarket_baseline           §3.18 阶段 2 盘前 VaR/ES 基线 (latest 单记录,
                                     供次日 §3.12 盘中对比 + §3.16 回撤归因)
    entry_var                        §3.4 入场 VaR/ES 基准 (latest 单记录,
                                     与 35号 §3.18 阶段 4b 配对, §3.19 阶段 4 加载)

读语义 (state_store 三分语义原样承接): 记录不存在 → None (冷启动); 存在且可读 →
dict; 存在但损坏 → StateCorruptError 上抛 (消费方 fail-closed, 本层不静默兜底)。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/36_var_es_monitoring.md §3.4/§3.13/§3.18
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from collections.abc import Iterable, Mapping
from datetime import date
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "VarBacktestStore",
    "InvalidBacktestStoreError",
    "ENTRY_VAR_NAMESPACE",
    "PREMARKET_BASELINE_NAMESPACE",
]

logger = logging.getLogger(__name__)

#: §3.4 入场基准命名空间 (latest 单记录)
ENTRY_VAR_NAMESPACE: Final = "entry_var"
#: §3.18 阶段 2 盘前基线命名空间 (latest 单记录)
PREMARKET_BASELINE_NAMESPACE: Final = "var_premarket_baseline"

_BACKTEST_REPORT_PREFIX: Final = "var_backtest_report_"
_PNL_DUAL_PREFIX: Final = "var_pnl_dual_"
_INTRADAY_RECALC_PREFIX: Final = "var_intraday_recalc_"


class InvalidBacktestStoreError(ZephyrBaseError):
    """backtest_store 持久化载荷非法 (非有限值/不变式违反/日期非法)。"""

    error_code = "ZA-RK-0032"


def _validate_trade_date(trade_date: date) -> str:
    """交易日 → 命名空间日期后缀 (ISO 格式纯名字, 无路径分隔符)。"""
    if not isinstance(trade_date, date):
        raise InvalidBacktestStoreError(f"trade_date must be datetime.date, got {type(trade_date).__name__}")
    return trade_date.isoformat()


def _require_finite(value: float, field: str) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise InvalidBacktestStoreError(f"{field} 必须为有限值, got {value!r}")
    return v


class VarBacktestStore:
    """VaR 域持久化门面 (36号 §3.4/§3.13/§3.18)。

    Args:
        store: JsonStateStore 或同接口对象 (save(namespace, dict) / load(namespace))——
            双后端切换经 zephyr.shared.state_store.make_state_store 工厂注入。
    """

    def __init__(self, store: Any) -> None:
        self._store = store

    # ── §3.18 阶段 6: 回测报告 ──

    def save_backtest_report(self, trade_date: date, report: Mapping[str, Any]) -> None:
        """盘后持久化回测报告 (供 §3.10 校准/重构决策 + §3.16 回撤归因参考)。"""
        day = _validate_trade_date(trade_date)
        if not isinstance(report, Mapping):
            raise InvalidBacktestStoreError(f"report must be Mapping, got {type(report).__name__}")
        self._store.save(f"{_BACKTEST_REPORT_PREFIX}{day}", dict(report))

    def load_backtest_report(self, trade_date: date) -> dict[str, Any] | None:
        """加载指定日回测报告 (None=无记录 / StateCorruptError=损坏)。"""
        day = _validate_trade_date(trade_date)
        return self._store.load(f"{_BACKTEST_REPORT_PREFIX}{day}")

    # ── §3.13/§3.18 阶段 4: clean/dirty P&L 双轨 ──

    def save_pnl_dual(self, trade_date: date, clean_pnl: float, dirty_pnl: float) -> None:
        """双轨持久化 clean/dirty P&L (§3.13: clean 供回测验证, dirty 供实际盈亏报告)。"""
        day = _validate_trade_date(trade_date)
        clean = _require_finite(clean_pnl, "clean_pnl")
        dirty = _require_finite(dirty_pnl, "dirty_pnl")
        self._store.save(
            f"{_PNL_DUAL_PREFIX}{day}",
            {"trade_date": day, "clean_pnl": clean, "dirty_pnl": dirty},
        )

    def load_pnl_dual(self, trade_date: date) -> dict[str, Any] | None:
        """加载指定日双轨 P&L (None=无记录)。"""
        day = _validate_trade_date(trade_date)
        return self._store.load(f"{_PNL_DUAL_PREFIX}{day}")

    def load_pnl_dual_history(self, trade_dates: Iterable[date]) -> list[dict[str, Any] | None]:
        """按显式日期序列加载历史双轨 P&L (§3.9 回测加载历史 clean P&L)。

        缺失日返回 None 由调用方过滤——不静默补 0 (数据缺口即缺口,
        补 0 会污染回测超限判定)。
        """
        return [self.load_pnl_dual(d) for d in trade_dates]

    # ── §3.4 入场基准 (latest 单记录, 35号 §3.18 阶段 4b 配对) ──

    def save_entry_var(
        self,
        trade_date: date,
        entry_var: float,
        entry_es: float | None = None,
    ) -> None:
        """持久化入场 VaR/ES 基准 (§3.4: 策略开仓日盘前快照)。

        latest 单记录语义——最近一次开仓快照即真源 (35号 §3.16 回撤归因消费
        current_var vs entry_var); entry_es 可空 (仅 VaR 基准场景)。
        """
        day = _validate_trade_date(trade_date)
        var = _require_finite(entry_var, "entry_var")
        if var < 0:
            raise InvalidBacktestStoreError(f"entry_var 必须 ≥0, got {entry_var}")
        es: float | None = None
        if entry_es is not None:
            es = _require_finite(entry_es, "entry_es")
            if es < var:
                raise InvalidBacktestStoreError(f"entry_es({es}) 必须 ≥ entry_var({var}) (ES ≥ VaR 不变式)")
        self._store.save(
            ENTRY_VAR_NAMESPACE,
            {"trade_date": day, "entry_var": var, "entry_es": es},
        )

    def load_entry_var(self) -> dict[str, Any] | None:
        """加载入场基准 (None=首次启动/前日未持久化, §3.4 冷启动守卫:
        消费方需 None 守卫)。"""
        return self._store.load(ENTRY_VAR_NAMESPACE)

    # ── §3.18 阶段 2: 盘前 VaR/ES 基线 (latest 单记录) ──

    def save_premarket_baseline(self, trade_date: date, var_95: float, cvar_95: float) -> None:
        """持久化盘前 VaR/ES 基线 (供次日 §3.12 盘中对比 + §3.16 回撤归因)。

        ES ≥ VaR 不变式写入守卫 (§3.18 阶段 0: 违反即拒绝持久化)。
        """
        day = _validate_trade_date(trade_date)
        var = _require_finite(var_95, "var_95")
        cvar = _require_finite(cvar_95, "cvar_95")
        if var < 0:
            raise InvalidBacktestStoreError(f"var_95 必须 ≥0, got {var_95}")
        if cvar < var:
            raise InvalidBacktestStoreError(f"cvar_95({cvar}) 必须 ≥ var_95({var}) (ES ≥ VaR 不变式, §3.18 阶段 0)")
        self._store.save(
            PREMARKET_BASELINE_NAMESPACE,
            {"trade_date": day, "var_95": var, "cvar_95": cvar},
        )

    def load_premarket_baseline(self) -> dict[str, Any] | None:
        """加载盘前基线 (None=首次启动/前日未持久化, §3.19 阶段 2:
        盘中重算 var_change_ratio 跳过对比)。"""
        return self._store.load(PREMARKET_BASELINE_NAMESPACE)

    # ── §3.18 阶段 3: 盘中重算日志 ──

    def save_intraday_recalc_log(
        self,
        trade_date: date,
        entries: Iterable[Mapping[str, Any]],
    ) -> None:
        """持久化当日盘中重算日志 (§3.12 重算结果反馈回测 + §3.16 FHS 触发 3)。"""
        day = _validate_trade_date(trade_date)
        rows = [dict(e) for e in entries]
        self._store.save(
            f"{_INTRADAY_RECALC_PREFIX}{day}",
            {"trade_date": day, "entries": rows},
        )

    def load_intraday_recalc_log(self, trade_date: date) -> list[dict[str, Any]] | None:
        """加载指定日盘中重算日志条目 (None=无记录/当日无重算)。"""
        day = _validate_trade_date(trade_date)
        rec = self._store.load(f"{_INTRADAY_RECALC_PREFIX}{day}")
        if rec is None:
            return None
        entries = rec.get("entries")
        return list(entries) if isinstance(entries, list) else None
