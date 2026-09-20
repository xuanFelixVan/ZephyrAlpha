---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成（3 条，逐条摘录）**
> - L35: 【问题】现有信号结构（权重面板/SynthesizedSignal/FactorSignal 契约）无任何 X 流判别字段，SellSignal 流未接入回测（grep 实证 sell_decision 包外零消费者）——消融器从哪拿"哪些动作是 X 流"？剥离时简单置 0 会被引擎 Σ=1 归一化
> - L62: 2. **T2 消融器实弹回放**：待 Owner 放行（协议 §12：参数没定稿不跑回测）；放行后 `run_ablation(...)` → rescued 序列喂 `run_validation(batch="XFLOW", ablation_diff=...)`。
> - L68: 8. **注册表驱动重构 TODO**：method→handlers dict 待第三批（F 流 portfolio_attribution）时评估。
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 3 个，其中判废弃 0、路径漂移 0）+ commit 提及 6 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# X 流验证批施工收尾报告（节点级可回测治理·第二期：风控批）

> 施工 session：st-xflow-20260910 ｜ 日期：2026-09-10 ｜ 真源：Owner 2026-09-10 X 流验证批施工指令
> 前置：治理真源 `2026-09-09-node-backtest-governance.md` §七/§八（P1-12 第二位=风控 + P2-3）；上一班晨报 `2026-09-10-nodebt-night-report.md` 裁定②③=本批施工项。
> 结论先行：**T1/T2/T3/T4 全部完成并提交**（T1 `ebc98ac1` / T3 `579c8c85` / T2 `ecdcdcab` / 收尾随本报告）；台账实弹 60 行（42 旧 + 18 新 X 流 verdict，全部 pending+insufficient_samples 如实披露）；T4 全量回归 **129 passed**（基线 104 + 新增 25 精确吻合，零回归）；align_all 硬问题清零；反方复核 Agent 审计**零阻断**（10 项硬约束全过，提示级 4 条均登记不违规）。

## 一、完成清单（落盘物 × commit × 验收证据）

| # | 落盘物 | 落点 | 验收证据 | commit |
|---|---|---|---|---|
| T1 | 成交流水加 decision_price/order_type（裁定③） | matching_logic.py（MatchingFill 尾部两字段+market/limit/tick 三成交点回填）、matching_engine.py（_to_backtest_fill 透传）、portfolio.py（BacktestFill 两字段+_trades_log 补键）、backtest_result_sink.py（TradeRecord 尾部两字段）、run_backtest.py（_collect_timeseries 补键）、result_repository.py（build_artifact_from_data 投影补键）、tests/backtest/test_backtest_result_sink.py（新 8 用例） | 新测试 8/8 绿（旧 6 键兼容/全链投影贯通/撮合三语义/未成交 None/portfolio 透传）；tests/backtest 全域+fills_adapter **982 passed** 零回归；存量 34 产物不回填（消费方 .get 容错，api_server dict 原样透传） | `ebc98ac1` |
| T2 | 信号消融对照器（裁定②） | src/zephyr/trading/validation/ablation.py（新，MOD-TDMVAL-001）、tests/trading/test_validation_ablation.py（新 9 用例）、blueprint.md（§5 验收）、error_code_registry.yaml（ZA-TDMVAL-0002 登记） | 9/9 绿（空剥越恒等/clear/reduce 回滚保 Σw=1/非法拒绝/幂等基线 rescued≡0/清仓差额非零）；引擎零改动；run_ablation 零生产调用方=未实弹（§12 纪律） | `ecdcdcab` |
| T3 | X 流验证批（本批目的） | runner.py（load_xflow_nodes 18 节点/compute_exit_counterfactual_metrics/apply_exit_soil_rules/run_validation batch 参数）、test_validation_runner.py（14→21）、blueprint.md（v1.0.1→v1.1.0） | 单测 21/21 绿；**实弹台账：run_id=VAL-20260909-164042 写入 18 行**（dry_run 预演→实弹；全部 exit_counterfactual+pending+insufficient_samples+holdout 披露 notes）；衰减巡检尾随 checked=60/decayed=0（全 pending 无 valid 基线，天然安静） | `579c8c85` |
| T4 | 回归与验收 | — | pytest 三套件+新增两套件+冒烟：**129 passed**（基线 104+25 吻合，f4 锚=一期 14 行断言原样保留）；align_all 硬问题清零（domain_mismatches=0/ghost_anchors=0/frontend fail=0/decision_map error=0）；test_tdm_structure 绿；verify_schema_truth 仍 4 处既有遗留**无新增漂移** | — |

施工顺序实际执行为 T1→T3→T2（T2 等 Step 1.5 盘点回传；T3 台账产出不依赖 T2 实弹——holdout 锁窗下全 pending+降级披露，指标函数设计为吃消融差额序列、缺省优雅降级）。三任务三个独立 commit，符合"每个独立落盘物验收+提交后再进下一个"。

## 二、自裁记录（按指令 §〇 协议格式）

