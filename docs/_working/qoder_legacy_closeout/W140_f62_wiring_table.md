---
ttl: task_bound
---

# W-140 · F62 合规门禁 12 件接线表（模拟盘执法先行）

- 任务: P0-10（裁定 F62：12 件注入转普通施工任务），lane=st-zcloseout-f62，session=st-zcloseout-20260928
- 日期: 2026-09-28 · 分支: st/st-zcloseout-f62（基线 dev@4e719ff8723）
- 真源: REG-CMP-REPORT-001（`docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml`，safety=H）
- 铁律: 先报告后交易——任一必报项 broker_ack 缺失 → C-002 拒单；拒单=保险丝正确工作
- 范围: 仅模拟侧执法接线；实盘路径文件零改动（见 §3 安全声明）

判定方法：`grep -rn` 于 `src/zephyr` + `scripts`（排除 tests/ 与模块自引用）；
"ZERO HITS"=除自身文件头/docstring/API facade 再导出外无任何生产 import 或调用。

## 1. 12 行接线表

| # | Gate | 实现 path:line | 现有生产调用者（grep 证据 / ZERO HITS） | Fail-Closed | 模拟侧接线 |
|---|------|---------------|----------------------------------------|-------------|-----------|
| G01 | ReportGate 先报告后交易（MOD-CMP-009） | `src/zephyr/compliance/compliance_report_registry.py:133`（`check` :144） | `ex_core/order_manager.py:70`（注入 `_check_compliance_gates` 闸1）; `ex_core/qmt_trading_session.py:42,135`; `frontend/dashboard/app_panel.py:524,534`; `scripts/start_paper_session.py:547` | 是（登记表不可读→BLOCK :148-155；broker_ack 缺失→BLOCK :156-162） | 已接线（broker_ack=true ×6 已回填，ReportGate 实测 BLOCK→PASS）——本轮零改动 |
| G02 | TradingComplianceDetector §7.2 异常2条+§7.3 操纵4类 | `src/zephyr/compliance/trading_compliance_detector.py:129` | `ex_core/trading_session.py:95`; `compliance/manipulation_realtime_monitor.py:65`; `compliance/manipulation_stream_driver.py:41`; `compliance/intraday_manipulation_detector.py:69` | 是（Hard Block verdict，:280） | 已接线（经 G04 监测器+TradingSession）——零改动 |
| G03 | ManipulationStreamDriver 委托/成交流驱动 | `src/zephyr/compliance/manipulation_stream_driver.py:61` | `compliance/intraday_manipulation_detector.py:68`; `compliance/manipulation_realtime_monitor.py:64` | 是（委托消费侧 verdict→HARD_BLOCK） | 已接线（G04 消费）——零改动 |
| G04 | ManipulationRealtimeMonitor 盘中操纵冻结闸（MOD-CMP-018） | `src/zephyr/compliance/manipulation_realtime_monitor.py:215` | `ex_core/order_manager.py:81`（注入 `_check_compliance_gates` 闸3）; `ex_core/qmt_trading_session.py:43`; `frontend/dashboard/app_panel.py:525` | 是（监测失效→Fail-Closed 拒单，order_manager `_check_compliance_gates`） | 已接线——零改动 |
| G05 | DisciplineGuard 必做清单闸 | `src/zephyr/compliance/discipline_must_do_checker.py:109` | `ex_core/trading_session.py:83` | 是（ChecklistVerdict 未完成→拦截） | 已接线（TradingSession）——零改动 |
| G06 | DisciplineGuard 禁止项闸（KillSwitchLite 报复腿） | `src/zephyr/compliance/discipline_prohibition_checker.py:205`（KillSwitchLite :124） | `ex_core/trading_session.py:88`; `pf_alloc/batched_position_builder.py:57` | 是（熔断禁新开仓） | 已接线——零改动 |
| G07 | ProgrammaticTradingGuard 程序化报备闸（40 号 §决策⑱） | `src/zephyr/ex_core/programmatic_trading_guard.py:273`（`check_can_trade` :418） | **ZERO HITS**（文件头 CONSUMERS 声称 trading_session/miniqmt_broker，但全仓无 import；仅 `tests/ex_core/test_programmatic_trading_guard.py`） | 是（未报备→BLOCKED_UNREGISTERED :462；未知实盘 broker→BLOCKED_LIVE_BROKER :448；配置漂移→BLOCK :492；SIM/PAPER 豁免 :438） | **本轮接线**：OrderManager 注入闸4（`registration_guard`，submit 前 `check_can_trade(broker_id)`，blocked→`ComplianceGateBlockError`，守卫异常→Fail-Closed 拒单）；paper 会话装配 `scripts/start_paper_session.py` 注入 `mode=SIMULATION`（豁免语义不变，模式一旦 LIVE 即执法） |
| G08 | IntradayManipulationDetector 盘中批量扫描 | `src/zephyr/compliance/intraday_manipulation_detector.py:140`（`run_batch` :165） | **ZERO HITS**（仅 `info_asymmetry_manipulation_detector.py:34` docstring 提及） | 是（batch 报告 hit→HARD_BLOCK） | **DEFER**——批量扫描器非逐单闸，自然执法点=盘后/批窗批扫（涉及 sibling 热路径 `batch_window_preflight.py`，本 lane 禁触）。插入点备忘：批窗 preflight 内对当窗委托批量调 `run_batch(ManipulationBatchInput)`，hit→阻断后续申报 |
| G09 | InfoAsymmetryManipulationDetector 信息空窗操纵回避（MOD-CMP-014） | `src/zephyr/compliance/info_asymmetry_manipulation_detector.py:135`（`avoid_symbols` :302，`scan` :253） | **ZERO HITS** | 是（suspected/空窗命中→入回避名单，`_avoid` :291；名单=漏斗排除语义） | **本轮接线**：OrderManager 注入闸5（`avoidance_detector`，`order.symbol ∈ avoid_symbols()`→`ComplianceGateBlockError` reason_code=`INFO_ASYMMETRY_AVOIDED`；检测异常→Fail-Closed 拒单）；paper 会话注入空检测器（无披露登记=空名单=零误拒，披露经 `register_disclosure`/`scan` 进入即执法） |
| G10 | FeatureGate 功能二元裁定闸（MOD-CMP-005） | `src/zephyr/compliance/hard_boundary_adjudicator.py:103`（`check` :119） | **ZERO HITS**（仅 `compliance/api/__init__.py:50` facade 再导出，无执法调用点） | 是（未登记→PENDING 视同 BLOCK；登记表不可读→BLOCK） | **DEFER**——REG-FEATURE-ADJ-001 自述管"功能建设权（设计/上线时门禁），不管运行时"，逐单接线违反其 scope；且未登记即 BLOCK，覆盖模拟交易功能须 Owner 先登记 feature 条目（safety=H, ai_autonomy=human_gated，§5 人机门位）。插入点备忘：`scripts/start_paper_session.py assemble_session()` 启动前置 `FeatureGate.check(<模拟交易功能名>)`，BLOCK→拒启动 |
| G11 | LicenseUsageAuditor 许可证审计（MOD-CMP-008） | `src/zephyr/compliance/license_usage_auditor.py:118`（`audit` :145） | **ZERO HITS**（仅 `compliance/api/__init__.py:57` facade 再导出） | 是（ViolationLevel→finding/report） | **DEFER**——依赖引入/审计期门禁，非交易路径；逐单接线语义错误。插入点备忘：依赖引入流程（new dependency ingestion）或周期合规巡检调 `audit()` 出 LicenseAuditReport |
| G12 | RegulatoryReportGenerator 监管报告生成器（MOD-RPT-006） | `src/zephyr/reporting/regulatory_report_generator.py:155`（`generate_programmatic_trading` :169 等 4 类 + `validate_report` :307） | **ZERO HITS** | 是（`_require` :101 缺字段→InvalidRegulatoryReportError；`validate_report` hash 校验） | **DEFER**——报告工件生产器非拒单闸（G01 才是拒单保险丝）；自然消费点=报送管道。插入点备忘：EOD 对账（`ex_core/eod_reconciliation.py`）或合规持续运维面调 `generate_*` 出报告并 `validate_report` 留痕 |

