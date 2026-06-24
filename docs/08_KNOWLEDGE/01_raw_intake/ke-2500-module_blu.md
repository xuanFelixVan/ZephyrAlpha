---
module_id: KE-2405
status: active
title: 6.9 漂移演练手册自动生成
category: module_blueprint
---

# 6.9 漂移演练手册自动生成

6.9 漂移演练手册自动生成

```yaml
drift_runbook:
  description: "每个漂移事件自动生成一份结构化演练手册，供 AI/Owner 按步骤修复"
  content:
    - metadata:
        - "漂移 ID / 模块 / 检测器 / 发现时间 / ROI 评分"
    - diagnosis:
        - "漂移描述（自然语言）"
        - "期望状态 vs 实际状态（结构化 diff）"
        - "根因分析（git bisect 结果 / 关联漂移）"
    - remediation:
        - "修复步骤（若 auto_fixable → 可以直接执行的命令/脚本）"
        - "若 needs_suggestion → 提供 2-3 种修复方案 + 推荐方案 + 理由"
        - "每步的验证方法（修复后如何确认成功）"
    - rollback:
        - "修复失败时的回滚步骤"
        - "回滚验证方法"
    - references:
        - "相关蓝图章节链接"
        - "相关 ADR 链接"
        - "历史类似漂移的处理记录"

  format: "Markdown + YAML frontmatter（机器可解析 + 人类可读）"
  storage: "data/drift_runbooks/<event_id>.md"
  ttl: "漂移 VERIFIED 后保留 30 天作为知识资产"
```
