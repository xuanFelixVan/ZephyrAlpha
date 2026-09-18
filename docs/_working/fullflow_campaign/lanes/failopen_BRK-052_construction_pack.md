---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# BRK-052 施工包 · 告警只评估不升级（auto_escalation=false）

> 车道 `st-ff-failopen-20260918` 只出包不翻 flag。

## 1. 现状

- `config/flags.yaml` §`flags.alerts`：
  `{"enabled": true, "description": "告警规则评估 (基础条件解析可用，Multi-Window 未实现)", "auto_escalation": false}`
- `config/alert_rules.yaml` 有规则面，但评估结果不产生升级动作：告警停在"被算出来"，
  无人被通知、无升级级别、无超时再升级。
- 与本车道本轮实修的 `data/scheduler.py` CH 探活告警同族（**投递返回值被丢弃**，
  见 `failopen_triage.md` §3 关键发现）；BRK-052 是这条病灶在配置层的总闸。
- 配合 BRK-055（外发四类凭据缺，Owner 门位）= 告警链两端都断。

## 2. 缺哪几件实现

| # | 缺件 | 说明 |
|---|---|---|
| E-1 | Multi-Window 求值 | "同一条件在 N 窗内 M 次成立才升级"，防单次抖动升成事故（description 自认未实现） |
| E-2 | 升级动作实体 | 升级目标（值班 / Owner / KillSwitch 前置通知）+ 每级超时未确认则升下一级 |
| E-3 | 投递结果闭环 | 复用 `_deliver_alert_with_latch` 口径：未落盘一律判"未投递"并保留未升级态重试；**严禁先置 `escalated=True` 再发** |
| E-4 | 凭据缺失期的 fail-visible 形态 | 无外发凭据时 = 本地 DLQ/audit 留痕 + 面板红；**不得白名单消警**（裁定#273） |

## 3. 验收判据

1. 注入满足"3 窗 2 次"的假告警 → 升级态逐级推进，每级有审计行；
2. 断开外发通道 → 事件仍可在 `data/audit_trail/` 或 failures/ 回读，且去重/已升级标志**不被置位**；
3. 恢复通道 → 同一事件补投 1 次且不刷屏（沿用 `Alerter` 300s 冷却语义）。

## 4. 风险与回滚 / 翻 flag 前置

- 风险：升级噪声（凭据缺失期反复本地留痕）。缓解：E-1 是前置而非可选。
- 回滚：`auto_escalation=false` 单点回退。
- 前置：E-1..E-3 齐 + §3 三条实测；E-4 需 Owner 凭据（登记即闭环，不计未完成）。
