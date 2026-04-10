---
module_id: DOCS_09_AUDIT_STATE_BASENAME_COLLISIONS_20260411
standard_type: audit_state
applicable_scope: 同名不同路径（basename · C2 输入）
generated_date: '20260411'
generated_by: scripts/governance/scan_basename_collisions.py
---

# Basename 碰撞报表（同名不同路径）

> **机器真源**：[`BASENAME_COLLISIONS_20260411.json`](./BASENAME_COLLISIONS_20260411.json)
> **范围**：docs/ ｜ **后缀**：`md`
> **候选路径数**：3197 ｜ **发生碰撞的 basename 数**：4

## 说明

- 与 **C1（内容 hash 相同）** 不同：basename 相同**不**表示正文相同，**禁止自动合并**；处置见 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3.3**。
- 下列 **`INDEX.md` / `README.md` 等**在机构式文档树中**常**多份并存；默认单独统计，避免与「意外同名」混淆。

## 摘要

| 类别 | basename 数 |
|------|------------:|
| 非导航名（优先人工审） | 0 |
| 导航名（`changelog.md, contributing.md, index.md, license.md, readme.md, sitemap.md`） | 4 |

## 非导航名碰撞（逐条展开）

*（无 — 当前前缀与后缀下，除导航名外无 basename 碰撞。）*

## 导航名碰撞（统计表）

| basename | 路径条数 |
|----------|----------:|
| `INDEX.md` | 199 |
| `README.md` | 137 |
| `SITEMAP.md` | 5 |
| `CHANGELOG.md` | 2 |
