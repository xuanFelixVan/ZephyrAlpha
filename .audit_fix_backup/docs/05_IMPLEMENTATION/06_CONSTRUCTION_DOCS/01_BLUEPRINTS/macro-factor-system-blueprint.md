---

module_id: MACRO_FACTOR_SYSTEM_001

version: 1.0.0

status: Active

created_date: 2026-04-08

last_updated: '2026-04-08'

owner: 战略与因子团队

standard_type: 专业量化机构蓝图

applicable_scope: Layer 11 战略决策 — 宏观因子系统

compliance_level: 专业标准

layer: layer_11

responsibility:

  - 宏观因子定义、计算与版本治理

  - 资产/组合对宏观因子的暴露分析与约束

  - 与组合优化及风险预算的接口约定

---



# 宏观因子系统蓝图（Macro Factor System）



> **定位**：对应 [ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md) Layer 11「宏观因子系统」；替代原 LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md 中仅挂 **EXTENDED_OPTIMIZATION** 的弱匹配。  

> **相关（中观/状态）**：ECONOMIC_REGIME_ENGINE_BLUEPRINT.md、MARKET_REGIME_DETECTION_BLUEPRINT.md



## 职责边界



- **负责**：宏观因子库（增长、通胀、利率、信用、汇率等代理）、标准化与发布频率、组合暴露监控、进入战略配置与风险预算的约束。  

- **不负责**：单券基本面因子（Layer 2）；纯技术优化模块细节见 EXTENDED_OPTIMIZATION_MODULES_BLUEPRINT.md。



## 核心能力（蓝图阶段）



| 能力 | 说明 |

|------|------|

| 因子定义 | 可审计的公式、数据源与修订历史 |

| 暴露计算 | 组合/资产对宏观因子的 beta 或因子载荷 |

| 应用 | 战略配置、压力情景、与 PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md 联动 |



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。宏观因子定义、数据源版本、发布事件、暴露计算口径等需以该真源或其子契约为准。

- 与数据层接口：原始宏观数据（频率、时区、修订）到标准化因子输出的字段字典需闭合到契约。

- 与组合优化接口：因子暴露约束/目标（如目标 beta 区间、风险预算联动）需以契约形式供优化模块消费。

- 与风险管理/情景分析接口：压力情景输入与宏观因子冲击映射需闭合到契约。



## 验收标准（可检查）



- 能对任一宏观因子给出“定义公式/数据源/发布频率/版本历史”，并可复现任一历史版本的因子序列。

- 能对任一组合输出宏观因子暴露（至少一个计算口径）并能说明窗口、频率与缺失值处理。

- 能将至少一项宏观因子约束或目标传递给组合优化/风险预算模块，并验证结果满足约束。

- 能在宏观数据修订或异常跳变时产生告警，并输出降级/回滚策略与记录。



## 已知限制



- 数据字典与 API 细化将在施工阶段补全并固化到 `API_Contract.md`；本蓝图先完成边界、接口闭合点与验收闭环。



## 相关文档



- STRATEGIC_DECISION_LAYER_BLUEPRINT.md  

- RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md  



