---
ttl: task_bound
completes_when: 九环节全部封矿+施工收口+循环检查连续两次 0 问题+红蓝通过+终局交付，或 Owner 叫停
title: 交易决策链总包战役——骨架挖矿总谱（环节全景封矿）/波次派发/状态回写
owner: ZephyrAlpha-Owner
session: st-tdchain-20260917
date: 2026-09-18
---

# 交易决策链总包战役 · 骨架挖矿总谱

> **总令**：Owner 通宵交接令 2026-09-18（做T v2+检测器重校准+WYF-3+G07 核查+准入判据+合并收口+E2E 模拟单）。**挖矿纪律**：先把环节挖清楚（本文档），每个环节一个子文件夹作业簿（六向台账：目标/证据/块/依赖/三态/下一步），挖干判据=六向台账填实+自审三态；"线内先挖后干、线间并行流水"，谁挖干谁先开工。
> **持久规则**：每完成一个有意义步骤即回写本文档 §6（防上下文压缩失忆）。

## 1. 三轴战役对账（防遗漏声明）

本仓库同一夜有三条战役轴并行，环节互不重叠：

| 战役轴 | 会话 | 环节轴 | 真源 |
|---|---|---|---|
| 自动化产线轴 | st-autolnk-20260917 | 8+1 工段（L1 上架/L2 转正/L3 胃/L4 体检/L5 标准库/L6 红线/车道G/事件轨） | docs/_working/automation/campaign/CAMPAIGN_LEDGER.md + mining/00_总环节谱.md |
| 残余挂账轴 | st-residual-20260917 | 6 施工环节+2 战役阶段（WO-1~WO-5 危机接线/归因/核对器/人群账本/演练/对冲/告警） | docs/_working/residual_construction/00_master_ledger.md |
| **交易决策链轴（本谱）** | st-tdchain-20260917 | **9 环节 E0-E8**（本文档 §2） | docs/_working/trading_vision/* + factory/t_v2/* + 本谱各作业簿 |

**交叉约束**：residual 战役 C1 裁定=pipeline_events.py / tasks.yaml / apply_market_tables_ddl.py 三共享文件归其总统筹独占——本轴 E1/E0 全程规避直改，涉及时登记挂单。

## 2. 环节清单（已封矿，共 9 环节）

| 环节 | 内容 | 作业簿 | 交接令任务映射 | 波次 | 状态 |
|---|---|---|---|---|---|
| E0 | 合并队列收口：regcal→p2b(拆函数)→orchp3→sowner001→sowner002 cherrypick×4→depgraph | e0_merge_closure/ | 任务 0 | W1 | 执行中 |
| E1 | 做T 数据面基建：ETF 分钟族时区修复+板块高周期合成+缺口登记 | e1_tdata_infra/ | 任务 1（数据半边） | W1 | 执行中 |
| E2 | 做T v2 复活口径封存：#304 砍现形态+窄考试 RED+复活条件 | e2_tv2_revival/ | 任务 1（考试半边） | W1 | 挖干 |
| E3 | regime r4/r10 重校准合并+复核（方向语义退役） | e3_regime_recal/ | 任务 2 | W1 | 挖干待合并 |
| E4 | WYF-3 封矿核实：#264→#271→#285 证伪加厚链 | e4_wyf3_closeout/ | 任务 3 | W1 | 挖干（前班已完成） |
| E5 | G07×state_label 关联核查（只读） | e5_g07_linkage/ | 任务 4 | W1 | 执行中 |
| E6 | 模拟盘准入判据：E6 双尺重考取证+STD-SIM-ACCESS-002 转正 | e6_sim_admission/ | 任务 5 | W2 | 执行中 |
| E7 | QMT 模拟盘 100 股端到端烟测+证据归档 | e7_qmt_e2e/ | 通宵令 E2E 明令 | W2 | 阻塞待终端 |
| E8 | 红蓝对抗+循环检查×2（连续两次 0 问题） | e8_redblue_loop/ | 通宵令第五条 | W3 | 待 W1/W2 |
| Q1 | 裁定批量原子登记+台账回写+临时文件清零+终局报告 | 本文档 §6 | 通宵令第六、七条 | 末 | 待 E8 |

**环节清单封矿声明**：交接令五任务+E2E+红蓝收尾，经对账（§1 三轴+裁定 #304-#326 新口径）归并为上述 9 环节，骨架拆分到"真源或口径变化"为止，不再新增环节；新发现一律记各作业簿"长尾"。

## 3. 接班时关键情报（防重挖，2026-09-18 03:0x-04:0x 侦察）

- **裁定已至 #326**：新裁定从 #327 起。owner_fast_sign 一页读全场：docs/_working/kimi_audit/owner_fast_sign_20260917.md。
- **做T v2 已被 #304 砍现形态**；窄考试已跑=RED（共振 +0.88bp vs 对照 +0.87bp，p=0.4997，净 -7.5bp）；复活=单假设预注册卡（毛边际>12bp+DSR>0.5）或真实 001 考试产物。
- **交接令过时点勘误**：①股票 15/30/60min 表已全量在库（2021-09-01→2026-09-16，5849 只，9798万/4886万/2449万行）——"15min 表不存在"已失效；②WYF-3 前班已终态（#285 维持置零）；③regime r4/r10 重校准已执行（session/st-regcal-20260917 分支待合并）；④组合门打分器已建成（promotion_combo_gate.py，40ca90eb88）。
- **数据面真实缺口**（CH 实测）：ETF 分钟族五表 trade_date<=2026-06-30 UTC 误标（kline_etf_15min 误标 23,168,185 行未修，修复脚本 scripts/data/repair_etf_minute_tz_split.py 在盘未入库）；kline_sector_intraday 09-11/14/15 仅 1m 合成行；kline_1min/15min 止于 09-16（09-17/18 缺，miniQMT 白班关停）；120min 全库空白（豁免：tasks.yaml:2027 先例"60min 两根聚合"，查询期聚合即可）；kline_index_intraday 不存在（intraday_l1_tracker.py:406 已登记 510300 代理）。
- **QMT E2E**：runbook=docs/_working/automation/campaign/qmt_e2e_runbook.md；协议=scripts/tests/smoke_test_qmt_broker.py（600000.SH 100 股跌停价限价买→撤单，零成交零风险）；09-15 有全通过先例；今夜尚无人下过单（防重复下单）；执行前置=XtMiniQmt.exe 进程在线（侦察时仅 XtItClient.exe 在线，Owner 白班会亲自开）。
- **在飞会话**：st-crisis-gate-20260918 / st-flashbiz-20260918 / st-altdatamap-20260918 / st-sopfix-20260918 等今晚活跃；主区有大量他会话未提交件与 staged 内容——本轴所有提交走队列正门（--enqueue）防连坐。

## 4. 波次计划（线间并行流水）

- **W1**：E0 合并链（主线串行 git 手术）+ E1/E5 代理执行 + E2/E4 封矿落档。
- **W2**：E6 转正+判据终稿 → E7 QMT 烟测（终端就绪即插队执行）→ E3 合并后复核。
- **W3**：E8 红蓝+循环检查×2 → Q1 裁定批量+台账回写+清理+终局报告。

## 5. 提交账本（回写用）

- e7a17a9012 骨架挖矿总谱+9 环节作业簿（q-0003，R5 目录改名 tdchain_mine/ 后落地）
- 0060289c66 M1 merge(regime) regcal 并入——r4/r10 方向语义退役（E3 ✓）
- 259b15c612 M2 merge(plan-engine) p2b 场景引擎+daily_plan 拆函数（Flash 前置件）
- 2fa92002 M3 merge(strategy-pipeline) orchp3 编排器（E0 ✓）
- (M4) merge(factory) s-owner001 模块+FAIL 出证并入
- 08d3fa97 M5a s-owner002 冻结文档 cherry-pick；M5b 出证报告
- q-0004 M5c 切换器模块 17 件（复杂度重构 16→6/22→8 等价对拍 152 组+depgraph 登记 9 节点+M11 注记）
- q-0005 E6 批：STD-SIM-ACCESS-002 转 frozen（裁定#337）+双证据归档
- ETF 五表时区修复：五表 remaining_utc=0 全绿（工具三治本随批收编）

## 6. 状态回写

| 环节 | 状态 | commit/证据 | 备注 |
|---|---|---|---|
| E0 | ✅ | M1-M4+cp1/cp2/cp4 落地 | cp3 六闸实录：分支留档 89dd33dd8a（#310 档案件），修复清单移交维护班 |
| E1 | ✅ | 五表 remaining_utc=0 | 板块高周期合成裁定跳过（登记） |
| E2 | ✅ | 封存簿 |
| E3 | ✅ | 0060289c66+835 tests |
| E4 | ✅ | #285 链核实 |
| E5 | ✅ | e5 簿关账 |
| E6 | ✅ | 裁定#337+q-0005 |
| E7 | ✅（他会话 03:08 实弹+我方不重复下单） | 60747a8a47 |
| E8 | ✅（依终局报告§二） | R1/R2 连续两轮 1766 件通过+红蓝抓出 1 真红已修 | f21ba9b286 |
| Q1 | ✅（依终局报告；临时件清零=部分，tdchainJ 登记） | 裁定#337=c1bddad9db+报告 f21ba9b286/bf65648609 | 详见下节验收复核 |

### 验收复核（st-ff-tdchainJ-20260918，2026-09-18 午后，HEAD=36c9ca4db2）

#### 6.1 十一件 sha 祖先核实（`git merge-base --is-ancestor <sha> HEAD` 逐条实测）

| 件 | sha | 结果 |
|---|---|---|
| M1 regcal 方向语义退役 | 0060289c66 | ANCESTOR-YES |
| M2 p2b 场景引擎 | 259b15c612 | ANCESTOR-YES |
| M3 orchp3 编排器 | 2fa92002 | ANCESTOR-YES |
| M4 s-owner001 factory merge | 29967c99ad | ANCESTOR-YES |
| cp1 冻结文档 cherry-pick | 08d3fa97 | ANCESTOR-YES |
| cp4 收尾交接包 | 324cf187d7 | ANCESTOR-YES |
| E6 批（裁定#337 转正） | c1bddad9db | ANCESTOR-YES |
| ETF 修复工具收编 | 60ed3aa49c | ANCESTOR-YES |
| 挖矿总谱+九簿 | e7a17a9012 | ANCESTOR-YES |
| 终局报告 | f21ba9b286 | ANCESTOR-YES |
| 终局报告 cp3 修正段 | bf65648609 | ANCESTOR-YES |

11/11 均为 HEAD 祖先，前夜战役交付全部在 dev 链上。

#### 6.2 ETF 五表只读核验（repair_etf_minute_tz_split.py --verify，仅只读通道）

- remaining_utc=0 ×5 实测：1min=327,074,832 / 5min=72,070,158 / 15min=23,950,305 /
  30min=11,973,785 / 60min=5,975,672（全 beijing 口径，ok=true）。
- 备份五表 `*_tz_bak_20260918` 在库（DatabaseService system.tables 实测）：
  1min=326,301,055 / 5min=71,856,186 / 15min=24,331,141 / 30min=11,939,337 / 60min=5,962,194 行。
- 边界：本车道未跑 dry-run/--execute（instL 独占脚本；--execute=Owner 门位）。

#### 6.3 测试基线

- `tests/regime/ tests/plan_engine/ tests/strategy_factory/` 实测 **1766 passed**（61.93s），
  与基线 1766 差值=0（口径遵裁定#325：该套件本轮检出 1766 件通过）。
- 他会话 unstaged 件（test_stop_loss_strategy.py / test_take_profit_strategy.py）本轮未造成漂移。

#### 6.4 QMT 只读对账（XtMiniQmt 在线，模拟目录双重断言过）

- connect→get_positions（cash=9,651,613.46；510300.SH 1100 股/600036.SH 100 股）→
  query_trades_today=4 笔（全 510300.SH，与柜台 Deal.csv 4 行一致）→query_order 抽样 None→
  disconnect；零新下单、零撤单、禁区未触。详见 e7 作业簿回写节。
- D3 晨间复核：c3 隔夜单本地 #DONE/ack 仅 SENT，今日柜台 Order.csv（828 行，全 20260918）无
  600000 委托——与 e7 簿契约缺口②（隔夜单静默丢弃）一致，登记不处置；成交腿=今日 4 笔 510300
  （test-002），c3 600000.SH 零成交 ✓；循环单 801 笔（smoke-e2e-1789694891，09:30:01-11:30:22，
  800 已报+1 已撤）已停 6h+，批量撤单=Owner 门（flash-nightbuild 簿已请）。

#### 6.5 队列死信处置（tdchain 系）

- q-20260918-st-tdchain-20260917-0001/0002：内容已被 q-0003（e7a17a9012）取代 → 判定已取代。
- 同 -0004/0009/0010/0011/0012（cp3 切换器批）：裁定停止强推+总包预裁②（待门禁触发随批做），
  内容保全于分支 89dd33dd8a → 判定已取代，不 requeue（requeue 必再撞 NO-LONG-PARAM-LIST，违预裁②）。
- 同 -0014（危机闸收编批）：pf_alloc=landA 独占且现 staged（R-001：landA 按原批次配方落地），
  对症修需改 TDM algo_note=本车道禁写 → 不 requeue 不 purge，移交 landA/总包。
- **工具事实**：commit_queue.py 无 `purge` 子命令（enqueue/status/drain/requeue/cleanup/health），
  且 cleanup 明文"dead/ 永不清理"→ 死信原件按设计保留=取证材料，仅登记判定。
- 积压：pending=0 / processing=0（health 实测，dead 总 939 为历史代际，非本车道范围）。

#### 6.6 .runtime/tmp 临时件

- 多会话并发写同目录窗口实测仍在（16:5x/17:3x 有他会话新 msg 文件）→ 按纪律"并发窗口禁 rm"
  **跳过删除，登记留档**：tdchain 系已落地批 msg（msg_e1final/msg_e6/msg_final/msg_final2/
  msg_m5b/msg_m5d、tdchain_* 7 件）待并发窗关闭后由总包/收尾班统一清；msg_m5c.md 对应
  q-0004 未落地批（内容在分支），保留。

#### 6.7 裁定清单登记

- pending_for_max.md（七项，①R-001 关闭/②⑦预裁落档/⑤Owner 门位登记不催）+
  req_tdchainJ_01..03（③tombstone 实证/④family_registry 立案书/⑥建表申请）+
  lanes/tdchainJ_kline_index_intraday_spec.md（⑥规格）；COORDINATION_LEDGER §6 待裁表已回写 3 行。
