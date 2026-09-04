---
module_id: MOD-REGIME-005
title: "筹码分布引擎蓝图 — 华泰2026前沿VWAP三角分布+筹码龄分层+32相对网格（regime特征管道#12/#5/S2底部筹码数据源）"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
ttl: permanent
layer: L2_domain
layer_name: regime
functional_domain: regime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-06"
last_updated: "2026-08-06"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-REGIME-005 ChipDistributionEngine — 筹码分布引擎 蓝图

> **module_id**: MOD-REGIME-005 | **域**: D_REGIME | **层**: L2 业务域
> **优先级**: P1 | **成熟度**: design | **建设标记**: 🟡 待施工
> **SSoT**: depgraph MOD-REGIME-005 | **算法真源**: 华泰证券2026前沿筹码分布算法
> **消费方**: [RegimeFeatureBuilder](../regime_feature_builder/blueprint.md) MOD-REGIME-002（#12筹码结构 / #5空间位置 / S2底部筹码堆积）

## 0. 本蓝图存在理由（第一性原理）

RegimeFeatureBuilder §5.1.12 原本用"换手率代理"计算 #12 筹码结构——**换手率≠筹码分布**。换手率高只代表交易活跃，不代表筹码在哪个价位堆积。用户 2026-08-06 明确要求"不能用代理，应该有自己的算法"。华泰证券 2026 前沿算法用 VWAP 中心三角分布换手递推，从 OHLCV 数据自建筹码分布，无需额外数据源。

## 1. 定位

筹码分布引擎——从 OHLCV 数据计算个股/指数的筹码分布（每个价位上的筹码量），供 regime 特征管道判断套牢盘/底部堆积/高位派发。

属 **B 类核心业务模块**（特征工程 + 递推算法），算法参数为 C 类可调参数。

### 1.1 核心算法（华泰2026前沿）

```
# 换手递推公式（核心）：
# C_t(p) = (1-τ_t) × C_{t-1}(p) + τ_t × D_t(p)
#
# τ_t = 当日换手率（volume / 流通股本）
# D_t(p) = 当日三角分布密度（以VWAP为中心，[low, high]为范围）
# C_t(p) = 价格p处的筹码量（t日收盘后）
```

**三层增强**：
1. **筹码龄分层**：超短期(1-2天)/短期(3-10天)/中期(11-100天)/长期(101+天)，每层独立递推
2. **投资者类型分层**：小单/中单/大单/超大单（对接 money_flow 表），各类型独立分布
3. **32相对网格映射**：绝对价格→32个相对网格(0=最低,31=最高)，实现跨股比较

### 1.2 不做什么

- **不做 regime 判定**（归 MOD-REGIME-001）
- **不做 Shrinkage 计算**（归 MOD-REGIME-001）
- **不做选股/仓位**（归 StrategyBook / MOD-POS-001）
- **只产出筹码分布数据**，四档系数映射由 RegimeFeatureBuilder §5.1.12 完成

## 2. 输入 / 输出

### 2.1 输入

| category_id | 全限定表名 | 用途 | 就绪 |
|-------------|-----------|------|:----:|
| market_kline_daily | c1_market.kline_daily | OHLCV（VWAP计算+换手率） | ✅ |
| market_money_flow | c1_market.money_flow | 投资者类型分层（超大/大/中/小单净流入） | ✅ |

> **无需额外数据源**：筹码分布从 OHLCV 自建，不依赖外部筹码数据。

### 2.2 输出

```python
chip_distribution: dict[str, Any] = {
    "symbol": str,                    # 标的代码
    "date": datetime,                 # 计算日期
    "grid_prices": list[float],       # 32个相对网格对应的价格（0=最低,31=最高）
    "total_distribution": list[float], # 32网格的总筹码分布（归一化，Σ=1.0）
    "age_layers": {                   # 筹码龄分层分布
        "ultra_short": list[float],   # 超短期(1-2天) 32网格分布
        "short": list[float],         # 短期(3-10天)
        "medium": list[float],        # 中期(11-100天)
        "long": list[float],          # 长期(101+天)
    },
    "investor_layers": {              # 投资者类型分层分布（可选，需money_flow）
        "super_large": list[float],   # 超大单分布
        "large": list[float],         # 大单分布
        "medium": list[float],        # 中单分布
        "small": list[float],         # 小单分布
    },
    "metrics": {                      # 衍生指标（供RegimeFeatureBuilder直接消费）
        "long_term_bottom_ratio": float,    # 长期桶底部网格占比（#12健康度）
        "upper_trap_peak": float,           # 上方套牢峰强度
        "bottom_accumulation": float,       # 底部堆积度
        "distribution_migration": float,    # 筹码迁移方向（正=上移派发，负=下移吸筹）
    },
    "schema_version": str,            # "1.0"
}
```

## 3. 核心算法详细

### 3.1 VWAP中心三角分布（当日增量 D_t(p)）

