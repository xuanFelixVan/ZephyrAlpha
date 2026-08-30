# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.git_hook_pre_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git Hook预扫描不可跳过;risky_patterns必须匹配
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Git Hook Pre-Scanner — v0.14.0 Git操作Hook预扫描器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: git_hook_pre_scanner.py
# 层: 算法
# - id: A1
#   name_zh: ① GitHookPreScanner
#   name_en: GitHookPreScanner
#   intro: class GitHookPreScanner 源码 L55-L60
#   desc: 公共方法（定义序）: scan_hook, is_safe；源码 L55-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: GitHookPreScanner
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

SUSPICIOUS_HOOK_CONTENT: Final[list] = ["rm -rf", "git push --force", "curl", "wget", "eval"]


class GitHookPreScanner:
    def scan_hook(self, hook_content: str) -> list[str]:
        return [s for s in SUSPICIOUS_HOOK_CONTENT if s in hook_content]

    def is_safe(self, hook_content: str) -> bool:
        return len(self.scan_hook(hook_content)) == 0
