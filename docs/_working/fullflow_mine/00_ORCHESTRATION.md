---
ttl: task_bound
title: "全流通数据挖矿接线战役——总包台账"
owner: st-datasop-20260930
language: zh
status: active
version: "1.2.0"
date: 2026-10-01
topic: fullflow_mine
---

# 全流通数据挖矿接线战役——总包台账（st-datasop-20260930）

> 总包=本会话。授权：Owner 睡前总包令（2026-10-01 03:25）。挖干判据=六向台账+自审闸三态；线内先挖后干、线间并行流水。

## 一、战役阶段状态

| 阶段 | 状态 | 产出/commit |
|---|---|---|
| P0 SOP 落地 | ✅ | 46db7d42f5（onboarding v2.0.0+mining v1.5.0+index 补漏；期间根修 .git/index.lock 死锁+debt 手柄带留痕） |
| P1 环节骨架 | ✅ 挖干 | skeleton/ 14 件：环节总数=122 环节/13 段（96✅/20🔨/6⬜），时钟轴 44 环节=同资产投影 |
| P2 数据族挖矿 | ✅ 九车道挖干 | lanes/ 9 本作业簿：逐实体六问+12 应用面+工单+六向台账+自审闸三态 |
| P3 册面接线 | ✅ | e405020493：黑户补注册 40（DS-306~345）/幽灵降级 13/锚定校正 2/DS-123 复活/孤岛 20 入账（--check rc=0）/mounts 6 卡 9 处/漂移修账 3 |
| P3 代码接线 | ⬜ 待执行 | E3=MAC 传感器 score() 下游接 llm_premarket_analysis（L08-WO1） |
| P3 断供止血 | ⬜ 工单已备 | 期权 greeks 停 09-23 在役吃旧数（L01b-W1）/news_sentiment_score 13 个月断粮（L04-W1）/cftc+gold_etf+market_signal_history 挂钩缺失 |
| P4 循环检查+红蓝 | ⬜ | 门禁三件复跑×2=0+红蓝对抗 |
| P5 落地交付 | ⬜ | 战役文档进 HEAD（反收割：本文档族曾两度被清道车道收割，13 路代理自上下文第三轮重写） |

## 二、战果速览

- 骨架：122 环节/13 段；F27+F48 断链已被兄弟队 8c5117b600 修复（交叉验证✅）；alloc_budget_daily 同证已修。
- 情绪：C1/C3/C4/C5/C6 五成分零消费；market_signal_history 止 09-04、news_sentiment_window 止 08-20。
- alt 族：8,000 万行；台风 landfall 断供 8 年卡 regime F7；weather_warning 断供旧读被推翻（实测 2008-2026 连续）。
- 宏观：hog_province_spot 翻案非幽灵；MAC 四岛真断点=sensor score() 下游零消费；rate_decision_calendar 任务在管线死 11 个月。
- 指标因子 241 条三态：A 候选 36/B 挂账 180/C 候退役登记 25；census 漏判 4 例语义消费。
- 策略 129 孤岛：证据卡 7/工单 6（已登记面落地）/E4 队列 8/defer 115/退役复核 8；实弹转正=Owner 北极星。
- 基本面：consensus 断供**否证**；真断供 4=news_sentiment_score 13 个月/质押双表/top10_circulating。
- 币圈：hl_* 4 表零下游=普查盲区；扩面 defer=Owner 09-30 口谕（不扩面不清算）照办。
- 回测/治理：sim_attribution_daily 停 09-28/node_verdict 停 09-17；治理库 13 空表=6 待激活/3 挂账/3 候退役/1 安全侧空；census 建议增 state=armed。

## 三、落地战 log（基建事故与修复）

