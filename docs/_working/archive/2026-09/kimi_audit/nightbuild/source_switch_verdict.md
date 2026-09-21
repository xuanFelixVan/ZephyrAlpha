---
ttl: task_bound
rule_form: data
verifiability: manual
title: 数据源切换对决裁决——miniQMT 退役日 93 备忘 §2.2 三选一落地（2026-09-18 下午实测）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
---

# 数据源切换对决裁决（miniQMT 退役 · 93 备忘 §2.2 三选一）

> 实测时点：2026-09-18 13:0x 午后盘（两只终端在线、桥文件实时）。实测脚本与原始数据：`.runtime/bakeoff/`。
> 爆炸半径：tasks.yaml **63 个任务**挂 source=miniqmt，六大能力族。

## 一、实测数据

### akshare 线（外网实拉）
| 项 | 结果 |
|---|---|
| 东财日线主接口 stock_zh_a_hist | **5/5 全挂**（ConnectionError RemoteDisconnected），隔 3s 重试 2 次仍挂——非瞬时限流 |
| 备胎 sina 日线 stock_zh_a_daily | ✓ 2.6s / 13 行（9 月以来全） |
| ETF 1min fund_etf_hist_min_em | ✓ 0.5s / 121 根（上午盘整段精确） |
| 财务 balance_sheet_by_report_em | ✗ TypeError（接口变动） |
| 财务摘要备胎 stock_financial_abstract | ✓ 0.9s / 80 行 |

### QMT 桥线（本地实测）
| 项 | 结果 |
|---|---|
| CH 今日 tick 落地 | **1,163,176 行 / 7,936 标的**（tick_subscriber 在跑=合成线燃料充足） |
| ticks3.csv 快照 | 38,765 行 / 8,402 标的（全市场定时快照语义，非逐笔） |
| quote.csv（29 列 5 档） | ✓ 实时 |
| HTTP 下单桥 127.0.0.1:18901 | ✓ 探活 OK |
| K 线合成通道（ch_tick_kline） | 代码在库、1min 燃料充足；本地聚合演示 0.003s/标的 |

## 二、裁决（§2.2 三选一 → 按能力族分主线）

| 能力族（63 任务分解） | 主线 | 副线 | 依据 |
|---|---|---|---|
| tick / 盘口 / 竞价（tick_data、l2_tick、auction_*、market_breadth_snapshot、index_quote） | **QMT 桥**（唯一线） | — | akshare 无此能力；桥今日已实证活 |
| 分钟族 1-60min（A股/ETF/LOF） | **QMT 桥合成（方案 b）** | akshare 副线 | 收盘即有+零外网依赖 vs akshare 延迟+限流+深度仅数日 |
| 日线族（daily/hfq/weekly/monthly/index/ETF 日线） | **akshare 主线（备胎 sina 必配）** | QMT 合成副线 | akshare 广域成熟但主接口今日实证会断——主备双接口为稳定性下限 |
| 财务族（balance/income/cashflow/indicator/dividend/express/audit/main_business/earnings_forecast/daily_valuation） | **akshare**（唯一线） | — | QMT 桥无财务通道 |
| QMT 独有（futures_position、margin_trading_qmt、futures_kline_qmt、option_greeks/iv、kline_us_daily） | **QMT 桥** | — | akshare 无对等能力 |
| 交叉可切（dragon_tiger_qmt、block_trade_qmt、stock_list、index_weight、sector_list） | **akshare** | QMT | akshare 有成熟接口 |

**一句话**：不是单一赢家——**盘口/tick/分钟/衍生品族 QMT 桥完胜且唯一，日线/财务/广域族 akshare 唯一**；分钟族实测 QMT 实时合成碾压 akshare 外网拉取（收盘即有 vs 限流+浅深度）；日线族今天 akshare 主接口当场断连恰好证明了"主线必须带备胎"。

## 三、落地义务（接线归 residual C1 tasks.yaml + 数据线实现）

1. **tasks.yaml 拆分**（residual 总统筹 C1 独占，本班不代改）：63 任务按上表 `source: miniqmt` → `qmt_bridge` / `akshare` 两列拆分。
2. **桥 K 线族"未实现"→按本裁决实现**（数据线）：分钟族 fetch 接 _call_synth 合成；日线族按副线语义接合成或标明 akshare 主线后桥不承载。
3. **声明面**：policies.yaml `requires_process: XtMiniQmt.exe` → 仅 tick 类任务保留，akshare/桥任务摘除；source_health_check 探针同步。
4. **akshare 线稳定性加固**：日线族主备双接口（em→sina 自动切换）写入 provider——今日主接口断连为实锤依据。
5. **验证门**：切换后第一个收盘（今日 15:30）跑缺口体检（kline_1min/daily/index 当日行数+财务增量），零缺口才算切换完成。
