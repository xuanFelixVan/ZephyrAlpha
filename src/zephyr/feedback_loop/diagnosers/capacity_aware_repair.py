"""Capacity Aware Repair — v0.9.0 R120

Blindspot: FLE executes repairs without accounting for current resource headroom.
Risk: R120 — Repair action itself causes resource exhaustion — cascading failure.
"""
from dataclasses import dataclass


@dataclass
class CapacityAwareRepair:

    def check_headroom(self, action_cost: float, available: float) -> bool:
        return available >= action_cost * 1.2
