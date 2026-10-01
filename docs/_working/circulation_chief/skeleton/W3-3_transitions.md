---
ttl: task_bound
title: W3-3 三态变迁清单（I/J/K/L/M 五段，10-01 实查 vs 09-26 骨架）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# 三态变迁清单（单列档·W3-3 责任段）

> 口径承 00_skeleton.md §0.1（挖干=built/存疑=partial·design/盲区=missing·登记态）。
> 变迁=骨架三态（09-26/10-01 定版卷口径）→本轮代码级复核三态。升级 3 笔、降级 2 笔、坐实 2 笔、注记级 3 笔。

## 升级（好消息，骨架过时）

| # | 环节 | 变迁 | 证据锚 | 剩余尾巴 |
|---|------|------|--------|----------|
| T1 | **I-07(F82)** 订单结算常驻 | 存疑(P0 断链)→**挖干(接线)** | scheduler.py:816-821→pipeline_events.py:1348(subscribe)/:1121/:1202(maybe_drain_order_daemon，st-circ-a7 2026-09-30) | 运行态流量未实测；PG 面部署与 F86 同题（I_scheduler/F82.md） |
| T2 | **K-15(F124)** 状态词表册 | 盲区(P0)→**登记面建成** | state_vocabulary_registry.yaml 634 行 status:active（W3-E/裁定#398#399）+执法门 state_vocab_registry_gate.py:8 | 门 warn-only 未翻 block（观察期无到期日=自动关闭缺失，K_governance_gates/F124.md） |
| T3 | **M-06(F121)** 研究性三域 | 存疑(design)→**实件+主链消费实证**（Owner 门仍挂） | 四域 37 py 实测；backtest/core/matching_engine.py:804 lazy import execution_simulation.almgren_chriss_impact_model | Owner 追认+四域逐件登记（M_crosscut/F121.md） |

## 降级（坏消息，骨架过乐观）

| # | 环节 | 变迁 | 证据锚 | 风险 |
|---|------|------|--------|------|
| T4 | **I-06(F81)** 监控告警 | 挖干→**存疑（运行载体缺失）** | scripts/*.ps1 全族 grep health_monitor=0；全景 §1.1/§1.2 无 health_monitor 任务/进程（ch_health_probe 属 A 段 CH 探针） | 告警流上游空转传导 F114/F84（I_scheduler/SEG_I.md 行注记） |
| T5 | **L 段运行态（F111/F112）** | 挖干(常驻)→挖干(码面)+运行态空白 | 全景快照无 api_server/app_panel 进程；启动链=I-10 ensureApi（其自身存疑） | 值守面可能整段不在跑（L_frontend/SEG_L.md 段注） |

## 坐实（负向确认，骨架口径失真修正）

| # | 环节 | 变迁 | 证据锚 |
|---|------|------|--------|
| T6 | **J-12(F130)** ml_serve | 盲区(P1，11py 线索)→**盲区坐实**：7 py 全空壳 | find src/zephyr/ml_serve=7 件全 `__init__.py`（J_ai_layer/F130.md） |
| T7 | **J-02(F87)** AI 红线 | 存疑→**存疑加重（外部消费=0）** | 两轮 grep 消费面命中全落在 redline 自身（J_ai_layer/F87.md） |

## 注记级（态不变，口径/证据修正）

| # | 环节 | 注记 |
|---|------|------|
| T8 | J-03(F88) LSG | 挖干维持；两口径漂移：防御"五层"→代码 L0-L8 十层模块（gateway.py:28-32+）；拦截面"4 库注记"→实测 10 域 25 文件 |
| T9 | K-02(F98) GateEngine | 挖干维持；门数 91→实测 gate_id 181/own_scope 143（gate_registry.yaml），机生口径待生成器定版 |
| T10 | J-07(F92) 原问题账本 | 存疑维持；"entry_count=0 空转"无代码锚且审计账 1177 行在——空转判定证据不足，需 PG 复核（J_ai_layer/F92.md） |

## 配套口径漂移（非态变，登记备查）

- I-01(F76)：resource registry 实体 96→101（generated 2026-09-30，机生四源）。
- K-13(F109)：ROOR total_registries=76（:926）/"registry_id"粗 grep 83（含引用非纯条目）——三读数并存禁混写。
- M-01(F116)：SOP 目录实测 11（骨架 12 目录口径）。
- M-04(F119)："L0-L6 唯一真源"落位 docs/_working（临时区）与永久手册定位冲突——建议迁址。
