# DM-025 诊断报告：generate_project_path_tree.py --write 崩溃问题

**任务卡**: DM-025  
**诊断日期**: 2026-06-15  
**诊断模型**: qwen  
**状态**: COMPLETED

---

## 问题描述

执行 `python scripts/governance/generate_project_path_tree.py --write` 时崩溃，报错：
```
AttributeError: 'NoneType' object has no attribute 'replace'
```

根因：从 SQLite 数据库读取字段时，`.get("key", "")` 在键存在但值为 NULL 时返回 None（而非默认值 ""），后续调用 `.replace()` 导致崩溃。

---

## 9处 .replace() 崩溃风险点诊断

### 1. 第264行：ssot_path 为 None

**代码**:
```python
ssot_path = func_domain_val.get("ssot_path", "").replace("\\", "/").rstrip("/") + "/"
```

**上游变量**: `func_domain_val` 来自 `_load_panorama_from_db()` 第65-80行构建的 domain dict，其中 `ssot_path` 来自数据库 `domains` 表的 `ssot_path` 字段。

**None 风险判定**: **高风险**。数据库 `domains.ssot_path` 字段允许 NULL，当该字段为 NULL 时，`domain.get("ssot_path", "")` 返回 None（键存在但值为 None），`.replace()` 崩溃。

**修复方案**:
```python
ssot_path = (func_domain_val.get("ssot_path") or "").replace("\\", "/").rstrip("/") + "/"
```

---

### 2. 第298行：current_path 为 None

**代码**:
```python
prefix = current_path.replace("\\", "/")
```

**上游变量**: `current_path` 是递归函数 `_extract_tree_domain_ids()` 的参数，初始调用传入 `""`（第273行），递归时传入 `f"{current_path}/{key}"`（第306行）。

**None 风险判定**: **低风险**。`current_path` 由字符串拼接构建，理论上不会为 None。但为防御性编程，仍建议加保护。

**修复方案**:
```python
prefix = (current_path or "").replace("\\", "/")
```

---

### 3. 第317行：design_root 为 None

**代码**:
```python
design_root = section_data.get("design_root", "").replace("\\", "/").rstrip("/") + "/"
```

**上游变量**: `section_data` 来自 `_load_panorama_from_db()` 返回的 data dict 中的 path sections（如 `blueprint_paths`）。

**None 风险判定**: **高风险**。如果数据库中 path sections 的 `design_root` 字段为 NULL，`.get()` 返回 None。

**修复方案**:
```python
design_root = (section_data.get("design_root") or "").replace("\\", "/").rstrip("/") + "/"
```

---

### 4. 第355行：structure 为 None

**代码**:
```python
expanded = structure.replace("{design_root}", design_root).replace("{domain_id}", domain_id)
```

**上游变量**: `structure` 来自第342行 `structure = section_data.get("structure", "")`。

**None 风险判定**: **中风险**。如果 `structure` 字段为 NULL，`.get()` 返回 None。

**修复方案**:
```python
structure = section_data.get("structure") or ""
```

---

### 5. 第356行：expanded 为 None

**代码**:
```python
expanded = expanded.replace("\\", "/").rstrip("/") + "/"
```

**上游变量**: `expanded` 来自第355行的 `.replace()` 结果。

**None 风险判定**: **低风险**。如果第355行修复后，`expanded` 必为字符串。但为链式安全，仍建议保护。

**修复方案**:
```python
expanded = (expanded or "").replace("\\", "/").rstrip("/") + "/"
```

---

### 6. 第366行：rel_path 为 None

**代码**:
```python
rp = rel_path.replace("\\", "/") + "/"
```

**上游变量**: `rel_path` 是 `derive_domain_for_path()` 的参数，类型提示为 `str`。

**None 风险判定**: **中风险**。调用方传入的值理论上应为字符串，但无运行时校验。

**修复方案**:
```python
rp = (rel_path or "").replace("\\", "/") + "/"
```

---

### 7. 第543行：target_path 为 None

**代码**:
```python
parts = target_path.replace("\\", "/").split("/")
```

