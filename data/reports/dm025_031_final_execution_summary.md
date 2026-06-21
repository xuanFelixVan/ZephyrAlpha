# DM-025~DM-031 遗留问题修复 — 最终执行总结

**执行日期**: 2026-06-15  
**执行模型**: qwen (诊断/复查) + deepseek (修复)  
**状态**: COMPLETED

---

## 修复问题清单

### 问题1: generate_project_path_tree.py --write 崩溃

**症状**: `AttributeError: 'NoneType' object has no attribute 'replace'`  
**根因**: SQLite 字段为 NULL 时，`.get("key", "")` 返回 None（键存在但值为 None），后续 `.replace()` 崩溃  
**修复**: 9处 `.get("key", "")` 改为 `.get("key") or ""`，9处 `var.replace(...)` 改为 `(var or "").replace(...)`

### 问题2: spec_auditor.py 导入不存在的模块

**症状**: `ModuleNotFoundError: No module named 'zephyr.autonomy_core.agent_lifecycle'`  
**根因**: 导入路径错误，`zephyr.autonomy_core.agent_lifecycle.registry` 不存在  
**修复**: 2个文件导入路径改为 `from zephyr.governance.agent_spec.registry import AgentCapability`

---

## 任务卡执行记录

| 任务卡 | 类型 | 执行模型 | 状态 | 交付物 |
|--------|------|---------|:---:|--------|
| DM-025 | 诊断 | qwen | COMPLETED | `data/reports/dm025_path_tree_crash_diagnosis_report.md` |
| DM-026 | 修复 | deepseek | COMPLETED | `scripts/governance/generate_project_path_tree.py` (9处修复) |
| DM-027 | 复查 | qwen | COMPLETED | `data/reports/dm027_path_tree_verification_report.md` |
| DM-028 | 诊断 | deepseek | COMPLETED | `data/reports/dm028_spec_auditor_import_diagnosis_report.md` |
| DM-029 | 修复 | deepseek | COMPLETED | 2个 `spec_auditor.py` 文件导入路径修正 |
| DM-030 | 复查 | qwen | COMPLETED | `data/reports/dm030_spec_auditor_verification_report.md` |
| DM-031 | 集成验证 | qwen | COMPLETED | `data/reports/dm031_integration_verification_report.md` |

---

## 验收标准达成

### DM-025/DM-026/DM-027 (path_tree 修复链)

- [x] 诊断报告包含所有9处 `.replace()` 调用的行号、上游变量名、None风险判定、修复方案
- [x] `generate_project_path_tree.py --write` exit 0 且无 AttributeError
- [x] 9196 节点成功写入
- [x] 复查验证通过，无副作用

### DM-028/DM-029/DM-030 (spec_auditor 修复链)

- [x] 诊断报告包含错误导入路径、正确替代路径、AgentCapability兼容性分析
- [x] 2个修复文件导入成功
- [x] AgentCapability 兼容性确认
- [x] 复查验证通过

### DM-031 (集成验证)

- [x] `generate_project_path_tree.py --write` exit 0
- [x] `generate_project_depgraph.py` exit 0
- [x] `audit_registration.py` exit 0
- [x] 无 AttributeError
- [x] 无 ModuleNotFoundError

---

## 修复文件清单

### generate_project_path_tree.py (9处)

| 行号 | 修复前 | 修复后 |
|:---:|--------|--------|
| 264 | `func_domain_val.get("ssot_path", "").replace(...)` | `(func_domain_val.get("ssot_path") or "").replace(...)` |
| 298 | `current_path.replace(...)` | `(current_path or "").replace(...)` |
| 317 | `section_data.get("design_root", "").replace(...)` | `(section_data.get("design_root") or "").replace(...)` |
| 342 | `section_data.get("structure", "")` | `section_data.get("structure") or ""` |
| 356 | `expanded.replace(...)` | `(expanded or "").replace(...)` |
| 366 | `rel_path.replace(...)` | `(rel_path or "").replace(...)` |
| 543 | `target_path.replace(...)` | `(target_path or "").replace(...)` |
| 610 | `entry.get("old_path", "").replace(...)` | `(entry.get("old_path") or "").replace(...)` |
| 611 | `entry.get("new_path", "").replace(...)` | `(entry.get("new_path") or "").replace(...)` |

### spec_auditor.py (2个文件)

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| `src/zephyr/governance/audit_trail/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | `from zephyr.governance.agent_spec.registry import AgentCapability` |
| `src/zephyr/governance/semantic_auditor/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | `from zephyr.governance.agent_spec.registry import AgentCapability` |

---

## 执行纪律遵守

### RULE-ZERO (写入文件锁协议)

- [x] 修复前检查文件锁状态：`python scripts/lock_files.py check` → FREE
- [x] 修复后文件锁正常释放

### RULE-ONE (原子写入)

- [x] 使用 Edit 工具精确替换，非删除+重建

### RULE-SEVEN (创建即自测)

- [x] DM-026 修复后立即运行 `--write` 验证 → exit 0
- [x] DM-029 修复后立即运行导入测试 → exit 0

### RULE-TWO (反孤儿)

- [x] 所有修复文件已在注册表中
- [x] 诊断报告和验证报告已生成到 `data/reports/`

### RULE-FIVE (零残留)

- [x] 无临时文件产生

### RULE-EIGHT (搜索先行)

- [x] DM-028 诊断时搜索了所有 spec_auditor.py 副本（发现6个）
- [x] 确认了 AgentCapability 的正确位置

---

## 后续建议

1. **P2 基线问题**: `audit_registration.py` 报告 708 个孤儿，建议后续建卡治理（本次不建卡）
2. **防御性编程**: 建议项目中所有 `.get("key", "")` 后接字符串方法时，统一改为 `.get("key") or ""` 模式
3. **导入路径统一**: 建议统一 `AgentCapability` 的导入路径为 `zephyr.governance.agent_spec.registry`

---

## 结论

DM-025~DM-031 七张任务卡全部完成，两个遗留问题已修复，集成验证通过。
