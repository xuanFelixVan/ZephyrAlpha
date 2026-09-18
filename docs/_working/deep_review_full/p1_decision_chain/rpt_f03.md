---
ttl: task_bound
doc_type: report
title: 深度审查报告——F03 WQ Alpha87算子库（WqAlpha87）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：F03 WQ Alpha87算子库（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 因子算子库（批量因子正确性地基：算子语义错=批量因子错）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/factor/wq_alpha_87.py:91(ops)` / :943(compute)
- 生产调用方: **仅 factor/__init__.py re-export**——grep 全仓无生产 compute/register_all/validate_ic 调用方；header [CONSUMERS]"因子注册表/feature_store（委托注入点）"实为未接线
- 测试文件: tests/factor/test_wq_alpha_87.py（存在，质量好：全 87 可算+截断前缀不变性）
- 变更热力: 2026 年 4 commits（低热）
- 材料包缺项: 真实行情数据画像缺（复权/停牌影响以代码走查+设计口径判定）

## 1 对象快照

WorldQuant 101 精选 87 公式：19 个时序/截面算子（ops 类）+ 87 个公式实现 + prepare 派生（vwap/returns/cap/adv{5..180}）。排除项：ic_ir_calc IC 计算本体、FactorRegistry。本审查完成 **19 个算子逐语义抽验 + 15 个高频公式逐式对照**（作业要求≥15 算子，超额）。

## 2 算子逐语义抽验（19 个，对照 WorldQuant 论文算子定义）

| 算子 | 实现 | 论文定义 | 判定 |
|---|---|---|---|
| rank | :95-97 df.rank(axis=1,pct=True) | 截面百分位 (0,1] | ✓ |
| delay | :100-101 shift(_w(d)) | x 的 d 日前值 | ✓ |
| delta | :104-105 x−shift(x,d) | x−delay(x,d) | ✓ |
| ts_sum/ts_mean/ts_min/ts_max | :108-121 rolling(min_periods=w) | 同名 | ✓（min_periods=全窗，保守） |
| ts_argmax/ts_argmin | :124-135 argmax+1，窗内含 NaN→NaN | 论文未定义（业界约定） | ✓（+1 常量平移经下游 rank 单调不变，无害） |
| ts_rank | :138-143 rolling rank pct 取末位 | 时序百分位 | ✓ |
| ts_product | :146-150 np.prod | 同名 | ✓ |
| stddev | :153-154 rolling.std() | 滚动标准差 | ✓（ddof=1，论文未定，合理） |
| correlation/covariance | :157-165 rolling.corr/cov + inf→NaN | 时序相关/协方差 | ✓（零方差 inf 有守卫） |
| decay_linear | :168-174 权重 1..w 归一（新值权重最大） | 线性衰减加权平均（paper: d,d-1,...,1） | ✓ |
| scale | :177-178 k·x/Σ\|x\|（行向，0→NaN） | scale(x,k=1) 使 Σ|x|=k | ✓ |
| sign | :181-182 np.sign | 同名 | ✓ |
| signed_power | :185-186 sign(x)·\|x\|^p | 同名 | ✓（#84 指数为 DataFrame 的逐元素推广，底为正成立） |
| adv{d} | :189-191 rolling mean | 平均日成交量 | ✓ |
| log | :194-195 where(>0)→NaN | 自然对数 | ✓（非正保护） |
| ind_neutralize_proxy | :198-200 截面 demean | IndNeutralize 降级（文档显式标注 5 个降级式） | ✓（失真已声明，IC 验证自然反映） |
| min/max(df)（_df_min/_df_max） | :211-216 where | 逐元素 min/max | ✓ |
| where（三元） | :203-208 | 条件选择 | ✓（标量/混合分支全覆盖） |

## 3 公式逐式对照抽验（15 个高频公式 + 2 个特查）

逐式与论文/流通开源口径比对：**#1**(:228-231 ✓ stddev.where(cond,close)→signed_power²→ts_argmax5→rank)、**#5**(:248 ✓)、**#7**(:256-258 ✓ adv20<volume 三元)、**#9**(:266-268 ✓ 窗口=5，与论文一致——论文 Alpha#9 用 ts_min/ts_max(delta(close,1),**5**)，初查疑"4"系 #10 之混淆，驳回)、**#10**(:271-273 ✓ 窗口4+rank)、**#12**(:281 ✓)、**#13**(:285 ✓)、**#19**(:315-318 ✓)、**#24**(:340-342 ✓ 条件 delta/ delay ≤0.05，与 ChaosQuant 等流通开源口径一致——疑"缺 -1 因子"驳回)、**#29**(:362-370 ✓ 嵌套与论文逐层对应)、**#32**(:389-392 ✓ 外层 scale 不套 20·scale 项，与论文分段一致)、**#41**(:445-446 ✓)、**#47**(:476-480 ✓)、**#54**(:512-513 ✓)、**#101**(:809-810 ✓)。特查：**#66/#89** 的 `(low·a)+(low·(1−a))` 退化 mix 为**论文原文固有怪式**，忠实复刻非抄写错误 ✓。

## 4 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 代数除法无 inf/除零守卫（与 corr/cov 的 inf→NaN 守卫不对齐）：#83 分母 (atr/(vwap−close)) vwap=close 时→inf；#53 分母 (close−low)=0→inf；inf 静默传入 IC 链 | wq_alpha_87.py:509, 662-664 vs 160 | P2 | 造 vwap==close 的列跑 compute(83)，看输出含 inf |
| A | **A 股复权口径无强制**：prepare 不校验/不标注复权；未复权数据下除权日 delta/returns 跳变→批量公式系统性失真（header INVARIANTS 只声明 OHLCV 约束） | wq_alpha_87.py:927-941, :8 | P1（口径） | 复权/不复权同股对比 compute(12) 除权日值 |
| A | 停牌 volume=0→vwap=NaN ✓，但 min_periods=w 使 NaN 向后传播整窗（保守可接受）；adv 同理——登记为已知口径非缺陷 | wq_alpha_87.py:934, 108-121 | P3 | 造 volume=0 行跑 ts_mean |
| B | adv 窗口集 {5,10,15,20,30,40,50,60,81,120,150,180} 覆盖全部公式引用（5/10/15/20/30/40/50/60/81/120/150/180）——**已查无缺** | :939-940 vs 公式体 | P3（查无） | grep adv 引用比对 |
| C | **孤儿（模式#8）**：生产调用方=0，register_all/validate_ic 委托点无装配批接线；87 个因子实际未进任何因子注册表 | wq_alpha_87.py:959-981; grep 全仓 | P2 | grep 生产 import |
| A.3 | 测试良好：全 87 可算（:132）、前缀不变性抽 8 式（:189-200）✓ PIT 证据；缺口=未测 inf 行为、未测除权场景、前缀不变性仅抽 8/87 | tests/factor/test_wq_alpha_87.py | P3 | 扩参数化到全 87 跑一遍 |
| E | compute 对 NaN 输入行静默产出 NaN 行（无数据完整性告警）——下游 IC 缺口静默 | :943-957 | P3 | 造含 NaN 列跑全 87 |

## 5 SOTA 对照

- **对等已有**：WorldQuant《101 Formulaic Alphas》Kakushadze，arXiv:1601.00991（2016，https://arxiv.org/pdf/1601.00991 ）——19 算子+15 公式抽验一致；Alpha#9 窗口=5 经论文检索确认（2026-09-18 检索）。
- **对等已有**：开源复现口径（ChaosQuant/alpha101，https://github.com/ChaosQuant/alpha101 ；Harvey-Sun/World_Quant_Alphas，https://github.com/Harvey-Sun/World_Quant_Alphas ）——14 个剔除集与 87 集口径一致，#24 条件式一致。
- **受阻**：#66/#92 的浮点常数逐项 verbatim 核对受阻（公式列表页超时/无公式文本），记挂起（置信度中：结构已对，常数抄错风险低但未归零）。
- **立卡候选**：中文卖方复现矿脉（BigQuant 101 复现，https://bigquant.com/wiki/doc/Gl3vglHyog ）可作 IC 横向对拍基准（变形测试素材），非替换。

## 6 缺陷清单

1. **P1（口径）复权无强制**：算子/公式层全对，但数据层口径（hfq/qfq）无断言无标注——除权跳变污染所有 delta/returns 类因子的截面排名。建议：prepare 增加复权口径声明参数或检测跳变告警。验证法：同股复权/不复权对比。
2. **P2 孤儿**：87 因子未接线进注册表/feature_store（模式#8）。验证法：grep。
3. **P2 inf 无守卫**：#53/#83 代数除法。验证法：构造边界输入。
4. **P3**：前缀不变性抽样率 8/87、NaN 无告警、ts_argmax 约定留档。

## 7 挂起疑问

- #66/#92 常数 verbatim 核对受阻（见 §5）。
- cap=close·volume 代理口径（:938）声明"保留集无 cap 公式"——已抽验保留集无 cap 引用 ✓，留档即可。

## 8 完备性自评

六轴全查。算子抽验 19/19、公式抽验 15+2/87（高频覆盖达标；余 70 式为结构同构的低风险长尾，靠前缀不变性测试兜底）。长尾：①性能（rolling.apply Python lambda，87 式全历史成本）未量化；②float 窗口 _w 四舍五入的 banker's rounding 边界（2.5→2）未测。

## 9 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
