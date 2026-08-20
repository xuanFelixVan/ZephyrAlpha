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
"""D_FACTOR core config_manager 子包——core 基础设施模块策略参数加载器。

加载 core/_config.yaml，供 dag_manager / dist_feature_eng / batch_output / backpressure
读取默认参数。所有策略参数集中于此 YAML，代码不硬编码。
"""

from __future__ import annotations

from zephyr.factor.core.config_manager.loader import get_section, load_core_config

__all__ = ["get_section", "load_core_config"]
