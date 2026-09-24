---
title: "B 班填卡样板七表（st-library-final-20260924 机械生成，禁手抄禁自造）"
ttl: task_bound
date: "2026-09-24"
session: "st-library-final-20260924"
status: "sample_cards_ready"
---

# B 班样板卡（首批七表·07:4x 重建版）

> 生成方式=三真源机械 join（翻译册 plain_zh/词表别名/lib_assets 现状），零手抄。
> 填卡铁律：title_zh 抄禁自起｜plain_zh 照抄翻译册｜tags 枚举内 1-5 禁造词｜
> 三关自检：tags assert 枚举+lookup 抽样+fingerprint 不变，任一失败整批打回。

## 卡 1 龙虎榜
- asset_id: TBL:ch:c1_market.dragon_tiger ｜ title_zh: 龙虎榜（DB 保留）｜ tags: [ch, 行情]
- plain_zh: 照抄翻译册 schemas/categories/market/market_dragon_tiger.py 条目
- 词表别名: 龙虎榜→[LHB] ✅

## 卡 2 龙虎榜席位
- asset_id: TBL:ch:c1_market.dragon_tiger_seat ｜ title_zh: 龙虎榜席位（保留）｜ tags: [ch, 行情]
- plain_zh: 照抄翻译册 market_dragon_tiger_seat.py 条目

## 卡 3 融资融券（两融）
- asset_id: TBL:ch:c1_market.margin_trading ｜ title_zh: 两融数据（保留）｜ tags: [ch, 行情]
- plain_zh: 照抄翻译册 market_margin_trading.py 条目 ｜ 词表别名: 融资融券→margin_trading ✅

## 卡 4 北向持仓
- asset_id: TBL:ch:c1_market.northbound_hold_snapshot ｜ title_zh: 北向持仓快照（翻译册 name_zh 去「表结构」，本班已填）｜ tags: [ch, 行情]
- plain_zh: 照抄翻译册 market_northbound_hold_snapshot.py 条目 ｜ 词表: 北向→[北向资金,陆股通,外资,northbound,北向持仓] ✅

## 卡 5 每日估值
- asset_id: TBL:ch:c1_market.daily_valuation ｜ title_zh: 每日估值（保留）｜ tags: [ch, 行情, 估值]
- plain_zh: 照抄翻译册 market_daily_valuation.py 条目 ｜ 词表: 估值→[valuation]

## 卡 6 股东户数（股东人数）
- asset_id: TBL:ch:c3_fundamental.shareholder_count ｜ title_zh: 股东人数（保留）｜ tags: [ch]
- plain_zh: 翻译册缺位（schema 文件不存在）→第二真源=data_asset_registry DS-218
  （produced_by_job=shareholder_incremental，name_zh=股东人数）按注册事实撰写注出处，禁虚构
- 词表: 股东→[十大股东,holdings,股东户数] ✅

## 卡 7 每日基本面
- asset_id: TBL:ch:c1_market.stock_daily_basic（已核实——初稿猜 c3_fundamental 系错，lookup 实测纠正=「禁自推」价值实证）
- title_zh: 每日基本面 ｜ tags: [ch, 估值]
- plain_zh: 照抄翻译册 market_stock_daily_basic.py 条目 ｜ 词表: 每日基本面→[stock_daily_basic] ✅

## 三关自检（每批必过）+ B 班流程
1. tags 全枚举 assert ｜ 2. 抽 3 卡 lookup 命中 title ｜ 3. fingerprint_sha256 前后一致
每批 20 资产：读卡→Librarian.act("update") 填卡→三关→批次台账→下一批。
potential_consumers 等裁定号 DDL 后开启，只填供给台账有出处者。
