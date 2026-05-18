---
module_id: DW-RATIONALE-001
title: ZephyrAlpha 2.0 架构推导与决策链
doc_type: log
status: active
version: 1.32.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-05-01
summary: >
  ZephyrAlpha 2.0 架构推导完整记录（Stage 1~26，R1-R92+）�?
  核心里程碑：S14 14层命名收�?�?S15 正交视图体系 �?S18-24 TOGAF 10视图就位 �?
  S26 S14-Phase2 彻底收工（OQ-026 拍板 + ADR-0010）�?
  产出：ADR-0001~0010 accepted + 10/10 TOGAF 视图 + 14层体�?+ 38跨层契约 +
  17架构不变�?+ 双树职责分离。详�?R 号索引表�?
date: '2026-04-22'
ttl: permanent
review_cycle: quarterly
---

# ZephyrAlpha 2.0 架构推导与决策链

> ⚠️ **过时引用警告**：本文件�?append-only 日志，包含对已删除目录（catalogs/、by-domain/）的历史引用。这些引用是历史事实，不应修改，但不应作为当前架构的导航依据。当前架构导航请�?index.md + _index.yaml 为准�?

> **📖 AI 读取指引**：本文件体积较大�?150KB）。新 session 无需全文读取——按以下顺序消费�?
> 1. �?frontmatter `summary`（已�?Stage 1~26 完整结论索引�?
> 2. 按需跳转到下�?R 号索引表，找到对�?R 号的�?
> 3. �?`offset` 定位到该 R 号的具体段落读取
> 4. 无需按顺序读全文——这�?append-only 日志，不是叙事文�?

---

## ⚠️ 关于 R59 / R60 / R61 重号事故的说明（2026-04-19�?

**事故事实**：批�?F（H6 Domain Event / H7 DDD Aggregate / H11 五张时序图，2026-04-19 午间�?Opus 会话完成）与批次 G（S2-S6 五视�?Architecture Runway 章节�?026-04-19 午后�?Sonnet 会话完成）在同一�?*并发执行**时，任务书派发的 R 号区段重叠，导致 R59/R60/R61 三个编号在本日志下表中各�?*双登�?*（批�?F 一�?+ 批次 G 一条）�?

**根因**：两批次任务书起草时都独立向 R 号空间后续顺延取号，**未建�?取号前强制复�?rationale-log 最�?R �?的派号台账机�?*。批�?G handoff 日志�?026-04-19 条目）明确记�?与任务书指定一致，本批次据实执�?，说明占号冲突并非执行错误，而是**任务书源头的 R 号区段被重复派发**�?

**治理决策**（遵�?ADR 编号不可变铁�?+ 项目既有 R15-R22 superseded append-only 模式）：

1. **历史记录不改�?*：下表原有两�?R59/R60/R61 条目**全部保留**，任何已落盘的引用均视为历史事实
2. **为区分两轨引用，批次 F 的三�?R 号统一追加后缀 "-F"**，即 **R59-F / R60-F / R61-F**（对�?H6 / H7 / H11�?
3. **批次 G �?R59-R63 保持原号**（先后仅差数小时，但 G 轨含 5 条连续号码更难拆分，�?先到先得 + 改动面最�?原则保留 G 轨原号）
4. **所有新引用**必须�?带后缀 = 批次 F / 原号 = 批次 G"解读，避免歧�?
5. **本公告及下表中批�?F 的三�?"-F" 条目**作为治理案例永久留痕，不得删�?
6. **防止复发机制**：本批次 H（R64）同步在 `taskbooks/serial-execution-plan.md` 顶部新增"R 号并发派号规�?，规定任何新批次任务书起草时必须�?`grep -E "^\| R[0-9]+ \|" rationale-log | tail -1` 核实当前最�?R �?

**本轮（批�?H�?026-04-19）实施的同步改动**（共 10 处引用同步打 "-F" 后缀）：

| 文件 | 改动位置 | 改动�?�?改动�?|
|------|----------|----------------|
| `rationale-log.md`（本文件�?| 下表批次 F 三行首列 | R59 / R60 / R61 �?**R59-F / R60-F / R61-F** |
| `catalogs/domain-event-catalog.md` | frontmatter `related_rationale` + §revision | R59 �?**R59-F** |
| `catalogs/ddd-aggregates.md` | frontmatter `related_rationale` + §revision | R60 / R59 �?**R60-F / R59-F** |
| `target-architecture/README.md` | frontmatter + §6 diagrams �?× 5 + §revision | R61 �?**R61-F**（批�?F 相关�? R59/R60 在修订记录区指代批次 F 处一并改 **R59-F/R60-F** |
| `handoff-log.md` | S14-BatchF 条目（整段） | R59/R60/R61 �?**R59-F/R60-F/R61-F** |
| `serial-execution-plan.md` | 批次 F �?+ 7.2/7.3/8.1 完成状态行 × 3 | R59/R60/R61 �?**R59-F/R60-F/R61-F** |

**不改动的引用**（均指代批次 G 产出物，保留原号）：
- `01-BA.md` v1.2.0 frontmatter `related_rationale: R59` �?保持�? 批次 G S2�?
- `target-architecture/README.md` frontmatter `R61` 出现两处：�? 表格内指代批�?F �?5 行时序图�?`R61-F`，但 frontmatter 头部若已有的是批�?F �?R61 则改 `R61-F`（本次已核实：README frontmatter 唯一�?R61 是批�?F 时序图索引的登记来源，统一�?-F�?
- 批次 G 产出�?5 份视图（01-BA / 02-IA / 03-AA / 04-TA / 00-overview）其余章�?R59-R63 引用均保持原�?

---

## 1. 本文档的作用

本文档不是普通会议纪要，也不是某个专题设计稿�?

它承担的�?*架构推导主线**职责，回答以下问题：

1. 系统为什么会从当前问题演化到当前方案
2. 某份文档是为了解决哪一步问题而出现的
3. 哪些结论已经形成，哪些仍未形�?
4. 下一个会话应从哪里继续，而不是重新从头讨�?

对人来说，它帮助快速找回思路�?
�?AI 来说，它帮助恢复上下文、理解讨论脉络、避免重复绕圈�?

## 2. 讨论起点

最初触发点不是“记忆系统”，而是**文件治理与文档系统失�?*�?

- 文件治理架构混乱
- 蓝图系统混乱
- 双真源并�?
- 文件名、内容、链接、索引不规范
- 原有项目结构已经不适合继续增量修补

因此第一个大判断是：

**与其在既有项目上继续补丁式修复，不如建立 ZephyrAlpha 2.0 新架构，先定终局架构，再做迁移�?*

## 3. 讨论链条

### Stage 1：从“修补旧系统”到“建立新树�?

当确认原有项目存在结构性混乱后，核心讨论不再是“怎么改一个文件”，而是�?

**是否需要一棵新的、干净的、唯一真源的新树�?*

结论是：需要�?
于是 `ZephyrAlpha 2.0` 新树成为新的讨论和建设载体�?

### Stage 2：从“新树目录”到“机构级治理视角�?

接下来讨论不再只是目录树，而是升级为：

**你虽然是单人，但开发方式本质上是多 AI 代理、多会话、多上下文断裂�?*

这意味着你面对的问题不是普通个人项目问题，而是�?

**�?owner 的多代理组织治理问题�?*

### Stage 3：从“组织协作”到“决策连续性�?

一旦把问题看成多代理协作，马上就会出现一个核心痛点：

- 前面拍板的事情，后面�?AI 怎么知道�?
- 为什么这样定�?
- 后来有没有被覆盖�?
- 哪份文档是当前有效口径？

因此最小刚需不是“大而全记忆系统”，而是�?

**Decision Memory System（决策记忆系统）**

因为它负责保存：

- 决策对象
- 决策理由
- 决策影响范围
- 决策覆盖关系

### Stage 4：从“决策记忆”到“组织记忆系统�?

在讨论决策记忆之后，进一步发现系统里需要记住的不只是决策，还包括：

- 架构
- 交付
- 研究
- 因子
- 策略
- 组合
- 执行
- 风险
- 报告
- 运维

于是问题升级为：

**需要一�?Organizational Memory System（组织记忆系统）**

但这个系统不是单一大仓库，而是�?

**统一 taxonomy + 统一 contract + 分域 canonical + 后续检索与自动化层�?*

### Stage 5：从“记忆系统设计”到“先全貌后细颗粒�?

随后又确认一个重要原则：

当前阶段不应先做细颗粒实现，而应先完�?*终局信息架构与抽屉体�?*�?

因此当前顺序被明确为�?

1. 先完成系统全貌架�?
2. 先让未来 P0 / P1 / P2 内容都有正确抽屉
3. 再进入具体制度、模板、索引与自动化实�?

这意味着�?

- **架构层面**：先整体放入记忆系统
- **实施层面**：后续先�?`Decision Memory System`

### Stage 6：从“记忆系统讨论”到“简易决策记忆系�?v0�?

继续往下讨论后，又确认了一个更落地的判断：

**当前工作区其实已经形成一个“人工主导、结构化的简易决策记忆系�?v0”�?*

它不是自动化平台，但已经具备决策记忆系统最关键的四层分工：

- **原因 / 推导�?*：写�?`architecture-rationale-log.md`
- **结果 / 结构 / 边界**：写入专题设计稿（如 `organizational-memory-system-design.md`�?
- **未决�?*：写�?`open-questions-register.md`
- **执行动作**：写�?`taskbook.md`

这一步很关键，因为它把“是不是要等系统做完再规范”这个问题，推进成了�?

**既然 v0 已存在，就应现在开始按统一标准收口，而不是等未来自动化完成后再倒推清理�?*

这又带出一个新的当前结论：

**现在就应该规范工作区文档格式，让未来 Decision Memory / Organizational Memory 的入库变得直接可接，而不是事后反向清洗�?*

### Stage 7：从"工作�?v0"�?前置项目会话留痕机制迁移"

继续讨论后，又把前置项目"为什么所有对话像是自动保存在项目�?这件事拆清了�?

它其实不是一个单点按钮，而是两层机制叠在一起：

1. **Cursor / 客户端层**：原�?transcript 自动保存在本机（JSONL / 对话记录）�?
2. **仓库规则�?*：前置项目通过 `.cursor/rules`、`AGENTS.md`、session-log-template 和会话管理规则，要求每次会话结束前把整理后的 **Session Log** 写入项目目录�?

这说明前置项目并不是"把所有原始对话自动塞进仓�?，而是�?

**原始 transcript 自动留在本机；项目内保存的是面向交接和提炼的 session log�?*

这一步把一个重要问题讲清楚了：

- **要迁移的不是"一个神秘功�?**
- 而是要把"原始 transcript + 项目�?Session Log + 关键决策升格"这套机制，在新树里重新建�?

因此当前又形成三个新判断�?

1. **新树也需要保留两�?*：外�?transcript + 项目�?session log�?
2. **新树正式 session log 路径应进�?`18_audit_and_evidence/session-logs/`**，与�?IA 对齐�?
3. **前置项目聊天记录要吸收，但不应原样全部复制进新项�?*；应先登记来源地址，再�?`raw / candidate / active` 思路分批吸收�?

### Stage 8：从"机构标准确认"�?元数据契约与触发机制细化"

本轮讨论进一步确认了组织记忆系统专题设计稿（`organizational-memory-system-design.md`）中已有的机构级标准�?

1. **元数据契约（envelope�?*�? 大类字段（Identity / Lifecycle / Provenance / Scope & Impact / Retrieval / Security & Privacy / Content）已是完整机构标准，无需额外修正�?
2. **异步流水�?*：专业机构采�?主对话模型不负责记忆整理，后台异步处�?的分层架构，避免高�?token 和上下文挤占�?
3. **知识边界分层**：明�?知识库存全文，记忆系统存索引"的分层策略，避免双真源问题�?

本轮同时暴露一个新未决问题�?

### Stage 9：从"脚本位置未决"�?记忆系统 canonical 落位确定"

本轮讨论追溯�?OQ-010（异步流水线脚本位置）的依赖链，发现其最底层依赖�?OQ-001（记忆系�?canonical 物理落位）�?

因此优先确定了记忆系统的物理落位方案�?

1. **核心原则**：分散存�?+ 集中索引，避免双真源
2. **索引�?*：`08_ai_engineering_and_agent_ops/memory-and-context/` 内部按语义分�?
   - `decision-memory/` —�?决策记忆索引（ADR、关键决策、依赖追踪）
   - `operational-memory/` —�?操作记忆索引（session logs、执行轨迹）
   - `knowledge-memory/` —�?知识记忆索引（链接到 15_knowledge_base/�?
   - `context-services/` —�?上下文服务能力（装配、交接、检索接口）
   - `memory-governance/` —�?记忆治理（schema、质量闸门、留存策略）
3. **全文�?*：各业务域（02/15/18 等）存实际文档，记忆系统只存索引和元数据
4. **状态管�?*：candidate/raw/active/superseded 用索引层状态字段，不按目录�?

这一落位方案符合机构标准�?按域分放，不用单一记忆层堆全文"），为后续确定脚本位置、Session Log 路径、数据流设计提供了基础�?

### Stage 10：从"物理落位确定"�?P0/P1/P2 实施优先级划�?

本轮讨论追溯�?OQ-002（记忆系统零件地�?P0/P1/P2 划分），并对比验证了机构标准做法�?

**关键发现**�?
- 机构标准 P0 �?**Decision Memory System（决策记忆闭环）**，不是多个组件并�?
- operational-memory 是决策记忆闭环的 **输入�?*，不是独立的 P0
- 机构踩过的坑�?同时做大而全数据库、向量服务、UI、自动写回……会变成大项目里的又一个大项目"

**最终确定的 P0/P1/P2 划分**�?

| 优先�?| 组件 | 说明 |
|--------|------|------|
| **P0** | **Decision Memory System（决策记忆闭环）** | decision-memory 核心 + operational-memory 输入支撑；必须跑�?raw �?candidate �?active �?superseded 完整链条 |
| **P1** | context-services + knowledge-memory | 上下文装配、知识索引；�?P0 后可以运转但效率�?|
| **P2** | memory-governance 全自�?| 自动质量闸门、自动留存、自动升格；系统成熟后实�?|

这一划分符合机构标准（文�?§3.3 "P0 建议：Decision Memory System"），避免了范围蔓延�?

**当前仍依赖下一�?*：回�?OQ-010（脚本位置）�?OQ-008（Session Log 路径）的确定�?

### Stage 11：从"P0/P1/P2 确定"�?跨域核心价值链确认"

本轮讨论�?大颗粒度全貌"角度，确认了 ZephyrAlpha 2.0 的跨域核心价值链�?

**关键结论**�?

1. **核心价值链是机构通用标准**：无论机构大小、策略类型，量化投资的核心价值链都是
   ```
   数据 �?研究 �?模型 �?策略 �?组合 �?执行 �?报告
   ```
   这是投资决策的自然流程，无法跳过�?

2. **横向治理贯穿始终**�?
   - `00_governance/` —�?政策控制
   - `17_risk_and_controls/` —�?风险监控
   - `08_ai_engineering_and_agent_ops/memory-and-context/` —�?记忆沉淀

3. **价值链与目录结构的映射**�?
   | 价值链环节 | 对应 docs/ 目录 |
   |------------|-----------------|
   | 数据 | `09_data_platform/` |
   | 研究 | `10_research_and_factor_lab/` |
   | 模型 | `11_model_and_ml_platform/` |
   | 策略 | `12_strategy_and_portfolio/` |
   | 执行 | `13_execution_and_order_lifecycle/` |
   | 报告 | `14_reporting_and_distribution/` |

4. **第二级颗粒度（数据契约）延后**：先完成全貌架构，再讨论每步的输入输出契约�?

**本轮明确**：核心价值链已确认，可作为架构全貌的基础；细颗粒度数据契约留待后续�?

### Stage 12：从"脚本位置未决"�?异步流水�?canonical 落位确定"

本轮讨论追溯�?OQ-010（异步流水线脚本位置）的根源问题，发现其本质�?*脚本的职责边界与系统的功能域划分尚未完全对齐**�?

**触发�?*�?
- 用户指出应先讨论记忆系统的治理体系定位，再确定脚本位�?
- 需要明确记忆系统在治理体系中的完整位置，才能确定异步流水线的归�?

**关键结论**�?

1. **记忆系统在治理体系中的四层分�?*�?
   ```
   记忆系统治理体系
   ├─ L1 治理总控     docs/00_governance/                        —�?政策定义：记忆系�?应该怎么工作"
   ├─ L2 AI 工程�?   docs/08_ai_engineering_and_agent_ops/...   —�?索引存储：运行能力、检索接�?
   ├─ L3 审计�?      docs/18_audit_and_evidence/session-logs/   —�?输入源：Session Log 留痕
   └─ L4 脚本治理�?  scripts/governance/                        —�?生产线：后台异步流水�?
   ```

2. **机构分层原则**（踩坑教训）�?
   | �?| 后果 | 正确做法 |
   |----|------|----------|
   | 把记忆处理脚本放�?`src/` 产品代码�?| 治理逻辑与业务逻辑耦合，升级困�?| 治理是治理，产品是产�?|
   | 把记忆处理放在主对话模型�?| Token 成本高、上下文挤占、响应慢 | 必须异步解�?|
   | 把记忆脚本分散在各域 | 无法统一 schema、质量闸门、留存策�?| 需要统一治理�?|
   | 一开始就做大而全的数据库+向量服务+UI | 变成"大项目里的又一个大项目" | P0 只跑通闭环，不堆基础设施 |

3. **异步流水�?Layer 2 的最终落�?*�?
   - **路径**：`scripts/governance/memory-pipeline/`
   - **中文路径**：`脚本/治理/记忆流水�?`
   - **理由**：它在后台异步生产结构化记忆，属�?*治理范畴**（让内容变规范、状态流转），不是审计检查，也不是产品运行时

4. **`scripts/governance/` 的职责合�?*�?
   - �?`audit/` �?`governance/` 已合并为单一 `governance/` 目录——所有审计和治理脚本统一入口
   - `governance/` = 治理工厂 + 质检部门（生产记�?+ 检查规�?+ 生成报告�?
   - 异步流水线放 `governance/memory-pipeline/`——在生产记忆，属治理范畴

**本轮明确**：异步流水线脚本位置已确定，OQ-010 关闭；记忆系统的治理体系四层分布已清晰�?

### Stage 13：从"记忆系统前提"�?治理体系全貌确认"

本轮讨论确认�?*记忆系统的前提是先确定治理文件体系的全貌**�?

**触发�?*�?
- 用户指出记忆系统的位置依赖于治理体系架构
- 需要先理解专业机构文件治理体系的完整架�?

**关键结论**�?

1. **治理体系五层架构**（机构标准）�?
   | 层级 | 路径 | 职责 |
   |------|------|------|
   | L1 治理政策�?| `docs/00_governance/` | 定义系统应该怎么被管�?|
   | L2 标准定义�?| `docs/01_policies_and_standards/` | 定义合格产物标准 |
   | L3 架构真源�?| `docs/02_enterprise_architecture/` | 全系统总体架构真源 |
   | L4 域级治理�?| �?`docs/XX_*/` 内部 | 域内自治 + 横向对齐 |
   | L5 执行代码�?| `scripts/` + `src/` | 实际执行治理逻辑 |

2. **横向治理三条主线**�?
   - 政策控制（`00_governance/`）：系统应该怎么被管�?
   - 风险监控（`17_risk_and_controls/`）：什么风险、怎么监控
   - 记忆沉淀（`08_ai_engineering_and_agent_ops/memory-and-context/`）：决策和操作怎么被记�?

3. **记忆系统的治理定�?*�?
   - 记忆系统不是独立�?�?个治理域"
   - 记忆系统�?**AI 工程域（08/）的核心能力之一**
   - 治理政策�?0/）定义记忆应该怎么管理
   - AI 工程域（08/）实现记忆的技术能�?

4. **重新讨论记忆系统的前提问�?*�?
   - 记忆系统的治理政策应该放在哪里？
   - 记忆系统的执行代码应该放在哪里？
   - 记忆系统的索引应该放在哪里？

**本轮明确**：治理体系全貌已确认，为重新讨论记忆系统位置提供了前提；三个问题（政�?执行/索引位置）待回答�?

### Stage 14：骨架对齐机构终局�?026-04-17 下半段，Opus 4.7 收口�?

**触发**�?

- 用户 + Opus 联合做了一�?埋雷清单"审查，发�?13 处不符合专业机构做法的风险点
- 用户决定全修�? �?🔴🟡），并要求此前未完成的骨架建设任务一并完�?
- 采用"先骨架、后内容"策略：先把目录结构、schema、ADR 范式敲定，内容按需填充

**推导与决�?*�?

1. **"沙盒�?正式�?�?schema 是错误方�?*
   - 背景：v1 标准曾引�?沙盒�?3 字段起步 / 正式�?12+ 字段"双轨
   - 对标：机构（Google、IETF、ISO、JPMorgan、McKinsey）普遍采�?单一 schema + status 驱动"
   - 决策：采�?单一 schema + 分阶段必填闸�?，升格只�?`status`，不做字段迁�?
   - 升格：落地为 ADR-0002

2. **ADR 必须�?canonical 域，不能放在 workspace**
   - 背景：此前计划把 ADR 放在 `19_development_workspace/05_adr/`
   - 问题：ADR �?canonical 凭证（accepted 后长期有效），不应与讨论沙盒混放
   - 决策（历史）：ADR canonical 家曾映射�?`docs/02_enterprise_architecture/adr/`；草稿区 = `docs/19_development_workspace/adr-drafts/`
   - **现行�?026-05-05 session-012�?*：accepted 条目权威�?**KB:decisions**（SQLite `knowledge`，`category=architecture_decision`）；物理 `adr/` 树已删除——映射见 `ssot-authority-map.md`
   - 升格：落地为 ADR-0001 的一部分（真源的内部分层）；后续演进�?KB ingestion / GOV-DOC-003 §2.2

3. **workspace 子目录采用语义命名，取消 `0N_` 数字前缀**
   - 背景：机构内�?workspace 惯例是语义命名（`taskbooks/` 而非 `00_taskbooks/`�?
   - 数字前缀用于 canonical �?外部引用优先�?，workspace 内部用不�?
   - 决策：一次性重命名 5 个老目�?+ 批量更新 98 处引用路�?

4. **`doc_type` 必须有受控词表（controlled vocabulary�?*
   - 背景：无约束�?`doc_type` 会导致同一类型文档出现不同值（`adr` vs `ADR` vs `architecture_decision_record`�?
   - 机构做法：预定义合法值清单，新增值需�?KB 决策记录流程
   - 决策：在 `discussion-document-standard.md` v2.0.0 §3 明确 15 个合�?`doc_type` �?

5. **`module_id` 必须有命名规�?*
   - 背景：此�?`module_id` 命名混乱（`DW-INDEX` 无编号，`DW-TASK-001` 有编号）
   - 机构做法：统一格式 `<DOMAIN>-<TYPE>-<NNN>`；ADR 特殊保留 `ADR-NNNN` 短格�?
   - 决策：在 `discussion-document-standard.md` v2.0.0 §4 明确格式、DOMAIN 值表、TYPE 值表

6. **`~~删除线~~` 处理 superseded 是错误做�?*
   - 背景：rationale-log 此前用删除线标记被推翻的结论（R15/R17/R19-R22�?
   - 问题：删除线是视觉效果，不是机器可读状态；未来 AI 索引无法识别"此条已失�?
   - 机构做法：append-only，保留原文，`status: superseded` 字段 + `superseded_by` 指向新条�?
   - 决策：本轮清�?rationale-log 所有删除线；在标准 v2.0.0 §6.2 明确 append-only 规则

7. **Taskbook 状态必须用符号化表�?*
   - 背景：taskbook 此前用散文状态（"重新讨论�?�?本轮完成"�?暂定"�?
   - 问题：机器无法检�?所有进行中的任�?�?所有阻塞的任务"
   - 机构做法：用 `[ ] [/] [x] [~]` 四符号统一表示 open / in-progress / closed / blocked
   - 决策：本轮清�?taskbook 所有散文状态；在标�?v2.0.0 §8 明确四符号规�?

8. **ADR / rationale-log / Decision Memory Index 三者边界必须明�?*
   - 背景：用户与 AI 都容易混淆三�?
   - 决策：在 `document-triage-guide.md` v2.0.0 §1.2 明确�?
     - rationale-log = 推导�?*时间�?*（append-only�? 份、workspace�?
     - ADR = 单决�?*快照凭证**（不可变、N 份、canonical�?
     - Decision Memory Index = **路由索引**（可重建�? 份、canonical�?

9. **需要大白话 �?行业术语的术语映射表**
   - 背景：用户记不住所有行业黑话，需要翻译帮�?
   - 机构做法：主流机构都�?"Enterprise Business Glossary"（JPMorgan、高盛、BCG、McKinsey 等）
   - 决策：新�?`terminology-mapping.md`，双向映射表（大白话 �?行业术语），覆盖架构/治理/决策/记忆/任务/流程/元数�?AI 协作/投资业务 9 �?

10. **文档分类�?4 类扩展到机构标准 8 �?*
    - 背景：v1 triage-guide 只覆�?taskbook / rationale-log / open-questions / design-draft 四类
    - 机构完整分类：再�?ADR / roadmap / risk-register / session-log
    - 决策：triage-guide 升级�?v2.0.0�? 类完整图�?+ 每类的定义与边界

**本轮明确**：骨架已对齐机构终局；内容按需填充；接下来的讨论可以在这套骨架上无负担推进�?

### Stage 15：src 14 层最终命名收口（2026-04-18 会话 12，Opus 4.7�?

**触发**�?

- 物理 `src/zephyr/` 现状�?12 层（l00-l11），�?14 层终�?�?2 �?
- 现存物理层中�?3 个层名（`l09_research_innovation` / `l10_governance_compliance` / `l11_strategic_decision`）与对标矩阵速记（`l09_sandbox` / `l10_governance` / `l11_ml_platform`）和 ADR-DRAFT-0009（保�?`l10_governance_compliance` / `l11_strategic_decision`，但已规�?l12/l13/l14/l15）三方互相不一�?
- 必须�?专业机构怎么�?+ AI 找得最�?为标尺，�?`l11_strategic_decision` 整层处置 + `l10` 命名两件事一次性收�?
- 用户原则：架构终局期不动物理代码，�?*命名决议必须先在决策记忆里固�?*，未�?ADR-DRAFT-0009 修订时同步搬�?

**Q1：l11_strategic_decision 整层怎么处理�?*

业界 4 种主流模式扫描：

| 模式 | �?| 物理形�?|
|---|---|---|
| P1 作为 L05 子模�?| **BlackRock Aladdin** | `l05/asset_allocation/strategic/` + `l05/asset_allocation/tactical/` |
| P2 纯流程不进代�?| Goldman / JPM / Citadel | Investment Committee 流程，进 docs/ |
| P3 完全不存�?| Two Sigma / 大部分纯量化 | 决策都在算法�?|
| P4 前端工具 | BlackRock Aladdin Studio / MSCI Barra | Investment Committee Workspace 是前�?|

业界**没有任何机构**�?`strategic_decision` 列为独立顶层。我们的 14 层对标矩�?L11 直接就是 ml_platform，根本没�?strategic_decision 这一层�?

**决策（R31�?*：采�?**P1 BlackRock 模式**，将 strategic_decision 移入 `l05_portfolio_construction/strategic/` 子模块�?

理由�?

