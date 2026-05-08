---
module_id: KE-module_blu-5_2_python___________pyproject-000
title: 5.2 Python 依赖（锁定版本写入 pyproject.toml）
category: module_blueprint
---

# 5.2 Python 依赖（锁定版本写入 pyproject.toml）

5.2 Python 依赖（锁定版本写入 pyproject.toml）

```toml
[project.optional-dependencies]
vector-memory = [
    "chromadb==0.6.*",
    "onnxruntime>=1.17,<2.0",
    "transformers>=4.40,<5.0",  # BGE-M3 tokenizer
    "filelock>=3.13",
    "pydantic>=2.5,<3.0",       # 已有
]
```
