---
ttl: task_bound
---

# 2026-09-17 清洁审计报告（Sharpe2 决赛准备战·分包C③）

- 审计子代理: st-sharpe2c-20260917。**本报告只定性、只建议，未执行任何清理/删除/改名**；一切破坏性操作=待 Owner 批准。
- 基线: `fe8fce25b7`（2026-09-17）；CH 行数为当日实查（只读）。
- 方法: git ls-files 模式扫描 + 未追踪文件系统扫描 + CH system.tables/逐表 count+range + 引用面 grep（src/scripts/config/registry）+ config 全量 51 件引用计数（超出抽样 30 件要求，做了全查）。

---

## 1 仓库文件垃圾

### 1.1 git 追踪树：干净
`git ls-files` 全量匹配 bak/tzbak/old/dup/orig 模式（排除 dedup/redup 误配）：**0 件**。追踪树无备份文件残留。

### 1.2 未追踪垃圾件（11 件大件 ≈ 205 MB）

| 文件 | 大小 | 定性 | 风险 | 建议 |
|---|---|---|---|---|
| `data/audit_trail/events.jsonl.bak_20260916_gwa_forensic`（+.sha256） | 85.2 MB | 2026-09-16 GW 取证快照（当晚生成） | 中 | 决赛取证期保留，赛后归档冷存储（待 Owner 批准） |
| `data/backup/stock_indicator_circmv_20260916/integrator_progress.db.bak` | 32.7 MB | 09-16 集成器修复备份 | 中 | 主表健康确认后退役（待 Owner） |
| `data/integrator_progress.db.bak_20260909b` / `..._20260909c` | 28.9 MB ×2 | **同字节数（28,282,304）疑似逐字节重复** | 低 | 纯重复，三连备份 b/c 二选一保留即可（待 Owner） |
| `data/integrator_progress.db.bak_20260909` | 28.9 MB | 09-09 修复备份 | 低 | 同上，修复已完成 8 天 |
| `data/audit_trail/events.jsonl.bak_20260526` | 21.1 MB | 5 月底审计日志备份（3.5 个月未动） | 低 | 归档或删（待 Owner） |
| `data/vector_db/chroma.sqlite3.bak.20260628` / `.wwp20260628` | 1.2 MB ×2 | 6 月底向量库双备份 | 低 | 删（待 Owner） |
| `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml.bak_pre_one_question` | 1.07 MB | 注册表手工备份——**git 历史已是真备份**，违"静态清单禁手工维护"精神 | 低 | 删（待 Owner；git log 可回溯） |
| `.trae/documents/_algo_flow_script_backup/pre-commit-config.yaml.bak` | 77 KB | 脚本目录残留备份 | 低 | 删（待 Owner） |

### 1.3 CAS 临时文件残留：110 件 / 15.3 MB（面大量广，本次最大宗）

`.yaml_<8位随机>.tmp` 点前缀文件（safe_write_text CAS 写的崩溃残留）：
- `docs/01_policies_and_standards/_registry/catalogs/` **100 件**（rule_catalog_registry 34 件、ruling_registry 15 件、registry_master_index 14 件、gate_registry 3 件…）
- `config/` 6 件（trading_decision_map ×6）
- `data/` 3 件、`data/telemetry/` 1 件
风险：**低**（临时件，非真源；但 100+ 残留说明 CAS 清理路径经常没走到 finally）。建议：决赛后跑既有 `scripts/ops/cleanup_runtime_tmp_residue.py` 类机制统一清（待 Owner 批准）；治本方向=safe_write_text 崩溃残留的自清逻辑。

另有零星：`data/governance/watchdog_state.json.64804.tmp`、`data/.metrics_prom_*.tmp` ×2、`data/telemetry/.watchdog_heartbeat_*.tmp` —— 同类，低。

## 2 CH 孤儿/备份表（22 张逐表实查）

主表健康佐证：kline_1min max=2026-09-16（14.8 亿行）、tick_data max=2026-09-16（88.2 亿行）、kline_5min max=2026-09-16 15:00（2.93 亿行）、kline_daily_hfq 2026-09-11 日已去重（5,206 行 vs 备份 5,207）、news_data max=2026-09-17 —— **2026-09-14/15 时区大修复均已完成，救援备份普遍进入"可退役"状态**。

### 2.1 空壳表（0 行）—— 10 张，低风险

`kline_15min_tzbak2_20260914`、`kline_15min_tzbak_20260914`、`kline_1min_tzbak2_20260914`、`kline_30min_tzbak2_20260914`、`kline_30min_tzbak_20260914`、`kline_5min_tzbak3_20260914`、`kline_5min_tzbak4_20260914`、`kline_60min_tzbak2_20260914`、`kline_60min_tzbak_20260914`、`crypto_kline_daily_bak_okxshell`
→ DROP 无数据损失（待 Owner 批准）。

### 2.2 有数据备份表 —— 12 张，≈6,860 万行

