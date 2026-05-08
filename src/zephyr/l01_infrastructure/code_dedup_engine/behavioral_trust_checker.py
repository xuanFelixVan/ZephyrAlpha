"""行为信任检查器 — 行为漂移DIVERGED检测."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TrustCheck:
    function_name: str = ""
    behavior_signature: str = ""
    current_hash: str = ""
    original_hash: str = ""
    trusted: bool = False
    status: str = "TRUSTED"


class BehavioralTrustChecker:
    """行为正确性检查."""

    def __init__(self) -> None:
        self._signatures: dict[str, str] = {}

    def register(self, function_name: str, behavior_signature: str) -> None:
        self._signatures[function_name] = behavior_signature

    def verify(self, function_name: str, current_behavior: str) -> TrustCheck:
        original = self._signatures.get(function_name)
        if original is None:
            return TrustCheck(
                function_name=function_name,
                current_hash=current_behavior,
                trusted=True,
                status="UNTRACKED",
            )
        if current_behavior == original:
            return TrustCheck(
                function_name=function_name,
                behavior_signature=original,
                current_hash=current_behavior,
                original_hash=original,
                trusted=True,
                status="TRUSTED",
            )
        return TrustCheck(
            function_name=function_name,
            behavior_signature=original,
            current_hash=current_behavior,
            original_hash=original,
            trusted=False,
            status="DIVERGED",
        )