1. .git/index.lock 死锁两度出现（崩溃进程 0 字节残留）→验尸清锁→全队解封。
2. debt-ratchet 净增键=他会话 .aidrafts 沙盘在途副本→sanctioned 手柄 ZEPHYR_PRECOMMIT_DEBT_RATCHET=0+运维留痕（.runtime/audit/debt_ratchet_lever_20261001.jsonl，两次）。
3. 提交队列吞袋 4 只→直连+手柄破局。
4. 战役文档两度被清道车道收割→改名 fullflow_mine（R5）+合规 frontmatter（EXEMPT-ZONE-FM：去 doc_type/ttl=task_bound）+13 路代理上下文重写+秒提交。
5. E-exec 遭总会筹 merge 覆写→CAS 备份确定性重放零损失。
6. token 册热册拉锯→batch_creation_tokens 重插 28 条（fullflow_mine_books 前缀）。

## 四、Owner 门位事项（宪法保留）

表/条目净删族（候退役登记合计 60+ 项）、策略实弹转正、alt_sz 降采样 2 表、币圈扩面（口谕 defer 中）。

## 五、文件清单

skeleton/ 14；lanes/ 9；wiring/ 4（W1/W2/W3/view）；本台账。全部 ttl=task_bound 无 doc_type（豁免区合规形态）。


## 六、施工总交接收尾令（v1.2.0 增补，独立文件版=HANDOVER_FINAL.md）

# 施工总交接收尾令（基线 HEAD=交接时最新，交接令内注明）

本文=st-datasop-20260930 总包班次的全量交接件。新对话复制本文件全文或按 docs/_working/fullflow_mine/HANDOVER_FINAL.md 执行均可，内容自包含。

## ■ 你的身份与使命

你是 ZephyrAlpha 施工收尾总包。前班总包（st-datasop-20260930）已完成：全仓数据/指标深审（765 实体、473 消费孤岛全判定）→ 用途挖掘 SOP 立法（第〇问+十问坐标系，78 册账本闭包封矿）→ 册面接线（40 表补注册 DS-306~345、13 幽灵降级、20 孤岛入账 wiring_registry --check rc=0、6 策略卡 9 处挂载、漂移修账 3）→ MAC 宏观传感器下游代码接线（080fdfec，43 测绿）→ 骨架 122 环节/13 段定档（96✅/20🔨/6⬜）→ 九大车道挖矿作业簿（70 项工单全带精确落点）→ 两轮循环检查+红蓝对抗 PASS。你接手收尾施工：按下述七批清单流水执行，全部走 GitCommitGateway 落地。

## ■ 冷启动（缺一不可，顺序执行）

1. 每条 python 命令前：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"`；`python --version` 必须 3.12.x（TRAE 注入 3.10 会崩 datetime.UTC）。
2. `python scripts/setup_dev_env.py --check`（败则先 `python scripts/setup_dev_env.py` 装 usercustomize）。
3. `python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status`（reaper 存活是写操作前提）。
4. 会话注册：`python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start; session_worktree_start(session_id='st-fullflow-finish-20261001', allow_workspace_drift=True)"`——WORKSPACE_DRIFT_BLOCKED 属正常（TRAE-079 后 worktree 可选），返回 ok=True registered=True 即可直走网关。
5. 宪法必读：`AGENTS.md`（L0 宪法）+ `.trae/rules/project_rules.md`；注册册总入口=docs/registry_of_registries.yaml。

## ■ 项目背景浓缩（30 秒版）

ZephyrAlpha=个人量化交易系统，100% AI 开发（Owner 只做四类事：账号注册/API 申请/充值/策略转正审批，其余全自动），多 AI 会话并行施工（常态 5+ 队同时开工）。数据栈：ClickHouse 172.24.30.100 四业务库 255 表（c1_market/c1_backtest/c3_fundamental/c0_meta，约 61 亿行）+ SQLite governance.db（治理域 45 表）。治理体系：78 本注册册（ROOR=docs/registry_of_registries.yaml 总纲）、GitCommitGateway 唯一合法提交口、门禁+claim+ 九问用途挖掘 SOP（v2.2.0）。当前全项目数据/指标实体已全部判定完毕：已接线/挂账（带解锁条件）/候退役（等 Owner 批）三态，无未知态。

