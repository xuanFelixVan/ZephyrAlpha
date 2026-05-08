---
task_id: "TASK-INF-0001"
title: "drift-detector 模块骨架搭建与目录结构初始化"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "2h"
actual_effort: null
assigned_to: null
created_by: "AI-Decomposer"
created_date: "2026-05-06"
updated_date: "2026-05-06"
depends_on: []
blocks: ["TASK-INF-0002","TASK-INF-0003","TASK-INF-0004","TASK-INF-0058"]
related_adrs: ["ADR-0022"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\_detector_registry.yaml"
  - "D:\\ZephyrAlpha\\data\\drift_baselines\\"
  - "D:\\ZephyrAlpha\\data\\drift_checkpoints\\"
  - "D:\\ZephyrAlpha\\data\\drift_audit\\"
  - "D:\\ZephyrAlpha\\data\\drift_runbooks\\"
  - "D:\\ZephyrAlpha\\data\\drift_handoffs\\"
acceptance_criteria:
  - "src/zephyr/drift_detector/__init__.py 存在，含 module docstring 说明轨道归属（B轨，cross_layer）与蓝图真源路径"
  - "__init__.py 中声明 module_id=MOD-INF-023, layer=cross_layer"
  - "data/drift_baselines/ 目录存在且含 .gitkeep"
  - "data/drift_checkpoints/ 目录存在且含 .gitkeep"
  - "data/drift_audit/ 目录存在且含 .gitkeep"
  - "data/drift_runbooks/ 目录存在且含 .gitkeep"
  - "data/drift_handoffs/ 目录存在且含 .gitkeep"
  - "_detector_registry.yaml 占位文件存在，含顶层 detectors: {} 骨架"
rollback_instructions: "删除 src/zephyr/drift_detector/ 目录。删除 data/drift_* 子目录。git checkout 恢复所有变更。"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§1.1","§1.4","§2.1","§7"]
tags: ["drift-detector","skeleton","initialization","directory-structure"]
compliance_tags: ["GOV-DOC-002","ADR-0022"]
risks: []
---

# TASK-INF-0001: drift-detector 模块骨架搭建与目录结构初始化

## 目标

按照 blueprint.md §1.1 和 §7 的定义，创建 drift-detector 模块的完整目录骨架和初始化文件。本模块属于 B 轨平台能力（`src/zephyr/drift_detector/`），layer 为 `cross_layer`。

## 触发条件

- 所有前置文件读取完毕
- 模块目录不存在或为空

## 执行步骤

### Step 1: 创建 src/zephyr/drift_detector/ 代码目录

在 `D:\ZephyrAlpha\src\zephyr\drift_detector\` 下创建 `__init__.py`，内容包含：
- 模块级 docstring：说明本模块是 ZephyrAlpha 漂移运行时检测系统，B 轨平台能力，module_id=MOD-INF-023，layer=cross_layer，蓝图真源路径 `docs/03_modules/l01_infrastructure/drift-detector/blueprint.md`
- `__version__ = "0.1.0"`
- 空 `__all__` 列表

### Step 2: 创建数据存储目录

在 `D:\ZephyrAlpha\data\` 下创建以下子目录，每个含 `.gitkeep`：
- `data/drift_baselines/` — 基线快照存储
- `data/drift_checkpoints/` — 崩溃恢复检查点
- `data/drift_audit/` — Git AUDIT 日志
- `data/drift_runbooks/` — 演练手册存储
- `data/drift_handoffs/` — Session 交接包

### Step 3: 创建检测器注册表占位文件

在 `D:\ZephyrAlpha\src\zephyr\drift_detector\_detector_registry.yaml` 创建骨架：

```yaml
detectors:
  existing: []
  new: []
```

### Step 4: 注册 data/ 子目录到 .gitignore 豁免

确保 `data/drift_*/` 在 `.gitignore` 中被正确管理——`.gitkeep` 文件确保目录被追踪，但 `.db`、`.json` 运行时产物不被追踪。

## 验收标准

- `src/zephyr/drift_detector/__init__.py` 存在，含 module docstring 说明轨道归属（B轨，cross_layer）与蓝图真源路径
- `__init__.py` 中声明 module_id=MOD-INF-023, layer=cross_layer
- `data/drift_baselines/` 目录存在且含 `.gitkeep`
- `data/drift_checkpoints/` 目录存在且含 `.gitkeep`
- `data/drift_audit/` 目录存在且含 `.gitkeep`
- `data/drift_runbooks/` 目录存在且含 `.gitkeep`
- `data/drift_handoffs/` 目录存在且含 `.gitkeep`
- `_detector_registry.yaml` 占位文件存在，含顶层 `detectors: {}` 骨架

## 风险与缓解

无明显风险。本任务为纯文件创建操作。

## 回滚指令

删除 `src/zephyr/drift_detector/` 目录。删除 `data/drift_baselines/`、`data/drift_checkpoints/`、`data/drift_audit/`、`data/drift_runbooks/`、`data/drift_handoffs/` 目录。`git checkout` 恢复所有变更。
