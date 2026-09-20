---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L85: | `data/strategy_intake/c4_deferrals.csv` | 321 条挂起登记（理由码） |
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 16 个，其中判废弃 0、路径漂移 2）+ commit 提及 0 处。
> **路径漂移（非缺失，勿误判）**：`docs/_working/2026-09-14-sim-platform-blueprint.md` 路径漂移→docs/_working/archive/2026-09/2026-09-14-sim-platform-blueprint.md；`scripts/data/backfill_stock_indicator_daily_basic.py` 路径漂移→scripts/backtest/backfill_stock_indicator_daily_basic.py
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# CH 连接统一治本——交接文档（2026-09-14）

> 移交方：st-zcode-c4-20260912（模拟盘平台+估值翻译批）
> 接收方：新会话（基建施工专班）
> 优先级：P1（不阻塞主线但影响所有模块稳定性）

## 一、项目背景（60 秒）

ZephyrAlpha = 个人 A 股量化交易系统，100% AI 开发。数据库 = ClickHouse（行情/策略/治理）+ SQLite（治理元数据）+ PostgreSQL（depgraph）。所有模块通过 `clickhouse_driver.Client` 裸连接或经 `ch_writer`/`ch_config` 读写 CH。当前多个 AI 会话并发施工，每个会话的脚本各自创建 `Client` 连接，无共享连接池，导致连接数不受控、间歇性 `Code: 181` 断连。

## 二、问题根因

| 层 | 现状 | 问题 |
|---|---|---|
| **基础设施** | `DatabaseService.get_clickhouse_conn()` 已有惰性初始化+双重检查锁 | **未被子模块使用**——ch_writer/ch_config 各自维护独立 Client |
| **数据层** | `ch_writer.py` 有自己的 `get_client()` + HTTP 降级 | 每个调用点独立创建 Client，无进程级缓存 |
| **脚本层** | `scripts/backtest/` 下各模块各自 `Client(...)` | 同上；部分已修（_c4_engine/sim_paper_ledger/strategy_screen_query 加了进程内缓存+atexit） |
| **翻译件** | `scripts/backtest/translated/` 35 个文件经 `_c4_engine._q()` | **已修**——_c4_engine 有缓存+atexit |

## 三、治本方案

**统一走 `DatabaseService.get_clickhouse_conn()`**，禁止任何模块自己建裸 `Client`。

### 改造文件清单（按依赖序）

| 序 | 文件完整路径 | 改动 | 模块号 |
|---|---|---|---|
| 1 | `src/zephyr/infrastructure/database_service.py` | 确认 `get_clickhouse_conn()` 返回带 `disconnect()` 的 Client（可能需包装） | MOD-INFRA |
| 2 | `src/zephyr/data/ch_writer.py` | `get_client()` 改为调 `DatabaseService.get_clickhouse_conn()`，保留 HTTP 降级路径 | 已有 |
| 3 | `src/zephyr/data/ch_config.py` | 不改（配置加载层） | — |
| 4 | `scripts/backtest/translated/_c4_engine.py` | `_q()` 改为调 `ch_writer.get_client()`（删除自己的缓存/atexit） | MOD-BT-039 |
| 5 | `scripts/backtest/sim_paper_ledger.py` | 同上 | MOD-BT-099 |
| 6 | `scripts/backtest/sim_platform_journal.py` | 同上 | MOD-BT-090 |
| 7 | `scripts/backtest/sim_deviation_report.py` | 同上 | MOD-BT-092 |
| 8 | `scripts/backtest/sim_governance.py` | 同上 | MOD-BT-140 |
| 9 | `scripts/backtest/strategy_screen_query.py` | 同上 | MOD-BT-078 |
| 10 | `scripts/data/backfill_stock_indicator_daily_basic.py` | **已迁至** `scripts/backtest/backfill_stock_indicator_daily_basic.py` | MOD-BT-080 |

### 已修（无需再改）

| 文件 | 修法 |
|---|---|
| `scripts/backtest/translated/_c4_engine.py` | 进程内单客户端缓存+atexit disconnect |
| `scripts/backtest/sim_paper_ledger.py` | 同上 |
| `scripts/backtest/strategy_screen_query.py` | 同上 |
| `scripts/backtest/sim_deviation_report.py` | 同上 |
| `scripts/backtest/sim_platform_journal.py` | 同上 |

### 需改（仍用裸连接）

| 文件 | 现状 |
|---|---|
| `src/zephyr/data/ch_writer.py` | 自己的 `get_client()` + HTTP 降级——改为调 DatabaseService |
| `scripts/backtest/translated/_c4_engine.py` | 已有缓存但绕过了 ch_writer——改走统一入口 |
| 其余 `sim_*.py` 模块 | 已有缓存但同样绕过 ch_writer |

**注意**：ch_writer 的 HTTP 降级路径（TCP 失败→HTTP API）是独有功能，统一后必须保留。

## 四、"完成"定义

1. 全仓 `grep -rn "clickhouse_driver.Client" --include="*.py" | grep -v database_service | grep -v ch_writer | grep -v test` = 零命中（所有 Client 创建收敛到 DatabaseService）；
2. 测试全过（现有测试 + 新增连接池压力测试）；
3. 多会话并发不再出现间歇性 `Code: 181` 断连。

## 五、纪律提醒

- 按施工 SOP 走（`sop/construction_sop/construction_workflow_sop.md`，路径已可通过 capability_lookup.find("施工") 检索）；
- ch_writer 是热文件——safe_write_text CAS 写入；
- 测试既有用例不得回退（`test_c4_batch_smoke.py` / `test_sim_paper_ledger.py` / `test_sim_platform_journal.py` / `test_sim_deviation_report.py`）；
- **禁止引入新依赖**（连接池用 clickhouse_driver 自带能力+Python atexit，不引第三方库）。

## 六、关联文件

| 文件 | 角色 |
|---|---|
| `docs/_working/2026-09-14-sim-platform-blueprint.md` | 模拟盘平台蓝图（批1-4 全完工） |
| `docs/_working/2026-09-14-sim-partition-discussion.md` | 模拟盘分仓专题讨论材料 |
| `docs/_working/2026-09-13-c5-cluster-differentiation-report.md` | C5 聚类对质报告（含 RSRS 寻路终审） |
| `docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml` | 策略登记册（150+1 条） |
| `docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml` | 模块翻译登记表 |
| `data/strategy_intake/c4_deferrals.csv` | 321 条挂起登记（理由码） |
| `scripts/backtest/strategy_screen_query.py` | 台账查询器（summary/trace/failed/scored） |
