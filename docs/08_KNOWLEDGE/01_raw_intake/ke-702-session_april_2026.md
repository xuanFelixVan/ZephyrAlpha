---
module_id: KE-630----------2026-04-17---006
status: active
title: Stage 14：骨架对齐机构终局（2026-04-17 下半段，Opus 4.7 收口）
category: documentation
ttl: permanent
---

# Stage 14：骨架对齐机构终局（2026-04-17 下半段，Opus 4.7 收口）

Stage 14：骨架对齐机构终局（2026-04-17 下半段，Opus 4.7 收口）

**触发**：

- 用户 + Opus 联合做了一次"埋雷清单"审查，发现 13 处不符合专业机构做法的风险点
- 用户决定全修（7 条 🔴🟡），并要求此前未完成的骨架建设任务一并完成
- 采用"先骨架、后内容"策略：先把目录结构、schema、ADR 范式敲定，内容按需填充

**推导与决策**：

1. **"沙盒档/正式档"双 schema 是错误方向**
   - 背景：v1 标准曾引入"沙盒档 3 字段起步 / 正式档 12+ 字段"双轨
   - 对标：机构（Google、IETF、ISO、JPMorgan、McKinsey）普遍采用"单一 schema + status 驱动"
   - 决策：采用"单一 schema + 分阶段必填闸门"，升格只改 `status`，不做字段迁移
   - 升格：落地为 KBG-0002

2. **ADR 必须在 canonical 域，不能放在 workspace**
   - 背景：此前计划把 ADR 放在 `19_development_workspace/05_adr/`
   - 问题：ADR 是 canonical 凭证（accepted 后长期有效），不应与讨论沙盒混放
   - 决策（历史）：ADR canonical 家曾映射为 `docs/02_enterprise_architecture/adr/`；草稿区 = `docs/19_development_workspace/adr-drafts/`
   - **现行（2026-05-05 session-012）**：accepted 条目权威为 **KB:decisions**（SQLite `knowledge`，`category=architecture_decision`）；物理 `adr/` 树已删除——映射见 `ssot-authority-map.md`
   - 升格：落地为 KBG-0001 的一部分（真源的内部分层）；后续演进见 KB ingestion / GOV-DOC-003 §2.2

3. **workspace 子目录采用语义命名，取消 `0N_` 数字前缀**
   - 背景：机构内部 workspace 惯例是语义命名（`taskbooks/` 而非 `00_taskbooks/`）
   - 数字前缀用于 canonical 域"外部引用优先级"，workspace 内部用不到
   - 决策：一次性重命名 5 个老目录 + 批量更新 98 处引用路径

4. **`doc_type` 必须有受控词表（controlled vocabulary）**
   - 背景：无约束的 `doc_type` 会导致同一类型文档出现不同值（`adr` vs `ADR` vs `architecture_decision_record`）
   - 机构做法：预定义合法值清单，新增值需走 KB 决策记录流程
   - 决策：在 `discussion-document-standard.md` v2.0.0 §3 明确 15 个合法 `doc_type` 值

5. **`module_id` 必须有命名规范**
   - 背景：此前 `module_id` 命名混乱（`DW-INDEX` 无编号，`DW-TASK-001` 有编号）
   - 机构做法：统一格式 `<DOMAIN>-<TYPE>-<NNN>`；ADR 特殊保留 `ADR-NNNN` 短格式
   - 决策：在 `discussion-document-standard.md` v2.0.0 §4 明确格式、DOMAIN 值表、TYPE 值表

6. **`~~删除线~~` 处理 superseded 是错误做法**
   - 背景：rationale-log 此前用删除线标记被推翻的结论（R15/R17/R19-R22）
   - 问题：删除线是视觉效果，不是机器可读状态；未来 AI 索引无法识别"此条已失效"
   - 机构做法：append-only，保留原文，`status: superseded` 字段 + `superseded_by` 指向新条目
   - 决策：本轮清理 rationale-log 所有删除线；在标准 v2.0.0 §6.2 明确 append-only 规则

7. **Taskbook 状态必须用符号化表示**
   - 背景：taskbook 此前用散文状态（"重新讨论中"、"本轮完成"、"暂定"）
   - 问题：机器无法检索"所有进行中的任务"、"所有阻塞的任务"
   - 机构做法：用 `[ ] [/] [x] [~]` 四符号统一表示 open / in-progress / closed / blocked
   - 决策：本轮清理 taskbook 所有散文状态；在标准 v2.0.0 §8 明确四符号规范

8. **ADR / rationale-log / Decision Memory Index 三者边界必须明确**
   - 背景：用户与 AI 都容易混淆三者
   - 决策：在 `document-triage-guide.md` v2.0.0 §1.2 明确：
     - rationale-log = 推导链**时间轴**（append-only、1 份、workspace）
     - ADR = 单决策**快照凭证**（不可变、N 份、canonical）
     - Decision Memory Index = **路由索引**（可重建、1 份、canonical）

9. **需要通俗解释 ↔ 行业术语的术语映射表**
   - 背景：用户记不住所有行业黑话，需要翻译帮助
   - 机构做法：主流机构都有 "Enterprise Business Glossary"（JPMorgan、高盛、BCG、McKinsey 等）
   - 决策：新建 `_registry/vocabularies/terminology_mapping.yaml`，双向映射表（通俗解释 ↔ 行业术语），覆盖架构/治理/决策/记忆/任务/流程/元数据/AI 协作/投资业务 9 类

10. **文档分类从 4 类扩展到机构标准 8 类**
    - 背景：v1 triage-guide 只覆盖 taskbook / rationale-log / open-questions / design-draft 四类
    - 机构完整分类：再加 ADR / roadmap / risk-register / session-log
    - 决策：triage-guide 升级到 v2.0.0，8 类完整图谱 + 每类的定义与边界

**本轮明确**：骨架已对齐机构终局；内容按需填充；接下来的讨论可以在这套骨架上无负担推进。
