---
module_id: KE-1732------------------------d--002
status: active
title: 2.18 文件底层属性漂移——编码、换行符、权限（决策 D-023-27）
category: module_blueprint
---

# 2.18 文件底层属性漂移——编码、换行符、权限（决策 D-023-27）

2.18 文件底层属性漂移——编码、换行符、权限（决策 D-023-27）

> **决策 D-023-27**：文件内容可能完全一致但底层属性不一致——编码（UTF-8 BOM vs 无BOM）、换行符（CRLF vs LF）、文件权限（可执行位）——这些都可能导致跨平台问题且对 git diff 不可见。
>
> **决策依据**：AI 施工在不同 session 中可能在 Windows/Linux 间切换，产生换行符不一致。这是氛围编程社区的经典痛点——"在 Windows 上拉了 Linux 项目的代码，AI 改完提交，CI 在 Linux 上跑挂了"。

```yaml
file_attribute_drift:
  encoding:
    description: "UTF-8 BOM / UTF-16 LE / UTF-16 BE / Latin-1 等编码不一致"
    method: "chardet / cchardet 检测文件编码 → 与项目标准（UTF-8 无 BOM）对比"
    severity: MEDIUM
    auto_fixable: true
    auto_fix_action: "自动转换为 UTF-8 无 BOM"

  line_ending:
    description: "CRLF (Windows) vs LF (Unix) 混用"
    method: "检测文件中的 \r\n 出现频率 → 若同时存在 \r\n 和纯 \n → LINE_ENDING_MIXED"
    severity: MEDIUM
    auto_fixable: true
    auto_fix_action: |
      转换为 LF（Unix 标准）——写入 .gitattributes 强制 LF。
      不自动改已有文件（避免 diff 噪声），仅在 .gitattributes 中声明策略。

  file_permissions:
    description: "可执行位不一致——.py 文件不应该有 +x（除非是 CLI 入口脚本）"
    method: "检查 src/zephyr/**/*.py 的可执行位 → 非 __main__ 入口不应有 +x"
    severity: LOW
    auto_fixable: true

  gitattributes_enforcement:
    description: ".gitattributes 文件是否覆盖了所有关键文件类型的换行符/编码声明"
    check: "*.py text eol=lf / *.yaml text eol=lf / *.md text eol=lf"
```
