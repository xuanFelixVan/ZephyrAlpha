---
module_id: KE-385---------rec-008
title: 5. 推荐做法（🟢 REC）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5. 推荐做法（🟢 REC）

5. 推荐做法（🟢 REC）

> 以下行为建议遵守但不强制。违反不触发阻断，但应记录原因。

| #      | 推荐做法                                                  | 原因                        | 来源                            | <br />                        |
| ------ | ----------------------------------------------------- | ------------------------- | ----------------------------- | :---------------------------- |
| REC-01 | 每次修改规则后更新 `document-metadata-index-registry.yaml`     | 保持注册表与实际文件同步              | rule_lifecycle_and_change_standard.yaml  | <br />                        |
| REC-02 | 新增文件后更新 `document-metadata-index-registry.yaml`              | 保持文档清单完整                  | ai-onboarding-guide.md        | <br />                        |
| REC-03 | session 结束前写 Session Log                              | 知识传承不依赖特定 AI 的记忆          | ai-onboarding-guide.md        | <br />                        |
| REC-04 | 移动文件时 commit message 包含 \`moved: old/path -> new/path | reason: ...\`             | 便于搬迁历史追溯                      | trae_029_doc_operation_security.yaml |
| REC-05 | 引用尚不存在的文件时使用 `<!-- PLANNED: path -->` 格式              | 避免推高断链阈值                  | trae_029_doc_operation_security.yaml | <br />                        |
| REC-06 | pre-commit 集成密钥检测工具（git-secrets / detect-secrets）     | 自动化防止密钥入库                 | SOC 2 CC6.1                   | <br />                        |
| REC-07 | AI 输出前自检是否包含密钥模式                                      | 防止 AI 在响应中泄露密钥            | OWASP LLM #6                  | <br />                        |
| REC-08 | 外部内容进入 AI 上下文前标记来源（trusted/untrusted）                 | 为 ABS-37 的执行提供基础          | Cursor trusted/untrusted 分离   | <br />                        |
| REC-09 | AI 禁止奉承 Owner，必须以客观架构师视角参与讨论                          | 奉承导致错误决策被放行，"你说的对"必须跟具体理由 | 讨论文档行为准则                      | <br />                        |
| REC-10 | 每次执行流水线必须重新扫描项目状态，不得复用上次扫描结果                          | 项目状态随时变化，静态快照可能过时         | 升级版指令集-v4                     | <br />                        |
| REC-11 | Pydantic 模型禁止 `Any` 类型字段（边界透传场景除外且需注释）                | `Any` 绕过类型校验，等于放弃结构化约束    | adr-0040                      | <br />                        |

***