```
# 当日成交的筹码假设服从以VWAP为中心的三角分布
vwap = sum(amount) / sum(volume)          # 成交量加权均价
price_low = low                            # 当日最低价
price_high = high                          # 当日最高价
price_range = price_high - price_low

# 三角分布概率密度函数
def triangular_pdf(p, center=vwap, low=price_low, high=price_high):
    if p < low or p > high:
        return 0.0
    if p <= center:
        return 2 * (p - low) / (price_range * (center - low))
    else:
        return 2 * (high - p) / (price_range * (high - center))

# 离散化到价格网格
D_t = [triangular_pdf(p_i) for p_i in grid_prices]
D_t = normalize(D_t)   # 归一化 Σ=1.0
```

> **设计理由**：三角分布是 OHLCV 数据中最合理的当日成交价格分布假设——VWAP 是重心（峰值），low/high 是边界。比均匀分布更合理，比正态分布少假设（不需要标准差）。

### 3.2 换手递推（核心公式）

```
# 初始化：C_0 = 均匀分布（或上市首日分布）
# 每日递推：
for t in range(1, T):
    tau_t = volume_t / circulating_shares_t   # 换手率
    C_t = (1 - tau_t) * C_{t-1} + tau_t * D_t
    # 旧筹码按(1-τ)衰减，新筹码按τ注入

# 递推性质：
# - 高换手日：旧筹码快速衰减，新筹码快速注入（筹码快速换手）
# - 低换手日：旧筹码保留，新筹码少量注入（筹码稳定）
# - 极端情况 τ=1（100%换手）：C_t = D_t（完全替换）
# - 极端情况 τ=0（零换手）：C_t = C_{t-1}（完全保留）
```

### 3.3 筹码龄分层（时间维度）

```
# 4层独立递推，跟踪不同"年龄"的筹码
# 每日新注入的筹码 D_t 进入 ultra_short 层
# 按时间规则跨层迁移：

# ultra_short(1-2天): 持有1-2天的筹码
#   每日: ultra_short = (1-τ) * ultra_short + τ * D_t
#   2天后未换手的筹码迁移到 short

# short(3-10天): 持有3-10天的筹码
#   每日: short = (1-τ) * short + 迁入_from_ultra_short
#   10天后未换手的筹码迁移到 medium

# medium(11-100天): 持有11-100天的筹码
#   每日: medium = (1-τ) * medium + 迁入_from_short
#   100天后未换手的筹码迁移到 long

# long(101+天): 持有101天以上的筹码（"死筹码"）
#   每日: long = (1-τ) * long + 迁入_from_medium
#   long层筹码占比高 = 底部堆积（长期持有者未卖）

# 迁移规则简化实现：
#   每日检查各层筹码的"年龄"，超龄的迁移到下一层
#   实际实现可用衰减系数近似（避免逐日追踪每个筹码的年龄）
```

### 3.4 投资者类型分层（对接 money_flow）

```
# 从 money_flow 表获取各类型投资者净流入
super_large_net = money_flow.super_large_net_inflow   # 超大单净流入
large_net = money_flow.large_net_inflow               # 大单净流入
medium_net = money_flow.medium_net_inflow             # 中单净流入
small_net = money_flow.small_net_inflow               # 小单净流入

# 各类型独立分布递推（买入=注入该类型分布，卖出=从该类型分布衰减）
# super_large 买入的筹码假设集中在当日 VWAP 附近（机构大宗交易）
# small 买入的筹码假设分散在当日 [low, high] 均匀分布（散户分散交易）

# 用途：
# - super_large 分布长期底部堆积 = 机构吸筹
# - small 分布高位堆积 = 散户接盘（派发信号）
```

### 3.5 32相对网格映射（跨股比较）

```
# 问题：不同股票价格不同，绝对价格网格无法跨股比较
# 解决：映射到32个相对网格

# 1. 确定"参考区间"
lookback = 250  # 参考过去250个交易日
price_min = min(low over last 250 days)
price_max = max(high over last 250 days)

# 2. 等分32个网格
grid_size = (price_max - price_min) / 32
grid_prices = [price_min + i * grid_size for i in range(32)]
# 网格0 = 最低价，网格31 = 最高价

# 3. 把绝对价格筹码分布映射到相对网格
# C_t(p) → C_t(grid_i)
# 每个网格内的筹码量 = 该价格区间内所有 C_t(p) 的积分

# 4. 归一化
C_t_grid = normalize(C_t_grid)   # Σ=1.0

# 跨股比较：
# - 网格0-7（底部1/4）堆积 = 底部筹码堆积
# - 网格24-31（顶部1/4）堆积 = 高位套牢盘
# - 所有股票用同一套网格定义，可横向比较
```

### 3.6 衍生指标计算（供 RegimeFeatureBuilder 直接消费）

```python
# #12 筹码结构四档判定指标
long_term_bottom_ratio = sum(age_layers["long"][0:8]) / sum(age_layers["long"])
# >0.6 → 健康（底部单峰+长龄堆积）
# 0.3-0.6 → 触及上方套牢峰
# <0.3 → 底部未堆积

upper_trap_peak = max(total_distribution[24:32]) - mean(total_distribution[24:32])
# 套牢峰强度（高位异常堆积）

bottom_accumulation = sum(total_distribution[0:8]) / sum(total_distribution)
# 底部堆积度

distribution_migration = sum(age_layers["long"][24:32]) - sum(age_layers["long"][0:8])
# 正值 = 筹码上移（高位派发）
# 负值 = 筹码下移（底部吸筹）
```

