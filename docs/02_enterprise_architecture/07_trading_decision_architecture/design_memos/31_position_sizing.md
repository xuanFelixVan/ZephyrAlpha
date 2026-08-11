---
ttl: permanent
doc_type: architecture_view
title: 仓位算法（分层裁定落地）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.24.0"
date: 2026-08-12
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
- **σ_i 缺失/异常判定阈值（2026-08-10 施工流程补充）**：降级为等权（w_i = 1/N），不阻断。**异常判定算法**（任一触发即降级该标的为等权，非阻断整个策略）：
  1. **缺失检查**：σ_i = NaN / None / 0（方差非正）→ 降级
  2. **样本量门控**：60 日窗口内有效交易日 < 30（停牌/一字板致数据不足窗口 50%）→ 降级（与 §2.3.2 降级触发判定算法第 3 项样本量门控同源，completetradersedge 实证 ±5% 胜率误差致 Kelly 变 3×）
  3. **极端值检查**：σ_i 年化 > 150%（新股/次新股/事件冲击期极端波动，inverse-vol 估 1/σ 会被极端值主导失稳）→ 降级
  4. **新股冷启**：上市 < 60 个交易日（窗口填不满，σ_i 估计无统计意义）→ 降级
  降级后该标的在 inverse-vol 池中按等权 w_i = 1/N 参与分配，其余标的仍按 inverse-vol。**部分降级**（仅异常标的降级）保证不影响正常标的的风险均衡分配
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

#### 2.3.1 Kelly 公式（精确形式 + Merton 极限）

Kelly 有三种等价参数化形式，统一于**精确 Kelly** `f*=(μ-r)/((μ-r)+σ²/(1+(μ-r)))`（arXiv:2604.24723 Bloomberg 2026-04 严格推导）：

```
【精确形式】（二值 bet 的 μ/σ² 参数化，大 edge 自动饱和到 1）
f*_i = (μ_i - r) / ((μ_i - r) + σ_i² / (1 + (μ_i - r)))

【Merton 极限】（小 edge 近似，μ→0 时精确形式退化为连续 Kelly）
K_i = (μ_i - r) / σ_i²            # = f*_i 当 μ_i << σ_i²

【二值形式】（当前代码实现，BM-SEL-13 产出 p/b）
f*_i = (b_i × p_i - q_i) / b_i    # q_i = 1 - p_i

三者关系：精确形式是 Kelly 最优解的完整表达；Merton K=μ/σ² 是小 edge 极限；
         二值形式是精确形式的 (p,b) 参数化（μ=p(1+b)-1, σ²=p(1-p)(1+b)²）
```

**施工采用**：半 Kelly 硬上限 + f_i≥0 截断，作用于精确形式（或等价的二值形式）：

```
f_i = max(0, 0.5 × f*_i)     # 半 Kelly 硬上限 + 不能做空（f_i<0 截 0）

其中：
  μ_i  = 标的 i 的预期总收益（年化，来自密度 PDF 积分，已扣除预期交易成本）
  r    = 无风险利率（年化，取逆回购利率 GC001，与现金管理 §2.5 一致）
  σ_i² = 标的 i 的收益方差（年化，来自密度 PDF 积分）
  f_i  = Kelly 精裁决后的标级仓位建议（≥0，禁做空）
```

