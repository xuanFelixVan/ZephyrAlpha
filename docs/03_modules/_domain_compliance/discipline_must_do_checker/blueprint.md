---
module_id: MOD-CMP-001
title: "四项必做清单检查器蓝图 — 盘前/盘中/盘后/晚间完成度检测"
doc_type: blueprint
status: Active
version: "0.1.4"
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
priority: P1
blueprint_level: module
---

# MOD-CMP-001 | Checklist Completion Checker 四项必做清单检查器

> **域**: D_COMPLIANCE | **优先级**: P1 | **safety**: H | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-001 (node 8661726)

## 1. 模块定位

交易日 4 个关键时点（盘前/盘中/盘后/晚间）自动检测四项必做清单完成度，操作合规"自律层"——防"AI 全自动跑、人不复盘"的纪律衰减。BM-BUY-08-A 落地载体（D-COMPLIANCE-23 组件 A）。

依据: `43_compliance_discipline.md` §3（裁定=MVP 轻量检查器，纪律辅助非阻断，盘中执行除外）

## 2. 不变量 (INVARIANTS)

- 必做清单是纪律辅助非阻断：超时只 Warning 不阻交易；**盘中执行项唯一 Hard Block**
- 处置方向一律"更保守"（Fail-Closed）
- 检测失效 → 降级人工 checklist（paper 模式）；盘中项失效 → 拒单
- 完成度信号消费工作流 artifact 存在性，不侵入复盘/分析模块内部逻辑

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| ChecklistCheckerError | ZA-CMP-0001 | 检查器内部错误 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.compliance.compliance_log | ComplianceLogger | 判定落 compliance_log |
| 依赖 | 调用方注入 CompletionProvider | (ChecklistCheckpoint, date) -> set[str] | 完成度信号源（复盘报告/分析任务/C-004 确认位） |
| 消费 | C-004 风控引擎 | INTRADAY 检查 | 订单提交前嵌入（Pre-Trade 拦截链一环，40 号决策⑭同通道）——**已接线**（AI-ASM-001，trading_session._validate_and_submit 整批 Hard Block） |

## 5. 核心逻辑

```
四时点清单（43 号 §3.3）：
PRE_MARKET(08:00 截止): prev_day_review/today_plan/risk_checklist → 超时 WARNING
INTRADAY(实时): signal_compliance_check/risk_param_confirm/position_limit_verify → 缺失 HARD_BLOCK
POST_MARKET(次日 09:15 截止): decision_review/deviation_analysis/discipline_self_assessment → 超时 WARNING
EVENING(次日 08:00 截止): close_data_archive/tomorrow_strategy/risk_forecast → 超时 WARNING

判定：全完成→NONE；截止前缺失→NONE（进行中）；超时缺失→WARNING（INTRADAY 任何缺失→HARD_BLOCK）
跨日语义：盘后/晚间截止=次日，trade_date 由调用方显式传入（前一交易日）
```

## 6. 接口

```python
ChecklistCompletionChecker(completion_provider, logger=None, *,
                           pre_market_deadline=time(8,0),
                           post_market_deadline=time(9,15),
                           evening_deadline=time(8,0))
.check_checkpoint(checkpoint: ChecklistCheckpoint, now: datetime,
                  trade_date: date | None = None) -> ChecklistVerdict
# ChecklistVerdict(checkpoint, complete, missing_items, action[NONE|WARNING|HARD_BLOCK], checked_at, detail)
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 信号源注入而非直连工作流 | 43 号 §3.4：不侵入复盘/分析模块内部；artifact 存在性由编排层供给 |
| 截止前缺失不告警 | 清单是自律辅助，截止前属正常进行中，告警=噪音 |
| 盘中项失效拒单 | §1.3 Fail-Closed 铁律：合规检测失效降级方向一律更保守 |

## 8. 测试计划

tests/compliance/test_discipline_must_do_checker.py — 11 用例：全完成/截止前/超时/盘中阻断/部分缺失/跨日不超时/次日超时/信号源失效两分支/落日志/自定义截止。

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CMP-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CMP-001` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-CMP-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CMP-001 | MOD-CMP-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
