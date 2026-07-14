# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.impact.impact_propagator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_impact_propagator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Impact Propagator — 变更影响传播分析。

依据：
    蓝图 MOD-TASK_SYSTEM §6.11.5 + v0.6.0
    任务卡 TASK-INF-0128
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ImpactPath:
    source_file: str
    target_file: str
    path_length: int
    intermediate_nodes: list[str]
    impact_type: str = "direct"


@dataclass
class PropagationReport:
    task_id: str
    source_files: list[str]
    affected_files: list[str]
    propagation_depth: int
    paths: list[ImpactPath]
    critical_paths: list[ImpactPath]


class ImpactPropagator:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def analyze_propagation(self, task_card: dict[str, Any]) -> PropagationReport:
        downstream = task_card.get("downstream_outputs", [])
        source_files = [o.get("path", "") for o in downstream]
        depends_on = task_card.get("depends_on", [])

        affected_files: set[str] = set()
        paths: list[ImpactPath] = []

        for src in source_files:
            for dep in depends_on:
                paths.append(
                    ImpactPath(
                        source_file=src,
                        target_file=dep,
                        path_length=1,
                        intermediate_nodes=[],
                        impact_type="direct",
                    )
                )
                affected_files.add(dep)

        for src in source_files:
            for tgt in source_files:
                if src != tgt:
                    paths.append(
                        ImpactPath(
                            source_file=src,
                            target_file=tgt,
                            path_length=1,
                            intermediate_nodes=[],
                            impact_type="inter_source",
                        )
                    )

        critical = [p for p in paths if p.path_length <= 1]

        return PropagationReport(
            task_id=task_card.get("task_id", ""),
            source_files=source_files,
            affected_files=list(affected_files),
            propagation_depth=max((p.path_length for p in paths), default=0),
            paths=paths,
            critical_paths=critical,
        )

    def estimate_blast_radius(self, task_card: dict[str, Any]) -> int:
        downstream = task_card.get("downstream_outputs", [])
        depends_on = task_card.get("depends_on", [])
        blocked_by = task_card.get("blocked_by", [])

        return len(downstream) * 2 + len(depends_on) + len(blocked_by)
