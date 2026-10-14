---
ttl: task_bound
title: 深史回补评估册——daban 双表缺日补齐留证＋史浅根因分解（akshare 30 日窗约束对象更正）＋深史源候选盘点
created: '2026-10-13'
session: st-cdx-sent-20261013
status: assessment_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: daban 深史回补决策落定（执行排期/放弃申报）且随 CONDAXIS-CAMPAIGN 归档
---

# 深史回补评估册（1_L1 §1"daban 浅史回补+缺日修复"两步走之第二步；执行班=st-cdx-sent-20261013）

## §0 结论速览（三条，含一条挖矿册前提更正）

1. **缺日已补齐（本班 2026-10-13 执行，§1 留证）**：真缺日=**09-29/30 两日**——09-25 系中秋休市非交易日（交易日历+kline_daily+stk_limit+akshare 四源互证），挖矿册"三缺日"表述据此更正；daban_board_event FINAL 1,906→2,044 行、22→**24** 交易日（非 25）；daban_engine_load 同根因裂缝同批补齐（0→138 行、22→24 交易日）。
2. **C1/C2 深史≠"永久史浅"——挖矿册前提更正**：akshare 涨停池族"源侧仅存近约 30 交易日"约束的是 **limit_up_pool 表**（真实封单额/首末封时刻/行业等 stock_zt_pool_em 专有字段）；而 C1/C2 真源=daban_board_event=**kline 派生表**（daban_board_event_deriver.py 设计目的即"三缺口历史可推导（代理口径）"，:29-31），原料 kline_daily 1990+/stk_limit 2015+ 库内全史——**深史回补零新外部源、纯仓内推导可得**（era 矩阵见 §2）。
3. **limit_up_pool 表深史=永久史浅（实证）**：EM 原生 push2ex getTopicZTPool 对 30 交易日外日期服务端静默空帧（§3 实证）；该表 C1/C2 零消费（builder 原料表常量 :89-104 两 SQL 均只打 daban_board_event），史浅无情绪线影响。

## §1 缺日补齐台账（证据链）

### 1.1 跑前/跑后计数对照

| 表 | 跑前（FINAL） | 跑后（FINAL） | 备注 |
|---|---|---|---|
| c1_market.daban_board_event | 1,906 行/22 交易日（09-01→10-12）；09-29/30 窗口=0 行 | **2,044 行/24 交易日**（09-01→10-12） | 09-29=68 行（封住 56/触板 68/max 连板 6）；09-30=70 行（封住 56/触板 70/max 连板 7）；既有日逐日行数零变动（09-24=66、09-28=50 前后一致） |
| c1_market.daban_engine_load | 09-29/30 窗口=0 行（22 交易日） | 09-29=68 行、09-30=70 行（**24 交易日**） | 行数=事件数（一事件一负载行），10-08 起与既有日衔接 |

富化完整度（09-29/30 两日 138 行）：first_touch_time 138/138、open_board_count 138/138、seal_amount_proxy 112/138（其余为未封住/无达标 tick，如实空缺）。连板链跨补日连续：24→28→29→30→10-08 的 max_consec=5→5→6→7→8。

### 1.2 命令原文（一次性回补脚本，集成器生产同构链路）

链路=InternalComputeProvider.fetch（table 路由 → collect_derived_events CH 只读推导 / _fetch_daban_engine_load 逐日驱动 ex_core.daban_load_producer.run_daily_batch）→ ch_writer.write_result（调度器写通道同款落库原语）。脚本存 `.runtime/tmp/`（生命周期隔离，跑毕随车道清理），核心段：

```python
payload = FetchPayload(
    table="c1_market.daban_board_event",          # 第二脚本换 "c1_market.daban_engine_load" + extra capability 同名
    symbols=None,
    start=dt.date(2026, 9, 29),                   # 窗口=真缺日（09-25 非交易日不出行）
    end=dt.date(2026, 9, 30),
    incremental=False,
    extra={"capability": "daban_board_event"},
)
for result in InternalComputeProvider().fetch(payload, get_registry().get_policy("internal")):
    assert ch_writer.write_result(result)         # 纯 additive INSERT，零删改；ReplacingMergeTree 同键重放幂等
```

运行输出（留证）：`write_result ok=True rows=138 ... last_key=2026-09-30 / BACKFILL DONE total_rows=138`（事件表单批）；负载表逐日两批 `rows=68 / rows=70`。写通道质量闸例行标注 `quality_gate flagged 61/138 rows (change=61)`（事件行 pct_change 口径与 OHLC 闸的启发式差异，与原 09-22 复通重放同款，非新异象）。reaper keep 登记跑前加/跑毕除（`data/runtime/process_reaper_keep.txt`，会话子串 `st-cdx-sent-20261013`，已核零残留）。

### 1.3 akshare/EM 源侧窗口实证（2026-10-13 当日探测）

| 探测 | stock_zt_pool_em | push2ex 原生接口 |
|---|---|---|
| 2026-09-29 | 57 行 ✓ | tc=52 ✓ |
| 2026-09-30 | 52 行 ✓ | tc=52 ✓ |
| 2026-09-25 | 0 行（非交易日） | — |
| 2026-08-15 | **0 行（静默空帧）** | **tc=0（空池）** |
| 2026-06-01 / 2025-06-01 | 0 行 | tc=0 |

