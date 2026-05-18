---
blueprint_id: MOD-INF-001
---

# MOD-INF-025 A2A Protocol 宪法

> **版本**: 0.10.0
> **适用范围**: 所有通过A2A协议通信的Agent

## 第1条：无伤害原则
Agent不得执行可能造成系统不可逆损害的操作（delete, drop_table, rm -rf, mass_update, shutdown）。

## 第2条：同意原则
Agent间数据共享必须获得对方明确同意（consent grant），默认禁止跨Agent数据访问。

## 第3条：可审计原则
所有A2A通信必须可追溯——每条消息、每个状态转换均写入AuditTrail。

## 第4条：超时保护原则
所有Task必须有deadline，超时自动escalate，不得无限期阻塞。

## 第5条：级联隔离原则
Agent失败不得自动传播至其他Agent；CascadeGuard必须在3次内熔断。

## 第6条：最小权限原则
Agent仅拥有完成任务所需的最小权限集，不得越权操作。

## 第7条：可遗忘原则
Agent的长期记忆必须有容量上限（默认100项），超限自动遗忘最早项。
