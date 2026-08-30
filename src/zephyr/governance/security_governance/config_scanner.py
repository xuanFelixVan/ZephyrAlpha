# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.config_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] AI配置注入扫描不可禁用;恶意配置必须检测
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Config Scanner — v0.9.0 AI配置文件注入扫描器: 检测AI修改的配置+注入攻击。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: config_scanner.py
# 层: 算法
# - id: A1
#   name_zh: ① ConfigScanner
#   name_en: ConfigScanner
#   intro: class ConfigScanner 源码 L51-L79
#   desc: 公共方法（定义序）: baseline, set_baseline, detect_modification, check_injection；源码 L51-L79
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ConfigScanner
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ConfigScanner:
    def __init__(self):
        self._baseline: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def baseline(self) -> dict[str, str]:
        """只读：baseline（Stage 4 公共化）。"""
        return self._baseline

    @baseline.setter
    def baseline(self, value):
        """写入：baseline（Stage 4 公共化）。"""
        self._baseline = value

    def set_baseline(self, filepath: str, content_hash: str):
        self._baseline[filepath] = content_hash

    def detect_modification(self, filepath: str, current_hash: str) -> bool:
        baseline = self._baseline.get(filepath)
        return baseline is not None and baseline != current_hash

    def check_injection(self, content: str) -> list[str]:
        suspicious = []
        if "{{" in content and "}}" in content:
            suspicious.append("template_injection")
        if "eval(" in content:
            suspicious.append("code_injection")
        return suspicious
