---
ttl: task_bound
---

# X 流验证批遗留项跟进设计（exec v2 口径 / 定稿锚点 / 消融实弹预案）

> 日期：2026-09-10 ｜ session：st-xflow-20260910 ｜ 前置：2026-09-10-xflow-batch-report.md §三遗留清单
> Owner 问"现在就调研修复可以吗"——四项分诊：④③=本轮已施工（见 §一/§二），①=设计稿待裁定（§三），②=纪律闸不动、预案备好（§四）。

## 一、④ exec 滑点 v2 口径（已施工）

**改动**：`compute_exec_metrics`（runner.py）滑点基准优先级=decision_price（T1 起新产物携带，真滑点=成交价 vs 记录意图价）→ ref_prices VWAP 代理（旧产物兜底）→ 两路皆缺跳过（不猜）。新增返回键 `slip_basis`：`decision_price | vwap_proxy | mixed(dp=N,vwap=M) | None`，L4 批 notes 带"基准口径=…"进台账（面板可读）。

**设计决策**：
1. **兜底不剔除**：0/34 存量产物带 decision_price（实测核实），剔除=旧产物永远无滑点指标；混合口径用 notes 明示比例，不混装不隐瞒。
2. **lag_recheck 语义变化**：decision_price 是记录意图（事件时点锚定），非行情派生基准——PB-16 "加 1 天滞后重算"的前视诊断对该路径无意义（意图价不存在"偷看未来"问题），该诊断仅对 VWAP 兜底路径保留。v1 的 lag_recheck 开关未实际接基准右移实现（一期 note 披露过），本次不改其机制。
3. **连续性声明**：一期 42 行+本批 18 行台账全部 pending+insufficient_samples、零真结论——口径切换零历史连续性成本（本设计文档即为切换记录）。

**测试**：TestExecMetricsV2Basis 7 用例（优先级/方向符号/VWAP 兜底/mixed 标注/双缺跳过/脏值回落/notes 贯通），runner 套件 21→28。

## 二、③ SellSignal→XFlowAction 自动化第一层（已施工）

**改动**：ablation.py 新增 `sell_signals_to_xflow_actions(signals)` 纯函数——sell_decision.SellSignal → XFlowAction 映射：CLEAR/REPLACE→clear（换股=先清仓，v1 无建仓动作位）、REDUCE→reduce 且 reduce_to=1.0−confidence（减仓量∝置信度，conf≤0 保守忽略）、source=signal.source 或默认 "TDM-X-S1"。ablate_weight_panel 索引匹配加双侧 [:10] 容错（"2026-01-06" 字符串可命中 Timestamp 索引）。测试 +7（TestSellSignalsToXFlowActions，真实 SellSignal dataclass 构造+端到端贯通 ablate_weight_panel），ablation 套件 9→16。

**调研事实**（subagent_A_sellsignal.md）：sell_decision/core 22 模块 21 个纯函数/显式状态注入（唯一内存状态=笔级熔断器，平凡可重演）——**可重放性不是障碍；真正缺口=8 类 signal_type 的 provider 全仓零实现**（stop_loss/take_profit/breakout_failure/replacement_rebalance 四个算法族存在且可历史驱动，但没有任何代码在历史 K 线上逐 bar 调它们产 SellSignal；测试全部标量夹具零 K 线）。

**语义关键点（下一层工程的前置问题，本轮不动）**：历史重放式自动化的持仓耦合——全量跑与剥离跑持仓路径不同，卖出信号生成应基于哪个持仓状态？分析：应基于**全量跑的持仓路径**（X 流信号在真实（全量）世界里生成，剥离跑模拟"若无 X 流"的反事实世界——反事实世界里不该再产 X 流信号，否则自我指涉）。该语义+前视风险（卖出逻辑用当日收盘判定当日卖出=前视，须 T+1 生成信号）留待 provider 工程立项时一并定稿。

## 三、① 定稿锚点方案（设计稿，**待 Owner 裁定，未改码**）

**张力陈述（原文逐字）**：
- 现机制（runner.py holdout_cutoff）：`inside = ts ≤ (as_of − 12 个月)`——任何新流水要压满 12 个月才进在验窗口。
- 晨报 2026-09-10 原文："T1/T2 的价值=机制就绪，窗口前移（2026-09-09 之后新数据积累）即出真结论"；收尾报告同款表述。
- 两者矛盾：按现机制，2026-09-09 之后的流水最早 2027-09 才可考，"新数据积累即出真结论"永远不成立。

