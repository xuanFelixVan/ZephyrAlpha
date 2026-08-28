---
ttl: permanent
doc_type: architecture_view
title: 模块工厂手动 SOP（Phase 0 六环节检查单）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-22
topic: module_factory_manual_sop
scope: 09_ai_architecture
---

# 模块工厂手动 SOP（Phase 0 六环节检查单）

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：SOP 全文六环节检查单定稿（环节 1 采集→环节 6 入库，每环节输入/操作/输出/验收/常见坑五段式）；已被 1 个完整手动实例走通验证（2026-08-22，FCT-SENT-028，17 项检查全 PASS，实例报告+注册表条目三方互证）。
> **最终成果**：模块工厂手动形态的执行真源确立（"另一个 AI 会话零上下文独立执行"的载体），并作为 Phase 1 自动化的需求基线。**本案已结案**。
> **未做+原因**：无（后续手动实例按本 SOP 执行；自动化属 13 号文 GP1+ 范围）。

> 本文定位：13 号文 [13_module_factory.md](13_module_factory.md) §4.1 P0-S2 的产出物——把 29 号文人工抽取的隐性流程显性化为**六环节检查单**，供"另一个 AI 会话"零上下文独立执行（P0-S4 验收口径）。
> 设计真源：13 号文 §3.0~§3.6（六环节定义与决策推理）；入库 schema 真源=62 号文 §6.1.1 与 `docs/01_policies_and_standards/_registry/catalogs/` 落盘 YAML（v2.1），本文只引用不复制。
> 已验证：本 SOP 已被 1 个完整手动实例走通验证（2026-08-22，实例报告 `docs/_working/reports/2026-08-22-module-factory-manual-instance.md`，17 项检查全 PASS）。

---

## 0. 适用范围与铁律

**适用**：把一条知识（课程条目/论文要点/既有设计备忘中的量化规则）转化为 factor/strategy registry 的 candidate 条目片段。Phase 0 全手动：人（AI 会话）采集、分类、映射、写模块、验证、产出登记片段。

**铁律（违反即停）**：

1. **不直接写注册表 YAML**。产出物=待登记条目片段（`.runtime/p3_fragments/` 下独立 YAML 文件），由统筹集中写入 catalogs（18 号清单 E6 裁定：注册表统筹集中串行写）。
2. **depgraph L1 铁律**（规则 19）：若实例伴随新建代码模块，第一步=登记 depgraph 设计态节点（apply_depgraph，统筹执行），最后一步=验证通过后 planned→production。纯条目片段（复用既有代码锚点）不产生新代码模块，只需在片段中登记 depgraph 建议。
3. **真源唯一**：不新建任何注册表/知识库（13 号文 §5 #5）；分类词表、schema、MUST 字段全部以落盘 YAML 头部注释与 entry_schema 块为准（不用记忆，逐次现读）。
4. **candidate 封顶**：条目只到 `status: candidate` + `algorithm_status: pending_backtest` + evidence 回填；晋升（candidate→active）是 62 号 PROMOTE_ENTRY 9 门禁职责，本 SOP 永不触碰（13 号文 §5 #9）。
5. **留痕**：每个环节的输入/输出/验收结论写入实例报告（`docs/_working/reports/YYYY-MM-DD-module-factory-manual-instance.md`，frontmatter 只带 `ttl: task_bound`）。

**开工前必读（按序）**：13 号文 §3.0~§3.6 → 目标注册表 YAML 头部注释（schema 版本说明 + 标签词表 + 字段推导规则）→ entry_schema 块（字段全集）。

---

## 环节 1 · 知识采集（输入）

| 项 | 内容 |
|---|---|
| **输入** | 一个知识源定位：29 号文条目编号（如 §F1.2）/ 设计备忘章节（如 44 号文 §9.1 F2）/ 一篇论文。三选一，必须有可引用的 doc_ref 锚点 |
| **操作** | ① 精读源文，抽取候选量化规则：必须有可计算的 formula（或明确可公式化）；② 判定分流：是"对标的出信号的可复用量化规则"（→因子/策略候选，继续）还是"系统怎么建的知识"（→不入业务库，归属模块设计文档，停）还是"观测框架/目录综述"（→不入库，停）。分流判据照抄 29 号文结案报告 §二 的三类不入库判据：无法产出可计算信号 / 属系统设计知识 / 目录性内容 |
| **输出** | 采集卡片：{源锚点 doc_ref、一句话定义、原始公式/规则文本、分流结论} |
| **验收标准** | 分流结论三态明确（继续/归属设计文档/不入库）；"继续"项必须有可写成一行表达式的公式核 |
| **常见坑** | ①把"方法论/框架"当因子采（29 号文 B 类 22 条先例——复盘 KPI、因子检验四法这类是方法不是条目）；②源锚点写成文件名不带章节号（后续 doc_ref 反链失效）；③口语化表述未转结构化定义（29 号文先例要求全部转化） |

