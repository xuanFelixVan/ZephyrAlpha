---
module_id: KE-1661
status: active
title: 2.1.1 asset_type（资产类型——基于目录位置 + 扩展名）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1.1 asset_type（资产类型——基于目录位置 + 扩展名）

2.1.1 asset_type（资产类型——基于目录位置 + 扩展名）

```python
from enum import StrEnum

class AssetType(str, Enum):
    MODULE = "module"        # src/zephyr/**/*.py（Python 模块）
    SCRIPT = "script"        # scripts/**/*.py（独立脚本）
    DOC = "doc"              # docs/**/*.md（蓝图/标准/报告）
    CONFIG = "config"        # config/**/*.yaml + *.json + *.toml
    GATE = "gate"            # src/zephyr/gates/*.yaml
    TEST = "test"            # tests/**/*.py
    DATA = "data"            # data/**/*.db + *.jsonl + *.yaml
    INFRA = "infra"          # pyproject.toml / .gitignore / *.bat / *.ps1
    REGISTRY = "registry"    # *_registry.yaml / *manifest.yaml
    UNKNOWN = "unknown"      # 无法自动分类——需人工判定
```

**分类规则**（纯机械——基于目录前缀 + 扩展名映射，无需 AI 判断）：

| 目录前缀 | 扩展名 | → asset_type |
|----------|--------|-------------|
| `src/zephyr/gates/` | `.yaml` | `gate` |
| `src/zephyr/` | `.py` | `module` |
| `scripts/` | `.py` | `script` |
| `docs/` | `.md` | `doc` |
| `config/` | `.yaml/.json/.toml` | `config` |
| `tests/` | `.py` | `test` |
| `data/` | `.db/.jsonl/.yaml` | `data` |
| 根目录 | `.toml/.bat/.ps1` | `infra` |
| 任意 | `_registry.yaml/manifest.yaml` | `registry` |
