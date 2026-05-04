from __future__ import annotations

from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/broker_interface.py

OCP-003: BrokerInterface / 券商扩展点

L06 券商接口契约。所有券商适配器必须实现此接口。支持同时接入多家券商，通过 SOR 路由。

SSoT: cross-layer-contracts.yaml → OCP-003
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class BrokerInterface:
    pass
