# [A_test] module_id: SRC-TST-0115 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
# [BLUEPRINT] MOD-TEST-272 | tests/governance/__init__.py | §
# [TTL] task_bound

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-13 DEDUP/平铺债批）】
# 本目录 67 个 .py 按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（top12）：
#   - apply_* (5 件)
#   - generate_* (5 件)
#   - check_* (4 件)
#   - battle_* (3 件)
#   - commit_* (3 件)
#   - architecture_* (2 件)
#   - audit_* (2 件)
#   - post_* (2 件)
#   - registry_* (2 件)
#   - run_* (2 件)
#   - sync_* (2 件)
#   - conftest_* (1 件)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
