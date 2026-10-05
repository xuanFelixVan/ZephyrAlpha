---
ttl: task_bound
---

# L-A 收敛线作业簿（重建版，全文存档=代理 transcript agent_5a9d0158）

决定性证据：现役 SQL 消费方仅两处——逆势榜（counter_trend_board.py L75-80）与贡献拆解（index_contribution_decomposer.py L70-76），均单日读取纯分钟收益/比值口径、无 data_source 过滤、走 FINAL——**绝对点位与跨日连续性零依赖**。J 腿（synth_board_minute）：level=prev_close×Σw·p(t)/Σw·p(t0) 跨日链式，已三断（09-14 口径孤日/09-23 人工断/09-30 排班 0 行=强依赖 t-1 日K 管线脆弱源）；1m/580 板；校准行业 corr 0.995+。resample 判死：kline_sector_880 全表仅 1d。

裁定：**方案甲**——新任务（internal_eqw 五周期 727 板，vs 真 tdx RMS 1.4bps）为收敛终点；J 计划任务 S12 不注销转 --dry-run 留观；施工必修=tdx 真值保护（R2 PASS）+回补清场 delete_where 非 tdx 旧行；哨兵 tdx 腿重指+册内同表双 category_id 归一（已施工）。
