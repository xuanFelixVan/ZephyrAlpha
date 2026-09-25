---
ttl: task_bound
title: OBJ_T T1 盘点报告 v0（一次性快照，长期真源=config/tool_inventory.yaml）
status: snapshot
generated_at: 2026-09-22T23:11:59.849194+00:00
---

# T1 工具资产盘点 v0 报告（DESIGN §2.2 登记处）

- total_tools: 122（计数用字段，禁写死散文）
- source_counts: {'capability_cards': 35, 'mcp_servers': 14, 'session_skills': 23, 'builtin_tools': 2, 'script_entries': 48}
- content_sha256: ec5f2445666afd1752dc06fd420d1e7b8ad19bd33208b12983358820bddaa315

## 人工核对栏（勾选后本报告方可作验收证据）

- [ ] 删除族条目 delete_class 逐条抽核
- [ ] mcp servers 与 config/mcp.json 实挂面一致
- [ ] 会话技能扫描缺席项确认（S4 空源留痕）

## extraction_warnings

- scripts_scope:top_level_entry_only:入口清单=顶层 *.py（递归展开属后续批次）
