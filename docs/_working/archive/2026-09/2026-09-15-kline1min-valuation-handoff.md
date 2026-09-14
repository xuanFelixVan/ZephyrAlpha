---
ttl: task_bound
---

# 交接包：kline_1min / daily_valuation 覆盖疑云排查 → 待执行 remediation

> 本文档为**完整自包含交接**，可整段复制粘贴到新对话执行。
> 生成时间：2026-09-15 02:08（排查会话已闭环，本包交出新会话执行 remediation）。

---

## 一、项目背景简介（必读）

`D:\ZephyrAlpha` = 个人量化系统（A 股 + 数字货币，Python + ClickHouse + FastAPI 面板），100% AI 开发。

- **数据总览页（8890）** 提供全库资产审计；CH host = `172.24.30.100`（**禁 localhost 探测**），配置 `config\.env.clickhouse`。
- 读侧协议 `src\zephyr\data\ch_reader.py`（**自动在表名后注 FINAL——禁用表别名**，`FROM t FINAL 别名` 是非法语法）。
- 写侧唯一正门 = provider + `ch_writer.py` / `BufferedWriter`（禁裸 duckdb / 裸 SQL 散落）。
- 当前**多会话并行施工**，工作区脏文件（backtest.js / chainmap* / docs 蓝图等）是其他会话 WIP，**禁碰禁提交**。
- **miniQMT 通道 2026-09-18 券商关停**（迁移工程进行中）；kline_1min 喂料任务（intraday_minute 族）9/17 前仍由 miniQMT 供数——本交接的北交所回补窗口就是 9/17 前。
- CH 只读探针写法：`from zephyr.data import ch_reader as R; R.query(sql)`（样板见 `scripts\data\backfill_lof_minute_history.py` 的 `_q` 函数；账号用 `reader_user/reader_password`，经 `from zephyr.data.ch_config import load_ch_config`）。

---

## 二、本交接的来龙去脉（为什么有这份包）

数据总览 v2 会话做板块指数合成对拍时，发现两个"数据质量问题疑云"，派本次排查。排查**已闭环**（只读、零写库），结论如下，详细报告见第四节路径。

**三疑云定性：**
| # | 疑云 | 定性 | 关键证据 |
|---|------|------|----------|
| ② | kline_1min 覆盖腰斩（515 成分只命中 256） | **证伪** | 近 11 交易日覆盖率恒定 5205–5209 × 241 根，零异常；"515" 是多快照重复计数假象（880825.SH 真实去重成分仅 **260**），命中 256=98.5%，缺 5 只（002870 退市 + 4 只北交所） |
| ②' | （排查新发现）分钟族无北交所 | **真实缺口** | kline_1min/5/15/30/60min 全族 9 开头 = **0 只**；同 capability 日线侧已生效(5549)但分钟线侧未生效(5207) → 342 只北交所缺失 |
| ① | daily_valuation 权重断链 | **部分成立** | 09-10 整日 **0 行**（至今未补）、09-09 部分写入 4875/5558；"0 命中"真因 = `sector_constituent` 代码带后缀 vs `daily_valuation` 无后缀（消费方须 `.split('.')[0]` 归一） |
| ③ | kline_sector_intraday 断供 | **确认** | 09-11 起断供（mootdx 通道死），09-10 半日截断（880825 仅 144/240 根） |

**根因实证（fetch_perf JSONL）**：akshare 全市场估值抓取约 10h/次，D 日数据 D+1 落库；而 `daily_valuation_incremental` 在 09-10/09-14 等日以 `source=mock / rows=0` 空转通过——增量"每日可靠供给"不成立。

---

## 三、⚠️ 新会话待执行的 remediation（P1/P2，已登记 gaps，status=open）

> 以下三项均未完成，须按优先级在新会话推进。**P1/P2 涉及写库（补数据/改代码），须严格走第五节提交纪律与宪法硬规则。**

### P1-a：补 `daily_valuation` 2026-09-10（写库 / backfill）
- 数据源 akshare，全量约 10h/次；D 日数据 D+1 落库属常态。
- 跑完顺带校验 09-09 的 4875/5558 是否需重刷。
- 治理侧（代码改动）：`daily_valuation_incremental` 多次以 `source=mock rows=0` 空转通过却不告警 → 给"增量任务 0 行成功"加告警（同族问题已在 `news_sentiment_window` 登记过）。

