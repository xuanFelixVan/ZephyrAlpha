---
module_id: FAULTY_SAMPLE_DOUBLE_YAML_001
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 测试系统
responsibility:
  - 用于测试双YAML检测器的已知错误样本
layer: layer_test
---

---
module_id: FAULTY_SAMPLE_DOUBLE_YAML_001_SECONDARY
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 测试系统
responsibility:
  - 这是第二个YAML块，会触发D-01检测
layer: layer_test
---

# 已知缺陷：双YAML Frontmatter

> **用途**: 这个文件用于测试 doc_guard_pre_commit.py 的双YAML检测逻辑
> **预期**: 检查器应该在此文件检测到 D-01 错误

## 文件特点

- 包含两个完整的YAML frontmatter块
- 第二个块也包含有效的YAML键值对（module_id, version等）
- 这会导致文档解析歧义

## 测试方法

```bash
python scripts/doc_guard_pre_commit.py --scan-double-yaml
```

预期输出应该包含:
```
[D-01] tests/faulty_samples/double-yaml-sample.md:25 — 发现双 YAML frontmatter
```
