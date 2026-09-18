---
ttl: task_bound
completes_when: 回测引擎 TradeRecord 归因字段落地且 FF-12 多维归因首轮出数
---

# 需求登记 · 回测引擎 `TradeRecord` 归因字段（BRK-045 / id=bt_trade_log_attribution_fields_missing）

> 车道 `st-ff-datagap-20260918` 只做**需求与影响面登记**，不改回测引擎（跨簇，会撞车）。
> 列入 Max 待执行清单。日期 2026-09-18。

## 1. 现状（file:line 与归属）

| 面 | 位置 | 事实 |
|---|---|---|
| 产物 | `data/backtest_artifacts/bt-*.json`（c1_backtest trade_log，60 件） | 台账条目 `bt_trade_log_attribution_fields_missing`（`src/zephyr/data/config/known_data_gaps.yaml:840`）status=**no_source**，gap_type=field_missing |
| 引擎 | `src/zephyr/backtest/**` 的 `TradeRecord`（本车道**未改**，仅指认归属） | 只落 `order_type='market'` 常量、无 `algo_id` 字段 |
| 消费方 | TDM `TDM-F-C3-01` 多维归因（FF-12 绩效归因）、`REG-VALM-001` exec_quality 分桶线 | 拿不到归因维度 → 回测↔实盘同构性无法验证 |
| 归属澄清 | 任务书提到的 z-land 面是 `src/zephyr/ex_core/**` 与 `src/zephyr/pf_alloc/**`；**回测引擎不在其中** | 请总包另派 FF-04/FF-12 面车道，本文件作需求与判据输入 |

## 2. 实测统计（本车道复跑，非沿用台账）

遍历 `data/backtest_artifacts/bt-*.json` 全 60 件的 trade_log：

- 件数 = 60；
- `order_type` 取值集合 = {market}，**无一非 market**；
- `algo_id` **全部为空或字段缺失**。

与台账 2026-09-18 同口径结论一致（本车道按"动手前先实测"纪律复跑确认，此条**仍成立**）。

## 3. 需要加的两个字段（最小充分集）

| 字段 | 类型 | 语义 | 取值域 | 迁移成本 |
|---|---|---|---|---|
| `order_type`（**改语义，不改类型**） | String | 委托类型 | market / limit / b2b（排板）/ stop | 旧值 market 仍合法 → 无 schema 变更，仅语义变宽；历史 60 件不回填 |
| `algo_id`（**新增**） | String（CH 侧 LowCardinality(String)） | 产生该笔的算法实例标识，须与实盘同源命名 | 与实盘执行算法枚举一致（6 个 EXA 算法）；回测路径建议 `backtest:<run_id>:<algo>` | JSON 产物新增可选字段；表侧若建列走 admin 角色 DDL，另批 |

## 4. 谁会消费（逐跳）

1. FF-12 绩效归因引擎（TDM `TDM-F-C3-01` 多维归因）→ 按 algo_id 拆贡献；
2. `REG-VALM-001` exec_quality 分桶（桶内 n>=30 且滑点均值 <=20bp→valid / <=40bp→pending / >40bp→noise），
   分桶脚本 `.runtime/tmp/exp/p6/flash/F03_bucketed_exam_algo.md`；
3. E-L4-05 打板执行专项（排板/限价桶）、E-L4-06 执行算法逐桶 → 真分桶考试（当前不可行，
   只能维持 L4 批全量代理口径 run_id=VAL-20260918-015408，台账 notes 与 lane P6 报告已披露）；
4. 回测↔实盘同构性判据（BRK-077 CC_06 四模式开关的 shadow 模式）→
   无归因维度则 sim↔live divergence 无法按算法分解，转正门缺量化依据。

## 5. 风险与向后兼容

| 风险 | 说明 | 处置建议 |
|---|---|---|
| 占位值造错数 | 若给 `algo_id` 填 'unknown'/'default' 之类占位串，归因引擎会把它当成一个**真实算法桶** → 比缺字段更坏 | **必须 NULL/字段缺失语义**，禁占位串（宁缺毋错，与 R-014 同判据） |
| 历史产物不可回补 | 引擎不产此字段，60 件旧 JSON 无从回填 | 明示"历史不回补"，统计口径以字段落地日为准 |
| 命名空间不同源 | 回测 algo_id 与实盘 algo_id 若两处各自硬编码 → 分桶结果不可比 | 两侧共同引用同一枚举真源（建议进注册表册，禁两处字典） |
| 旧读者兼容 | 已存在的 trade_log 消费方按现有字段读，新增字段应为可选 | 反序列化禁 fail-closed on unknown；缺字段读为 None |
| 门禁连带 | staged .py 的 for 体内出现 write_result 触 CH-BATCH-SIZE 硬拦（本车道 `BufferedWriter` 配方已验证可用） | 回测侧若批量落盘，照 §7 代码红线写法：`BufferedWriter(table, max_rows=N)` + 循环内 `writer.add(fr)` + 循环后 `writer.flush()`，行数读 `writer.total_flushed`/`flush_count` |

## 6. 落地后的验收（映射验收规范 §1 六向）

- ①入口有料：真跑一次含限价/排板委托的回测，产物中 order_type 取值集合 size>=2；
- ③出口有货：落盘后**读盘** `json.loads(saved.read_text())` 与内存值逐位对比
  （本仓教训：`cash_curve` 只随内存 ts 返回而落盘 0 点，测试却全绿）；
- ④下游能取：FF-12 归因引擎给出消费点 `file:line`，且 `scripts/` 里的 import 不算引用；
- ⑤哨兵在岗：归因覆盖率（algo_id 非空率）阈值行；
- ⑥失败会响：把 order_type 改回常量 'market' 或把 algo_id 置空时，测试必须红（变异证据）。
