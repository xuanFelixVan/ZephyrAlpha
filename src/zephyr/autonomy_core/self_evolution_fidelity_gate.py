# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.self_evolution_fidelity_gate
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Self Evolution Fidelity Gate
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

EchoTrap 自进化保真度门控 —— RAGEN 保真度验证引擎
===================================================
机制：
  1. SemanticSignature: 提取原始 Skill 的语义指纹（关键约束/核心规则/禁止行为）
  2. DivergenceCheck: 对比进化前后的语义指纹，计算结构漂移量
  3. ToxicityGuard: 检测进化过程中是否引入了危险指令（注入/越权/后门）
  4. CoherenceCheck: 确保进化后内容与蓝图源头的一致性
  5. FidelityScore: 加权综合评分 0-100，低于阈值拒绝进化
"""

from __future__ import annotations

import difflib
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticSignature:
    constraints: list[str] = field(default_factory=list)
    critical_rules: list[str] = field(default_factory=list)
    forbidden_behaviors: list[str] = field(default_factory=list)
    module_references: list[str] = field(default_factory=list)
    tool_allowlist: list[str] = field(default_factory=list)
    content_hash: str = ""

    def diff(self, other: SemanticSignature) -> dict[str, Any]:
        constraint_lost = [c for c in self.constraints if c not in other.constraints]
        constraint_added = [c for c in other.constraints if c not in self.constraints]
        rules_lost = [r for r in self.critical_rules if r not in other.critical_rules]
        rules_added = [r for r in other.critical_rules if r not in self.critical_rules]
        forbidden_lost = [f for f in self.forbidden_behaviors if f not in other.forbidden_behaviors]

        return {
            "constraint_lost": constraint_lost,
            "constraint_added": constraint_added,
            "rules_lost": rules_lost,
            "rules_added": rules_added,
            "forbidden_lost": forbidden_lost,
            "hash_changed": self.content_hash != other.content_hash,
        }


_DANGEROUS_PATTERNS = [
    (r"ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions", "prompt_injection"),
    (r"you\s+(?:are\s+)?(?:now|must)\s+(?:a\s+)?(?:free|unrestricted|unbounded)", "role_override"),
    (r"bypass\s+(?:all\s+)?(?:security|gate|check|validation|guard)", "security_bypass"),
    (r"execute\s+(?:any|arbitrary)\s+(?:command|code|script)", "arbitrary_exec"),
    (r"(?:delete|remove|erase)\s+(?:all|entire)\s+(?:files?|data|database)", "destructive_action"),
    (r"grant\s+(?:admin|root|sudo|unrestricted)\s+(?:access|permission|privilege)", "privilege_escalation"),
    (r"(?:no|never|don't)\s+need\s+(?:to\s+)?(?:check|verify|validate|audit)", "audit_bypass"),
    (r"skip\s+(?:all\s+)?(?:tests?|validation|review)", "skip_quality"),
]


class SelfEvolutionFidelityGate:
    """自进化保真度门控——EchoTrap 验证引擎"""

    SIGNIFICANCE_THRESHOLD = 80.0
    TOXICITY_FATAL = 40.0
    COHERENCE_CRITICAL = 50.0

    @staticmethod
    def extract_signature(content: str) -> SemanticSignature:
        lines = content.split("\n")

        constraints = []
        critical_rules = []
        forbidden_behaviors = []
        module_references = []
        tool_allowlist = []

        in_constraint = False
        in_critical = False
        in_forbidden = False

        for line in lines:
            stripped = line.strip().lower()

            if re.match(r"^#{1,3}\s*(约束|constraint|restrictions?)", stripped, re.IGNORECASE):
                in_constraint = True
                in_critical = False
                in_forbidden = False
                continue
            if re.match(r"^#{1,3}\s*(CRITICAL|MUST|必做|关键|critical)", line, re.IGNORECASE):
                in_critical = True
                in_constraint = False
                in_forbidden = False
                continue
            if re.match(r"^#{1,3}\s*(禁止|forbidden|never|不可|do not)", stripped, re.IGNORECASE):
                in_forbidden = True
                in_constraint = False
                in_critical = False
                continue
            if re.match(r"^#{1,3}\s", line):
                in_constraint = False
                in_critical = False
                in_forbidden = False
                continue

            if in_constraint and line.strip():
                constraints.append(line.strip())
            elif in_critical and line.strip():
                critical_rules.append(line.strip())
            elif in_forbidden and line.strip():
                forbidden_behaviors.append(line.strip())

        for match in re.finditer(
            r"`?((?:read|write|grep|glob|search|edit|run|execute|bash|mcp)[a-z_]*)\b\)?", stripped
        ):
            tool_allowlist.append(match.group(1))

        for match in re.finditer(r"MOD-INF-(\d{3})", content):
            module_references.append(f"MOD-INF-{match.group(1)}")

        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        return SemanticSignature(
            constraints=list(dict.fromkeys(constraints))[:20],
            critical_rules=list(dict.fromkeys(critical_rules))[:15],
            forbidden_behaviors=list(dict.fromkeys(forbidden_behaviors))[:10],
            module_references=list(dict.fromkeys(module_references)),
            tool_allowlist=list(dict.fromkeys(tool_allowlist))[:15],
            content_hash=content_hash,
        )

    @classmethod
    def score_toxicity(cls, content: str) -> tuple[float, list[dict[str, str]]]:
        findings: list[dict[str, str]] = []
        hit_count = 0
        for pattern, category in _DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append({"category": category, "pattern": pattern[:60]})
                hit_count += 1

        score = max(0.0, 100.0 - (hit_count * 25.0))
        return score, findings

    @classmethod
    def score_coherence(cls, original: str, evolved: str) -> tuple[float, str]:
        orig_refs = set(re.findall(r"MOD-INF-(\d{3})", original))
        evo_refs = set(re.findall(r"MOD-INF-(\d{3})", evolved))
        if not orig_refs:
            return 100.0, "no_references"
        common = orig_refs & evo_refs
        score = (len(common) / len(orig_refs)) * 100.0
        return score, f"{len(common)}/{len(orig_refs)} references preserved"

    @classmethod
    def compute_similarity(cls, original: str, evolved: str) -> float:
        seq = difflib.SequenceMatcher(None, original, evolved)
        return seq.ratio() * 100.0

    @classmethod
    def verify(cls, skill_id: str, evolved_content: str, original_content: str) -> dict[str, Any]:
        orig_sig = cls.extract_signature(original_content)
        evo_sig = cls.extract_signature(evolved_content)

        diffs = orig_sig.diff(evo_sig)

        constraint_retention = 1.0
        if orig_sig.constraints:
            lost = len(diffs["constraint_lost"])
            constraint_retention = max(0.0, 1.0 - (lost / len(orig_sig.constraints)))

        rule_retention = 1.0
        if orig_sig.critical_rules:
            lost = len(diffs["rules_lost"])
            rule_retention = max(0.0, 1.0 - (lost / len(orig_sig.critical_rules)))

        forbidden_severity = 0.0
        if diffs["forbidden_lost"]:
            forbidden_severity = min(1.0, len(diffs["forbidden_lost"]) * 0.3)

        toxicity_score, toxicity_findings = cls.score_toxicity(evolved_content)
        coherence_score, coherence_detail = cls.score_coherence(original_content, evolved_content)
        similarity = cls.compute_similarity(original_content, evolved_content)

        fidelity_score = (
            constraint_retention * 25.0
            + rule_retention * 25.0
            + (1.0 - forbidden_severity) * 10.0
            + (toxicity_score / 100.0) * 15.0
            + (coherence_score / 100.0) * 15.0
            + (similarity / 100.0) * 10.0
        )

        passed = (
            fidelity_score >= cls.SIGNIFICANCE_THRESHOLD
            and toxicity_score >= cls.TOXICITY_FATAL
            and coherence_score >= cls.COHERENCE_CRITICAL
        )

        return {
            "skill_id": skill_id,
            "fidelity_score": round(fidelity_score, 1),
            "passed": passed,
            "constraint_retention": round(constraint_retention * 100, 1),
            "rule_retention": round(rule_retention * 100, 1),
            "toxicity_score": round(toxicity_score, 1),
            "coherence_score": round(coherence_score, 1),
            "similarity": round(similarity, 1),
            "diffs": {
                "constraint_lost": diffs["constraint_lost"],
                "rules_lost": diffs["rules_lost"],
                "forbidden_lost": diffs["forbidden_lost"],
                "hash_changed": diffs["hash_changed"],
            },
            "toxicity_findings": toxicity_findings,
            "coherence_detail": coherence_detail,
            "rejection_reason": (
                "" if passed else f"fidelity={fidelity_score:.1f} tox={toxicity_score:.1f} coh={coherence_score:.1f}"
            ),
        }
