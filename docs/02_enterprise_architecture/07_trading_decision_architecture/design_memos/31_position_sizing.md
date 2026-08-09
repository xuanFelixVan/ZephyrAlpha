---
ttl: permanent
doc_type: architecture_view
title: 仓位算法（分层裁定落地）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.4"
date: 2026-08-08
topic: position_sizing
scope: 07_trading_decision_architecture
---

# 仓位算法（分层裁定落地）

> 本备忘把 [30_multi_strategy_concurrency §2.1](30_multi_strategy_concurrency.md) 已定稿的"分层裁定"框架落地为可施工的参数与接口契约。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 边界：本备忘只定仓位**算法与参数**（how much 的 why+spec）；FirmRiskAggregator 的求和/裁剪**执行逻辑**（G13）、BudgetChangeHandler 三级升级（G14）、RegimeMetaAllocator 参数（G15）不在本备忘范围。

## 1. 背景

### 1.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1，不能做空）
- 多策略并发架构已定稿为 Model A（独立账本 + firm 风险聚合），见 [30_multi_strategy_concurrency §2](30_multi_strategy_concurrency.md)
- 仓位决策采用"分层裁定"（30_multi_strategy_concurrency §2.1 方案 A）：策略层做粗仓位，firm 层做 Kelly 精裁决
- 当前处于施工前阶段，框架已定但缺可施工的参数与接口契约

### 1.2 核心问题
30_multi_strategy_concurrency §2.1 已锁定分层裁定的**框架**（策略层等权/risk parity 不用 Kelly + firm 层 Kelly 精裁决定），但未定义：
- 各策略具体用哪种粗仓位算法、公式是什么
- Kelly 参数（预期收益/方差）从哪来、用几分之几 Kelly
- 单票 8% / 行业 / 总仓位硬上限的具体阈值与裁剪口径
- 分层之间的接口契约（数据结构）
- Kelly 不在策略层重复、不做 MVO 的边界确认

本备忘的工作就是把这些框架变成可施工的 spec。

### 1.3 约束条件
- **system_charter §3 约束四（策略三维度解耦）**：策略 = 选股信号 × 组合权重 × 执行方式（what × how much × how），仓位（how much）必须独立于选股（what）实现 → 强化分层裁定
- **system_charter §3 约束五（少而精）**：3-5 个策略，各策略特性不同，粗仓位算法应差异化适配而非统一一种
- **30_multi_strategy_concurrency §3.1**：不做 MVO，不做协方差估计 → 粗仓位用 inverse-vol（只估 σ），不用 full risk parity（估协方差）
- **30_multi_strategy_concurrency §2.2**：regime 只缩 budget 数值，不调仓位算法 → 仓位算法本身不内置 regime 切换逻辑
- A 股 T+1 / 不能做空 / 打板容量极小（单票几万~几十万）→ 打板必须小账本、粗仓位不能按波动率机械决定

## 2. 决策：分层裁定（策略层粗仓位 + firm 层 Kelly 精裁决 + 硬上限裁剪）

### 2.1 分层流程总览

仓位决策分两段，按以下顺序执行（求和 → Kelly → 裁剪）：

```
[各 StrategyBook]                [FirmRiskAggregator]           [MOD-POS-001]              [FirmRiskAggregator]
策略层粗仓位         →   按标的求和(自然叠加)  →   Kelly精裁决      →    硬上限裁剪        →  firm_target_portfolio
(等权/inverse-vol)        (30_multi_strategy_concurrency §2.3)     (半Kelly+分布感知)     (单票8%/行业/总仓位/现金)
不用Kelly                 O(N) 加法替代优化器        只减不增为主           兜底不可突破
```

**顺序理由**：Kelly 是"精算"（可调大调小，但只减不增为主），裁剪是"兜底"（不可突破）。先精算后兜底——Kelly 看到的是求和后的真实总暴露，精算准确；裁剪是最后安全网，保证输出一定合规。与 battle_map BM-POS-02 → BM-POS-04 的数据流方向一致（Kelly 在前，硬限制在后）。

### 2.2 策略层粗仓位（StrategyBook / MOD-POS-020）

#### 2.2.1 算法映射表（差异化，静态先定，G04 产出后校准）

各策略按类型用不同粗仓位算法。映射表先静态，等 G04（20_first_batch_strategies 首批 3 策略定义）产出后校准：

| 策略类型 | 粗仓位算法 | 理由 |
|---|---|---|
| 打板 | **等权** | 标的少（1-3 只）、容量小；每票仓位本应由连板梯队/情绪周期规则定，不应被波动率机械决定；标的少时 60 日波动率估计噪声大，inverse-vol 反而不如等权稳 |
| 多因子 | **inverse-vol** | 标的分散（10-20 只），inverse-vol 风险均衡有实证收益（Morwane）；只估 σ 不估协方差，鲁棒 |
| 价值反转 / 动量趋势 | **inverse-vol** | 标的分散，同多因子 |
| 事件驱动 | **等权** | 标的少、事件冲击主导，波动率历史估计在事件期失效 |

