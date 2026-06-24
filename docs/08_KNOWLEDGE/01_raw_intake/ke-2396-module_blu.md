---
module_id: KE-2301
status: active
title: 5.2.2 判定标准
category: module_blueprint
---

# 5.2.2 判定标准

5.2.2 判定标准

**判定 1：功能重复检测**

```python
def has_functional_duplicate(orphan: File, all_files: list[File]) -> DuplicateResult:
    """
    使用 Code Dedup Engine 的语义相似度检测。
    相似度 > 0.85 → 视为功能重复。
    """
    scores = [(f, dedup_engine.similarity(orphan, f)) for f in all_files if f != orphan]
    high_scores = [(f, s) for f, s in scores if s > 0.85]
    return DuplicateResult(has_duplicates=bool(high_scores), duplicates=high_scores)
```

**判定 2：独特价值检测**

```python
def has_unique_value(orphan: File, duplicates: list[tuple[File, float]]) -> ValueJudgment:
    """
    即使是重复文件，也可能包含独特价值：
    - 不同的函数/类实现
    - 不同的文档注释
    - 不同的配置参数
    - 不同的边界处理逻辑
    """
    orphan_content = parse_ast(orphan)
    duplicate_contents = [parse_ast(d) for d, _ in duplicates]

    unique_elements = []
    for node in orphan_content.nodes:
        if not any(node.matches(d_node) for d in duplicate_contents for d_node in d_content.nodes):
            unique_elements.append(node)

    return ValueJudgment(
        has_unique=bool(unique_elements),
        unique_elements=unique_elements,
        recommendation="EXTRACT_AND_MERGE" if unique_elements else "DELETE"
    )
```

**判定 3：独立价值检测**

```python
def has_standalone_value(orphan: File) -> ValueJudgment:
    """
    无功能重复的孤儿，评估是否有独立保留价值：
    - 文件大小 > 500 bytes（不是空壳）
    - 包含可执行逻辑（不只是注释/import）
    - 不是临时/测试文件（文件名不含 tmp/test/wip）
    - 最后一次修改在 30 天内（近期活跃）
    """
    size_score = min(orphan.size / 500, 1.0)
    has_logic = bool(parse_ast(orphan).function_defs or parse_ast(orphan).class_defs)
    not_tmp = not any(kw in orphan.name.lower() for kw in ['tmp', 'test_', 'wip', 'draft'])
    recent = (datetime.now() - orphan.mtime).days < 30

    confidence = (size_score + (1.0 if has_logic else 0) + (1.0 if not_tmp else 0) + (1.0 if recent else 0)) / 4

    if confidence > 0.5:
        return ValueJudgment(has_unique=True, recommendation="REGISTER")
    return ValueJudgment(has_unique=False, recommendation="DELETE")
```
