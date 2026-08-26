---
blueprint_id: MOD-DATA-064
module_name: data_compression_archiver
domain: D_DATA
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
domain_id: D_DATA
path: src/zephyr/data/data_compression_archiver.py
granularity: file
---

# MOD-DATA-064 data_compression_archiver 蓝图（行情数据压缩与归档）

> **module_id**: MOD-DATA-064 | **域**: D_DATA | **优先级**: P2
> **来源**: B1-00106（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DAT-018，C2 D-DATA-08）
> 代码：`src/zephyr/data/data_compression_archiver.py`

## 0. 定位

行情热(Redis/CH)→温(CH分区)→冷(Parquet按年月分区+snappy压缩)三层归档编排：归档任务plan(cutoff)->应归档分区清单，执行经注入archiver回调（真Parquet写可选），归档索引登记（SQLite注入连接），DuckDB直查冷层查询门面（注入duckdb连接，测试用真duckdb+tmp parquet）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data/test_data_compression_archiver.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
