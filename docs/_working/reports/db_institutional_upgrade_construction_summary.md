---
ttl: task_bound
---
# 数据库机构级升级建设 · 施工总结报告

- **任务规格**：`.runtime/working_archive/1784837317/db_institutional_upgrade_task_spec.md`
- **报告日期**：2026-07-25
- **审查基线**：2026-07-22 审查 81.3% B+（audit_03 64 项清单）
- **收尾评分**：62.0/64 A+（audit_03_remediation_summary.md）
- **本报告范围**：P0→P2 全条目处置结果 + Wave 1 Schema 真源回写专项

---

## 0. 总览

| 维度 | 基线（2026-07-22） | 收尾（2026-07-25） |
|------|--------------------|--------------------|
| audit_03 总分 | 81.3% B+ | **96.9% A+**（62/64） |
| 已完成项数 | — | 67 项 |
| 遗留 ⚠️ 项 | — | 2 项（5.8 单节点 HA / 7.7 异地副本，均用户裁定接受） |
| schemas/categories DDL 真源 | 10/101 | **26/101**（含 Wave 1 新增 8 张 c3 表） |
| Schema 漂移校验工具 | 无 | `scripts/ch/verify_schema_truth.py`（治本） |

**Wave 1 专项（本会话产物，commit `d6ae260754`）**：
- 8 张 c3 表 DDL-as-Code 真源回写 → `verify_schema_truth.py` 校验 **零漂移**
- 治本校验器 `verify_schema_truth.py`（支持 `--table` / `--quiet` / `--output`，退出码可接入 CI 门禁）
- 全量漂移证据留证：`wave1_schema_drift_report_20260725.md`（26 表 / 10 漂移，作为 Wave 2 输入）

---

## 1. P0 回测正确性修复（#ARCH-CH-021）

| 项 | 处置 | 证据 / 理由 |
|----|------|-------------|
| **P0-1** 幸存者偏差 | ✅ 已修 | commit `469d3c2ceb`/`989617d112`：stock_list 改造为 SCD-2（list_status + delist_date + valid_from/valid_to），接入 stock_list_delisted capability，policy 收敛 |
| **P0-2** tick 数据缺口 | ⚠️ 部分（数据永久丢失已接受；**预防机制未实装**） | `p0_2_tick_gap_diagnosis.md`：QMT 服务器仅保留<30 天 tick，2026-06 数据永久丢失已接受。**预防机制仅"建议"未实装**——日级 market-type 覆盖检查未做。**遗留**：登记改期，触发条件=实盘立项或下次 tick 缺口事件 |
| **P0-3** option_iv_surface 排序键 | ✅ 已修 | commit `6ed0e20940`：排序键加 option_type，备份后重建+迁移对账完成 |
| **P0-4** 质量门有壳无芯 | ⚠️ 部分 | `quality_gate.py` 仍为 30 行 re-export 包装器（真源在 `zephyr.gov_enforcement.rule_enforcement.quality_gate`）。OHLC 逻辑/涨跌幅/缺口/复权四条门禁的实装与 ch_writer 写入路径接入**未完成**。**遗留**：登记改期，触发条件=backtest 域质量回归或 P0-5 PIT 推进时一并实装 |
| **P0-5** 财报 PIT 化 | ✅ 已修 | commit `6a8ecf1522`/`ae07879e03`/`66a9db9d0e`：按 announce_date 建立 point-in-time 查询能力，与 pit_manager.py 三公理对齐 |
| **P0-6** 18 张 SCD 表时点版本化 | ⚠️ 部分 | commit `56f066e620`：4 张确认（stock_list/index_weight/sector_list/sector_meta）。**其余 14 张无 DDL 真源未确认**——需 Wave 2 真源回写后逐表核验。**遗留**：并入 Wave 2 |
| **P0-7** index_quote 生命周期真源冲突 | ✅ 已修 | commit `6ed0e20940`/`1d5a7e4aae`：对齐为永久保留，全库 lifecycle 冲突排查完成 |
| **P0-8** c3 八表 ReplacingMergeTree 迁移 | ✅ DB 已迁移 + **Wave 1 真源回写完成** | DB 迁移在 audit 早期完成；**本会话 commit `d6ae260754` 完成 8 张表 DDL-as-Code 真源回写**（analyst_forecast / disclosure_plan / equity_pledge_detail / industry_class_suppl / restricted_shares / rights_issue / share_change / share_unlock），`verify_schema_truth.py` 校验零漂移 |

**P0 小结**：8 项中 5 项已修、3 项部分（P0-2 预防/P0-4 门禁实装/P0-6 14 表真源），均登记改期触发条件。

---

## 2. P1 A 组 Schema 治理（#ARCH-CH-022）

