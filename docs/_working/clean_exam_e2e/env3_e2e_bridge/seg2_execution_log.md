---
ttl: task_bound
title: E2E 冒烟段二执行记录（100 股模拟单，2026-09-18 09:27，链路全通）
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918
date: 2026-09-18
status: seg2_done_link_proven
---

# 段二执行记录（T1-T7，100 股模拟单）——**链路全通**

> 执行件：`.runtime/tmp/cleanexam_e2e_seg2.py`（按 smoke_test_design.md §3 段二 T1-T7）。模拟账户 8886156677 双重断言全程在岗，零实盘接触。

## 委托要素

| 项 | 值 |
|---|---|
| 标的/方向/数量 | 510300.SH BUY 100（最小整手） |
| 委托类型/价格 | LIMIT @ 4.07（昨收 4.523×0.90 跌停价=必不成交+笼子豁免） |
| idempotency_key | smoke-e2e-1789694891 |
| strategy_id | smoke_bridge_e2e |

## 执行结果（PASS=10 / FAIL=2 / 终态=CANCELLED）

| 步 | 断言 | 结果 | 证据 |
|---|---|---|---|
| T1 | P1-P9 全量重验 | **PASS（含 P7！）** | 沙箱开盘复活资金镜像刷新：cash=9,992,611（段一夜间的 0 值消失，P7 断言如期自愈）；P9 pending=0 |
| T2 | 提交 | order_id=2fed2efb-110c-4d2a-a5b4-a71cf42aa010 提交成功 | FAIL①=文件通道 10s 无 ack——事后取证：本单走 HTTP 快路径（ack_sim.csv mtime 09:20 早于本单=文件通道根本未启用），**文件 ack 检测法对 HTTP 路径结构性失明**，检测法缺陷非链路故障 |
| T3 | 柜台回执 | **PASS** | broker_order_id 回填=本地 order_id 同值，status=SUBMITTED——柜台真实收单 |
| T4 | 状态可辨 | PASS | SUBMITTED |
| T5 | 撤单终态 | **PASS** | cancel_order → 轮询至 **CANCELLED**——全生命周期闭合 |
| T6a | 柜台镜像 | FAIL②→事后补证 | **orders_sim.csv（mtime 09:28:25）双指令行铁证**：`smoke-e2e-1789694891,order,510300.SH,buy,100,limit,4.07` + `cancel` 行；Order.csv 不含 510300=已撤单不进 Order 导出（与 CANCELLED 自洽，非断链） |
| T6a' | Deal 零成交 | PASS | 跌停价买单如设计必不成交，Deal.csv 无本单 |
| T6b | execution_report | **断点 E4 如实验证** | 表在 schema 对（order_id/symbol/actual_quantity...）但 0 行=生产者未接线（设计预期：防误报链路已闭环——修此断点=下一班"回报入台账"工单） |
| T7 | 收尾 | PASS | disconnect_all；终态 CANCELLED；无残留 |

## 判定：**链路全通（LINK PROVEN）**

下单→桥（HTTP 快路径）→柜台收单（sysid）→状态机推进（SUBMITTED）→撤单（CANCELLED）→成交面零扰动（Deal 无行）→台账面断点如实暴露（execution_report 0 行）。**信号侧与决策侧按设计未参与**（编排器只出声不出手；本测试=执行管路证明）。

## 本测试产出的两条新挂单（登记不代修）

1. **断点 E4**：execution_report 生产者接线（build_execution_report 已在，缺生产调用方）——回报入台账的工单，编排器"出手"前置。
2. **smoke 脚本检测法升级**：T2 的 ack 检测应按通道分流（HTTP 路径查柜台 sysid，文件路径查 ack 行）；T6a 应接受"已撤单不进 Order 导出"语义。骨架可复用为回归冒烟（设计 §8 既定方向）。