## 4. 关键不变量 (INVARIANTS)

- `total_distribution` Σ=1.0（32网格归一化）
- `age_layers` 各层 Σ=1.0（独立归一化）
- 换手率 τ ∈ [0, 1]，递推不会产生负值
- 32网格网格0=最低价、网格31=最高价，跨股统一定义
- 筹码龄分层4层之和 = total_distribution

## 5. 错误契约

- `ChipDistributionError` (ZA-REGIME-0050): OHLCV数据缺失/NaN
- `VWAPCalculationError` (ZA-REGIME-0051): amount/volume 为0或负值
- `GridMappingError` (ZA-REGIME-0052): 250日参考区间为0（停牌股）

## 6. 测试规划

### Phase 1 测试 (~15)
- 三角分布密度函数正确性（VWAP=峰值，low/high=边界）
- 换手递推正确性（τ=0保留/τ=1替换/τ=0.5混合）
- 筹码龄分层迁移正确性（2天/10天/100天边界）
- 32网格映射正确性（跨股可比性）
- 衍生指标计算（long_term_bottom_ratio/upper_trap_peak/migration）
- 降级：OHLCV缺失时返回均匀分布

### Phase 2 测试 (~5)
- 历史案例验证（2015股灾顶部筹码上移 / 2024底部筹码堆积）
- 投资者类型分层（超大单底部吸筹 vs 散户高位接盘）

## 7. 依赖

### 7.1 上游
| 依赖 | 用途 | 模块 |
|------|------|------|
| TableRegistry | 取表名 | MOD-L00-004 |
| ClickHouse | OHLCV + money_flow 查询 | zephyr.data.providers |
| numpy/pandas | 分布计算 | 标准 |

### 7.2 下游消费
| 消费方 | 消费内容 | 用途 |
|--------|---------|------|
| RegimeFeatureBuilder | chip_distribution 全部 | #12筹码结构四档系数 / #5空间位置 / S2底部筹码堆积 |

### 7.3 depgraph 边
```
MOD-REGIME-005 → MOD-REGIME-002 (RegimeFeatureBuilder 消费筹码分布)
MOD-REGIME-005 → MOD-L00-004 (TableRegistry)
MOD-REGIME-005 → D_DATA (ClickHouse OHLCV + money_flow)
```

## 8. 错误契约与降级

| 错误码 | 场景 | 处理 |
|--------|------|------|
| ZA-REGIME-0050 | OHLCV 数据缺失 | 返回均匀分布（32网格各1/32），标记 degraded |
| ZA-REGIME-0051 | VWAP 计算异常（amount/volume=0） | 用 (open+high+low+close)/4 代替 VWAP |
| ZA-REGIME-0052 | 250日参考区间为0（停牌） | 用可用数据的最小范围，标记 degraded |
| ZA-REGIME-0053 | money_flow 表缺失 | 跳过投资者类型分层，仅输出 total + age_layers |

## 9. 实施阶段

| 阶段 | 内容 | 产出 |
|------|------|------|
| **P1** | VWAP三角分布 + 换手递推 + 32网格映射 | `compute_chip_distribution()` 基础版 |
| **P2** | 筹码龄分层（4层迁移） | `compute_age_layers()` |
| **P3** | 投资者类型分层（对接money_flow） | `compute_investor_layers()` |
| **P4** | 衍生指标 + 历史案例验证 | `compute_metrics()` + 测试 |

> **P1 完成定义**：单股筹码分布递推正确 + 32网格归一化 + 衍生指标可输出。

## 10. 设计决策记录

| 决策 | 理由 |
|------|------|
| VWAP中心三角分布 | OHLCV数据中最合理的当日成交分布假设，比均匀/正态少假设 |
| 换手递推公式 C_t=(1-τ)C_{t-1}+τD_t | 华泰2026前沿算法，从换手率自然推导，物理意义明确 |
| 筹码龄4层分层 | 区分短期投机筹码和长期持有筹码，底部堆积=长期层低位占比高 |
| 32相对网格 | 跨股比较的标准做法，32格平衡精度和计算量 |
| 投资者类型分层 | 超大单底部吸筹 vs 散户高位接盘是A股核心信号 |
| 不依赖外部筹码数据 | 从OHLCV自建，无数据源依赖，适合100%AI开发 |

## 11. 遗留问题

| # | 遗留 | 处理 |
|---|------|------|
| L1 | 筹码龄分层迁移的精确实现（逐日追踪 vs 衰减系数近似） | P2 实现时定，推荐衰减系数近似（计算量低） |
| L2 | money_flow 投资者类型分层的分布假设（超大单集中在VWAP？） | P3 实现时校准，可用大宗交易数据验证 |
| L3 | 250日参考区间的动态更新（walk-forward） | 季度更新参考区间，与HMM walk-forward对齐 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-REGIME-005`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-REGIME-005` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-REGIME-005` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-REGIME-005 | MOD-REGIME-005 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 12. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 12.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 12.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §12（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


