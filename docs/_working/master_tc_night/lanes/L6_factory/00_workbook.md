---
ttl: task_bound
title: "L6 全流通工厂车道作业簿（st-mastertc-l6）"
created: 2026-10-07
sid: st-mastertc-l6
session_worktree: .aidrafts/st-mastertc-l6
---

# L6 车道作业簿（11 卡+L11 移交 1 件）

> 模板=00_orchestration §四：每卡六向台账（①卡面处方 ②HEAD 现状实证 ③上游依赖 ④下游消费者 ⑤冲突面 ⑥残余与移交）+自审闸三态+施工记录。
> 施工域=worktree `.aidrafts/st-mastertc-l6`（session_worktree_start 注册，allow_workspace_drift）；文档面在主区（--allow-non-worktree，2026-08-13 裁定默认）。

## C46 二期序列余项定性（F42/F43/F45/F46-F47）——GREEN，已定性落本册

- ①卡面：00_workorders §四逐项定性；②实证：daily_loop_master_switch.py 对 position_triage/thesis_survival/position_drift_monitor/t_trade_coordinator/t0_trading_pipeline/s1_scan_orchestrator **零命中**（grep 计 0）；s1_scan_orchestrator.py 在 HEAD（30477B，07427f41c0 落）；③上游=各 per-F 卷挖干判读；④下游=二期排产班；⑤冲突=无；⑥残余=四项全大件（编排面 >2h）。
- **自审闸 GREEN（定性卡）**：F42 体检编排=体检五件纯库挂机（P1-06 分配语义已接），大件→**排期登记**；F43 做T统一调度=零自动化触发（t_trade_coordinator 3 文件全 paper 族内），大件→**排期**；F45 S1 扫描=**扫描器已落地销账**（07427f41c0：s1_scan_orchestrator 738 行+18 测+出仓件；余项=X 流消融实弹 G45-2 待 Owner 放行+回测接入，**排期+Owner 门**）；F46-F47 离场执行编排=S2-01/03/05 码成闸空（唯一活线=local_order_queue 半接线+kill_switch 横切在岗），大件→**排期**。

## C232 事件轴显式层——GREEN，已施工

- ①卡面：波10 G-B.3（封板/炸板/busted 事件枚举+缠论轴引用既有 chanlun）；②实证：7 件基座在 src/zephyr/signal_ashare/limit_up/，无事件轴件；③上游=limit_up_followthrough 双池口径；④下游=L02 c1/c2 簇候选；⑤冲突=无；⑥残余=缠论轴正交引用（CHANLUN_AXIS_REF 常量），不重复实现。
- **施工记录**：event_axis.py（MOD-SIG-146，SEALED/BUSTED/BROKEN 互斥单选+frozen dataclass）+13 测绿；翻译+depgraph 16408444；袋=q-20261007-st-mastertc-l6-0001。

## C234 摆动结构序列——GREEN，已施工（C253 同批）

- ①卡面：波10 G-C.2 LH/HL 双峰检测，禁第二套极值算法；②实证：chanlun_structure.py（MOD-SIG-072）分型链在库；③上游=chanlun 分型；④下游=C235 共振定义器；⑤冲突=无；⑥残余=left/right>1 广义 TV 确认窗不在本层（口径声明在 docstring，扩参归 chanlun）。
- **施工记录**：swing_sequence.py（MOD-SIG-147，复用 analyze_chanlun 分型做序列标注）+12 测绿；**C253 落格**=TV 枢轴口径（left/right bars 对照+包含处理差异）显式标记于模块 docstring；镜像测试三纪律（StatOasis：镜像对称/最小样本门槛/全网格一致性）写进单测头注并三面落地；翻译+depgraph 16408445；袋同上。

## C235 共振定义器——GREEN，已施工（C252 同批）

- ①卡面：波10 G-C.3 15M 上沿×1M 双峰组合判定，READY_NOT_FIRED 不点火；②实证：C234 双峰件新落可消费；③上游=swing_sequence；④下游=共振矩阵统计面（候选）；⑤冲突=无；⑥残余=点火面归下游（fired 恒 False 铁律字段载体）。
- **施工记录**：resonance_pair.py（MOD-SIG-148，三前置齐备判定+四态显式降级）+12 测绿；**C252 落格**=docstring 选型口径三声明（trendln 思想自实现零依赖/merge_asof 已落归 G-C.1 跨周期层不重做对齐/不引 pandas-ta 2026-07 归档风险）；token 三条带 no_mount_reason（研究面消费位未定禁造假）；翻译+depgraph 16408446；袋同上。

## C75 CNS 消费接线——GREEN，1 件接线+2 条销账/处方，余登记

