---
ttl: task_bound
title: 矿考循环班 R1 车道 L14 台账（TDM-E-L1 大盘总闸 / TDM-E-L1-AGG 市场状态判定 深挖）
created: "2026-10-10"
sid: st-mineloop-20261010
family_id: MENELOOP-CAMPAIGN
---

# R1 L14 台账 — 深挖 TDM-E-L1（大盘总闸，verified/critical）+ TDM-E-L1-AGG（市场状态判定，proposed/critical）

> 任务书真源=`.runtime/tmp/st-mineloop-20261010/MINING_BRIEF_R1.md`；节点定义真源=`config/trading_decision_map.yaml`（L1=389-447、AGG=675-712、状态矩阵=6460-6484、边表=6164-6187/6250-6450）。
> 本轮取数纪律：21:00-22:30 让路通知在册 ⇒ **本车道零新 CH 查询**；所有 `data_window_evidence` 均引在册实测并抄文件+行号，未在册面一律写 `待总包 22:30 后实测` 并把卡标 blocked。

## 六向逐节点账

| node_id | ①上游 | ②下游 | ③算法 | ④后端 | ⑤呈现 | ⑥数据 | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-E-L1 | 7 条判据性陈述逐条入卡/入对照（下表） | Grep 命中 6 处消费面（下 §2） | 近亲卡=TDM-E-L1-AGG 族 4 张 + 战役 L3 前役 2 张（不重复立卡）；三件套已内置（响应曲线分桶/时滞 shift(-1) 条件/牛熊+OOS 条件稳定性） | 读 regime_detector.py（module_ref/MOD-REGIME-001）+ vol_target_allocator.py（MOD-BT-082，TDM:401-403 记名，本轮未读=长尾） | 一句话：总闸输出在仪表盘无独立呈现面（未逐件核实，登记不追） | 逐字段核 5 表，3 处缺段写死（熵表覆盖窗/六段段态历史/成交额列） | 3 | calibration1 + comparison1 + ablation1 | **否**（长尾见 §5） | 2 张 blocked_on_data + 1 张 blocked_on_data（矩阵空档卡） |
| TDM-E-L1-AGG | 9 条判据性陈述逐条入卡/入对照（下表） | Grep 命中 daily_condition_sensor/index_sensor 的 [CONSUMERS] 标 + 边表 8 条出边 | 近亲卡=S5/S2/S3/S4 母卡族与 L3 前役 AGG/02（只替换输入源，不复用其双臂） | 实读 anchored_state_machine.py:9,29-39,98-153（**单轴实现**：dominant 只由 classify_state(vol_pct) 生成，无月/周/日三层合成、无熵仲裁、无滞回、无隶属度） | 一句话：AGG 三件套输出（预算带/六段/路由）在图注中声明 broadcast 全流，未见呈现件级消费卡 | 逐字段核 4 表；在册可考面 2 张已落 preregistered | 5 | calibration3 + comparison1 + ablation1 | **否**（长尾见 §5） | blocked_on_impl1 + blocked_on_data3 |

新卡合计 **8**（写根=`.aidrafts/st-mineloop-20261010/docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/`）：

1. `TDM-E-L1-AGG/calibration/02_四档风险轴前向收益单调` — status **preregistered**
2. `TDM-E-L1-AGG/calibration/03_子信号族到状态轴传导保真度` — status **preregistered**（任务书点名的"总闸合成分↔子信号族传导"未挖面）
3. `TDM-E-L1-AGG/calibration/04_存量博弈量能分位门` — status **blocked_on_data**（成交额列口径未实测）
4. `TDM-E-L1-AGG/comparison/02_锚定四档vs旧hmm概率链双臂` — status **blocked_on_data**（旧链覆盖窗/run_id 分布未实测）
5. `TDM-E-L1-AGG/ablation/03_跨层封顶与对齐加成双臂` — status **blocked_on_impl**（三层合成件不存在）
6. `TDM-E-L1/calibration/02_谨慎度分裂度熵轴保真度` — status **blocked_on_data**（快照表覆盖未实测+写方口径在册矛盾）
7. `TDM-E-L1/comparison/03_六段预算带带内位置双臂` — status **blocked_on_data**（六段段态历史未落台）
8. `TDM-E-L1/ablation/02_状态矩阵空档段路由代价` — status **blocked_on_data**（段态+逐 sleeve 权重帧+activation 注入器三缺）