- **精确形式的优势（A股约束友好）**：当 μ_i→∞（大 edge），f*_i→1 自动饱和满仓，**不产生杠杆建议**；而 Merton K=μ/σ² 在大 edge 时 K>>1 需依赖硬上限裁剪。精确形式天然满足 A 股 f≤1（不能加杠杆）+ f≥0（不能做空）双约束，减少对裁剪层的依赖
- **Merton 极限的适用条件**：当 μ_i << σ_i²（薄 edge，如 μ=2%、σ=25% → μ/σ²=0.32），精确形式与 Merton 近似相等（误差 <5%）；A 股量化策略多为薄 edge，Merton 极限在多数场景够用，但精确形式在大 edge（如事件驱动 μ=15%）时更准确
- **半 Kelly（0.5×f*）是硬上限**：禁全 Kelly。行业共识（2026 多源实证）：full Kelly 回撤 50-80%；half Kelly 保 75% 增长、大幅降回撤；Thorp 本人用 0.25-0.5×；机构普遍 0.2-0.5×
- **⚠️ 胖尾场景下半 Kelly 的理论不稳定性（Taleb 论点，2026-08-10 审查补充，[convexly 2026-03](https://www.convexly.app/blog/kelly-criterion-explained)）**：Kelly 公式（无论二值/精确/Merton 形式）均隐含依赖**有限方差**假设。Taleb 在 *Statistical Consequences of Fat Tails*（2020 ch.10）严格论证：当收益分布尾部服从幂律且 **Hill 尾指数 α<2** 时，样本方差随样本增大而发散（不收敛），任何依赖方差的 sizing 规则（含半 Kelly）都在估计一个不存在的量。convexly 对 Polymarket 8656 钱包实证测得 α=1.28（95%CI 1.20-1.36），半 Kelly 继承该不稳定性，建议改用 **quarter-Kelly（0.25×f*）+ barbell**（投机腿总暴露封顶 10-20%，腿内每仓位 quarter-Kelly）。**对本项目的校准启示**：① A 股个股收益尾指数经验值 α≈2-4（中等厚尾，低于美股大盘但高于预测市场极端值），单票层面 α<2 风险主要存在于次新股/事件冲击期（已被 §2.2.2 σ_i 异常判定第 3/4 项降级覆盖）；② **本项目不把半 Kelly 降为 quarter-Kelly**——理由是设计本就不依赖半 Kelly 单层防护，而是叠加 §2.3.3 分布感知调整（VaR/CVaR 下调）+ §2.3.4 多约束取最小（sizing_basis 含 var_cap/cvar_cap/single_name_cap）+ §2.4 硬上限裁剪 + regime Shrinkage 四层独立兜底，在尾部场景下有效仓位已远低于半 Kelly 名义值（与 Taleb barbell 思路异曲同工：多层硬约束等效于"投机腿封顶+腿内 quarter-Kelly"）；③ **校准参数**：G04 首批策略 50+ trades 后，用 Hill 估计器测各策略 PnL 序列的 α，若 α<2 则将该策略 Kelly 倍数从 0.5× 收紧至 0.25×（或维持 0.5× 但收紧 §2.3.3 VaR/CVaR 阈值），与 §6 EVT-Based Tail Budgeting 候选同源（EVT GPD 拟合可同时产出 α 估计）。此论点为现有四层防御栈提供**理论背书**——保留多层硬约束而非简化为纯半 Kelly，正是 Taleb 胖尾批判所要求的风险架构
- **A 股 Kelly 实证校准**（浙商证券 2026-07-27，[筹码微观结构系列十三](http://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/838481485080/index.phtml)）：基于中证全指 2016.06-2026.06 十年日频回测，①**半 Kelly 优于全 Kelly**——半 Kelly 在 A 股高波动环境中风险收益比更优（与行业共识一致但 A 股实证背书）；②**短期窗口优于长期窗口**——10 日滚动窗口收益全面优于 30 日窗口（A 股趋势持续性弱、风格切换频繁，长窗口信息陈旧易产生滞后信号）；③**Kelly 更适合中长期仓位管理**——非短期投机择时工具。**对本项目校准**：当前 §2.3.2 降级源用 60 日历史均值/方差，A 股实证建议缩短至 10-30 日滚动窗口（BM-SEL-13 密度 PDF 未就绪时的降级参数校准）；BM-SEL-13 主源就绪后此约束弱化（密度 PDF 不依赖历史窗口长度）
- **不能做空约束（f_i≥0）**：A 股 T+1 不能做空，f_i<0（即 μ_i<r，预期收益低于无风险利率）时截断为 0（不持有），不做空。与 ryanoconnellfinance / xueqiu 实证"f*<0→不下注"一致
- **量纲统一年化**：μ_i、r、σ_i² 均用年化口径，保证 f_i 落在 0~1 量级（如 μ=12%、r=2%、σ=25% → 精确 f*=(0.10)/(0.10+0.0625/1.10)=0.638 → 半 Kelly f=0.319；Merton K=0.10/0.0625=1.6 → 半 Kelly f=0.8，精确形式更保守且不需额外裁剪）
- **交易成本从 μ 扣除**：μ_i 是扣预期交易成本（佣金+印花税+滑点+冲击，system_charter §3 约束一）后的净收益；薄 edge 扣成本后 f*_i≤0 → f_i=0，自动过滤劣质标的

> **⚠️ 实现现状与设计统一（2026-08-10 审查回填）**：当前已施工代码 [MOD-POS-001](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py) `_compute_kelly_fraction(p, b)` 实现的是**二值 Kelly** `f*=(bp-q)/b`（胜率 p + 盈亏比 b），与 [BM-POS-02](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_08_position_management.md) "从条件 PDF 积分计算胜率 p 和赔率 b" 一致。
>
> **三者统一**（arXiv:2604.24723 Bloomberg 2026-04 严格证明）：二值 `f*=(bp-q)/b`、精确 `f*=μ/(μ+σ²/(1+μ))`、Merton `K=μ/σ²` 是**同一 Kelly 最优解的三种参数化**，非不同算法：
> - 二值 ↔ 精确：μ=p(1+b)-1, σ²=p(1-p)(1+b)² 代入精确形式即得二值形式（代数等价）
> - 精确 → Merton：μ→0 时 σ²/(1+μ)→σ²，f*→μ/σ²（小 edge 极限）
>
> **结论**：代码实现的二值 Kelly **已经是精确 Kelly**（非近似），与设计目标的"连续 Kelly"不冲突——两者通过精确形式统一。Merton K=μ/σ² 是小 edge 近似，在薄 edge 场景下与二值/精确形式近似相等。**原 §5 "Kelly 形式统一"待裁定项已解决**，不再需要 BM-SEL-13 接口定型后统一——三者本就统一。半 Kelly 硬上限、f_i≥0 截断、分布感知调整对三种形式同样适用。

#### 2.3.2 Kelly 参数来源（密度 PDF 主 + 历史降级）

| 参数 | 主源 | 降级源 | 触发降级条件 |
|---|---|---|---|
| μ_i（预期总收益，扣成本后） | 密度 PDF 积分（BM-SEL-13） | 60 日历史均值收益 | BM-SEL-13 未就绪 / 输出异常 |
| r（无风险利率） | 逆回购利率 GC001（市场公开） | 固定 2.5% | 逆回购数据缺失 |
| σ_i²（方差） | 密度 PDF 积分（BM-SEL-13） | 60 日历史方差 | BM-SEL-13 未就绪 / 输出异常 |

- **主源用密度 PDF**：与 battle_map BM-POS-02 现有设计一致（"从条件 PDF 直接积分计算胜率 p 和赔率 b"），能捕捉未来分布的偏度/峰度/厚尾
- **降级用历史回测**：保证施工不被 BM-SEL-13 阻塞；历史回测在 regime 切换时滞后，但作为降级兜底可接受
- **降级触发判定算法（2026-08-10 施工流程补充）**：密度 PDF 输出异常的检测须在施工时实现以下检查链，任一触发即降级到历史回测源：
  1. **NaN/Inf 检查**：`μ_i` 或 `σ_i²` 为 NaN/Inf → 降级
  2. **分布合理性检查**：`σ_i² ≤ 0`（方差非正）或 `|μ_i| > 1.0`（年化收益超 100% 不合理）→ 降级
  3. **样本量门控**：BM-SEL-13 有效样本 < 30（completetradersedge 实证：±5% 胜率误差致 Kelly 变 3×，§5 样本不足降级）→ 降级
  4. **覆盖率检查**：密度 PDF 75% 区间覆盖率 < 60%（Conformal Kelly arXiv:2608.01494 标定 75% 目标，§2.3.2 "稳不要锐"原则）→ 降级
  降级后 `kelly_adjustments` 中标记 `param_source="historical_fallback"` 供归因审计区分"密度 PDF 估错"还是"历史回测滞后"
- **"稳不要锐"原则**（吸收自 Conformal Kelly arXiv 2026-08 发现）：密度 PDF 估计用 slow rolling，**宽度稳定性 > 局部 regime 自适应锐度**——越自适应的估计反而越差。BM-SEL-13 工程实现应避免过度追求 regime 局部锐度
- **⚠️ Conformal Kelly lockbox 样本外负结果**（[arXiv:2608.01494v1](https://arxiv.org/abs/2608.01494), 2026-08-02）：开发窗口（2016-2021）表现优异——28.5% 年化净 log 增长、Sharpe 1.34、MaxDD 27.7%（vs S&P 500 的 15.9%）；但**lockbox 样本外（2022+）增长未持仓**——两个预注册配置仅 8.5% 和 7.0% 年化，低于被动基准，pre-registered hindsight benchmark 在 raw growth 上击败它们但承担 46% drawdown。**关键警示**：calibration 持仓（0.745 vs 0.750 目标）≠ growth 持仓——区间校准正确不代表 sizing 盈利能力 OOS 持仓。论文同时报告一个**正面结果**：风险控制策略（当 conformal 区间在下行方向错过历史比率时削减杠杆）将 MaxDD 27.7%→20.3% 同时提升 Sharpe，rank-based p=1/41≈0.024。**对本项目启示**：① Conformal Kelly 作为 §5 待裁定远期候选，lockbox 负结果警示"开发窗口过拟合"风险——200 配置自主 LLM-agent 搜索可能过拟合开发窗口，本项目若引入须用独立 lockbox 样本验证；② "模型失效检测+自动降杠杆"思路（下行 miss → 削杠杆）可借鉴到本节降级触发判定——作为第 5 项补充：密度 PDF 连续 N 日下行 miss 超 historical rate → Kelly 降级（与 §2.3.2 四检查链互补，检测"参数渐变失效"而非"瞬时异常"）。**第 5 项施工参数（2026-08-10 施工流程补充）**：① **N = 20 交易日**（月级窗口，对齐浙商证券 A 股实证"10 日窗口优于 30 日"的短期窗口建议——月级是短期窗口的稳健上界，既能累积足够 miss 样本做统计判定，又不至于过长导致信号滞后）；② **historical rate = 滚动 60 日下行 miss 率的 95 分位数**（用 60 日历史 miss 率分布的 P95 作动态阈值，而非固定值——不同标的/不同 regime 的 baseline miss 率不同，动态阈值自适应）；③ **下行 miss 定义**：密度 PDF 预测的下行区间（如 75% conformal 区间下界）被实际收益突破（actual < lower_bound）；④ **降级动作**：触发后该标的 Kelly 分数 ×0.5（额外半 Kelly 削减），持续至连续 10 日 miss 率回落至 historical rate 以下恢复。此参数属 MVP 施工可调，G04 首批策略 50+ trades 后用实盘 miss 率分布校准 N 和分位数
- **A 股 Kelly 不做 regime 检测的本土负结果印证**（[中邮证券 2026-07-09](https://pdf.dfcfw.com/pdf/H3_AP202607091826846688_1.pdf)，LSTM-GHMM 混合方案）：中邮证券用 LSTM 自编码器（90 日×25 维→10 维）+ 高斯 HMM 5 状态做 A 股择时+动态仓位管理，2021 年以来 8 个主要指数均相对买入持有正超额。**关键失败案例**：对 2021 年（历史极低振幅高速轮动）和 2026 年（K 型极端分化）结构性行情适应性偏弱，超额损失高度集中于某一特定状态——归因发现**问题不在状态识别层，而在仓位执行层**：基于历史频度统计的 Kelly 公式在该状态下存在"均值回归"保守倾向，对"假摔反包"类行情响应不足。**对本项目启示**：① Kelly 层不应承担"识别假摔反包"职责——那是 sleeve alpha（[28号情绪周期](28_sentiment_cycle_trading.md)）的事，与本项目 [30号 §2.2](30_multi_strategy_concurrency.md) "情绪周期=sleeve 内 alpha 择时，regime=市场级风险节流，两者正交"的分工边界一致；② 项目 regime→Shrinkage 节流路径正确——避免了对 Kelly 做 regime-conditioned 检测（呼应 Conformal Kelly "稳定性优先"）；③ 中邮的失败正是"用 regime/Kelly 同时做择时+仓位"的混淆后果，印证本项目 Kelly 不内置 regime 切换（§2.7 边界声明）

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

> **⚠️ 实现现状（2026-08-10 审查回填）**：当前已施工代码 [MOD-POS-001](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py) 实现了 **VaR/CVaR 下调**（C4/C5，`var_reduce_factor=0.8` / `cvar_reduce_factor=0.7`）和**波动率检查**（C3，超 μ+2σ 仓位减半），但**偏度/峰度调整（C10）尚未实现**（代码 docstring 标注"阶段2: 分布感知(C10)"，当前属 P0 阶段外）。偏度/峰度调整依赖 BM-SEL-13 密度 PDF 的高阶矩输出，属 §4.2 阶段 3 目标。当前 MVP 用 VaR/CVaR 做尾部风险防御，已覆盖"只减不增"原则的核心场景。

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

> **Binding constraint 显式化（2026-08-10 审查补充，吸收 deadeye-rs 2026-06 `sizing_basis` 模式）**：合成公式 `f_i^final = min(w_i^sum × dist_adj_i, f_i)` 实质是**多约束取最小 + 命名 binding constraint**的简化形式。完整约束栈为：
>
> ```
> f_i^final = min(
>     w_i^sum × dist_adj_i,        # 策略意愿约束（粗仓位求和 × 分布调整）
>     f_i,                          # Kelly 风险预算约束（半 Kelly + 截0）
>     var_cap_i,                    # VaR_95 上限约束（§2.3.3，前瞻 VaR 超阈值时下调）
>     cvar_cap_i,                   # CVaR_95 上限约束（§2.3.3，比 VaR 更严）
>     single_name_cap_i,            # 单票硬上限约束（§2.4.1，8%/5% 三层口径）
>     liquidity_cap_i,              # 流动性硬上限约束（§2.4.4，ADV 口径，2026-08-10 补）
> )  且 f_i^final ≥ 0
>
> sizing_basis_i = 命名 binding constraint（"strategy_intent" / "kelly_budget" / "var_cap" / "cvar_cap" / "single_name_cap" / "liquidity_cap_moderate" / "liquidity_cap_severe"）
> ```
>
> - **多约束取最小**：6 个约束中取最小者，任一约束 binding 即限住仓位，符合"只减不增为主"
> - **`sizing_basis` 命名**：记录哪个约束是 binding（起作用的），供归因审计（deadeye-rs 2026-06 v0.1.17 实现 `sizing_basis: half-kelly / cvar-cap / budget`，本项目扩展为 7 值）。亏损复盘时可区分"是 Kelly 估错（kelly_budget binding）还是尾部风险超预期（cvar_cap binding）还是策略选股过激（strategy_intent binding）还是流动性不足（liquidity_cap binding）"
> - **当前代码现状**：[MOD-POS-001](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py) 实现 `min(w_i^sum, f_i)` + VaR/CVaR 下调因子（C4/C5），但未显式输出 `sizing_basis`。施工填充时应补 `sizing_basis` 字段到输出，提升归因可观测性（记入 §6 待定问题）

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
- **冷启动 ×30% 执行时机（2026-08-10 施工流程补充）**：30% 缩减在**策略层 budget 分配时即生效**——`strategy_budget_cold = strategy_budget × 0.3`，由 RegimeMetaAllocator（G15）或 StrategyBook 冷启动状态机设定。如此求和/Kelly/裁剪全链路基于已缩减值运行，归因清晰（冷启动策略贡献天然小）；若在 firm 聚合后裁剪时才乘 30%，则 Kelly 精算看到的是未缩减暴露，精算失真且归因需事后追溯缩减因子。冷启动状态由 StrategyBook 维护（`is_cold_start: bool` + `cold_start_until: date`），track record 达阈值（如 50 trades 或 3 月）后自动退出冷启动

> **⚠️ 8% vs 5% 分层口径澄清（2026-08-10 审查回填）**：本节 8% 是 **FirmRiskAggregator（MOD-POS-021）组合级聚合后**的单票上限——代码 `single_name_cap=0.08` 印证。但当前已施工的 MOD-POS-001 `default_single_position_cap=0.05`（5% NAV，策略层裁决默认）与 MOD-POS-010 不变量"单票 ≤ 5% NAV"（最终硬限执行器）更保守。分层关系：
> - MOD-POS-001 策略层裁决默认 5%（`default_single_position_cap`，可被 `RiskLimits.symbol_overrides` 覆盖）
> - MOD-POS-021 firm 聚合后 8%（`single_name_cap`，跨策略求和后的中间裁剪）
> - MOD-POS-010 最终硬限 5% NAV（`position_limit_enforcer`，5 级否决裁决的兜底）
>
> 因 8% > 5%，MOD-POS-010 的 5% 会在 MOD-POS-021 的 8% 之后再次裁剪，8% 实为冗余中间值。2026 行业基准（[algovestiq](https://www.algovestiq.com/learn/answers/how-to-size-stock-positions) 2026-05："hard cap of 8–10% per position and 20–25% per sector"）支持 8% 合理。**最终值待校准**：G04 首批策略产出后，统一 MOD-POS-001/010/021 三处单票口径（候选：全部对齐 8% 或全部对齐 5%），消除冗余裁剪。记入 §5 待裁定。

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
| ⑩危机（CRISIS，特殊态） | 5%（仅减仓不开新） |
| ⑪复苏（RECOVERY，特殊态） | 50%（逐步重建） |
| ⑫突破（BREAKOUT，特殊态） | 70%（趋势确立加仓） |
| overlay·事件驱动（bool flag） | 基础 × 70%（正交叠加，不占 enum） |
| overlay·板块轮动（bool flag） | 基础（行业集中度放宽至 ±15%，正交叠加） |

- 来源：battle_map BM-POS-04 §20.3 仓位上限框架 + [MOD-POS-001](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py) `MARKET_REGIME_CAPS`（12 态 enum immutable 映射）
- **⚠️ 编号澄清（2026-08-10 审查回填）**：代码 `SizingMarketRegime` enum 有 12 态（9 基础网格 ①-⑨ + 3 特殊态 ⑩CRISIS/⑪RECOVERY/⑫BREAKOUT），事件驱动/板块轮动是**正交 overlay**（`is_event_driven`/`is_sector_rotation` bool flag，不占 enum 槽位，代码注释明确"事件驱动/板块轮动为正交 overlay，由标志位表达，不占 enum"）。本表早期版本将 overlay 误编为 ⑩⑪ 与 enum 碰撞，现修正：⑩⑪⑫ 属 enum 特殊态，overlay 用 bool flag 标注
- **边界**：仓位算法本身不读市场状态，只收到 regime Shrinkage 缩放后的 budget 数值上限（30_multi_strategy_concurrency §2.2"策略本身不知道市场态，只收到 budget 数字"）

> **Regime Shrinkage ≈ Regime-aware Vol-Targeting（2026-08-10 审查补充）**：本项目总仓位上限由 regime Shrinkage 给定（G15 RegimeMetaAllocator 定参数），本质是 **regime-aware vol-targeting**——不同 regime 态对应不同目标波动率（①牛市 80% ≈ 高目标 vol、⑨恐慌崩盘 10% ≈ 低目标 vol）。2026 主流 vol-targeting 机制（[quant67](https://quant67.com/post/quant/17-position-sizing/17-position-sizing.html) 2026-05 / [fortraders](https://www.fortraders.com/blog/best-practices-volatility-adjusted-returns) 2026-05 / [pomegra](https://pomegra.io/wiki/volatility-targeting-portfolio-strategy/) 2026 / [blave](https://blave.org/blaveclaw/en/learn/vol_targeting) 2026）的公式 `L_t = σ*/σ_t`（目标 vol / 当前 vol）是连续版，本项目 regime Shrinkage 是离散版（按 regime 分档）。两者等价关系：
> - **vol-targeting**：连续测 σ_t → 连续调杠杆 L_t（如 fortraders VIX Regime 三档 <16/16-25/>25 → 1.0x/0.6-0.75x/0.3-0.5x）
> - **regime Shrinkage**：离散分 regime 态 → 离散调总仓位上限（①80%/⑨10%）
>
> **为何选 regime Shrinkage 而非纯 vol-targeting**：A 股 regime 切换是结构性的（情绪周期/政策驱动），纯 vol-targeting 在 regime 转折点（如冰点→反核）会滞后（vol 尚未飙升但风险已变）。regime Shrinkage 由 10_regime_detector_spec 的 HMM 提前识别 regime 转换，比 vol 反应快。但 vol-targeting 的"波动率聚集"特性（Mandelbrot：高 vol 后续高 vol）作为 regime 的补充信号，记入 G15 RegimeMetaAllocator 的 Shrinkage 参数校准（[34号](34_regime_meta_allocator.md)）。vol-targeting 不替代 regime Shrinkage，是其连续化补充
>
> **⚠️ 纯 vol-targeting 的系统性风险警示（2026-08-10 审查补充）**：Michael Burry 2026-08 警告（[insta-forex](https://www.insta-forex.com/in/forex_analysis/453380) 2026-08-05）——约 $5000 亿规模的 vol-targeting 基金构成**机械级联抛售风险**：S&P 500 仅需下跌 2.5% 即可触发这些基金从 77% → 50% 股权配置削减，形成"下跌→vol 上升→机械减仓→进一步下跌"的恶性循环（与 1987 Black Monday 的 portfolio insurance 机制同构）。**对本项目启示**：纯连续 vol-targeting（`L_t = σ*/σ_t`）在极端行情下会与全市场同类策略同步减仓，形成踩踏；本项目 regime Shrinkage 的**离散分档**（9 基础态 + 3 特殊态）+ HMM **提前识别**（vol 飙升前已切态）可部分规避此风险——regime 转换信号早于 vol 飙升，减仓时点分散于不同 regime 切换事件，非全部策略同步响应同一 vol 阈值。但须注意：若全市场 regime 检测器同质化（都用类似 HMM），同样会形成同步减仓。**缓释措施**：① Shrinkage 分档阈值差异化（与 34号 RegimeMetaAllocator 参数校准同步，避免整数阈值扎堆）② 减仓速度受限（33号 convergence_window 防抖，非瞬间机械减仓）③ 保留现金储备（§2.5 最低储备金 + 机会储备，下跌期有子弹抄底而非纯减仓）
>
> **⚠️ regime-conditional 重分配的换手率风险（2026-08-10 审查补充）**：[MDPI Economies](https://www.mdpi.com/2227-7099/14/7/268) 2026-07-09 实证（欧洲 10 资产 2000-2026 严格 walk-forward）：naive regime-conditional CVaR 分配产生**过高换手率 ~226%/年**，在任何现实交易成本下净表现**低于简单基准**；实现感知替代方案（regime-constrained weight bands，限制单次 rebalance 权重变动幅度）在 ~29% 换手率下恢复差距（net Sharpe 与静态基准差 0.009）。**核心发现**："瓶颈不是 regime 检测，而是透明、稳定、成本感知的决策规则设计"。**对本项目校准**：① 本项目 regime Shrinkage 的离散分档（非连续 CVaR 重分配）天然换手率更低——regime 切换是低频事件（月/季级），每次切换才调总仓位上限，非每日重分配；② 33号 BudgetChangeHandler 的 convergence_window + 防抖阈值是控制换手率的关键执行机制（防止 regime 在边界态抖动导致高频 rebalance）；③ 硬上限裁剪（§2.4）是"只减不增"的单向约束，非每日优化重分配，换手率天然可控；④ **待校准**：G04 首批策略产出后，实测 regime 切换频率 + rebalance 换手率，若换手率 >100%/年须评估 weight bands 限制（MDPI 实证的实现感知方案）
>
> **⚠️ 闭环比例控制 vol-targeting（BlackRock AI Lab 2026-03，2026-08-10 二十二次审查补充）**：[Devanathan/Rueter/Boyd/Candès/Hastie/Kochenderfer, BlackRock AI Lab + Index Services, arXiv:2603.01298](https://arxiv.org/abs/2603.01298) 2026-03-03 "Single-Asset Adaptive Leveraged Volatility Control" 提出**比例反馈控制（proportional control）替代开环 `L_t = σ*/σ_t`**——开环 vol-targeting 三大已知缺陷（turnover 尖峰 / leverage spikes / 对 σ 估计误差敏感），BlackRock 改用闭环反馈**显式修正跟踪误差**：
> - **跟踪误差**：`e_k = log(σ̂_k^ind / σ^tar)`（对数化的实现指数波动率 vs 目标波动率，已知 t_k 时可算）
> - **比例控制律**：`w_k = w_{k-1} - K_p · e_k`（K_p 比例增益，跟踪误差为正=实现 vol 高于目标→减仓；为负→加仓），闭环反馈天然平滑权重震荡、抑制 leverage spikes
> - **drawdown suppression 扩展**：在比例控制基础上叠加回撤抑制项（回撤加深时额外降杠杆），仿真显著降低最大回撤——与本项目 [35号回撤 Protocol](35_drawdown_protocol_impl.md) 的四级回撤控制**目标同构**（都是"回撤加深→减仓"），但 BlackRock 是连续反馈版，35号是离散分档版
> - **实证**：比例控制在**持续达成目标波动率**上优于开环方案；drawdown suppression 扩展进一步降回撤
>
> **对本项目的定位（远期候选，非 MVP 替代）**：
> - **范式差异**：本项目 regime Shrinkage 是**离散分档**（9+3 态 HMM → 离散调总仓位上限），BlackRock 比例控制是**连续闭环**（每期跟踪误差反馈调权）。两者非互斥——可视为 vol-targeting 的"粗粒度离散版"（本项目）vs "细粒度连续版"（BlackRock）的频谱两端
> - **为何 MVP 不切换到连续比例控制**：① regime Shrinkage 已由 30号§2.2 + 34号定稿，切换是替代范式非增量改进，成本高；② BlackRock 模型是**单资产**（risky + risk-free 两资产），本项目是多策略多标的组合，多资产推广需重新设计跟踪误差聚合口径（组合层 σ̂^ind 如何从各 sleeve 合成）；③ 连续闭环要求每期可观测 σ̂_k^ind 并 rebalance，与本项目 T+1 + convergence_window 防抖的低频再平衡哲学有张力——A 股 T+1 下连续反馈的边际收益受限
> - **可借鉴的洞察**：① **drawdown suppression 与 35号回撤 Protocol 的同构性**为 35号的离散分档提供连续版理论参照——若 G04 实盘后发现四级回撤分档"阶梯感"过强（regime 切换时仓位跳变过大），可评估引入比例控制的平滑项（在分档基础上叠加 `−K_p · e_k` 微调，而非纯离散跳变）；② **跟踪误差 e_k 作为监控维度**——即便不采用连续控制律，`e_k = log(σ̂^ind/σ^tar)` 可作为 [55号监控](55_monitoring_review.md) 的"实现 vs 目标 vol 偏离度"指标，regime Shrinkage 分档后实际组合 vol 偏离目标 vol 时告警（与 §2.4.3 vol-targeting 等价关系的定量化监测）；③ **缓释 Burry 级联风险的新视角**：§2.4.3 已登记 Burry 警告（开环 vol-targeting 机械级联抛售），BlackRock 闭环控制通过"跟踪误差反馈"部分缓释此风险——反馈机制使减仓速度受限（非瞬间机械减仓），与本项目 convergence_window 防抖思路一致。**记为 Phase 2+ 远期候选**：G04 实盘 regime Shrinkage 换手率/回撤数据积累后，若发现离散分档"阶梯跳变"问题，评估引入比例控制平滑项（非完全替代，而是离散分档 + 连续微调的混合范式）

#### 2.4.4 流动性硬上限（ADV 口径，2026-08-10 十九次审查补充）

> **施工算法缺失补全**：§2.4.1-2.4.3 定义了**资金口径**硬上限（单票 8%/行业 30%/总仓位 regime），但缺**流动性口径**硬上限——即仓位占标的日均成交额（ADV）的比例上限。对 A 股打板策略（§2.2.1 已注"容量极小，单票几万~几十万"）+ T+1（无法当日退出）+ 涨跌停板（流动性可瞬间归零），流动性口径上限是**比资金口径更先 binding 的约束**：一个 8% 资金仓位在低 ADV 标的上可能占 ADV 50%+，根本无法退出。

**流动性成本三组件**（[pomegra 2026](https://pomegra.io/learn/library/track-e-trading-risk/risk-management/chapter-04-position-sizing-methods/liquidity-adjusted-sizing) + [skill4agent 2026](https://www.skill4agent.com/en/skill/joellewis-finance_skills/bet-sizing) 行业框架）：
```
Spread Cost    = PositionSize × Spread% / 2                    # 买卖价差半程
Market Impact  = (PositionSize / ADV) × DailyVolatility × PositionSize  # 自身卖出推价反向
Execution Risk = MaxPositionLoss × P(gap)                       # 涨跌停/停牌致无法退出
TotalLiquidityCost = Spread + Impact + ExecutionRisk
```

**施工算法（ADV 口径硬上限，只减不增，作为 §2.4.1 单票 8% 之外的独立约束）**：
```python
# 输入：标级仓位建议 f_i^final（§2.3.7 Kelly 输出）+ ADV_i（20 日均成交额）+ 账户总资金
# 输出：流动性裁剪后仓位 + liquidity_cap binding constraint

ADV_PCT = (f_i^final × 账户总资金) / ADV_i    # 仓位占 ADV 的比例

# 三档流动性硬上限（A 股 T+1 + 涨跌停板适配，比 pomegra 标准 10-20% 更保守）
if ADV_PCT > 0.20:        # 仓位 > 20% ADV → 无法在 5 日内退出（T+1 下需 5+ 日清仓）
    f_i^liq = f_i^final × (0.20 / ADV_PCT)   # 削到 20% ADV
    sizing_basis_i = "liquidity_cap_severe"
elif ADV_PCT > 0.10:      # 仓位 > 10% ADV → 退出有显著冲击
    f_i^liq = f_i^final × 0.5                 # 削半（pomegra 规则：>10-20% ADV 减半）
    sizing_basis_i = "liquidity_cap_moderate"
else:
    f_i^liq = f_i^final                        # 流动性充足，不裁剪
```

**施工参数（A 股校准）**：
- **ADV 窗口**：20 个交易日（与 §2.2.2 inverse-vol 60 日窗口不同——流动性需更近期数据，60 日 ADV 会平滑掉近期流动性恶化；20 日对齐月度 rebalance 周期）
- **严重档阈值 20% ADV**：比 pomegra/skill4agent 国际标准 10-25% 取下限——A 股 T+1（不能当日退出）+ 涨跌停板（流动性可瞬间归零）+ 打板标的本就低 ADV，需更保守
- **削半档阈值 10% ADV**：触发后仓位减半，与 §2.3.4 binding constraint 栈并列（sizing_basis 增加 "liquidity_cap_moderate" / "liquidity_cap_severe" 两值）
- **降级路径**：ADV_i 缺失/停牌致成交额=0 → 该标的降级为 §2.2.2 σ_i 异常判定同源处理（降级为等权池中按 1/N 参与但叠加 ADV 严重档约束，即 f_i^liq = min(f_i^final, 0.20 × ADV_median / 账户总资金)，ADV_median 取同行业近期中位数）

**最坏情况流动性 sizing 原则**（pomegra 2026 核心洞察）：流动性压力在市场崩溃时飙升（价差扩大+成交萎缩），须按**危机期 ADV 而非常态 ADV** sizing。本项目实现：ADV_i 取 20 日均值的 **P25（下四分位）** 而非均值，天然偏向最坏情况（与 §2.4.3 Burry vol-targeting 级联警示协同——崩溃期流动性枯竭是同步减仓踩踏的微观机制）

**与 §2.2.1 打板等权的协同**：§2.2.1 打板用等权因"标的少+容量小+60 日波动率噪声大"。本节 ADV 上限是等权之上的**流动性兜底**——等权定了粗仓位比例，ADV 上限确保该比例在低流动性标的上不超可退出规模。两者叠加：`f_i^打板 = min(等权 1/N, 0.20 × ADV_i^P25 / 账户总资金)`

**盘后固定价格交易缓解路径（2026-08-10 二十次审查补充，[A 股新规 2026-07-06](https://finance.sina.com.cn/wm/2026-07-06/doc-inifwsct1833700.shtml)）**：2026-07-06 施行的 A 股交易新规将**盘后固定价格交易扩展至全市场所有 A 股**（此前仅科创板/创业板），以当日收盘价撮合成交。这对 §2.4.4 流动性上限违反提供了**低冲击退出路径**——当仓位 > 20% ADV 须削减时，盘后固定价格交易以收盘价一次性成交，避免盘中卖出对自身价格的冲击（Market Impact 组件最小化）。**施工衔接**：33号 BudgetChangeHandler Tier 3 强裁已实现盘后固定价格交易 fallback（[33号 §3.4 伪代码](33_budget_change_handler.md) `_use_after_hours_fixed_price_fallback`），本节流动性上限触发时复用该路径——sizing_basis 标记 `liquidity_cap_severe` 后，执行层优先走盘后固定价格交易而非盘中 TWAP 拆单。**注意**：盘后固定价格交易流动性有限（全市场机构竞争收盘价），不可作为常规退出路径，仅作为流动性上限违反的**应急 fallback**

**过度工程审查**：ADV 口径硬上限是单标级 O(1) 查表+比较，非优化器/协方差估计，与 §2.6 拒绝 MVO 一致。三档阈值+削半/削到上限两动作，施工简单。**MVP 必做**（非远期）——打板策略标的低 ADV 是 A 股实盘生存级风险，无此约束会在低流动性标的上被锁死无法退出。记入 §2.3.4 binding constraint 栈第 6 项 `liquidity_cap`

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
- **资金利用率 70-90% 是特性非缺陷**（2026-08-10 审查补充，quanthedgeai 2026-05 实证）：[quanthedgeai](https://www.quanthedgeai.com/blog/building-a-robust-composite-score-2/) 2026-05-26 明确"Capital utilization below 100% is a feature. Most portfolios should run at 70 to 90%"——满仓运行意味着无缓冲应对回撤/机会/保证金追加。本项目总仓位上限 80%（牛市）~10%（恐慌崩盘），常态运行在 50-80% 区间（regime Shrinkage 后），天然符合 70-90% 指引。**与 §2.4.3 Michael Burry vol-targeting 级联警示协同**：保留现金储备是缓释"全市场同步减仓踩踏"的第三道防线（前两道：regime 离散分档 + convergence_window 防抖），下跌期有子弹抄底而非纯减仓
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

# FirmTargetPortfolio 权威定义见 [32号 §2.7](32_firm_risk_aggregator.md)（v1.23.0 同步：
# 原 31号 4 字段 holdings/kelly_adjustments/clip_log/timestamp 为 v1.0.0 遗留简化版，
# 32号 v1.0.x 演进后补 constraint_checks/conflicts_resolved/degraded/contributions/
# idempotency_key/schema_version 等字段，31号 旧定义已过时致跨文档数据结构漂移）
@dataclass(frozen=True)
class FirmTarget:                          # 32号 §2.7 子结构
    target_weight: float                   # 裁剪后最终权重
    contributions: dict[str, float]        # {strategy_id: 贡献权重}（归因用）
    cut_ratio: float                       # 被裁剪比例（0=未裁剪，0.2=削了20%）

@dataclass(frozen=True)
class FirmTargetPortfolio:                 # firm 层最终输出（权威定义：32号 §2.7）
    firm_positions: dict[str, FirmTarget]  # symbol → FirmTarget（含 CASH）
    total_exposure: float                  # 所有标的 target_weight 之和
    total_budget: float                    # 所有策略 budget 之和
    cash_ratio: float                      # = total_budget − total_exposure
    constraint_checks: dict[str, Any]      # 单票/行业/总仓位/流动性检查结果（含是否触发裁剪）
    conflicts_resolved: list[ConflictRecord]  # 冲突标的净额处理记录
    degraded: bool                         # 降级标记（含 Kelly 参数降级 historical_fallback）
    created_at: datetime
    idempotency_key: str
    schema_version: str = "1.0"
```

> **v1.23.0 字段映射说明**（旧 4 字段 → 新 10 字段）：
> - 旧 `holdings: dict[str, float]` → 新 `firm_positions: dict[str, FirmTarget]`（FirmTarget 含 target_weight + contributions + cut_ratio，比裸 float 更丰富，支撑归因审计）
> - 旧 `kelly_adjustments: dict[str, float]` → 新 `degraded: bool` + `constraint_checks`（Kelly 降级 `param_source="historical_fallback"` 由 post_kelly_clip 的 `kelly_param_source` 参数传入，触发 `degraded=True`，见 [32号 §2.1 post_kelly_clip](32_firm_risk_aggregator.md)）
> - 旧 `clip_log: list[ClipRecord]` → 新 `constraint_checks` 各级裁剪 cuts 记录 + `FirmTarget.cut_ratio`（每标的裁剪比例）
> - 旧 `timestamp` → 新 `created_at` + `idempotency_key` + `schema_version`（幂等性 + 版本控制）

**契约纪律**：
- 策略层不算 Kelly、不估密度 PDF（第一性原理：Kelly 需密度预测不宜每策略重复）
- firm 层求和用加法（自然叠加，O(N)），不用优化器
- Kelly 只在 firm 层 MOD-POS-001 做一次
- 输出 `firm_positions` 权重和 + `cash_ratio` = `total_budget`（含 CASH，见 [32号 §2.7](32_firm_risk_aggregator.md)）

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
- **采用半 Kelly（0.5×f*）**：保 75% 增长、大幅降回撤；Thorp 本人用 0.25-0.5×；机构普遍 0.2-0.5×
- **理论支撑**：有限时域分位数优化（Quantile Optimization）的最优策略当时域→∞时渐近收敛于 Kelly 策略（CSDN 2026-06 综述严格数学证明）——即 Kelly 是所有有限时域风险控制策略的长期极限。这说明 Kelly 方向正确（长期最优），但有限时域内需 fractional Kelly 控制尾部风险，half Kelly 是 return/variance trade-off 的行业最优点

### 3.5 与 Morwane 的差异说明
Morwane（30_multi_strategy_concurrency §7.4 核心实证）是 sleeve 信号 + **firm 层 inverse-vol risk parity**（sleeve 级）。本项目是**策略层 inverse-vol**（标的级）+ **firm 层 Kelly**（标的级）。分层思想一致，但 Kelly 放 firm 层是本项目选择——策略层已做 inverse-vol 粗分，firm 层需要基于密度 PDF 的"精裁决"（半 Kelly + 偏度/峰度/VaR 分布感知调整），risk parity 做不到分布感知。Morwane 印证的是"分层"思想，不是"具体在哪层用哪种算法"。

### 3.6 multivariate Kelly（估协方差）—— 拒绝且有实证印证
- **理论形式**：多标的 Kelly 最优解是 w=Σ⁻¹μ（Σ=协方差矩阵，μ=预期超额收益向量），即 mean-variance 解
- **拒绝理由**：需估协方差矩阵，与 30_multi_strategy_concurrency §3.1 拒绝协方差一致
- **实证印证**（Conformal Kelly arXiv:2608.01494 §6.4）：在硬上限（gross cap）约束下，multivariate Kelly w=Σ⁻¹μ 增长仅 0.023–0.179，**远差于** per-asset Kelly（不考虑协方差）。原因是"Markowitz 不稳定性 + 对冲掉权益溢价"。论文原话："under a binding gross cap only the direction survives"（有总仓位硬上限时，只有方向信息有用，协方差是理论上最大的洞但实证不起作用）
- **结论**：本项目 per-asset Kelly（K_i=(μ_i−r)/σ_i² 不考虑标的间相关）+ 硬上限裁剪的架构，不仅可行，且在硬上限约束下比理论上的 multivariate Kelly 更优。把"不做协方差"从"拒绝理由"升级为"有实证支持的更优选择"

### 3.7 Hierarchical Risk Parity（HRP，层次风险平价）—— 评估后拒绝，记为远期候选

- **算法**（López de Prado 2016，2026 主流 [foliolab](https://www.foliolab.ai/docs/guide/methods/hrp) / [marketmaker.cc](https://marketmaker.cc/en/blog/post/portfolio-optimization-algorithms-compared/) / [pfolio](https://www.pfolio.io/academy/hierarchical-risk-parity) / [metricgate](https://metricgate.com/docs/hierarchical-risk-parity/) / [stockalpha](https://stockalpha.ai/alpha-learning/hierarchical-risk-parity-clustering-based-allocation-that-survives-estimation-er)）：三步——① 树聚类（相关性距离 `d_ij=√(0.5(1-ρ_ij))` + 层次聚类 → dendrogram）；② 准对角化（按 dendrogram 重排协方差矩阵）；③ 递归二分（按子簇方差反比分配权重）。**核心优势：不需协方差矩阵求逆**，比 MVO 鲁棒，OOS 表现优于 MVO 和等权
- **评估**：HRP 解决了 MVO 的"协方差求逆不稳定"问题，但**仍需相关性矩阵**（N(N-1)/2 个 ρ_ij 估计），属协方差范畴。本项目分层裁定已分工：
  - 策略层用 inverse-vol（只估 σ_i，1 个参数，§2.2.2）——比 HRP 更简单更鲁棒
  - firm 层用 Kelly（分布感知 μ/σ²，§2.3）——比 HRP 的纯风险均衡多了收益维度
  - HRP 在"策略层 inverse-vol"和"firm 层 Kelly"之间**无位置**——它既非纯 σ 估计（需 ρ），又非分布感知（标准 HRP μ=1 仅最小方差）。**⚠️ 2026-04 更新**：[Wuebben 2026-04 arXiv:2604.23833](https://arxiv.org/abs/2604.23833) 提出 **HRP-μ / HRP-Σμ / CRISP** 三变体，将 HRP 扩展为**信号感知**（incorporates μ）——HRP-μ 在同一相关性 dendrogram 上用 signed inverse-variance 作代表组合，2×2 mean-variance 解 between-branch budget split，γ∈[0,1] 控制跨簇协方差纳入；**当 γ=0 且 μ=1 时精确退化为 De Prado 标准 HRP**（Proposition 4.2），并提供对冲感知（正相关资产反向信号利用，Proposition 4.4）；计算 O(N²) 与标准 HRP 同阶。此更新**修正"HRP 无 μ"判断**：HRP-μ 解决了信号盲限制，但**不改变核心拒绝理由**（仍需相关性矩阵 ρ_ij + A 股 regime 转折点聚类不稳定 + 小规模聚类优势不显著）
- **拒绝理由**：HRP 需相关性矩阵，与 30_multi_strategy_concurrency §3.1 拒绝协方差不完全一致（HRP 不求逆但需 ρ），但 A 股情绪周期切换时相关性飙升（冰点期 ρ→0.8+），HRP 的聚类结构在 regime 转折点不稳定。且 N=3-5 策略 × 10-20 标的的小规模组合，HRP 的聚类优势不显著（聚类需 N 较大才体现层次结构）
- **与 32号 correlation clustering 的区别**：32号 §5 待裁定"相关性聚类"是 tierzero 2026-01 的简化版（pairwise ρ>0.6 → 同 cluster → cluster cap），只需二元判定不需完整聚类树，比 HRP 轻得多。HRP 是完整聚类+递归二分，复杂度更高
- **远期候选条件**：若 ① 策略数显著增加（>8）且 ② 标的数显著增加（>50）且 ③ 相关性估计方案成熟（因子模型+shrinkage），可评估 **HRP-μ**（信号感知版，非标准 HRP）替代策略层 inverse-vol。当前 MVP 不做

### 3.8 Bayesian Kelly with Parameter Uncertainty —— 评估后记为 Phase 2 候选

- **算法**（Sukhov 2026-06，[sergeisukhovmkt/Bayesian-Kelly-Criterion-with-Parameter-Uncertainty](https://github.com/sergeisukhovmkt/Bayesian-Kelly-Criterion-with-Parameter-Uncertainty)）：用 Beta 共轭先验的后验正则化替代 plug-in Kelly 分数。核心公式（Eq. 13）：

  ```
  f*_bayes = (p̄ − (1−p̄)/b) · n_eff / (n_eff + κ)

  其中：
    p̄ = α/(α+β)   # Beta 共轭先验的后验均值（α/β 为先验+观测更新的超参）
    n_eff = α+β    # 有效样本量
    κ              # 正则化强度（prior strength）
  ```

  当 `n_eff >> κ`（样本充足）→ `f*_bayes → plug-in Kelly`（不收缩）；当 `n_eff → 0`（样本少）→ `f*_bayes → 0`（自动收缩到不赌）

- **与固定半 Kelly / Empirical Kelly UQ 的三方对比**：

  | 方法 | 调整对象 | 公式 | 哲学 | 计算成本 |
  |---|---|---|---|---|
  | **固定半 Kelly（当前 MVP）** | 分数（固定） | `f = 0.5 × f*` | 隐含"edge 估计误差固定 50%"，不随样本量变化 | O(1) |
  | **Empirical Kelly with UQ（§5 待裁定）** | 分数（MC 动态） | `f = f_kelly × (1 − CV_edge)` | 频率派，MC 模拟 edge 估计的变异系数 | O(MC 模拟) |
  | **Bayesian Kelly（本节）** | 分数（闭式动态） | `f = f*_bayes × n_eff/(n_eff+κ)` | 贝叶斯派，Beta 后验有效样本量做收缩 | O(1) 闭式 |
  | **Conformal Kelly（§5 待裁定）** | σ 估计（区间宽度） | `f ∝ 1/区间宽度` | 用 conformal prediction 区间宽度调 σ | O(rolling quantile) |

  Bayesian Kelly 的优势是**闭式解**（不需 MC 模拟，计算轻），且收缩因子 `n_eff/(n_eff+κ)` 有明确贝叶斯解释——"有效样本量不足时自动不信估计"

- **κ 推荐值与施工参数（2026-08-10 施工流程补充，Sukhov 2026-06 Monte Carlo 校准）**：Sukhov 按 trading frequency 给出 κ 推荐值——HFT κ=10（10 笔达半 Kelly）、**swing trading κ=30**（30 笔达半 Kelly，本项目打板/事件驱动/多因子均为日频 swing 级，取 κ=30）、position trading κ=50。本项目各策略属 swing 级，**施工采用 κ=30**——含义：有效样本量 n_eff=30 时 f*_bayes 收缩到 plug-in Kelly 的 50%（等价半 Kelly），n_eff=60 时收缩到 67%，n_eff→∞ 收缩到 100%（趋近 full Kelly）。**额外约束**：Sukhov 建议 correlated portfolio（多策略共享因子/同市场）设 `f_max=0.15`（单标的 Kelly 上限 15%）——本项目多策略同 A 股市场天然相关，施工应叠加上限 `f*_bayes = min(f*_bayes, 0.15)`，与 §2.4.1 单票 8% 硬上限（更严）叠加取最小。**与固定半 Kelly 的等价关系**：n_eff=κ=30 时 `f*_bayes = plug-in × 30/(30+30) = 0.5 × plug-in` = 半 Kelly——即 Bayesian Kelly 在样本量=κ 时精确等价半 Kelly，样本更多时自动放宽（比固定半 Kelly 更 adaptive），样本更少时自动收紧（no data→no bet）。**Monte Carlo 实证**（Sukhov p=0.55, n=50, 10000 路径）：Bayesian Kelly 2.47× 增长 9.1% MaxDD 24.6% Sharpe 0.89 破产率 0.8%，优于 Half Kelly 2.21× 增长 7.9% MaxDD 31.2% Sharpe 0.72 破产率 4.2%——捕获 Full Kelly 87% 增长 + 回撤减 60% + 破产风险降 96%

- **评估**：Bayesian Kelly 是固定半 Kelly 的自然演进——不引入协方差/优化器，仍属 per-asset Kelly（§3.6 不做协方差不受影响），只在 Kelly 分数计算层做贝叶斯收缩。与 Conformal Kelly（调 σ）和 Empirical Kelly UQ（调分数）三方互补但不互斥——可组合（如 Bayesian 收缩 + Conformal 区间宽度双调），但 MVP 不做组合

- **记为 Phase 2 候选**：当前 MVP 固定半 Kelly（0.5×）已够（§2.3.1）。Bayesian Kelly / Empirical Kelly UQ / Conformal Kelly 三者均待各策略 50+ trades track record 后评估择优。三者处理参数不确定性的角度不同（贝叶斯收缩 / MC 不确定性 / conformal 区间），择优标准是 OOS 增长 + 回撤 + 计算成本的综合 trade-off

### 3.9 Tepelyan 多元 Kelly sigmoid 标度律 —— 评估后记为 Phase 3 远期候选

> **v1.17.0 新增**：§3.6 拒绝了 multivariate Kelly（需估 N×N 协方差矩阵，O(2^N) 复杂度），§3.8 Bayesian Kelly 是 per-asset Kelly 的参数不确定性增强。本节登记 Tepelyan 2026-04 多元 Kelly 的**积分变换方法**——将 O(2^N) 降至 O(N)，并发现 sigmoidal 标度律，为"多元 Kelly 不可计算"的拒绝理由提供远期突破路径。

- **算法**（[Tepelyan 2026-04](https://arxiv.org/abs/2604.11550)，"Multivariate Kelly Criterion: Sigmoidal Scaling Law via Integral Transform"）：用积分变换方法求解多元 Kelly 优化问题 `max_f E[log(1 + f^T r)]`，核心贡献：
  1. **O(2^N) → O(N) 降维**：标准多元 Kelly 需枚举 2^N 种联合结果（N 标的的二叉树），Tepelyan 用 Fourier/Laplace 积分变换将离散求和转化为连续积分，解析降维到 O(N) per-asset 计算 + O(N²) 交叉项修正
  2. **sigmoidal 标度律**：实证发现多元 Kelly 最优分数 `f*_i` 随交叉相关性 `ρ_ij` 的变化遵循 sigmoid 函数 `f*_i = f*_i^{independent} × σ(ρ)`（σ 为 sigmoid），即：低相关时多元 ≈ 独立 Kelly（`σ(ρ)→1`），高相关时多元 Kelly 大幅缩减（`σ(ρ)→0.5`，接近半 Kelly），过渡区呈 S 形
  3. **闭式近似**：给出 sigmoid 标度律的闭式参数化近似 `σ(ρ) = 1/(1 + exp(α × (ρ - ρ_0)))`，参数 α/ρ_0 由收益分布矩确定，无需数值优化

- **与 §3.6 multivariate Kelly 拒绝理由的关系**：
  | 维度 | §3.6 拒绝的 multivariate Kelly | Tepelyan 积分变换法 |
  |---|---|---|
  | 复杂度 | O(2^N) 枚举联合结果 | O(N) + O(N²) 交叉项 |
  | 协方差需求 | 完整 N×N Σ 矩阵 | 仅需 pairwise ρ_ij（与 §3.7 HRP 同输入） |
  | 计算方式 | 数值优化（非线性规划） | 闭式 sigmoid 近似 |
  | 可解释性 | 黑箱优化器输出 | sigmoid 标度律有物理含义（低相关≈独立/高相关≈半 Kelly） |

  §3.6 拒绝的三理由（① 需估协方差 ② O(2^N) 复杂度 ③ A 股 regime 转折点聚类不稳定）中，Tepelyan 直接解决②（O(N) 降维），部分缓解①（仅需 pairwise ρ 而非完整 Σ），但③仍成立——A 股 regime 转折时 pairwise ρ 仍不稳定。

- **与 §3.8 Bayesian Kelly 的关系**：Bayesian Kelly 是 per-asset Kelly 的**参数不确定性收缩**（单标的维度），Tepelyan 是 multivariate Kelly 的**计算复杂度突破**（标的间维度）。两者正交——Bayesian Kelly 管"单个 edge 估计准不准"，Tepelyan 管"多个 edge 之间相关性怎么折算"。理论上可组合（Bayesian 收缩 per-asset edge + Tepelyan sigmoid 折算交叉相关），但 MVP 不做组合。

- **与 §2.3.4 合成规则的关系**：当前 §2.3.4 用 binding constraint（5 约束取最小）做 per-asset Kelly 的硬裁剪，不估协方差。Tepelyan 的 sigmoid 标度律提供"轻量相关性折算"的远期路径——用 pairwise ρ 做 sigmoid 缩减替代完整 multivariate Kelly 优化，复杂度从 O(2^N) 降到 O(N²)，且闭式可解释。但 MVP 用 binding constraint 已足够保守（硬上限取最小天然覆盖高相关场景的缩减需求）。

- **优势**：① **O(N) 突破**——解决 multivariate Kelly 的计算不可行性核心障碍；② **sigmoid 标度律**——有物理含义的参数化近似，低相关≈独立 Kelly / 高相关≈半 Kelly，过渡区 S 形，比黑箱优化器可解释；③ **仅需 pairwise ρ**——与 §3.7 HRP 同输入，不需求完整 Σ 矩阵；④ **闭式**——无需数值优化，O(N²) 一次性计算

- **评估**：Tepelyan 是 multivariate Kelly 的**计算突破**而非 per-asset Kelly 的替代——§3.6 拒绝 multivariate Kelly 的核心理由③（A 股 regime 转折时 ρ 不稳定）仍成立，Tepelyan 的 sigmoid 近似在 ρ 不稳定时仍有参数噪声。但 O(N) 突破 + sigmoid 标度律使 multivariate Kelly 从"不可计算"变为"可计算但需校准"，是远期升级路径。与 §3.8 Bayesian Kelly 正交（per-asset 不确定性 vs 交叉相关折算），理论上可组合但 MVP 不做。

- **记为 Phase 3 远期候选**：当前 MVP per-asset Kelly（§2.3.1 精确公式 + 半 Kelly + §2.3.4 binding constraint 硬裁剪）已够。Tepelyan 的价值在"策略数扩展到 8+ 且 pairwise ρ 校准稳定后"——届时 sigmoid 标度律可作为 §2.3.4 binding constraint 的**连续替代**（硬上限取最小 → sigmoid 连续缩减），提供更平滑的仓位曲线。重评条件：① 策略数 ≥8；② §3.7 HRP 评估时同步校准 pairwise ρ 稳定性；③ 实盘 ≥1 年后 ρ 估计窗口稳定性验证通过。

### 3.10 Multi-period mean-DCVaR optimization via RNN —— 评估后记为 Phase 4 远期候选

- **来源**：[Lelong, Maume-Deschamps, Thevenot arXiv:2604.14439](https://arxiv.org/abs/2604.14439) 2026-04-17（SCOR 再保险数学团队）"Multi-period mean-Deviation CVaR optimization using Recurrent Neural Networks"
- **算法**：离散时间多期组合优化，约束为 **Deviation CVaR（DCVaR）**——CVaR 超过期望终财富的部分（`DCVaR = CVaR - E[W_T]`），而非 CVaR 本身。用 **RNN 近似最优预承诺策略（pre-commitment strategy）**，无需动态规划，支持路径依赖风险约束和高维状态空间。应用于完全市场金融模型和（再）保险多期配置。

- **核心创新**：
  1. **DCVaR 作为偏差度量（deviation measure）**比 mean-CVaR 更良态——DCVaR 在数学上 coercive（强制性的），保证优化问题良态；mean-CVaR 的 CVaR 约束在多期设置下时间不一致（time-inconsistent），DCVaR 通过"偏差"定义绕开此问题
  2. **RNN 参数化绕开动态规划维数灾难**——传统多期 CVaR 优化需动态规划，状态空间随期数指数增长；RNN 用循环结构隐式编码路径依赖，将无限维最优策略映射到有限维参数空间
  3. **预承诺策略（pre-commitment）**——在 t=0 锁定整个轨迹的最优策略，后续不重新优化。虽非时间一致但 RNN 的端到端训练使其可执行

- **与本项目 §2 分层裁定架构的关系**：
  - **范式差异**：本项目是**分层裁定**（策略层粗仓位 → firm 层 Kelly 精裁决 → 硬上限裁剪），DCVaR RNN 是**统一多期优化器**——将整个投资周期的仓位决策作为单一优化问题。与 §3.1 全 MVO 统一优化器（拒绝）同类，但 DCVaR RNN 有两个关键改进：① DCVaR 比 mean-variance 更适合重尾分布（CVaR 捕捉尾部）；② RNN 绕开 MVO 的协方差矩阵估计（§3.1 拒绝理由之一）
  - **与 §3.7 HRP / §3.8 Bayesian Kelly / §3.9 Tepelyan 的区别**：HRP/Bayesian Kelly/Tepelyan 都是**单期**仓位方法（每期独立决策），DCVaR RNN 是**多期**方法（跨期联合优化）。多期优化的优势是显式建模路径依赖（如回撤约束、终端财富约束），劣势是计算复杂度和时间不一致性
  - **与 35 号 §4.14 CDaR / §4.16 CED 的关系**：CDaR/CED 是回撤的路径依赖度量，DCVaR RNN 是终端财富的路径依赖优化——两者从不同角度处理路径依赖，理论上 DCVaR 可扩展为约束 CDaR 的多期优化

- **记为 Phase 4 远期候选（非近期）**：
  1. **架构范式不兼容**：本项目分层裁定架构（§2.1 分层流程总览）的核心是"策略层粗仓位 + firm 层 Kelly 精裁决 + 硬上限裁剪"三层分离，DCVaR RNN 是统一优化器——切换是范式替代非增量改进，成本极高
  2. **RNN 参数化的不可解释性**：本项目"可解释性优先"原则（§2.7 边界声明），RNN 的黑箱仓位决策与 Kelly 公式的闭式可解释性形成对比。即便 DCVaR 数学上更优，RNN 参数化使仓位决策不可审计
  3. **多期预承诺的时间不一致性**：预承诺策略在 t>0 时不再最优（时间不一致），投资者有偏离预承诺策略的动机。本项目 T+1 + convergence_window 的低频再平衡哲学与多期联合优化有张力
  4. **SCOR 再保险场景 ≠ A 股交易场景**：论文应用于（再）保险多期配置（低频年度决策+长期负债约束），A 股日频/盘中交易的高频场景与论文场景差异大，DCVaR 在高频下的有效性未验证
  5. **DCVaR 偏差度量的借鉴价值**：即便不采用 RNN 统一优化器，**DCVaR 作为偏差度量比 CVaR 更良态**的洞察可用于 36 号 VaR/ES 监控——当前 36 号用 CVaR（ES），可评估 DCVaR 作为 ES 的偏差变体是否提供更稳定的尾部风险度量

- **重评条件**：① 策略数扩展到 ≥10 且分层裁定架构证明不足以处理跨期路径依赖（如多期回撤约束）时；② RNN 仓位决策的可解释性技术（attention 可视化/SHAP 归因）成熟后；③ 实盘 ≥2 年后多期优化样本充足时。**不设近期施工计划**

> **为何列入而非直接拒绝**：DCVaR RNN 是多期组合优化的前沿方法（SCOR 再保险团队 2026-04），DCVaR 偏差度量比 mean-CVaR 更良态的洞察 + RNN 绕开动态规划的方法论创新，是组合优化领域的重要进展。登记此方向避免实盘后跨期路径依赖需求出现时重新调研多期优化方法。与 §3.7 HRP（单期风险平价）+ §3.8 Bayesian Kelly（单期参数不确定性）+ §3.9 Tepelyan（单期多元 Kelly）形成"单期 → 多期"的演进维度。Phase 4 定位确保不挤占近期施工带宽，且 DCVaR 偏差度量洞察可先于 RNN 优化器在 36 号 ES 监控中评估借鉴

> **⚠️ 路径依赖警示——"凸性才创造价值"（v1.22.0 补）**：[Noguer i Alonso 2026-08-03 "Path Portfolio Optimization: Defect, Lift, and the Price of Path Complexity" arXiv:2608.02355](https://arxiv.org/abs/2608.02355) 用**路径签名（path signature）**的张量代数做组合优化，发现**全部增益在对称块（终端增量的凸性），而非路径依赖块**——即"路径复杂性本身不创造价值，凸性才创造价值"。实证：期望签名已知时 2 资产确定性等价提升 11 倍、20 资产截面提升 60 倍，但估计时未正则策略在样本约 6 观测/参数前严重为负（过拟合风险极高）。**对 DCVaR RNN 的直接警示**：RNN 学到的"路径依赖"可能部分是过拟合，真正信号在对称凸性结构。Phase 4 评估 DCVaR RNN 时须验证：① RNN 捕获的路径依赖信号是否在对称化（去除路径信息）后消失（若消失则信号在凸性非路径）；② 与 Noguer 签名方法的对称块做 ablation 对比（若对称块已捕获大部分增益，RNN 的路径建模复杂度不值得）。此警示不改变 DCVaR RNN 的 Phase 4 远期候选定位，但为评估提供了"路径依赖 vs 凸性"的验证维度

## 4. 上限定义

### 4.1 参数上限汇总

| 参数 | 上限值 | 性质 |
|---|---|---|
| 单票仓位 | 8%（总资金口径，MOD-POS-021）/ 5%（MOD-POS-001 默认 + MOD-POS-010 硬限） | 硬上限，按比例削；三层口径待统一（§2.4.1 / §5） |
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
| **MVP（当前）** | 静态差异化映射表；密度 PDF 未就绪时 Kelly 降级历史回测；硬上限裁剪就绪；精确 Kelly 公式（§2.3.1）已采用（代码二值 Kelly 即精确 Kelly） | 本备忘定稿即可施工 |
| **阶段 2** | G04 产出首批 3 策略定义后，校准粗仓位映射表 | 20_first_batch_strategies 产出 |
| **阶段 3** | BM-SEL-13 密度 PDF 就绪，Kelly 主源切换（p/b → μ/σ² 参数化可选，两者等价） | BM-SEL-13 施工完成 |
| **阶段 4（待裁定）** | 评估 Conformal Kelly 替代/补充 σ 估计；评估 Bayesian Kelly 处理参数不确定性 | Conformal Kelly OOS 增长验证有效 / 各策略 50+ trades track record |

### 4.3 为何这是上限而非妥协
- 策略层 inverse-vol + firm 层半 Kelly + 硬上限裁剪，是 2026 年主流实证共识（Morwane / quanthedgeai / crucible-backtester）
- 个人系统不需要机构级 MVO/协方差估计的复杂度——那是钱多/人多必须分散的产物（system_charter §3 约束五）
- 真正的上限 = 在分层裁定框架内把每个 StrategyBook 粗仓位 + firm 层 Kelly 精裁决做到极致，而不是在 firm 层堆优化器

### 4.4 过度工程审查（2026-08-10）

| 组件 | 是否过重 | 裁定 |
|---|---|---|
| **firm 层 Kelly 精裁决** | ⚠️ 需评估密度预测需求 | **不过重**。半 Kelly 是 2026 全行业共识（[xueqiu](https://xueqiu.com/7992658178/396010169) 2026-06 / [arrowalgo](https://arrowalgo.com/kelly-criterion-position-sizing/) 2026-06 / [nexusfi](https://nexusfi.com/a/risk-management/kelly-criterion) 2026-06 / [pfolio](https://www.pfolio.io/academy/kelly-criterion) 2026-04 / [marketmaker.cc](https://marketmaker.cc/nl/blog/post/kelly-criterion-strategy-sizing/) 2026-06 均确认 half Kelly 保 75% 增长），非可选优化。v1.4.0 采用精确 Kelly 公式（arXiv:2604.24723 Bloomberg 2026-04）消除了"连续 vs 二值形式冲突"的过重评估——代码二值 Kelly 已是精确 Kelly，无需额外实现连续形式。分布感知调整是**防御性只减不增**，即使估计不准也不会增加风险（最坏退化为不调整）。当前代码 MVP 仅实现 VaR/CVaR（C4/C5）+ 波动率检查（C3），偏度/峰度（C10）属阶段 3，渐进式落地不算过重 |
| **inverse-vol 粗仓位** | ✅ 合适 | 只估 1 个参数（σ），2026 实证（[xfinlink](https://xfinlink.com/blog/risk-parity-mega-cap-drawdown-python) 2026-06）确认降回撤（−19.1%→−17.6%），[pomegra](https://pomegra.io/learn/library/track-e-trading-risk/risk-management/chapter-05-portfolio-risk/risk-parity-in-practice) 2026 确认零售级 inverse-vol 可行（季度重算即可）。full risk parity 需协方差才是过重，已拒绝（§3.3） |
| **分布感知（偏度/峰度/VaR/CVaR）** | ⚠️ 偏度/峰度可缓 | VaR/CVaR（C4/C5）已施工且必要（A 股尾部风险）。偏度/峰度（C10）依赖 BM-SEL-13 高阶矩，当前缓施合理。一旦密度 PDF 就绪，偏度/峰度只是乘法因子，边际成本低 |
| **pro-rata 归一化** | ✅ 合适 | O(N) 缩放，保留 Kelly 相对排序，[prevayo/eltonaguiar](https://github.com/) 2026 实践确认。不引入优化器，非过重 |

**结论**：分层裁定整体不过重。Kelly 精裁决的"精"在半 Kelly 硬上限 + 防御性分布调整，不在协方差估计或优化器。真正的过重是 MVO/协方差（已拒绝 §3.1/§3.6）。当前代码 MVP（二值 Kelly + VaR/CVaR + 波动率检查）是恰当的起点，分布感知高阶矩随 BM-SEL-13 渐进补充。

### 4.5 已施工设施盘点（2026-08-12 审查新增，通用规则 #11）

> 本备忘 §2 的算法 spec 对应的已施工代码资产盘点。先清楚有什么，才知怎么改、该退役什么。

| 设施 | 模块 | 路径 | 状态 | 覆盖本备忘章节 |
|---|---|---|---|---|
| 仓位决策引擎 | MOD-POS-001 | `src/zephyr/position/core/position_sizing_engine.py`（881 行） | ✅ production | §2.3 主体：C1 半 Kelly（二值 `f*=(bp-q)/b`，§2.3.1 已证即精确 Kelly）+ C2 风险配额 + C3 波动率检查（μ+2σ 减半）+ C4/C5 VaR/CVaR 下调（0.8/0.7）+ C12 单票默认 5%（`RiskLimits.symbol_overrides` 可覆盖）+ C13 总仓位 12 态 `MARKET_REGIME_CAPS`（§2.4.3 映射一致）+ C6 参与率 >15% 否决 + C7/C8 退出时间减仓 + C9 策略容量 + C11 冲击成本否决（sqrt 模型）+ POS-006 现金 / POS-007 资金曲线 / POS-017 日历 + 降级模式（D-SIGNAL 缺失默认态④）+ 幂等键 |
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | ✅ production（70 测试，30号 v2.5.0 §2.2 施工状态块） | §2.2 策略层粗仓位：`size_positions` 支持 equal_weight / risk_parity / custom，**禁用 Kelly/MVO**（与 §2.7 边界声明一致） |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | ✅ production（54 测试） | §2.4 硬上限裁剪执行（求和/按比例削/冲突净额，G13 范围） |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | ✅ production（47 测试） | G14 三级升级（本备忘只引用不展开） |

**设计已定但代码未施工**（均属已知演进项，非缺口）：

| 未施工项 | 本备忘出处 | 阻塞条件 |
|---|---|---|
| C10 偏度/峰度分布感知 | §2.3.3 | BM-SEL-13 密度 PDF 高阶矩输出（阶段 3） |
| `sizing_basis` 显式输出（6 约束取最小命名） | §2.3.4 | MOD-POS-001 输出 dataclass 补字段（§6 待定） |
| ADV 三档流动性硬上限（20%/10% 两档削减） | §2.4.4 | 代码 C6 参与率 >15% 否决是**近似但不等价**——C6 是否决（veto 保持现仓），§2.4.4 是削减（truncate 到 20% ADV）且含 P25 最坏情况口径；施工时注意口径差异 |
| 策略层 inverse-vol σ_i 异常判定 4 检查链 | §2.2.2 | StrategyBook risk_parity 路径的异常降级逻辑（§2.2.2 补的施工参数） |

**域文档滞后提示**：64_d_position.md（auto-generator，date 2026-08-05）仍将 MOD-POS-020/021 标为"设计态/骨架 v0.1.0"，与 30号 v2.5.0 + 本表不符——该文档需重新生成，见 §6 待定问题。

## 5. 待裁定（暂缓项）

> 以下项目暂不施工，**非永久禁止**。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **Conformal Kelly** | 2026-08 arXiv 前沿研究，用 conformal prediction 区间宽度做 fractional Kelly 缩放，有有限样本覆盖率保证；但论文 lockbox OOS 增长失效（2022 后 8.5%/7.0% 低于被动基准），不成熟 | Conformal Kelly OOS 增长验证有效；其 drawdown dial（区间 downside miss 频繁→砍杠杆）可作为风控叠加，与 30_multi_strategy_concurrency §2.5 回撤 Protocol 互补 |
| **Bayesian Kelly（参数不确定性）** | 固定半 Kelly 隐含"edge 估计误差固定 50%"假设；Bayesian Kelly 对 edge 参数（p/b 或 μ/σ²）建先验分布，后验期望 Kelly 自动按不确定性缩放。**理论基础**（[Browne & Whitt, Columbia 1995](https://business.columbia.edu/sites/default/files-efs/pubfiles/6343/bayes_kelly.pdf)）：Beta 共轭先验下最优策略是 bet a fraction = posterior mean increment 的线性函数（经典 Bayesian Kelly 最优性证明，连续时间极限可显式计算最优控制），为 Sukhov 2026 工程实现提供理论根基。[sergeisukhovmkt 2026-06](https://github.com/sergeisukhovmkt/Bayesian-Kelly-Criterion-with-Parameter-Uncertainty) S&P 500 E-mini 2000-2019 实证（Donchian 20 日通道突破）：**捕获全 Kelly 87% 增长 + 最大回撤减 60% + 破产风险降 96% + Sharpe 最高**——优于固定半 Kelly（半 Kelly 保 75% 增长但未按不确定性动态调整）。与 Empirical Kelly with UQ（下行）互补：Empirical Kelly 用 MC 模拟量化 edge 的 CV，Bayesian Kelly 用先验→后验更新；两者本质都是"按 edge 估计不确定性动态调 Kelly 分数" | 各策略 50+ trades track record 可估计 edge 参数先验分布；与 §4.2 阶段 4 Conformal Kelly 评估同步进行。**§3.8 已补施工参数**：κ=30（swing trading）、f_max=0.15（correlated portfolio 上限，与单票 8% 叠加取最小）、n_eff=κ 时精确等价半 Kelly |
| **动态粗仓位算法选择** | MVP 用静态差异化映射表；动态（按策略滚动 Sharpe 自适应选算法）增加 meta 参数 | 各策略有 6+ 月实盘 track record |
| **Kelly 分数自适应 / Empirical Kelly with UQ** | MVP 固定半 Kelly（0.5×）；自适应 Kelly 分数增加复杂度。**2026-08 前沿算法**：Empirical Kelly with Monte Carlo Uncertainty Quantification（[xarticle](https://www.xarticle.news/article/tech/how-to-use-prediction-market-data-like-hedge-funds-complete-roadmap) 2026-02）公式 `f_empirical = f_kelly × (1 - CV_edge)`，其中 `CV_edge = σ_edge / μ_edge`（edge 估计的变异系数）。高不确定性 → 大 CV → 激进 haircut；低不确定性 → 小 CV → sizing 接近理论 Kelly。比固定半 Kelly 更精细——半 Kelly 隐含假设"edge 估计误差固定 50%"，Empirical Kelly 按 edge 估计的实际不确定性动态调整。与 Conformal Kelly（§5 第一行）互补：Conformal 用区间宽度调 σ，Empirical Kelly 用 edge 的 MC 不确定性调分数 | 密度 PDF 主源稳定运行 6+ 月，各策略 50+ trades track record 可量化 CV_edge |
| **full risk parity** | 需估协方差，与 §3.1 拒绝协方差一致 | 协方差估计方案成熟（因子模型+shrinkage 验证有效），且 N 策略数显著增加 |
| **样本不足 Kelly 降级** | MVP 固定半 Kelly；样本 <50 trades 时 Kelly 估计误差大（completetradersedge 实证：±5% 胜率误差致 Kelly 变 3×），应进一步降级或忽略 Kelly 用固定比例 | 各策略有 50+ trades track record |
| ~~**Kelly 形式统一（二值 vs 连续）**~~ | ✅ **已解决**（v1.4.0）：arXiv:2604.24723 Bloomberg 2026-04 证明二值 `f*=(bp-q)/b`、精确 `f*=μ/(μ+σ²/(1+μ))`、Merton `K=μ/σ²` 是同一 Kelly 最优解的三种参数化（§2.3.1）。代码二值 Kelly 已是精确 Kelly，与设计目标统一，无需 BM-SEL-13 接口定型后再统一 | — 已关闭 |
| **单票上限三层口径统一** | MOD-POS-001 默认 5% / MOD-POS-021 聚合 8% / MOD-POS-010 硬限 5%，8% > 5% 致冗余裁剪（§2.4.1） | G04 首批策略产出后，统一三处单票口径（候选：全对齐 8% 或全对齐 5%） |
| **偏度/峰度分布感知（C10）** | 代码当前仅实现 VaR/CVaR（C4/C5）+ 波动率检查（C3），偏度/峰度调整（C10）依赖 BM-SEL-13 高阶矩，属阶段 2/3（§2.3.3） | BM-SEL-13 产出偏度/峰度，C10 施工完成 |
| **Factor-Based Conditional Diffusion Model（密度 PDF 远期）** | MVP 密度 PDF（BM-SEL-13）用条件分布积分；扩散模型（arXiv:2509.22088v3, CUHK 2026-06）用 Diffusion Transformer 学习 A 股下一日收益截面分布，生成样本做 mean-CVaR 优化，A 股实证优于 mean-variance/等权/DCC-GARCH。属密度预测的生成式 AI 演进，工程重 | BM-SEL-13 稳定运行 + GPU 资源充足 + 扩散模型 OOS 验证有效 |
| **MARCD: Regime-Conditioned Diffusion + CVaR QP（密度 PDF 远期增强版）** | **2026-08 最新研究**（arXiv:2510.10807v3, Alzahrani PIF 2025-11）：在 Factor-Based Diffusion 基础上叠加 **regime 条件** ——① Gaussian HMM 推断 latent regime（与本项目 10_regime_detector HMM 同构）；② regime-conditioned diffusion generator 生成情景样本；③ **tail-weighted diffusion loss** 上加权低分位结果（专为回撤控制设计）；④ **Regime-MoE denoiser** gate 随 crisis posterior 增大（危机态更敏感）；⑤ **CVaR epigraph QP** 凸优化分配器（box/turnover 约束，可审计）。严格 walk-forward 2005-2025 多资产 ETF 实证：MaxDD 9.3% vs BL 14.1%（**降 34%**），scenario calibration 更强。**比 Factor-Based Diffusion 更优**——regime 条件化 + 尾部加权损失 + 凸 CVaR 分配器三者协同，且与本项目 regime 架构天然契合（HMM→diffusion→CVaR 对应 regime_detector→BM-SEL-13→Kelly+CVaR 裁剪）。属密度 PDF + regime 联合远期候选，工程更重（需训练 diffusion + HMM 联合） | BM-SEL-13 稳定运行 + GPU 资源充足 + regime HMM C1 验证通过 + MARCD OOS 验证有效 |
| **Diffolio: Direct Portfolio Distribution Diffusion（组合分布远期候选）** | **2026-02 最新研究**（WSDM 2026, Jeon/Lee/Kang Seoul National University, DOI:10.1145/3773966.3777955）：与 MARCD/Factor-Based Diffusion 的**范式差异**——不生成收益分布再优化，而是**直接学习伪最优组合分布**（portfolio distribution），在去噪扩散过程中嵌入 **risk guidance 机制**（用户指定风险水平 → 引导去噪方向），直接采样组合权重。实证：多市场数据集 Annualized Rate of Return **+12.1pp** 优于基线，风险控制+可靠性均优。**与 MARCD 的区别**：MARCD 是"生成收益情景→CVaR QP 优化"两阶段（density→optimizer），Diffolio 是"直接生成组合"端到端（density=portfolio）。**优势**：避免中间优化步骤的误差传播，risk guidance 原生嵌入去噪过程；**劣势**：可解释性不如 MARCD 的凸 QP（Diffolio 的去噪过程是黑箱，无 KKT 审计），且"伪最优"标签依赖训练时的优化器选择（训练-推理一致性风险）。属直接组合分布远期候选，与 MARCD 互补（MARDD 可审计+解释，Diffolio 端到端+性能） | BM-SEL-13 稳定运行 + GPU 资源充足 + Diffolio OOS 验证有效 + 可解释性需求评估 |
| **Conformal Prediction for VaR/ES（有限样本覆盖保证）** | §2.3.3 分布感知调整使用"前瞻 VaR_95 / CVaR_95"做尾部风险下调，但**VaR/CVaR 的计算方法未指定**（参数化 GARCH/EVT 假设分布形态，A 股厚尾+偏度下失真）。**2026 前沿**：[arXiv:2602.03903](https://arxiv.org/abs/2602.03903)（Schmitt, Oxford, 2026-02）提出 **regime-weighted conformal risk control (RWC)**——用 conformal prediction 校准 VaR 安全缓冲，指数时间衰减 + **regime-similarity 权重**（按 regime 相似度加权历史预测误差），在 weighted exchangeability 下提供**有限样本覆盖保证**，不假设分布形态。**与本项目 regime 架构的天然契合**：RWC 的 regime-similarity weighting 与 10_regime_detector 的 HMM regime 态直接对接——当前 regime 下历史同类 regime 的预测误差做 conformal 校准，比全局校准更精准。time-weighted conformal (TWC) 是 strong default，RWC 在 regime-conditional 稳定性上可额外改善。[MDPI Mathematics 14(15):2847](https://www.mdpi.com/2227-7390/14/15/2847)（2026-08-06 发表）进一步给出 **joint VaR/ES conformal bounds**——在非可交换金融时间序列下用 swap-distance bound + regime-drift bound 联合校准 VaR 突破频率与 ES 突破幅度。[marketmaker.cc 2026-06](https://marketmaker.cc/en/blog/post/conformal-prediction-trading/) 给出 conformal position sizing 工程实现。**为何记为待裁定而非采纳**：MVP 的 VaR/CVaR 已由代码 C4/C5 实现（var_reduce_factor=0.8/cvar_reduce_factor=0.7），当前 VaR 来源待确认（§6 待定问题）。Conformal VaR/ES 需 calibration set + 在线更新，且 exchangeability 假设在 regime 切换时需 weighted 扩展，工程成本中等。但比参数化 VaR（Gaussian 假设在 A 股厚尾下系统性低估尾部风险）理论更严谨——是 §2.3.3 VaR/CVaR 计算方法的首选远期方案 | §2.3.3 VaR/CVaR 计算方法定型（§6 待定问题）+ 各策略 50+ trades 校准数据 + regime HMM C1 验证通过 |
| **MPC 动态风险调整（Stochastic Model Predictive Control）** | **2026 前沿**（[arXiv:2604.00415](https://arxiv.org/abs/2604.00415), Tan/Hsieh, 2026-04）：Double Linear Policy + Stochastic MPC（DLP-SMPC）——将权重选择形式化为**滚动时域最优控制问题**（receding-horizon），显式最大化风险调整收益 + 强制 survivability 约束 + 预测正期望约束，解析梯度 + L-BFGS-B 求解。实证：动态闭环方法在 risk-adjusted performance 和 drawdown control 上优于常量权重和预设时变 DLP 基线。**与本项目 regime Shrinkage 的范式差异**：regime Shrinkage 是**离散分档**（9 基础态 + 3 特殊态，HMM 提前识别 regime → 离散调总仓位上限）；MPC 是**连续闭环**（每期滚动优化，预测模型 + 场景生成 + 约束求解）。**为何记为待裁定而非采纳**：① regime Shrinkage 已由 30_multi_strategy_concurrency §2.2 + 34_regime_meta_allocator 定稿，MPC 是替代范式非增量改进，切换成本高；② MPC 需收益预测模型 + 场景生成（scenario generation），比 regime Shrinkage 的"HMM→分档映射"重得多——属研究课题级复杂度（与 §3.1 拒绝 MVO 同类：AI 能写对优化器代码但写不出准确的预测模型）；③ MPC 的核心价值（连续闭环+约束求解）在 A 股 T+1 低频再平衡场景下优势不显著——T+1 + convergence_window 防抖已天然限制再平衡频率，连续优化的边际收益有限。**但 MPC 思路可部分借鉴**：regime Shrinkage 的"离散分档"可视为 MPC 的"粗粒化离散版"（§2.4.3 已建立 vol-targeting 等价关系），未来若 regime 检测精度提升 + 场景生成方案成熟，可评估 MPC 替代离散分档。另见 [arXiv:2603.28898](https://arxiv.org/abs/2603.28898)（Bayforest + Bertsekas, 2026-03）MPC for Trade Execution——凸 QP 每步求解，平衡 completion/impact/opportunity cost，NASDAQ Level-3 数据实证降 schedule shortfall 40-50%，属执行层远期候选（见 41_buy_flow §5.2） | regime Shrinkage 实盘换手率/回撤数据积累 + 收益预测模型 + 场景生成方案成熟（因子模型 + shrinkage） |

## 6. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 首批 3 策略确认（打板+多因子+事件驱动）→ 粗仓位映射表校准 | 30_multi_strategy_concurrency §6.1 / G04 | 待 G04（20_first_batch_strategies）产出 |
| BM-SEL-13 密度 PDF 就绪时间 → Kelly 参数主源切换 | 本备忘 §2.3.2 | 待 BM-SEL-13 施工 |
| convergence_window 按换手率定（打板 1-2 / 多因子 3-5 / 事件 2-3 天）→ 影响再平衡成本-收益 | 30_multi_strategy_concurrency §6.4 / G14 | 待首批策略定后校准 |
| Kelly 参数密度 PDF 降级触发条件细化 | 本备忘 §2.3.2 | 待 BM-SEL-13 接口契约明确后定 |
| `sizing_basis` 输出字段补全（5 约束取最小 + 命名 binding constraint） | 本备忘 §2.3.4（2026-08-10 补充） | 待 MOD-POS-001 Kelly 精裁决施工时补 `sizing_basis` 到输出 dataclass，提升归因可观测性（deadeye-rs 2026-06 `sizing_basis` 模式） |
| §2.3.3 前瞻 VaR_95 / CVaR_95 的**计算方法**未指定 | 本备忘 §2.3.3（2026-08-10 审查发现） | 当前代码 C4/C5 已实现 var_reduce_factor=0.8 / cvar_reduce_factor=0.7 的下调逻辑，但 VaR/CVaR **数值从何而来**未定型——候选：① 参数化（GARCH/EVT，假设分布形态，A 股厚尾下易失真）② 密度 PDF 积分（BM-SEL-13 就绪后，与 §2.3.2 Kelly 参数同源）③ **Conformal Prediction**（§5 待裁定，regime-weighted conformal，有限样本覆盖保证，与 regime 架构契合）④ **EVT-Based Tail Budgeting**（[stockalpha](https://stockalpha.ai/alpha-learning/evt-based-tail-budgeting-allocating-capital-by-expected-tail-loss) 2026-02-17：GPD 拟合尾部超限 + ETL=Expected Tail Loss 做 tail budget 分配，不依赖整体分布假设只拟合尾部，A 股厚尾场景理论最严谨；与 36号 VaR/ES 监控的 GPD 校准同源可复用）。需人决策：MVP 先用哪种（密度 PDF 未就绪时降级方案），远期演进为 conformal 的触发条件 |
| 30号 §2.2 遗留描述待同步（StrategyBook"Kelly/risk parity/等权"旧文字与 §2.1"策略层不用 Kelly"矛盾；FirmRiskAggregator 链路缺 MOD-POS-001 Kelly 环节） | 2026-08-12 审查发现（30号 v2.5.0 §2.2，与其 §2.1/§7.2 及代码 size_positions 不符） | 归 30号作者侧修订，本备忘不越界改；与本备忘 §2.1/§2.7 引用一致性不受影响（31号引用的 30号 §2.1 分层裁定内容成立） |
| 64_d_position.md 域文档滞后待重新生成（MOD-POS-020/021 标"设计态/骨架"，实际已 production 171 测试全绿；64号全文未引用本备忘） | 2026-08-12 审查发现（64号 date 2026-08-05 早于 08-10 三模块施工） | 归 auto-generator 重新生成；本备忘 §4.5 已盘点真实状态可作生成输入 |

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
- **Conformal Kelly (arXiv:2608.01494v1, 2026-08-02)** — conformal prediction 75% 区间做 fractional Kelly 缩放；反直觉发现"宽度稳定性 > 局部锐度"（每个自适应调整损失 0.7-5.3pp 年化增长）；开发窗口 28.5% 年化/Sharpe 1.34/MaxDD 27.7% 但 **lockbox 样本外增长未持仓**（8.5%/7.0% 年化低于被动基准，calibration 0.745 vs 0.750 持仓但 growth 不持仓）；风险控制策略（下行 miss→削杠杆）MaxDD 27.7%→20.3% Sharpe 提升 rank-based p=1/41。本备忘吸收"稳不要锐"原则（§2.3.2）+ lockbox 负结果风险提示（§2.3.2）+ 模型失效检测思路（§2.3.2 降级第 5 项），Conformal Kelly 记为待裁定演进路径（§5）；其 §6.4 实测 per-asset Kelly 在硬上限约束下优于 multivariate Kelly（w=Σ⁻¹μ），印证本项目不做协方差的决策（§3.6）
- **quanthedgeai Strategy Allocation Methods (2026-06)** — "Theory says mean-variance. Practice says inverse volatility." 印证 inverse-vol 估 1 参数最鲁棒，强化策略层 inverse-vol 选择（§2.2 / §3.3）
- **crucible-backtester PR#559 (2026-07)** — fractional-Kelly = `kelly_fraction × μ / σ²` 工程实现，印证连续 Kelly 形式（§2.3.1）
- **2026 多源 fractional Kelly 共识**（momentumq / backtrex / journalplus）——机构 0.2-0.5× Kelly，half Kelly 保 75% 增长，强化半 Kelly 硬上限（§2.3.1 / §3.4）
- **[marketmaker.cc Kelly 系列](https://marketmaker.cc/nl/blog/post/kelly-criterion-strategy-sizing/)（2026-06）** — 连续 Kelly `f*=μ/σ²`（Merton fraction）推导 + 与 Sharpe 关系（g*=SR²/2）；二值/连续两种形式等价最优目标。印证 §2.3.1 连续形式选择 + §2.3.1 实现差异协调（二值/连续均为单标的 Kelly）
- **[pfolio.io Kelly criterion](https://www.pfolio.io/academy/kelly-criterion)（2026-04）** — 多标的 Kelly 全解需协方差矩阵（w=Σ⁻¹μ），per-asset Kelly 不需。印证 §3.6 per-asset Kelly + 硬上限优于 multivariate Kelly
- **[ryanoconnellfinance Kelly Calculator](https://ryanoconnellfinance.com/calculators/kelly-criterion-calculator/)（2026）** — 连续 `f*=(μ-r)/σ²`（投资版）vs 二值 `f*=p-q/b`（赌博版）双模式；half Kelly 保 75% 增长。印证 §2.3.1 两种形式 + 半 Kelly
- **[nexusfi Kelly for Futures](https://nexusfi.com/a/risk-management/kelly-criterion)（2026-06）** — full Kelly 破产风险 20-43%，half Kelly 降至 1.5-12%，quarter Kelly <2%。印证半 Kelly 硬上限（§2.3.1 / §3.4）
- **[xfinlink inverse-vol 实证](https://xfinlink.com/blog/risk-parity-mega-cap-drawdown-python)（2026-06）** — 10 只 mega-cap 3 年回测：inverse-vol vs 等权，年化波动 15.8%→13.5%，MaxDD −19.1%→−17.6%（降回撤），但收益 26.9%→20.7%（降收益）。印证 §2.2.2 inverse-vol 降回撤 + §3.3 不用 full risk parity
- **[pomegra retail risk parity](https://pomegra.io/learn/library/track-e-trading-risk/risk-management/chapter-05-portfolio-risk/risk-parity-in-practice)（2026）** — 零售级 inverse-vol 可行，季度重算波动率即可，不需杠杆。印证 §2.2.2 inverse-vol 适合个人系统
- **[algovestiq position sizing](https://www.algovestiq.com/learn/answers/how-to-size-stock-positions)（2026-05）** — 行业基准"hard cap 8-10% per position, 20-25% per sector"。印证 §2.4.1 单票 8% + §2.4.2 行业 30% 绝对上限
- **[tierzero multi-venue risk limits](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading)（2026-01）** — 三层限仓栈（strategy → venue → portfolio），"portfolio limit is the hard ceiling"，"common mistake is to set limits only at layer 1 and assume aggregation takes care of itself"。印证 §2.4 firm 层硬上限裁剪必要性（G13 FirmRiskAggregator 存在理由）
- **[arXiv:2503.17927 Optimal Betting](https://arxiv.org/pdf/2503.17927)（2025-03）** — fractional Kelly 统一框架（离散/连续），Kelly 估计误差致过注→破产，fractional Kelly 等价于收缩估计器。印证 §2.3.2 "稳不要锐" + §3.4 半 Kelly
- **[arXiv:2604.24723 Efficient Multivariate Kelly](https://arxiv.org/pdf/2604.24723v2)（Bloomberg 2026-04）** — 严格推导精确 Kelly `f*=μ/(μ+σ²/(1+μ))`，证明 Merton `K=μ/σ²` 是 μ→0 小 edge 极限，二值 `f*=(bp-q)/b` 是 (p,b) 参数化等价形式。**核心发现**：大 edge 时精确形式自动饱和到 1（不杠杆），Merton 给出 f>>1 需裁剪。**解决 §2.3.1 连续/二值形式冲突**（三者统一），关闭 §5 "Kelly 形式统一"待裁定项。其 multivariate Kelly §6.4 实测（gross cap 约束下 w=Σ⁻¹μ 增长 0.023-0.179 远差于 per-asset Kelly）印证 §3.6 不做协方差
- **[CSDN 有限时域分位数优化综述](https://bbs.csdn.net/weixin_33502772/article/details/100128334)（2026-06）** — 严格数学证明：有限时域分位数优化最优策略当时域→∞渐近收敛于 Kelly 策略。即 Kelly 是所有有限时域风险控制策略的长期极限。印证 §3.4 Kelly 方向正确 + fractional Kelly 控制有限时域尾部风险的必要性
- **[湘财证券 2026年8月大类资产配置](http://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/838419242728/index.phtml)（2026-07-26）** — A 股券商研究用波动率锚定风险平价均衡模型（inverse-vol + 风险贡献度），目标每类资产对组合风险贡献基本相等。印证 §2.2.2 inverse-vol 在 A 股的实际应用 + §2.4.2 行业硬约束必要性
- **[licai.cofool 量化仓位管理指南](https://licai.cofool.com/user/guide_view_3417771.html)（2026-07-03）** — A 股量化场景仓位管理参数基准：单票 5-15%、总仓位 60-80%、行业 ≤30%、单一风格 ≤50%。印证 §2.4 硬上限参数（单票 8%、行业 30%、总仓位 80%）符合 A 股行业基准
- **[xueqiu 多标的凯利公式](https://xueqiu.com/8100256332/395264697)（2026-06-17）** — A 股多标的 Kelly 实践：∑f_i>1 时等比例缩放到 100%（多元 Kelly 标准解法），半 Kelly/1/3 Kelly，保留 10-30% 现金缓冲。印证 §2.3.5 pro-rata 归一化 + §2.5 现金管理
- **[elearnmarkets Kelly's Criterion](https://blog.elearnmarkets.com/kellys-criterion-explained/)（2026-08-06）** — SEBI 2025-07 数据 91% F&O 交易者亏损（方向对但 size 错）。half Kelly + disciplined risk management 提升一致性、降回撤。印证 §2.3.1 半 Kelly 硬上限 + §3.4 全 Kelly 拒绝
- **[deadeye-rs #33 risk-aware position sizing](https://github.com/teddyjfpender/deadeye-rs/issues/33)（2026-06，v0.1.17 已实现）** — fractional-Kelly / CVaR cap 双约束 + `sizing_basis` 命名 binding constraint（half-kelly / cvar-cap / budget），多约束取最小。印证 §2.3.4 binding constraint 显式化（本项目扩展为 5 约束：strategy_intent / kelly_budget / var_cap / cvar_cap / single_name_cap）
- **[xarticle Empirical Kelly with MC UQ](https://www.xarticle.news/article/tech/how-to-use-prediction-market-data-like-hedge-funds-complete-roadmap)（2026-02）** — 对冲基金实践：`f_empirical = f_kelly × (1 - CV_edge)`，CV_edge 为 edge 估计的变异系数（MC 模拟得到）。比固定 fractional Kelly 更精细——按 edge 估计的实际不确定性动态调整。印证 §5 Empirical Kelly with UQ 待裁定项
- **[pooyagolchian Portfolio Risk Management 2026](https://pooyagolchian.com/blog/portfolio-risk-var-cvar-kelly-criterion-2026/)（2026-04）** — Full Kelly -62% MaxDD / Half Kelly -38% / Quarter Kelly -22% / Risk Parity Baseline -18%。Quarter Kelly 85% 增长 + 35% 回撤，是 return/drawdown trade-off 甜点。印证 §2.3.1 半 Kelly 选择（0.5×介于 half/quarter 之间，比 quarter 略激进但符合 A 股薄 edge 需适度下注）
- **[vzeman trading-autoresearch 2026](https://github.com/vzeman/trading-autoresearch/blob/main/systematic_equity_trading_research.md)（2026-05 编译）** — "Use 0.25× Kelly as a sanity ceiling on position sizes; do not let any single position's allocation exceed 0.25 × (signal_strength / signal_volatility²)"。quarter Kelly 作 sanity ceiling + 单标的上限 = 0.25×K。印证 §2.3.1 半 Kelly（0.5×比 0.25× 激进，但本项目有单票 8% 硬上限兜底，无需 quarter Kelly 那么保守）
- **[A股量化私募7月集体回撤·涵德风控升级](https://m.toutiao.com/group/7670831772460794420/)（2026-08）** — 2026-07 量化私募集体回撤（幻方单月-22%、明汯 9/14 产品年内负）。涵德投资风控升级：单票上限 1%→0.3%、持股 600→900 只、动量/残差波动率因子软约束→硬约束、敞口压至 0.2 倍标准差以内。印证 §2.4.1 单票硬上限必要性 + §2.3.3 分布感知（尾部风险防御）的实盘价值——2026-07 极端行情下因子共振导致多因子分散失效，硬约束+尾部风控是生存关键
- **[中信证券8月配置研报](https://36kr.com/newsflashes/3932984519146887)（2026-08-10）** — 8月初超跌反弹，科技持仓向核心资产集中，非科技增配能化/有色/创新药/头部券商。持仓成本/融资盘出清/拥挤度三视角量化评估修复进度。印证 §2.4.2 行业硬约束必要性（A 股结构性行情下行业轮动剧烈，行业集中度控制是必需风控）
- **[fortraders Volatility-Adjusted Returns](https://www.fortraders.com/blog/best-practices-volatility-adjusted-returns)（2026-05）** — VIX Regime 三档（<16/16-25/>25 → 1.0x/0.6-0.75x/0.3-0.5x），vol-targeting 在 2008 GFC 将 S&P drawdown -37%→-21.4%。印证 §2.4.3 regime Shrinkage ≈ regime-aware vol-targeting + §2.3.3 波动率检查（C3）
- **[HRP 2026 多源](https://www.foliolab.ai/docs/guide/methods/hrp)（foliolab/marketmaker/pfolio/metricgate/stockalpha 2026）** — López de Prado 2016 HRP 算法 2026 主流化，不需协方差求逆、OOS 优于 MVO。评估后拒绝（§3.7）：仍需相关性矩阵、A 股 regime 转折点聚类不稳定、小规模组合聚类优势不显著。记为远期候选（策略数>8 且标的数>50 时重评）
- **[Bayesian Kelly with Parameter Uncertainty](https://github.com/sergeisukhovmkt/Bayesian-Kelly-Criterion-with-Parameter-Uncertainty)（Sukhov 2026-06）** — Beta 共轭先验 + 有效样本量正则化 `f*=(p̄−(1−p̄)/b)·n_eff/(n_eff+κ)`，样本少自动收缩到不赌，闭式解不需 MC。比固定 fractional Kelly 更自适应。印证 §3.8 Bayesian Kelly 评估 + §5 Phase 2 候选（与 Conformal Kelly/Empirical Kelly UQ 三方对比）
- **[Factor-Based Conditional Diffusion Model](https://arxiv.org/html/2509.22088v3)（arXiv:2509.22088v3, CUHK 2026-06）** — Diffusion Transformer 学习 A 股下一日收益截面分布（token-wise conditioning），生成样本做 mean-CVaR 优化，A 股实证优于 mean-variance/等权/DCC-GARCH/shrinkage 估计器。属密度 PDF（BM-SEL-13）的生成式 AI 演进。印证 §5 Diffusion Model 远期候选
- **[nexusfi Multi-Strategy Automated Futures](https://nexusfi.com/a/automation/multi-strategy-portfolio-automated-futures)（2026-06）** — 多策略组合风险引擎实践：Risk Engine 聚合所有策略暴露+检查限仓+监控相关性；Effective Number of Bets（ENB=1/Σwᵢ²）衡量真实分散度；Incremental VaR（IVaR）衡量单策略对总组合 VaR 贡献；三层 kill switch（strategy/underlying/portfolio)。印证 32号 §2.7 contributions 归因（IVaR 简化版）+ §2.4 组合级硬裁剪必要性
- **[MARCD: Regime-Conditioned Diffusion for CVaR Portfolio](https://arxiv.org/html/2510.10807v3)（arXiv:2510.10807v3, Alzahrani PIF 2025-11）** — Multi-Agent Regime-Conditioned Diffusion 框架：Gaussian HMM 推断 regime + regime-conditioned diffusion 生成情景 + tail-weighted loss 上加权低分位 + Regime-MoE denoiser（crisis posterior gate）+ CVaR epigraph QP 凸分配器。严格 walk-forward 2005-2025 多资产 ETF：MaxDD 9.3% vs BL 14.1%（降 34%）。**比 Factor-Based Diffusion（arXiv:2509.22088v3）更优**——regime 条件化 + 尾部加权 + 凸 CVaR 三者协同，且与本项目 HMM→density PDF→Kelly+CVaR 架构天然契合。印证 §5 MARCD 远期候选（密度 PDF + regime 联合演进）
- **[algovantis Drawdown-Based Re-sizing](https://algovantis.com/optimizing-position-sizing-for-multi-strategy-risk-management-and-stability/)（2026-03）** — 多策略仓位管理实践：Drawdown-Based Re-sizing（策略回撤时缩减仓位，performance 恢复后逐步加回，作为自适应断路器）+ Volatility-Adjusted Sizing（ATR/std 逆波动率）+ Risk-Parity Allocation（等风险贡献，需协方差）+ 动态相关性矩阵（EWMA）。印证 §2.4.1 冷启动 ×30%（防未验证即满仓的同理：回撤/冷启动期都需缩减）+ 33号三级升级（drawdown 触发降级与恢复）+ §2.2.2 inverse-vol（volatility-adjusted sizing）
- **[Score-Based Diffusion for Dynamic Portfolio](https://arxiv.org/pdf/2507.09916)（arXiv:2507.09916v2, Aghapour & Bayraktar 2025-07）** — score-based diffusion 模型求解动态 mean-variance 组合选择：adapted Wasserstein 度量误差界 + policy gradient 算法 + RNN 编码市场状态。生成环境产出的组合 beat Markowitz/等权/S&P 500。印证 §5 Diffusion 远期候选（score-based 是 diffusion 的另一参数化，与 Factor-Based Diffusion 的 DDPM 互补）
- **[Passify Global Risk Overlay](https://www.einpresswire.com/article/896092429/passify-releases-new-quantitative-report-on-multi-algorithm-correlation-and-risk-aggregation)（2026-02）** — 多算法相关性风险报告："1% risk per trade on ten different bots can quickly escalate into 10% open exposure on a single correlated move"。Global Risk Overlay 独立于策略层，监控总组合暴露/杠杆/日浮盈亏，超阈值干预。印证 32号 §2.5 相关性聚类待裁定（跨策略相关性隐藏集中度风险）+ §2.4 组合级硬裁剪必要性（策略级限制不够，需 portfolio overlay）
- **[Karl Whelan: Kelly Strategies and Return on Capital Deployed](https://www.karlwhelan.com/Papers/KellyROI.pdf)（UCD 2026-05）** — Ethier-Tavaré 1983 结果扩展：Kelly 仓位最大化长期财富增长，但使**每美元部署资本的回报率约为固定下注策略的一半**（当预期收益→0 时收敛到指数分布均值 2）。fractional Kelly 随 scale 缩减，部署资本回报率趋向完整预期收益。**过度自信信念**会降低已实现部署资本回报率，零和设定下即使微小感知优势也可导致亏损。**对本项目启示**：个人系统无外部资金流压力（Whelan 指出的 Kelly ROI 与 fund flow 的张力对个人不适用），但**过度自信风险**印证 §2.3.2 "稳不要锐"原则 + §5 Bayesian Kelly/Empirical Kelly UQ 待裁定项（按 edge 估计不确定性动态调 Kelly 分数，避免过度自信下的过度下注）。半 Kelly 是部署资本 ROI 与财富增长的 trade-off 平衡点
- **[MDPI Economies: From Regime Detection to Decision Rules](https://www.mdpi.com/2227-7099/14/7/268)（Grube Martín-Lunas et al. 2026-07-09）** — 欧洲 10 资产 2000-2026 严格 walk-forward 实证：naive regime-conditional CVaR 分配产生**过高换手率 ~226%/年**，现实交易成本下净表现低于简单基准；实现感知替代方案（regime-constrained weight bands）在 ~29% 换手率下恢复差距（net Sharpe 与静态基准差 0.009）。**核心发现**："瓶颈不是 regime 检测，而是透明、稳定、成本感知的决策规则设计"。印证 §2.4.3 regime Shrinkage 离散分档比连续 CVaR 重分配换手率更低 + 33号 convergence_window 防抖的必要性 + §2.4 硬上限"只减不增"单向约束的换手率可控性
- **[Michael Burry Vol-Targeting Cascade Warning](https://www.insta-forex.com/in/forex_analysis/453380)（2026-08-05）** — 约 $5000 亿 vol-targeting 基金构成机械级联抛售风险：S&P 500 跌 2.5% → 这些基金从 77% → 50% 股权配置削减，形成"下跌→vol 上升→机械减仓→进一步下跌"恶性循环（与 1987 Black Monday portfolio insurance 同构）。印证 §2.4.3 纯连续 vol-targeting 系统性风险警示 + regime Shrinkage 离散分档+HMM 提前识别的缓释价值
- **[Diffolio: Diffusion Models for Risk-Aware Portfolio Optimization](https://doi.org/10.1145/3773966.3777955)（WSDM 2026, Jeon/Lee/Kang SNU）** — 直接学习伪最优组合分布（非收益分布），去噪过程中嵌入 risk guidance 机制，直接采样组合权重。多市场实证 ARR +12.1pp 优于基线。与 MARCD 互补（MARCD density→optimizer 两阶段可审计，Diffolio 端到端性能优但黑箱）。印证 §5 Diffolio 远期候选（直接组合分布 diffusion，范式不同于 MARCD/Factor-Based Diffusion）
- **[中邮证券：基于 LSTM-GHMM 混合方案的量化择时与动态仓位管理](https://pdf.dfcfw.com/pdf/H3_AP202607091826846688_1.pdf)（黄子崟, 2026-07-09）** — LSTM 自编码器 + 高斯 HMM 5 状态做 A 股择时+动态仓位。8 指数均相对买入持有正超额。**关键负结果**：2021/2026 结构性行情适应性偏弱，超额损失集中于仓位执行层——基于历史频度统计的 Kelly 公式在特定状态下"均值回归"保守倾向，对"假摔反包"响应不足。**印证 §2.3.2 Kelly 不做 regime 检测的正交设计**——Kelly 层不应承担择时职责（归 sleeve alpha 情绪周期），中邮失败正是"用 regime/Kelly 同时做择时+仓位"的混淆后果。A 股本土负结果实证，与 Conformal Kelly "稳定性优先"互印证
- **[Taming Tail Risk: Conformal Risk Control for Nonstationary Portfolio VaR](https://arxiv.org/abs/2602.03903)（Schmitt, Oxford, 2026-02）** — regime-weighted conformal risk control (RWC)：用 conformal prediction 校准 VaR 安全缓冲，指数时间衰减 + regime-similarity 权重，weighted exchangeability 下有限样本覆盖保证。TWC (time-weighted) 是 strong default，RWC 在 regime-conditional 稳定性上改善。**与本项目 regime 架构契合**——RWC 的 regime-similarity weighting 直接对接 10_regime_detector HMM。印证 §5 Conformal Prediction for VaR/ES 待裁定项（§2.3.3 VaR/CVaR 计算方法的首选远期方案）
- **[Finite-Sample Conformal Risk Bounds for Joint VaR and ES Forecasting](https://www.mdpi.com/2227-7390/14/15/2847)（Ye et al., MDPI Mathematics, 2026-08-06）** — 非可交换金融时间序列下 joint VaR/ES conformal 校准：swap-distance bound + regime-drift bound + β-mixing cost，联合校准 VaR 突破频率与 ES 突破幅度。八汇率+Bitcoin+GIFT-Eval 实证 violation rate 2.51%。印证 §5 Conformal VaR/ES 待裁定项（ES 不可单独 elicitable，需与 VaR 联合校准）
- **[Conformal Prediction for Risk-Aware Position Sizing](https://marketmaker.cc/en/blog/post/conformal-prediction-trading/)（marketmaker.cc, 2026-06）** — split conformal prediction 工程实现：nonconformity score → quantile → 预测区间，有限样本覆盖保证不依赖分布假设。分布无关（Gaussian/fat-tailed/skewed/heteroskedastic 均有效）。印证 §5 Conformal VaR/ES 工程可行性
- **[Dynamic Weight Optimization for DLP: A Stochastic MPC Approach](https://arxiv.org/abs/2604.00415)（Tan/Hsieh, 2026-04）** — Double Linear Policy + Stochastic MPC（DLP-SMPC）：滚动时域最优控制，显式最大化风险调整收益 + survivability 约束 + 预测正期望约束，解析梯度 + L-BFGS-B。实证动态闭环优于常量权重和预设时变基线。印证 §5 MPC 动态风险调整待裁定项（regime Shrinkage 离散分档 vs MPC 连续闭环的范式对比）
- **[Model Predictive Control For Trade Execution](https://arxiv.org/abs/2603.28898)（McAuliffe et al., Bayforest + Bertsekas, 2026-03）** — MPC 框架用于大单执行：凸 QP 每步求解，平衡 completion/impact/opportunity cost，NASDAQ Level-3 数据降 schedule shortfall 40-50%。比 RL 轻量（凸 QP vs 神经网络），属执行层远期候选（41_buy_flow §5.2 阶段 5/6）
- **[Portfolio Choice and the Bayesian Kelly Criterion](https://business.columbia.edu/sites/default/files-efs/pubfiles/6343/bayes_kelly.pdf)（Browne & Whitt, Columbia, Advances in Applied Probability 28(4):1145-1176, 1995/1996）** — 经典 Bayesian Kelly 理论奠基：参数未知的随机游走下，对数效用最优策略是 bet a fraction = posterior mean increment 的线性函数（state-dependent control，Kelly 策略的 Bayesian 推广）。Beta 共轭先验下连续时间极限可显式计算最优控制（rescaled Brownian motion），量化 randomness 的 financial value / perfect information gain / learning cost。**印证 §5 Bayesian Kelly 待裁定项的理论根基**——Sukhov 2026-06 工程实现（`f*=(p̄−(1−p̄)/b)·n_eff/(n_eff+κ)`）是 Browne & Whitt 理论的离散化参数化，闭式解不需 MC
- **[Bayesian Kelly Betting](https://github.com/s-vishnoi/bayesian-kelly-betting)（s-vishnoi, 2026-05-15）** — Beta 共轭先验 + 后验更新的教学级简化实现：θ~Be(α,β) 先验，二元胜负数据后验更新，按后验均值 Kelly sizing。与 Sukhov 2026-06 同思路但更简（无 n_eff/(n_eff+κ) 鲁棒性收缩项）。**印证 §5 Bayesian Kelly 待裁定项**——Beta 共轭先验是 Bayesian Kelly 的自然选择（θ∈[0,1] 约束 + 二元数据共轭），Sukhov 的有效样本量正则化是必要的鲁棒性增强

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
| 2026-08-10 | 1.3.0 | 已施工算法 why 回填 + 代码-设计差异协调 | §2.3.1 加实现现状差异框（连续 Kelly 设计目标 vs 二值 Kelly 代码现状，BM-SEL-13 产出 p/b，两者均单标的不需协方差）；§2.3.3 加 C10 偏度/峰度未实现标注（代码当前仅 C3/C4/C5）；§2.4.1 加 8%/5% 三层口径澄清（MOD-POS-001 默认 5% / MOD-POS-021 聚合 8% / MOD-POS-010 硬限 5%，冗余裁剪待统一）；§2.4.3 补 ⑩CRISIS/⑪RECOVERY/⑫BREAKOUT 三特殊态 + overlay 编号碰撞修正（事件驱动/板块轮动为 bool flag 非 enum）；§4.1 单票上限行更新；新增 §4.4 过度工程审查（Kelly 精裁决/inverse-vol/分布感知/pro-rata 四组件裁定）；§5 新增 3 项待裁定（Kelly 形式统一/单票口径统一/C10 偏度峰度）；§7.4 补 10 条 2026 实证（marketmaker/pfolio/ryanoconnell/nexusfi/xfinlink/pomegra/algovestiq/tierzero/arXiv 2503.17927）；全网搜索 2026 Kelly/risk parity/position sizing 实证 |
| 2026-08-10 | 1.4.0 | 精确 Kelly 公式统一三种形式 + 2026-08 最新研究补充 | §2.3.1 重写：引入精确 Kelly `f*=(μ-r)/((μ-r)+σ²/(1+(μ-r)))`（arXiv:2604.24723 Bloomberg 2026-04），证明二值/精确/Merton 三者统一（同一 Kelly 最优解的三种参数化），大 edge 自动饱和到 1 不需裁剪，消除"连续 vs 二值形式冲突"；§3.4 补有限时域分位数优化渐近收敛 Kelly 的理论支撑（CSDN 2026-06）；§4.2 阶段 3 更新（p/b↔μ/σ² 等价，可选参数化）；§4.4 Kelly 精裁决行补精确公式采用；§5 "Kelly 形式统一"待裁定项✅已解决关闭；§7.4 补 6 条 2026-08 最新实证（arXiv:2604.24723/CSDN/湘财证券/licai.cofool/xueqiu/elearnmarkets）；全网搜索 2026-08-08 最新 position sizing/Kelly/risk parity 算法 |
| 2026-08-10 | 1.5.0 | 施工流程算法缺失补充 + 选项外更好算法评估 + 2026-08-08 最新研究 | §2.3.4 补 binding constraint 显式化（5 约束取最小 + `sizing_basis` 命名，吸收 deadeye-rs 2026-06 v0.1.17 模式）；§2.4.3 补 regime Shrinkage ≈ regime-aware vol-targeting 等价关系（quant67/fortraders/pomegra/blave 2026）；§3.7 新增 HRP 评估节（López de Prado 2016，2026 主流化，评估后拒绝记为远期候选：仍需相关性矩阵、A 股 regime 转折点聚类不稳定、小规模组合聚类优势不显著）；§5 "Kelly 分数自适应"升级为"Empirical Kelly with UQ"（xarticle 2026-02 `f_empirical=f_kelly×(1-CV_edge)`，比固定半 Kelly 更精细）；§6 新增 `sizing_basis` 输出字段待定问题；§7.4 补 8 条 2026-08 最新实证（deadeye-rs/xarticle/pooyagolchian/vzeman/涵德风控升级/中信证券/fortraders/HRP 多源）；全网搜索 2026-08-08 最新 position sizing/portfolio aggregation/HRP/CVaR/vol-targeting 算法，评估选项外更好答案 |
| 2026-08-10 | 1.6.0 | 施工流程算法缺失补充 + Bayesian Kelly 评估 + Diffusion mean-CVaR 远期候选 + 2026-08 最新研究 | §2.3.2 补 Kelly 降级触发判定算法（NaN/分布合理性/样本量门控/覆盖率四检查链 + param_source 标记）；§2.4.1 补冷启动 ×30% 执行时机（策略层 budget 即乘 + 冷启动状态机 is_cold_start/cold_start_until + 退出阈值）；§3.8 新增 Bayesian Kelly with Parameter Uncertainty 评估节（Sukhov 2026-06 Beta 共轭先验+有效样本量正则化闭式解，与固定半Kelly/Empirical Kelly UQ/Conformal Kelly 三方对比，记为 Phase 2 候选）；§5 新增 Factor-Based Conditional Diffusion Model 远期候选（arXiv:2509.22088v3 CUHK A 股实证 mean-CVaR 优于 mean-variance/等权/DCC-GARCH，密度 PDF 生成式 AI 演进）；§7.4 补 3 条 2026-08 最新实证（Bayesian Kelly/Diffusion mean-CVaR A 股/nexusfi ENB+IVaR 归因）；全网搜索 2026-08-08 最新 position sizing/Kelly uncertainty/portfolio CVaR/Diffusion model 算法，评估选项外更好答案 |
| 2026-08-10 | 1.7.0 | HRP 评估二次审查 + HRP-μ 信号感知变体补充 | §3.7 HRP 评估节修正"HRP 无 μ"判断：Wuebben 2026-04 arXiv:2604.23833 提出 HRP-μ/HRP-Σμ/CRISP 三变体将 HRP 扩展为信号感知（incorporates μ），当 γ=0 且 μ=1 时精确退化为 De Prado 标准 HRP（Proposition 4.2），提供对冲感知（Proposition 4.4），O(N²) 与标准 HRP 同阶；此更新修正信号盲限制判断，但不改变核心拒绝理由（仍需相关性矩阵 ρ_ij + A 股 regime 转折点聚类不稳定 + 小规模聚类优势不显著）；远期候选条件更新为评估 HRP-μ（信号感知版，非标准 HRP）；全网搜索 2026-08-10 最新 HRP/portfolio allocation 算法 |
| 2026-08-10 | 1.8.0 | MARCD regime-conditioned diffusion 远期候选 + 2026-08 最新研究补充 | §5 新增 MARCD: Regime-Conditioned Diffusion + CVaR QP 远期候选（arXiv:2510.10807v2 Alzahrani PIF 2026-10：Gaussian HMM + regime-conditioned diffusion + tail-weighted loss + Regime-MoE denoiser + CVaR epigraph QP，MaxDD 9.3% vs 14.1% 降 34%，比 Factor-Based Diffusion 更优——regime 条件化+尾部加权+凸 CVaR 协同，与本项目 HMM→density PDF→Kelly+CVaR 架构天然契合）；§7.4 补 4 条 2026-08 最新实证（MARCD regime-conditioned diffusion/algovantis drawdown-based re-sizing/score-based diffusion dynamic portfolio/Passify global risk overlay）；全网搜索 2026-08-08 最新 position sizing/Kelly/diffusion model/CVaR portfolio/regime-conditioned 算法，评估选项外更好答案——MARCD 为本次搜索发现的最优远期候选 |
| 2026-08-10 | 1.9.0 | vol-targeting 系统性风险警示 + regime CVaR 换手率风险 + Diffolio 远期候选 + MARCD v3 更新 + 2026-08 最新研究 | §2.4.3 补纯 vol-targeting 系统性风险警示（Michael Burry 2026-08：$5000 亿 vol-targeting 基金 2.5% 跌幅触发 77%→50% 机械级联抛售，与 1987 portfolio insurance 同构；本项目 regime Shrinkage 离散分档+HMM 提前识别+convergence_window 防抖+现金储备四缓释措施）+ regime-conditional 重分配换手率风险（MDPI Economies 2026-07：naive regime-conditional CVaR 换手率 226%/年侵蚀净表现，瓶颈是决策规则设计非 regime 检测；本项目离散分档+只减不增+防抖天然换手率可控，待 G04 后实测）；§5 新增 Diffolio 远期候选（WSDM 2026 SNU：直接学习伪最优组合分布非收益分布，risk guidance 嵌入去噪过程，ARR +12.1pp；与 MARCD 互补——MARCD density→optimizer 可审计，Diffolio 端到端性能优但黑箱）；§5 MARCD 更新 v2→v3（arXiv:2510.10807v3 2025-11）；§7.4 补 4 条 2026-08 最新实证（Karl Whelan UCD Kelly ROI/MDPI Economies regime CVaR 换手率/Michael Burry vol-targeting 级联/Diffolio 直接组合分布 diffusion）；全网搜索 2026-08-08 最新 position sizing/Kelly/vol-targeting/regime CVaR/diffusion portfolio 算法，评估选项外更好答案——Diffolio 为本次搜索发现的新远期候选（与 MARCD 范式互补） |
| 2026-08-10 | 1.10.0 | A 股 Kelly 不做 regime 检测的本土负结果印证 + 2026-08 最新研究 | §2.3.2 补中邮证券 LSTM-GHMM 负结果（2026-07-09：LSTM 自编码器+高斯 HMM 5 状态做 A 股择时+动态仓位，2021/2026 结构性行情适应性偏弱，超额损失集中于仓位执行层——基于历史频度统计的 Kelly 公式在特定状态下"均值回归"保守倾向，对"假摔反包"响应不足；问题不在状态识别层而在仓位执行层。对本项目启示：Kelly 层不应承担择时职责归 sleeve alpha 情绪周期，regime→Shrinkage 节流路径正确避免 Kelly 做 regime-conditioned 检测，中邮失败正是"用 regime/Kelly 同时做择时+仓位"的混淆后果）；§7.4 补 1 条 A 股本土实证（中邮证券 LSTM-GHMM 负结果，与 Conformal Kelly"稳定性优先"互印证）；全网搜索 2026-08-08 最新 position sizing/Kelly/A 股实证算法，评估施工算法完整性——结论：§2.3 Kelly 施工算法（精确公式+降级触发判定四检查链+分布感知+合成规则+pro-rata归一化+CASH豁免）已完整可施工，中邮负结果为正交设计提供 A 股本土实证支撑非算法变更 |
| 2026-08-10 | 1.11.0 | Conformal Kelly lockbox 样本外负结果 + 降级触发第 5 项 + 2026-08-08 最新研究 | §2.3.2 补 Conformal Kelly lockbox 样本外负结果（arXiv:2608.01494v1 2026-08-02：开发窗口 28.5% 年化/Sharpe 1.34/MaxDD 27.7% 但 lockbox 样本外增长未持仓——8.5%/7.0% 年化低于被动基准，calibration 0.745 vs 0.750 持仓但 growth 不持仓；200 配置 LLM-agent 搜索过拟合开发窗口风险警示；正面结果——风险控制策略下行 miss→削杠杆 MaxDD 27.7%→20.3% Sharpe 提升 rank-based p=1/41，借鉴为降级触发第 5 项：密度 PDF 连续 N 日下行 miss 超 historical rate→Kelly 降级，检测"参数渐变失效"与四检查链"瞬时异常"互补）；§7.4 更新 Conformal Kelly 条目补 lockbox 具体数字+风险控制策略；全网搜索 2026-08-08 最新 Conformal Kelly/Bayesian Kelly/position sizing 算法，评估选项外更好答案——lockbox 负结果为 Conformal Kelly 远期候选提供重要风险校准（calibration 持仓≠growth 持仓），"模型失效检测+自动降杠杆"思路补充降级触发判定 |
| 2026-08-10 | 1.12.0 | Conformal Prediction for VaR/ES + MPC 动态风险调整待裁定 + VaR/CVaR 计算方法待定问题 | §5 新增 2 项待裁定：① Conformal Prediction for VaR/ES（arXiv:2602.03903 Schmitt Oxford 2026-02 regime-weighted conformal risk control，有限样本覆盖保证+regime-similarity 权重与本项目 HMM 契合；MDPI Mathematics 2026-08-06 joint VaR/ES conformal bounds；marketmaker.cc 2026-06 工程实现）——§2.3.3 前瞻 VaR/CVaR 计算方法未指定，conformal 是首选远期方案（参数化 GARCH/EVT 在 A 股厚尾下失真）② MPC 动态风险调整（arXiv:2604.00415 DLP-SMPC 2026-04 滚动时域最优控制+survivability 约束，regime Shrinkage 离散分档 vs MPC 连续闭环范式对比；arXiv:2603.28898 MPC for Trade Execution 凸 QP 执行层远期候选）；§6 新增待定问题：§2.3.3 VaR/CVaR 计算方法未指定（参数化/密度 PDF 积分/conformal 三候选，需人决策 MVP 先用哪种）；§7.4 补 5 条 2026 最新实证；全网搜索 2026-08-08 最新 conformal prediction VaR/ES + MPC portfolio 算法，评估选项外更好答案——Conformal VaR/ES 为 §2.3.3 未定型计算方法的首选远期方案，MPC 为 regime Shrinkage 的替代范式远期候选（非采纳，切换成本高+T+1 低频场景边际收益有限） |
| 2026-08-10 | 1.13.0 | Bayesian Kelly 理论根基补强 + 2026-08 最新研究 | §5 Bayesian Kelly 待裁定项补 Browne & Whitt 1995 经典理论根基（Columbia Advances in Applied Probability：Beta 共轭先验下最优策略是 bet fraction = posterior mean increment 线性函数，state-dependent control 是 Kelly 策略的 Bayesian 推广，连续时间极限可显式计算最优控制；为 Sukhov 2026-06 工程实现 `f*=(p̄−(1−p̄)/b)·n_eff/(n_eff+κ)` 提供理论奠基——Sukhov 是 Browne & Whitt 理论的离散化参数化闭式解）；§7.4 补 2 条 2026 最新实证（Browne & Whitt 1995 经典 Bayesian Kelly 理论/s-vishnoi 2026-05 Beta 共轭先验教学级简化印证 Sukhov 鲁棒性增强必要性）；全网搜索 2026-08-08 最新 Bayesian Kelly/parameter uncertainty Kelly/Beta prior position sizing 算法，评估选项外更好答案——Browne & Whitt 1995 为 Bayesian Kelly 待裁定项补强经典理论支撑（非算法变更，待裁定状态不变） |
| 2026-08-10 | 1.14.0 | 施工算法参数缺口补全 + Sukhov κ 推荐值 + 2026-08-08 最新研究 | §2.2.2 补 inverse-vol σ_i 异常判定阈值施工算法（4 条检查链：缺失检查 NaN/0 + 样本量门控<30 有效交易日 + 极端值>150% 年化 + 新股冷启<60 交易日，部分降级非阻断整策略）；§2.3.2 补降级触发第 5 项施工参数（N=20 交易日对齐浙商短期窗口 + historical rate=滚动 60 日下行 miss 率 P95 动态阈值 + 下行 miss 定义 + 降级动作 Kelly×0.5 持续至连续 10 日回落恢复）；§3.8 补 Sukhov κ 推荐值施工参数（swing trading κ=30 + correlated portfolio f_max=0.15 与单票 8% 叠加取最小 + n_eff=κ 精确等价半 Kelly + Monte Carlo 实证 Bayesian 优于 Half Kelly 增长 9.1% vs 7.9% 回撤 24.6% vs 31.2% Sharpe 0.89 vs 0.72）；§5 Bayesian Kelly 待裁定项重评条件补 κ=30/f_max=0.15 施工参数引用；全网搜索 2026-08-08 最新 position sizing/Kelly/Bayesian Kelly/A 股实证算法，评估施工算法完整性——结论：§2.2.2 σ_i 异常阈值 + §2.3.2 降级第 5 项 N 日值 + §3.8 κ 推荐值三项施工算法缺口已补全，Kelly 施工算法（精确公式+降级触发五检查链+分布感知+合成规则+pro-rata 归一化+CASH 豁免+σ_i 异常阈值）完整可施工 |
| 2026-08-10 | 1.15.0 | 资金利用率 70-90% 指引 + EVT Tail Budgeting 候选 + 文档结构审查 | §2.5 补资金利用率 70-90% 是特性非缺陷（quanthedgeai 2026-05-26 实证"Most portfolios should run at 70 to 90%"，本项目 regime Shrinkage 后常态 50-80% 天然符合，与 §2.4.3 Burry vol-targeting 级联警示协同——现金储备是缓释全市场同步减仓踩踏的第三道防线）；§6 VaR/CVaR 计算方法待定问题补第 4 候选 EVT-Based Tail Budgeting（stockalpha 2026-02-17 GPD 拟合尾部超限+ETL 做 tail budget 分配，不依赖整体分布假设只拟合尾部，与 36号 GPD 校准同源可复用）；全网搜索 2026-08-08 最新 position sizing/Kelly/firm risk aggregator/portfolio aggregation 算法+文档结构顺序内容审查——结论：31号文档结构（§1背景→§2决策→§3替代→§4上限→§5待裁定→§6待定→§7引用→§8交接→§9修订）符合 01_design_memo_management_spec §4.3 推荐章节，顺序正确无需调整；施工算法完整性——§2.2 粗仓位（等权+inverse-vol+σ_i 异常阈值）+§2.3 Kelly（精确公式+五检查链降级+分布感知+合成规则+pro-rata+CASH 豁免）+§2.4 硬上限（单票+行业+总仓位+冷启动）+§2.5 现金管理 全链路施工算法完整可施工，无缺失 |
| 2026-08-10 | 1.16.0 | Taleb 胖尾 quarter-Kelly 理论背书 + 2026-08-08 最新研究 | §2.3.1 补 Taleb 胖尾论点（convexly 2026-03 + Taleb *Statistical Consequences of Fat Tails* 2020 ch.10：Hill 尾指数 α<2 时样本方差不收敛，半 Kelly 依赖方差估计本身不稳定，建议 quarter-Kelly+barbell；convexly 实测 Polymarket α=1.28 印证。对本项目校准启示：① A 股个股 α≈2-4 中等厚尾，α<2 风险主要在次新股/事件期已被 §2.2.2 σ_i 异常判定覆盖；② **不把半 Kelly 降为 quarter-Kelly**——设计本就不依赖半 Kelly 单层，而是叠加 §2.3.3 分布感知+§2.3.4 多约束取最小+§2.4 硬上限+regime Shrinkage 四层独立兜底，尾部场景有效仓位已远低于半 Kelly 名义值，与 Taleb barbell 异曲同工；③ 校准参数：G04 首批策略 50+ trades 后用 Hill 估计器测 α，α<2 则 Kelly 倍数 0.5×→0.25× 或收紧 VaR/CVaR 阈值，与 §6 EVT Tail Budgeting 同源 GPD 可同时产出 α 估计。此论点为现有四层防御栈提供理论背书——保留多层硬约束而非简化为纯半 Kelly 正是 Taleb 胖尾批判所要求的风险架构）；全网搜索 2026-08-08 最新 position sizing/Kelly/fat tail 算法，评估选项外更好答案——Taleb 胖尾 quarter-Kelly 为本次搜索发现的理论补强（非算法变更，为现有四层防御栈提供学术背书+Hill α 校准参数），施工算法完整性不变 |
| 2026-08-10 | 1.17.0 | §3.9 新增 **Tepelyan 多元 Kelly sigmoid 标度律**（Tepelyan 2026-04 arXiv:2604.11550）——积分变换方法将多元 Kelly 从 O(2^N) 降至 O(N)+O(N²) 交叉项，发现 sigmoidal 标度律 `f*_i = f*_i^{independent} × σ(ρ)`（低相关≈独立 Kelly / 高相关≈半 Kelly，过渡区 S 形）+ 闭式参数化近似。**与 §3.6 拒绝 multivariate Kelly 的关系**：直接解决拒绝理由②（O(2^N) 复杂度），部分缓解①（仅需 pairwise ρ 而非完整 Σ），但③（A 股 regime 转折 ρ 不稳定）仍成立。**与 §3.8 Bayesian Kelly 正交**：Bayesian 管 per-asset 参数不确定性收缩，Tepelyan 管 multivariate 交叉相关折算。**与 §2.3.4 binding constraint 的关系**：sigmoid 标度律是硬上限取最小的**连续替代**远期路径。记为 Phase 3 远期候选，重评条件：策略数≥8 + §3.7 HRP 评估时同步校准 ρ 稳定性 + 实盘≥1 年 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。登记搜索 agent 返回的 6 项远期候选算法之一——Tepelyan 是 multivariate Kelly 的计算复杂度突破（O(2^N)→O(N)），使"多元 Kelly 不可计算"的拒绝理由②失效，但拒绝理由③（ρ 不稳定）仍成立，属远期升级路径非 MVP 施工 |
| 2026-08-10 | 1.18.0 | §2.4.4 流动性硬上限（ADV 口径）+ §2.3.4 binding constraint 栈第 6 项 + 2026-08-08 最新流动性 sizing 研究 | 十九次审查发现施工算法真实缺失——§2.4.1-2.4.3 仅有资金口径硬上限（单票 8%/行业 30%/总仓位 regime），缺流动性口径硬上限（仓位占 ADV 比例）。对 A 股打板（容量极小）+ T+1（无法当日退出）+ 涨跌停板（流动性瞬间归零），流动性口径是比资金口径更先 binding 的约束。§2.4.4 新增流动性硬上限施工算法（pomegra 2026 + skill4agent 2026 行业框架）：流动性成本三组件（Spread+Market Impact+Execution Risk）+ 三档 ADV 阈值（>20% ADV 削到 20%、>10% ADV 削半、否则不裁）+ A 股校准（20 日 ADV P25 最坏情况 sizing、T+1+涨跌停板取国际标准下限）+ 降级路径（ADV 缺失取同行业中位数）+ 与 §2.2.1 打板等权协同（min(等权, 0.20×ADV/资金)）+ MVP 必做（非远期）；§2.3.4 binding constraint 栈同步更新（5→6 约束、sizing_basis 5→7 值增加 liquidity_cap_moderate/severe、归因审计增加"流动性不足"维度）。全网搜索 2026-08-08 最新 liquidity-adjusted sizing/ADV position cap 算法，评估选项外更好答案——ADV 口径硬上限为本次审查发现的核心施工算法缺失（非理论背书，是实盘生存级 MVP 必做约束），前 18 轮未覆盖 |
| 2026-08-10 | 1.19.0 | §2.4.4 盘后固定价格交易缓解路径 + 2026-07-06 A 股新规整合 + 33号三级升级机制完整性验证 | 二十次审查 31/33号深度审查+2026-08-08 最新 A 股交易规则研究：①§2.4.4 补盘后固定价格交易缓解路径（A 股新规 2026-07-06：盘后固定价格交易扩展至全市场所有 A 股，以收盘价撮合——流动性上限违反时提供低冲击退出路径，Market Impact 组件最小化；施工衔接 33号 Tier 3 已实现 `_use_after_hours_fixed_price_fallback`，本节复用该路径，sizing_basis 标记 liquidity_cap_severe 后优先走盘后固定价格交易而非盘中 TWAP；注意：盘后流动性有限不可作常规退出仅作应急 fallback）；②33号三级升级机制完整性验证（general-purpose agent 全文读取 927 行——Tier1/2/3 触发条件+伪代码 650 行+convergence_window 表格+budget 防抖 5%/10% 双阈值+trim_ratio 公式+lot 对齐+涨跌停顺延+盘后 fallback+部分成交追踪+System Error CB+hysteresis 全部完整，前 Explore agent 报告的"缺失"为幻觉）；③A 股 2026-07-06 新规影响评估——ST 股 ±5%→±10% 不影响项目（21号已排除 ST 股），盘后固定价格交易扩展至全市场是利好（为流动性上限+Tier 3 强裁提供低冲击退出路径）。全网搜索 2026-08-08 最新 A 股交易规则/overnight gap risk/T+1 execution 算法——盘后固定价格交易为本次审查发现的核心衔接改进（连接新规与流动性上限），overnight gap risk 已被 regime Shrinkage+drawdown protocol+单票 8%+ADV 上限多层覆盖无需新增 |
| 2026-08-10 | 1.20.0 | §2.4.3 补 BlackRock 比例控制闭环 vol-targeting 远期候选 | 二十二次审查+2026-08-08 最新 vol-targeting 研究：§2.4.3 补 BlackRock AI Lab 2026-03（arXiv:2603.01298 Devanathan/Rueter/Boyd/Candès/Hastie/Kochenderfer）比例反馈控制 vol-targeting——开环 `L_t=σ*/σ_t` 三缺陷（turnover 尖峰/leverage spikes/σ 估计误差敏感），BlackRock 改闭环跟踪误差反馈 `e_k=log(σ̂^ind/σ^tar)`、控制律 `w_k=w_{k-1}-K_p·e_k` + drawdown suppression 扩展（与 35号回撤 Protocol 离散分档目标同构）。**定位远期候选非 MVP 替代**：regime Shrinkage 离散分档 vs BlackRock 连续闭环是 vol-targeting 频谱两端；MVP 不切换理由——① regime Shrinkage 已定稿切换成本高 ② BlackRock 单资产模型多资产推广需重设跟踪误差聚合 ③ 连续闭环与 T+1+convergence_window 低频再平衡哲学有张力。**可借鉴洞察**：① drawdown suppression 与 35号同构为离散分档提供连续版参照（G04 后若阶梯跳变过强评估引入平滑项）② 跟踪误差 e_k 作 55号监控维度（实现 vs 目标 vol 偏离度告警）③ 闭环反馈缓释 Burry 级联风险新视角。全网搜索 2026-08-08 最新 vol-targeting/leveraged volatility control/proportional control portfolio 算法，评估选项外更好答案——BlackRock 闭环控制为本次搜索发现的 vol-targeting 连续化替代范式（远期候选非采纳），施工算法完整性不变 |
| 2026-08-10 | 1.21.0 | §3.10 新增 Multi-period mean-DCVaR optimization via RNN —— arXiv:2604.14439 Lelong/Maume-Deschamps/Thevenot 2026-04 SCOR | 三十轮审查 + 后台搜索 agent 返回 2026-08-08 最新仓位管理研究 5 领域 15 篇论文，§3.10 新增 DCVaR RNN 多期组合优化（arXiv:2604.14439 Lelong/Maume-Deschamps/Thevenot 2026-04-17 SCOR 再保险数学团队）：离散时间多期组合优化约束为 Deviation CVaR（DCVaR=CVaR−E[W_T] 偏差度量），RNN 近似最优预承诺策略绕开动态规划维数灾难。**核心创新**：① DCVaR 作为偏差度量比 mean-CVaR 更良态（coercive），绕开多期 CVaR 时间不一致性；② RNN 参数化将无限维最优策略映射到有限维参数空间；③ 预承诺策略端到端训练可执行。**与本项目关系**：范式差异（分层裁定 vs 统一多期优化器），与 §3.1 全 MVO 统一优化器（拒绝）同类但 DCVaR RNN 有两改进（DCVaR 适合重尾 + RNN 绕开协方差估计）；与 §3.7 HRP/§3.8 Bayesian Kelly/§3.9 Tepelyan 区别是单期 vs 多期。**记为 Phase 4 远期候选**：① 架构范式不兼容（分层裁定 vs 统一优化器）；② RNN 不可解释性违反可解释性优先原则；③ 多期预承诺时间不一致性与 T+1 低频再平衡有张力；④ SCOR 再保险场景 ≠ A 股交易场景。**DCVaR 偏差度量洞察可先于 RNN 在 36 号 ES 监控评估借鉴**。**施工算法完整性结论**：31 号 22 轮审查施工算法完整性闭合，本次为多期组合优化远期候选登记非新施工算法 |
| 2026-08-10 | 1.22.0 | §3.10 补 **路径依赖警示——"凸性才创造价值"**（Noguer i Alonso arXiv:2608.02355 2026-08-03 Path Portfolio Optimization） | 三十三轮审查+后台搜索 agent 返回 2026-08-01~08 窗口 7 领域 13 篇论文，经覆盖检查 11/13 已整合，仅 2 项未整合（Noguer Path Portfolio + Garcia Seuma 临界性异质性）。§3.10 DCVaR RNN 章节补 Noguer i Alonso 2026-08-03 arXiv:2608.02355"Path Portfolio Optimization: Defect, Lift, and the Price of Path Complexity"路径签名（path signature）张量代数组合优化——核心发现"路径复杂性本身不创造价值，凸性才创造价值"（全部增益在对称块=终端增量凸性，非路径依赖块）；实证：期望签名已知时 2 资产确定性等价提升 11 倍/20 资产截面提升 60 倍，但估计时未正则策略在样本约 6 观测/参数前严重为负（过拟合风险极高）。**对 DCVaR RNN 的直接警示**：RNN 学到的"路径依赖"可能部分是过拟合，真正信号在对称凸性结构。Phase 4 评估 DCVaR RNN 时须验证：① RNN 捕获的路径依赖信号是否在对称化（去除路径信息）后消失（若消失则信号在凸性非路径）；② 与 Noguer 签名方法的对称块做 ablation 对比（若对称块已捕获大部分增益，RNN 的路径建模复杂度不值得）。此警示不改变 DCVaR RNN 的 Phase 4 远期候选定位，但为评估提供"路径依赖 vs 凸性"验证维度。**施工算法完整性结论**：31 号施工算法完整性闭合，本次为路径依赖方法论警示非新施工算法 |
| 2026-08-10 | 1.23.0 | §2.6 FirmTargetPortfolio 跨文档数据结构同步修复（31号 4 字段过时定义 → 32号 §2.7 权威 10 字段定义） | 六十一轮审查。自动化跨文档数据结构字段一致性审计发现 `FirmTargetPortfolio` 在 31号 §2.6（L423）与 32号 §2.7（L602）定义完全不一致：31号 4 字段（holdings/kelly_adjustments/clip_log/timestamp）为 v1.0.0 遗留简化版，32号 10 字段（firm_positions/total_exposure/total_budget/cash_ratio/constraint_checks/conflicts_resolved/degraded/created_at/idempotency_key/schema_version）为 v1.0.x 演进后权威版——两者字段集零交集，31号 缺 constraint_checks/conflicts_resolved/degraded/contributions 等施工关键字段，代码施工若依 31号 旧定义将产出不完整 FirmTargetPortfolio。修复：31号 §2.6 FirmTargetPortfolio 定义替换为 32号 §2.7 权威版（含 FirmTarget 子结构 target_weight/contributions/cut_ratio），补字段映射说明（旧 holdings→firm_positions、旧 kelly_adjustments→degraded+kelly_param_source、旧 clip_log→constraint_checks+cut_ratio、旧 timestamp→created_at+idempotency_key+schema_version），契约纪律"holdings 权重和=1.0"更新为"firm_positions 权重和+cash_ratio=total_budget"。StrategyTarget 定义两文档一致无需同步。**施工算法完整性结论**：跨文档数据结构漂移修复填补施工契约缺口，非新算法 |
| 2026-08-12 | 1.24.0 | 新增 §4.5 已施工设施盘点 + §6 两项跨文档同步待定问题 | 架构审查回填（通用规则 #11 已施工设施盘点要求）：① §4.5 盘点分层裁定全链路代码资产——MOD-POS-001（881 行 production，C1-C13+POS-006/007/017 全约束链，与本备忘 §2.3/§2.4.3 映射一致）+ MOD-POS-020/021/022 三模块 production（171 测试全绿，30号 v2.5.0 §2.2 印证）；登记 4 项"设计已定代码未施工"演进项（C10 偏度峰度/sizing_basis 显式输出/ADV 三档与 C6 参与率否决的口径差异警示/inverse-vol σ_i 异常 4 检查链）；② §6 新增 2 项跨文档同步待定问题（30号 §2.2 遗留矛盾描述待修订、64_d_position.md 域文档滞后待重新生成——均不越界改）；全网施工状态核查确认 §2 决策链已完整落地可施工 |