> **差异化 vs 统一的取舍**：约束五（少而精）下各策略特性差异大，统一一种算法会牺牲适配性。差异化映射表是静态先定（MVP），随策略 track record 积累可演进为动态（按策略滚动 Sharpe 自适应选算法），但 MVP 不做动态。

#### 2.2.2 inverse-vol 公式（Morwane 范式）

```
w_i = (1 / σ_i) / Σ_j (1 / σ_j)

σ_i = 标的 i 的 60 日年化波动率（日收益标准差 × √252）
```

- **窗口选 60 日**：与 RegimeMetaAllocator 的 PerformanceScore（60 日 Sharpe）窗口对齐，统一滚动窗口口径
- **σ_i 缺失/异常（如新股、停牌）**：降级为等权（w_i = 1/N），不阻断
- **只估 σ 不估协方差**：与 30_multi_strategy_concurrency §3.1 拒绝协方差一致。2026 实证（quanthedgeai）确认 inverse-vol 估 1 个参数最鲁棒，12 月数据 ±10% 准确；full risk parity 估协方差（N(N+1)/2 参数），N=5 策略需 60 月数据才 borderline

#### 2.2.3 等权

```
w_i = 1 / N   （N = 策略选出的标的数）
```

#### 2.2.4 策略层输出契约

StrategyBook 输出 `StrategyTarget`：

```python
@dataclass
class StrategyTarget:
    strategy_id: str                          # 策略标识
    target_portfolio: dict[str, float]        # symbol -> 权重（相对策略 budget）
    budget_used: float                        # 实际占用 budget（权重和 ≤ strategy_budget）
    timestamp: datetime
    # 注：策略层不算 Kelly、不估密度 PDF，只输出粗仓位
```

**约束**：`sum(target_portfolio.values()) ≤ strategy_budget`（权重和不超过策略分到的 budget，剩余为该策略保留的现金，由 firm 层统一管理）。

### 2.3 firm 层 Kelly 精裁决（MOD-POS-001）

#### 2.3.1 连续 Kelly 公式

采用**连续形式** Kelly（非二值赌博版 `f*=(bp-q)/b`），更适合多标的组合：

```
K_i = (μ_i - r) / σ_i²

f_i = max(0, 0.5 × K_i)     # 半 Kelly 硬上限 + 不能做空（f_i<0 截 0）

其中：
  μ_i  = 标的 i 的预期总收益（年化，来自密度 PDF 积分，已扣除预期交易成本）
  r    = 无风险利率（年化，取逆回购利率 GC001，与现金管理 §2.5 一致）
  σ_i² = 标的 i 的收益方差（年化，来自密度 PDF 积分）
  f_i  = Kelly 精裁决后的标级仓位建议（≥0，禁做空）
```

- **半 Kelly（0.5×K）是硬上限**：禁全 Kelly。行业共识（2026 多源实证）：full Kelly 回撤 50-80%；half Kelly 保 75% 增长、大幅降回撤；Thorp 本人用 0.25-0.5×；机构普遍 0.2-0.5×
- **连续形式选择理由**：二值版 `f*=(bp-q)/b` 适合单笔输赢赌博，多标的组合收益是连续分布，K=(μ-r)/σ² 是 Markowitz 框架下 Kelly 的连续等价（与 mean-variance 理论衔接），crucible-backtester 2026-07 工程实现亦用此形式
- **不能做空约束（f_i≥0）**：A 股 T+1 不能做空，f_i<0（即 μ_i<r，预期收益低于无风险利率）时截断为 0（不持有），不做空。与 ryanoconnellfinance / xueqiu 实证"f*<0→不下注"一致
- **量纲统一年化**：μ_i、r、σ_i² 均用年化口径，保证 f_i 落在 0~1 量级（如 μ=12%、r=2%、σ=25% → K=(0.12-0.02)/0.0625=1.6 → f=0.8，再受硬上限裁剪）
- **交易成本从 μ 扣除**：μ_i 是扣预期交易成本（佣金+印花税+滑点+冲击，system_charter §3 约束一）后的净收益；薄 edge 扣成本后 K_i≤0 → f_i=0，自动过滤劣质标的

#### 2.3.2 Kelly 参数来源（密度 PDF 主 + 历史降级）

| 参数 | 主源 | 降级源 | 触发降级条件 |
|---|---|---|---|
| μ_i（预期总收益，扣成本后） | 密度 PDF 积分（BM-SEL-13） | 60 日历史均值收益 | BM-SEL-13 未就绪 / 输出异常 |
| r（无风险利率） | 逆回购利率 GC001（市场公开） | 固定 2.5% | 逆回购数据缺失 |
| σ_i²（方差） | 密度 PDF 积分（BM-SEL-13） | 60 日历史方差 | BM-SEL-13 未就绪 / 输出异常 |

