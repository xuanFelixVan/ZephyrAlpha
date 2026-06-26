---
module_id: KE-MODULE-BLU-CODEGEN-DIFF-000
status: active
title: 记录所有被 codegen 覆盖但已手动修复的文件及修复 diff
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 记录所有被 codegen 覆盖但已手动修复的文件及修复 diff

记录所有被 codegen 覆盖但已手动修复的文件及修复 diff
fixes:
  - file: "src/zephyr/factor/__init__.py"
    sha256_before_fix: "abc123..."        # codegen 生成的原始 __init__.py
    sha256_after_fix: "def456..."          # 手动修复后的 __init__.py
    fix_description: "补全 FactorRegistry/autodiscover_factors 导出"
    fix_source: "session-20260505-005"     # 哪个 session 做的修复
    detection:
      current_sha256: "abc123..."          # ← 引擎运行时检测到的当前值
      status: "OVERWRITTEN"                # OK | OVERWRITTEN
      overwritten_by: "codegen-v2.3.0"     # 推断的覆盖源
```
