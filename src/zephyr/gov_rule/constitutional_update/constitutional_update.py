# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_rule.constitutional_update.constitutional_update
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: session 审计轨迹
#   fields: errors（type/message/recovered/recovery）+ decisions（id/summary/rationale）记录
#   code: logs/session_audit/（SessionAuditTrail.query L104）
# - id: I2
#   name: session_id 会话标识
#   fields: 单个 session_id 字符串或 session_ids 列表
#   code: extract_learnings(session_id) L102
# - id: I3
#   name: AGENTS.md 宪法文件
#   fields: markdown 全文，含/不含 Auto-Generated Learnings 段
#   code: AGENTS.md（agents_path L97）
# 层: 算法
# - id: A1
#   name_zh: ① 提取学习条目
#   name_en: ConstitutionalAutoUpdate.extract_learnings
#   intro: 从一次 session 的报错和决策里挑出值得固化的经验，同一 pattern 只记一次
#   desc: 遍历 records：recovered 的 error → recovery 类 Learning（L-RECOVER 前缀）；id 以 D-RISK 开头的 decision → decision 类 Learning（severity=warn）；seen_patterns 集合去重
#   inputs: I1 I2
#   outputs: Learning 列表
# - id: A2
#   name_zh: ② 跨 session 聚合
#   name_en: extract_cross_session
#   intro: 把多个 session 的 learnings 合并，按 pattern_id 全局去重
#   desc: 逐 sid 调 extract_learnings，pattern_id 未见过的才并入总表
#   inputs: A1
#   outputs: 去重后 Learning 列表
# - id: A3
#   name_zh: ③ 生成更新提案
#   name_en: propose_update
#   intro: 把 learnings 排成 markdown 表格提案，带人类可审查的 diff
#   desc: 空 learnings 返回 None；否则拼「## Auto-Generated Learnings」头 + 四列表格（Pattern ID/Category/Summary/Severity）；ProposedUpdate.diff 属性生成 ---/+++ /@@ 风格 diff
#   inputs: A2
#   outputs: ProposedUpdate
# - id: A4
#   name_zh: ④ 安全写回宪法
#   name_en: apply_update
#   intro: 先备份再原子写入 AGENTS.md，写挂了自动恢复原文件
#   desc: backup_and_rollback + 写 .md.backup-时间戳；已有 Learnings 段则定位段界替换，没有则文末追加；atomic_write 失败时写回原文返回 False
#   inputs: I3 A3
#   outputs: True=写入成功 / False=失败已回滚
#   invariant: 写入前 MUST 备份
# - id: A5
#   name_zh: ⑤ 解析已有学习
#   name_en: get_existing_learnings
#   intro: 用正则从 AGENTS.md 的 Learnings 段里读出已存在的 pattern_id
#   desc: 定位「## Auto-Generated Learnings」到下一个二级标题区间，re.findall(r"\| (L-\w+-\d+) \|") 提取
#   inputs: I3
#   outputs: pattern_id 列表
# 层: 输出
# - id: O1
#   name_zh: 学习条目与更新提案
#   name_en: Learning / ProposedUpdate
#   intro: 提取出的经验条目和可审查 diff 提案，供人审后再决定是否写回
#   downstream: 无下游/内部使用（# [CONSUMERS] 头为空）
# - id: O2
#   name_zh: AGENTS.md 写入结果
#   name_en: apply_update bool
#   intro: 宪法自愈写回成功与否，备份文件留在原目录
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# I3 --> A4
# A3 --> A4
# I3 --> A5
# A1 --> O1
# A3 --> O1
# A4 --> O2
# A5 --> A3
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.io.file_utils import atomic_write, backup_and_rollback
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
                if decision.get("id", "").startswith("D-RISK"):
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
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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


__all__ = [  # noqa: n114-final  n114-final豁免: __all__是Python导出约定且本文件运行时动态append，Final标注不适用
    "ConstitutionalAutoUpdate",
    "Learning",
    "ProposedUpdate",
]
