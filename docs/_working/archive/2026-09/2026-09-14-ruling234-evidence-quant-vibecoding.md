---
ttl: task_bound
---

# 调研：量化研究社区与 Vibe Coding 社区的研究笔记留存/清理实践

> 调研日期：2026-09-14。方法：web_search 检索 + autoglm-open-link 打开原文核实。
> 背景：100% AI 会话开发的个人 A 股量化系统，docs/_working/ 每日交接文档/研究报告 tracked 文件数达 120 上限，评估 (a) TTL 自动归档 vs (b) 源头减量两类策略。
> 所有条目均来自真实检索并打开核实过的原文；未找到的维度如实标注。

---

## 1. qlib（微软开源量化平台）：实验记录与文档代码分离，走 MLflow 外挂系统

**做法**：qlib 不把实验记录/研究结果存进仓库 docs，而是内置 QlibRecorder（基于 MLflow 的实验管理系统），把每次实验的参数、指标、产物（模型/预测文件）统一记录在仓库外的 MLflow tracking URI 中，并提供显式的删除生命周期 API（`delete_exp` / `delete_recorder`），从机制上保证"仓库=代码+文档，实验痕迹=外部系统"。

**来源**（已打开原文核实）：
- https://qlib.readthedocs.io/en/latest/component/recorder.html （原文确认：ExperimentManager/Experiment/Recorder 三层结构、save_objects/log_metrics 存产物到 uri、`R.delete_exp(experiment_name='test')`、`R.delete_recorder(recorder_id=...)` 删除接口，后端 MLflowExpManager）

**可借鉴点**：把"每日 AI 会话的实验性产出"与"仓库耐久文档"物理分离——会话产物写到仓库外的运行时区（如 .runtime/sessions/<sid>/staging/，正是本仓库现行做法），docs/ 只留需要长期引用的结论，且删除走显式 API 而非散乱手工清理。

---

## 2. MLflow 生态通用惯例：逻辑删除 + gc 两阶段清理

**做法**：MLflow 对 Run/Experiment 采用"逻辑删除"（软删除，先标记可恢复），再用 `mlflow gc` 命令对已删除运行做永久物理清理——两阶段设计防止误删，删除动作与物理回收分离。

**来源**：
- https://mlflow.org/docs/latest/troubleshooting.html （官方 FAQ："MLflow uses logical deletion for the Runs and Models to avoid accidental deletion of data. To completely clean up the deleted runs and models, use the mlflow gc..."，来源为 mlflow.org 官方域，经搜索核实）
- https://mlflow.org/docs/latest/tracking/backend-stores.html （官方 Backend Stores 文档："The mlflow gc CLI is provided for permanently removing Run metadata and artifacts for deleted runs"，来源为 mlflow.org 官方域，经搜索核实）

**可借鉴点**：若实施 TTL 自动归档，采用"软归档（可逆移动到冷存档区）→ 宽限期后物理清理"的两阶段设计，而非一步删除；这与本仓库 RULE-DATA-OPS 的可逆性三步验证天然契合。

---

## 3. 科研界 ELN（电子实验记录本）保留惯例：按价值分级定保留期，退出活跃即封存

**做法**：NIH 电子实验记录本（ELN）政策对记录生命周期分级管理——活跃期（Active）记录带防删与不可变版本控制；项目结束且不再需要科学引用后转"Inactive"标签，进入锁定归档库、对用户不可见；再按记录类型定保留期（一般项目 7 年、涉专利 30 年、历史性项目转国家档案馆永久保存），到期经审查后处置。

**来源**（已打开原文核实）：
- https://oir.nih.gov/sourcebook/intramural-program-oversight/electronic-lab-notebooks/intramural-electronic-lab-notebook-policy （原文确认 §IV.D Records Retention："ELNs documenting all other intramural research must be retained for 7 years after completion of the project and until no longer needed for scientific reference"；Active/Inactive RRL 两态生命周期；Inactive 后"permanently locked state in an archival cloud repository and are not accessible to the Investigator"）

**可借鉴点**：文档按"是否仍被引用/是否仍准确"而非单纯年龄决定去留——TTL 到期先转冷存档（可检索但不在活跃工作区），而非直接删除；"科研价值 + 法定/追溯需求"决定保留时长，映射到个人量化系统即：结论性研究报告长留，过程性交接文档短留。

---

## 4. Scala 社区"AI slop 假冒文档"治理：源头阻断比事后修复便宜

**做法**：Scala 核心贡献者对 AI 自动生成的"伪文档"站（如 DeepWiki 自动生成的 scala3 文档）的公开控诉与社区共识：修正自动生成文档的工作量巨大且会在下次生成时被再次破坏（"Correcting the auto-generated trash would be a massive effort, which would get likely destroyed anyway the next time the AI touches the docs"），治理的关键是阻断源头而非事后修补。

