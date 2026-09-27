---
ttl: task_bound
completes_when: "9.1 十二闸逐闸五列表成文且每行附可复算 grep 命令原文；零消费者清单可从表内直接复算；本卷 verified/assumed 分列齐备"
---

# W-140 · 实盘合规门 12 闸逐闸接线表（波 9.1）

turn_budget: 骨架第 8 次工具调用落盘；取数 6 块内完成；后续块只落盘
verified: 见 §5（全部行数为 `git grep` / 直读 file:line 实测，命令照录 §1 末列与 §6）
assumed: 见 §5-b（仅 3 项，均不改变"未接线"结论方向）
input_set_disjoint_with: 本卷只读 git 跟踪面（src/、scripts/、tests/、docs/）与 `git grep`；不碰计划任务（另卷 `offhours_task_action_truth.md`）、不碰 DB、不碰运行进程、不改任何文件
evidence_ref.cmd: §6 命令清单（全部在车道根 `D:/ZephyrAlpha/.aidrafts/st-final-build-20260926`、分支 `session/st-final-build-20260926` 树面执行）

## 0. 口径与在册依据

- 任务书出口判据（照抄 `10_wave_plan.md` 波 9 行 9.1）："表成文且每行给 grep 命令；'零消费者'清单可复算"。
- 在册起点（X-61，`02_field_corrections_and_new_cases.md:121`）四个抽查对象——**本卷实测复核结果**：
  1. `programmatic_trading_guard` 非自身引用=0 —— **证实**（src+scripts 面 git grep 零命中，tests 命中唯一）。
  2. `regulatory_report_generator` 非自身引用=0 —— **证实**（同上）。
  3. `manipulation_realtime_monitor` 仅 `order_manager.py:81` TYPE_CHECKING 预接线 —— **证实并补全**：另有 `order_enums.py:14` 一处 [TESTS] 注释引用（非代码）；`ManipulationRealtimeMonitor(` 构造调用在 src/scripts 面**零命中**。
  4. `compliance_rule_engine` 引用=1 —— **字面成立、性质改判**：唯一命中 `compliance_policy_engine.py:33` 是"查重分工"**文档注释**，非 import/调用；`ComplianceRuleEngine` 代码级消费=**0**。且该模块头注 `[CONSUMERS]` 自称已接 MOD-EX-024（pre_execution_checker）——实测 `pre_execution_checker.py` 零命中 ⇒ **声明-实测漂移**（见 G9 行）。
- "12 闸"名册在册状态：`gate_registry` 内无"12 合规闸"条目（dossier_H H-93 在册句照录："gate_registry 内无'12 合规闸'条目"）。本表口径 = 挖矿册 `docs/_working/fullflow_mining/m7_live_execution/06_compliance_gates.md` §三执行链合规闸三层全景，并入 X-61 抽查的 regulatory_report_generator 与 compliance_rule_engine，凑成逐件点名 12 闸。**注意**：执行前四级闸（pre_execution_checker）在 06 册标"已接线"，不属本 12 闸计数口径，单列注记 §4-c。
- dossier_A 定点核对：任务书所指"提交链续跑令 1"段在 `dossier_A_commit_chain.md` 内 grep "续跑令" **零命中**（复算：`git grep -n "续跑令" docs/_working/total_command_closeout/dossier_A_commit_chain.md`）；该出处实体在 `dossier_H_ruling_candidates_merge.md` §1.7 H-93 行（转录 HBD-10 §四-1 L1026-1028）。
- 判据纪律：**装饰性接线（import 但不在生产路径 / 仅 TYPE_CHECKING / 仅注释）一律判未接线**。

## 1. 逐闸五列表

消费者数写法：**A/B** ＝ A：`git grep -l <符号> -- src scripts` 非自身文件数（原始命中）；B：其中代码级消费（import/构造/调用）数。括号注文件。
"生产真经过?"判据：该闸在现存生产入口（`scripts/start_paper_session.py`、`src/zephyr/ex_core/qmt_trading_session.py` 等）中是否被非 None 注入并被订单流实际撞过。