## §1 ①上游：判据性陈述→卡（逐条，不合并）

TDM-E-L1（algo_note_zh:400-413 / decision_question:398）
- "消费 RegimeSnapshot 7 态概率当谨慎度：概率越分裂越谨慎"→ 卡 6（熵-shrinkage 单调+次日收益 IC）。
- "六段情绪预算带 吸筹30-50/点火50-70/扩张60-80/亢奋封顶30%只卖不买"→ 卡 7（带内位置上/下沿双臂）；"带开关"整体代价已由前役 L1/02 覆盖，不重立。
- "月级定大档、日级水温微调"→ 卡 5（跨层封顶/对齐加成）覆盖月-周-日三层，水温单腿未挖（§5 长尾）。
- "波动率目标化仓位系数（凯利简版：滚动 σ 目标化，MOD-BT-082）"→ **未入卡**（件未读，§5 长尾，禁凭 TDM 记名造判据）。
- "R-055a fail-closed 地板 0.30 / 检测器档 0.80 统一=A16 待 Owner 裁定"→ **不立卡**（代裁档位=越权；两档差已在前役 L1/02 的 FAIL_CLOSED 臂与 fail_closed_cost 柱登记，本车道只补记"档表统一属 Owner 面"）。
- "裁定#304：r4/r10/r1 无稳定方向信息，谨慎度按风险分档口径读"→ 卡 1（四档风险序单调）+ 卡 6 的 dominant_leg_audit 柱。⚠ 编号 #304/#229 只出现在 TDM 文本与源码注释，**ruling_registry.yaml 未在 config/ 寻得**（`Glob config/**/ruling_registry*.yaml` 零命中）⇒ 本车道卡面一律引"文件+行号"而不引裁定编号署名，防伪署名。
- strategy_mounts 六条 evidence（三窗数字 SCR-*）→ 属分数册面，不作卡（禁写分数册）。

TDM-E-L1-AGG（decision_question:691 / algo_note_zh:693-700 / 注释 684-690）
- "双轴相乘，一致取结论，分裂按就低不就高，缺数最谨慎"→ 卡 2（传导保真度）+ 卡 5（仲裁与合成规则代价）。
- "熵高→分裂市降档"（阈值未给数）→ 卡 6（熵轴先验冻结）承载可判面；降档动作在卡 5 冲突柱。
- "四层架构：月7态/周六段/日 S5 三温度计独立 + 封顶 + 对齐加成"→ 卡 5。
- "D90 六段冲突=听弱的（废除人工接管）"→ **部分入卡 5**（conflict_rule_cost 柱取下限）；"听弱 vs 听强"双臂需逐日两轴读数，读数面=卡 4 同款缺段，登记为 §5 长尾（不拆成半成品卡）。
- "D90 量×轮动二维状态机：成交额 250 日分位<25%/60%"→ 卡 4。
- "D90 轮动强度>80% 分位=电风扇市"→ **未入卡**：轮动强度无历史落台 + 代码阈值 0.75 与册上 0.80 在册不一致（见 §6 假绿 3），阈值孰是未定，不代拍。
- "D90 二值权限门滞回：进段连续 2 日隶属度>60%、退出<40%"→ **未入卡**：源码无任何隶属度/滞回实现（anchored_state_machine 全文只 classify_state），无载体系；折入卡 4 的 dwell 柱只建档，完整双臂列 §5 长尾。
- "AGG 消费切换 2026-09-23（锚定四档，回滚窗至 2026-10-23）"→ 卡 4 之外单列卡 4bis=卡 4 编号 4 即 `comparison/02`（新链 vs 旧链双臂）。
- "策略路由阈值未冻结暂不接线"→ 不立卡（禁代拍未冻结阈值），登记为在册冻结缺口。

