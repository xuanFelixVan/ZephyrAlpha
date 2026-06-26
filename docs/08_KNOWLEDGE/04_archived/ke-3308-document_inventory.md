---
module_id: KE-3308
title: 2. Document inventory / 文档清单
category: documentation
ttl: permanent
---

# 2. Document inventory / 文档清单

2. Document inventory / 文档清单

| File / 文件 | Layer / 层 | Answers / 回答的核心问题 | Primary audience / 主要读者 | Status / 状态 |
|------------|-----------|------------------------|--------------------------|--------------|
| `index.md`（本文） | — | 本文档组是什么？怎么读？ | 所有人 | active |
| `overview.md` | Cross-layer | 整体架构哲学？四层如何关联？关键 ADR 汇总？ | 架构师、新加入者 | active |
| `business_architecture.md` | BA | 为谁服务？核心业务能力？端到端流程？NFR？ | 业务负责人 | active |
| `information_architecture.md` | IA | `docs/` 有哪些抽屉？怎么分？文档生命周期？ | 文档维护者、AI 协作者 | active |
| `application_architecture.md` | AA | 系统有哪些应用/模块？`src/` 与 `scripts/` 如何分层？ | 开发者、架构师 | active |
| `technology_architecture.md` | TA | 用什么技术栈？运行时拓扑？部署方式？ | SRE、实施者 | active |
| `runtime_planes.md` 🔷 **正交视图 1** | Orthogonal | **运行平面**（Hot < 10ms / Warm 10ms-1s / Cold > 1s）怎么把 14 层业务代码 + 前端 + 治理层重新切分？Sim-to-Real Gap 怎么消？低延迟交易激活路径？ | 架构师、SRE、量化工程师、前端开发者、治理工程师 | active · v1.0.0 · 2026-04-19 |
| `capability_heatmap.md` 🔷 **正交视图 2** | Orthogonal | 14 层业务能力 × 10 能力域（7 业务 + 3 横切）的**成熟度热力图**（L0-L5）？Gap-to-Target 差距？每季度 review 机制？对标顶级机构差在哪？ | 架构师、产品设计、决策层、外部评审、合规 | active · v1.0.0 · 2026-04-19 |
| `data_architecture.md` | DA | 系统有哪些**业务数据对象**？PIT / Survivorship / 血缘 / MDM / 数据质量 / 保留归档怎么治理？ | 量化研究员、数据工程师、AI 架构师、风控合规 | active · v1.0.0 · 2026-04-19 |
| `security_architecture.md` | SEC | 安全域划分？IAM？密钥管理？数据保护？审计日志？威胁模型？ | 安全工程师、合规、架构师 | **active** · v1.0.0 · 2026-04-24 |
| `integration_architecture.md` | INTEG | 集成风格？内外部集成拓扑？接口契约治理？ACL 策略？事件总线规划？ | 开发者、架构师、SRE | active · v1.0.0 · 2026-04-19 |
| `operations_architecture.md` | OPS | 运维域全景（部署/监控/备份/灾备/变更/事件/容量/成本）？Runbook 目录？ | SRE、运维工程师、架构师 | **draft** · v0.2.0 · 2026-04-19 |
| `governance_architecture.md` | GOV | 治理体系三层边界（Policy/Factory/Runtime）？39 治理系统分层归属？AI 自治三层预留口子？激活路径？ | 架构师、合规、治理工程师、AI 协作者 | active · v1.0.0 · 2026-04-19 |
| `frontend_architecture.md` | FE | 前端层（frontend/）的分层 / Module Federation / State / Design System / 构建部署 / Activation Triggers ？ | 前端开发者、架构师、产品设计 | active · v1.0.0 · 2026-04-19 |
| `architecture_model/cross-cutting/capability_heatmap.yaml` | BA | 业务能力与成熟度条目（机器可读 SSoT） | 业务负责人、架构师 | active |
| `architecture_model/index.yaml` + `architecture_model/layers/*.yaml` | AA | 应用/模块与分层属性（联邦制索引 + 各层清单） | 开发者、架构师 | active |
| `architecture_model/technology/technology_landscape.yaml` | TA | 技术雷达与选型清单（Adopt/Trial/Hold） | SRE、实施者 | active |
| `integration_architecture.md` §3.2 | AA/TA | 集成点枚举（EI 系列等；v1.1.0 起由本视图承载） | 开发者、SRE | active |
| `architecture_model/` 🆕 | **YAML SSoT** | 联邦制 YAML 模型（24 分区：14 层 + shared + frontend + scripts + cross-cutting + contracts + events + ddd-model + technology + core-services + shared-infra），所有视图的模块属性数据源 | AI 协作者、架构师、CI 门禁 | active · v2.0.0 · 2026-04-21 |
| `architecture_model/scripts/check_architecture_gates.py` 🆕 | CI | GATE-01~08 + GATE-SC + EXTRA-01~03 自动检查脚本（已迁移至 `scripts/governance/d5_architecture/`） | CI、架构师 | active · v2.1.0 · 2026-05-02 |
| `architecture_model/cross-cutting/invariants.yaml` 🆕 | GOV | 不变核心（immutab
