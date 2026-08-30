# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.__main__
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.cli
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] re-export cli.main; 支持 python -m zephyr.data
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 透传 cli.main 返回的退出码
# [TESTS] tests/zephyr/data/test_cli.py
# [A_module] module_id=MOD-GOV-main | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
python -m zephyr.data — 数据源集成器 CLI 入口。

re-export cli.main，等价于 `integrator` 命令。

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
#   desc: 源码 L1-L54；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import sys

from zephyr.data.cli import main

if __name__ == "__main__":
    sys.exit(main())
