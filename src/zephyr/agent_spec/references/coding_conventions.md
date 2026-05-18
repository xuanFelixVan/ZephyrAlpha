---
blueprint_id: MOD-INF-019
---

# L3 Reference: Coding Conventions

> Belongs to: implementer (SKILL-ROL-IMP-001)
> Must comply before any file write

## Project-wide Rules

1. **Never write comments in generated code** — blueprint is the SSoT
2. **All imports at top of file**, grouped: stdlib → third-party → zephyr
3. **Type annotations mandatory** on all public functions
4. **No single-letter variables** except in loop counters (i, j, k)
5. **Max line length**: 120 chars (black formatter default)
6. **Encoding**: UTF-8 with `# -*- coding: utf-8 -*-` header not needed (Python 3 default)

## Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Modules | snake_case | `skill_factory.py` |
| Classes | PascalCase | `PipelineOrchestrator` |
| Functions | snake_case | `progressive_load()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES = 3` |
| Private members | `_leading_underscore` | `self._cache` |

## File Structure Template

```python
"""Module docstring — one-line summary + extended description."""

from __future__ import annotations

import stdlib_module
from third_party import ClassName

from zephyr.internal import InternalClass

_MODULE_CONSTANT = "value"

class PublicClass:
    """Public API class."""

    def __init__(self, param: str):
        self._private_field = param
```

## Gate Requirements Before Write

- G0: Syntax valid (AST parse)
- G1: Import resolution (all imports resolvable)
- G3: Schema validation (if data model)
- G6: Security scan (no hardcoded secrets, no eval/exec)
- G7: Docstring present on all public classes/functions