## 环节 2 · 知识分类（处理 1）

| 项 | 内容 |
|---|---|
| **输入** | 环节 1 的采集卡片 |
| **操作** | ① 定主分类：factor 10 类（value/quality/momentum/volatility/size/liquidity/event/intraday/technical/sentiment）或 strategy 6 类（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）——词表以注册表 entry_schema 注释为准；其他（风控规则/执行算法/技术指标/数据资产）分流到对应注册表，本 SOP 后续环节以 factor 为例（strategy 同理换 schema）；② 填多维适用性标注十字段：primary_timeframe（枚举 1min~monthly）/applicable_timeframes/regime_valid/regime_invalid（枚举 trend_up/trend_down/ranging/panic/euphoria/high_vol/low_vol，空=未标注）/direction（long/short/both/neutral）/entry_role（trigger/state/filter/ranking/rule/timing/reference）/applies_to（stock/etf/index/futures/sector/market）/tags；③ **tags 归并纪律**：从注册表 YAML 头部注释的 v2.0 标签词表现读（67 词），tags 必须是词表子集；词表外新词两条路——归并到既有同义词（如"翻转→反转"），或放弃入 tags 改放 aliases（aliases 自由文本不受词表约束），并在实例报告登记"新词待 Owner 裁定是否入词表" |
| **输出** | 分类结论：{factor_class、十字段标注值、tags（词表子集）、aliases} |
| **验收标准** | factor_class ∈ 10 类枚举；tags ⊆ 词表（用脚本断言，不靠肉眼）；primary_timeframe ∈ 枚举 |
| **常见坑** | ①凭记忆写词表——词表以落盘 YAML 头部注释为准，逐次现读；②timeframe 用 "5min" 之外的自创写法（"5m"/"五分钟"均非法）；③direction 无方向语义时硬填 long/short（应 neutral） |

## 环节 3 · 知识→模块映射（处理 2，核心独创）

| 项 | 内容 |
|---|---|
| **输入** | 环节 2 的分类结论 |
| **操作** | ① **语义抽象**：手写 schema_plan 五字段——event（什么市场事件/状态变化触发本条目）/context（适用环境：数据前置、股票池、交易规则约束）/qualities（数值语义：正/负/极值各意味着什么，与兄弟条目怎么联读防单维误判）/direction（long/short/both/neutral）/output（输出列、值域、消费方式）。五字段缺一不可，这是语义与实现解耦的载体（62 号 v1.19.0 预留字段，LLM 来源 MUST，人工来源本 SOP 同样强制——它是后续检索与验证的语义锚）；② **检索查重**：对 factor_registry + strategy_registry 做文本检索——Grep 搜公式关键符号（如 `acc_15m`）、中文名关键词、aliases 关键词；命中则逐条比对：公式等价？同族公式内已提及？③ **四选一裁决**：新建（new entry，无任何命中）/ 变体（variant_of 指向 parent——语义同源、参数或阶数不同）/ 重复（reject 或归并——公式与语义均等价，名称进宿主 aliases + doc_ref 标"吸收"，不新建）/ 组合（多条既有条目组合，登记 combination 语义）。**裁决必须留痕**：检索词、命中条目、比对结论写进实例报告；④ 定 factor_id：族内编号顺延（Grep `FCT-{CLASS}-` 取最大号 +1），全库唯一 |
| **输出** | 映射裁决书：{schema_plan 五字段、检索留痕、四选一裁决+理由、factor_id、variant_of（变体时）} |
| **验收标准** | schema_plan 五字段全非空；检索留痕含 ≥2 组检索词（符号+中文）；裁决四选一且理由一句话可说清；factor_id 全库唯一且族内顺延 |
| **常见坑** | ①跳过检索直接新建→重复造轮子（本环节存在的意义就是生成前拦截，13 号文 §3.3）；②把"旧因子新参数/新阶数"误判为新建（应变体）——变体用 variant_of 指向 parent，治理字段 correlation_group/redundancy_status 留给后续审计；③把"多条旧因子拼一起"误判为新建（应组合）；④factor_id 跳号或撞号 |

