# [BLUEPRINT] SRC-025 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.constitutional_update.constitutional_update
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.shared.file_utils; zephyr.shared.session_audit
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
# [A_module] module_id=MOD-GOV_constitutional_update | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
constitutional_update.py —— 宪法自愈（Phase 14 | 盲点 B27）

痛点修复：AGENTS.md 是静态的——AI 无法把"犯错-学到"写回宪法。
SessionAuditTrail 记录了每次 session 的 errors/decisions/patterns，
ConstitutionalAutoUpdate 从中提取 learnings -> 提议 -> 安全地写回 AGENTS.md。

设计对标：
  - Claude Code CLAUDE.md auto-evolution: Agent 自我更新指南
  - Self-Improving Agent: 从历史错误中学习并固化规则
  - Git pre-commit safety: 写入前备份 + dry-run 验证

AI 施工约定：
  - AGENTS.md 写入前 MUST 备份——backup_and_rollback 集成
  - 每次 extract_learnings() MUST 去重——同一 pattern 只记录一次
  - propose_update() MUST 输出人类可审查的 diff——再 apply_update()

SSoT: DOM-GOV-001 §12 盲点 B27
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.utils.file_utils import atomic_write, backup_and_rollback
from zephyr.shared.session.session_audit import SessionAuditTrail


@dataclass
class Learning:
    """单条学习——从 SessionAuditTrail 中提取的错误/决策模式。"""

    pattern_id: str
    category: str
    summary: str
    source_session: str
    extracted_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    severity: str = "info"
    proposed_rule: str = ""


@dataclass
class ProposedUpdate:
    """宪法更新提案——供人类审查的 diff。"""

    section: str
    original_lines: list[str]
    new_lines: list[str]
    rationale: str
    learnings: list[Learning] = field(default_factory=list)

    @property
    def diff(self) -> str:
        lines: list[str] = []
        lines.append(f"--- a/AGENTS.md (section: {self.section})")
        lines.append(f"+++ b/AGENTS.md (section: {self.section})")
        lines.append(f"@@ Rationale: {self.rationale}")
        for i, orig in enumerate(self.original_lines):
            lines.append(f"-{orig}")
        for i, new in enumerate(self.new_lines):
            lines.append(f"+{new}")
        return "\n".join(lines)


