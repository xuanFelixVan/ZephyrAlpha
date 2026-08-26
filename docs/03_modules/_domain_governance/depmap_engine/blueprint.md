---
blueprint_id: MOD-GOV-051
module_name: depmap_engine
domain: D_GOVERNANCE
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
domain_id: D_GOVERNANCE
path: src/zephyr/governance/depmap_engine.py
granularity: file
---

# MOD-GOV-051 depmap_engine 蓝图（DepMap依赖扫描引擎）

> **module_id**: MOD-GOV-051 | **域**: D_GOVERNANCE | **优先级**: P2
> **来源**: B13-04303（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-WORKTREE-002，A3 MOD-INF-040）
> 代码：`src/zephyr/governance/depmap_engine.py`

## 0. 定位

AST依赖扫描引擎：全仓import解析（ast.walk，目录过滤）→分层(L0/L1/L2层注册表)存储→与depgraph库diff（注入depgraph_reader回调）→循环依赖/越层调用报告（接CI门禁语义）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/governance/test_depmap_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