## 环节 4 · 施工落码（处理 3）

| 项 | 内容 |
|---|---|
| **输入** | 环节 3 的映射裁决书 |
| **操作** | ① 判形态优先级：因子优先**表达式/公式文本**（可解释性最强，13 号文 §3.4）；需要代码时两种情形——**a) 代码已存在**（设计备忘施工时已落码，如本 SOP 验证实例）：code_symbol 指向既有 `<relative_path>::<Class>.<method>`，code_path 留空串（族内惯例），不新写代码；**b) 代码不存在**：按 depgraph 铁律先登记设计态节点（片段中给 depgraph 建议，统筹执行 apply_depgraph），再在既有因子模块包（`src/zephyr/factor/` 或设计指定包）落模板化实现——继承既有基类/复用既有纯函数风格，带 blueprint 锚定头；② 填实现参数：params/inputs/outputs 与公式逐项对应（参数名对齐代码 config 字段名）；③ 填 pit_policy（price_only 或数据实际口径）、universe（默认 UNI-RULE-001）、benchmark_id（默认 BMK-INDEX-001，以落盘取值为准） |
| **输出** | 实现规格：{code_symbol 或 depgraph 建议、params、inputs、outputs、pit_policy、universe、benchmark_id} |
| **验收标准** | code_symbol 指向的符号 AST 级真实存在（用环节 5 的脚本断言，不肉眼）；params 键与代码 config 字段一致；无新增自由 Python 文件时 depgraph 建议非空 |
| **常见坑** | ①code_symbol 凭印象写→锚点漂移（门禁A `check_registry_code_anchor.py` 会拦，但应在入库前自检）；②为条目新建独立 .py 文件（孤儿模块门禁会拦——因子表达式优先，代码尽量挂既有分析器/因子模块）；③params 与代码默认值两张皮（以代码 config 默认值为真源回填 params） |

## 环节 5 · 四级验证（验证）

| 项 | 内容 |
|---|---|
| **输入** | 环节 1~4 全部产出 + 条目片段草稿 |
| **操作** | 写一次性验证脚本（`.runtime/tmp/` 下，用完即删），断言式逐项检查、exit code 0/1 分明。模板照抄本 SOP 验证实例脚本（`.runtime/p3_fragments/w4_13_factor_entry.yaml` 的同族验证脚本，见其实例报告附录清单）：**L1 静态**——A. schema 校验（片段字段全集 ⊇ 注册表 entry_schema 键集；MUST 非空清单：factor_id/name/name_zh/factor_class/formula/alpha_source/doc_ref/direction/entry_role/algorithm_status/evidence/code_symbol/frequency/universe/benchmark_id/neutralization/pit_policy/module_id/status/version/owner/causal_graph/discovery_agent/primary_timeframe + 变体时 variant_of；枚举合法；inputs/outputs 非空列表；schema_plan 五字段齐；discovery_agent=human 时 llm_safety_stack 为 null）；B. 检索复核（factor_id 唯一、族内顺延、variant_of 目标存在）；C. tags ⊆ 词表；D. code_symbol AST 存在性（复刻 check_registry_code_anchor.py 逻辑：文件存在 + AST 顶层 def/class 或 Class.method 点号命中）；**L2 回测**——有真实数据：走 C-003（`src/zephyr/backtest/`，门槛=62 号 §4.13 G1/G2，引用不复制）；无真实数据（Phase 0 常见）：降级为**功能验证**——真跑实现代码做公式逐值对拍（确定性合成序列 vs 手算值）、NaN/降级纪律验证、合成注入信号演示 rank IC（证明管道可跑），evidence 必须显式标注"演示级，非正式 G1/G2 回测"；**L3 合规**——逐条过：信号是否个股可交易方向（市场级状态量注明"T+1 不直接适用，作择时确认"）、PIT 口径（pit_policy 与数据延迟一致）、A 股规则（涨跌停/T+1 语义不冲突）；**L4 人审**——产出物（片段+报告）交统筹/Owner 即人审回路，实例报告末尾给"经济含义一句话"供快速裁决 |
| **输出** | 验证记录：{L1 逐项 PASS/FAIL、L2 证据（或降级声明）、L3 合规结论、L4 待裁决点}；evidence 字段定稿 |
| **验收标准** | 脚本 exit 0；evidence 非空且分级标注（正式回测/演示级）；L3 三小项逐条有结论；报告含经济含义一句话 |
| **常见坑** | ①演示级 evidence 不标注→污染库（等于伪造回测证据，红线）；②合成数据 IC 当真实 alpha 引用；③NaN 纪律不测（静默外推=前视风险温床）；④脚本留在 src/ 或 tests/ 目录（一次性脚本必须 `.runtime/tmp/` 用完即删） |