**定稿锚点设计**：`ValidationConfig` 增 `finalized_at: date | None = None`；`partition_by_holdout` v2 分支：
- finalized_at=None → 现行为（12 个月锁，保守模式，默认不变）。
- finalized_at=D → `ts > D` 的流水可考（D=参数定稿日；调参发生在 D 之前，定稿后才产生的流水天然无污染）；`ts ≤ D` 全锁（含原 12 个月窗口，一律不再碰）。
- D 候选值=2026-09-09（治理真源裁定日）。"考完作废前移"落法：D 即前移后的保密线；考过一次后若再改参数→新 D'（换卷重考），旧 D' 之前的全部锁死。台账只追加+run_id 追踪（同参数同窗口二次考=审计可见），防重复考试。

**与 §12 原文对照**：§12 "12 个月保密考卷/考完作废前移/定稿前不许跑回测"——锚点方案是"前移"语义的显式实现（12 个月窗是一次性封存，考完/定稿后前移到 D），非放宽；定稿前不许跑回测的约束原样保留（消融实弹仍待放行）。

**风险**：①D 定错（定稿声明后 map 又改）→ 换 D' 重锁即可（台账只追加可审计）；②重复考试 → run 追踪+纪律；③D 之后新流水本身被后续调参污染 → 参数搜索若用 D 后数据拟合，则 D 需重新前移（换卷）。

**裁定请求（Owner 直接回同意/不同意即可）**：
> 建议把 holdout 机制升级为"定稿锚点"：在现有 12 个月保密窗口之外，增加参数 finalization（参数定稿日 D=2026-09-09）；D 之后产生的行情流水不再受 12 个月封存约束（调参时它们不存在，天然无污染），可直接用于验证批出真结论；D 之前的全部流水（含现 12 个月窗口）永久封存不再碰。不改此默认（finalized_at=None 时行为与现在完全一致），仅在你裁定"参数已定稿"时启用。同意后我施工（改动面：ValidationConfig+partition_by_holdout+单测，约 0.5 人日）。

## 四、② 消融实弹执行预案（纪律闸不动，放行后照此执行）

**前置条件**：①Owner 裁定参数定稿（或启用 §三锚点）；②窗口选择（下述两通路二选一）。

**证据**（probe_artifacts 实测）：34 个产物 0 个带 decision_price；流水窗口全部 >2025-09-09（最早起点 2025-09-30）——即"在验窗口（≤2025-09-09）目前没有任何已跑回测流水"，旧窗口重放不存在"已经被考过"的记录，但也没有现成对照产物。

**通路 A（推荐）：定稿参数重跑旧窗口**——用定稿后的策略参数对 ≤2025-09-09 窗口跑全量+剥离两支回测（该窗口不在任何已有产物的流水范围内=从未被考过，不碰保密考卷；且是旧数据，跑完不影响 D 后新流水继续积累）。命令序列：
1. `run_ablation(data=load_history(...≤2025-09-09), panel_full=..., actions=...)` → rescued 序列
2. `run_validation(batch="XFLOW", ablation_diff=rescued)` → 18 节点真 verdict 进台账
**通路 B：等新流水积累**——D 后实盘/模拟流水自然积累（无需回测），窗口前移后直接 run_validation。保守但最慢。

**产出预期**：两通路最终都产生 18 行 exit_counterfactual verdict（valid/noise/pending 按土规）；消融差额=X 流救回金额（ablation_report.rescued）。

## 五、本轮施工与验证

| 项 | 状态 | commit |
|---|---|---|
| ④ exec v2 口径（runner.py+7 单测） | 已施工，28/28 绿 | 见提交记录 |
| ③ 转换助手（ablation.py+7 单测+索引容错） | 已施工，16/16 绿 | 同上 |
| ① 定稿锚点 | 本文档 §三待裁定 | 未改码 |
| ② 实弹预案 | 本文档 §四备妥 | 未改码 |

调研产物：.runtime/tmp/xflow-followup-20260910/subagent_A_sellsignal.md（可重放性判定表）、probe_artifacts.py（证据核实脚本）。