- **主源用密度 PDF**：与 battle_map BM-POS-02 现有设计一致（"从条件 PDF 直接积分计算胜率 p 和赔率 b"），能捕捉未来分布的偏度/峰度/厚尾
- **降级用历史回测**：保证施工不被 BM-SEL-13 阻塞；历史回测在 regime 切换时滞后，但作为降级兜底可接受
- **"稳不要锐"原则**（吸收自 Conformal Kelly arXiv 2026-08 发现）：密度 PDF 估计用 slow rolling，**宽度稳定性 > 局部 regime 自适应锐度**——越自适应的估计反而越差。BM-SEL-13 工程实现应避免过度追求 regime 局部锐度

#### 2.3.3 分布感知调整（防御性，只减不增为主）

Kelly 精裁决后，叠加密度 PDF 的分布特征调整（与 battle_map BM-POS-02 一致）：

| 分布特征 | 调整 | 方向 |
|---|---|---|
| 偏度 > 0（正偏=上涨惊喜概率高） | f_i × (1 + α_skew)，但加仓幅度 ≤ 原粗仓位求和值的 10% | 有限加仓（唯一例外） |
| 偏度 < 0（负偏=下跌风险大） | f_i × (1 − \|α_skew\|) | 减仓 |
| 超额峰度 > 0（厚尾=极端事件概率高） | f_i × (1 − β_kurt) | 减仓 |
| 前瞻 VaR_95 > 阈值 | f_i 上限下调 | 减仓 |
| 前瞻 CVaR_95 > 阈值 | f_i 上限进一步下调（比 VaR 更严） | 减仓 |

**约束**：调整后 f_i ≤ 原粗仓位求和值（防御性原则，默认只减不增；正偏例外允许有限加仓 ≤10%）。

#### 2.3.4 Kelly 与粗仓位合成规则

Kelly 精裁决不是"替代"策略层粗仓位，而是对粗仓位求和值做"上限约束 + 分布调整"。合成公式：

```
f_i^final = min(w_i^sum × dist_adj_i, f_i)     且 f_i^final ≥ 0

其中：
  w_i^sum    = 各策略对标的 i 的粗仓位求和值（自然叠加，§2.1）
  dist_adj_i = 分布感知调整因子（§2.3.3，默认 ≤1，正偏例外 ≤1.1）
  f_i        = Kelly 精裁决值（§2.3.1，半 Kelly + 截0）
  f_i^final  = 最终 Kelly 精裁决输出
```

**语义**：
- Kelly 是"风险预算上限"——f_i^final 不超过 Kelly 算出的 f_i（防止策略意愿过度下注）
- 粗仓位是"策略意愿"——f_i^final 不超过 w_i^sum × dist_adj（尊重策略选股，Kelly 不凭空加仓）
- 取两者较小者 = 在"策略意愿"和"风险预算"之间取保守平衡，符合分层裁定"只减不增为主"

#### 2.3.5 多标的 pro-rata 归一化

各标的 f_i^final 独立算，sum(f_i^final) 可能 > 总仓位上限（如 10 个标的各 0.1，sum=1.0）。为保留 Kelly 相对排序（高 edge 标的相对多配），在 Kelly 层做 pro-rata 归一化，而非纯靠硬上限裁剪：

```
若 sum(f_i^final) > 总仓位上限（regime Shrinkage 后，§2.4.3）：
    f_i^norm = f_i^final × (总仓位上限 / sum(f_i^final))     # 按比例缩放
否则：
    f_i^norm = f_i^final                                      # 不超限不缩放
```

**理由**（prevayo / eltonaguiar 2026 实践）：先算各 fractional Kelly，sum 超总暴露阈值则 pro-rata 缩放，保留 Kelly 相对排序信息。若纯靠 §2.4 硬上限按比例削，可能丢失 Kelly 排序。归一化在 Kelly 层做一次，硬上限裁剪作为最后兜底。

**注**：归一化只缩不放（f_i^norm ≤ f_i^final），不引入杠杆。

#### 2.3.6 CASH 豁免

CASH 不参与 Kelly 精裁决：
- CASH 的 σ≈0，K=(μ-r)/σ² → ∞，Kelly 公式无意义
- CASH 权重由现金管理约束（§2.5）直接定：firm_target_portfolio 中 `CASH = 1.0 − sum(股票权重)`，再叠加最低储备金 / 节假日等约束
- CASH 的 μ 取逆回购利率（= r），作为"无风险收益"基准，不进入 Kelly 算式

#### 2.3.7 Kelly 精裁决输出

MOD-POS-001 对求和后每个标的输出 `kelly_adjusted_weight`（= f_i^norm，经合成 + 归一化后的最终仓位建议），交 FirmRiskAggregator 做硬上限裁剪。

### 2.4 硬上限裁剪（FirmRiskAggregator / MOD-POS-021）

> 本节定**阈值与口径**（G12 范围）；裁剪的**执行算法**（按比例削的具体实现、冲突标的处理、O(N) 复杂度保证）归 G13。

#### 2.4.1 单票硬上限 8%（总资金口径）

