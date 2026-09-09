---
ttl: task_bound
---

# 交易决策全景图字段升级——全网调研对照与讨论稿

> **日期**：2026-09-09 ｜ **会话**：st-tdmbe-20260909（fork 承接新闻+产业链后续）｜ **状态**：讨论稿，未裁定
> **任务**：Owner 指令——调研专业机构/量化社区/学术界的同类工程字段，对照本图 33 个节点字段，讨论还缺什么。
> **铁律前置**：先讨论后落盘；字段全可选向后兼容（存量 136 节点不动）；新增字段必须过双测试套件+validate+align_all。

---

## 一、现状字段全清单（基线，2026-09-09 快照）

**图级**：schema_version(1.1) / map_id / name_zh / effective_from / markets

**节点 33 字段**：

| 类 | 字段 |
|---|---|
| 结构 | node_id / name_zh / market / flow / layer / node_type / point / parent_node |
| 语义 | decision_question(≤100字) / algo_note_zh(R37必填) / doc_ref |
| 锚定 | strategy_mounts{strategy_ref,confidence,evidence} / factor_refs / data_refs / algo_refs(IND·EXA·DAL) / model_refs(ML) / module_ref / module_id / 11 库交叉轴(pattern·seat·macro·cycle·universe·cost_model·event·risk_limit·portfolio_model·benchmark·threshold) |
| 治理 | activation / invalidation / ai_autonomy / fallback / note_confirmed |

**边 4 字段**：from_node / to_node / edge_type(feed·sequence·broadcast·feedback) / payload_zh(≤20字)

## 二、六路业界调研对照

