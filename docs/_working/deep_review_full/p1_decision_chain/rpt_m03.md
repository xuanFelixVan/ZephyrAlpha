---
ttl: task_bound
doc_type: report
title: 深度审查报告——M03 条件密度预测（conditional_density_predictor）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：M03 条件密度预测（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 算法（条件经验分布+矩估计+VaR/CVaR+CRPS）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/ml_forecast/conditional_density_predictor.py:56(Config)(:141 主入口)`
- 生产调用方: 真实——fine_scoring_engine.py（密度要素摘要消费）、risk/core/adaptive_risk_forecast.py、ml_train/implementations/qnn_two_stage.py、factor/core/distribution_feature_engineer.py、event_conditional_density.py（同族扩展）
- 测试文件: tests/signal_ashare/ml_forecast/test_conditional_density_predictor.py（存在，112 行）
- 变更热力: 2026 年 3 commits（低热）
- 材料包缺项: 真实收益率分布画像缺（矩估计稳健性以设计口径判定）

## 1 对象快照

条件经验分布法：按条件标签分桶取 trailing window 经验分布→矩估计（均值/方差/偏度/Fisher 超额峰度）+7 点分位网格+VaR/CVaR（负=亏损）+degraded 回退；crps_empirical 提供闭式 CRPS。排除项：event_conditional_density.py（同族扩展件，旁系登记未审）；下游 BM-SEL-18 扣分公式（G02/骨架件另审）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **window=0/负数配置静默语义反转（复算实锤）**：`r_list[-0:]`==全量切片（Python 陷阱），window=0 → n_samples=300 不截断（已实测）；config 无 __post_init__ 校验 window≥1/quantiles 单调/var_level∈(0,1) | conditional_density_predictor.py:169, 177, 55-69 | P2 | 复算脚本：ConditionalDensityConfig(window=0) + 300 样本 → n_samples==300（已实测） |
| A | 数学四问-矩：总体矩口径（std ddof=0，skew=E z³，excess kurt=E z⁴−3）✓ 一致 Fisher；常数序列 std<1e-12 → skew/kurt=0 ✓ 边界守卫；均值/方差 NaN 输入无防御（samples 含 NaN → 全部输出 NaN 静默传播） | :105-114 | P3 / P2(NaN) | 造含 NaN 样本跑 conditional_density 看全 NaN |
| A | 数学四问-VaR/CVaR：var=quantile(samples,1−var_level) 负=亏损 ✓；tail=samples≤var 非空（min 恒 ≤ var）✓；cvar=尾均值 ✓；var_level=1.0 边界→tail_p=0→var=min→cvar=min（退化但安全） | :122-126 | ✓ 查无 | 造全正收益序列看 var>0 时 cvar 口径 |
| A | 数学四问-CRPS：NRG 闭式 E\|X−y\|−0.5E\|X−X'\| ✓（对角零元含入 1/n² 为标准经验口径）；恒有 CRPS≥0（Jensen）✓；O(n²) 250 窗可忽略 ✓ | :185-199 | ✓ 查无 | 对拍 properscoring 库（若可用）小样本 |
| B | **PIT 靠调用方纪律**：函数不校验序列时序性/升序——错序传入静默产出伪"trailing"分布（INVARIANTS :8 声明"仅用传入历史"，实现无法保证） | :141-182, :8 | P3 | 乱序传入对比输出差异 |
| A（降级） | 桶样本<min_samples 回退全样本 degraded=True ✓（:180-182）；但降级后 quantiles/var 仍以 condition 标签呈现——消费方若忽略 degraded 标志会把无条件分布当条件分布（标记在字段不在语义） | :180-182, :94 | P3 | grep 消费方 degraded 检查率 |
| D | quantiles dict 键为 float：JSON 序列化变 string，下游 round-trip 后类型漂移；density_summary forward_var_pct=abs(var)*100 ✓ 量纲（%）一致 | :91, :96-102 | P3 | asdict 后 json.dumps 复读对比键类型 |
| C | 消费链闭合 ✓（≥4 生产消费方，含跨域 risk/ml_train）；与 conformal 的"PDF 分位数输入"衔接经 2026-09-05 AI-08 审计实证未接线（header :5 自认） | :5; grep | ✓ | grep |

## 3 SOTA 对照

- **对等已有（理论）**：经验分布 CRPS 闭式为 Gneiting & Raftery (2007, JASA) 标准结果——**受阻未搜 URL**（本批检索预算用于 WQ101/保形/TA-Lib；CRPS 实现正确性经独立推导验证，不依赖检索）。
- **对等已有（路线）**：91 号 memo 裁定"轻量密度头、禁重模型依赖"——本实现与裁定一致（对照项=仓内 design memo，非外部源）。
- **立卡候选**：无（经验分布法在 window=250 上无 SOTA 升级必要；若升级应为条件核密度/分位回归——涉及 memo 路线变更，非审查者立卡范围）。

## 4 缺陷清单

1. **P2 window=0 静默不截断（复算实锤）+ config 零校验**：建议 __post_init__ 强制 window≥2/quantiles 严格递增∈(0,1)/var_level∈(0,1)。验证法：§2 A-1 复算。
2. **P2 NaN 无防御**：矩/分位/VaR 全链 NaN 静默传播（对比 M04 三变体中两个已 fail-closed——本件与 conformal_predictor 主件同为 NaN 裸奔，族内纪律不一）。验证法：含 NaN 输入。
3. **P3 组**：PIT 依赖调用方、degraded 语义标记弱、float 键 JSON、CRPS 理论源未挂 URL。

## 5 挂起疑问

- 消费方（fine_scoring_engine/qnn_two_stage）是否检查 degraded——若普遍忽略，P3-3 应升 P2（条件/无条件混淆=密度要素失真）。

## 6 完备性自评

六轴全查（F 部分受阻记）。数学四问逐项过（矩/VaR/CRPS/分位）。长尾：①event_conditional_density 同族未审；②min_samples 与 window 的相对配置合理性（min_samples=60 < window=250 桶最多 24% 占比即可用）未做数据实证。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
