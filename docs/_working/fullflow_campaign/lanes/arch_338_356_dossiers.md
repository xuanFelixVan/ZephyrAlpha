---
ttl: task_bound
completes_when: 总包/Max 依本案卷对 #ARCH-338..356 逐条作出架构裁定（每条含实测证据+处置选项+门位标注）
---

# #ARCH-338..356 架构挂起项 · 逐条案卷（架构裁定项案卷车道 st-ff-arch-20260918）

> **本件定位**：交付"逐条案卷"，非"逐条修复"。每条带本次（2026-09-18）**实测证据**，让总包/Max 看完能直接下判、不必重新勘察。
> **真源**：`docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml:22147-22379`（19 条原文，全部 `status: open`）。
> **证据纪律**：凡不确定的对象，标"未能定位/证据不足/转报"，绝不编造编号或数字（R-024 教训）。
> **R-019 前置复跑**：每条均**实跑命令复测注册表记载**，未按陈旧记载照抄。凡实测与注册表不符，**以实测为准并明说**。
> 任务书内给的路径/主题词仅作检索线索，最终以注册表原文 + 代码实测为准。
>
> **六向断点类型图例**：①入口无料 / ②转化不跑 / ③出口无货 / ④下游无取 / ⑤哨兵缺位 / ⑥失败不响。

## 0. 四态分布总览（本次实测）

| 态 | 条数 | 条目 |
|---|---|---|
| **仍成立**（核心断点实测在位） | 17 | 338*,339*,340,341,342,343*,344,345,346,347,348,349,350,351,353,354,355 |
| **已闭合（部分）** | 1 | 352（webhook 通道机制已建已接线，**但落 HEAD 由本案卷批次达成；剩余缺口=无真实外部接收方=黄-门位**） |
| **口径不符/记载过粗**（核心仍成立，含于上行 17 内，带 * 者） | 3* | 338*、339*、343*（"零接线/仅 W03"等 headline 与实测 import 面/调用点口径不符，见各条；**核心缺陷仍成立**，仅归因措辞需修） |
| **纯研究 backlog（非断点）** | 1 | 356（轴F 8 项立卡评估队列） |

> 合计 17（仍成立，含 3 条 headline 口径需修）+ 1（部分闭合）+ 1（backlog）= **19**。
- **证据不足**：346-B05/B08 子项、351-"24 无退路"精确子集计数、350-I08"空串永久缓存"行级路径——均标转报/未亲验，见各条。
- **触 Owner 门位（§7）**：341（武装需券商 ack 数据源+时点）、347（D_FRONTEND human_gated + 需签发体系/凭据）、352（需 Owner 外部凭据 BRK-055）、351（9/18 退役=生产流转/实盘相关）、344（断供自动禁交=主动动作闸，参 R-022③）、340 保命轨 auto-trip（R-022③已列 Max）。

---

## #ARCH-338 执行域孤儿族接线或退役裁定（OrderExecutionSaga/ExecutionEngine/ex_sor/order_splitter/process_fill 零生产接线）
- 注册表登记态：`open` / 登记日 2026-09-18 / 引裁定号 `#309/#304` / severity `P1高`
- **本次实测是否仍成立**：**核心成立，但 headline 口径需修（3/5 子项）**。
  - **OrderExecutionSaga = 孤儿（亲验）**：全仓非 test 仅见 `order_execution_saga.py:104`(__all__)、`:324`(模块内自身工厂)、`rejection_action_handler.py:20`(注释)——**无外部生产实例化**，Saga 补偿链确未接线。
  - **ExecutionEngine ≠ 零接线（亲验，与记载不符）**：`risk_validation_bridge.py:81 engine = ExecutionEngine(order_manager=om, risk_validator=bridge)` 存在装配点。是否"生产可达"须顺装配链核（该 bridge 由谁实例化未追到底）→ 记"1 个非 test 实例化点，生产可达性待核"。
  - **process_fill ≠ 零调用（亲验，与记载不符）**：`aggregate_root_manager.py:125/232`、`fill_handler.py:188` 有真实调用。X07 真断点是 **process_fill 的 JSONL 落盘→盘后对账读空**（出口断链），非"方法没人调"。
- 精确锚点：`src/zephyr/ex_core/order_execution_saga.py:104`（Saga 孤儿）；`src/zephyr/ex_core/aggregate_root_manager.py:125`（process_fill 有调用，反证"零接线"）；`src/zephyr/governance/adapters/risk_validation_bridge.py:81`（ExecutionEngine 有装配）
- 证据：`grep -rn "OrderExecutionSaga" src/zephyr --include=*.py | grep -vE "test|class|# \["`→仅 __all__/self-factory/注释；`grep -rn "\.process_fill("`→3 处 src 真实调用。
- 断点类型：Saga/补偿=④下游无取；process_fill JSONL→对账=③出口无货；X04 SOR 参与率 5% 红线不强制=⑥失败不响（监管红线软约束）。
- 处置选项：①**先更正记载口径**（把"零接线"细化到"哪些真零实例化/Saga vs 装配但未达钱路径"）②再逐件裁"接线/退役/重分类"——**禁整族一刀切**（ExecutionEngine 若在钱路径则不能退役）。代价：需一笔完整生产可达性 trace（本车道预算内未完成）。风险：按错口径裁"退役"可能删掉真在跑的执行引擎。
- 影响面：钱路径实跑=`TradingSession→OrderManager` 裸路径（补偿/超时/算法切片纸面化），X04 参与率 5%/LOT_SIZE=100 科创板隐患。**不直接触 Owner**（裁决级），但接线落地涉 ex_core 钱路径。
- 总包预裁对照：无 R-K 直配（属"接线/退役/语义三选一"晨报批）。**与晨报"孤儿族"措辞不一致处**：实测 3/5 子项有装配/调用点，须以本条更正。
- **建议裁定 + 依据等级**：先更正归因口径（**亲验**）→ 再分件裁：Saga 走接线或退役、ExecutionEngine 先定生产可达性、process_fill 治 JSONL→对账出口。核心断点成立属**亲验**；"ExecutionEngine 是否钱路径可达"属**推断**（未追装配链到底）。

## #ARCH-339 风控孤儿闸族产而不消（K03 StopGate/K06 A股止损引擎/K09 清仓保护/K07 黑天鹅）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**核心成立，StopGate 归因需重分类（亲验）**。
  - **StopGate ≠ 零实例化（亲验，与"生产零调用"措辞不符）**：`auto_runtime_core.py:137 self._stop_gate = StopGate()` **在生产核心里被实例化**。K03 真问题是"**它是会话质量闸、非交易闸，未接在下单/清仓动作上**"→ 需重分类，而非"没人 new"。
  - **K06 ashare_stop_loss_engine**：非 test 引用极少（grep `ashare_stop_loss_engine` 命中=1，且 `#ARCH-339` 说"per-position 止损整体缺位"）→ 与"产而不消"一致（转报 rpt_k06 细分）。
  - **K09 drawdown_liquidation_guard / LiquidationGuard**：grep 命中 6 处需逐条辨（部分是头注/CONSUMERS）；与"双守卫零接线"未做行级证伪 → 记转报。