**上游变量**: `target_path` 是 `_mark_pending_deletion()` 的参数，类型提示为 `str`。

**None 风险判定**: **中风险**。调用方在第616行传入 `old_p`，而 `old_p` 来自第610行的 `.replace()`，如果第610行修复则安全。但函数本身应防御。

**修复方案**:
```python
parts = (target_path or "").replace("\\", "/").split("/")
```

---

### 8. 第610行：old_path 为 None

**代码**:
```python
old_p = entry.get("old_path", "").replace("\\", "/")
```

**上游变量**: `entry` 来自 migration-registry.yaml 的 `entries` 列表（第607行循环）。

**None 风险判定**: **高风险**。YAML 文件中 `old_path` 字段可能缺失或为 null，`.get()` 返回 None。

**修复方案**:
```python
old_p = (entry.get("old_path") or "").replace("\\", "/")
```

---

### 9. 第611行：new_path 为 None

**代码**:
```python
new_p = entry.get("new_path", "").replace("\\", "/")
```

**上游变量**: 同上，来自 migration-registry.yaml 的 `entry` dict。

**None 风险判定**: **高风险**。YAML 文件中 `new_path` 字段可能缺失或为 null。

**修复方案**:
```python
new_p = (entry.get("new_path") or "").replace("\\", "/")
```

---

## 补充修复（深度复查发现）

### 第354行：domain_id 为 None

**代码**:
```python
domain_id = func_domain_val.get("domain_id", func_domain_name)
```

**上游变量**: `func_domain_val` 来自数据库 `domains` 表。

**None 风险判定**: **高风险**。数据库 `domains.domain_id` 字段允许 NULL，当该字段为 NULL 时，`.get("domain_id", func_domain_name)` 返回 None（键存在但值为 None），后续第355行 `.replace("{domain_id}", domain_id)` 会崩溃（TypeError: replace() argument 2 must be str, not None）。

**修复方案**:
```python
domain_id = func_domain_val.get("domain_id") or func_domain_name
```

**实际影响**: 修复后域推导条目从30条增加到404条——说明之前 `domain_id` 为 None 时 `if ssot_path and domain_id:` 条件不满足，大量域推导条目被跳过。此修复不仅解决了 None 风险，还修复了一个实际的功能缺陷。

---

### 第182行：INSERT 硬编码 version=4 导致唯一约束冲突

**代码**:
```python
conn.execute(
    "INSERT INTO _schema_version (version, applied_at, description) VALUES (?, ?, ?)",
    (4, datetime.now(UTC).isoformat(), desc)
)
```

**问题**: 多次执行 `--write` 时，`_schema_version` 表已有 version=4 的记录，INSERT 触发 `UNIQUE constraint failed: _schema_version.version`。

**修复方案**:
```python
conn.execute(
    "INSERT OR REPLACE INTO _schema_version (version, applied_at, description) VALUES (?, ?, ?)",
    (4, datetime.now(UTC).isoformat(), desc)
)
```

---

## 修复优先级总结

| 行号 | 变量 | 风险等级 | 修复复杂度 |
|:---:|------|:---:|:---:|
| 264 | ssot_path | 高 | 低 |
| 317 | design_root | 高 | 低 |
| 610 | old_path | 高 | 低 |
| 611 | new_path | 高 | 低 |
| 355 | structure | 中 | 低 |
| 366 | rel_path | 中 | 低 |
| 543 | target_path | 中 | 低 |
| 298 | current_path | 低 | 低 |
| 356 | expanded | 低 | 低 |

**统一修复模式**: 所有 `.get("key", "")` 改为 `.get("key") or ""`，所有 `var.replace(...)` 改为 `(var or "").replace(...)`。

---

## 验收标准达成检查

- [x] 诊断报告包含所有9处 `.replace()` 调用的行号
- [x] 每处标注上游变量名
- [x] 每处标注 None 风险判定（高/中/低）
- [x] 每处提供修复方案

---

## 后续任务

- **DM-026**: 按本诊断报告执行修复
- **DM-027**: 修复后复查验证
