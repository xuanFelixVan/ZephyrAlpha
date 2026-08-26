---
blueprint_id: MOD-KNW-001
module_name: kb_engine
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
path: src/zephyr/knowledge/kb_engine.py
granularity: file
---

# MOD-KNW-001 kb_engine 蓝图（知识库引擎）

> **module_id**: MOD-KNW-001 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B1-00128（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-002，C2 D-KNOW-06）
> 代码：`src/zephyr/knowledge/kb_engine.py`

## 0. 定位

统一KBEngine门面：八Collection通用CRUD（collection词表注入）+条目版本号（每次写version递增+历史留存）+变更审计（注入audit回调）+按版本回滚+FTS5全文搜索（注入sqlite连接，测试用真:memory: FTS5）。LlamaIndex式知识库单机版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_kb_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