## 2. 本轮改动清单（模拟侧，全部 None=未注入不校验，承继 order_manager 既有 INVARIANTS 口径）

1. `src/zephyr/ex_core/order_manager.py`：`_check_compliance_gates` 增闸4 `registration_guard`（G07）、闸5 `avoidance_detector`（G09）；`submit_order` 传 `broker_id` 入闸链；异常→`ComplianceGateBlockError`（reason_code 落 details）。构造参数默认 None——qmt_trading_session 等实盘装配零改动零影响。
2. `scripts/start_paper_session.py`：`_assemble_paper_order_manager` 注入 `registration_guard=ProgrammaticTradingGuard(mode=SIMULATION, live_broker_ids={"miniqmt"})` + `avoidance_detector=InfoAsymmetryManipulationDetector()`。
3. `tests/ex_core/test_order_manager_sim_compliance_wiring.py`：红绿对（ack/名单命中→拒；豁免/干净→过），全 synthetic tmp_path。

## 3. 实盘安全声明（live-path 零改动证明）

- 未触碰：`src/zephyr/ex_core/qmt_trading_session.py`（实盘 QMT 会话装配）、`src/zephyr/ex_core/adapters/miniqmt_broker.py`、`src/zephyr/ex_core/adapters/okx_broker.py`、`src/zephyr/ex_core/live_simulation_switcher.py`、`src/zephyr/ex_core/trading_session.py`、`src/zephyr/ex_core/qmt_file_bridge*`（sibling 禁触清单）。
- `order_manager.py` 改动向后兼容：新闸 None 默认=既有装配（含实盘路径装配）行为逐字节不变（与既有 INVARIANTS"门禁未注入不影响既有行为"同口径）；零 flag 翻转、零 broker 凭据接触、零真实订单。
- G07/G09 在模拟装配注入后：SIMULATION 模式豁免语义=程序化报备闸对模拟盘天然放行（拒单保险丝仅对真实未报备实盘触发）；回避名单空=零误拒。

## 4. 验收对照

- 12 行齐：6 已接线（G01-G06，caller 证据在表）+ 2 本轮接线（G07/G09）+ 4 DEFER 带精确插入点（G08/G10/G11/G12）。
- G07/G09 接线后生产调用点=1 处（order_manager 闸链）+1 处生产装配（start_paper_session）。
- 模拟路径测试绿 + 既有 `test_order_manager_compliance_gate.py` 回归绿。