| # | 闸（实现符号） | 实现 file:line | 消费者数 A/B | 触发路径 file:line | fail-closed? | 生产真经过? |
|---|---|---|---|---|---|---|
| G1 | ReportGate | compliance/compliance_report_registry.py:133 | 2/2（api/__init__.py:29 出口面、ex_core/order_manager.py:70 import） | order_manager.py:331 `_check_compliance_gates` → :365 `if self._report_gate is not None`；构造参 :155 默认 None | **是**：登记表不可读→BLOCK（compliance_report_registry.py:144-155 注释+代码）；**但未注入=静默跳过（fail-open by absence）** | **否**——6 处 `OrderManager()` 全裸构造（§3），闸永不执行 |
| G2 | CancelRateGuard 日申报硬计数器 | ex_core/cancel_rate_guard.py:80 | 3/2（order_manager.py:71、trading_session.py:347 兜底自建；trading_compliance_detector.py:35 仅 docstring） | 订单级：order_manager.py:375 BLOCKED→抛 ComplianceGateBlockError（:343 record_submit / :443 record_cancel 仅持 guard 时计数）；会话级：trading_session.py:829 can_place_order、:872 can_submit_now（:347 `or CancelRateGuard()` 空实例） | 订单级读态 BLOCK→raise＝是；**未注入=不计数也不拦** | **半**：会话级空实例被经过但**永不阻断**（record_submit/record_cancel 全仓无生产调用者——计数只在 order_manager 持 guard 路径，裸构造下计数恒 0）＝1 万笔防线现役未激活（06 册 B2，本卷代码级复算一致） |
| G3 | manipulation_realtime_monitor（冻结闸+监测族头） | compliance/manipulation_realtime_monitor.py:215 | 2/0（order_manager.py:81-82 **TYPE_CHECKING** import、shared/contracts/enums/order_enums.py:14 仅 [TESTS] 注释） | order_manager.py:395 `if self._manipulation_monitor is not None`；构造参 :157 默认 None；`ManipulationRealtimeMonitor(` 在 src/scripts 零构造 | 消费侧：monitor 抛异常→raise fail-closed（order_manager.py:397-403）；monitor 内部自注"检测失效→降级跳过不误判"（:8 INVARIANTS）＝**自身偏 fail-open** | **否**——TYPE_CHECKING-only ＝装饰性预接线，判**未接线** |
| G4 | KillSwitchLite 策略级当日熔断 | compliance/discipline_prohibition_checker.py:124 | 3/3（api/__init__.py:46/95、trading_session.py:88 import、pf_alloc/batched_position_builder.py:57-66 import） | 会话级：trading_session.py:986 `if self._kill_switch is not None`（构造参 :312 默认 None）；分批建仓：batched_position_builder.py:409 默认 None → :438-440 None 时**出声**warn"未接线"；allocation_orchestrator.py:709 `discipline_guard: Any = None`、:920 仅传 discipline_guard **不传 kill_switch** | 是：异常→return True 阻断（trading_session.py:995-1001 `except Exception ... Fail-Closed 拒单`） | **否**——生产装配零注入（start_paper_session.py:555-564 不传；orchestrator 链 kill_switch 恒 None） |
| G5 | 四项严禁纪律闸 DisciplineGuard | compliance/discipline_prohibition_checker.py:205 | 4/2（api/__init__、trading_session.py:88、batched_position_builder.py:57；compliance_log.py:5/:63 仅注释） | trading_session.py:1000 `if self._discipline_guard is not None`（:322-328 成对注入 fail-fast）；bpb 经 allocation_orchestrator.py:920 注入但生产调用侧恒 None（:709 默认值，全仓无 `discipline_guard=<真件>` 传参点——复算见 §6-cmd9） | 是：异常→保守 Hard Block（trading_session.py:1006-1010）；**未注入=跳过** | **否**（bpb 路径会 warn 出声"BM-BUY-08 纪律闸未接线"，恰为未接线的自证） |
| G6 | 交易合规检测 TradingComplianceDetector | compliance/trading_compliance_detector.py:129 | 9/5（api/__init__、intraday:159、monitor:244、driver:77、trading_session.py:95 import＋_run_compliance_detection:1060 起；compliance_log:5、info_asymmetry:33、trading_review_engine:26、fake_move_distribution:29 均注释） | trading_session.py:1025 `if self._compliance_detector is not None`；族内三件"复用"仅发生在 monitor/driver/intraday **被构造之后**（它们生产零构造，见 G3/G10/G11） | 是：异常→return True（trading_session.py:1030-1033） | **否**——零注入；族内复用链整体悬空 |
| G7 | programmatic_trading_guard 实盘报备硬校验 | ex_core/programmatic_trading_guard.py:273 | **0/0**（src+scripts 非自身零命中；tests/ex_core/test_programmatic_trading_guard.py 唯一外部引用） | assert_can_start :514 / assert_can_submit :551 存在，**调用者=0**；:278 构造=自身 docstring 示例 | 设计为是（enforce_on_start/submit 默认 True，:216-217，抛 ProgrammaticTradingGuardError）；可配宽松 False=跳过（:517/:540） | **否**——零实例化（"唯一在产"的反证不存在） |
| G8 | regulatory_report_generator 监管报告生成器 | reporting/regulatory_report_generator.py:155 | **0/0**（同 G7；:162 构造=自身 docstring 示例） | 无任何调用者；头注自述"基础版不含自动化报送(GATE-002/003)、手动生成" | n/a——**非拦截闸**，是报告件；必填缺失抛 InvalidRegulatoryReportError(ZA-RPT-0006)（契约级） | **否** |
| G9 | compliance_rule_engine（MOD-CMP-012） | compliance/compliance_rule_engine.py:253 | 1/0（compliance_policy_engine.py:33 查重分工注释——**X-61"引用 1"即此条，非代码**） | 无生产调用者；evaluate_pre_trade :283 就绪 | 设计为是（异常→HARD_BLOCK，:296-300 + 头注 INVARIANTS） | **否**；且头注 `[CONSUMERS] MOD-EX-024(pre_execution_checker)` **与实测矛盾**：pre_execution_checker.py grep rule_engine 零命中 ⇒ 在册声明漂移（登记本卷发现，不改册） |
| G10 | manipulation_stream_driver | compliance/manipulation_stream_driver.py:61 | 2/2（intraday:230、monitor:246——**均为族内默认构造**，随父件悬空） | 仅当 monitor/intraday 被装配才被经过；生产二者零装配（G3/G11） | 内部降级跳过（头注"不接真实流(调用方喂事件)…降级不阻断"）＝fail-open by design | **否** |
| G11 | intraday_manipulation_detector（批扫层） | compliance/intraday_manipulation_detector.py:140 | 1/0（info_asymmetry:34 仅注释；`IntradayManipulationDetector(` src/scripts 零构造） | 无生产喂入者；MANIPULATION_BATCH_SCAN 落痕只在被调用时产生 | 批扫本身不阻断（首命中去重+留痕）；无消费闸 | **否** |
| G12 | info_asymmetry_manipulation_detector | compliance/info_asymmetry_manipulation_detector.py:135 | **0/0**（src/scripts 非自身零命中；仅 tests/compliance/test_info_asymmetry_manipulation_detector.py） | 无 | 检测件，无阻断语义 | **否** |

