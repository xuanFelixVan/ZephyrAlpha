---
created: 2026-09-26
ttl: task_bound
volume: 93_true_gap_list_20260926
session: st-ailayer-final-20260924
creation_token: fullflow-true-gap-list-20260926
---

# 93 真缺清单（诚实态＝无簿可指的环节，一行一格，只登记不认领）

> 口径＝机生尺改为"只认正向声明位"（文件名 `fnn`／册标题行／`本册覆盖` 行／`covers:` 行）之后，**仍没有任何作业簿以该环节对象为主题**的环节。
> 反自绿声明：本册与 94 记录册被尺当作业簿扫时**零认领**——全册不写任何以 `#`、`本册覆盖`、`covers:` 起头且含环节号的行（编号一律落在表格行内），文件名也不含 `fnn` 段。续表者请守此格式，否则本册会把列出的缺口自己洗成已挖。
> **车道分区**：§一＝W4-F1（本道 8 格）；§二＝W4-F2（**重建件，非原文**）；其他车道请在 §三 之下按同格式续表，**勿改他人行**。
> **⚠ 事故登记（2026-09-26 03:31，W4-F1 责任）**：本册由 W4-F2 于 ~03:30 首建并写入其 12 行；W4-F1 未先盘上核实即整档 Write ⇒ **F2 原文 12 行被覆盖丢失**（git 无 HEAD/无 index 记录，全盘 `find` 仅此一份，`.runtime/sessions` 无副本＝不可恢复）。现 §二 为 W4-F1 依 `95_declaration_pass_F2.md` §三 重建的**降级版**（只有该册明写的理由），其余以"原文丢失"占位。请 F2 车道覆写 §二 恢复全文；总筹请以本行＋94 册 §五 为事故凭据。
> **并发教训（写给他道）**：本窗内多车道同时向同名新件追加 ⇒ Write（整档覆盖）禁用于共享件，一律先读后 Edit 追加；同窗已见 `m1_data/01_ingest.md` 被他道同法改写过一次。


## 一、W4-F1 车道判 B 的 8 格

