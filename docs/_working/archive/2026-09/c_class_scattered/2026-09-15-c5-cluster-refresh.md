---
ttl: task_bound
---

# C5 聚类复检刷新报告（2026-09-15 夜班）

> 数据源=c1_backtest.strategy_screen（verdict=translated_c4，22 件估值/市值族 + canonical 三只 OOS-only 行）。
> 方法=因子主导+参数形状聚类；结论只做**簇首标记与 redundant 建议**，台账只增不改，取舍执行归后续批次。

## 0. 总结论

1. **全族无一具备 sim 晋级资格**：IS 2019-2023 窗口 22 件中 4 件正 Sharpe，OOS 2024-2026 全部转负（含 4 件 decay≥0.84 的风格反转件）。
2. **小市值成长门族的 IS 有效性=风格β非α**：三只 +0.79~+0.88 在 OOS 全崩（-0.97/-1.00/-1.12），与 2024 年小微风格反转一致；不建议以 IS 成绩晋级任何生命周期。
3. canonical 三只（VAL-PE/PB/DIV-HIGH）IS 行缺位（首批只落了 OOS 行）——如需完整族谱，后续班补跑 IS 批（--only valuation）。

## 1. 簇划分与簇首

| 簇 | 成员（IS Sharpe） | 簇首 | redundant 建议 |
|---|---|---|---|
| 小市值成长门 | 9519cb55d6b7(+0.876) / b1fb7e2246dd(+0.824) / 79ae77fb3af7(+0.792) / 0319395c57a7(+0.418，偏价值门边界件) | 9519cb55d6b7 | 无（三强件 OOS 崩塌后簇级放弃） |
| 破净高 ROA 孪生 | 6ba459329476(-0.215) / a016c519e8bd(-0.215，同参克隆) | 6ba459329476（在先） | **a016c519e8bd 标 redundant**（参数全同，双行仅存证） |
| 低 PB 排序 | VAL-PB-LOWTURN-035(-0.203) / VAL-WIZ-CITICS-020(-0.569) / VAL-PB-LOW-020(canonical 无 IS 行) | VAL-PB-LOWTURN-035 | CITICS 与簇首参数近似（不同源策略保留存证） |
| 高股息 | VAL-DIV-STEADY-005(-0.089) / VAL-DIV-NOPEG-020(-0.346) / VAL-DIV-PRETTY50-010(-2.2) / VAL-DIV-HIGH-020(canonical 无 IS 行) | VAL-DIV-STEADY-005 | PRETTY50=高换手反例存证（周频全A 成本吞噬样本） |
| 大市值 | ab4dc295d8eb(-0.523) / 5e3284032a17(-1.3) | ab4dc295d8eb | 无（参数不同频次不同） |
| 成长门宽池 | 4da841c734ae(-0.592) / 38cceabf3946(-0.683) / a5ac9cc45ab3(-1.018) / 3238a5ce80c8(-1.591) | 4da841c734ae | 38cceabf3946 保真度最低（加速语义无承载），后续簇内加权时降权 |
| 价值门混合 | VAL-WIZ-VALUE1-020(-0.181) / b1ab2a40225a(-0.586) / bb0b9f37ce93(-0.755) / 751983843b3f(-1.236) | VAL-WIZ-VALUE1-020 | 无（门组合各异构） |

## 2. 工具化裁定

不新建常驻聚类工具（规范预算净零：cluster_id 列留批测工具域，一次性分析以本报告交付；
台账=唯一真源，本报告所有数字可由 scored 查询复现）。

## 3. 后续

- decay_watch（蓝图批 4）上线后，本报告的 redundant/簇首建议作为 lifecycle 流转建议的输入。
- canonical 三只 IS 行补齐后本报告 §1 表相应行补注。
