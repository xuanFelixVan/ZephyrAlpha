from __future__ import annotations

from dataclasses import dataclass, field
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/strategy_base.py

OCP-002: StrategyBase + StrategyRegistry / 策略扩展点

L05 策略基类契约。所有策略必须继承 StrategyBase，实现 generate_target_weights()，向 StrategyRegistry 注册。

SSoT: cross-layer-contracts.yaml → OCP-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""

@dataclass(frozen=True)
class StrategyBase + StrategyRegistry:
    pass
