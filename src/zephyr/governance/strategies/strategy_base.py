# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.governance.strategies.strategy_base
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_interface
# status: active
# created: "2026-05-05"
# ---

"""
D_PORTFOLIO_CORE — StrategyBase + StrategyMeta + StrategyRegistry

Hand-maintained OCP extension point. DO NOT overwrite via codegen.

CTR 契约：
  OCP-002  StrategyBase + StrategyRegistry   策略扩展点

SSoT: cross_layer_contracts.yaml v3.0 -> OCP-002

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: package_path 参数
#   fields: 参数 package_path，类型注解 str
#   code: strategy_base.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StrategyBase
#   name_en: StrategyBase
#   intro: 策略抽象基类（OCP-002 OCP 扩展点）
#   desc: 策略抽象基类（OCP-002 OCP 扩展点） 所有策略实现 MUST: - 实现 generate_target_weights() - 定义 meta 属性返回 Strate…；公共方法（定义序）: generat…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② StrategyRegistry
#   name_en: StrategyRegistry
#   intro: 策略注册表
#   desc: 策略注册表 用法: @StrategyRegistry.register class MyStrategy(StrategyBase): meta = StrategyMeta(…；公共方法（定义序）: registe…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ autodiscover_strategies
#   name_en: autodiscover_strategies
#   intro: autodiscover_strategies(package_path) 源码 L181-L199
#   desc: 源码 L181-L199
#   inputs: package_path
#   outputs: int
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
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
    """自动发现并注册策略模块。

    扫描范围（2026-09-01 修）：包顶层 *.py + 一层子包（如 pf_core/strategies/）。
    此前只扫顶层——strategies/ 子目录里的 multifactor-sleeve / eventdriven-sleeve
    永远不被发现，回测页策略库只剩 2 个（#BT-PIPELINE-001 Owner 实测反馈）。
    """
    found = 0
    try:
        pkg = importlib.import_module(package_path)
        pkg_dir = Path(pkg.__file__).parent if pkg.__file__ else None
        if pkg_dir and pkg_dir.exists():
            files = sorted(pkg_dir.glob("*.py"))
            # 一层子包（strategies/ 等，含 __init__.py 的目录）也扫其 *.py
            for sub in sorted(p for p in pkg_dir.iterdir() if p.is_dir() and (p / "__init__.py").exists()):
                if sub.name.startswith("_"):
                    continue
                files.extend(sorted(sub.glob("*.py")))
            for fp in files:
                if fp.stem.startswith("_") or fp.stem == "__init__":
                    continue
                mod_name = (
                    f"{package_path}.{fp.parent.relative_to(pkg_dir).as_posix().replace('/', '.')}.{fp.stem}"
                    if fp.parent != pkg_dir
                    else f"{package_path}.{fp.stem}"
                )
                try:
                    importlib.import_module(mod_name)
                    found += 1
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    _logger.warning("Failed to auto-discover strategy %s: %s", mod_name, exc, exc_info=True)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning("Strategy autodiscover skipped: %s", exc, exc_info=True)
    return found


__all__ = ["StrategyBase", "StrategyMeta", "StrategyRegistry", "autodiscover_strategies"]
