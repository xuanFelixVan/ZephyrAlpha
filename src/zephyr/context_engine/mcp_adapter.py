# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.mcp_adapter

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""mcp_adapter.py — 双轨 MCP 适配 (DD109, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class MCPSource:
    track: str  # A(Bounded) or B(Indexed)
    connected: bool
    features: list[str]


class MCPAdapter:
    """A/B 双轨适配 + 5 个 MCP 工具 (DD109)."""
    def probe_track(self, track: str) -> MCPSource:
        return MCPSource(track=track, connected=True, features=["search", "inject", "status"])

    def get_features_for_track(self, track: str) -> list[str]:
        probe = self.probe_track(track)
        return probe.features if probe.connected else []
