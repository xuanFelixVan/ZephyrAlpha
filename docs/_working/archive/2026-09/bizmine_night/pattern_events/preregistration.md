---
ttl: task_bound
---

# 图形事件研究预注册（P 车道 st-bizmine-pat-20260919）

> 状态：计算前钉死。本文件在数据计算开始前落盘，之后只读不改（如需偏离，在 report.md「偏离记录」节写明）。事件表勘察与映射核对属只读查证，先于本文件完成。

## 1. 研究问题

图形库 287 条目录中 prereview.csv 判「值得考」的 78 条图形/形态，其对应事件（c1_market.market_pattern_event）在事件后 5/10/20 个交易日前瞻收益上，相对全样本基线是否具有方向性预测力？在大盘灰度状态（T-1 PIT）条件下预测力如何变化？

## 2. 数据与口径（勘察实测，2026-09-19）

- 事件表：`c1_market.market_pattern_event FINAL`（ReplacingMergeTree）。实测 22,315,277 行，全day 周期，覆盖 2021-09-01..2026-09-18，uniq(name)=104，uniq(pattern_id)=18475。去重核验：(pattern_id,timeframe,symbol,anchor) 无重复；(name,direction,symbol,anchor) 有 35,203 个重复组（图形实例多 pattern_id 同日同股，0.16%）→ 聚合前按该四键 SELECT DISTINCT 去重。
- 收益表：`c1_market.kline_daily FINAL`（1990-12-19..2026-09-18，全 A_share，quality_flag=1 占 10,085,114 / 0 仅 651 行剔除）。事件 symbol_canonical 100% 命中 kline。
- 复权诚实条款：`kline_daily.adj_factor` 恒 1（未复权）→ 本报告一切日线结论=**暂定**，「待复权链修复后复核」。
- 大盘灰度轴（三套，T-1 PIT）：
  1. `c1_market.alt_regime_signal`（FINAL）signal_id=F4_BDI_MOMENTUM_Z20——该表唯一全程覆盖事件窗的日度信号（9,271 行，1989 起），生产定义三态 risk_on/neutral/risk_off（状态阈值生产期钉死，无本研究重拟合）。PIT：状态=signal_date ≤ 事件锚日−1 自然日的最近一行。
  2. `c1_backtest.regime_state_anchored`（plain MergeTree，无 FINAL，4,469 行 2017-07 起）dominant∈{r1,r2,r3,r4} 生产状态机。PIT 同上（trade_date ≤ 锚日−1）。
  3. 同表 vol_pct 连续灰度三分位：**IS 期=2021-09-01..2023-12-31 分位边界钉死=0.212 / 0.532**（实测 33.3%/66.7% 分位），OOS=2024-01+ 仅套用不重算。
- 注：任务原文写「分年稳定性 2019..2025」——事件数据实测 2021-09 起，故实际分年=2021(9月起,部分)/2022..2025/2026(至9月,部分)，偏差如实记录。

## 3. 事件单元定义（78 条 → 102 cell）

- 研究单元=cell=(事件name, direction)，direction 为引擎 PIT 可观察量（CDL 符号/规则判定），取库内原文。
- 78 条候选逐一映射（映射真源=prereview.csv entry_id/name ↔ 事件表 name；TA-Lib CDL 名直接对应；中文 A 股特色形态对应引擎中文名）。**映射成功率 78/78，无跳过**。
- 单向条目（如 Hammer→CDLHAMMER/向上）1 cell；双向条目（如 Marubozu、Three Inside Up/Down、对称三角形、矩形箱体）每方向 1 cell；Hikkake 含变体 CDLHIKKAKEMOD（2 方向）共 4 cell；中性条目（缠论中枢/搓揉线/窄幅整理日/内包日）direction=中性。全表映射共 102 cell。
- 完整映射表硬编码于计算脚本 `.runtime/tmp/bizmine/p/run_study.py` 常量 `MAP`（与 report.md 附录一致，commit 同批）。

## 4. 统计设计（计算前钉死）

- 前瞻收益：r_N = close(tseq+N)/close(tseq) − 1，tseq=全市场交易日序（kline distinct trade_date 行号），N∈{5,10,20}；窗内任一日无价（停牌/末尾截断）→ 该窗缺测。事件锚日=anchor_trade_date（confirmed_at=形态末根 bar 收盘，PIT：收益自确认收盘起算）。
- 基线=同期（2021-09-01..2026-09-18）全部个股日（quality_flag=1）同窗口收益，同一 tseq 口径。
- 每窗口统计：n / mean / median(quantileTDigest) / 胜率 / std。超额=事件 mean − 基线 mean（同窗口）；Welch t=(m_e−m_b)/√(s²_e/n_e+s²_b/n_b)。
- 功效阈值：某 cell 某窗口 n<30 → 标「功效不足」，仍入册。
- 分年稳定性：按 anchor 年分组，n_year≥30 的年份计 sign(年超额)；一致性=与全样本超额同号年份占比（主窗口=10 日）。
- regime 条件版：三套轴各分桶报 n/mean/胜率/超额（桶内 n<30 标功效不足）。桶边界：BDI 三态与 dominant 四态=生产态原样；vol_pct=§2 IS 钉死三分位。
- 多重检验警示（入报告）：主检验=102 cell×3 窗=306；分年=306×6 年；regime=306×10 桶；合计 ≈4,700+ 检验。α=0.05 下 Bonferroni 阈值≈t>4.2（√(检验数) 量级警示另注）。**top 只升「待考池」，不判 PASS**。
- 排名册综合分：score = t_10d × (2×consistency_10d − 1)（惩罚方向不稳），并列参考 t_5d+t_20d。负超额同样入册（反向信号线索）。

## 5. 已知局限（诚实条款）

1. 未复权（adj_factor≡1）→ 分红送转日附近 r_N 有系统性向下偏移，且对高送转股事件污染不可忽略；一切结论暂定。
2. 重叠窗口+事件跨股相关 → t 值膨胀，仅作筛选用。
3. 事件表 confidence 为引擎初拍值 0.6，未标定，不参与本统计。
4. 2026 年为不完整年（至 09-18），分年一致性仅计 n≥30 年份。
5. 未剔除 ST/退市整理/新股上市初期；未做行业/市值中性化——本研究的超额=相对全市场的原始超额。
