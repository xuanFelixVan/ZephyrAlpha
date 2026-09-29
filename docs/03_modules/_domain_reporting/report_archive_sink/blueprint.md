---
module_id: MOD-RPT-037
title: "报告归档持久化出口蓝图 — JSONL append-only 落盘 + 跨进程哈希链接续（F115 R2 归档链薄刀）"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: st-c9-f115
date: "2026-09-29"
last_updated: "2026-09-29"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: design
build_status: stable
---

# MOD-RPT-037 Report Archive Sink — 报告归档持久化出口 蓝图

> **module_id**: MOD-RPT-037 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: experimental | **真源**: src/zephyr/reporting/report_archive_sink.py
> **SSoT**: depgraph MOD-RPT-037 | **断点真源**: M6 前端API链补挖波 2026-09-25 分册 04_reporting.md §四-2 + 90_backfill_wave.md R2

## 1. 定位

F115 R2 归档链薄刀。04 册 §四-2 实证：ReportPublisher 的 `self._archive`＝进程内存
list（:261-262/:335-336），头注自认"基础版不含持久化"——"报告域唯一归档出口"
（D-RPT-D05）实际易失，进程重启归档全丢，verify_chain 校验的是内存对象。

本模块补**文件持久化薄刀**（54 号 §7 全量落库施工的前置面，DDL 真源
reconciliation_schema.py 不动，跨 data 域协同后续批）：append-only JSONL 落盘
`data/reports/report_archive.jsonl`，哈希链跨进程连续。

**内收自检（裁定#375 四判据）**：不是第二归档出口——ReportPublisher 唯一出口面不变，
本模块是其注入式持久化 sink（ArchiveSink Protocol 挂 publish 路径）；同真源（哈希链
字段逐字节复用 ArchivedReport），非平行重复件。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | ArchivedReport（publish 归档产物） | zephyr.reporting.report_publisher |
| 输出 | 盘面 JSONL 追加行（一行一记录，UTF-8） | data/reports/report_archive.jsonl |
| 输出 | last_record_hash()（跨进程接链用尾哈希） | ReportPublisher._tail_prev_hash 消费位 |
| 输出 | load_report_records()（只读投影读面） | api_server /api/reports（R3）消费位 |

## 3. 核心规则

### 3.1 append-only 落盘

- persist()：json.dumps(sort_keys, ensure_ascii=False) 规范行 + `open("a")` 追加；
  父目录惰性 mkdir；线程安全（内部 Lock）。
- 禁改写历史行（append-only，与 publisher 归档不变量同源）。

### 3.2 跨进程哈希链连续

- last_record_hash()：盘面最后一条**可解析**记录的 record_hash；坏行跳过留 WARN。
- ReportPublisher.publish 内存链为空时以该值接续 prev_hash——进程重启不再空链起链。

### 3.3 失败降级语义

- persist IO 异常原样上抛；publisher 侧捕获降级为内存态并留 ERROR 日志，
  **不阻断归档主链**（同 review_orchestrator.action_item_sink 隔离先例）。
- load_records 坏行跳过不抛（读面只读降级）。

## 4. 依赖与消费者

- 依赖：zephyr.reporting.report_publisher（ArchivedReport/frozen 契约）。
- 消费者：report_publisher（archive_sink 注入位）、review_trigger（默认装配挂 sink）、
  api_server /api/reports（load_report_records 只读投影，lazy import）。

## 5. 边界（不做什么）

- 不做 DB 落库（54 号 §7 后续批，跨 data 域）；不做 Merkle 树/Parquet；
- 不做分发（WEBHOOK/EMAIL 归 publisher 渠道面）；不做哈希重算校验（verify_chain 归 publisher）。

## 6. 施工指引

- 测试：tests/reporting/test_report_archive_sink.py（10 用例：append-only/父目录/坏行/
  尾哈希/注入位/跨进程接链/失败降级/verify_chain 共存）。
- 入口协议：ArchiveSink（report_publisher.py 内 Protocol，防反向 import 循环）。

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/reporting/attribution_result_store.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_attribution_result_store.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
