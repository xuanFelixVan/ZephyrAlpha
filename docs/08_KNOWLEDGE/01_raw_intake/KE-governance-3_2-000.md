---
module_id: KE-governance-3_2-000
title: 3.2 手动检查工具
category: governance
---

# 3.2 手动检查工具

3.2 手动检查工具

| 工具 | 用途 | 适用场景 |
|------|------|---------|
| `ripgrep` | 全文搜索违规模式 | 定向审计时快速定位 |
| `git log --oneline -20` | 查看最近提交 | 审计 commit 格式 |
| `git diff --stat` | 查看变更范围 | 评估审计范围 |
| IDE 诊断 | 类型错误 / lint | 代码质量审计 |
| `pytest --collect-only` | 测试收集验证 | GATE-18 |
