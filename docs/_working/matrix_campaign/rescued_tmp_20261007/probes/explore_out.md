---
ttl: task_bound
---

```
== DESCRIBE c1_market.emotion_index ==
name	type	default_type	default_expression	comment	codec_expression	ttl_expression
trade_date	Date			交易日		
stage	LowCardinality(String)			close_final/pre_open（v0.2 预留 auction/intraday_vN）		
ts	DateTime64(3, \'Asia/Shanghai\')			状态时戳（收盘态15:10/盘前09:15）		
emotion_index	Float64			0-1 灰度分位（0=冰点 1=沸点）		
components	String			JSON 数组[{name,raw_value,percentile,weight,status,obs,asof,source,note}]		
version	LowCardinality(String)			语义化版本（成分集/权重变更必须升版）		
ingest_ts	DateTime64(3, \'UTC\')	DEFAULT	now()	入库时间		
source	LowCardinality(String)	DEFAULT	\'live\'	行来源：live=活管道日批；replay=全历史回放班		


== emotion_index head/tail 样本 ==
Row 1:
──────
trade_date:    1991-06-10
stage:         close_final
ts:            1991-06-10 16:10:00.000
emotion_index: 0.90625
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-10", "source": "daban_board_event", "note": "sub_missing=['touched', 'max_consec', 'seal_rate']"}, {"name": "C2_promotion", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.9583333333333333, "weight": 0.5, "status": "ok", "obs": 120, "asof": "1991-06-10", "source": "kline_daily+kline_index", "note": "sub_missing=['index_ret']"}, {"name": "C4_volume", "raw_value": null, "percentile": 0.8541666666666667, "weight": 0.5, "status": "ok", "obs": 120, "asof": "1991-06-10", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-10", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-10", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-09-23 11:21:15.000
source:        replay

Row 2:
──────
trade_date:    1991-06-11
stage:         close_final
ts:            1991-06-11 16:10:00.000
emotion_index: 0.67562
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-11", "source": "daban_board_event", "note": "sub_missing=['touched', 'max_consec', 'seal_rate']"}, {"name": "C2_promotion", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.5785123966942148, "weight": 0.5, "status": "ok", "obs": 121, "asof": "1991-06-11", "source": "kline_daily+kline_index", "note": "sub_missing=['index_ret']"}, {"name": "C4_volume", "raw_value": null, "percentile": 0.7727272727272727, "weight": 0.5, "status": "ok", "obs": 121, "asof": "1991-06-11", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-11", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-11", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-09-23 11:21:15.000
source:        replay

Row 3:
──────
trade_date:    1991-06-12
stage:         close_final
ts:            1991-06-12 16:10:00.000
emotion_index: 0.897541
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-12", "source": "daban_board_event", "note": "sub_missing=['touched', 'max_consec', 'seal_rate']"}, {"name": "C2_promotion", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.9590163934426229, "weight": 0.5, "status": "ok", "obs": 122, "asof": "1991-06-12", "source": "kline_daily+kline_index", "note": "sub_missing=['index_ret']"}, {"name": "C4_volume", "raw_value": null, "percentile": 0.8360655737704918, "weight": 0.5, "status": "ok", "obs": 122, "asof": "1991-06-12", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-12", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-12", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-09-23 11:21:15.000
source:        replay

Row 4:
──────
trade_date:    1991-06-13
stage:         close_final
ts:            1991-06-13 16:10:00.000
emotion_index: 0.928862
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-13", "source": "daban_board_event", "note": "sub_missing=['touched', 'max_consec', 'seal_rate']"}, {"name": "C2_promotion", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.959349593495935, "weight": 0.5, "status": "ok", "obs": 123, "asof": "1991-06-13", "source": "kline_daily+kline_index", "note": "sub_missing=['index_ret']"}, {"name": "C4_volume", "raw_value": null, "percentile": 0.8983739837398375, "weight": 0.5, "status": "ok", "obs": 123, "asof": "1991-06-13", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-13", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-13", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-09-23 11:21:15.000
source:        replay

Row 5:
──────
trade_date:    1991-06-14
stage:         close_final
ts:            1991-06-14 16:10:00.000
emotion_index: 0.745968
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-14", "source": "daban_board_event", "note": "sub_missing=['touched', 'max_consec', 'seal_rate']"}, {"name": "C2_promotion", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.5725806451612904, "weight": 0.5, "status": "ok", "obs": 124, "asof": "1991-06-14", "source": "kline_daily+kline_index", "note": "sub_missing=['index_ret']"}, {"name": "C4_volume", "raw_value": null, "percentile": 0.9193548387096774, "weight": 0.5, "status": "ok", "obs": 124, "asof": "1991-06-14", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-14", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": null, "percentile": null, "weight": 0.0, "status": "missing", "obs": 0, "asof": "1991-06-14", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-09-23 11:21:15.000
source:        replay

Row 1:
──────
trade_date:    2026-10-05
stage:         pre_open
ts:            2026-10-05 09:15:00.000
emotion_index: 0.514124
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": 0.4473684210526315, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "2026-10-04", "source": "daban_board_event", "note": ""}, {"name": "C2_promotion", "raw_value": 1.0, "percentile": 1.0, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.5536, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-04", "source": "kline_daily+kline_index", "note": ""}, {"name": "C4_volume", "raw_value": null, "percentile": 0.504, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-04", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": -0.507569758635499, "percentile": 0.004, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-05", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": 0.10025999999999999, "percentile": 0.9948979591836735, "weight": 0.25, "status": "ok", "obs": 196, "asof": "2026-10-05", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-10-05 00:34:00.000
source:        live

Row 2:
──────
trade_date:    2026-10-02
stage:         pre_open
ts:            2026-10-02 09:15:00.000
emotion_index: 0.511534
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": 0.4473684210526315, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "2026-10-01", "source": "daban_board_event", "note": ""}, {"name": "C2_promotion", "raw_value": 1.0, "percentile": 1.0, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.5536, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-01", "source": "kline_daily+kline_index", "note": ""}, {"name": "C4_volume", "raw_value": null, "percentile": 0.504, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-01", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": -0.507569758635499, "percentile": 0.004, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-02", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": 0.08280000000000001, "percentile": 0.9845360824742269, "weight": 0.25, "status": "ok", "obs": 194, "asof": "2026-10-02", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-10-05 00:34:00.000
source:        live

Row 3:
──────
trade_date:    2026-10-02
stage:         pre_open
ts:            2026-10-02 09:15:00.000
emotion_index: 0.566809
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": 0.4473684210526315, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "2026-10-01", "source": "daban_board_event", "note": ""}, {"name": "C2_promotion", "raw_value": 1.0, "percentile": 1.0, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.5536, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-01", "source": "kline_daily+kline_index", "note": ""}, {"name": "C4_volume", "raw_value": null, "percentile": 0.504, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-01", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": -0.015858778830870834, "percentile": 0.22, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-02", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": 0.07780000000000001, "percentile": 0.9896373056994818, "weight": 0.25, "status": "ok", "obs": 193, "asof": "2026-10-02", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-10-02 00:36:24.000
source:        live

Row 4:
──────
trade_date:    2026-10-01
stage:         pre_open
ts:            2026-10-01 09:15:00.000
emotion_index: 0.566809
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": 0.4473684210526315, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "2026-09-30", "source": "daban_board_event", "note": ""}, {"name": "C2_promotion", "raw_value": 1.0, "percentile": 1.0, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.5536, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-09-30", "source": "kline_daily+kline_index", "note": ""}, {"name": "C4_volume", "raw_value": null, "percentile": 0.504, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-09-30", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": -0.015858778830870834, "percentile": 0.22, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-10-01", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": 0.07780000000000001, "percentile": 0.9896373056994818, "weight": 0.25, "status": "ok", "obs": 193, "asof": "2026-10-01", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-10-02 00:36:24.000
source:        live

Row 5:
──────
trade_date:    2026-09-30
stage:         pre_open
ts:            2026-09-30 09:15:00.000
emotion_index: 0.36591
components:    [{"name": "C1_limitup_temp", "raw_value": null, "percentile": 0.4473684210526315, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "2026-09-29", "source": "daban_board_event", "note": ""}, {"name": "C2_promotion", "raw_value": 1.0, "percentile": 1.0, "weight": 0.0, "status": "insufficient", "obs": 19, "asof": "", "source": "daban_board_event(self-join)", "note": ""}, {"name": "C3_breadth", "raw_value": null, "percentile": 0.6464000000000001, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-09-29", "source": "kline_daily+kline_index", "note": ""}, {"name": "C4_volume", "raw_value": null, "percentile": 0.502, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-09-29", "source": "kline_daily", "note": ""}, {"name": "C5_margin", "raw_value": -0.015858778830870834, "percentile": 0.22, "weight": 0.25, "status": "ok", "obs": 250, "asof": "2026-09-30", "source": "margin_trading(as-of)", "note": ""}, {"name": "C6_news", "raw_value": 0.0, "percentile": 0.09523809523809523, "weight": 0.25, "status": "ok", "obs": 189, "asof": "2026-09-30", "source": "news_sentiment_window(rule)", "note": ""}]
version:       v0.1.0
ingest_ts:     2026-10-01 00:34:00.000
source:        live


== emotion_index 全行数/日期范围 ==
   n       dmin       dmax
8659 1991-06-10 2026-10-05

== emotion_index 版本/状态分布（若列存在） ==
Traceback (most recent call last):
  File "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\Lib\site-packages\pandas\core\indexes\base.py", line 3812, in get_loc
    return self._engine.get_loc(casted_key)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "pandas/_libs/index.pyx", line 167, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/index.pyx", line 196, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/hashtable_class_helper.pxi", line 7088, in pandas._libs.hashtable.PyObjectHashTable.get_item
  File "pandas/_libs/hashtable_class_helper.pxi", line 7096, in pandas._libs.hashtable.PyObjectHashTable.get_item
KeyError: 'name'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "D:\ZephyrAlpha\.runtime\tmp\st-matrix-20261007\emo_explore.py", line 77, in <module>
    main()
  File "D:\ZephyrAlpha\.runtime\tmp\st-matrix-20261007\emo_explore.py", line 55, in main
    cols = desc["name"].tolist()
           ~~~~^^^^^^^^
  File "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\Lib\site-packages\pandas\core\frame.py", line 4113, in __getitem__
    indexer = self.columns.get_loc(key)
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\Lib\site-packages\pandas\core\indexes\base.py", line 3819, in get_loc
    raise KeyError(key) from err
KeyError: 'name'

```