## 环节 6 · 入库登记（输出）

| 项 | 内容 |
|---|---|
| **输入** | 环节 5 全部通过的条目片段 |
| **操作** | ① 片段定稿：独立 YAML 文件放 `.runtime/p3_fragments/`（命名 `{工单号}_factor_entry.yaml` 同族），文件头注释写明：目标注册表路径、目标列表键（factors/strategies）、裁决类型、与族内既有条目的刻意差异清单（每项给理由，统筹可裁定保留或回退）；② 状态字段纪律：status=candidate、algorithm_status=pending_backtest、created_at/updated_at=当日、owner=MOD-GOVERNANCE（照抄族内惯例）、code_commit=null（G5 绑定留统筹）；③ 治理字段默认值照抄族内最新条目整块（data_quality_policy/rmt_denoised 等，不自己编）；④ 片段引用写进工单片段（`w*.md`）交统筹；⑤ 实例报告收尾：六环节输入/输出/验收结论汇总表 + 观察项登记 |
| **输出** | 待登记条目片段（YAML）+ 实例报告 + 工单片段引用 |
| **验收标准** | 片段过环节 5 脚本终跑（exit 0）；片段头注释含目标路径与差异清单；工单片段含片段路径 |
| **常见坑** | ①直接改 catalogs 下注册表 YAML（铁律 1，统筹集中写）；②治理字段自己编默认值（库级一致性靠照抄族内惯例）；③状态字段越过 candidate（铁律 4）；④片段头注释缺差异清单（统筹无法判断刻意差异 vs 笔误） |

---

## 附 A · 条目片段字段骨架（factor 示例）

字段全集=注册表 entry_schema 键集（逐次现读，2026-08-22 实测 66 字段）。骨架与默认值照抄族内最新一条同 factor_class 条目，按下表替换实质字段：

| 字段组 | 替换内容 |
|---|---|
| 标识 | factor_id（族内顺延）、name/name_zh、aliases、doc_ref（源锚点+实例报告锚点） |
| 语义 | formula、alpha_source、schema_plan（五字段）、causal_graph（自然语言经济逻辑，MVP 口径）、causal_structure（confounders/colliders/specification_audit） |
| 分类 | factor_class、primary_timeframe、applicable_timeframes、direction、entry_role、applies_to、tags（词表子集） |
| 实现 | params/inputs/outputs（与公式和代码 config 对齐）、code_symbol（AST 验证过）、code_fingerprint=null、code_path=""（族内惯例）、code_commit=null |
| 状态 | status=candidate、algorithm_status=pending_backtest、evidence（分级标注）、version="1.0.0"、created_at/updated_at |
| 裁决 | variant_of（变体时非空）、discovery_agent（human/枚举值）、llm_safety_stack（human→null） |

## 附 B · 已验证实例索引

| 日期 | 条目 | 裁决 | 报告 |
|---|---|---|---|
| 2026-08-22 | FCT-SENT-028 涨跌家数二阶加速度 breadth_acc（44 号文 §9.1 F2） | 变体（variant_of=FCT-SENT-020） | `docs/_working/reports/2026-08-22-module-factory-manual-instance.md`（17 项检查全 PASS） |

## 附 C · 与自动化的分工（Phase 1+ 预告，本 SOP 不施工）

本 SOP 六环节中，环节 2（分类）与环节 3 的检索部分是纯机械操作，Phase 1 由 knowledge_classifier / module_mapper 两模块自动化（13 号文 §4.2）；环节 4 的受控生成与环节 5 的编排 Phase 2 自动化（§4.3）。环节 1 的源筛选、环节 3 的裁决终审、环节 5 的 L4 人审**永留人工**（C2 零审核=自杀）。

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|---|---|---|---|
| 2026-08-22 | 1.0.0 | 初版：六环节检查单（输入/操作/输出/验收/常见坑）+片段骨架附录；经 1 个手动实例（FCT-SENT-028）全链路验证 | 13 号文 §4.1 P0-S2；18 号清单 §6 波4-13 工单 |

---

*维护者：AI 架构协调者*