| 表 | 行数 | 数据范围 | 引用面 | 定性 | 风险 |
|---|---|---|---|---|---|
| `c1_market.kline_1min_tzbak_20260914` | 36,194,235 | 2026-06-01..07-15 | **0 引用**；主表健康到 09-16 | 修复已完成可退役 | 低 |
| `c1_market.kline_daily_bak_256` | 9,669,695 | ≤2026-08-21 | `api_server.py:1447`（仪表盘表标签"日 K 备份（256）"） | 老备份被前端展示；先摘标签再退役 | 中 |
| `c3_fundamental.news_data_corrupt_20260828` | 8,040,882 | — | rebuild_news_data.py（RENAME 保留观察目标）+ api_server.py:1481（前端"归档"展示） | 修复源归档，属"刻意保留观察" | 中 |
| `c3_fundamental.news_data_pre_tz2_20260828` | 7,872,827 | — | rebuild_news_data_tz2.py + api_server.py:1482（同上） | 同上 | 中 |
| `c1_market.kline_5min_tzbak_20260914` | 4,456,056 | — | repair_kline5min_tz_deprecated_update_key.py:40（回滚锚） | 修复完成；保留至决赛后退役 | 中 |
| `c1_market.auction_book_limit_bak_20260908` | 1,911,474 | 2026-07-21..09-03 | **该名字唯一副本**（主名 `auction_book_limit` 不存在，活表为 `auction_book`/`auction_snapshot`）；全仓无任何 `auction_book_limit` 消费代码 | 疑似弃用变体，但唯一副本——**需 Owner 裁定是否还要该变体** | 中 |
| `c1_market.tick_data_tzbak_20260914` | 507,700 | 09-09..09-10 | wipe_tick3days.py:31,48 + p0_tick_backfill.py:38（回滚锚注释） | 修复完成；回滚保险期保留 | 中 |
| `c1_market.kline_daily_hfq_bak_20260915dup` | 5,207 | 仅 2026-09-11 | 0 引用；主表已去重（5,206） | 去重前救援快照，使命已完成 | 低 |
| `c3_fundamental.balance_sheet_bak_1970clean_20260914` | 2,395 | — | 0 引用 | 1970 清洗修复救援备份，可退役 | 低 |
| `c3_fundamental.cashflow_statement_bak_1970clean_20260914` | 2,402 | — | 0 引用 | 同上 | 低 |
| `c3_fundamental.financial_indicator_bak_1970clean_20260914` | 2,585 | — | 0 引用 | 同上 | 低 |
| `c3_fundamental.income_statement_bak_1970clean_20260914` | 2,401 | — | 0 引用 | 同上 | 低 |

汇总：**高 0 / 中 6（kline_daily_bak_256、news×2、5min_tzbak、tick_tzbak、auction_bak）/ 低 16（10 空壳+6 有数据）**。所有 DROP/归档均为破坏性操作=**待 Owner 批准**；建议执行窗口：低风险件决赛前安静期清理，中风险件决赛后统一处置（auction_bak 需先裁定）。

## 3 死配置抽查（config/*.yaml 全量 51 件，超抽样要求）

引用计数法：src+scripts .py 直接引用数 + 全仓 yaml/ps1/注册表引用数（排除自引用）。

- **疑似死配置 4 件（零源码消费，仅注册表翻译/资产条目引用）**：
  | 配置 | src 引用 | 全仓引用 | 引用性质 | 风险 |
  |---|---|---|---|---|
  | `config/ai_context_policy.yaml` | 0 | 1 | 仅 module_translation_registry 翻译条目 | 中（需考证：可能经动态路径加载） |
  | `config/crypto_top50_usdt.yaml` | 0 | 2 | 仅 data_asset_registry / capability_canonical_file_registry 登记 | 中（加密数据源配置，可能由集成器动态拼路径消费——**判死前必查 data 集成器运行日志**） |
  | `config/error_budget_config.yaml` | 0 | 1 | 仅翻译条目 | 中 |
  | `config/owner_offline_protocol.yaml` | 0 | 1 | 仅翻译条目 | 中 |
- 其余 **47 件均有真实消费方**（top：flags 123、capabilities 113、immutable_core 74、asset_inventory 37、trading_decision_map 20、trigger_router 17、risk_params 10、capacity_slo 9、alert_rules 8…）。
- 结论：config 面无高风险死件；4 件疑似件**只登记不删除**，转 Owner 考证清单。

## 4 docs/_working 与 .runtime 残留

- `docs/_working/**.md`：323 件，314 件带 ttl 字段、**316 件 task_bound**（181+135 两种写法，本身即是双写漂移证据）；最早 date=2026-09-04（13 天前）。task_bound 件应随任务收口归档，现全部滞留原位——**中低风险**（量大但有 git 历史、无覆盖风险）。建议：决赛后按 ttl 机械清点归档（顺带修 ttl 双写）。
- `.runtime/sessions/`：138 个会话目录，**111 个 mtime>24h（超 staging TTL 候选）、103 个 >7 天**。风险：中——可能有死会话 stale claim（宪法 §2.7 处置通道已有）；清理须走 reaper/lock 机制而非手删（待工具链收口，不代执行）。

## 5 总规模速览

| 类别 | 高风险 | 中风险 | 低风险 |
|---|---|---|---|
| 文件垃圾 | 0 | 2 件（forensic bak、backup/db.bak） | 9 件 + 110 件 CAS tmp |
| CH 备份表 | 0 张 | 6 张 | 16 张（含 10 空壳） |
| 死配置 | 0 | 4 件疑似 | 0 |
| _working/.runtime | 0 | sessions 111 个过期候选 | task_bound md 316 件 |

**执行窗口建议**：决赛前只做零风险宣示性清理（10 张空壳表 DROP、110 件 CAS tmp、纯重复 db bak 二选一——均待 Owner 批准）；其余全部推到决赛后窗口。本代理未执行其中任何一项。