**来源**（已打开原文核实，含 Discourse search.json 确认主题 URL）：
- https://contributors.scala-lang.org/t/ai-slop-claiming-to-be-documentation/7382 （主题：`"AI" slop claiming to be "documentation"`，2026-02-11）

**可借鉴点**：对 AI 会话产生的交接文档，"过期后修改/维护"不如"过期后归档或淘汰"——过期文档不要试图修补，直接按 TTL 移入冷区或淘汰，避免维护成本高于重写。

---

## 5. 开源界 AI 贡献政策：人工签名/披露制度 + "审查成本 > 贡献价值就不收"黄金法则

**做法**：开源社区已形成系统性的 AI 生成内容治理政策库（收录 150+ 项目的 AI 政策）：要求 AI 辅助贡献打显式标签（`Assisted-by:` / `Generated-by:`，禁止与 AI 虚构 `Co-authored-by:`，如 Linux Kernel、Mesa、OpenInfra）；curl 提出黄金法则"贡献对项目的价值必须大于审查它花的时间，LLM 大比例代写的 PR 通常不满足"；多项目（Zig、libxml2 等）对 AI 生成内容直接禁入。核心逻辑：**源头准入控制**（披露+标签+价值门槛）替代事后清洗。

**来源**（已打开原文核实全文清单）：
- https://github.com/melissawm/open-source-ai-contribution-policies （原文确认：Linux Kernel 行 `"Assisted-by:" required; DCO required`；curl 行 `"The golden rule is that a contribution should be worth more to the project than the time it takes to review it, which is usually not the case if large parts of your PR were written by LLMs."`；OpenInfra 行 `Required use of "Assisted-by:" or "Generated-by:"`；Zig 行 `Strict No LLM / No AI Policy`）

**可借鉴点**：对会话产出文档建立"入库准入门槛"（对应策略 b）——只有"耐久产物"（结论、决策、可复现配置）才允许提交进 docs/，过程稿、阶段汇报、重复背景叙述不进 tracked 区；每份入库文档可带来源标记（会话 ID/日期），便于追溯和批量淘汰。

---

## 6. Scala 编译器的 LLM 政策（真实部分）：PR 模板强制披露 LLM 依赖度

**做法**：scala/scala3 于 2026-02-24 合并 PR #25326，新增 LLM_POLICY.md，要求贡献者在 PR 中声明 LLM 工具使用程度（配套 PR 模板含固定问题："How much have your relied on LLM-based tools in this contribution?"），并配套 prompt 历史留存要求——用制度化披露让评审者可据此索要验证材料。注意：该社区 2026-04-01 的"AI-only"后续公告是愚人节恶搞文（LLM "Trurl" 进核心团队投票），只有 2 月的披露政策是真实的，引用时已区分。

**来源**（已打开原文核实）：
- https://github.com/scala/scala3/pull/25326 （原文确认：标题 "Add a policy regarding LLM-generated code in contributions to the Scala 3 compiler"，Merged Feb 24, 2026，+88 行新增 LLM_POLICY.md；后续 #25348 PR 模板含 "How much have your relied on LLM-based tools in this contribution?" 固定字段）
- https://contributors.scala-lang.org/t/new-policy-for-contributing-to-the-scala-language/7428 （仅用于佐证 2 月政策真实存在；4 月 1 日 "AI-only" 正文为愚人节玩笑，已识别不作为事实引用）

**可借鉴点**：AI 会话产出的交接文档天然没有"作者自审"环节，入库前加一道结构化元数据（日期、会话来源、结论 vs 过程标记），让 TTL 归档和淘汰可以按元数据自动化判定，而不是靠文件名肉眼判断。

---

## 7. AI 编码工作流社区（dev.to 实践文）：源头减量的文件宪法——四文件分离 + 高入库门槛 + 会话产物默认不落库

**做法**：AI 重度使用者的上下文管理实践：将文档按职责分离为 AGENTS.md（行为规则）/ OVERVIEW.md（当前状态）/ MEMORY.md（决策与被否方案）/ ERRORS.md（昂贵踩坑），每类文件有严格的入库门槛测试（如 MEMORY.md："是否存在一个真实决策，后人不知道理由就可能改回去？"），普通变更日志、过程记录**明确不配入库**（"Added the settings page. That is a changelog entry. It does not need memory."）；并在 AGENTS.md 写入硬规则 "do not commit, push, deploy, or delete things unless I ask"，从源头阻止会话产物自动入库。核心哲学："Context is only helpful while there is still a reasonable amount of it"——文档膨胀本身是负资产。

