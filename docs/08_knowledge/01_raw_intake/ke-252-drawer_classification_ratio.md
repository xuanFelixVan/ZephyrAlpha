---
module_id: KE-231
status: active
title: 3. Drawer classification rationale / 抽屉分类依据
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3. Drawer classification rationale / 抽屉分类依据

3. Drawer classification rationale / 抽屉分类依据

20 top-level directories use **mixed classification by three governance attributes** (Matrix Organization — standard in large enterprises):

20 个顶级目录按**三种治理属性混合分类**（Matrix Organization——大型企业标准做法）：

| Category / 类别 | Directories / 目录编号 | Nature / 性质 |
|----------------|----------------------|--------------|
| **Governance layer / 治理层（横向贯穿）** | `00`, `01`, `16`, `17`, `18` | Cross-domain, governs everything / 跨业务域，管所有东西 |
| **Architecture layer / 架构层（中枢）** | `02`, `03`, `04`, `05` | Architecture design, blueprints, construction / 架构设计、蓝图、施工 |
| **Business domain / 业务域（垂直抽屉）** | `09`, `10`, `11`, `12`, `13`, `14` | Quantitative investment value chain layers / 量化投资价值链各层 |
| **Platform capability / 平台能力层** | `06`, `07`, `08` | Security, SRE, AI engineering (serve all domains) / 安全、SRE、AI 工程（服务所有业务域）|
| **Knowledge layer / 知识沉淀层** | `15` | Cross-time, reusable cognition / 跨时空、可复用的认知 |
| **In-progress / 过程区** | `19` | Discussion, draft, pending / 讨论中、未定稿 |
| **Historical / 历史区** | `99` | Archived, retired / 归档、退役 |

> Why not purely domain-based? Some capabilities (compliance, audit, AI) must act simultaneously across multiple business domains. Pure domain classification scatters compliance docs across 10+ directories, violating single canonical source.
>
> 为什么不纯粹按业务域分？因为有些能力（合规、审计、AI）需要同时作用于多个业务域。纯业务域分类会造成"合规文档分散在 10+ 个目录里"，违反单一真源原则。

---
