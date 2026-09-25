---
ttl: task_bound
---

# [BLUEPRINT] SH-DOC-001 | docs/_working/decision_map_campaign_20260924/links/L05_t0/SKEL.md §5 D1/D2/D3 + 17_quantified_acceptance.md §三
<!-- [MODULE] t0_state_match_readme -->
<!-- [STABILITY] frozen_after_launch -->
<!-- [SAFETY] L -->

# L05-C03/C04 · 多周期买卖点轴 + 全量×状态匹配引擎 README

> 班组：L05-C03/C04 施工班（Owner 主攻方法论①②）。本件=本轮交付的口径真源+重算命令。
> 上游判据全部引用不重写：成本 31.2bp / 前置 ≥30bp / 土规 30 对（`scripts/audit/cost_trio_exam.py`，
> import 复用）；成交模型骨架=`T0_MATERIAL_EXAM_CARD_draft.md` §4（M0，写死）；
> 六段相位真源=B4（`six_phase_history_v1.csv`，routed 行法定）。

## 0. 一页读法

1. **规则卡 4 张已预注册**（`rule_cards/`，先卡后跑禁主观盘感，17 §三.1）：
   R01 固定网格（34法2.1，与 M0 同参，**v1 执行**）、R02 波动自适应带（2.2）、
   R03 VWAP 带反转（3.2）、R04 ORB（3.3）——全部出自 34 法"7 可考"族的分钟可落地子集
   （5.4=tick 面/9.1=GBM/9.3=因子族不可规则卡化，登记于 §4 排除清单）。
2. **引擎**=`scripts/backtest/t0_rule_engine.py`：复用 `t0_material_line` 数据面与周期接口
   （1min 原生，{5,15,30,60}min 序数分桶重采样，120min 不做），批内一次取数多规则共享，
   50 只/批确定性分批断点续跑；卡哈希入 manifest 逐批校验（跑中改卡=中断）。
3. **匹配引擎**=`scripts/backtest/t0_state_match_matrix.py`：对集×状态轴 → 四元组矩阵
   （n / raw / Wilson LB / 区间宽；排序只认 Wilson LB，04 号文 §15）；**n<30=insufficient_no_merge
   禁并格**；逐相位样本数披露（17 §三.5）。
4. **新闻十分位轴 v1 阻断**（实测证据见 §3.4）：研究窗 per-symbol 新闻标注=0 条，
   发布时点审计未过前禁标题模糊匹配造料（8.3/D3 ⑥ 在册项）。
5. **闭卷纪律**：全部研究面止于 2025-09-09 切点（引擎 `enforce_closed_book` 硬拦 +
   矩阵对集 max(trade_date) 断言）；WFE≥50% + Wilson LB 衰减≤30% 双轨（17 §三.2 零改动引用）
   属切点后闭卷考卡的面，本批零触碰。

## 1. 产物清单（本目录）

| 件 | 说明 |
|---|---|
| `rule_cards/r01_fixed_grid_day_t.yaml` | R01 卡（frozen_for_v1_run；grid=100bp 与 M0 同参，触发委托 `run_model_m0` 零重实现） |
| `rule_cards/r02_vol_adaptive_band.yaml` | R02 卡（registered_not_precap：带宽=clamp(k×T-1真波幅, 50bp, 300bp)，k=1.0） |
| `rule_cards/r03_vwap_reversion_band.yaml` | R03 卡（同上：运行 VWAP±50bp 带，typical 价） |
| `rule_cards/r04_open_range_breakout.yaml` | R04 卡（同上：前 K 根 OR，K={1:30,5:6,15:2,30:1,60:1}≈首 30 分钟；stop 进入 fill=max(open,or_high)；目标 100bp） |
| `t0_state_match_matrix_<tag>.csv` | 全交叉四元组矩阵（rule×period×phase×sector_family×mcap_q） |
| `t0_state_match_phase_period_<tag>.csv` | D2 主视图（rule×period×phase） |
| `t0_state_match_phase_coverage_<tag>.csv` | 逐相位样本数披露（含 unrouted 单列） |
| `t0_state_match_meta_<tag>.yaml` | 口径/输入哈希/重算命令（机读） |
| 本件 | 口径真源+重算命令+回执 |

执行件产物（数据面）：`data/backtest_artifacts/t0_rule_engine/t0_rule_manifest_<tag>.yaml`
（显式路径清单，消费禁 glob）+ `t0_rule_pairs_<tag>_b####_<rule>_<P>min.parquet` +
`t0_rule_stats_<tag>.yaml`。**禁 summary.json**（n_trial_ledger glob 污染教训）。

## 2. 重算命令

```bash
# 预检冒烟（20 只，4 规则×5 周期，~25min；r01 对数须与 material_precapacity_sample20_stats.yaml 同值）
python scripts/backtest/t0_rule_engine.py --sample 20 --rule r01,r02,r03,r04 \
  --period 1,5,15,30,60 --batch-size 20 --tag smokesample20

# 全市场 v1（R01×5 周期，5,410 只×2021-09-01→2025-09-09，109 批×50 只断点续跑，Idle 优先级脱管）
python scripts/backtest/t0_rule_engine.py --rule r01 --period 1,5,15,30,60 \
  --batch-size 50 --tag r01_grid100bp_full_v1 --resume
# 中断后重跑同命令即续（manifest 逐批锚点）；跑中禁改 rule_cards/（卡哈希校验=中断）

# 匹配矩阵（全量跑完后）
python scripts/backtest/t0_state_match_matrix.py \
  --manifest data/backtest_artifacts/t0_rule_engine/t0_rule_manifest_r01_grid100bp_full_v1.yaml \
  --out-dir docs/_working/decision_map_campaign_20260924/links/L05_t0 --tag v1

# 测试（36 例：引擎 13 + 矩阵 9 + material_line 回归 14；构造数据零真库）
python -m pytest tests/backtest/test_t0_rule_engine.py tests/backtest/test_t0_state_match_matrix.py \
  tests/backtest/test_t0_material_line.py
```

