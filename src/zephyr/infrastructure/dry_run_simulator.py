# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.dry_run_simulator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_dry_run_simulator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RI-14 DryRunSimulator — 干运行模拟器
=====================================
职责：在真实执行前进行安全预演——模拟操作流程，检测潜在风险，输出风险评估报告。
对标：K8s dry-run + Terraform plan + SQL EXPLAIN
使用方式：
    sim = DryRunSimulator(sandbox_root="data/dry_runs/")
    result = sim.simulate(operation_plan)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

__all__ = [
    "DryRunSimulator",
    "SimulationResult",
    "SimulationRisk",
    "SimulationStatus",
]


_RISK_ORDER: dict[str, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class SimulationRisk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimulationStatus(str, Enum):
    PASSED = "passed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class SimulationResult:
    simulation_id: str
    status: SimulationStatus = SimulationStatus.PASSED
    risk: SimulationRisk = SimulationRisk.NONE
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    estimated_duration_s: float = 0.0
    rollback_plan: str = ""
    simulated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_safe(self) -> bool:
        return self.status != SimulationStatus.BLOCKED


class DryRunSimulator:
    """干运行模拟器

    在真实执行前，在隔离沙箱中进行操作预演：
    - 文件操作模拟（只读/不修改真实文件）
    - 权限预检查
    - 破坏性操作识别
    - 回滚计划生成
    """

    _DANGEROUS_PATTERNS: list[str] = [
        "rm -rf",
        "del /f",
        "DROP TABLE",
        "DROP DATABASE",
        "format",
        "FORMAT C:",
        "shutdown",
        "restart",
        "chmod 777",
        "icacls /grant Everyone:F",
    ]

    _SENSITIVE_PATHS: list[str] = [
        "C:\\Windows\\",
        "C:\\Program Files\\",
        "/etc/",
        "/usr/",
        ".git\\",
        ".git/",
        "node_modules\\",
        "node_modules/",
    ]

    def __init__(self, sandbox_root: str | Path = "data/dry_runs/"):
        self._sandbox_root = Path(sandbox_root)
        self._sandbox_root.mkdir(parents=True, exist_ok=True)
        self._sim_count: int = 0

    def simulate(
        self,
        operation: dict[str, Any],
        check_permissions: bool = True,
    ) -> SimulationResult:
        self._sim_count += 1
        sim_id = f"SIM-{self._sim_count:04d}"
        result = SimulationResult(simulation_id=sim_id)

        op_type = operation.get("type", "unknown")
        target = str(operation.get("target", ""))
        content = str(operation.get("content", ""))

        if op_type in ("file_write", "file_delete", "file_move", "dir_create", "dir_delete"):
            result.affected_files.append(target)

        for pattern in self._DANGEROUS_PATTERNS:
            if pattern.lower() in content.lower() or pattern.lower() in target.lower():
                result.warnings.append(f"检测到危险操作模式: {pattern}")
                result.risk = SimulationRisk.CRITICAL
                result.status = SimulationStatus.BLOCKED
                break

        for sensitive in self._SENSITIVE_PATHS:
            if sensitive.replace("\\", "/") in target.replace("\\", "/"):
                result.warnings.append(f"操作涉及敏感路径: {sensitive}")
                if _RISK_ORDER[result.risk.value] < _RISK_ORDER[SimulationRisk.HIGH.value]:
                    result.risk = SimulationRisk.HIGH

        if check_permissions and op_type in ("file_write", "file_delete"):
            target_path = Path(target) if target else None
            if target_path and target_path.exists():
                if not os.access(str(target_path), os.W_OK):
                    result.errors.append(f"无写入权限: {target}")
                    result.status = SimulationStatus.BLOCKED
                    result.risk = SimulationRisk.HIGH

        if result.risk is SimulationRisk.NONE and result.warnings:
            result.risk = SimulationRisk.LOW

        if result.warnings and result.status == SimulationStatus.PASSED:
            result.status = SimulationStatus.PASSED_WITH_WARNINGS

        if op_type in ("file_write", "file_delete") and target:
            result.rollback_plan = f"restore from backup: {target}"

        self._save_artifact(sim_id, result, operation)
        return result

    def simulate_batch(
        self,
        operations: list[dict[str, Any]],
    ) -> list[SimulationResult]:
        results: list[SimulationResult] = []
        for op in operations:
            results.append(self.simulate(op))
        return results

    def _save_artifact(
        self,
        sim_id: str,
        result: SimulationResult,
        operation: dict[str, Any],
    ) -> None:
        artifact_dir = self._sandbox_root / sim_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        tmp_path = artifact_dir / f"result.json.{os.getpid()}.tmp"
        data = {
            "simulation_id": result.simulation_id,
            "status": result.status.value,
            "risk": result.risk.value,
            "warnings": result.warnings,
            "errors": result.errors,
            "affected_files": result.affected_files,
            "rollback_plan": result.rollback_plan,
            "simulated_at": result.simulated_at,
            "operation": operation,
        }
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(str(tmp_path), str(artifact_dir / "result.json"))
        except PermissionError:
            try:
                os.remove(str(tmp_path))
            except OSError:
                pass
