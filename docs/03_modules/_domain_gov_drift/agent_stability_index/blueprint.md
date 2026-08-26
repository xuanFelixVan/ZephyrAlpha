---
blueprint_id: MOD-GOV-055
module_name: agent_stability_index
domain: D_GOV_DRIFT
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_GOV_DRIFT
path: src/zephyr/gov_drift/agent_stability_index.py
granularity: file
---

# MOD-GOV-055 agent_stability_index 蓝图（Agent稳定度指数检查器）

> **module_id**: MOD-GOV-055 | **域**: D_GOV_DRIFT | **优先级**: P2
> **来源**: B11-03056（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-GOVDRIFT-003，A7）
> 代码：`src/zephyr/gov_drift/agent_stability_index.py`

## 0. 定位

ASI可落子集：响应语义一致性（embedding余弦注入embedder）+工具调用序列Levenshtein稳定性+推理路径编辑距离+多Agent一致率，50交互滚动窗，ASI<0.75连续3窗告警+落gov_drift事件回调+周频盘后语义。canonical承接GOVDRIFT-002归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/gov_drift/test_agent_stability_index.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
