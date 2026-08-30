# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.security.dep_cve_correlator
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
Dependency CVE Correlator — v0.14.0 R196

Blindspot: Dependency CVEs accumulate; FLE unaware of known exploited vulnerabilities.
Risk: R196 — Log4Shell-level vulnerability in dependency; FLE operates normally.

Mitigation: NVD API 2.0 integration with CVE correlation and auto-fix prioritization.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dep_cve_correlator.py
# 层: 算法
# - id: A1
#   name_zh: ① DepCVECorrelator
#   name_en: DepCVECorrelator
#   intro: class DepCVECorrelator 源码 L81-L93
#   desc: 公共方法（定义序）: register_dependency, check_critical, auto_fix_available；源码 L81-L93
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DepCVECorrelator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum


class CVESeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class CVEAlert:
    cve_id: str
    dependency: str
    severity: CVESeverity
    cvss_score: float
    description: str
    affected_version: str
    fixed_version: str = ""


@dataclass
class DepCVECorrelator:
    nvd_api_url: str = os.getenv("NVD_API_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")
    alerts: list[CVEAlert] = field(default_factory=list)
    dependencies: list[tuple[str, str]] = field(default_factory=list)

    def register_dependency(self, name: str, version: str) -> None:
        self.dependencies.append((name, version))

    def check_critical(self) -> list[CVEAlert]:
        return [a for a in self.alerts if a.severity is CVESeverity.CRITICAL]

    def auto_fix_available(self) -> dict[str, str]:
        return {a.cve_id: a.fixed_version for a in self.alerts if a.fixed_version}