- 精确锚点：`src/zephyr/trading/auto_runtime_core.py:137`（StopGate 有实例化，反证"零调用"）；K06/K09 具体调用点：本车道未逐行证伪，转报 `rpt_k06.md/rpt_k09.md`。
- 证据：`grep -rn "StopGate(" src/zephyr --include=*.py | grep -vE "test|class "`→ auto_runtime_core.py:137。
- 断点类型：④下游无取（风控闸产而不消）+ per-position 止损缺位=①入口无料（该动作无触发源）。
- 处置选项：①StopGate 重分类为"会话质量闸"并另建交易级总停闸 ②整族接电（kill switch→清仓→复核闭环，与 #ARCH-340 K02 联动）③退役零价值件。代价：接电触钱路径 + K06 与 #317 改造区冲突。风险：一刀切退役会砍掉 StopGate 现有的会话质量守卫作用。
- 影响面：清仓/止损缺位=危机时不能真停。**接线落地涉 risk 域（z-land3/residG 落地权）**。
- 总包预裁对照：无直配 R-K。与晨报一致（孤儿闸族成立），但**StopGate 措辞需从"生产零调用"更正为"已实例化但未接交易动作"**（不一致处已实测）。
- **建议裁定 + 依据等级**：StopGate 重分类（**亲验**）；K06/K09 接电/退役随 K01/K02 kill switch 闭环一并裁（**转报** rpt_k0x）。

## #ARCH-340 K02 资金事故假处置 + 系统级开关纯内存（route_incident('funds') 翻旗无下单路径消费）
- 注册表登记态：`open` / 2026-09-18 / `#317` / **`P0高`**
- **本次实测是否仍成立**：**仍成立（亲验，两个独立断点均现网可复现）**。
  - **假处置断点**：`kill_switch_orchestrator.route_incident('funds')`→`trip(SwitchLevel.DOMAIN/SYSTEM)`→最终翻 `kill_switch.py._global_tripped`（`:244`）。而**下单路径读的探针是另一套状态**——`pre_execution_checker._kill_switch_probe`→`validator.kill_switch_active`（`default_risk_validator.py:447`，paper 会话 `start_paper_session.py:565` 接线）。**两态互不相通** → route_incident 翻的系统级 `_global_tripped` **不进入下单拒单判定** = 事故"路由"了但钱路径无反应（假处置）。
  - **探针 fail-open 独立缺陷（亲验）**：`pre_execution_checker.py:181-183` 当 `kill_switch_probe is None` 时仅 `_logger.debug("…按未激活继续")` → **探针未接线=静默放行下单**（⑥失败不响）。
  - **系统级纯内存（亲验，局部）**：`kill_switch.py`（13,798B）内 grep **无 json.dump/open(w)/state_store** → `_global_tripped` 重启即丢。**注**：`DefaultRiskValidator` 的 `_kill_switch_active` **有 record 持久化**（`:144-172`），故"重启即丢"**特指编排器系统级开关**，非 validator 自有开关——须精确表述。
- 精确锚点：`src/zephyr/autonomy_core/kill_switch_orchestrator.py:432`（route_incident）；`src/zephyr/security/access_control/kill_switch.py:150/244`（`_global_tripped` 内存态）；`src/zephyr/ex_core/pre_execution_checker.py:181-183`（探针缺省 DEBUG 放行）；`src/zephyr/risk/implementations/default_risk_validator.py:447`（下单实际读的开关）
- 证据：`grep -rn "route_incident" src`→emergency_track_guardian.py:562 是唯一非 test 调用（且该保命轨 auto-trip 未启用，R-022③）；`grep -n "json.dump\|state_store" kill_switch.py`→空。
- 断点类型：**⑥失败不响**（资金事故路由了但钱路径静默不响）+ ③出口无货（系统级开关不持久=事故现场不落地）。
- 处置选项：①把 route_incident→SYSTEM 的 `_global_tripped` **统一为下单探针的单一权威源**（让 pre_execution_checker 真读它）+ 系统级开关 crash-only 持久化（对标 Nautilus）②探针 None 改 fail-closed（缺探针=拒单不 DEBUG 放行）③显式登记"当前 funds 事故仅写审计 jsonl 不阻下单"为已知降级。代价：改钱路径闸语义=high 域，须配能红测试钉（不 mock 防线自身）。风险：统源若把三套态并错=可能误拒正常单或漏拒真事故单。
- 影响面：**头号资金安全面**。**触 Owner/Max 门位部分**：保命轨 `emergency_track_guardian` 盘内 auto-trip（R-022③已列 Max，Flash 不签）；本条"统源+持久化"本身是架构接线（不必然门位，但涉钱路径改动需严测）。
- 总包预裁对照：**R-K6 一致**（假处置必须改真处置或显式 fail-closed）；R-K6 已给具体实例 `scheduler.py:732-762`（`8a8a3f9290` 已落地）。本条是 R-K6 在 kill switch 路径的**第二个具体实例**，可补充进 R-K6 案。
- **建议裁定 + 依据等级**：**建议裁=统源 + 系统级 crash-only 持久化 + 探针 None 改 fail-closed**，三件均配能红测试钉；保命轨 auto-trip 维持 R-022③不启用等 Owner。**依据：假处置断点=亲验；两态不通的完整闭环需 Max 复核=亲验偏强、统源方案=推断**。

## #ARCH-341 K08 先报告后交易闸从未武装（report_gate 全仓零注入、broker_ack 0/6）
- 注册表登记态：`open` / 2026-09-18 / `#309` / **`P0高`**
- **本次实测是否仍成立**：**完全成立（亲验，逐条可复现）**。
  - `ReportGate(` 全仓**零实例化**（grep 返回空）→ 唯一消费点 `order_manager.py:365-366 if self._report_gate is not None: check()` 因**8 个 `OrderManager()` 构造点全部不传 report_gate**（默认 None）而永不触发。
  - `compliance_report_registry.yaml`：6 个 `required: true` 项（RPT-ACCOUNT-INFO/SOFTWARE-INFO/STRATEGY-TYPES/MAX-ORDER-RATE/MAX-DAILY-ORDERS/MAJOR-CHANGE）**全部 `broker_ack: false`** → **"0/6"精确核实**。
  - 结构性后果：`ReportGate.check()`（`:156` 缺 ack 项→BLOCK）逻辑正确且 fail-closed（`:8` INVARIANTS 登记表不可读=Fail-Closed BLOCK），**但若现在武装，6 项 0 ack→全单被 C-002 拒→交易砖化**。故"未武装"是**有意的 fail-closed 闸被刻意停在 off**，非疏漏可径行打开。
- 精确锚点：`src/zephyr/ex_core/order_manager.py:155/168/365`（有参数+消费，无装配）；`src/zephyr/compliance/compliance_report_registry.py:134/156`（闸逻辑）；`docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml:35-76`（6 项 broker_ack 全 false）
- 证据：`grep -rn "ReportGate(" src`→空；`grep -c "broker_ack" <yaml>`=6 全 false；`grep -n "OrderManager("`→8 处均无 report_gate 实参。
- 断点类型：⑥失败不响（监管红线 C-002 未生效=出事不拒）+ ④下游无取（闸码有、无装配方注入）。
- 处置选项：①维持 off 并**显式登记"生产侧监管闸未武装、broker_ack 数据流未建"为受控降级**（当前实况，风险最低）②建券商 ack 数据流（人工/AI 置 broker_ack 真值）后再择时点武装 ③引入"部分项可先武装"细粒度门。代价：②依赖外部券商报送渠道（人工）。风险：**盲武=C-002 全拒单砖化交易**（注册表原话，实测逻辑印证）。
- 影响面：**监管红线面**。**触 Owner 门位**：武装时点 + broker_ack 数据源属 production 流转/外部数据，须 Owner 定（§7）。
- 总包预裁对照：无 R-K 直配；与晨报 §1.5 一致（不裁不动）。
- **建议裁定 + 依据等级**：**建议裁=维持 off + 显式受控降级登记 + 备券商 ack 工单**，武装与否交 Owner。**依据：全条亲验**。

