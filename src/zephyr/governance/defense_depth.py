from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DefenseLayer(str, Enum):
    L1_DEP_AUDIT = "L1_DEP_AUDIT"
    L2_STATIC_ANALYSIS = "L2_STATIC_ANALYSIS"
    L3_SANDBOX = "L3_SANDBOX"
    L4_SECRETS = "L4_SECRETS"
    L5_AUDIT_TRAIL = "L5_AUDIT_TRAIL"
    L6_CIRCUIT_BREAKER = "L6_CIRCUIT_BREAKER"


class LayerDef(BaseModel):
    layer: DefenseLayer
    label: str
    enabled: bool
    tech_stack: str
    audit_frequency_days: int


DEFENSE_DEPTH: dict[DefenseLayer, LayerDef] = {
    DefenseLayer.L1_DEP_AUDIT: LayerDef(
        layer=DefenseLayer.L1_DEP_AUDIT,
        label="依赖审计",
        enabled=True,
        tech_stack="SBOM: pip-lock + npm-lock + Grype扫描",
        audit_frequency_days=7,
    ),
    DefenseLayer.L2_STATIC_ANALYSIS: LayerDef(
        layer=DefenseLayer.L2_STATIC_ANALYSIS,
        label="静态分析",
        enabled=True,
        tech_stack="Ruff + mypy + Bandit",
        audit_frequency_days=1,
    ),
    DefenseLayer.L3_SANDBOX: LayerDef(
        layer=DefenseLayer.L3_SANDBOX,
        label="沙箱隔离",
        enabled=True,
        tech_stack="wasmtime-py + 最小权限容器",
        audit_frequency_days=30,
    ),
    DefenseLayer.L4_SECRETS: LayerDef(
        layer=DefenseLayer.L4_SECRETS,
        label="Secrets管理",
        enabled=True,
        tech_stack="local vault + Git加密 + .env 本地化",
        audit_frequency_days=1,
    ),
    DefenseLayer.L5_AUDIT_TRAIL: LayerDef(
        layer=DefenseLayer.L5_AUDIT_TRAIL,
        label="审计追踪",
        enabled=True,
        tech_stack="every mutation logged + journal + checkpoint",
        audit_frequency_days=0,
    ),
    DefenseLayer.L6_CIRCUIT_BREAKER: LayerDef(
        layer=DefenseLayer.L6_CIRCUIT_BREAKER,
        label="断路器",
        enabled=True,
        tech_stack="kill_switch.py + 自动熔断 + 自愈",
        audit_frequency_days=0,
    ),
}


def get_layer(layer: DefenseLayer) -> Optional[LayerDef]:
    return DEFENSE_DEPTH.get(layer)


def get_layer_by_level(level: int) -> Optional[LayerDef]:
    layers = list(DefenseLayer)
    if 0 <= level - 1 < len(layers):
        return DEFENSE_DEPTH.get(layers[level - 1])
    return None


def all_enabled() -> bool:
    return all(d.enabled for d in DEFENSE_DEPTH.values())
