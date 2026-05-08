---
task_id: "TASK-INF-0201"
source_blueprint: "MOD-INF-014"
source_section: "蓝图 §1 概述"
title: "LLM Security Gateway 模块骨架搭建与路径合规创建"
description: |
  为 MOD-INF-014 LSG 模块创建完整的代码目录骨架（src/zephyr/llm_security/）和文档目录结构。
  确保所有产出物路径符合 GOV-DOC-002 目录结构标准 + MTH-013 路径合规创建原则。
  创建 layers/、patterns/、payloads/、sandbox/、self_protection/、dashboard/ 子目录。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\governance-methodology-standard.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
    description: "LLMSecurityProtocol 抽象基类"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\__init__.py"
    description: "layers 包初始化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\patterns\\__init__.py"
    description: "patterns 包初始化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\__init__.py"
    description: "payloads 包初始化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\sandbox\\__init__.py"
    description: "sandbox 包初始化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\__init__.py"
    description: "self_protection 包初始化"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\patterns\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\sandbox\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\*"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\behavior_audit_logger.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-INF-{NNNN}"
  - module_id: "GOV-DOC-002"
    section: "全篇"
    reason: "路径映射——产出物物理存放"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建——产出物必须符合目录结构标准"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "本蓝图——§13 文件组成与代码落位 + §60 产出物存放目录"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "目录结构标准——路径映射"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 5000
timeout_minutes: 30
acceptance_criteria:
  - "src/zephyr/llm_security/layers/ 目录存在且含 __init__.py"
  - "src/zephyr/llm_security/patterns/ 目录存在且含 __init__.py"
  - "src/zephyr/llm_security/payloads/ 目录存在且含 __init__.py"
  - "src/zephyr/llm_security/sandbox/ 目录存在且含 __init__.py"
  - "src/zephyr/llm_security/self_protection/ 目录存在且含 __init__.py"
  - "src/zephyr/llm_security/protocol.py 含 LLMSecurityProtocol 抽象基类"
  - "所有路径符合 GOV-DOC-002 §5.1.2 防幻觉路径映射表"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\protocol.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\__init__.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\patterns\__init__.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\payloads\__init__.py
  5. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\sandbox\__init__.py
  6. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\self_protection\__init__.py
  7. 删除空目录 layers/ patterns/ payloads/ sandbox/ self_protection/
depends_on: []
blocked_by: []
status: "done"
tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-014"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

创建 MOD-INF-014 LLM Security Gateway 的完整代码目录骨架。建立 LSG 的模块入口、抽象基类和子目录结构，为后续 L0-L8 九层防御层的代码施工提供路径锚点。

## 触发条件

- 蓝图 MOD-INF-014 §13 文件组成与代码落位已定义完整文件清单
- 蓝图 MOD-INF-014 §60 产出物存放目录已定义所有产出物路径
- GOV-DOC-002 + MTH-013 路径标准已落地

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §13 完整文件清单 + §60 产出物存放目录
- `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` §5.1.2 路径映射

### 做
1. 创建 `src/zephyr/llm_security/protocol.py` ——定义 `LLMSecurityProtocol` 抽象基类（九层防御层的统一接口契约）
2. 创建子目录 `layers/` `patterns/` `payloads/` `sandbox/` `self_protection/` ——各含 `__init__.py` + 模块 docstring
3. 更新 `src/zephyr/llm_security/__init__.py` ——模块入口架构注释从四层更新为九层（L0-L8）

### 产
- `protocol.py`（抽象基类）
- `layers/__init__.py` 等 5 个 `__init__.py`

### 检
```bash
python -c "import os; [print(d) for d in ['layers','patterns','payloads','sandbox','self_protection'] if os.path.isdir(os.path.join('src/zephyr/llm_security', d))]"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | files | 6 个产出物全部存在 + UTF-8 |
| 2 | lint | 0 errors, 0 warnings |
| 3 | diff | 仅修改 allowed_touch 范围内 |
