---
module_id: KE-2027----api-000
status: active
title: 3.1 公共 API
category: module_blueprint
---

# 3.1 公共 API

3.1 公共 API

> 列出所有公开类和方法。每个方法必须包含：函数签名 + 输入/输出说明 + 核心逻辑描述。

```python
from pydantic import BaseModel

class {ModuleName}:
    """模块主类——一句话说明职责"""

    def method_name(self, param: str) -> "{ResultType}":
        """
        方法说明

        输入：param 的含义和约束
        输出：ResultType 的含义和结构
        核心逻辑：简要描述做什么
        """
        ...
```
