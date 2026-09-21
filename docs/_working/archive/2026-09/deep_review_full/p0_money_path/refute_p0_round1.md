---
ttl: task_bound
title: P0 资金路径复算反驳报告（第 1 轮 · 8 对象）
session: st-deeprev-20260918
role: 复算反驳者（与审查者完全隔离，未读取 deep_review_full_20260918 下任何他方产出）
baseline_commit: 2fa92002c3
head_commit: 562320d091
baseline_drift: 2fa92002c3 为 HEAD 祖先；9 个目标文件自基线以来零改动（git log 基线..HEAD 对该 9 文件为空），对拍有效
date: 2026-09-18
owner: ZephyrAlpha-Owner
verification_scripts: .runtime/tmp/deepreview_refute/{v01_wilson,v02_certifier,v03_fdr,v04_neff,v05_gate,v07_dsr,c04_position,c07_vol}.py
---

# 复算反驳报告 · P0 money path 第 1 轮

方法：对 8 个 P0 数学对象，从源码提取核心公式/断言，用独立实现复算（V01 双代数形互证+教科书锚点；V02 对 `math.comb` 精确分数；V03 自写 BHY/BH 步进；V04 手工索引交集+`np.corrcoef`；V07 闭式+数值积分 ∫x·N·φ·Φ^(N−1)；C04/C07 逐场景账目追踪），构造阈值"恰上/恰下"边界反例。全部脚本在 `.runtime/tmp/deepreview_refute/`，未修改 src/tests/config 任何文件，未 commit。

## 总判定表

| 对象 | 核心公式复算 | 反例 | 判定 |
|------|-------------|------|------|
| V01 Wilson 下界 | 一致（≤1e-12，三方互证） | 1（rate∉[0,1] 复数崩溃） | 数值一致；边界反例成立 |
| V02 四闸认证器 | 一致（整数 n 尾概率精确对拍） | 0 | 一致（4 项观察） |
| V03 FDR 双实现 | 一致（70+ 组随机/并列/极端集） | 0 | 一致 |
| V04 n_eff/账本 | 一致（iid/完全相关/边界） | 1（grid_root 仓外崩溃） | 核公式一致；反例成立 |
| V05 决策闸 | 阈值语义全部按 spec 翻转 | 2（偏差 0.3 浮点误 warn；passed 字符串真值） | 一致；反例成立 |
| V07 DSR | 一致（docstring 偏差自述经数值积分独立验证为真） | 0 | 一致 |
| C04 仓位引擎 | Kelly/约束一致 | 2（veto 保留现仓/defensive_only 的账目脱节） | 反例成立（会计口径） |
| C07 VolTarget | 10 组 + 全序列对拍一致 | 1（NaN→满仓，反保守） | 一致；反例成立 |

---

## V01 Wilson 下界（pattern_win_rate_provider.py:42）

**复算方法**：独立实现 (a) Wilson 二次方程下根 `(2np+z²−z√(z²+4np(1−p)))/(2(n+z²))`；(b) centre-margin 代数形。与实现 `_wilson_lower_bound` 三方对拍。

**对拍结果**：20 组随机 (k,n)（n∈[1,500]）三方一致 ≤1e-12；LB∈[0,1] 且 ≤p 对 n=1..100×p 网格扫描零违例；LB 对 n 单调不减（p∈{0.3,0.55,0.8}，n→500）；锚点 10/20 → 0.299298008（文献 ~0.2993）；边界 n≤0→0.0、p=0→0.0、p=1→1/(1+z²/n)、自定义 z 一致。

**反例清单**：
| # | 输入 | 期望 | 实际 | 位置 |
|---|------|------|------|------|
| R1 | rate=1.2,n=5（及 -0.3/50、2.0/1 等 p(1−p)+z²/(4n)<0 组合） | 报错或钳位 | `TypeError: '>' not supported between 'complex' and 'float'`——负方差项 `**0.5` 产复数，:55 `max(0.0, complex)` 崩溃 | pattern_win_rate_provider.py:54-55 |
| R2 | rate=NaN, n=30 | None/报错（与"查无=None"契约对齐） | 静默返回 0.0（`max(0.0, nan)` 参数序决定），"无数据"被翻译为"零信任满分下界 0"——行为可辩但语义未声明 | 同 :55 |

**判定**：合法输入域 [0,1]×n≥1 内数值完全一致；R1 成立（垃圾输入崩溃，生产 hit_rate 来自 DB 无入参校验，建议钳位或 raise）。

---

## V02 四闸认证器（pattern_evidence_certifier.py:186）

