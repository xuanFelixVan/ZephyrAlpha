---
module_id: KE-4111
title: 4.3 三件套强制清单
category: module_blueprint
---

# 4.3 三件套强制清单

4.3 三件套强制清单

| 步骤 | 内容 | 验证方法 |
|:---:|------|---------|
| **A 落位** | 放入 `scripts/governance/{dimension}/`，文件名遵循 `validate_*` / `detect_*` / `audit_*` / `check_*` / `register_*` 约定 | 文件存在于正确位置 |
| **B manifest注册** | 在 `scripts/governance/script-manifest.yaml` 添加条目（dimensions + priority + timeout + args + description） | `python scripts/governance/check_registry_consistency.py` → 零不一致 |
| **C 运行验证** | `python scripts/governance/{dimension}/{script}.py --warn-only` → exit 0 + 零诊断 | 四档退出码（0=全通过/1=警告/2=错误/3=崩溃） |

> **清单生成（病根闭环）**：`script-manifest.yaml` 为 **生成物**——须在各 `.py` 内维护 `__manifest__` 并运行 `python scripts/governance/generators/generate_script_manifest.py`。生成器 **同时支持**：（1）ASCII 三引号包裹的 YAML；（2）模块顶层的 `__manifest__ = { ... }` **dict 字面量**（`ast` 解析）。历史上仅支持（1）导致（2）被误报为「缺失 manifest」、清单与 `run_all` 漂移。
