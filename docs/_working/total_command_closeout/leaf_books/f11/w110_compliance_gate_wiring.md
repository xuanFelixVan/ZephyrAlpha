---
ttl: task_bound
---

# 叶簿 W-110 · 实盘合规门 12 闸接线（前置=程序化交易报告义务履行+回执回填）

> 族 11（终局能力补齐）· 骨架行锚=`00_master_skeleton.md` L168（态 🌑，出处「提交链续跑令 1」，案卷列 A）
> 编译：2026-09-28，会话 st-zcloseout-20260928（Agent-H），lane HEAD=`325b69a193`。
> 状态标记：🌑 Owner 门位（前置=报告义务履行+回执回填，AI 不可自决）；接线本体部分落地（本会话实证 3 闸已入正门装配，见 M2）。
> 素材真源：`wave9/compliance_gate_wiring.md`（12 闸五列表全卷，W-140 产物）+ 本会话 HEAD 直读增量；骨架出处对勘=`wave9/compliance_gate_wiring.md` §0（「续跑令 1」实体在 `dossier_H_ruling_candidates_merge.md` §1.7 H-93 行，dossier_A grep「续跑令」零命中）。
> 关联区分：本叶簿=骨架 W-110（终局能力/门位面）；逐闸接线表细目=W-140（族 13）已由 wave9 成品覆盖，两 W 同域**同对象**——定稿时 W-140 应回链本簿，禁两册各自维护（内收判据 w5_1 同真源必并）。

## 1. 六向台账（对象=合规 12 闸的生产装配面）

| 向 | 内容 | 锚 |
|---|---|---|
| 上游供数 | 12 闸实现件集中在 `src/zephyr/compliance/**` 与 `ex_core/programmatic_trading_guard.py`、`reporting/regulatory_report_generator.py` | wave9 §1 表「实现 file:line」列 |
| 下游消费 | 订单流消费位=`order_manager.py` `_check_compliance_gates`（G1/G2/G3 触发）；会话级=trading_session.py :829/:986/:1000/:1025 | wave9 §1「触发路径」列 + §6-cmd8 |
| 名册声明 | `gate_registry` 内**无「12 合规闸」条目**（dossier_H H-93 在册句）；本 12 闸口径=挖矿册 `fullflow_mining/m7_live_execution/06_compliance_gates.md` §三三层全景凑成 | wave9 §0 |
| 读声明的代码 | 判读纪律在册：装饰性接线（import 不在产路径/仅 TYPE_CHECKING/仅注释）一律判未接线 | wave9 §0 判据纪律 |
| 覆盖测试 | `tests/compliance/test_runtime_wiring.py:3` 自述「真实触发非 mock」——但只证**注入后**行为；生产不注入则绿是假象（06 册 B2 口径的代码级复算） | wave9 §3 末段 |
| 执法门禁 | fail-closed 面在册：ReportGate 登记表不可读→BLOCK；KillSwitchLite/纪律闸/合规检测 异常→阻断（trading_session.py:995-1041）；但「未注入=静默跳过」=fail-open by absence | wave9 §1 G1/G4/G5/G6 行 |

## 2. 现状实测（wave9 基线 → 本会话 HEAD=`325b69a193` 直读增量）

