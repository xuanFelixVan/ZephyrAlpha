---
module_id: GOV-045
doc_type: index
status: Active
version: 1.0.0
generated: '2026-05-02'
depends_on:
- target: EA-ARCH-MODEL-INDEX
  at: §文件清单
  why: 父级 architecture_model 索引——layers 为其子目录，引用父级文件清单
title: Layers
---

# Layers — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**14 层层定义 YAML（l00-data-source ~ l13-experiment-pipeline + shared + _schema）**。

## 文件清单

| 文件 | 说明 |
|------|------|
| _schema.yaml | YAML Schema |
| l00_data_source.yaml | YAML 结构定义 |
| l01_infrastructure.yaml | YAML 结构定义 |
| l02_alpha_factor.yaml | YAML 结构定义 |
| l03_signal_generation.yaml | YAML 结构定义 |
| l04_risk_management.yaml | YAML 结构定义 |
| l05_portfolio_construction.yaml | YAML 结构定义 |
| l06_trade_execution.yaml | YAML 结构定义 |
| l07_post_trade_analytics.yaml | YAML 结构定义 |
| l08_human_ai_interface.yaml | YAML 结构定义 |
| l09_research_innovation.yaml | YAML 结构定义 |
| l10-governance-compliance.yaml | YAML 结构定义 |
| l11_ml_platform.yaml | YAML 结构定义 |
| l12_system_telemetry.yaml | YAML 结构定义 |
| l13-experiment-pipeline.yaml | YAML 结构定义 |
| shared.yaml | YAML 结构定义 |

## 排除规则（不应放入本目录的内容）

- ❌ 跨层契约 → `02_enterprise_architecture/target_architecture/architecture_model/contracts/`

## 父级目录

- 父级：[architecture_model](../index.md)
