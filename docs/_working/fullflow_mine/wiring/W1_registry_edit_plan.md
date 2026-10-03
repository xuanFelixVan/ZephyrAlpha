---
ttl: task_bound
title: "注册册面精确编辑工单书"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

> 注记：本工单已执行：commit e405020493（清道车道清理后自会话上下文原样重建，仅增本行）。

# W1 册面精确编辑工单书（只产出草案，本文件不执行任何编辑）

证据基线（2026-10-01 只读实测）：CH 四库 255 表（c0_meta 1 / c1_backtest 16 / c1_market 204 / c3_fundamental 34）；黑户 63 张（CH 有表、册无登记，逐张枚举见 §2/§3/§8）；active 幽灵 13；production 幽灵 2；governance.db（data/databases/governance.db，sqlite）45 表 13 张 0 行（costs/task_snapshots/tx_idempotency/circuit_breaker_state/task_files/task_events/knowledge/ke_tombstones/reconciliation_differences/attribution_results/audit_trail/report_archive/switch_registry）。

## §0 执行纪律（执行会话必读）

1. 本工单全部编辑落点=`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（下称"册"）与 `docs/registry_of_registries.yaml`（下称 ROOR）。两册均为热文件：**必用 `safe_write_text`（src/zephyr/shared/io/file_utils.py，CAS）**，禁裸 Edit 后不复核；写后进程外复核（yaml.safe_load 全文件解析+行数 diff）。
2. 执行前按 RULE-WORKTREE claim 两册（`lock_files.py acquire <file> <sid>`）；完成后 `git_commit.py --session <sid> --files <清单>`，禁裸 commit。
3. 每批编辑同 commit 内同步改册头 `entry_counts` 与版本注释行（机械重算：sources/datasets/jobs 数组实测长度），禁留新漂移。
4. 新建条目另需 CREATE-GUARD/登记义务由执行会话承担；本文件自身新建已按 W1 授权登记。
5. 所有 CH 访问只读（zephyr_reader）；本工单行数为 2026-10-01 快照，执行日如行数漂移>±5% 先停下报 Owner。

## §1 格式真源（写条目前必读）

- schema：册 L138-234（source_schema/dataset_schema/job_schema）；dataset 条目字段序以 dataset_schema（L169-205）为准。
- 三正例：完整 active=`DS-084`（册 L3760）；candidate=`DS-003`（册 L844）；degraded 带 degradation_note=`DS-237`（册 L10032）。
- 取号规则：现存最大号 `DS-305`（datasets 数组实测 294 条），新登记自 **DS-306** 起按 P0→P1 顺序连续取号。

## §2 黑户补注册——P0 核心活表 12 张（DS-306~DS-317，完整条目）

渲染规则：下列"完整模板"为唯一格式，每张表按 §2.1 值表代入 `{}` 槽位，值表未列字段一律取模板默认值。逐字执行即可机械生成 12 条 YAML。

```yaml
- dataset_id: {DS_ID}
  entity_name: {ENTITY}
  entity_type: dataset
  scope: production
  contract_ref:
  physical_type: {DDL_ANCHOR}
  produced_by_job: {JOB}
  consumed_by_jobs: [{CONSUMERS}]
  domain_id: {DOMAIN}
  pit_policy: {PIT}
  format_summary: "{ZH}（CH 实测 {ROWS} 行，2026-10-01 system.tables）"
  valid_since: '2026-10-01'
  module_id: MOD-L00-004
  design_maturity: production
  name: {ENTITY}
  name_zh: {ZH}
  status: active
  version: 1.0.0
  created_at: '2026-10-01'
  updated_at: '2026-10-01'
  owner: MOD-L00-004
  produced_by_source: {SRC}
  survivorship_free: {SURV}
  pit_available: {PITAV}
  earnings_lag_days:
  llm_training_cutoff: 'N/A'
  lookahead_test_method: 'N/A'
  label_delay_days:
  drift_detector: none
  entry_role: {ROLE}
  applies_to: [{APPLIES}]
  tags: ["数据", {TAG}]
  algorithm_status: not_applicable
  evidence: "2026-10-01 W1 补注册批：CH 行数实测+消费方 grep 证据（src 路径见工单 §2.1）"
  code_symbol:
  code_fingerprint:
