# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.__main__
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.cli
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] re-export cli.main; 支持 python -m zephyr.data
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 透传 cli.main 返回的退出码
# [TESTS] tests/zephyr/data/test_cli.py
# [A_module] module_id=MOD-L00-004-__main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""python -m zephyr.data — 数据源集成器 CLI 入口。

re-export cli.main，等价于 `integrator` 命令。
"""
import sys

from zephyr.data.cli import main


if __name__ == "__main__":
    sys.exit(main())