## 2. 零消费者清单（从 §1 直接复算）

- **字面零消费者（src+scripts 非自身文件 grep 命中 0）**：G7 programmatic_trading_guard、G8 regulatory_report_generator、G12 info_asymmetry_manipulation_detector。
- **代码级零消费者（有命中但全为注释/docstring）**：G9 compliance_rule_engine（1 命中=注释）、G11 intraday_manipulation_detector（1 命中=注释）、G3 manipulation_realtime_monitor（代码命中仅 TYPE_CHECKING，按纪律判未接线）。
- 复算命令模板（§6）逐符号一条，`grep -v` 自身文件即得。

## 3. 生产路径装配证据（"裸构造"穷尽复算）

`OrderManager(` 生产构造 6 处（git grep -- src scripts 除 test 实测）：
`scripts/construction/demo_e2e_pipeline.py:326`、`scripts/construction/qmt_bridge_regression_smoke.py:230`、`scripts/start_paper_session.py:492`、`src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py:52`、`src/zephyr/ex_core/qmt_trading_session.py:115`、`src/zephyr/frontend/dashboard/app_panel.py:524`
——三合规参（report_gate/declaration_guard/manipulation_monitor，order_manager.py:155-157）全默认 None。
会话装配：`scripts/start_paper_session.py:555-564` `TradingSession(...)` 仅传 risk_layer（kill_switch/discipline_guard/compliance_detector/checklist_cancel_rate 四路合规参零注入），:565 `attach_pre_execution_gate(...)`（执行前闸属 06 册另一口径，见 §4-c）。
`compliance/api/__init__.py`（06 册所称"C-002 消费出口"）**生产 import 者零**：`git grep "compliance\.api\|from zephyr\.compliance import" -- src scripts` 排除包内 = 0 命中 ⇒ 门面本身也悬空。
测试面反证：`tests/compliance/test_runtime_wiring.py:3` 自述"合规闸门在买入/执行链路真实触发，非 mock 闸"——该绿只证**注入后**行为；生产不注入（本卷 §3），即 06 册 B2"防线存在的假象来自测试"在代码级复算成立。

## 4. 三态汇总

- **a. 真执法闸（当前在生产路径上能改变订单行为）：0 / 12。** 最近的边缘是 G2 会话侧空实例被经过（:829/:872），但计数永不递增 ⇒ 不能阻断任何单，判"经过而永不变行为"＝未执法。
- **b. 装饰性接线（有 import/出口但不过货）：G1、G4、G5、G6（注入链在，源零注入）+ G3（TYPE_CHECKING-only）+ G9/G11（仅注释引用）**；族内互用 G10 随父悬空。
- **c. 口径注记**：执行前四级闸（pre_execution_checker）06 册标"已接线"（start_paper_session.py:565 实传 kill_switch_probe），不属本 12 闸；本表若照"⚑-1① 裸奔"口径引用时勿把两者混数。另：06 册 §三 的"执行前四级闸…闸1.5 blocks_live_trading（S-1）"是**唯一现役硬门**——"实盘开单等于裸奔"的准确表述应为"合规 12 闸裸奔、S-1 实盘门本身关着"（与 93 册①行 129 行"实盘那扇门本身还没开"一致，无新增矛盾）。
- **d. 对 ⚑-1① 定稿的输入**：呈报口径建议改"12 闸中 12 闸零执法；其中 3 闸字面零消费者、3 闸仅注释/类型期消费、6 闸注入链就绪待装配"；接线前置仍是 Owner 报送+broker_ack 回填（G1 接上即 BLOCK 第一笔，fail-closed 正确行为）。