## #ARCH-342 对账链双零接线 + 结算单缺失日绿灯（ThreeWayReconEngine/EodReconciler 仅在测试；15:30 纸面）
- 注册表登记态：`open` / 2026-09-18 / `#317` / `P1高`
- **本次实测是否仍成立**：**仍成立（亲验），并避坑 R-013**。
  - `ThreeWayReconEngine(` / `EodReconciler(` 全仓非 test **零实例化**（grep 返回空）→ "双零接线"核实。定义分别在 `trading/three_way_reconciliation.py:52`、`ex_core/eod_reconciliation.py:253`。
  - `build_post_settlement_jobs`（15:30 硬时点纸面）非 def/test 命中=2，须辨是否调用方；本车道未追实跑 → 子项标转报。
  - **避坑（R-013 实测更正）**：`orchestrator/execution/reconciliation_loop.py` **不是成交对账链**（调编排器自完整性五不变量），普查曾误归因；本案卷按真缺口 `execution_report 零读者/无事件扇出` 评估，**未把 reconciliation_loop 当对账链**。
  - **七件并存不重复评估**：对账实现七件全零消费差异表引用 `docs/_working/fullflow_campaign/lanes/registry_recon_six_implementations.md`（R-015）。
- 精确锚点：`src/zephyr/trading/three_way_reconciliation.py:52`、`src/zephyr/ex_core/eod_reconciliation.py:253`；差异表 `lanes/registry_recon_six_implementations.md`
- 证据：`grep -rn "ThreeWayReconEngine(\|EodReconciler(" src scripts --include=*.py | grep -v test`→空；`ls lanes/registry_recon_six_implementations.md`→存在(8417B)。
- 断点类型：④下游无取（对账引擎零生产消费）+ ⑥失败不响（eod cash_checked=False 不告警）+ ⑤哨兵缺位。
- 处置选项：①**必须事件触发**接线（禁 cron/Timer/sleep-loop，R-K10）——成交事件→`PositionReconciler.handle_execution_report`（z-wire-recon 处方 G6）②随 #317 盘中对账改造一并接 ③Fill 契约加 `side` 字段（R04 公式忽略买卖方向）。代价：涉 6 文件语义比对 + 删冗余触注册表净删=Owner 门位。风险：按"孤儿"字面接错对象=造假闭环（R-013 教训）。
- 影响面：对账断链=钱/仓不一致不可见。**触 Owner 门位部分**：删冗余对账实现=注册表净删（§7）。
- 总包预裁对照：**R-K10 一致**（事件触发 + 判重 `check_tick_duplication.py` 禁聚合数）；**采纳 R-013 更正**（避开 reconciliation_loop 误归因）；**采纳 R-015**（七件差异引用 registry_recon 文件不重复评估）。R-K10 提到 z-wire-recon `eef42ae008`/z-land2 `175f837e89` 落地进度：本车道未独立核 commit 内容，标转报（R-027 账本记 `eef42ae008`=FF-12 闭环首通、`175f837e89`=execution_report 生产端四件套落地）。
- **建议裁定 + 依据等级**：**建议裁=先立"唯一入口"（盘中 position 事件入口 + 日终 recon_runner）、其余标 superseded_by，事件触发接线随 #317**。**依据：双零接线=亲验；落地进度 eef42/175f=转报**。

## #ARCH-343 pf_alloc 整域接线/退役裁定（7 件仅 W03 真接线）
- 注册表登记态：`open` / 2026-09-18 / `#304/#306` / `P1高`
- **本次实测是否仍成立**：**核心成立，但 headline"仅 W03 真接线"口径与 import 面不符（亲验，需修）**。
  - in-pkg 非 test importer 计数：W01 signal_synthesis_combiner=2、W02 regime_bma_weighting=0、W03 regime_meta_allocator=5、W04 strategy_correlation_gate=4、W05 risk_budget_allocator=5、W06 tail_hedge_signal=0、W07 maxdd_limit_allocator=0。
  - → W02/W06/W07=0 importer（**孤儿成立**）；W01/W04/W05 **有 in-pkg importer**，"仅 W03 真接线"**在 import 层不成立**。但"in-pkg importer"≠"生产 orchestrator 可达"（可能互引成孤儿子网）——**生产可达性终判属 z-land3**（R-K12 落地权）。
  - C04 veto 路径 `total_exposure=0/cash_reserve=全额`（接线即 P0）、W05 risk_parity≈inverse_var 逐位相同（模式开关无效）：本车道未复算 → 转报 rpt_c04/rpt_w05（晨报 §2/§3 记为"实测复现"）。
- 精确锚点：`src/zephyr/pf_alloc/core/regime_meta_allocator.py`（W03，ledger 称唯一真接线）；W05 `src/zephyr/pf_alloc/core/risk_budget_allocator.py:29`；差异/importer 实测见本条证据
- 证据：`for m in …; do grep -rl "$m" src/zephyr --include=*.py | grep -v /$m.py | grep -viE test | wc -l; done`（计数见上）。
- 断点类型：④下游无取（W02/W06/W07 零 importer）+ ③出口错货（C04 veto 若接线=静默错账）+ 口径矛盾。
- 处置选项：①整域裁决"接线（含 W05 真 ERC 立卡）/退役"（注册表原裁）②先补生产可达性 trace 把"W01/W04/W05 是否真在钱链"钉死再裁 ③C04 veto 单独列 P0 先治（接线前必修）。代价：整域涉 pf_alloc 落地权在 z-land3（R-K12）。风险：按"仅 W03"口径退役可能删掉真被 orchestrator 调的件。
- 影响面：组合资源配置=钱链上游。**接线落地涉 pf_alloc（z-land3）+ 触 production 流转门位**。
- 总包预裁对照：**R-K12 一致**（落地权 z-land3，本车道只出案卷）。**不一致处**：headline"仅 W03 真接线"import 层不成立，已明说并以 importer 计数为准。
- **建议裁定 + 依据等级**：**建议裁=交 z-land3 出"生产可达性 trace 后再逐件裁"；C04 veto 先挂 P0 前置**。**依据：importer 计数=亲验；"仅 W03"被推翻=亲验；C04/W05 复算=转报**。

## #ARCH-344 Regime 断供即满部署三腿（D01 均匀分布/D12 参数缺失→1.0/D05 detect→1.0）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**三腿均成立（亲验 2/3 + 结构确认 1/3）**。
  - **D01（亲验）**：`regime_detector.py:716 return {s: 1.0/n_states for s in HMM_STATES}`（异常/无法 fit 时→4 态均匀分布，max P=0.25）；`:669` except 亦回 `np.full(..., log(1/n_states))`。**断供→均匀分布** 核实。
  - **D12（亲验）**：`risk_signal_builder.py:137 params[pid]=1.0`（数据缺失参数→系数 1.0=不收缩）；`:8` INVARIANTS 明文"无异常=1.0 / 数据缺失→参数=1.0降级"。**断供→1.0** 核实。
  - **D05（结构确认，偏转报）**：`regime_feature_builder.py` 多处 except（`:430/467/518`）+ `:489 schedule[dt]=1.0 # warmup 期满部署`；"detect 异常→1.0" 具体行未逐一定位，但降级到"满部署/不收缩"语义与 D12 同族一致。
- 精确锚点：`src/zephyr/regime/core/regime_detector.py:716`；`src/zephyr/regime/risk_signal_builder.py:137`；`src/zephyr/regime/regime_feature_builder.py:489`
- 证据：见上 sed/grep 输出（三处 fallback 常量可指认）。
- 断点类型：**⑥失败不响**（数据事故日局部保守合成"全局风险机制静默失效"→危机时全账户敞口放大而不响）。
- 处置选项：三腿统一 fallback 语义裁定=**hold-prev / 防御上限 / 告警显化**（注册表原选项）。R-K9 已预裁方向：断供时**降级 fail-closed 不允许交易**，禁 fail-open 默认继续 + 每腿加哨兵阈值行。代价：改 fallback 会改变正常运行期仓位行为（须灰度）。风险：三腿若各自改而不统一=新的口径漂移。
- 影响面：regime=生死线三件套之首，断供即满部署=**最大回撤放大器**。**触 Owner/Max 门位部分**：断供"自动禁交"=系统主动做"停"的动作（参 R-022③ 逻辑），启用自动禁交属资金影响面。
- 总包预裁对照：**R-K9 一致**（三腿独立供数+哨兵阈值行+断供 fail-closed 禁交，禁 fail-open）。
- **建议裁定 + 依据等级**：**建议裁=R-K9 落地（三腿各加哨兵阈值行 + 断供降级 fail-closed 禁交 + 显式告警），统一 fallback 语义**。**依据：D01/D12=亲验；D05=结构确认（偏转报）**。

