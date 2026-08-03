# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_and_decisions/panorama/generator_auto_trigger_pilot.md | §
# [MODULE] scripts.governance.git_hooks
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] scripts.governance.git_hooks.post_commit_regen_yaml (静态导入入口); scripts.governance.verify_generator_paths (静态导入)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 包标记——使 git_hooks 成为可导入 Python 包（post_commit_regen_yaml 等 git hook 脚本的包入口）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS]
# [A_module] module_id=MOD-GOV-git_hooks-pkg | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""git_hooks 包标记——post_commit_regen_yaml 等 git hook 脚本的 Python 包入口。

新建于 2026-08-03（IMPORT-INTEGRITY 治本）：verify_generator_paths.py 将动态
``importlib.import_module("post_commit_regen_yaml")`` 改为静态
``from scripts.governance.git_hooks import post_commit_regen_yaml``，
需本 __init__.py 使 git_hooks 成为可导入 Python 包（消除 sys.path hack + 动态导入隐患）。
"""
