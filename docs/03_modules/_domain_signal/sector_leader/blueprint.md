---
blueprint_id: MOD-SIG-062
module_name: sector_leader
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

# MOD-SIG-062 sector_leader 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：22号 spec §3.1⑦ 步骤① 龙头识别 + 架构审查报告 §11.5 SEC-04 行 + 92号清单 §7.7。
> 代码：`src/zephyr/signal_ashare/sector_leader.py`

## 0. 定位

板块龙头识别器——板块内个股角色四档定位（观测先行不接交易）：龙头 leader（×1.5，连板高度最高且≥2 板）/ 中军 backbone（×1.2，成交额板块 Top3 + ret_20d>0 + 当日非连板）/ 跟风 follower（×0.8，当日红盘且非前三档）/ 中位股 neutral（×0 禁区，3-5 板非龙头跟风=55188 死亡区域强制规避；其余无特征个股同归）。

## 1. 接口

```python
def identify_sector_leaders(
    trade_date: str | date | datetime | None = None,  # None=kline_daily 最新数据日（PIT 数据日口径）
    sector: str | None = None,                        # 单板块代码（如 "881319.SH"）；None=全板块扫描
    ch_client: Any | None = None,                     # None=延迟取 ch_writer.get_client，不可得→degraded
    config: SectorLeaderConfig | None = None,         # 四档传导权重与阈值（22号 §3.1⑦ 定稿值）
) -> SectorLeaderBoard
```

只读三表：kline_daily / stk_limit / sector_constituent（SCD-2 时点过滤）。

## 2. 输出契约

`SectorLeaderBoard`（frozen dataclass，asdict JSON 可序列化）：trade_date + `sectors: list[SectorRoleGroup]`（per 板块 leader/backbones/followers/neutrals + n_neutral_total + annotation 无龙头中文注解）+ n_sectors/n_stocks/degraded/notes。

`StockRoleEntry`：symbol/sector_code/role（leader/backbone/follower/neutral）/weight（config 四档值透传）/score（0-100 合成）/consec_limit（连板高度，0=当日未封板）/amount/pct_change。

评分（2026 社区五维框架，MVP 取前三维可得数据）：情绪 30%（0.6×连板高度板块内分位+0.4×当日涨幅分位）+ 地位 25%（成交额分位）+ 形态 20%（0.5×5 日动量+0.5×20 日动量分位）→0-100 按可用维度权重重归一；筹码 15%/基本面 10% 权重入 config 留扩展口（MVP 不参与归一）；分位采用中秩（mid-rank）ties 约定（对齐 MOD-SIG-060/sector_momentum 口径）。

## 3. 不变量（头注 INVARIANTS 原文）

- 观测先行纪律：只出四档榜单+评分，不接交易/不出买卖点（92号 §7.7 原文）
- 四档传导权重 1.5/1.2/0.8/0 走 config（SectorLeaderConfig），不硬编码进消费方
- 连板高度=stk_limit.limit_up×kline_daily.close 收盘封板连续推导（0.005 价格网格容差，对齐 MOD-SIG-060 炸板判定口径）
- 当日涨幅=相邻收盘推导（kline_daily.pct_change 列 2026-08-22 实证全 0 未填充，不用）
- 无龙头板块→leader 档空+中文注解（不强行封龙）
- 中位股=3-5板非龙头跟风（55188 死亡区域，×0 强制规避）
- PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）
- frozen dataclass asdict JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→degraded=True 空榜不炸；stk_limit 缺失→连板维度降级（全宇宙按 0 连板处理+notes 留痕，各板块出无龙头注解）；成分股缺失→degraded；trade_date 格式非法→ValueError（fail-closed）；个股当日无 K 线→跳过计数留痕
- 连板推导窗口截断（默认 45 自然日≈30 交易日）按窗长上限留痕
- limit_up NULL=无涨跌幅限制→非涨停日

## 5. 边界（不做）

- MVP 阶段无消费方——观测先行不接交易（候选：SEC-01 板块盘后报告器、Dashboard D-05 龙头/中军/跟风榜、远期 daban sleeve §3.1⑦ 步骤② 加权传导）

## 6. 测试

tests/signal_ashare/test_sector_leader.py