## #ARCH-345 Wyckoff 证伪旁路（WYF-3 置零只封主出口，overlay_features.s2_wyckoff_score MVP 回退支弱 guard 静默接管）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**结构成立（亲验锚点 + 转报数值）**。
  - `overlay_signals_builder.py:395 cache["wyckoff"]=overlay_features.s2_wyckoff_score(...)` 在**弱 guard `if close is not None:`（:394）下**执行，委托 MVP 回退支。锚点行号 394（guard 行）/395（调用行），注册表记 394=吻合（±1 系 guard/调用之别）。
  - 弱 guard 含义：只判 `close` 存在即接管，**不判 WYF-3 证伪标志** → 证伪置零封的是引擎主出口，回退支绕过证伪门。
  - "可达 70>门槛 60"数值：本车道未跑 s2_wyckoff_score 打分实证 → **转报 rpt_d09/rpt_d11**。
- 精确锚点：`src/zephyr/regime/overlay_signals_builder.py:394-395`
- 证据：`sed -n '385,400p' overlay_signals_builder.py`→ `if close is not None:` 下 `cache["wyckoff"]=…s2_wyckoff_score`。
- 断点类型：**⑥失败不响**（证伪门被静默旁路=该拦不拦）+ ①入口（旁路喂进未证伪信号）。
- 处置选项：①旁路拆除（回退支也过 WYF-3 证伪标志）②等强证伪门（overlay_features 层统一 gating）③**合法用例改为显式登记的豁免通道（留痕可审计），禁隐式旁路**（R-K7）。代价：需先辨"回退支有无正当使用场景"。风险：直接拆旁路可能打掉当前依赖回退的实盘 overlay。
- 影响面：overlay 直接改仓位语义（rpt_d11）。
- 总包预裁对照：**R-K7 一致**（旁路收口，合法用例改显式登记豁免通道，禁隐式旁路）。
- **建议裁定 + 依据等级**：**建议裁=R-K7——回退支纳入证伪 gating；确需回退则走显式登记豁免（留痕）；禁弱 guard 隐式接管**。**依据：旁路结构=亲验；70>60 数值=转报**。

## #ARCH-346 验证链 embargo/purge 双承载与缺省归零（B05 pit_query 默认 0；B09 名义 CPCV 裸 CV；B08 无 purge/embargo）
- 注册表登记态：`open` / 2026-09-18 / `#306` / `P1高`
- **本次实测是否仍成立**：**B09 成立（亲验）；B05 记载口径存疑（亲验反证）；B08 转报**。
  - **B09（亲验，完全吻合）**：`cpcv.py:109 t1=None, :110 embargo=0` 缺省；`:118` 注释"t1 为 None 时…退化为无 purge" → **名义 CPCV 实为裸 CV** 核实。
  - **B05（亲验反证，口径需核）**：`pit_manager.py:82 embargo_days: int = DEFAULT_EMBARGO_DAYS`，docstring `:78`"默认5"。注册表称"pit_query 默认 0"——**pit_manager 自身默认=5 不是 0**；"默认 0/零传参"疑指 backtest 数据路径里另一消费点 `pit_query`（非本件），本车道未定位到该符号 → **记"证据不足，注册表锚点可能张冠李戴"**。
  - **B08（转报）**：walk_forward 三模式无 purge/embargo 能力，本车道未核 → 转报 rpt_b08。
- 精确锚点：`src/zephyr/backtest/core/cpcv.py:109-110,118`（B09 亲验）；`src/zephyr/backtest/core/pit_manager.py:82`（B05 反证，默认=5）；B08：`walk_forward.py:88`（未核）
- 证据：`grep -n embargo src/zephyr/backtest/core/pit_manager.py`→`DEFAULT_EMBARGO_DAYS`(默认5)；`grep -n "t1.*None\|embargo.*0" cpcv.py`→`:109/:110`。
- 断点类型：⑥失败不响（PIT 隔离缺省归零=前视泄漏静默放行）+ 口径（"默认 0"与"默认 5"混记）。
- 处置选项：①先更正 B05 锚点（到底哪个符号默认 0/是否真存在该符号）②embargo/purge 默认值与消费方统一（LdP 语义，R-056 轴F 对齐）③B09 缺省改"显式要求传 t1/embargo 否则 raise"（fail-closed）。代价：改缺省会打断既有裸 CV 调用方。风险：B05 若本无默认 0 缺陷而径改=无病呻吟。
- 影响量：PIT 失守=回测/研究全虚。**不触 Owner**（缺省值裁定级）。
- 总包预裁对照：无 R-K 直配。
- **建议裁定 + 依据等级**：**建议裁=B09 先行（缺省 fail-closed 要求显式 t1/embargo）；B05 先更正锚点再裁；B08 待 rpt 复核**。**依据：B09=亲验；B05"默认 0"=亲验反证（真实缺陷证据不足）；B08=转报**。

## #ARCH-347 策略管线三洞 T02 intake fail-open / T05 窗冻结 / T06 晋升 API token=None 零认证 CORS*
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**T06 完全成立（亲验，最危险）；T02/T05 转报**。
  - **T06 CORS 全源（亲验）**：`api_server.py:57 app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])`。
  - **T06 无鉴权+服务端自取密钥（亲验）**：`api_server.py:4350 @app.post("/api/promotion-decide")`→`:4351 def promotion_decide(body: dict)` **无 Depends/无 token 校验**→`:4375 _pa.decide(advisory_id, decision, token=None, via="frontend")`；`:4356` docstring 自承"S12 无签发体系前的最小半径"。→ **任意网页 drive-by localhost 可批晋升（Owner 门位数字化）**，且 token=None 服务端自取密钥。
  - T02 intake decay=None/空 segments 三条件静默通过、T05 滚动窗不在指纹内：本车道未核 → 转报 rpt_t02/t05。
- 精确锚点：`src/zephyr/frontend/dashboard/api_server.py:57`（CORS*）、`:4350-4351/4375`（promotion-decide 无鉴权 token=None）
- 证据：`grep -n "allow_origins\|promotion-decide\|token=None" api_server.py`→命中上述三处。
- 断点类型：**⑤哨兵缺位 + ⑥失败不响**（无鉴权闸=缺省不拒、drive-by 直通资金/晋升门位）。**全流通唯一"外部攻击面直通资金"项（R-K5）。**
- 处置选项（方案，非落码，D_FRONTEND human_gated）：①`/api/promotion-decide` 加 token 鉴权，**缺省 fail-closed 401 + 审计落痕**，令牌走 `zephyr.security.secrets`（禁裸 getenv），**127.0.0.1 缺省不豁免** ②CORS 收白名单 origin（收口 `api_server.py:57`）③晋升动作二次确认落 Owner 门位记录。改动点：`api_server.py:57`（origins 列表）+ `api_server.py:4350/4351`（加 `Depends(verify_token)`）。代价：需先建令牌签发体系（现"无"）。风险：收 CORS 可能打断合法前端联调。
- 影响面：**唯一外部攻击面直通资金/晋升门位**。**触 Owner 门位**：D_FRONTEND human_gated（本车道只出方案+精确改动点，**未改前端代码**）+ 真实凭据/签发体系=Owner。
- 总包预裁对照：**R-K5 一致**（必须加鉴权且缺省 fail-closed；令牌走 secrets 禁裸 getenv；401+审计落痕；127.0.0.1 缺省不豁免；D_FRONTEND 只出方案）。
- **建议裁定 + 依据等级**：**建议裁=按 R-K5 落 token 鉴权 fail-closed + 收 CORS；先建签发体系为前置**。**依据：T06/CORS=亲验；T02/T05=转报**。

