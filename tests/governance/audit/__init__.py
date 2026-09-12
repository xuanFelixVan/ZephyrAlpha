# tests/governance/audit

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-13 DEDUP/平铺债批）】
# 本目录 82 个 .py 按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（top12）：
#   - blueprint_* (3 件)
#   - integrity_* (3 件)
#   - reconcile_* (3 件)
#   - runtime_* (3 件)
#   - delegation_* (2 件)
#   - error_* (2 件)
#   - forensic_* (2 件)
#   - gct_* (2 件)
#   - git_* (2 件)
#   - merkle_* (2 件)
#   - tiered_* (2 件)
#   - trust_* (2 件)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
