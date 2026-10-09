---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/02_gap_ledger.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# 全流通缺口总账（B0 考古批次：16 役合并去重）——st-workingchief-20261006

> 考古对象：fullflow_mining / fullflow_campaign / fullflow_mine / fullconnect_campaign / chain_fullflow_20260926+closeout / full-auto-chain / circulation_chief / total_command_closeout / night_sweep / night_totalflow_* / chain_circulation_campaign / fullcirc_closeout_chief / unified_campaign / fullflow_chief_closeout。
> **归属分流（R-3 裁定）**：他队在施工→交叉验证；无人认领+今晚可动→线3 施工；Owner 门位→备料不代裁；治理在案→登记。

## §1 P0 实盘 Flip 组（死线 2026-10-08 首交易日）——归属：st-datasop-20260930（fullflow_mine E4 线）→ 本役交叉验证

| # | 缺口 | 证据 |
|---|---|---|
| 1 | GAP-1 执行腿 env 翻转：sim_daily_runner bridge-execute `_BRIDGE_ENV="sim"`→real 装配 | fullflow_mine/wiring/E4_wave1_live.md §4 |
| 2 | GAP-2 三卡 T 日信号生成件（E-TIMING-001/TSMALL-001/DABAN-023 均为回测重放接口） | 同上 |
| 3 | GAP-3 卡级监控消费面（card_state_observation 无消费者；kill_switch 挂点未接） | 同上 |
| 4 | GAP-4 实弹台账行+credential 换正式 | 同上 |
| 5 | T1 冠军配方 36388958b3d8 送晋级池走样本外+前向验证 | fullcirc_closeout_chief/90_execution_log.md |

## §2 数据断供组——归属：st-datasop（EXEC 线）→ 交叉验证已修项，其余登记

- 新闻评分链 news_sentiment_score 断 13 月（HANDOVER 1-2）
- 期权 greeks/iv_surface **已修** 84bb7f8d83a（EXEC-2a）→ 线4 验证
- 台风 F7 复活/reservoir_level 半死/board_index_tick 断档（HANDOVER 1-4/1-5/1-6）
- P1 断供批 17 项（HANDOVER 2-1..2-17；EXEC-1 已消 3 项）→ 线4 验证+余项登记
- market_etf_share_snapshot：任务在岗源死（东财 push2 拒连），源恢复自愈

## §3 消费接线组（数据活着没人吃，20 项）——HANDOVER 3-1..3-20，登记待认领

情绪温度计五成分拆露/attribution_results 接线/knowledge 写口/溢价率三表互救/BOM 叶挂价/style_regime 接宏观/AH 溢价/基本面五岛/convertible_bond_list/futures_term_structure 等。

## §4 骨架断链组（fullflow_mine 5-1..5-11）——登记

F16-F20 五条进货车道复活（lane_c 停 14 天）；D13-20 竞价窗闸恒 skipped；D13-44 日界交接断供；F38 noqa 摘除；P2 弱运行簇 7 件；3 个空调度槽。

## §5 结构性治理组（无人认领+在案）——本役线3 候选池

| # | 缺口 | 证据 | 本役处置 |
|---|---|---|---|
| 16 | 合并器 MERGER-TOPKEY-SWALLOW 新顶层族整族吞没（部分缓解未修本） | night_sweep/99 §③ | 登记（立法项） |
| 17 | 入队预检旁路：requeue/enqueue_item 直调第 4 入口无预检 | chain_fullflow_20260926→C1 | 登记 |
| 18 | 快照自洽见证层未建+W17 --base-head 不填 base_blobs | 同上→C2 | 登记 |
| 19 | 假绿灯交叉尺：task_runs 回执与目标表真行数未互证 | 同上→C4 | 登记 |
| 20 | 门禁卫生：CREATE-GUARD 无 files_trigger 累计 10 万+s | chain_fullflow_20260926 | 登记 |
| 21 | gate 名册标量手工维护被合并器吞 → 机生化立法项 | chain_circulation/91 §三 | 登记 |
| 22 | capability 册 HEAD↔PG 分叉 ~375 条 | fullcirc_closeout_chief/90 ① | 登记 |
| 23 | 翻译册重复 module_path 6-7 组 --dedupe 未清 | night_sweep/99 §①③ | 登记 |
| 24 | 自动化红线 V2-V4（keeper 伪造活性/idle 自退失效） | circulation_chief/LEDGER 钩子3 | 登记 |
| 25 | TI 分钟计算核 09-19 语义漂移（回填 HOLD） | night_totalflow_20261001/B_mine.md | 登记 |
| 26 | 91_machine_crosscheck.yaml STALE rc=1 | fullflow_mining/96 §七 | 线3 候选（重生检查） |
| 27 | 7 个 0 字节死库待 Owner 批删 | fullcirc_closeout_chief/c1 | Owner 门位 |
| 29 | confirm_gate.py 已建未接线（W6-C 修前禁接线） | fullflow_mining/96 项5 | 登记 |