**复算方法**：`binomial_ge_pvalue` 对 `math.comb` 精确和（n∈{5,10,30,100,300}×p0∈{0.3,0.5,0.55}×k 网格）；非整数 n_eff（30.5/33.33/12.25/7.5）对照 floor/ceil 真实尾概率；闸公式（effective_n/shrunk_rate/within_regime_edge）逐式重写；`bh_qvalues` 对自写 step-up 50 组；状态机逐闸构造恰上/恰下输入。

**对拍结果**：整数 n 尾概率与精确值差 ≤1e-9 全对；退化边（n=0→1.0、hits=0→1.0、hits>n→0.0、p0∈{0,1} 精确值、越界 raise）全对；**非整数 n 的广义二项和全部落在 [floor 尾, ceil 尾] 区间内且对 hits 单调不减**（未发现反保守翻车）；shrunk=(hr·n_eff+k·base)/(n_eff+k) 精确；翻转边界：n_eff=29.9→failed / 30.0→通过（严格 <30）✓；q 闸在 p=0.05944(failed)/0.04695(probation) 间翻转（q≥0.05 失败）✓；conc 严格 >0.9（=0.9 放行）✓；w_edge≤0→probation ✓；baseline/None-rate/零 n 切片 fail-closed 排除 ✓。

**观察清单（非反例）**：
1. conc 边界受 ±1ulp 浮点噪声影响：构造"恰 0.9"集中度（900×0.2 vs 400×0.05）实际得 0.8999999999999999→放行；翻转点在 1e-16 尺度抖动（模块无容差）。
2. 结构性：**单个正 edge regime 切片 → conc=1.0 → 永远 probation**；空 regime 切片 → w_edge=0 → probation。certified 需要 ≥2 个均衡正切片——单 regime 形态在机制上不可认证（与闸C 语义一致但值得 Owner 知晓）。
3. **"WilsonLB 闸"实际不存在**：状态机（:237-242）只消费 q/n_eff/w_edge/conc；wilson 与 shrunk 仅作记录字段输出。四闸实为 A=BH-FDR、B=n_eff、C=edge+集中度、D=收缩读数（只记不判）。
4. 认证器闸A 用 `bh_qvalues`（c(m)=1 纯 BH，:228-230），而 strategy_pipeline 的 `bh_filter` 用 BHY c(m)=Σ1/i——同仓两种 FDR 口径并存（各有文档背书，无对错，列为例行对齐项）。

**判定**：一致；0 反例；观察 1-4 供审查者/Owner 参考。

---

## V03 FDR 双实现对拍（bhy_fdr.py:79 / bh_fdr.py:42）

**复算方法**：自写 BHY（k=max{i: p₍ᵢ₎≤i·q/(m·c(m))}，前缀拒绝）与自写 BH step-up q 值；对拍 rejected 掩码/n_rejected/threshold 三元组。

**对拍结果**：40 组随机集（m∈{1..100}，均匀/立方偏/重并列/极值混采，q∈{0.05,0.1,0.25}，c(m) 两态）全一致（≤1e-12）；固定极值（单 0/单 1/全 0/全 1/[0,1]/0.05 边界组）全一致（全 0 → 全拒 thr=q/c(m)；全 1 → 零拒绝）；错误契约（NaN/inf/负/>1 p、q∈{0,1,1.1,-0.1}）全部 ValueError、空集→空结果 ✓；`bh_qvalues` 30 组随机/并列一致（大 p 并列 [0.9,0.9]→[0.9,0.9] 不放大）✓；`bh_filter` keep 集 == BHY 拒绝集且 passed 旗标构成前缀（2×15 组）✓；q=1 退化短路全过 vs canonical 抛错=文档声明分歧 ✓；bool/字符串 p 均拒 ✓。

**观察**：`bh_threshold` 展示字段=BH 口径 k/m·q，判定核=BHY（更紧）；经证明 passed 条目必有 p<两阈值（BHY 阈值 ⊂ BH 阈值），"p>展示阈值却 passed"不可能出现，字段自洽无误导；`np.int64` 被 bh_filter 拒（isinstance 检查）而 canonical bhy_fdr 经 np.asarray 可收——宽松度不一致，无害。

**判定**：一致；0 反例。

---

## V04 n_eff 与 N 试次账本（n_trial_ledger.py:135/:179）

**复算方法**：独立 effective_rank（手工索引交集对齐 + `np.corrcoef` + 特征值熵 + ceil 容差复刻）；TrialLedger 全路径在 tmp 注册表上跑（未触生产路径）。

