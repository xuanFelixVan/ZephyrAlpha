---
module_id: KE-2225------a-003
status: active
title: 4.2 触发条件 A：文件失联
category: module_blueprint
ttl: permanent
---

# 4.2 触发条件 A：文件失联

4.2 触发条件 A：文件失联

| 属性 | 值 |
|------|-----|
| **确定性** | **100%** — 文件存在性是布尔值 |
| **检测逻辑** | 规则中引用的文件路径 → 磁盘验证 → 文件不存在 = 触发 |
| **严重度** | RED |
| **可自动修复** | ❌（修复文本需要 LLM 生成） |

```python
def detect_file_disconnection(refs: ExtractedReferences, project_root: Path) -> list[DisconnectionIssue]:
    """
    核心逻辑：引用路径 → Path.exists() → False = 触发。
    这不需要 AI——文件要么存在，要么不存在。
    """
    issues = []
    for ref_path in refs.file_paths:
        full_path = project_root / ref_path
        if not full_path.exists():
            # 尝试模糊匹配——文件可能被重命名了
            alternatives = self._fuzzy_find(ref_path, project_root)
            issues.append(DisconnectionIssue(
                referenced_path=str(ref_path),
                exists=False,
                alternatives=[str(a) for a in alternatives],
                severity=Severity.RED,
                suggestion=self._build_disconnection_fix(ref_path, alternatives)
            ))
    return issues

def _fuzzy_find(ref_path: str, root: Path) -> list[Path]:
    """用文件名 + 前缀做模糊匹配。"""
    filename = Path(ref_path).name
    candidates = list(root.rglob(filename))
    return [c for c in candidates if c.exists()]
```

**修复建议模板**（Stage 6 送 LLM 润色）：

```
模板：文件 "{ref_path}" 已不存在。
      可能的新位置：{alternatives}
      建议：{if alternatives → "更新引用路径" else → "删除过时引用"}

LLM 只负责：将上述结构化数据转为自然语言建议。
```