- ①卡面：CNS-01~14 选 2-3 条纯代码接线（优先 cn_macro），其余处方登记，禁造假消费；②实证：cn_macro 已有真消费（regime/features/macro_regime_sensor.py 565 行+macro_indicator_series_map.yaml 16 条，NB1-B5 R2-R3 前班 09-30 落）——**census §⑤"cn_macro 零引用"读数陈旧，销账注记**；CNS-01 实态=indicator_reader 与 multifactor_synthesis 两层在库各有消费（ex_core/signal_providers 消费合成层）但**中间"宽表→因子值"腿零代码**（L3 生产可达=0 根因实锚）；③上游=TechnicalIndicatorRegistry 214 列白名单；④下游=ex_core signal_providers 升级候选+分析入口；⑤冲突=无；⑥残余=IC 证据（≥3 条 FCT-TECH）须 CH 实弹跑批——链可达≠证据在册，禁造假，归 91 §③-5 CH 复活实弹批。
- **施工记录**：tech_factor_pipeline.py（MOD-L02-031，build_tech_factor_values+synthesize_tech_signal 一键链，PIT 透传+白名单双校验）+10 测绿（monkeypatch 零 DB）；翻译+depgraph 16408447；袋=q-20261007-st-mastertc-l6-0002。
- **其余 CNS 处方登记**：CNS-02 退役听证（机账 zero=114 逐条）→排产；CNS-03 block_trade_detail 建/退评审→排产；CNS-04 sw_daily 腿零引用仍开口（cn_macro 腿已销账）→二期评审或退役；CNS-05 基本面 ZERO 标签+restricted_shares 落码→排产；CNS-06 kline 口径归一裁定→L10；CNS-07 情绪成分治理→排产；CNS-08/09 alpha_sources/belongs_to 机械回填→排产（生成器件）；CNS-10 ipo/index_adjust 过滤器入 universe 链→排产；CNS-11 auction 因子接线（266k 行在库）→排产；CNS-12 北向因子立项→排产；CNS-13 零客老表死亡证明批量→w5_1 退役通道；CNS-14 机账 schema v2 分列→排产。

## C400 接线普查宽口径——GREEN，已产册

- ①卡面：34 环节触发面清单，逐项三态；②实证：机械筛规则 A（per-F 卷"自动化触发"行非零，F100-F132 中 23 环）+规则 B（环节名触发语义关键词，11 环），A∩B=∅，**34=23+11**；③上游=night_sweep 总表+fullconnect per-F 卷+recovered inventory §1.6；④下游=排产班/触发面补线班；⑤冲突=无；⑥残余=34 册中 7 待接线（F013/F014/F082/F084/F110/F122/F129）为净新增指证。
- **施工记录**：`lanes/L6_factory/34_trigger_surface.md`（已接线 22/待接线 7/不适用 5，逐项证据锚）。

## C383 F123-F132 四态缺口二期排程——GREEN，已回填

- ①卡面：91_progress 终局清单追加"二期排程登记"节，F124/F129/F131/F126 四行各一处方指针；②实证：00_skeleton_verified 定版行+C400 触发行四态复核；③上游=91 §③-3（F125/F127/F128/F130 已在案不重复）；④下游=二期排产班；⑤冲突=91_progress 已 claim（st-mastertc-l6）；⑥残余=无。
- **施工记录**：safe_write_text CAS 回填四行（F124 词表生命周期编排/F129 训练线触发链立项/F131 三跳链直连化+哨兵并卡/F126 字段字典 align_all 常规轴化）。

## C106 W6-M 拒认领核对——GREEN（诚实降档），已补定性

- ①卡面：20 拒认领逐条核对，缺理由的 3-5 条补定性行；②实证：**逐格拒认领账本机面不可复得**——对账尺无拒认领字段（重跑实测 declared-but-uncovered=0），24+20 分账仅存 §五散文；③上游=W6-M 判据收紧卷（wiring_M_meter_hardening.md）；④下游=W6-M 继任收紧班；⑤冲突=96 报告已 claim；⑥残余=逐格账本回补归原声明车道。
- **施工记录**：safe_write_text CAS 追加 §五-附录（账本定位披露+尺面重跑诚实读数 covered60/uncovered62+5 条代表格定性：F57 已收敛/F56 墓碑/F60-F61 K 袋已落/F74 真缺口开口/F117-F119 类目错配）；随袋重生成 91_machine_crosscheck.yaml（STALE→fresh，96 §七遗留簿务缺陷自愈）。

## C191 P2 销账台账——GREEN，已产册

