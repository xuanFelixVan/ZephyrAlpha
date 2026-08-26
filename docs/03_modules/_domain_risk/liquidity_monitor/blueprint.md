---
module_id: MOD-RK-08
doc_type: blueprint
ttl: permanent
blueprint_id: MOD-RK-08
domain_id: D_RISK
path: src/zephyr/risk/core/liquidity_monitor.py
design_maturity: production
build_status: stable
granularity: file
ai_autonomy: ai_modifiable
safety: L
stability: evolving
responsibility_domain: 
---

# MOD-RK-08 流动性监控器 (LiquidityMonitor)

## 1. 定位

D_RISK 域 A 类基础设施——纯机制零参数流动性监控。消费 OHLCV 数据，
计算 Amihud 非流动性指标 + 成交量萎缩比率，产出 `LiquidityMetrics`。

与 `ashare_systemic_risk_detector.py` 的 LIQUIDITY_CRISIS 信号互补：
- 系统性风险检测器：买卖价差扩大 + 卖盘压力 → 紧急性流动性危机（盘内即时）
- 本模块：Amihud + 成交量萎缩 → 结构性流动性恶化（日频趋势）

## 2. 输入/输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | OHLCV DataFrame (close + volume) | pandas.DataFrame |
| 输入 | bid_ask_spread (可选) | float |
| 输出 | LiquidityMetrics | frozen dataclass |

## 3. 核心规则

### 3.1 Amihud 非流动性指标

```
ILLIQ_d = |r_d| / V_d
```
- r_d = 日收益率 = (close_d - close_{d-1}) / close_{d-1}
- V_d = 日成交额（元）
- ILLIQ_N = (1/N) × Σ_{d=1}^{N} ILLIQ_d  （N日均值）

阈值：ILLIQ_N > 1e-8 → is_illiquid=True（阈值来源：A股经验值）

### 3.2 成交量萎缩比率

```
V_ratio = V_t / MA(V, N)
```
- V_t = 当日成交额
- MA(V, N) = N日成交额移动平均

阈值：V_ratio < 0.5 → volume_shrinkage=True

### 3.3 综合判定

is_illiquid = (amihud_illiq > amihud_threshold) OR (volume_shrinkage_ratio < volume_threshold)

## 4. 契约

| 契约ID | 方向 | 描述 |
|--------|------|------|
| CTR-006 | 消费 | OHLCV 标准化行情数据 |
| CTR-P1-018 | 生产 | LiquidityMetrics 流动性指标 |

## 5. 依赖

| 依赖 | 类型 | 用途 |
|------|------|------|
| zephyr.risk.risk_manager_base | import | RiskReport/RiskCheckResult 类型 |
| pandas | import | DataFrame 计算 |

## 6. 验收标准

- [x] Amihud 计算正确（与手工计算一致）
- [x] 成交量萎缩比率正确
- [x] 单元测试 ≥ 15 个
- [ ] 延迟 < 100ms（单标的 20 日窗口）
- [ ] 接入编排器

## 7. 施工步骤

- S1: depgraph 登记 ✓
- S2: 五图对齐 ✓
- S3: 写代码（Amihud + 成交量萎缩）
- S4: 测试
- S5: 状态转换 + 验收
- S6: 接入编排器

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-08`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-08` 的 5 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-08` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-08 | MOD-RK-08 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 5 文件 | N/A | — |

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
| `src/zephyr/risk/core/liquidity_monitor.py` | ✅ 已实现 | |
| `src/zephyr/risk/core/risk_budget_allocator.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_liquidity_monitor.py` | ✅ 已实现 | |
| `tests/risk/core/test_orchestrator_liquidity_integration.py` | ✅ 已实现 | |
| `tests/risk/test_risk_budget_allocator.py` | ✅ 已实现 | |

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


