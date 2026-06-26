---
module_id: KE-3272
title: 3.5 Git 操作安全
category: documentation
ttl: permanent
---

# 3.5 Git 操作安全

3.5 Git 操作安全

| #      | 禁止行为                       | 原因                       | 替代方案                                         | 来源                     |
| ------ | -------------------------- | ------------------------ | -------------------------------------------- | ---------------------- |
| ABS-26 | `git add .` 或 `git add -A` | 可能提交不该提交的文件（临时文件、密钥等）    | 逐个 `git add <具体文件>`                          | ai-onboarding-guide.md |
| ABS-27 | `git commit --no-verify`   | 绕过 pre-commit hooks，门禁失效 | 修复 pre-commit 报错后正常提交                        | ai-onboarding-guide.md |
| ABS-28 | `git push --force`         | 覆盖远端历史，不可恢复              | 使用正常 push 或 `--force-with-lease`（需 Owner 批准） | ai-onboarding-guide.md |
