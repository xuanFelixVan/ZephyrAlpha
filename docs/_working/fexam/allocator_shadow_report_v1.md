---
campaign: matrix-20261006
lane: E-exam
ttl: task_bound
---

# 批4 分配器影子考报告（v1，机生）

- 生成：2026-10-06 02:28:17.133165+00:00｜同窗=批2｜合成列=indicator_ch_backed_fallback(n=215)——批1因子0可考时的prereg回退
- 简化实现声明：五套=权重变换向量化和的简化实现（非 pf_alloc 逐行复用）；MOD锚：RK-08=risk/core/risk_budget、PA-015=regime_bma_weighting、SIG-131=signal_weight_adjuster；逐行复用属 M 级施工另行登记

| 分配器 | IS Sharpe | OOS Sharpe | OOS MaxDD | OOS 收益 | 判定 |
|--------|-----------|------------|-----------|----------|------|
| ALC-THREELAYER-001 | -0.88 | 0.52 | -22.39% | 8.18% | measured |
| ALC-EQUAL-001 | -0.87 | -0.22 | -15.89% | -3.97% | measured |
| ALC-RK08-001 | -0.85 | 0.36 | -27.19% | 5.77% | measured |
| ALC-PA015-001 | -0.84 | 0.32 | -25.89% | 4.50% | measured |
| ALC-SIG131-001 | -0.87 | -0.22 | -15.89% | -3.97% | measured |

## 证据量（champion vs challengers，只报证据不判终胜负）

- ALC-THREELAYER-001 vs ALC-EQUAL-001: n=2122 年化差=1.30% t=0.48
- ALC-THREELAYER-001 vs ALC-RK08-001: n=2122 年化差=0.93% t=0.46
- ALC-THREELAYER-001 vs ALC-PA015-001: n=2122 年化差=0.62% t=0.35
- ALC-THREELAYER-001 vs ALC-SIG131-001: n=2122 年化差=1.30% t=0.48

> 只报当前证据量不判终胜负（MOD-PF-008 序贯统计口径）