- **口径**：8% 按**账户总资金**算（非策略 budget 口径）。例：100 万资金 → 单票最多 8 万
- **跨策略叠加**：多策略同标的仓位求和后 > 8%，按各策略贡献比例削到 8%
- **理由**：单票上限是组合级约束，必须跨策略叠加后管得住——这是分层裁定第一性原理（组合级约束天然在 firm 层）。若按策略 budget 口径，各策略各 8% 叠加可达 24%，管不住
- **新策略冷启动**：新策略仓位上限 = 正常 × 30%（防未验证即满仓），与 battle_map BM-POS-04 一致

#### 2.4.2 行业硬约束

| 约束 | 阈值 | 说明 |
|---|---|---|
| 单行业偏离基准 | ±10% | 常态 |
| 板块轮动叠加态激活时 | ±15% | 叠加态⑪激活放宽 |
| 单行业绝对上限 | 30% | 不可突破硬顶 |

- **口径**：按持仓权重按行业归类求和（只需持仓权重 + 行业映射，**不估协方差**）
- 来源：battle_map BM-POS-04（与 30_multi_strategy_concurrency §3.1 不估协方差一致）

#### 2.4.3 总仓位硬约束（regime Shrinkage 节流后）

总仓位上限由 regime Shrinkage 节流后给定（G15 RegimeMetaAllocator 定参数，firm 层执行裁剪）：

| 市场状态 | 总仓位上限 |
|---|---|
| ①平稳牛市 / ②动量牛市 | 80% |
| ③恐慌反弹 / ⑥压缩突破 | 60% |
| ④窄幅盘整 | 40% |
| ⑤宽幅震荡 | 50% |
| ⑦阴跌 | 30% |
| ⑧加速下跌 | 20% |
| ⑨恐慌崩盘 | 10% |
| ⑩事件驱动叠加态 | 基础 × 70% |
| ⑪板块轮动叠加态 | 基础（行业集中度放宽至 ±15%） |

- 来源：battle_map BM-POS-04 §20.3 仓位上限框架
- **边界**：仓位算法本身不读市场状态，只收到 regime Shrinkage 缩放后的 budget 数值上限（30_multi_strategy_concurrency §2.2"策略本身不知道市场态，只收到 budget 数字"）

### 2.5 现金管理（显式 CASH 标的）

**现金也是一种仓位**（30_multi_strategy_concurrency §2.4）。`firm_target_portfolio` 显式包含 `CASH` 虚拟标的，所有权重加和 = 1.0：

```python
firm_target_portfolio: dict[str, float]
# 例: {"600519": 0.08, "000858": 0.06, ..., "CASH": 0.25}
# sum(values) == 1.0
```

现金硬约束（与 battle_map BM-POS-06 一致）：

| 约束 | 值 | 说明 |
|---|---|---|
| 最低储备金 | 账户最低现金底线 | 任何仓位决策不可突破 |
| 机会储备 X% | 预留突发机会现金 | 配置项 |
| T+1 结算约束 | 当日卖出资金 T+1 才可用 | 仓位决策按 T+1 可用资金计算 |
| 节假日现金 | 节前 2 天 + 节后 1 天提高 5-15% | 规避节假日不确定性 |
| 闲置资金逆回购 | 闲置现金做逆回购生息 | 提升资金利用率 |

- **现金拖累可接受**（30_multi_strategy_concurrency §2.4）：budget 增加时策略不必立即满部署，现金拖累可接受
- **现金在仓位层直接表达**：最低储备金/节假日等约束直接作用在 `CASH` 权重上，无需另开机制

### 2.6 分层接口契约（数据结构汇总）

```
[StrategyBook × N]                 [FirmRiskAggregator]              [MOD-POS-001]              [FirmRiskAggregator]
   ↓                                   ↓                                ↓                          ↓
List[StrategyTarget]  ──→  按标的求和(自然叠加)  ──→  Kelly精裁决  ──→  硬上限裁剪  ──→  FirmTargetPortfolio
```

```python
@dataclass
class StrategyTarget:                      # 策略层输出（§2.2.4）
    strategy_id: str
    target_portfolio: dict[str, float]     # symbol -> 权重（相对策略 budget）
    budget_used: float                     # ≤ strategy_budget
    timestamp: datetime

@dataclass
class FirmTargetPortfolio:                 # firm 层最终输出
    holdings: dict[str, float]             # symbol -> 权重（含 "CASH"，和=1.0）
    kelly_adjustments: dict[str, float]    # symbol -> Kelly 调整记录（审计）
    clip_log: list[ClipRecord]             # 硬上限裁剪记录（审计）
    timestamp: datetime
```

**契约纪律**：
- 策略层不算 Kelly、不估密度 PDF（第一性原理：Kelly 需密度预测不宜每策略重复）
- firm 层求和用加法（自然叠加，O(N)），不用优化器
- Kelly 只在 firm 层 MOD-POS-001 做一次
- 输出 `holdings` 权重和严格 = 1.0（含 CASH）

### 2.7 边界声明（确认不做什么）

