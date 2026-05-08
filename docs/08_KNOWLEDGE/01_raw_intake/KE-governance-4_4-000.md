---
module_id: KE-governance-4_4-000
title: 4.4 脚本未就绪时的后备方案
category: governance
---

# 4.4 脚本未就绪时的后备方案

4.4 脚本未就绪时的后备方案

`task_completion_gate.py` 尚未实现时，AI 必须执行以下手动检查清单：

| 检查项 | 方法 | 通过条件 |
|--------|------|---------|
| 临时文件扫描 | 在 scope-paths 下搜索 `temp_*`、`*-v2.*`、`*-v3.*`、`*-round2.*`、`*.backup`、`__pycache__` | 零匹配 |
| 空壳文件检测 | 检查 scope-paths 下文件大小 < 100 bytes 的文件内容是否为空壳/占位 | 无空壳 |
| 文件一致性 | 对比 `deliverables` 列表与 scope-paths 下实际文件列表 | 无遗漏、无多余 |
| 编码检测 | 检查所有产出文件是否为 UTF-8 无 BOM + LF 换行 | 全部合规 |

手动检查结果必须记录在 Session Log 中：

```yaml
- topic: 任务 {task_id} 清扫检查（手动后备——task_completion_gate.py 尚未实现）
  decision: 通过 / 不通过（附具体不通过项）
  rationale: <检查摘要，列出执行的具体命令和结果>
```