## 5. verified（实测可复算）

1. X-61 四项抽查：3 项证实、1 项改性质（"引用 1"＝注释）。
2. 每闸 A/B 消费者数＝§1 表（命令 §6-cmd1/2）。
3. OrderManager 裸构造 6 处、TradingSession 装配不传合规参＝§3 行号直读。
4. KillSwitchLite/纪律闸/合规检测/冻结闸/ReportGate 的"注入后 fail-closed"＝代码直读（trading_session.py:986-1041、order_manager.py:365-418、compliance_report_registry.py:144-155）。
5. PTG enforce 默认 True＝programmatic_trading_guard.py:216-217 直读。
6. compliance/api 门面生产零 import＝git grep 实测。

## 5-b. assumed（未实测项，不翻结论）

1. `checklist_checker`（盘前清单闸，C-004 第四件）未纳入 12 闸口径（06 册把 C-004 记三闸），其接线态未测——若 Owner 要"闸全集"需补一行，不影响本 12 行结论。
2. 06 册引用的 43 号设计备忘 §号未逐条开窗核对（只按代码内注释转述 fail-closed 语义）。
3. 本表测于车道分支树（session/st-final-build-20260926）；主仓 dev HEAD 面若有他会话在途改动，数字可能衍生漂移——定稿呈报前建议以 `git grep <符号> dev -- src scripts` 复跑一遍（命令 §6-cmd3 变体）。

## 6. 复算命令（每闸一行，车道根执行）

```bash
# cmd1 原始命中 A 口径（逐闸换符号）：
for s in ReportGate CancelRateGuard ManipulationRealtimeMonitor KillSwitchLite DisciplineGuard TradingComplianceDetector ProgrammaticTradingGuard RegulatoryReportGenerator ComplianceRuleEngine ManipulationStreamDriver IntradayManipulationDetector InfoAsymmetryManipulationDetector; do echo "== $s =="; git grep -l "$s" -- src scripts | grep -v "$(echo $s | sed 's/\([A-Z]\)/_\L\1/g;s/^_//;s/^__*//')"; done
# （简化：人工按 §1 表文件名剔自身；文件名见实现列）
# cmd2 构造级消费：
git grep -n "ReportGate(\|CancelRateGuard(\|KillSwitchLite(\|DisciplineGuard(\|TradingComplianceDetector(\|ComplianceRuleEngine(\|ProgrammaticTradingGuard(\|RegulatoryReportGenerator(\|ManipulationRealtimeMonitor(\|ManipulationStreamDriver(\|IntradayManipulationDetector(\|InfoAsymmetryManipulationDetector(" -- src scripts | grep -v _test
# cmd3 dev HEAD 面复核（定稿前）：
git grep -l "ProgrammaticTradingGuard\|RegulatoryReportGenerator\|ComplianceRuleEngine" dev -- src scripts
# cmd4 裸构造穷尽：
git grep -n "OrderManager(" -- src scripts | grep -v test
# cmd5 装配注入面（全仓找合规参传点）：
git grep -n "report_gate=\|declaration_guard=\|manipulation_monitor=\|kill_switch=\|discipline_guard=\|compliance_detector=\|checklist_checker=" -- src scripts
# cmd6 门面出口消费：
git grep -n "compliance\.api\|from zephyr\.compliance import" -- src scripts | grep -v "src/zephyr/compliance/"
# cmd7 注释级引用甄别（G9/G11/G3）：
git grep -n "compliance_rule_engine\|intraday_manipulation_detector\|manipulation_realtime_monitor" -- src scripts | grep -v "compliance/compliance_rule_engine.py\|compliance/intraday_manipulation_detector.py\|compliance/manipulation_realtime_monitor.py"
# cmd8 触发路径行号：
git grep -n "_check_compliance_gates\|_is_blocked_by_compliance_gates" -- src/zephyr/ex_core/order_manager.py src/zephyr/ex_core/trading_session.py
# cmd9 纪律闸生产传参点（判 None）：
git grep -n "discipline_guard" -- src/zephyr/pf_alloc/allocation_orchestrator.py
# cmd10 日计数调用者（判恒 0）：
git grep -n "record_submit\|record_cancel" -- src/zephyr/ex_core/order_manager.py src/zephyr/ex_core/trading_session.py
```
