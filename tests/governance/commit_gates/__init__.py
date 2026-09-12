# tests/governance/commit_gates

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-13 DEDUP/平铺债批）】
# 本目录 100 个 .py 按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（top12）：
#   - capability_* (4 件)
#   - bare_* (3 件)
#   - blueprint_* (3 件)
#   - frontend_* (3 件)
#   - registry_* (3 件)
#   - ch_* (2 件)
#   - depgraph_* (2 件)
#   - domain_* (2 件)
#   - file_* (2 件)
#   - import_* (2 件)
#   - msg_* (2 件)
#   - rule_* (2 件)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
