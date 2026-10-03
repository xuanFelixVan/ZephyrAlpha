---
ttl: task_bound
title: "期权greeks断供修复报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-2a 期权 greeks/iv_surface 断供修复报告（P0 第一甲）

## 1. 症状与取证

- `c1_market.option_greeks` / `c1_market.option_iv_surface` 停在 2026-09-23（11 天旧数）；同通道 `option_kline`（akshare 主源）鲜至 09-30，`convertible_bond_iv`/`tick_data`（同为 miniqmt intraday）正常 → 通道活、产出步断。
- fetch_perf 取证：两任务自 09-24 起 `status=SUCCESS, rows=0`（静默零值，不报错），integrity_check 自 09-23 起每日报"当日数据不达标"。
- QMT 环境实测（2026-10-04 只读探针）：
  - `xtdata.get_instrument_detail` 对 CH option_kline 近 30 天窗口内 **20/20 活跃合约全量返回 None**（仅能解析 09-23 前到期的旧合约，最新 ExpireDate=20260923）；
  - `get_stock_list_in_sector("上证期权")` 594 只全部为旧合约，活跃代码（10011425+）不在板块表；`get_trading_contract_list` 返回空；`download_sector_data` 刷新无效。
  - 结论：**QMT 模拟环境期权合约册冻结（09-23 后不再收录新合约/无期权权限），环境侧故障**。与 tasks.yaml 中 option_kline 2026-08-14 治本留痕"QMT 模拟账户无期权权限"同根源，09-24 起蔓延到合约元数据层。

## 2. 断点机理

`option_greeks_incremental` / `option_iv_surface_incremental`（miniqmt 源）计算链：

```
_load_option_symbols_from_kline(CH)→OK → _get_option_detail_safe(QMT)→None ⇒ 每合约 return []
```

价格半边本就有降级（`_load_option_close_from_ch` 读 CH option_kline，akshare_sina 喂数鲜至 09-30），但**合约静态元数据半边（标的/行权价/到期日/购沽）无降级路径**，detail=None 直接断链 → 静默 0 行。

## 3. 修复（最小面，单文件）

文件：`src/zephyr/data/implementations/miniqmt_provider.py`

1. `_get_option_detail_safe`：QMT `get_instrument_detail` 返回 None 时，降级 `_get_sina_option_meta`（新浪/上交所期权目录，与 option_kline 主源同族 akshare_sina）；原 QMT 解析体拆出 `_parse_qmt_option_detail`，两路返回同一形状 dict，iv/greeks 下游零改动。
2. `_fetch_sina_option_meta`：`option_sse_greeks_sina` 单合约快照，解析 `交易代码`（如 `510300P2612M05500`：标的/购沽/到期月/行权价）+ 官方`行权价`字段。
3. `_sina_month_expiry`：月度到期日 `option_sse_expire_day_sina` 优先，缺席时按上证 ETF 期权规则（当月第 4 个周三）`_sse_fourth_wednesday` 日历兜底。
4. 持久缓存 `.runtime/cache/option_sina_contract_meta.json`（合约静态属性一经挂牌不变 → 命中零 HTTP；原子写 + merge-on-save 防双任务并发互覆盖；解析失败记 negative 标记 3 天 TTL，防 API 抖动误判永久退市）。

不变式保持：SVX-1-P0（iv 反解失败不落库、greeks 由本行 iv 经 `calc_bs_greeks` 真源导出）、PIT/质量三件套、BufferedWriter 写库链路均未触碰；`data_source` 列诚实标注实际价格来源（akshare_sina）。

## 4. 验证读数

- 单合约管线（10011460.SHO，510300 沽 5.5，20261223 到期）：greeks 4 行 + iv 4 行（09-24..09-30，iv=0.391，delta=-0.885，量纲正常）。
- 生产任务实跑（`python -m zephyr.data run option_greeks_incremental`，2026-10-04 05:04）：`SUCCESS rows=615 elapsed=141s`。
- CH 只读复核 `select trade_date, count() from c1_market.option_greeks where trade_date>='2026-09-22' group by trade_date`：断供窗口回填 **09-24:176 / 09-28:182 / 09-29:189 / 09-30:68** 行（此前停在 09-23:51）。
- 说明：2026-10-04 为国庆休市，新行 trade_date 落在真实交易日 09-24..09-30（补断供窗口），非"10-04 当日行情"；09-25 行缺因上游 option_kline 该日本就无数据（akshare 源缺口，非本修复面）。
- iv_surface 任务同批实跑（05:05）：`SUCCESS rows=572 elapsed=14s`；CH 复核回填 **09-24:162 / 09-28:173 / 09-29:173 / 09-30:64** 行；新窗口 `iv=0` 行数=0、`delta=0` 行数=0（SVX-1-P0 静默零值不变式守住）。

## 5. 遗留与建议（不属本修复面）

1. **环境治本**：QMT 终端重新登录/期权权限订阅恢复后，可整体回切 QMT 合约册（代码无需回滚——detail 优先走 QMT，sina 仅为降级路径）。建议给 QMT 运维方开工单。
2. option_kline 上游 09-25 缺口（akshare 新浪源当日缺数）建议另行核查补数。
3. 深交所期权（900xxx）不在新浪 SSE 目录覆盖内；当前 CH option_kline 无 SZ 合约，不构成缺口，接入时需另行扩展。

## 6. 变更清单

- `src/zephyr/data/implementations/miniqmt_provider.py`（+模块级常量/日历兜底/缓存读写 3 函数；+4 方法；`from pathlib import Path` 导入）
- `data/runtime/process_reaper_keep.txt`（长批防误杀登记 2 行）
- 本报告 + creation_token 登记（CREATE-GUARD）
