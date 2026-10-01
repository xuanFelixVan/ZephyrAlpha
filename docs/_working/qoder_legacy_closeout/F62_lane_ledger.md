---
ttl: task_bound
lane: lane-f62
session: st-ffchief-20261001
date: 2026-10-01
head_anchor: a03280dc6b870e5429e910544194f0e5f4db512f
---

# F62 · 合规门与程序化交易报告（F-04）六向台账

> **落地迁移注记（R5 处方，2026-10-01）**：本册原定路径
> `docs/_working/fullflow_chief_20261001/skeleton/F_risk_compliance/F62.md` 被
> R5-DIGIT-SUFFIX 闸硬拦（gov_doc_003：目录数字后缀禁落地，战役目录自身文件同因全部
> 已索引未落地）——按 W140 先例（commit fa9ae3653319「R5 处方：落无数字后缀目录」）
> 迁移至本路径；原路径仅留指针存根（worktree 态，不落地）。

> **结论先行**：总册 00_skeleton.md 的「F62 合规门零注入=码成闸空 P0 断链」判定**已陈旧**。
> 该 P0 于 2026-09-28 由 W140 十二件接线表落批闭合（commit `fa9ae3653319`，st-zcloseout-20260928），
> 2026-09-29 C41 逐行 HEAD 复核在案（`docs/_working/qoder_legacy_closeout/W140_f62_wiring_table.md` §5）。
> 本车道于 HEAD `a03280dc` 实测复核（grep+测试 435 green）确认闭合，并落掉最后一件代码道余量
> **G12 监管报告工件生成器接线**（W140 §1 表 G12 DEFER 备忘的精确落点）。
> 残余断链面全部为 Owner 门位或非本域（见 §4 跳过登记），无代码道余量。

## §1 六向台账

| 向 | 内容与实证（HEAD a03280dc 实测） |
|---|---|
| 上游输入 | 监管真源：43_compliance_discipline.md §7.4/§7.5/§8/§10（归档态，M7 B4 待裁升迁）；程序化新规两文（2025-07-07/2026-06-08）；登记表 REG-CMP-REPORT-001=`docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml`（6 项义务 **broker_ack=true ×6 已回填**，reported_at=2025-12 Owner 口述锚，2026-09-27 回填） |
| 下游消费 | C-002 拒单前置=`src/zephyr/ex_core/order_manager.py` `submit_order:348`→`_check_compliance_gates:371` **五闸链全接**：①ReportGate 先报告后交易（BLOCK→ComplianceGateBlockError ZA-EX-0011）②日申报 5000 预警/1 万阻断（同实例 CancelRateGuard）③盘中操纵冻结（is_frozen，失效 Fail-Closed）④程序化报备（check_can_trade，LIVE 未报备/漂移/未知 broker 拒发，SIMULATION 豁免）⑤信息空窗回避（avoid_symbols 命中拒发）；会话级 C-004=trading_session 纪律闸/KillSwitchLite/清单闸（assemble_session 注入） |
| 自动化触发 | 装配正门=`scripts/start_paper_session.py` `assemble_session`（report_gate/declaration_guard/manipulation_monitor/registration_guard/avoidance_detector 五件齐注，:714-733；monitor `attach_order_manager` 喂事件流）；实盘装配=`ex_core/qmt_trading_session.py:42-43`（ReportGate+monitor 在）；**本轮新增**：G12 报告工件快照随装配正门自动产出（`_emit_regulatory_report_snapshot`，事件 `REGULATORY_REPORT_SNAPSHOT` 落 compliance_log） |
| 真源与注册表 | 闸体真源=`src/zephyr/compliance/compliance_report_registry.py`（MOD-CMP-009，ReportGate.check Fail-Closed：登记表不可读=BLOCK）；十二件台账真源=W140 接线表（qoder_legacy_closeout，C41 复核 §5）；挖矿底册=M7-06（fullflow_mining/m7_live_execution/06_compliance_gates.md，2026-09-25 时点快照，其「零注入」结论已被 09-28 接线批取代） |
| 门禁与质量尺 | 五闸全 Fail-Closed（登记表不可读/检测失效/守卫异常→拒单）；测试面 435 passed（tests/compliance 21 件+F62 接线 26 件+G12 新增 3 件+reporting 回归，--basetemp=.runtime/tmp/lane-f62/）；同实例约束/attach spy/裸构造跳过语义均有红绿断言（test_f62_compliance_gate_wiring.py） |
| 当前运行状态 | **绿（模拟侧执法闭环）**：五闸注入即生效+broker_ack 全确认→ReportGate 实测 PASS；G12 工件快照收口后十二件中**代码道 8 已接（G01-G07/G09）+G12 本轮落**，G08/G10/G11 三件非交易路径闸按 W140 处方缓（§4）；实盘腿=绑 TRD-A10（Owner 等待，非代码道） |

## §2 总册 P0 判定纠偏（证据链）

