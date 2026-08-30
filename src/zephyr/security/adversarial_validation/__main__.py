# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §10
# [MODULE] zephyr.security.adversarial_validation.__main__
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.cli
# [CONSUMERS] End users; CI/CD
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] python -m zephyr.security.adversarial_validation is the ONLY CLI entry
# [MODIFY-GUARD] Changes MUST delegate to cli.main()
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SystemExit from cli.main()
# [TESTS] None
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __main__.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: __main__.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L51；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: End users; CI/CD
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.security.adversarial_validation.cli import main

if __name__ == "__main__":
    main()
