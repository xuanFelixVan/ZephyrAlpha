---
ttl: task_bound
title: LANE-CAGE · 桥路径价格笼子静默失效（UNKNOWN 原价通过）复证与 fail-closed 治本
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-CAGE
status: 进行中（复证已成立；修法/证尺/同族扫描见正文各段）
---

# LANE-CAGE · 桥路径价格笼子治本

> 缺陷源自九环节深挖判最要命一条（L07 深挖 s3_qmt_bridge_client，登记于 LEDGER W3-1）。
> 本册逐段随做随写。禁裸"裁定#<数字>"引用（涉此规者以"编号见 ruling_registry"表述）。

## 段1 · 复证（成立）

**调用签名 vs 实现形参核对**（证据为盘上工作树实读，含 BUILD2 在途改动）：

- 实现真源 `src/zephyr/ex_core/price_cage.py:153` 形参：
  `check_price_cage(side, limit_price, symbol, ask1=None, bid1=None, last_price=None, prev_close=None)`。
- 桥消费点 `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:627`（修复前）：
  `cage = check_price_cage(order.side, order.limit_price, order.symbol)` —— **仅传 3 参，四个基准价形参全默认 None**。

**UNKNOWN 从何而来**：`_resolve_base_price`（price_cage.py:123）在 ask1/bid1/last/prev_close 全为
None（或 <=0）时返回 None；`check_price_cage:186-195` 见 base is None → 直接返回
`CageStatus.UNKNOWN, clamped_price=limit_price`（原样回填委托价）。⇒ 桥路径 **恒 UNKNOWN**。

**下游如何处置 UNKNOWN（=静默放行的根因）**：消费点仅 `if cage.status == CageStatus.CLAMPED` 记一条
warn（:628），UNKNOWN 无分支；随后 `price = float(cage.clamped_price)`（:636）= **原价**，写进指令行进桥。
即"未知＝通过"，2% 价格笼子在唯一在产通道上 0 防护。原注释 :621 自述"降级无盘口：UNKNOWN 原价通过"，
把缺陷当设计写死。

**旁证一致**：EXE-2 C-GATE-01 / L07-s2_order_pipeline §②（同一次调用两通道语义不同：miniqmt 传齐基准价真校验、
文件桥三参恒 UNKNOWN）、历史深评 rpt_x05 P1-1 / rpt_x08 B / #ARCH-355 备忘，四处独立指认同一点。

**为何恒缺基准价**：`QmtFileBridgeBroker` 构造（:395）无任何行情/基准价入参，桥件本身不持实盘 order book。
但**同族已存在真源**——`qmt_file_bridge_quote.py` 的 `QmtFileBridgeQuoteProvider` 读 QMT 沙箱 `quote.csv`
（含 ask1/bid1/last_price/last_close 且带 `is_fresh()` 新鲜度闸），CONSUMERS 已注 trading_session/start_paper_session。
⇒ 修法=接此真源喂基准价，而非继续降级放行。

**与 BUILD2（TRD-A10）袋的冲突判定**：`git diff` 核 BUILD2 在 `submit_order` 只改了 `read_only` 守卫与
`_submitted_at_ms` 记录两处，价格笼子块（:621-636）为**未触碰上下文**；我的改动纯增量落在该块 + 一个新私有
helper + `__init__` 增一个可选参 + 一条同族 import，**不与 BUILD2 袋重叠、不回退其任何改动**。判断=不冲突。

## 段2 · 修法与 fail-closed 语义

（随做随写）

## 段3 · 证尺（红/绿两向）

（随做随写）

## 段4 · 同族"未知即放行"清单

（随做随写）

## 段5 · 外部双源与交易所口径

（随做随写）
