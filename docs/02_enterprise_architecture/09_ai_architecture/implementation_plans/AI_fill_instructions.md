---
ttl: permanent
doc_type: architecture_view
title: AI 架构施工图填充指令集
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.3.0"
date: 2026-08-17
topic: ai_architecture_fill_sop
scope: 09_ai_architecture
---

# AI 架构施工图填充指令集

> **本文定位**：18 篇 AI 架构骨架文档的填充 SOP——为每个骨架文档提供独立、可循环、可并发的填充指令。
>
> **与 AI_review_instructions.md 的区别**：AI_review 是"审查已有内容"（已有内容查缺补漏），本指令集是"填充空骨架"（从 why→how 逐层填入）。
>
> **与交易决策侧的关系**：AI 层设施依赖交易决策侧业务模块（如策略定义、仓位算法、风控设施）。填充时引用交易决策侧文档**只读不改**，发现需同步改的记在本文档「开放问题」节。
>
> **编号规则**：本指令集使用 AI-FILL-01 ~ AI-FILL-18 编号，与交易决策侧 AI-01 ~ AI-23 不冲突（不同目录/不同任务）。

---

## 0. 通用规则（所有填充 AI 必须遵守）

1. **三层分治**：implementation_plan 只写 why（决策推理）和 how（施工步骤），不写 what is 的实现细节（代码级细节由 blueprint/代码维护）。引用用稳定 path/blueprint_id（禁止 node_id/edge_id）。
2. **文档规范**：遵循 `01_design_memo_management_spec §4`——frontmatter 字段集（ttl/doc_type/title/owner/language/status/version/date/topic/scope）、末尾必须有「修订记录」节、必须有「开放问题/待定问题/待裁定」等价节。
3. **不破坏交叉引用**：含 `#L行号` 锚点的引用不得断裂；章节编号不强制统一；不为"结构统一"重排已有章节。
4. **修订升版本**：改动后升 version（骨架填充完成→0.2.0，小改 0.x.1，大改→0.(x+1).0），修订记录补一行（日期+版本+改了什么+为什么改）。
5. **过度工程红线（判定基准：system_charter §2 硬边界 + 施工方式）**：以 [system_charter.md §2 硬边界约束](../../04_architecture_principles_decisions/system_charter.md#L61-72) + 实际施工方式为唯一判定基准——①约束一人力：1 人全栈开发+AI 协作者，代码 100% AI 生成；②施工方式：1 人在 TRAE 编译器上用多 AI 多对话并发施工；③约束二硬件：单机 PC 工作站（i7-12700KF / RTX 3090 24GB 显存<90% / 64GB RAM / 30Mbps 网络），无集群/K8s；④约束三资金：个人资金双账户（实盘+QMT 模拟），miniQMT 10笔/秒、Tick=3秒；⑤约束四规则：T+1、涨跌停、融券受限、日频及以上根频率；⑥约束五运维：单机部署无热备家用环境，RTO<5分钟；⑦约束六范式：AI 生成代码需交叉验证+依赖锁定+自治熔断。凡是超出这些硬边界的机制/设计 = 过度工程，一律去掉或降级；**远期工程不算过度工程**——已显式标注 P4/P5/远期愿景/待裁定的予以保留，但远期属性必须在文档中明确可见。
6. **搜索约束**：WebSearch 限定 2026 年（尤其 2026-07/08），找最新研究/实践/开源实证；找到的更好算法登记到文档「考虑过的替代方案」或「前沿演进方向」节，不直接替换已定决策（已定决策修订需升版本+记理由）。
7. **循环填充（含 git 提交闭环）**：每轮做完整闭环（盘点→填充→验证→清理→提交），发现的问题/缺失**更新修复后立即提交**。提交必须走 GitCommitGateway（`python scripts/git_commit.py`，串行锁+stash 隔离，见 66 号备忘），**禁止裸 `git commit`，禁止 `--no-verify` 绕过门禁**；若 Gateway 不可用，只 `git add <你修改的文件>` 暂存并在「开放问题」节标注「待 Gateway 提交」，不擅自裸提交。提交后重新通读全文再查一轮；如此循环，直到**问题数量=0 且缺失功能/模块数量=0**（连续 1 轮零改动确认）= 任务完成。
8. **不擅自定决策**：需人决策的开放问题标在「待定问题」节，AI 不替人拍板；已 active 的定稿决策如要推翻，必须升大版本+写推翻理由+标「待裁定」。
9. **⚠️ Git 安全铁律（#ARCH-GIT-CLEAN-GUARD-FIX）**：
   - **每轮修改后立即 `git add <你修改的文件>`**——staged 文件不会被 `git clean -fd` 删除。每完成一轮修改必须执行，不可跳过。
   - **禁止执行以下危险命令**：`git clean`、`git clean -fd`、`git reset --hard`、`git checkout --`、`git restore`、`git stash`、`git checkout .`
   - **如需清理工作区**：只能用 `git add` 把文件 staged，不能删除任何文件。
   - **如需丢弃修改**：标在文档「开放问题」节等用户决策，不擅自用 git 命令丢弃。
10. **⚠️ 文件锁使用（防止跨 AI 冲突）**：
    - **修改文件前先加锁**：`python scripts/lock_files.py acquire <file> <session_id>`
    - **完成修改后释放锁**：`python scripts/lock_files.py release <file> <session_id>`
    - **检查文件是否被锁**：`python scripts/lock_files.py check <file>`——返回 FREE 才能修改
    - **session_id 用法**：用 AI-FILL-XX 编号作为 session_id
    - **锁冲突时**：如果 check 返回 LOCKED，等待 5 分钟后重试，不要强制修改
11. **⚠️ 基础设施盘点（前置必做，第 1 轮核心任务）**：
    - 全面扫描项目代码和配置，找出与本文档主题相关的**所有**已建设施、配套组件、规则指令，包括：代码模块、配置文件、Schema 定义、注册表条目、测试文件、脚本工具、前端组件、治理规则、其他文档引用。
    - 在文档「已施工设施盘点」节按类别列出：| 类别 | 路径/位置 | 内容简述 | 状态（production/draft/deprecated）|
    - 确保读者从文档就能知道：这个功能在项目里有哪些设施、配套与规则指令。
12. **⚠️ 填充纪律**：骨架文档已有 frontmatter + 空节模板（§2 背景 / §3 设计决策 / §4 施工计划 / §5 不做什么 / §6 开放问题）。填充时：
    - **§2 背景**：写项目处境、核心问题、约束条件、已施工设施盘点（why 我们面临什么问题）
    - **§3 设计决策**：写 why（为什么选择这个方案，考虑过哪些替代方案），不写 what is（实现细节）
    - **§4 施工计划**：写 how（具体施工步骤、优先级、验收标准、Phase 0→3 分阶段），可引用 blueprint 但不说代码怎么写
    - **§5 不做什么**：明确范围边界，列出超出范围的内容（尤其过度工程项）
    - **§6 开放问题**：列出需人裁定的开放问题，不替人决策
    - **禁止行为**：禁止填入无法施工的模糊描述（如"未来可以考虑"）、禁止填入与现有代码矛盾的假设、禁止删除骨架已有的 frontmatter/主题组信息/修订记录结构
13. **⚠️ 交易决策侧文档只读不改**：本指令集涉及的 18 篇文档全部在 `09_ai_architecture/` 下。填充时如需引用 `07_trading_decision_architecture/design_memos/` 下的文档（如 20_first_batch_strategies / 30_multi_strategy_concurrency / 62_business_registry_construction 等），**只读不改**。发现需同步改的，记在本文档「开放问题」节标「待用户裁定」。
14. **⚠️ 07_trading_decision_architecture 侧审计收口期间特殊纪律**：另一 AI 正在对 AI-AUDIT15/17/19/20 做审计收口，merge 回 dev 前可能修改交易决策侧文档。填充 AI 引用交易决策侧文档时：①只用稳定文件名（禁止行号锚点）；②如发现引用内容已被审计 AI 修改，记在本文档「开放问题」节；③绝不修改交易决策侧任何文件。
15. **⚠️ 实测纪律（反幻觉铁律）**：文档中所有数量、清单、路径、状态一律实测——用 LS/Glob/Grep/Read 实际验证后写入，禁止凭记忆/推测报数。「已施工设施盘点」的每一行必须是实际验证存在的路径；文件/模块数量以实际扫描为准（如 intelligence_governance 文件数以 LS 实测为准，不写"约 20 个"）；引用代码事实必须能给出验证命令或读取位置。每条结论基于实际读取/检索/验证。
16. **⚠️ 真源唯一与向内收（防噪音铁律）**：每个主题在全目录只允许一个真源文档——施工顺序/解锁点的真源是 00_index.md §5，外部对标的真源是 01 号文，资产盘点的真源是 02 号文，各专题细节的真源是 03~17 号文。写入任何内容前先搜索 00/01/02 是否已有：已有→用链接引用，**禁止复制内容**；部分已有→扩展而非重复；没有→才写入。禁止双向同步，禁止同一事实两处维护。禁止创建任何报告/附属文件（所有产出只进你负责的那一篇文档）。新增编号（开放问题号/解锁点号）前先全目录 Grep 查重。
17. **⚠️ 红蓝对抗验证轮（收尾前必做）**：最后一轮对自己填充的内容做对抗测试——红队逐条质疑：这个路径真实存在吗？这个数字实测过吗？这个设计与 system_charter §2 约束矛盾吗？这个内容与 00/01/02 重复吗？这个接口在依赖文档里有定义吗？蓝队逐条给出证据（验证命令+结果摘要），无法给出证据的内容一律删除或降级为「开放问题」。
18. **可发现性自检**：填充完成后确认：①本文档已从 00_index.md §5.2 目录树可达（链接正确）；②frontmatter 的 topic/scope/title 与实际内容一致；③本文档引用的其他文档链接全部有效（用 LS 验证目标文件存在）。新进项目的 AI 必须能通过 00_index 找到本文档。
19. **施工计划的 depgraph L1 铁律**（仅当文档涉及新建模块/依赖变更时适用）：§4 施工计划中凡涉及新建模块的步骤，第一步必须是"用 apply_depgraph 将依赖关系登记到 depgraph 设计态（status=planned）"，最后一步必须是"验证通过后 status planned→production"。禁止出现"先施工后补登记"的计划。纯信息类文档（01/02/03/17）无此要求。
20. **收尾三问（任务结束前必答，写入返回结果）**：①本文档最终落盘状态是否已进程外核实（git diff / git status / Read 回读，不信工具回显）？②是否已 Gateway 提交并给出 commit hash？③是否全程未产生临时文件（_probe_/_test_/临时脚本/测试 log 一律不留仓）？三问任一答"否"则不得宣布完成。

---

## 0.5 填充分类与跳过门（先于一切工作）

每个填充 AI 启动后先判定本文档类型，输出"适用条款清单+跳过条款清单+跳过理由"，后续按类型决定执行项：

| 类型 | 文档 | 跳过门 |
|---|---|---|
| 索引类 | 00 | 只更新 §5/§6 及修订记录，不重写其他节；规则 19 N/A |
| 信息库类 | 01 | 规则 19 N/A；WebSearch 轮必做不可跳 |
| 盘点类 | 02 | 规则 19 N/A；规则 15（实测纪律）最高优先级 |
| 裁定类 | 03 | 规则 19 N/A；禁止给出未授权裁定，选项分析+标「待裁定」即可 |
| 施工类（涉新模块） | 04/06/07/09/10/11/12/13/14/15/16 | 全部规则适用；规则 19 必做 |
| 施工类（治理/整合） | 05/08 | 规则 19 仅当施工计划涉新模块时适用 |
| 路线类 | 17 | 规则 19 N/A；依赖状态检查（03~16 填充进度）必做 |

---

## 1. 18 篇文档分配总表与施工顺序

### 1.1 轨道划分（5 条并行轨道）

> 轨道内串行（依赖解锁），轨道间并行（无依赖）。每条轨道 1~4 个 AI，可独立开工。

```
轨道 A：前置与基础设施（P0，无业务依赖，立即开工）
  AI-FILL-03 → AI-FILL-04 → AI-FILL-08 → AI-FILL-10
  03域边界 → 04AutoRuntime → 08多AI并发治理 → 10LLM基础设施

轨道 B：元设计与安全（P1，依赖轨道 A，可部分并行）
  AI-FILL-05 → AI-FILL-06 → AI-FILL-07 → AI-FILL-09
  05包整合 → 06模型画像流水线 → 07ContextEngine → 09LLM安全栈

轨道 C：自我进化层（P1，依赖轨道 B）
  AI-FILL-11 → AI-FILL-12 → AI-FILL-13
  11证据技能路由 → 12自反Agent+多Agent → 13模块工厂

轨道 D：执行与横切层（P1，依赖轨道 C + 交易决策侧业务模块）
  AI-FILL-14 → AI-FILL-15 → AI-FILL-16
  14执行层 → 15自治边界风险 → 16AI安全+运维

轨道 E：信息与路线（随时可并行，信息库不阻塞施工）
  AI-FILL-01 + AI-FILL-02 + AI-FILL-17
  01外部对标 + 02资产盘点 + 17分阶段路线

轨道 F：总索引更新（依赖所有轨道至少完成第 1~2 轮填充）
  AI-FILL-00
  00_index.md 更新施工顺序和解锁点
```

### 1.2 解锁点定义

| 解锁点 | 条件 | 解锁文档 | 说明 |
|---|---|---|---|
| U1 域边界就绪 | 03 完成 | 04, 05, 08 | AI 层域归属裁定后，才能确定设施归属 |
| U2 基础设施就绪 | 04 + 10 完成 | 06, 07, 09, 11 | AutoRuntime + LLM 基础设施是上层能力地基 |
| U3 画像流水线就绪 | 06 完成 | 11 | 模型路由依赖画像→考试→护照链路 |
| U4 自我进化层就绪 | 11 + 12 + 13 完成 | 14 | 执行层 Agent 依赖自我进化能力 |
| U5 执行层就绪 | 14 完成 | 15 | 自治边界需知道有哪些 Agent 才能定边界 |
| U6 安全层就绪 | 09 + 15 完成 | 16 | AI 安全+运维需 LLM 安全栈和自治边界先就位 |
| U7 业务模块就绪（交易决策侧） | G04 策略定义完成 | 14 业务 Agent 细化 | 业务 Agent 需策略载体才能执行 |
| U8 注册表就绪（交易决策侧） | 62 号注册表 P0 完成 | 13 模块工厂 Phase 0→1 | 模块工厂依赖 factor/strategy 注册表 |

### 1.3 文档分配明细

| AI-FILL | 负责文档 | 复杂度 | 预计行数 | 说明 | 关键依赖 |
|---|---|---|---|---|---|
| AI-FILL-00 | 00_index.md | 中 | 400~600 | 更新施工顺序+解锁点，非从零填充 | 所有其他文档第 1~2 轮 |
| AI-FILL-01 | 01_external_benchmark_analysis.md | 高 | 1500~2000 | 已有框架，补详细对标分析 | 无（信息库） |
| AI-FILL-02 | 02_design_asset_inventory.md | 高 | 1500~2000 | 已有框架，补资产映射+缺口 | 无（盘点） |
| AI-FILL-03 | 03_domain_boundary_definition.md | 中 | 800~1200 | 域归属裁定 | depgraph 73 域 |
| AI-FILL-04 | 04_autoruntime_core_build.md | 高 | 1500~2000 | 五层同心圆施工映射 | 03 域边界 |
| AI-FILL-05 | 05_intelligence_governance_consolidation.md | 高 | 1200~1500 | ~20 文件整合方案 | 03 域边界 |
| AI-FILL-06 | 06_model_profiling_pipeline.md | 中 | 800~1200 | 画像→考试→护照→门控 | 10 LLM 基础设施 |
| AI-FILL-07 | 07_context_engine_build.md | 中 | 800~1200 | 上下文注入管道 | 04 AutoRuntime |
| AI-FILL-08 | 08_multi_ai_concurrency_governance.md | 中 | 800~1200 | 会话隔离/git安全/提交队列 | 无（当前施工方式） |
| AI-FILL-09 | 09_llm_security_integration.md | 高 | 1200~1500 | L0~L8 纵深防御 | 10 LLM 基础设施 |
| AI-FILL-10 | 10_llm_infrastructure.md | 高 | 1500~2000 | 三层运行时+MCP+推理优化 | 04 AutoRuntime |
| AI-FILL-11 | 11_evidence_skill_router.md | 高 | 1500~2000 | 证据关联+技能库+模型路由 | 06 画像流水线 |
| AI-FILL-12 | 12_reflexion_multi_agent.md | 高 | 1500~2000 | 自反Agent+多Agent协作 | 11 证据技能路由 |
| AI-FILL-13 | 13_module_factory.md | 极高 | 2000~2500 | 核心独创，复杂度最高 | 12 自反Agent + 62 号注册表 |
| AI-FILL-14 | 14_execution_layer.md | 高 | 1500~2000 | 治理/业务/算法/自我迭代 Agent | 11/12/13 + G04/G12 |
| AI-FILL-15 | 15_autonomy_boundary_risk.md | 高 | 1200~1500 | 自治边界+Drift+Agent风险 | 14 执行层 |
| AI-FILL-16 | 16_ai_security_ops.md | 高 | 1500~2000 | AI安全+自治运维闭环 | 09 + 15 |
| AI-FILL-17 | 17_phase_roadmap.md | 中 | 800~1200 | Phase 0→3 详细路线 | 03~16 至少骨架填充完成 |

> **合计**：18 个 AI-FILL，覆盖 18 篇文档，5 条轨道并行。

---

## AI-FILL-00 指令（负责 00_index.md 更新）

```
你是 ZephyrAlpha 项目的 AI 架构总索引维护 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】更新 1 篇总索引文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\00_index.md

【文档性质】这是 AI 层的总结构设计文档（architecture_design），不是从零填充，而是**在现有 v0.5.0 基础上更新施工顺序和解锁点**。现有内容（目标架构图、外部框架速览、核心设计、约束）保持不变，重点更新 §5 目录结构（增加解锁点标注）和 §6 待办（增加施工顺序）。

【背景知识】
- 01 号规范：§4.1 段位编号制；§4.4 施工总案类按"目标→现状→改动→验证→不做"组织
- 本指令集 §1.1 轨道划分和 §1.2 解锁点定义是更新依据
- 交易决策侧 00_index_trading_decision.md §4 依赖关系图是 AI 层设施的业务解锁依据

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读取所有其他 17 篇文档的当前状态
1. 用 Read offset/limit 快速读取 01~17 号文的 frontmatter + 主题组信息 + 开放问题（每篇读前 30 行）
2. 记录每篇文档的 status（draft/骨架/已填充）、version、开放问题数量
3. 判断哪些文档已完成第 1~2 轮填充（§2 背景 + §3 设计决策已填），哪些还是空骨架

■ 第 2 轮：更新 §5 目录结构
1. 在 §5.1 细分支预估的每个文档后增加「状态/解锁点」标注：
   - 例：├── 03_domain_boundary_definition.md     ← 域边界 [U1] draft v0.1.0
2. 在 §5.2 目录树的每个文档后增加「轨道+解锁点」标注
3. 新增 §5.3 施工顺序图（文字版，用解锁点连接）

■ 第 3 轮：更新 §6 待办
1. 将现有 8 条待办按施工顺序重新排序
2. 增加解锁点相关待办（如"等待 62 号注册表 P0 完成以解锁模块工厂"）
3. 增加与交易决策侧的联动待办（如"G04 策略定义完成后更新 14 号业务 Agent"）

■ 第 4 轮：一致性与交叉引用审查
1. 核对 §5 标注的文档编号与实际文件是否存在
2. 核对解锁点定义与 §1.2 是否一致
3. 核对交易决策侧文档引用是否使用稳定路径（禁止行号锚点）

■ 第 5 轮：过度工程审查
1. 检查新增内容是否引入过度工程（如新增文档、新增层级）
2. 00_index.md 本身不应膨胀超过 600 行——如超过，考虑将部分内容拆分到 01/02 号文档

■ 第 6 轮：文档质量与规范符合性
1. frontmatter：ttl/doc_type/title/owner/language/status/version/date/topic/scope 是否齐全
2. 修订记录：本次更新升 v0.6.0，补一行变更说明
3. 开放问题：如有新增开放问题，补入 §7

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：本轮发现的问题是否全部修复？
- 若有未修复：更新修复 → 提交 git → 进入下一轮
- 若本轮零发现零修复，再跑一轮确认——连续两轮零发现，任务结束
- 升版本号在修订记录登记（v0.5.0→v0.6.0）

■ 约束
- 只改 00_index.md 本身
- 不改 01~17 号文的内容（只读取状态）
- 不改交易决策侧任何文档
- 引用其他文档时只读不改
- 不擅自新增骨架文档（18 篇已固定）
```

---

## AI-FILL-01 指令（负责 01_external_benchmark_analysis.md）

```
你是 ZephyrAlpha 项目的 AI 架构外部对标分析 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇信息库文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\01_external_benchmark_analysis.md

【文档性质】这是外部顶级框架分析的信息库。已有 v0.4.0 框架（量化社区/Vibe Coding/GitHub/机构实践四栏速览+模块工厂落地性评估），需**深度填充各框架的详细分析、与本项目的映射关系、前沿演进方向**。文档超大（已有内容），需用 offset/limit 分段读或 Grep 定位章节。

【背景知识】
- 01 号规范：§4.4 信息库类按"来源→分析→映射→不做"组织
- 00_index.md §2 已有速览表格，本文档负责深度展开
- 模块工厂评估见 01 号文 §5，需保留并深化

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 用 Read offset/limit 分段读 01 号全文（每段 1500 行），或用 Grep 定位 H2 章节逐段读
2. 盘点已有内容：哪些框架已有详细分析，哪些只有一句话速览
3. 扫描 src/zephyr/intelligence/ 下已有实现，判断哪些外部框架已有对应代码
4. 读 00_index.md §2 确认速览表格与本文档的对应关系

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：更新"已有分析框架数量/深度"现状
2. §2.2 核心问题：哪些框架值得深入对标？哪些只需一句话？
3. §3.1 量化社区深度分析：AQuA/NeMo/TiMi/AlphaQuanter/AI Agent Swarm 各补 200~300 字 why（为什么选择关注这个框架、具体启示、与本项目的差距）
4. §3.2 Vibe Coding 深度分析：Karpathy 三层架构/Zenera/VibeDev 各补 200~300 字
5. §3.3 GitHub 开源深度分析：claude-flow/CrewAI/Hermes/Qualixar 各补 200~300 字
6. §3.4 机构实践深度分析：Man Group/Balyasny 各补 200~300 字
7. 每个框架增加「对本项目的映射」小节：具体哪个 AI 层设计受此框架启发

■ 第 3 轮：What 层填充（§4 施工计划）——信息库无施工计划，改为"前沿演进方向"
1. 新增 §4「前沿演进方向」：2026 年 8 月最新研究/开源动态
2. 每个框架增加「考虑过的替代方案」：为什么没选其他类似框架

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 明确本文档不做代码实现细节（只分析不施工）
2. 明确不做框架的完整复现（只取启示）
3. 明确不做远期框架的深度评估（P4/P5 标注）

■ 第 5 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"AQuA Princeton 2026"验证 IC=0.190 Sharpe=+2.50 参数
2. 搜"NVIDIA NeMo agent 2026"验证三 Agent 循环
3. 搜"Hermes runtime skill generation 2026"验证工程实现细节
4. 搜"Qualixar OS model routing 2026"验证 Q-learning 路由
5. 搜"AI agent swarm quant trading 2026"验证 42.5% 交易量数据

■ 第 6 轮：过度工程审查
1. 检查是否有框架分析超出"个人项目可借鉴"范围（如需集群/多团队的框架，降级为远期参考）
2. 检查是否有分析深度过度（如完整论文复现计划 = 过度工程）
3. 模块工厂落地性评估是否保持务实（已移除成功标准指标，保留定性评估）

■ 第 7 轮：一致性与交叉引用审查
1. 与 00_index.md §2 速览表格一致性：本文档深度分析是否与速览一致
2. 与 02_design_asset_inventory.md 一致性：本文档提到的框架是否已在盘点中登记
3. 与 13_module_factory.md 一致性：模块工厂评估是否与 13 号文档口径一致

■ 第 8 轮：文档质量与规范符合性
1. frontmatter：检查字段齐全
2. 修订记录：填充完成升 v0.5.0
3. 开放问题：如有新增框架待评估，补入开放问题

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束
- 升版本号在修订记录登记

■ 约束
- 只改 01 号本身
- 引用 00_index.md / 02_design_asset_inventory.md / 13_module_factory.md 时只读不改
- 发现其他文档需同步改的，记在 01 号「开放问题」节
- 不擅自定决策（如框架取舍），标「待裁定」
```

---

## AI-FILL-02 指令（负责 02_design_asset_inventory.md）

```
你是 ZephyrAlpha 项目的 AI 架构资产盘点 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇盘点文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\02_design_asset_inventory.md

【文档性质】这是 AI 层设计资产、AI 员工体系、已有域、运行态设施的盘点文档。已有 v0.3.0 框架，需**深度填充各资产的代码实现映射、状态评估、缺口分析**。

【背景知识】
- 01 号规范：§4.4 盘点类按"资产清单→状态→缺口→计划"组织
- 00_index.md §1 目标架构图是盘点依据
- 交易决策侧 62 号注册表是业务资产映射依据

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 用 Read 读 02 号全文（盘点类通常较长，分段读）
2. 全面扫描 src/zephyr/ 下与 AI 相关的所有模块：
   - src/zephyr/intelligence/（所有子目录）
   - src/zephyr/governance/intelligence_governance/
   - src/zephyr/autonomy_core/（context/ memory/ 等）
   - src/zephyr/security/
   - data/brain/（护照/考试结果/记忆等）
3. 扫描 config/ 下与 AI 相关的配置
4. 扫描 docs/03_modules/_cross_layer/ 下与 AI 相关的 blueprint
5. 读 00_index.md §1 目标架构图，核对盘点是否覆盖所有组件

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：更新"AI 层资产覆盖率"现状（已施工/设计/空白 各占多少）
2. §2.2 核心问题：哪些组件已有代码但无文档？哪些有文档但无代码？
3. §3.1 设计资产盘点：每个设计资产增加「代码映射」列（指向 src/zephyr/ 具体路径）
4. §3.2 AI 员工体系：更新各 Agent 的当前状态（production/draft/planned）
5. §3.3 已有域盘点：更新 depgraph 中与 AI 相关的域状态
6. §3.4 运行态设施盘点：更新各设施的实际运行状态

■ 第 3 轮：What 层填充（§4 施工计划）——盘点类无施工计划，改为"缺口填补计划"
1. 新增 §4「缺口分析与填补优先级」：按 P0/P1/P2 列出缺失组件
2. 每个缺口标注：依赖哪个交易决策侧模块（如"业务 Agent 需 G04 策略定义"）

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 明确盘点不做代码审查（只盘点存在性，不评代码质量）
2. 明确盘点不做设计决策（只记录现状，不改架构）
3. 明确盘点范围限 AI 层（不盘点交易决策侧业务模块）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：盘点是否覆盖目标架构图所有组件
2. 与 01_external_benchmark_analysis.md 一致性：盘点中的设计资产是否在对标中有映射
3. 与 05~16 号施工文档一致性：盘点中的组件状态与各施工文档口径是否一致
4. 与交易决策侧 62 号注册表一致性：AI 层引用的注册表是否已登记

■ 第 6 轮：过度工程审查
1. 盘点是否过度详细（如盘点到函数级 = 过度，应到模块级）
2. 缺口分析是否引入过度工程项（如"需要 K8s 部署"= 过度）

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 填充完成升 v0.4.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 02 号本身
- 引用 00_index.md / 01_external_benchmark_analysis.md 时只读不改
- 交易决策侧文档只读不改
```

---

## AI-FILL-03 指令（负责 03_domain_boundary_definition.md）

```
你是 ZephyrAlpha 项目的 AI 架构域边界裁定 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇域边界文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\03_domain_boundary_definition.md

【文档性质】这是 AI 层在 depgraph 中的域边界定义——**裁定哪些域归入 AI 层，AI 层是横切视图还是独立域**。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 裁定类按"问题→选项→依据→裁定"组织
- 00_index.md §4 目录结构提到 depgraph 域划分
- 02_design_asset_inventory.md 提到已有域盘点
- depgraph 现有 73 域，需扫描确定哪些与 AI 层相关

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 depgraph 现有域清单（ Glob d:\ZephyrAlpha\docs\03_modules\ 下所有域目录）
2. 读取与 AI 相关的域 blueprint：
   - _domain_autonomy_core/
   - _domain_intelligence/
   - _domain_ml_train/ / _domain_ml_serve/
   - _domain_knowledge/
   - _domain_security/
   - _domain_orchestrator/
3. 读 00_index.md §1 目标架构图，确定 AI 层涉及的组件
4. 读 02_design_asset_inventory.md §3.3 已有域盘点

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：depgraph 73 域中，AI 相关域的现状（哪些有代码/哪些空壳/哪些边界不清）
2. §2.2 核心问题：Q1 AI 层是横切视图还是独立域？Q2 D_KNOWLEDGE 保留还是合并？
3. §3.1 选项分析：
   - 选项 A：横切视图——不新增域，跨现有域打 AI 标签
   - 选项 B：独立域——新增 D_AI 域，迁入相关模块
   - 选项 C：混合——核心域独立，横切能力跨域
4. §3.2 裁定依据：system_charter 约束、已有代码分布、未来扩展性
5. **注意**：如无法裁定（需用户决策），标「待裁定」，不写假裁定

■ 第 3 轮：What 层填充（§4 施工计划）
1. 如裁定横切视图：写「标签机制」施工计划（如何在 depgraph 中标记 AI 层组件）
2. 如裁定独立域：写「域迁移」施工计划（哪些模块迁入 D_AI）
3. 如混合：写「核心域+横切标签」双轨施工计划
4. D_KNOWLEDGE 处置方案：保留/合并/退役

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做 depgraph 结构重构（只裁定边界，不改全局架构）
2. 不做跨域代码迁移（只出方案，迁移由具体施工文档负责）
3. 不做新域的详细设计（D_AI 如新建，设计由后续文档补充）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：域边界裁定是否覆盖目标架构图所有组件
2. 与 02_design_asset_inventory.md 一致性：盘点中的域状态与本文档裁定是否一致
3. 与 04_autoruntime_core_build.md 一致性：AutoRuntime Core 的域归属是否已裁定

■ 第 6 轮：过度工程审查
1. 新增 D_AI 域是否过度？个人项目 73 域已足够，新增域需有充分理由
2. 横切标签机制是否过度？简单方案 vs 复杂方案

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 03 号本身
- 引用 depgraph / 00_index.md / 02_design_asset_inventory.md 时只读不改
- 不擅自重构 depgraph（只出裁定方案）
```

---

## AI-FILL-04 指令（负责 04_autoruntime_core_build.md）

```
你是 ZephyrAlpha 项目的 AI 架构基础设施施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇基础设施文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\04_autoruntime_core_build.md

【文档性质】这是 AutoRuntime Core（五层同心圆）的施工图。空骨架，需从零填充。AutoRuntime Core 是 AI 层所有能力的运行时底座。

【背景知识】
- 01 号规范：§4.4 施工类按"目标→现状→改动→验证→不做"组织
- 00_index.md §1 基础设施层提到 AutoRuntime Core
- 交易决策侧 30_multi_strategy_concurrency 提到 AutoRuntime 是并发执行底座
- 扫描对象：src/zephyr/autonomy_core/ blueprint、docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 读 docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md（已有蓝图）
2. 扫描 src/zephyr/autonomy_core/ 所有 .py 文件，列出清单和状态
3. 读 00_index.md §1 目标架构图，确认 AutoRuntime Core 的定位
4. 读 03_domain_boundary_definition.md（如已填充），确认域归属

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：AutoRuntime Core 当前实现状态（五层同心圆各层完成度）
2. §2.2 核心问题：哪些层已有代码？哪些层只有设计？哪些层缺失？
3. §3.1 五层架构设计决策：每层 why（为什么这样分层、替代方案是什么）
   - L1 配置层 / L2 服务层 / L3 核心层 / L4 适配层 / L5 驱动层
4. §3.2 与 AI 层的关系：AutoRuntime 如何支撑 AI 自我进化、AI 执行、AI 安全

■ 第 3 轮：What 层填充（§4 施工计划）
1. 按五层逐层写施工计划：每层的 P0/P1/P2 任务、验收标准、依赖
2. 与 10_llm_infrastructure.md 的接口：AutoRuntime 如何承载 LLM 推理运行时
3. 与 07_context_engine_build.md 的接口：AutoRuntime 如何承载 Context Engine
4. Phase 0→3 分阶段：哪些层 Phase 0 可完成，哪些需等上层能力

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做分布式运行时（system_charter 约束二：单机无集群）
2. 不做热备/故障转移（RTO<5 分钟用降级策略，非热备）
3. 不做与交易决策侧业务逻辑耦合（AutoRuntime 是底座，业务逻辑在下游）

■ 第 5 轮：一致性与交叉引用审查
1. 与 blueprint.md 一致性：施工计划是否与蓝图一致
2. 与 00_index.md §1 一致性：定位是否匹配
3. 与 10_llm_infrastructure.md 一致性：接口定义是否对齐

■ 第 6 轮：过度工程审查
1. 五层是否过多？个人项目是否可简化为三层？
2. 每层的抽象是否过度？是否有"为设计而设计"的层？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 04 号本身
- 引用 blueprint / 00_index.md / 03_domain_boundary_definition.md 时只读不改
```

---

## AI-FILL-05 指令（负责 05_intelligence_governance_consolidation.md）

```
你是 ZephyrAlpha 项目的 AI 架构治理包整合 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇治理包整合文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\05_intelligence_governance_consolidation.md

【文档性质】这是 `src/zephyr/governance/intelligence_governance/` 约 20 个文件的整合方案——统一入口、职责边界、与 AI 层的关系。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 整合类按"现状→问题→方案→迁移→不做"组织
- 00_index.md §1 执行层提到治理 Agent
- 扫描对象：src/zephyr/governance/intelligence_governance/ 下所有 .py 文件
- 相关文档：14_execution_layer.md（治理 Agent 施工）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 用 LS + Glob 扫描 src/zephyr/governance/intelligence_governance/ 所有文件
2. 逐文件读取关键 .py 的 docstring / 类定义 / 主要函数（按复杂度选读 5~10 个核心文件）
3. 列出 20 个文件的职责矩阵：| 文件名 | 当前职责 | 状态 | 与其他文件关系 |
4. 读 00_index.md §1 执行层·治理 Agent 的定位
5. 读 03_domain_boundary_definition.md（如已填充），确认 D_ORCHESTRATOR 与 intelligence_governance 的边界

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：20 个文件散落、无统一入口、职责重叠/缺失的现状
2. §2.2 核心问题：Q1 是否需要统一入口？Q2 与 D_ORCHESTRATOR 的边界在哪？
3. §3.1 整合方案：统一入口设计（如 `__init__.py` 暴露公共 API / 新建 facade）
4. §3.2 职责重划：哪些文件合并？哪些拆分？哪些退役？
5. §3.3 与 D_ORCHESTRATOR 的边界裁定：intelligence_governance 做"治理决策"，D_ORCHESTRATOR 做"Agent 编排"（61 号备忘已裁定不做编排，边界需明确）

■ 第 3 轮：What 层填充（§4 施工计划）
1. 整合三阶段：盘点→重划→迁移
2. 统一入口施工：公共 API 设计、向后兼容策略
3. 与 14_execution_layer.md 的接口：治理 Agent 如何调用 intelligence_governance
4. Phase 0：不改动代码，只出文档和统一入口 wrapper

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做大规模代码重构（整合以文档和 wrapper 为主，逐步迁移）
2. 不改 D_ORCHESTRATOR 代码（只裁定边界，不改其他域）
3. 不做 agent 编排系统（61 号备忘已裁定）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：治理 Agent 定位是否匹配
2. 与 03_domain_boundary_definition.md 一致性：域边界是否已裁定
3. 与 14_execution_layer.md 一致性：治理 Agent 与 governance 包的接口是否对齐

■ 第 6 轮：过度工程审查
1. 统一入口是否过度？个人项目 20 个文件是否可直接用，无需 facade？
2. 整合方案是否引入不必要的抽象层？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 05 号本身
- 引用代码 / 00_index.md / 03_domain_boundary_definition.md / 14_execution_layer.md 时只读不改
- 不改 intelligence_governance 包内的任何代码
```

---

## AI-FILL-06 指令（负责 06_model_profiling_pipeline.md）

```
你是 ZephyrAlpha 项目的 AI 架构模型画像流水线施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇模型画像流水线文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\06_model_profiling_pipeline.md

【文档性质】这是模型画像（7 维评测）→ 能力考试（五维评测）→ 能力护照（CapabilityPassport）→ 任务门控（TaskGate）的完整流水线施工。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 流水线类按"输入→处理→输出→验证→不做"组织
- 00_index.md §1 自我进化层提到模型路由
- 已有实现：data/brain/passports/ 已有 10+ LLM 能力护照 JSON、data/brain/*_exam_results.json 已有五维评测结果
- 依赖模块：MOD-INF-034（模型画像器）+ MOD-INF-036（模型能力考试）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 data/brain/passports/ 列出所有护照文件，读 2~3 个样本
2. 扫描 data/brain/ 找 *_exam_results.json，读样本
3. 扫描 src/zephyr/intelligence/model_profiling/ 列出所有文件
4. 读 MOD-INF-034 / MOD-INF-036 的 blueprint（如存在）
5. 读 00_index.md §1 模型路由的定位

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：画像/考试/护照各环节当前实现状态
2. §2.2 核心问题：Q1 画像 7 维与考试五维是否重复？Q2 护照更新频率？
3. §3.1 画像→考试→护照→门控的链路设计 why：为什么分四步、每一步的作用
4. §3.2 7 维 vs 五维的互补性裁定：画像 = 静态能力评估，考试 = 动态任务表现
5. §3.3 护照更新策略：触发式更新 vs 定时更新

■ 第 3 轮：What 层填充（§4 施工计划）
1. 链路打通施工：画像输出→考试输入→护照生成→门控消费
2. 与 11_evidence_skill_router.md 的接口：护照如何驱动模型路由
3. 与 10_llm_infrastructure.md 的接口：画像/考试的运行时环境
4. Phase 0：手动跑通链路；Phase 1：半自动更新护照

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做模型训练（画像只评估，不训练）
2. 不做分布式评测（单机评测，本地模型+API）
3. 不做通用 LLM 评测（只评测与量化交易相关的任务能力）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：模型路由定位是否匹配
2. 与 11_evidence_skill_router.md 一致性：护照→路由接口是否对齐
3. 与 10_llm_infrastructure.md 一致性：运行时接口是否对齐

■ 第 6 轮：过度工程审查
1. 7 维+五维是否过度？个人项目是否需要这么多维度？
2. 护照门控是否过度？简单路由是否不需要门控？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 06 号本身
- 引用 passport/blueprint / 00_index.md / 11_evidence_skill_router.md 时只读不改
```

---

## AI-FILL-07 指令（负责 07_context_engine_build.md）

```
你是 ZephyrAlpha 项目的 AI 架构上下文引擎施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇上下文引擎文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\07_context_engine_build.md

【文档性质】这是 Context Engine（上下文引擎）剩余未实现部分的施工计划。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 施工类按"目标→现状→改动→验证→不做"组织
- 00_index.md §1 执行层提到业务 Agent 需要上下文管理
- 已有实现：src/zephyr/autonomy_core/context/ 有 22 个 .py 文件
- 相关蓝图：MOD-CONTEXT_ENGINE

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 src/zephyr/autonomy_core/context/ 列出 22 个文件，选读 5~8 个核心文件
2. 判断上下文注入管道 build→compress→validate→inject 各环节的实现程度
3. 读 MOD-CONTEXT_ENGINE 蓝图（如存在）
4. 读 00_index.md §1 执行层·业务 Agent 的定位
5. 读 04_autoruntime_core_build.md（如已填充），确认运行时底座接口

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：22 个文件各环节的实现状态（production/draft/空白）
2. §2.2 核心问题：Token 预算管控、上下文压缩、记忆检索的实现程度
3. §3.1 上下文管理设计决策：为什么需要 build→compress→validate→inject 四步
4. §3.2 与 D_INTELLIGENCE 的边界：D_INTELLIGENCE 33 模块做上下文管理，Context Engine 做上下文注入——边界在哪？
5. §3.3 压缩策略：摘要 vs 向量化 vs 关键词提取

■ 第 3 轮：What 层填充（§4 施工计划）
1. 按四步逐环节写施工计划：build（上下文收集）→ compress（压缩）→ validate（校验）→ inject（注入）
2. 缺失环节重点施工（如 compress 未实现，写 compress 的施工方案）
3. 与 14_execution_layer.md 的接口：业务 Agent 如何消费 Context Engine
4. 与 10_llm_infrastructure.md 的接口：上下文如何传递给 LLM 运行时

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做通用对话记忆（只做与量化交易相关的上下文管理）
2. 不做跨会话长期记忆（单会话内上下文，长期记忆由技能库/证据库负责）
3. 不做多模态上下文（只处理文本）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：业务 Agent 定位是否匹配
2. 与 04_autoruntime_core_build.md 一致性：运行时接口是否对齐
3. 与 14_execution_layer.md 一致性：Agent→Context Engine 接口是否对齐

■ 第 6 轮：过度工程审查
1. 22 个文件是否过多？个人项目是否需要这么多上下文组件？
2. 四步管道是否过度？两步（build→inject）是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 07 号本身
- 引用代码 / 00_index.md / 04_autoruntime_core_build.md / 14_execution_layer.md 时只读不改
```

---

## AI-FILL-08 指令（负责 08_multi_ai_concurrency_governance.md）

```
你是 ZephyrAlpha 项目的 AI 架构多 AI 并发治理施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇多 AI 并发治理文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\08_multi_ai_concurrency_governance.md

【文档性质】这是 61/65/66 号备忘的多 AI 并发治理方案施工落地——会话隔离、git 安全、提交队列串行化。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 治理类按"规则→机制→工具→验证→不做"组织
- 00_index.md §1 治理层提到多 AI 协作
- 已有实现：scripts/lock_files.py、scripts/git_commit.py、scripts/git_guard.py、session_worktree.py
- 设计备忘：design_memos/61_lifecycle_multi_ai.md、65_git_safety_governance.md、66_commit_queue_serialization.md

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 读 design_memos/61/65/66 号备忘（分段读，每篇读关键章节）
2. 扫描 scripts/ 下与 git 安全/并发相关的脚本：lock_files.py、git_commit.py、git_guard.py
3. 扫描 src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
4. 评估三件套（会话隔离/git安全/提交队列）各自的施工状态
5. 读 00_index.md §1 治理层·多 AI 协作的定位

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：多 AI 并发施工方式下的实际问题和事故历史
2. §2.2 核心问题：Q1 66 号备忘的提交队列是否已施工？Q2 文件锁是否覆盖全部冲突场景？
3. §3.1 会话隔离设计：worktree 隔离 vs session 隔离的 why
4. §3.2 git 安全设计：guardrails 三层（预防→检测→恢复）
5. §3.3 提交队列设计：串行化机制、冲突解决策略

■ 第 3 轮：What 层填充（§4 施工计划）
1. 三件套逐项施工：会话隔离（已部分实现，补缺口）→ git 安全（已部分实现，补缺口）→ 提交队列（可能未实现，写方案）
2. 与 00_index.md 的接口：多 AI 协作在 AI 层架构中的位置
3. 与交易决策侧 61/65/66 号备忘的对齐：施工计划是否与备忘一致
4. Phase 0：当前施工方式已部分可行，补安全缺口即可

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做 agent 编排系统（61 号备忘 §2.3 已裁定）
2. 不做分布式锁（单机文件锁足够）
3. 不做 git hook 强制拦截（Windows git 2.48.1 限制，用 wrapper 替代）

■ 第 5 轮：一致性与交叉引用审查
1. 与 61/65/66 号备忘一致性：施工计划是否与备忘一致
2. 与 00_index.md §1 一致性：定位是否匹配
3. 与 16_ai_security_ops.md 一致性：git 安全与 AI 安全运维的边界

■ 第 6 轮：过度工程审查
1. 提交队列串行化是否过度？个人项目是否可用简单互斥锁替代？
2. 三件套是否过度？两件套（隔离+锁）是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 08 号本身
- 引用 61/65/66 号备忘 / scripts/ / 00_index.md 时只读不改
- 不改交易决策侧任何文件
```

---

## AI-FILL-09 指令（负责 09_llm_security_integration.md）

```
你是 ZephyrAlpha 项目的 AI 架构 LLM 安全栈施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇 LLM 安全栈文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\09_llm_security_integration.md

【文档性质】这是 LLM 安全栈 L0~L8 纵深防御的集成施工图。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 安全类按"威胁→防御→验证→不做"组织
- 00_index.md §3.3 已有 AI 安全核心设计速览
- 已有实现：docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
- 相关文档：16_ai_security_ops.md（AI 安全+运维）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 读 large_language_model_security/blueprint.md（已有安全蓝图）
2. 扫描 src/zephyr/security/ 下与 LLM 安全相关的模块
3. 读 00_index.md §3.3 AI 安全核心设计
4. 读 10_llm_infrastructure.md（如已填充），确认运行时环境
5. 评估 L0~L8 各层的当前实现状态

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：L0~L8 各层当前实现状态（哪些层已有代码/哪些只有设计）
2. §2.2 核心问题：各层防御的完备性、层间协同、与业务流的集成点
3. §3.1 L0~L8 分层设计 why：每层防御什么威胁、为什么需要这一层
4. §3.2 四层 guardrails（G1~G4）与 L0~L8 的关系
5. §3.3 MCP Triple Gate 与 L0~L8 的映射

■ 第 3 轮：What 层填充（§4 施工计划）
1. 按 L0~L8 逐层写施工计划：每层的 P0/P1/P2 任务、验收标准
2. 与 10_llm_infrastructure.md 的接口：LLM 推理时如何嵌入安全栈
3. 与 16_ai_security_ops.md 的接口：安全事件如何流入运维闭环
4. Phase 0：L0（输入过滤）+ L1（输出审查）优先

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做外部安全服务集成（如第三方内容审核 API——延迟和成本不可控）
2. 不做形式化验证（个人项目用测试+审计替代）
3. 不做零知识证明（已在 00_index 移除，不过度工程）

■ 第 5 轮：一致性与交叉引用审查
1. 与 blueprint.md 一致性：施工计划是否与蓝图一致
2. 与 00_index.md §3.3 一致性：设计口径是否对齐
3. 与 16_ai_security_ops.md 一致性：安全栈与运维闭环的接口

■ 第 6 轮：过度工程审查
1. L0~L8 九层是否过多？个人项目是否可合并为 5~6 层？
2. 某些层（如 L7 供应链安全）是否超出个人项目范围？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 09 号本身
- 引用 blueprint / 00_index.md / 10_llm_infrastructure.md / 16_ai_security_ops.md 时只读不改
```

---

## AI-FILL-10 指令（负责 10_llm_infrastructure.md）

```
你是 ZephyrAlpha 项目的 AI 架构 LLM 基础设施施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇 LLM 基础设施文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\10_llm_infrastructure.md

【文档性质】这是 LLM 基础设施的施工——三层运行时（L1 Trae / L2 Local Ollama / L3 API）、MCP 工具调用、推理优化、模型注册、数据增强。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 基础设施类按"资源→配置→优化→验证→不做"组织
- 00_index.md §1 基础设施层提到三层运行时+MCP+推理优化
- 约束：单 GPU RTX 3090 24GB、网络 30Mbps、无集群
- 已有实现：部分 LLM 调用代码散落在 src/zephyr/

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 src/zephyr/ 下与 LLM 调用相关的模块（Grep "openai\|ollama\|llama\|anthropic"）
2. 扫描 config/ 下与 LLM 相关的配置（API key、模型端点、超时设置）
3. 读 00_index.md §1 基础设施层的定位
4. 读 04_autoruntime_core_build.md（如已填充），确认运行时底座
5. 评估三层运行时（L1/L2/L3）当前实现状态

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：LLM 调用的分散现状、无统一运行时、无推理优化
2. §2.2 核心问题：三层运行时如何分工？MCP 如何动态发现工具？
3. §3.1 三层运行时设计：L1 Trae（云端大模型）/ L2 Local Ollama（本地小模型）/ L3 API（第三方 API）的 why
4. §3.2 MCP 工具调用设计：动态发现 vs 静态注册
5. §3.3 推理优化设计：llama.cpp + GPTQ INT4（显存 14→4GB）的 why
6. §3.4 模型注册设计：MLflow 注册 vs 简单 JSON 配置

■ 第 3 轮：What 层填充（§4 施工计划）
1. 三层运行时统一入口施工：L1/L2/L3 统一 API
2. MCP 工具调用集成：与 04_autoruntime_core_build.md 的接口
3. 推理优化落地：llama.cpp 集成、GPTQ 量化、显存管理
4. 模型注册：MLflow 或轻量替代方案
5. 数据增强：TimeGAN/扩散模型的集成点

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做分布式推理（单机约束）
2. 不做模型训练（只做推理优化）
3. 不做 GPU 集群调度（单卡约束）
4. 不做高并发推理（个人项目低并发）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：基础设施定位是否匹配
2. 与 04_autoruntime_core_build.md 一致性：运行时接口是否对齐
3. 与 09_llm_security_integration.md 一致性：安全栈嵌入点是否对齐
4. 与 11_evidence_skill_router.md 一致性：模型路由的运行时依赖

■ 第 6 轮：过度工程审查
1. 三层运行时是否过度？个人项目是否可简化为两层（本地+API）？
2. MLflow 是否过重？轻量 JSON 配置是否足够？
3. TimeGAN/扩散模型是否过度？简单数据增强是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 10 号本身
- 引用 00_index.md / 04_autoruntime_core_build.md / 09_llm_security_integration.md 时只读不改
```

---

## AI-FILL-11 指令（负责 11_evidence_skill_router.md）

```
你是 ZephyrAlpha 项目的 AI 架构自我进化组件施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇自我进化组件文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\11_evidence_skill_router.md

【文档性质】这是自我进化核心组件的施工——证据关联（假设→证据→迭代引导）、技能库（AutoSkill+Voyager）、模型路由（级联控制器）。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 组件类按"输入→处理→输出→验证→不做"组织
- 00_index.md §1 自我进化层提到证据关联/技能库/模型路由
- 对标：AQuA（证据关联）、Hermes（技能库）、Qualixar（模型路由）
- 依赖：06_model_profiling_pipeline.md（护照驱动路由）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 src/zephyr/intelligence/ 下与证据/技能/路由相关的模块
2. 扫描 data/brain/ 下与证据/技能相关的数据文件
3. 读 00_index.md §1 自我进化层的定位
4. 读 06_model_profiling_pipeline.md（如已填充），确认护照接口
5. 读 01_external_benchmark_analysis.md §AQuA/Hermes/Qualixar 部分

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：证据/技能/路由各组件的当前实现状态
2. §2.2 核心问题：三组件如何协同？证据如何引导迭代？技能如何入库？
3. §3.1 证据关联设计：假设→证据→迭代引导的 why（AQuA 启示）
4. §3.2 技能库设计：AutoSkill + Voyager 的 why（自动生成技能→测试→入库）
5. §3.3 模型路由设计：级联控制器（本地/API 分时分任务）的 why
6. §3.4 三组件协同设计：证据→技能→路由的闭环

■ 第 3 轮：What 层填充（§4 施工计划）
1. 证据关联施工：假设管理、证据收集、迭代引导
2. 技能库施工：技能定义、自动生成、测试验证、入库管理
3. 模型路由施工：级联控制器、护照消费、任务分派
4. 与 06_model_profiling_pipeline.md 的接口：护照如何驱动路由
5. 与 13_module_factory.md 的接口：技能库如何支撑模块工厂

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做通用技能库（只做量化交易相关技能）
2. 不做强化学习路由（单 GPU 约束，用规则+Q-learning 轻量方案）
3. 不做实时证据关联（日频/周频批量处理）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：自我进化层定位是否匹配
2. 与 06_model_profiling_pipeline.md 一致性：护照→路由接口是否对齐
3. 与 13_module_factory.md 一致性：技能库→模块工厂接口是否对齐
4. 与 01_external_benchmark_analysis.md 一致性：对标启示是否落地

■ 第 6 轮：过度工程审查
1. 三组件是否过度？个人项目是否可简化为两组件（证据+路由）？
2. AutoSkill 自动生成是否过度？手动技能定义是否足够？
3. Q-learning 路由是否过度？规则路由是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 11 号本身
- 引用 00_index.md / 01_external_benchmark_analysis.md / 06_model_profiling_pipeline.md / 13_module_factory.md 时只读不改
```

---

## AI-FILL-12 指令（负责 12_reflexion_multi_agent.md）

```
你是 ZephyrAlpha 项目的 AI 架构自反 Agent 施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇自反 Agent 与多 Agent 协作文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\12_reflexion_multi_agent.md

【文档性质】这是自反 Agent（Reflexion Agent）与多 Agent 协作的施工——L1/L2/L3 反思 + PreFlect + Agent-R + 投票优先 + FactorMAD + 涌现检测。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 组件类按"输入→处理→输出→验证→不做"组织
- 00_index.md §1 自我进化层提到自反 Agent 和多 Agent 协作
- 对标：TiMi（数学反思闭环）、FactorMAD（因子挖掘）、R&D-Agent（联合优化）
- 依赖：11_evidence_skill_router.md（证据/技能/路由）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 src/zephyr/intelligence/ 下与反思/多 Agent 相关的模块
2. 读 00_index.md §1 自反 Agent 和多 Agent 协作的定位
3. 读 01_external_benchmark_analysis.md §TiMi/FactorMAD/R&D-Agent 部分
4. 读 11_evidence_skill_router.md（如已填充），确认证据/技能接口
5. 评估 L1/L2/L3 反思、PreFlect、Agent-R 的当前实现状态

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：反思/多 Agent 各组件的当前实现状态
2. §2.2 核心问题：L1/L2/L3 反思如何分工？多 Agent 如何投票？涌现如何检测？
3. §3.1 L1/L2/L3 反思设计：单轨迹反思/同类任务反思/跨任务反思的 why
4. §3.2 PreFlect 设计：预反思 vs 事后反思
5. §3.3 Agent-R 设计：实时反思的频率控制（ReflCtrl）
6. §3.4 多 Agent 投票设计：3-5 Agent 投票→选最优的 why
7. §3.5 涌现检测设计：非预期涌现→告警+介入的 why

■ 第 3 轮：What 层填充（§4 施工计划）
1. L1 反思施工：单轨迹反思（最轻量，先行）
2. L2 反思施工：同类任务反思（需 N=5 次累积）
3. 多 Agent 投票施工：投票机制、结果聚合、冲突解决
4. 涌现检测施工：行为基线、偏差检测、告警介入
5. 与 11_evidence_skill_router.md 的接口：反思结果如何入证据库
6. 与 13_module_factory.md 的接口：反思如何驱动模块优化

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做 agent 编排系统（61 号备忘已裁定，多 Agent = 人调度多会话）
2. 不做实时多 Agent 通信（文件落盘交接，非消息队列）
3. 不做 L3 跨任务反思（Phase 3 远期，需大量数据积累）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：自反 Agent 定位是否匹配
2. 与 11_evidence_skill_router.md 一致性：反思→证据接口是否对齐
3. 与 13_module_factory.md 一致性：反思→模块优化接口是否对齐
4. 与 01_external_benchmark_analysis.md 一致性：对标启示是否落地

■ 第 6 轮：过度工程审查
1. L1/L2/L3 三级反思是否过度？个人项目是否可只做 L1？
2. 多 Agent 投票是否过度？单 Agent + 人工审核是否足够？
3. 涌现检测是否过度？简单规则检测是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 12 号本身
- 引用 00_index.md / 01_external_benchmark_analysis.md / 11_evidence_skill_router.md / 13_module_factory.md 时只读不改
```

---

## AI-FILL-13 指令（负责 13_module_factory.md）

```
你是 ZephyrAlpha 项目的 AI 架构模块工厂施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇模块工厂文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\13_module_factory.md

【文档性质】这是模块工厂（Module Factory）的施工——知识采集→分类→映射→代码生成→验证→入库的完整流水线。**核心独创设计，没有任何已公开系统有此概念**。空骨架，需从零填充。预计行数 2000~2500，是最复杂的文档。

【背景知识】
- 01 号规范：§4.4 流水线类按"输入→处理→输出→验证→不做"组织
- 00_index.md §1 自我进化层提到模块工厂
- 01_external_benchmark_analysis.md §5 有模块工厂落地性评估
- 依赖：62 号注册表（factor/strategy registry）+ 11 号技能库 + 12 号自反 Agent
- 约束：单 GPU、Phase 2 保留人工审核、Phase 3 用 ICL 替代 MAML/EWC

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 读 01_external_benchmark_analysis.md §5 模块工厂落地性评估
2. 扫描 src/zephyr/ 下与模块生成/代码生成相关的模块
3. 读 62_business_registry_construction.md（交易决策侧）§factor_registry / strategy_registry
4. 读 11_evidence_skill_router.md（如已填充），确认技能库接口
5. 读 12_reflexion_multi_agent.md（如已填充），确认反思接口
6. 读 00_index.md §1 模块工厂的定位和约束

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：模块工厂各环节的当前实现状态（知识采集→分类→映射→代码生成→验证→入库）
2. §2.2 核心问题：知识→模块映射的核心独特点是什么？Phase 0→1 的施工路径？
3. §3.1 知识采集设计：从哪里采集知识（论文/开源/社区/内部经验）
4. §3.2 知识分类设计：如何分类（因子/策略/风控/执行/其他）
5. §3.3 知识→模块映射设计：核心独创环节——如何将知识映射为可执行模块
6. §3.4 代码生成设计：LLM 生成代码的质量控制
7. §3.5 验证设计：生成模块的验证流程（回测+合规+性能）
8. §3.6 入库设计：验证通过的模块如何入 factor/strategy registry

■ 第 3 轮：What 层填充（§4 施工计划）
1. Phase 0（手动）：人采集知识→人分类→人写模块→人验证→人入库
2. Phase 1（半自动）：AI 采集→AI 分类→人写模块→AI 辅助验证→人入库
3. Phase 2（全自动，保留人工审核）：AI 采集→AI 分类→AI 生成→AI 验证→人审核→入库
4. Phase 3（自我进化）：ICL 替代 MAML/EWC，模块工厂自我优化
5. 与 62 号注册表的接口：模块入库的 schema 和流程
6. 与 11 号技能库的接口：技能如何复用为模块组件
7. 与 12 号自反 Agent 的接口：反思如何驱动模块优化

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做 MAML/EWC（单 GPU 约束，Phase 3 用 ICL 替代）
2. 不做零审核全自动（Phase 2 保留人工审核，零审核=自杀）
3. 不做通用代码生成（只生成量化交易相关模块）
4. 不做实时模块工厂（日频/周频批量处理）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：模块工厂定位是否匹配
2. 与 01_external_benchmark_analysis.md §5 一致性：落地性评估是否对齐
3. 与 62 号注册表一致性：入库接口是否对齐
4. 与 11/12 号一致性：技能库/反思接口是否对齐

■ 第 6 轮：过度工程审查
1. 模块工厂是否过度？个人项目是否可用简单"知识库+手动开发"替代？
2. 六环节是否过多？是否可简化为三环节（采集→生成→入库）？
3. Phase 3 自我进化是否过度？Phase 2 是否已是终点？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 13 号本身
- 引用 00_index.md / 01_external_benchmark_analysis.md / 62 号注册表 / 11/12 号时只读不改
- 交易决策侧文档只读不改
```

---

## AI-FILL-14 指令（负责 14_execution_layer.md）

```
你是 ZephyrAlpha 项目的 AI 架构执行层施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇执行层文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\14_execution_layer.md

【文档性质】这是 AI 执行层的施工——治理 Agent、业务 Agent、算法 Agent、自我迭代 Agent。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 组件类按"输入→处理→输出→验证→不做"组织
- 00_index.md §1 执行层提到四类 Agent
- 依赖：11/12/13 号（自我进化层）+ G04/G12（交易决策侧业务模块）
- 交易决策侧：20_first_batch_strategies（G04）、30_multi_strategy_concurrency（G12）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 扫描 src/zephyr/ 下与 Agent 相关的模块（Grep "agent\|Agent"）
2. 读 00_index.md §1 执行层的定位
3. 读 11/12/13 号文（如已填充），确认自我进化层接口
4. 读交易决策侧 20_first_batch_strategies.md（G04 策略定义）
5. 读交易决策侧 30_multi_strategy_concurrency.md（G12 多策略并发）
6. 评估四类 Agent 的当前实现状态

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：四类 Agent 的当前实现状态（哪些已有代码/哪些只有设计）
2. §2.2 核心问题：四类 Agent 如何分工？如何与自我进化层协同？
3. §3.1 治理 Agent 设计：gate 检查/规则执行的 why
4. §3.2 业务 Agent 设计：因子/策略/组合的 why
5. §3.3 算法 Agent 设计：信号/模型/训练的 why
6. §3.4 自我迭代 Agent 设计：评估/优化/反馈的 why
7. §3.5 四类 Agent 协同设计：治理→业务→算法→迭代的闭环

■ 第 3 轮：What 层填充（§4 施工计划）
1. 治理 Agent 施工：与 05 号 intelligence_governance 包的接口
2. 业务 Agent 施工：与 G04 策略定义、G12 多策略并发的接口
3. 算法 Agent 施工：与 11 号模型路由、13 号模块工厂的接口
4. 自我迭代 Agent 施工：与 12 号自反 Agent 的接口
5. Phase 0：单 Agent 手动触发；Phase 1：多 Agent 半自动

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做 agent 编排系统（61 号备忘已裁定）
2. 不做实时 Agent 通信（文件落盘交接）
3. 不做全自动业务 Agent（Phase 2 保留人工审核）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1 一致性：执行层定位是否匹配
2. 与 05/11/12/13 号一致性：各接口是否对齐
3. 与交易决策侧 G04/G12 一致性：业务 Agent 与策略/并发的接口
4. 与 15_autonomy_boundary_risk.md 一致性：执行层 Agent 的自治边界

■ 第 6 轮：过度工程审查
1. 四类 Agent 是否过多？个人项目是否可简化为两类（治理+业务）？
2. 自我迭代 Agent 是否过度？手动优化是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 14 号本身
- 引用 00_index.md / 05/11/12/13 号 / 交易决策侧文档时只读不改
- 交易决策侧文档只读不改
```

---

## AI-FILL-15 指令（负责 15_autonomy_boundary_risk.md）

```
你是 ZephyrAlpha 项目的 AI 架构自治边界与风险施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇自治边界与风险文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\15_autonomy_boundary_risk.md

【文档性质】这是 AI 自治边界与风险的施工——三分类边界（ai_modifiable/human_gated/immutable）、Agentic Drift 防护、有界自治 5 级、OWASP 风险、Kill Switch、ARS 双轨。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 风控类按"风险→控制→验证→不做"组织
- 00_index.md §3.1/§3.2 已有自治边界和 Agent 风险核心设计
- 依赖：14_execution_layer.md（执行层 Agent 清单）
- 相关：09_llm_security_integration.md（LLM 安全栈）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 读 00_index.md §3.1/§3.2 自治边界和 Agent 风险核心设计
2. 扫描 src/zephyr/ 下与自治边界/风险控制相关的模块
3. 读 14_execution_layer.md（如已填充），确认 Agent 清单
4. 读 09_llm_security_integration.md（如已填充），确认安全栈接口
5. 评估三分类边界、Drift 防护、有界自治、Kill Switch 的当前实现状态

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：自治边界/风险控制的当前实现状态
2. §2.2 核心问题：三分类如何落地？Drift 如何检测？Kill Switch 如何触发？
3. §3.1 三分类边界设计：ai_modifiable/human_gated/immutable 的 why
4. §3.2 Agentic Drift 防护设计：双维度阈值+Hard-Gate+行为基线+Agent Challenge
5. §3.3 有界自治 5 级设计：L0 人工→L3 中风险的 why
6. §3.4 Kill Switch 设计：多路径（<1ms 自动/100ms 人工）的 why
7. §3.5 ARS 双轨设计：Fee+Principal 双轨防自利的 why

■ 第 3 轮：What 层填充（§4 施工计划）
1. 三分类边界施工：如何标记每个组件的自治级别
2. Drift 防护施工：行为基线建立、偏差检测、告警介入
3. 有界自治施工：L0~L3 逐级解锁的条件和验证
4. Kill Switch 施工：多路径触发机制、Windows 环境适配
5. 与 14_execution_layer.md 的接口：执行层 Agent 的自治边界标记
6. 与 16_ai_security_ops.md 的接口：风险事件如何流入运维闭环

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做 L4/L5 高自治（个人项目 L3 已是上限）
2. 不做 FPGA 级 Kill Switch（Windows 用户态限制，用软件级替代）
3. 不做实时 Drift 检测（日频/周频批量检测）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §3.1/§3.2 一致性：设计口径是否对齐
2. 与 14_execution_layer.md 一致性：Agent 自治边界是否对齐
3. 与 09_llm_security_integration.md 一致性：安全栈与风险控制的边界
4. 与 16_ai_security_ops.md 一致性：风险事件→运维闭环接口

■ 第 6 轮：过度工程审查
1. 三分类是否过度？两分类（可改/不可改）是否足够？
2. 有界自治 5 级是否过度？3 级是否足够？
3. ARS 双轨是否过度？单轨是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 15 号本身
- 引用 00_index.md / 09/14/16 号时只读不改
```

---

## AI-FILL-16 指令（负责 16_ai_security_ops.md）

```
你是 ZephyrAlpha 项目的 AI 架构安全与运维施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇 AI 安全与自治运维文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\16_ai_security_ops.md

【文档性质】这是 AI 安全（LLM guardrails/串谋/涌现/幻觉/记忆投毒/MCP Triple Gate/KILLSWITCH）与自治运维（Detect→Diagnose→Remediate→Learn/TNR/成熟度/知识库/保命轨）的施工。空骨架，需从零填充。

【背景知识】
- 01 号规范：§4.4 安全运维类按"威胁→防御→监控→恢复→不做"组织
- 00_index.md §3.3/§3.4 已有 AI 安全和自治运维核心设计
- 依赖：09_llm_security_integration.md（LLM 安全栈）+ 15_autonomy_boundary_risk.md（自治边界）
- 相关：08_multi_ai_concurrency_governance.md（git 安全）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改）
1. 读 00_index.md §3.3/§3.4 AI 安全和自治运维核心设计
2. 扫描 src/zephyr/security/ 和 src/zephyr/monitoring/ 相关模块
3. 读 09_llm_security_integration.md（如已填充），确认 LLM 安全栈接口
4. 读 15_autonomy_boundary_risk.md（如已填充），确认自治边界接口
5. 评估安全机制和运维闭环的当前实现状态

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：AI 安全和运维闭环的当前实现状态
2. §2.2 核心问题：安全机制如何覆盖所有威胁？运维闭环如何自愈？
3. §3.1 LLM guardrails 设计：G1~G4 四层防御的 why
4. §3.2 Agent 安全设计：串谋检测/涌现检测/幻觉防护/记忆投毒的 why
5. §3.3 MCP Triple Gate 设计：输入过滤+对齐审查+权限隔离的 why
6. §3.4 KILLSWITCH 设计：三级响应的 why
7. §3.5 自治运维闭环设计：Detect→Diagnose→Remediate→Learn 的 why
8. §3.6 TNR 设计：可撤销+不恶化的 why

■ 第 3 轮：What 层填充（§4 施工计划）
1. LLM guardrails 施工：G1~G4 逐层实现
2. Agent 安全施工：串谋检测/涌现检测/幻觉防护逐项实现
3. 自治运维施工：监控→诊断→修复→学习闭环
4. 知识库施工：故障模式库/修复策略库/根因因果图
5. 与 09 号 LLM 安全栈的接口：安全事件如何流入运维闭环
6. 与 15 号自治边界的接口：边界违规如何触发运维响应

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做外部安全服务（如第三方 SOC）
2. 不做形式化安全验证（用测试+审计替代）
3. 不做实时自愈（RTO<5 分钟用降级策略，非全自动）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §3.3/§3.4 一致性：设计口径是否对齐
2. 与 09_llm_security_integration.md 一致性：安全栈与运维闭环的接口
3. 与 15_autonomy_boundary_risk.md 一致性：边界违规→运维响应接口
4. 与 08_multi_ai_concurrency_governance.md 一致性：git 安全与 AI 安全的边界

■ 第 6 轮：过度工程审查
1. 安全机制是否过度？个人项目是否可简化？
2. 自治运维闭环是否过度？手动运维+告警是否足够？
3. 知识库是否过度？简单日志+经验文档是否足够？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 16 号本身
- 引用 00_index.md / 08/09/15 号时只读不改
```

---

## AI-FILL-17 指令（负责 17_phase_roadmap.md）

```
你是 ZephyrAlpha 项目的 AI 架构分阶段路线施工 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】填充 1 篇分阶段路线文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\17_phase_roadmap.md

【文档性质】这是 AI 层的分阶段实现路线——Phase 0 手动 → Phase 1 半自动 → Phase 2 全自动 → Phase 3 自我进化。空骨架，需从零填充。**依赖 03~16 号文至少完成第 1~2 轮填充**。

【背景知识】
- 01 号规范：§4.4 路线类按"阶段→目标→任务→验收→不做"组织
- 00_index.md §1 目标架构和 §4 约束是路线依据
- 对标：Agentic Engineering 三层架构（Karpathy 2026-02）
- 依赖：03~16 号文至少完成第 1~2 轮填充（背景+设计决策已填）

【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 依赖盘点（只读不改）
1. 用 Read 快速读取 03~16 号文的 frontmatter + 主题组信息 + 施工计划（如有）
2. 记录每篇文档的当前状态（空骨架/已填充背景/已填充设计/已填充施工计划）
3. 读 00_index.md §1 目标架构和 §4 约束
4. 读 01_external_benchmark_analysis.md §Agentic Engineering 部分
5. 判断哪些文档已就绪可纳入路线，哪些还在填充中

■ 第 2 轮：Why 层填充（§2 背景 + §3 设计决策）
1. §2.1 项目处境：AI 层 18 篇文档的填充进度、各组件的实现状态
2. §2.2 核心问题：Phase 0→3 的划分依据？各阶段的解锁条件？
3. §3.1 Phase 0（手动）设计：为什么从手动开始、手动阶段的范围
4. §3.2 Phase 1（半自动）设计：半自动的边界、人机分工
5. §3.3 Phase 2（全自动，保留人工审核）设计：全自动的范围、人工审核的必要性
6. §3.4 Phase 3（自我进化）设计：ICL 替代 MAML/EWC 的 why

■ 第 3 轮：What 层填充（§4 施工计划）
1. Phase 0 详细计划：哪些组件 Phase 0 可完成（如 AutoRuntime 基础层、LLM 基础设施 L1）
2. Phase 1 详细计划：哪些组件 Phase 1 可完成（如画像流水线、Context Engine）
3. Phase 2 详细计划：哪些组件 Phase 2 可完成（如模块工厂、多 Agent 投票）
4. Phase 3 详细计划：哪些组件 Phase 3 可完成（如自我进化层、自治运维）
5. 各阶段验收标准：如何判断一个阶段完成
6. 各阶段依赖：Phase N 依赖 Phase N-1 的哪些产出

■ 第 4 轮：约束与边界填充（§5 不做什么）
1. 不做跳过 Phase 0 直接 Phase 1（手动是基础）
2. 不做 Phase 2 零人工审核（保留人工审核）
3. 不做 Phase 3 MAML/EWC（单 GPU 约束，用 ICL 替代）

■ 第 5 轮：一致性与交叉引用审查
1. 与 00_index.md §1/§4 一致性：路线是否与目标架构和约束对齐
2. 与 03~16 号文一致性：各组件的 Phase 归属是否一致
3. 与 01_external_benchmark_analysis.md 一致性：对标启示是否落地

■ 第 6 轮：过度工程审查
1. 四阶段是否过多？个人项目是否可简化为三阶段？
2. Phase 3 自我进化是否过度？Phase 2 是否已是终点？

■ 第 7 轮：文档质量与规范符合性
1. frontmatter / 修订记录 / 开放问题
2. 骨架填充完成升 v0.2.0

■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：修复 → 提交 git → 下一轮
- 连续两轮零发现，任务结束

■ 约束
- 只改 17 号本身
- 引用 00_index.md / 01_external_benchmark_analysis.md / 03~16 号时只读不改
- 如 03~16 号还在填充中，先等其完成第 1~2 轮再填充本文档
```

---

## 使用说明

1. **开新对话**：在 Trae/CLI 中开 18 个新对话窗口（或分批开，如每批 4~5 个并行，按轨道分组）
2. **复制指令**：从本文档复制对应 AI-FILL 编号的指令块（``` 之间的内容）
3. **粘贴执行**：粘贴到新对话，AI 会自动开始读取文件、盘点、填充、验证、循环
4. **监控进度**：每个 AI 独立工作，互不通信，通过修改的文档文件交接
5. **轨道并行**：轨道 A/B/C/D/E 可并行开工，轨道内按顺序串行（如轨道 A：03→04→08→10）
6. **冲突处理**：若两个 AI 改同一交叉引用（如 00_index.md 被 AI-FILL-00 负责，但所有 AI 都引用），各 AI 只改自己负责的文档，引用对方文档时只读不改
7. **依赖等待**：若 AI-FILL-14 发现 11/12/13 号还在填充中，先填充其他部分，或等待后再填充依赖部分

> **注意**：18 个 AI 并发可能产生资源竞争。建议每个 AI 独立 commit，或全部完成后统一 review 合并。
> **通用纪律（适用全部 18 个 AI，下文各特殊提示不再重复）**：只改自己负责的文档本身，引用其他文档时只读不改；发现其他文档需同步改的，记在自己负责文档的开放问题/待定问题节，不越界改。
> **与交易决策侧的关系**：AI 层设施依赖交易决策侧业务模块。填充时引用交易决策侧文档只读不改，发现需同步改的记在本文档「开放问题」节标「待用户裁定」。

> **AI-FILL-00 特殊提示**：00_index.md 是总索引，更新施工顺序和解锁点，非从零填充。需等所有其他文档至少完成第 1~2 轮填充后再更新。
> **AI-FILL-01 特殊提示**：01 号文档是信息库，已有框架，填充重点是深度分析和前沿演进，不是从零开始。与 02/13 号有交叉引用。
> **AI-FILL-02 特殊提示**：02 号文档是盘点，已有框架，填充重点是代码映射和缺口分析。与 00/01/05~16 号有广泛交叉引用。
> **AI-FILL-03 特殊提示**：03 号文档是域边界裁定，是 U1 解锁点，优先开工。裁定结果影响 04/05/08 号。
> **AI-FILL-04 特殊提示**：04 号文档是 AutoRuntime Core 施工，是 U2 解锁点之一。与 07/10 号有接口。
> **AI-FILL-05 特殊提示**：05 号文档是治理包整合，涉及 ~20 个文件，需大量代码扫描。与 03/14 号有交叉引用。
> **AI-FILL-06 特殊提示**：06 号文档是模型画像流水线，已有 data/brain/ 数据。与 10/11 号有接口。
> **AI-FILL-07 特殊提示**：07 号文档是 Context Engine，已有 22 个文件。与 04/14 号有接口。
> **AI-FILL-08 特殊提示**：08 号文档是多 AI 并发治理，涉及 61/65/66 号备忘。与 00/16 号有交叉引用。
> **AI-FILL-09 特殊提示**：09 号文档是 LLM 安全栈，已有 blueprint。与 10/16 号有接口。
> **AI-FILL-10 特殊提示**：10 号文档是 LLM 基础设施，是 U2 解锁点之一。与 04/06/09/11 号有接口。
> **AI-FILL-11 特殊提示**：11 号文档是自我进化组件，是 U4 解锁点之一。与 06/12/13 号有接口。
> **AI-FILL-12 特殊提示**：12 号文档是自反 Agent，与 11/13 号有接口。
> **AI-FILL-13 特殊提示**：13 号文档是模块工厂，核心独创，复杂度最高（2000~2500 行）。依赖 62 号注册表 + 11/12 号。是 U4 解锁点之一。
> **AI-FILL-14 特殊提示**：14 号文档是执行层，依赖 11/12/13 号 + 交易决策侧 G04/G12。是 U5 解锁点。
> **AI-FILL-15 特殊提示**：15 号文档是自治边界，依赖 14 号。与 09/16 号有接口。
> **AI-FILL-16 特殊提示**：16 号文档是 AI 安全+运维，依赖 09/15 号。与 08 号有交叉引用。
> **AI-FILL-17 特殊提示**：17 号文档是分阶段路线，依赖 03~16 号至少完成第 1~2 轮填充。最后开工。

---

## 编排模式（两种执行方式）

### 方式一：手动多窗口（原始方式）

按上方「使用说明」逐条复制 AI-FILL-XX 指令块到新对话执行。适合精细控制、逐篇验收。

### 方式二：单对话编排自动子代理（推荐）

复制下方「一键编排指令」到一个新对话（Kimi3 等支持 Task 子代理工具的模型），该对话作为**编排者**自动启动子代理完成全部填充。

**最大火力原则**：不设并行上限——第一轮 16 篇施工文档（01~16）全部同时开工，一轮打满；只有 17（分阶段路线）和 00（总索引）因硬依赖前 16 篇的产出，放第二轮。软依赖（如 14 读 11/12/13）不做波次等待，子代理读到未填充的依赖文档时按指令块「如已填充」降级处理——把接口假设写进自己文档的开放问题，不阻塞。

### 一键编排指令（复制到新对话执行）

```
你是 ZephyrAlpha 项目的 AI 架构文档填充总编排 AI。项目是个人+100%AI 开发的 A股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的唯一职责】编排，不亲自填充任何文档内容。读取指令集文件，用 Task 工具以最大并行度启动子代理，每个子代理负责一篇文档的填充。

【指令集文件（唯一真源）】
d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\AI_fill_instructions.md

【执行流程——两轮打满，不设并行上限】
1. 先读指令集文件的「§0 通用规则」「§0.5 填充分类与跳过门」「§1 分配总表与施工顺序」三节，理解解锁点（U1~U8）。
2. 第一轮（16 个子代理，同一条消息中全部并行启动，一个不留）：
   AI-FILL-01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16
3. 第二轮（2 个子代理，并行启动）：AI-FILL-17、AI-FILL-00（前置：第一轮 16 篇全部完成——这两篇是汇总类，硬依赖前 16 篇产出）
4. 每个子代理的任务描述统一用此模板（XX 替换为实际编号）：
   「你是 ZephyrAlpha 项目 AI 架构文档填充子代理，编号 AI-FILL-XX。先完整阅读 d:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans\AI_fill_instructions.md 的以下两节：①「## 0. 通用规则」（含「## 0.5 填充分类与跳过门」）；②「## AI-FILL-XX 指令」。然后严格按指令块执行填充。你只负责这一篇文档，只改这一篇文档，引用其他文档只读不改。你与其他 15 个子代理并行施工——若指令块要求读的依赖文档尚未填充，按「如已填充」降级处理：把接口假设写进你文档的开放问题，继续填充，不等待不阻塞。文件锁 session_id 用 AI-FILL-XX。完成后返回：文档路径、最终版本号、commit hash、开放问题清单、收尾三问答案。」
5. 失败补救：子代理返回"部分完成"时，记录遗留项并重启一次同编号子代理补完；连续两次未完成则标记「待人工介入」并继续，不全局阻塞。
6. 冲突纪律：每个子代理负责不同文档，天然无文件冲突；所有提交走 GitCommitGateway 串行通道（Gateway 自行处理并发排队，子代理不用管）；绝不修改交易决策侧任何文件。
7. 第二轮完成后做最终验收：18 篇文档逐篇 Read frontmatter + 开放问题节，确认 version/修订记录/实质内容三要素，然后在对话里直接输出总验收结论（每篇一行：路径+版本+commit+遗留项），禁止创建任何报告文件。

【禁止事项】
- 禁止你亲自填充任何文档内容（你是编排者，不是施工者）
- 禁止限制并行数量——第一轮 16 个必须同一条消息全部发出
- 禁止修改 AI_fill_instructions.md 本身
- 禁止修改交易决策侧（07_trading_decision_architecture）任何文件
- 禁止裸 git commit / --no-verify
```

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 初版：18 个 AI-FILL 指令集，5 条轨道并行，8 个解锁点定义 | 用户要求建立填充 SOP |
| 2026-08-17 | 0.2.0 | 吸收审计指令精华升级：规则 7 提交改走 GitCommitGateway（禁裸 commit）；新增规则 15 实测纪律/16 真源唯一与向内收/17 红蓝对抗验证轮/18 可发现性自检/19 depgraph L1 铁律/20 收尾三问；新增 §0.5 填充分类与跳过门；新增「编排模式」节（方式二手动→方式二单对话自动子代理）+ 一键编排指令 + 波次计划 | 用户提供审计指令，要求提取有价值内容升级文档；并要求支持单 AI 对话自动开子代理 |
| 2026-08-17 | 0.3.0 | 编排模式改最大火力原则：移除并行上限和 7 波次计划，改两轮打满（第一轮 16 个全并行，第二轮 17+00）；软依赖降级为「接口假设写开放问题，不阻塞」；子代理模板增加并行施工说明 | 用户裁定：不限制并行度，指令不应让模型自我设限 |

---

*维护者：AI 架构协调者*
