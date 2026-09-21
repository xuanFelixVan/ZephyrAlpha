---
ttl: task_bound
title: 深度审查作业簿——VaR计算器
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：VaR计算器（K05）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（目标文件基线后零漂移；9 commits=稳定）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/risk/core/var_calculator.py:233`（参数法 :365-379；历史模拟 :381-393；校验 :397-430）
- 生产调用方（实测 grep）: `ex_core/risk_layer_orchestrator.py:461,787`（回撤链降级回退路径）；`risk/core/var_intraday_recalc.py:325`（盘中重算）——**已接线非孤儿**；且 FHS(GARCH) 引擎为主链、本件为回退（orchestrator:770-796）
- 测试文件: tests/risk/test_var_calculator.py（34 用例）
- 运行结果: `python -m pytest tests/risk/test_var_calculator.py -q` → 34 passed（Python 3.12.8 / numpy / scipy）

## 1 对象快照

- **范围**：VaRCalculator 全文件（参数法+历史模拟+conservative_max+数据校验）；上游喂入窗口与下游消费只审接线面。
- **排除项**：FHS 引擎/tail_risk_monitor/var_breach 状态机（各自独立对象）；var_backtest_store。
- **材料缺项声明**：数据画像（实际喂入窗口长度、nav 序列 NaN 率）未取——min_history 充分性结论受此限制（见 §4-1 验证法）。
- **测试覆盖概况**：34 用例含边界（NaN 过滤/占比 raise/样本不足/配置非法/两法对拍）；质量好（信任）；portfolio_value 非有限值路径无覆盖。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 参数法公式正确：VaR=(z·σ−μ)·V·√T，z=\|ppf(1−c)\|，ddof=1；高均值低波动负值→下限 0，语义正确 | var_calculator.py:154-157,365-379 | 已查无 | 手算 0.95/1.6449 对拍测试 |
| A | 历史模拟公式正确：−quantile(r,1−c)·V·√T；√T 缩放为近似已如实注释；identical 收敛 σ=0/全正收益→VaR=0 边界语义成立 | var_calculator.py:381-393 | 已查无 | 构造全正收益序列→0 |
| A | **min_history=30 对 95% 分位数统计不足**：n=30 时 (1−c)=5% 分位数下仅约 1.5 个尾样本，分位数估计噪声大（Hendricks 1996：小样本极难准确估计 95/99 极端分位数）；conservative_max 的 parametric 侧部分兜底（σ 估计 n=30 相对稳），但 HS 侧贡献的 max 值可在尾部样本巧合时低估或高估 | var_calculator.py:129,136；轴 F 出处见 §3 | P2 | `VaRCalculator().calculate(returns[:30], 1e6)` 与 `[:2500]` 的 value 对比观察分位数漂移；对照生产实际喂入窗口长度（orchestrator min_samples_for_var 配置） |
| A | **portfolio_value 非有限值穿透**：NaN 比较恒 False→`portfolio_value <= 0` 检查放行→value_pct=value/NaN=NaN 全链传播（VaRResult.value_pct/tail 链消费 NaN）；±Inf 同理 | var_calculator.py:282-283,303 | P2 | `calculate(np.ones(50)*0.01, portfolio_value=float("nan"))`→不抛且 value_pct=NaN |
| A | 非有限值过滤+占比闸（≤5% 过滤计数、>5% raise）设计正确且方向 Fail-Closed（双轮审查裁定在案，编号纠纷有终局记录） | var_calculator.py:101-113,397-430 | 已查无 | 已有测试覆盖 |
| A | calculate_portfolio：合成收益=Σwᵢrᵢ（固定权重近似，未计再平衡漂移——业界常规）；weights 不校验 Σ=1/非负（空头/杠杆权重静默接受，与 A 股 long-only 体系不符但作为通用计算器可辩护） | var_calculator.py:333-361 | P3 | 传 weights=[2,-1] 静默出值 |
| B | 上游窗口：orchestrator 有独立 min_samples_for_var 闸（不足→degraded），FHS 为主链、本件回退，FHS 失败回退链有留痕（record_fhs_failure）；上游 nav 非有限未在喂入前过滤（A 轴 P2 的入口） | risk_layer_orchestrator.py:770-796,799-801 | P2（并入 A 轴） | 读码 |
| C | 下游：value_pct→tail/回撤链 position_cap 缩放与 var_breach 状态机；评估失效→degraded+回撤链仍生效（Fail-Safe 方向正确，回撤链独立保底） | risk_layer_orchestrator.py:787-801 | 已查无 | 读码 |
| D | 旁系：tail_risk_monitor 提供 ES（本模块无 ES——Phase 1 声明，ES 职责在旁系模块完成闭环）；var_intraday_recalc 复用同一 calculator 实例口径一致；未发现第二套 VaR 实现双承载 | var_calculator.py:29-30（Phase 声明）；var_intraday_recalc.py:325 | 已查无 | grep 全仓 VaR 计算 |
| E | 假阳性过关：数据洞期间 ≤5% NaN 静默过滤——已按裁定带 warning+计数（Fail-Closed 上限闸在）；本审无新洞 | var_calculator.py:411-427 | 已查无 | 读码 |
| E | 静默失败：无吞异常点（错误契约三类显式 raise）；数值 NaN 穿透是唯一"静默"通道（A 轴 P2） | 全文 | （已计） | — |
| E | 重复触发：纯计算无状态，幂等；时序攻击：now 可注入，无死角 | var_calculator.py:260-284 | 已查无 | — |
| A.3 | 测试审查：34 用例断言强（对拍数值+异常类型），无日期漂移依赖；缺 portfolio_value NaN 用例与 min_history 统计充分性用例 | tests/risk/test_var_calculator.py | P3 | grep portfolio_value.*nan 零命中 |

## 3 SOTA 对照（轴 F，含 URL+发布方+年份）

- **小样本分位数可靠性**：Hendricks, D. (1996) *Evaluation of Value-at-Risk Models Using Historical Data*，纽约联储（[PDF](https://www.newyorkfed.org/medialibrary/media/research/epr/96v02n1/9604hend.pd)，New York Fed，1996）——"95 尤其 99 分位数在小样本下极难准确估计"。**结论：立卡候选**（min_history 默认提到 ≥100，或对 HS 侧单独要求 n·(1−c)≥10，改造点=VaRConfig 校验+注释）。
- **√T 缩放与回测框架**：Basel 交通灯回测以 250 日 99% VaR 例外数为基准（BIS 1996 事后检验框架；日本银行工作论文 *Benchmarking of Unconditional VaR and ES Calculation*，[PDF](https://www.boj.or.jp/en/research/wps_rev/wps_2014/data/wp14e01.pdf)，Bank of Japan，2014）；实践口径≈1 年 252 日日收益为最低可靠窗（Ryan O'Connell, *VaR Historical Method*，[ryanoconnellfinance.com](https://ryanoconnellfinance.com/var-historical-method/)，2024，从业者博客=弱源仅佐证）。**结论：√T 近似对等已有（已注释）；回测验证（Kupiec/交通灯）本模块未含——立卡候选（var_backtest_store 已有落点，属 K05 邻接面）。**
- ES（97.5/99%）替代 VaR 的 Basel FRTB 趋势：本仓 tail_monitor 已产 ES，方向**对等已有**（职责分离而非缺失）。

## 4 缺陷清单（按严重级排序）

1. **[P2] portfolio_value NaN/±Inf 穿透**：现状→正数校验被 NaN 绕过。影响→NaN VaR 下游污染 position_cap/var_breach 判定（NaN 比较恒 False→分级可能全不触发=fail-open 数值通道）。爆炸半径=回撤/VaR 联动降级链单轮失效（下轮恢复）。建议修法→`math.isfinite(portfolio_value)` 校验入 InvalidVaRConfigError。验证法→NaN 输入断言 raise。
2. **[P2] min_history=30 默认对 95% HS 分位数统计薄弱**：建议默认≥100（或 HS 单独闸 n(1−c)≥10）并核对生产实际窗口；在改前先取数据画像确认实际喂入长度。验证法→不同窗口长度 VaR 稳定性对比。
3. **[P3] 三条打包**：weights 无 Σ=1/非负校验；A.3 缺 NaN portfolio_value 用例；√T 对 HS 的适用性注释已到位无需改。

## 5 挂起疑问

1. 生产实际喂入 returns 的窗口长度是多少（orchestrator min_samples_for_var 现值与 nav_history 深度）？——决定 P2-2 的实际严重度，需收口方取配置核实。
2. FHS 主链与本回退链的 VaR 口径一致性（GARCH 条件波动 vs 无条件分位数）是否有人工对齐记录？属 36 号文范围，本报告仅挂起。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学四问逐公式过（参数法/历史模拟/合成/缩放/年化）；E 轴五问逐条。
- 长尾清单：① FHS 引擎/tail_monitor/var_breach 三个邻接模块未深审（各自值得单独立卡）；② annualized_vol 只在 to_dict 暴露，消费方未见（疑似预留）；③ scipy/numpy 版本锁定未记录（运行环境锁定项：Python 3.12.8 已记，库版本未取）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 portfolio_value NaN穿透: 确认→治本(isfinite raise InvalidVaRConfigError)+实弹回归,63/63绿。
- 立卡: min_history=30对95%分位统计不足(Hendricks 1996 NY Fed)。