## §2 ②下游 Grep 命中（消费方，逐条）

- `src/zephyr/signal_ashare/core/daily_condition_sensor.py:5` `[CONSUMERS] … TDM-E-L1-AGG（四层温度计日级输入）`
- `src/zephyr/regime/features/index_sensor.py:5` `[CONSUMERS] … TDM-E-L1-AGG（L1 聚合输入）`
- 边表出边：`trading_decision_map.yaml:6171`（AGG→L1 decision）、6181/6289/6299/6347（→L2-05-1/P3-01/P2-01/X-S1-04 state）、6250/6251/6266（→P-P1/X-S1/F-C1 governance broadcast）、6361（→L0 体温单）、6389（→F-C1-01 体制态路由）、6430（→L9-V2 情绪相位）；入边 6164-6167/6183/6187（S1-S5/S0 feed，pit_proof 全 `legacy-unaudited`）→ 卡 2 即对该未审计边的机检。
- 表级消费：`strategy_pipeline/screen_source.py:48` `SNAP_TABLE="c1_backtest.regime_snapshot_history"`、`strategy_pipeline/daily_gate_snapshot.py:40,120-126`（L1 PIT 读快照）、`strategy_factory/owner_band_t/regime_gate.py:17,45`+`owner_regime_switcher/data_loader.py:22,108`（run_id 钉死 PINNED_RUN_ID）、`pf_alloc/crisis_gate.py:12`（危机判定从 CH 现读零内存态）。
- 已考面：`TDM-E-L1-S2` 14 卡（13 examined 全 fail，任务书 §3）⇒ 本车道未重复任何广度单腿假设。

## §3 ③④ 后端读件结论（关键）

- `src/zephyr/regime/core/anchored_state_machine.py`（AGG module_ref，MOD-REGIME-001）：**四档由 vol_pct 单轴生成**（行 98-110 classify_state、136-153 build_states），阈值 0.30/0.60/0.80 硬编码结构值；头注释行 29-31 自带可推翻命题（"唯一双段稳定轴=波动率风险轴"）→ 卡 1 直接把它转成机判面。
- 未挖实现在册缺位：三层合成/封顶/对齐加成/熵仲裁/滞回/隶属度 **全部无件**（卡 5 blocked_on_impl 凭此）。
- `regime_detector.py`（L1 module_ref）本轮只读列清单来源（`scripts/backtest/print_regime_history.py:59-74` 给七态键与全列名），未读检测器内部 shrinkage 生成分支 → §5 长尾。
- `vol_target_allocator.py`（MOD-BT-082）未读 → §5 长尾。

## §4 ⑥数据面逐字段核（在册/待测，禁自创数字）

- 可即用：`c1_backtest.regime_state_anchored` 2017-07-11..2026-10-09/4,488 行（close/ma20/ma60/ma120/vol_pct/dominant/data_source/ingest_ts）；`c1_market.kline_index` 1990-12-19..2026-10-09/3,104,162 行/1,097 symbols，000300/000905/000852/399006 各 1,843 行覆盖 2018-06-01..2025-12-31；`c1_market.emotion_index` stage='close_final' 2019..2025 逐年 244/243/243/242/242/242/243 天（components 含 C1_limitup_temp/C2_promotion，source='daban_board_event'）——全部出处=L1/02、AGG/02、S3/06 三张在册卡的 data_window_evidence 行号，已在卡内逐一抄明。
- 在册断供/缺口（照抄任务书 §3 并按卡面写死）：emotion_index 10 月仅 pre_open 腿且 close_final=0 ⇒ OOS 终点保 2025-09-09 不延展；`c1_market.limit_up_down` 2026-07-20..2026-10-09/5,397 行/54 天（冻结窗零行）；`daban_board_event` 仅 2026-09-01..2026-10-09/1,767 行；sector 881/8803 深史上限 2021-08-02；涨停回放诚实上限 2019-01-03。
- 待总包 22:30 后实测（卡内已给命令原文）：regime_snapshot_history 按 run_id 分组的覆盖窗与行数；kline_index 成交额列名/单位与 000001/399001 行存在性；六段段态逐日落台表名与列；AGG 输入消费日志（无件需新建）。

