# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.security_config_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 安全配置扫描不可跳过;数据库/云/API配置必须检查
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Security Config Scanner — v0.13.0 缺失安全配置扫描器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: security_config_scanner.py
# 层: 算法
# - id: A1
#   name_zh: ① SecurityConfigScanner
#   name_en: SecurityConfigScanner
#   intro: class SecurityConfigScanner 源码 L59-L65
#   desc: 公共方法（定义序）: scan；源码 L59-L65
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SecurityConfigScanner
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

REQUIRED_CONFIGS: Final[dict] = {
    "limits.yaml": "resource_limits",
    "cors.yaml": "cors_whitelist",
    "secrets.yaml": "api_keys",
}


class SecurityConfigScanner:
    def scan(self, existing_files: list[str]) -> dict:
        missing = {}
        for req_file, desc in REQUIRED_CONFIGS.items():
            if not any(req_file in f for f in existing_files):
                missing[req_file] = desc
        return {"missing_count": len(missing), "missing": missing, "complete": len(missing) == 0}
