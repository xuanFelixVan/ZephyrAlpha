---
module_id: KE-agent_inst-6_16____________static_manifes-000
title: 6.16 静态清单自动生成铁律（Static Manifest Auto-Generation Mandate）
category: agent_instruction
---

# 6.16 静态清单自动生成铁律（Static Manifest Auto-Generation Mandate）

6.16 静态清单自动生成铁律（Static Manifest Auto-Generation Mandate）

> **v1.0.0（2026-05-04）**：对标 K8s code-generator / Terraform terraform-docs / OpenAPI codegen——五家顶级机构一致：重复性清单不允许手工维护。

任何文件若主要内容是"条目列表+计数"，必须为以下两类之一：
- **A 类（生成物）**：脚本从 Schema 自动产出，标注 `generated_at`。AI 和人类均不得手工编辑。
- **B 类（Schema 输入）**：手工定义字段和约束，标注 `schema_input: true` + `consumed_by: [生成器脚本路径]`。是生成器的输入数据。

**两分类法**：
- 事实清单（磁盘有什么 → 脚本扫描得知）→ 永远自动生成
- 决策清单（人类决定应该有什么 → Schema 定义）→ 手工定义 Schema，脚本校验一致性

**绝对禁止**：
- 手工维护任何包含条目计数的清单
- 手工在 index.md 中写"本目录含 N 个文件"
- "以后改成自动生成"——不存在"以后"

**生成管道模式**：Schema（手工决策）→ 生成器 → 派生文件（机器产物）+ CI 校验（防止漂移）
