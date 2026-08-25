---
module_id: MOD-GOV-050
title: "阈值拆分检测器蓝图 — 反化整为零（滑动窗累计+提请审批+阻断）MVP"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L2_domain
layer_name: gov_enforcement
functional_domain: gov_enforcement
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-GOV-050
domain_id: D_GOV_ENFORCEMENT
path: src/zephyr/gov_enforcement/rule_enforcement/threshold_split_detector.py
design_maturity: design
build_status: planned
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-GOV-050 阈值拆分检测器（Threshold Split Detector）蓝图

> **module_id**: MOD-GOV-050 | **域**: D_GOV_ENFORCEMENT | **层**: L2 规则执行
> **优先级**: P0 | **来源**: CAND-GOVENFOR-001（B11-03054，AUD-DRAFT-001-DIGEST P0 波 W2a）

## 1. 定位

反化整为零 = AML 结构化交易（smurfing）检测的滑动窗口累计思路。
AI 拆分交易绕过审批属 AI 自治熔断硬缺口：审批网关（MOD-L08-001）是**单笔视角**，
可被化整为零击穿；场内此前无任何拆分规避检测。本模块补该缺口：

1. **交易意图先登记**——所有委托意图先过本检测器登记再放行；
2. **滑动窗累计**——30 分钟滑动窗 + 当日窗两档，对**同标的同方向**累计数量/金额；
3. **阈值比对**——窗内**单笔均低于审批阈值**（≥2 笔）但**累计 ≥ 阈值 80%** 即判拆分；
4. **处置**——阻断该（标的，方向）后续单 + 提请人工审批（ApprovalRequest 经审批网关
   submit）+ 告警落审计哈希链（audit_sink 生产接线 AiAuditLogger）。

与存量件分工（探查复用，不 import 不复制）：
- `default_approval_gateway.py`（MOD-L08-001）：提请审批的载体，经注入网关 submit
  `ApprovalRequest`（契约类型 import 自 `frontend.interface_base`）；
- `stop_gate.py`（MOD-INF-035）：session 质量闸门语义不同，不复用；
- `ai_audit_logger.py`（MOD-INF-035）：哈希链审计载体，经注入 audit_sink
  （运行时装配批接线）。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | OrderIntent（intent_id/strategy_id/symbol/side/quantity/amount）+ ThresholdSplitConfig（双阈值+80%+30分钟+symbol 覆盖）+ 注入端口（审批网关/告警/审计/时钟） | frozen dataclass |
| 输出 | SplitDetectionResult（verdict=CLEAN/SPLIT_SUSPECTED/BLOCKED、两档窗累计、阈值、是否阻断、提请审批 request_id） | frozen dataclass |

## 3. 核心规则

1. 登记即检测：`register_intent` 先校验（非法意图 InvalidOrderIntentError），
   已阻断（标的，方向）直接 BLOCKED 且**不计入**窗口。
2. 判定拆分（满足全部）：窗内笔数 ≥2；窗内**每笔**数量与金额均低于阈值；
   30 分钟窗或当日窗累计数量/金额 ≥ 阈值 × alert_ratio（默认 0.8）。
3. 判拆分后：该（标的，方向）入阻断集（后续单 BLOCKED）；仅首次判定时提请
   审批一次（request_id 幂等：SPLIT-{symbol}-{side}-{day}）；告警 CRITICAL +
   审计落 SPLIT_SUSPECTED。
4. 提请审批/告警/审计端口异常不阻断检测主流程（隔离记录），但阻断集必生效
   （Fail-Closed：宁可误阻断不可漏拆分）。
5. 时钟可注入保判定确定性；线程安全（内部锁）；窗口惰性清理跨日数据。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| ApprovalRequest（提请审批契约） | zephyr.frontend.interface_base（MOD-L08-001） | import |
| ZephyrBaseError（错误契约基类） | zephyr.shared.foundation.errors（MOD-INF-016） | import |

## 5. 测试锚点

- 多笔低于阈值累计 ≥80%（30 分钟窗/当日窗各一档）→ SPLIT_SUSPECTED + 阻断 +
  提请审批一次 + 审计告警；
- 窗内存在单笔 ≥ 阈值 → CLEAN（非拆分，走单笔审批视角）；
- 累计 <80% → CLEAN；阻断后同标的同方向后续单 BLOCKED 且不计入窗口；
- 提请审批幂等（同标的同方向同日仅一次）；端口异常隔离但阻断生效；
- 非法意图校验；时钟注入窗口边界（30 分钟滑出即不计）；frozen 不可变。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-GOV-050`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-GOV-050` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-GOV-050` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-GOV-050 | MOD-GOV-050 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | planned | ❌ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
