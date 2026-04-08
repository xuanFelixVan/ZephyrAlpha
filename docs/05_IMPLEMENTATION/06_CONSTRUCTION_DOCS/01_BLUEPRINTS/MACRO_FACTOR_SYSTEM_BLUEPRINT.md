---
module_id: MACRO_FACTOR_SYSTEM_001
version: 0.1.0
status: Draft
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 战略与因子团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 11 战略决策 — 宏观因子系统
compliance_level: 专业标准
layer: Layer 11 (战略决策层)
responsibility:
  - 宏观因子定义、计算与版本治理
  - 资产/组合对宏观因子的暴露分析与约束
  - 与组合优化及风险预算的接口约定
---

# 宏观因子系统蓝图（Macro Factor System）

> **定位**：对应 [ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md) Layer 11「宏观因子系统」；替代原 [LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md](../../../09_AUDIT/STATE/LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md) 中仅挂 **EXTENDED_OPTIMIZATION** 的弱匹配。  
> **相关（中观/状态）**：[ECONOMIC_REGIME_ENGINE_BLUEPRINT.md](./ECONOMIC_REGIME_ENGINE_BLUEPRINT.md)、[MARKET_REGIME_DETECTION_BLUEPRINT.md](./MARKET_REGIME_DETECTION_BLUEPRINT.md)

## 职责边界

- **负责**：宏观因子库（增长、通胀、利率、信用、汇率等代理）、标准化与发布频率、组合暴露监控、进入战略配置与风险预算的约束。  
- **不负责**：单券基本面因子（Layer 2）；纯技术优化模块细节见 [EXTENDED_OPTIMIZATION_MODULES_BLUEPRINT.md](./EXTENDED_OPTIMIZATION_MODULES_BLUEPRINT.md)。

## 核心能力（蓝图阶段）

| 能力 | 说明 |
|------|------|
| 因子定义 | 可审计的公式、数据源与修订历史 |
| 暴露计算 | 组合/资产对宏观因子的 beta 或因子载荷 |
| 应用 | 战略配置、压力情景、与 [PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md](./PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md) 联动 |

## 相关文档

- [STRATEGIC_DECISION_LAYER_BLUEPRINT.md](../../../01_FRAMEWORK/STRATEGIC_DECISION_LAYER_BLUEPRINT.md)  
- [RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md](./RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md)  

---

**状态**：Draft v0.1 — 批次 F 新增；数据字典与 API 在实施阶段补全。
