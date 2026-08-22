---
ttl: task_bound
---

# 模块工厂手动实例全链路报告（13号文 §4.1 P0-S3）

- 日期：2026-08-22
- 工单：18号清单 §6 波4-13（GP0 退出项 E0-6 之一）
- 设计真源：`docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/13_module_factory.md` §4.1（P0-S2/S3）
- 执行依据：`docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/19_module_factory_manual_sop.md`（本实例为其首个验证实例）
- 范围纪律：未执行 git；未写注册表 yaml（条目片段交统筹集中写）；src 零改动（实例复用既有代码锚点）；一次性验证脚本置 `.runtime/tmp/`，用完即删。

## 实例选题

**FCT-SENT-028 涨跌家数二阶加速度 breadth_acc**——44号文 §9.1 定义的 M1-① 涨跌加速度族 F2。选题理由（工单三选一口径之"44号 FCT-SENT 族某条未落码变体"）：

1. 44号文 §2.1 裁定 M1-① 登记 3 条目（breadth_vel/lu_net_rate/break_rate），实测已登记 FCT-SENT-020/021/022；**F2 二阶加速度 acc_15m 仅在 FCT-SENT-020 公式文本内提及（"另有二阶加速度 acc_15m"），未独立登记**——真实缺口。
2. 代码已随 M1-① 施工落码（`market_sentiment_analyzer.py:792-797/831`，`breadth_acc_15m` 为 `analyze_breadth_acceleration` 既有输出）——实例可走"代码已存在"分支，不新增 src 文件。
3. 条目小、语义清晰、族内有 7 条同族条目作惯例参照——适合作为 SOP 首个练兵实例；且天然走"变体"裁决路径，覆盖四选一裁决中最易误判的一支。

## 六环节留痕

| 环节 | 输入 | 输出 | 验收结论 |
|---|---|---|---|
| 1 知识采集 | 44号文 §9.1 F2（`44_premarket_intraday_decision_upgrade.md`） | 采集卡片：{doc_ref=44号 §9.1+M1-①；定义=上涨家数 5min 速度的 15min 二阶差分；公式核=breadth_acc_15m=vel_5m(t)-vel_5m(t-15)；分流=可计算因子，继续} | **PASS**：有独立可计算公式核；非框架/方法论（对照 29号文 B 类判据） |
| 2 知识分类 | 采集卡片 | factor_class=sentiment；primary_timeframe=intraday；applicable=[intraday,daily]；direction=long；entry_role=timing；applies_to=[index]；tags=["情绪"]（词表子集）；aliases=["44号 M1/M3 升级增量","宽度二阶加速度","breadth_acc_15m"] | **PASS**：枚举全合法；tags 经脚本断言 ⊆ 词表（67 词） |
| 3 知识→模块映射 | 分类结论 | schema_plan 五字段（见片段）；检索留痕（`acc_15m`/`二阶加速度` 两组词，命中=FCT-SENT-020 公式内提及）；裁决=**变体**（variant_of=FCT-SENT-020）；factor_id=FCT-SENT-028（族内 027 顺延，全库 152 条无撞号） | **PASS**：裁决理由一句话——语义同源（宽度动能）、阶数不同（二阶 vs 一阶），非新建非重复 |
| 4 施工落码 | 映射裁决书 | code_symbol=既有锚点（AST 验证真实存在）；params={vel_window_min:5, acc_window_min:15, zscore_window_d:20, gap_nan_threshold_min:2}（对齐代码 config `accel_vel_window_min/accel_acc_window_min` 默认值）；inputs/outputs 与公式逐项对应；pit_policy=price_only；universe=UNI-RULE-001；benchmark_id=BMK-INDEX-001 | **PASS**：走"代码已存在"分支，src 零改动；无 depgraph 新代码节点需求 |
| 5 四级验证 | 环节1~4 产出+片段草稿 | L1 静态 12 项 PASS（schema 66 字段全覆盖/MUST 非空/枚举/词表/AST 锚点/查重复核）；L2 降级功能验证 5 项 PASS（公式逐值对拍×2/NaN 纪律/优雅降级/演示 IC）；L3 合规：市场级状态量不直接出个股交易方向（T+1 不直接适用，作择时确认）；PIT=price_only 与分钟快照口径一致；无涨跌停规则冲突；L4 待裁决点见末节 | **PASS（L2 为降级实证）**：脚本 exit 0，17/17 |
| 6 入库登记 | 验证通过的片段 | 片段 `.runtime/p3_fragments/w4_13_factor_entry.yaml`（头注释含目标路径/裁决类型/与族内条目 5 项刻意差异清单）；状态=candidate/pending_backtest；code_commit=null 留统筹 | **PASS**：终跑 exit 0；未触碰 catalogs 注册表本体 |

**经济含义一句话（L4 速裁用）**：上涨家数速度的 15 分钟二阶差分——市场宽度动能"加速/减速"的领先确认量，acc>0=修复动能正在加强，与一阶速度（FCT-SENT-020）联读可区分"走强中"与"走强但在减速（拐点临近）"。

## 验证明细（L1/L2，一次性脚本实测输出）

脚本：`.runtime/tmp/w4_13_instance_verify.py`（用完即删），两跑均 exit 0：