| 项 | 处置 | 证据 / 理由 |
|----|------|-------------|
| **A1** ingest_ts 全覆盖 | ⚠️ 部分 | commit `d41695431c`：行情表补齐 ingest_ts（audit 1.7 ⚠️→✅）。**Wave 1 漂移报告暴露 7 张表 DB 有 ingest_ts 但真源无**（auction_snapshot/auction_book/futures_position/futures_term_structure/index_quote/option_iv_surface/sector_snapshot）——真源回写未跟上。**遗留**：Wave 2 真源补 ingest_ts 列 |
| **A2** DDL-as-Code 真源扩面 | ⚠️ 部分（10→26） | Wave 1 新增 8 张 c3 表，总真源数 26/101。**遗留**：剩余 75 张表真源回写，按 Wave 2/N 推进 |
| **A3** kline_daily 三处漂移对齐 | ✅ 已修 | `verify_schema_truth.py` 校验 `c1_market.kline_daily` OK |
| **A4** 分钟 K 线族 15 表族内对齐 | ❌ 改期 | schemas/categories/ 无任何 minute-kline schema 文件。**理由**：当前回测不依赖分钟 K 线族，优先级低于 c3 主表。**触发条件**：分钟策略实盘立项 |
| **A5** 财务表 Float64→Decimal | ✅ 已修 | commit `cf3dbe3034`/`f5ce5ffb58`：财务三表 53 字段迁移至 Decimal(18,2/4)，#ARCH-CH-026 |
| **A6** 时区防线 DateTime→DateTime64(3,'Asia/Shanghai') | ✅ 已修 | commit `7479954c0f`/`ba1c52282d`：全库时区标准化，AGENTS.md 时区铁律登记 |
| **A7** 复权体系补原始价层 | ⚠️ 部分 | adj_factor Decimal(18,8) 已做；**原始价层 raw OHLC 未找到**。**遗留**：登记改期，触发条件=复权回测质量回归 |
| **A8** 行情表补 currency 列 | ❌ 改期 | `market_tick.py` / `market_kline_daily.py` 真源均无 currency 列。**理由**：当前回测仅 A 股，港美股摄取未启动。**触发条件**：港美股回测需求立项 |

**A 组小结**：8 项中 4 项已修、3 项部分、2 项改期。

---

## 3. P1 B 组管线韧性（#ARCH-DATA-PIPELINE-001）

| 项 | 处置 | 证据 / 理由 |
|----|------|-------------|
| **B1** fallback_sources 覆盖 8→≥50% | ✅ 已修 | commit `26b40adcd7`：3%→72%（audit 3.6/4.7 ⚠️→✅） |
| **B2** RUNNING>24h 任务治理 | ⚠️ 部分 | `scheduler.py:307` 启动时 reap_stale_runs(max_age_hours=24) 已实装；**自动重置+告警不完整**——运行中每小时 reap 阈值 6h 已配，但告警通道接入未验证。**遗留**：并入 B7 告警通道验证 |
| **B3** error_classifier 规则扩充 | ✅ 已修 | commit `6877257401`：akshare 接口漂移 / xtquant 断连归类完成 |
| **B4** task_id 重复消除 | ✅ 已修 | commit `6877257401`：kline_us_daily_incremental 去重 |
| **B5** l2_tick 表/任务对齐 | ⚠️ 部分 | commit `4fc17e03ae`：`_has_l2` AttributeError 修复 + l2_tick_snapshot disabled flag。**建表/摘除任务未确认**——目前以 disabled 暂搁。**遗留**：登记改期，触发条件=L2 数据需求 |
| **B6** 告警通道实装 | ✅ 已修 | commit `d1806af65e`：飞书 webhook + SMTP 邮件触达（#ARCH-CH-023，audit 8.3） |
| **B7** 空表漏检修复 | ✅ 已修 | commit `6877257401`：阈值为 0 的表显式"应空"白名单机制 |
| **B8** cls/eastmoney_news 登记进 data_sources_registry | ❌ 未做 | `architecture_model/data/data_sources_registry.yaml` 中无 cls/eastmoney_news 条目。**遗留**：登记改期，触发条件=新闻因子接入 |

**B 组小结**：8 项中 5 项已修、2 项部分、1 项改期。

---

## 4. P1 C 组治理与灾备（#ARCH-DR-BACKUP-001）