**对拍结果**：5 组 iid（n≤11,T=200）impl==mine；8 条完全相同序列→1；完全反相关→1；1e-12 噪声近似同序列→1（round-9 防虚增守卫有效）；真不相交索引→boundary n=2 ✓；common_T=59/60 边界 ✓；n=1→(1,boundary) ✓；账本：缺失 fail-closed、骨架自举、record_run 幂等、缺 n_trials→0、manual_population 只入 known_floor、n_trials_effective 非法型→None、CAS 幂等重同步（grid 1999+50 幂等追加、screen 读数 5→12 传播）全对。

**反例清单**：
| # | 输入 | 期望 | 实际 | 位置 |
|---|------|------|------|------|
| R1 | `sync_screen_counts(grid_root=<仓外 tmp>)`（docstring 明文邀请"测试注入 tmp_path"） | 正常发现/登记 grid 批次 | 未捕获 `ValueError: ... is not in the subpath of 'D:\ZephyrAlpha'`——`summary_path.relative_to(REPO_ROOT)` 在 try/except（仅护 json 解析，:397-403）之外。pytest tmp_path 必在仓外 ⇒ 网格发现路径的测试必崩 | n_trial_ledger.py:416 |
| R2a | `compute_effective_rank({})` | TrialLedgerError（ERROR_CONTRACT 口径） | 裸 `ValueError: No objects to concatenate`（pandas 直抛；方向仍 fail-closed，仅类型契约偏差） | :156 |
| R2b | 账本 YAML 畸形 | TrialLedgerError | yaml `ParserError` 直抛（同上，类型契约偏差；仍是 fail-closed） | :204 |
| R3 | 全常值收益列 ×2 | —（行为注记） | pandas corr 对角=NaN→fillna(0)→全零矩阵→total=0→返回 1 且 boundary 未置位：零方差序列把 N_eff 静默压到 1（DSR 侧同输入判"不可判定"，两侧姿态不一） | :166-170 |

**判定**：核心估计器一致；R1 反例成立（建议把 relative_to 移入容错或对仓外根退化处理）；R2 为契约类型偏差。

---

## V05 决策闸（decision_gate.py:539）

**复算方法**：对每个阈值构造"恰在阈上/阈下"输入对（IS>0.5、WFA>0.5、灾难>0.5、OOS≥0.7、收缩>0.30、DSR 三线 0.95/0.5、偏差>0.3/0.5），逐一验证翻转方向与缺字段行为。

**对拍结果**：IS 0.5 拒/0.5+1e-12 过、NaN sharpe 优雅判负、None 抛错 ✓；空敏感性 dict 空 vacuous 通过、空扫描点=不稳定 ✓；WFA 2/4=0.5 拒（严格>）、3/4 过、回撤 0.5 不触发/0.5+ε 触发、负回撤取 abs 触发、缺字段计未过、零窗口拒、非 dict 窗口抛错 ✓；OOS 比率 0.7 恰过（≥）、0.6999999 拒、is≤0 拒、参数未锁拒、DSR=0.95 过/0.9499999 review/0.5 review/0.4999 overfitting/None unavailable/NaN 落 review 带（fail-closed 拒）✓；dsr_threshold=None 退回旧行为 ✓；evaluate 跳级防护 ✓；Phase5 收缩恰 0.30 不降格/0.31 降格、未知 regime/未登记策略类型降格、checker 启用缺上下文抛错 ✓；偏差退役/告警严格 > 边界（0.5 恰到 warn 不 retire）✓。

**反例清单**：
| # | 输入 | 期望 | 实际 | 位置 |
|---|------|------|------|------|
| R1 | `monitor_backtest_live_deviation(1.0, 0.7)` | deviation 恰=30%，spec "偏差>30%告警" ⇒ action="ok" | `1.0-0.7=0.30000000000000004` → `>0.3` 成立 → "warn"。恰在阈值的常见组合被浮点推过线（0.5 边界恰好可整除，无误） | decision_gate.py:1205-1212 |
| R2 | WFA 窗口 `{"passed": "0"}` | 非法类型报错或按未通过 | `bool("0")=True` 计为通过窗口——任意真值字符串/对象=通过（类型洞） | decision_gate.py:681 |

**观察**：plateau 相对变化恰 0.2 边界同样受浮点影响（(1.0−0.8)/1.0=0.1999…8 被视为 <0.2 → 稳定）；用精确可表示对 (5.0,4.0) 时严格 < 判非稳定 ✓——行为符合 spec，仅边界精度 ±1ulp。