| 业界体系 | 核心字段 | 我们的对应物 | 缺口 |
|---|---|---|---|
| 监管模型清单（[OCC 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html)/[SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm)，[Trussed 清单指南](https://trussed.ai/resources/bank-ai-model-inventory-sr-26-2-compliance-guide)、[Databricks MRM 实操](https://www.databricks.com/blog/model-risk-management-2026-bankers-guide-revised-interagency-guidance)、[Yields.io](https://www.yields.io/use-cases/model-inventory)） | model ID/版本/**owner**/**risk tier**/用途/validation status+日期+结论/监控频率与结果/review date/approved-use/数据血缘 | module_id=ID；module_ref+data_refs=血缘；ai_autonomy≈approved-use；invalidation≈use 边界 | **owner 缺**、**risk_tier 缺**、validation 状态缺（真源在 node_verdict 台账，见 §四-3）、review 节奏缺 |
| WorldQuant Brain alpha 平台（[官方示例](https://worldquantbrain.com/alpha-examples)、[平台文档](https://www.scribd.com/document/728780335/World-Quant-Brain-Alpha-Documentation)） | fitness/turnover/**decay**/neutralization/universe/delay/truncation/IS→OS 生命周期/分类标签 | universe_refs=universe；pit_shift≈delay；invalidation+PB-14 decay_watch≈decay；分类=layer/flow | turnover/capacity 类是**策略/因子属性**非节点属性——应挂 strategy_registry（§四-5） |
| 特征库（[Feast FeatureView](https://docs.feast.dev/master/getting-started/concepts/feature-view)/[Tecton](https://docs.tecton.ai/docs/defining-features/feature-views)） | **owner**/tags/entity/source/transformation/**TTL/freshness**/lineage | entity=market/point；source=data_refs；TTL≈activation 时效窗 | **tags 缺**、freshness=数据侧 SLA（ODCS，§四-6） |
| 量化信号目录（[信号全生命周期实践](https://youngandcalculated.substack.com/p/how-quant-hedge-funds-actually-build)、[Maven 衰减](https://www.mavensecurities.com/alpha-decay-what-does-it-look-like-and-what-does-it-mean-for-systematic-traders/)、[停用判据](https://derivvaluation.medium.com/)） | **holding_period**/**capacity**/**decay half-life**/universe/regime 适用/stop criteria | regime 适用=**state_matrix+activation_state 已覆盖**；stop criteria=invalidation+升降级管线(F-C3-02)；holding_period/capacity→挂策略库 | holding_period 对做T/日内类节点有图上意义（可选） |
| 学界交易智能体（[FinMem AAAI](https://ojs.aaai.org/index.php/AAAI-SS/article/view/31290/33450)、[Agentic Trading 综述](https://arxiv.org/html/2605.19337v1)、[结构化反思](https://www.emergentmind.com/topics/structured-reflection-in-llm-agents)） | 决策时刻市场上下文快照/**推理链**/**置信度→仓位缩放**/**反思记录**（结果回写） | **全部是运行时字段**——真源=node_verdict 台账+scenario_plan_recorder，地图=设计真源不承载运行数据（§一铁律） | 零缺口（分层正确），写明防越界 |
| 数据契约（[ODCS v3.0](https://github.com/bitol-io/open-data-contract-standard)、[OpenMetadata](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-contracts/spec)、[OpenLineage](https://openlineage.io/blog/openlineage-takes-inspiration-from-opentelemetry/)） | schema/**SLA(freshness/latency/availability)**/**ownership**/质量期望/retention | ownership=owner 缺口同上；血缘=边+data_refs 覆盖 | **latency_budget 对盘中/持续节点有实战意义**（超时→fallback 联动） |

## 三、候选新增字段（A 必补 / B 可选 / C 不做）

### A 档（业界普遍 + 我们有真源可挂 + 防腐化价值高）

| # | 字段 | 枚举/格式 | 必填 | 依据 | 门禁影响 |
|---|---|---|---|---|---|
| A1 | `owner` | 常驻会话 id（如 st-tdmbe-20260909）或 `owner`（Owner 亲自管） | 新节点必填（R15 扩展），存量欠账 warning | 模型清单硬字段（OCC/SR 26-2 全家要求）；100% AI 开发下"谁在管这个节点"是第一治理问题 | 新节点 R15 检查+欠账 warning；L0 节点组第一批补登 |
| A2 | `risk_tier` | high/medium/low（离钱近先验：执行/风控=high，判定=medium，输出/横切=low） | 新节点必填，存量 warning | SR 11-7 风险分级驱动验证强度（[Risk.net 分级实践](https://www.risk.net/journal-of-risk-model-validation/6710566/model-risk-tiering-an-exploration-of-industry-practices-and-principles)）——正好机械驱动 PB-12 验证排序 | 高 tier 节点未入验证台账→巡检 warning（接 PB-14） |
| A3 | `review_frequency` | on_decay_alert(默认)/monthly/quarterly/semiannual | 可选，默认 on_decay_alert | PB-14 事件驱动复审的字段化（"报警才复审"的报警订阅粒度） | 无阻断；衰减巡检消费 |
| A4 | `tags` | 自由字符串列表（如 [盘中, 事件驱动, 板块]） | 可选 | Tecton/WorldQuant 分类标签；全库检索/前端过滤 | 无阻断 |
| A5 | `latency_budget` | 自由文本或枚举（tick/秒/分钟/盘后批量） | 可选，盘中(intraday)/持续节点建议填 | 数据契约 SLA 字段（ODCS）；超时→既有 fallback 字段联动 | 无阻断；盘中运行时消费 |

### B 档（挂库不挂图——字段真源在策略库/因子库）

| # | 字段 | 落点 | 依据 |
|---|---|---|---|
| B1 | holding_period（预期持有周期） | strategy_registry 条目字段 + StrategyMeta | 信号目录/WorldQuant 核心属性；地图经 strategy_mounts 间接获得；做T/日内节点可在 algo_note 引用 |
| B2 | capacity / turnover 上限 / neutralization | strategy_registry + pf_core StrategyMeta | WorldQuant 属性，属"策略执行参数"；节点级写会污染设计真源 |
| B3 | decay half-life | factor_registry（因子衰减）+ node_verdict 台账（PB-14 巡检产物） | 业界衰减半衰期是**测量结果**不是登记项 |

### C 档（不做，已有对应物或分层不符——写明防重复提案）

| 候选 | 不做理由 |
|---|---|
| regime_applicability | **已有**：state_matrix（节点×六段）+ strategy_mounts.activation_state |
| lineage/depends_on | **已有**：边（feed/sequence/broadcast/feedback）+ data_refs + module_ref 全覆盖 |
| reasoning_trace/market_context_snapshot/reflection | **分层不符**：运行时字段，真源=node_verdict 台账+scenario_plan_recorder；地图=设计真源（INV-1 铁律） |
| node version | git 即版本历史（PB-07 生效日同款裁定） |
| kill_criteria/sunset | invalidation（当日失效）+ F-C3-02 升降级管线（退役评审）已覆盖 |
| approved_use_scope | ai_autonomy 治理档位已覆盖 |
| validation_status 字段 | **派生不登记**：真源=node_verdict 台账（run_id/window/verdict），API 层 /api/tdm 联查透出，防双真源漂移（同 PB-03"验证态不进 YAML"裁定） |

## 四、与既有体系的关系（不破坏性核查）

1. **向后兼容**：五个 A 档字段全部 optional + 默认值，存量 136 节点零改动可过 validate；新节点 R15 渐进必填。
2. **验证体系联动**：A2 risk_tier 直接喂 PB-12 验证排序（high 先验）；validation 状态经台账派生进 /api/tdm → 前端抽屉"验证档案"区显示（Owner 已建的 P0-3 区）。
3. **ALGO-NOTE-SYNC 门禁兼容**：新字段不触碰 algo_note_zh 绑定逻辑。
4. **edge 层**：本轮不加字段（payload_zh 刚落；条件/优先级语义由节点承载）。
5. **schema_version**：字段全可选 → 维持 1.1 亦可；若 Owner 希望显式升版 → 1.2（_SCHEMA_VERSIONS 增枚举，一分钟改动）。

## 五、待 Owner 拍板

1. A1-A5 五个字段是否全收（我推荐全收，成本≈半天含门禁+测试+存量批量补登脚本）；
2. owner 字段的值规范：常驻会话 id 是否作为正式值（vs 引入"角色名"抽象——我推荐会话 id，直接可问责）；
3. risk_tier 三档够不够（SR 11-7 业界有 3-4 档流派；我们离钱近先验三档可覆盖）；
4. B 档三个字段的 strategy_registry 升级是否另立批次（涉及 pf_core StrategyMeta 代码，归施工轨）；
5. schema_version 是否显式升 1.2。

## 六、调研来源索引

- 监管：[OCC 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html) ｜ [SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm) ｜ [Bank AI Model Inventory (Trussed)](https://trussed.ai/resources/bank-ai-model-inventory-sr-26-2-compliance-guide) ｜ [Databricks MRM 2026 Guide](https://www.databricks.com/blog/model-risk-management-2026-bankers-guide-revised-interagency-guidance) ｜ [Yields.io Model Inventory](https://www.yields.io/use-cases/model-inventory) ｜ [Risk.net Model Risk Tiering](https://www.risk.net/journal-of-risk-model-validation/6710566/model-risk-tiering-an-exploration-of-industry-practices-and-principles)
- WorldQuant：[Alpha Examples](https://worldquantbrain.com/alpha-examples) ｜ [BRAIN Alpha Documentation](https://www.scribd.com/document/728780335/World-Quant-Brain-Alpha-Documentation) ｜ [仿真设置选择](https://github.com/hr-23/Worldquant-Brain-Alpha-/blob/main/How%20to%20choose%20the%20Simulation%20Settings)
- 特征库：[Feast FeatureView](https://docs.feast.dev/master/getting-started/concepts/feature-view) ｜ [Tecton Feature Views](https://docs.tecton.ai/docs/defining-features/feature-views)
- 信号目录：[How Quant Hedge Funds Build and Vet Signals](https://youngandcalculated.substack.com/p/how-quant-hedge-funds-actually-build) ｜ [Alpha Decay (Maven)](https://www.mavensecurities.com/alpha-decay-what-does-it-look-like-and-what-does-it-mean-for-systematic-traders/) ｜ [信号质量度量 (Macrosynergy)](https://macrosynergy.com/)
- 学界：[FinMem (AAAI/ICLR)](https://ojs.aaai.org/index.php/AAAI-SS/article/view/31290/33450) ｜ [Agentic Trading 综述](https://arxiv.org/html/2605.19337v1) ｜ [结构化反思](https://www.emergentmind.com/topics/structured-reflection-in-llm-agents)
- 数据契约：[ODCS v3.0 (Bitol)](https://github.com/bitol-io/open-data-contract-standard) ｜ [OpenMetadata Data Contracts](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-contracts/spec) ｜ [OpenLineage](https://openlineage.io/blog/openlineage-takes-inspiration-from-opentelemetry/)
