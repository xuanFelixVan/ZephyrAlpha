---
module_id: KE-documentat-stage_11___p0_p1_p2-004
title: Stage 11：从"P0/P1/P2 确定"到"跨域核心价值链确认"
category: documentation
---

# Stage 11：从"P0/P1/P2 确定"到"跨域核心价值链确认"

Stage 11：从"P0/P1/P2 确定"到"跨域核心价值链确认"

本轮讨论从"大颗粒度全貌"角度，确认了 ZephyrAlpha 2.0 的跨域核心价值链。

**关键结论**：

1. **核心价值链是机构通用标准**：无论机构大小、策略类型，量化投资的核心价值链都是
   ```
   数据 → 研究 → 模型 → 策略 → 组合 → 执行 → 报告
   ```
   这是投资决策的自然流程，无法跳过。

2. **横向治理贯穿始终**：
   - `00_governance/` —— 政策控制
   - `17_risk_and_controls/` —— 风险监控
   - `08_ai_engineering_and_agent_ops/memory-and-context/` —— 记忆沉淀

3. **价值链与目录结构的映射**：
   | 价值链环节 | 对应 docs/ 目录 |
   |------------|-----------------|
   | 数据 | `09_data_platform/` |
   | 研究 | `10_research_and_factor_lab/` |
   | 模型 | `11_model_and_ml_platform/` |
   | 策略 | `12_strategy_and_portfolio/` |
   | 执行 | `13_execution_and_order_lifecycle/` |
   | 报告 | `14_reporting_and_distribution/` |

4. **第二级颗粒度（数据契约）延后**：先完成全貌架构，再讨论每步的输入输出契约。

**本轮明确**：核心价值链已确认，可作为架构全貌的基础；细颗粒度数据契约留待后续。
