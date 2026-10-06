---
campaign: matrix-20261006
lane: E-exam-w2
ttl: task_bound
---

# state_recognizer_exam_v1 — 市场状态识别器（HMM 四态）准确度考试报告

- lane：J道（市场状态识别器专项，非个股 IC 范式）｜ 生成：2026-10-06T12:18:20.721795+00:00
- 考窗：2019-04-01..2026-08-31（2026-09 为前向缓冲）｜ 大盘代理：000300 收盘（`c1_market.kline_index`；施工单拟查的 `kline_daily` 实测无 000300，等权 fallback 未触发）
- HMM 态：`c1_backtest.regime_snapshot_history`（同日多快照取末笔，PIT 按表设计）｜ prereg 判据开跑前冻结于本册 yaml 头部，禁看分改
- 样本：1801 个交易日｜ HMM 态分布：{"ranging_low_vol": 646, "trend_up": 575, "ranging_mid_vol": 335, "trend_down": 245}
- realized 态分布（冻结定义）：{"trend_down": 930, "trend_up": 554, "ranging_mid_vol": 317}；ranging_low_vol 恒空（定义推论，见 yaml）｜ fwd60 尾部 NaN 丢 39 行

## 总判：**不合格**（①②③ 任一未过即不合格，prereg 冻结规则）

| # | 判据（冻结） | 实测 | 判定 |
|---|---|---|---|
| ① | trend_up 态 P(fwd20>0)≥55% | 52.17% | FAIL |
| ② | trend_down 态 P(fwd20<0)≥55% | 49.80% | FAIL |
| ③ | 混淆对角占比≥40% | 20.62% | FAIL |
| ④ | median|lag|≤5 交易日 | 4.5 交易日 | PASS |
| ⑤ | 四指标全面不劣于 SMA200 | 2胜2负（见考卷4） | FAIL |

## 考卷1 命中率表（forward 收益 vs 000300 线）

| HMM 态 | n | fwd5 均值/中位/胜率 | fwd20 均值/中位/胜率 | fwd60 均值/中位/胜率 |
|---|---|---|---|---|
| ranging_low_vol | 646 | +0.0013 / +0.0005 / 50.77% (n=646) | +0.0006 / -0.0070 / 44.89% (n=646) | +0.0132 / +0.0010 / 50.39% (n=641) |
| ranging_mid_vol | 335 | -0.0001 / +0.0027 / 53.13% (n=335) | -0.0012 / -0.0027 / 47.16% (n=335) | +0.0098 / -0.0042 / 47.76% (n=335) |
| trend_up | 575 | -0.0004 / -0.0006 / 49.22% (n=575) | +0.0070 / +0.0020 / 52.17% (n=575) | +0.0097 / +0.0026 / 52.13% (n=541) |
| trend_down | 245 | +0.0028 / +0.0028 / 53.06% (n=245) | +0.0021 / +0.0007 / 50.20% (n=245) | +0.0027 / +0.0065 / 53.06% (n=245) |

要点：trend_up 态 fwd20 胜率 52.17%（未达 55% 线）；trend_down 态 fwd20 胜负比反挂（P(负)=49.80%，均值 +0.21%——喊熊日随后平均上涨）；两档震荡态 fwd20 胜率均 <50%。

## 考卷2 混淆矩阵（HMM 行 × realized 列，行归一化）

| HMM \ realized | ranging_mid_vol | trend_up | trend_down | 行合计 |
|---|---|---|---|---|
| ranging_low_vol | 0.170(110) | 0.279(180) | 0.551(356) | 646 |
| ranging_mid_vol | 0.155(52) | 0.316(106) | 0.528(177) | 335 |
| trend_up | 0.179(103) | 0.343(197) | 0.478(275) | 575 |
| trend_down | 0.212(52) | 0.290(71) | 0.498(122) | 245 |

- 对角线占比：**20.60%**（判据≥40%，均匀随机 25%）——未过
- 类失衡警示：多数类 trend_down 占 51.64%（零模型基线）；realized ranging_low_vol 恒空，实际 4×3 矩阵。即便按多数类基线读数，HMM 对角占比仍不足其一半，结论稳健

## 考卷3 换挡及时性（realized 转折 38 个 vs HMM 原始变化点 128 个）

| 指标 | 数值 |
|---|---|
| 真实体制转折数（前后段≥5 日） | 38 |
| HMM 原始变化点数（无持续过滤） | 128（≈真实转折 3.4 倍，抖动偏大） |
| median \|lag\| | **4.5** 交易日（判据≤5，PASS） |
| mean / P90 / max \|lag\| | 7.89 / 20.0 / 20.0（±20 截断） |
| \|lag\|≤5 占比 | 52.63% |

## 考卷4 基线对照（SMA200 土办法，同口径）

| 指标 | HMM | SMA200 | HMM 不劣于？ |
|---|---|---|---|
| ① trend_up 态 P(fwd20>0) | 52.17% | 51.04% | ✓ |
| ② trend_down 态 P(fwd20<0) | 49.80% | 55.42% | ✗ |
| ③ 混淆对角占比 | 20.60% | 42.70% | ✗ |
| ④ median|lag|（交易日） | 4.5 | 20.0 | ✓ |

- SMA200 画像：③=42.67%（接近多数类基线，靠吃 trend_down 51.6% 份额）但 ④ 惨（median 20=触截断，慢半拍是均线的天性）；HMM ④ 快但准头塌。⑤=2胜2负，不构成全面压过。

## 附赠 情绪层盘点

- **MOD-ALT-EMOTION-INDEX-BUILDER**：blueprint=docs/03_modules/MOD-ALT-EMOTION-INDEX-BUILDER.md（Draft；depgraph 五图对齐 production，2 file 节点）；代码 `src/zephyr/alt_data/emotion_index_builder.py`；落表 `c1_market.emotion_index` 实测 8659 行（1991-06-10..2026-10-05），考窗内 1801 行（close_final/v0.1.0）。
  - 能考/缺口：现在能考——考窗 1801 个交易日全覆盖（close_final/v0.1.0），可与 HMM 态逐日对齐做情绪-体制联动考；缺 prereg 及格线与版本稳定性承诺（v0.1.0 evolving，1991 年起回填段质量未验），考分只能证窗内联动不能证可上线。
- **news_score_daily**：实测 **不存在**（system.tables 无此名）。最接近真源：`c3_fundamental.news_sentiment_score` 7947739 行事件级（2010-01-02..2026-10-04）、`c3_fundamental.news_data` 8118037 行、`c1_market.news_sentiment_window` 19,831 行（night 窗：symbol 19,635 + market 仅 196）。
  - 能考/缺口：现在能考（间接）——事件级 795 万行可按日聚合出情绪曲线再考与 regime 的区分力，聚合口径需先 prereg；缺日频落地表 news_score_daily（实测 system.tables 无此名）；market 级日窗仅 196 行，覆盖太薄。

## 判读注记（诚实披露）

> 纪律：CH 全程只读；零既有文件改动、零 git 操作；临时脚本=.runtime/tmp/st-matrix-20261006/；prereg 冻结块与 .runtime/tmp/st-matrix-20261006/prereg_snapshot_v1.yaml 逐字一致。