- ①卡面：22 条缺口×状态防两战役重复立卡；②实证：INDEX 汇总行 22 与行内枚举 24 与簿列逐条 23 三口径不一致（计数漂移，文档纪律 §4.3 登记）；③上游=L02_emotion 12 簿 MINE.md；④下游=decision_map 二期排产+本夜继任班；⑤冲突=无；⑥残余=并组建议 23→19。
- **施工记录**：`lanes/L6_factory/p2_card_ledger.md`（23 行逐条+防重复立卡规则+并组建议；以簿列逐条为准，汇总行勘误登记）。

## L11 移交真债：test_strategy_card_lifecycle_map_adversarial 3F——RED，部分修复+移交

- ①卡面：3F 若 D15-S1 锚被归档致，修锚注册或更新期望（真源为准禁白洗）；②实证：3F=结构面 rc!=0（原 3 违规=D15-S1 锚×2+CV-HOST 欠账）；锚真源盘面**正在被他班重排**（emotion_line 归档后又移回原位；sector/t0 仅存 archive/2026-10/）——三次落地尝试内：锚路径改现盘真态（emotion=原位/sector+t0=archive）后 D15-S1 锚错全消；为清 CV-HOST 重跑机生器（欠账 10→9）但机生器从骨架上游（fig15_cardlife/01_状态族前段.md 证据行）**回灌旧路径**；③上游=fig15 骨架证据行+卡注册批；④下游=docs 归档浪班+L11 继任；⑤冲突=config/strategy_card_lifecycle_map.yaml=他会话 MM+stomper 战在飞（本会话修复两次被 clobber 实证）；⑥残余=移交处方见下。
- **移交处方（继任班三步）**：①等 docs 归档浪落定后改 `docs/_working/map_build/fig15_cardlife/01_状态族前段.md:37` 等证据行路径到实存位；②重跑 generate_strategy_card_lifecycle_map.py（机生幂等）；③CV-HOST 欠账 9 项（emotion/sector/t0 系 prereg 卡+L05_t0 双胞胎）随卡注册批逐卡判态入册——登记属判态工作非机械活，禁白洗清账。
- **自审闸 RED**：config/strategy_card_lifecycle_map.yaml 本会话不提交（他会话 MM stomper 战在飞，§3.4 不代修不抢跑），本会话改动留在盘面随其落地窗收敛。

## OPEN_QUESTIONS

1. C106：逐格拒认领账本（24+20）真源在哪？仅散文可考——若 Owner 认为该账必须机读化，需 W6-M 声明车道补交账本文件（本车道不臆造）。
2. L11：strategy_card_lifecycle_map 的 docs 归档浪与 fig15 骨架证据行的真源归属班次待 Owner 指认（现两班互相等）。
3. C75：IC 证据验收（≥3 条 FCT-TECH）绑 CH 复活实弹窗——排期归 91 §③-5 批还是二期序列，待排产班定。

## CONFLICT_LEDGER

| 文件 | 冲突 | 处置 |
|---|---|---|
| docs/01_.../capability_canonical_file_registry.yaml | st-mastertc-l0 锁定（stomper 战 36 条在飞），本会话 token 6 条写入后遭 clobber 一次（13596→13594），已 CAS 重放存活 | token 随主区在飞面落地；worktree 副本已含同批 token 随 q-0001/q-0002 袋落（双写保险，_collect_registered_files 集合去重无冲突） |
| config/strategy_card_lifecycle_map.yaml | 他会话 MM+stomper 战（本会话修复两次被 clobber） | RED 不提交，移交处方见 L11 节 |
| docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml | 生成物 STALE（96 §七既有病） | 本日重跑自愈（fresh），随 docs 袋落 |

## DONE_SUMMARY

| 卡 | 闸 | 交付 | 袋/锚 |
|---|---|---|---|
| C46 | GREEN | 四项定性（F45 销账+三排期+Owner 门） | 本册 |
| C232 | GREEN | event_axis.py+13 测 | q-0001 |
| C234+C253 | GREEN | swing_sequence.py+12 测（TV 口径+镜像三纪律落格） | q-0001 |
| C235+C252 | GREEN | resonance_pair.py+12 测（选型三声明落格） | q-0001 |
| C75 | GREEN | tech_factor_pipeline.py+10 测+cn_macro 销账+14 处方 | q-0002 |
| C400 | GREEN | 34_trigger_surface.md（22/7/5） | docs 袋 |
| C383 | GREEN | 91_progress §二期排程登记四行 | docs 袋 |
| C106 | GREEN | 96 报告 §五-附录+crosscheck 自愈 | docs 袋 |
| C191 | GREEN | p2_card_ledger.md（23 行+并组 19） | docs 袋 |
| L11 | RED | 锚真态修正存活+机生欠账 10→9+三步移交处方 | 盘面/移交 |

测试读数：三新模块 37 测+CNS 链 10 测全绿；adversarial 套件 12 passed/3 failed（RED 移交，见上）。
