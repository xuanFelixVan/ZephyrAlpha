---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：证据不足，保守处理。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 3 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 恐慌反弹 sim/paper 前哨建图（E7 模拟盘前哨首例）

> 策略工厂 E7 模拟盘前哨首个实操策略：恐慌反弹（CAND-e3da6fa71af1）。
> **三窗口全绿**：IS 2020-2023 Sharpe +1.15 / OOS 2024-2026 +0.83 / S3 2016-2019 +0.98。
> 本文档定义 sim/paper 前哨的完整配置与晋级/退回标准。

## 一、策略身份（出生证+身份证）

| 字段 | 值 |
|---|---|
| strategy_id | CAND-e3da6fa71af1 |
| 类型 | factor（index timing，非选股） |
| 标的 | 000852 中证1000 指数收益模拟 |
| 出生渠道 | 车道 A（社区策略翻译：2022年度精选策略/57 别人恐惧我贪婪3） |
| 出生批次 | SCR-C4-20260913-014220（IS）+ SCR-C4-OOS2-20260913（OOS） |
| blueprint | tdm-upgrade-blueprint.md UP-2 |

## 二、三窗口成绩单

| 窗口 | Sharpe | 最大回撤 | 判定 |
|---|---|---|---|
| IS 2020-2023 | +1.15 | -6.1% | ✅ |
| OOS 2024-2026 | +0.83 | -7.8% | ✅ 年衰减 11% |
| S3 2016-2019 | +0.98 | -5.9% | ✅ |

## 三、sim/paper 前哨配置

| 参数 | 值 | 说明 |
|---|---|---|
| 前哨期 | ≥20 交易日 | 最短模拟盘观察期 |
| 仓位系数 | UP-1 波动率目标化 K（vol_target_allocator） | 不满仓——按波动率缩放 |
| 止损 | UP-2 前瞻概率止损（forward_stop_loss P(跌)≥65%） | 替代固定百分比 |
| 风控 | E9 归因回灌 E2 假说库 | 闭环反馈 |
| 晋级条件 | 前哨期 Sharpe>0 且 max_drawdown>-10% | |
| 退回条件 | 前哨期 Sharpe<0 或 max_drawdown<-15% | 退回 E6 标 decayed |

## 四、信号逻辑（伪代码）

```
IF ret(T-1) <= -1.5% AND ret(T) <= -1.4%:
    K = vol_target_weight(returns[T-20:T])  # UP-1 波动率目标化
    BUY index at T close, hold 19 days
    IF day % 20 == 0:
        SELL → back to cash
ELSE:
    hold cash
```

## 五、sim/paper 前哨施工清单

- [ ] 注册 strategy_registry 条目（lifecycle_status=sim）
- [ ] 建 sim 账户（QMT 模拟单模式）
- [ ] 接入 forward_stop_loss 信号（每日盘前计算 P(跌)）
- [ ] 接入 vol_target_allocator 仓位系数
- [ ] 前哨期日志落 strategy_screen（新增 batch=sim-paper-e3da6fa71af1）
- [ ] 20 日后首次评估→晋级 live 或退回 decayed
