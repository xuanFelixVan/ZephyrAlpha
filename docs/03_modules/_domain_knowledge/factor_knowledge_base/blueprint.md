---
blueprint_id: MOD-KNW-005
module_name: factor_knowledge_base
domain: D_KNOWLEDGE
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
domain_id: D_KNOWLEDGE
path: src/zephyr/knowledge/factor_knowledge_base.py
granularity: file
---

# MOD-KNW-005 factor_knowledge_base 蓝图（因子知识库）

> **module_id**: MOD-KNW-005 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B10-02181（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-004，A1 D-KNOWLEDGE-02）
> 代码：`src/zephyr/knowledge/factor_knowledge_base.py`

## 0. 定位

因子定义/关系/历史三表（定义：formula/类别/假设；关系：同族/正交/父子；历史：IC序列/衰减/状态变迁）+挂vector_memory knowledge集合语义（注入kb写入回调）+查询接口（按类别/状态/相关性）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_factor_knowledge_base.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
