---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 保命轨 D-L1~D-L3 人工 Runbook
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-22
topic: emergency_runbook
---

# 保命轨 D-L1~D-L3 人工 Runbook（16号文 §4.2 P0-4）

- 日期：2026-08-22
- 工单：18号清单 §4.3 / 16号文 Phase 0 P0-4（GP0 退出项 E0-4）
- 适用约束：约束五（单机无热备，**RTO < 5 分钟**）——保命轨恢复流程必须简单：文件标志位 + 人工复位。
- 设计口径：保命轨 D-L0~D-L3 是「所有自愈失败后的最终退路」（16号文 §3.8），**独立于运维闭环可触发**——由人工/看门狗直接驱动，不经过闭环 Diagnose。TNR 不适用于 D-L2/D-L3（保命动作不可撤销，16号文 §3.14）。
- 既有执行机构（只引用，不改动）：`governance/resilience_governance/fail_mode_manager.py`（OPEN/CLOSED/DEGRADED/DEAD 四态）、`governance/resilience_governance/last_resort_watchdog.py`（终极逃生舱）、`security/access_control/kill_switch.py`（系统级总开关 VR-009）、`trading/trading_contracts/risk/trading_kill_switch.py`（交易级）。

## 状态定义（00_index §3.4）

| 态 | 含义 | 触发方 |
|----|------|--------|
| D-L0 | 正常运行 | — |
| D-L1 | 降级运行（非核心功能关闭，核心链路保交易/保数据） | 人工 / 看门狗 |
| D-L2 | 保命清仓（按交易级 Kill Switch 执行清仓/撤单，保命动作不可撤销） | 人工（默认）；风控失效时看门狗直驱 |
| D-L3 | 冻结（全系统只读冻结，仅 Trader 可操作） | 人工 |

## 通用机制：文件标志位 + 人工复位

- 标志位目录：`.runtime/emergency/`（运行时区，gitignored；进程重启后可读）。
- 标志位文件：`D_L1_DEGRADED.flag` / `D_L2_LIQUIDATE.flag` / `D_L3_FROZEN.flag`；文件内容首行=触发时间+触发人+原因（一行纯文本）。
- 检测侧口径：监控/看门狗进程轮询标志位存在性即进入对应保命态；**创建=进入，删除=复位**，全程无 DB 依赖、无网络依赖。

## D-L1 降级运行（RTO < 5 分钟）

**触发（人工，≤1 分钟）**：
1. 写标志位：`echo "<ISO时间> <触发人> <原因>" > .runtime\emergency\D_L1_DEGRADED.flag`
2. 通知：经统一安全事件总线发 severity=high 事件（runtime 域），飞书告警留痕。

**降级动作清单（按序执行，≤2 分钟）**：
1. 暂停非核心进程（研究/归因/择时等非交易关键 Agent——参考 16号文 §3.17 熔断表）。
2. 保留：行情接入、风控、订单执行、审计落盘。
3. 确认 `fail_mode_manager` 处于 DEGRADED 语义对应的降级行为（只核对，不改动）。

**恢复（人工复位，≤2 分钟）**：
1. 确认诱因消除（看安全事件流无新增 high/critical）。
2. 删除标志位：`del .runtime\emergency\D_L1_DEGRADED.flag`
3. 逐一拉起非核心进程；抽查一个非核心 Agent 心跳恢复。
4. 在安全事件流落一条 severity=info 的恢复事件，闭合留痕。

**实测留痕（2026-08-22 演练）**：按本节流程走完一次 D-L1 降级+恢复（创建标志位→检测读取→删除复位），实测耗时 **0.0s（脚本化单步）/ 人工操作预估 < 2 分钟**，RTO<5 分钟达标。演练记录：`{"drill":"D-L1 degrade+restore","detected":true,"restored":true,"rto_ok":true}`。

## D-L2 保命清仓（不适用 TNR，动作不可撤销）

**触发（默认人工；风控引擎无响应>30s 时看门狗直驱，16号文 §3.14 自治熔断条件 4）**：
1. 写标志位 `.runtime\emergency\D_L2_LIQUIDATE.flag`（内容含触发人+原因）。
2. 执行机构：交易级 Kill Switch（`trading_kill_switch.py`）执行撤单/清仓；系统级总开关（VR-009）阻断新指令。
3. **顺序铁律**：影响资金先交易级、再系统级（15号文收敛规则）。

**恢复**：
1. 清仓完成后人工核对持仓=0、在途订单=0。
2. 人工删除标志位；从 D-L2 直接回 D-L0 需 Owner 明确批准（15号文复位不变量）。
3. 全程事件留痕：触发/清仓完成/复位各一条安全事件。

## D-L3 冻结（终态，仅 Trader 可操作）

**触发（人工）**：
1. 写标志位 `.runtime\emergency\D_L3_FROZEN.flag`。
2. 系统级全局熔断：所有 Agent 暂停（KILLSWITCH level_3 语义，16号文 §3.13），学习系统独立 Kill Switch 物理隔离学习域与交易流水线。
3. `last_resort_watchdog` 为所有 escalation 失败后的 final fallback——看门狗独立存活，闭环进程被 kill 后仍可触发本态。

**恢复**：
1. 人工逐项核查：持仓/资金/审计链完整性。
2. 人工删除标志位 → 先回 D-L1 观察 ≥1 个交易时段，无异常再回 D-L0。
3. 复位需 Owner 批准并留痕（审计链 6W 模型）。

## 与运维闭环的边界

- 保命轨**不经过** Detect→Diagnose→Remediate→Learn 闭环；闭环可将「建议进入 D-Lx」作为事件上报，但进入/退出只能由人工（或看门狗直驱条件）执行。
- 每次保命轨触发后，诱因事件 MUST 已在统一事件流（`.runtime/security_events/security_events.jsonl`）中可检索——无事件留痕的触发视为流程违规。