| 环节 | 为什么算真缺（"提过一句"不算簿） | 要开哪本（新簿主题，暂名） | 建议车道 | 本车道实测到的相邻证据＋为什么不够 |
|---|---|---|---|---|
| F07 | PG 架构库的 schema 应用面/版本台账/回滚面/校验面四面**没有一本作业簿**；现有深证全在 `05_missing_p0/` 的取证页与接线册里（那是"环节终数该怎么定"的分析面，按 92 指挥册 §一 与尺的 NON_WORKBOOK 口径＝非作业簿，禁加声明位） | `m3_governance/08_pg_architecture_library.md`（主题＝`depgraph_schema.apply_pg_schema`→`02_create_pg_schema.sql`→`_schema_version` 台账→`backup_pg_architecture` 回滚→GATE-C2/G_TRAE_059 校验，含"入口建成零调用方"断链复测） | M3 治理 | `05_missing_p0/04_p1p3p5_evidence_pages.md` §PG 架构库 4 行（file:line 级）＋`wiring_E_anchor_register.md` §F07 补锚行——两页均已被尺列为非作业簿/取证面；`04_knowledge_supply/f32`、`f36` 只在 §七 复核命令里 import `get_depgraph_pg_connection`（工具用法，非对象）；`m4_ai_layer/04_meta_question_pg.md` 的对象是 PG 283 问，异对象不并 |
| F59 | 风控限额册本体（`risk_limit_registry` 九类 117 条）与 ATR 止损引擎本体全仓作业簿**零命中**；`m7_live_execution/02_kill_switch.md` §一 边界行自注"kill_switch 注册表限额面（62 条）→M3"，M3 侧实测亦无该册 | `m7_live_execution/07_risk_limits_and_stop_engine.md`（主题＝REG-RLM-001 限额九类逐类落码面＋`risk_manager.py`＋`atr_stop_engine.py`＋与 F60/F61 的仲裁点） | M7（限额注册表面与 M3 合流） | `atr_stop`／`risk_limit_registry` 在全部作业簿里的实测命中＝0（只在 `00_skeleton` 两册与 `m1_data/05_tdm_crossaxis.md` §三"风险限额库 RLM＝risk_limit_registry.yaml／R33／12"一行轴登记——且计数 12 与总册口径 117 冲突，属登记面不是执法面）；`02_tdm_decision/f42_p1_position_checkup.md` §二 有止损触发 7 种/严重级/亏损限额三档（读 `ashare_stop_loss_engine.py`）＝TDM 节点判定语义，其 §八 也只 grep 该件，未挖限额册与 ATR 腿 |
| F60 | 回撤分级状态机三件的**工程面**（触发者/落盘/双保险互锁）无簿；唯一逐件在册的是 `02_tdm_decision/14_f47_r1_emergency_lifeline.md`，而该册 §一 分工行自己写明"drawdown 全家桶与 kill switch 三实例的工程面归 M7/RC 车道（已挖干）；本册只管 TDM 节点判定语义与消费面"——在 M7 实测无该簿的情况下给这册加声明位＝替一本明示不认领的册硬认领，且替一句无簿可指的"已挖干"背书 | `m7_live_execution/08_drawdown_state_machine_and_guards.md`（主题＝`risk/core/drawdown_state_machine.py`(MOD-RK-049)/`drawdown_liquidation_guard.py`(MOD-RK-050 零外部消费)/`drawdown_broker_side_stop.py` 三件与 F63 NAV 分级入口、F47/F59 仲裁） | M7／RC | f47 册 §三 六向台账（自动化触发＝`daily_gate_snapshot`/`session_persistence`；真源＝DAL-CIRCUIT-5）＋§四 三件行（含行数与消费方）＝**判定语义面充分、工程面自认不管**；M7 目录 grep `drawdown` 只命中 `02_kill_switch.md` §二 上游一行与 `03_position_sell.md` 的 `position/core/drawdown_controller.py`（仓位侧，异对象）⇒ 记 B 不记 A |
| F64 | 三件套"每测 MUST 指定"的**执法面**（谁在跑前强制选 universe/benchmark/cost_model、缺指定怎么拦）无任何作业簿；两本被上一班补过锚的册（`m2_backtest_sim/02_backtest.md`、`05_cost_gates.md`）自己写的是"回测入口契约面""cost_model 门半面"＝半面，且其声明行以 `> 覆盖锚点：` 起头、新尺根本不认（格式失效，见 94 册 §四.1） | `m2_backtest_sim/08_three_registry_enforcement.md`（主题＝universe/benchmark/cost_model 三册条目数与版本、`decision_map.py` 校验器缺册即红的复跑、跑前 MUST 指定的 gate 本体） | M2＋M1 交叉轴 | `m1_data/05_tdm_crossaxis.md` §三 三行（UNI 宇宙库 R30/4、BMK 基准库 R35/4、CST 成本模型库 R31/4）＝TDM 轴登记面；`m2/02` §一 与 §二 真源行只提 `CST-ASTOCK-001`；universe/benchmark 执法面在作业簿内零 file:line ⇒ 半面不整格认领 |
| F65 | 回测引擎族本体（事件驱动引擎＋CH tick replay＋撮合内核＋组合核算）无簿：`ch_tick_replay` 全仓作业簿命中＝0（只在 `00_skeleton` 两册）；撮合内核只在别册病灶里挂名 | `m2_backtest_sim/09_backtest_engine_core.md`（主题＝`backtest/core/matching_engine.py`+`matching_logic.py`+`ch_tick_replay.py`+组合核算与净值口径，含"回测=模拟=实盘"三处撮合一致性对照） | M2 | `m2_backtest_sim/03_sim_daily.md` §四 病灶 5（"撮合面＝回测撮合=`zephyr/backtest/core/matching_engine.py`+`matching_logic.py`"一行，属堵点陈述）；`m2/02` §三 2.4 只读 `MatchingConfig` 成本；`m2/06` §二 上游行只点名 `vectorized_engine`（向量化考尺，非事件驱动引擎）⇒ 无六向 |
| F66 | 回测预注册与七步循环（`backtest_backlog` 137 对象跑前写死阈值、无注册不归档、`sop_a`/`sop_b` 七步）无簿；`generate_backtest_backlog` 在作业簿里只出现在一句"可合并"的堵点建议中 | `m2_backtest_sim/10_backtest_preregistration_seven_steps.md`（主题＝`scripts/backtest/generate_backtest_backlog.py`＋backlog 137 对象口径＋`backtest_system_sop` sop_a/sop_b 七步闭环＋"无注册不归档"的门） | M2 | `m2/02_backtest.md` §四 堵点 1（三件都绕 run_archive 转、可合一个 CLI）＝合并建议；注意别把 `m2/04` §三 4.1 的 `config/search_space_prereg.yaml`（GPU 搜索预算闸）当本环——两 prereg 不同对象，混用即假绿 |
| F67 | 实验登记与档案（`experiment_registry` 11 条＋FallbackBackend＋Panel 实验 Tab）无簿；现有两行都是"谁在写/零消费"的旁证 | `m2_backtest_sim/11_experiment_registry_and_archive.md`（或 M6 侧合册：登记表 11 条逐条、写入者、FallbackBackend 兜底路径、前端实验 Tab 消费面） | M2（前端腿 M6） | `m2/02_backtest.md` §二 下游消费行（`eval_exp_expectations`→`experiment_registry EXP-FACTOR-EVAL-*`）＝出口一句；`m6_frontend/补挖波_20260925/04_reporting.md` §三 `attribution_registry_mapper`→experiment_registry "零"＝消费普查一行 ⇒ 皆非主题 |
| F70 | 模拟撮合与偏差检测（涨板队列撮合＋前视偏差检测＋过拟合保护门＋DSR，`src/zephyr/simulation/`）无簿：唯一挂名处是 `m2_backtest_sim/06_ibt_backtest.md` §三 6.6 一行（该册主题是 IBT 整装回测四窗/协议/红蓝），涨板队列撮合全仓零命中 | `m2_backtest_sim/12_simulation_matching_and_bias_detectors.md`（主题＝`simulation/` 7 件逐件：`look_ahead_bias_detector`/`overfitting_protection_gate`/`deflated_sharpe_calculator`/`pit_manager`…＋涨板队列撮合与不可成交建模＋DSR 与 n_trial 台账关系） | M2 | `m2/06` §三 6.6 行（`src/zephyr/simulation/`（ls 实测 7 件）＋`backtest/core/`（6 件），判"绿"）＝一行级；grep `涨停队列`/`涨板`/`zephyr/simulation` 在 m2 各册＝除该行外零命中；`m2/03` 是模拟盘日链（plan-bridge/账本/日刊），与本环撮合内核异对象 ⇒ 记 B |

