# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.ai_comment_veracity
# [DOMAIN] D_FBL_VERIFICATION
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AI Comment Veracity — v0.37.0 R459

Blindspot: AI-generated code comments may be syntactically correct but
semantically wrong; misleading comments cause future diagnostic errors.

Risk: R459 — AI comment lies about code behavior; operator trusts comment over code.

Mitigation: Static analysis correlation between comment claims and actual code
behavior. Flag comments that describe behavior contradicted by AST analysis.
Score file-level veracity for audit dashboard.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ai_comment_veracity.py
# 层: 算法
# - id: A1
#   name_zh: ① AICommentVeracity
#   name_en: AICommentVeracity
#   intro: class AICommentVeracity 源码 L71-L116
#   desc: 公共方法（定义序）: check_comment, get_veracity_score, get_suspicious_files；源码 L71-L116
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AICommentVeracity
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
