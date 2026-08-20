---
module_id: MOD-GOV-045
title: "降级/回退五态状态机蓝图 — 53 号 §3.8 伪代码代码落地（#ARCH-QUANT-003）"
doc_type: blueprint
status: Active
version: "0.1.11"
ttl: permanent
layer: L1_foundation
layer_name: governance
functional_domain: governance
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-17"
last_updated: "2026-08-17"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-GOV-045 Rollback State Machine — 降级状态机 蓝图

> **module_id**: MOD-GOV-045 | **域**: D_GOVERNANCE | **层**: L1_foundation
> **优先级**: P1 | **成熟度**: production | **设计真源**: 53_simulation_live_path.md §3.8（G24；#ARCH-QUANT-003 方案 C）

## 1. 定位

D_GOVERNANCE 域 lifecycle_governance 包安全设施——策略模拟→实盘迁移期的**降级/回退五态有限状态机**（NORMAL/THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING）。

维度分工（#ARCH-QUANT-003 方案 C，按维度各一真源）：降级维度（快变量/每 tick 评估/自动触发/单向更保守）唯一真源=本模块；阶段维度（慢变量/晋级仪式/人工审批）唯一真源=同包 paper_live_transition.py 三阶段。两机唯一耦合点=阶段晋级前置"当前降级姿态=NORMAL"。与 src/zephyr/infrastructure/rollback/rollback_state_machine.py（回滚步骤编排机 RollbackStep/StepStatus）仅同名巧合，零关系。

## 2. 输入 / 输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | metrics（intraday_dd/daily_loss/reject_rate/circuit_breaker/p0_event/reject_rate_duration_s） | dict |
| 输入 | 当前状态 + 累计交易笔数 | RollbackState / int |
| 输入 | 恢复三要素（rca_written/dual_approval/position_flat） | bool |
| 输入 | 持久化记录（JsonStateStore 命名空间 rollback_state） | dict / None / StateCorruptError |
| 输出 | 新状态（等于当前或更保守态） | RollbackState |
| 输出 | 持久化载荷（state/reason/trade_count/updated_at） | dict（原子写） |

## 3. 核心规则

- 五态序=保守程度序：NORMAL < THROTTLED < SOFT_HALT < HARD_HALT < UNWINDING
- 自动迁移只向更保守（每 tick 单步梯子）：NORMAL→THROTTLED（soft 超限）→SOFT_HALT（hard 超限/持续 60s）→HARD_HALT（daily_loss≥3%/熔断/P0）；HARD_HALT→UNWINDING 不自动
- Hysteresis：trip≠recover（intraday_dd 0.01/0.003；daily_loss 0.03/0.00；reject_rate 0.01/0.005）——recover 仅人工参考，不参与自动迁移
- 样本地板：自动降级须累计 ≥30 笔（AlphaFactory G2.2），P0 事件绕过
- 恢复=人工专用 recover()：RCA 已写+双人复核缺一 PermissionError；反向/同级 ValueError；UNWINDING→NORMAL 须 position_flat=True（T+1：当日买入不可卖，仅 T-1 持仓可平）
- fail-closed：读取失败/无持久化/畸形一律 SOFT_HALT（停错代价<不停代价；与 circuit breaker fail-open 职责相反）

## 4. 关键不变量 (INVARIANTS)

- 自动迁移方向不变量：to_idx > from_idx，无自动恢复路径
- recover() 检查序：权限（RCA+双人）→ 方向（更宽松）→ 仓位（UNWINDING 须平）
- 持久化只消费 JsonStateStore 公开接口（save/load 三分语义），不碰实现内部
- 本模块永不生成/撤销订单——只产出姿态；执行动作由消费方按姿态执行

## 5. 错误契约

| 异常 | 触发 |
|------|------|
| PermissionError | recover 缺 RCA 已写或双人复核；check_promotion_allowed 姿态非 NORMAL（耦合点，paper_live_transition 侧） |
| ValueError | recover 目标非更宽松态 / UNWINDING 仓位未平 |

## 6. 数据模型

- `RollbackState(str, Enum)`：NORMAL/THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING
- 持久化载荷：`{"state": str, "reason": str, "trade_count": int, "updated_at": ISO8601}`（JsonStateStore 命名空间 `rollback_state`，原子写 pid-tmp+os.replace）

## 7. API

- `evaluate_rollback(metrics, current, trade_count) -> RollbackState`（每 tick 评估，单向降级）
- `recover(current, target, rca_written, dual_approval, position_flat) -> RollbackState`（人工恢复）
- `safe_read_state(persisted) -> RollbackState`（fail-closed 纯函数）
- `persist_state(store, state, *, reason="", trade_count=0) -> Path` / `load_persisted_state(store) -> RollbackState`（持久化对）
- 耦合点：`paper_live_transition.check_promotion_allowed(posture)`（非 NORMAL → PermissionError）

## 8. 依赖

- zephyr.shared.state_store（JsonStateStore/StateCorruptError，#ARCH-QUANT-002 承载层，production）
- 消费方：paper_live_transition.py（晋级前置校验）；后续执行层（撤单/阻断/平仓动作按姿态执行，待 SHADOW 阶段接线）

## 9. 测试

tests/governance/trading/test_degradation_rollback_fsm.py——五态枚举序/迁移矩阵全路径/单步梯子/无自动恢复/Hysteresis 不对称/29 笔不触发+30 笔触发边界/P0 绕过地板/recover 权限三件套/fail-closed 畸形持久化/持久化 roundtrip/重启存活/晋级耦合点参数化，57 项全绿（2026-08-17）。

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/governance/trading/test_degradation_rollback_fsm.py` | ✅ 已实现 | |

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

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-GOV-045`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-GOV-045` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-GOV-045` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-GOV-045 | MOD-GOV-045 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
