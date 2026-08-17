---
module_id: MOD-CMP-009
title: "程序化交易报告登记+报送门禁蓝图 — 6 项义务 + ReportGate"
doc_type: blueprint
status: Active
version: "0.1.5"
ttl: permanent
design_maturity: production
layer: L1_foundation
layer_name: compliance
functional_domain: compliance
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-15"
last_updated: "2026-08-15"
priority: P0
blueprint_level: module
---

# MOD-CMP-009 | Compliance Report Registry + ReportGate 程序化交易报告门禁

> **域**: D_COMPLIANCE | **优先级**: P0 | **safety**: H | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-009 (node 9651494)

## 1. 模块定位

程序化交易报告 6 项义务登记 + 报送门禁（BM-BUY-15 §7.4）。**铁律：先报告后交易**——任一必报项 broker_ack 缺失，C-002 执行域拒绝发送任何订单。报送动作为人工（券商渠道），本模块管登记/确认位/门禁。

依据: `43_compliance_discipline.md` §7.4/§7.5

## 2. 不变量 (INVARIANTS)

- 先报告后交易：必报项 broker_ack 缺失 = BLOCK
- 登记表不可读 = Fail-Closed BLOCK
- 50μs 订单停留时间锁不实现；order_min_dwell_us=50 仅记录性参数（§7.5：本系统天然满足）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| ComplianceReportError | ZA-CMP-0006 | 登记表不存在/解析失败 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | catalogs/compliance_report_registry.yaml | REG-CMP-REPORT-001 | 6 项义务+确认位真源 |
| 依赖 | zephyr.compliance.compliance_log | ComplianceLogger | 门禁校验落 compliance_log |
| 消费 | C-002 执行域 | ReportGate.check() | 拒单前置校验——**已接线**（AI-ASM-001，order_manager._check_compliance_gates，BLOCK→ZA-EX-0011） |
| 协同 | ex_core.programmatic_trading_guard | 报备双校验 | 40 号决策⑱（券商报备状态）与本门禁（6 项义务确认位）互补不重复 |

## 5. 核心逻辑

```
6 项义务（§7.4）：账户基本信息/交易软件信息/策略类型(6大类)/
  最高申报速率(通道 10 笔/秒填报)/单日最高申报笔数(MVP 2000 笔/日待校准)/重大变更(T+1)
check(): 任一 required 项 broker_ack=false → BLOCK(missing 列表)；全确认 → PASS
```

## 6. 接口

```python
ComplianceReportRegistry(registry_path=None)
.load_items() -> list[ReportItem]
.order_min_dwell_us() -> int | None
ReportGate(registry=None, logger=None)
.check() -> ReportGateResult  # decision PASS|BLOCK, missing, detail
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 只读门禁，确认位人工回填 | §7.4：报送动作本身为人工（券商渠道），系统管登记/确认位/门禁；代码改写 YAML 丢注释风险大于收益 |
| 最高申报速率取通道值 10 笔/秒填报 | §7.4 表格：内部限频 ≤15 笔/秒是安全垫，监管填报取 miniQMT 通道物理上限 |

## 8. 测试计划

tests/compliance/test_compliance_report_registry.py — 7 用例：全确认/缺确认 BLOCK/非必报不阻断/表缺失 Fail-Closed/50μs 参数/落日志/真表初始态回归。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CMP-009`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CMP-009` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-CMP-009` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CMP-009 | MOD-CMP-009 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
