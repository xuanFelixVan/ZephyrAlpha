"""progressive_disclosure_injector.py — 渐进式披露 (B7, DD81, TASK-015 beta w)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DisclosureResult:
    summary_injected: bool
    ke_ids_available: list[str]
    expanded_ke_id: str = ""


class ProgressiveDisclosureInjector:
    """摘要先注→agent 请求展开完整 KE (DD81)."""
    def inject_summary(self, ke_ids: list[str]) -> DisclosureResult:
        return DisclosureResult(summary_injected=True, ke_ids_available=ke_ids)

    def expand(self, ke_id: str) -> str:
        return f"Full content for {ke_id}"