## #ARCH-348 卖出族族内对账（E03/E06 同 spec 双实现分化；E02/E01 对 UNKNOWN 共振口径相反；E04 RISK 子串匹配脆弱）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**双实现并存成立（亲验存在性）；分化细节转报**。
  - E03 `src/zephyr/sell_decision/core/stop_loss_strategy.py` 与 E06 `src/zephyr/sell_decision/core/scaling_out.py` **均存在**（`ls` 确认）→ "同 spec 双实现"存在性核实。
  - "E03 降级锚已矫、E06 为正确示范"、"E02/E01 UNKNOWN 口径相反"、"E04 RISK 子串匹配脆弱"：本车道未逐行 diff → **转报 rpt_e01-e06**（晨报 §2.22 记 E03 已治本，与注册表一致）。
- 精确锚点：`src/zephyr/sell_decision/core/stop_loss_strategy.py:121`、`src/zephyr/sell_decision/core/scaling_out.py`
- 证据：`ls src/zephyr/sell_decision/core/{stop_loss_strategy,scaling_out}.py`→两文件在。
- 断点类型：④下游无取/口径（族内对账未统一，接电前风险）——**晨报明"未接线无现行损失"**，属接线期地雷。
- 处置选项：①接电前族内对账统一（注册表原裁）②以 E06 为示范收敛 E03/E01/E02/E04 ③E04 改结构化枚举匹配替代子串。代价：涉 sell_decision 域语义。风险：口径不一致时接线=同信号双实现给出相反卖出建议。
- 影响面：卖出决策一致性。不触 Owner（族内对账属语义裁定）。
- 总包预裁对照：无 R-K 直配。与晨报一致。
- **建议裁定 + 依据等级**：**建议裁=接电前族内对账统一（E06 为真源示范）**。**依据：双实现存在=亲验；分化细节=转报**。

## #ARCH-349 信号域接线期地雷（S03 单 NaN 毒化全横截面/S08 五维默认=通过 fail-open/S11 缺数据双满分）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**S03 score_fine 零调用方成立（亲验）；S08/S11 细节转报**。
  - **S03（亲验）**：`grep score_fine`非 def/test 命中=1（几乎确定是头注/CONSUMERS），**score_fine 无真实生产调用方** → "接线期地雷，接线时必修"核实（ledger s03 同记"score_fine 零调用方"）。
  - S08 粗筛五维默认值=通过值（全域唯一 fail-open 反例）、S11 缺数据双向各拿满分、MATURITY=production 标签漂移 5 例：未逐件核 → 转报 rpt_s01-s12。
- 精确锚点：`src/zephyr/signal_ashare/fine_scoring_engine.py:52`（S03 score_fine 零调用方）
- 证据：`grep -rn "score_fine" src/zephyr --include=*.py | grep -viE "test|def score_fine" | wc -l`=1。
- 断点类型：**⑥失败不响**（S08 默认=通过 fail-open、S11 缺数据加分非中性、S03 单 NaN 毒化全排名）+ ④（未接线）。**接线期地雷，未接线无现行损失（晨报口径）。**
- 处置选项：①接线前逐件矫治（NaN 防御/默认≠通过/缺数据=中性非满分）②MATURITY 标签治理（去 production 虚标）③S01/S04、S05/S12 双承载/loader 同族病根合并。代价：件多（S01-S12）。风险：接线与矫治不同批=先接线带雷。
- 影响面：选股/信号全域。不触 Owner（接线期矫治）。
- 总包预裁对照：无 R-K 直配。与晨报一致。
- **建议裁定 + 依据等级**：**建议裁=接线前置闸：S03/S08/S11 逐件矫治 + MATURITY 治理，未矫不接**。**依据：S03 零调用方=亲验；S08/S11 反例=转报**。

## #ARCH-350 数据基建三洞（I03 熔断仅本进程/I08 ch_writer 缓存投毒+绕 quality_gate/I09 FINAL 三通道静默失效）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**I08 绕 quality_gate 成立（亲验）；缓存投毒/FINAL 静默失效转报；I03 未核**。
  - **I08 绕过 quality_gate（亲验）**：`ch_writer.py` 内 grep **无 `quality_gate` 引用** → "主写入链绕过 quality_gate"核实（无该调用）。
  - **I08 缓存投毒（转报，未亲验）**：`ch_writer.py:603 table_cols_cache: dict` 存在，`_invalidate_tcp_client/http_host`（`:288/317`）是**连接缓存**失效，**未见 table_cols_cache 的对应 invalidate 清理** → 与"空串永久缓存 invalidate 不清"方向吻合，但"CH 故障后 FINAL 全表永久失效"完整路径未追 → 转报 rpt_i08。
  - I03 pause/resume 仅本进程内存生效（常驻调度器熔断无效）、I09 FINAL 三通道静默失效：本车道未核 → 转报。
- 精确锚点：`src/zephyr/data/ch_writer.py:603`（table_cols_cache 无配套 invalidate，亲验偏结构）；quality_gate 绕过：`grep quality_gate ch_writer.py`→空（亲验）
- 证据：`grep -n "quality_gate" src/zephyr/data/ch_writer.py`→空；`grep -n "table_cols_cache\|_invalidate" ch_writer.py`→603/288/317。
- 断点类型：⑥失败不响（缓存投毒/ FINAL 静默失效=读到旧值不报）+ ③出口错货（FINAL 永久失效→聚合口径错）+ ⑤（I03 熔断不跨进程）。
- 处置选项：①缓存失效治理（table_cols_cache 加与连接失效联动的 invalidate）②主写入链接 quality_gate 或显式登记"写链不经过质量闸"及其边界 ③I03 熔断落盘/跨进程生效裁定。代价：热路径改动（写入链）。风险：缓存策略改动可能引入性能/一致性回归。
- 影响面：CH 读写地基（全数据链）。不直接触 Owner；写链改 quality_gate 属接线（z-land 域）。
- 总包预裁对照：无 R-K 直配。
- **建议裁定 + 依据等级**：**建议裁=缓存失效联动治本 + 写链 quality_gate 边界显式化；I03/I09 补实测再裁**。**依据：绕 quality_gate=亲验；缓存投毒完整路径=转报；I03/I09=证据不足未核**。

## #ARCH-351 自动化任务族退路与 DAG 系统洞（miniQMT 退役 24 任务无退路 / TF07 daban 名义 DAG 边 / TF15 不在哨兵 16 表）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**TF07 名义 DAG 边完全成立（亲验）；miniQMT 依赖成立但"24"子集计数未复现（转报）；TF15 未核**。
  - **TF07（亲验，R-K11 核心）**：`daban_board_event_derive`（tasks.yaml:1637）`schedule: weekend_calibration`（**周频**）→ 产 `daban_board_event`；`daban_engine_load_daily`（`:3387`）`schedule: daily_kline`（**日频**）、`:3389` 注释"读 c1_market.daban_board_event 事件"、`:3393 dependencies:["daban_board_event_derive",…]`、`:3390` 注"trade_date=打板事件日…T 日盘前消费"。**日频任务依赖周频产出=名义 DAG 边**，task_queue 视依赖"已满足"→周二至周五装载上周事件=PIT 污染，**实盘相关**。
  - **miniQMT 依赖（亲验总量）**：`grep -c "source: miniqmt" tasks.yaml`=**63 个任务行**以 miniqmt 为主源。注册表"24 任务无退路"（TF01 8 主源/TF02 16 全裸）为**特定子集**——本车道 awk 粗扫仅命中 4 个紧邻 `fallback_sources: []`，**无法可靠复现 24 这个数**（R-024 纪律：不编造）→ **"24"标转报 rpt_tf01/tf02**，退路矩阵须由该报告 + 规范化 fallback 扫描产出。
  - TF15 trade_calendar 不在哨兵 16 表：未核 → 转报。