```

### §2.1 P0 值表（| 表 | DS | 库 | 行数 | 中文 | 域 | 源 | PIT | 生产代码证据 | 消费方 grep 证据 |）

| 表名 | DS_ID | 库 | 行数 | name_zh | domain_id | produced_by_source | pit_policy | produced_by_job(代码证据) | consumed_by_jobs(代码证据) |
|---|---|---|---|---|---|---|---|---|---|
| tick_depth_5 | DS-306 | c1_market | 130143451 | 五档 tick 深度 | D_MARKET | SRC-QMT-001 | strict | tick_depth_writer.py/tick_subscriber.py | calendar_coverage_checker.py;qmt_bridge_provider.py |
| emotion_index | DS-307 | c1_market | 8655 | 情绪指数 | D_SENT | SRC-INTERNAL-001 | strict | alt_data/emotion_index_builder.py | alt_data/emotion_index_replay.py |
| board_index_tick | DS-308 | c1_market | 1533258 | 板指 tick | D_MARKET | SRC-QMT-001(回填核) | strict | alt_data/board_index_supply.py | alt_data/board_index_supply.py(自产自用) |
| sector_state | DS-309 | c1_market | 429901 | 板块状态 | D_SECTOR | SRC-INTERNAL-001 | strict | data/sector_state_pipeline.py | l9_readiness_aggregator.py;scheduler.py |
| sector_preference | DS-310 | c1_market | 4 | 板块偏好 | D_SECTOR | SRC-INTERNAL-001 | strict | data/sector_state_pipeline.py | signal_ashare/sector/sector_state_aggregator.py |
| sector_fund_flow | DS-311 | c1_market | 6490 | 板块资金流 | D_MFLOW | SRC-AKSHARE-ALT-001 | strict | implementations/sector_fund_flow_collector.py | policy_theme_mapper.py;sector_factor_manager.py |
| sector_constituent_snapshot | DS-312 | c1_market | 962741 | 板块成分快照 | D_SECTOR | SRC-INTERNAL-001 | strict | alt_data/board_index_supply.py | alt_data/board_index_supply.py(自产自用) |
| sector_constituent_sw_history | DS-313 | c1_market | 46133 | 申万成分历史 | D_SECTOR | SRC-AKSHARE-001(回填核) | strict | scripts/governance/meta_question/wo_a2legs/backfill_sw_member_history.py | （grep 无 src 消费，research 用） |
| regime_state_anchored | DS-314 | c1_backtest | 2242 | 锚定状态机快照 | D_SIG | SRC-INTERNAL-001 | strict | implementations/internal_compute_provider.py | pf_alloc/allocation_inputs.py;regime/core/anchored_state_machine.py |
| strategy_screen | DS-315 | c1_backtest | 1389 | 策略筛选结果 | D_SIG | SRC-INTERNAL-001 | strict | pf_alloc/core/strategy_screener_3d.py | strategy_pipeline/screen_source.py;frontend/dashboard/api_server.py |
| limit_up_pool | DS-316 | c1_market | 1276 | 涨停池 | D_MARKET | SRC-AKSHARE-ALT-001 | strict | implementations/limit_up_pool_collector.py | sector_state_pipeline.py;daban_board_event_deriver.py |
| news_sentiment_score | DS-317 | c3_fundamental | 7733898 | 新闻情感分 | D_SENT | SRC-INTERNAL-001(派生核) | strict | scripts/governance/meta_question/wo_a2legs/backfill_news_sentiment.py | 同目录 build_news_sentiment_window.py |

公共槽位默认值：`survivorship_free: true`、`pit_available:`（空）、`entry_role: reference`、`applies_to: [stock, market]`（sector_* 三张+sw_history 用 `[sector, market]`）、`tags` 第二元素：行情类=["行情"]/板块类=["板块"]/情感类=["情绪"]、`physical_type: clickhouse_table`（DDL-as-code 锚点落地时回填 schemas/categories/ 路径）。`SRC-QMT-001(回填核)`/`(派生核)` 标记=按证据尽量回填、落地时须核实后去括号，不得带括号入库。

## §3 P1 低频活表 28 张（DS-318~DS-345，compact 条目：模板同 §2，字段默认值同 §2，仅值不同）

| # | 表(库) | 行数 | DS | 中文/域 | 源 | 生产/消费证据 |
|---|---|---|---|---|---|---|
| 1 | cftc_positioning(c1_market) | 81270 | DS-318 | CFTC 持仓/D_POS | SRC-AKSHARE-ALT-001 | akshare_alt_provider.py |
| 2 | agri_wholesale_index(c1_market) | 23254 | DS-319 | 农批指数/D_MACRO | SRC-AKSHARE-ALT-001 | akshare_alt_provider.py;apply_market_tables_ddl.py |
| 3 | commodity_futures_main(c1_market) | 189 | DS-320 | 商品期货主连/D_MACRO | SRC-AKSHARE-ALT-001 | apply_cross_asset_ddl.py |
| 4 | commodity_spot_price(c1_market) | 1134 | DS-321 | 商品现货价/D_MACRO | SRC-AKSHARE-ALT-001 | apply_cross_asset_ddl.py |
| 5 | ndrc_fuel_price(c1_market) | 660 | DS-322 | 发改委油价/D_MACRO | SRC-AKSHARE-ALT-001 | akshare_alt_provider.py |
| 6 | road_freight_index(c1_market) | 86 | DS-323 | 公路运价/D_MACRO | SRC-AKSHARE-ALT-001 | akshare_alt_provider.py |
| 7 | gold_etf_holdings(c1_market) | 2871 | DS-324 | 黄金ETF持仓/D_POS | SRC-AKSHARE-ALT-001 | apply_cross_asset_ddl.py |
| 8 | rate_decision_calendar(c1_market) | 6172 | DS-325 | 议息日历/D_MACRO | SRC-AKSHARE-001 | akshare_provider.py;supply_sentinel.py(消费) |
| 9 | macro_data_vintage(c1_market) | 16091 | DS-326 | 宏观初值修正/D_MACRO | SRC-INTERNAL-001 | data/macro_vintage.py;ch_writer.py |
| 10 | futures_warehouse_receipt(c1_market) | 2920363 | DS-327 | 仓单/D_POS | SRC-AKSHARE-ALT-001 | akshare_alt_provider.py;supply_sentinel.py(消费) |
| 11 | option_daily_stats(c1_market) | 11544 | DS-328 | 期权日统计/D_MKT | SRC-AKSHARE-001(回填核) | scripts/backfill_option_daily_stats.py |
| 12 | ex_dividend_event(c3_fundamental) | 57864 | DS-329 | 除权除息事件/D_MKT | SRC-AKSHARE-001(回填核) | c3_fundamental 批量管道 |
| 13 | index_adjustment(c1_market) | 15196 | DS-330 | 指数调整/D_MKT | SRC-AKSHARE-001(回填核) | index 批量管道 |
| 14 | sector_code_name_map(c1_market) | 1198 | DS-331 | 板块码表/D_SECTOR | SRC-INTERNAL-001 | implementations/sector_code_bridge.py |
| 15 | l9_readiness_daily(c1_market) | 156 | DS-332 | L9 就绪度/D_SIG | SRC-INTERNAL-001 | l9_readiness_aggregator.py;pf_alloc/allocation_inputs.py(消费) |
| 16 | ir_activity_extracted(c3_fundamental) | 30 | DS-333 | IR 活动抽取/D_FCT | SRC-INTERNAL-001 | LLM 抽取管道（与 DS-302 记录表分置） |
| 17 | irm_interactive_extracted(c3_fundamental) | 74 | DS-334 | IRM 问答抽取/D_FCT | SRC-INTERNAL-001 | LLM 抽取管道（与 DS-303 分置） |
| 18 | account_nav_daily(c1_market) | 1 | DS-335 | 账户净值日/D_PERF | SRC-INTERNAL-001 | 交易记录管道 |
| 19 | execution_report(c1_market) | 1 | DS-336 | 成交回报/D_EXEC | SRC-INTERNAL-001 | 交易记录管道 |
| 20 | sim_attribution_daily(c1_backtest) | 122 | DS-337 | 归因日/SIG | SRC-INTERNAL-001 | c1_backtest sim 管道 |
| 21 | sim_daily_report(c1_backtest) | 256 | DS-338 | 仿真日报/SIG | SRC-INTERNAL-001 | c1_backtest sim 管道 |
| 22 | sim_trade_log(c1_backtest) | 85 | DS-339 | 仿真成交流水/SIG | SRC-INTERNAL-001 | c1_backtest sim 管道 |
| 23 | cohort_daily_ledger(c1_backtest) | 221 | DS-340 | 队列日账/SIG | SRC-INTERNAL-001 | alt_data/cohort_daily_ledger.py |
| 24 | hypothesis_precheck(c1_backtest) | 309 | DS-341 | 假设预检/SIG | SRC-INTERNAL-001 | c1_backtest 管道 |
| 25 | daban_board_event(c1_market) | 3106 | DS-342 | 打板事件/D_MKT | SRC-AKSHARE-ALT-001 | implementations/daban_board_event_deriver.py;alt_data/emotion_index_builder.py(消费) |
| 26 | alt_fx_rate_ecb(c1_market) | 93 | DS-343 | ECB 汇率/D_MACRO | （ECB 直连，produced_by_source 留空+注） | implementations/fx_ecb_provider.py |
| 27 | etf_benchmark(c1_market) | 2373 | DS-344 | ETF 基准/D_MKT | SRC-AKSHARE-001 | akshare_provider.py;frontend/dashboard/api_server.py(消费) |
| 28 | market_pattern_certification(c1_market) | 68 | DS-345 | 形态认证/D_SIG | SRC-INTERNAL-001 | internal_compute_provider.py;pattern_evidence_certifier.py(消费) |

公共默认：status: active / design_maturity: production / pit_policy: strict（9~17 号历史/日历类可 partial）/ entry_role: reference / applies_to: [market] / survivorship_free: true。`SRC-*-001(回填核)` 执行时核实去括号。

## §4 P2 候退役清单 14 项（不注册，Owner 门位裁决后走退役/删除流程）

9 张 legacy/quarantine 备份表：kline_daily_hfq_legacy_20260924(8426036)、kline_daily_hfq_preversion_20260925(10079242)、kline_daily_hfq_quarantine_20260925(10475)、kline_daily_hfq_recalc(100054)、kline_monthly_hfq_legacy_20260924(502496)、kline_monthly_hfq_legacy_r1_20260924(524474)、kline_weekly_hfq_legacy_20260924(2127400)、kline_weekly_hfq_legacy_r1_20260924(1856391)、index_valuation_daily_quar_20260920(8125)；4 视图：dividend_tax_node、macro_data_compat、macro_data_latest、v_kline_sector_880_named；+_tmp_mat_test(0 行)。处置顺序：视图确认无人引用后 DROP（改名留档 7 天→删）；备份表先验证 G:/backup 夜镜像覆盖（INFRA-STORE-003），覆盖成立才可退役；_tmp_mat_test 即删候选。

## §5 幽灵处置——13 个 active 幽灵（CH 四库+governance.db+PG 均无物理表实测）

统一编辑形态（锚定式，禁全局 sed）：对每个 DS_ID，定位行 `^- dataset_id: {DS_ID}$`，在其后 40 行内将首个 `  status: active` 替换为 `  status: candidate`，并在该 status 行后插入一行 `  degradation_note: "{NOTE}"`；同块 `  updated_at:` 改 `'2026-10-01'`。批量执行器：

```python
import re,io,sys
F=r'docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml'
GHOST={'DS-029':'factor_analysis 六件套注册时仅设计态，CH 无物理表，降级待物化',
 'DS-030':'同 DS-029','DS-031':'同 DS-029','DS-032':'同 DS-029','DS-033':'同 DS-029',
 'DS-034':'同 DS-029','DS-035':'同 DS-029','DS-036':'同 DS-029','DS-037':'同 DS-029',
 'DS-038':'同 DS-029','DS-039':'同 DS-029',
 'DS-224':'W1 复核：physical_type=postgres_table（depgraph PG），非 CH 表，本次 CH 排查不含 PG——降级候选，PG 侧复验四表族存活后可回升 active',
 'DS-225':'派生流视图（无物理表为设计态），降级候选；若 api_server /api/chain-impact-stream 仍在用，改登 job/endpoint 资产而非 dataset'}
