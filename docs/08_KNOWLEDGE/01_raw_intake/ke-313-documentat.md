---
module_id: KE-289
title: 3.4 编码安全
category: documentation
ttl: permanent
---

# 3.4 编码安全

3.4 编码安全

| #      | 禁止行为                                          | 原因                              | 替代方案                                  | 来源                                |
| ------ | --------------------------------------------- | ------------------------------- | ------------------------------------- | --------------------------------- |
| ABS-23 | 用 PowerShell `echo`/`Out-File` 默认参数写 `.md` 文件 | PowerShell 默认编码不是 UTF-8，会导致中文乱码 | 使用 Python 写文件并指定 `encoding='utf-8'`   | AGENTS.md                         |
| ABS-24 | Python 写文件不指定 `encoding='utf-8'`              | Windows 默认编码是 GBK，不指定会写入乱码      | 所有 `open()` 调用必须指定 `encoding='utf-8'` | AGENTS.md                         |
| ABS-25 | 两个编辑器同时打开同一文件编辑                               | 并发编辑导致冲突和编码损坏                   | 一次只用一个编辑器操作同一文件                       | AGENTS.md, ai-onboarding-guide.md |
