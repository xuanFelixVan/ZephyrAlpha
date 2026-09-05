---
module_id: MOD-TRADING-008
title: "D-SIGNAL-150 策略异常退出处理蓝图 — 冻结/撤单/平仓/核对/置态/告警审计 MVP"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L03_trading
layer_name: trading
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-TRADING-008
domain_id: D_TRADING
path: src/zephyr/trading/strategy_abnormal_exit_orchestrator.py
design_maturity: production
build_status: production
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-TRADING-008 D-SIGNAL-150 策略异常退出处理（Strategy Abnormal Exit Orchestrator）蓝图

> **module_id**: MOD-TRADING-008 | **域**: D_TRADING | **层**: L03 交易运营
> **优先级**: P0 | **来源**: CAND-TRD-002（B10-02264，AUD-DRAFT-001-DIGEST P0 波 W2a）

## 1. 定位

策略异常安全退出的**编排面**（业界对标：Lean 算法异常 liquidate；vnpy 策略停止回收）。
场内现状：通用优雅清理器 `finalizer.py`（K8s Finalizer 式，MOD-INF-035）与
`stop_gate.py`（session 质量闸门）在位，但缺**策略级**异常退出的仓位清理与安全退出编排。

五步编排（顺序固定）：

1. **冻结新信号**——阻断策略后续信号流入（防边退边开）；
2. **按优先级撤单/平仓**——撤单与平仓均按优先级降序执行；
3. **仓位清理核对**——核对残留仓位，残留即不得宣称退出完成；
4. **状态置 EXITED**——经 `StrategyLifecycleEvent`（CTR-P1-006 契约）留痕状态迁移；
5. **告警与审计留痕**——触发即告警，每阶段落审计，失败升级告警。

覆盖三触发路径：**崩溃（CRASH）/ 超时（TIMEOUT）/ 风控触发（RISK_TRIGGERED）**。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | AbnormalExitRequest（strategy_id/trigger/reason/open_orders/positions/idempotency_key）+ 注入端口（冻结器/撤单器/平仓器/核对器/生命周期记录器/告警/审计） | frozen dataclass |
| 输出 | AbnormalExitReport（final_status=EXITED/EXIT_FAILED、各阶段结果、残留仓位、告警与审计计数） | frozen dataclass |

## 3. 核心规则

1. 编排顺序固定：冻结 → 撤单 → 平仓 → 核对 → 置态 → 告警/审计；不得乱序。
2. **冻结失败不宣称 EXITED**（Fail-Closed：新信号可能继续流入，最终态必为 EXIT_FAILED + 升级告警），但撤单/平仓仍继续（安全方向）。
3. 撤单/平仓按优先级降序；单腿失败记录后继续其余腿，残留由核对阶段兜底。
4. 核对发现残留仓位 → final_status=EXIT_FAILED，不置 EXITED，升级告警。
5. 幂等：同 idempotency_key 重复请求返回缓存报告，不重复执行。
6. 纯编排无 IO；执行细节（券商撤单/平仓）全部经注入端口，时钟可注入保判定确定性。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| StrategyLifecycleEvent（状态迁移契约） | zephyr.shared.contracts.strategy_lifecycle_event（MOD-INF-016） | import |
| ZephyrBaseError（错误契约基类） | zephyr.shared.foundation.errors（MOD-INF-016） | import |

集成（运行时装配批接线，本模块不 import 不复制）：`finalizer.py` 可
`register("strategy-abnormal-exit", cleanup)` 消费 `make_finalizer_cleanup()` 产物；
`stop_gate` 语义为 session 质量闸门，可消费 `has_unresolved_exits()` 判定未决退出。

## 5. 测试锚点

- 三触发路径（CRASH/TIMEOUT/RISK_TRIGGERED）全覆盖；
- 冻结失败 → EXIT_FAILED 且撤单/平仓仍执行；
- 优先级降序撤单/平仓次序断言；
- 核对残留 → EXIT_FAILED + 升级告警；
- 幂等键重放 → 同一报告缓存返回；
- 端口异常隔离（单腿失败不中断编排）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-008`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-008` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-008` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-008 | MOD-TRADING-008 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
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
| — | — | 本模块尚无已实现代码 |

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