| 边界 | 内容 | 依据 |
|---|---|---|
| **Kelly 不在策略层重复** | 策略层只用等权/inverse-vol，禁 Kelly；Kelly 只在 firm 层 MOD-POS-001 做一次 | 30_multi_strategy_concurrency §2.1 第一性原理：Kelly 需密度预测不宜每策略重复 |
| **不做 MVO / 不估协方差** | firm 层只求和+Kelly+裁剪，不做 MVO，不估协方差矩阵 | 30_multi_strategy_concurrency §3.1：协方差估计是研究课题，放大噪声，归因纠缠 |
| **仓位算法不内置 regime 切换** | 仓位算法（等权/inverse-vol/Kelly）本身不随 regime 变；regime 只通过 Shrinkage 缩 budget 间接影响仓位上限 | 30_multi_strategy_concurrency §2.2：策略不知道市场态，只收到 budget 数字。system_charter §3 约束二"状态切换权重"的张力已由 30_multi_strategy_concurrency 移除 RegimeScore 裁定收敛（regime 不做 alpha 择时，只做风险节流） |
| **不做 G13/G14/G15 的事** | FirmRiskAggregator 求和/裁剪执行逻辑（G13）、BudgetChangeHandler 三级升级（G14）、RegimeMetaAllocator 参数（G15）不在本备忘 | 00_index_trading_decision 主题组分工 |

## 3. 考虑过的替代方案（拒绝理由）

### 3.1 全 MVO 统一优化器 —— 拒绝
- **拒绝理由**（30_multi_strategy_concurrency §3.1）：统一 MVO 需协方差矩阵（5000×5000），是研究课题不是工程任务；协方差估计在 A 股情绪周期切换时全错（冰点期相关性飙升到 0.8+）；优化器放大输入噪声；归因纠缠（亏钱时无法区分策略 alpha 错/优化器权重错/协方差估错）
- AI 能写对优化器代码，但写不出"准确的协方差矩阵"——那是数据+研究问题

### 3.2 策略层重复 Kelly —— 拒绝
- **拒绝理由**（30_multi_strategy_concurrency §2.1 第一性原理）：Kelly 需密度预测（估 μ/σ²），每策略都估一遍又累又错；密度 PDF 估计是重资源计算，不宜每策略重复
- Kelly 放 firm 层做一次，对所有策略求和后的标的统一精算

### 3.3 full risk parity（估协方差） —— 拒绝
- **拒绝理由**：full risk parity 需估协方差矩阵（N(N+1)/2 参数），N=5 策略需 60 月数据才 borderline 准确；与 30_multi_strategy_concurrency §3.1 拒绝协方差一致
- **采用 inverse-vol**（只估 σ，1 个参数）：2026 实证（quanthedgeai）确认 inverse-vol 几乎和等权一样鲁棒，12 月数据 ±10% 准确；Morwane 实证 inverse-vol risk parity OOS Sharpe +1.43

### 3.4 全 Kelly（不半 Kelly） —— 拒绝
- **拒绝理由**：full Kelly 回撤 50-80%（2026 多源实证），即便策略有正期望也可能在连亏中破产
- **采用半 Kelly（0.5×K）**：保 75% 增长、大幅降回撤；Thorp 本人用 0.25-0.5×；机构普遍 0.2-0.5×

### 3.5 与 Morwane 的差异说明
Morwane（30_multi_strategy_concurrency §7.4 核心实证）是 sleeve 信号 + **firm 层 inverse-vol risk parity**（sleeve 级）。本项目是**策略层 inverse-vol**（标的级）+ **firm 层 Kelly**（标的级）。分层思想一致，但 Kelly 放 firm 层是本项目选择——策略层已做 inverse-vol 粗分，firm 层需要基于密度 PDF 的"精裁决"（半 Kelly + 偏度/峰度/VaR 分布感知调整），risk parity 做不到分布感知。Morwane 印证的是"分层"思想，不是"具体在哪层用哪种算法"。

### 3.6 multivariate Kelly（估协方差）—— 拒绝且有实证印证
- **理论形式**：多标的 Kelly 最优解是 w=Σ⁻¹μ（Σ=协方差矩阵，μ=预期超额收益向量），即 mean-variance 解
- **拒绝理由**：需估协方差矩阵，与 30_multi_strategy_concurrency §3.1 拒绝协方差一致
- **实证印证**（Conformal Kelly arXiv:2608.01494 §6.4）：在硬上限（gross cap）约束下，multivariate Kelly w=Σ⁻¹μ 增长仅 0.023–0.179，**远差于** per-asset Kelly（不考虑协方差）。原因是"Markowitz 不稳定性 + 对冲掉权益溢价"。论文原话："under a binding gross cap only the direction survives"（有总仓位硬上限时，只有方向信息有用，协方差是理论上最大的洞但实证不起作用）
- **结论**：本项目 per-asset Kelly（K_i=(μ_i−r)/σ_i² 不考虑标的间相关）+ 硬上限裁剪的架构，不仅可行，且在硬上限约束下比理论上的 multivariate Kelly 更优。把"不做协方差"从"拒绝理由"升级为"有实证支持的更优选择"