lines=open(F,encoding='utf-8').read().splitlines(keepends=True)
out=[];cur=None;done=set()
for ln in lines:
    m=re.match(r"^- dataset_id: (DS-\d+)$",ln)
    if m: cur=m.group(1)
    if cur in GHOST and cur not in done and ln.rstrip('\r\n')=='  status: active':
        ln='  status: candidate\n  degradation_note: "%s"\n'%GHOST[cur]; done.add(cur)
    out.append(ln)
missing=set(GHOST)-done
assert not missing, f'未命中:{missing}'
sys.stdout.write('降级 %d 条\n'%len(done))
open(F,'w',encoding='utf-8',newline='').writelines(out)  # 执行会话须改走 safe_write_text
```

注：DS-224/DS-225 为"非 CH 物理形态"非纯幽灵，note 已带复核路标；DS-029~039 若后续物化落库，须回填 produced_by_job 并翻回 active。

## §6 production 幽灵 2 条（两案并列+推荐）

- **DS-084 meta.index_member**（册 L3760）：证据字段自证"落库复用既有 SCD-2 表"=c1_market.index_constituent（实测 697395 行）。**方案A（推荐）实体名锚定校正**：`entity_name: meta.index_member`→`entity_name: c1_market.index_constituent`（name 同步），status 保 production——数据真实存活，仅登记名漂移。方案B：降级 candidate（按 §5 形态）。推荐 A：零数据动作、消除幽灵、消费语义不变。
- **DS-085 meta.st_status**（册 L3799）：证据自证复用 c1_market.st_stock_list（实测 424304 行）+tushare namechange 派生历史段。**方案A（推荐）**：`entity_name: meta.st_status`→`entity_name: c1_market.st_stock_list`（format_summary 补"派生历史段=data_source=tushare_namechange_derived"）。方案B：降级 candidate。推荐 A，理由同上。

## §7 断供/空壳处置草案（均不执行，登记后走 Owner 复核）

1. **DS-123 daily_valuation 退役登记草案**（册 L5304）：块内 `  status: degraded`→`  status: retired`，degradation_note 追加"；2026-10-01 W1 退役登记：候选退役，禁任何消费方引用"。**⚠ 新证据（2026-10-01 CH 实测）与 2026-09-12 全 0 结论冲突**：全表 273847 行中 close≠0 有 272485（99.4%），max(trade_date)=2026-09-30，近 10 日非零率 97.8%——空壳状态已被修复。故本草案**先复验后执行**：复验确认数据健康则改登 active（撤黑名单）而非退役；确认仍不可信再落退役。二选一，禁跳过复验直接执行。
2. **SRC-OKX-001 status 缺填补全**（册 L683-704，块尾止于 `  code_path: ...` 即断，schema 尾 12 字段整体缺失）：在 `  code_path: src/zephyr/data/implementations/crypto_provider.py` 行后插入：

```yaml
  status: degraded
  version: 1.0.0
  created_at: '2026-09-11'
  updated_at: '2026-10-01'
  owner: MOD-L00-004
  entry_role: "reference"
  applies_to: ["market"]
  tags: ["加密", "行情"]
  algorithm_status: "not_applicable"
  evidence: ""
  code_symbol:
  code_fingerprint:
  degradation_note: "2026-09-11 实测跨境不可达；下游 DS-226 crypto_kline_daily 存活（18952 行，produced_by_source=SRC-INTERNAL-001 与本源 provides_datasets=[DS-226] 互指矛盾待裁）；恢复采集前维持 degraded"