| 时点 | 事件 | 锚点 |
|---|---|---|
| 2026-09-25 | M7 挖矿：12 件合规闸「码成闸空零注入」P0 立案（6 处 OrderManager 裸构造实证） | M7-06 §二/§三/B1 |
| 2026-09-27 | F62 装配批：C-002 三门注入 assemble_session；broker_ack ×6 回填 | start_paper_session F62 装配批注记 |
| 2026-09-28 | W140 十二件接线表：G07/G09 接入五闸链+paper 会话装配；8 项红绿测试绿；commit `fa9ae3653319` | W140 §1/§2 + git log |
| 2026-09-29 | C41 销账复核：12 行逐行 HEAD 读数，实体零丢失 | W140 §5 |
| 2026-10-01 | 本车道 HEAD 实测复核闭合+G12 收口 | 本册 |

**总册 00_skeleton.md §P0 断链清单第 2 行（F-04）与 §1 F 段红标应按本册改判「已闭（模拟侧）」——总册为共享热文件，本车道不动，留总筹改判。**

## §3 本轮施工（G12 收口，最小面）

| 项 | 内容 |
|---|---|
| 接线点 | `scripts/start_paper_session.py` `assemble_session` 装配正门尾段（[COMPLIANCE] 横幅后）：`_emit_regulatory_report_snapshot(compliance_logger, broker_id, strategy_id, constraints)` |
| 语义 | RegulatoryReportGenerator（MOD-RPT-006，此前 ZERO HITS）产出程序化交易报告工件快照（portfolio_id=_BROKER_ID、报告期锚装配年、strategies=当会话策略、risk_rules=五闸+预警线同源姿态）→`validate_report` 完整性自校验→事件 `REGULATORY_REPORT_SNAPSHOT` 落 compliance_log 留痕（report_id+data_hash） |
| 失效语义 | 工件生成器异常吞没不阻断装配（`# noqa: BLE001`，同 alert_sink 口径——G12 是报告工件生产器非拒单闸，拒单保险丝=order_manager 五闸链） |
| 测试 | `tests/compliance/test_f62_compliance_gate_wiring.py::TestRegulatoryReportSnapshotWiring` 3 件：工件落 tmp 链且 validate=True+五闸姿态同源断言+生成失效不阻断装配 |
| 改动面 | scripts/start_paper_session.py（+import 行+helper+1 调用点）、tests/compliance/test_f62_compliance_gate_wiring.py（+3 测）——零新 .py，实盘路径文件零改动（qmt_trading_session 等未触） |

## §4 自裁与跳过登记（Owner 总授权自裁记日志）

| # | 项 | 处置 | 理由 |
|---|---|---|---|
| 1 | G08 IntradayManipulationDetector 批扫接线 | **跳过（堵死）** | W140 备忘插入点 `batch_window_preflight.py` **文件不存在**（HEAD 实测）——插入面无承载，批扫非逐单闸，待批窗 preflight 工件落地后另单 |
| 2 | G10 FeatureGate | **跳过（Owner 门位）** | REG-FEATURE-ADJ-001 未登记模拟交易 feature 条目=safety H/ai_autonomy human_gated（W140 §1/G10 处方不变）；启动前置 `FeatureGate.check` 待 Owner 登记 |
| 3 | G11 LicenseUsageAuditor | **跳过（无生产消费面）** | 依赖引入流程无承载工件、周期合规巡检（MOD-CMP-004）探针契约扩展超本车道最小面且归 M3 治理域（M7 §三明示「本册不判其接线」） |
| 4 | F62.md 命名闸 | `lock_files.py acquire --skip-naming-check` 显式逃生旗 | 总包战役指定车道路径（N-01/N-13 拒 `F62.md` 大写）；提交侧无命名 gate（git_commit.py/commit_preflight 零 naming 检查，存量例=W140_f62 大写目录先例在库） |
| 5 | CCR token 登记触禁区文件 | batch_creation_tokens.py **官方通道**登记（唯一合法插入式通道）+ 本 commit 同袋原子 | 新 .md 无 token=CREATE-GUARD 阶段2 硬阻断；token 真源 capability_canonical_file_registry.yaml 在禁区清单，但禁区义为禁手改/禁重构——官方 append-only 通道为任何新文档唯一合法登记路（W140 车道同先例，commit fa9ae365 记录）；工作树在途同会话 token 插入（st-ffchief-20261001 L27/归档批）为同总包 own 面 |

## §5 遗留（非本车道代码道）

1. **broker_ack 确认位维护**=Owner 人工义务（报送券商渠道，重大变更 T+1 回填 REG-CMP-REPORT-001）。
2. **实盘腿 TRD-A10**=Owner 等待（W140 §5）；五闸对 LIVE 模式即执法（SIMULATION 豁免语义随 mode 翻转生效）。
3. G08 批扫接线=待 `batch_window_preflight` 承载工件（施工归后续单，插入语义已记 W140 §1）。
4. M7 B4 真源升迁（43 号归档态）与 B5 KillSwitchLite 生产路径 env 化=待裁/0.5h 级，非断链。
5. `EodReconciler`/`eod_processor` 自身零生产装配=F63 对账域问题，本车道不越界（G12 未接入彼处防造新零注入对）。
