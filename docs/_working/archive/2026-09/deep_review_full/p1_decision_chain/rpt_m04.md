---
ttl: task_bound
title: 深度审查报告——M04 保形预测族（三变体 D 轴合并审查）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：M04 保形预测族（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 算法（覆盖率失真=置信虚高为本批专项）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `conformal_predictor.py:54`（MOD-SIG-044 split/rolling 基线）+ `tcp_rm_conformal.py:128`（MOD-SIG-128 RM+DDCI 在线）+ `adaptive_conformal_tcp_rm_ddci.py:71`（MOD-SIG-052 加权 split）——三变体合并审查
- 生产调用方：SplitConformalPredictor→risk/core/adaptive_risk_forecast.py:55（**真实消费**，conformal_var_pct=var_pct+margin 口径）；TCP-RM(128)/adaptive(052) 无生产消费方（header 自认远期/装配批）
- 测试文件: test_conformal_predictor.py（109 行）/test_tcp_rm_conformal.py（301 行）/test_adaptive_conformal_tcp_rm_ddci.py（均存在）
- 变更热力: 3/2/2 commits（低热）
- 材料包缺项: 真实残差序列画像缺（覆盖率结论以受控模拟+理论判定）

## 1 对象快照

三变体分工（header 互相声明一致）：044=split 一次性校准+rolling 无加权窗口基线；128=Robbins-Monro 在线分位跟踪+DDCI 覆盖率双反馈+CP-VaR 回测；052=加权 split-conformal（权重由调用方供给）。排除项：adaptive_risk_forecast 消费侧换算（var_pct+margin 单侧上 buffer 口径，已走查声明 :8）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **CP-VaR 目标破位率口径错位（复算实锤）**：target_breach_rate=1−τ（双侧漏覆盖），但破位只统计下轨 actual<lower（单侧）；对称残差下均衡破位率≈(1−τ)/2。复算：iid N(0,1) 4000 步 τ=0.90 → breach_rate=0.0542 vs target=0.10，**gap 恒虚 −0.05**，系统性把 2× 欠覆盖显示为"优于目标" | tcp_rm_conformal.py:261, 264 vs 117-125 | **P1** | 复算脚本（已实测 0.0542 vs 0.10）；或读 backtest 破位统计只取 a<iv.lower |
| A | **冷启动烧入回测统计**：reset() 后 margin=min_margin=1e-6，回测/统计从近零阈值起步→前期必然欠覆盖计入 breach_rate 与 mean_margin，无 warmup 剔除；docstring 仅提示"可 reset() 保证确定性"未提示 burn-in 污染 | tcp_rm_conformal.py:164, 247-263, 277-294 | P2 | reset 后对平稳序列回测，对比前 100 步与后段破位率 |
| A | **NaN 静默传播（复算实锤，族内纪律不一）**：044 SplitConformalPredictor.fit 与 RollingCalibrator.update 无 NaN 校验→margin=NaN→区间 (nan,nan)；052 calibrate fail-closed ✓（:90-91）；128 _finite fail-closed ✓（:174-181）——同族三件两种纪律 | conformal_predictor.py:95-103, 139-141 vs adaptive:90-91, tcp_rm:174-181 | P2 | 复算脚本（已实测 fit 含 NaN → margin nan）；造 NaN 调 052/128 观察抛错对比 |
| A | **k>n 退化正确**：k=⌈(n+1)(1−α)⌉>n 时取样本 max（=+∞ 外推的保守工程化）✓ 不产生虚窄区间；min_periods 语义=分母不缩水 ✓ | conformal_predictor.py:70-79 | ✓ 查无 | n=10, α=0.05 手算 k=11→clamp 10 |
| A | 052 加权分位推导：均匀权重时 cum[i]=(i+1)/n，target=k/n → idx=k−1 恰为第 k 小 ✓ 退化为 split-conformal；NaN/负权/全零 fail-closed ✓ | adaptive_conformal_tcp_rm_ddci.py:58-68, 85-105 | ✓ 查无 | weights=None 对拍 044 同输入同 margin |
| A | 128 RM 步长 step0/n 满足 Robbins-Monro 收敛条件（Σγ=∞,Σγ²<∞）✓ 收敛到历史得分 τ 分位；但 1/n 全程衰减=收敛到**全程**分位，对分布漂移无追踪力——补偿全靠 DDCI 常数增益（设计上成立，行为特征未文档化） | tcp_rm_conformal.py:206-211, 213-224 | P3 | 前后半段不同方差的合成序列看 margin 是否跟上 |
| E | 044 RollingCalibrator 允许 min_samples>window 配置→ready() 永假、predict_interval 恒 None 静默降级（调用方拿 None 须自行兜底）；无告警通道 | conformal_predictor.py:128-136, 147-155 | P3 | 构造 window=250,min_samples=300 观察恒 None |
| D | **052 名实不符**：模块名 adaptive_conformal_tcp_rm_ddci 但无 RM/DDCI 实现（docstring :26-27 自认"留接口位"，实为加权 split-conformal）——误导性命名+MOD-SIG-052 与 128 的 DDCI 概念双登记 | adaptive:19-27; tcp_rm:28-32 | P3 | 读两 header 分工声明（声明本身一致 ✓） |
| C | 消费侧：044 被 adaptive_risk_forecast 真实消费 ✓；conformal_band_around_quantiles/empirical_coverage 无生产调用方（工具函数，可接受）；128/052 半孤儿已声明 | adaptive_risk_forecast.py:4, 31, 55, 113 | ✓/P3 | grep |
| A.3 | 测试：tcp_rm 301 行覆盖 RM/DDCI/回测/确定性重放，无 lookahead 断言 ✓（:92-99）；缺口=无"对称噪声下 breach_rate→(1−τ)/2"的统计断言（恰漏过 P1）、044 无 NaN 用例（恰漏过 NaN P2） | tests/signal_ashare/ml_forecast/test_tcp_rm_conformal.py:221-231 | P2（测试缺口） | 补统计断言（收口方施工） |

