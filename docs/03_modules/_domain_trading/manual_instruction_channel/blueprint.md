---
module_id: MOD-TRADING-011
title: "Manual Instruction Channel 人工指令通道蓝图 — C-013 外部指令盯盘（schema+校验+对账+审计）"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_trading
layer_name: trading
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P1
blueprint_level: module
design_maturity: production
build_status: stable
responsibility_domain: 
---

# MOD-TRADING-011 Manual Instruction Channel — 人工指令通道（C-013 外部指令盯盘）蓝图

> **module_id**: MOD-TRADING-011 | **域**: D_TRADING | **层**: 交易运营层增量
> **优先级**: P1 | **来源**: CAND-TRD-003（B1-00192，C-013，跨域元文档 §功能域模块，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-TRADING-011
> **铸号备注**: 初铸 MOD-TRADING-009 与 W-P1-23 并行会话 trading_order_aggregate 撞号，
> 本方退让改铸 MOD-TRADING-011（对方节点先登先落码，本方节点 10631553 已 set-blueprint-id 改号）。

## 0. 查重裁定（RULE-EIGHT 探查结论）

候选 spec：人工买入/卖出/调仓指令通道——指令 schema（标的/方向/数量/时限）+ 录入接口
（CLI/前端）+ 必经 C-004 风控与盘前边界校验 + 执行回报对账，指令全程审计。业界对标：
OMS 手工单通道。场内现状：无。

场内既有件逐一探查（查重铁律④——trading 既有监控/盯盘族）：

- health_monitor（MOD-INF-035）/ status_dashboard / stop_gate：系统健康与停摆门面，
  无"人工指令录入→校验→对账"链路；
- admission_controller（MOD-INF-033）：行为准入门（TokenBucket/熔断，面向治理事件），
  非交易指令通道；
- verdict_engine / auto_dispatcher：信号自动执行链（策略信号驱动），非人工录入面；
- track_fusion（MOD-PLAN-020）：四轨融合器仅声明"轨道3 人工指令"枚举占位，无指令
  schema/校验/对账实现（消费方，非通道本体）；
- pre_execution_checker（MOD-EX-024，C-004 前置闸）/ premarket_checker（MOD-EX-063，
  盘前边界）：**被委托方**，已 stable，本通道注入回调不重造；
- settlement_reconciliation（MOD-TRADING-003）：交易级日终对账（Fill vs 券商结算单），
  非"指令 vs 执行回报"逐单对账。

**裁定：独立缺口成立（人工指令通道判定核心缺失），按补充层施工：通道只产
ACCEPTED/REJECTED 裁决与对账状态，下单执行委托既有 ex_core 链（不直连券商）。**

## 1. 定位

交易运营层人工指令入口判定核心：
① 指令 schema 校验（标的/方向/数量/时限/操作人，frozen，Fail-Closed）；
② 录入裁决（intake）：盘前边界校验（premarket_check_fn 委托 MOD-EX-063）→
   C-004 风控校验（risk_check_fn 委托 MOD-EX-024/trading_session 合规闸）→
   ACCEPTED/REJECTED + reason_code；探针未接线/异常 = REJECTED（Fail-Closed，
   绝不臆造放行）；
③ 执行回报对账（reconcile）：execution_probe 取回报，成交量 vs 指令量容差比对 →
   MATCHED/DRIFT/UNFILLED；DRIFT 告警 + 审计；
④ 全程审计：接收→边界→风控→裁决→对账逐事件落审计链（audit_sink 委托 D_GOV_AUDIT）。

不做什么：不直连券商/下单（ACCEPTED 后执行委托既有 ex_core 链）；不做 C-004 判定
本身（委托）；CLI/前端录入界面属装配面（本模块提供函数级 intake 入口）。

## 2. 输入 / 输出

- 输入：ManualInstruction（frozen）：instruction_id/symbol/side(BUY/SELL/ADJUST)/
  quantity(Decimal)/expire_at/operator/created_at/note；
  reconcile 输入：execution_probe(instruction_id→回报对象，filled_quantity 属性)。
- 输出：IntakeVerdict（frozen）：instruction_id/accepted/reason_code/reason/
  audit_trail(tuple[InstructionAuditEvent])；
  ExecutionReconReport（frozen）：instruction_id/status(MATCHED/DRIFT/UNFILLED/
  PROBE_ERROR)/expected_quantity/filled_quantity/detail。

## 3. 核心规则（MVP）

1. schema 校验：instruction_id/symbol/operator 非空；quantity 为正有限 Decimal；
   expire_at > created_at（时限有效）——非法抛 InvalidManualInstructionError
   （Fail-Closed，占位未登码）。
2. intake 顺序固定：边界闸 → 风控闸（不短路，两级结果全量落审计）；任一不过 →
   REJECTED（reason_code=PREMARKET_NOT_READY/RISK_REJECTED/PROBE_UNWIRED/
   PROBE_ERROR）；全过 → ACCEPTED。
3. Fail-Closed：premarket_check_fn/risk_check_fn 未注入（None）或抛异常 → REJECTED，
   绝不臆造放行（对齐 MOD-EX-063 未接线 ready=False 口径）。
4. reconcile：execution_probe 异常 → PROBE_ERROR + alert；无回报（None）→ UNFILLED；
   |filled−expected|>qty_tolerance(默认 0) → DRIFT + alert + audit；否则 MATCHED。
5. 不变量：Decimal-only 数量；全部输出 frozen；审计事件含序号/阶段/结果/时间戳，
   指令全程可追溯；audit_sink/alert_sink 异常吞没不阻断主链。

## 4. 依赖与委托

- C-004 风控面：pre_execution_checker（MOD-EX-024，risk_check_fn 生产接线目标）。
- 盘前边界面：premarket_checker（MOD-EX-063，premarket_check_fn 生产接线目标）。
- 执行委托面：trading_session（MOD-L06-001，ACCEPTED 指令下游执行链，装配批接线）。
- 对账语义面：settlement_reconciliation（MOD-TRADING-003，日终对账互补：指令级 vs 交易级）。
- 审计：D_GOV_AUDIT writer（audit_sink 委托）。
- 消费方（下游，非本波依赖）：track_fusion 轨道3 人工指令枚举（MOD-PLAN-020）。

## 5. 测试锚点

tests/trading/test_manual_instruction_channel.py：schema 校验全边界、intake
ACCEPTED/三种 REJECTED、Fail-Closed（未接线/异常）、审计链事件序、reconcile
MATCHED/DRIFT/UNFILLED/PROBE_ERROR、alert/audit 委托吞没。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-011`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-011` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-011` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-011 | MOD-TRADING-011 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/trading/manual_instruction_channel.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_manual_instruction_channel.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
