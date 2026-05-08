---
task_id: TASK-OPS-0019
module_id: MOD-INF-005
title: "AI Session Zero-Memory Quickstart Card — §22 QUICKSTART.md ≤500 tokens 验证 + B60/B62 上下文窗口治理"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - quickstart
  - ai-context
  - token-budget
  - cold-start
description: |
  验证蓝图 §22 QUICKSTART.md（B15）的有效性，并落地 B60/B62 上下文窗口治理。
  
  §22：AI 冷启动卡片 ≤500 tokens——一句话概述 / 3 条命令 / 架构地图 / 快查表 / 门槛规则 / 1人+AI备忘
  B60：上下文窗口污染——Tier-1(必注入≤500tokens) / Tier-2(按需) / Tier-3(禁止)
  B62：规则版本过期——AI 注入文件的 valid_from 时间戳检查，>7天→[STALE]

acceptance_criteria:
  - "QUICKSTART.md token 数 ≤ 500（中英文混合计算）"
  - "QUICKSTART.md 包含 6 项内容（概述/命令/架构/快查/门槛/备忘）"
  - "validate_rule_freshness.py 检查AI注入规则文件 freshness——>7天→标记 [STALE]"
  - "AGENTS.md 中增加上下文注入 Tiers 指令"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\QUICKSTART.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_rule_freshness.py"

rollback_instructions: "git checkout -- scripts/governance/QUICKSTART.md AGENTS.md"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§22.1", "§22.2", "§22.3"]

phase: phase_2_extend
effort_estimate: S
risk_level: LOW
depends_on_task: ["TASK-OPS-0018"]
blocks_task: ["TASK-OPS-0020"]
related_blind_spots: ["B15", "B60", "B61", "B62"]
related_risks: []
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0019: AI Session Zero-Memory Quickstart — §22 QUICKSTART.md 验证 + 上下文窗口治理

## 1. 任务概述

QUICKSTART.md 已创建。需要：验证 token 预算 ≤500、补全 6 项内容、落地 B60 Tier-1/2/3 上下文注入策略、B62 规则新鲜度检查。

## 2. 施工步骤

### Step 1: Token 计数
验证 QUICKSTART.md ≤ 500 tokens。

### Step 2: 内容完整性检查
确认 6 项：
- 一句话概述 ✓
- 3 条常用命令 ✓
- 架构地图 ✓
- 关键文件速查表 ✓
- 门槛规则 ✓
- 1人+AI 维护备忘 ✓

### Step 3: validate_rule_freshness.py
新建脚本：检查 AI session 注入文件的 valid_from 字段→>7 天→ 标记 [STALE]。

### Step 4: AGENTS.md 上下文注入指令
在 AGENTS.md 中增加：
- 每次 AI session 启动：先读 QUICKSTART.md（Tier-1，≤500 tokens）
- 按任务按需注入相关蓝图节选（Tier-2）
- 禁止在单次 session 注入完整 manifest（Tier-3）

## 3. 验收标准
- [ ] QUICKSTART.md ≤ 500 tokens
- [ ] 6 项内容完整
- [ ] validate_rule_freshness.py 可运行
- [ ] AGENTS.md 含上下文注入指令
