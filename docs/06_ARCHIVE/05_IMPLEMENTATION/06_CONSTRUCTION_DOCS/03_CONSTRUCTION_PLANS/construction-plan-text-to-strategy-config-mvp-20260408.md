---
module_id: AUTO_37119
owner: System_Guardian
version: 1.0
status: AUDITED
last_updated: 2026-04-13
---
﻿---
```
module_id: IMPL_CONSTRUCTION_PLAN_TEXT_TO_STRATEGY_CONFIG_MVP_20260408
```
version: 1.0.0
status: Active
created_date: 2026-04-08
last_updated: 2026-04-08
owner: 仓库 Owner
standard_type: 施工计划
applicable_scope: 桌面端（表单+对话）“文字/对话→策略配置→回测→报告”最小闭环
related_documents:
  - ../01_BLUEPRINTS/STRATEGY_AUTHORING_ASSISTANT_BLUEPRINT.md
  - ../01_BLUEPRINTS/STRATEGY_ENGINE_BLUEPRINT.md
  - ../01_BLUEPRINTS/EXECUTION_STRATEGY_BACKTESTER_BLUEPRINT.md
  - ../01_BLUEPRINTS/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md
  - ../01_BLUEPRINTS/PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md
  - ../../../03_TRADING_TACTICS/API_Contract.md
  - ../00_MANAGEMENT/CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md
layer: layer_05
responsibility: "处理CONSTRUCTION_PLAN_TEXT_TO_STRATEGY_CONFIG_MVP_20260408相关业务"
```
```---
```



# 施工计划：文字/对话 → 策略配置 → 回测 → 报告（MVP）

## 0. 范围与非目标（先保证“小白可用”）

### 0.1 本计划要交付什么

- **桌面端入口**：表单 + 对话框（Agent）协同，支持用户用中文自然语言描述策略意图。
- **落盘配置**：生成并保存 `StrategyConfig`（JSON/YAML 均可），并具备版本号与审计字段。
- **一键回测**：基于 `StrategyConfig` 触发回测任务，生成可下载/可查看的报告。
- **可回滚**：任何一次策略修改都可回退到历史 `strategy_config_version`，并复跑得到同结论。

### 0.2 本计划不做什么（MVP 明确不背锅）

- 不承诺“自动赚钱/稳定盈利”。  
- 不在 MVP 中覆盖全部市场与全部策略类型（先做 1–2 个策略模板即可）。  
- 不在 MVP 中实现完整的实盘下单链路（回测/模拟优先）。  

## 1. 里程碑与依赖

### 1.1 依赖（必须先明确）

- **契约真源**：`docs/03_TRADING_TACTICS/API_Contract.md` 已增补 “StrategyAuthoringAssistant 子契约（第 11 节）”。  
- **蓝图依赖**：
  - `STRATEGY_AUTHORING_ASSISTANT_001`（入口与校验）
  - `STRATEGY_ENGINE_001`（策略执行/调度）
  - `EXECUTION_STRATEGY_BACKTESTER_001` 与/或 `FACTOR_BACKTEST_INTEGRATION_001`（回测）
  - `PORTFOLIO_PERFORMANCE_EVALUATION_001`（指标/报告）

### 1.2 里程碑（建议 3 次可演示交付）

1. **M1：可生成配置（不跑回测）**  
   - 完成“文字输入→澄清问答→生成 DraftSpec→校验→落盘 StrategyConfig”。  
2. **M2：可跑回测并出报告（单策略模板）**  
   - 用 1 个策略模板（例如 `sma_cross`）完成回测与报告输出。  
3. **M3：可迭代与可回滚（最小审计闭环）**  
   - 对同一策略做 2 次修改，能回滚到历史版本并复跑对账。  

## 2. 用户输入模板（填空式，适合编程小白）

> 你只需要按模板填空；系统允许你先“随便写”，再通过澄清问答补齐。

### 2.1 策略意图（自然语言）

- **我想交易的市场/标的**：  
- **我认为的机会来源（一句话）**：  
- **买入条件**：  
- **卖出/退出条件**：  
- **我最在意的风险约束**（最大回撤/仓位/杠杆/禁忌）：  
- **回测区间**（起止日期）：  
- **成本假设**（手续费/滑点/冲击模型偏好）：  
- **我希望看的报告指标**（例如 夏普、回撤、胜率、换手、成本拆解）：  

### 2.2 系统澄清问答（最小集合）

- 若 **标的范围** 缺失：问 `universe`（指数成分/自选列表/全市场筛选）。  
- 若 **频率** 缺失：问 `timeframe`（1D/1H/5m 等）。  
- 若 **基准** 缺失：问 `benchmark_id`。  
- 若 **成本** 缺失：问 `commission_bps`/`slippage_bps`。  
- 若 **随机性** 相关：固定 `seed`（用于可复现）。  

## 3. 校验与回滚策略（LLM 辅助但可控）

### 3.1 校验（执行前必须过）

- **Schema 校验**：字段齐全、类型正确、枚举值合法。  
- **逻辑校验**：例如 `signals.fast < signals.slow`、回测日期合法、频率与数据集匹配。  
- **风险提示**：超出边界则提示并要求用户确认（但不自动修改）。  

### 3.2 回滚（必须支持）

- 每次生成 `StrategyConfig` 都必须生成新的 `strategy_config_version`。  
- 支持按 `strategy_config_version` 回滚并复跑回测。  

## 4. 验收标准（可检查）

- **A. 配置闭环**：完成 1 次“文字/对话→StrategyConfig 落盘”，并能导出 JSON（或 YAML）。  
- **B. 回测闭环**：用同一个 `StrategyConfig` + `dataset_id` + `seed` 触发回测 2 次，报告结论可复现（允许数值微差但差异需记录原因）。  
- **C. 迭代闭环**：同一策略做 2 次修改并生成 3 个版本（v1/v2/v3），可回滚到 v1 并复跑。  
- **D. 审计字段**：报告/结果里能看到 `strategy_config_version`、`dataset_id`、`seed`、`engine_version`。  

## 5. 风险清单（MVP 常见坑）

- LLM 误解用户意图：必须做“配置中文回显 + 用户确认”与字段级校验。  
- 数据口径不一致导致回测不可复现：必须固定 `dataset_id` 与数据版本。  
- 策略模板过多导致复杂度爆炸：MVP 只做 1–2 个模板，其余先落为“文本记录 + 待扩展”。  

