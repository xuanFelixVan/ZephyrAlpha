---
task_id: TASK-OPS-0003
module_id: MOD-INF-005
title: "依赖声明验证 — §2 必备链接与 depends_on 链完整性校验"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - dependency
  - depends-on
  - validation
  - link-integrity
description: |
  验证蓝图 §2 中声明的 8 条必备链接和 6 条 depends_on 声明全部有效。
  
  §2.1 必备链接（8 条）：
  1. MOD-INF-006 任务系统蓝图
  2. PS-STD-001 元数据注册表
  3. PS-STD-012 规则验证标准
  4. SCRIPT-QUALITY-001 脚本质量标准
  5. script_manifest.yaml
  6. AGENTS.md
  7. scripts/governance/index.md
  8. module-registry.yaml
  
  §2.2 depends_on 声明（6 条）：
  1. MOD-INF-006 @ §4 — G0-G7 门禁体系
  2. MOD-INF-006 @ §5 — M1-M11 管线节点
  3. MOD-INF-006 @ §3.2.1+§4.2+§3.1.2 — TaskCard 模型
  4. MOD-KB-001 @ §3.2+§6 — KE Schema + KB 入库
  5. PS-STD-001 @ §7 — 元数据注册表
  6. SCRIPT-QUALITY-001 @ §2 — 退出码约定

acceptance_criteria:
  - "8 条必备链接指向的文件在磁盘上全部存在"
  - "§2.2 中 6 条 depends_on 声明的模块目标（MOD-INF-006、MOD-KB-001）在 module-registry.yaml 中为 Active"
  - "§2.2 中 2 条标准目标（PS-STD-001、SCRIPT-QUALITY-001）指向的文件在磁盘上存在"
  - "validate_depends_on_format.py 对蓝图 §2 的检查 exit 0"
  - "d2_links/audit_broken_links.py 对蓝图文件的链接检查 exit 0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\rule-verification-standard.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\quality-standard.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\index.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\module-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"

downstream_outputs: []

rollback_instructions: "无需回滚——本任务卡仅验证不修改文件"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§2.1", "§2.2", "§2.3"]
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    sections: ["§4", "§5", "§3.2.1"]

phase: phase_0_setup
effort_estimate: S
risk_level: LOW
depends_on_task: ["TASK-OPS-0001"]
blocks_task: ["TASK-OPS-0006"]
related_blind_spots: ["B2", "B65"]
related_risks: ["R3"]
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0003: 依赖声明验证 — §2 必备链接与 depends_on 链完整性校验

## 1. 任务概述

蓝图 §2 声明了脚本系统对外部模块和文档的依赖关系。这些依赖链必须在磁盘上可验证——如果一条必备链接指向的文件不存在或模块已废弃，脚本系统在运行时会因缺失上下文而错误决策。

## 2. 施工步骤

### Step 1: 必备链接文件存在性验证
遍历 §2.1 的 8 条必备链接，逐个检查路径是否存在：
```bash
python scripts/governance/d4_paths/detect_ruins_references.py --scope docs/03_modules/l01_infrastructure/script-system/blueprint.md
```

### Step 2: depends_on 目标状态验证
遍历 §2.2 的 6 条 depends_on 声明：
- 4 条模块目标（MOD-INF-006×3 + MOD-KB-001）→ 检查 module-registry.yaml 中状态
- 2 条标准目标（PS-STD-001 + SCRIPT-QUALITY-001）→ 检查磁盘文件存在
```bash
python scripts/governance/d5_architecture/validate_depends_on_format.py
```

### Step 3: 链接有效性
```bash
python scripts/governance/d2_links/audit_broken_links.py docs/03_modules/l01_infrastructure/script-system/blueprint.md
```

### Step 4: 与 MOD-INF-006 的接口一致性
检查 §2.2 中声明的 MOD-INF-006 依赖点在 task-system 蓝图中确实存在对应章节：
- MOD-INF-006 §4（G0-G7 门禁体系）
- MOD-INF-006 §5（M1-M11 管线节点）
- MOD-INF-006 §3.2.1（TaskCard 模型）

## 3. 验收标准
- [ ] 8 条必备链接全部指向磁盘上存在的文件
- [ ] §2.2 4 条模块目标（MOD-INF-006×3 + MOD-KB-001）状态为 Active
- [ ] §2.2 2 条标准目标（PS-STD-001 + SCRIPT-QUALITY-001）文件存在
- [ ] audit_broken_links.py 对蓝图 exit 0
- [ ] validate_depends_on_format.py 对蓝图 §2 exit 0
- [ ] MOD-INF-006 三个依赖点的章节引用有效
