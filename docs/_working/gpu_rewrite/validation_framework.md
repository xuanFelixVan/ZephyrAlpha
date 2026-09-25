---
ttl: task_bound
title: GPU 重写挖矿④——等价性验证框架设计（CPU 真源 vs GPU 被测）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
family_id: GPU-REWRITE
---

# ④ 等价性验证框架设计（对拍红蓝）

> 定位：GPU 重写的**转正门**。没有本框架，L2/L3 禁止产出任何进入 manifest 的数字（红蓝纪律=方案①先例：`docs/_working/decision_map_campaign/17_quantified_acceptance.md:28` "Spearman≥0.99 且 top50 重合率≥0.9 且轻档单格≤8s → 可实施；任一不达标=草案作废"）。
> 真源方向：**CPU 引擎（现行 `_c4_engine.py`）=真源蓝军；GPU/向量化实现=被测红军**。判定函数（exam_cost_gate 三门）两侧共用同一实现（扫描/判定分离既有纪律，`exam_cost_gate.py:8`）。

## 一、对拍维度（三层，逐层口径）

### 层1 · 逐位层（bitwise）——只对 L1
- 对象：L1 hoisting/缓存改造前后，**同一 CPU 实现**的 net 序列。
- 标准：**bitwise 全等（容差=0）**——L1 不改浮点运算顺序，任何一位漂移=实现错误（③文 L1 验证节）。
- 证据：net 序列 sha256 对账 + sharpe/mdd/turnover 逐位 diff 表落 `data/strategy_intake/val_<ts>/bitwise_report.yaml`。

### 层2 · 统计量层（tolerance）——对 L2/L3
- 对象：同一格点 CPU-FP64 vs GPU 输出：net 序列、sharpe、ann_return、max_drawdown、avg_turnover、五档 tier_sharpes。
- 容差标准（引用业界做法）：
  - **GPU-CPU 不追求 bitwise**：NVIDIA 官方口径=bitwise 可复现仅在"同卡+同库版本+同形状"内成立（[cuFFT determinism docs](https://docs.nvidia.com/docs.cupy.dev) 口径，cuFFT 12.8 文档 2025-01：结果确定性以条件恒定为前提）；跨实现浮点求和顺序（并行归约）必然 ULP 级漂移，复利累积会放大。
  - **离散量精确一致**：交易/持仓信号、持仓只数、调仓日集合、五档门 PASS/FAIL 判定——**必须 100% 一致**（业界通则：signals/trades exact match, floats tolerance——GPU 数值验证通行实践，见②文调研记录）。
  - **浮点统计量**：net 序列逐日相对容差 ≤**1e-5**（FP32 路径）/ ≤1e-8（FP64 路径）；sharpe/ann_return 绝对差 ≤0.005；max_drawdown 相对差 ≤1e-4；期末净值差 ≤**2bp**。
  - 依据：quant 工程实践通行的 1e-8~1e-6 returns 相对误差带 + 期末权益 bp 级带（GPU vs CPU 数值验证实践综述，②文 §7 引）；本项目侧无现成先例，此为**建议判据 (建议)** 标注，Owner 可调（17 号文判据两档纪律）。
- FP32 累积误差的定量预检（施工前跑一次）：1,650 日 cumprod 的 FP32 vs FP64 期末净值差实测——若 >2bp，L2 精度策略升级为"关键累计段 FP64"（③文），容差表随之重签。

### 层3 · 排名层（ordinal）——整批验收
- 对象：整批格点的 cost_adjusted_sharpe 排名（搜索主目标函数，`factory_grid_executor.py:872-874` 口径）。
- 标准（沿方案①先例加严，标注 (建议)）：**Spearman ≥0.999**（方案①线 0.99 是"不同口径"间的线，同口径不同实现应收得更紧）；**top50 重合 ≥0.98**；净收益符号一致率 100%（赚钱/亏钱判断不许翻转）；五档单调性破缺数=0（`exam_cost_gate.py:186` 门1 在两实现下同判）。

## 二、测试格子集选择

| 池 | 构成 | 数量 | 用途 |
|---|---|---|---|
| T0 主池 | 方案①红蓝标定既有的 T0 200 格（分层抽样，`03_gpu_campaign.md:34`） | 200 | 常规对拍 |
| 边界格（手工构造，不进批产物） | ①全退市/ST 宇宙（掩码全遮）②单票宇宙（cols=1，`factory_grid_executor.py:745-749` cols<30 阴性线两侧各一格=29/30/31）③min_days 边界 59/60/61（`exam_cost_gate.py:48` DEFAULT_MIN_DAYS=60 两侧）④五档 sharpe 平坦（单调性容差 1e-9 贴线，`exam_cost_gate.py:46`）⑤insufficient_net（std=0）⑥涨跌停封板密集窗（gate 实际生效非平凡）⑦all_a 大宇宙列序乱序（稀疏 gather 索引错位猎杀） | ~20 | 回归雷区 |
| 抽查池 | 每波 GPU 批次随机 5%（预注册种子） | 动态 | 防批量错位的持续哨兵 |

## 三、通过判据与流程

```
L1 转正：层1 全绿（bitwise）+ T0 200 格 manifest 逐列 diff 全等 → 直接转正（同口径零风险）
L2 转正：层2 全绿 + 层3 全绿 + 边界格零翻车 + 抽查池 3 个连续批次零失败
       → fail-closed：任一 red = 停，产出打 degraded 标记禁入 manifest（`19_gpu_plan` 验收口径 backtest_dead/eval_dead/degraded=0 同精神）
仲裁通道：容差边界争议格 → FP64 fallback 单格重算（③文 L2 精度开关）→ 仍不一致=实现 bug 非 FP 问题
```

- 产物：每轮对拍落 `data/strategy_intake/val_<ts>/`（bitwise_report.yaml / tolerance_report.yaml / rank_report.yaml / 边界格逐项表），报告头带两实现 git hash+库版本（GPU 可复现性以"同卡同版本"为前提，②文 §7）。
- **衔接冗册多校纪律**：本框架是 `docs/_working/quant_methodology/02_overfitting_defense.md`（DSR/PBO/CSCV/WFA 多校链）的**工程实现层前置**——引擎本身不可信则多校全空转；GPU 成绩单沿用 17 号文 §一 GPU 成绩单判据（完成率/成本门真实性/负结果纪律三线不放松），本框架只增加"实现等价性"一维，**不替代、不稀释**多校。

## 四、负决策条款（框架自身的止损）

验证成本超过 L2 本体工程量的 50%（对拍脚本+修复 >1 周）即上报 Owner 重估：可能意味着实现语义分叉过深，应退回 L1+CPU 多进程扩展（②' 分片）而不是硬上 GPU——**等价性买不来就是不该上**。
