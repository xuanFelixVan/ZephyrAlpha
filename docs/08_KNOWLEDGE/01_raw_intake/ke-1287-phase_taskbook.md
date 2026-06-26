---
module_id: KE-1200
status: active
title: 检查每个 Phase taskbook 必须有双门
category: governance
ttl: permanent
---

# 检查每个 Phase taskbook 必须有双门

检查每个 Phase taskbook 必须有双门
def validate_phase_transition_schema(taskbook_path: str) -> list[Violation]:
    violations = []
    frontmatter = parse_frontmatter(taskbook_path)

    if "phase" not in frontmatter:
        violations.append(P0("missing 'phase' field"))

    if "exit_criteria" not in frontmatter or not frontmatter["exit_criteria"]:
        violations.append(P0("missing or empty 'exit_criteria'"))

    # stable 例外：无 next_phase_entry_criteria
    if frontmatter["phase"] < 4:
        if "next_phase_entry_criteria" not in frontmatter:
            violations.append(P0("missing 'next_phase_entry_criteria'"))

    # 零暗门原则校验
    entry_items = frontmatter.get("next_phase_entry_criteria", [])
    for item in entry_items:
        if "references_exit" not in item and not is_entry_exclusive(item):
            violations.append(P0(
                f"ENTRY {item['id']} violates zero-backdoor principle: "
                f"no references_exit and not entry-exclusive"
            ))

    return violations
```

---