| 项 | 处置 | 证据 / 理由 |
|----|------|-------------|
| **C1** dr_policy.yaml 登记 RTO/RPO | ✅ 已修 | commit `1d5a7e4aae`：DR 策略 + TTL 声明对齐（audit 5.5/6.5/7.5） |
| **C2** lifecycle hot_90d 落地 CH TTL | ✅ 已修 | commit `1d5a7e4aae`：声明与 CH TTL 二选一闭环 |
| **C3** 备份恢复演练 + 容量评估 | ⚠️ 部分 | `scripts/ch/_recovery_drill.py` 脚本已建（2026-07-24）。**无执行验证记录 + 容量评估方案未确认**。**遗留**：登记改期，触发条件=下次 restic 备份完成后人工触发演练 |

**C 组小结**：3 项中 2 项已修、1 项部分。

---

## 5. P2 性能与工程卫生

| 项 | 处置 | 证据 / 理由 |
|----|------|-------------|
| **P2-1** 物化视图/Projection 评估 | ❌ 改期 | **理由**：回测期查询路径未达性能瓶颈。**触发条件**：查询 P95 > 500ms |
| **P2-2** tick 排序键 market_type 前缀评估 | ❌ 改期 | **理由**：改造需走 P0 级备份流程，当前无单票裁剪性能诉求。**触发条件**：单票回测延迟敏感场景 |
| **P2-3** 240 处硬编码表名替换 | ⚠️ 部分 | `table_registry.py` 已建。**未全量清扫**——240 处硬编码散落各处。**遗留**：登记改期，按模块分批替换 |
| **P2-4** redundant_source 接线或降级决议 | ⚠️ 部分 | `src/zephyr/data/redundant_source/__init__.py` 4 组件齐全（heartbeat_monitor/source_switcher/sqlite_fallback/recovery），状态 production。**仅被 tick_subscriber 可选接入**，未接线主链路。**遗留**：登记降级决议——保留可选接入，主链路接入触发条件=实盘立项 |
| **P2-5** pyproject.toml 补声明 | ✅ 已修 | `pyproject.toml:80-81`：clickhouse-driver>=0.2.6,<1.0.0 / baostock>=0.8.8,<0.9.0 均已声明 |
| **P2-6** kline_daily 残留脏数据清理 | ✅ 已修 | 1970-01-01 symbol 空行走三步验证清理完成 |

**P2 小结**：6 项中 2 项已修、2 项部分、2 项改期。

---

## 6. Wave 1 Schema 真源回写专项（本会话产物）

### 6.1 病根（第一性原理）

audit_01 实测 101 张表中 87 张"无代码侧真源（仅存在于 CH 实例）"。P0-8 八表迁移等变更直接 ALTER 了 DB 却未回写 `schemas/categories/` 真源，制造"DB 改了、真源没改"的漂移债务——**100% AI 开发场景下 AI 无法可靠维护不在代码里的 schema，是幻觉/漂移根源**（#ARCH-CH-025）。

### 6.2 治本方案

**先用证据把漂移全量暴露，再逐表回写**：

1. **建校验器** `scripts/ch/verify_schema_truth.py`
   - 对比 `schemas/categories/*.py` 的 `*_DDL` 真源与 `system.tables/system.columns`
   - 暴露列/类型/引擎/排序键漂移
   - 引擎词提取（`_engine_token`）、键归一化（`_norm_key`）解决误报
   - 退出码 0=零漂移 / 1=有漂移 / 2=CH不可达，可接入 CI 门禁
   - 支持 `--table` / `--quiet` / `--output`（markdown 报告，带 `ttl: task_bound` frontmatter）

2. **回写 8 张 c3 表真源**（基于 system.tables/system.columns 实测结构转录）
   - `fundamental_analyst_forecast.py` / `fundamental_disclosure_plan.py` / `fundamental_equity_pledge_detail.py`
   - `fundamental_industry_class_suppl.py` / `fundamental_restricted_shares.py` / `fundamental_rights_issue.py`
   - `fundamental_share_change.py` / `fundamental_share_unlock.py`

3. **creation_tokens 登记**：9 个新文件已登记于 `capability_canonical_file_registry.yaml`（commit `cb71d3be78`）

### 6.3 校验结果（commit `d6ae260754`）

```
校验 26 张表真源，发现 10 处漂移。

=== 漂移明细 ===
  - [cross_validation_log] 真源有定义但 DB 中不存在
  - [auction_snapshot] 列 'ingest_ts' DB 有但真源无
  - [auction_book] 列 'ingest_ts' DB 有但真源无
  - [futures_position] 列 'ingest_ts' DB 有但真源无
  - [futures_term_structure] 列 'ingest_ts' DB 有但真源无
  - [index_quote] 列 'ingest_ts' DB 有但真源无
  - [index_weight] 列 'index_code' DB 有但真源无
  - [option_iv_surface] 列 'ingest_ts' DB 有但真源无
  - [sector_snapshot] 列 'ingest_ts' DB 有但真源无
  - [tick_data] 列 'recorded_time' 真源有但 DB 无
```

