---
ttl: task_bound
completes_when: 10 项全批或全裁（随战役收官归档）
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-V1-OWNER
---

# Owner 签字单 v1.0（三总包并行战役·10 项，逐项批 a 即生效）

> 全部带默认推荐案；批 b 请写行内替代方案。批文回给任何一个在飞总包会话即登记裁定生效。
> 汇编依据=包④§7 六项+包② A11/A12/估值选型+勘误新增两项（⑨tasks.yaml 门位件挂接/v0.1 丢失项②载体；⑩tick 合成评估/P1-3 Owner 门）——全项目合并去重后 10 项，无重复无遗漏。

| # | 事项 | 推荐案（批 a 即采） | 影响线/波次 |
|---|---|---|---|
| ① | 尸体表/备份污染表处置（包④W1=包②A11 同物，35.4G；清单 17 张 R1 §5 vs 12 张包④，执行日实测仲裁） | a=逐表 export Parquet 双副本（F+G）→行数 verify→DROP（etf 5 张 tz_bak 保留至修复后月度复盘再清） | 乙 W1（独占窗+Owner 在场） |
| ② | 1970 假日期 18 表 43.6 万行（A12，大头 restricted_shares 34.3 万；convertible_bond_list 1,054 行未登记先补册） | a=PIT 关死（登记 known_data_gaps）+补真值排 backlog | 乙 W-并入 |
| ③ | 估值 P0 修法（裁定#379 推荐：A1 三选一+A2 配套） | a=version 列单写者（A1）+行情腿同步修（A2 价格腿自 kline_daily 回填）+交易日 gate+0 行告警随批 | 甲 W1（即刻可做无门位半） |
| ④ | vhdx 压缩复决+热层 150G 冗余定案（包④ W6） | a=季度压缩机制化+按 150G 留冗余 | 乙 W6（全局冻结+Owner 在场） |
| ⑤ | INV-RET-002 契约修订（"进冷层必须手动触发"→自动化三步走 shadow→半自动→全自动；INFRA-STORE-002/LOG-OPS-001 同步） | a=三步走（shadow 起算=批文日） | 乙（滚动归档 reconciler） |
| ⑥ | offsite 异地副本形式 | a=月度拔 G 盘轮换（体量大于上云，成本零） | 乙 W4/W7 |
| ⑦ | db_dumps 版本化保留天数 | a=14 天轮转 | 乙 W5 |
| ⑧ | 批次排期（波次网络 00_master_plan_v1_0 §6 确认） | a=甲丙即刻（甲 P0 无门位半先行）+乙 W2 闪断窗先行+W1 签字后连夜独占窗+W3 周末+W4 次周末+W6 Owner 在场+研报删 ≥10-18 | 三线 |
| ⑨ | tasks.yaml 门位件挂接（甲 R13 stock_daily_basic 每日增量+A9 哨兵日历 diff 检查器挂载） | a=批（两挂接随甲 W3/W4 落地，改动随裁定登记） | 甲 W3/W4 |
| ⑩ | tick 09-17 永久缺口处置（P1-3） | a=只登记 known_data_gaps 留痕，不做 kline_1min 合成近似（合成需 data_source=synth 标记，如需另批 b） | 甲 W3 |

——汇编：st-unified-plan-20260920（2026-09-20，v1.0 重制班）；裁定承载=#378（勘误采纳框架）+#379（排程裁定含③推荐案）。
