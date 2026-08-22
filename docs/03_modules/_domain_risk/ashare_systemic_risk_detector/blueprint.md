---
module_id: MOD-RK-10
title: "A股系统性风险检测器蓝图 — 5信号扫描 + 三级警报 + 情绪断路器"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
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

# MOD-RK-10 A-Share Systemic Risk Detector — A股系统性风险检测器 蓝图

> **module_id**: MOD-RK-10 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●, C-020◐(外围冲击)
> **SSoT**: depgraph MOD-RK-10 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-10, §6 决策记录(A股系统性风险5信号)

## 1. 定位

A股系统性风险检测器——扫描5大系统性风险信号, 按触发信号数判定三级警报,
LEVEL_3 时联动 RK-17 Kill Switch 执行清仓:
- 5大信号: 融资盘平仓潮 / 量化踩踏 / 流动性危机 / 政策转向 / 外围冲击
- 三级警报: 1信号停开仓 / 2信号降仓30% / ≥3信号清仓
- 情绪断路器: 情绪指数超阈值 → 强制升级至 LEVEL_3
- 逃生执行器: LEVEL_3 时产出逃生指令 (清仓+撤单+暂停)

属 A 类基础设施(信号扫描 + 阈值判定, 逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 融资余额变化+跌停数+指数涨跌+成交量+价差+卖压+政策标志+外围+情绪 | — |
| 输出 | SystemicRiskAlert(signals/level/action/position_cap/kill_switch) | → RK-17 Kill Switch |
| 依赖 | RK-17 Kill Switch (LEVEL_3 清仓联动) | L1 依赖先行 |

## 3. 核心规则 (设计真源 §1.2 RK-10, §6)

### 3.1 5大信号扫描

| 信号 | 触发条件 (双因子 AND) | 默认阈值 |
|------|---------------------|---------|
| 1. 融资盘平仓潮 | 融资余额急降 AND 跌停股数超阈值 | ≤-3% AND ≥50只 |
| 2. 量化踩踏 | 指数快速下跌 AND 成交量激增 | ≤-2% AND ≥2.0x |
| 3. 流动性危机 | 卖盘压力 AND 买卖价差扩大 | ≥0.65 AND ≥0.5% |
| 4. 政策转向 | 政策信号转向标志 | flag=True |
| 5. 外围冲击 | 外围市场大跌 | ≤-3% |

> 信号1/2/3 为双因子 AND (两者均触发才算), 信号4/5 为单因子。

### 3.2 三级警报 (按触发信号数)

| 级别 | 信号数 | 动作 | 仓位上限 | Kill Switch |
|------|:------:|------|:--------:|:-----------:|
| NONE | 0 | 正常交易 | 100% | ❌ |
| LEVEL_1 | 1 | 停止新开仓, 仅允许减仓 | 100% (现有不动) | ❌ |
| LEVEL_2 | 2 | 仓位上限降至 70% (降30%) | 70% | ❌ |
| LEVEL_3 | ≥3 | 清仓 + 撤单 + 暂停 + Kill Switch | 0% | ✅ |

### 3.3 情绪断路器

- 情绪指数 >= 0.85 (极度恐慌) → 强制升级至 LEVEL_3
- 即使信号数 < 3, 情绪断路器触发即升级
- 已 LEVEL_3 时不重复升级

### 3.4 逃生执行器

- LEVEL_3 时产出逃生指令: liquidate_all + cancel_pending_orders + halt_new_orders
- 供 RK-17 Kill Switch 执行
- 非 LEVEL_3 调用 build_escape_directive → 抛异常

## 4. 关键不变量 (INVARIANTS)

- 5大信号互斥检测 (各自独立判定)
- 三级警报按信号数递进: 0=NONE, 1=LEVEL_1, 2=LEVEL_2, ≥3=LEVEL_3
- LEVEL_3 必须联动 RK-17 Kill Switch (kill_switch_required=True)
- 情绪断路器超阈值 → 强制升级至 LEVEL_3 (不论信号数)
- 仓位上限递减: LEVEL_1(100%) > LEVEL_2(70%) > LEVEL_3(0%)
- 双因子信号(1/2/3)需两因子均触发才算一次信号

## 5. 错误契约

- `InvalidSystemicRiskInputError` (ZA-RK-0010): 输入非法(阈值符号错/范围越界/级别非递进/逃生指令非LEVEL_3)

## 6. 测试

- `tests/risk/test_ashare_systemic_risk_detector.py` (34 用例)
- 覆盖: 5信号各自触发/不触发、三级警报、情绪断路器强制升级、逃生执行器、双因子AND逻辑、部分输入跳过、自定义配置、to_dict

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: RK-17 Kill Switch (LEVEL_3 清仓联动), RK-03 Portfolio Risk Monitor (告警)
- 替代: 陈旧节点 MOD-RSK-010 (src/zephyr/risk/ashare_systemic_risk_detector.py, 文件不存在, 已软删除)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-10`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-10` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-10` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-10 | MOD-RK-10 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/ashare_systemic_risk_detector.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_ashare_systemic_risk_detector.py` | ✅ 已实现 | |

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