## 3 SOTA 对照

- **对等已有**：split-conformal 有限样本边际覆盖 P(Y∈C)≥1−α、分位阶 ⌈(n+1)(1−α)⌉——Vovk, Gammerman & Shafer《Algorithmic Learning in a Random World》(Springer, 2005；alrw.net；2nd ed 2022, DOI 10.1007/978-3-031-06649-8)；实现 044:70-79 一致。（2026-09-18 检索）
- **对等已有**：split/inductive conformal 计算化路线（Papadopoulos et al. 2002 起，Lei & Wasserman 2014 形式化）——044 rolling 基线属此谱系；docstring 引"Conformal Kelly 实证慢而稳"为路线依据（仓内 memo 承载）。
- **立卡候选**：在线 conformal 的 tracking 形式（如 ACI, Gibbs & Candès 2021 "Adaptive Conformal Inference Under Distribution Shift", arXiv:2106.00170）与 128 的"1/n 衰减 RM+DDCI"目标一致但步长设计不同——若 128 进入生产漂移场景，建议以 ACI 作对照基准（适配点：γ 固定小步长替代 1/n）。受阻部分：ACI URL 凭训练记忆给出，本批未检索验证——如实记，采纳前需复核。
- 驳回：052 的加权分位近似（target=k/n 而非 (n+1)(1−α)/n 连续比）——误差 ≤1/n，加权场景本无精确有限样本保证，驳回升格要求。

## 4 缺陷清单

1. **P1 CP-VaR 双侧/单侧口径错位（复算实锤）**：现状=target_breach_rate=1−τ 对照下轨破位率；影响=VaR 回测报告系统性乐观，最多 2× 破位超标不可见（置信虚高的报告层形态），爆炸半径=CP-VaR 回测消费方（装配批）全量。建议修法：target_breach_rate=(1−τ)/2，或报告并列双侧 miss 率与单侧破位率双口径+测试统计断言。验证法：§2 A-1 复算（已实测）。
2. **P2 NaN 静默传播（044 主件）**：唯一被生产消费的变体恰是 NaN 裸奔件。建议 fit/update 校验 isfinite（对齐 052/128）。验证法：§2 A-3 复算（已实测）。
3. **P2 冷启动烧入**：回测报告无 warmup 剔除选项。建议：backtest 报告附 burn-in 分段统计或支持 min_margin 起始值注入。验证法：§2 A-2。
4. **P2 测试缺口**：无覆盖率统计断言/无 NaN 用例——P1/P2 正是从该缝隙漏过。验证法：grep 测试文件。
5. **P3 组**：RM 漂移行为特征未文档化、min_samples>window 静默、052 名实不符、128/052 半孤儿。

## 5 挂起疑问

- ACI 引用（Gibbs & Candès 2021）URL 未检索验证——立卡采纳前由收口方复核（本审查不给该条出"对等/立卡"终判）。
- adaptive_risk_forecast 的 conformal_var_pct=var_pct+margin 为单侧上 buffer：margin 源自 |residual| 的双侧分位→单侧使用=偏保守（安全方向），但与 044 的双侧区间语义不同轴——消费侧口径是否经裁定待查。

## 6 完备性自评

六轴全查。覆盖率专项（作业点题）四问闭环：分位阶修正 ✓（k>n 保守退化正确）、有限样本保证 ✓（044 对齐 Vovk）、rolling/在线变体的保证弱化已登记（128 P3 漂移行为、044 rolling 依赖 exchangeability 近似——INVARIANTS :8 "有限样本边际覆盖保证"对 rolling 变体表述偏强，P3 文档级）、NaN/边界 ✓（两实锤）。长尾：①052 权重由外部 regime 模型供给时的权重质量未审（无生产消费方）；②三变体合并为"保形核+策略层"的重构机会登记（轴 D：_conformal_quantile 与 _weighted_conformal_quantile 小重复，暂不立卡）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