## 4. 上限定义

### 4.1 参数上限汇总

| 参数 | 上限值 | 性质 |
|---|---|---|
| 单票仓位 | 8%（总资金口径） | 硬上限，按比例削 |
| 单行业绝对 | 30% | 硬上限 |
| 单行业偏离基准 | ±10%（叠加态 ±15%） | 硬约束 |
| 总仓位 | 80%（牛市）~ 10%（恐慌崩盘），regime Shrinkage 节流 | 硬上限 |
| Kelly 分数 | 0.5（半 Kelly） | 硬上限，禁全 Kelly |
| 新策略冷启动 | 正常 × 30% | 硬约束 |
| 正偏加仓幅度 | ≤ 原粗仓位求和值 10% | 硬上限（唯一允许加仓的例外） |
| 最低储备金 | 账户最低现金底线 | 硬约束 |
| Kelly 仓位下限 | f_i ≥ 0（禁做空） | 硬约束（A 股 T+1 不能做空） |

### 4.2 演进路径

| 阶段 | 内容 | 触发条件 |
|---|---|---|
| **MVP（当前）** | 静态差异化映射表；密度 PDF 未就绪时 Kelly 降级历史回测；硬上限裁剪就绪 | 本备忘定稿即可施工 |
| **阶段 2** | G04 产出首批 3 策略定义后，校准粗仓位映射表 | 20_first_batch_strategies 产出 |
| **阶段 3** | BM-SEL-13 密度 PDF 就绪，Kelly 主源切换 | BM-SEL-13 施工完成 |
| **阶段 4（待裁定）** | 评估 Conformal Kelly 替代/补充 σ 估计 | Conformal Kelly OOS 增长验证有效 |

### 4.3 为何这是上限而非妥协
- 策略层 inverse-vol + firm 层半 Kelly + 硬上限裁剪，是 2026 年主流实证共识（Morwane / quanthedgeai / crucible-backtester）
- 个人系统不需要机构级 MVO/协方差估计的复杂度——那是钱多/人多必须分散的产物（system_charter §3 约束五）
- 真正的上限 = 在分层裁定框架内把每个 StrategyBook 粗仓位 + firm 层 Kelly 精裁决做到极致，而不是在 firm 层堆优化器

## 5. 待裁定（暂缓项）

> 以下项目暂不施工，**非永久禁止**。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **Conformal Kelly** | 2026-08 arXiv 前沿研究，用 conformal prediction 区间宽度做 fractional Kelly 缩放，有有限样本覆盖率保证；但论文 lockbox OOS 增长失效（2022 后 8.5%/7.0% 低于被动基准），不成熟 | Conformal Kelly OOS 增长验证有效；其 drawdown dial（区间 downside miss 频繁→砍杠杆）可作为风控叠加，与 30_multi_strategy_concurrency §2.5 回撤 Protocol 互补 |
| **动态粗仓位算法选择** | MVP 用静态差异化映射表；动态（按策略滚动 Sharpe 自适应选算法）增加 meta 参数 | 各策略有 6+ 月实盘 track record |
| **Kelly 分数自适应** | MVP 固定半 Kelly（0.5×）；自适应 Kelly 分数（按估计置信度调整）增加复杂度 | 密度 PDF 主源稳定运行 6+ 月，置信度可量化 |
| **full risk parity** | 需估协方差，与 §3.1 拒绝协方差一致 | 协方差估计方案成熟（因子模型+shrinkage 验证有效），且 N 策略数显著增加 |
| **样本不足 Kelly 降级** | MVP 固定半 Kelly；样本 <50 trades 时 Kelly 估计误差大（completetradersedge 实证：±5% 胜率误差致 Kelly 变 3×），应进一步降级或忽略 Kelly 用固定比例 | 各策略有 50+ trades track record |

## 6. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 首批 3 策略确认（打板+多因子+事件驱动）→ 粗仓位映射表校准 | 30_multi_strategy_concurrency §6.1 / G04 | 待 G04（20_first_batch_strategies）产出 |
| BM-SEL-13 密度 PDF 就绪时间 → Kelly 参数主源切换 | 本备忘 §2.3.2 | 待 BM-SEL-13 施工 |
| convergence_window 按换手率定（打板 1-2 / 多因子 3-5 / 事件 2-3 天）→ 影响再平衡成本-收益 | 30_multi_strategy_concurrency §6.4 / G14 | 待首批策略定后校准 |
| Kelly 参数密度 PDF 降级触发条件细化 | 本备忘 §2.3.2 | 待 BM-SEL-13 接口契约明确后定 |

## 7. 引用

