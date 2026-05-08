---
task_id: TASK-OPS-0022
module_id: MOD-INF-005
title: "第五层盲点 B92-B107（取证专家终极穿透）+ §32-§33（完整性声明+灾备）落地卡"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - fifth-layer
  - forensic-audit
  - trust-root
  - evidence
  - disaster-recovery
description: |
  将蓝图 §31 第五层盲点 B92-B107（16 项致命漏洞——取证专家视角）、§32 跨五层穷尽声明、§33 物理韧性与灾备策略拆解为防御任务。
  
  致命度 Top 3（§32.3）：
  1. B92 启动信任悖论——SHA256哈希和验证脚本在同一个repo→需要带外验证锚点(Git签名/外部哈希存证)
  2. B101 自述证据不可验证——Finding.evidence 字段只有脚本自述，没有哈希存证/文件快照/第三方见证
  3. B93 D1单点灾难性失效——D1→D3交接处缺少合理性校验
  
  其余关键漏洞：
  - B94 僵尸脚本（从未产出Finding的脚本B51不检测）
  - B95 Manifest 语义欺诈（dimension声明与实际不符）
  - B96 时间涂抹窗口（50s扫描期间代码库未被冻结）
  - B97 Error Budget 可预测重置窗口
  - B98 Shadow Mode 定时炸弹（sleeper attack: Phase1-2良性→Phase3定时激活恶意逻辑）
  - B99 AI决策溯源链缺失
  - B100 人因绕过疲劳（Owner疲劳→系统向Owner报告"你绕过47次"无效）

acceptance_criteria:
  - "B92缓解：validate_rules_integrity.py 增加带外验证通道——检查git signed commit或外部哈希存证URL"
  - "B101缓解：Finding Schema 新增 content_hash + snapshot_path 字段——证据可独立验证"
  - "B93缓解：D1产出物合理性校验——run_all.py 在 D1完成后 D3开始前做逻辑自洽检查"
  - "B96缓解：run_all.py 全量扫描前 git stash snapshot→scan→unstash"
  - "§33灾备：backup_runtime_state.py 脚本新建——SQLite导出JSON + YAML快照→commit"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_rules_integrity.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_d1_output_sanity.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\backup_runtime_state.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\script_system\\finding.py"

rollback_instructions: "git checkout -- scripts/governance/meta/validate_d1_output_sanity.py scripts/governance/meta/backup_runtime_state.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§31.1", "§31.2", "§31.3", "§31.4", "§32.1", "§32.2", "§32.3", "§33.1", "§33.2"]

phase: phase_3_systematize
effort_estimate: XL
risk_level: HIGH
depends_on_task: ["TASK-OPS-0021"]
blocks_task: ["TASK-OPS-0023"]
related_blind_spots: ["B92", "B93", "B94", "B95", "B96", "B97", "B98", "B99", "B100", "B101", "B102", "B103", "B104", "B105", "B106", "B107"]
related_risks: ["R2", "R3", "R5"]
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: human_required
---

# TASK-OPS-0022: 第五层盲点 B92-B107（取证专家终极穿透）+ §33 灾备落地

## 1. 任务概述

取证专家视角的 16 致命漏洞（B92-B107）覆盖信任根/依赖链/时态完整性/证据法理学。Top3（B92/B101/B93）如果不修——系统"信任根腐败、证据不可验证、串行链前端失效=全线坍塌"。

## 2. 施工步骤

### Step 1: B93 — D1产出物合理性校验
新建 `D:\ZephyrAlpha\scripts\governance\d1_structure\validate_d1_output_sanity.py`：
- 在 D1 完成后、D3 开始前检查 D1 产出是否逻辑自洽
- 检查项：所有前端文件（frontmatter 文件）数 vs D3 扫描目标文件数
- 不一致 → BLOCK D3（exit 2，避免下游在垃圾输入上运行）

### Step 2: B101 — Finding 证据独立可验证
在 Finding Schema 新增：
- `evidence_content_hash`: SHA256 of the file content at time of detection
- `evidence_snapshot_ref`: optional git commit SHA at detection time

### Step 3: B92 — 带外验证锚点
在 validate_rules_integrity.py 增加 --verify-git-signature 参数：
- 检查最后一次修改规则的 commit 是否 GPG 签名
- 无签名 → exit 1 WARNING

### Step 4: §33 backup_runtime_state.py
新建 `D:\ZephyrAlpha\scripts\governance\meta\backup_runtime_state.py`：
- 导出 SQLite→JSON
- YAML 状态文件快照→single JSON
- Commit 到 `meta/backups/`
- 保留 12 周备份→自动清理

## 3. 验收标准
- [ ] validate_d1_output_sanity.py 可运行
- [ ] Finding Schema 含 evidence_content_hash
- [ ] Git signature 检查可用
- [ ] backup_runtime_state.py 周度自动导出