## 3. 口径（引用零改动）

### 3.1 对集与判据
- 配对=`cost_trio_exam.build_pairs`（同票同日既买又卖计 1 对、配对量=min(Σ买,Σ卖)、全侧 VWAP）。
- 成本=31.2bp 固定口径（CST-T0-001，滑点唯一承担方，模型内零叠加）；净=毛−31.2；
  前置=毛≥30bp；土规=n≥30 才出结论。
- 材料门：M-1/M-2 构造性满足、M-3 not_applicable（直接生成无重放件）、M-4 板别涨跌停门
  （主板±10%/创业科创±20%/北交所±30%，超限剔除计数）。
- 可交易过滤：周期 bar 数下限 {1:200,5:40,15:14,30:7,60:4}；零价 bar 剔（除零契约）。

### 3.2 四元组与排序
- 格行=n、win_rate_raw（net_bp>0 占比，**仅观察列**）、wilson_lb（95%，复用
  `pattern_win_rate_provider._wilson_lower_bound`，禁本地公式顶替）、interval_width；
  **排序只认 Wilson LB**（04 号文 §15）。期望（net_mean_bp）/前置命中率/毛均值=观察披露列。
- n<30 格 verdict=`insufficient_no_merge`，禁并入任何邻格（V3 卡 §8.4 同纪律）。

### 3.3 状态轴
- **相位**：B4 真源 routed 行法定；未路由日=unrouted 单列披露禁并入；ignition 全史 2 日
  → 其格如实 INSUFFICIENT。
- **周期**：{1,5,15,30,60}min，1min 原生，高周期按日内 bar 序数分桶（不按钟面对齐）。
- **板块族**：SW L1（`industry_class` 最新 valid_to IS NULL 快照，32 值含 nan 剔除）。
  **非 PIT 静态观察轴**——单快照回溯映射属前视（SKEL §4 C-F6 缺口如实登记），
  仅可作观察分层不可作信号条件；symbol 缺失=unknown 单列。
- **市值五分位**：`stock_daily_basic` T-1 circ_mv 日截面分位（q1=最小；PIT 对齐：
  当日格用前一日市值）；缺=missing 单列。
- **新闻十分位**：v1 阻断，矩阵 news_axis 列=常量 `blocked_no_pit_symbol_news`。

### 3.4 新闻轴阻断证据（2026-09-26 CH 实测）
- `c3_fundamental.news_data` 研究窗 2021-09-01→2025-09-09：2,841,834 条；
  `related_symbols` 非空条数=**0**（uniq=0）→ per-symbol 活跃度（近 30 日条数）不可构造。
- `c1_market.news_sentiment_window`：symbol 级为"预留"（DDL 注释），研究窗 scope=market。
- 解锁路径：新闻 per-symbol 标注回填 + 发布时点审计（PIT）先行（SKEL 8.3 / D3 ⑥ 在册），
  另立卡；禁标题模糊匹配造料（D-7 同构）。

### 3.5 闭卷与样本外（后续卡预注册引用，零改动）
- 研究语料=[2021-09-01, 2025-09-09]（975 交易日）；闭卷段 253 日零触碰。
- 样本外判据=WFE=OOS/IS≥50%（Pardo）+ Wilson LB 衰减≤30% 双轨并行（17 §三.2）——
  本批矩阵=IS 侧观察层；闭卷考=切点后另卡走卷。

## 4. 规则集报备与排除清单（17 §三.1"规则数先行报备"）

- **v1 执行=1 规则（R01）×5 周期=5 次构建**（与 material_precapacity_report 报备一致，
  23.3h<48h 不触发强制分层）。
- R02/R03/R04 已预注册未执行：单规则全市场单遍建模 ≈21.4h（承同量级外推），
  4 规则齐跑 ≈92h>48h → **触发 17 §三.1 强制分层**。分层方案：
  1. 按规则串行分夜跑（每夜一规则，Idle 优先级）；或
  2. 按周期分层 {1,5} 先行（信息主轴）+15/30/60 次批；或
  3. 向量化改造（≥10×，21.4h→~2h，属优化不属前置）后再并。
  执行前置=各规则独立容量预检报告（预检先行硬规矩）+ 卡状态翻 frozen_for_run。
- 排除（不可规则卡化，另路径）：5.4（tick 面，L05-C11 时区核验前置）、
  9.1 GBM（模型非规则，同族消融义务在册）、9.3 因子族（GPU 条件维候选）。

## 5. 启动回执

- 全市场 v1：见本目录 `T0_STATE_MATCH_LAUNCH_RECEIPT` 节（运行编号/PID/日志路径/ETA）。

## 6. 已登记缺口债

1. 板块族静态快照非 PIT（§3.3）——S1 成分 PIT 落库（L05-C09）前，板块轴只作观察。
2. 新闻轴阻断（§3.4）——解锁路径在册，另卡。
3. unrouted 相位日（研究窗约 40%+ 交易日无相位路由）单列，不参与任何相位格。
4. R02 状态门变体（带宽=f(状态,情绪段)）待 C05 词表裁定/C07 趋势支换源 Owner 门位后另卡
   （D-14 悬案 + 自由度≈1 悬案裁前禁两维展开，SKEL D2 ⑥）。
5. M0 触档即成交偏乐观（无排队/无冲击）——材料线卡 §9.2 披露承袭，判读带此保留。
