---
module_id: KE-1201-------------------------005
status: active
title: 🔴 PRE-OP：任何操作前必须通过的强制检查（最高优先级 — 高于 FIRST-READ）
category: governance_rule
ttl: permanent
---

# 🔴 PRE-OP：任何操作前必须通过的强制检查（最高优先级 — 高于 FIRST-READ）

🔴 PRE-OP：任何操作前必须通过的强制检查（最高优先级 — 高于 FIRST-READ）

> **在你执行任何 Write / SearchReplace / DeleteFile / 新建操作前，必须先回答以下 3 个机械问题（不需要判断，只需要查）。任一答案 = NO → STOP，执行对应的强制命令。**

| 你要做什么 | 必须先问自己 | 答案=NO时的强制命令 |
|-----------|-------------|-------------------|
| **进入新 session** | Phase 0 检查全部 GREEN 了吗？ | `from zephyr.governance import session_startup; r=session_startup(); print(r['next_action'])` |
| **创建新文件** | 这个文件已经在注册表中了吗？ | `python scripts/scaffold.py module/script/gate ...` |
| **修改已有文件** | 我拿到了这个文件的锁吗？ | `python scripts/lock_files.py acquire <file> <session_id>` |
| **删除任何文件** | 这个文件的每一行内容在别处还有吗？ | RULE-THREE 三步审判 → 全通过才能删 |
| **任何新功能** | 已有脚本/模块覆盖了这个需求吗？ | 搜 `registry_of_registries.yaml` → Grep → 复用决策 |
| **结束 session** | 所有锁释放了吗？临时文件清了吗？ | `python scripts/lock_files.py release-all` + 零残留扫描 |
| **处理任何任务** | 有对应的 Agent Skill 可以加载吗？ | `python -m zephyr.agent_spec list` → 匹配关键词 → `progressive_load(skill_id)` |

> **如果你跳过上表任何一步 → 你的操作可能产生孤儿文件、死锁、重复轮子。这是机械判决，不是建议。**

---