## §5 未挖长尾明列（禁封矿）

1. `TDM-E-L1`：日级水温微调对月级大档的**边际增量**单独一卡（卡 5 只判跨层规则整体，未隔离日级腿）。
2. `TDM-E-L1`：凯利简版滚动 σ 目标化输入质量（件 `vol_target_allocator.py` 未读，读完可立"σ 估计→实现 σ"保真卡）。
3. `TDM-E-L1-AGG`：D90"冲突听弱 vs 听强"双臂（读数面=段态历史，解锁同卡 4/卡 7）。
4. `TDM-E-L1-AGG`：二值权限门滞回（进 2 日>60%/退<40%）vs 直切——无隶属度载体，需先建落台面。
5. `TDM-E-L1-AGG`：策略路由阈值未冻结（在册原文），待 Owner 面定数后才可立卡。
6. `TDM-E-L1` 的 6 处 strategy_mounts evidence（SCR-* 三窗数字）→ 属分数册复考面，非本车道权限。

## §6 假绿风险（本车道发现，如实上报，未代修）

1. **同名不同义**：`dominant` 列在两链语义冲突——锚定链 r3=低/r2=中/r1=中高/r4=高风险（anchored_state_machine.py:36-39），旧 HMM 链状态键 r1,r2,r3,r4,r10,r11,r12（print_regime_history.py:64）。下游按名消费（screen_source.py:48、owner_band_t/regime_gate.py:17 读旧链）存在**静默错档**风险；卡 4 把两臂映射固定为"各用各表列"以隔离，但这是治理面，非本车道可修。
2. **写方口径自相矛盾**：pipeline_events.py:1033 称快照表"唯一自动产出者=maybe_refresh_regime_snapshot"，fw_backtest.py:71 称"唯一写方=print_regime_history.py（manual CLI）"——同一张表两行冲突，在册文档矛盾=事故（根宪法 §4.3 精神），需总包核实。
3. **阈值漂移**：电风扇市册上 80% 分位（trading_decision_map.yaml:690）vs 代码 `VELOCITY_PERCENTILE_THRESHOLD=0.75`（boundary_revision_engine.py:117）。
4. **未审计边**：S1/S2/S3/S4/S0/S5→AGG 六条 feed 边 pit_proof 全 `legacy-unaudited`（6164-6167,6183,6187），而代码实测 AGG 只吃 vol_pct——"消费六路"的叙事与本卡 2 的实测面若不吻，卡 2 就是那把尺（预计 fail，fail 即真相，非本车道成绩）。

## §7 交叉复挖建议（20% 名单，含"前役封矿不成立"具体点）

- `TDM-E-L1-S1`（前役仅 2 卡）：D109 攻防板块特征（券商/银行 5 日超额、券商÷银行涨幅比>1 且放量=进攻态）在 algo_note:474 是**在册判据、零卡**——建议复挖，判其封矿不成立。
- `TDM-E-L1-S5`（前役 2 卡）：11 信号里 A6"红盘家数<1500 绝对回避"、A5"昨日溢价<=-5% 退潮"两条绝对阈无卡；且"同源指标重复计票→相关性去重"（TDM:580 在册自述风险）未考。
- `TDM-E-L1-S4`（前役 4 卡）：SVX-1-P0 事故（delta 恒 0 ⇒ ATM 筛子排除 9653/9653、主路径半年零产出静默回退，TDM:554-557）——"主路径可用性"本身可立卡，前役只考了读数面。
- `TDM-E-L1-S0/S0-1`：宏观四组（A/B/C/D）与"政策/产业因子权重↑、总量因子权重↓"的范式修正（TDM:586-589）无权重卡；S0-1 有 2 卡但 news_data 断崖（2025=31,427 vs 2024=759,512，任务书 §3）使长窗卡须复判 blocked。
- `TDM-E-L2-05-1`：AGG→L2-05-1 的"封顶"边（6181）在册而对应卡缺（本车道卡 5 覆盖合成规则，未覆盖 05-1 消费侧）。
