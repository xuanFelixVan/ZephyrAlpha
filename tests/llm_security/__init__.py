# [A_test] module_id: MOD-GOV_init | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
# [BLUEPRINT] MOD-TEST-337 | tests/llm_security/__init__.py | §
# [TTL] task_bound

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-13 DEDUP/平铺债批）】
# 本目录 63 个 .py 按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（top12）：
#   - llm_* (9 件)
#   - security_* (4 件)
#   - ai_* (2 件)
#   - dep_* (2 件)
#   - hallucination_* (2 件)
#   - input_* (2 件)
#   - l5_* (2 件)
#   - l6_* (2 件)
#   - l7_* (2 件)
#   - process_* (2 件)
#   - adversarial_* (1 件)
#   - batch_* (1 件)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