## 二、W4-F2 车道判 B 的 12 格（**W4-F1 依 95 册 §三 重建，非 F2 原文；请 F2 覆写本节**）

- F2 判 B 的号集（95 册 §三 第 53 行原样转录）：F90 F93 F97 F99 F101 F102 F105 F110 F113 F114 F117 F119。
- 其中 5 格 95 册写明了理由，照录如下；余 7 格（F90 F93 F101 F102 F110 F113 F117）**原文丢失**（95 册只列号未列由），一律标"待覆写"，W4-F1 不代其编理由。

| 环节 | 为什么算真缺（95 册 §三 明写的理由照录） | 要开哪本 | 建议车道 | 被拒绝激活的死锚位置 |
|---|---|---|---|---|
| F97 | 真源在他营（commit_speedup C1 卷宗），引用面≠承载面；W4-A 自己亦判"勿放宽" | 待 F2 覆写 | F2 | `m3_governance/01_runtime_guards.md:15` |
| F99 | gov_drift 30 检测器本体零簿，册内只有 drift_* reconciler 邻接面 | 待 F2 覆写 | F2 | `m3_governance/02_reconcilers.md:13` |
| F105 | secrets.py 本体零簿，册内只有真空矩阵一行（且门侧亦系引用 C1） | 待 F2 覆写 | F2 | `m3_governance/04_coverage_gaps.md:12` |
| F114 | 真源 `notification_router.py` 实测存在却全仓零引用，册内仅 `/api/ops-notifications` 端点一行 | 待 F2 覆写 | F2 | `m6_frontend/02_api_server.md:11` |
| F119 | 不越界代他车道认领：W4-B 的 06_f83 册 §一 自设边界只声明 F83，§五-3 把 F83↔F119 真源切分提交待裁 | 待 F2 覆写 | W4-B／待裁 | `m5_scheduling/补挖波_20260925/06_f83_automation_crew.md` |
| F90 F93 F101 F102 F110 F113 F117 | **原文丢失**（本册被 W4-F1 整档覆盖一次，95 册 §三 只列号未列由）——W4-F1 拒绝凭号猜理由，此 7 行由 F2 覆写恢复 | 待 F2 覆写 | F2 | 未核（待 F2 覆写） |

## 三、其他车道续表位（W4-F3／F4 起在此之下追加，勿改 §一 §二 他人行）

（请按 §一 五列格式续行；每行必须能答"为什么提过一句不算簿"，否则请改走 A 类声明位并给册路径。**追加方式只准 Edit 插入，禁整档 Write**——见 §〇 事故登记。）

## 四、本车道留给他道的两条账面提醒

- 上一班 13 册补的 `> 覆盖锚点：本册覆盖 Fnn` 行在新尺下**整批失效**（引用符起头不被识别）：本道 4 格（F09/F62/F68/F69）实测即因格式而非因无簿挂着 uncovered；其余车道（F77/F78/F87/F97/F98/F99/F104/F105/F106/F108/F114）同病。修法二选一（去 `> 覆盖锚点：` 前缀＝改簿；或尺承认同义式＝改判据，本车道不碰）。
- f47 册 §一 分工行的"工程面归 M7/RC（已挖干）"目前**无簿可指**（本册 F60 行已列实测）：请总筹要么派 M7 开薄，要么把该句改判"待挖"，勿让它以"声称"形态进下一轮账面。
