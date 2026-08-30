# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-CFG
# [MODULE] zephyr.factor.core.config_manager
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng; zephyr.factor.core.batch_output; zephyr.factor.core.backpressure
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配置真源为 _config.yaml；改后重启进程即生效
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] yaml 不存在->返回空 dict（开发友好）；子节缺失->返回 {}
# [TESTS] tests/factor/test_config_manager.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_FACTOR core config_manager 子包——core 基础设施模块策略参数加载器。

加载 core/_config.yaml，供 dag_manager / dist_feature_eng / batch_output / backpressure
读取默认参数。所有策略参数集中于此 YAML，代码不硬编码。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, get_section, load_core_config
#   code: __init__.py import L50
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 get_section, load_core_config（共 2 符号）
#   desc: __init__ import L50；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: get_section, load_core_config
#   downstream: zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng; zephyr.fac…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.factor.core.config_manager.loader import get_section, load_core_config

__all__ = ["get_section", "load_core_config"]