## §6 Owner 门位组（备料不代裁，34 项在案）

fullflow_mine 第〇批 8 项（净删 CH 9 表/空表3/候退役 25 指标+8 因子…）；TRD-A10 实盘腿合规十闸；circulation_chief 十项；total_command_closeout 补-1..16；散项（commit_queue_interactive 出厂翻转/见证层实盘域/F34 DDL --apply/F51 币圈退役/hfq lineage/9 空壳表/三真源收敛/immutable_tree flag ON 复测/tdx 退役/NB1 B2/B5）。

## §7 已被后续修复（交叉验证抽样池，线4 用）

清洗三引擎(1bd86833)/order_daemon(8c5117b600)/裸 duckdb 拦(M3-C1b)/KillSwitch 持久化(461a86be17)/tilib 夜回填(514698ba62)/F53 Saga(fce51c3da67)/F73 AB 联赛(3992e4b024a)/F75(501f14a82f)/F74 通知(d988f1e6d0)/F62 十闸余量部分(5ddaf667aa 等)/etf_benchmark(3c01517bb2)/macro RepoRate(6d4177ec)/migration_registry(67be6338)/resource_profile 计数(aae09a6550a)/metaq reconcile(10-04 复跑 result=0)/T2 发车(grid_20261005-215457)。

## §8 本役施工裁定（终局全貌量尺，mining SOP §6 自审闸）

- **施工**：七图入 ROOR（消灭"注册表发现真源不全"的人工记忆依赖，直接服务终局全自动发现）——无人认领、纯登记性、零冲突。
- **挂起排期**：TDM 回链/FACTORY counts+边（地图本体属地图战役域，他队窗内）；对账链建设（ENV-15，大件，需施工令级立项）。
- **封矿（本役不碰）**：Owner 门位 34 项、他队活跃领地、MERGER 立法项（需 Owner）。

## §9 线4 交叉验证 FINDING（2026-10-06 03:4x，8 项抽验：6 CONFIRMED / 1 哈希笔误 / 1 HIGH）

| 严重度 | 发现 | 证据 | 处置 |
|---|---|---|---|
| **HIGH** | **净删 21 条宣称"已落地"不实**：fullflow_mine/wiring/E1_netdelete21.md §二宣称"机核断言全绿（IND 143→128/FCT 175→169）、净删两册先行落地"，但 dev 主区、session/st-datasop-20260930 分支 HEAD、其 worktree 工作区三处实测均仍是净删前态（version 1.6.1/IND-TREND-003:307、IND-MOM-028:1191、FCT-LIQ-060:10586 抽样全在册），全分支自 10-03 起零 commit 触碰该册 | 三处仓库实况 + git log --all --since=2026-10-03 零命中 | 移交 st-datasop-20260930（其役 ACTIVE 中）：按 E1_netdelete21.md §六附表（21 条原文已存档）重做落地；疑被陈旧快照覆写战争吞没 |
| MEDIUM | F75 宣称哈希 501f14a82f 不存在（全分支+reflog），真身=5071f14a82f（一字之差，内容与宣称完全吻合，两侧接线实测在位） | promotion_advisory.py:623/714 | 台账引用方按真身哈希修正；实质 CONFIRMED |
| LOW | T2 大考 grid_20261005-215457 实际 10-05 21:55 已完成（evaluated=24/零死），非"在跑" | data/strategy_intake/grid_20261005-215457/ 四件成果 | 状态口径更新，成果有效 |

其余 5 项 CONFIRMED：期权 greeks 修复（commit+注册面+CH 行数三重实证，max(trade_date)=09-30 无新断供）/F73 联赛 13 件（5 模块 import 冒烟 OK）/account_nav_daily 接线（run_post_settlement.py:434-452 对位）/执行腿 sim 现状（_BRIDGE_ENV="sim" 硬编码=Owner 门未翻转，GAP-1 前置成立）/翻译册 dedupe（9f32c9011b8 恰删 24 行=3 条目×8 行，真悬空删得对）。

**他队成果总体可信度：高（8 项中 7 项实质成立）**。
