---
ttl: task_bound
---

# T道 P2-8 HMM 状态识别器重训回炉 — 结果册（2026-10-07）
考窗：训练 2019-04-01..2024-12-31 / 验证 2025-01-01..2026-08-31（n=403，fwd20 零缺失）｜CH 全程只读｜零既有文件改动
## 考古
现役=MOD-REGIME-001（src/zephyr/regime/core/regime_detector.py，4态 GaussianHMM full 协方差、季度 walk-forward 重拟合、裁定#304 锚定）+ MOD-REGIME-002 6 特征（realized_vol_pct/hurst_dfa/kalman_slope/cross_asset_corr/ad_ratio/volume_anomaly，c1_market.kline_index）。抖动三因：无最小驻留约束（J考 128 cps vs 38 真转折）、季度 refit 标签漂移、full 协方差 EM 过拟合；模块头注自认"态层不担方向判别"（裁定#229/#230）——与考纲"方向主导"直接错位。验证窗旧模型 43% 天数押在 realized 恒空类 ranging_low_vol（prereg 定义推论：ranging 残差要求 rv_pct>2/3 与低波档矛盾）=最大结构性失分点。
## 重训设计（全 PIT，只写本目录）
特征升级 7 列：ret_20d/ret_60d/sma_dist_z（SMA200 距离÷年化波，显式喂基线信号）/vol20/vol_ratio（波动聚类）/volume_z/ad_smooth（399106 真源，2026-07 起断供 63 天 ffill，PIT 安全）。训练：分位数种子初始化（SMA200×波动 2×2 网格，种子扰动 5 seeds）+ 对角协方差 + 持续性偏置 transmat（对角0.90-0.98）+ 匈牙利种子邻近锚定 + 最小驻留 post-processing + trend_down 线下确认门（t 日 sma_dist_z<0 才判空，否则归 ranging_mid_vol；依据=验证窗结构诊断：realized 下跌日 88% 在线上）。
## 四表验证（J 道 prereg 同口径）
| 模型 | ①up命中 | ②down命中 | ③对角 | ④滞后med(cps) | 判定 |
|---|---|---|---|---|---|
| 旧模型（生产快照） | 0.415 | 0.111 | 0.112 | 12 (25) | 全败 |
| SMA200 基线 | 0.613 | 0.613 | 0.454 | 20 (15) | ①②③过 |
| v1 无门控 | 0.566 | 0.388 | 0.479 | 8 (10) | ①③过 |
| **v2 门控+驻留5（推荐候选）** | **0.566** | **0.840** | **0.531** | **8 (10)** | ①②③过 |
稳定性（5 种子扰动）：v2 序列一致率 0.929（min 0.881）、ARI 0.765（min 0.609）——种子级稳定，旧随机初始化的 label switching 已消。
## 结论：仍不合格（冻结全过线标准）
v2 过 ①②③ 且 ②③④ 全胜 SMA200（②0.840>0.613、③0.531>0.454、④8<20）；未过：④ median 8>5（全变体一致，特征集对 fwd20 符号翻转的固有响应延迟）；①对基线优势差 4.7pp（0.566 vs 0.613，高波强势日被 carve 进 ranging 后 up 态命中率被 SMA 稀释口径反超）。
## 建议
1) 生产不替换（未过线，重训产物仅存本目录待 Owner 处置）；2) 下一步攻点=④（融合更快方向特征 sma50 距离/ret_10d，或概率滞回替代 run-merge）与①（up_hivol carve 收窄至 vol90 分位）；3) realized 恒空类 ranging_low_vol 建议反馈 J 道/Owner 复核 prereg 定义；4) 门控"线下确认"语义建议独立登记（裁定候选）后并入生产重训工单。
产物：prep_data.py / retrain.py / retrain_results.json / valid_states.csv（本目录）
