---
module_id: MOD-RPT-017
title: "报告水印追踪器蓝图 — 报告完整性+来源追溯+哈希链水印"
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
priority: P2
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RPT-017 Report Watermark Tracker — 报告水印追踪器 蓝图

> **module_id**: MOD-RPT-017 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P2 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-017 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.3 D-REPORTING-17

## 1. 定位

报告水印追踪器——为每份报告加盖不可篡改水印, 提供:
- **来源追溯**: 记录报告生成源模块(source) + 时间戳
- **完整性校验**: content_hash 检测内容篡改
- **哈希链审计**: 水印间哈希链接, 任何删除/篡改可检测
- **水印签名**: signature = SHA-256(source + content_hash + timestamp)

复用 POS-009/EX-15/RPT-013 的哈希链模式。属 A 类基础设施, 纯消费层不发布事件。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | report_id (报告标识), content (报告内容 dict), source (生成源模块名) |
| 输出 | ReportWatermark (含水印+哈希链的不可变记录) |
| 输出 | verify 结果 (bool, 完整性校验) |

## 3. 核心规则

### 3.1 水印加盖 (stamp)

- 每份报告可多次加盖水印(如: 生成时盖一次, 审核时盖一次)
- content_hash = SHA-256(canonical_json(content))
- watermark_signature = SHA-256(source + content_hash + timestamp)
- prev_watermark_hash = 上一个水印的 record_hash(同 report_id 内链接)

### 3.2 完整性校验 (verify_watermark)

- 重算 content_hash 比对 → 检测内容篡改
- 重算 watermark_signature 比对 → 检测水印伪造

### 3.3 哈希链验证 (verify_chain)

- 遍历同 report_id 所有水印, 重算哈希链, 检测删除/篡改

## 4. 数据模型

```python
@dataclass(frozen=True)
class ReportWatermark:
    watermark_id: str
    report_id: str
    source: str           # 生成源模块 (如 "RiskReportEngine")
    timestamp: datetime
    content_hash: str     # SHA-256(canonical_json(content))
    watermark_signature: str  # SHA-256(source + content_hash + timestamp)
    prev_watermark_hash: str  # 链接前一水印, 首个为 ""
    record_hash: str      # 链指纹
    schema_version: str = "1.0"
```

## 5. API

```python
class WatermarkTracker:
    def stamp(self, report_id: str, content: dict, source: str) -> ReportWatermark: ...
    def get_watermark(self, report_id: str) -> ReportWatermark | None: ...
    def list_watermarks(self, report_id: str) -> list[ReportWatermark]: ...
    def verify_watermark(self, watermark: ReportWatermark, content: dict) -> bool: ...
    def verify_chain(self, report_id: str) -> bool: ...
    def list_sources(self) -> list[str]: ...
```

## 6. 依赖

| 依赖 | 类型 | 就绪 |
|------|------|------|
| errors foundation | import_depends | ✓ production |

## 7. 测试计划

- 水印加盖: 字段正确 / content_hash / signature / 链接
- 完整性校验: 内容匹配 / 内容篡改检测 / 签名伪造检测
- 哈希链: 单水印 / 多水印链接 / 篡改检测 / 删除检测
- 来源追溯: 多来源 / list_sources
- frozen不可变 / 线程安全 / 边界值

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-017`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-017` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-017` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-017 | MOD-RPT-017 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_report_watermark_tracker.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