### 裁定 1：T1 决策价与订单类型语义
【问题】指令要求 decision_price/order_type 两字段，但 tick 模式存在语义分叉（触发 tick last_price vs 撮合 VWAP），order_type 枚举指令列举"限价/市价/排板"而回测实际不存在限价与排板路径。
【分析过程】指令原文"决策价（下单/信号价）"指向前者（信号价）；撮合层 MatchingFill 是日频/分钟/tick 全模式汇聚的单 seam（_generate_fills_from_order_books→_match_order_dict→三 match_* 纯函数），在此回填一条缝全覆盖且实盘 MiniQmtBroker 共享 MatchingLogic 但不读新键=零影响；撮合引擎全链 limit_price 恒缺省、打板仅在 ex_core 实盘侧（盘点④⑤），LIMIT/排板枚举位保留但不伪造类别。
【裁定结果】decision_price=撮合前基准/信号价（market=ask1/bid1 基准价、tick=触发 tick 的 last_price、limit=委托限价）；order_type=market|tick|limit 小写枚举（对齐 side 小写口径），排板留位待回测侧有打板路径再引入。测试锁定三语义+未成交 None。

### 裁定 2：T1 并发冲突——未提交增量被回退后重放
【问题】T1 施工中发现 HEAD 被并发 session 前移（1eb9f0cf75→e78d8ee157→267f649c5b），我已落盘的 result_repository.py 投影增量消失（工作区回退到 HEAD 版），git diff 列表中该文件静默缺席。
【分析过程】git show HEAD:<file> 核对 HEAD 版仍为 6 字段=对方提交未动该文件，我的未提交增量被并发 session 的 worktree 操作冲掉（共享工作区常态）；直接重放会遇锚点"已应用"假象（其余 5 文件锚点还在），须单独重放该文件增量；若不重放，新字段在该投影点静默丢失（正是盘点⑥-1 最大的坑）。
【裁定结果】单独重放 rr1 增量（带 count==1 断言）→ 复跑 8/8 绿 → 立即走网关提交落袋（未提交改动不隔夜原则）。此后 T2/T3 提交前均先 git log/status 核对 HEAD 与文件状态。

### 裁定 3：T2 消融动作标注来源与剥算子语义
【问题】现有信号结构（权重面板/SynthesizedSignal/FactorSignal 契约）无任何 X 流判别字段，SellSignal 流未接入回测（grep 实证 sell_decision 包外零消费者）——消融器从哪拿"哪些动作是 X 流"？剥离时简单置 0 会被引擎 Σ=1 归一化放大回满仓（再分配污染）。
【分析过程】盘点⑤三方案对比：方案 A（双权重面板重放差+回滚式剥算子）代价最低且与裁定②"信号层剥离"语义严格一致；xflow_actions 两条来源路（双面板 diff/待 SellSignal 接入）各有代价，v1 先做机制、标注由调用方注入最诚实——不猜测不伪造归因。
【裁定结果】XFlowAction 调用方显式注入（v1）；剥算子=回滚式保 Σw=1（clear=标的归零+缺口等比分摊给其余标的、reduce=降至 reduce_to、全清仓日持币由引擎保持昨仓）；notes 披露"差额=X 流直接效应+资金路径二阶效应"。SellSignal 接入回测后可直接消费其 source/direction 生成 actions（接口已留）。

### 裁定 4：T3 批次形态与触发计数口径
【问题】runner v1 是纯函数 if 链+过程式单入口，第二批怎么挂（注册表 vs 分支）？X 流触发计数无节点归因可用。
【分析过程】derive_method 已是 method 分叉既有点（exit_counterfactual 分支一期已存在且测试锁定）；2 个方法上注册表属过度设计（盘点⑤明示第三批 F 流时再评估）；触发计数与一期裁定 4"全量口径+notes 披露"同例。
【裁定结果】run_validation 加 batch 参数（"L4"|"XFLOW"，默认 L4 行为不变=一期 14 行测试锚保留）；新增 compute_exit_counterfactual_metrics/apply_exit_soil_rules 按方法分派；触发计数=在验窗口卖出流水代理+notes 披露；指标函数入参留 ablation_diff（消融差额序列），缺省时 avoided_amount=None→pending 如实降级（方法学"对照未建保持 pending"的代码形态）。

### 裁定 5：T3 实弹写台账的时机
【问题】铁律"参数没定稿不跑回测、holdout 只考一次"——X 流验证批写入 18 行 pending 是否违反？
【分析过程】第一期 42 行 pending 是同款先例（晨报裁定 3："宁可 pending 不作弊"）；写 pending 行=机制就绪登记+面板可见，不消耗 holdout 考卷（在验窗口流水=0，无任何指标计算）；T2 消融回放才是"跑回测"语义，已按 §12 未放行不实弹（run_ablation 零生产调用方）。
【裁定结果】dry_run 预演（18 行/全 pending 断言通过）→ 实弹 run_validation(batch="XFLOW") 写入 run_id=VAL-20260909-164042，18 行全部 exit_counterfactual+pending+insufficient_samples+holdout 披露 notes；decay_check=True 尾随自动跑（checked=60/decayed=0）。这是纪律不是欠账，窗口前移后重跑出真结论。

