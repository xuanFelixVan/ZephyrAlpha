"""
Capacity Runbook Generator — 容量运维知识自动文档化 (盲点 #44)
特性：
  - 每次 SEV-1/SEV-2 事后产出 runbook
  - 诊断+修复步骤+预防措施
"""
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Runbook:
    incident_id: str
    severity: str
    timestamp: str
    root_cause: str
    repair_steps: list[str] = field(default_factory=list)
    prevention_steps: list[str] = field(default_factory=list)
    affected_modules: list[str] = field(default_factory=list)


class CapacityRunbookGenerator:
    """
    容量 Runbook 生成器 (盲点 #44)
    """

    def __init__(self):
        self._runbooks: list[Runbook] = []

    def generate(self, incident_id: str, severity: str,
                 root_cause: str, affected_modules: list[str]) -> Runbook:
        runbook = Runbook(
            incident_id=incident_id,
            severity=severity,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            root_cause=root_cause,
            repair_steps=["1. Isolate affected module", "2. Verify Error Budget", "3. Restore gradually"],
            prevention_steps=["1. Add capacity test for root cause", "2. Update SLO thresholds"],
            affected_modules=affected_modules,
        )
        self._runbooks.append(runbook)
        return runbook

    def export(self) -> str:
        lines = ["# Capacity Runbooks", f"Total: {len(self._runbooks)}", ""]
        for rb in self._runbooks:
            lines.append(f"## {rb.incident_id} ({rb.severity})")
            lines.append(f"- Time: {rb.timestamp}")
            lines.append(f"- Root Cause: {rb.root_cause}")
            lines.append(f"- Affected: {', '.join(rb.affected_modules)}")
            lines.append("- Repair Steps:")
            for step in rb.repair_steps:
                lines.append(f"  {step}")
            lines.append("- Prevention Steps:")
            for step in rb.prevention_steps:
                lines.append(f"  {step}")
            lines.append("")
        return "\n".join(lines)
