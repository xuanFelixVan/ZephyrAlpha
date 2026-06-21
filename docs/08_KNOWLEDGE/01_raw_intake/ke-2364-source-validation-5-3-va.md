---
module_id: KE-2269----5-3-va-000
status: active
title: 5. Source Validation — §5.3 VALIDATE-C01
category: module_blueprint
---

# 5. Source Validation — §5.3 VALIDATE-C01

5. Source Validation — §5.3 VALIDATE-C01

VALIDATE-C01 (no_hallucinated_sources):
```
check: "ALL context.sources 路径在磁盘上存在"
severity: error
on_failure: auto_fix
fix_hint: "移除不存在的source → 重新assemble"
```

禁止注入不存在文件路径作 source——防止 LLM 幻觉连锁（AP5 直接破解）。