### 7.1 相关 design_memo
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)
  - §2.1 分层裁定（方案 A）——本备忘的框架来源
  - §2.2 三个核心模块（StrategyBook / FirmRiskAggregator / RegimeMetaAllocator）——regime 只缩 budget 不调仓位算法
  - §2.3 自然叠加——求和用加法替代优化器
  - §2.4 权重变动操作流程——现金也是一种仓位
  - §3.1 拒绝 MVO——不做协方差估计
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G12 仓位算法 spec / §5 轨道 B / §7.3 编号占用表
- [01_design_memo_management_spec.md](01_design_memo_management_spec.md) §4.3 推荐章节 / §5.2 引用纪律（用 path/blueprint_id 不用 node_id）

### 7.2 depgraph 模块（用 blueprint_id / path 引用）

| 模块 | blueprint_id | path | 本备忘角色 |
|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | 策略层粗仓位（§2.2） |
| position_sizing_engine | MOD-POS-001 | —（见 battle_map BM-POS-02 锚点） | firm 层 Kelly 精裁决（§2.3） |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | 硬上限裁剪执行（§2.4，参数定，执行归 G13） |

> MOD-POS-022（BudgetChangeHandler，三级升级）与 MOD-PA-007（RegimeMetaAllocator，Shrinkage 节流）属 G14/G15，本备忘只引用不展开。

### 7.3 相关 battle_map
- BM-POS-02 标级仓位 Kelly（MOD-POS-001）——半 Kelly 硬上限、分布感知调整的现有设计来源
- BM-POS-04 跨策略仓位硬限制（MOD-POS-010）——单票 8% / 行业 ±10% / 总仓位 9 态框架
- BM-POS-06 现金管理约束（MOD-POS-006）——最低储备金 / T+1 / 节假日 5-15%

### 7.4 开源实证参考
- **[Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book)** — inverse-vol risk parity OOS Sharpe +1.43；regime 风险节流 MaxDD −14.2%→−10.3%。印证分层思想（30_multi_strategy_concurrency §7.4 已引）
- **Conformal Kelly (arXiv:2608.01494v1, 2026-08-02)** — conformal prediction 区间做 fractional Kelly 缩放；反直觉发现"宽度稳定性 > 局部锐度"；OOS 增长失效。本备忘吸收"稳不要锐"原则（§2.3.2），Conformal Kelly 记为待裁定演进路径（§5）；其 §6.4 实测 per-asset Kelly 在硬上限约束下优于 multivariate Kelly（w=Σ⁻¹μ），印证本项目不做协方差的决策（§3.6）
- **quanthedgeai Strategy Allocation Methods (2026-06)** — "Theory says mean-variance. Practice says inverse volatility." 印证 inverse-vol 估 1 参数最鲁棒，强化策略层 inverse-vol 选择（§2.2 / §3.3）
- **crucible-backtester PR#559 (2026-07)** — fractional-Kelly = `kelly_fraction × μ / σ²` 工程实现，印证连续 Kelly 形式（§2.3.1）
- **2026 多源 fractional Kelly 共识**（momentumq / backtrex / journalplus）——机构 0.2-0.5× Kelly，half Kelly 保 75% 增长，强化半 Kelly 硬上限（§2.3.1 / §3.4）

### 7.5 system_charter 约束映射
- §3 约束四（策略三维度解耦）→ 强化分层裁定（仓位独立于选股）
- §3 约束五（少而精）→ 支持差异化粗仓位映射（§2.2.1）
- §3 约束二（统一框架派/状态切换）→ 与 regime 节流的张力已由 30_multi_strategy_concurrency §2.2 移除 RegimeScore 裁定收敛；本备忘边界声明仓位算法不内置 regime 切换（§2.7）

## 8. 交接清单（供兄弟主题组 AI 索引）

> 本节抽取 G12 仓位算法 spec 中供兄弟主题组（G13/G14/G15）直接消费的交接点，方便兄弟组 AI 不必通读全文即可定位所需输入。完整上下文见对应章节。
> 交接纪律（00_index_trading_decision §7.2）：AI 间不直接通信，通过产出物 + depgraph path 交接。兄弟组认领时读本节 + 对应章节即可开工。

### 8.1 给 G13 FirmRiskAggregator（产出 `32_firm_risk_aggregator`）的交接项

| 交接项 | G12 出处 | G13 需自行定义 |
|---|---|---|
| 单票硬上限 8%（总资金口径，按比例削） | §2.4.1 | 按比例削的具体执行算法 |
| 新策略冷启动 ×30% | §2.4.1 | 冷启动状态判定逻辑 |
| 行业硬约束（±10% / 叠加态 ±15% / 绝对 30%） | §2.4.2 | 行业归类求和的执行实现 |
| 总仓位 9 态上限（80%~10%） | §2.4.3 | 总仓位裁剪执行 |
| Kelly 精裁决输出 `kelly_adjusted_weight` | §2.3.4 | 作为裁剪输入接入求和后标的 |
| `FirmTargetPortfolio` 数据结构 | §2.6 | 生成过程实现 |
| 不做 MVO / 不估协方差 | §2.7 | O(N) 求和实现保证 |
| 冲突标的处理（一策略买、一策略卖同标的） | — | **G13 独有**，G12 不涉及 |

