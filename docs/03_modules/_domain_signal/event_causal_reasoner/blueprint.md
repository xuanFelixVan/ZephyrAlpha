---
blueprint_id: MOD-SIG-112
module_name: event_causal_reasoner
domain: D_ASHARE_SIGNAL
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
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/event_causal_reasoner.py
granularity: file
---

# MOD-SIG-112 event_causal_reasoner 蓝图（A股事件因果推理器）

> **module_id**: MOD-SIG-112 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B1-00125（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-029，C2 D-ALT-22）
> 代码：`src/zephyr/signal_ashare/event_causal_reasoner.py`

## 0. 定位

事件类型→传导边模板（产业链上下游/同业/供应链三类词表闭合）+DoWhy反事实校验（注入dowhy_runner回调，库未装则降级标记不阻断）+事件链时序存储（注入sqlite连接）+事件影响路径与强度输出（路径BFS+强度衰减系数）。EconML/DoWhy思想单机版。canonical承接TESTA-018/TESTB-052归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_event_causal_reasoner.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
