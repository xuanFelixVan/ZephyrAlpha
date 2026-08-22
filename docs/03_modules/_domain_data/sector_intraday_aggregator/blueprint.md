---
blueprint_id: MOD-DATA-061
module_name: sector_intraday_aggregator
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

# MOD-DATA-061 sector_intraday_aggregator 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：架构审查报告 §11.5 SEC-02 行 + 92号清单 §7.6。
> 代码：`src/zephyr/data/sector_intraday_aggregator.py`

## 0. 定位

盘中板块实时聚合器（SEC-02）——sector_snapshot 30s 轮询字段（582 板块，amount/inside/outside/涨跌家数/涨速）→ 板块资金榜/涨跌家数结构/涨速榜/新开板清单，18-30s 刷新级纯函数聚合器。

## 1. 接口

```python
def aggregate_sector_intraday(
    snapshots: Any,                                  # list[dict] 或 pandas DataFrame 鸭子类型
    previous_board: SectorIntradayBoard | None = None,  # 上轮榜（新开板对照基线，M1-④ 回路逐轮持有）
    config: SectorIntradayConfig | None = None,
) -> SectorIntradayBoard                              # 纯函数，无 I/O 无副作用

def load_latest_snapshots(minutes: int = 5, ch_client=None, ...) -> list[dict]
    # CH 查询异常/客户端不可用→返回 []+log（不抛，对齐 ch_reader 降级语义）
```

调度挂接点：本模块**不注册调度任务**（M1-④ 载体职责，波5 注册）；回路每 18-30s 调 `load_latest_snapshots` + `aggregate_sector_intraday(previous_board=上轮 board)`。

## 2. 输出契约

`SectorIntradayBoard`（frozen dataclass，asdict JSON 可序列化）：asof/n_sectors + 四件输出 + rows/degraded/notes：

1. `inflow_top` 资金榜：窗口成交额增量降序——盘中资金活跃度代理。口径裁定：sector_snapshot 18 采集字段无主力净流入类字段（22号 spec §3.1⑥ 实证），盘后真净流入=money_flow×sector_constituent 聚合（SEC-01 范围非本模块）；880xxx 板块指数 inside/outside 实证为指数自身合成报价 tick 计数（近恒 0-4），不作资金流主口径；行内保留 net_active_buy 估算字段供未来数据源前向兼容，默认不参与排名
2. `breadth` 涨跌家数结构：全市场板块合计 up/down 家数+涨跌比+结构变化量（窗口首尾快照差），板块级 latest 逐行可下钻
3. `speed_top` 涨速榜：最新 zangsu 降序（通达信涨速=近 N 分钟涨幅%，Decimal(10,3) 采集口径）+窗口变化量
4. `new_open_boards` 新开板清单：本刷新周期新晋入榜（资金榜∪涨速榜）而上周期未入榜的板块代码——"开板"=板块新晋浮出水面进入监控榜，非个股涨停开板（sector_snapshot 无个股腿）

## 3. 不变量（头注 INVARIANTS 原文）

- 纯函数聚合（aggregate_sector_intraday 无 I/O 无副作用，同输入同输出）
- 本模块不注册调度任务（M1-④ 载体职责）
- 资金腿口径=成交额增量代理（880xxx inside/outside 不作资金流主口径）
- 市场统计指数（880001-880009）默认剔除出板块榜
- PIT（只读 ≤ 查询时点快照）
- frozen dataclass asdict JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：输入为空/全部非法→degraded=True 空榜不炸；单板块仅 1 条快照→窗口增量为 0/速度 None 不炸（notes 留痕）；CH 查询异常/客户端不可用→load_latest_snapshots 返回 []+log 不抛；timestamp 无法解析的记录跳过不炸
- 无 previous_board 基线→new_open_boards 空集+notes

## 5. 边界（不做）

- MVP 阶段无消费方（候选：SEC-01 板块盘后报告器、Dashboard D-02 板块全景页、SEC-05 主线候选榜盘中修正）
- 不做盘后真净流入聚合（SEC-01 范围）；不做个股开板监控（44号 M1-④ 全市场分钟快照口径）

## 6. 测试

tests/zephyr/data/test_sector_intraday_aggregator.py
