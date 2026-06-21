---
module_id: KE-3191
title: 14. 可验证性标注
category: documentation
---

# 14. 可验证性标注

14. 可验证性标注

| 条目         | 可验证性 | 验证方式                                                   |
| ---------- | :--: | ------------------------------------------------------ |
| ABS-01     |   A  | file\_operation\_safety\_gate.py 检查 immutable\_core 标记 |
| ABS-02     |   A  | file\_operation\_safety\_gate.py 拦截 AI 删除操作            |
| ABS-03\~04 |   M  | AI 自检 + Session Log 审计                                 |
| ABS-05\~10 |   A  | rule-lifecycle-and-change-protocol.py 检查变更级别                    |
| ABS-11\~13 |   M  | AI 自检（onboarding 流程）                                   |
| ABS-14\~18 |   A  | pre-commit hooks 自动检查                                  |
| ABS-19\~20 |   A  | CI 流水线字段重复检测                                           |
| ABS-21\~22 |   M  | 代码审查                                                   |
| ABS-23\~25 |   A  | pre-commit hooks 编码检查                                  |
| ABS-26\~28 |   A  | git hooks 拦截危险命令                                       |
| ABS-29     |   A  | pre-commit 集成 git-secrets/detect-secrets               |
| ABS-30     |   M  | AI 自检 + 日志审计                                           |
| ABS-31     |   A  | 日志写入前密钥模式过滤                                            |
| ABS-32     |   A  | pre-commit 硬编码密钥检测                                     |
| ABS-33\~34 |   A  | 审计日志 append-only + checksum 校验                         |
| ABS-35\~37 |   M  | AI 自检 + LSG 运行时检查                                      |
| ABS-38     |   A  | 沙箱环境强制执行                                               |
| ABS-39     |   A  | 破坏性命令白名单 + Owner 确认机制                                  |
| ABS-40     |   A  | pre-commit hooks / CI 检查 `threading.Lock` 导入           |
| ABS-41     |   A  | LSG 运行时 fail-closed 策略强制执行                             |
| ABS-42     |   A  | 沙箱创建失败 → 任务 FAILED，不降级                                 |
| ABS-43     |   A  | pre-commit hooks 检查 `shell=True` 调用                    |
| ABS-44     |   A  | pre-commit hooks 检查废墟路径引用                              |
| ABS-45     |   A  | 审计日志系统健康检查 + 关键操作前置校验                                  |
| ABS-46     |   A  | CI 测试套件通过后方可部署                                         |
| ABS-47     |   A  | kill switch 运行时断言，绕过即阻断                                |
| ABS-48     |   A  | 最小权限策略运行时强制执行                                          |
| ABS-49     |   A  | AI 输出校验——实盘数值模糊化检测                                     |
| ABS-50     |   A  | AI 输出校验 + 网络出口白名单拦截外部 API 调用                           |
| ABS-51     |   A  | confirm-action gate——交易决策需Owner确认，建议附带置信区间+回测数据 |
| ABS-52     |   A  | pre-commit hooks——修改前强制重新读取文件全文验证当前版本          |

> **A** = 自动化验证 | **M** = 人工验证 | **S** = 自声明

***
