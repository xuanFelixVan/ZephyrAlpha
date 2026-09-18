---
ttl: task_bound
completes_when: 总包对 daily_valuation 行情腿口径与两片段合并授权作出裁定
---

# 申请裁定 req_datagap_01 · daily_valuation 行情腿口径 + 两片段合并授权 + DLQ 因果链

> 车道 `st-ff-datagap-20260918`｜2026-09-18｜禁停等：本件登记后车道继续做下一件。

## 议题 A：`c1_market.daily_valuation` 行情腿列的"无值"表达方式

**背景**：该表是"行情腿 + 估值腿"复合表，但唯一在跑的写者（akshare 百度估值链路）
只产 pe/pb/ps/pcf，9 个行情腿列（open/high/low/close/preclose/volume/amount/turnover/pct_change）
在 DDL 里是 **非 Nullable** 的 Decimal/UInt64，provider 传 None → 落库变 0。

**实测证据（2026-09-18 本车道）**：
`SELECT count(), countIf(toFloat64(close)>0), countIf(toFloat64(amount)>0), countIf(toFloat64(turnover)>0)
FROM c1_market.daily_valuation FINAL` → `259238 / 0 / 0 / 0`（全表零真值行情腿，2026-08-01~09-17）。
根因位：`src/zephyr/data/implementations/akshare_provider.py`
`_fetch_valuation_one_symbol`（注释自述"K线字段填 None；is_st 填 0"）+
`_SQL` 列序含 9 个行情腿列；DDL 列非 Nullable（`SHOW CREATE` 经 system.tables 实测）。
另两处失真：`ps_ttm` 列写入的是"市盈率(静)"（同函数指标映射注释自述）；
`data_source` 因 DEFAULT 恒为 `local_valuation`，而真实写者是 akshare 链路。

**选项**：
- **A1 列改 Nullable**：语义最正确（无值=NULL），代价=DDL 变更（CREATE/ALTER 需 admin 角色）
  + schemas/categories 品类真源同步 + 下游 Decimal 算术需加 NULL 分支。
- **A2 行情腿由 kline_daily 同步行填**：本表语义变成真复合表，代价=新增一条派生链路
  （写者归属与 DAG 依赖需 z-dag 配合），且"行情腿"与该表存在的意义重叠。
- **A3 摘除 9 列**（该表定位为纯估值表）：最干净，但**净删列=注册表净删=Owner 门位**，
  且 api_server 已有按 trade_date/symbol 读该表的消费点（`api_server.py:3954` 只读 pe/pb，不受影响；
  `:3900` 读 is_st）。

**影响面**：一切读 daily_valuation 金额/换手/收盘的场景。已知消费侧在规避
（`api_server.py:206` "价格列全 0 不可用"、`:265` "turnover 全 0 暂无真源→None"），
故**不阻断他人**；但 0 值仍在库里以"合法数值"外观存在，任何新消费方一旦直读即中招
（流通市值权重公式 amount/turnover 已被此坑过一次，见台账 `stock_indicator_circ_mv_outage`）。

**建议**：A1（改 Nullable），并把"非 Nullable 列 + 多写者 + 无 version 列"组合登记为
架构级反模式（本簇 BRK-034 与 N-1 是同一反模式的两个受害者）。A1 需 DDL 变更，非 provider 层能单独定，故申请裁定。

## 议题 B：两份配置片段的合并授权（单一写者制）

- `lanes/datagap_sentinel_yaml_fragment.yaml`：11 张表的业务锚阈值行 + 3 项机制需求
  （dimension_filter / source_min_rows / computed 非空率）。**目标文件 `data_supply_sentinel.yaml`
  归 z-failopen**（该车道正在改 allow_empty，且 reaper 已报其会话遗物被 SALVAGED，写者状态需总包确认）。
- `lanes/datagap_tasks_yaml_fragment.yaml`：8 条任务改道（分红切 akshare / 议息双源并接 /
  金十腿 disabled / index_valuation 重算必跑 / intraday_sector 档期停用等）。
  **目标文件 `tasks.yaml` + `schedule.yaml` 归 z-dag**。
- 本车道按纪律**未直改**任一文件。建议总包按片段原文合入（片段已带实测依据与不合并后果）。

## 议题 C：BRK-054（DLQ / strict_mode）与本簇的因果链——请列入 Owner 切 Max 首件

普查 BRK-054 实测 `config/flags.yaml §flags.schema_validation` =
`strict_mode:false` + `dlq_enabled:false` + "runtime drift 检测未实现"。
本簇两个腐败案例能落库并长期不被发现，正是这三项缺位的直接后果：

1. **BRK-034**：写者①（只产原始列）整窗重灌把写者②的计算列抹成 NULL——
   列级非空率从 ~35% 骤降到 0% 属**结构性 schema/语义违例**，strict_mode+DLQ 在位即会在写入时拦住；
2. **N-1**：9 个行情腿列以 0 值形态存在 259238 行——"0 是合法数值"所以任何计数型哨兵全绿，
   只有"按列非零率 + 出处一致性"的校验能判红；
3. **BRK-035**：撞码判别一旦失效即整组静默丢数据（fetcher 返回的 `_dropped` 计数无人消费）。

**结论（要写进报告与 ledger）**：**不补 DLQ/strict_mode，本簇修完仍会复发**——
本车道落地的只有"写前携带"这一处 provider 级止血，它挡住的是同表多写者互相抹值，
挡不住任何新的整窗重灌语义、列类型放宽或新写者接入。
该施工包归 z-failopen，本车道不建，仅锁定因果关系与三处证据。
