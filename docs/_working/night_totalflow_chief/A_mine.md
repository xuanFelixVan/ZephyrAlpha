---
ttl: task_bound
---

# L-A 收敛线作业簿（重建版，代理全文存档=agent_5a9d0158 transcript）

决定性证据：现役 SQL 消费仅两处（counter_trend_board.py L75-80/index_contribution_decomposer.py L70-76），均单日读取纯分钟收益口径、无 data_source 过滤、走 FINAL——绝对点位与跨日连续性零依赖。J 腿跨日链式三断（09-14 孤日/09-23 人工断/09-30 排班 0 行=强依赖 t-1 日K 管线）。resample 判死（kline_sector_880 全表仅 1d）。

裁定甲：internal_eqw 为收敛终点（vs 真 tdx RMS 1.4bps/五周期/727 板 PIT/6 测绿）；J 计划任务 S12 不注销转 --dry-run 留观；施工必修=tdx 真值保护（R2 PASS）+回补清场 delete_where 非 tdx 旧行；品类双注册归一；哨兵 tdx 腿重指。
