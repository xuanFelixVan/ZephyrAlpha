# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.impact.llm_impact_analyzer
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
# [A_module] module_id=MOD-INF_llm_impact_analyzer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
LLM Impact Analyzer — 语义影响分析器。

依据：
    蓝图 MOD-TASK_SYSTEM §6.11.2 + v0.6.0
    任务卡 TASK-INF-0117
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ImpactAssessment:
    task_id: str
    files_affected: list[str]
    risk_level: str
    blast_radius: int
    requires_rollback_sim: bool = False
    recommendation: str = ""


@dataclass
class DependencyCluster:
    cluster_id: str
    tasks: list[str]
    shared_files: list[str]
    cluster_risk: str


class LLMImpactAnalyzer:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def analyze_impact(self, task_card: dict[str, Any]) -> ImpactAssessment:
        downstream = task_card.get("downstream_outputs", [])
        files_affected = [o.get("path", "") for o in downstream]

        depends_on = task_card.get("depends_on", [])
        blocked_by = task_card.get("blocked_by", [])

        blast_radius = len(files_affected) + len(depends_on) + len(blocked_by)

        if blast_radius > 10:
            risk_level = "CRITICAL"
            recommendation = "Run rollback simulation before execution"
            requires_sim = True
        elif blast_radius > 5:
            risk_level = "HIGH"
            recommendation = "Review dependencies before execution"
            requires_sim = False
        elif blast_radius > 2:
            risk_level = "MEDIUM"
            recommendation = "Standard procedure"
            requires_sim = False
        else:
            risk_level = "LOW"
            recommendation = "Safe to execute immediately"
            requires_sim = False

        return ImpactAssessment(
            task_id=task_card.get("task_id", ""),
            files_affected=files_affected,
            risk_level=risk_level,
            blast_radius=blast_radius,
            requires_rollback_sim=requires_sim,
            recommendation=recommendation,
        )

    def compute_file_similarity(self, file_a: str, file_b: str) -> float:
        root = self._project_root
        path_a = root / file_a
        path_b = root / file_b

        if not path_a.exists() or not path_b.exists():
            return 0.0

        content_a = path_a.read_text(encoding="utf-8")
        content_b = path_b.read_text(encoding="utf-8")

        hash_a = hashlib.sha256(content_a.encode("utf-8")).hexdigest()
        hash_b = hashlib.sha256(content_b.encode("utf-8")).hexdigest()

        if hash_a == hash_b:
            return 1.0

        lines_a = set(content_a.splitlines())
        lines_b = set(content_b.splitlines())

        if not lines_a or not lines_b:
            return 0.0

        intersection = lines_a & lines_b
        union = lines_a | lines_b

        return len(intersection) / len(union)

    def cluster_dependencies(self, tasks: list[dict[str, Any]]) -> list[DependencyCluster]:
        clusters: list[DependencyCluster] = []

        for task in tasks:
            task_id = task.get("task_id", "")
            downstream = [o.get("path", "") for o in task.get("downstream_outputs", [])]

            merged = False
            for cluster in clusters:
                if set(downstream) & set(cluster.shared_files):
                    if task_id not in cluster.tasks:
                        cluster.tasks.append(task_id)
                    for f in downstream:
                        if f not in cluster.shared_files:
                            cluster.shared_files.append(f)
                    merged = True
                    break

            if not merged:
                clusters.append(
                    DependencyCluster(
                        cluster_id=f"CLUSTER-{len(clusters) + 1}",
                        tasks=[task_id],
                        shared_files=downstream,
                        cluster_risk="LOW",
                    )
                )

        for cluster in clusters:
            if len(cluster.tasks) > 5:
                cluster.cluster_risk = "CRITICAL"
            elif len(cluster.tasks) > 3:
                cluster.cluster_risk = "HIGH"
            elif len(cluster.tasks) > 1:
                cluster.cluster_risk = "MEDIUM"

        return clusters
