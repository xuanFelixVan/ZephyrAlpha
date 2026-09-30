# E4 完整三阶段正考档案 — E1C-09（P3-E1C-09 唯一 PASS 候选）

- 考试: IS(mining段) → 滚动 WFA → OOS(strict_oos段)（判定零重写: strategy_validation_pipeline+DecisionGate+OverfittingDetector）
- 候选: `ts_corr_20(ts_delta_5(mul(-0.614, close_ma20)), min(close_ma20, sqrt(div(vol_20d, ret_20d))))`
- 全窗: 2024-06-18..2026-09-15（548td, 预注册冻结窗）；折法: 12m/6m/6m 共 3 折（30 个月窗装不下默认 24m 训练窗, 降 12m 披露在案）
- IS 阶段: sharpe=1.469（mining_overlap 2025-09-04..2026-09-15，挖矿发生窗=IS 类比段；P3 登记 1.511）
- OOS 阶段: sharpe=2.027 / 298td（strict_oos 2024-06-18..2025-09-03，矿工未见过；P3 登记 2.004）；OOS/IS 比率=1.3797
- DSR: MOD-SIM-024 精确口径 N_eff=13 → 0.732（P3 登记 0.7256；落带=review）

## 判定: **存疑**

各硬线全过, 仅存边际存疑项(fail-closed, 不构成放行)
DSR落中间带存疑(0.50<=DSR<0.95): fail-closed需补样本或人工复核
WFA门控多数通过但60%稳定性边际未达(正折占比相关见overfitting reasons: ['Walk-Forward Sharpe变异系数1.83超过阈值1.50', 'Walk-Forward存在灾难fold(最低Sharpe=-1.95<-0.50)'])

- 门控: overall_passed=False, can_deploy=False, WFA=2/3 折通过(灾难=False), 过拟合检出=True

## WFA 逐折表（全链路截断面板因果求值）

| 折 | 训练窗 | 测试窗 | 段标签 | 天数 | sharpe | maxDD |
|---|---|---|---|---|---|---|
| 0 | 2024-06-18..2025-06-17 | 2025-06-18..2025-12-17 | strict_oos | 125 | 3.310 | -12.40% |
| 1 | 2024-12-18..2025-12-17 | 2025-12-18..2026-06-17 | mining_overlap(IS偏内) | 118 | 3.934 | -10.14% |
| 2 | 2025-06-18..2026-06-17 | 2026-06-18..2026-09-15 | mining_overlap(IS偏内) | 63 | -1.953 | -40.44% |

## 诚实边界

- IS/OOS 角色对调披露: 本候选挖矿窗=最近 250td, 故 IS 类比段=尾段(mining_overlap)、真 OOS=前段(strict_oos)——与 F-06 幸存者(IS 在前)方向相反, 系候选出生方式决定, 非口径漂移;
- WFA 折测试段多数落 mining_overlap 窗=「选择偏内」滚动稳定性证据（同 MOD-BT-211 折 1-4 披露法）;
- E2 幂等预审/E3 构造环未跑（预注册卡注明 E4 不替代）; 本档案不构成放行, 放行权=Owner 门位;
- 登记对照: oos sharpe/IS sharpe/DSR 三值复算 vs P3-E1C-09.json 登记值, 偏差超限即作废（见 summary.json registration_crosscheck）。

> 合规声明：研究方法与工程产出，不构成投资建议。
