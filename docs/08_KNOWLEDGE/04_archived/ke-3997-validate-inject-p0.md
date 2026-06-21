---
module_id: KE-3844---inject-p0-002
title: 12.3 Validate & Inject P0
category: module_blueprint
---

# 12.3 Validate & Inject P0

12.3 Validate & Inject P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-V1 | token 超 budget 时 violations | 手构造超限 bundle | validate | passed=False, violations 含 "token_overflow" |
| P0-V2 | stale reference 检测 | bundle 含 30 天前 ADR source_trace | validate | violations 含 "stale_reference:..." |
| P0-I1 | Cursor 多通道注入 | ide_id=CURSOR | inject | channels_used 含 prompts + tools + resources |
| P0-I2 | Trae 偏 resources | ide_id=TRAE | inject | channels_used 优先 resources + prompts |
| P0-I3 | Claude-Desktop 全通道 | ide_id=CLAUDE_DESKTOP | inject | channels_used 含 prompts + tools + resources + sampling |
| P0-I4 | 未知 IDE 兜底 prompts | ide_id=GENERIC_MCP | inject | channels_used=[PROMPTS]，channels_skipped 含未支持通道 |
| P0-I5 | 所有通道失败 DEGRADE-003 | mock 所有 channel 注入失败 | inject | ack_received=False，自动丢低优先级 slot |
