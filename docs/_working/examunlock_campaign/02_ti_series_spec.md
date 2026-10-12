---
ttl: task_bound
title: 技术指标族日频基序列物化件规格（本班考试解锁②）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 一、本件替代什么（全资产净零声明，根宪法 §4.1）

替代对象=前役一次性临时件 `.runtime/tmp/st-nightmine-20261010/derive_breadth_series.py`
（2026-10-10 产出 `docs/_working/nightmine_campaign/series/` 现有 7 枚日频序列；无 argparse、
无 depgraph 登记、随 TTL 自然退役）。本班不把该临时件升格为常驻件，而是**只收编其输出契约**
（表头 `trade_date,value`／ISO 日／LF／逐日唯一），并把口径改为**从卡面派生**：列集与窗不再手抄，
读取考试卡 `data_binding.baseline_birth.piece_1_signal_face` 的表.列引用原文而来。

# 二、缺口事实（实测，非读文）

- 20 张 `TDM-E-L1-S2/calibration/17..36_ind_*_high_event` 卡面 `status=blocked_on_impl`，
  `impl_gap` 自书开考前两项验证：①物化序列逐日可复算 ②event flag 列进 `judge_event`；
  并明文"物化接线跑通即转 preregistered 开考，禁改卡面"。
- `SERIES_DIR`（`scripts/backtest/fexam/card_binding.py:74`）实测 7 枚 CSV＝
  blast_ratio／limit_down_count／limit_up_count／max_streak_height／net_breadth／seal_ratio／streak_distribution，
  技术指标族 **0 枚**；7 枚覆盖 2019-01-04..2025-09-09、逐日 1,622 行无缺日。
- 20 卡列集实测自卡面派生得 20 个唯一列名（adosc／pdi_14／ar_26／natr_14／histvol_20／parkinson_20／
  rogers_satchell_20／garman_klass_20／yang_zhang_20／rmi_14／wt1／tsi／rvgi_10／ppo／coppock／
  qqe_14／mfi_14／cmo_14／aroon_up／cr_26），全部命中
  `schemas/categories/market/market_technical_indicator.py` 的 `INSERT_COLUMNS` 与 DDL
  （219／215 列两处集合各 20/20；本班中途一次"4 列查无"是**自家解析伪影**——对 str 做
  `join(map(str,·))` 致逐字符加空格，已按在册正对照法自纠，见本班台账 §自纠）。
- 表面真源＝`c1_market.technical_indicator`，品类 id `market_technical_indicator`
  （`docs/03_modules/_cross_layer/database/business_data_categories.yaml:1659-1674`），
  DDL `ORDER BY (symbol, period, trade_time)`、`ReplacingMergeTree` 无版本列
  （同件 `:39-41` 自述"原 ORDER BY (symbol,period,trade_date) 无法区分日内多根 K 线"）
  ⇒ **同键多版共存**，按日读必走 `anyLast` 去重口径（`card_binding.py:18` 在册 30 倍放大事故铁律）。

# 三、物化口径（零自创：每条指回卡面原文或 DDL）

| 项 | 取值 | 出处 |
|---|---|---|
| 表 | `get_registry().table("market_technical_indicator")` | 表名唯一真源，禁字面量（TABLE-NAME-REGISTRY） |
| 行过滤 | `period='daily'` | `scripts/audit_technical_indicator_columns.py:69-72,119` 在册默认档 |
| 基序列定义 | 该列逐日**全市场等权均值**，非缺格截面 | 卡面 `piece_1_signal_face`／`piece_2_universe`（20 卡同文） |
| 缺格处理 | `IS NOT NULL`，禁前向填充 | 卡面 `piece_2_universe`"缺格=自然缺格，禁前向填充冒充" |
| 去重 | 先按 (symbol, 日) `anyLast` 再跨票 `avg` | DDL 同键多版（§二）＋`card_binding.py:18` |
| 窗 | 2019-01-04..2025-09-09 | 20 卡 `window.in_sample`/`oos_window_ref` 全同；末日=在册闭卷切点（`t0_six_phase_materialize.py:52`） |
| 版本 | 文件名带 `v1`；映射变更升版禁原地改 | 卡面 `piece_1_signal_face`"六段物化件同款纪律：PHASE 版本化" |
| 输出 | `ti_ew_<col>_v1.csv`（表头 `trade_date,value`）＋同名 `.meta.yaml` | 现有 7 枚契约＋六段件 provenance 契约 |
| 逐日截面票数 | 逐日 `n_symbols` **只入 meta/边册，不进 value 列、不做阈值筛** | 本班零自创判据；截面塌缩如实呈报由卡面判据承担 |

# 四、接线位（不新建第二条取数路）

`op_event_flag_rolling_pctile`（`card_binding.py:744`）的底座 `_event_base_series`（`:720`）
硬规 `base_op` 与 `base_csv` 恰选其一；现成先例＝绑定册 `16_max_streak_high_event_v2` 格用
`base_csv: max_streak_height.csv`（`docs/_working/mineloop_campaign/02_binding_book.yaml:267`）。
本班据此产**本班自有绑定册**（`03_binding_book_event20.yaml`），**不改矿考二班属主册**，
也不给 `card_binding.py` 加第三条取数路。`--scores` 按 CLI 强制显式口径写回在册分数册
`docs/03_modules/_domain_backtest/exam_scores_v1.yaml`（only-add，禁改旧行）。

# 五、考尺读数口径更正（供统筹，不替统筹裁）

考试班 §23.3 给矿考二班的规格把 20 卡的堵点记为"甲=`technical_indicator` 未进
`_REGISTERED_TABLES`＋乙=物化件缺失"。**甲对本班实测不成立**：`classify_card` 在
`card_binding.py:252-253` 先要求 `data_binding.signal_table` 存在，20 卡只有
`baseline_birth` 散文形（无 `signal_table`/`signal_column` 键），因此在册尺对 20 卡一律给
`U / no_data_binding_section`，**走不到 `:308` 的配方册闸**；而事件底座算子的表名取自绑定册
args（`:394` 形），运行面本就不依赖 `_REGISTERED_TABLES`。
⇒ 20 卡的真实缺口＝乙（物化件）＋丙（绑定册无 20 格）＋丁（`status` 停在 blocked_on_impl）。
尺只认 `signal_table` 这一形态盲区另记本班台账，是否补尺属判据面改动，本班不自决。