- 精确锚点：`src/zephyr/data/config/tasks.yaml:1637-1643`（derive weekend）、`:3387-3393`（load daily 依赖 derive）
- 证据：`grep -n "daban_board_event_derive\|daban_engine_load_daily" tasks.yaml -A6`→cadence 与 deps 见上；`grep -c "source: miniqmt" tasks.yaml`=63。
- 断点类型：**①入口无料**（miniQMT 退役=24/63 任务断供且无退路）+ **⑤哨兵缺位**（TF15 不在哨兵表；且参 R-026/R-013 现有哨兵按 ingest_ts 判滞后，可能根本测不出这次断供）+ 名义边=①/③（日消费读过期周数据=PIT）。
- 处置选项：①退役映射表**逐任务改接**（R-K8，禁简单删任务=删即断供→哨兵 breach）②TF07 名义边补真边（derive 改日频）或显式标注名义+消费侧加 freshness 断言（R-K11）③TF15 补哨兵阈值行。代价：逐任务 matrix 工作量大（tasks.yaml 归 residG，本车道只出案卷）。风险：**R-006/R-026 交叉警示**——评估"删任务会不会致哨兵 breach"须同时说明"现有哨兵按 ingest_ts 判滞后可致盲、可能测不出本次断供"，勿据"breach=0"误判安全。
- 影响面：**实盘相关**（打板引擎日消费）。**涉生产流转/实盘门位**（9/18 退役是 production 流转）。
- 总包预裁对照：**R-K8 一致**（逐任务改接禁删任务 + tasks.yaml 归 residG）；**R-K11 一致**（名义边补真或显式标注=PIT 污染）。**R-K8 交叉警示一致**：本案卷已写明"现有哨兵可能测不出断供"。
- **建议裁定 + 依据等级**：**建议裁=①TF07 derive 改日频或消费侧加 freshness 断言（P0 实盘）②miniQMT 退路矩阵按 rpt_tf01/tf02 逐任务出（24 数待规范化复算）③TF15 补哨兵 + 同步修哨兵判据按业务日期**。**依据：TF07=亲验；63 miniqmt 行=亲验；"24无退路"=转报（未复现）；TF15=证据不足**。

## #ARCH-352 告警无推送通道（飞书/SMTP 裁撤后=日志+json+前端页纯被动；health 失败无 notify，最坏 14h）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P1高`
- **本次实测是否仍成立**：**已闭合（部分）（亲验落地态）**。
  - **机制已建已接线（亲验）**：`src/zephyr/data/alert_webhook_dispatch.py`（35,588B）+ `config/alert_webhook.yaml`（3,316B）**在盘**；触发点 `Alerter._fanout_critical`（`alerter.py:182`）`:192 from zephyr.data.alert_webhook_dispatch import dispatch_on_failure_event` → **事件触发外发已接**（零轮询，符合 R-K4/§9.3）。
  - **但 untracked 未落 HEAD（亲验）**：`git cat-file -e HEAD:…alert_webhook_dispatch.py`→**not in HEAD**。z-alarm 交的是 2 笔入队（R-031），落地待 serializer 消化 → **案卷时点未落地**。
  - **剩余缺口=无真实外部接收方（黄-门位）**：通道端点凭据属 Owner（BRK-055），零内置厂商通道（R-K4 缺省 fail-closed）→ 无凭据即 blocked/failed 投影到 OpsAlertFeed 红条，无真外发。**此为"原语已建、外发未活"的部分闭合**，与 R-K4 预裁完全一致。
- **R-K4 指定并核项（亲验）**：`flags.py:345-360` 加载循环**只按顶层 key 注册 FeatureFlag、state 仅取 `spec.get("enabled")`**（`:351-357`）→ 嵌套子键如 `flags.alerts.auto_escalation` **根本不进 FlagRegistry**（`is_enabled` 查不到）→ **翻该子键零效果**。若某 #ARCH 条目把"升级(auto_escalation)"列为未做能力，**其真瓶颈是 flag 注册机制（缺唯一读者/嵌套子键不支持），不是 flag 值**。已写进本条。
- 精确锚点：`src/zephyr/data/alert_webhook_dispatch.py`（在盘未落 HEAD）；`src/zephyr/data/alerter.py:182/192`（触发点）；`src/zephyr/shared/foundation/flags.py:348-358`（嵌套子键不入注册表）
- 证据：`git cat-file -e HEAD:src/zephyr/data/alert_webhook_dispatch.py`→"not in HEAD"；`sed -n '345,360p' flags.py`→注册循环仅 `reg.register(FeatureFlag(key=str(key), … spec.get("enabled")))`。
- 断点类型：**⑥失败不响**（原语态：health 失败路径无 notify）——**本案卷判已闭合（部分）后残余=黄-门位（缺真实外部接收方）**。
- 处置选项：①先落 HEAD（z-alarm 2 笔入队，等 serializer / 或催办）②Owner 给四类 webhook 凭据后接通真接收方（门位）③auto_escalation 若要生效，先建"唯一读者"并扩 flags 支持嵌套子键（escalation_flip_prereq P1-P6）。代价：凭据属 Owner 非我可控。风险：**禁判绿**（无真外发方=⑥向未真证明）；勿因"机制已建"当"通道已通"。
- 影响面：告警出口（全战役 ⑥向兜底）。**触 Owner 门位**：真实外部凭据（BRK-055）。
- 总包预裁对照：**R-K4 一致**（可插拔 webhook + 缺省 fail-closed + 零内置厂商通道；已交付件；剩余缺口=无真实外部接收方=黄-门位）；**R-K4 并核项一致**：auto_escalation 翻旗零效果=亲验（flags.py:345-360 机制根因），已写入。
- **建议裁定 + 依据等级**：**建议裁=判"已闭合（部分）"→落 HEAD（催 z-alarm 队列）→ 剩余"无真实外部接收方"标黄-门位交 Owner 凭据；auto_escalation 走"先建唯一读者+flags 嵌套支持"非翻值**。**依据：落地态/触发点/flags 机制=全亲验**。

