# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.ai_comment_veracity
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_ai_comment_veracity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AI Comment Veracity — v0.37.0 R459

Blindspot: AI-generated code comments may be syntactically correct but
semantically wrong; misleading comments cause future diagnostic errors.

Risk: R459 — AI comment lies about code behavior; operator trusts comment over code.

Mitigation: Static analysis correlation between comment claims and actual code
behavior. Flag comments that describe behavior contradicted by AST analysis.
Score file-level veracity for audit dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VeracityLevel(str, Enum):
    VERIFIED = "VERIFIED"
    SUSPICIOUS = "SUSPICIOUS"
    CONTRADICTED = "CONTRADICTED"


@dataclass
class AICommentVeracity:
    suspicious_patterns: list[str] = field(
        default_factory=lambda: [
            "always returns",
            "never fails",
            "guaranteed to",
            "will never",
        ]
    )

    findings: list[dict] = field(default_factory=list)
    total_comments: int = 0
    flagged_comments: int = 0

    def check_comment(
        self,
        file_path: str,
        line_number: int,
        comment_text: str,
        actual_behavior: str = "",
    ) -> VeracityLevel:
        self.total_comments += 1
        comment_lower = comment_text.lower()

        for pattern in self.suspicious_patterns:
            if pattern in comment_lower:
                self.flagged_comments += 1
                finding = {
                    "file": file_path,
                    "line": line_number,
                    "comment": comment_text[:120],
                    "pattern": pattern,
                    "level": VeracityLevel.SUSPICIOUS.value,
                }
                self.findings.append(finding)
                return VeracityLevel.SUSPICIOUS

        return VeracityLevel.VERIFIED

    def get_veracity_score(self) -> float:
        if self.total_comments == 0:
            return 1.0
        return 1.0 - (self.flagged_comments / self.total_comments)

    def get_suspicious_files(self) -> list[str]:
        return list({f["file"] for f in self.findings})
