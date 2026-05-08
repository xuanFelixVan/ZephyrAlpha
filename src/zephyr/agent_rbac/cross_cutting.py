"""
横切面模块集合 — PermissionHookRegistry, PermissionTopology, AutoMaintenance, ForensicAssurance

MOD-INF-018 cross_cutting package
"""

import time
import hashlib
import hmac
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


HookCallback = Callable[[dict], None]


class HookType(str, Enum):
    PRE = "pre"
    POST = "post"
    ON_BLOCKED = "on_blocked"
    ON_KILL_SWITCH = "on_kill_switch"


@dataclass
class Hook:
    type: HookType
    callback: HookCallback
    name: str = ""
    enabled: bool = True


class PermissionHookRegistry:
    def __init__(self) -> None:
        self._hooks: list[Hook] = []

    def register(self, hook_type: HookType, callback: HookCallback, name: str = "") -> Hook:
        hook = Hook(type=hook_type, callback=callback, name=name)
        self._hooks.append(hook)
        return hook

    def trigger(self, hook_type: HookType, context: dict) -> int:
        count = 0
        for hook in self._hooks:
            if hook.type == hook_type and hook.enabled:
                try:
                    hook.callback(context)
                    count += 1
                except Exception:
                    pass
        return count

    def disable(self, name: str) -> bool:
        for hook in self._hooks:
            if hook.name == name:
                hook.enabled = False
                return True
        return False

    def clear(self) -> None:
        self._hooks.clear()


@dataclass
class TopologyNode:
    name: str
    depends_on: list[str] = field(default_factory=list)
    depended_by: list[str] = field(default_factory=list)
    layer: int = 0


class PermissionTopology:
    def __init__(self) -> None:
        self._nodes: dict[str, TopologyNode] = {}

    def add_node(self, name: str, depends_on: list[str] | None = None) -> TopologyNode:
        node = TopologyNode(name=name, depends_on=depends_on or [])
        self._nodes[name] = node
        for dep in node.depends_on:
            if dep in self._nodes:
                self._nodes[dep].depended_by.append(name)
        return node

    def detect_cycles(self) -> list[list[str]]:
        cycles: list[list[str]] = []
        visited: set[str] = set()
        stack: list[str] = []

        def dfs(node: str) -> None:
            if node in stack:
                cycle_start = stack.index(node)
                cycles.append(stack[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            stack.append(node)
            n = self._nodes.get(node)
            if n:
                for dep in n.depends_on + n.depended_by:
                    dfs(dep)
            stack.pop()

        for name in self._nodes:
            if name not in visited:
                dfs(name)
        return cycles

    def get_impact(self, node_name: str) -> list[str]:
        affected: set[str] = set()
        queue = [node_name]
        while queue:
            current = queue.pop(0)
            if current in affected:
                continue
            affected.add(current)
            n = self._nodes.get(current)
            if n:
                queue.extend(n.depended_by)
        return list(affected)


class AutoMaintenance:
    def __init__(self) -> None:
        self._rule_last_used: dict[str, float] = {}
        self._zombie_threshold_days: float = 30.0

    def record_rule_usage(self, rule_id: str) -> None:
        self._rule_last_used[rule_id] = time.time()

    def detect_zombie_rules(self) -> list[str]:
        cutoff = time.time() - (self._zombie_threshold_days * 86400)
        zombies = [
            rid for rid, last in self._rule_last_used.items()
            if last < cutoff
        ]
        return zombies

    def complexity_budget(self, rule_count: int, threshold: int = 500) -> dict:
        usage = rule_count / threshold if threshold > 0 else 0
        return {
            "total_rules": rule_count,
            "budget_limit": threshold,
            "usage_percent": round(usage * 100, 2),
            "over_budget": rule_count > threshold,
        }


class ForensicAssurance:
    def __init__(self, signing_key: Optional[bytes] = None) -> None:
        self._signing_key = signing_key or hashlib.sha256(b"zephyr-alpha-forensic").digest()
        self._signed_records: list[dict] = []

    def sign_record(self, event: dict) -> dict:
        payload = str(event).encode("utf-8")
        signature = hmac.new(self._signing_key, payload, hashlib.sha256).hexdigest()
        record = {
            **event,
            "signature": signature,
            "timestamp": time.time(),
        }
        self._signed_records.append(record)
        return record

    def verify_signature(self, record: dict) -> bool:
        sig = record.pop("signature", "")
        ts = record.pop("timestamp", None)
        payload = str(record).encode("utf-8")
        expected = hmac.new(self._signing_key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)

    def get_records(self) -> list[dict]:
        return list(self._signed_records)
