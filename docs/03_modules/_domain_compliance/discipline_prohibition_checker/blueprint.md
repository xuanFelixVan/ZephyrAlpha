---
module_id: MOD-CMP-002
title: "四项严禁纪律闸蓝图 — 追高/补仓/骄傲/报复检测 + KillSwitchLite"
doc_type: blueprint
status: Active
version: "0.1.11"
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

# MOD-CMP-002 | Discipline Guard + KillSwitchLite 四项严禁纪律闸

> **域**: D_COMPLIANCE | **优先级**: P0 | **safety**: H | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-002 (node 8661727)

## 1. 模块定位

订单提交前 + 盘中实时检测四类严禁交易行为——踏空追高/被套补仓/盈利骄傲/亏损报复，触发即按等级处置。41 号已定命名与拦截定位（§2.3/§3.1），本模块补检测阈值+检测算法+Kill Switch 轻量版联动（43 号 §4）。BM-BUY-08-B 落地载体（D-COMPLIANCE-23 组件 B）。

依据: `43_compliance_discipline.md` §4

## 2. 不变量 (INVARIANTS)

- 追高/补仓/报复 = Hard Block 拒单；骄傲 = Warning 推送不阻断
- 检测引擎失效 → 保守 Hard Block（Fail-Closed，宁可不交易）
- KillSwitchLite 作用域=仅触发策略、当日有效、次日自动复位+人工确认
- KillSwitchLite 失效 → 升级全局 Kill Switch（RC-03，35 号四级梯子）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| DisciplineGuardError | ZA-CMP-0002 | 纪律闸内部错误 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.compliance.compliance_log | ComplianceLogger | 判定/熔断落 compliance_log |
| 消费 | C-004 风控引擎 | DisciplineGuard.check(order, ctx) | 订单提交前嵌入（43 号 §4.3）——**已接线**（AI-ASM-001，trading_session._is_blocked_by_compliance_gates） |
| 消费 | MOD-PA-006 分批建仓 | 同上 | 每批下单前过闸（41 号 §3.6 契约注释）——**已接线**（AI-ASM-001，BatchedPositionBuilder.gate_batch_order） |

## 5. 核心逻辑

```
阈值（43 号 §4.3，chase/win_streak 为 MVP 初始值待 C1 实盘校准）：
1) CHASING: price/signal_ref_price-1 > +2% 且 surge_30min > +5% → HARD_BLOCK
   （41 号 §3.5 限价锚定=事前预防，本检测=事后拦截，两层互补；浮点尾差 ε=1e-9）
2) ADDING_TO_LOSER: is_add 且 position_pnl_pct < -5% → HARD_BLOCK
3) REVENGE_TRADING: daily_pnl_pct < -2% 且 (频率>2.0×20日基线 或 单笔>1.5×基线)
   → HARD_BLOCK + KillSwitchLite.trigger(strategy_id, 当日收盘失效)
4) OVERCONFIDENCE: win_streak ≥5 且 risk_exposure > 1.5×常规 → WARNING
判定优先级：报复 > 追高/补仓（Hard Block 先于 Warning）
```

## 6. 接口

```python
DisciplineGuard(thresholds=None, kill_switch=None, logger=None)
.check(order: OrderRequest, ctx: DisciplineContext) -> DisciplineVerdict
KillSwitchLite(state_path=None, on_escalate=None, logger=None)
.trigger(strategy_id, reason, trade_date) -> bool
.is_blocked(strategy_id, today) -> bool   # 状态不可读→True（Fail-Closed）
.reset(strategy_id) -> bool               # 人工确认复盘后解除
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 报复判定先于骄傲 | Hard Block 优先于 Warning，防"骄傲 Warning 遮蔽报复阻断" |
| 频率用 projected_daily_freq | 盘中部分日频率与全日基线不可比，调用方外推后传入 |
| 信号锚缺失跳过追高检测 | 无锚不可判；锚缺失本身由上游信号链保证（留 detail 备查） |
| KillSwitchLite 状态落 JSON 文件 | MVP 轻量；状态损坏=Fail-Closed 阻断+升级全局 |

## 8. 测试计划

tests/compliance/test_discipline_prohibition_checker.py — 18 用例：四行为命中/不命中/边界/优先级、熔断触发-复位-次日自动复位-状态损坏 Fail-Closed 升级、落日志、自定义阈值。

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CMP-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CMP-002` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-CMP-002` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CMP-002 | MOD-CMP-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
