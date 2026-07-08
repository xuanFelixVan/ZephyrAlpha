# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.semantic_diff
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_semantic_diff | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 语义差异引擎 — 结构感知的 Agent 间差异检测

超越 line-level diff——识别函数/类/段落级别的语义差异:
  - 同一函数被 Agent A 加日志、Agent B 改算法 -> 语义冲突
  - 同一类 Agent A 加方法、Agent B 删方法 -> 架构冲突
  - 同一段落 Agent A 改措辞、Agent B 删段落 -> 上下文冲突

输出: SemanticDiffReport — 冲突区域 + 类型 + 重合度评分
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from enum import Enum


class SemanticDiffType(str, Enum):
    FUNCTION_MODIFIED = "function_modified"
    CLASS_STRUCTURE = "class_structure"
    PARAGRAPH_REWRITTEN = "paragraph_rewritten"
    PARAGRAPH_DELETED = "paragraph_deleted"
    IMPORT_CHANGED = "import_changed"


@dataclass
class SemanticRegion:
    name: str
    start_line: int
    end_line: int
    content: str = ""
    region_type: str = "function"


@dataclass
class SemanticDiffEntry:
    region_name: str
    region_type: str
    diff_type: SemanticDiffType
    agent_a_change: str
    agent_b_change: str
    overlap_ratio: float
    conflict_risk: float


@dataclass
class SemanticDiffReport:
    agent_a_id: str
    agent_b_id: str
    file_path: str
    entries: list[SemanticDiffEntry] = field(default_factory=list)

    @property
    def has_conflict(self) -> bool:
        return any(e.conflict_risk > 0.5 for e in self.entries)

    @property
    def max_conflict_risk(self) -> float:
        if not self.entries:
            return 0.0
        return max(e.conflict_risk for e in self.entries)


class SemanticDiffEngine:
    """结构感知的语义差异引擎.

    比较两个 Agent 对同一文件的修改——提取函数/类/段落级别的差异.
    """

    _SYMBOL_PATTERNS = [
        ("def ", "function"),
        ("class ", "class"),
        ("async def ", "function"),
    ]

    def diff(
        self,
        agent_a_id: str,
        agent_b_id: str,
        regions_a: list[SemanticRegion],
        regions_b: list[SemanticRegion],
        file_path: str = "",
    ) -> SemanticDiffReport:
        report = SemanticDiffReport(agent_a_id=agent_a_id, agent_b_id=agent_b_id, file_path=file_path)

        names_a = {r.name: r for r in regions_a}
        names_b = {r.name: r for r in regions_b}
        common_names = set(names_a.keys()) & set(names_b.keys())
        a_only = set(names_a.keys()) - set(names_b.keys())
        b_only = set(names_b.keys()) - set(names_a.keys())

        for name in common_names:
            ra = names_a[name]
            rb = names_b[name]

            overlap_ratio = self._overlap_ratio(ra, rb)
            content_similarity = difflib.SequenceMatcher(None, ra.content, rb.content).ratio()

            conflict_risk = (1.0 - content_similarity) * 0.7 + (1.0 - overlap_ratio) * 0.3
            conflict_risk = min(1.0, max(0.0, conflict_risk))

            diff_type = SemanticDiffType.FUNCTION_MODIFIED
            if content_similarity < 0.5 or overlap_ratio < 0.3:
                diff_type = SemanticDiffType.FUNCTION_MODIFIED

            report.entries.append(
                SemanticDiffEntry(
                    region_name=name,
                    region_type=ra.region_type,
                    diff_type=diff_type,
                    agent_a_change=f"A: L{ra.start_line}-L{ra.end_line} ({len(ra.content)} chars)",
                    agent_b_change=f"B: L{rb.start_line}-L{rb.end_line} ({len(rb.content)} chars)",
                    overlap_ratio=overlap_ratio,
                    conflict_risk=conflict_risk,
                )
            )

        for name in a_only:
            report.entries.append(
                SemanticDiffEntry(
                    region_name=name,
                    region_type=names_a[name].region_type,
                    diff_type=SemanticDiffType.PARAGRAPH_DELETED,
                    agent_a_change=f"A only: L{names_a[name].start_line}-L{names_a[name].end_line}",
                    agent_b_change="B: absent",
                    overlap_ratio=0.0,
                    conflict_risk=0.8,
                )
            )

        for name in b_only:
            report.entries.append(
                SemanticDiffEntry(
                    region_name=name,
                    region_type=names_b[name].region_type,
                    diff_type=SemanticDiffType.PARAGRAPH_REWRITTEN,
                    agent_a_change="A: absent",
                    agent_b_change=f"B only: L{names_b[name].start_line}-L{names_b[name].end_line}",
                    overlap_ratio=0.0,
                    conflict_risk=0.6,
                )
            )

        return report

    def extract_regions(self, source: str) -> list[SemanticRegion]:
        lines = source.split("\n")
        regions: list[SemanticRegion] = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            for prefix, rtype in self._SYMBOL_PATTERNS:
                if stripped.startswith(prefix):
                    name = self._extract_name(stripped, prefix)
                    start = i + 1

                    end = self._find_region_end(lines, i)
                    content = "\n".join(lines[i : end + 1])

                    regions.append(
                        SemanticRegion(
                            name=name,
                            start_line=start,
                            end_line=end + 1,
                            content=content,
                            region_type=rtype,
                        )
                    )
                    break

            if stripped.startswith("# ") or stripped.startswith("## "):
                name = stripped.lstrip("# ").strip()[:60]
                regions.append(
                    SemanticRegion(
                        name=f"section:{name}",
                        start_line=i + 1,
                        end_line=i + 1,
                        region_type="heading",
                    )
                )

        return regions

    def _overlap_ratio(self, ra: SemanticRegion, rb: SemanticRegion) -> float:
        overlap_start = max(ra.start_line, rb.start_line)
        overlap_end = min(ra.end_line, rb.end_line)
        if overlap_end <= overlap_start:
            return 0.0
        overlap = overlap_end - overlap_start
        union = max(ra.end_line, rb.end_line) - min(ra.start_line, rb.start_line)
        if union <= 0:
            return 0.0
        return overlap / union

    def _extract_name(self, line: str, prefix: str) -> str:
        after = line[len(prefix) :].strip()
        name = after.split("(")[0].split(":")[0].strip()
        return name

    def _find_region_end(self, lines: list[str], start: int) -> int:
        indent = len(lines[start]) - len(lines[start].lstrip()) if lines[start].strip() else 0
        end = start + 1
        while end < len(lines):
            line = lines[end]
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= indent and line.strip():
                    break
            end += 1
        return min(end - 1, len(lines) - 1)

    @staticmethod
    def _classify(condition: bool) -> SemanticDiffType:
        return SemanticDiffType.FUNCTION_MODIFIED