1. **业界最专业的对�?*：BlackRock Aladdin（管�?$10T+ 资产）就是这么做�?
2. **语义最准确**：strategic asset allocation 本来就是 portfolio construction 的长周期版本
3. **未来扩展自然**：以后真�?IC（投资委员会）流程，可以�?`l05/ic_workflow/` 子模�?
4. **�?OQ-070 的全球扩展契�?*：portfolio construction 未来�?jurisdiction 分片（cn / us / eu），strategic 自然也按 jurisdiction �?
5. **AI 找得�?*：AI 看到 `l05_portfolio_construction/strategic/` 立刻明白这是"战略组合构建"，不需要查文档
6. **不�?P2 / P3 的原�?*：用户已规划 AI Operator �?strategic 决策中介入（OQ-063 C-1 �?`l05/_ai_operator/`），需要代码承载，不能纯流程或完全删除

**Q2：l10 命名 `l10_governance` vs `l10_governance_compliance` vs `l10_compliance`�?*

业界 governance vs compliance 的本质区别：

| �?| 含义 | 谁负�?| 进代码层�?|
|---|---|---|---|
| **Governance（治理）** | "谁能做什么决定，怎么�? | Board / Risk Committee / IC | �?通常不进，在 docs/ 和配�?|
| **Compliance（合规）** | "做出来的事是否符合外部法�? | CCO / Compliance Officer | �?进代码，运行时硬约束 |

业界扫描�?

| 机构 | L10 层名 | 涵盖 |
|---|---|---|
| Goldman SecDB | `compliance/` | 仅外部合�?|
| JPM Athena | `regulatory/` + `governance/` 分两�?| 监管单独，治理单�?|
| Citadel | `compliance_lab/` | 偏合�?|
| Two Sigma | `compliance/` | 偏合�?|
| BlackRock Aladdin | `compliance/` + risk_governance（属 L04�?| 合规独立�?|
| Bloomberg AIM | `compliance_engine/` | 偏合�?|

**关键观察**：业界绝大多数顶级机构的 L10 这一层叫 `compliance`，不�?`governance`。原因：代码层承载的�?*硬约束的运行时检�?*（如订单送出前查 MiFID II best execution），所以叫 compliance 最准；governance 内容（IPS、IC 决策、Risk Committee 决议）通常�?docs/ 或配置文件�?

**�?OQ-070 的契合度验证**：OQ-070 已规�?L10 �?jurisdiction 分片�?`policies/cn_a_share/` / `us_share/` / `eu_mifid2/`——这�?*全部�?compliance 政策**（MiFID II 是欧盟合规法规），不�?governance�?

**决策（R32�?*：采�?**B3：`l10_compliance`** 命名�?

理由�?

1. **业界绝对主流**：Goldman / Citadel / Two Sigma / BlackRock / JPM 都叫 compliance
2. **语义最�?*：代码层承载的就是硬合规约束（OPA 政策、订单合规检查、报告生成等�?
3. **�?OQ-070 完美对齐**：`policies/cn_a_share/` / `eu_mifid2/` 就是 compliance 政策
4. **Governance 概念另放，不冲突**：内部治理（IPS、IC 决策、AI 自治公司组织规则�?9 治理系统、文件治�?7 层）属于 `docs/07_governance_and_compliance/META_GOVERNANCE/` + `scripts/governance/`（用户之前已规划），不进 L10 代码�?
5. **AI 找得�?*：AI 看到 `l10_compliance` 立刻明白"这是外部合规约束的运行时�?
6. **不�?B1（governance）的原因**：词义错误，几乎没有机构这样命名
7. **不�?B2（governance_compliance）的原因**：长、混合两个不同概念，无业界对�?

**14 层最终命名锁�?*�?

```
l00_data_source                数据�?
l01_infrastructure             基础设施
l02_alpha_factor               Alpha 因子
l03_signal_generation          信号生成
l04_risk_management            风险管理
l05_portfolio_construction     组合构建（含 strategic/ + tactical/ 子模块） �?R31
l06_trade_execution            实盘执行/券商接入
l07_post_trade_analytics       事后分析/归因
l08_human_ai_interface         人机接口（LLM/Agent�?
l09_sandbox                    沙箱/回测
l10_compliance                 合规（外部监管硬约束�?                       �?R32
l11_ml_platform                ML 平台/MLOps
l12_system_telemetry           遥测
l13_experiment_pipeline        实验流水�?
+ shared/                      跨层契约（横切，不计入主层数�?
```

**对比物理 src/ 现状的变化总览**�?

| 物理现状 | 终�?| 变化类型 |
|---|---|---|
| l09_research_innovation | l09_sandbox | 改名 |
| l10_governance_compliance | l10_compliance | 改名（R32�?|
| l11_strategic_decision | 删除（功能移�?l05/strategic/�?| 删层（R31�?|
| —（未建�?| l11_ml_platform | 新建 |
| —（未建�?| l12_system_telemetry | 新建 |
| —（未建�?| l13_experiment_pipeline | 新建 |

**净变化**�?1 + 3 = **+2 �?*，从 12 �?14 层�?

**本轮限定动作**�?

- �?R31 / R32 写入本日志（决策记忆�?
- �?OQ-073 �?OQ register 关闭存档（含完整对标证据�?
- �?handoff-log 追加留痕
- �?**不动** `src/zephyr/` 物理目录（架构终局期原�?1�?
- �?**不修�?* ADR-DRAFT-0009（避免大改；但在本日志末尾点�?未来修订时同�?R31/R32 + 把标题从 11�?5 层改�?12�?4 �?�?

**未来同步任务（待办备忘，不在本轮执行�?*�?

1. ADR-DRAFT-0009 修订：标�?"11�?5 �? �?"12�?4 �?；内�?layer 命名 `l10_governance_compliance` �?`l10_compliance`、`l11_strategic_decision` �?移除（写�?§3.x "已移�?l05/strategic/"）；引用 R31 / R32 / OQ-073
2. `target-architecture/03-application-architecture.md` 同步：当前文件标题写"11-layer"、又�?15 �?，存在大幅不一致，待架构终局拍板后一次性修�?
3. `target-architecture/by-domain/src-domain/README.md` §4 14 层结构提醒块：`l10_governance_compliance` �?`l10_compliance`、`l11_strategic_decision` �?删除、`l11_ml_platform` 顶上�?
4. `kimi任务-v2.md` 中的 14 层命名核对（用户已声�?kimi 任务暂停，未来恢复时一次性同步）
5. 物理 `src/zephyr/` 改名（重命名 l09/l10、删�?l11_strategic_decision、新�?l11_ml_platform / l12 / l13）——架构终局正式锁定后由施工 Sprint 0 一次性执�?

**本轮明确**�?4 层最终命名已锁，依据业界最专业对位（BlackRock + Goldman/Citadel 主流�? AI 可发现性。R31 / R32 自此为单一真源；其他文档与物理代码后续�?R31 / R32 + OQ-073"反向同步�?

---

## Stage 16�?3-AA 微调 + OQ 收尾（S14 Phase 1�?026-04-19�?

**上下�?*：基�?Stage 15 �?14 层终态命名决策（R31/R32/OQ-073），�?Stage 执行"阶段 1：OQ 收尾 + 03-AA 微调"——将已拍板的命名决策落盘�?`03-application-architecture.md`，同时关闭三个悬�?OQ，并补充 N11/J5 两项架构设计决策�?

**本轮产出文件**：`03-application-architecture.md` v1.6.0 �?v1.7.2（新增约 150 行，含附�?A）、`open-questions-register.md` v2.14.0 �?v2.15.0�? OQ closed）、本日志 v1.15.0 �?v1.16.0（Stage 16 + R33/R34/R35）、`handoff-log.md`（S14-Phase1 entry）�?

**�?Stage 关闭�?OQ**：OQ-030（R33�? OQ-068（R34�? OQ-023（R35）�?

### 决策 R33：L12 命名最终锁定为 `l12_system_telemetry`（Closes OQ-030�?

**决策**：L12 命名采用 `l12_system_telemetry`，永久否�?`l12_observability`�?

**完整理由�?*�?
- `system_telemetry` 强调"系统产出的结构化指标�?（metrics/logs/traces 三支柱），是机器消费（AI 读取）的数据流——这�?L07 `post_trade_analytics`（给人看的业务报表）明确区分，避免歧�?
- `observability` �?Google SRE Book 的工程文化概念（�?Debugging / Profiling / Post-mortem 等人工活动维度），适合做工程理念标签，不适合做代码层�?
- `zephyr-src-gap-analysis.pdf` 原始分析文档明确使用 `l12_system_telemetry`，与本决策一�?
- 前期设计�?`ai-autonomy-architecture-design.md v1.1.0` 已采�?`l12_system_telemetry`
- **业界对标**：Google 内部层命名倾向�?"telemetry" 而非 "observability" 作为代码模块名（前者是技术准确描述，后者是文化/哲学描述）；Netflix OSS 同理

**落盘位置**：`03-application-architecture.md` §4.1 `l12_system_telemetry/` 完整子模块清�?+ rationale 注释

### 决策 R34�?4 层架构对标业界顶级机构，足够，不新增顶层（Closes OQ-068�?

**决策**�?4 层（l00–l13 + shared）对标业界顶级量化机构，覆盖度足够，**不需要新增任何顶�?*�?

**对标证据摘要**（完整证据见 `03-AA.md` 附录 A）：

| 机构 | 核心分层�?| L10 命名 | L11+ AI �?| 结论 |
|------|----------|---------|-----------|------|
| Goldman Sachs SecDB | ~12�?4 �?| compliance �?| 无独�?strategic �?�?| 对位完全一�?|
| JPMorgan Athena | ~10�?3 �?| compliance（regulatory）✅ | 无独�?ML Platform�?024 补建中）| 我们先行 |
| Two Sigma | ~12�?4 �?| compliance �?| Telemetry + Experimentation 均独�?�?| 完全对齐 |
| Citadel | ~8�?2 �?| compliance_lab �?| 风控拆子层不增顶层（证明 submodule 优于增层）| 方法论对�?|
| BlackRock Aladdin | ~14 �?| compliance �?| ML Engine + Monitoring 均独�?�?| 最强对�?|

**核心洞察**：专业机构通过"子模块扩�?而非"增加顶层"来处理细分需求（Citadel 案例），这验证了本项�?14 �?+ submodule"的架构哲学正确性�?

**落盘位置**：`03-application-architecture.md` 新增附录 A�?4 层架构对标证据，�?80 行）

### 决策 R35：meta_strategy 归属 `l05/meta_router/`，不新建 l15 层（Closes OQ-023，N11�?

**决策**：Meta-Strategy Router 代码归属 `l05_portfolio_construction/meta_router/`，否决新建独�?`l15_meta_strategy/` 层�?

**方案对比**�?

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案 A**：独�?`l15_meta_strategy/` | meta_strategy 单独成顶�?| 语义独立清晰 | 产生 15 层超出业界惯例；依赖 L05 优化器和 L04 风控，独立出去跨层耦合变重；AI Operator 挂载位置�?OQ-063 C-1 预留冲突 | �?否决 |
| **方案 B**：归�?`l05/meta_router/` �?| 元策略作�?portfolio construction 子模�?| 语义准确（元策略是组合构建的高阶形态）；共�?StrategyRegistry�?4 层保持；AI Operator 自然�?`l05/_ai_operator/` | 初看不直觉（"�?字让人觉得该�?L05 之上）| �?采纳 |

**归属理由**：meta_strategy（元策略路由）从 700+ 策略池选取并加权组合，�?`l05/optimization/`（权重优化）共用底层数学工具，与 `l05/rebalancing/`（再平衡）共用时间维度管理，�?`StrategyRegistry` 高度耦合——三重耦合决定归属 L05 最优。`diversity_gatekeeper`（OQ-031）同�?`l05/meta_router/`�?

**落盘位置**：`03-application-architecture.md` §4.1 L05 `meta_router/` 子模块完整清�?+ 归属决策说明

### 附记：J5 L00 ACL 显式化（非正�?OQ，补充落盘）

**背景**：J5 是后�?H8（ACL 设计深化）阶段的前置基础，本 Stage �?§4.1 L00 中明确标�?`connectors/` 子模块为 **Anti-Corruption Layer (ACL)**�?

**ACL 选型依据**（vs Adapter / Facade）：
- **Adapter** 只做接口适配（方法签名转换），无法处理语义差异（�?tushare 用整数表示价格分、AKShare 不同时区约定�?
- **Facade** 是简化复杂系统调用的门面，目标是"隐藏复杂�?而非"隔离外部领域概念"
- **ACL（Anti-Corruption Layer�?* �?DDD 战略设计模式，核心价值是将外部领域概�?翻译"为内部领域语言，防�?Vendor 命名约定和数据模型渗透到核心业务层——这正是 `connectors/` 的职�?

**落盘位置**：`03-application-architecture.md` §4.1 L00 `connectors/` 子模块说明（�?250 字）；H8 阶段将在此基础上深�?Vendor Registry + �?Vendor 故障转移设计�?

## Stage 17：G1 新建独立 Data Architecture 视图（S14 Phase 2 子任�?2.1�?026-04-19�?

**上下�?*：基�?`serial-execution-plan.md` 阶段 2 子任�?2.1（G1，Opus 单批），新建独立 TOGAF Data Architecture 视图 `05-data-architecture.md`。任务源头是 2026-04-18 会话 `cda60b89`�?ZephyrAlpha vs 专业机构差距分析" §2.1）：Opus 当时指出 TOGAF 8 视图本项目只覆盖 4 个，**Data Architecture (DA) �?合并�?IA �?*——DA 关心"业务数据对象"，IA 关心"信息资产组织"，两者不同�?

**本轮产出文件**：`05-data-architecture.md` v1.0.0（新建，�?300 行，�?11 章节）、`target-architecture/README.md` v1.1.0 �?v1.2.0（文档清单与导航新增 DA 行）、本日志 v1.16.0 �?v1.17.0（Stage 17 + R36）、`handoff-log.md`（S14-G1 entry）、`serial-execution-plan.md`（子任务 2.1 勾�?[x]）�?

**�?Stage 关闭�?OQ**：无（G1 是新建视图，不直接关闭已登记 OQ；但补足�?OQ-068 时代识别出的"TOGAF 视图覆盖度不�?长期缺口）�?

### 决策 R36：Data Architecture 独立成视图（v1.0.0 新建，非�?IA 迁移�?

**决策**：在 `02_enterprise_architecture/target-architecture/` 下新�?`05-data-architecture.md`，作为独立的 TOGAF DA 视图，与 02-IA 平级�?*v1.0.0 是全新创建，0 字内容自 02-IA 搬走�?*

**关键事实澄清（任务下达时的预�?vs 实际情况�?*�?

任务原始指令假设"内容�?02-IA 中拆出数据架构相关部�?。实际查 `02-information-architecture.md` v1.1.0 全文�?83 行）后发现：02-IA 全篇只讲 docs/ 21 抽屉、文档生命周期、frontmatter 元数据标准、抽屉成熟度—�?*完全不含任何业务数据对象（Order/Fill/Bar/Factor 等）**。也就是说，DA 此前从未存在于任何视图中，包�?02-IA。R36 因此选择"新建"而非"迁移"�?

**方案对比**�?

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案 A**：保�?DA 缺位，留在未来按需�?| 不新建视�?| 0 工作�?| TOGAF 8 视图覆盖度仍只有 4/8；PIT/Survivorship/血缘等量化红线�?canonical 落盘点；新成�?�?AI 找不到数据架构主入口 | �?否决（被 cda60b89 会话定性为"严重缺失"�?|
| **方案 B**：把 DA 内容补到 02-IA �?| 复用现有 IA 文件 | 0 新文�?| TOGAF 标准�?DA �?IA 是两个平级视图，混在一起会�?02-IA 同时承担"文档抽屉治理"�?业务数据治理"两套语义，违�?SRP�?2-IA �?v1.1.0 active，强行扩展会造成版本号跳变与读者混�?| �?否决 |
| **方案 C**：新建独�?`05-data-architecture.md` �?| �?02-IA 平级、与 03-AA/04-TA 通过 §10 边界关系图严格区�?| �?TOGAF 标准一致；PIT/Survivorship/Lineage/MDM/Quality/Retention �?canonical 落盘点；02-IA 不动；未来新�?Security/Integration/Operations 视图时复用同一编号节奏�?5-DA / 06-Sec / 07-Integ / 08-Ops�?| 多一个文件需维护 | �?采纳 |

**视图内容 10 章节决策依据**（呼应任务书要求�?cda60b89 会话 §5.1/§5.2 量化行业专有清单）：

| 章节 | 来源 | 核心决策�?|
|------|------|----------|
| §2 Data Entity Catalog�?9 条） | cda60b89 §5 + 旧体系 L00 工作 | 粒度只到 entity + 字段族；字段�?DDL �?09_data_platform |
| §3 三维分类（温度×节奏×来源） | 业界 Data Mesh + Lambda 架构通用做法 | 分类驱动 04-TA 选型，但 DA 不指定具体技�?|
| §4 PIT 三字段铁�?| cda60b89 §7 + SQL:2011 bitemporal | `asof_date` / `ts_ingest` / `vendor_release_ts` 三字段必填；CI fitness function 强制 |
| §5 Survivorship 反偏差查询契�?| cda60b89 §5.1 | 强制�?`build_universe(asof, include_delisted=True)`；禁止裸�?`WHERE status='active'` |
| §6 三层血缘模型（Schema/Pipeline/Instance�?| OpenLineage / DataHub | DA 定接口标准，不选具体工�?|
| §7 MDM 三件�?| cda60b89 §5.1 + 旧体系 L00-M5 catalog | Security/TradingCalendar/CorporateAction，bitemporal + Steward 责任矩阵 |
| §8 Data Quality 五类断言 | Great Expectations / Soda Core 业界规范 | PIT/Survivorship/Lineage 三类业界工具不覆盖，必须自研（呼�?OQ-032 Build vs Buy 五大铁律�?|
| §9 保留与归档矩�?| 监管 7 �?+ 量化历史永久 | Order/Fill 永久保留对齐合规；具体监管条款映射延后到 16_compliance_and_legal |
| §10 与其他视图边�?| TOGAF 标准 + 本项�?by-domain 双轨 | DA vs IA �?图书馆书�?vs 资金账本"类比强化区分，防止读者混�?|

**R 编号微调说明**：原任务指令�?R33"，但 rationale-log �?R33 已被占用（L12 命名锁定�?026-04-19 S14 Phase 1）。本决策使用下一个可用编�?**R36**，符�?R 编号永不复用"约定�?

**落盘位置**�?
- `02_enterprise_architecture/target-architecture/05-data-architecture.md` v1.0.0（新建）
- `02_enterprise_architecture/target-architecture/README.md` v1.2.0（文档清单加�?DA 行）
- 本日�?Stage 17 + 结论 R36

**未关闭事�?/ 后续衔接**�?
- DA 视图引用了若�?未来视图"�?6-Security / 09_data_platform 子文档），那些视图的具体内容由后�?G2/G3/G4 任务建设
- DA §6 提到�?`lineage_root` 字段需要在未来 09_data_platform 物化�?schema；本视图只定原则
- DA §8 提到�?`test_no_lookahead_bias.py` / `test_no_survivorship_bias.py` / `test_lineage_completeness.py` 三个 fitness function �?scripts/fitness_functions/ 实施 Sprint 落盘

## 4. 当前已形成的关键结论

