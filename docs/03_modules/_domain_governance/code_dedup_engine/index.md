---
module_id: MOD-INF-017
title: "代码去重引擎 — 目录索引"
doc_type: index
status: Draft
version: "0.3.0"
layer: L1_foundation
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
created_by: AI
date: "2026-05-05"
ttl: permanent
summary: "code-dedup-engine/ 模块目录索引。全生命周期代码去重系统——从生成时预防到进化沉淀的六阶段闭环。覆盖函数/常量/类/import/部分重复/参数化模板等10+检测维度。增量缓存加速pre-commit。自动修复+SSoT注册+Feedback Loop进化。"
depends_on: []
---

# code-dedup-engine — 代码去重引擎

## 责任声明（Single Responsibility）

本模块负责：**全生命周期代码去重——六阶段闭环（①生成时预防 ②提交时拦截 ③定期扫描 ④自动修复 ⑤SSoT注册 ⑥进化沉淀）。消除 Vibe Coding AI 上下文失忆导致的重复造轮子。覆盖语义级AST相似度检测（函数/常量/类/import/部分重复/参数化模板），增量缓存加速 pre-commit，自动提取到 shared 并验证测试全绿。**。

## 文件清单

| 文件 | 说明 |
|------|------|
| blueprint.md | 代码去重引擎蓝图（MOD-INF-017 v0.3.0 — 全生命周期去重系统） |
| index.md | 本文件 |

## 当前状态

`draft` — v0.3.0 蓝图已升级为全生命周期去重系统，施工待 Wave 1 开工。

## 排除规则

- ❌ 不负责代码格式化/风格检查 → `01_policies_and_standards/`
- ❌ 不负责测试覆盖率 → CI 管线

## 父级目录

- 父级：[基础设施域](../index.md)
