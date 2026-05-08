---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "知识库系统蓝图（MOD-KB-001）"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: 知识库系统蓝图（MOD-KB-001）

## CRITICAL Rules

### Core Operations
# .git/hooks/post-commit（install-hooks.py 自动安装，零 Owner 操作）
def post_commit_hook():
    marker = "docs/19_development_workspace/session-logs/handoff-current.md"
    if not os.path.exists(marker):
        return  # 不是 session 结束 commit → 跳过

    # 1. 自动生成 Session Log（§3.9.3 YAML 格式）
    handoff = auto_handoff_log.generate()

    # 2. 自动 §5.10 五级切片
    chunks = knowledge_slicer.slice(handoff)

    # 3. 自动 G1-G5 五门禁管道
    ke_count, ko_count = 0, 0
    for chunk in chunks:
        result = ingest_pipeline.run(chunk)  # §5.1-5.6: Ingest→Triage→Analyze→Activate→Extract
        if result.entity_type == "KE":
            ke_count += 1
        else:
            ko_count += 1

    # 4. 自动归档
    archive_handoff(handoff)
    logger.info(f"[轨道1] 完成: {len(chunks)} slices → {ke_count} KE + {ko_count} KO")
```

**触发器B：pre-commit failure → 轨道2（门禁阻断自动吸收）**

```python

### Unique Constraints
### 11.3 文件创建约束

- 每次 session 新建文件 ≤ 5 个（AGENTS.md §5.1 认知约束）
- 所有路径使用绝对路径
- 所有 Python 文件必须通过 ruff + mypy + pytest 三阶段质检
- 知识文件（KE .md）必须标注 UTF-8 编码、无BOM、LF换行

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md
