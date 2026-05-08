---
module_id: KE-documentat-20_________19-006
title: 文件清单（本目录 **20** 个文件：**19** 份登记/契约类工件 + **本 index.md**）
category: documentation
---

# 文件清单（本目录 **20** 个文件：**19** 份登记/契约类工件 + **本 index.md**）

文件清单（本目录 **20** 个文件：**19** 份登记/契约类工件 + **本 index.md**）

| 文件 | 类型 | 说明 | 维护方式 |
|------|:---:|------|:---:|
| `registry-master-index.yaml` | 总索引 | 登记表总索引——`total_registries` / `registries[]` 以本文件为准（**勿写死**） | manual |
| `document-metadata-index.yaml` | 注册表 | 与 `rule-catalog.yaml` 同步的规则树元数据索引（**141** 条，以生成器为准） | auto |
| `adr-status-registry.yaml` | 登记表 | ADR 状态登记表（**冻结壳**；活跃决策见 KB / rationale） | manual |
| `task-card-meta-registry.yaml` | 注册表 | 三套任务卡系统元层管理 | manual |
| `infrastructure-registry.yaml` | 登记表 | **9** 个运行时基础设施组件（以 `total_registered` 为准） | manual |
| `cross-module-dependency-registry.yaml` | 登记表 | 5条跨模块依赖——含正反向双图 | semi_auto |
| `script-health-registry.yaml` | 登记表 | 39个治理脚本维度/超时/健康评分 | semi_auto |
| `ai-risk-register.yaml` | 登记表 | 8个AI操作特有风险——含热力矩阵 | manual |
| `knowledge-article-registry.yaml` | 登记表 | KMS知识条目索引（beta 落地） | semi_auto |
| `ai-session-registry.yaml` | 登记表 | AI Session摘要记录（beta 落地） | semi_auto |
| `frontmatter-field-registry.yaml` | 登记表 | 40个 frontmatter 字段的类型/必填性/枚举值 | manual |
| `directory-registry.yaml` | 登记表 | **83** 个目录——职责声明/轨道归属/index.md 存在性 | manual |
| `gate-registry.yaml` | 登记表 | **25** 个门禁（以 `total_gates` 为准）——pre-commit / 架构 / 元数据 等 | manual |
| `declarative-contract-tracker.yaml` | 登记表 | **11** 条声明式契约跟踪（config 与蓝图承诺 vs 实现） | manual |
| `frontier-llm-benchmark-ranking.md` | 登记表 | 前沿 LLM 基准排名——模型能力/价格/延迟对比 | manual |
| `rule-registry.md` | 登记表 | 规则登记表——全部规则的集中发现入口（v1.4.0，从 meta/ 迁入） | manual |
| `registry-of-registries.yaml` | 契约 | 登记表的登记表——跨登记表共享字段一致性契约（v1.1.0，从 meta/ 迁入） | manual |
| `ai-autonomy-authority-registry.md` | 登记表 | AI 自治权限登记表——全模块权限终表（v1.3.0，从 governance/ai/ 迁入） | manual |
| `rule-catalog.yaml` | 登记表 | 规则目录——全部规则的分类索引与交叉引用 | manual |