### P1-b：排查分钟线族"京市A股未生效"原因（调查 + 可能改代码）
- 同一 capability 声明 `miniqmt_provider._KLINE_CAPABILITIES`（L213-219）日线侧已生效（kline_daily 09-11=5549 含 342 只 9 开头），但分钟线侧未生效（kline_1min 09-14=5207，前缀仅 0/3/6）。
- 查：板块取数路径差异，还是分钟周期下京市A股返回空。
- **窗口：9/17 前**（miniQMT 退役前，是最后能补分钟历史 + 验证治本的窗口）。
- 验证治本：修完后跑一次 `SELECT uniqExact(symbol) FROM c1_market.kline_1min WHERE symbol LIKE '9%'` 应 >0。

### P2：9/17 前回补分钟族北交所历史（五表 × 342 只，写库 / backfill）
- 表：kline_1min / kline_5min / kline_15min / kline_30min / kline_60min。
- 过期（9/18 miniQMT 退役）后 bdpan 无分钟归档 = **永久缺口**。
- 消费侧（方案 J）：合成器须加"成分覆盖率"自检闸门（<98% 标记当日不可用，禁静默产出偏差指数）。

### 对方案 J（板块指数合成器）的硬性约束（消费方施工时遵守）
1. kline_1min 本体健康，可放心吃。
2. 含京市成分的 880/881 板块须显式统计"成分覆盖率"，<98% 直接标记该板块当日不可用。
3. 新管线（桥 tick 合成 ch_tick_kline）接线时**必须显式跑一次 9 开头 symbol 计数**，不能假设 capability 声明 = 实际生效。
4. 代码后缀归一：`sector_constituent`（带后缀）↔ `kline_1min`/`daily_valuation`（无后缀），统一 `.split('.')[0]`。
5. 校准真值窗口最晚 09-10，且须避开半日段（880825 09-10 仅 144/240 根）。

---

## 四、项目必看文件（完整路径，按序读）

1. `D:\ZephyrAlpha\AGENTS.md` —— 项目宪法 L0（冷启动序列 / 十二条硬规则 / 运维红线）
2. `C:\Users\fanzi\.trae-cn\memory\projects\-d-ZephyrAlpha--p2-1c552864b6a6a396cfb0\project_memory.md` —— 项目硬约束（QMT 桥分区 / 提交纪律 / PIT 原则 / Decimal 除法须 toFloat64 等）
3. `D:\ZephyrAlpha\docs\_working\2026-09-08-qmt-bridge-migration-ledger.md` —— miniQMT→文件桥迁移台账（1min 任务族退役语境）
4. `D:\ZephyrAlpha\src\zephyr\data\config\tasks.yaml` —— 任务真源（搜 `intraday_minute` 族 `kline_1min_incremental` / `daily_valuation_incremental`）

---

## 五、本排查工作文件（完整路径，新会话先读结论）

- **报告（被 docs 清理批自动软归档）**：`D:\ZephyrAlpha\docs\_working\archive\2026-09\2026-09-15-kline1min-valuation-coverage-investigation.md`
  - ⚠️ 报告顶部"结案报告 / 待办已闭环"是清理批**关键词扫描自动生成的误标**，忽略它；真实待办看本文第三节与 gaps 登记。
- **缺口登记真源（已加 3 条，status=open）**：`D:\ZephyrAlpha\src\zephyr\data\config\known_data_gaps.yaml`
  - `daily_valuation_2026_09_10_missing`（约 577 行）
  - `kline_minute_no_bse_universe`（约 596 行）
  - `kline_sector_intraday_tdx_dead`（约 615 行）

---

## 六、相关源文件 / 证据（完整路径）

- 读侧协议：`D:\ZephyrAlpha\src\zephyr\data\ch_reader.py`（自动注 FINAL，禁表别名）
- 任务→provider 链路：`D:\ZephyrAlpha\src\zephyr\data\scheduler.py`
- miniQMT capability：`D:\ZephyrAlpha\src\zephyr\data\implementations\miniqmt_provider.py`（L213-219 `_KLINE_CAPABILITIES`；`stock_to_symbol` 去后缀）
- CH 探针样板：`D:\ZephyrAlpha\scripts\data\backfill_lof_minute_history.py`（`_q` 函数）
- 任务运行证据（每日 JSONL，非 CH 表）：目录 `D:\ZephyrAlpha\.runtime\fetch_perf\fetch_perf_YYYYMMDD.jsonl`；写入器 `D:\ZephyrAlpha\src\zephyr\data\fetch_perf_recorder.py`（查 `base_dir` 逻辑）
- CH 账号：`D:\ZephyrAlpha\config\.env.clickhouse`（host=172.24.30.100）

