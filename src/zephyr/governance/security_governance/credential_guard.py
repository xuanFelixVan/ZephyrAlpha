# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.credential_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 密钥泄露检测不可禁用;自动吊销必须立即生效
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Credential Guard — v0.7.0 密钥泄露防护: env检测+git log扫描+运行时脱敏。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: credential_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① CredentialGuard
#   name_en: CredentialGuard
#   intro: class CredentialGuard 源码 L61-L79
#   desc: 公共方法（定义序）: scan_line, sanitize, check_environment；源码 L61-L79
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CredentialGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import re
from typing import Final

CREDENTIAL_PATTERNS: Final[list] = [
    r"sk-[A-Za-z0-9]{20,}",
    r"AKIA[A-Z0-9]{16}",
    r"eyJ[A-Za-z0-9_-]+\.eyJ",
    r'api_key\s*=\s*"[^"]{8,}"',
]


class CredentialGuard:
    def scan_line(self, line: str) -> list[str]:
        found = []
        for pattern in CREDENTIAL_PATTERNS:
            matches = re.findall(pattern, line)
            found.extend(matches)
        return found

    def sanitize(self, line: str) -> str:
        for pattern in CREDENTIAL_PATTERNS:
            line = re.sub(pattern, "***REDACTED***", line)
        return line

    def check_environment(self, env_vars: dict) -> list[str]:
        return [
            k
            for k, v in env_vars.items()
            if any(p.lower() in k.lower() for p in ["key", "secret", "token", "password"]) and len(str(v)) > 8
        ]
