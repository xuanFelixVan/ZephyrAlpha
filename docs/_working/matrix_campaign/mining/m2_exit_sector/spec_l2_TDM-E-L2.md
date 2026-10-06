---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-00 | TDM-E-L2 板块选择（组骨架）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **L（只登记）**——组节点；但其数据底座判定属本车道核心结论，载于本卡
- 真源: `config/trading_decision_map.yaml#TDM-E-L2`；t3 挖矿 §1.3（29 节点全缺口）+§2-M3

## 1. 组节点结论

子机制拆卡 11 张（见 00 索引）；本卡承载**全族共用数据底座**判定（CH 实测 2026-10-06）：

| 资产 | 物理表 | 列名（DESCRIBE 实测） | 覆盖面实测 | 底座判定 |
|---|---|---|---|---|
| 个股日线 | `c1_market.kline_daily` | trade_date, symbol, open/high/low/close, volume, amount, ... | 1990-12 起 1002 万行 | **主通道原料** |
| 行业归属锚 | `c1_market.industry_class` | symbol, industry_sw, industry_zsi, industry_level, valid_from, valid_to, updated_at, ... | L1 现行快照 10472 行/31 行业（+1 'nan' 坏行已被词表闸拦） | **主通道锚**：×kline_daily 聚合成 31 个申万一级行业指数，PIT 全历史 |
| 板块指数 | `c1_market.kline_sector` | trade_date, code, open/high/low/close, volume, amount | 728 个 880xxx 代码，**2025-07-18 起 ~14.5 个月** | 仅近期校验窗，禁作深回测底座（负结果 #9） |
| 个股资金流 | `c1_market.money_flow` | trade_date, symbol, close, pct_change, main_net_inflow(_pct), super_large/large/medium/small_net_inflow(_pct) | **2021-01-04 起 5781 票**（登记快照"2026-08 起"已过时） | 资金流域可考 2021 起 |
| 行业成分 | `c1_market.sector_constituent` | sector_code, sector_name, stock_code, update_date, valid_from/valid_to | 727 板块/6229 票，月度静态 | PIT 弱，只作 880↔申万桥接候选 |
| 板块快照 | DS-059 `data.sector_snapshot_collector` | —（physical_type=python 模块） | status=candidate/design，**物理不可用** | 涨停梯队类字段走封板掩码代理（负结果 #13） |

**任务问题的直接回答**：行业分类表= `c1_market.industry_class`（industry_sw 列，L1，PIT
valid_from/valid_to）——不是 sector_constituent；"板块表"若指板块 K 线=`c1_market.kline_sector`
（code 列，880xxx）。以上全部经 CH DESCRIBE/uniqExact 实测确认。

## 2. 主通道（M3 首选，全族 S/M 卡共用）

`industry_class`（valid_to IS NULL 快照或 PIT 区间 join）→ symbol→industry_sw 映射 →
kline_daily 逐行业聚合（流通市值加权/等权，市值源 `c1_market.stock_indicator.total_mv` 在册
`_SQL_MV`）→ **31 行业日频 OHLCV/金额宽表**。此宽表是 L2-01 族/02 族/03 族/07 卡的共同输入，
一次构建批级共享（executor T5 pre_tensor 同款 hoist 纪律）。词表=`io_sector_sws_map.yaml`
（sws2021_l1，禁硬编码清单，schema industry_anchor 同款纪律）。

## 3. 考法

组节点无独立考法；全族共同 prereg 项=行业聚合宽表的构建耗时计入信号侧（cost_tier=signal_side），
非每格重算。
