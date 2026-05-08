---
task_id: "TASK-INF-0003"
title: "检测器注册表填充 + detector_dispatcher.py 并行调度器实现（D-023-01 + D-023-05 调度）"
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
blocks: ["TASK-INF-0005","TASK-INF-0006"]
related_adrs: ["ADR-0022"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\_detector_registry.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\detector_dispatcher.py"
acceptance_criteria:
  - "_detector_registry.yaml 中 existing 部分含全部 18 个现有治理脚本映射，每个含 id/script/drift_dimension/check_dims/severity/category"
  - "_detector_registry.yaml 中 new 部分含全部 13 个待实现检测器，每个含 id/drift_dimension/severity/category/method/status/auto_fixable"
  - "detector_dispatcher.py 实现 asyncio subprocess pool 并行执行，每批最多 8 个并行"
  - "检测器结果缓存：同一文件未变更 + 同一检测器 → SHA256 校验 → 复用上次结果"
  - "并行度控制：LIGHT=4 / STANDARD=4 / DEEP=8"
rollback_instructions: "git checkout src/zephyr/drift_detector/_detector_registry.yaml src/zephyr/drift_detector/detector_dispatcher.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.1","§2.4"]
tags: ["drift-detector","detector-registry","parallel-scheduler","D-023-01","D-023-05"]
compliance_tags: ["GOV-DOC-002"]
risks:
  - risk_id: "R-INF-023-02"
    description: "18 个现有脚本路径可能已变更或不存在"
    impact: "检测器调度失败——无法找到脚本"
    likelihood: "medium"
    mitigation: "逐脚本验证磁盘路径存在性。不存在的脚本标记为 MISSING_SCRIPT，不阻塞调度但记录到 drift_events"
    owner: "TASK-INF-0003执行者"
---

# TASK-INF-0003: 检测器注册表填充 + 并行调度器实现

## 目标

按蓝图 §2.1 中 YAML 代码块的完整定义，填充 `_detector_registry.yaml`（现有18个 + 新13个），并实现 `detector_dispatcher.py` 并行调度器。

## 执行步骤

### Step 1: 填充 _detector_registry.yaml existing 部分

将 blueprint §2.1 YAML 代码块现有18个检测器定义逐条写入注册表。每条包含：
- `id`, `script`（scripts/governance/下的脚本路径）, `drift_dimension`, `check_dims`, `severity`, `category`

验证每个 `script` 路径在磁盘上存在。

### Step 2: 填充 _detector_registry.yaml new 部分

写入13个待实现检测器：
- `ai_hallucination_import`, `ai_dead_code`, `ai_broken_logic`, `ai_duplicate_functionality`, `ai_session_style_drift`, `ai_knowledge_pollution`
- `contract_implementation`, `semantic_drift`, `db_schema_drift`, `dep_version_drift`, `security_policy_drift`, `doc_code_coevolution`, `test_coverage_drift`

每个含 status: "待实现" 和 method 字段。

### Step 3: 实现 detector_dispatcher.py

```python
class DetectorDispatcher:
    def __init__(self, registry_path: str, max_parallel: int = 8):
        ...
    
    async def dispatch(
        self, 
        detectors: list[Detector], 
        changed_files: list[str],
        cache: ResultCache
    ) -> list[DetectorResult]:
        # asyncio.Semaphore 控制并行度
        # asyncio.create_subprocess_exec 执行脚本
        # 解析 stdout JSON → DetectorResult
        ...
    
    def cache_key(self, detector_id: str, file_path: str) -> str:
        # SHA256(detector_id + file_content_hash)
        ...
```

## 验收标准

- `existing` 部分含全部 18 个现有脚本映射
- `new` 部分含全部 13 个待实现检测器
- `detector_dispatcher.py` 实现 asyncio subprocess pool，最多8并行
- 检测器结果缓存生效（SHA256 校验）
- 并行度：LIGHT=4 / STANDARD=4 / DEEP=8

## 回滚指令

`git checkout src/zephyr/drift_detector/_detector_registry.yaml src/zephyr/drift_detector/detector_dispatcher.py`
