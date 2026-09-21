---
ttl: task_bound
title: 深度审查作业簿——Regime元分配器（W03）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Regime 元分配器 RegimeMetaAllocator（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代，两 commit 间本文件无变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/regime_meta_allocator.py:199`
- 生产调用方: **真实接线**——allocation_orchestrator.py:790,1024-1026（C01 日批）；allocation_inputs.py:334-336（compute_performance_score 复用）
- 测试文件: tests/pf_alloc/test_regime_meta_allocator.py（67 测试，随批实跑通过）
- 备注: 他会话在途施工=未跟踪新件 `src/zephyr/pf_alloc/crisis_gate.py`（WO-2a，危机判读，复用 load_regime_input）——**漂移风险**见 §5

## 1 对象快照

- 范围：`regime_meta_allocator.py` 全 795 行：global_shrinkage（ConfidenceSignal 四档 × RiskSignal clamp）+ Base×PerformanceScore 归一 + floor/cap water-filling 裁剪（#206 Σ=1 兜底）+ 冷启动校验 + D1 敏感性网格。
- 排除项：`compute_performance_score` 的 Sortino/Sharpe 统计口径（§3.2.2 有四件套防护且 67 测试覆盖密集）只做 NaN 专项与 gap 监控复核。
- 测试覆盖概况：67 测试全绿，含 crisis floor 可达性双锚定（源码 line 103-109 注明）；**NaN 概率/NaN risk/NaN perf 三条边界无测试**。
- 材料包缺项声明：运行时证据包未取（以编排器代码审计代偿）；数据画像未取（上游 allocation_inputs 侧防护经代码审计判定）；Python 3.12.8 + numpy 已锁定。
- checklist 前置过检：#4（双份承载）专项裁定见 D 轴；#6（断供→fail-closed vs 恒 0）上游已防；#8 不命中（本件有生产调用方）；其余查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | **NaN 概率向量 → ConfidenceSignal=1.0 满确信**：`NaN < threshold` 恒 False（line 455-458），循环走完落 sentinel 1.00。实测 probs 首位 NaN → conf=1.0。方向=不安全侧（NaN 反而满部署） | regime_meta_allocator.py:452-458 | P1 | allocate(probs=[nan,.5,...], risk_base=0.5) → shrinkage_detail.confidence_signal==1.0 |
| A 深度 | **NaN risk_base → RiskSignal=1.0 无节流**：`min(RISK_SIGNAL_MAX, nan)` Python 语义=1.0（line 475）。实测 shrinkage=0.85（本应更低） | line 471-475 | P1 | risk_base=float("nan") → risk_signal==1.0 |
| A 深度 | **NaN PerformanceScore → 静默等权**：NaN 进 water-filling → scale=NaN → 全员 NaN → 最终裁剪全部钳到 cap（line 572-574）→ Σ≠1 → #206 兜底按比例归一=等权（line 576-586），仅一条误导性 warning（"破产兜底"）。实测 {x:nan,y:0.8} → allocations {x:.5,y:.5} | line 511-515,532-586 | P1 | 实测脚本（本报告复算通过） |
| A 深度 | **混合 NaN 收益 → NaN Sortino/Score**：np.mean 传播 NaN（line 626），映射段产出 NaN（line 666-674）。实测 [-0.01]×20+[0.005]×30+NaN×10 → (nan,nan,nan)。全 NaN/无下行日情形被 DOWNSIDE_MIN_OBSERVATIONS 门槛偶然拦住（line 637-643）——护栏存在但非针对性 | line 622-653,666-674 | P2 | 上述收益序列调 compute_performance_score |
| A 深度 | **perf_scores 值域 [0.5,1.5] 不校验**：docstring 声明"已由上游映射"（line 273-275），allocate 原样吃（line 296）——越界值（如 10.0）直接主导分配；编排器 screen_panel 只拦 ≤0/非有限，不拦越界（allocation_orchestrator.py:638-640） | line 273-275,296 | P2 | allocate 传 perf=10.0 观察独大 |
| A 深度 | **strategy_sample_days=None 则跳过冷启动强制中性**：line 366-368 直接返回原值——可选参数承载校验开关，调用方漏传即免检（docstring 有声明，属"软校验"） | line 305-307,366-368 | P2 | 不传 sample_days + perf=1.5 + days<30 不被拉回 1.0 |
| A 深度(边界·查无) | Σ=1 硬不变量兜底（#206）、N=2 cap 放宽（实测触发 0.95）、除零防（free_sids 非空论证 line 550-556）、floor/cap 钳制、CRISIS floor 0.05 当前参数域不可达已在码内自洽（line 101-109,414-417）——四问其余各项**查无缺陷** | line 492-586 | — | 实测 N=2 触发无解兜底 |
| A.3 测试 | 67 测试密集覆盖主路径+参数域可达性；NaN 三路径（P1×3）零测试 | tests/pf_alloc/test_regime_meta_allocator.py | P3 | grep 测试文件无 nan 用例 |
| B 上游 | 生产上游已被编排器侧清洗：概率向量非有限/≤0→0、全零→平坦（allocation_inputs.py:411-423）；RiskSignal 三档口径 NaN/0→neutral_fail_closed=1.0 且概率平坦→conf 落最低档 0.30（line 426-455）；perf 非有限→dead member 剔除（allocation_orchestrator.py:613-640）。**直接 API 调用方绕过全部清洗**——A 轴 P1×3 是 API 契约层缺口（防御纵深缺失） | allocation_inputs.py:411-455；allocation_orchestrator.py:613-640 | P2（契约） | 从本模块直接 allocate（不经编排器）复现 P1×3 |
| B 上游(契约) | probs 向量 Σ≈1 不校验（只取 max）：未归一向量（如 [0.6,0.6]）使 max(P) 虚高→跳档满部署 | line 441-458 | P3 | 传 [0.6,0.6,0,...] 观察 conf |
| C 下游 | 输出经 verify_allocation_invariants 硬闸（Σ=1/越界/负值即抛，allocation_orchestrator.py:655-680）→ BudgetChangeHandler（防抖+三级升级+显式 0 剔除，line 810-851）→ StrategyBook。**静默吞没点：查无**（下游链显式失败）。爆炸半径=全 sleeve（global_shrinkage 全局缩放总暴露） | allocation_orchestrator.py:655-680,803-851 | — | 构造 Σ≠1 输出 → 硬闸抛 AllocationInputError |
| D 旁系 | **双承载嫌疑裁定：无双承载**。allocation_inputs.confidence_signal_from_max_prob（line 401-408）与 W03 CONFIDENCE_THRESHOLDS 的关系=**同源导入**（line 403 `from ...regime_meta_allocator import CONFIDENCE_THRESHOLDS`），常量单承载，漂移不可能发生。预算带（shrinkage 带 [0.09,1.00]，CRISIS 前瞻 0.05）单承载于本件；C01 编排器无第二份预算带（verify_allocation_invariants 只验不产）。注：协调单措辞"六段预算带"在对象与蓝图中**均未检出**，实际为 conf 四档 × risk clamp 的乘积带——见 §5 | allocation_inputs.py:401-408 | — | 读 allocation_inputs.py:401-408 导入链 |
| D 旁系(兄弟) | 两处 Kelly：vol_target_allocator.py:74-96（kelly_full_weight=E(R)/σ²×0.5）vs pf_core/core/portfolio_optimizer.py:388-404（μ/diag_var×0.5）——公式口径初判一致（半 Kelly 同式），均非本件成员；multi_strategy_capital_allocator（MOD-PA-003"MaxDD>15% 全线×50%"组合级）与 W07（逐策略）分层声明在案（maxdd_limit_allocator.py:30-31），但 MOD-PA-003 在 C01 链同样未接线——**整域多分配器并存、仅 MOD-PA-007 接线**，登记合并/退役评估建议（挖矿联动） | vol_target_allocator.py:95；portfolio_optimizer.py:404 | P3 | grep MultiStrategyCapitalAllocator src/ → 编排器无引用 |
| E 对抗 | allocate 无外部副作用、幂等（created_at 仅构造默认值）；D1 网格经克隆 probe 不污染实例态（line 746-758）；线程不安全（无锁）但生产为单线程日批——**查无静默失败/重复触发/时序死角**（NaN 类静默已单列 A 轴） | line 697-794 | — | 同参两次 allocate 比对 |
| E 对抗(时戳) | BudgetAllocation.created_at 用 naive `datetime.now`（line 162）无 tzinfo——落库/跨时区比对有时歧义（宪法 §RULE-SCHEMA-TZ 邻接面） | line 161-162 | P3 | `BudgetAllocation().created_at.tzinfo is None` |

## 3 SOTA 对照

- regime 做 risk-throttle（只减不增）vs alpha-timing：代码头注已引 Morwane/multi-strategy-alpha-book（Sharpe +1.43 vs +0.87，line 41-43）及 quantt.co.uk 2026-04、BestFolio 2026-04、1uptick 2026-06（line 84,450）——**代码内引证与本审查战役检索预算（2 次，已耗于 W02/W05）均未独立核验，如实记"受限"**。
- 结论：机制属业界常规（regime 条件风险预算/floor-cap 约束组合构建，与 CPPI 型 floor 思路同族）；**对等已有**；floor/cap+全局 shrinkage 两层结构无需立卡改造。Black-Litterman 为"观点先验后验"不同族，不适用对照。

## 4 缺陷清单

1. **[P1] NaN 概率→满确信（API 层）**：现状=NaN 直达 sentinel 1.00（实测）。影响：直接消费方（编排器之外的装配批/回放工具）NaN 时满部署；生产主链已被 allocation_inputs 清洗兜住（爆炸半径有限）。建议：`_compute_confidence_signal` 入口 `np.max` 前做 isfinite 校验，非有限→抛 AllocationError（fail-closed 对齐头注 INVARIANTS line 8）。验证法：§2 实测一行复现。
2. **[P1] NaN risk→无节流（API 层）**：同上修法（`float(params.get(...))` 后 isfinite 校验，非法即抛或落 RISK_SIGNAL_MIN 保守侧）。验证法：§2 实测。
3. **[P1] NaN perf→静默等权（API 层）**：现状=NaN 污染 water-filling 全局，#206 兜底伪装成"破产兜底"等权且告警文案误导。建议：allocate 入口对 perf_scores 逐值 isfinite 校验抛 AllocationError；#206 兜底告警文案补"疑似 NaN 输入"提示。验证法：§2 实测。
4. **[P2] compute_performance_score 混合 NaN→NaN 分数**：建议入口 `np.isfinite(returns_arr).all()` 校验或 nan 过滤并记数告警。验证法：§2 实测 (nan,nan,nan)。
5. **[P2] perf_scores 值域不校验**：建议 ∈[0.5,1.5] 越界告警或钳制（与上游映射契约联动）。验证法：传 10.0 观察。
6. **[P2] 冷启动校验可被漏参绕过**：建议 strategy_sample_days 缺失时按"未知"处理并告警（而非静默免检）。验证法：§2 实测。
7. **[P3] API 契约层小结**：probs Σ≈1、thresholds 表有序性（line 455-458 依赖升序，`__init__` line 245-247 不验）、created_at naive——三项补校验/补 tz。
8. **[P3] 旁系整合**：MOD-PA-003/两处 Kelly 与本域未接线件的合并/退役评估（转挖矿子节点）。

## 5 挂起疑问

1. **他会话在途漂移风险**：未跟踪件 `src/zephyr/pf_alloc/crisis_gate.py`（WO-2a 危机判读，2026-09-18）建立 normal/warning/crisis 双档口径（crisis=dominant==r10 硬拦；warning=p_r10≥θ），而本件 is_crisis 入参现由 allocation_inputs.py:523（dominant==r10）单一供给——crisis_gate 接线后**"危机判定"将有两处口径**（本件 is_crisis 布尔 vs crisis_gate 三态），须裁决主从（建议：is_crisis 改由 crisis_gate.resolve_crisis_state 供给，避免 #4 双承载）。本报告按工作区现状审，crisis_gate.py 本体不在 7 对象清单、未审。
2. 协调单"W03=六段预算带源头"与实物不符（对象/蓝图均无"六段"表述；实为 conf 四档×risk clamp 乘积带）——请收口方与战役台账核对是否指别处（如 environment_switch 六段态）。
3. 代码内 4 处外部实证引证（Morwane/quantt/BestFolio/1uptick）URL 均未给全，无法核真——建议施工批补锚点或降格为"经验值"。

## 6 完备性自评

- 六轴全查：A（四问+边界实测×3 组 NaN 复算）/B（含上游清洗链逐条）/C（下游硬闸+吞没点排查）/D（双承载专项裁定+两处 Kelly+MOD-PA-003 口径）/E 全查；F 受限已记。
- 长尾：water-filling 在 N>25 策略面、极端 base 分布下 5 轮迭代的收敛性未做穷举（#206 兜底存在，属可接受下界）；D1 网格 verdict 阈值 0.30 的标定依据未追（34 号文档侧）；crisis_gate.py 本体审查归属他会话/后续批次。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
