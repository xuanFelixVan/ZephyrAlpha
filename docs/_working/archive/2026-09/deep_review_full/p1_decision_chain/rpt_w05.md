---
ttl: task_bound
title: 深度审查作业簿——风险预算分配（W05）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：风险预算分配器 risk_budget_allocator（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 算法
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/risk_budget_allocator.py:29`（predicted_var :69 / predicted_cvar :79）
- 生产调用方: `risk_budget_allocate` **零调用方**；`predicted_var` 有一个域内消费方 sector_distribution_comparator.py:30；`predicted_cvar` 零调用方
- 测试文件: tests/pf_alloc/test_risk_budget_allocator.py（9 测试，随批实跑通过）
- 备注: 头注 STABILITY=experimental 标注诚实；头注宣称消费方"TDM UP-3/策略工厂 E8"均查无

## 1 对象快照

- 范围：`risk_budget_allocator.py` 全 96 行：三模式权重（inverse_var/risk_parity/sharpe_weight）+ 滚动历史分位 VaR/CVaR。纯函数无 IO。
- 排除项：sector_distribution_comparator 对 predicted_var 的下游用法（属 B 序列对象，本报告只登记挂接事实）。
- 测试覆盖概况：9 测试全绿；**无 NaN、无负值 VaR（符号口径）、无 risk_parity≡inverse_var 等价性测试**。
- 材料包缺项声明：运行时证据包与数据画像未取；Python 3.12.8 + numpy/pandas 已锁定。
- checklist 前置过检：#7（量纲/口径——VaR 符号口径）命中；#4 变体（CVaR 双实现漂移，与 W06）命中；#8（孤儿）命中；其余查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | **"risk_parity" 模式与 inverse_var 逐位相同**：两分支代码完全一致（`raw=1/vars; raw/=sum`，line 49-54），实测三资产输出 dict 相等。docstring 宣称"risk_parity=等风险贡献近似"——真 ERC 需解 RC_i 相等（迭代求解），1/σ 归一只是 naive 近似且**连近似差异都没有**（模式开关是无效开关） | risk_budget_allocator.py:49-54 | P1 | `risk_budget_allocate(d, mode="inverse_var")==risk_budget_allocate(d, mode="risk_parity")` → True |
| A 深度 | **模块内 VaR 符号口径互斥**：`risk_budget_allocate` 要求正值 VaR（line 37 docstring），而同模块 `predicted_var` 返回收益 5% 分位=负值（line 74-76）。若直连喂入，`max(var,1e-8)` 把全部负值钳到 1e-8 → **静默等权**。实测 {-0.02,-0.05} → {0.5,0.5} | line 37,47,69-76 | P1 | 上述输入实测；`predicted_var(负收益序列)` 观察负值 |
| A 深度 | **NaN 直通**：NaN var → max(nan,1e-8)=nan → 权重全 NaN 无告警（line 47,50-51）；NaN er → softmax 全 NaN。实测 {'A':nan,'B':.05} → {A:nan,B:nan} | line 46-62 | P2 | 上述输入实测 |
| A 深度 | **近零 VaR → 全额集中**：1e-8 钳制使 inv=1e8 → 该标的权重≈1（line 47,50-51）。极端低风险资产吸走全部预算，无分散下限 | line 47 | P2 | var=0.0 与 0.05 两资产 → 权重≈{1.0,~0} |
| A 深度 | **头注不变量与实现矛盾**：头注"风险度量=预测分布的 VaR/CVaR（非历史回溯）/预测分布由车道 E 分位数回归产出"（line 7-8），实现=滚动历史分位（line 74-76,84-86），无任何分位数回归。文档 vs 代码漂移（同一矛盾复制到 W06 头注） | line 7-8 vs 69-96 | P2 | 对照读 |
| A 深度(边界·查无) | 空 var_estimates/sharpe 缺 er 拒收（line 41-44）；未知 mode 拒收（line 63-64）；softmax 减 max 数值稳定（line 61）——除 NaN/符号外边界**查无** | line 41-64 | — | 传参实测 |
| A.3 测试 | 9 测试只盖主路径；P1×2/P2×2 全部无测试 | tests/.../test_risk_budget_allocator.py | P3 | 测试文件通读 |
| B 上游 | var/er 估计的提供方未指定（UP-3 车道 E 未落地）；NaN/符号契约缺失即 P1-2 成因；checklist #6："断供恒 0 vs 报错"——本件对空输入报错（对），对 NaN 恒 NaN（漏） | 全文件 | P2 | — |
| C 下游 | `risk_budget_allocate`/`predicted_cvar` 零消费方；`predicted_var` → sector_distribution_comparator.py:30（唯一活链，符号口径在该消费方处是否取负需该对象审查确认——登记）。爆炸半径当前小 | sector_distribution_comparator.py:30 | — | grep 调用方 |
| D 旁系 | **CVaR 双实现且已漂移**：W05.predicted_cvar 窗口切片 `iloc[i-window+1:i+1]`（line 92，window 条）vs W06 内联 `r[max(0,i-window):i+1]`（line 61，**window+1 条**）——同概念两处算、结果不同，checklist #4 实锤 | risk_budget_allocator.py:92 vs tail_hedge_signal.py:61 | P2 | 两函数同输入对比 warmup 后首行 |
| D 旁系(兄弟) | Kelly 双实现（vol_target_allocator.py:74-96 / pf_core portfolio_optimizer.py:388-404）与本件无口径交叉（不同层）；登记于 W03 报告 | — | — | — |
| E 对抗 | 纯函数幂等、无副作用、无时序（查无）；round 6 位致 Σ=1±1e-6 与头注"sum=1.0"硬不变量微漂（line 66 vs 头注 line 7） | line 66 | P3 | 极端权重和断言 !=1.0 |

## 3 SOTA 对照

1. **立卡候选（接线前必修名实）**：naive risk parity（反波动率/反风险加权）与真等风险贡献（ERC）是文献明确区分的两法；真 ERC 需迭代解。引证：Quantpedia, *Risk Parity Asset Allocation*（三种方法：Naive/ERC/Max Diversification）, https://quantpedia.com/risk-parity-asset-allocation/ ；QuantDare, *Risk parity vs. inverse volatility*, https://quantdare.com/risk-parity-versus-inverse-volatility/ ；*Portfolio Optimization* book §6.5 Risk-Based Portfolios, https://portfoliooptimizationbook.com/book/6.5-risk-based-portfolios.html 。适配点：若 UP-3 转正，risk_parity 模式改真 ERC（cyclical coordinate descent）或改名 inverse_var_proxy。
2. 其余两模式（inverse_var/sharpe softmax）为常规启发式，**对等已有**。

## 4 缺陷清单

1. **[P1] risk_parity ≡ inverse_var**：现状=模式开关无效。影响：语义欺骗——调用方以为用了 ERC 近似，实际拿到的与反 VaR 完全一样；后续调参/归因全部建立在假区分上。建议：实现真 ERC 或删模式并在 docstring 声明等价。验证法：§2 实测相等断言。
2. **[P1] VaR 符号口径互斥**：现状=本模块两个函数的输出/输入符号约定相反，直连即静默等权（实测）。影响：接线时必踩；sector_distribution_comparator 挂 predicted_var 的活链需自查。建议：统一约定（建议风险幅度取正），predicted_var 输出取负或 allocate 内显式处理负值并告警。验证法：§2 实测。
3. **[P2] NaN 直通无校验**：建议入口 isfinite 校验抛 ValueError（对齐 ERROR_CONTRACT line 12）。验证法：§2 实测。
4. **[P2] 近零 VaR 集中**：建议权重上限或最小分散约束。验证法：§2 实测。
5. **[P2] 头注"分位数回归/非历史回溯"与实现矛盾**：建议头注改为"当前=历史模拟法实现，车道 E 分位数回归为升级路线"。验证法：对照读。
6. **[P2] CVaR 双实现漂移（与 W06 共享）**：建议收敛为单一 CVaR 工具函数（W06 报告同步登记）。验证法：两函数对拍。
7. **[P3] round 破坏 Σ=1.0 硬不变量/object dtype None 序列/O(n·window) 循环**：随接线批清理。

## 5 挂起疑问

- sector_distribution_comparator 消费 predicted_var 后的符号处理方向未审（B 序列对象）——若该处直接把负分位当幅度用，将复现 P1-2 的镜像错误，请 B 序列审查者专项核对。

## 6 完备性自评

- 六轴全查：A/B/C/D/E 全查；F 已做（SOTA 两条带 URL）。
- 长尾：er_estimates 与 var_estimates 键集不一致时的静默交集行为（未在 var 集中的 er 键被忽略）——低危挂起；UP-3 车道 E 落地后需复审预测分布口径。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
