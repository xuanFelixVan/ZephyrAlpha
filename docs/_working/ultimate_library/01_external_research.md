---
title: "终极图书馆 · 业界与学术调研存档 2026-09-21"
ttl: task_bound
completes_when: 归档件随总蓝图转正或退役，无独立活性
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 业界与学术调研存档（2026-09-21，两路全网调研汇编制）

> 结论先行：**"单仓库、全资产（代码+数据+文档+管线+备份）统一分层目录、供 AI 代理查询"无完整先例**——业界是三套拼接（Backstage 管代码文档 / 数据目录管数据管线 / 备份进 CMDB）。空白真实，属自建；积木约七成现成。

## §1 业界全资产目录实践

| 系统 | 验证了什么 | 可移植点/教训 | URL |
|---|---|---|---|
| Spotify Backstage | 软件目录+TechDocs+Scorecard | 资产卡随资产入库；失败模式=catalog rot（手填元数据必腐、文档过期拖慢一切） | https://backstage.io/docs/features/software-catalog/ |
| LinkedIn DataHub / OpenMetadata / Amundsen | 数据目录+血缘 | schema/清单/血缘=连接器自动爬取；业务描述/Owner=人填+覆盖率看板督促 | https://www.decube.io/post/open-source-data-catalog-comparison |
| OpenLineage / Marquez | 运行时血缘规范 | 血缘是规范层非平台；本项目 data_asset_registry 已对标 | https://oneuptime.com/blog/post/2026-09-08-choose-openlineage-datahub-openmetadata-column-lineage/view |
| Sourcegraph SCIP（原 LSIF）/ GitHub stack graphs | 代码索引随 CI 重建/免配置推导 | 索引=派生物，commit 触发重建，永不手编 | https://github.blog/2021-12-09-introducing-stack-graphs/ |
| Cursor 代码库索引 | Merkle 树根哈希定位变更 chunk，只重嵌入改动部分 | 增量同步防索引漂移的业界标准答案 | https://read.engineerscodex.com/p/how-cursor-indexes-codebases-fast |
| dbt manifest.json | 一次构建同产"可执行 DAG+资产清单+人类文档" | 三者同源零漂移；馆页=构建产物 | https://docs.getdbt.com/reference/artifacts/manifest-json |
| Data mesh | data as product+联邦计算治理 | 每资产带 Owner/SLO/契约产品卡；全域标准=策略即代码 | https://martinfowler.com/articles/data-mesh-principles.html |
| 备份 3-2-1 → 3-2-1-1-0 | +不可变/WORM 副本；末位 0=零错误 | checksum manifest 随盘生成；"没演练过恢复的备份不算备份" | https://www.veeam.com/blog/321-backup-rule.html |

## §2 AI 原生工程与学术

| 件 | 是什么 | 对图书馆的可移植点 | URL |
|---|---|---|---|
| AGENTS.md | OpenAI 2025-08 事实标准，20k+ 仓库 | 入口 L0 格式 | https://agents.md |
| Anthropic context engineering | CLAUDE.md 精瘦高信号；细节靠检索不预载 | 分层渐进披露；预载过肥执行率下降（与宪法 §6 互证） | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| GitHub Spec Kit | 规格驱动开发 specify→plan→tasks→implement | 骨架→血肉的施工令范式 | https://github.com/github/spec-kit |
| Aider repo map | tree-sitter 抽符号+引用图+PageRank+token 预算二分 | 馆页目录图排序生成，禁手工 | https://aider.chat/2023/10/22/repomap.html |
| RAPTOR（arXiv 2401.18059） | 递归聚类+摘要建树，多层抽象导航 | **最贴"上千条目必须分层摘要"需求，馆藏导航层首选** | https://arxiv.org/abs/2401.18059 |
| GraphRAG / LightRAG / HippoRAG 2 | 实体图+社区摘要/双层级检索/PPR 记忆 | 导航选 RAPTOR；实体问答 GraphRAG/LightRAG；多跳 HippoRAG 2（不产层级摘要） | https://github.com/microsoft/graphrag ; https://github.com/HKUDS/LightRAG ; https://arxiv.org/abs/2502.14802 |
| RACG 综述（arXiv 2510.04905） | 首个仓库级检索增强代码生成系统框架 | 检索粒度/时机/接地设计对标 | https://arxiv.org/abs/2510.04905 |
| MemGPT/Letta、Reflexion | 两级自编辑记忆；语言化反思入记忆 | 无验证的记忆库会退化成幻觉源——馆页必须带机器可验新鲜度 | https://arxiv.org/abs/2310.08560 ; https://arxiv.org/abs/2303.11366 |
| 幻觉缓解综述 | 主流路线=检索接地+强制引用+自反思校验 | 引用必经+写后核实（与宪法硬规则 13 互证） | https://arxiv.org/abs/2311.05232 |
| MCP（Model Context Protocol） | AI 查询资产的工具层，官方 filesystem/git server | 工具口承载（本仓已有 19 server 簇） | https://github.com/modelcontextprotocol/servers |

## §3 量化社区资产注册表

| 件 | 形态 | 可移植点 | URL |
|---|---|---|---|
| Microsoft Qlib | 因子=代码化 handler，Alpha158 由 get_feature_config() 生成 | 因子目录由生成器产出 | https://qlib.readthedocs.io/en/latest/component/data.html |
| WorldQuant BRAIN | alpha 统一登记+仿真+指标门槛 | 登记制（本仓 factor_registry 175/strategy_registry 161 同构） | https://www.worldquant.com/brain/ |
| Alpha101 | 因子=表达式清单目录 | 目录形态 | https://arxiv.org/abs/1601.00991 |
| PIT 实践 | as-of 时间戳防前视 | 血缘+保守滞后=行业共识 | https://hedgefundalpha.com/education/why-quants-pay-more-for-point-in-time-data/ |
| zvt / vnpy / Hikyuu | 统一 schema 数据字典/网关抽象 | 数据字典组织参照 | https://github.com/zvtvz/zvt |

## §4 综合结论

1. **可行性=高，约七成现成积木**。五条可移植模式：①清单即构建产物（dbt）；②机器采集优先、人填最小化+覆盖率门禁（DataHub）；③哈希/commit 触发增量重建、索引永不手编（Cursor/SCIP）；④产品卡+计算治理（data mesh）；⑤checksum manifest+恢复演练（3-2-1-1-0）。
2. **缺口两处=自研空间**：跨五类资产统一 schema 与单一查询入口无现成品；手填字段防腐须一等公民化（每条目机器可验新鲜度，过期自动报警或退役）。
3. **双真源防范（业界共识）**：目录只存指针+摘要+校验和，真源留资产本体；"条目清单+计数"必须生成器产出——业界独立验证了本仓 ROOR/gate 路线正确。
4. **公认反模式**：手工维护静态清单必然漂移；规则/记忆预载过肥致执行率下降；无验证记忆库退化成幻觉源；扁平 RAG 答不了全局导航问题（分层摘要不可省）。
