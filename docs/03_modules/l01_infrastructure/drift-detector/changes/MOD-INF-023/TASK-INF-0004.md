---
task_id: "TASK-INF-0004"
title: "基线快照管理器 baseline_manager.py 实现（D-023-03）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "6h"
actual_effort: null
assigned_to: null
created_by: "AI-Decomposer"
created_date: "2026-05-06"
updated_date: "2026-05-06"
depends_on: ["TASK-INF-0001","TASK-INF-0002"]
blocks: ["TASK-INF-0006","TASK-INF-0020","TASK-INF-0050"]
related_adrs: ["ADR-0022"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\baseline_manager.py"
acceptance_criteria:
  - "baseline_manager.py 实现 BaselineManager 类"
  - "SnapshotContent 四类型支持：tree_hash(SHA256树)、interface_snapshot(公开接口签名)、import_graph(依赖图)、config_snapshot(YAML/JSON canonical值)"
  - "Lifecycle 触发：construction_progress 变更为 phase_*_complete → 自动拍摄基线；Owner 手动触发 → 重新拍摄 known-good"
  - "DiffMode 三模式：full_diff(baseline vs current)、slow_creep_detection(累计差异度)、contract_only(仅接口签名)"
  - "存储路径 data/drift_baselines/<module_id>/，格式 JSON + SHA256 manifest，保留最近10个版本"
rollback_instructions: "git checkout src/zephyr/drift_detector/baseline_manager.py。删除 data/drift_baselines/ 下由本任务生成的基线文件。"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.2"]
tags: ["drift-detector","baseline","snapshot","D-023-03"]
compliance_tags: ["GOV-DOC-002"]
risks:
  - risk_id: "R-INF-023-03"
    description: "1500 模块基线快照磁盘占用过大"
    impact: "超出 2GB 磁盘预算（§6.16）"
    likelihood: "low"
    mitigation: "使用 SHA256 树而非全量文件副本；单个基线 < 100KB → 1500 × 100KB = 150MB × 10版本 = 1.5GB，内控"
    owner: "TASK-INF-0004执行者"
---

# TASK-INF-0004: 基线快照管理器 baseline_manager.py

## 目标

实现 `baseline_manager.py`，提供基线快照的拍摄、存储、对比、版本化管理功能。对标 blueprint §2.2 YAML 定义。

## 执行步骤

### Step 1: SnapshotContent 四种类型实现

- `tree_hash`: 递归遍历模块目录树，对每个文件计算 SHA256，生成 `{relative_path: sha256}` 字典
- `interface_snapshot`: AST 解析模块所有 `.py`，提取 `def`/`class` 签名（函数名/参数名+类型注解/返回类型）
- `import_graph`: AST 提取 import 语句，构建 `{file: [imported_modules]}` 有向图
- `config_snapshot`: 提取模块关联 YAML/JSON 配置文件的 canonical 键值对

### Step 2: 生命周期钩子

- `on_phase_complete(module_id, phase)`: 自动触发基线拍摄
- `manual_capture(module_id)`: Owner 手动重新拍摄 known-good 基线

### Step 3: 差异比较

- `full_diff(baseline_version, current)`: 全量差异，返回 `DiffReport`
- `slow_creep_check(module_id)`: 累积差异度 = Σ micro-drift，超过阈值告警
- `contract_diff(baseline_version, current)`: 仅接口签名对比

### Step 4: 存储与版本化

- JSON 存储到 `data/drift_baselines/<module_id>/v<NNN>.json`
- SHA256 manifest 文件 `data/drift_baselines/<module_id>/manifest.json`
- 自动清理 > 10 版本的旧基线（移到 `archive/`）

## 验收标准

- 四种 SnapshotContent 类型均可独立拍摄和对比
- Phase complete 自动触发基线拍摄
- 三种 DiffMode 均可输出结构化差异报告
- 基线保留10版本，旧版本自动归档

## 回滚指令

`git checkout src/zephyr/drift_detector/baseline_manager.py`。删除 `data/drift_baselines/` 下由本任务生成的基线文件。
