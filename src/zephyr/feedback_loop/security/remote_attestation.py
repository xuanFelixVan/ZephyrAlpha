# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.security.remote_attestation
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Remote Attestation — v0.15.0 R211

Blindspot: FLE runtime integrity unverifiable remotely; trusted only by self-report.
Risk: R211 — Compromised FLE reports "I'm fine"; no hardware-rooted trust verification.

Mitigation: TPM-based remote attestation with runtime measurement verification.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: remote_attestation.py
# 层: 算法
# - id: A1
#   name_zh: ① RemoteAttestation
#   name_en: RemoteAttestation
#   intro: class RemoteAttestation 源码 L68-L84
#   desc: 公共方法（定义序）: verify, last_verified；源码 L68-L84
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RemoteAttestation
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AttestationReport:
    pcr_values: dict[int, str]
    quote: str
    signature: str
    verified: bool = False


@dataclass
class RemoteAttestation:
    reports: list[AttestationReport] = field(default_factory=list)
    expected_pcr_hashes: dict[int, str] = field(default_factory=dict)
    attestation_required: bool = True

    def verify(self, report: AttestationReport) -> bool:
        for pcr_idx, expected_hash in self.expected_pcr_hashes.items():
            if report.pcr_values.get(pcr_idx, "") != expected_hash:
                report.verified = False
                self.reports.append(report)
                return False
        report.verified = True
        self.reports.append(report)
        return True

    def last_verified(self) -> AttestationReport | None:
        return self.reports[-1] if self.reports else None
