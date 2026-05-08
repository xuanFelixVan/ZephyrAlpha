---
module_id: KE-documentat-2_1________c___l00-l13-000
title: 2.1 层级目录对齐（C 轨 L00-L13）
category: documentation
---

# 2.1 层级目录对齐（C 轨 L00-L13）

2.1 层级目录对齐（C 轨 L00-L13）

| 层 | YAML 定义目录 | 代码实际目录 | 对齐状态 |
|---|---|---|---|
| L00 | `l00_data_source` | `l00_data_source` | ✅ 对齐 |
| L01 | `l01_infrastructure` | `l01_infrastructure` | ✅ 对齐 |
| L02 | `l02_alpha_factor` | `l02_alpha_factor` | ✅ 对齐 |
| L03 | `l03_signal_generation` | `l03_signal_generation` | ✅ 对齐 |
| L04 | `l04_risk_management` | `l04_risk_management` | ✅ 对齐 |
| L05 | `l05_portfolio_construction` | `l05_portfolio_construction` | ✅ 对齐 |
| L06 | `l06_trade_execution` | `l06_trade_execution` | ✅ 对齐 |
| L07 | `l07_post_trade_analytics` | `l07_post_trade_analytics` | ✅ 对齐 |
| L08 | `l08_human_ai_interface` | `l08_human_ai_interface` | ✅ 对齐 |
| L09 | `l09_research_innovation` | `l09_research_innovation` | ✅ 对齐 |
| L10 | `l10_compliance` | `l10_compliance` | ✅ 对齐 |
| L11 | `l11_ml_platform` | `l11_ml_platform` | ✅ 对齐 |
| L12 | `l12_system_telemetry` | `l12_system_telemetry` | ✅ 对齐 |
| **L13** | **`l13_experiment_pipeline`** | **`l13_experimentation`** | ❌ **命名不一致** |
| shared | `shared` | `shared` | ✅ 对齐 |

**P0 发现**：L13 命名不一致。YAML 定义为 `l13_experiment_pipeline`，代码实际为 `l13_experimentation`。