**判定**：阈值语义与缺字段 fail-closed 全部一致；R1、R2 反例成立（R2 建议对 passed 字段做类型校验）。

---

## V07 DSR（deflated_sharpe_calculator.py:327）

**复算方法**：按 Bailey & López de Prado 2014 独立重推 `V[SR]=(1−γ·SR+(κ_P−1)/4·SR²)/(T−1)`（κ_P=超额+3）、E[maxZ] 闭式 `(1−γ_e)Φ⁻¹(1−1/N)+γ_eΦ⁻¹(1−1/(Ne))`、DSR=Φ(SR/√V−E[maxZ])；另用 40 万格梯形数值积分 `∫x·N·φ(x)·Φ(x)^{N−1}dx` 独立验证闭式近似质量。

**对拍结果**：5 组参数集 (SR,N,T,γ,κ) DSR 与独立实现差 ≤1e-12（含 N=4497 大折减与 N=1 无修正）；V[SR] iid 正态锚点 (1+SR²/2)/(T−1) 精确成立（SR∈{0,0.1,0.5,2}）；E[max] 单调不减（N=2..2000）且 N≤1→0 ✓；**docstring 自述的闭式对精确积分偏差（N=2 −0.0444 / 3 +0.0065 / 10 +0.0358 / 50 +0.0272 / 4497 +0.0103）经独立数值积分逐一复现到第 4 位小数——自述诚实**；退化态全部 fail-closed：T=1→V=0、零方差收益、互斥矩（γ=3,κ=0,SR=1.0 → V<0）、T=3<矩下限 4 → 全部 degenerate=True + dsr=0 + 不判显著 ✓；空/T<3/num_trials=0 抛 SimulationError ✓；DSR∈[0,1]、对 N 非增、is_significant 谓词自洽 ✓。

**判定**：一致；0 反例。该模块是 8 对象中唯一"文档声明可被独立验证逐字兑现"的对象。

---

## C04 仓位引擎（position_sizing_engine.py:379）

**复算方法**：Kelly f*=(bp−(1−p))/b 逐点重算；按 veto/C3/C7/C8/C12/C2/POS-006/007/017 逐路径构造场景，追踪每条路径的 total_exposure/cash_reserve/positions 并核对账目恒等式（cash==nav×(1−exposure)，exposure 为比例口径）。

**对拍结果**：Kelly 公式含截 0 与全部报错路径（p∈{0,1,-0.2,1.5}、b∈{0,-1}）精确 ✓；默认单票上限 0.05 截断 half-Kelly 0.10 → basis=single_name_cap ✓；strategy_intent 绑定（target≤half-Kelly）✓；10 标的降级等权 10×0.04=0.40、现金 0.60 ✓；C2 缩放、gross_leverage=2.0 不放大（min(2.0, 0.4)）✓；日历强清、f*≤0 不下注 ✓；nav/price/负 target/空表报错 ✓；C8 软折扣可达性用例（w=0.001 → 0.0008, qty=80）✓；恒等式在比例空间全部成立 ✓。

**反例清单**：
| # | 输入 | 期望 | 实际 | 位置 |
|---|------|------|------|------|
| R1 | 标的 V：现仓 20000 股（0.2 nav）+ C6 参与率 0.2>0.15 否决（有现仓→保留现仓）；另加正常 Kelly 标的 N（0.05） | 计划账目自洽：exposure 应含保留的 V | plan.total_exposure=0.05、cash=950000，但 plan.positions 含 V@0.2——**持仓权重和 0.25 ≠ exposure 0.05**；执行计划后真实未投资=0.75 nav，plan 报 0.95。否决"保留现仓"路径的权重（veto 返回 weight=0.0）从未进入 total_weight | position_sizing_engine.py:749/:763 + :836 |
| R2 | defensive_only + 新开 Kelly 仓位（默认帽 0.05） | exposure 反映执行后敞口 | target_qty 强制为 current=0，但 positions 仍带 target_weight=0.05 且 total_weight 不同步 → exposure=0.05 而 qty=0 | :889-910 + :836 |
| R3 | 任一成功计划 | "exposure+cash=总资金"（币值口径） | total_exposure=比例(0.10)、cash_reserve=币值(900000)——裸相加差 99999.9；恒等式仅在 `cash==nav×(1−exposure)` 比例空间成立，字段单位混用无文档警示 | :836-845 |
| R4 | p=0.6,b=1（Kelly w=0.09999999999999998） | qty=10000 | `int()` 截断 → qty=9999、target_weight=0.09999（浮点噪声 0.6−0.4=0.1999…98 在整数股边界损失 1 股；良性但真实） | :542 |

