---
blueprint_id: MOD-SIG-063
module_name: similar_day_inference
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-SIG-063 similar_day_inference 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘录 §9.3 + 92号清单 §8.1，M1-③ 剩余走势推演——相似日 KNN。
> 代码：`src/zephyr/signal_ashare/similar_day_inference.py`

## 0. 定位

相似日 KNN 剩余走势推演——只输出尾盘三档情景概率 P(走强/持平/转弱) + 五阶段转移概率，不输出点位/收益幅度预测（90号 §7 哲学）。是状态推演器不是因子（44号 §2.1 裁定：不登记 factor_registry）。

## 1. 接口

```python
def infer_remaining_session(
    today_series: pd.DataFrame | None,               # 当日 09:30→当前时刻快照序列（列契约见下）
    history_store: Iterable[pd.DataFrame] | None = None,  # 历史日快照注入；None/空→恒走兜底分支
    config: SimilarDayConfig | None = None,           # k=10 / min_history_days=60 / max_mean_distance=0.35 等
) -> SimilarDayInference
```

快照序列 DataFrame 列契约（today_series 与历史日帧共用，生产=market_breadth_snapshot 分钟快照表，本模块按注入消费**零 SQL**）：ts（快照时刻）+ breadth_vel / lu_net / vol_extrap_ratio / yw_spread 四维 + if_basis（可选，缺列剔除重配权重）+ index_price（仅历史日帧需要，剩余时段收益标签）。history_store 生产实现=market_breadth_snapshot 读取器（后续波次接）。

## 2. 输出契约

`SimilarDayInference`（to_dict JSON 可序列化）：

- `prob_strong/prob_flat/prob_weak`：近邻中剩余时段收益 >+0.3% / ±0.3% 内 / <−0.3% 的占比（三者和=1）
- `dominant_scenario`：走强/持平/转弱（argmax；平票宁标"持平"不编方向）
- 五阶段转移概率（先验，28号阶段转移平滑口径 diag=0.6 邻阶各 0.2；后验更新留数据期）
- `enabled` / `disabled_reason`：walk-forward 验证命中率 <55%→自动停用（纪律开关）
- `fallback_used` / `fallback_reason`：退化先验兜底留痕
- `n_history_days` / `n_neighbors`：参与匹配的有效历史日数 D / 实际近邻数（兜底=0）

算法链路（§9.3）：五维曲线重采样 30 时点（等距时钟分钟网格，np.interp 线性插值）→ 对历史 D 日同时刻切片算 **Pearson 距离（1−corr）**（量纲各异免归一化；语义=曲线族协同形态相似非水位一致）取 k=10 近邻 → 近邻剩余时段收益分档占比。兜底：D<60 或近邻平均距离>0.35 → 退化五阶段转移先验。

## 3. 不变量（头注 INVARIANTS 原文）

- 不出点位只出三档情景概率（90号 §7 哲学，prob_strong+prob_flat+prob_weak=1，不预测点位/收益幅度）
- 历史不足 D<60 或近邻平均距离超阈 → 退化五阶段转移先验兜底
- history_store 注入式（本模块零 SQL，生产=market_breadth_snapshot 读取器）
- to_dict JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：today_series 为空/特征列全缺/可用历史不足/近邻距离超阈→退化先验兜底不抛（fallback_used=True+fallback_reason 留痕）；历史日缺 ts/index_price/有效点不足→该日剔除并计数不抛；ts 列缺失或含非法时刻值→ValueError（fail-closed）
- if_basis 缺列→该维剔除并重配权重（notes 留痕）
- 当前零数据积累→恒走兜底分支（设计内常态）

## 5. 边界（不做）

- 数据期前无消费方（候选：尾盘决策 closing_session_decision、M2 边界修正引擎 44号 §9.5、prediction_log 落库 92号 §7.13）
- 不登记 factor_registry（状态推演器非因子）；不输出点位/收益幅度

## 6. 测试

tests/signal_ashare/test_similar_day_inference.py
