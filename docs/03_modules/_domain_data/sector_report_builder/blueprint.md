---
blueprint_id: MOD-L00-009
module_name: sector_report_builder
domain: D_DATA
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

# MOD-L00-009 sector_report_builder 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：92号清单 §7.5 + 架构审查报告 §11.5 SEC-01/§11.2 需求对账 + 22号板块轮动 spec。
> 代码：`src/zephyr/data/sector_report_builder.py`

## 0. 定位

板块盘后全景报告器（SEC-01 P1 观测层）——编排已落码库模块（均 import 消费不重复造）→ 日频 sector_report：① Top10 板块榜（涨幅+主力五层资金流+momentum+ranking_score+涨停比+结构强度）；② 5 状态标签（经 mainline_candidates 透传）；③ 涨停梯队（连板高度分档×成分归属）；④ 主线候选（SEC-05 嵌入）；⑤ 虹吸态（sector_siphon 三信号 z-score）。

## 1. 接口

```python
def build_sector_report(
    trade_date: str | date | datetime | None = None,  # None=kline_sector_880 最新数据日（PIT 数据日口径）
    ch_client: Any | None = None,
    config: SectorReportConfig | None = None,
) -> SectorReport
```

CLI：`python -m zephyr.data.sector_report_builder [--date YYYY-MM-DD] [--no-write]`。只读八表：kline_sector_880 / sector_constituent / kline_daily / money_flow / limit_up_down / stk_limit / sector_snapshot / sector_meta。

## 2. 输出契约

`SectorReport`（frozen dataclass，asdict JSON 可序列化）：date/generated_at/rotation_state/watch_score/lead_streak + top_sectors（Top10 榜）+ limit_ladder（涨停梯队）+ siphon（虹吸态）+ mainline（主线候选）+ availability/degraded/notes。

- `report_to_dict()` 结构化 dict + `write_report()` 落 `.runtime/reports/sector_report_YYYYMMDD.json`（运行时产物不入 git）+ CLI 摘要
- 净流入单位=亿元（money_flow **万元口径**实证 ÷1e4，schema COMMENT 标"元"与实值不符；yi_unit 配置可调）
- 涨停梯队双源并集（limit_up_down ∪ stk_limit 触价收封，close ≥ limit_up − 0.005 网格容差）
- 板块名称真源=sector_meta（881xxx 同花顺行业真名，裸码归一 +.SH）；sector_constituent 回显名过滤；880xxx 概念板无中文名→代码直出
- 881xxx 行业板无 K 线→成分股等权/合计聚合合成；880xxx 成分在册但 K 线缺失不合成（官方指数缺口，防代理冒充，notes 留痕）

## 3. 不变量（头注 INVARIANTS 原文）

- 观测层只读：不接交易链路（B-007）
- 单维度缺数据该维度标 availability=unavailable 不炸整体
- PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）
- 净流入单位=亿元（money_flow 万元实证口径÷1e4）
- 涨停梯队双源并集（limit_up_down ∪ stk_limit 触价收封）
- frozen dataclass asdict JSON 可序列化
- 报告落盘 .runtime/reports/（运行时产物不入 git）

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→对应维度降级 notes 留痕不抛；板块全集为空/当日无收益截面→degraded=True；trade_date 格式非法→ValueError（fail-closed）；快照最新日期≠报告日→ranking 维度 unavailable

## 5. 边界（不做）

- MVP 阶段无消费方（候选：IDX-02 Dashboard 板块页 D-02/D-03/D-06、Owner 盘后复盘、.runtime/reports 落盘文件直读）
- 不接交易链路；880xxx K 线缺失不合成代理

## 6. 测试

tests/zephyr/data/test_sector_report_builder.py
