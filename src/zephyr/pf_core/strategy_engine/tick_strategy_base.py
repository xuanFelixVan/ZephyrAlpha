# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.tick_strategy_base
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.backtest.core.tick_replay
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] on_tick 返回 {symbol: target_weight}；target_weight=0 表示清仓；空 dict 表示不调仓
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] on_tick 抛异常时 EDE 捕获并跳过该 tick（不中断回测）
# [TESTS] tests/pf_core/test_tick_strategy.py
# [A_module] module_id=MOD-PRT-tick_strategy_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_PORTFOLIO_CORE — TickStrategyBase + TickStrategyRegistry（路径 B：tick 级策略/做T）

与 StrategyBase（日频截面，signals=dict[str,float]）正交。本基类的策略每个 tick
被 EDE 调用一次，接收 TickEvent（含 5 档盘口 TickSnapshot），返回 {symbol: target_weight}。
EDE 撮合层根据 (target_weight - 当前持仓) 算 delta 下单。

策略可维护内部状态（如 30 秒窗口的 high/low、理想持仓），实现 intraday 做 T 逻辑。
与 StrategyBase 的关系：独立基类 + 独立注册表，不继承——日频截面与 tick 级是不同范式，
强行继承会让 generate_target_weights（日频）与 on_tick（tick）语义混淆。

EDE callback 契约：Callable[[TickEvent], dict[str, float]]，与本基类 on_tick 完全对齐，
故 StrategyRunner.run_tick_strategy_backtest 可直接传 strategy.on_tick 给 EDE.run_tick。

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7（EDE 做T场景）
"""
from __future__ import annotations

import abc
import importlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:  # 避免运行时跨域循环 import
    from zephyr.backtest.core.tick_replay import TickEvent

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TickStrategyMeta:
    """Tick 策略元数据。"""

    strategy_id: str
    name: str
    description: str = ""
    author: str = "agent"
    tags: list[str] = field(default_factory=list)


class TickStrategyBase(abc.ABC):
    """Tick 级策略抽象基类（做T专用）。

    子类 MUST:
      - 实现 on_tick()
      - 定义 _meta: TickStrategyMeta
      - 通过 @TickStrategyBase.register 装饰器注册

    on_tick 语义：
      - 每个 tick 调用一次，返回 {symbol: target_weight}
      - target_weight=0.0 表示清仓该 symbol
      - 返回空 dict 表示本 tick 不调仓（持仓不变）
      - EDE 根据 (target_weight * 总市值 / price - 当前持仓) 算 delta 撮合
      - 策略无需感知当前持仓——只表达"理想目标权重"，EDE 负责 delta 计算

    状态管理：
      - 策略可在 __init__ 初始化状态（窗口、阈值）
      - on_tick 可读写实例状态（如维护 30 秒 tick 窗口）
      - on_fill 回调可用于成交后状态更新
    """

    _registry: ClassVar[dict[str, type["TickStrategyBase"]]] = {}

    @abc.abstractmethod
    def on_tick(self, event: "TickEvent") -> dict[str, float]:
        """每个 tick 调用，返回目标权重 dict。

        Args:
            event: TickEvent，含 timestamp/symbol/tick_data(TickSnapshot)/sequence

        Returns:
            {symbol: target_weight}，空 dict 表示不调仓
        """
        ...

    def on_fill(self, fill) -> None:
        """成交回调（子类可覆写，用于成交后状态更新）。"""
        pass

    @classmethod
    def meta(cls) -> TickStrategyMeta | None:
        return getattr(cls, "_meta", None)

    @classmethod
    def register(cls, strategy_class: type["TickStrategyBase"]) -> type["TickStrategyBase"]:
        m = strategy_class.meta
        if callable(m):
            m = m()
        if m:
            if m.strategy_id in cls._registry:
                raise ValueError(f"TickStrategy '{m.strategy_id}' already registered")
            cls._registry[m.strategy_id] = strategy_class
            _logger.info("TickStrategyRegistry: registered %s (%s)", m.strategy_id, m.name)
        return strategy_class

    @classmethod
    def get(cls, strategy_id: str) -> type["TickStrategyBase"] | None:
        return cls._registry.get(strategy_id)

    @classmethod
    def list_all(cls) -> dict[str, type["TickStrategyBase"]]:
        return dict(cls._registry)

    @classmethod
    def count(cls) -> int:
        return len(cls._registry)

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


def autodiscover_tick_strategies(
    package_path: str = "zephyr.pf_core",
) -> int:
    """自动发现并注册 tick 策略（扫描 package_path 下的 .py 模块）。"""
    found = 0
    try:
        pkg = importlib.import_module(package_path)
        pkg_dir = Path(pkg.__file__).parent if pkg.__file__ else None
        if pkg_dir and pkg_dir.exists():
            for fp in sorted(pkg_dir.glob("*.py")):
                if fp.stem.startswith("_") or fp.stem == "__init__":
                    continue
                try:
                    importlib.import_module(f"{package_path}.{fp.stem}")
                    found += 1
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    _logger.warning("Failed to auto-discover tick strategy %s: %s", fp.stem, exc, exc_info=True)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning("Tick strategy autodiscover skipped: %s", exc, exc_info=True)
    return found


__all__ = ["TickStrategyBase", "TickStrategyMeta", "autodiscover_tick_strategies"]
