# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.governance.strategies.strategy_base
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_strategy_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_interface
# status: active
# created: "2026-05-05"
# ---

"""D_PORTFOLIO_CORE — StrategyBase + StrategyMeta + StrategyRegistry

Hand-maintained OCP extension point. DO NOT overwrite via codegen.

CTR 契约：
  OCP-002  StrategyBase + StrategyRegistry   策略扩展点

SSoT: cross_layer_contracts.yaml v3.0 → OCP-002
"""

from __future__ import annotations

import abc
import importlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StrategyMeta:
    """策略元数据（OCP-002 meta_fields）"""

    strategy_id: str
    name: str
    strategy_type: str
    version: str
    description: str
    factor_dependencies: list[str] = field(default_factory=list)
    author: str = "agent"
    tags: list[str] = field(default_factory=list)
    supported_markets: list[str] = field(default_factory=list)


class StrategyBase(abc.ABC):
    """策略抽象基类（OCP-002 OCP 扩展点）

    所有策略实现 MUST:
      - 实现 generate_target_weights()
      - 定义 meta 属性返回 StrategyMeta
      - 通过 @StrategyRegistry.register 装饰器注册
    """

    _registry: ClassVar[dict[str, type[StrategyBase]]] = {}

    @abc.abstractmethod
    def generate_target_weights(
        self,
        universe: list[str],
        signals: dict[str, float],
        constraints: dict[str, Any],
    ) -> dict[str, float]: ...

    def validate_constraints(self, weights: dict[str, float]) -> bool:
        """验证约束条件（默认通过，子类可覆写）"""
        return True

    @classmethod
    def meta(cls) -> StrategyMeta | None:
        return getattr(cls, "_meta", None)

    def on_fill(self, fill) -> None:
        pass

    def on_risk_alert(self, alert) -> None:
        pass


class StrategyRegistry:
    """策略注册表

    用法:
        @StrategyRegistry.register
        class MyStrategy(StrategyBase):
            meta = StrategyMeta(...)
            ...
    """

    _strategies: dict[str, type[StrategyBase]] = {}

    @classmethod
    def register(cls, strategy_class: type[StrategyBase]) -> type[StrategyBase]:
        m = strategy_class.meta
        if callable(m):
            m = m()
        if m:
            if m.strategy_id in cls._strategies:
                raise ValueError(f"Strategy with id '{m.strategy_id}' already registered")
            cls._strategies[m.strategy_id] = strategy_class
            _logger.info("StrategyRegistry: registered %s (%s)", m.strategy_id, m.name)
        return strategy_class

    @classmethod
    def get(cls, strategy_id: str) -> type[StrategyBase] | None:
        return cls._strategies.get(strategy_id)

    @classmethod
    def list_all(cls) -> dict[str, type[StrategyBase]]:
        return dict(cls._strategies)

    @classmethod
    def count(cls) -> int:
        return len(cls._strategies)

    @classmethod
    def clear(cls) -> None:
        cls._strategies.clear()


def autodiscover_strategies(
    package_path: str = "zephyr.pf_core",
) -> int:
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
                except Exception as exc:
                    _logger.warning("Failed to auto-discover strategy %s: %s", fp.stem, exc)
    except Exception as exc:
        _logger.warning("Strategy autodiscover skipped: %s", exc)
    return found


__all__ = ["StrategyBase", "StrategyMeta", "StrategyRegistry", "autodiscover_strategies"]
