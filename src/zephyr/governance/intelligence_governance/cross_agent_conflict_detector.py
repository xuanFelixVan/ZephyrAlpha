# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.cross_agent_conflict_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
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
# [A_module] module_id=MOD-INF_cross_agent_conflict_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CrossAgentConflictDetector — 多 Agent 并发冲突检测。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B128

两个 AI agent 同时修改同一文件 -> 检测冲突 -> 仲裁 -> 串行化。
双写入检测：同一文件被不同 session_id 同时修改 -> ConflictResolution。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class ConflictReport:
    file_path: str
    agent_a: str
    agent_b: str
    has_conflict: bool
    resolution: str
    timestamp_utc: str


class CrossAgentConflictDetector:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def detect_conflicts(self) -> list[ConflictReport]:
        reports: list[ConflictReport] = []

        all_uncommitted = self._get_all_uncommitted_files()
        if not all_uncommitted:
            return reports

        modified_by_agent: dict[str, set[str]] = {}
        for f in all_uncommitted:
            author = self._get_most_recent_author(f)
            if author:
                if author not in modified_by_agent:
                    modified_by_agent[author] = set()
                modified_by_agent[author].add(f)

        agents = list(modified_by_agent.keys())
        if len(agents) <= 1:
            return reports

        for f in all_uncommitted:
            authors = set()
            for agent, files in modified_by_agent.items():
                if f in files:
                    authors.add(agent)
            if len(authors) > 1:
                agent_list = list(authors)
                reports.append(
                    ConflictReport(
                        file_path=f,
                        agent_a=agent_list[0],
                        agent_b=agent_list[1] if len(agent_list) > 1 else "",
                        has_conflict=True,
                        resolution="SERIALIZE",
                        timestamp_utc=datetime.now(UTC).isoformat(),
                    )
                )

        return reports

    def resolve_conflicts(self, reports: list[ConflictReport]) -> list[ConflictReport]:
        for report in reports:
            if report.has_conflict:
                try:
                    self._run_git(["add", report.file_path])
                except Exception as e:
                    logger.warning("suppressed error in cross_agent_conflict_detector", exc_info=True)
        return reports

    def _get_all_uncommitted_files(self) -> list[str]:
        try:
            mod = self._run_git(["diff", "--name-only", "HEAD"])
            staged = self._run_git(["diff", "--cached", "--name-only"])
            files = [f for f in mod.split("\n") if f] + [f for f in staged.split("\n") if f]
            return list(set(files))
        except Exception:
            return []

    def _get_most_recent_author(self, file_path: str) -> str:
        try:
            result = self._run_git(["log", "-1", "--format=%ae", "--", file_path])
            return result.strip()
        except Exception:
            return ""

    def _run_git(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout
        except Exception:
            return ""