```

3. **DS-237 alt_sz_weather_warning 断供标注**（册 L10032，现 status 已=degraded）：在 `  evidence: "DDL schemas/...weather_warning.py；实测 9,349 行；` 行后（或块内 status 行后）插入 `  degradation_note: "2026-10-01 W1 断供标注：源平台 2020-09-23 后止更是既定断供（非临时故障），CH 现存 10026 行历史档案，仅限历史事件窗研究，禁当活跃流消费"；updated_at→'2026-10-01'`。

## §8 口径漂移修账 3 处（精确 old→new）

1. ROOR `REG-DATAFLOW-001` 块（L719）：old=`        entry_count: 342` → new=`        entry_count: 434`；同行组 counting_rule 建议追加"；2026-10-01 复测 434=sources 18+datasets 294+jobs 122"。锚定上下文：前一行 `physical_path: .../data_asset_registry.yaml`。（ROOR 另一处 434 为 REG-SCRIPT-002 脚本册计数，勿误伤。）
2. 册 L85：old=`entry_counts: {sources: 18, datasets: 293, jobs: 122}` → new=`entry_counts: {sources: 18, datasets: 294, jobs: 122}`（行尾两条历史注释原样保留，仅换数字；本工单 §2/§3 落地后同批重算为新实测值）。
3. ROOR `REG-TECHNICAL-INDICATOR-001` description（L690）：old 子串=`= 41 条，覆盖 1min~月线 9 周期` → new=`= 102 条（与本块 entry_count=102 对齐，2026-10-01 修账；"41 条"为 2026-08-14 历史快照），覆盖 1min~月线 9 周期`。⚠ 附带发现：technical_indicator_registry.yaml 顶层 list 实测 143 项≠102≠41，三层不一致交 reconciler 专项，不在本工单强改。

## §9 10 张 0 行旧账表（实测 9 张旧账+_tmp_mat_test=10；消费引用面+处置顺序）

grep 证据：edb_data（api_server.py+consumption_census.py 只读引用）；index_valuation_daily_v2（仅 recheck_empty_tables.py 自查脚本）；ipo_schedule（api_server+consumption_census）；l2_tick（miniqmt_provider.py 采集代码+api_server——**有活采集链路**）；margin_target_adjustment（api_server）；msci_adjustment（api_server）；stock_candidate_pool（signal_ashare/tradability_preflight.py+candidate_pool_snapshot.py——**有活消费**）；stock_valuation（api_server）；reconciliation_differences（治理 reconciler 系统表）。
处置顺序：①reconciliation_differences 保留（事件触发 reconciler 待写入，禁删）；②stock_candidate_pool/l2_tick 修产不删（活引用，先查产线为何 0 行）；③api_server 只读引用五表（edb_data/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation）端点空态防护复核后进退役清单（Owner 门位）；④index_valuation_daily_v2 直接退役。全部先过 G:/backup 覆盖验证。