| # | 断言 | wave9 基线（st-final-build 车道树面） | 本会话复读 |
|---|---|---|---|
| M1 | 12 闸执法态总判 | **0/12 真执法闸**（§4-a）；装饰性 8 闸+零消费者 3 闸（§4-b） | wave9 §4（基线面，本会话未逐闸重跑全表） |
| M2 | 正门装配增量 | §3：start_paper_session.py:555-564 仅传 risk_layer，四路合规参零注入 | ✅ **已变**：本会话实读 `start_paper_session.py` L691-701：`declaration_guard=CancelRateGuard()` / `report_gate=ReportGate()` / `manipulation_monitor=ManipulationRealtimeMonitor()` 三件齐装注入 `OrderManager(report_gate=…, declaration_guard=…, manipulation_monitor=…)` + `manipulation_monitor.attach_order_manager(order_manager)`（喂事件流）；行内注释自述「同实例硬约束：CancelRateGuard 一个对象同时给 OrderManager 与 TradingSession，分裂双实例…计数失明」 |
| M3 | 仍未接线闸 | G7 PTG/G8 RRG/G12 InfoAsym 字面零消费者；G9/G11 仅注释 | ⚠ 本会话 `git grep -l` 复读：RegulatoryReportGenerator/InfoAsymmetryManipulationDetector/ComplianceRuleEngine 仍**仅自身文件**（1 文件=self）；PTG 在 start_paper_session.py 的命中=L793 告警文案「TradingComplianceDetector / ProgrammaticTradingGuard 均未注入本正门——」**属注释级，非接线**（判读纪律：仅注释=未接线） |
| M4 | 裸构造面 | §3：OrderManager( 6 处生产构造全裸（三合规参默认 None） | 部分已变：start_paper_session.py:692 已非裸；其余 5 处（demo_e2e_pipeline:326/qmt_bridge_regression_smoke:230/qmt_file_bridge_integration:88/qmt_trading_session:123/app_panel:524）本会话仅确认位置在，**是否已传参未逐处核**（行号已漂移：492→692、52→88、115→123） |
| M5 | G2 日申报计数 | G2 行：record_submit/record_cancel 全仓无生产调用者→计数恒 0、防线未激活 | 本会话未复读调用面（接线刚落，计数腿是否随 M2 打通须按 wave9 §6-cmd10 复跑） |
| M6 | 前置义务 | G7 行+骨架 L168：实盘报备硬校验零调用者；前置=程序化交易报告义务履行+回执回填 | 🌑 未变（G7 enforce 默认 True 但零实例化，wave9 §5-5） |

## 3. 缺口与根因（转述）

- 根因=「防线存在的假象来自测试」：注入后 fail-closed 行为有测试绿，但生产装配零注入（wave9 §3）——M2 落地后该判据**对正门一名失效**、对其余 5 构造位仍待复核（M4）。
- 口径陷阱在册：勿把「执行前四级闸（pre_execution_checker，start_paper_session.py:565 实传 kill_switch_probe，06 册标已接线）」混入 12 闸计数（wave9 §4-c）；「实盘裸奔」准确表述=「12 闸裸奔、S-1 实盘门本身关着」。
- wave9 §5-b assumed 三条：checklist_checker 未纳入口径；43 号备忘 §号未逐条核；车道树面读数对 dev 有漂移风险——本会话 M2/M3 复读即在 dev 面证实了漂移实际发生（555→691），定稿前须全表重跑。

## 4. 施工项（带锚）

1. 全表重跑到 dev 现值：按 wave9 §6 cmd1-cmd10 重跑 12 闸五列表（M4/M5 两格本会话未闭合），产出增量注记而非覆写 wave9（其 completes_when 口径是车道面快照）。
2. 正门之外 5 个 OrderManager 构造位逐处定性（M4），裸构造位补注记或接闸——先例=start_paper_session 同实例硬约束注释（M2）。
3. 计数腿验证：M2 接线后跑 §6-cmd10 证 record_submit/record_cancel 真被经过（G2 由「未激活」转「现役」的判据）。
4. Owner 门位面（🌑，AI 不代裁）：G7 前置报告义务+回执回填；G1 接上即 BLOCK 第一笔的呈报口径（wave9 §4-d 建议原文：「12 闸中 12 闸零执法；3 字面零消费者、3 仅注释/类型期、6 注入链就绪待装配」——M2 后须改写为含正门 3 闸的现值）。

## 5. 复验命令（可重跑）

```bash
cd /d/ZephyrAlpha/.worktrees/st-zcloseout-leaves
git show HEAD:scripts/start_paper_session.py | sed -n '685,702p'   # M2：三门齐装+attach 喂流
git grep -n "均未注入本正门" HEAD -- scripts/start_paper_session.py  # M3：PTG/检测器仍未接线的在册自述
git grep -c "RegulatoryReportGenerator\|InfoAsymmetryManipulationDetector" HEAD -- src/zephyr/reporting/regulatory_report_generator.py src/zephyr/compliance/info_asymmetry_manipulation_detector.py
# 期望：第 3 条两文件各=1（仅自身命中=零消费者维持）。若出现非自身消费文件，M3 失效须重挖
```

## 6. 自审闸三态

- **挖干**：已干——wave9 全卷（12 闸×五列+零消费清单+装配穷尽+复算命令 10 条）+ 本会话 dev 面增量复读（M2/M3）两面闭合；未闭合格（M4 五处、M5）已逐格点名并给复跑命令，属「施工项」不是「未挖」。
- **施工中**：正门三门装配已落地（M2，🔨→✅ 待全表复验）；12 闸全表面=施工项 §4-1。
- **未开工**：其余 9 闸接线与 Owner 前置（M6）——证据=G7/G8/G12/G9 零消费复读维持 + 🌑 门位（骨架 L168）。
