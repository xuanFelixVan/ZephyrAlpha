"""
CBAC 能力矩阵（Capability-Based Access Control Matrix — CT-CBAC-001）

依据：MOD-MASTER-001 蓝图 §十五
12×12 系统授权矩阵——18条精确 capability 声明。
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field


class Capability(BaseModel):
    capability_id: str
    caller: str
    target: str
    actions: list[str]
    auth_token: str = ""
    description: str = ""


class CbacMatrix:
    def __init__(self):
        self._capabilities: dict[str, Capability] = {}
        self._checksum: str = ""
        self._init_capabilities()

    def _init_capabilities(self) -> None:
        caps = [
            ("CAP-001", "orchestrator", "script_system", ["dispatch_task"], "Webhook Client"),
            ("CAP-002", "orchestrator", "context_engine", ["build_context"], "Internal RPC"),
            ("CAP-003", "orchestrator", "vector_memory", ["write_vector", "read_vector"], "gRPC"),
            ("CAP-004", "orchestrator", "gate_engine", ["invoke_gate"], "Internal RPC"),
            ("CAP-005", "orchestrator", "database", ["write_taskcard", "read_taskcard", "update_status"], "SQLite"),
            ("CAP-006", "script_system", "orchestrator", ["report_finding"], "Webhook Server"),
            ("CAP-007", "script_system", "knowledge_base", ["write_knowledge_entry"], "Internal RPC"),
            ("CAP-008", "script_system", "gate_engine", ["report_script_result"], "Internal RPC"),
            ("CAP-009", "knowledge_base", "orchestrator", ["query_knowledge"], "Internal RPC"),
            ("CAP-010", "knowledge_base", "vector_memory", ["write_vector"], "gRPC"),
            ("CAP-011", "context_engine", "orchestrator", ["query_context"], "Internal RPC"),
            ("CAP-012", "context_engine", "vector_memory", ["search_vector"], "gRPC"),
            ("CAP-013", "context_engine", "llm_security", ["check_safety"], "Internal RPC"),
            ("CAP-014", "feedback_loop", "orchestrator", ["report_anomaly"], "Internal RPC"),
            ("CAP-015", "feedback_loop", "database", ["write_metrics", "read_metrics"], "SQLite"),
            ("CAP-016", "system_telemetry", "orchestrator", ["push_metrics"], "Internal RPC"),
            ("CAP-017", "system_telemetry", "feedback_loop", ["push_metrics"], "Internal RPC"),
            ("CAP-018", "pipeline", "orchestrator", ["route_task"], "Internal RPC"),
        ]
        for cap_id, caller, target, actions, auth in caps:
            self._capabilities[cap_id] = Capability(
                capability_id=cap_id,
                caller=caller,
                target=target,
                actions=actions,
                auth_token=auth,
            )
        self._compute_checksum()

    def _compute_checksum(self) -> None:
        raw = json.dumps(
            {k: v.model_dump() for k, v in sorted(self._capabilities.items())},
            sort_keys=True,
        )
        self._checksum = hashlib.sha256(raw.encode()).hexdigest()

    @property
    def checksum(self) -> str:
        return self._checksum

    def check(self, caller: str, target: str, action: str) -> tuple[bool, str]:
        current = hashlib.sha256(
            json.dumps(
                {k: v.model_dump() for k, v in sorted(self._capabilities.items())},
                sort_keys=True,
            ).encode()
        ).hexdigest()
        if current != self._checksum:
            return False, f"CBAC_CHECKSUM_MISMATCH: 矩阵已被篡改"

        for cap in self._capabilities.values():
            if cap.caller == caller and cap.target == target and action in cap.actions:
                return True, "GRANTED"
        return False, "DENIED"

    def list_capabilities(self) -> list[Capability]:
        return list(self._capabilities.values())


_classes_export = {"Capability": Capability, "CbacMatrix": CbacMatrix}
