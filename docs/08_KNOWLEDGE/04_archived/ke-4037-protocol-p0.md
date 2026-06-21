---
module_id: KE-3884----p0--------5-003
title: 13.4 Protocol 解耦 P0（关键，遗漏 #5 对应）
category: module_blueprint
---

# 13.4 Protocol 解耦 P0（关键，遗漏 #5 对应）

13.4 Protocol 解耦 P0（关键，遗漏 #5 对应）

| # | 用例 | 预期 |
|:-:|------|------|
| P0-P1 | 用 Mock ContextAdjustActionProtocol 验证调用 | FLE 不 import CE 实现类 |
| P0-P2 | 下游未注入时缓冲 | context_action=None 时写 pending_actions.ndjson |
| P0-P3 | 下游调用失败时缓冲 | 抛异常后同上 |
| P0-P4 | replay_pending_actions 回放成功 | expires_at 内的 action 全派发 |
| P0-P5 | expires_at 过期丢弃 | 过期 action 不派发 |