## #ARCH-353 F02 因子阶段闸恒真 + G01 基本面合成器 stub
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P2中`
- **本次实测是否仍成立**：**G01 uuid-in-idempotent-key 成立（亲验）；G01 "只写不读"已修（亲验反证）；F02 转报**。
  - **G01 幂等键含 uuid（亲验）**：`signal_synthesizer.py:120 return f"syn-{symbol}-{ts}-{uuid.uuid4().hex[:8]}"` → **幂等键非确定性** → 复算必产不同键=无法去重，"复算实锤"核实。
  - **G01 registry 恒空（亲验反证，部分更新）**：`:73 _registry` dict + `:83/88` 已加**读取 API**（注释"5.116.2 修复: 消除只写不读"）→ "只写不读"子claim**已修**；但"恒空"（无 concrete synthesizer 子类注册）本车道未实证 → registry 有读者但可能运行时为空，转报。
  - F02（ITERATION→VALIDATION 后底层 FSM=retired 且回炉因子照常注册 + 三重门禁缺省 `lambda:True` 全开）：未核 → 转报 rpt_f02（晨报 §2 记 F02 为"复算实锤"）。
- 精确锚点：`src/zephyr/signal_fundamental/synth/signal_synthesizer.py:120`（uuid 幂等键，亲验）、`:73/83`（registry 已有读者，反证只写不读）；F02 `src/zephyr/factor/factor_factory.py:78`（未核）
- 证据：`grep -n "uuid\|_registry" signal_synthesizer.py`→`:50 import uuid`、`:120 …uuid.uuid4()…`、`:83 提供 _registry 读取 API,消除只写不读`。
- 断点类型：F02 恒真门禁=**⑥失败不响**（三重门 lambda:True 全开）；G01 stub=③出口无货（uuid 键使产物不可幂等复算）。
- 处置选项：①G01 幂等键去 uuid（确定性：symbol+ts+内容 hash）②G01 stub 填实或退役 ③F02 门禁缺省改 fail-closed（lambda:True→须显式注册否则 BLOCK）+ FSM 回炉态治理。代价：F06 挖矿基建接线前必修。风险：幂等键改法若破坏既有已入库因子键=需回填。
- 影响面：因子/基本面管线。P2（接线前）。不触 Owner。
- 总包预裁对照：无 R-K 直配。
- **建议裁定 + 依据等级**：**建议裁=G01 幂等键去 uuid + stub 填实或退役；F02 恒真门禁 fail-closed 化（接线前）**。**依据：G01 uuid=亲验；只写不读已修=亲验反证；F02=转报**。

## #ARCH-354 预测域接线期必修（M04 NaN→(nan,nan)/M03 NaN 裸奔/M02 symbol 直插 SQL）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P2中`
- **本次实测是否仍成立**：**M02 symbol 直插 SQL 成立（亲验）；M03/M04 细节转报**。
  - **M02（亲验）**：`next_day_8state_forecast.py:316 sql = _SQL_INDEX_KLINE.format(table=…, symbol=symbol, start=…, end=…)`——**symbol 经 `.format()` 字符串插值进 SQL**（非参数化绑定）→ "symbol 直插 SQL"核实。风险=非法 symbol 可注入/破 SQL（本仓是内部 symbol，实际危害偏代码规范但违反参数化）。
  - M04 044 主件 NaN→区间(nan,nan)、M03 NaN 全链裸奔（window=0 与 config 校验已矫，ledger m03"已收口"）：未逐行核 → 转报 rpt_m03/m04。
- 精确锚点：`src/zephyr/signal_ashare/ml_forecast/next_day_8state_forecast.py:67`（`SELECT … FROM {table} FINAL` 模板）`:316`（.format 插 symbol）
- 证据：`grep -n "\.format(\|SELECT" next_day_8state_forecast.py`→`:67` SQL 模板含 `{table} FINAL`、`:316` .format(table=…,symbol=…)。
- 断点类型：**③出口错货**（NaN 区间/裸奔产出貌似合理错数）+ M02 代码规范/注入面。
- 处置选项：①M02 SQL 参数化（symbol 走绑定参数，非 .format）②M04/M03 补 NaN 防御（isfinite raise，对齐 K05/B01 已治本范式）③接线前逐件矫治。代价：低（局部）。风险：NaN 防御改法可能把既有静默降级转 raise 需回归。
- 影响面：预测域（选股输入）。P2（接线前）。不触 Owner。
- 总包预裁对照：无 R-K 直配。
- **建议裁定 + 依据等级**：**建议裁=M02 参数化 SQL + M03/M04 NaN fail-closed（接线前）**。**依据：M02 .format 插 symbol=亲验；M03/M04 NaN 链=转报**。

## #ARCH-355 X05 价格笼子实盘路径形同虚设（文件桥调 check_price_cage 不传基准价→恒 UNKNOWN 原价通过）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P2中`
- **本次实测是否仍成立**：**成立（亲验）**。
  - `qmt_file_bridge_broker.py:536 cage = check_price_cage(order.side, order.limit_price, order.symbol)` — **仅传 side/limit_price/symbol，无基准价（prev_close/reference）** → CageStatus 恒 UNKNOWN → 原价通过。与注册表"文件桥调笼子不传基准价→实盘路径恒 UNKNOWN 形同虚设"逐字吻合。官方 ±2%+0.1 元规则实现本身一致（price_cage.py 未被本缺陷污染，缺的是**传参**）。
  - 对照：`miniqmt_broker.py:836 check_price_cage(` 亦调用（参数未展开核，转报）。
- 精确锚点：`src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:536`
- 证据：`grep -rn "check_price_cage" src | grep -v def|test`→ file_bridge:536 三参无基准价；tradability_preflight.py:191 另有调用（有价则有效）。
- 断点类型：**⑥失败不响**（价格合规硬约束在实盘文件桥路径静默失效=不夹边不拒）。
- 处置选项：①券商层 quote 源接入设计（注册表原裁），使文件桥调用传真基准价 ②无基准价时 fail-closed（UNKNOWN→拒单/待价，不放行）③实盘首日以真柜台 CSV 复验。代价：依赖券商 quote 数据流。风险：**恒 UNKNOWN 原价通过=越界价单可能实盘漏网**（虽模拟盘无碍，实盘相关）。
- 影响面：实盘价格合规。**涉实盘路径（接线=production，须真柜台验证）**。
- 总包预裁对照：无 R-K 直配。与晨报/ledger x05 一致。
- **建议裁定 + 依据等级**：**建议裁=无基准价 fail-closed（UNKNOWN 不放行）+ 券商 quote 源接入设计**。**依据：file_bridge 三参无基准价=亲验；miniqmt 调用参数=转报**。

## #ARCH-356 轴F 立卡清单（本战役 SOTA 对照产出，8 项）
- 注册表登记态：`open` / 2026-09-18 / `#309` / `P2中`
- **本次实测是否仍成立**：**口径更正——非"断点"，是研究/立卡 backlog（8 项）**：K02 系统级开关持久化（crash-only，与 #ARCH-340 同源）/ K05 VaR min_history=30 对 95% 分位统计不足（Hendricks 1996）/ B08 purge-embargo 对齐（与 #ARCH-346 同源）/ W05 真 ERC 迭代解（与 #ARCH-343 同源）/ B01 metrics 频率感知年化 / D01 HMM 平滑 Hungarian 匹配 / D08 ATM 方差互换口径 / F05 TA-Lib 数值对拍。
- 精确锚点：本条无单一代码断点；8 项分散在 K02/K05/B08/W05/B01/D01/D08/F05 各件（锚点在各 rpt §3 SOTA 节，转报）。
- 证据：注册表原文 `:22367-22377`（逐项列 8 项）。
- 断点类型：**N/A（非六向断点，属"待立卡评估"研究队列）**。
- 处置选项：①逐项按 mining_sop 立卡评估（注册表原裁）②与 #ARCH-340/343/346 同源项合并推进，勿重复登记 ③明确区分"代码缺陷"与"方法论 SOTA 差距"，后者不计入流通断点分母。代价：研究工时。风险：把 SOTA 差距混入"待修断点"会污染闭合率分母（R-009/R-024 教训）。
- 影响面：方法论精度（非现行资金/监管）。不触 Owner。
- 总包预裁对照：无 R-K 直配。
- **建议裁定 + 依据等级**：**建议裁=改判为"研究/立卡 backlog"非架构断点；K02/B08/W05 三同源项并入 340/346/343 处理；其余 5 项按 mining_sop 排队**。**依据：口径=亲验（读注册表原文分类）；逐项代码状态=转报**。

---

