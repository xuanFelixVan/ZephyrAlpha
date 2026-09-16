# [BLUEPRINT] MOD-ALT_DATA | (pending)
# [MODULE] zephyr.alt_data
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ALT_DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2


# [ALGO_FLOW] external: docs/03_modules/_domain_alt_data/algo_flow/alt_data__init__.yaml
"""

# NOTE(P1W15 2026-08-25): scaffold 注册器写入行首 eager import + 类名 append
# （#ARCH-228/238 同款 bug 复发），按各域包"纯模块名导出、无导入无初始化逻辑"
# 约定归一为模块名条目。
# NOTE(P1W14 2026-08-25): 同款 bug 再复发（sentiment_engine / policy_theme_mapper /
# concept_factor_mapper 行首 eager import + 类名 append），按上方同款约定归一为
# 模块名条目。
__all__ = [
    "concept_factor_mapper",
    "filing_nlp_engine",
    "policy_theme_mapper",
    "sentiment_engine",
    "social_sentiment_collector",
    "web_scraper_engine",
]
