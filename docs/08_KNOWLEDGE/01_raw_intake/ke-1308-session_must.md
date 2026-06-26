---
module_id: KE-1221-----must-002
status: active
title: 每日安检（每次新 session 启动时 MUST 执行）
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 每日安检（每次新 session 启动时 MUST 执行）

每日安检（每次新 session 启动时 MUST 执行）

```
python scripts/lock_files.py check-session <session_id>   # 一键检查所有临时文件
```

或手动扫描：
```
Get-ChildItem -Path D:\ZephyrAlpha -File | Where-Object { $_.Name -match '^_temp|^_check|^_fix|^_phase_|^_deep|^_construction|^_rebuild|^_audit' }
```

发现任何匹配 → **必须先处置再施工**（不帮别人擦屁股，但也不能在脏环境上盖楼）。
