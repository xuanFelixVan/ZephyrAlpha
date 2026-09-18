---
ttl: task_bound
---

# 窄考卡 04：光头光脚 Marubozu/向上（CDLMARUBOZU，PAT-CANDLE-014）

> 状态：**计算前钉死**，先于本车道任何回测计算。P 车道真源=`../pattern_events/`（commit dbdef721，只读）。未复权暂定，待复权链修复后复核。

## 1. 受试 cell

- cell=(name=CDLMARUBOZU, direction=向上)，entry_id=PAT-CANDLE-014。**映射说明：任务令「光头光脚 Marubozu/向上」按 P csv 实际列名就近映射=CDLMARUBOZU/向上（entry_name "Marubozu"）；CDLCLOSINGMARUBOZU（PAT-CANDLE-015）为另一 entry，不在本考。**
- P 筛选证据（背景）：n10=135,757，ex10=+0.81%，t10=24.3（膨胀，不作判定），cons10=6/6，胜率 51.5%——弱但全窗口稳；P 另报 BDI 开关型：risk_off +1.34% vs risk_on −0.85%。
- 方向=**做多**。

## 2-8. 协议条款

执行模型、成本、基线、判定门槛（成本后年化超额 Sharpe≥0.8 且 NW t(lag=N)≥2 且分年 ≥4/6 正，主窗 10 日）、显著性三重、多重检验两档（1.056e-5/4.854e-4，判定按常规档，PASS 须标 4733 存活与否）、regime 稳健段（BDI 三态×vol 三分位 IS 钉死 0.212/0.532，T-1 PIT）——**全部与 exam_card_01_tower_bottom.md §2-§8 逐字相同**。

## 9. 本 cell 特有局限

1. P 筛选期 ex10 仅 +0.81%，成本后大概率收窄至负带——本考预期以 RED 检验为主，如实报告不硬凑。
2. Marubozu 为单 bar K 线，信号密度高（13.6 万仓次），等权组合容量假设名义摊薄成立。
3. 未复权暂定。
