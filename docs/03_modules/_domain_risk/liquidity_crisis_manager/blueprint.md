---
module_id: MOD-RK-21
title: "流动性危机管理器蓝图 — 37号流动性危机协议 6 项算法施工落地"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-14"
last_updated: "2026-08-17"
blueprint_level: module
blueprint_id: MOD-RK-21
domain_id: D_RISK
path: src/zephyr/risk/core/liquidity_crisis_manager.py
design_maturity: production
build_status: stable
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-RK-21 流动性危机管理器 (LiquidityCrisisManager)

## 1. 定位

D_RISK 域盘中流动性危机管理辅助层——37号设计备忘
（37_liquidity_crisis_protocol v1.0.18，G18）的施工落地模块。承载 memo 已定义
但未落码的 6 项算法，与 MOD-RK-10/MOD-RK-08 互补不重复：

- 37号 §3.1.1 `compute_sell_pressure`：OBI 反转卖盘压力（ΣVolAsk/(ΣVolBid+ΣVolAsk)）
- 37号 §3.1.2 `compute_bid_ask_spread`：Quoted Spread 买卖价差 (ask-bid)/mid
- 37号 §3.5.1 `detect_limit_status`：A股涨跌停五状态检测（涨跌停时 spread 失效）
- 37号 §3.5 `resolve_effective_spread`：跌停置 1.0 / 涨停置 None（算法断裂修复）
- 37号 §3.6 `check_recovery` + `LiquidityRecoveryState`：危机恢复（hysteresis 半阈值 + 最短持续时间门控）
- 37号 §3.8 `run_intraday_liquidity_check`：盘中流动性监控单遍编排（涨跌停→检测→响应→恢复）
- 37号 §3.2a `compute_ipo_liquidity_drain`：IPO 流动性抽离前瞻预警（四级仓位上限调整）

**设计边界（37号 §4.1）**：不新建独立检测器——危机检测委托 MOD-RK-10
`AshareSystemicRiskDetector.check()`，触发阈值一律从 `detector.config` 读取，
本模块不提供第二套检测阈值（检测真源唯一，消除两处真相源）。
本模块无内部轮询/定时器——由调用方（盘中风控循环 30s tick，对齐 35号 §3.13）
逐 tick 驱动（事件驱动铁律 trae_060）。

与既有模块的分工：

| 模块 | 时间尺度 | 职责 |
|------|---------|------|
| MOD-RK-10 AshareSystemicRiskDetector | 盘内秒级 | 5 信号检测 + 三级警报 + 逃生指令（本模块委托其检测） |
| MOD-RK-22 LiquidityMonitor | 日频 | Amihud + 成交量萎缩（结构性恶化，事后检测） |
| MOD-RK-21 本模块 | 盘内 tick | 盘口特征计算 + 涨跌停处理 + 恢复状态机 + 编排 + IPO 前瞻预警 |

## 2. 输入/输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | MarketLiquiditySnapshot（盘口快照，对齐 miniQMT get_full_tick 五档） | frozen dataclass |
| 输入 | LiquidityRecoveryState（危机恢复状态，调用方持有跨 tick） | dataclass |
| 输入 | RecoveryCheckInput（恢复判定入参，阈值真源从 detector.config 读取） | frozen dataclass |
| 输入 | IPOEvent 列表 + 全市场 20 日均成交额（亿元） | frozen dataclass / float |
| 输出 | LiquidityLoopResult（alert + halt_new_orders + position_cap + recovery_target） | frozen dataclass |
| 输出 | IPOLiquidityDrain（drain_ratio / drain_level / position_cap_adjustment） | frozen dataclass |

## 3. 核心规则

### 3.1 卖盘压力（37号 §3.1.1）

```
sell_pressure = ΣVolAsk / (ΣVolBid + ΣVolAsk)   # 等价 (1-OBI)/2，值域 [0,1]
```

- 无盘口数据返回 0.5（中性值不触发）
- 0.65 触发阈值真源 = MOD-RK-10 AshareSystemicRiskConfig.sell_pressure_threshold

### 3.2 买卖价差（37号 §3.1.2）

```
spread = (ask - bid) / mid,  mid = (ask + bid) / 2
```

- 盘口缺失/非法返回 None（检测器跳过检查）
- 0.005（0.5%）触发阈值真源 = MOD-RK-10 AshareSystemicRiskConfig.bid_ask_spread_threshold

### 3.3 涨跌停检测与有效价差（37号 §3.5/§3.5.1）

- LIMIT_UP：价达涨停 + 卖一缺失 → effective_spread=None（买压主导，不触发危机）
- LIMIT_DOWN：价达跌停 + 买一缺失 → effective_spread=1.0（跌停=平仓通道冻结=危机子类，使 AND 可满足）
- NEAR_UP/NEAR_DOWN：距板 <0.5% 提前预警（不触发危机）
- 判定顺序：精确封板（封单消失）先于接近判定

### 3.4 危机恢复（37号 §3.6）

- hysteresis 双阈值：恢复阈值 < 触发阈值（spread 半阈值=触发×0.5；卖压 0.50）
- 最短持续时间门控：LEVEL_1 10min / LEVEL_2 15min / LEVEL_3 30min（覆盖 Kill Switch 冷却）
- 恢复路径：L1→0（双半阈值+0 信号）/ L2→1（信号≤1+spread<半阈值×1.2）/ L3→2（信号≤2+冷却期满）
- ⚠️ target_level=0 是有效恢复，调用方须 `is not None` 判定（37号 v1.0.16 已修真值检查 bug）

### 3.5 IPO 流动性抽离（37号 §3.2a）

```
drain_ratio = 未来 5 日 IPO 募资总额 / 全市场 20 日均成交额（亿元）
```

| drain_ratio | drain_level | position_cap_adjustment |
|---|---|---|
| <1% | NEGLIGIBLE | 1.0 |
| 1-2% | MODERATE | 0.90 |
| 2-3% | SEVERE | 0.75 |
| ≥3% | EXTREME | 0.60 |

## 4. 依赖

| 依赖 | 类型 | 用途 |
|------|------|------|
| zephyr.risk.core.ashare_systemic_risk_detector (MOD-RK-10) | import | 危机检测 + 逃生指令（检测真源唯一） |
| zephyr.shared.foundation.errors | import | ZephyrBaseError 基类 |

## 5. 验收标准

- [x] sell_pressure / spread / 涨跌停检测 / 恢复判定 / IPO 预警计算正确（手工验证）
- [x] 跌停时 spread 置 1.0 触发危机（37号 v1.0.2 算法断裂修复不回退）
- [x] 涨停时不触发危机
- [x] 恢复经 min_hold 门控 + hysteresis 半阈值（临界值不 thrashing）
- [x] 单元测试 54 个全通过
- [ ] 接入盘中风控循环调用方（35号 §3.13 同 tick，由编排层会话施工）
- [ ] IPO 数据源接入（akshare stock_ipo_info 当前不存在，见 37号 §6 待裁定）

## 6. 施工步骤

- S1: depgraph 设计态登记 ✓（blueprint_id=MOD-RK-21 file 节点，design 边 ×2）
- S2: 五图对齐 ✓（sync 991 模块 0 失败；无新增孤儿/域不一致）
- S3: 写代码（6 项算法落码）✓
- S4: 测试（54 passed）✓
- S5: 状态转换 + 验收
- S6: 接入编排层（调用方施工，非本模块范围）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-21`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-21` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-21` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-21 | MOD-RK-21 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_liquidity_crisis_manager.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