### 涉及表（库 `c1_market`）
| 表 | 关键形态 |
|---|---|
| `kline_1min` | **无 trade_date 列**，时间过滤用 `toDate(trade_time)`；symbol 无后缀；列=trade_time,symbol,open,high,low,close,volume,amount,data_source,ingest_ts |
| `kline_5min` / `kline_15min` / `kline_30min` / `kline_60min` | 同 kline_1min 形态 |
| `daily_valuation` | symbol 无后缀；amount/turnover 是 Decimal，**直接除会撞 scale 错误 Code 69** → 须 `toFloat64(amount)/toFloat64(turnover)`；列 trade_date |
| `kline_sector_intraday` | code 带后缀（如 `880825.SH`）；trade_date 是 DateTime 分钟戳；period='1m' |
| `sector_constituent` | stock_code 带后缀（如 `000007.SZ`）；sector_code 含 `.SH`；**多快照叠加**（按 `update_date` 取最新 + 去后缀）；有一行 `sector_name='880825.SH'` 脏行 |
| `stock_basic` | 基准全市场标的（约 5549，含 342 北交所） |
| `kline_daily` | 日线侧京市A股已生效（09-11=5549，含 342 只 9 开头） |

---

## 七、执行步骤与纪律红线

### 环境前置（每条 python 前）
```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:/usr/bin:/bin:$PATH"
export PYTHONPATH=D:/ZephyrAlpha/src
export PYTHONIOENCODING=utf-8
cd /d/ZephyrAlpha
python --version   # 必须 = 3.12.x（托管 3.13 缺 yaml/numpy，git 正门会崩）
```

### 提交正门（改了 yaml/py 才需要；纯只读排查不需提交）
```bash
# 1) 前置 add + claim
git add <文件清单>
python scripts/git_commit.py --session <你的session> --files "<文件清单,逗号分隔>" --claim-only

# 2) 规则反查留审计（写 yaml/py 必做）
python -c "from zephyr.integration.mcp.rule_discovery_server import RuleDiscoveryServer; RuleDiscoveryServer().discover_applicable_rules(operation='file_write', session_id='<同一session>')"

# 3) 提交（被锁竞争拦截时：加大 --wait 重试，或加 --no-auto-enqueue 同步争锁）
python scripts/git_commit.py --session <同一session> --files "<文件清单>" --message-file <UTF-8消息文件> --allow-non-worktree --adopt-prior-work --allow-tracked-drift --wait 300

# 4) 提交后核实
git log -1 --name-only
```
- **禁裸 `git commit`**、禁 `--no-verify`、禁 `--allow-overlap`（24h 配额已熔断）。
- 锁竞争：`FOREIGN_CHANGE` → 先 `git diff` 核实归属，属正门；循环重试争锁即可。
- git 正门在并发会话下可能挂起（等串行锁），用系统 python 3.12 + 上述 PYTHONPATH；循环重试别用超短 timeout。

### 红线
- 工作区他会话 WIP（backtest.js / chainmap* / docs 蓝图等）**禁碰禁提交**。
- 禁生产数据 `DELETE` / `ALTER`（backfill 走 provider+ch_writer 正门，不裸写）。
- 禁 cron / Timer / sleep-loop（reconciler 须事件触发）。
- `tmp\` 下 `dump_*.tsv` 是事故快照留证，**勿删**。
- 金额/除法：Decimal 列一律 `toFloat64()` 包裹再运算。

### 建议新会话启动顺序
1. 先读第四节两份工作文件（报告 + gaps）掌握结论，再读必看文件（第四节）。
2. 若执行 P1-a/P2 写库：先读懂 `tasks.yaml` 里 `daily_valuation_incremental` / `kline_1min_incremental` 任务定义与 provider 路由，确认补数走哪条 path（避免重复造轮子）。
3. 若执行 P1-b 查因：直接读 `miniqmt_provider.py` L213-219 及 `stock_to_symbol`，对比日线 vs 分钟线的板块取数差异；必要时跑一次 9 开头 symbol 计数验证。
4. 任何写库前先 `git add` + claim + 规则反查，再走正门提交。