## 附录 A · 分包11 任务3 归因：`tests/rule/test_rule_red_blue.py::TestRedBlueReport::test_generate_report` 失败
- **复跑实测**：
  - 独立跑 `pytest "tests/rule/test_rule_red_blue.py::TestRedBlueReport::test_generate_report"` → **FAIL: `Expected at least 9 test results, got 0`（assert 0>=9）**（1.21s）。
  - 整文件跑 `pytest tests/rule/test_rule_red_blue.py` → **exit 0（通过）**（后台跑约 2min+，因 9 个 TestTRAE 类做静态扫描）。
- **归因（数据/日期/路径三查）**：
  - **根因=测试自包含性缺失（共享可变全局态）**：`_results: list[dict] = []`（`:41` 模块级全局）由 `TestTRAE001-009` 各类的 `_record()` 追加；`test_generate_report`（`:411`，`TestRedBlueReport` 类内）直接 `total = len(_results)`（`:415`）并 `assert total >= 9`（`:431`）。**它不是生成器读外部结果集，而是依赖同进程内兄弟测试先执行写入 `_results`**。pytest 恰好按定义序先跑 TRAE001-009（整文件通过），但**独立跑/乱序/xdist 分片→`_results` 空→total=0→FAIL**。
  - **数据查**：`_results` 是**内存 list，不读 `data/audit_trail/`**——晨报所引"12,965 件 failures / 990 CRITICAL"**与本测试无关**（测试从不打开这些文件）。排除"空表/空文件"。
  - **日期查**：`:419 generated_at=datetime.now(UTC)` 仅作报告时间戳，**非过滤窗**；`total` 不受日期影响。排除"今天/近 N 天窗导致 0 结果"。（注：测试内 `datetime.now(UTC)` 不违"生成器禁 now"红线——该红线针对生成器/落盘产物，测试用 now 打时间戳合法。）
  - **路径查**：`REPO_ROOT`（`:24`）赋 `_PROJECT_ROOT`（`:26`）供静态扫描用，**与 total=0 无因果**（0 来自空 `_results`，非路径解析不到文件）。排除"REPO_ROOT 错位"。
- **结论**：**非数据/日期/路径三查之任一，而是"测试依赖跨用例累积的模块级全局 `_results`"的隔离性缺陷**（红蓝检出率门 #324 的载体测试写成了顺序耦合）。晨报 §4 记为"报告生成器空结果"——更精确表述是**报告测试非自包含**。
- **精确修法是纯机械（无翻案/无语义变更）**（但 `tests/rule/` **不在本案卷车道写权限内**，据禁越界§，**登记交总包**，处方如下）：把"确保 `_results` 被填充"从"兄弟测试恰好先跑"改为**显式前置**——最简=为 `TestRedBlueReport` 加 **session/function-scoped autouse fixture** 调一个 `_run_all_recordings()`（把 TRAE001-009 的 `_record` 逻辑抽成可独立调用的函数供 fixture 跑），使检出率门测试在任意选取/乱序/分片下都自足。验收判据：**单独 `pytest …::TestRedBlueReport::test_generate_report` 必须 PASS 且 total>=9**（现在必须红→修后绿）。
  - 备选：给该测试打 `@pytest.mark.dependency(depends=[…9 个 TRAE 测试…])`（xdist 下依赖标记不保证同进程，**不如 fixture 治本**）。
- **本车道动作**：仅归因 + 出精确修法，**未改 `tests/rule/**`**（越界），登记交总包（可依 CONSTRUCTION_DISCIPLINE §"纯机械修"由 rule 车道或总包落地）。

## 附录 B · R-K5/R-K6 同族第二源交叉核实：BRK-021 paper_hedge_leg 落地态
- **实测**：`src/zephyr/risk/paper_hedge_leg.py`（30,720B）+ `config/paper_hedge.yaml`（3,316B）**在盘但 untracked**（`git ls-files --error-unmatch …paper_hedge_leg.py`→"did not match any file(s) known to git"；`git log -- …paper_hedge_leg.py`→空）。
- **结论**：**R-K5/R-K6 同族第二源标的件尚未落地 HEAD** → **列入待办**（落地权 R-020 指 z-land2；本案卷时点仍未落）。BRK-021 hedge_execution_skill 零消费的治本件仍悬空，须 z-land2 原子落地（新 .py 三件套 + token 同批）。
- 依据等级：**亲验**（三态实测：在盘 / 不在 git / 无 commit 历史）。

## 附录 C · 本车道「我的高风险判断」（R-018 自报义务）
> 格式：判断内容 | 依据(亲验/转报/推断) | 若错会怎样 | 一条能让 Max 验真的命令
1. **route_incident 系统级 `_global_tripped` 与下单探针 `validator.kill_switch_active` 互不相通=假处置** | 亲验（两文件 grep+读码）| 若其实经某未见的 bridge 相连，则 K02"无下单消费"不成立 | `grep -rn "is_global_tripped\|_global_tripped" src/zephyr/ex_core src/zephyr/risk --include=*.py`（若返回引用即存在连接，需重判）
2. **K08 未武装是"刻意 fail-closed 停在 off"而非疏漏** | 亲验（0/6 ack + 零注入 + check() 逻辑）| 若生产别处已注入 ReportGate，则"零注入"错 | `grep -rn "ReportGate(" src --include=*.py`（现返空）
3. **#ARCH-343 "仅 W03 真接线"在 import 层不成立** | 亲验（W01/W04/W05 有 in-pkg importer）| 若这些 importer 本身是孤儿子网（不被 orchestrator 调），则注册表"仅 W03"仍可能对 | 需 z-land3 从 allocation orchestrator 入口做生产可达性 DFS（本车道未做）
4. **#ARCH-351 miniQMT"24 无退路"数未能复现（测得 63 miniqmt 任务）** | 亲验 63 总量 / 转报 24 子集 | 若 24 是 rpt_tf01/02 规范口径、我 63 含已有退路项，则两者不矛盾但我未证 | 规范化：对 `source: miniqmt` 任务批量核 `fallback_sources` 非空比例（须用 YAML parser 非 awk，本车道 awk 不可靠故不采信自算数）
5. **#ARCH-346 B05 "pit_query 默认 0"锚点疑张冠李戴** | 亲验反证（pit_manager 默认=5）+ 未定位 pit_query | 若 `pit_query` 在别处（data_handler）确默认 0，则注册表对、我搜错符号 | `grep -rn "def pit_query\|pit_query(" src --include=*.py`
6. **flags 嵌套子键不进注册表→auto_escalation 翻旗零效** | 亲验（flags.py:348-358 只注册顶层 key + spec.enabled）| 若别处有子键展开加载器，则结论弱 | `python -c "from zephyr.shared.foundation.flags import …; load; print('alerts.auto_escalation' in reg)"`（预期 False）
7. **#ARCH-352 判"已闭合（部分）"依赖 z-alarm 2 笔队列会落地** | 亲验当前 untracked | 若队列项已 dead 未 requeue，则机制长期不入 HEAD，"部分闭合"退化为"仅在盘" | `python scripts/commit_queue.py status | grep -i alarm`（核队列项存活）
- **仅读注册表/报告、未做代码级实测的条目（须 Max 重点复查）**：#ARCH-338 ExecutionEngine 生产可达性、#ARCH-339 K06/K09 调用点、#ARCH-340 三套开关态是否真无桥、#ARCH-342 `build_post_settlement_jobs`/eef42/175f 落地内容、#ARCH-344 D05 detect 具体行、#ARCH-346 B05/B08、#ARCH-347 T02/T05、#ARCH-348 双实现分化 diff、#ARCH-349 S08/S11 反例、#ARCH-350 I08 缓存投毒完整路径/I03/I09、#ARCH-351 "24"子集/TF15、#ARCH-353 F02、#ARCH-354 M03/M04、#ARCH-355 miniqmt_broker:836 参数、#ARCH-356 8 项逐项 —— **上述标"转报"者我只引注册表/晨报/rpt，未独立跑其原始证据命令**。