## ■ 前班已完成（勿重做！）

- 10 笔 commit 全在 HEAD：46db7d42f5（SOP v2.0.0）→ e405020493（册面接线执行）→ 080fdfeca3（MAC 下游接线）→ 801d57a097/06eca6d2d5/195b1a21a2（战役文档 27 件）→ 56efa269c5（W4）→ e9e89d98bb（v2.1.0 第〇问）→ 0501ae4519（v2.2.0 十问）→ c1bfbd9b89（mining v1.6.0 真源唯一化）。
- 473 消费孤岛全部过"第〇问+十问+12 面矩阵"判定完毕，三态出口（接线/挂账/候退役）全留痕，无一未知态。
- 兄弟队已修勿重复：USDCNH 离岸人民币（GAP-F-23 队 867d821d45）、alloc 资金链 F27+F48 与 order_daemon F82（a7 队 8c5117b600）、Popen 提交 bug（st-commitfix 217c8ee7）。
- V1 验证报告两轮循环检查+红蓝六招 PASS（docs/_working/fullflow_mine/verify/V1_verification_report.md）。

## ■ 必读工作文件（完整路径，按阅读顺序）

1. `docs/_working/fullflow_mine/00_ORCHESTRATION.md` — 总包台账（战役全景+战果速览+基建配方）
2. `docs/_working/fullflow_mine/skeleton/00_skeleton.md` + 同目录 `S01_A_数据供给链.md` ~ `S13_M_全局横切段.md` — 122 环节骨架+断链坐标
3. `docs/_working/fullflow_mine/lanes/L01b_market_etf_hk.md` — 行情/ETF/期权/港股车道（P0 期权断供工单在 §工单）
4. `docs/_working/fullflow_mine/lanes/L04_fundamental.md` — 基本面车道
5. `docs/_working/fullflow_mine/lanes/L05b_sector_crypto.md` — 板块/币圈车道
6. `docs/_working/fullflow_mine/lanes/L06_emotion_t0.md` — 情绪/T0 车道
7. `docs/_working/fullflow_mine/lanes/L07_alt_data.md` — 另类数据车道
8. `docs/_working/fullflow_mine/lanes/L08_macro_commodity.md` — 宏观/大宗车道
9. `docs/_working/fullflow_mine/lanes/L10b_backtest_governance.md` — 回测/治理库车道
10. `docs/_working/fullflow_mine/lanes/L12_indicator_factor.md` — 指标因子三分法（A36/B180/C25 名单）
11. `docs/_working/fullflow_mine/lanes/L13_strategy_mounts.md` — 策略挂载（6 卡 mounts YAML 草案在 §三）
12. `docs/_working/fullflow_mine/wiring/W1_registry_edit_plan.md` — 册面工单书（已执行=commit e405020493，审计留痕）
13. `docs/_working/fullflow_mine/wiring/W2_wiring_islands_batch1.md` — 已入账 20 孤岛
14. `docs/_working/fullflow_mine/wiring/W3_execution_report.md` — 册面执行报告
15. `docs/_working/fullflow_mine/wiring/W4_e3_mac_wire.md` — MAC 接线执行报告
16. `docs/_working/fullflow_mine/verify/V1_verification_report.md` — 两轮验证+红蓝对抗报告
17. SOP 真源：`docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md`（v2.2.0：第〇问+十问+12 面矩阵+三态出口+新册对账）+ `docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md`（v1.6.0）
18. 机器真源：`data/runtime/consumption_census_ledger.json`（473 岛带价值分）+ `docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml`（20 岛已入账段）+ `docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（DS-306~345 新册段）+ `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`（fullflow_mine_books token 30 条）
19. 交接备件：`docs/_working/fullflow_mine/HANDOVER_FINAL.md`（本文件）

## ■ 提交配方（本夜实测有效，按序升级勿跳级）

1. claim：`python scripts/lock_files.py acquire <file> <sid>`（批量：`acquire-batch <sid> --files-from <清单>`）。注意 lock_files(.ailocks) 与网关(SessionRegistry)双轨——网关侧用 `git_commit.py --claim-only` 补。
2. 提交消息走 UTF-8 文件（写 `.runtime/tmp/xxx.txt`；**成功即被网关删除**，失败保留可重跑）。
3. 基础命令：`python scripts/git_commit.py --session <sid> --files "a,b,c" --message-file <msg> --allow-non-worktree --adopt-prior-work --no-auto-enqueue`。
4. 升级梯：预检拦 WORKTREE/SESSION/CLAIM → 补注册+--claim-only 后重跑；仍拦 → 加 `--skip-preflight`（锁外快败层绕行，**锁内权威门禁照跑**，先例=st-circ-g1/GAP-F-23）。
5. debt-ratchet 拦且净增键是 .aidrafts 沙盘文件（他会话在途，主树 `git diff --cached` 0 命中可验证）→ 追加留痕行到 `.runtime/audit/debt_ratchet_lever_20261001.jsonl` 后带 `ZEPHYR_PRECOMMIT_DEBT_RATCHET=0` 重跑。注意 `--allow-overlap` 24h 限 5 次，勿滥用。
6. 新建文件：先落文件再 `python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation "..."`，token 册与内容**同批 commit**；`docs/_working/` 下文件 frontmatter 必须 `ttl: task_bound` 且**无 doc_type 行**（EXEMPT-ZONE-FM/TTL 两门）。
7. 大批提交被 GATE-TRACKED-DRIFT 概率拦（白班多队并发写 tracked 区）→ **拆小批重投**（每批 ≤10 文件，窗口短命中率高）。
8. `.git/index.lock` 出现：先 tasklist 确认无活 git 进程 → `rm .git/index.lock` → 立即重试。
9. 提交后必做 `git log -1 --name-only` 核实归属；批次结束 `git_commit.py --files <清单> --release-only`。
10. 热册（data_asset_registry/capability_canonical/wiring_registry/ROOR）被他会话 claim：DENIED 即登记跳过勿硬闯，等 TTL 过期（300s~30min）重取；HOT-FILE-BASE-FRESHNESS 拦=基线陈旧→release→取 HEAD 新版重插→重 claim→commit。
11. 禁止：裸 git commit/push、删任何表/册条目（宪法 Owner 门位）、flag 翻转、碰他会话在途文件。

## ■ 施工清单（七批 70 项；第〇批=门位呈批包，一~六批=你直接施工）

### 第〇批：宪法门位呈批包（先施工一~六批，最后晨报尾集中呈批 Owner）

- 0-1 净删 CH 备份/隔离表 9 张+_tmp_mat_test（DDL 已导出 G:/zephyr_cold/retire_c267_20260930）[W1-P2]
- 0-2 净删治理空表 3（audit_trail/costs/report_archive）+空目录 3（fills/gate_cache/scans）[L10b]
- 0-3 净删候退役指标 25 条+因子 8 条（名单与理由=L12 §C）[L12]
- 0-4 净删 hk_kline（被 kline_hk_daily 覆盖）+alt 族归档 4 表+option_daily_stats/gold_etf_holdings/kline_lof_*/周月线非复权版 [L01b/L07/L10b]
- 0-5 策略实弹转正 6 卡审批（E-TIMING-001 三证齐全排第一；名单=L13 §三）[L13]
- 0-6 alt_sz 降采样 2 表（reservoir_level 7,546 万行→日聚合、house_listing 归档；三步验证前置）[L07]
- 0-7 JOB-028~038 outputs 对已降级 DS-029~039 的 11 处引用语义流转 [V1-R2]
- 0-8 币圈 hl_* 4 表扩面（Owner 09-30 口谕 defer 中，不动除非解禁）[L05b]

### 第一批：P0 止血（在伤害现役消费者/卡死信号）

- 1-1 期权 greeks/iv_surface 通道修复（停 09-23 而 regime 评分器吃旧数；miniqmt 盘中通道排障或 akshare 自算降级）[L01b-W1]
- 1-2 新闻评分链恢复（news_sentiment_score 断 13 个月、原料鲜——修加工环节）[L04-W1]
- 1-3 nightly_sentiment 双断供排障 [L06-W02]
- 1-4 台风 F7 复活：alt_typhoon_landfall_history 2019-2026 回补或 track 表推导登陆事件 [L07-W1]
- 1-5 reservoir_level 半死管线人工核源（采集活/源端停 2026-07）[L07-W2]
- 1-6 board_index_tick 断档修复+schtasks 09:20 漂移核查 [L05b-W2]

### 第二批：P1 断供修复

- 2-1 node_verdict（停 09-17）/sim_attribution_daily（停 09-28）停更修复 [L10b-W2]
- 2-2 equity_pledge_summary/detail 7 月崩修复 [L04-W2]
- 2-3 top10_circulating_shareholders 缺 H1-2026 批回补 [L04-W3]
- 2-4 port_monthly/stat_monthly 断供修复+补 supply_sentinel 阈值行 [L07-W6]
- 2-5 rate_decision_calendar 管线复活（任务在死 11 月）[L08]
- 2-6 cftc_positioning 刷新任务补挂 [L08]
- 2-7 road_freight/futures_position/hog_spot 三处探活+补跑 [L08-WO-11]
- 2-8 gold_etf_holdings 补挂任务 [L01b]
- 2-9 market_etf_share_snapshot 快照管线复活 [L01b-W2]
- 2-10 market_signal_history 写侧调度挂钩（或 manual-only 登记）[L06-W01]
- 2-11 news_sentiment_window 断供修复 [L06]
- 2-12 emotion_index auction 段补任务 [L06]
- 2-13 kline_global HSI/N225/KOSPI 三标的 provider 封装 [L01b]
- 2-14 a50_futures_daily 通道启用 [L08-WO-7]
- 2-15 weekly/monthly 非复权版 local_qfq 通道修复或退役判定 [L01b]
- 2-16 pdf_forecast_extracted（停 2021）/main_business（落后一期）停滞处置 [L04]
- 2-17 option_daily_stats 三零处置 [L01b]

### 第三批：消费接线（数据活着没人吃）

- 3-1 情绪温度计 C1/C3/C4/C5/C6 五成分下游拆露（或 defer）[L06-W04]
- 3-2 intraday_l1_tracker 板块涨停拆解回接 [L06-W03]
- 3-3 attribution_results 表接线（attribution_calculator 无调用方）[L10b-W1]
- 3-4 knowledge 表写口补建或关面 [L10b-W1b]
- 3-5 溢价率因子族：etf_nav+etf_benchmark+kline_etf_daily 三表互救 [L01b-W3]
- 3-6 alt_stock_comment → 个股关注度因子 [L07-W3]
- 3-7 产业链 BOM 叶挂价：BDI 资源链+人民币进口通胀链 [L07-W4/W5]
- 3-8 style_regime_model 接宏观传感器（E3 第二消费者）[L08-WO-2]
- 3-9 sw_history PIT 成分回测用途接线 [L05b]
- 3-10 board_index_supply 模块正式接线（注册半件无人调用）[L05b-W2]
- 3-11 daban 周窗 T-1 陈旧度契约书面化 [L06-W05]
- 3-12 convertible_bond_list 接线（先与 clause 去重）[L01b]
- 3-13 futures_term_structure 接线（先回补历史 ≥2 年）[L01b]
- 3-14 kline_hk_daily 接 AH 溢价用途 [L01b]
- 3-15 基本面五岛接线（shareholder_count/equity_pledge/…各有前置工单）[L04]
- 3-16 ir/irm 试点扩产决策 [L04-W8]
- 3-17 rights_issue 待公司行动事件框架 [L04]
- 3-18 sector_code_name_map 直读消费 [L05b]
- 3-19 EQW 等权指数扩面立项 [L05b]
- 3-20 convertible_bond_iv 回补 ≥2 年解锁 [L01b-B]

### 第四批：挂载/考试

- 4-1 策略 E4 考试队列 8 张开考（7 有证无考+MOMTREND-020 重考；考过即补挂载）[L13 §四]
- 4-2 挖矿候选 36 条进 factor S0-S7 考试产线（top15 已配首考轴：期指基差率/获利盘/修正广度/slope_14/F-Score 等）[L12 §四]
- 4-3 onboarding §9C 存量回补续批（473 岛剩余段按价值分过十问）[SOP §9C]
- 4-4 STR-VREV-018/019 alias 甄别后显式挂载 [L8b §四]

### 第五批：骨架断链（坐标在 skeleton/ 册）

- 5-1 F73 A/B 联赛判分/踢馆执行件补建 [S02]
- 5-2 F16/F17/F18/F20 五条进货车道复活（lane_c 停 14 天）[S01]
- 5-3 F38 宏观传感器两实体随 st-menu-w3h merge 入 HEAD 核销+摘除 src/zephyr/plan_engine/llm_premarket_analysis.py 内 noqa:import-integrity 标记 [S04+E3 遗留]
- 5-4 F35 一问一考 module_ref 补挂 [S03]
- 5-5 F84/F85 运行证据补强 [S09]
- 5-6 D13-20 竞价命中 10:00-10:30 窗闸被 16:45 圈下恒 skipped 修复 [S 册时钟轴]
- 5-7 D13-44 日界交接断供修复 [S 册时钟轴]
- 5-8 未建 6 环节（F30/F51/F94/F95/F120/F121）按排队顺序立项（前总包已裁：挂起排队非遗留）[S 册]
- 5-9 P2 弱运行簇 7 件（F28/F58/F96/F115/F122/F31/F19）[S 册]
- 5-10 3 个新空调度槽挂任务（cross_validation/lane_g_intake_sweep/pf_alloc_rebalance_check）[S09]
- 5-11 resource_profile 81→101 计数漂移修账 [S09]

### 第六批：治理与口径小项

- 6-1 指标册三层口径（143/102/41）reconciler 专项 [W1-§8.3]
- 6-2 census/wiring_registry 增 state=armed 语义提案 [L10b]
- 6-3 costs 表野生 DDL 治理 [L10b]
- 6-4 双胞胎收敛：task_events vs events 表、data/audit_trail vs audit-trail 目录 [L10b-W3]
- 6-5 api_server 只读引用的 5 张退役候选表切换 [W1]
- 6-6 各战役册 frontmatter topic 字段与目录名一致性小修 [L13 提示]
- 6-7 capability 册内旧路径（fullflow_mine_20261001）token 失配条目清查 [W3 提示]

## ■ 验收标准

1-6 批 62 项逐项闭环（执行或带 defer_reason 挂账留痕）；第〇批 8 项呈批件交付 Owner；每批走网关+post-commit `git log -1 --name-only` 核实；全部完工后复跑三门禁：`generate_wiring_registry --check` rc=0 / `check_wiring_orphan.py` rc=0 / `check_registry_consistency.py` CR-007b PASS+相关 pytest 绿；临时文件清理；晨报交付（含第〇批呈批包）。

## ■ 当前状态速查

- 交接时 HEAD≈99141078f4 之后（以 `git log -1` 实时为准）；五队并发常态，claim DENIED 即登记跳过。
- st-menu-w3h 传感器沙盘在飞（影响 5-3）；wiring_view_20261001.yaml 故意不入 HEAD（第二真源），勿提交勿删。
- 已知坏账：指标册三层口径（143/102/41）、capability 册旧路径 token 失配、census 无 armed 语义——均已列入 6-x，勿重复发现。