```
[PASS] A1 schema 全字段覆盖: schema 66 字段；片段缺 无；片段多出 无
[PASS] A2 MUST 字段非空（13号文§3.6+62号口径）: 空值字段: 无
[PASS] A3 inputs/outputs 非空列表: inputs=2 项, outputs=2 项
[PASS] A4 schema_plan 五字段齐全（语义抽象层）
[PASS] A5 枚举字段合法
[PASS] A6 human 来源 llm_safety_stack 置 null（62号口径）
[PASS] B1 factor_id 全局唯一: FCT-SENT-028 未占用；库内现有 152 条
[PASS] B2 族内编号顺延: 族内最大 FCT-SENT-027 → 本条 FCT-SENT-028
[PASS] B3 variant_of 目标存在: variant_of=FCT-SENT-020
[PASS] B4 同公式/同名检索: 命中=['FCT-SENT-020']（仅父条目公式内提及 → 裁决=变体）
[PASS] C1 tags ⊆ v2.0 词表: tags=['情绪']；词表外=无（词表 67 词）
[PASS] D1 code_symbol 锚点 AST 存在: ...::MarketSentimentAnalyzer.analyze_breadth_acceleration
[PASS] E1 公式对拍·稳态: vel=0.001（期 0.001）acc=0.0（期 0）
[PASS] E2 公式对拍·拐点二阶: acc=0.0002（期 0.0002，kink@200 确定性序列手算值）
[PASS] E3 NaN 纪律（缺 minute 234 快照 → 尾部 vel/acc 置 None 不外推）
[PASS] E4 输入不足优雅降级（None/2快照 → 均返回 None）
[PASS] F1 演示级 rank IC=+0.2860（n=11460，60 合成交易日×240min，注入 β=0.3）
===== ALL PASS (17 项) =====
```

**L2 降级声明**：M1-① 消费分钟级全市场快照序列，其落库任务（44号文 M1-④ 实时调度回路）未在产——历史快照数据不存在，正式 C-003 G1/G2 回测不可执行。按工单"无新代码则免测试；产生片段走既有校验工具验证"口径与 18号清单 E3（合成故障+留痕实证）同族降级：功能验证证明"公式实现正确+纪律正确+验证管道可跑"，evidence 已显式标注"演示级，非正式 G1/G2 回测"。正式回测待 M1-④ 快照积累后按 C-003 排期（登记观察项 O1）。

## 走查复盘（P0-S4：SOP 可独立执行性自评）

**自评结论：可独立执行**。本实例由 SOP 六环节检查单逐步驱动完成，执行中未需要向设计文档外的"隐性知识"求助的断点；关键环节（词表现读、族内惯例照抄、AST 锚点断言、片段交统筹）均有明确指令与工具路径。S4 验收口径（"另一个 AI 会话独立执行不重问"）达成的佐证：本报告全部操作均可由 SOP 文本+落盘文件复现。

**执行中发现的 SOP 改进点（已回写 SOP 对应环节常见坑）**：

1. 环节 2 原稿未强调"词表外新词的两条出路"——执行中实测族内既有条目 tags 用语表外词汇（见 O2），SOP 已补"归并或入 aliases+登记待裁定"分支。
2. 环节 4 原稿未区分"代码已存在/不存在"两分支——实例实际走"已存在"分支，SOP 已补分支判定与 depgraph 铁律挂载点。
3. 环节 5 原稿 L2 只有"走 C-003"一口径——实测数据前置缺失是 Phase 0 常态，SOP 已补降级功能验证口径（含 evidence 分级标注红线）。

**观察项登记（不修，供后续 Phase/统筹裁定）**：

- O1：FCT-SENT-028 正式 G1/G2 回测挂账——前置=44号文 M1-④ 分钟级全市场快照落库积累；排期属交易决策侧。
- O2：族内既有 7 条（FCT-SENT-020~027）tags 含词表外词汇（"市场级择时""44号升级"，v2.0 词表 67 词无此二词）——本实例片段严格归并（仅"情绪"）+检索词改由 aliases 承载；既有条目是否回填校正、词表是否登记新词，属注册表治理范畴，待 Owner 裁定（本工单不动既有条目）。
- O3：族内既有条目 schema_plan/causal_graph 均 null 占位——62号"注册时 MUST 声明 causal_graph"口径与存量条目现状有落差；本实例片段演示了填写范式，存量回填属 62 侧条目重填流程，不在本工单范围。
- O4：factor_registry 实测 152 条（13号文 §2.4 记 140 条为 2026-08-17 勘察口径，44号文施工已新增 12 条）——13号文数字下次验证时顺手更新。

**depgraph 占位节点登记建议（P0-S1 留统筹执行）**：13号文 §4.1 P0-S1 要求登记"模块工厂"设计态节点（status=planned，编号与域归属开放问题 Q6 待 03 号文裁定，先占位）。建议参数：name=module_factory（模块工厂），status=planned，域归属暂挂 D_AI（待 03 号文裁定后修正），依赖边建议：读→factor_registry/strategy_registry（REG-FCT-001/REG-STR-001）、复用→skill_sandbox（L1 沙箱）、复用→backtest C-003（L2）、写→candidate 追加仅（ catalogs ）；节点说明标注"Phase 0 手动 SOP 形态=19_module_factory_manual_sop.md，无新代码模块"。本实例本身不产生新代码节点（复用既有锚点）。

**L4 待裁决点（交统筹/Owner）**：①片段 5 项刻意差异（schema_plan/causal_graph 填写、tags 严格归并、params/inputs/outputs 实填、演示级 evidence）保留或回退；②演示级 evidence 保留或置空待正式回测；③depgraph 占位节点建议采纳与执行。

## 产物清单

| 产物 | 路径 |
|---|---|
| SOP 文档 | `docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/19_module_factory_manual_sop.md` |
| 待登记条目片段 | `.runtime/p3_fragments/w4_13_factor_entry.yaml` |
| 本报告 | `docs/_working/reports/2026-08-22-module-factory-manual-instance.md` |
| 验证脚本（一次性，用完即删） | `.runtime/tmp/w4_13_instance_verify.py` |