→ 30 交易日窗是**服务端行为**（非 akshare 封装层限制）；检索面声称"EM 接口传日期可查历史"（[东财涨停板专题](https://quote.eastmoney.com/ztb)）被原生实证否定。limit_up_pool 表自身 09-01→10-13 全交易日齐（25 交易日），无缺日。

### 1.4 缺日根因（月末裂缝）

`daban_board_event_derive`（tasks.yaml:1668）schedule=weekend_calibration、incremental=false → 调度窗=**[月初, 今日]**（scheduler.py `_compute_start_date` :2313-2332 全量从月初）。9 月窗最后一次重放止于 09-28（该日有行），09-29/30 两日落窗；10 月重放自 10-01 起——月末跨界日永久落洞。同构裂缝伤及 daban_engine_load_daily（daily_kline 档，增量 last_key 驱动，同样不回看）。治本选项（呈 Owner，本班不动调度器）：①`_compute_start_date` 对 weekend_calibration 档改"近 N 交易日回看窗"（语义改动）；②维持现状+把月末 1-2 日纳入 catchup_guard overdue 检测面（gap_list:114 既有监控零新增路线）。

## §2 daban 事件表深史可得性 era 矩阵（C1/C2 真源，库内实测 2026-10-13）

| 字段族 | <2015 | 2015-01→2021-08 | 2021-09→2026-06 | 2026-07→今 |
|---|---|---|---|---|
| touched/close_sealed/is_one_word/consec_limit/pre_close/limit 价 | ✅（规则推导链：st_stock_list+昨收链，重叠窗 88445 样本 100% 验证） | ✅（ch_stk_limit 2015-01-05 起，2,859 交易日实测） | ✅ 同左 | ✅ 同左 |
| first_touch_time/open_board_count（kline_1min） | None | None | ✅（2021-09-01 起，1,235 交易日实测） | ✅ |
| seal_bid_volume/seal_amount_proxy（tick） | None | None | None（tick_data 2026-01 起但 bid_volume 2026-07 起非空） | ✅ |

C1 公式三输入（触板家数/最高连板/封住率）与 C2 晋级率（daban 自 JOIN consec≥1∩次日 sealed）**全史可得**；E5 炸板潮（开板次数）/E8 修复确认（首触/溢价）样本窗上限=2021-09 起；封单代理类判据样本窗=2026-07 起。

## §3 limit_up_pool 专有字段深史源候选盘点（30 日窗外）

| 候选 | 类型 | 深史可得性 | 标注 |
|---|---|---|---|
| EM push2ex（akshare stock_zt_pool_em 底层） | 免费官方 | 30 交易日外服务端空帧（§1.3 原生实证） | 🌑 近窗滚动 |
| tushare limit_list_d（fd_amount/first_time/open_times） | 付费积分档 | 深史在档但本机 token 无权限（probe 实证留痕，deriver :26-28） | 💰 最贴近既有栈 |
| 同花顺数据中心涨停聚焦（datacenterph） | 免费网页 | 网页面近窗为主，深史未验证 | ⬜ 低优先（无消费方需求） |
| web.archive.org 等网页存档 | 免费存档 | JS 动态页/API 调用基本无快照 | 🌑 |
| Wind/iFinD/掘金/聚宽 | 付费 | 多有涨停池族深史 | 💰 |

**结论**：免费源皆不可得 → **limit_up_pool 表申报永久史浅态**（30 日滚动窗，前瞻增量采集器已在产）；该表当前消费方仅 GAP-F-13 后端数据腿，情绪线 C1/C2 零消费——不触发付费采购提案。若未来 025/引擎侧需要真实封单额深史，首选 tushare 高积分档（💰，另立呈批）。

## §4 三判据影响（校准窗起点，两分支）

- **分支 A（执行 daban 深史重放，本册建议）**：C1/C2 观测数即刻越过 120 门槛（builder :76 `_MIN_OBS`），摆脱 insufficient 降档；250 观测分位窗即刻满窗可用；三判据（Brier 校准/分档单调性/事件命中率）校准窗起点可前移至重放起点（受 era 矩阵约束：全史判据=C1/C2 面；事件判据=2021-09 起；封单代理判据=2026-07 起）。
- **分支 B（不执行，维持 09-01 起点）**：C1/C2 持续 INSUFFICIENT 至约 2027 年 1-2 月（09-01 起 120 交易日）；250 观测分位窗满窗需至约 2027 年 9 月；三判据校准窗起点同等后移——等权重分配 fail-closed 机制继续兜底（builder :76/:199 已支持，非阻塞降级，1_L1 §4 时序裁定原文）。
- 深史重放属重批（分钟/tick 富化逐日 walk），**本班不执行**（授权令范围=评估）：2 日窗实测约 40 秒（含 40 日 lookback 全市场 kline 装载+富化+写库），外推月窗≈10-20 分钟、年窗≈2-4 小时、5 年全史≈10+ 小时——建议按月分块+夜间窗+reaper keep 登记，排期呈 Owner。

## §5 自审闸三态裁定

**裁定=评估完结＋深史执行呈批**。①缺日补齐=已执行已留证（§1）；②"永久史浅"申报对象更正为 limit_up_pool 单表（§0.2/§3），C1/C2 深史改判"仓内可得、待排期"——本册为后续施工的唯一口径真源；③反驳者一问："深史重放会不会改写既有 09-01 起历史值？"——不会：ReplacingMergeTree 同键重放幂等且派生口径同版本（derive_version=v1），分位窗重算导致的全史值变走 emotion_index minor 升版纪律（1_L1 §3.1），与重放本身解耦。
