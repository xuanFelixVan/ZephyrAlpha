---
module_id: KE-governance-ttl-003
title: 一、TTL 分级定义
category: governance
---

# 一、TTL 分级定义

一、TTL 分级定义

| TTL 值 | 含义 | 适用场景 | 过期处理 |
|--------|------|---------|---------|
| `permanent` | 永久有效 | 治理规范、架构视图、ADR、知识库条目 | 不过期，需要 Owner 明确废弃 |
| `30d` | 30 天后过期 | 审计报告、状态快照、迁移报告 | 过期后移入 `09_audit/archive/` 或直接删除 |
| `7d` | 7 天后过期 | 临时工作文件、草稿、中间产物 | 过期后直接删除 |
| `session` | 本 session 结束后删除 | 临时脚本、一次性工具、session 内草稿 | session 结束时必须删除，不得提交到 git |