class ConstitutionalAutoUpdate:
    """宪法自愈引擎——从 session 记录中提取 learnings 并安全更新 AGENTS.md。

    Usage::

        auto = ConstitutionalAutoUpdate(agents_path="AGENTS.md")
        learnings = auto.extract_learnings(session_id="session-20260507-001")
        proposal = auto.propose_update(learnings)
        if proposal:
            auto.apply_update(proposal)
    """

    def __init__(self, agents_path: str = "AGENTS.md", audit_dir: str = "logs/session_audit/"):
        self.agents_path = Path(agents_path)
        self.audit_dir = audit_dir
        self._trail = SessionAuditTrail(audit_dir=audit_dir)

    def extract_learnings(self, session_id: str) -> list[Learning]:
        """从指定 session 的审计轨迹中提取 learnings。"""
        records = self._trail.query(session_id)
        if not records:
            return []

        learnings: list[Learning] = []
        seen_patterns: set[str] = set()

        for record in records:
            for error in record.get("errors", []):
                error_type = error.get("type", "UnknownError")
                message = error.get("message", "")

                if error.get("recovered"):
                    pattern_id = f"L-RECOVER-{session_id}-{len(learnings):03d}"
                    l = Learning(
                        pattern_id=pattern_id,
                        category="recovery",
                        summary=f"Recovered from {error_type}: {message[:100]}",
                        source_session=session_id,
                        proposed_rule=f"// On {error_type}: attempt {error.get('recovery', 'standard recovery')}",
                    )
                    if l.pattern_id not in seen_patterns:
                        learnings.append(l)
                        seen_patterns.add(l.pattern_id)

            for decision in record.get("decisions", []):
                if decision.get("id", "").startswith("D_RISK"):
                    pattern_id = f"L-DEC-{session_id}-{len(learnings):03d}"
                    l = Learning(
                        pattern_id=pattern_id,
                        category="decision",
                        summary=f"Decision {decision['id']}: {decision.get('summary', '')[:100]}",
                        source_session=session_id,
                        severity="warn",
                        proposed_rule=f"// Risk decision pattern: {decision.get('rationale', '')[:100]}",
                    )
                    if l.pattern_id not in seen_patterns:
                        learnings.append(l)
                        seen_patterns.add(l.pattern_id)

        return learnings

    def extract_cross_session(self, session_ids: list[str]) -> list[Learning]:
        """从多个 session 中提取 learnings，自动去重。"""
        all_learnings: list[Learning] = []
        seen_patterns: set[str] = set()

        for sid in session_ids:
            for l in self.extract_learnings(sid):
                if l.pattern_id not in seen_patterns:
                    all_learnings.append(l)
                    seen_patterns.add(l.pattern_id)

        return all_learnings

    def propose_update(self, learnings: list[Learning]) -> ProposedUpdate | None:
        """基于 learnings 生成 AGENTS.md 更新提案。"""
        if not learnings:
            return None

        new_rules: list[str] = []
        for l in learnings:
            new_rules.append(f"| {l.pattern_id} | {l.category} | {l.summary} | {l.severity} |")

        header = "\n## Auto-Generated Learnings (from ConstitutionalAutoUpdate)\n"
        header += "> 以下规则由 AI 从 session 审计轨迹中自动提取，供人类审查。\n\n"
        header += "| Pattern ID | Category | Summary | Severity |\n"
        header += "|---|---|---|---|\n"

        content = header + "\n".join(new_rules) + "\n"

        return ProposedUpdate(
            section="Auto-Generated Learnings",
            original_lines=[],
            new_lines=content.split("\n"),
            rationale=f"{len(learnings)} learnings extracted from cross-session audit trail",
            learnings=learnings,
        )

    def apply_update(self, proposal: ProposedUpdate) -> bool:
        """安全地将提案写入 AGENTS.md——先备份再写入。"""
        if not self.agents_path.exists():
            return False

        original_content = self.agents_path.read_text(encoding="utf-8")

        backup_path = self.agents_path.with_suffix(f".md.backup-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}")
        backup_and_rollback(str(self.agents_path))
        backup_path.write_text(original_content, encoding="utf-8")

        if "## Auto-Generated Learnings" in original_content:
            section_start = original_content.find("## Auto-Generated Learnings")
            next_section = original_content.find("\n## ", section_start + 10)
            if next_section == -1:
                next_section = len(original_content)

            new_content = (
                original_content[:section_start]
                + "\n".join(proposal.new_lines)
                + "\n"
                + original_content[next_section:]
            )
        else:
            new_content = original_content.rstrip() + "\n\n" + "\n".join(proposal.new_lines) + "\n"

        try:
            atomic_write(str(self.agents_path), new_content)
            return True
        except Exception:
            self.agents_path.write_text(original_content, encoding="utf-8")
            return False

    def get_existing_learnings(self) -> list[str]:
        """解析 AGENTS.md 中已有的 auto-generated learnings。"""
        if not self.agents_path.exists():
            return []

        content = self.agents_path.read_text(encoding="utf-8")
        section_start = content.find("## Auto-Generated Learnings")
        if section_start == -1:
            return []

        next_section = content.find("\n## ", section_start + 10)
        if next_section == -1:
            next_section = len(content)

        section = content[section_start:next_section]
        pattern_ids = re.findall(r"\| (L-\w+-\d+) \|", section)
        return pattern_ids


__all__ = [
    "ConstitutionalAutoUpdate",
    "Learning",
    "ProposedUpdate",
]