### 8.2 给 G14 BudgetChangeHandler（产出 `33_budget_change_handler`）的交接项

| 交接项 | G12 出处 | G14 需自行定义 |
|---|---|---|
| 总仓位硬上限触发 rebalance 条件 | §2.4.3 / §4.1 | 三级升级触发阈值与流程（Tier1 封锁/Tier2 信号/Tier3 强裁） |
| 单票/行业上限触发 rebalance | §2.4.1 / §2.4.2 | Tier 分级判定逻辑 |
| 现金约束（CASH 最低储备金 / 节假日 5-15%） | §2.5 | 现金不足时的降级处理 |
| 显式 CASH 数据结构（权重和=1.0） | §2.6 | rebalance 时 CASH 权重调整 |
| convergence_window 参考值 | §6（待定：打板 1-2 / 多因子 3-5 / 事件 2-3 天） | 窗口参数校准（**G14 独有**） |
| `rebalance_to_budget` 接口 | — | **G14 独有**（策略不能说"我不卖"），G12 不涉及 |

### 8.3 给 G15 RegimeMetaAllocator（产出 `34_regime_meta_allocator`）的交接项

| 交接项 | G12 出处 | G15 需自行定义 |
|---|---|---|
| 总仓位 9 态上限框架 | §2.4.3 | Shrinkage 缩 budget 后落到此表上限 |
| 仓位算法不内置 regime 切换（边界声明） | §2.7 | Shrinkage 输出的 budget 数字是仓位算法唯一 regime 输入 |
| 2 叠加态（事件驱动 ⑩ / 板块轮动 ⑪）总仓位规则 | §2.4.3 | 叠加态激活判定（G15 / regime 侧） |

> ⚠️ G15 依赖 11_regime_backtest_validation_plan C1 验证结果 + G04 策略 PnL，第二阶段上线（P3），当前不阻塞 G12/G13/G14。G15 定 Shrinkage 参数，G12 只消费其输出的 budget 数字。

### 8.4 G12 不做的事（避免兄弟组误判覆盖范围）

| 不做的事 | 归属 | 说明 |
|---|---|---|
| 求和 / 裁剪执行算法 | G13（MOD-POS-021） | G12 只定参数和口径，不定执行 |
| 三级升级机制 | G14（MOD-POS-022） | G12 只定上限触发条件，不定降级流程 |
| regime Shrinkage 参数 / 分配公式 | G15（MOD-PA-007） | G12 只消费 budget 数字，不估 regime |
| 选股 / 策略定义 | G04 / G05 | G12 只接收 `StrategyTarget`，不定选股 |
| `convergence_window` 校准 | G14 | G12 仅给参考值，校准归 G14 |
| 冲突标的处理 | G13 | G12 不涉及买卖冲突仲裁 |

---

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-08 | 1.0.0 | 初稿 | 落地 30_multi_strategy_concurrency §2.1 分层裁定框架为可施工 spec：策略层差异化粗仓位（等权/inverse-vol）+ firm 层连续 Kelly 精裁决（K=μ/σ²，半 Kelly，密度 PDF 主+历史降级）+ 硬上限裁剪（单票 8% 总资金口径/行业/总仓位/显式 CASH）；吸收 Conformal Kelly "稳不要锐"原则；记录 Conformal Kelly 为待裁定演进路径；与 system_charter §3 约束对齐确认边界 |
| 2026-08-08 | 1.1.0 | 新增 §8 交接清单 | 抽取 G12 供 G13/G14/G15 兄弟组直接消费的交接点，方便兄弟组 AI 不通读全文即可索引所需输入；修订记录顺延为 §9 |
| 2026-08-08 | 1.2.0 | 补全 Kelly 施工细节 | §2.3.1 公式补无风险利率 r（逆回购）+ f_i≥0 截断（不能做空）+ 量纲年化 + 交易成本扣 μ；§2.3 新增 Kelly 与粗仓位合成规则（§2.3.4）/ pro-rata 归一化（§2.3.5）/ CASH 豁免（§2.3.6）；§3 新增 per-asset Kelly 优于 multivariate Kelly 的实证印证（§3.6，Conformal Kelly §6.4）；§4.1 加 f_i≥0 上限；§5 加样本不足降级 |
| 2026-08-09 | 1.2.1 | 文件名 design_memo_004_position_sizing.md → 31_position_sizing.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 1.2.2 | §8 前向引用旧名（design_memo_005-007）更新为段位名（32_firm_risk_aggregator/33_budget_change_handler/34_regime_meta_allocator） | 文档体系重排补遗：前向引用未随 1.2.1 改名同步更新 |
| 2026-08-09 | 1.2.3 | §1 管理规范链接 `design_memo_management_spec.md`→`01_design_memo_management_spec.md` | 改名工程遗留断链修复（全量断链扫描发现） |
| 2026-08-09 | 1.2.4 | 文档头统一：frontmatter 补 title/owner/language，H1 去"设计备忘·"前缀与 title 对齐；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