| 编号 | 结论 | 含义 |
|------|------|------|
| R1 | ZephyrAlpha 2.0 需要新架构 | 既有项目不再适合作为长期唯一真源 |
| R2 | 当前问题是多代理组织治理问题 | 不是普通单人项目文档问�?|
| R3 | 决策连续性是最小刚需 | 决策记忆是记忆系统的最小落地点 |
| R4 | 组织记忆系统需要整体设�?| 不应把问题缩成单一聊天记忆 |
| R5 | 当前阶段先做全貌架构 | 先定抽屉，再谈细颗粒制度与实�?|
| R6 | `19_development_workspace` 必须存在 | 用于承载讨论、设计稿、任务书与未决问�?|
| R7 | 当前工作区已形成简易决策记忆系�?v0 | 原因、结果、未决、任务已经各有承载文�?|
| R8 | 现在应先做格式规范化 | 先让讨论文档具备可升格、可检索、可入库的统一结构 |
| R9 | 前置项目“自动保存到项目里”是两层机制 | Cursor transcript 自动保存 + 仓库规则强制 Session Log |
| R10 | 新项目应迁移的是机制，不是原样复制旧日志 | 新项目要重建 session log 制度�?intake 规则 |
| R11 | 前置项目聊天记录未来应分批吸�?| 先登记来源，再按 `raw / candidate / active` 处理 |
| R12 | 元数据契约已是机构标�?| `organizational-memory-system-design.md` §5.2 �?7 大类字段无需修正 |
| R13 | 异步流水线是专业机构标准 | 主对话模型不负责记忆整理，后台异步处�?|
| R14 | 知识边界分层策略已明�?| 知识库存全文，记忆系统存索引，避免双真源 |
| R15 | 记忆系统 canonical 物理落位（初版） | 索引层在 `08_ai_engineering_and_agent_ops/memory-and-context/` 的方案；**status: superseded**（需重新讨论，见 OQ-001 已重新打开�?|
| R16 | 记忆系统内部结构（初版） | decision/operational/knowledge/context-services/memory-governance 的语义分类；**status: superseded**（需重新讨论�?|
| R17 | 记忆系统 P0/P1/P2 划分（初版） | P0 = Decision Memory System 的方案；**status: superseded**（需重新讨论，见 OQ-002 已重新打开�?|
| R18 | 跨域核心价值链已确�?| 数据→研究→模型→策略→组合→执行→报告；横向治理贯穿；细颗粒度数据契约延后 |
| R19 | 记忆系统在治理体系中的四层分布（初版�?| 政策定义+索引存储+输入�?生产线的四层方案�?*status: superseded**（需重新讨论�?|
| R20 | 异步流水线脚本位置（初版�?| `scripts/governance/memory-pipeline/` 的方案；**status: superseded**（需重新讨论，见 OQ-010 已重新打开�?|
| R21 | 机构分层原则（初版） | 治理≠审计≠产品的分层方案；**status: superseded**（需重新讨论�?|
| R22 | 记忆系统治理体系（初版） | 四层分工方案�?*status: superseded**（需重新讨论�?|
| R23 | 治理体系五层架构 | **当前结论**：L1政策�?00_governance/) �?L2标准�?01_policies/) �?L3架构�?02_enterprise/) �?L4域级�?各XX_*/) �?L5执行�?scripts/src) |
| R24 | 横向治理三条主线 | **当前结论**：政策控�?00_governance/) + 风险监控(17_risk/) + 记忆沉淀(08_ai_engineering/memory-and-context/) |
| R25 | 记忆系统的治理定�?| **当前结论**：记忆系统不是独立治理域，而是AI工程�?08/)的核心能力；治理政策(00/)定义规则，AI工程�?08/)实现能力 |
| R26 | 采用单一 frontmatter schema + 分阶段必填闸�?| **当前结论**：所有文档共用完�?schema，不�?`status` 对应不同必填集；取代 v1 �?沙盒�?正式�?双轨。落地：ADR-0002、`discussion-document-standard.md` v2.0.0 |
| R27 | ADR canonical �?= `02_enterprise_architecture/adr/`；草稿区 = workspace | **当前结论**：正�?ADR �?canonical 域；草稿�?`adr-drafts/`，拍板后搬家。落地：ADR-0001 隐含条款、`adr/README.md` |
| R28 | `doc_type` �?`module_id` 必须规范�?| **当前结论**：`doc_type` 采用 15 项受控词表；`module_id` 统一 `<DOMAIN>-<TYPE>-<NNN>` 格式（ADR 保留 `ADR-NNNN` 短格式）。落地：`discussion-document-standard.md` v2.0.0 §3/§4 |
| R29 | Superseded �?append-only 字段表示，禁止删除线；taskbook 状态用 `[ ]/[/]/[x]/[~]` 四符�?| **当前结论**：machine-readable 优先于视觉效果；所有失效内容保留原�?+ 状态字段。落地：标准 v2.0.0 §6.2 / §8 |
| R30 | 文档分类�?4 类扩展到 8 类机构完整图�?| **当前结论**：新�?ADR / roadmap / risk-register / session-log 四类；明�?ADR / rationale-log / Decision Memory Index 三者边界。落地：`document-triage-guide.md` v2.0.0 §1/§1.2 |
| R31 | strategic_decision 不独立成层，移入 l05_portfolio_construction/strategic/ | **当前结论�?026-04-18 会话 12 锁定�?*：业�?4 种主流模式扫描后采纳 BlackRock Aladdin 模式（P1）。strategic asset allocation 本质�?portfolio construction 的长周期版本，业界没有任何顶级机构把它列为独立顶层。原 `l11_strategic_decision` 整层删除，功能下沉为 `l05/strategic/` 子模块；未来�?`l05/tactical/` 并列。AI Operator 自然落到 `l05/_ai_operator/`（OQ-063 C-1 已预留）。落地：本日�?Stage 15 + OQ-073 closed；ADR-DRAFT-0009 + 03-AA + src/ 物理代码待架构终局后同步�?|
| R32 | l10 命名采用 `l10_compliance`，不�?`governance` �?`governance_compliance` | **当前结论�?026-04-18 会话 12 锁定�?*：业界顶级机构（Goldman/Citadel/Two Sigma/BlackRock/JPM/Bloomberg AIM）的 L10 层名绝大多数�?`compliance`。代码层承载的是硬合规约束的运行时检查（OPA 政策、订单合规、报告生成），用 compliance 最准；governance 内容（IPS/IC 决议/AI 自治组织规则/39 治理系统/文件治理 7 层）属于 docs/07_governance_and_compliance/META_GOVERNANCE/ + scripts/governance/，不�?L10 代码层。与 OQ-070 全球扩展规划完美契合（policies/cn_a_share/ / eu_mifid2/ 全部�?compliance 政策）。落地：本日�?Stage 15 + OQ-073 closed；ADR-DRAFT-0009 + 03-AA + src/ 物理代码待架构终局后同步�?|
| R33 | L12 命名最终锁定为 `l12_system_telemetry`（Closes OQ-030�?| **当前结论�?026-04-19 S14 Phase 1 锁定�?*：`system_telemetry` �?`observability` 更精确——强�?结构化指标流�?AI �?（机器消�?metrics/logs/traces），�?L07 给人看的业务报表明确区分。`observability` 是工程文化哲学概念不适合作代码层名。对�?`zephyr-src-gap-analysis.pdf` 原始分析文档命名。落地：`03-AA.md` v1.7.2 §4.1 `l12_system_telemetry/` 完整子模块清�?+ rationale 注释。OQ-030 closed�?|
| R34 | 14 层架构对标业界顶级机构，足够，不新增顶层（Closes OQ-068�?| **当前结论�?026-04-19 S14 Phase 1 锁定�?*：Goldman Sachs（~12�?4 层）/ JPMorgan（~10�?3 层）/ Two Sigma（~12�?4 层）/ Citadel（~8�?2 层）/ BlackRock Aladdin（~14 层）五家顶级机构对标结果：核心价值链覆盖�?100%，横向支撑层覆盖�?100%，L11/L12/L13 �?AI 时代先行层（Two Sigma/BlackRock 已有，JPM/Citadel 追赶中）。专业机构通过"子模块扩�?处理细分需求（Citadel 案例），不增加顶层�?4 层架构正确，不需要新增。落地：`03-AA.md` v1.7.0 附录 A 完整对标表格。OQ-068 closed�?|
| R35 | meta_strategy 归属 `l05/meta_router/`，不新建 l15 层（Closes OQ-023，N11�?| **当前结论�?026-04-19 S14 Phase 1 锁定�?*：meta_strategy（元策略路由）本质是 portfolio construction 的高阶形态——从策略池选取并加权组合，�?`StrategyRegistry` / `optimization/` / `rebalancing/` 三重耦合，归�?L05 最优。新�?l15 层会产生 15 层架构（超出业界惯例），且跨层耦合变重。`diversity_gatekeeper` 同归 `l05/meta_router/`（OQ-031）。AI Operator 自然�?`l05/_ai_operator/`（OQ-063 C-1 预留）。落地：`03-AA.md` v1.7.1 §4.1 L05 `meta_router/` 子模块说明。OQ-023 closed�?|
| R36 | Data Architecture 独立成视图（v1.0.0 新建，非�?IA 迁移�?| **当前结论�?026-04-19 S14 Phase 2 G1 锁定�?*：TOGAF 8 视图覆盖度补齐，DA �?IA 平级而非合并。经�?02-IA v1.1.0 全文不含业务数据对象（IA 纯讲 docs/ 抽屉与文档生命周期），DA 此前缺位——本次为新建非迁移。方�?A（留白）/ B（并�?IA）均被否决（理由：TOGAF 标准冲突 + IA SRP 违反）。视图含 19 条数据实�?+ 三维分类 + PIT 三字段铁律（`asof_date`/`ts_ingest`/`vendor_release_ts`�? �?Survivorship 查询契约 + 三层血缘模型（Schema/Pipeline/Instance，对�?OpenLineage�? MDM 三件�?bitemporal + 五类数据质量断言（PIT/Survivorship/Lineage 自研、其余用 Great Expectations/Soda�? 保留归档矩阵 + §10 �?IA/AA/TA 严格边界。落地：`05-data-architecture.md` v1.0.0 + `target-architecture/README.md` v1.2.0 文档清单更新。R 编号本应�?R33（任务指令），但 R33 已被 L12 命名占用，按"永不复用"约定改为 R36�?|
| R37 | Integration Architecture 独立成视图（v1.0.0 新建�?| **当前结论�?026-04-19 S14 Phase 2 G3 锁定�?*：TOGAF 8 视图补齐�?7 个维度。差距分析（cda60b89 #16）判定集成架�?🟡 只有 catalog 没有 view，接口语义没有叙事层"。本次新建叙事视图，�?catalogs/integration-catalog.md（数据层）互补。视图含 6 种集成风格分析（Batch/Streaming/Request-Reply/Event-Driven/File-based/Shared-DB�? 当前采用情况 + 内外部集成拓扑（Mermaid�? 接口契约版本管理（Semantic Versioning�? Breaking Change 流程 + 废弃政策 + ACL 策略（引�?03-AA §4.1 J5 已落盘的 L00 connectors/ 设计�? Event Backbone 占位（含候选技术方案对比）+ §8 视图关系图。落地：`07-integration-architecture.md` v1.0.0�?|
| R38 | Security Architecture 建立 skeleton 骨架（v0.1.0），暂不展开实质内容 | **当前结论�?026-04-19 S14 Phase 2 G2 锁定�?*：差距分析（cda60b89 #16）判定安全架�?�?仅占位，严重——监管合规前不可能通过审计"。但当前阶段（单人开发、无真实资金、无外部用户）不具备完整展开必要条件，过度设计产生虚假安全感。方案选择：建�?skeleton 占位（保�?TOGAF 8 视图体系完整），§8 �?8 条明确激活触发条件（接入真实券商 API / 接入 KYC 数据 / 多人协作 / 对外暴露 API / 生产环境部署 / 数据订阅合同 / 监管合规审查 / AI Agent 系统级权限）。激活前禁止向视图添加实质性内容（防污染架构一致性）。落地：`06-security-architecture.md` v0.1.0，status: skeleton�?|
| R39 | Operations Architecture 建立 skeleton 骨架（v0.1.0），暂不展开实质 Runbook | **当前结论�?026-04-19 S14 Phase 2 G4 锁定�?*：差距分析（cda60b89 #16）判定运维架�?🟡 04-TA.md §3 占位——运维人员无法从架构图推�?SRE 动作"。与 04-TA §6 边界明确�?4-TA §6 = 部署图（物理节点 how），本视�?= 运维全景（生命周�?流程+角色 what）。当前无生产环境、无守护进程，写详细 Runbook 无法演练形同虚设，故建立 skeleton�? 个运维域总表（D1-D8：部�?监控/备份/灾备/变更/事件/容量/成本�? §9 Runbook Catalog 11 条占�?+ §10 Activation Triggers 8 条。落地：`08-operations-architecture.md` v0.1.0，status: skeleton�?|
| R40 | README.md v1.3.0 收口，TOGAF 8 视图体系完整登记 | **当前结论�?026-04-19 S14 Phase 2 批次 A 收口�?*：TOGAF 8 视图（BA/IA/DA/AA/TA/SEC/INTEG/OPS）全部在 target-architecture/ 中有对应文档�?6-08 �?skeleton，余�?active）。README 升级�?v1.3.0：�? 文档清单新增 06/07/08 三行（标�?status·version·日期）；§3 推荐阅读顺序更新（完整路�?00�?1�?2�?5�?3�?7�?4�?6�?8，新�?Security/SRE/Data Engineer 路径）；§4 视图依赖图升级为 Mermaid flowchart（含 INTEG→SEC/OPS 依赖线）；新�?§4bis Skeleton 视图说明（为什�?skeleton + 何时激�?+ 为什么现在建空骨架）。本次是批次 A 总收口，阶段 2 五张视图�?.1-2.5）全部就位。落地：`target-architecture/README.md` v1.3.0�?|
| R41 | 01-BA §2 Stakeholder RACI Matrix 升级（H4，单�?AI 协同显式化） | **当前结论�?026-04-19 S14 Phase 2 批次 B H4 锁定�?*：差距分析（cda60b89）要�?Stakeholder 不能�?4 行、必�?8-12 �?+ RACI 责任矩阵"。升级方案：Stakeholder �?4 行扩展为 12 行（S1 Architect / S2 Quant / S3 Trader / S4 Risk / S5 Compliance / S6 Data / S7 SRE / S8 AI collab / S9 AI Operators 预留 / S10 Vendor / S11 Partner / S12 Regulator），每行标注"当前阶段归属"以显式暴露人机合一现实。新�?§2.2 RACI 矩阵�?8 活动 × 12 Stakeholder，每行唯一 A �?TOGAF/PMI 铁律）覆盖架构决策→研究→因子→信号→组合→执行→风控→归因→数据→合规→运维全链。新�?§2.3 "单人+AI 协同" 5 条铁律（A 不可委托 / R 可渐进迁移到 AI Operator / AI collaborator 仅限 C / 七维度决策日�?/ 升级触发）。方�?A（只�?Stakeholder 表不�?RACI）被否决（TOGAF 要求 RACI �?BA 核心构件）；方案 B（RACI 独立�?catalogs/）被否决（BA 核心叙事不应外流）。未�?S9 AI Operators 激活后 A04/A06/A07/A08/A10/A11 �?R 列从 you 迁移�?S9，A 列永远不变。落地：`01-business-architecture.md` v1.1.0 §2.1-§2.4�?|
| R42 | 01-BA §4 Value Stream Map 升级（H1，精�?VSM 三维度） | **当前结论�?026-04-19 S14 Phase 2 批次 B H1 锁定�?*：原 §4 仅为 8 行纯文本链（"Market data �?Ingest �?... �?Feed back"），缺时间维�?/ 交接维度 / 浪费维度，TOGAF 判定�?VSM 缺位。升级方案：§4.1 Mermaid flowchart VSM�? 阶段 ①输�?�?②研究因�?�?③信�?�?④组�?�?⑤执�?�?⑥交易后 �?⑦反馈，10 节点含反馈回路虚�?+ 横向治理节点 + Handoff 橙色高亮）。�?.2 Stage-level 10 �?LT/PT/%C&A 指标表，时间单位为秒/分钟/小时/天（对齐 §5 NFR "Non-HFT，daily/hourly batch"定位，未来激�?intraday 高频时重写）。�?.3 识别 **5 个关�?Handoff**（HO-1 Vendor→湖 / HO-2 研究→生�?/ HO-3 信号→风�?/ HO-4 组合→券�?/ HO-5 成交→反馈），每个标契约 + 风险 + 治理手段（引�?03-AA H8 ACL / H10 幂等 / OQ-063 决策日志）。�?.4 按精益七大浪费识�?**6 个瓶�?浪费�?*（B1 vendor 窗口等待 / B2 回测排队 / B3 合规审批 / B4 因子重算 / B5 �?AI 协作往�?/ B6 信号失效 drift 监控缺失），每个�?deferred 改进方向（OSS Catalog X3 fallback / Airflow/Prefect 调度 / policy-as-code / L13 champion-challenger 等）。�?.5 保留横向治理链（00_governance / META_GOVERNANCE / 17_risk / 08_ai_engineering / 15_knowledge_base）。落地：`01-business-architecture.md` v1.1.0 §4.1-§4.5�?|
| R44 | 02-IA §9 `07_sre_and_platform_ops` �?deferred 升为 planned（K1�?| **当前结论�?026-04-19 S14 Phase 2 批次 C K1 锁定�?*：差距分析（cda60b89）判�?SRE 抽屉"�?deferred 且无激活条�?，但在批�?B（R43）中 SLO-6 已引�?`04-TA §10 Observability H14`，意味着 SRE 能力路径已规划，�?deferred �?planned roadmap 不符。K1 决定：`07_sre_and_platform_ops` �?`deferred` 升为 `planned`，新增三条激活条件（任一满足即激活）：① 接入真实券商 API（Broker API EXT-001 进入生产）；�?系统月可用性需�?>99.9%（SLO-6 触发）；�?�?Agent 并发协同 >3 个。保�?`06_security_and_identity` = deferred 不变（两者激活条件性质不同）。落地：`02-information-architecture.md` v1.1.0 �?v1.2.0 §9�?|
| R45 | 04-TA §6 Deployment Diagram 填充（H12，Phase 1 Mermaid �?+ Post-Activation 拓扑�?| **当前结论�?026-04-19 S14 Phase 2 批次 C H12 锁定�?*：差距分析（cda60b89）判�?�?§6 是占位符"，专业机构标�?Deployment Diagram（物理节点）。H12 填充方案：�?.1 Phase 1 单机本地拓扑 Mermaid 图（开发机 Windows �?Python Virtual Env + Git Hooks + 本地存储 + AI IDE；外部：行情数据�?券商网关/LLM/Feishu；远�?CI；标清网络边界表�?行出站规则）；�?.2 Post-Activation �?+ 多节点拓�?Mermaid 图（云端应用节点集群 + 数据存储节点 + OTel 可观测性节�?+ 调度节点�? Phase 1 vs Post-Activation 6 维度对比表；§6.3 抽屉状态表�?6_security deferred / 07_sre planned R44）；链接 `08-operations-architecture.md §1` 边界说明。落地：`04-technology-architecture.md` v1.1.0 �?v1.2.0 §6�?|
| R46 | 04-TA §9 Environment Matrix 新增（H13�? 环境 × 6 维度矩阵�?| **当前结论�?026-04-19 S14 Phase 2 批次 C H13 锁定�?*：差距分析（cda60b89）判�?�?没有环境矩阵"。H13 设计原则：环境分级而非独立系统，Dev/UAT/Staging/Prod 共用同一代码库，仅配置与数据源不同（ADR-0001 单一真源约束）�? 维度（数据源/LLM Provider/资金规模/监控等级/审批流程/回退策略）�?4 环境的矩阵覆盖所有关键决策点。新�?§9.3 环境晋级门禁（Dev→UAT→Staging→Prod 三道 Gate，每道标必须满足的可量化条件）。关键细节：Prod 资金规模 = 个人资本/单账�?不对外募资（BA §6 约束）；Staging 可用极小仓位�?Shadow Trading；Prod 监控�?SLO-6 可用�?99.9% + SLO-3 下单 p99 �?0s �?SLO 实时告警。落地：`04-technology-architecture.md` §9（原 §8 修订记录后移�?§11）�?|
| R47 | 04-TA §10 Observability Architecture 新增（H14，三支柱：Metrics/Logs/Traces�?| **当前结论�?026-04-19 S14 Phase 2 批次 C H14 锁定�?*：差距分析（cda60b89）判�?�?`07_sre` �?deferred，Observability 完全缺位"�?1-BA §5.2（R43）设置了 📌�?4-TA §10 的引用锚，本节为回填。三支柱设计�?1) **Metrics** �?业务指标（`zephyr_orders_total` / `zephyr_order_fill_rate` / `zephyr_pnl_daily` �?6 条，每条�?SLO 关联�? 技术指标（`zephyr_request_duration_seconds` / `zephyr_error_rate` / `zephyr_llm_tokens_total` / `zephyr_data_freshness_lag_seconds` 4 条，每条标告警阈值）+ 基础设施指标（CPU/内存/磁盘）；(2) **Logs** �?结构�?JSON 格式（含 trace_id / span_id 字段，支�?Logs-Traces 关联�? 三级体系（L1 App Log 30/90 �?/ L2 Audit Log append-only �? �?/ L3 Security Log 90 �?deferred�? 4 环境保留策略表；(3) **Traces** �?端到端链路（策略触发→L02→L03→L04→L05→L06→Broker API→L07�? �?Span�? 6 个关�?Span Attribute（zephyr.layer/strategy_id/signal_id/order_id/broker_id�? 3 场景采样策略（Dev 100% / Staging 20%+错误100% / Prod 尾部采样10%+异常100%）。本�?metric name 同步回填 01-BA §5.2 的所�?TODO 引用锚。落地：`04-technology-architecture.md` §10�?|
| R48 | 04-TA §10.4 OTel 集成方案（K7，Python SDK + Collector + Exporter + 采样�?| **当前结论�?026-04-19 S14 Phase 2 批次 C K7 锁定�?*：差距分析（cda60b89）和 profAlign�?9556ad0）均�?K7 OpenTelemetry 集成列为"open"待落盘项，与 H14 合并执行。设计决策：SDK = Python `opentelemetry-sdk` �?1.20（自�?instrumentation 覆盖 requests/logging/asyncio）；Collector 当前阶段 = 本地 Agent（与主进程同机，最简配置，零网络跳跃），Post-Activation = 独立 Gateway（支持尾部采样和流量控制），Sidecar 暂不适用（非容器化，Q5-5 激活后评估）；Exporter 对接 = Prometheus（指标）+ Grafana Tempo（Traces OTLP gRPC�? Loki（Logs HTTP push），Grafana 统一看板；采样配�?= 头部采样（Dev/UAT 100%�? 混合（Staging 20%+错误100%�? 尾部采样（Prod：`tailsampling` processor，decision_wait 10s，错误全保留 + 慢请�?>5s 全保�?+ 随机 10%）。提�?`otel_bootstrap.py` SDK 初始化参考代�?+ `otel-collector-config.yaml` + Docker Compose 可观测性栈参考配置。落地：`04-technology-architecture.md` §10.4�?|
| R43 | 01-BA §5 SLA/SLO/SLI 矩阵升级（H3�? 条量�?SLO + Observability 引用锚） | **当前结论�?026-04-19 S14 Phase 2 批次 B H3 锁定�?*：原 §5 仅为 7 行定�?NFR 表（"Latency / Availability / Auditability..."），量化完全缺失，TOGAF 与业界顶级机构（Goldman/Two Sigma/BlackRock）判定为硬缺陷。升级方案：§5.1 定�?NFR 保留 + 增加 Data Quality 一�?+ �?3 条边界原则（Non-HFT 定位 / 市场时段 vs 非市场时段分�?/ 可审�?�?可用性）。�?.2 SLO/SLI 矩阵 **8 行量化指�?*：SLO-1 Data Freshness（分�?bar p50/p95/p99 = 15s/60s/180s、日�?T+1 11:00�? SLO-2 Signal Gen（intraday p99 �?90s、EOD p95 �?10min�? SLO-3 Order Submit（p99 �?30s �?pre-trade risk �?1s�? SLO-4 Backtest TAT（常�?p95 �?30min、重�?p95 �?4h�? SLO-5 Factor Refresh（日�?EOD+90min、分�?5min 滚动�? SLO-6 Availability（市场时�?99.9%/�?= �?43.2min 停机，非市场时段 best-effort�? SLO-7 Data Quality（Completeness �?99.5% / Consistency �?99.9% / Fitness Function 100% pass�? SLO-Audit（ADR append-only 100% / AI 七维度日�?�?99%�? 容忍违约）。每条标 SLI 测量方法（ts 差�?/ OTel span / histogram / 断言 / hook�? 上报位置（�?�?04-TA §10 Observability H14 TODO 引用锚，批次 C 任务 5.3 完成后回填真�?metric name）。�?.3 SLA 现实说明（仅 iFinD 真合�?SLA，其�?internal；S11 合伙�?S12 监管激活后 internal SLO �?external SLA）。�?.4 4 条重写触发（L1 行情/组合 �?$10M / S11-S12 激�?/ 流式架构 / 连续 3 月未达标）。�?.5 与其他视图边界（DA §4-§8 / AA §9 H10 / TA §10 H14 / TA §11 H15）。落地：`01-business-architecture.md` v1.1.0 §5.1-§5.5�?|
| R56 | 03-AA §9 + src-domain/idempotency-design.md（H10 量化资金安全一级红线）| **当前结论�?026-04-19 S14 Phase 2 批次 D H10 锁定 �?量化红线�?*：订单重发不重复是量化系统生命线，分布式 + CAP 原理下无法严�?Exactly-Once�?*业界标准（Stripe/AWS/支付宝同款）= 接受 At-Least-Once + 幂等层等价实�?"Effectively Exactly-Once"**�?*Key 生成公式**：`SHA-256(strategy_id‖signal_id‖asof_ts‖instrument_id‖side‖target_qty‖target_price_hint‖nonce)` �?128-bit prefix�? 字段覆盖业务意图唯一性�?*双层存储**：Redis SETNX+TTL 热层�?10ms，TTL = 交易日结�?24h 覆盖跨夜�? append-only JSONL journal 冷层（RPO=0，对�?ADR-0002 + 04-TA §8.1 + §10.2）�?*broker 双保�?*：Idempotency Key 必须作为 client_order_id / FIX Tag 11 传入 broker�?*不支持此能力�?broker 不允许接入实�?*（选型硬约束）�?*Fail-Closed 降级**：Redis 故障 �?journal-only 模式（性能降不损正确性）；journal 写失�?�?**立即拒绝所有新订单**�?*绝不 fail-open**�?*异常处置 8 �?E1-E8**：重�?Key 命中 / broker 双保险触�?/ 降级期碰�?/ journal 失败 / hash 完整性违规（P0�? 跨日边界 / 部分成交重发（强制新 Key�? 取消重发（强制新 Key）�?*自检清单 4 �?20+ 断言**：单元测试（Key 确定�?+ SETNX 语义 + 降级正确性）/ 集成测试�?�?signal 重复 100 �?broker 只收 1 �?核心断言�? 生产前（broker 能力 + Redis 部署 + 磁盘监控 + 告警通道 + 人为故障演练�? 运行期（integrity_violation 日增=0 + stuck_pending EOD=0 + journal �?Redis 对账 + broker �?client_order_id 全量 diff）�?*方案 D 落地**：父视图 03-AA §9 承载**端到�?Mermaid 时序�?*�?0 行含三场景：正常首次 / Retry 去重 / Redis 降级 + broker 双保险，读者第一视觉入口无需跳转�? §9.1-§9.6 场景说明 + 关键参数�?+ 量化红线自检 10 项结论表（本节作�?2026-04-19 十项全通过），完整实现（Key 字段详解 / schema / At-Least-Once 推理 / 8 异常处置 / 20+ 自检断言 / metric / Trace）落 `by-domain/src-domain/idempotency-design.md` v1.0.0 design-brief（~250 行）�?*红线关系**：R56（本条）+ R55（L06 Retry 必过 Idempotency Guard，H9 铁律�? R50（DR §8.3.2 已挂单处置依�?Key 去重）三条强耦合，缺一则量化链路存在资金风险�?*父视图终点行�?957**（原预估 858，实�?+99 因时序图和自检表写得比预算更厚），**�?< 1000 阈�?*（缓�?43 行），方�?D 仍有效，OQ-072 条件 �?未触发。落地：`03-AA` §9�?123 行）+ `by-domain/src-domain/idempotency-design.md`（新建，~250 行）。|
| R55 | 03-AA §8 + src-domain/fault-tolerance-matrix.md（H9�? �?× 5 策略容错矩阵）| **当前结论�?026-04-19 S14 Phase 2 批次 D H9 锁定�?*：差距分析识�?03-AA �?Fault Tolerance 章节，专业机构容错策略是资金安全第二防线。H9 设计�? 层覆盖（**L00 数据�?/ L02 因子 / L04 风控 / L06 执行 / L09 沙盒**）�?5 策略（Circuit Breaker / Bulkhead / Retry / Timeout / Fallback）完整矩阵�?*OSS 复用选型**：pybreaker（无外部依赖�? tenacity（装饰器�?+ 指数退避）+ asyncio.Semaphore/ThreadPoolExecutor（原�?Bulkhead�? 原生 asyncio.wait_for（Timeout�? 自研 Fallback 策略模式�?*三条跨层铁律**�?1) **Fail-Fast vs Fail-Safe vs Fail-Closed 分层决策**—�?L00/L02 = Fail-Safe 用降级数据（stale_warning）；**L04/L06 = Fail-Closed 拒绝优于放行**（资金安全铁律，pre-trade 检查超�?= 拒绝）；L09 = Fail-Reported 透明报告�?2) 每层独立 CB + 隔离线程池，故障不跨层级联（L00 Vendor 故障不拖�?L02 CB，L02 不拖�?L05 优化器）�?3) **L06 Retry 必须经过 Idempotency Guard**——任何故障转�?重试路径必须先检查幂�?Key 避免重复下单（H9 �?H10 强耦合铁律）�?*方案 D 落地**：父视图 03-AA §8 保留 5×5 压缩矩阵表（每格 �? 行）+ 三条铁律 + 6 �?metric 清单 + 五处边界引用（共 ~45 行，略超计划 15 行但表格结构合理，可接受）；完整实现（阈值详�?/ OSS 库参�?/ SLO 关联 / 失败业务影响 / §3 级联故障 5 场景预防 / §4 metric 6 �?+ Trace Attribute / §5 演练验证 / §6 八处边界）落 `by-domain/src-domain/fault-tolerance-matrix.md` v1.0.0 design-brief（~200 行）�?*级联故障场景�?*�? 个典型场景（Vendor 大面积故�?/ LLM 限流 / Pre-Trade �?/ Broker 故障 / Redis 故障�? 对应预防措施，首次正式入档。落地：`03-AA` §8�?45 行）+ `by-domain/src-domain/fault-tolerance-matrix.md`（新建，~200 行）。|
| R54 | 03-AA §3.5 + diagrams/c4-l3-*.mmd × 3（H5，C4 Level 3 三张关键层组件图）| **当前结论�?026-04-19 S14 Phase 2 批次 D H5 锁定�?*：C4 Model 原则要求 L1（系统上下文）→ L2（容器）�?L3（组件）�?L4（代码）递进。当�?L1/L2 .mmd 已存�?+ §3.3 容器图已就位，H5 �?L3 三张图�?*选层标准**：业务风险最高（L00 数据源头 + L06 资金执行）或架构复杂度最高（L11 ML 平台），其他层（L02/L05/L07/L08/L10）由 §4.4 扩展点表覆盖已足够，不单独绘制�?*产出**�?1) `c4-l3-l00-data-source.mmd`：Vendor Registry + ACL 三段（raw_client/mapper/facade�? 三家 Vendor（iFinD primary / Tushare Pro fallback 1 / AKShare fallback 2�? failover_policy.yaml + 原始缓存 + L12 telemetry 边界�?2) `c4-l3-l11-ml-platform.mmd`（⚠�?文件名历史保留，内容对应 L11 ML Platform）：Feature Store + PIT Query + Training Pipeline �?Model Registry �?Inference Engine + Drift Monitor + Shadow/Canary + ai_operator 预留口子（OQ-063 P4）；(3) `c4-l3-l06-trade-execution.mmd`：IBroker Interface + OMS + **Idempotency Guard（H10 红线关联�?* + SOR + Pre-Trade Risk Proxy + adapters（Simulation/Real Broker�? Fill Handler + Position Tracker + audit journal（RPO=0�? Redis idempotency 热层�?*03-AA §3.5 章节结构**：�?.5.1 图清单与文件映射�?/ §3.5.2 三视角阅读路径（数据入口 / 资金安全 / ML 生命周期�? §3.5.3 命名说明（`l04-ml-model` 文件名保留任务档案对齐，内容实际�?L11，未来可改名）。所�?L3 图采�?`C4Component` Mermaid 语法，风格对齐现�?L1/L2�?*文件命名历史遗留**正式登记�?§3.5.3（R54），避免未来读者困�?L04 �?ML 还是风控"。落地：`03-AA` §3.5�?27 行）+ 3 �?`.mmd` 文件（合�?~150 �?Mermaid）。|
| R53 | 03-AA §4.5 + src-domain/ocp-extension-points.md（H8，ACL 三段结构 + Vendor Registry + 故障转移）| **当前结论�?026-04-19 S14 Phase 2 批次 D H8 锁定�?*：批�?C �?§4.1 L00 已埋注释"后续扩展（H8 阶段）：connectors/ ACL 将在阶段 6.1 H8 进一步深化——引�?Vendor Registry 统一管理、按资产类别�?namespace、支持多 Vendor 混合接入与故障转�?（J5 / R33）。H8 在保留该决策的前提下新增三项能力�?1) **ACL 三段结构锁定**：每�?vendor 目录必须遵循 `raw_client.py`（原�?SDK 包装�? `mapper.py`（外部模型→canonical schema 翻译，对�?05-DA §5 PIT 三字�?asof_date/ts_ingest/vendor_release_ts�? `facade.py`（实�?`IDataSource` �?L01+ 暴露）；(2) **Vendor Registry 契约**：`vendor_registry.py` �?`VendorMeta` 数据类（vendor_id / asset_classes / jurisdictions / data_domains / priority / sla_tier / cost_per_month / health_status�? `register/resolve/healthcheck_all` 三方法；(3) **�?asset_class/jurisdiction �?namespace** = `connectors/{asset_class}/{country}_{vendor}/`（对�?OQ-070 全球�?+ OQ-071 P0 四条契约），不允许跨 jurisdiction 共享 mapper�?4) **�?Vendor 故障转移**：`failover_policy.yaml` �?circuit_breaker（失败率阈�?0.5 / 窗口 300s / OPEN 60s / 退避上�?960s�? fallback 链（priority 0 �?1 �?2�? `data_quality_degraded` 标志，驱�?L04 风控降保守档�?/ L06 执行保守策略�?*方案 D 落地**：父视图 03-AA §4.5 保留 15 行摘要（4 行能力表 + 关键约束 + 3 处视图边界）+ §4.1 L00 R33/J5 决策注释零改动；完整实现蓝图（~260 行）�?`by-domain/src-domain/ocp-extension-points.md` v1.0.0（doc_type: design-brief）。同步升�?`by-domain/src-domain/README.md` v0.1.0→v1.0.0 active�?*OQ-072 双轨制首次实质兑�?*），§3 承载内容清单首行"已就�?v1.0.0"+ §5 design-brief 类型约定锁定（比 ADR 轻、比正文厚、可迭代�? §6 整体下沉三条件说明。落地：`03-AA` §4.5�?23 行）/ `by-domain/src-domain/ocp-extension-points.md`（新建，~260 行）/ `by-domain/src-domain/README.md`（升级到 v1.0.0）。|
| R52 | 04-TA §12 Cost Architecture 新增（H17，三分类 + 单次操作成本 + 月预警三�?+ Cursor/Runtime 边界）| **当前结论�?026-04-19 S14 Phase 2 批次 D H17 锁定�?*：专业机构标�?Cost Architecture 未在 04-TA 登记，H17 新增。�?2.1 **三分类月度预算模�?*：基础设施 ~¥300 / LLM&AI ~¥1500（含 Cursor 订阅 $20-40 + Runtime API + 便宜模型爆搜�? 数据订阅 ~¥2000（iFinD 唯一真合�?SLA），合计 ~¥3800�?*Phase 1 目标 �?¥3000**，预�?¥3500�?16%），强制降级 ¥4500�?50%）。�?2.2 单次操作成本模型 8 行（常规回测 $0.2、重度回�?$1、实�?EOD 信号 $0.03、归�?$0.07、Opus Review $0.5、Kimi 夜间爆搜 $2.1、数据订阅固�?$280、Cursor 订阅固定 $30），月成本汇总按频率 × 单次。�?2.3 预警机制五档（软 ¥3000 / 预警 ¥3500 / 强制 ¥4500 / 日峰 ¥500 / 单次 LLM >$5�? 对接 §10.1 metric。�?2.4 7 条优化策略（LLM 分级路由 / 订阅降级 / 闲时回收 / Cursor 最大化 / 因子缓存 / 回测夜间 / Prompt 压缩）。�?2.5 **Cursor vs Runtime API 边界决策口诀**：人在键盘前 = Cursor�?0 边际，架�?代码审查/文档默认），机器独立决策 = Runtime API（AI Operator / 夜间批处�?/ webhook 必须）。�?2.6 5 条成本重建触发条件（T1 真实资金 / T2 外部 LP / T3 �? �?AI Operator / T4 跨境 jurisdiction / T5 连续 3 月超 150%）。�?2.7 �?§11/§5.4/§9/§10.1/OQ-067 边界引用。落地：`04-technology-architecture.md` §12�?~70 行）�?|
| R51 | 04-TA §11 Capacity Model 新增（H16�?4 层资源预�?+ LLM/数据流量 + 伸缩触发）| **当前结论�?026-04-19 S14 Phase 2 批次 D H16 锁定�?*：差距分析识�?04-TA �?Capacity Planning，专业机构标配按层分解资源预算。H16 设计：�?1.1 **14 �?× 5 列资源预算矩�?*（CPU core·h/�?/ Memory 峰�?GB / Storage 年增 GB / IOPS 峰�?/ 备注），合计峰�?~20-25 core·h/�?+ ~12GB 占用（含 OS buffer 24GB�? 155GB/�?+ 1500 ops/s，对应建议硬�?16-core/32GB/500GB SSD（Phase 1 单机参考值，Post-Activation 多节点近似线性放大）。�?1.1.1 GPU 预算（当�?0，触发后 1× RTX 4090 class 覆盖 Phase 2）。�?1.2 高峰时段 4 档（开盘前 CPU �?/ 盘中 IOPS+网络 / 收盘�?CPU+磁盘 / 夜间弹性），每档标扩容触发。�?1.3 LLM Token 预算 6 行（Cursor 订阅固定 $20-40 / Runtime API 现在 $5 / AI Operator 未来 $100-200 / 便宜模型爆搜 $20-50 / Feishu bot $5 / 月度总上�?~30M token / $200），配降级顺序（Opus �?Sonnet �?Haiku/Kimi �?Qwen-local）。�?1.4 数据订阅流量预算（iFinD ¥2000/月唯一合同 + Tushare planned ¥500 + AKShare $0 + Broker L2 tick Post-Activation），Phase 1 合计 ~¥2000/月。�?1.5 **8 条伸缩触发条�?*（CPU 月均 >60% / Memory >70% / Storage >70% / Backtest TAT >30min 连续 7 �?/ LLM 月成�?>$200 / 订阅到合�?90% / 订单 QPS >5 / AI Operator �? 层激�?�?GPU）。�?1.6 �?01-BA §5.2 SLO-4 / 04-TA §9/§10.1 / 04-TA §8 / 05-DA §9 五处边界。落地：`04-technology-architecture.md` §11�?~100 行）�?|
| R50 | 04-TA §8 DR/BCP 填充（H15，RTO/RPO 资产分级 + 三级灾备 + 量化特殊场景）| **当前结论�?026-04-19 S14 Phase 2 批次 D H15 锁定�?*：差距分析判�?"§8 仅为占位�?，专业机构标�?DR/BCP 明确 RTO/RPO。H15 填充方案：�?.1 **7 �?RTO/RPO 分层矩阵** 按资产级别分类（🔴 金融资金 = 订单+成交 RTO�?min/RPO=0 / 🔴 合规审计 = L2 Audit Log RTO�?5min/RPO=0 / 🟡 业务核心 = L00-L05 RTO�?5-30min/RPO�?-15min / 🟢 离线分析 = L07/L12/L13 RTO�?h/RPO�?h / 🟢 可丢�?= 中间缓存 无备份），按市场时段 vs 非市场时段双�?RTO（对�?01-BA §5.1 边界原则）。�?.2 三级灾备 Tier（热�?N+1 / 温备数据同步 / 冷备快照恢复），工具选型复用 PostgreSQL WAL + Parquet 版本�?+ Git + Loki remote_write（never reinvent）。�?.3 **量化特殊场景**：交易日 vs 非交易日 6 维度对比 / 已挂单处置流�?5 步（broker GetOrderStatus �?audit journal 对照 �?分类 a/b/c/d �?决策写入 audit �?T+1 对账，依�?03-AA §9 H10 幂等�? 数据�?不可丢边�?6 类。�?.4 Runbook 引用 08-OPS（当�?skeleton�? 当前阶段季度演练 �?Post-Activation 月度自动演练。�?.5 明确�?01-BA §5.1/§5.2 SLO-6/SLO-Audit / 03-AA §9 H10 / 04-TA §9/§10.2 / 08-OPS §9 七处引用边界。落地：`04-technology-architecture.md` §8�? ~107 行）。|
| R63 | 00-overview.md §8 Architecture Runway Index 总览（S6，批�?G�?| **当前结论�?026-04-19 S14 Phase 2 批次 G S6 锁定�?*：Architecture Runway 各视图章节（S2-S5）就位后，需要一个总览入口让读者能快速导�?37 条预留通道并理解激活机制。S6 �?`00-overview.md` 末尾追加 §8：�?.1 四视�?Runway 章节快速导航表（视�?章节编号/条目�?主要覆盖域）；�?.2 激活监控机制（何时 Review：季度例�?重大里程�?架构重大变更三触发类型；如何判断激活：5 步流程——检查触发条�?更新 activation_status/人工拍板/写入 ADR/条目归档；不应激活的信号：触发条件未满足/ROI 不足/底层未稳定）。`00-overview.md` v1.0.0 �?v1.1.0�?|
| R62 | 04-TA.md §14 Architecture Runway 预留通道（S5�? 条基础设施/技术栈�?P3�?| **当前结论�?026-04-19 S14 Phase 2 批次 G S5 锁定�?*：筛�?P3-blueprint-index �?`target_layer` �?`l01_infrastructure` 或技术栈类条�?7 条：RW-TA-01（分布式计算，P3-INF-003�? RW-TA-02（云原生迁移，P3-INF-004�? RW-TA-03（边缘计算，P3-INF-005�? RW-TA-04（多云部署，P3-INF-006�? RW-TA-05（区块链审计链，P3-GOV-003�? RW-TA-06（企业级 SSO，P3-INF-008�? RW-TA-07（跨机构合规技术栈，P3-GOV-001）。每条对接到现有 §6 Deployment Diagram / §8 DR/BCP / §10 Observability / §11 Capacity / technology-landscape 的具体挂载点。`04-technology-architecture.md` v1.3.0 �?v1.4.0�?|
| R61 | 03-AA.md §11 Architecture Runway 预留通道（S4�?2 条应用组件类 P3，按 6 层分组） | **当前结论�?026-04-19 S14 Phase 2 批次 G S4 锁定�?*：筛�?P3-blueprint-index �?`target_layer` �?l02-l11 的应用组件类条目 22 条，按架构层二级分组：�?1.1 l02 Alpha Factor�? 条：在线学习/因果推断/新闻事件/宏观因子�? §11.2 l03 Signal Generation�? 条：高频/跨资产套�?统计套利/期权/加密货币�? §11.3 l04/l11 ML Platform�?0 条：RL再平�?AutoML/GNN/联邦学习/迁移学习/生成模型/元学�?Transformer因子/贝叶斯优�?AI解释引擎�? §11.4 l07 Post-Trade�? 条：机构级报告）/ §11.5 l08 Human-AI Interface�? 条：NL策略/i18n/离线支持�? §11.6 l09 Research�? 条：AI研究自动�?量子计算/开源贡献）。每条标�?`§4.1` 精确挂载子目录路径。`03-application-architecture.md` v1.8.0 �?v1.9.0�?|
| R60 | 02-IA.md §11 Architecture Runway 预留通道（S3�? 条数�?信息对象�?P3�?| **当前结论�?026-04-19 S14 Phase 2 批次 G S3 锁定�?*：筛�?P3-blueprint-index �?`target_layer` �?`l02_alpha_factor`（P3-AI-018 多模态因子）/ `l09_research_innovation`（P3-AI-015 知识图谱自动构建�? `l02_alpha_factor`（P3-STR-008 ESG 因子）的信息层相关条�?3 条：RW-IA-01（多模态因子信息对象，挂载 §3 drawer 10_research_and_factor_lab/ 子目录扩展）/ RW-IA-02（ESG 因子信息对象，挂�?esg-factors/ 新增子目录规划）/ RW-IA-03（知识图谱自动构建，挂载 15_knowledge_base/09_knowledge_graph/ 新增子目录规�?+ §8 元数据标准扩展）。`02-information-architecture.md` v1.2.0 �?v1.3.0�?|
| R59 | 01-BA.md §8 Architecture Runway 预留通道（S2�? 条业务侧/战略�?P3�?| **当前结论�?026-04-19 S14 Phase 2 批次 G S2 锁定�?*：筛�?P3-blueprint-index �?`target_layer` �?`business` �?`l11_strategic_decision` 的条�?5 条：RW-BA-01（投委会支持工具，P3-STR-002�? RW-BA-02（多基金经理协调，P3-STR-011�? RW-BA-03（系统化全球宏观策略，P3-STR-012�? RW-BA-04（战略联盟框架，P3-GOV-004�? RW-BA-05（机构级报告体系，P3-STR-003）。每条标明挂载到 §2 Stakeholder / §4 Value Stream / §5.3 SLA / §6 Business Constraints 的具体位置。`01-business-architecture.md` v1.1.0 �?v1.2.0�?|
| R57 | business-capability-map.md 增列 Maturity + Investment Intensity（H2�?| **当前结论�?026-04-19 S14 Phase 2 批次 E H2 锁定�?*：差距分析（cda60b89 #16）判�?`catalogs/business-capability-map.md` 缺少成熟度维度，专业机构能力地图必须标注成熟度与投资优先级以支持资源分配决策（TOGAF BA 标配构件）。H2 设计�?1) **Maturity L1-L5 定义**——L1 Concept（概念阶段）/ L2 Design（架构设计完成，尚未实现�? L3 Prototype（有骨架代码，未达生产就绪）/ L4 Operational（生产就绪，仍在演化�? L5 Optimized（充分运行，SLO 全达标）�?2) **Investment Intensity 四档**——Low（维护性）/ Medium（定期迭代，Sonnet 级）/ High（Opus 深度设计�? Critical（阻塞其他能力）�?3) **10 �?Capability 填充结果**——C01 Data Acq = L2/Critical（ACL+VendorRegistry 设计完成但代码未实现，阻塞全链路�? C02 Research = L2/Critical（依�?C01，Alpha 核心�? C03 ML Platform = L1/High（仅层定义，Q5-3 ADR 待触发）/ C04 Strategy = L2/Critical（meta_router 锁定，portfolio 优化待实现）/ C05 Trade Exec = L2/High（BrokerInterface+幂等设计完成，实现待做）/ C06 Post-Trade = L1/Medium（仅层定义，依赖 C05 首批成交�? C07 AI Ops = L3/High（Feishu/Cursor 协作已运行，agent ops 待完善）/ C08 Risk = L2/Critical（H9 容错 + Pre-trade Gate 设计完成，代码层待实现）/ C09 Compliance = L1/Low（deferred，个人阶段不激活）/ C10 Knowledge = L3/Medium（KMS 10 层目录已建，持续填充中）。落地：`business-capability-map.md` v1.0.0 �?v1.1.0（新�?Maturity / Investment Intensity / 判断理由三列，新增等级定义框）�?|
| R58 | catalogs/technology-landscape.md 新建（R4，Tech Radar 风格替代 technology-standards.md�?| **当前结论�?026-04-19 S14 Phase 2 批次 E R4 锁定�?*：差距分析（cda60b89）判定现�?`technology-standards.md` 格式简单（仅三表：已确�?待定/延迟），�?Radar 分类与活文档机制，无法支撑开源选型决策与刷新管理。R4 设计�?1) **ThoughtWorks Tech Radar 四象�?*：Adopt（强烈推荐）/ Trial（低风险引入�? Assess（持续关注）/ Hold（谨慎对待）+ Build（自研）第五类；(2) **条目覆盖**：�? Adopt 12 条（Cursor/Trae IDE / Python / Markdown/Mermaid/Git / doc_guard / AKShare / tenacity/pybreaker / OTel SDK�? §2 Trial 9 条（Tushare/DuckDB/Parquet / Claude Runtime API / Grafana 四件�?Loki+Tempo+Prometheus+Dashboard / Redis�? §3 Assess 10 条（Prefect/Airflow / PyTorch/sklearn / PostgreSQL/ClickHouse / LiteLLM / OTel Gateway / Wind / TypeScript�? §4 Hold 6 条（LLM Gateway / Docker/K8s / Kafka / Compliance SaaS / SIEM / OpenRouter�? §5 Build 6 条（doc_guard / BrokerInterface+OMS / VendorRegistry+ACL / 幂等Key引擎 / OTel Bootstrap / Architecture Fitness Functions�? §6 数据源专�?5 �?/ §7 LLM Provider 专题 4 条；(3) **活文档机�?*：�? 刷新记录，每 3 个月刷新一次，刷新触发条件 3 条（季度例行 / 重大技术决�?/ 重大安全问题）；(4) **source of truth 关系**：本文件�?source of truth，`technology-standards.md` 标记 `superseded_by`，添加重定向注释。落地：新建 `catalogs/technology-landscape.md` v1.0.0（EA-ARCH-CATALOG-006�? `technology-standards.md` frontmatter `superseded_by` 更新 + 文件顶部重定向说明�?|
| R59-F | catalogs/domain-event-catalog.md 新建（H6�?2 领域事件 6 �?+ 量化红线补充事件；原编号 R59�?026-04-19 批次 H �?`-F` 后缀以区分批�?G 同号 R59）| **当前结论�?026-04-19 S14 Phase 2 批次 F H6 锁定�?*：差距分析（cda60b89）与 professional-alignment-taskbook 指出 catalogs/ �?Domain Event Catalog，DDD 事件风暴驱动开发的语义基石未入档。H6 设计�?1) **覆盖 6 �?22 事件**——Research 3（FactorResearched/BacktestCompleted/ModelValidated�? Signal 3（SignalGenerated/SignalRevoked/SignalExpired�? Portfolio 2（PortfolioRebalanced/PositionLimitBreached�? Execution 7（OrderSubmitted/OrderAccepted/OrderRejected/FillReceived/OrderCancelled/OrderExpired + **OrderIdempotencyBlocked 量化红线补充**�? Risk 4（RiskLimitBreached/MarginCalled/DrawdownAlerted + **PreTradeRejected H9 Fail-Closed 补充**�? Ops 3（DataIngestionFailed/ModelDriftDetected/SystemDegraded），超出 20 条指令要求；(2) **当前运行时声�?*——单进程架构 + 进程内回调分发（非消息总线），Catalog 定义的是领域语义单元与传输层解耦，未来触发 Pub/Sub 的升级路�?= 多独立进程（Phase 2 Redis Streams/NATS）或跨机房容灾（Phase 3 Kafka），�?Catalog 定义不随总线引入而改动只改分发通道�?3) **DDD 命名铁律**——过去时动词 + 名词在前 + 不含技术动�?+ 仅登记已发生事实（反例：SubmitOrder �?Command / FillInsertedToDB 是技术动�?/ OrderShouldBeRejected 是预测）�?4) **事件 vs 数据契约边界**——Event 登记业务事实单元不可�?/ Contract 登记 DTO 形状�?schema_version 演进，Event payload `�?contract:XXX` 引用 interface-contracts 字段，`�?entity:EXX` 引用 05-DA Entity�?5) **频率�?4 �?*（L1 低频 <10/�?/ L2 中频 10-100/�?/ L3 高频 1-10/分钟 / L4 突发取决触发），对齐 01-BA §5.1 Non-HFT 定位（最细事件频�?每分钟若干次"，不出现毫秒级事件）�?6) **每条事件 11 字段结构化描�?*——语�?Publisher/Subscribers/Payload Schema/频率�?上游 Aggregate/因果前置/因果后继/审计强度�?7) **§8 事件因果�?4 场景**——happy path / 幂等保护（H10 红线，E-EX-07 �?Idempotency Guard SETNX=0 触发�? 风控熔断（H9 Fail-Closed 铁律，E-RK-04 �?Pre-Trade checker 超时/异常/命中触发�? Vendor 降级（E-OP-01 �?持续未恢复升�?E-OP-03）；(8) **§9 Payload 复用策略**——事�?payload 优先引用 interface-contracts 已定义字段不重复定义（例：FillReceived 全字段引�?Fill Contract），事件额外字段（`*_id` 自身 UUID v7 / `*_ts` UTC ns / lineage_root / severity / reason_text）明确命名约定，版本管理"只追加不删除 + 事件名不可变（命名即契约�?。落地：`catalogs/domain-event-catalog.md` v1.0.0（module_id: EA-ARCH-CATALOG-007，~380 行）。|
| R60-F | catalogs/ddd-aggregates.md 新建（H7�? Aggregate Root + 6 Entity + 12 Value Object；原编号 R60�?026-04-19 批次 H �?`-F` 后缀以区分批�?G 同号 R60）| **当前结论�?026-04-19 S14 Phase 2 批次 F H7 锁定�?*：差距分析与 H7 指令要求 DDD 战术建模（Aggregate/Entity/VO）入档。H7 设计�?1) **5 �?Aggregate 边界铁律**（Eric Evans + Vaughn Vernon 精炼）——① 一致性边界（Aggregate 内部强一致性，�?Aggregate 最终一致性）�?单一事务原则（一次操作只修改一�?Aggregate 实例）③ ID 引用原则（跨 Aggregate 通过 ID 引用不嵌入对象）�?尽可能小（除非违反铁律①）⑤ 通过 Root 访问内部（外部不直接访问 Entity/VO）；(2) **8 �?Aggregate Root**（满�?6-10 要求）——AR-01 Order（含 Fill Entity，状态机 PENDING→NEW→ROUTED→PARTIAL→FILLED/CANCELLED/REJECTED/EXPIRED 对齐 interface-contracts §1.4�? AR-02 Position（含可�?Lot Entity，bitemporal�? AR-03 Portfolio（通过 position_ids/strategy_ids/order_ids/risk_policy_id 引用，不嵌入�? AR-04 Strategy（含 StrategyVersion append-only�? AR-05 Factor（含 FactorVersion，FactorValue 外置查询因海量时序）/ AR-06 Signal（本身即 Entity 无子 Entity，TTL 过期�? AR-07 RiskPolicy（含 RiskLimit Entity�? AR-08 Model（含 ModelVersion，TrainingRun 外置）；(3) **6 �?Entity**（Fill/Lot/StrategyVersion/FactorVersion/RiskLimit/ModelVersion）；(4) **12 �?Value Object**（Money/Price/Quantity/InstrumentId/ISIN/Exchange/Timestamp/DateRange/Percentage/IdempotencyKey/LineageRoot/Side），全部 frozen dataclass + 自验�?+ 值相等性；(5) **关键决策**——❌ 不引�?OrderLine（Order 即最细粒度，对齐 interface-contracts.md §1.4 + 量化业界共识�? �?FactorValue 不作�?Factor 内部 Entity（时序海量违反铁律④�? �?TrainingRun 不作�?Model 内部 Entity（训练产物海量）/ �?Fill 归属 Order（一致性边界：Order.filled_quantity 不变量依赖所�?Fill�? �?引入 Model Aggregate（R56 H10 + H6 E-RS-03/E-OP-02 要求建模）；(6) **事件发布责任显式登记**——每�?Aggregate Root 在状态变迁时发布对应 Domain Event（Order→E-EX-01/02/03/04/05/06 + E-EX-07 �?Idempotency Guard 发布 / Position→E-PF-02 / Portfolio→E-PF-01 / Strategy→E-SG-01/02/03 / Factor→E-RS-01/02 / RiskPolicy→E-RK-01/02/03/04 / Model→E-RS-03/E-OP-02）；(7) **Aggregate 行为方法**——Order.submit()→Idempotency Guard �?Pre-Trade �?SOR（与 H10/H9 红线强耦合�? RiskPolicy.evaluate_pre_trade()→Fail-Closed（对�?fault-tolerance-matrix §L04�? Portfolio.rebalance()→批量订单（每笔独立 Key）；(8) **§5 引用关系�?+ §6 代码包映�?*——所�?Aggregate 定位 src/zephyr/{layer}/domain/ 子目录（施工待做，属工作�?P 范围）；(9) **§10 �?05-DA Entity 19 条完整映�?*——声明无虚构实体（所�?AR 可追溯到 05-DA E01-E19 �?interface-contracts Contract 或明确声明为 DDD 建模新增�?Strategy/RiskPolicy/Model）；(10) **§8 自检 12 项全通过**（Aggregate 可追�?一致性边�?ID 引用/事件发布/状态机对齐/Fill 归属/FactorValue TrainingRun 不嵌�?VO frozen/OCP 接口一�?红线行为体现/AR 数量/VO 数量）�?*�?05-DA vs interface-contracts vs domain-event-catalog 三者定�?*—�?5-DA = 数据持久化与血缘视�?/ interface-contracts = DTO 字段形状 / domain-event-catalog = 事实单元（Event�? 本清�?= 领域模型与行为（Aggregate）。同名对象差异：Order 在本清单�?Aggregate Root（含 submit()/cancel()/add_fill() 方法），Order �?interface-contracts 是可�?dataclass（跨层传输对象）。落地：`catalogs/ddd-aggregates.md` v1.0.0（module_id: EA-ARCH-CATALOG-008，~580 行）。|
| R61-F | diagrams/seq-*.mmd × 5 新建（H11�? 张关键时序图对齐 H8/H9/H10；原编号 R61�?026-04-19 批次 H �?`-F` 后缀以区分批�?G 同号 R61）| **当前结论�?026-04-19 S14 Phase 2 批次 F H11 锁定�?*：H11 指令要求 5 张端到端 Mermaid 时序图覆盖订单提�?成交回报/风控触发/组合再平�?异常处置，每�?�? 参与者，�?H8 ACL / H9 容错 / H10 幂等既有设计严格一致。产出：(1) **`seq-order-submit.mmd`**�?2 参与�?90 行）—�?场景 A 正常首次提交（SETNX=1�? 场景 B 瞬时失败 Retry 必过 Guard（SETNX=0 �?E-EX-07 拦截�? 场景 C Broker CB OPEN �?SOR failover（failover 前重�?Guard）；参与�?Strategy/OMS/Idem/Redis/PreTrade/SOR/Facade/Mapper/Raw/Broker/Audit/Notif�?2) **`seq-fill-received.mmd`**�?1 参与�?70 行）—�?6 步骤：Order Aggregate.add_fill()→Position Aggregate.apply_fill()→L07 PnL 增量→L04 Risk 重算+limit check（E-PF-02/E-RK-01）→L05 Strategy.on_fill() 回调→合规留痕（RPO=0）；(3) **`seq-risk-trigger.mmd`**�?0 参与�?84 行）—�?三阶段：**Pre-trade Fail-Closed 4 分支**（PASS/hard limit/checker timeout/checker exception，后三者全部发 E-RK-04 PreTradeRejected�? At-trade 循环（Fill 触发+30s 定时，E-PF-02/E-RK-01/E-RK-02�? Post-trade（drawdown 定时+EOD，E-RK-03 + 不自动强制减仓人工复核）�?4) **`seq-rebalance.mmd`**�?1 参与�?75 行）—�?8 步骤：Scheduler 触发→数据准备（�?data_quality_caveat）→各策�?generate_signals→meta_router 融合→Risk 约束注入→Optimizer 收敛/不收敛→diff 产出订单计划→批量下单（**每笔订单独立 Idempotency Key 不共�?rebalance_id**）→归档+归因起算点；(5) **`seq-exception-handling.mmd`**�?4 参与�?104 行）—�?三场景：Vendor 故障+fallback 链耗尽+stale cache 兜底（E-OP-01 升级 E-OP-03�? Broker 断连+CB OPEN+SOR failover（含 BrokerQ 侧双保险识别重复 clOrdID�? Strategy 异常+策略�?CB（三�?Fallback：保持当�?保守默认/停机人工复核）�?*严格一致�?*：与 03-AA §9.2 Idempotency 时序图命名对齐（Strategy/OMS/Idem/Redis/SOR/Facade/Mapper/Raw/Broker/Audit�? �?c4-l3-l06-trade-execution.mmd 组件命名对齐 + �?ocp-extension-points.md §5 ACL 三段结构对齐 + �?fault-tolerance-matrix.md §L04 Fail-Closed 铁律�?§L06 Retry �?Guard 铁律对齐 + �?domain-event-catalog.md 事件命名对齐（E-EX-01/02/03/04/05/07/E-RK-01/02/03/04/E-PF-01/02/E-SG-01/02/E-OP-01/03 全部在图中显式出现）+ �?ddd-aggregates.md Aggregate 行为方法对齐（Order.add_fill/Position.apply_fill/RiskPolicy.evaluate_pre_trade/Portfolio.rebalance）�?*H9/H10 强耦合可视�?*：seq-order-submit 场景 B/C 显式画出"Retry 必过 Guard"+"failover 前重�?Guard"（H9+H10 铁律）；seq-risk-trigger 显式画出"Fail-Closed 铁律：checker timeout=拒单"+4 个分支全部走 E-RK-04；seq-exception-handling 显式画出"BrokerQ 双保�?DUPLICATE_CLIENT_ORDER_ID"（H10 broker 硬约束的价值体现）。落地：`diagrams/seq-order-submit.mmd`（新�?12/90�? `seq-fill-received.mmd`（新�?11/70�? `seq-risk-trigger.mmd`（新�?10/84�? `seq-rebalance.mmd`（新�?11/75�? `seq-exception-handling.mmd`（新�?14/104�? `target-architecture/README.md` diagrams 索引更新。|
| R65 | `serial-execution-plan.md` v0.3.0 �?v1.0.0 S14-Closure 阶段性收�?+ 批次 I 10.2 P10 `deferred-closure` 跳过 | **当前结论�?026-04-19 S14 Phase 2 Closure 锁定�?*：本串行执行计划 40 子任务中 **39 条已完成 [x]**（批�?A-pre/A/B/C/D/E/F/G/H 全部收工），唯一未完成条�?10.2 P10（`09-governance-architecture.md`）先决条件硬不满足——任务书指名�?`working-designs/governance-three-layer-boundary-design.md` 讨论�?*从未立项**（整�?Grep `governance-three-layer` / `治理三层边界` 零命中除任务书自身外�? 上游依赖 OQ-026 文件治理 7 层激活优先级�?`deferred`�?*用户拍板路径**：批�?H 完成�?Opus 启动批次 I 前置考古 �?核实三层边界设计稿文件不存在 + OQ 登记链断�?�?Opus 给出四分叉（A=先起草讨论稿拍板 / B=跳过阶段性收�?/ C=用户口述拍板 / D=用户新方案）�?用户 2026-04-19 选择**选项 B**（跳�?P10 阶段性收口，剩余问题后续逐条核对）�?*不阻塞架构终局四理�?*�?1) 业界先例——Goldman SecDB / Two Sigma / Citadel 公开资料中治理架构视�?*�?TOGAF 强制构件**，通常�?激活�?配套文档（真实资�?/ 合规上线 / 多人协作任一触发后补齐）�?2) OQ 登记一致性——OQ-026 登记原话明确"**架构终局讨论完成后第一个要拍板的议�?*"，说明这层治�?*设计上就是架构终局之后的激活工�?*�?3) TOGAF 8 视图完整�?9/10�?0-overview / 01-BA / 02-IA / 03-AA / 04-TA / 05-DA / 06-SEC skeleton / 07-INTEG / 08-OPS skeleton / 10-FE 全部就位），09-governance 缺位�?`03-AA §5 scripts 治理代码` + `06-SEC skeleton` + `l10_compliance` layer 共同兜底�?4) 防过早抽象—�?policy / factory / runtime 三层"切法为任务书起草时的新提法，全仓无其他讨论稿，现在强推会产生方案选型偏误�?*激活触发条�?T1-T6**（任一命中解除 `deferred-closure`）：T1 真实资金接入 / T2 多人协作第二位成员加�?/ T3 OQ-062 AI 自治�?P4 升格 P2/P1 / T4 外部审计合规（KYC/券商合规/监管报送）/ T5 Fitness Functions �?5 条落地（OQ-027�? T6 用户主动激活�?*重启工作流（激活时�?*：① 新建 `working-designs/governance-three-layer-boundary-design.md` v0.1.0 in_discussion 立项 D1-D4 四议题（D1 runtime 层是�?0 治理系统 / D2 三层边界定义与接�?/ D3 合规�?AI 员工规划 / D4 激活条件升级路径）+ 候选方案矩�?+ Opus 推荐；② 用户 + Opus 逐条拍板 D1-D4（预�?1-2 轮深度讨论）；③ 同步闭环 OQ-026；④ 拍板稿升�?v1.0.0 + 写入�?ADR（按当时 ADR 编号空间顺延）；�?独立启动"批次 I-重启"非本计划延续，产�?`09-governance-architecture.md` v1.0.0；⑥ 同步更新 target-architecture/README 导航 + 依赖图�?*本收口不影响的部�?*（继续正常运转）�?4 �?OQ-xxx �?`open` 由各自工作流推进 / architecture-rationale-log 继续 append-only / handoff-log 继续接受�?entry / ADR-DRAFT-0009 继续 proposed 等拍�?/ 未来新批次任务（�?governance 视图）不受限制�?*落地证据**：`serial-execution-plan.md` frontmatter v0.3.0 �?v1.0.0 + summary 扩写阶段性收口段�?+ §总进度看板批�?I BLOCKED �?`deferred-closure` 状态格 + 新增「�?S14-Closure 阶段性收口」章节（�?T1-T6 六触发条�?+ 重启工作�?6 �?+ 不影响项清单�? 子任�?10.2 完成状态格更新；`handoff-log.md` v1.21.0 �?v1.22.0 追加 S14-Closure 收口 entry；`architecture-rationale-log.md` v1.25.0 �?v1.26.0（本�?R65 + Stage 25 summary）；`target-architecture/README.md` 同步备注 09 号视图缺位一致性说明（�?OQ-026 deferred 对齐）；`open-questions-register.md` OQ-026 添加交叉引用指向 R65 阶段性收口决策�?|
| R64 | 10-frontend-architecture.md v1.0.0 新建�?0.1，Z-FE 批次 H，TOGAF �?10 视图）| **当前结论�?026-04-19 S14 Phase 2 批次 H 10.1 锁定�?*：差距分析识�?`target-architecture/` 缺少前端架构视图——前�?`frontend/` 物理目录尚未建立，但架构终局必须先行定义以避�?到实施才来想架构"的反模式（对�?Bloomberg Terminal / Refinitiv Workspace Platform / QuantConnect Lean+Cloud / Interactive Brokers TWS 四家机构标配前端独立架构文档）。前置治理修复（本批次顺带完成）�?a) **R 号并发派号事故治�?* —�?批次 F（H6/H7/H11）与批次 G（S2-S6）同日并发，R 号空�?R59/R60/R61 重号，按 append-only + 先到先得原则 = 批次 G 保原号、批�?F 三条�?`-F` 后缀（R59-F / R60-F / R61-F），下发《R 号并发派号规约》防复发�?b) **追溯�?ADR 升格** —�?现场核实发现 `ADR-DRAFT-0007-frontend-platform.md`（前端方�?D）与 `ADR-DRAFT-0008-federated-architecture.md`（Federated-Light 四域 Metamodel）已有完�?proposed 草案，但未升格为 accepted，本批次执行"Retroactive Backfill"将两者迁�?`adr-drafts/` �?`adr/` 并置 status=accepted，frontmatter valid_from 保留原决策日 2026-04-18，revision history 追加"升格补录"条目�?c) **ADR-0006 跳号决策** —�?现场核实 ADR-0006 为真空号（既�?draft 也无 accepted），按业界最佳实践（Linux Kernel / Rust RFC / Google / Amazon / Microsoft 均允�?ADR 编号不连续）�?`adr/index.md` 新增 `## 3bis. ADR-0006 跳号说明` 登记 status=skipped + 不可复用 + 理由（编号只是唯一标识非序列完整性保证，强行连号会产�?占位 ADR"治理垃圾）；(d) **僵尸草稿清理** —�?物理删除 `adr-drafts/ADR-DRAFT-0004-ocp-extension-points.md` + `ADR-DRAFT-0005-kms-architecture.md`（accepted 版早已落 `adr/` 目录，草稿为残留�? `ADR-DRAFT-0007` + `ADR-DRAFT-0008`（升格后源草稿删除）�?*10-frontend-architecture.md 设计**�?1) **§1 Purpose + �?03-AA 边界** —�?03-AA 治后�?15 �?Python（src/zephyr/），本视图治前端独立平台（frontend/ 顶级目录 Node/TS），两者在 03-AA §4.1 L08 api_gateway 子模块物理握手，契约�?07-INTEG §3/§4 定义�?2) **§2 7 条前端架构原�?* —�?FE-P1 独立可部署（frontend/ CI/CD �?src/zephyr/ 完全解耦）/ FE-P2 契约为王（OpenAPI + AsyncAPI 双规�?single source of truth�? FE-P3 API 网关唯一入口（L08 api_gateway 是唯一接触面，禁跨层直连）/ FE-P4 Design System 驱动（所�?UI 必须通过内部组件库，禁裸用外部组件库�?/ FE-P5 状态四分类（Server/App-Local/Session/Real-time 各司其职，禁混用�? FE-P6 前端可观测性（沿用 OTel + Sentry/自建，关联后�?trace_id�? FE-P7 渐进式激活（�?§9 Activation Triggers 触发升级，不提前过度工程化）�?3) **§3 Application/Container/Component/Tools 四层** —�?应用层（单页 React + 路由，每页一 feature�? 容器层（layout/nav/global-modal/error-boundary�? 组件库层（内�?Design System 组件 + 外部 antd/shadcn 封装�? 工具层（API Client/Auth/i18n/时区/货币格式�?图表引擎封装）；(4) **§4 Module Federation / MFE 策略** —�?当前单体（frontend/ 单仓 Monorepo 管理），Activation Trigger 5（见 §9）触发后拆分为壳应用（Shell�? 远程模块（Remote）by-business-domain（research/trading/risk/reporting 四域）via Webpack 5 Module Federation，共�?React + Design System �?singleton�?5) **§5 State 管理 4 �?* —�?Server State = TanStack Query（API 缓存+失效�? App-Local = Zustand（UI 状�?筛选）/ Session = URL + Session Storage / Real-time = WebSocket + BroadcastChannel（跨 tab 同步行情/订单状态）�?6) **§6 Design System** —�?基于 shadcn/ui + Tailwind CSS 自建金融领域组件（OrderTicket/PositionTable/RiskDashboard/CandlestickChart/OrderBook DOM），Token 层（颜色/字体/间距/阴影）通过 Tailwind config + CSS Variables 落地�?7) **§7 构建部署运行时拓�?* —�?构建 Vite（dev�? Webpack 5（prod，为 MFE 预留�? 部署 Nginx 静�?+ CDN（Cloudflare Pages 或自建）/ 运行时拓�?= Browser �?CDN/Edge �?L08 api_gateway �?src/zephyr/ 15 层后端（WebSocket 上行�?api_gateway 同端口）�?8) **§8 关联 by-domain/frontend-domain/** —�?本视图定架构终局，frontend-domain/README.md（v0.2.0 draft）承载实施级下沉内容（目录树 / 路由�?/ 接口映射 / 组件清单），触发条件 = frontend/ 物理建立 + 首版代码落盘�?9) **§9 Activation Triggers 7 �?* —�?T1 首版 Phase 1 MVP（触发条件：有真实数据源+回测能力已稳定，�?Application 层首批页面）/ T2 引入内部用户（触发：多于 Owner 一人使用，激�?Auth + RBAC�? T3 性能问题（触发：首屏 LCP >3s，激�?SSR/SSG 选型 + code splitting�? T4 团队规模扩大（触发：�? 前端工程师，激活目录规模化 + Storybook�? T5 模块拆分（触发：�?bundle >5MB 或多团队并行冲突，激�?MFE 方案 §4�? T6 多租户（触发：服务多个基金，激�?theming + tenant-aware routing�? T7 移动端（触发：需要移动端，激�?React Native 共享业务�?or �?PWA 路径分叉）�?*frontmatter** related_rationale: [R64] / related_adr: [ADR-0007, ADR-0008] / related_open_questions: []（OQ-043 本视图建立即关闭，OQ-045 �?ADR-0008 已关闭）/ tags �?target-architecture/frontend/react/typescript/monorepo/module-federation/microfrontend/design-system/api-gateway/z-fe/h1�?*落地证据**：新�?`target-architecture/10-frontend-architecture.md` v1.0.0（EA-ARCH-FE-001�? 升级 `target-architecture/by-domain/frontend-domain/README.md` v0.1.0→v0.2.0（skeleton→draft，仅 status 升级�? 升级 `target-architecture/README.md` v1.4.0→v1.5.0（�? 文档清单 +1 �?/ §3 阅读顺序架构师链扩到 10 + 新增 Frontend developer 路径 / §4 依赖�?Mermaid 新增 FE 节点 + 4 条边 AA→FE/INTEG→FE/FE→OPS/FE→SEC / frontmatter related_rationale +R64 / tags +frontend-architecture�? `adr/adr-0007-frontend-platform.md` accepted + `adr/adr-0008-federated-architecture.md` accepted + `adr/index.md` v1.2.0（新�?ADR-0006 skipped 登记 + ADR-0007/0008 entries�? 物理删除 `adr-drafts/ADR-DRAFT-0004/0005/0007/0008` 四份僵尸/已升格草稿�?|
| R66 | 09-governance-architecture.md v1.0.0 落地（批�?I-Reopen，S14-Phase2 100% 收工�? ADR-0010 accepted + OQ-026 closed + R65 实质性超�?| **当前结论�?026-04-19 S14 Phase 2 批次 I-Reopen 锁定�?*：R65 S14-Closure 阶段性收口决策（同日上午）被**同日下午**用户改选选项 A「硬�?OQ-026 拍板 + 起草三层边界讨论稿」实质性超越�?*用户拍板路径**：批�?H 完成 �?Opus 启动批次 I 前置考古 �?先决条件硬不满足（讨论稿未立�?+ OQ-026 deferred）→ Opus 给出 A/B/C/D 四分�?�?用户 **第一次�?B**（R65 阶段性收�?deferred-closure）→ **同会话内用户改�?A**（硬�?OQ-026 + 起草讨论稿）�?Opus WebSearch �?2026 年业界资料（Goldman SecDB / JPM Athena / Two Sigma / Citadel / Microsoft Azure Policy / Netflix / Google Zanzibar / OPA Gatekeeper 8 家主流三层切法共�?+ 2026 监管"Embedded, not paper"新趋�?+ Pulumi OPA v1.1.0 full-stack governance 演进）→ 起草 `working-designs/governance-three-layer-boundary-design.md` v1.0.0 accepted 整合 D1-D4 + OQ-026 五议题一次性拍�?�?产出 `target-architecture/09-governance-architecture.md` v1.0.0 active �?升格 `adr/adr-0010-governance-three-layer-boundary.md` v1.0.0 accepted �?关闭 OQ-026（deferred �?closed）→ 更新 6 份治理文件彻底收工�?*五议题拍板结�?*�?*D1-B** Runtime 层独立（�?AI 治理铺路，与 8 家业界共识一致）/ **D2-B** 三层 + 三角闭环（Policy �?Factory �?Runtime �?审计回写 Policy，对�?2026 监管"embedded practice"新要求）/ **D3-B** 三层都预�?AI 员工口子（Policy 花名�?+ Factory `_ai_operator/` 命名空间 + Runtime 审计 schema，与 OQ-063 已拍板三层口子完全对齐，只预留不实施�?T3 OQ-062 �?P2/P1 触发�? **D4/OQ-026** 方案 B 稳健分三轮激活（Sprint 9 L3+L4 发布守卫 �?Sprint 10 L5+AI Safety 三件�?施工 �?Sprint 11 L6 OPA 业务运行�?�?T4 触发补齐 L7 SBOM）�?*用户分阶段逻辑 �?方案 B Sprint 节奏对应**：用户原�?先激活能保证正常发布任务的（Sprint 9）→ 然后是施工（Sprint 10）→ 最后是业务（Sprint 11�?�?Opus 推荐方案 B 时间节奏完全吻合�?*治理三层横切范围澄清**（用户关键追问）：Policy/Factory/Runtime 三层**管整个系�?*所有被治理对象（src 15 层业务代�?+ docs 21 抽屉 + frontend 4 子层 + shared/contracts 契约 + 治理层自己自治），不�?业务层之�?，而是**平级正交**�?尺子 + 纪委 + 审计�?�?*R65 �?R66 的关�?*（append-only 历史保留）：R65 不删不改作为历史决策档案保留；R65 定义�?T1-T6 触发条件�?09 视图整体激活触发器"**降级�?09 视图局部子系统未来升级触发�?**（本视图�?active，T1 真实资金触发的是 06-SEC/08-OPS �?skeleton �?active �?L7 SBOM 激活，不是 09 视图本身）�?*TOGAF 8 视图体系完整�?10/10 就位**�?0-overview / 01-BA / 02-IA / 03-AA / 04-TA / 05-DA / 06-SEC skeleton / 07-INTEG / 08-OPS skeleton / **09-GOV active** / 10-FE 全部就位）�?*serial-execution-plan 主线 100% 完成**�?0/40 子任�?[x]，v1.0.0 �?v1.1.0�?*落地证据**：新�?`working-designs/governance-three-layer-boundary-design.md` v1.0.0 accepted（DW-GOV-THREE-LAYER-DESIGN-001，约 700 行，9 章节�? 新建 `target-architecture/09-governance-architecture.md` v1.0.0 active（EA-ARCH-GOV-001�? 章节，含 Mermaid 三层架构全景�?+ 四接口闭环图 + Gantt 激活时间表�? 新建 `adr/adr-0010-governance-three-layer-boundary.md` v1.0.0 accepted（ADR-0010�? 章节，含 4 候选方案对�?+ 5 议题拍板结论 + 正负影响分析 + 缓解措施�? 更新 `serial-execution-plan.md` v1.0.0 �?v1.1.0（summary 扩写 + 批次 I 表格�?[x] + 批次 I 章节标题�?BLOCKED �?已完�? + 子任�?10.2 完成状态格更新 + S14-Closure 章节分离为现�?S14-Phase2 批次 I-Reopen + append-only 保留 S14-Closure-Archive 历史档案�? 更新 `handoff-log.md` v1.22.0 �?v1.23.0（新�?S14-BatchI-Reopen entry�? 更新 `target-architecture/README.md` v1.5.0 �?v1.6.0（�? 文档清单 +1 �?`09-governance-architecture.md` active / §3 阅读顺序架构师链扩到�?09 / §4 依赖�?Mermaid 新增 GOV 节点 + �?/ §4bis 章节标题改回 "Skeleton Views" / 删除 §4ter 缺位说明改写�?§4ter. 决策追溯�?9 视图�?deferred-closure �?active 的历史路�?append-only 档案 / frontmatter related_rationale +R66 / tags +governance-architecture�? 更新 `adr/index.md` v1.2.0 �?v1.3.0（新�?ADR-0010 一行）+ 更新 `open-questions-register.md` v2.17.0 �?v2.18.0（OQ-026 deferred �?closed + 关闭日期 2026-04-19 + 拍板结论方案 B + 引用 R66 �?ADR-0010）�?|
| R70 | **S15-Phase1 J1 批次第二步：Capability Maturity Heatmap 正交视图（Orthogonal View 第二张）�?04ter 落地 + ADR-0012 accepted + OQ-084 closed**�?026-04-19 S15 Phase 1 J1 批次锁定 / �?R69 同批）| **当前结论**：R69 落地 04bis Runtime Planes 作为第一个正交视图后，同批顺带消�?`tests/外部评审.md` 四家 AI 外部评审（Gemini 2.5 Pro / GPT-5 Thinking / Claude Opus / Grok�?*共识指出�?P1 短板**�?缺少全局能力地图 + 成熟度可视化（top-tier 机构标配�?。用户在 R69 方案审批时主动提出「选项 β：本批次合并 Capability Heatmap」，Opus 确认可共�?frontmatter + 修订同步批次、边际成本极低后采纳�?*方法论对�?3 家业�?*�?1) **ArchiMate 3.2 Capability Map**（The Open Group 官方元模型，Capability × Resource × Outcome 三元�?+ 成熟�?投资强度两轴）；(2) **Gartner IT Capability Framework**（Gartner ITScore 评估模型，五档成熟度 L0-L5 + Gap-to-Target 差距分析）；(3) **Goldman Sachs Enterprise Architecture Capability Dashboard**（公开会议/白皮书披露的季度 review 机制�?4 层业务能�?× 7 核心能力�?= 98 格热力图，由架构师季度刷�?+ 执委会年度拍板目标状态）�?*五档成熟度模型定�?*：L0 Missing（缺失，无任何代码或设计�?/ L1 Design（设计稿完成，尚未施工） / L2 Draft（草稿代码存在，不可用） / L3 Available（基本可用，功能完整但未达生产标准） / L4 Production（生产级别，�?SLO 有监控有告警�?/ L5 Leading（顶级对标，ROI 证明 + 业界公开引用）�?*14 �?× 7 能力域热力图结构**：行 = L00-L13 14 业务�?+ Cross-cutting（shared + 治理 + 前端�? 15 行；�?= 7 核心能力域（数据 / 因子 / ML / 策略 / 执行 / 风控 / 治理）；每格填当前状�?+ 目标状态（T1 真实资金 / T3 AI 自治升格 / T-ENDGAME 顶级机构对标三档目标�? Gap-to-Target 差距描述 + 工时估算（人日）+ 对标证据（业界公开资料引用）�?*当前基线快照**�?026-04-19 评分）：L00 数据�?L2 / L02 因子�?L2 / L03 信号�?L2 / L04 风控�?L2 / L05 组合�?L2 / L06 执行�?L2 / L07 交易�?L1 / L08 人机 L3 / L09 研究 L2 / L10 合规 L1 / L11 ML L1 / L12 遥测 L1 / L13 SRE L1 / Cross-cutting 治理 L3 / Cross-cutting shared L3 / Cross-cutting 前端 L0�?*目标状态三�?*：T1 真实资金 �?全体 L3+（关键层 L4），T3 AI 自治升格 �?全体 L4（核心层 L5 达顶级对标），T-ENDGAME �?14 �?× 7 �?98 格中 �?80% �?L4+、≥ 30% �?L5�?*Gap-to-Target 总工时估�?*：T1 目标总工�?~120 人日（Sprint 0-8 覆盖�? T3 目标 ~400 人日 / T-ENDGAME ~2000+ 人日�?-8 年跨度）�?*季度 review 机制**（OV-P3 SSoT + OV-P4 零业务决策变动）：架构师每季度末刷新热力图评分（2026-07-19 Q3 / 2026-10-19 Q4 / 2027-01-19 Q1 依次循环），执委会每年锁定目标状态并调整投资强度�?*热力图不承载代码**——是 **meta-architecture 层面的可视化治理工具**，与 `catalogs/business-capability-map.md` �?*数据承载关系**：capability-map.md 登记能力条目�?Maturity 列（R57 批次 E H2 已落�?v1.1.0 �?L1-L5 + Investment Intensity + 判断理由三列），04ter 读取 capability-map.md 数据渲染为热力图；capability-map 是数据层 SSoT�?4ter 是可视化层叙事视图�?*落地证据**：新�?`target-architecture/04ter-capability-heatmap.md` v1.0.0 active（EA-ARCH-CAPABILITY-HEATMAP-001，Orthogonal View 第二张）+ 升格 `adr/adr-0012-capability-maturity-heatmap-view.md` v1.0.0 accepted + 登记即时关闭 `OQ-084 Capability Maturity Heatmap 正交视图立项`�?026-04-19 同日拍板�? 同步更新 `target-architecture/README.md` v1.6.0→v1.7.0（�?ter 正交视图体系方法论新�?+ §2 文档清单新增 04ter 登记�?🔷 标记 + §4 Mermaid 依赖图新�?CHM 黄色高亮节点 + 4 条虚线正交标注关�?BA/AA/DA/GOV）�?*�?R69 共享**：J1 批次同时同批落地，frontmatter 联动 +R69 +R70 / +OQ-083 +OQ-084 / +ADR-0011 +ADR-0012，方法论相同（正交视图铁�?OV-P1~P5 共享），验证"正交视图批量引入"可行性�?*外部评审 P1 短板消化状态从 open �?closed**：回应四家评审共�?需要一张能力地图让用户�?10 秒内看懂系统成熟�?这一诉求�?|
| R69 | **S15-Phase1 J1 批次第一步：Runtime Planes 正交视图（Orthogonal View 第一张，TOGAF 方法论级扩展）�?04bis 落地 + ADR-0011 accepted + OQ-083 closed + 前端/治理/03-AA/shared 四份同步**�?026-04-19 S15 Phase 1 J1 批次锁定 / �?R70 同批）| **当前结论**：S15 Phase 1 J0-sync 交付后用户追�?Q1「不�?14 层业务分层，专业机构的控制面 / 执行面的物理切分，是单开一层吗？如果专业机构是这么做的，我们现在能改吗？增加一层避免后面埋雷？本来现在的目标就是把架构终局全貌画出来，现在改成本最小」——精准命�?R66 09-GOV + R67 ADR-0009 v1.1.0 14 业务层锁定后�?*方法论级盲点**：控制面 vs 执行面切分是业界顶级量化机构标配，但若作为第 15 业务层会污染 03-AA 14 层业务本体（破坏 ACL/OCP/因子注册表契约），必须用**另一把尺�?*切。Opus 扫描业界五家顶级机构（Citadel Securities / Jane Street / Two Sigma / Jump Trading / Renaissance）公开资料 + ArchiMate 3.2 多视角方�?+ TOGAF 10 多视角扩展，发现**一致做�?*：业务分层（What 做什么，按抽象层切）与运行平面（How 何时以什么延迟在什么硬件上跑，按运行时特征切）�?*两把正交尺子，不能混为一�?*。Opus 给出三方案（A 单开新层/B 正交视图/C 只在 ADR 预留注释），用户�?B + β合并 Capability Heatmap + 命名 04bis�?*核心方法�?*�?*Orthogonal View 正交视图**（不�?TOGAF �?11 个层，是第一�?*�?TOGAF 10 视图切片维度正交**的视图）�?业务层（What/按抽象层）与运行平面（How/按运行时）两把尺子正交叠加，**零业务决策变�?*�?3-AA 14 层不�?+ 09-GOV Policy/Factory/Runtime 不变 + 10-FE 4 层不�?+ 所有已�?ADR 不变）�?*三档 Runtime Plane 定义（对齐业界）**�?*Hot Path** < 10ms 端到端（tick-to-trade 硬实时，C++/Rust + kernel-bypass DPDK/io_uring/Solarflare OpenOnload + 不可中断，对�?Citadel 做市 / Jump ETF 做市 / Jane Street 极速交易网关；**当前 NOT ACTIVATED**，T-ENDGAME 顶级机构对标阶段才激活） / **Warm Path** 10ms-1s（Python 3.12 + asyncio + uvloop + FastAPI + TanStack Query 前端，可中断协程调度，对�?Two Sigma 研究/ML 推理 / Renaissance 策略推理�?*当前 UNIQUE ACTIVATED**——ZephyrAlpha 2.0 Warm Path only 阶段，全�?14 业务�?+ 前端 + 治理 D 家族主力都在此平面）/ **Cold Path** > 1s 批处理（Spark / Dask / Airflow / Ray cluster + Python 批处理，完全可中�?checkpointing，对�?Two Sigma 历史回测 / Renaissance 模型训练 / Goldman 合规报表）；当前 COLD_PATH_PARTIAL_ACTIVATED（少�?cron + 回测作业跑在 Warm 进程内同步阻塞，未来分离）�?*Hot-adjacent 特殊子类**：不是独立平面，�?Warm 平面下的"对接 Hot Path 下游"子类（前�?WebSocket 订阅行情 / L08 api_gateway 订单端点 / data-client 实时通道），前端架构硬约束——浏览器 + React 技术栈**天然不满�?Hot Path 硬门�?*�? 10ms + kernel-bypass + 不可中断），前端所有低延迟需求的上限只能�?Hot-adjacent�?*正交视图 5 条铁律（README §1ter 方法论级�?*：OV-P1 不污染业务分层本体（正交标注叠加不替换也不新增业务层级）/ OV-P2 命名空间隔离�?4bis/04ter/04quater 后缀�?TOGAF 主序�?00-10 明确区分�? OV-P3 SSoT 单一源（每个正交视图是切片维�?canonical 真源，其�?TOGAF 视图只做引用索引�? OV-P4 零业务决策变动（引入新正交视图时 TOGAF 10 视图只增加正交标注引用不改变已有业务决策�? OV-P5 起码对标 2 家顶级机构（自创概念禁止入库）�?*治理维度 Runtime �?�?执行维度 Runtime Plane**（核心防漂移）—�?9-GOV 治理维度�?**Runtime �?*（Policy/Factory/Runtime 三层中第三层，治"运行时审计与反馈回写"）与 04bis 执行维度�?**Runtime Plane**（Hot/Warm/Cold 三平面中�?Warm 平面，治"什么代码何时以什么延迟在什么硬件上�?�?*名字都叫 Runtime 但意义完全不�?*�?9 视图 §1.2bis 新增完整对照�?+ 双标签联合引用语�?`[GOV:Runtime] × [Plane:Warm]` + 禁止单独使用 "Runtime" 一词的硬约束�?*D 家族 Runtime Plane 归属**�?9 §4.5.1 新列）：D-01 AISG = Warm �?+ security_gateway Hot-adjacent < 50ms + Factory 编译�?Cold / D-02 Scout = Cold（每�?cron�?/ D-03 Decision = Warm / D-04 Capital = Warm �?+ Cold 回测调优 / D-05 Failure = Cold �?/ D-06 Regime = Warm �?+ Cold 训练�?*前端三平面归�?*�?0-FE §7.5 新增整节）：apps/trading-terminal 核心视图 Warm + 行情/下单 Hot-adjacent + 批量导出 Cold；apps/research-ide / monitoring-center / ai-cockpit �?Warm；apps/risk-dashboard Warm 实时 + Cold 报表；platform/ Warm；packages/data-client Hot-adjacent + Warm 双栖；packages/chart-engine Warm�?0fps 16ms 帧预算）；packages/ui-kit/auth/shared-types Warm；SSR 报表服务 Cold；tools/ 不入运行平面（纯 dev-time）�?*Sim-to-Real Gap 消除路径**：Unified Contract（`runtime_plane_tag.py`�? Champion-Challenger Shadow Validation + Replay Testing 三件套，确保回测（Cold Path）结果能翻译到实盘（Warm Path / 未来 Hot Path）�?*激活触发器三档**：T-HOT（Hot Path 激活）= T1 真实资金 > 100 �?�?/ T-ENDGAME 顶级对标启动 / C++/Rust kernel-bypass PoC 通过三条件任一命中 �?ADR 升级 HOT_PATH_ACTIVATED=True；T-COLD-SEPARATE（Cold Path 独立 cluster�? 回测作业阻塞 Warm 主事件循�?> 5s 连续 7 �?�?训练任务 GPU 需求浮�?�?独立 Ray/Dask cluster 部署；T-HOT-ADJACENT-UPGRADE = 前端某组件延迟预算从 100ms 压到 50ms 连续 SLO 违约 �?ADR 升级 + 前端侧硬约束强化�?*跨面通信协议**：Hot �?Warm �?shared memory + lock-free ring buffer（nanomsg/ZeroMQ 零拷贝），Warm �?Cold �?Kafka/Redis Streams 异步队列，Hot �?Cold **禁止直�?*（必须经 Warm 桥接）�?*shared/contracts/runtime_plane_tag.py 契约预留**：定�?`RuntimePlane(str, Enum) { HOT, WARM, COLD }` + 四常量（HOT_PATH_LATENCY_BUDGET_MS=10.0 / WARM=1000.0 / COLD=inf / HOT_PATH_ACTIVATED=False / COLD_PATH_PARTIAL_ACTIVATED=True�? 模块标注协议（`__runtime_plane__` / `__runtime_plane_rationale__` / `__runtime_plane_adjacency__`）；**当前仅文档级标注**（Warm Path only 阶段），Hot Path 激活时升级�?CI 强制校验�?*落地证据�? 份文件联动）**�?1) 新建 `target-architecture/04bis-runtime-planes.md` v1.0.0 active（EA-ARCH-RUNTIME-PLANES-001，Orthogonal View 第一张）�?2) 升格 `adr/adr-0011-runtime-planes-orthogonal-view.md` v1.0.0 accepted�?3) 登记即时关闭 `OQ-083 Runtime Planes 正交视图立项`�?026-04-19 同日拍板）；(4) 更新 `03-application-architecture.md` v1.9.1 �?v1.10.0（�?.0 Runtime Plane Attribution Index 索引节新增，SSoT 指向 04bis，含 14 层快速归属表 + 决策�?+ 标注新模块指�?+ 修订记录）；(5) 更新 `09-governance-architecture.md` v1.1.0 �?v1.2.0（�?.2bis 铁律澄清节新�?+ §4.5.1 D 家族详表新增 Runtime Plane �?+ 修订记录）；(6) 更新 `10-frontend-architecture.md` v1.0.0 �?v1.1.0（�?.5 前端 Runtime Plane 归属四子节新增：7.5.1 12 行快查表 + 7.5.2 Hot-adjacent 硬约�?+ 7.5.3 Cold Path 场景 + 7.5.4 同步规则，含浏览器栈天然不满�?Hot Path 硬门槛澄�?+ 修订记录）；(7) 新建 `src/zephyr/shared/contracts/runtime_plane_tag.py` v1.0.0（约 150 行，�?docstring 规范 + enum + 常量 + 使用示范�? 更新 `shared/contracts/__init__.py` 导出�?8) 更新 `target-architecture/README.md` v1.6.0 �?v1.7.0（�?ter 正交视图体系方法论整节新�?+ §2 文档清单新增 04bis 登记�?🔷 标记 + §4 Mermaid 依赖图新�?RTP 黄色高亮节点 + 5 条虚线正交标注关�?AA/FE/GOV/INTEG/TA + classDef orthogonal 样式定义 + 修订记录 v1.7.0 条目）�?*零代码影�?*——所有变更均�?docs �?+ shared/contracts/ 契约层；runtime_plane_tag.py 当前仅为文档级标注载体不作运行时强制校验�?*方法论亮点产�?*�?a) **正交视图（Orthogonal View）方法论首次在本项目落地**，填�?TOGAF 10 视图方法论级空白，为未来 04quater 部署拓扑 / 04quinquies 数据生命周期 / 04sexies 故障域等候选正交视图提供标准范式；(b) **"业务分层 × 运行平面"双尺子正交切�?*方法论首次系统化整理（对�?Citadel/Jane Street/Two Sigma/Jump/Renaissance 五家顶级机构做法）；(c) **Hot-adjacent 子类概念引入**（非独立平面，是 Warm 平面�?对接 Hot 下游"子类），解决前端低延迟需求归属歧义；(d) **防漂移铁�?名字都叫 Runtime 但意义完全不�?** 的双标签语法 `[GOV:X] × [Plane:Y]` 首次落地，防止未来读者将治理�?Runtime 层与执行�?Runtime Plane 混为一谈；(e) **用户 Q1 拷问精准命中 R66 后方法论级盲�?*—�?控制�?执行面是单开一层吗"朴素表达直接触发正交视图整套方法论补齐，验证用户 review 不可�?Opus 自检替代�?|
| R68 | **S15-Phase1 J0-sync 批次�?9 视图 39�?5 系统扩展（D 家族 AI 治理基础设施�? 03 视图 L10/L11 子模块同�?+ file-governance-architecture-design §7ter.13 索引�?*�?026-04-19 S15 Phase 1 J0-sync 批次锁定）| **当前结论**：J0 批次（R67）交�?review 后用户检�?09 视图 §4.3 C 家族 16 VIB 表，**直接指出"这里我记得聊了不�?16 个啊，后面又加了非常多功能，还有反泄密的，抓取知识的等等"**——精准命�?Opus �?J0 批次中未�?AISG（OQ-076�?026-04-19 上午新增�? Scout Agent（OQ-079�? 四大引擎（OQ-080 G1-G4）同步回 09 视图 canonical 表的**落差**。Opus 执行落差扫描�?a) 09 视图 §4 系统表锁�?**39 系统**�?026-04-18 会话 10 快照）；(b) `ai-security-gateway-design.md v0.1.0` / `ai-autonomy-architecture-design.md v1.3.0 §12` 两份新增内容**未同�?09 视图**�?c) `03-application-architecture.md` �?L10/L11 子模块清�?*未同�?ADR-0009 v1.1.0 §3.5 已预留的 `ai_security/` 子目�?�?`ai-autonomy v1.3.0 §12.3` 指定�?`scout/` 归属**�?d) `file-governance-architecture-design.md` 39 系统表未加增量。用�?3 选项�?*�?A「立刻补同步（保架构终局活文档状态）�?*�?*核心方法�?*�?**canonical 单点真源 + 讨论稿索引节**"模式—�?9 视图�?canonical（永远是最新锁定），讨论稿（`file-governance-architecture-design.md`）只�?**index 不做重复内容**，彻底解�?同一事实在多份文件中各自维护导致的口径漂�?（回溯：此前已出�?14 vs 15 �?/ 39 vs 45 系统 / in_discussion vs superseded 等多次漂移事故，本次建立"canonical 优先 + 索引登记"防漂移模式）�?*D 家族的命名与分类依据**：D = Defense（防线）/ Data-Intelligence（情报）/ Decision（决策）首字母三重共识，强调 **AI 治理�?�?�?�?三大基建能力**；D 家族**独立于原 A（机构标�?21�? B（元治理 1�? C（氛围独�?16�? VIBE-BASE（共享底�?1�?*，理由：D 的治理对象是 **AI 员工本身**（AISG �?AI 泄密、Scout �?AI 学习、四引擎�?AI 做高阶决策），与�?39 系统治理�?业务/AI 协作行为"完全不同层；共享三层边界切法不破�?09 视图 v1.0.0 方法论，但单独成家族登记便于 T3 AI 自治升格�?D 家族整体扩展�?*D 家族与原 39 系统关系矩阵**�?9 §4.5.2 canonical 落盘）：独立分类（不重叠�? 共享三层边界 / **�?B-01 正交**（B-01 = 治理治理；D = AI 员工基建�? **�?VIB-03 正交**（VIB-03 = 业务 token/限流调度；D-01 AISG = 防泄�?*上游**层）/ **�?VIB-14 协同**（VIB-14 = 业务决策审计；D-01 prompt_guard & audit = 数据流审计）�?*D 家族 6 系统归属与激�?*：D-01 AISG�?*全三�?P0 红线 / OQ-081 Sprint 0 启动前硬闸门**，代码归�?`src/zephyr/l10_compliance/ai_security/`，承载文 AISG v0.1.0 六大模块�? D-02 Scout Agent（Runtime 为主，代码归�?`l11_ml_platform/scout/`，Sprint 9 简�?+ Sprint 11 完整，强制走 AISG�? D-03 Decision Engine（K2 占位 `l08_human_ai_interface/`�? D-04 Capital Allocation Engine（K2 G2 最高优先级 `l05/strategic/`�? D-05 Failure Learning Engine（K2 G3 末位 `l10_compliance/` + KMS L5�? D-06 Market Regime Engine（K2 G4 次位 `l09_research_innovation/` + `l05/meta_router/`）�?*分层汇总从 39�?5**：Policy 16 不变 / Factory 7 不变 / Runtime 15�?0 / 全三�?1�?（B-01 + D-01 AISG，D-01 成为**第二个全三层 P0 系统**，历史性地�?B-01 元治理平级标记）�?*AI 员工规划�?31→~38**（含 D 家族 ~7 员工）�?*J0-sync 批次顺手�?OQ-082 1/3**：`file-governance-architecture-design.md` v1.7.0 �?**v1.8.0** + status `in_discussion �?partial_accepted` + section_status 三段式（§7ter.13 accepted / §7ter.4/4bis v1.0.0 canonical / 其他 frozen_discussion），剩余 2 份（`architecture-docset-meta-design.md` + `governance-system-internal-structure-convention.md v1.1.0`）保留到下一 working-designs 相关批次顺便清�?*落地证据�? 份文件同�?+ 1 份登记）**�?1) `target-architecture/09-governance-architecture.md` v1.0.0 �?**v1.1.0**（新�?§4.5 D 家族 + §4.5.1 详表 + §4.5.2 关系矩阵 + §4.5.3 D-01 全三层展开 + §4.5.4 D-02 全三层展开 + §4.6 分层汇�?39�?5 + §4.7 激活时间轴�?Sprint 0 前硬闸门 + §5.2 AI 员工口子扩展 + §5.3 总数更新 + §7 v1.1.0 修订记录 + frontmatter related_rationale +R67 + related_open_questions +OQ-076/079/080/081 + related_adr +ADR-0009 + tags +aisg/scout-agent）；(2) `target-architecture/03-application-architecture.md` v1.9.0 �?**v1.9.1**（�?.1 L10 `compliance/` 新增 `ai_security/` 子模�?+ L11 `ml_platform/` 新增 `scout/` 子模�?+ 两者明�?治理归属�?09-GOV 全三�? + §10 v1.9.1 修订记录）；(3) `working-designs/file-governance-architecture-design.md` v1.7.0 �?**v1.8.0**（新�?§7ter.13 J0 批次后增量索引节 + status partial_accepted + section_status + frontmatter related_rationale +R66/R67 + related_open_questions +OQ-076/079/080/081/082 + tags +d-family/aisg/scout-agent + §10 v1.8.0 修订记录）；(4) `open-questions/open-questions-register.md` v2.20.0 �?**v2.21.0**（OQ-082 进度更新 3�? 剩余 + 新增 v2.21.0 修订记录条目）；(5) 本日�?v1.28.0 �?**v1.29.0**（本�?R68）；(6) `handoff-log.md` v1.24.0 �?**v1.25.0**（S15-J0sync entry）�?*零代码影�?*——所有变更均�?docs �?+ 架构视图层；`src/zephyr/l10_compliance/ai_security/` �?`l11_ml_platform/scout/` 子目录仅**登记归属，未施工**（施工触发器：AISG �?OQ-081 硬闸�?Sprint 0 前触�?/ Scout �?Sprint 9 L3+L4 激活时触发）�?*方法论亮点产�?*�?a) "**canonical 真源 + 索引�?*"防漂移模式落地（本次首次），为未来所�?一个事实多处引�?场景提供模板�?b) "**D 家族独立登记**"方法（D 不是�?A/B/C/VIBE-BASE 原分类的修改，是**补充分类**），保留 39 系统历史快照完整性同时新增分类扩展性；(c) "**review 用户精准命中文档落差**"机制验证——用�?我记得聊了不�?16 个啊"的朴素感觉直接命�?J0 批次的同步落差，印证架构终局阶段用户 review �?*必要性不可被 Opus 自检替代**（Opus 视野�?J0 批次已完成，但用户视野内 09 视图�?J0 产物的一致性才是真正的 Done 定义）�?|
| R67 | **S15-Phase1 J0 批次一次性完�?*：ADR-DRAFT-0009 升格 + AISG 独立稿新�?+ 2 现稿追加章节（partial_accepted + section_status�? 5 OQ 登记（含 4 缺口引擎）| **当前结论�?026-04-19 S15 Phase 1 J0 批次锁定�?*：用户拍板三问："15 �?vs 14 层哪个更专业？→ 14 业务层对外口径对齐业界（Goldman/JPM/Two Sigma/Citadel/BlackRock 全按业务层计数）�?5 是含 shared 的物理目录总数，两者都对，分口径使�?+ "ADR-DRAFT-0009 层数冲突专业机构怎么处理？→ 采用 IETF RFC / ISO 11179 / W3C 标准�?**Retitle + Errata** 做法（非 Supersede �?Inline Fix�? + "两现�?status 如何处理？→ **章节�?section_status**（Google API Design Guide / Anthropic 用法），避免整稿�?accepted 造成颗粒度级议题伪共�?+ 整稿保持 in_discussion 造成已拍板章节被误以为待讨论的双向漂�?�?*J0 三问决议 + 一次性执�?8 �?*�?1) **ADR-DRAFT-0009 v1.0.0 proposed 升格�?`adr/adr-0009-src-14-layer-upgrade.md v1.1.0 accepted`**——标题由"11�?5 层升�?改为"11�?4 业务层升�?+ shared 深化"；�?.1 末句"14 �?l-prefixed �?+ shared = 15 �?改为"14 个业务层（L00-L13�? shared 横切目录 = 15 个物理顶级目�?；L11 命名校准 strategic_decision �?ml_platform（R31/OQ-073�? training/inference/model_registry/hyperparameter_tuning 4 子模块；L10 命名校准 governance_compliance �?compliance（R32/OQ-073）；新增 §8 Errata 记录 E-1 标题歧义/E-2 L11 命名/E-3 L10 校准/E-4 历史计数段追溯（11 �?12 �?13 l+shared �?14 业务�?+ shared）；新增 §9 业界对标证据 5 家机构（OQ-068）；`adr-drafts/ADR-DRAFT-0009-src-15-layer-upgrade.md` 物理删除（git 历史保留）；(2) **新建 `working-designs/ai-security-gateway-design.md v0.1.0 in_discussion`**（DW-AISG-DESIGN-001，约 450 行，14 章节）——对标《AI治理报告.md 附录 C�? 八家业界机构（Goldman/JPM/Citadel/Two Sigma/Apple/Microsoft/Anthropic/Samsung 反面教训）；采用影子投影模型（Shadow Projection）三层隔离（Core 绝对隔离 / Abstraction 影子转换 / Interaction AI 协同�? 六大核心模块 + 六大核心能力；Phase 0 最小集 ~21h 工时 5 产物 + 3 路线；独立于 ai-autonomy-architecture-design.md §3.1 Immutable Core 三分区（后者是文件权限分区，AISG �?AI 调用链分区，互补）；(3) **ai-autonomous-company-endgame-design.md v1.2.0 �?v1.3.0**——status `in_discussion �?partial_accepted`；frontmatter 新增 section_status（�?-§7 `frozen_discussion` / AC-1..AC-6 `accepted OQ-063 v2.8.0` / §8 `accepted v1.3.0`）；新增 §8 L2 超时策略拍板收口（Scheme D = 四眼原则 + 红队复议 + 强制事后人工追认 + 分层 TTL 2h/24h/72h + 硬停兜底 + L3 永不适用），关闭 OQ-077�?4) **ai-autonomy-architecture-design.md v1.2.0 �?v1.3.0**——status `in_discussion �?partial_accepted`；frontmatter 新增 section_status（�?-§11 `accepted OQ-021/022/023/025/030/068 closed` / §12 `accepted v1.3.0` / §12.4 四缺�?`pending OQ-080`）；新增 §12 五维×三层治理矩阵 + Scout Agent 学习�?+ Decision/Capital/Failure/Regime 四缺口登记——五维（感知/量化业务/自治决策/安全不变�?人机协作）�?三层（Policy/Factory/Runtime�? 5×3=15 格矩阵，填充结果 13 组件已覆�?+ 2 缺口（实际四缺口 G1-G4）；§12.3 Scout Agent 定位（T3 commodity / 日频 / 归属 l11_ml_platform/scout/ / AISG 强制 / 输出 daily_digest）关�?OQ-079；�?2.4 G1-G4 四缺口（Decision/Capital/Failure/Regime Engine）登�?+ 归属 + G2>G4>G1>G3 优先级（Capital 最紧迫因资金安�?�?Regime 次之因策略方�?�?Decision 再次之因需前两者输�?�?Failure 最后因需前三者有失败可学）→ OQ-080 跟踪�?5) **新增 OQ-076**（AISG 升格 ADR-0011，P0 红线，含 5 �?OQ 076.1-076.5 本地模型选型/打分模型/密钥管理/CI 阻断/AST 重写深度）；(6) **新增 OQ-077 closed**（L2 超时 Scheme D）；(7) **新增 OQ-078 closed**（五维×三层矩阵方法论）；(8) **新增 OQ-079 closed**（Scout Agent 定位）；(9) **新增 OQ-080 open (deferred to K2)**（四缺口引擎 G1-G4 登记）；(10) **adr/index.md v1.3.0 �?v1.4.0**（新�?ADR-0009 �?+ §4 修订记录 2026-04-19 第二�?S15-Phase1 J0-b）�?*本批次零代码影响**：所有变更均�?docs �?+ ADR 层；施工预留位置�?ADR-0009 v1.1.0 �?L10 `ai_security/` 子目�?+ L11 `scout/` 子目录（均仅登记归属，未施工）�?*方法论产�?*�?a) "IETF Retitle + Errata" 升格做法首次在本项目落地，为未来 ADR 口径澄清提供模板�?b) "Section-level status + section_status frontmatter" 首次在本项目引入，为避免整稿粗粒�?status 造成伪共�?漂移提供工具�?c) "五维×三层矩阵" 方法论首次整合功能维�?× 技术维度，为未�?AI 自治架构演进提供坐标系�?*落地证据**：`adr/adr-0009-src-14-layer-upgrade.md` v1.1.0 accepted（新建约 220 行）+ `adr-drafts/ADR-DRAFT-0009-src-15-layer-upgrade.md` 物理删除 + `working-designs/ai-security-gateway-design.md` v0.1.0 in_discussion（新建约 450 行）+ `working-designs/ai-autonomous-company-endgame-design.md` v1.2.0→v1.3.0（frontmatter + 新增 §8 + 修订记录，约 +90 行）+ `working-designs/ai-autonomy-architecture-design.md` v1.2.0→v1.3.0（frontmatter + 新增 §12 + 修订记录，约 +110 行）+ `open-questions/open-questions-register.md` v2.18.0→v2.19.0�?5 OQ + v2.19.0 修订记录条目�? `adr/index.md` v1.3.0→v1.4.0�?ADR-0009 �?+ §4 修订记录�? 本日�?v1.27.0→v1.28.0（本�?R67�? `handoff-log.md` v1.23.0→v1.24.0（S15-J0 entry）�?|
| R71 | **Wave 0 终审 �?A/B 两区物理存放架构（drafts-and-audits + pending-arbitration�?* | **当前结论�?026-04-27 终审大法�?Claude-Opus-4.7 拍板�?*：建立蓝图真源生成的物理路径强制约束。A �?= `docs/19_development_workspace/drafts-and-audits/`（草�?+ 三轮审计），B �?= `docs/19_development_workspace/pending-arbitration/`（已完成三轮审计�?Opus 终审），任何文档进入正式真源目录必须�?A→B→真�?物理路径，由 V-12 门禁强制校验。`review-ready/` �?deprecated（DEPRECATED.md），�?B �?`pending-arbitration/` 取代�?*落地证据**：新�?`drafts-and-audits/README.md` + `pending-arbitration/README.md` + `review-ready/DEPRECATED.md` + `01_policies_and_standards/governance/task/drafts-audits-arbitration-protocol.md`（蓝图真源准入协议，标准层文档）�? 份候选池审计�?Wave 0 末尾迁入 A �?`drafts-and-audits/vibe-coding-infrastructure/` 永久档案，frontmatter �?`audit_status: arbitrated` + `audit_chain` + `arbitration` + `superseded_by` + `ttl: permanent
review_cycle: quarterly` + `migrated_from`�?|
| R72 | **Wave 0 终审 �?ADR 体系停用 + M2 建成同步删除** | **当前结论�?026-04-27 终审�?*：ADR 系统正式停用。原因：(1) 单人项目�?ADR �?rationale-log 双轨重复维护�?2) 三轮审计 + 终审决策机制下，决策已可�?R-XXX rationale-log + 双管�?+ B 区档案完整承载；(3) ADR 元数据（superseded/refines）已可由 frontmatter `superseded_by` 通用机制替代�?*执行规则**�?a) 现存 36 �?ADR（含 `adr-drafts/`）保留至 M2 知识库建成；(b) M2 建成时同 commit 内：批量迁入 M2 KMS �?`decisions` namespace（metadata.type=adr）→ 删除 `02_enterprise_architecture/adr/` 全目录；(c) �?Wave 0 起所有新决策只入 rationale-log（本日志）；(d) ADR-0003（双 AI 协作工作流）�?Wave 0 内即�?superseded_by `vibe-coding-development-workflow.md` §13-15（双管线 + A/B 两区 + V-12 门禁三件套）�?e) `adr-drafts/` 目录�?DEPRECATED.md�?*落地证据**：`adr-drafts/DEPRECATED.md` 创建 + ADR-0003 frontmatter �?superseded_by + `adr/index.md` 顶部追加全局停用横幅（M2 建成时整体退役）�?|
| R73 | **Wave 0 终审兜底 V-12 �?蓝图真源准入门禁 `validate_blueprint_provenance.py`** | **当前结论�?026-04-27 终审兜底 P0�?*：兜底缺口前三轮（GLM/Kimi/Qwen）均未发现的"蓝图本身合法性如何校�?问题。设计：pre-commit 钩子，扫�?`docs/02_enterprise_architecture/target-architecture/` + `docs/04_construction_plans/` + `docs/01_policies_and_standards/` 三个真源目录，每�?`doc_type �?(target_architecture, construction_plan, standard, protocol, registry)` 的文档必�?frontmatter 含完�?`provenance.origin_drafts[]`（指�?A 区文件路径） + `provenance.audit_chain[]`（≥3 个审计回合记录） + `provenance.arbitration.model` + `provenance.arbitration.rationale_log`，且物理路径必须真实存在。豁免清单：`doc_type �?(declaration, deprecated_marker, reference, log, index)`。骨�?P0 立即上线�?-6h），完整规则 Phase 1a 完善�?*AI 自治权限**：Immutable Core（自身代码受 ai_audit_guard 保护）�?*落地证据**：本条登�?+ `scripts/governance/validate_blueprint_provenance.py` 骨架�?8h 行动清单�?1 项）+ `01_policies_and_standards/governance/task/drafts-audits-arbitration-protocol.md` §4 校验规则�?|
| R74 | **Wave 0 终审兜底 V-11 �?AI 自治权限注册�?`ai-autonomy-authority-registry.md`** | **当前结论�?026-04-27 终审兜底 P0�?*：兜底前三轮分布式标�?60+ 模块权限存在 25-30% 错误率（典型错例：`AutoCleanScheduler` �?Human-Gated 偏低 / `EpicAggregator` �?AI-Modifiable 严重偏松 / `ai_audit_guard` 自身权限层未明确）。建立单一真源 `docs/01_policies_and_standards/governance/ai/ai-autonomy-authority-registry.md`，覆盖：业务核心层（C �?L00-L13�? 平台能力层（B 轨）/ Vibe Coding 基础设施（M1-M11�? 容量保障组件 / 脚本系统组件 / 双管线组�?/ 任务�?+ 知识库组�?/ 元层治理文档�?60+ 模块的三层权限（Immutable Core / Human-Gated / AI-Modifiable�? 判定理由 + 审批要求 + Provenance 字段要求�?*变更流程**：本注册表自�?Immutable Core，修改需 Owner 审批 + R-XXX 决策 + commit 内联�?ai_audit_guard 校验规则更新�?*落地证据**：`01_policies_and_standards/governance/ai/ai-autonomy-authority-registry.md` v1.0.0 active（已 Wave 0 落地）�?|
| R75 | **Wave 0 终审 �?容量保障 SLO 注册�?+ 6 �?P0 SLI** | **当前结论�?026-04-27 终审�?*：施工图 B3 `construction-plan-capacity-assurance.md` Phase 0 落地 `config/capacity/capacity_slo.yaml` + 6 �?P0 SLI（CAP-001 启动时间 P99 �?2000ms / CAP-002 事件总线吞吐 �?1000events/s / CAP-003 模块加载延迟 / CAP-004 配置校验耗时 / CAP-005 日志写入 P99 / CAP-006 Provenance 写入 P99）。技术栈终选：YAML + Pydantic v2（零依赖运行时校验）+ structlog + OpenTelemetry SDK（业界标准，Phase 1 即接入避�?Phase 4 重构�? 自研 EMA + 阈�?+ 持续时间（治理闭环）�?*接受 Qwen 修正**�?a) `ai_audit_guard.py` P0 立即部署骨架�?-6h），规则配置 Phase 1b 填表（安全优�?+ 工作量分摊）�?b) `context_compressor` 压缩率从 60% 调整�?40%（务实落地原则，避免 AI 成为瓶颈）�?*落地证据**：B3 施工�?v1.0.0 + ai_audit_guard 骨架�?8h 行动清单�?1 项延伸）+ capacity_slo.yaml schema 锁定�?|
| R76 | **Wave 0 终审 �?双管�?+ 脚本系统 + M1-M11 技术栈终�?* | **当前结论�?026-04-27 终审�?*：施工图 B4 `construction-plan-vibe-coding-pipelines.md` 锁定 11 个模块技术栈：M1 Context Engine（NetworkX + Qwen2.5-3B 本地压缩 + 三级回退�?/ **M2 Vector Memory：SQLite-VSS+FTS5  �?ChromaDB (Phase 2 触发条件 = 向量记录 > 50K)** / **M3 Agent Orchestrator：自�?dataclass+Pydantic  �?LangGraph (Phase 2 触发条件 = 并发 Agent > 3)** / M4-A FDE EMA + 阈�?+ 持续时间 / **M4-B Auto Fixer 升级 Immutable Core**（Wave 0 升级，原 GLM �?Human-Gated 偏低，sandbox 内修�?+ diff 必须修改非删除以�?reward hacking�? **M5 LLM Security Gateway 自研三件�?*：bandit + safety + regex + OWASP LLM01-05 规则集（拒绝 Guardrails 引入，触发条�?= OWASP LLM-04 命中 �?3 次）/ M6 Session Carryover SQLite + TTL 7 �?+ agent_role + task_id / M7-M11 标准化（Drift Detector / Code Health Validator / Knowledge Base / Kill Switch / Invariant Guard）。脚本系�?D1-D12 维度�?*D12 幻觉检测从 Phase 2 升级�?Phase 1（阈值版�?*，LLM-as-Judge 升级�?Hold（触发条�?= 模块 > 300 �?AI 错误�?> 10%�?*接受 Qwen 修正**）�?*接受 Qwen 修正**：V-03 Formal Invariants/TLA+ Hold（触发条�?= ADR > 20 �?�? 次不变量冲突，TLA+ 学习曲线陡峭单人 ROI 极低，Pydantic v2 + assert 已覆�?90% 场景）�?*落地证据**：B4 施工�?v1.0.0 + B1 vibe-coding-infrastructure-architecture v1.1.0（Wave 0 升级摘要�?+ B2 vibe-coding-development-workflow v1.1.0（�?3 双管�?+ §14 A/B 两区 + §15 V-12 门禁）�?|
| R77 | **Wave 0 终审兜底 V-13 �?任务卡元层注册表 `task-card-meta-registry.yaml`** | **当前结论�?026-04-27 终审兜底 P1�?*：兜底前三轮专注 schema/接口未解�?系统间过渡污�?问题。建�?`task-card-meta-registry.yaml` 登记三套并行任务卡系统：(a) **legacy_task_cards**（场外草�?任务�?，已归档�?43 张）状�?= FROZEN-LEGACY，迁移目�?= sqlite_task_db Phase-1b�?b) **v2_staging_zone**（场外草�?任务�?v2-终审-生成/，已归档）状�?= STAGING，限�?�?5 张，Phase-1b 批量导入释放�?c) **sqlite_task_db**（项目内 `.runtime/db/tasks.db`，schema �?B5 §2.1）状�?= PENDING-CREATION（Phase-1b 创建）；(d) **development_workspace_taskbooks**（`docs/19_development_workspace/taskbooks/`�? HIGH-LEVEL-PLANNING（高层规划留 markdown，与 SQLite 任务库通过 task_id 关联）。三层迁移规则：旧卡冻结只读 / v2 隔离区限�?/ SQLite 建成后批量导�?+ 隔离区清�?/ legacy 任务卡逐个评估迁移价值（无价值标 abandoned）�?*AI 自治权限**：Human-Gated（注册表本身），元规则（系统数量、迁移路径）= Immutable Core�?*落地证据**：本条登�?+ `task-card-meta-registry.yaml`�?8h 行动清单�?3 项）+ B5 §4 三层治理工作流�?|
| R78 | **Wave 0 终审 �?M9 KE �?M2 共享 ChromaDB collection（单一真源裁决�?* | **当前结论�?026-04-27 终审�?*：拒�?M9 KE 独立 collection 方案。理由：(a) 防止知识库与向量记忆双轨重复维护�?b) 单一真源原则�?c) 跨类型检索效率（KE / ADR / lessons / runtime_logs 联合查询）。终选方案：M9 �?M2 共享 collection 实例，通过 `metadata.type �?(adr, rationale, ke, lessons, runtime_logs, code_context)` 区分 + namespace 切分（`kms.decisions` / `kms.code_context` / `kms.lessons` / `kms.knowledge` / `kms.runtime_logs`）�?8 字段 schema 完整保留 + 新增 `arbitration_source` 字段（指�?B 区批次）。KBCrawler 本身 AI-Modifiable，输出强制经 `isolation_guard` 写入 quarantine 区（OWASP LLM-04 防自我循环）�?*升级权限**�?*EpicAggregator/EpicVirtualRegistry 升级 Human-Gated**（Wave 0 升级，原 GLM �?AI-Modifiable 严重偏松，Epic 创建涉及架构层级变更�? **AutoCleanScheduler 升级 Immutable Core**（Wave 0 升级，删除规则不可由 AI 修改�? **TagSchemaRegistry 锁定 Immutable Core**�?*落地证据**：B5 施工�?v1.0.0 §3.2 + `config/kms/collections.yaml` schema 锁定 + ai-autonomy-authority-registry.md §2.7 同步�?|
| R79 | **Wave 0 终审 �?5 条争议裁决全�?* | **当前结论�?026-04-27 终审大法官终审，不可上诉�?*�?1) **C-01 ContractBus 迁移批次 = B 三批�?5+15+14�?*——采�?Qwen 立场，Kimi 已指出验证工作量 > 修改工作量；15 文件/批可控回归风险；分两批一次性回归压力过大；每批�?修改 + 验证 + 回归测试 完整闭环 + 7 天稳定期方可进入下一批�?2) **C-02 ai_audit_guard = A P0 立即部署骨架�?-6h�? Phase 1b 配置规则**——采�?Qwen 修正，安全优先：骨架先拦截再配规则；总工作量分摊不阻�?P0�?3) **C-03 context_compressor 压缩�?= B 40%**——采�?Qwen 修正�?0% 压缩需大量人工修正→AI 成为瓶颈�?0% 更安全，符合务实落地原则�?4) **C-04 V-03 Formal Invariants/TLA+ = B Hold**——采�?Qwen 修正，触发条�?= ADR > 20 �?�? 次不变量冲突；TLA+ 学习曲线陡峭单人 ROI 极低；Pydantic v2 + assert 已覆�?90% 场景�?5) **C-05 V-04 LLM-as-Judge = B Hold**——采�?Qwen 修正，触发条�?= 模块 > 300 �?AI 错误�?> 10%；当�?AI 上下�?< 5%�?AI 评价 AI 写的系统"循环评估不可信。权限标注三方共识（C-06/C-07/C-08）已�?Claude 终审完整接纳，写�?G1 注册表�?*评分修正**：无。GLM 15 维度评分通过 Kimi 根因 + Qwen 落地已稳定�?*落地证据**�? 份候选池审计源末尾追�?"Claude 终审裁决结果" �?+ B1/B2/B3/B4/B5 五份蓝图 + G1/G2 两份治理 + 本日�?R71-R79 + V-11/V-12/V-13 三条兜底缺口（详�?R73/R74/R77）�?|
| R80 | **Wave 1 R71 撤销 �?A/B 双区合并为单一草稿�?* | **当前结论�?026-04-27 终审大法�?Claude-Opus-4.7 拍板�?*：撤销 R71 �?A/B 两区物理存放架构，原因：用户实操反馈"移动一次文件非常麻烦，还增加冗余动�?——同一草稿�?A→B→真源三段移动产生冗余动�?+ 额外维护成本，对单人项目而言负担超过价值�?*新架�?*：合�?`drafts-and-audits/`（原 A 区）+ `pending-arbitration/`（原 B 区）= **单一草稿�?* `docs/19_development_workspace/drafts-and-audits/`，通过 frontmatter `audit_status` 字段（draft / under_audit / arbitrated / superseded）做状态机驱动，不再做物理移动�?*落地证据**�?a) `01_policies_and_standards/governance/task/drafts-audits-arbitration-protocol.md` v1.0.0→v2.0.0（标题改"草稿—审计—裁�?单区流水线协�? + 添加 `single-zone` 标签 + 简�?两个物理存放区域"+ 状态机�?audit_status 字段驱动 + frontmatter 字段 `pending_arbitration_source` 重命名为 `drafts_zone_source`，v1 字段名保�?backward 兼容）；(b) `01_policies_and_standards/governance/document/directory-structure-standard.md` v2.1.0→v2.2.0（移�?pending-arbitration 子目录条�?+ drafts-and-audits 升级"单一草稿�?描述 + v2_2_changes 段落）；(c) `scripts/governance/validate_blueprint_provenance.py` 添加 P0-6 规则（`drafts_zone_source` �?`pending_arbitration_source`（v1 兼容）必须指向真实路径）�?d) 物理迁移 `pending-arbitration/2026-04-27-runtime-integration-meta-system/` + `2026-04-27-vibe-coding-infrastructure/` 入草稿区 + 删除�?pending-arbitration/ 目录�?*�?R71 的处�?*：append-only 历史保留，R71 不删改但 status 隐式�?active �?superseded_by R80（沿�?R15-R22 superseded append-only 模式）�?|
| R81 | **Wave 1 终审 �?5 条争议裁决全集（C-01~C-05 全部维持 Qwen 务实立场�?* | **当前结论�?026-04-27 终审，不可上诉）**：基于零依赖优先 + 渐进优先 + 当前阶段适配 + 安全优先 + 免费优先五原则�?1) **C-01 AlignmentMonitor 部署时机 = B Hold**——Phase 0 实验阶段自进化轮�?< 10，立即部署是过度工程；触发条�?= M4 自进化轮�?�?100 且修复回退 �?3 次。安全优先在该领域已�?CBAC + ai_audit_guard + sandbox 三道防线兜底，不需要第四道�?2) **C-02 CircuitBreakerGateway Phase 1 实现范围 = B Phase 1 单向 CLOSED→OPEN**——单人项目无高可用需求；HALF_OPEN 半开探测增加复杂度且 Phase 1 失败重试可手动恢复；Phase 3 触发条件 Agent �?3 时升级。零依赖原则：仍基于 gate_engine.py + SQLite�?3) **C-03 双层沙箱 L2b 部署归属 = B �?ADR-0018**——Windows ACL �?OS 级配置，�?ADR-0018 已确权；RI 层只协调 L2a（subprocess + 白名单）；不重复建设；与现有架构集成成本最低�?4) **C-04 A2A 协议优先�?= B Hold �?Phase 4**——当前单 Agent；A2A 协议引入 schema 复杂；触发条�?= Agent �?3 且出现冲�?+ �?Agent 任务交接频次 �?5 �?天。与 Wave 0 R76 V-05 Hold 决策一致延伸�?5) **C-05 Formal Invariants/TLA+ = B Hold（与 Wave 0 R79 C-04 立场一致延伸）**——单人项�?TLA+ 学习曲线陡峭 ROI 极低；Pydantic v2 frozen + assert 已覆�?90% 场景；触发条�?= ADR > 20 且不变量冲突 �?2 次�?*评分修正**：草�? GLM 综合评分 47/100 反映"运行时集成层未完整施�?现状，无修正必要——Wave 1 终审通过 B6 施工图把 47 分→Phase 1 完成后预�?65 分（运行时调用链路骨架闭环）�?*落地证据**：B6 施工�?§6 技术选型表（裁决标识 `Claude 裁决 = B`�? 草稿�?2 份草案末�?Claude 终审裁决块�?|
| R82 | **Wave 1 终审兜底 �?V-14/V-15/V-16 三项 Claude 独有视角缺口** | **当前结论�?026-04-27 终审兜底�?*：站在全局系统集成视角发现前三轮（Kimi/GLM/Qwen）单文档驱动思维下未识别的三个治理缺口�?*V-14 BlueprintOverlapMergeGate 双蓝图重叠合并门禁（P1�?*：两份草稿都讨论 CL-017~021 但前三轮无人发现"双蓝图覆盖同一组件"问题。前三轮未发现的根因 = GLM 扫描单文�?/ Kimi 深挖单视�?/ Qwen 起草本身单文档驱动；Claude 独有视角 = 跨草稿组件矩阵交叉表。AI 自治 = Immutable Core（治理门禁）。落�?= `scripts/governance/validate_blueprint_overlap.py` + GATE-13 接入 pre-commit�?*V-15 TruthSourceCascadeValidator 真源连锁回溯校验（P1�?*：现有终审通过新决策（�?R84 G1 修正 RI-02/RI-03 权限）会让已发布真源（B1 蓝图）变�?虽然 V-12 通过但内容已过时"，需�?R-XXX 决策→受影响真源的反向链表自动生成。前三轮未发现的根因 = 三轮聚焦"如何让蓝图通过门禁"，但没有"已通过门禁后，下次决策对它的影响如何追�?机制；Claude 独有视角 = 真源生命周期完整闭环（生成→通过门禁→后续决策影响追踪）。AI 自治 = AI-Modifiable（追踪报告，需 Owner 审批同步）。落�?= `scripts/governance/validate_truth_source_cascade.py` + 输出 `docs/19_development_workspace/state/truth-source-cascade-impact.md`�?*V-16 DraftsZoneLifecycleArchiver 草稿区生命周期归档器（P2�?*：A/B 区合并后，已 arbitrated 状态的草稿留在草稿区做证据；但 30/60 天后需自动归档�?`99_archive/` 防膨胀；前三轮只设计了 ttl 字段未设计自动归档器。前三轮未发现的根因 = A/B 区物理迁移本身就承担�?分离已裁定文�?的功能；R80 合并后这个机制消失，但前三轮没考虑�?R80 这种合并决策；Claude 独有视角 = R80 决策的连锁影响识别。AI 自治 = Human-Gated（归档触发需 Owner 确认）。落�?= `scripts/governance/archive_drafts_zone.py` + 30/60 天自动归档到 `99_archive/<year-month>/`�?*严守硬约�?*�? 项均�?Wave 0 V-11/V-12/V-13 不重叠（Wave 0 解决"权限/真源准入/任务系统过渡"，Wave 1 解决"双蓝图重�?真源后续追踪/草稿区生命周�?），�?3 项硬约束严格满足�?*落地证据**：B6 施工�?§10 风险与缓解表 + G4 cleanup-todos CL-022/CL-023/CL-024 三条任务登记 + G1 注册�?§2.11 三个组件权限登记�?|
| R83 | **Wave 1 终审 �?B6 施工�?+ CL-017~021 升级�?RI 扩展模式** | **当前结论�?026-04-27 终审�?*：新增施工图 B6 `construction-plan-runtime-integration-and-cl-gaps.md` v1.0.0�?74 行，未触�?600 行拆分阈值），统一承载 RI-01~07 + CL-017~021 + 三件套（CBAC/CBG/AlignmentMonitor）�?*关键架构裁决**�?a) **CL-017~021 升级�?RI 扩展模式**——CL-017 system_snapshot 嵌入 RI-01 M1 build()（不再是 scripts/ 独立脚本�? CL-018 DocCompressor 嵌入 RI-01（policy.yaml 单独�?Immutable Core �?V-01 Self-Modification�? CL-019 升级 ai-onboarding-guide.md 核心思想章（纯文档，独立�?RI 层）/ CL-020 master-registry-index Hold �?Phase 2（D-04 维持�? CL-021 EditorConfigGate 嵌入 RI-05�?b) **三件套引�?*——CBAC（Pydantic v2 frozen + 5 条能�?YAML，Phase 1a�? 人日�? CBG（扩�?gate_engine.py �?17 �?CheckType，Phase 1b�?.5 人日�? AlignmentMonitor（Phase 3 Hold）；(c) **AI 自治权限修正 4 �?*——RI-02 偏松→Human-Gated / RI-03 偏松→Human-Gated / RI-04 拆分缺失→M4-A Human-Gated + M4-B Immutable Core / RI-07 偏紧→算�?AI-Modifiable + 阈�?Human-Gated�?d) **Phase 1 总工作量 14 人日**（≤ 1 周硬约束 7 满足，假�?2 人日并行 = 7 工作日）�?e) **零新外部依赖**（全部基�?pydantic + sqlalchemy + pyyaml + structlog + watchdog 已有库）�?*蓝图回流**：B1 vibe-coding-infrastructure-architecture �?M1-M11 章节末尾追加"RI-XX 集成入口"指针（CL-025�? B4 §M4 章节末尾追加"RI-04 进入 B6"指针（CL-026），均挂 G4 cleanup-todos Phase 1a 触发�?*真源准入证据**：B6 通过 V-12 蓝图溯源门禁（origin_drafts 双源 + audit_chain 6 �?+ arbitration.model = Claude-Opus-4.7 + arbitration.drafts_zone_source 路径真实存在）�?|
| R84 | **Wave 1 终审 �?G1 ai-autonomy-authority-registry v1.0.0 �?v1.1.0** | **当前结论�?026-04-27 终审�?*：G1 注册�?v1.1.0 升级，增补三节：§2.9 RI-01~07 运行时集成模块（11 行）+ §2.10 CBAC/CBG/AlignmentMonitor 三件套（6 行）+ §2.11 CL-017~021 基础设施缺口组件�? 行）。修�?4 �?Wave 1 草稿权限误标：RI-02 AI-Modifiable�?*Human-Gated**（检索阈值影�?Agent 决策�?/ RI-03 AI-Modifiable�?*Human-Gated**（路由策略影�?Agent 行为�?/ RI-04 整体 Human-Gated�?*M4-A Human-Gated + M4-B Immutable Core**（拆分缺失，M4-B Self-Modification 风险�?/ RI-07 整体 Human-Gated�?*算法 AI-Modifiable + 阈�?Human-Gated**（偏紧，需拆分）。引�?Wave 1 兜底 V-14/V-15/V-16 三个治理组件权限：V-14 BlueprintOverlapMergeGate Immutable Core / V-15 TruthSourceCascadeValidator AI-Modifiable / V-16 DraftsZoneLifecycleArchiver Human-Gated�?*frontmatter 同步**：追�?`arbitration_wave1` 块（model = Claude-Opus-4.7 / date = 2026-04-27 / rationale_log = R-84 / drafts_zone_source = `docs/19_development_workspace/drafts-and-audits/2026-04-27-runtime-integration-meta-system/`）�?*落地证据**：G1 v1.1.0 active + frontmatter related_rationale 追加 R-80/R-81/R-83/R-84 + 版本历史段落追加 v1.1.0 条目�?|
| R85 | **Wave 1 终审 �?G4 post-final-audit-cleanup-todos v1.0.0 �?v1.1.0** | **当前结论�?026-04-27 终审�?*：G4 cleanup-todos 升级 v1.1.0�?a) **CL-017~021 升级�?RI 扩展模式**——R 反链追加 R83，触发条件改�?Phase 1c/1e 触发"（不再是独立脚本）；CL-020 �?Hold �?Phase 2（D-04 维持）；CL-018 升级双产出（standard 文档 + RI-01 doc_compressor.py）；(b) **新增 CL-022/CL-023/CL-024**（V-14/V-15/V-16 兜底任务）；(c) **新增 CL-025/CL-026**（B1/B4 蓝图回流任务）；(d) frontmatter 升级：version 1.0.0 �?1.1.0 / total_items 21 �?26 / related_decisions 追加 R80~R85 / arbitration_wave1 块新�?/ tags 追加 wave-1 + ri-modules + claude-gap-coverage�?*Wave 0 �?Wave 1 决策反链总览同步更新**：Wave 0 R71（A/B 区，Wave 1 R80 撤销�?+ R72-R79；Wave 1 R80（A/B 区合并）+ R81�? 项争议）+ R82（V-14/V-15/V-16 兜底�? R83（B6 施工图）+ R84（G1 升级�? R85（本条）�?*关联文档**：directory-structure-standard.md v2.2.0 + drafts-audits-arbitration-protocol.md v2.0.0 + ai-autonomy-authority-registry.md v1.1.0 + construction-plan-runtime-integration-and-cl-gaps.md v1.0.0�?|
| R86 | **Wave 1 终审 �?v2 隔离区限额提�?5�?5 + 10 张施工任务卡下发 + 模型选型策略落地** | **当前结论�?026-04-27 终审�?*：完�?Wave 1 终审收尾的最后一环——把 B6 + V-14/V-15/V-16 总计 14 人日 Phase 1 施工 + 4.5 人日治理兜底拆解�?10 张施工任务卡 T-V2-004~T-V2-013 下发�?v2 隔离区（场外草稿/任务�?v2-终审-生成/，已归档）�?*v2 区限额硬约束调整**：原 5 张限额（Wave 0 R77 设计）无法承�?Wave 1 终审产出，本条决策提升到 **15 �?*；G2 task-card-meta-registry.yaml v1.0.0 �?**v1.1.0**（限�?5�?5 + MR-02 同步调整 + current_items 注册 13 张完整列�?+ arbitration_wave1 块）；frontmatter `metadata_version: 1.1.0` + 修订记录 v1.1.0 条目；T-V2-001/002 状�?ready→done（artifact 已落地：validate_blueprint_provenance.py + task-card-meta-registry.yaml）�?*模型选型策略首次明文化（R76 哲学落地�?*：每张任务卡 frontmatter 新增 `model: GLM-5.1 / Sonnet / Opus` 字段 + `model_rationale` 说明；Wave 1 10 张新卡分配为 GLM-5.1×5（机械任务：CBAC / CL-019 / V-14 / V-16 + T-V2-003�? Sonnet×4（中等复杂度：CBG / M1 扩展 / RI-04+05+CL-021 / RI-06+07 / V-15�? Opus×1（关键架构：RI-02+03 跨模块设计）；总成本估�?= 14 人日 Phase 1�?0% �?GLM-5.1+Sonnet 完成，Opus 仅在关键裁决�?�?h/卡）�?*Wave 1 收工报告**：新�?`docs/19_development_workspace/structure-and-mapping/wave-1-handoff-summary.md` v1.0.0，与 Wave 0 wave-0-handoff-summary.md 配对，承�?Wave 1 全套交付物索�?+ Wave 1 �?Phase 1 衔接说明 + Phase 1 18.5 人日工作量分布�?*Owner 48h 行动清单（Wave 1 版）**�?1) 一�?commit 全部 Wave 1 改动（含 R80~R86 + 9 个文件操作）�?2) T-V2-004 启动 Phase 1a CBAC（GLM-5.1，Trae CN）；(3) T-V2-011 启动 V-14 骨架（GLM-5.1，Trae CN）；(4) 验证 G1 §2.9~2.11 权限修正无遗漏（Sonnet，Cursor）；(5) Owner 阅读 wave-1-handoff-summary.md 确认收工�?*关联文档**：task-card-meta-registry.yaml v1.1.0 + 13 �?T-V2-XXX 任务�?+ wave-1-handoff-summary.md v1.0.0�?*至此 Wave 1 终审 100% 收工**（B1-B5 真源 �?/ B6 真源 �?/ G1-G4 注册�?�?/ V-12 门禁 �?/ Wave 0+1 任务�?13 �?�?/ Wave 0+1 收工报告 2 �?✅）�?|
| R87 | **Phase 1a/1b 实施 �?V-11/V-14/V-15/V-16 治理门禁 + CBAC + CBG 落地** | **当前结论�?026-04-27 实施�?*：Phase 1a/1b 核心治理组件落地完成�?*GLM-5.1 完成 4 张任务卡**：T-V2-003（V-11 权限注册表自校验 �?`validate_authority_registry.py` + GATE-14�? T-V2-004（CBAC 最小版 �?`capabilities.yaml` + `capability.py`�? T-V2-011（V-14 蓝图重叠检�?�?`validate_blueprint_overlap.py` + GATE-13�? T-V2-013（V-16 草稿区归�?�?`archive_drafts_zone.py`）�?*Sonnet 完成 2 张任务卡**：T-V2-005（CBG 单向熔断 + L2a 沙箱 + L08 注册 �?`circuit_breaker.py` + `process_sandbox.py` + gate_engine �?17 �?CheckType�? T-V2-012（V-15 真源连锁回溯 �?`validate_truth_source_cascade.py`）�?*GLM-5.1 子任�?*：cbg.reset() CLI（`scripts/governance/reset_cbg.py`�? B6 §2.2 Phase 1b 实施记录 + ADR-0018 v1.0.1 / G4 §6.7 CL-023 V-15 启动记录�?*基础设施**：新�?`config/` + `.runtime/` 目录树（7 个子目录 + .gitkeep）�?*测试**�?6 个单元测试全部通过（T-V2-003: 22 / T-V2-004: 12 / T-V2-011: 17 / T-V2-013: 15）�?*affected_files**: `scripts/governance/validate_authority_registry.py`, `scripts/governance/validate_blueprint_overlap.py`, `scripts/governance/archive_drafts_zone.py`, `scripts/governance/validate_truth_source_cascade.py`, `scripts/governance/reset_cbg.py`, `config/capabilities.yaml`, `src/zephyr/shared/capability.py`, `src/zephyr/gates/circuit_breaker.py`, `src/zephyr/llm_security/process_sandbox.py`, `.pre-commit-config.yaml`, `docs/04_construction_plans/construction-plan-runtime-integration-and-cl-gaps.md`, `docs/02_enterprise_architecture/adr/adr-0018-agent-sandbox-windows-acl.md`, `docs/02_enterprise_architecture/target-architecture/09-governance-architecture.md` |
| R88 | **Phase 1c 实施 �?M1 扩展 + CL-017 system_snapshot + CL-018 DocCompressor 落地** | **当前结论�?026-04-27 实施�?*：Phase 1c 上下文引擎扩展完成�?*Sonnet 完成 T-V2-006**：SystemSnapshot（CL-017，`src/zephyr/context_engine/system_snapshot.py`，~260 行）+ SystemSnapshotter（含 run_in_build() 类方法，capture() 永不向上传播异常�? DocCompressor（CL-018，`src/zephyr/context_engine/doc_compressor.py`，~350 行）+ CompressionPolicy（Pydantic v2 frozen�? 不变量）+ `config/compression/policy.yaml`（Immutable Core�?0 行）+ M1 build() 扩展（context_budget_tracker.py 新增 register_doc_compressor / get_doc_compressor / compress_session_context 3 个方�?+ L2_THROTTLE 事件 payload 追加 compression_suggested=True）�?*关键设计决策**�?1) SystemSnapshotter.capture() 永不向上传播异常（仅 warnings.warn），保证 M1 backward 兼容�?2) DocCompressor._enforce_length 截断时只在文本后半段查找换行符，避免极端截断到文件头部；(3) CompressionPolicy min_chars �?100 �?Immutable Core 约束�?*测试**�?7 条全部通过（snapshot 31 + compressor 26）�?*GLM-5.1 子任�?*：B6 §2.3 Phase 1c 实施记录�?*affected_files**: `src/zephyr/context_engine/system_snapshot.py`, `src/zephyr/context_engine/doc_compressor.py`, `config/compression/policy.yaml`, `src/zephyr/context_engine/context_budget_tracker.py`, `docs/04_construction_plans/construction-plan-runtime-integration-and-cl-gaps.md` |
| R89 | **Phase 1d 实施 �?RI-02 统一记忆 API + RI-03 触发路由引擎落地** | **当前结论�?026-04-27 实施�?*：Phase 1d 运行时集成核心组件落地完成�?*Opus 完成 T-V2-007**：UnifiedMemoryAPI（RI-02，`src/zephyr/kb/unified_memory_api.py`�? TriggerRouter（RI-03，`src/zephyr/orchestrator/trigger_router.py`�? `config/trigger_router.yaml`�? 条路由映射）�?*测试**�?5 条全部通过（覆盖率 88%）�?*GLM-5.1 子任�?Step 9**：路由表 mapping 评估�? 真实 + 4 stub�? compression_needed 替换为真�?handler（`zephyr.context_engine.context_budget_tracker.ContextBudgetTracker.compress_session_context`�? 接线文档（`docs/19_development_workspace/structure-and-mapping/trigger-router-wiring-doc.md`�? YAML 追加接线状态注释�?*affected_files**: `src/zephyr/kb/unified_memory_api.py`, `src/zephyr/orchestrator/trigger_router.py`, `config/trigger_router.yaml`, `docs/19_development_workspace/structure-and-mapping/trigger-router-wiring-doc.md` |
| R90 | **蓝图体系元标�?PS-STD-005 发布 �?建立三级金字塔蓝图架�?* | **当前结论�?026-05-04 Owner+DeepSeek-V4-Pro 决策�?*：针�?每个功能域一个集成蓝�?这个架构决策，创建蓝图体系的元标准文�?`01_policies_and_standards/meta/blueprint-architecture-standard.md`（PS-STD-005，v1.0.0，~480 行）�?*推导�?*�?1) 根因 �?现有 19 份蓝图全部平铺在 `03_modules/l01_infrastructure/` 下，没有层级归属声明。新 AI session 不知�?哪份是总蓝图、子蓝图归属于谁"。从 19 蓝图扩展�?100+ 时扁平化不可持续�?2) 对标 �?Codified Context (arXiv 2602.20478) 三层记忆模型（热记忆宪法 / 领域触发 Agent / 冷记忆按需检索）、Microsoft Edge AI master-blueprint→domain-blueprint→component 三层、HP Inc specification.md + blueprint.md 双层分离、TOGAF Architecture Repository、ITIL SACM CI Hierarchy�?3) 决策 �?建立三级金字塔：Level 0 全系统总蓝�?`_system-master/`（SYS-MASTER-001�?4 层跨层契约）�?Level 1 域集成蓝�?`_domain-{layers}/`（每功能域一个）�?Level 2 模块蓝图 `l{NN}_{name}/{module}/blueprint.md`（单系统设计+施工指引）�?4) 方案比�?�?对比�?写进 blueprint-construction-template.md"（太窄——管单个蓝图不是管体系）�?写进 AGENTS.md"（太散——AGENTS.md 是入口不是规范）�?作为规则写进 constitutional 标准"（太重——蓝图重组可逆，不触发宪法条件③）。终选：创建独立元标�?PS-STD-005，与 PS-STD-002（标准文档模板）成姊妹篇�?5) 核心约定 �?`belongs_to` 前端字段（每份蓝�?MUST 声明上级蓝图�? `blueprint_level` 注册表字段（SYSTEM/DOMAIN/MODULE�? 14 �?ID 前缀表（MOD-MASTER/MOD-DOMAIN/MOD-INF/MOD-KB/MOD-DS/MOD-AF/MOD-SIG/MOD-RISK/MOD-PC/MOD-EXE/MOD-PTA/MOD-UI/MOD-RES/MOD-CMP/MOD-ML/MOD-EXP�? AI 冷启�?6 步定位路�?+ Token 三层加载策略 + 19 份既存蓝图归属映射（全部→MOD-MASTER-001）�?6) 1 瞬态豁�?�?当前 19 份蓝图不强制立即声明 `belongs_to`；Phase 1 结束（任务系�?v0.3.0 升级 + GateEngine G7 激活）时豁免自动失效�?7) `MOD-MASTER-001` 当前过渡角色 �?1 期它承担 L01 域集成蓝图职责；Phase 2 触发条件（首�?L02+ 蓝图创建）时改名 `MOD-DOMAIN-L01-001`，同时新建真正的 `SYS-MASTER-001`�?*文件类型判定**：本标准属于 PS-STD-002 �?格式定义�?子类型——管"结构怎么放、目录怎么命名"，不管技术决策内容�?*配套动作已完�?*�?a) PS-STD-005 文件创建（蓝图的蓝图）；(b) 本决�?R90 记录推导链（2026-05-04）；(c) blueprint-registry.yaml v2.0.0 �?v2.1.0（全 19 条记录添�?blueprint_level 字段 + 受控词表 + by_blueprint_level 统计）�?*违反可逆性验�?*：重组蓝图目录归属的操作完全可逆——不改代码、不改数据�?*关联文档**：`01_policies_and_standards/meta/blueprint-architecture-standard.md` (PS-STD-005) + `03_modules/blueprint-registry.yaml`（待升级�?+ `03_modules/index.md`（§蓝图体系层级待追加�?|
| R49 | 批次 D 6.0 行数闸门判断 + 方案 D "最小必要下�?采纳 | **当前结论�?026-04-19 S14 Phase 2 批次 D 启动前决策）**：按 `serial-execution-plan.md` 批次 D 任务 6.0 要求先做行数闸门判断再决定是否触�?OQ-072 下沉�?*数据核实**（Get-Content / Measure-Object -Line / byte newline 三种口径交叉验证）：03-AA 当前真实行数 = **738**（并非此前沟通中出现过的 590 / 653 两个历史/错误数字�?53 �?2026-04-18 会话 12 写入 OQ-072 背景段时的快照，批次 B R41/R42/R43 �?2026-04-19 把文件从 653 推到 738）；批次 D 预估增量（按方案 D 配置�? §3.5 C4-L3 引用�?~30 �?+ §4.5 Vendor Registry 摘要 ~15 �?+ §8 容错摘要 ~15 �?+ §9 幂等摘要 + Mermaid 时序�?~60 �?= �?**120 �?*；预计终�?= 738 + 120 �?**858 �?*，距 OQ-072 条件 �?"父视图对应章�?> 1000 �? 仍有 **142 行缓�?*�?*OQ-072 三条�?AND 逻辑核验**：条�?�?架构终局讨论已锁 = ❌（批次 D-I 仍在深加工中�? 条件 �?行数�?1000 = ❌（858 < 1000�? 条件 �?Opus 起草下沉计划且用户批�?= ❌（未启动）。三条件命中 0/3，按严格 OQ-072 规则**此刻并未硬触发强制下�?*�?*方案比较�? 选项�?*：方�?A（主动大手术下沉 §4.1 14 层详情到 src-domain/README）—�?�?被否决，理由 3 条：(a) §4.1 承载 R31/R32/R33/R34/R35/N11/OQ-023/OQ-030/OQ-063 多条架构级决策锚点，�?05-DA/07-INTEG/02-IA §9 �?rationale-log 多处反向引用，下沉需重写 15-30 处双向链接（�?60-90 min �?+45 min），收益/成本不划算；(b) 这些�?架构一级决�?rationale 而非实现细节"，下沉会削弱父视图权威性；(c) 未满�?OQ-072 条件 �?"架构终局已锁"，属于过早抽象——后续批�?E-I 仍可能追�?§4.1 内容（S 系列 AI Operator 预留 / Z-FE L08 引用等），现在下沉会产生后续双处维护负担。方�?B（硬�?1200 行不下沉）—�?�?违反阈值，浪费 OQ-072 预埋�?by-domain/ 结构。方�?C（拆分批�?D，推�?6.3/6.4）—�?�?延迟量化红线（幂等是资金安全一级议题），不接受�?*方案 D（采纳）= "最小必要下�?**：现�?§4.1 内容零重写零搬迁；批�?D �?*新增内容**中，重型深度章节（H8 Vendor Registry 详情 / H9 容错矩阵完整说明 / H10 Key 公式+存储 schema+异常处置清单）从一开始就直接写入 `by-domain/src-domain/` 下三份新 design-brief 文件；父视图 03-AA 只保�?机制可视�?+ 决策摘要 + 引用�?，确保读者在父视图能一眼理解核心机制而不需跳转�?*父视�?子文件边�?*：父视图承载（a�?.5 C4-L3 三图引用与阅读路�?/ （b）�?.5 Vendor Registry 摘要 ~15 �?/ （c）�? 容错 5 层压缩矩�?~15 �?/ （d）�? 幂等 Mermaid 时序图本�?~40 �?+ 场景说明 ~20 行；src-domain 承载（a）`ocp-extension-points.md` 完整三段结构 raw_client/mapper/facade + 资产�?namespace + 故障转移策略 / （b）`fault-tolerance-matrix.md` 每层策略完整说明 + 阈�?+ SLO 关联 / （c）`idempotency-design.md` Key 公式详解 + Redis+journal schema + At-Least-Once 推理 + 8 条异常处置清单�?*design-brief 类型锁定**：三份子文件 doc_type = `design-brief`（比 ADR 轻、允许迭代；比父视图厚、含完整设计；可被父视图引用），�?ADR 的区�?= design-brief 非不可变决议�?*src-domain/README 升格**：此轮从 `status: skeleton` v0.1.0 升到 `status: active` v1.0.0，�? "未来承载内容"表前 3 行标记为"已就�?+ 版本号，其余 4-6 行（architecture / layer-stack / layer-dependencies / immutable-core-inventory / ai-operator-slots / interfaces）保�?planned�?*这是 OQ-072 双轨制的首次实质兑现**�?*时序图位置决�?*：�? Mermaid 保留在父视图（读者第一视觉入口需要看到订单提交→重试→去重的流程链路），配置细节/存储选型/异常矩阵下沉�?*R 编号链路**：R49 = 本条闸门判断；R50-R52 = 5.5/5.6/5.7�?4-TA §8/§11/§12，不涉下沉）；R53 = 6.1 H8 Vendor Registry（�?.5 摘要 + src-domain 详情）；R54 = 6.2 H5 C4-L3�? .mmd + §3.5 引用）；R55 = 6.3 H9 容错（�? 摘要 + src-domain 详情）；R56 = 6.4 H10 幂等（�? 摘要/时序�?+ src-domain 详情）�?*落地证据**：本条（R49�? R50-R56 + `03-AA.md` v1.7.2→v1.8.0 + `04-TA.md` v1.2.0→v1.3.0 + `by-domain/src-domain/README.md` v0.1.0→v1.0.0 + 新建 3 �?design-brief + `diagrams/c4-l3-*.mmd` × 3�?|

### 关于 R15-R22 �?superseded 处理说明

上表�?R15 / R16 / R17 / R19 / R20 / R21 / R22 �?`status: superseded` 标记采用 **append-only 机制**（符�?discussion-document-standard v2.0.0 §6.2）：

- **原条目不删改**：保留原始结论描述，便于未来回溯"当时为什么这么想"
- **status 字段显式标注**：在描述中补 `status: superseded`
- **新结论写在后�?Stage / R 条目**：例�?R17 被后续新讨论覆盖时，应新�?R-N（N > 25）作为新版本，并在本表的"含义"栏链�?
- **不使用删除线**：删除线只是视觉效果，不是机器可读状�?

> 机构标准参考：ADR-0002 落地、ISO/IEC 11179 "Metadata Registries" 的状态管理规范�?

## 5. 当前已经产出的关键文�?

> ⚠️ **过时快照警告（R5 审计 2026-05-03�?*：本节及后续 §6-§9 是项目某个时间点的运营状态快照，**不保证最�?*。权威来源请查阅各自 SSoT 文件（index.md 做文档清单、OQ register 做待办追踪、handoff-log 做会话交接）。本节仅作历史参考�?

| 文档 | 角色 | 当前状�?|
|------|------|----------|
| [`02-information-architecture.md`](./target-architecture/02-information-architecture.md) | 系统终局抽屉与目标信息架构（Stage A 后权威位置） | 主架构文�?|
| `organizational-memory-system-design.md` [已归�?见外部工作区] | 组织记忆系统专题设计稿（**已归�?* archive/draft-abandoned/�?| 专题主稿（历史） |
| `memory-system-landing-v1-checklist.md` [已归�?见外部工作区] | 记忆系统专项主清单（**已归�?* archive/one-shot-completed/�?| 专项路线图（历史�?|
| `memory-system-landing-task-draft.md` [已迁�?见外部工作区] | 记忆系统细粒度任务草�?| 细项任务 |
| `memory-and-context-directory-guide.md` [待创建] | 记忆系统未来 canonical 落位说明 | 落位说明 |
| `discussion-document-standard.md` [待创建] | 讨论文档标准与最小字�?| v1 结构标准 |
| `taskbook.md` [已迁�?见外部工作区] | 总任务书与推进主�?| 总流程入�?|

## 6. 当前仍未完成的讨�?

以下内容尚未完全定稿�?

1. 组织记忆系统的最�?canonical 物理落位（R15 �?superseded，待重新讨论，见 OQ-001�?
2. 记忆系统零件地图�?P0 / P1 / P2 划分（R17 �?superseded，待重新讨论，见 OQ-002�?
3. taxonomy 扩展规则的正式制度化写法
4. 讨论文档标准格式的最终冻�?
5. ADR / session log / promotion 的正式模板化
6. 未来自动化、检索与向量层的具体实施边界
7. 简易决策记忆系�?v0 何时升格为正�?canonical 制度
8. 前置项目 session log 与本�?transcript 的来源登记应落在哪个正式路径
9. 前置项目聊天记录进入新项目时的批�?intake 顺序与清洗边�?

这些问题的当前状态，统一登记在：

- `open-questions-register.md` [已迁�?见外部工作区]

## 7. 当前阶段的工作原�?

当前应遵守以下顺序：

1. **先全貌，后细颗粒**
2. **先抽屉，后塞内容**
3. **先讨论区收敛，后升格�?canonical �?*
4. **先区分已定与未定，再写制度与实现**
5. **先把原因、结果、未决、任务分流清楚，再谈自动化入�?*

## 8. 给下一个会话的续接入口

若下一个会话需要继续推进，优先从以下三件事之一开始：

1. **回答记忆系统的三个前提问�?*：政策层放哪里？执行层放哪里？索引层放哪里？
2. 回到 OQ-001：组织记忆系统的最�?canonical 物理落位（现在有了治理体系前提，可以重新讨论了）
3. 回到 OQ-008：明确新�?Session Log 正式路径（建�?`18_audit_and_evidence/session-logs/`，但需拍板�?

## 9. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-17 | 初版：整理从文件治理失控到决策记忆，再到组织记忆系统与全貌架构优先的完整讨论链�?|
| 2026-04-17 | 增补：确认当前工作区已形成简易决策记忆系�?v0，并明确"原因/结果/未决/任务"分流与先标准化后入库原则�?|
| 2026-04-17 | 增补：澄清前置项目会话留痕是"Cursor transcript + 项目�?Session Log"两层机制，并提出新建项目应先重建机制、后分批吸收前置项目聊天记录�?|
| 2026-04-17 | 增补 Stage 8：确认机构标准下的元数据契约、异步流水线、知识边界分层；新增结论 R12-R14；新增未决问�?异步流水线脚本位�?�?|
| 2026-04-17 | 增补 Stage 9：确定记忆系�?canonical 物理落位，明确索引层�?`08_ai_engineering_and_agent_ops/memory-and-context/` 的内部结构；新增结论 R15-R16；关�?OQ-001�?|
| 2026-04-17 | 增补 Stage 10：确定记忆系�?P0/P1/P2 实施优先级划分，P0 = Decision Memory System（决策记忆闭环）；新增结�?R17；关�?OQ-002�?|
| 2026-04-17 | 增补 Stage 11：确认跨域核心价值链（数据→研究→模型→策略→组合→执行→报告），明确细颗粒度数据契约延后；新增结论 R18�?|
| 2026-04-17 | 增补 Stage 12：确定异步流水线脚本位置�?`scripts/governance/memory-pipeline/`，明确记忆系统治理体系四层分布，关闭 OQ-010；新增结�?R19-R22�?|
| 2026-04-17 | 增补 Stage 13：讨论治理体系全貌作为记忆系统前提，明确治理体系五层架构与三条横向主线；新增结论 R23-R25�?|
| 2026-04-17 | **Stage 14 骨架对齐机构终局**：做埋雷清单审查�?3 处）�?全修 🔴🟡 7 条；�?ADR canonical �?+ �?ADR-0001/0002/0003；workspace 子目录改语义命名；文档标准升级到 v2.0.0（单 schema + 分阶段必�?+ 受控词表 + append-only supersedes + 四符号状态）；triage-guide �?4 类扩�?8 类；新增 adr-drafts / roadmaps / risk-registers / session-logs / archive 5 个骨架目录；新增 terminology-mapping.md；新增结�?R26-R30�?|
| 2026-04-18 | **Stage 15 src 14 层最终命名收口（v1.15.0�?*：会�?12 用户拍板 R31 + R32 两条命名最终决议。R31 = strategic_decision 移入 l05_portfolio_construction/strategic/（BlackRock Aladdin P1 模式，业界无机构独立成层）；R32 = l10 命名采用 `l10_compliance`（业界绝大多数顶级机�?Goldman/Citadel/Two Sigma/BlackRock/JPM 都叫 compliance，与 OQ-070 jurisdiction 分片完美契合）。本轮纯决策记忆登记，物�?src/ + ADR-DRAFT-0009 + 03-AA 待架构终局后一次性同步（备忘清单已写�?Stage 15 末尾"未来同步任务"）。新增结�?R31-R32；OQ-073 同步关闭�?|
| 2026-04-19 | **Stage 16 03-AA 微调 + OQ 收尾（v1.16.0�?*：S14 Phase 1 执行�?1) R31/R32/OQ-073 决议落盘�?`03-application-architecture.md` §4.1（l10_compliance / l11_ml_platform / l12_system_telemetry / l13_experiment_pipeline 完整子模块清�?+ 14 层分层体系）�?2) R33 = L12 命名 `l12_system_telemetry` 最终锁定（OQ-030 closed）；(3) R34 = 14 层对标证据落盘到 03-AA 附录 A�? 家顶级机构完整对比（OQ-068 closed）；(4) R35 = meta_strategy 归属 `l05/meta_router/` 决策入档（OQ-023 closed）；(5) J5 L00 ACL 显式化补充到 §4.1 L00 `connectors/` 说明（H8 深化前置）�?3-AA 版本 v1.6.0 �?v1.7.2；OQ register v2.14.0 �?v2.15.0�? OQ closed）�?|
| 2026-04-19 | **Stage 17 G1 新建 Data Architecture 视图（v1.17.0�?*：S14 Phase 2 子任�?2.1 执行。经 agent-transcripts 考古（`cda60b89` 等）确认 TOGAF DA 视图此前缺位�?2-IA 全篇仅讲 docs/ 抽屉，不含业务数据对象），新�?`05-data-architecture.md` v1.0.0�?1 章节，含 19 条数据实体清�?/ 三维分类 / PIT 三字段铁�?/ �?Survivorship 查询契约 / 三层血缘模�?/ MDM 三件�?/ 五类数据质量断言 / 保留归档矩阵 / 与其他视图边界）。新增结�?R36（DA 独立成视图，新建非迁移；R 编号�?R33 调整�?R36 �?R33 已被 L12 命名占用）。`target-architecture/README.md` v1.1.0 �?v1.2.0 同步更新文档清单与导航�?|
| 2026-04-19 | **Stage 18 批次 A 完成——G3/G2/G4/G5 四张视图就位（v1.18.0�?*：S14 Phase 2 批次 A�?.2+2.3+2.4+2.5）执行�?1) G3=新建 `07-integration-architecture.md` v1.0.0（集成风格�? + 拓扑 Mermaid + 契约治理 + ACL 策略 + Event Backbone 占位，R37）；(2) G2=新建 `06-security-architecture.md` v0.1.0（skeleton�? 节安全域占位 + 8 �?Activation Triggers，R38）；(3) G4=新建 `08-operations-architecture.md` v0.1.0（skeleton�? 运维�?+ 11 �?Runbook 占位 + 8 �?Activation Triggers，R39）；(4) G5=`target-architecture/README.md` v1.2.0→v1.3.0（文档清�?3 行，阅读顺序更新�?00�?1�?2�?5�?3�?7�?4�?6�?8，视图依赖图 Mermaid 升级，新�?§4bis Skeleton 说明，R40）。TOGAF 8 视图（BA/IA/DA/AA/TA/SEC/INTEG/OPS）全部在 target-architecture/ 就位。阶�?2 五张视图�?.1-2.5）全部完成，批次 A 收口。新增结�?R37/R38/R39/R40�?|
| 2026-04-19 | **Stage 19 批次 B 完成—�?1-BA.md v1.1.0 补齐 RACI/VSM/SLA 三大 TOGAF 核心构件（v1.19.0�?*：S14 Phase 2 批次 B�?.1+3.2+3.3）执行，一�?Opus 会话连做三任务�?1) **H4** = §2 Stakeholder �?4 行扩展为 12 行（S1-S12 �?AI Operators 预留�? 新增 §2.2 RACI 矩阵�?8 活动 × 12 stakeholder，每行唯一 A �?TOGAF/PMI 铁律�? §2.3 "单人+AI 协同" 5 条铁�?+ §2.4 边界（R41）；(2) **H1** = §4 升级为完�?Value Stream Map：�?.1 Mermaid VSM�? 阶段 10 节点含反馈回路与横向治理�? §4.2 stage-level 10 �?LT/PT/%C&A 指标�?+ §4.3 5 �?Handoff 契约 + §4.4 精益七大浪费识别 6 个瓶�?浪费�?+ §4.5 横向治理（R42）；(3) **H3** = §5 NFR 升级�?SLA/SLO/SLI 矩阵：�?.1 定�?NFR + 3 条边界原�?+ §5.2 **8 条量�?SLO**（Data Freshness p99 180s / Signal Gen p99 90s / Order Submit p99 30s / Backtest TAT p95 30min / Factor Refresh EOD+90min / Availability 99.9% 市场时段 / Data Quality Completeness 99.5% + Consistency 99.9% / Audit append-only 100%）每条标 SLI 测量方法 + 📌�?4-TA §10 Observability H14 引用�?+ §5.3 SLA 现实（仅 iFinD 真合同）+ §5.4 4 条重写触�?+ §5.5 边界（R43）。`01-business-architecture.md` v1.0.0 �?v1.1.0（frontmatter related_rationale +R41/R42/R43，related_open_questions +OQ-063）。新增结�?R41/R42/R43�?|
| 2026-04-19 | **Stage 24 批次 G 完成—�? 份视�?Architecture Runway 章节就位（v1.23.0�?*：S14 Phase 2 批次 G�?.1 S2 + 9.2 S3 + 9.3 S4 + 9.4 S5 + 9.5 S6）执行，一�?Sonnet 会话连做 5 �?Runway 模板化任务。先决条件：批次 F �?+ S1 产出（p3-blueprint-index.md�?2 条）确认 ✅。R 号从 R59 起（任务书写�?R59-R63 与实际一致）�?1) **S2** = `01-BA.md` §8 Runway�? 条：投委会支�?多基金经理协�?全球宏观/战略联盟/机构级报告，均属 l11_strategic_decision，R59）；(2) **S3** = `02-IA.md` §11 Runway�? 条：多模态因�?ESG 因子/知识图谱自动构建，均�?l02/l09，R60）；(3) **S4** = `03-AA.md` §11 Runway�?2 条，�?6 层分组：l02×4/l03×5/l04(l11)×10/l07×1/l08×3/l09×3，R61）；(4) **S5** = `04-TA.md` §14 Runway�? 条：分布式计�?云原�?边缘计算/多云/区块链审�?SSO/合规技术栈，R62）；(5) **S6** = `00-overview.md` §8 Runway Index（导航表 4 视图 37 �?+ §8.2 激活监控机�?5 步流程，R63）。`01-BA.md` v1.1.0→v1.2.0 / `02-IA.md` v1.2.0→v1.3.0 / `03-AA.md` v1.8.0→v1.9.0 / `04-TA.md` v1.3.0→v1.4.0 / `00-overview.md` v1.0.0→v1.1.0。新增结�?R59-R63�?|
| 2026-04-19 | **Stage 22 批次 E 完成——catalogs 深加工（H2/R4）（v1.22.0�?*：S14 Phase 2 批次 E�?.1 H2 + 7.4 R4）执行，一�?Sonnet 会话连做 2 �?catalog 任务�?1) **H2** = `catalogs/business-capability-map.md` v1.0.0→v1.1.0：新�?Maturity（L1-L5 五级定义�? Investment Intensity（Low/Medium/High/Critical 四档�? 判断理由三列�?0 �?Capability 全部填充（C01-C10，覆�?Critical: C01/C02/C04/C08 / High: C03/C05/C07 / Medium: C06/C10 / Low: C09），R57�?2) **R4** = 新建 `catalogs/technology-landscape.md` v1.0.0（EA-ARCH-CATALOG-006）：ThoughtWorks Tech Radar 五象限（Adopt 12�?Trial 9�?Assess 10�?Hold 6�?Build 6条）+ 数据源专�?5�?+ LLM Provider 专题 4�?+ §8 刷新记录（每 3 个月一次）；`technology-standards.md` frontmatter `superseded_by` 更新 + 文件顶部重定向注释；R58。新增结�?R57/R58�?|
| 2026-04-19 | **Stage 21 批次 D 启动—�?.0 行数闸门判断与方�?D 采纳（v1.21.0 开篇）**：S14 Phase 2 批次 D 启动前强制闸门。数据核实：03-AA 当前 738 行（�?590/653 历史数字），预估增量 120 行，终点 858 行，�?1000 阈�?142 行缓冲。OQ-072 三条件命�?0/3（架构终局未锁 / 行数未超 / 无下沉计划批准），严格规则下并未硬触发。采�?*方案 D "最小必要下�?**：现�?§4.1 零重写，批次 D 新增的重型深度内容（H8/H9/H10 详情）从一开始直接写�?`by-domain/src-domain/` 下三�?design-brief 文件（`ocp-extension-points.md` / `fault-tolerance-matrix.md` / `idempotency-design.md`），父视图只保留"机制可视�?+ 决策摘要 + 引用�?；�? 幂等 Mermaid 时序图保留父视图�?*src-domain �?skeleton v0.1.0 �?v1.0.0 active，OQ-072 双轨制首次实质兑�?*。新增结�?R49（闸门判�?+ 方案 D 决策）；R50-R56 待批�?D 各子任务完成后顺次追加�?|
| 2026-04-19 | **Stage 20 批次 C 完成—�?2-IA + 04-TA 深加工（v1.20.0�?*：S14 Phase 2 批次 C�?.1 K1 + 5.1 H12 + 5.2 H13 + 5.3 H14 + 5.4 K7）执行，一�?Sonnet 会话连做 5 任务�?1) **K1** = `02-IA.md` §9 `07_sre_and_platform_ops` �?deferred 升为 planned，新�?3 条激活条件（R44）。`02-IA.md` v1.1.0 �?v1.2.0�?2) **H12** = `04-TA.md` §6 Deployment Diagram 填充：�?.1 Phase 1 单机 Mermaid 图（开发机 + Python 进程 + CI 节点 + 外部网关 + 网络边界表）+ §6.2 Post-Activation 云拓扑图（应�?数据/OTel/调度节点 + 6 维度对比表）+ §6.3 抽屉状态（R45）�?3) **H13** = `04-TA.md` §9 Environment Matrix 新建�? 环境（Dev/UAT/Staging/Prod）�?6 维度（数据源/LLM/资金/监控/审批/回退）矩�?+ §9.3 三道晋级门禁（R46）�?4) **H14** = `04-TA.md` §10 Observability Architecture 新建：�?0.1 三类 Metrics（业�?6 �?技�?4 �?基础设施�? §10.2 结构�?JSON 日志三级体系（App/Audit/Security + 4 环境保留策略�? §10.3 分布式追踪覆盖面（策略→信号→下单→成交 8 �?Span + Attribute 标准 + 3 场景采样）（R47）�?5) **K7** = §10.4 OTel 集成方案：Python SDK �?.20 + 本地 Agent Collector 配置 + Prometheus/Tempo/Loki Exporter + 尾部采样配置 + docker-compose 可观测性栈参考（R48）。`04-TA.md` v1.1.0 �?v1.2.0。新增结�?R44/R45/R46/R47/R48，同步回�?01-BA §5.2 的所�?📌�?4-TA §10 引用锚�?|
