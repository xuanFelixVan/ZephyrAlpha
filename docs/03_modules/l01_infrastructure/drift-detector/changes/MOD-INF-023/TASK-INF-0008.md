---
task_id: "TASK-INF-0008"
title: "自漂移检测 self_check.py 实现（D-023-07）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0001"]
blocks: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\self_check.py"
acceptance_criteria:
  - "self_check.py 纯 stdlib——只用 pathlib+hashlib+yaml安全解析，不导入 zephyr 任何模块"
  - "验证目标：_detector_registry.yaml SHA256 vs 上次已知值、drift_engine.py SHA256 vs git HEAD、reconciler.py SHA256 vs git HEAD"
  - "bootstrap_self_check()：验证核心文件存在性+SHA256完整性+注册表可解析性"
  - "on_failure: P0 告警——drift detector 自身可能已被损坏"
rollback_instructions: "git checkout src/zephyr/drift_detector/self_check.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.7"]
tags: ["drift-detector","self-check","integrity","D-023-07"]
compliance_tags: ["GOV-DOC-002"]
risks: []
---

# TASK-INF-0008: 自漂移检测 self_check.py（D-023-07）

## 目标

实现 drift detector 自身完整性验证——纯 stdlib、独立于主逻辑的 self_check.py。对标 blueprint §2.7。

## 执行步骤

### Step 1: 最小自检实现

```python
import hashlib
import sys
from pathlib import Path

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_core_files(base: Path) -> dict:
    results = {}
    for f in ["_detector_registry.yaml", "drift_engine.py", "reconciler.py"]:
        fp = base / f
        if not fp.exists():
            results[f] = "MISSING"
            continue
        results[f] = sha256_file(fp)
    return results

def bootstrap_self_check() -> bool:
    base = Path(__file__).parent
    results = check_core_files(base)
    # 验证注册表可解析性
    registry_path = base / "_detector_registry.yaml"
    if registry_path.exists():
        import yaml
        with open(registry_path, encoding="utf-8") as f:
            yaml.safe_load(f)
    return all(v != "MISSING" for v in results.values())
```

### Step 2: 不可变清单验证

- 对比 `immutable_manifest` 中文件列表的 SHA256 与 git HEAD 版本
- 不一致 → P0 CRITICAL

### Step 3: 每次 scan 前执行

- drift_engine.scan() 入口 → `if not self_check.bootstrap_self_check(): raise DriftDetectorCorrupted`

## 验收标准

- self_check.py 零 zephyr 依赖（只 import stdlib + yaml 安全解析）
- 核心文件存在性 + SHA256 + 注册表可解析性三重验证
- 失败时 P0 告警

## 回滚指令

`git checkout src/zephyr/drift_detector/self_check.py`