**观察**：C11 冲击成本闸（0.1√p>0.5% ⇒ 参与率 p≤0.25%）比 C6（15%）严 60 倍——正常 Kelly 权重+常见 ADV 几乎必被 C11 否决"保留现仓"（连锁放大 R1 的触发面）；C8 软折扣仅当 Kelly 权重极小（<0.25%）且现仓 exit_days∈(1,3] 同时成立才可达。为设计值域张力，非缺陷。

**判定**：Kelly 与约束级联数值一致；**R1/R2 反例成立（P0 资金路径上 plan 级账目与执行结果脱节，建议：保留现仓/defensive_only 路径将实际权重计入 total_weight 或在 plan 中单列 kept_exposure）**。

---

## C07 VolTarget（vol_target_allocator.py:32）

**复算方法**：独立重写 rolling std(ddof=0)×√244 → k=target/realized（0→NaN）→ clip → ewm(span=5,adjust=False) → fillna(min)；10 组 (E,σ) 对 kelly_full_weight 逐点重算；NaN/0/负/极端 σ 行为探针。

**对拍结果**：无缺口随机路径全序列与独立实现差 8.9e-16（两路径）✓；前 window−1 段=min_weight（"窗口不足=不满仓"）✓；常值收益→realized=0→k=NaN→min ✓；σ 微小→clip 1.0、σ_日=0.05→年化 0.781→k=0.1921（域内不 clip，与手算一致）✓；参数校验 5 例（window<2、target_vol∈(0,5] 外、max<min）全抛 ValueError ✓；NaN 收益段→min 填充、数据到达后正常计算 ✓；NaN 跨缺口的 EMA 语义=委托 pandas ewm(ignore_na=False) 缺口加权（本复算的简化 carry 递归跨缺口差 4.6e-2，确认为参考实现自身简化，模块侧为 pandas 规范语义）；kelly_full_weight 10 组全对（≤1e-12，含 σ=0/负/1e-8、E=0/负）✓；带宽容许 (min=1,max=2) ✓。

**反例清单**：
| # | 输入 | 期望 | 实际 | 位置 |
|---|------|------|------|------|
| R1 | `kelly_full_weight(0.10, sigma=float("nan"))`（或 E=NaN、E=+inf） | NaN 不可测量→min_weight（与 vol_target 侧"不可测量=不满仓"姿态一致）或报错 | `sigma <= 0` 对 NaN 为 False → kelly=NaN → `min(1.0, nan)` 参数序返回 1.0 → `max(0.0, 1.0)=1.0`——**NaN 输入得满仓**，同模块两侧对 NaN 姿态相反（vol_target NaN→min 保守） | vol_target_allocator.py:93-96 |

**观察**：min_weight 未校验非负，min_weight=-0.5 时 K 可为负（空头敞口），"K∈[min,max] 恒成立"形式上满足但风险语义未防；sigma=+inf→0.0 保守正确。

**判定**：数值一致；R1 反例成立（建议 `math.isnan` 前置或 `not (sigma > 0)` 判式——后者与 V07 `sharpe_variance_is_degenerate` 的同型范式一致）。

---

## 复算者总结

1. **全部 8 对象的核心数学公式复算通过**（Wilson、二项尾、BH/BHY、特征值熵 n_eff、DSR 全链、Kelly、Vol-target）：未发现任何"公式写错"级缺陷。V07 的 docstring 数值自述经独立数值积分验证为真，可作为该模块可信度锚点。
2. **成立的反例集中在边界与路径语义**，按资金路径风险排序：C04-R1/R2（plan 账目与执行脱节——exposure 低报/cash 高报，直接触及"账目恒等式"审查目标）＞ C07-R1（NaN→满仓，反保守输入处理）＞ V05-R2（passed 类型洞）＞ V05-R1/V02-obs1（浮点恰界翻转）＞ V04-R1（docstring 邀请的用法必崩）＞ V01-R1（垃圾输入崩溃）。
3. 与审查视角互补的提示：V02 的"WilsonLB 闸"在代码中是记录字段而非判定闸（闸序=BH/n_eff/edge+conc，shrunk 亦只记录）；认证器"certified"在单 regime 切片结构下不可达；认证器(BH c=1) 与管线(BHY c=Σ1/i) 两种 FDR 口径并存。
4. 复算脚本存于 `.runtime/tmp/deepreview_refute/`（8 文件，可复跑），未修改任何 src/tests/config 文件，未做任何 commit。
