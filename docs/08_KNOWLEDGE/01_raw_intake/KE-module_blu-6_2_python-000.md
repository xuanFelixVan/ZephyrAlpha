---
module_id: KE-module_blu-6_2_python-000
title: 6.2 Python 依赖
category: module_blueprint
---

# 6.2 Python 依赖

6.2 Python 依赖

```toml
[project.optional-dependencies]
context-engine = [
    "networkx>=3.2,<4.0",
    "llama-cpp-python>=0.2.70",
    "tiktoken>=0.6",
    "filelock>=3.13",
    "pydantic>=2.5,<3.0",
]
```
