---
module_id: MOD-RPT-003
title: "报告发布器蓝图 — 中心枢纽+归档+分发+哈希链审计(基础版)"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RPT-003 Report Publisher — 报告发布器 蓝图

> **module_id**: MOD-RPT-003 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-003 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.1 D-REPORTING-03, §2.1, §3

## 1. 定位

报告发布器——报告域唯一出口(D-RPT-D05)。所有报告模块(TCA/归因/PnL/风险/监管/
绩效审计/交易记录/版本/水印/执行审计)的输出汇聚至此, 归档+分发。

基础版功能:
  - 报告汇聚: publish() 接收各模块输出, 归档为 ArchivedReport
  - 报告归档: append-only + 哈希链(复用 POS-009/EX-15/RPT-013 模式)
  - 报告分发: ARCHIVE(仅归档→SENT) / WEBHOOK(微信→PENDING) / EMAIL(邮件→PENDING)
  - 报告查询: 按 archive_id/source/type 查询, get_latest
  - 完整性校验: verify_chain() 校验哈希链

受限功能(基础版不含):
  - LLM摘要: 需要 LLM 服务(Ollama+qwen3:8b)
  - Crypto-Shredding: 需要 GATE-004/GATE-006
  - SQLite+Parquet 持久化: 基础版用内存存储
  - Merkle树 L2集合完整性: 基础版用哈希链
  - 微信Webhook/邮件SMTP 实际发送: 基础版只记录分发状态

属 A 类基础设施(确定性归档 + 接口定义), 纯消费层不发布事件(D-RPT-D01)。
**纯基础设施: 不决定报告内容, 只负责"归档+分发+校验"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | report_id + source + report_type + content | 来自各报告模块 |
| 输入 | channels (分发渠道列表, 默认 [ARCHIVE]) | — |
| 输出 | ArchivedReport (含哈希链的不可变归档) | — |
| 输出 | DistributionRecord (分发记录) | — |
| 输出 | verify_chain 结果 (bool, 完整性校验) | — |

## 3. 核心规则

### 3.1 报告归档 (Append-Only + 哈希链)

复用 POS-009/EX-15/RPT-013 模式:
```
content_hash = SHA-256(canonical_json(content))
record_hash  = SHA-256(archive_id + archived_at + report_id + source
                        + report_type + content_hash + prev_hash)
prev_hash(v_n) = record_hash(v_{n-1})
```
首条 prev_hash="" (空串)。任何内容篡改 → content_hash 变 → record_hash 变 →
后续所有 record_hash 失效 → verify_chain 返回 False。

### 3.2 报告来源 (ReportSource)

| 枚举值 | 来源模块 |
|--------|---------|
| TCA | D-REPORTING-01 交易成本分析 |
| ATTRIBUTION | D-REPORTING-02 绩效归因 |
| REALTIME_PNL | D-REPORTING-04 实时盈亏 |
| REGULATORY | D-REPORTING-06 监管报告 |
| RISK | D-REPORTING-08 风险报告 |
| EXPLAINABILITY | D-REPORTING-14 可解释性 |
| TRADING_REVIEW | D-REPORTING-15 A股复盘 |
| PERFORMANCE_AUDIT | D-REPORTING-26 绩效审计 |
| VERSION | D-REPORTING-013 版本管理 |
| WATERMARK | D-REPORTING-017 水印追踪 |
| TRADE_RECORD | D-REPORTING-027 交易记录 |
| EXECUTION_AUDIT | D-EX-015 执行审计 |

### 3.3 分发渠道 (基础版)

| 渠道 | 基础版行为 | 状态 |
|------|-----------|------|
| ARCHIVE | 仅归档, 无外部发送 | SENT |
| WEBHOOK | 微信Webhook, 需外部服务 | PENDING |
| EMAIL | 邮件SMTP, 需外部服务 | PENDING |

channels=None 时默认 [ARCHIVE]。

### 3.4 报告查询

- get_report(archive_id) → ArchivedReport | None
- list_by_source(source) → list[ArchivedReport] (按归档时间升序)
- list_by_type(report_type) → list[ArchivedReport]
- get_latest(source) → ArchivedReport | None (最新归档)
- list_distributions(archive_id) → list[DistributionRecord]

## 4. 关键不变量 (INVARIANTS)

- ArchivedReport / DistributionRecord 为 frozen dataclass (不可变)
- append-only: 已归档报告禁止修改/删除
- 哈希链: prev_hash(v_n) == record_hash(v_{n-1}) 恒成立
- content 必须为 JSON 可序列化 dict
- 线程安全: 内部加 Lock 保护归档存储
- 纯消费层不发布事件 (D-RPT-D01)
- D-REPORTING-03 是报告域唯一出口 (D-RPT-D05)

## 5. 错误契约

- `InvalidPublishInputError` (ZA-RPT-0003): report_id/source/report_type/content 为空或非法

## 6. 数据模型

```python
class ReportSource(str, Enum):
    TCA = "tca"
    ATTRIBUTION = "attribution"
    REALTIME_PNL = "realtime_pnl"
    REGULATORY = "regulatory"
    RISK = "risk"
    EXPLAINABILITY = "explainability"
    TRADING_REVIEW = "trading_review"
    PERFORMANCE_AUDIT = "performance_audit"
    VERSION = "version"
    WATERMARK = "watermark"
    TRADE_RECORD = "trade_record"
    EXECUTION_AUDIT = "execution_audit"

class DistributionChannel(str, Enum):
    ARCHIVE = "archive"
    WEBHOOK = "webhook"
    EMAIL = "email"

class DistributionStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

@dataclass(frozen=True)
class ArchivedReport:
    archive_id: str
    report_id: str
    source: ReportSource
    report_type: str
    archived_at: datetime
    content: dict
    content_hash: str
    prev_hash: str
    record_hash: str
    schema_version: str = "1.0"

@dataclass(frozen=True)
class DistributionRecord:
    distribution_id: str
    archive_id: str
    channel: DistributionChannel
    status: DistributionStatus
    distributed_at: datetime
    error_message: str = ""
    schema_version: str = "1.0"
```

## 7. API

```python
class ReportPublisher:
    def publish(
        self,
        report_id: str,
        source: ReportSource,
        report_type: str,
        content: dict,
        channels: list[DistributionChannel] | None = None,
    ) -> ArchivedReport: ...
    def get_report(self, archive_id: str) -> ArchivedReport | None: ...
    def list_by_source(self, source: ReportSource) -> list[ArchivedReport]: ...
    def list_by_type(self, report_type: str) -> list[ArchivedReport]: ...
    def get_latest(self, source: ReportSource) -> ArchivedReport | None: ...
    def verify_chain(self) -> bool: ...
    def list_distributions(self, archive_id: str) -> list[DistributionRecord]: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者(入边): D-REPORTING-01/02/04/06/08/13/14/15/17/26/27 + D-EX-015 (共8条入边)
- 设计真源: D-REPORTING §1.1 D-REPORTING-03, §2.1, §3 (D-RPT-D05/D11/D13)

## 9. 测试

- `tests/reporting/test_report_publisher.py`
- 覆盖: 归档(append-only+哈希链)、分发(3渠道+状态)、查询(get/list/latest)、
  verify_chain(篡改检测)、frozen不可变、线程安全、边界值(空content/非法source/默认渠道)、
  多来源隔离、分发记录关联

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-003` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-003` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-003 | MOD-RPT-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_report_publisher.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