**来源**（已打开原文核实）：
- https://dev.to/sizzlebop/the-ai-coding-workflow-that-finally-stopped-making-me-repeat-myself-8ol （原文确认：AGENTS.md 规则列表含 "do not commit, push, deploy, or delete things unless I ask"；changelog 判断 "That is a changelog entry. It does not need memory."；高门槛 "If not, nothing gets added."；配套开源库 https://github.com/pinkpixel-dev/agent-context-kit）

**可借鉴点**：这是策略 (b) 源头减量的直接社区证据——耐久文档四分法（现状/决策/踩坑）+ 每份文档入库前过门槛测试，能把 docs/_working/ 的增量压到只含真正耐久的产物；过程性内容放会话暂存区（TTL 自动清），与 OpenClaw staging 24h TTL 机制同构。

---

## 8. 笔记社区的 TTL 自动归档实践：按"文件年龄 + 名称模式"定期移动到镜像结构存档区

**做法**：Obsidian 笔记社区的 Simple Archiver 插件提供 Auto-Archive 规则引擎：按文件夹（可正则匹配）+ 条件（文件年龄 ≥ N 天未修改 AND/OR 文件名正则如 `^\d{4}-\d{2}-\d{2}.*\.md$`）定期（默认每 60 分钟评估）把匹配文件移动到存档区的**镜像相对路径**，已存档文件自动跳过，启动时补跑错过的批次。同社区另有 Auto Note Mover、Auto Archive 等同类插件，属于笔记圈的成熟模式。

**来源**（已打开原文核实）：
- https://www.obsidianstats.com/plugins/simple-archiver （原文确认 README：`Conditions can be based on file age (days since last modified) and/or a file name regex`；`Rules are evaluated on a schedule (default every 60 minutes)`；`The items are moved to the same relative path in the archive folder`；示例规则 `File age >= 30 days`；作者同时在 README 声明 "Obviously vibe-coded contributions will receive little of my time"——同样体现源头门槛思维）

**可借鉴点**：这是策略 (a) TTL 自动归档的成熟社区参照——规则引擎三要素（目录范围 + 年龄/名称条件 + 镜像归档路径 + 定时评估 + 补跑）可直接映射到 docs/_working/ → 冷存档区：14 天未修改的带日期交接文档自动移入 docs/_archive/（保持目录镜像），存档区同样 tracked 但不计入活跃工作区配额。

---

## 未找到 / 证据不足的维度（如实说明）

1. **vnpy / zipline / quantlib 的 docs 结构与笔记归档惯例**：检索未命中这三个项目关于研究笔记/文档归档清理的直接公开讨论或政策文件。它们与 qlib 同属"代码+API 文档"仓库形态，未检索到专门的 docs 留存策略文档，如实标注"未找到直接证据"。（检索式：`vnpy zipline quantlib github documentation notes retention cleanup archive policy`，仅命中无关的通用仓库清理工具）
2. **量化从业者关于 research notes retention/cleanup 的专题公开讨论**（quant.stackexchange / Wilmott 等）：未找到直接讨论"研究笔记保留/清理"的高质量问答帖；命中的量化社区内容集中于回测方法论而非笔记治理。间接替代证据为第 1/3 条（qlib 的 MLflow 外挂 + 科研界 ELN 政策）。
3. **Hacker News 上关于"AI 会话产物 TTL / auto-archive"的专题讨论**：未找到聚焦"session 产物 TTL"的 HN 讨论帖（autoglm web_search 对 HN 站内检索命中率为 0）。替代证据为第 5/7 条（OSS AI 政策 + dev.to 实践文），均为 vibe coding 社区真实可核实来源。
4. **100% AI 开发仓库的公开文档卫生复盘**：未找到与本案完全同构（100% AI 会话开发 + 个人量化系统）的公开复盘文；最接近的是第 7 条（AI 重度工作流的文档宪法实践）。

---

## 对两类策略的映射小结（供决策参考，非本调研任务正文）

- 策略 (a) TTL 自动归档：第 2、3、8 条支持——两阶段（软归档→物理清理）、按引用价值分级、规则引擎（年龄+名称模式+镜像路径）是社区成熟做法。
- 策略 (b) 源头减量：第 1、4、5、7 条支持——实验痕迹不进仓库、文档入库门槛测试、"审查/维护成本>价值就不收"黄金法则、耐久文档四分法。
- 两者不互斥：社区实践普遍是"源头只收耐久产物（减量）+ 到期软归档冷区（TTL）+ 宽限后处置"的三段式。
