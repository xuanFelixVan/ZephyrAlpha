---
module_id: EA-ARCH-MODEL-LAYERS-INDEX
doc_type: index
status: active
version: 1.0.0
generated: '2026-05-02'
depends_on:
  - {target: EA-ARCH-MODEL-INDEX, at: "§文件清单", why: "父级 architecture-model 索引——layers 为其子目录，引用父级文件清单"}
---

# Layers — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**14 层层定义 YAML（l00-data-source ~ l13-experiment-pipeline + shared + _schema）**。

## 文件清单

| 文件 | 说明 |
|------|------|
| _schema.yaml | YAML Schema |
| l00-data-source.yaml | YAML 结构定义 |
| l01-infrastructure.yaml | YAML 结构定义 |
| l02-alpha-factor.yaml | YAML 结构定义 |
| l03-signal-generation.yaml | YAML 结构定义 |
| l04-risk-management.yaml | YAML 结构定义 |
| l05-portfolio-construction.yaml | YAML 结构定义 |
| l06-trade-execution.yaml | YAML 结构定义 |
| l07-post-trade-analytics.yaml | YAML 结构定义 |
| l08-human-ai-interface.yaml | YAML 结构定义 |
| l09-research-innovation.yaml | YAML 结构定义 |
| l10-governance-compliance.yaml | YAML 结构定义 |
| l11-ml-platform.yaml | YAML 结构定义 |
| l12-system-telemetry.yaml | YAML 结构定义 |
| l13-experiment-pipeline.yaml | YAML 结构定义 |
| shared.yaml | YAML 结构定义 |

## 排除规则（不应放入本目录的内容）

- ❌ 跨层契约 → `02_enterprise_architecture/target-architecture/architecture-model/contracts/`

## 父级目录

- 父级：[architecture-model](../index.md)
