---
ttl: task_bound
title: 04 P1 三张条件概率表（主施工文档）
---

# 04 · P1 三张条件概率表（主施工文档——Owner 愿景唯一缺的原材料）

> 定位：把"什么天气哪个板块赚钱"从两本账（天气账×板块账）对出来。数据全在库，一个计算批。
> 口径真源=quant_methodology/01_caliber_law.md + 03_conditional_stats_spec.md（裁定级引用）。

## 一、三张表定义

### T1 主表：P(板块收益 | 大盘相位)
- 维度：板块（kline_sector_880 有实石的板块，~580-880 个）× 六段相位（6 态）
- 每格四元组行（03 册规范）：**raw 原始频率、n 样本数、Wilson 置信下界、区间宽**
- 收益口径：期望值=均值日收益+分位数（P25/50/75）+胜率（仅观察列，禁单独排序）；**排序只认 Wilson LB**
- 样本门槛：**MIN_OBS=30 交易日地板**（condition_package.py:49 家族值）；不足→"不可考"第三态明示，禁硬给结论

### T2 辅表：板块相对排名条件表（轮动原料）
- 维度：相位内板块收益横截面排名 → top quintile 在相位持续期的持续性/换手率
- 用途：BM-SEL-08 板块轮动序列、22_sector_rotation_spec 的查询原料

### T3 可靠性表：相位转移矩阵（状态层自检——回应"状态准确性"）
- P(相位_t+1 | 相位_t) 全史转移矩阵 + 各相位平均停留天数 + 振荡指数
- 用途：下游置信度加权（状态传概率不传点的定量基础）

## 二、数据源与对齐（全部实测于 09-24）

| 输入 | 真源 | 对齐键 |
|---|---|---|
| 大盘相位序列 | c1_backtest.regime_snapshot_history（3,629 日，PIT）→ 六段折算走 **REGIME_STATE_TO_ACTIVATION_PHASE 唯一位点**（framework_composer.py:153）；r1/r2 不路由=NaN 宁漏勿误 | trade_date，as-of：detect(t) 只用 ≤t-1 |
| 板块日收益 | c1_market.kline_sector_880（2020-03→今） | trade_date+board code |
| 交叉验证 | sector_state（985 日）/ 六段全史 CSV（1,816 日，t0 班 0033 批件） | trade_date |

## 三、施工要点

1. 相位折算禁自造判定——只调法定映射位点（与 t0 班 D-1 同纪律：注册表明文禁异轴顶替）。
2. 重叠期取交集（880 从 2020-03 起，相位从 2019-04 起→有效窗 2020-03→2026-09，≈1,600 交易日）。
3. 产物落点（草案）：CSV+parquet 落 data/strategy_intake/conditional_tables/（与 GPU 产物同区），登记图书馆资产（Librarian.act，potential_consumers=[板块条件查询, BM-SEL-08, 04_P1]）；后续升 CH 表另批。
4. 每表附 README（口径+生成脚本路径+重算命令），脚本落 .runtime/tmp（一次性）→ 若需长期重估再转正 scripts/。
5. 验收：随机抽 10 格手工对账（CH 直查 vs 表值）；相位覆盖率报告（r1/r2 不路由日占比）；与 GPU 输入包条件轴（grid_gpu_sectorcond 四通道）一致性抽查。

## 四、排期与属主

- 属主：st-cmd-20260924（本班），GPU 跑批期间并行施工，**目标 09-25 白天交付**。
- 前置：无阻塞（数据面 09-24 已验）。GPU 完赛不依赖本表；本表是决策地图原料，与搜索成绩单互补。
