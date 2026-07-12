# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.conflict_detector
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_conflict_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 冲突检测引擎 — 语义+文本+资源三维冲突检测

检测两个 Agent 提交的变更是否冲突。
方法:
  - 文本层: 行级重叠检测 (line-level overlap)
  - 语义层: 同一函数/类/段落被两个 Agent 同时修改
  - 资源层: 同一文件/锁/DB表被两个 Agent 同时操作

输入: Agent A 和 Agent B 的变更集 (changed_files + changed_symbols)
输出: 冲突列表 + 严重度 + 重叠区域
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConflictSeverity(str, Enum):
    MERGEABLE = "mergeable"
    MODERATE = "moderate"
    SEVERE = "severe"
    BLOCKING = "blocking"


class ConflictType(str, Enum):
    LINE_OVERLAP = "line_overlap"
    SYMBOL_CONFLICT = "symbol_conflict"
    RESOURCE_LOCK = "resource_lock"
    SEMANTIC_DIVERGENCE = "semantic_divergence"


@dataclass
class ChangeRange:
    file_path: str
    start_line: int
    end_line: int
    symbols: list[str] = field(default_factory=list)


@dataclass
class ChangeSet:
    agent_id: str
    files: dict[str, ChangeRange] = field(default_factory=dict)
    locked_resources: list[str] = field(default_factory=list)

    def add_file(self, path: str, start: int, end: int, symbols: list[str] | None = None):
        self.files[path] = ChangeRange(
            file_path=path,
            start_line=start,
            end_line=end,
            symbols=symbols or [],
        )


@dataclass
class Conflict:
    conflict_type: ConflictType
    severity: ConflictSeverity
    agent_a: str
    agent_b: str
    description: str
    file_path: str | None = None
    overlap_start: int | None = None
    overlap_end: int | None = None
    conflicting_symbols: list[str] = field(default_factory=list)


class ConflictDetector:
    """A2A 冲突检测引擎.

    在 Supervisor 调度前运行——检测两个 Agent 的变更集是否存在冲突。
    若存在冲突 -> 交由 Arbitrator 仲裁。
    """

    def __init__(
        self,
        line_overlap_tolerance: int = 0,
        resource_exclusive: bool = True,
    ):
        self._line_overlap_tolerance = line_overlap_tolerance
        self._resource_exclusive = resource_exclusive

    def detect(self, changes_a: ChangeSet, changes_b: ChangeSet) -> list[Conflict]:
        conflicts: list[Conflict] = []

        all_files = set(changes_a.files.keys()) | set(changes_b.files.keys())

        for file_path in all_files:
            range_a = changes_a.files.get(file_path)
            range_b = changes_b.files.get(file_path)

            if range_a is None or range_b is None:
                continue

            overlap_start = max(range_a.start_line, range_b.start_line)
            overlap_end = min(range_a.end_line, range_b.end_line)

            if overlap_end - overlap_start > self._line_overlap_tolerance:
                severity = self._severity_from_overlap(overlap_start, overlap_end, range_a, range_b)

                common_symbols = list(set(range_a.symbols) & set(range_b.symbols))

                if common_symbols:
                    conflicts.append(
                        Conflict(
                            conflict_type=ConflictType.SYMBOL_CONFLICT,
                            severity=ConflictSeverity.BLOCKING,
                            agent_a=changes_a.agent_id,
                            agent_b=changes_b.agent_id,
                            description=f"Both agents modified symbols {common_symbols} in {file_path}",
                            file_path=file_path,
                            conflicting_symbols=common_symbols,
                        )
                    )
                elif severity in (ConflictSeverity.SEVERE, ConflictSeverity.BLOCKING):
                    conflicts.append(
                        Conflict(
                            conflict_type=ConflictType.LINE_OVERLAP,
                            severity=severity,
                            agent_a=changes_a.agent_id,
                            agent_b=changes_b.agent_id,
                            description=f"Line overlap L{overlap_start}-L{overlap_end} in {file_path}",
                            file_path=file_path,
                            overlap_start=overlap_start,
                            overlap_end=overlap_end,
                        )
                    )
                elif range_a.symbols and range_b.symbols:
                    conflicts.append(
                        Conflict(
                            conflict_type=ConflictType.SEMANTIC_DIVERGENCE,
                            severity=ConflictSeverity.MODERATE,
                            agent_a=changes_a.agent_id,
                            agent_b=changes_b.agent_id,
                            description=f"Adjacent symbols in {file_path}: A:{range_a.symbols} vs B:{range_b.symbols}",
                            file_path=file_path,
                        )
                    )

        if self._resource_exclusive:
            locked_a = set(changes_a.locked_resources)
            locked_b = set(changes_b.locked_resources)
            common_locks = locked_a & locked_b
            for resource in common_locks:
                conflicts.append(
                    Conflict(
                        conflict_type=ConflictType.RESOURCE_LOCK,
                        severity=ConflictSeverity.BLOCKING,
                        agent_a=changes_a.agent_id,
                        agent_b=changes_b.agent_id,
                        description=f"Resource lock conflict on '{resource}'",
                    )
                )

        return conflicts

    def has_conflict(self, changes_a: ChangeSet, changes_b: ChangeSet) -> bool:
        return len(self.detect(changes_a, changes_b)) > 0

    def is_blocking(self, changes_a: ChangeSet, changes_b: ChangeSet) -> bool:
        return any(c.severity is ConflictSeverity.BLOCKING for c in self.detect(changes_a, changes_b))

    def _severity_from_overlap(
        self, start: int, end: int, range_a: ChangeRange, range_b: ChangeRange
    ) -> ConflictSeverity:
        overlap_size = end - start
        total_a = range_a.end_line - range_a.start_line or 1
        total_b = range_b.end_line - range_b.start_line or 1
        max_ratio = max(overlap_size / total_a, overlap_size / total_b)

        if max_ratio >= 0.8:
            return ConflictSeverity.BLOCKING
        if max_ratio >= 0.5:
            return ConflictSeverity.SEVERE
        if overlap_size >= 10:
            return ConflictSeverity.MODERATE
        return ConflictSeverity.MERGEABLE

    @staticmethod
    def summary(conflicts: list[Conflict]) -> dict:
        counts: dict[str, int] = {}
        for c in conflicts:
            counts[c.severity.value] = counts.get(c.severity.value, 0) + 1
        return {
            "total_conflicts": len(conflicts),
            "blocking": counts.get("blocking", 0),
            "severe": counts.get("severe", 0),
            "has_blocking": any(c.severity is ConflictSeverity.BLOCKING for c in conflicts),
            "conflicts": [c.description for c in conflicts],
        }