### 裁定 6：T2 首版剥算子算术 bug 测试自愈
【问题】首版分摊实现 others_total 误含动作标的且整行缩放污染动作标的位（reduce 测试期望 0.1 实得 0.125），端到端测试又暴露 nav_series 首行 NaT 索引混入 rescued。
【分析过程】纯函数单测精确锁黄金数抓出算术错；NaT 行与 runner._collect_timeseries 首日过滤先例同源（引擎逐日循环前初始化行）。
【裁定结果】分摊改"排除动作标的的等比缩放 + .at 显式写入"（Σw=1 严格守恒）；nav 双序列 index.notna() 过滤后再对齐。修复后 9/9 绿——测试先行的价值实证。

### 裁定 7：error_code ZA-TDMVAL-0002 保护路径登记
【问题】ablation.py 新错误码未登记触发 GATE-ERRCODE-CONSISTENCY 阻断（首次 T2 提交失败根因，被终端 stderr 告警截断误判为非阻塞）。
【分析过程】error_code_registry.yaml 属保护路径（architecture_model/contracts/ 下）；登记格式沿 ZA-TDMVAL-0001 同款四行+introduced 惯例；授权依据=Owner 本指令+晨报裁定②。
【裁定结果】追加一条（非结构性变更），提交消息补 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]+授权来源，重提交成功。

## 三、遗留清单

1. **exit_counterfactual 真结论**：待窗口前移（2026-09-09 之后新流水积累）重跑 `run_validation(batch="XFLOW")` 出真结论；当前 18 行 pending 是纪律性占位。
2. **T2 消融器实弹回放**：待 Owner 放行（协议 §12：参数没定稿不跑回测）；放行后 `run_ablation(...)` → rescued 序列喂 `run_validation(batch="XFLOW", ablation_diff=...)`。
3. **消融动作标注自动化**：SellSignal 流接入回测后，xflow_actions 可从其 source/direction 直接生成（v1 调用方注入）。
4. **exec 滑点真决策价口径**：decision_price 已入流水（T1），exec_quality v1 仍用 VWAP 代理——口径切换需另批定稿（涉及一期指标连续性）。
5. **decay 对 exit 方法的比对口径**：X 节点出 valid 后，hit_ratio（避损额语义）的衰减比对需随消融器定义锁定（decay_watch 判据已按节点泛化，暂不阻塞）。
6. **verify_schema_truth 既有 4 处漂移**：factor_feature_value 未执行/calendar_event 3 列——Owner 窗口事项，本批未动。
7. **面板 API 8890 旧实例**：晨报遗留（需 Owner 手动重启），本批未动。
8. **注册表驱动重构 TODO**：method→handlers dict 待第三批（F 流 portfolio_attribution）时评估。

## 四、对 Owner 的建议

1. **面板验收**：tdm 页 X 流节点抽屉「验证档案」区现应有台账记录（18 行 pending 徽章）；冒烟 test_tdm_structure 已绿，目检即可确认。
2. **IMPORT-INTEGRITY gate 按 session 过滤**（晨报建议重申）：本批再次实证共享暂存区互锁（TRACKED-DRIFT 告警把并发 session 的 3 个无关文件写入记到本 session hook 运行期；index.lock 竞争一次）。gate 已收 `_files` 参数却扫全量——"只查自己"这最后一步值得尽快补上。
3. **消融回放放行语义**：建议明确"消融回放是否算 §12 意义上的跑回测"。若放行，建议先用合成/窗口前数据走通全链，再对新窗口实弹。
4. **窗口前移策略**：2026-09-09 后新流水积累时，建议按月滚动验证批（runner 幂等，追加新 run_id 是设计），让 L4/X 两批同时出真结论。

## 五、施工过程关键事实（备查）

- 盘点 Agent×3（只读）产物：`.runtime/tmp/xflow-20260910/subagent_01_T1盘点.md` / `subagent_02_T2盘点.md` / `subagent_03_T3盘点.md`
- 反方复核 Agent 产物：`.runtime/tmp/xflow-20260910/review.md`（10 项硬约束审计表+语义复核+测试复跑证据：sink+ablation 17 passed、runner 21 passed）
- T4 证据：基线 104 passed（改动前留档 `.runtime/tmp/xflow-20260910/baseline.txt`）→ 终跑 129 passed（=104+8+7+9+1 精确吻合）
- 提交链：`ebc98ac1`（T1）→ `579c8c85`（T3）→ `ecdcdcab`（T2）→ 本报告（收尾）
- 并发环境实录：施工期间 HEAD 被并发 session 前移 3 次（e78d8ee157/267f649c5b/b446417e22），index.lock 竞争 1 次（退避重试穿过），TRACKED-DRIFT 告警 3 文件均为他人 session 写入（已核实非本批文件）

—— st-xflow-20260910 · 2026-09-10