**8 张 c3 表零漂移 ✓**（Wave 1 目标达成）。10 处漂移作为 Wave 2 输入。

### 6.4 漂移分类与 Wave 2 路线

| 漂移类型 | 表数 | Wave 2 处置 |
|----------|------|-------------|
| `ingest_ts` 列 DB 有真源无 | 7 | 真源 DDL 补 ingest_ts 列（A1 任务延伸） |
| `index_code` 列 DB 有真源无 | 1 | 真源 DDL 补 index_code 列 |
| `recorded_time` 列真源有 DB 无 | 1 | 核验 DB 实际列名（可能为 `timestamp`），对齐真源 |
| 真源有定义但 DB 未建表 | 1 | `cross_validation_log`：建表决策（是否真需要此表） |

---

## 7. 验收对照（audit_03 64 项清单）

| 维度 | 基线 | 收尾 |
|------|------|------|
| 总分 | 81.3% B+ | **96.9% A+**（62/64） |
| 已完成项 | — | 67 项 |
| 遗留 ⚠️ | — | 2 项（均用户裁定接受） |

**2 项遗留 ⚠️ 项**（详见 `audit_03_remediation_summary.md`）：
- **5.8 单节点高可用**（#ARCH-CH-031）：回测期接受单节点 ClickHouse，依赖 restic 本地备份（RPO=24h、RTO=8h）；升级触发条件=实盘立项 / 数据量超单节点容量 / 多用户并发查询需求
- **7.7 异地副本**（#ARCH-CH-032）：用户已推翻，理由=单用户使用 + 仅防硬件损坏 + 外接硬盘两份备份足够 + 不采用 3-2-1 备份铁律

---

## 8. 改期项触发条件汇总

| 项 | 触发条件 |
|----|----------|
| P0-2 预防机制 | 实盘立项 / 下次 tick 缺口事件 |
| P0-4 质量门实装 | backtest 域质量回归 / P0-5 PIT 推进 |
| P0-6 14 表 SCD 真源 | 并入 Wave 2 真源回写 |
| A1 ingest_ts 真源补齐 | 并入 Wave 2 |
| A4 分钟 K 线族 | 分钟策略实盘立项 |
| A7 raw OHLC 价层 | 复权回测质量回归 |
| A8 currency 列 | 港美股回测需求立项 |
| B2 告警接入验证 | 并入 B7 告警通道验证 |
| B5 l2_tick 建表/摘除 | L2 数据需求 |
| B8 cls/eastmoney_news 登记 | 新闻因子接入 |
| C3 备份演练执行 | 下次 restic 备份完成后人工触发 |
| P2-1 物化视图 | 查询 P95 > 500ms |
| P2-2 tick 排序键改造 | 单票回测延迟敏感场景 |
| P2-3 240 硬编码表名 | 按模块分批替换 |
| P2-4 redundant_source 主链路接线 | 实盘立项 |

---

## 9. 关门验收

- ✅ `scripts/lock_files.py status`：本会话无残留锁
- ✅ 临时文件零残留：`scripts/governance/oneoff/_commit_wave1.py` 已删除
- ✅ TTL-METADATA 门禁通过：本报告带 `ttl: task_bound` frontmatter
- ✅ creation_tokens 登记：9 个新文件均登记（commit `cb71d3be78`）
- ✅ Wave 1 commit 引用 #ARCH 编号：`d6ae260754` 引用 #ARCH-CH-025
- ⚠️ 活跃 session 并发：`worker-b2724899-80568`（reconcile_worker 后台进程）运行中，不持有本次提交文件，已用 `allow_overlap=True` 逃生通道（TRAE-079 Phase 2，已确认的开发期告警）

---

## 10. 后续工作

**Wave 2**（Schema 真源继续收口）：
1. 处理 10 处漂移（见 §6.4）
2. 推进剩余 75 张表 DDL 真源回写（按业务优先级分批）
3. P0-6 14 表 SCD-2 真源确认
4. 将 `verify_schema_truth.py` 接入 CI 门禁（pre-merge 漂移阻断）

**Wave 3+**（按触发条件推进）：
- 实盘立项时：P0-2 预防 / A4 分钟线 / A8 currency / P2-4 主链路接线 / 5.8 单节点 HA 升级
- backtest 质量回归时：P0-4 质量门实装 / A7 raw OHLC
- 性能瓶颈时：P2-1 物化视图 / P2-2 tick 排序键

---

**报告终点**。任务规格要求的"每 P0/P1/P2 项处置结果（已修/改期/放弃+理由）"已逐条列出于 §1-§5；对账记录见 §6.3 漂移明细 + audit_03_remediation_summary.md；复评得分见 §7。
