---
module_id: KE-1240
status: active
title: 目录创建模板
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 目录创建模板

目录创建模板

当索引中已有定义（Step ② → 是）时，按以下模板创建目录后写入文件：

```python
import os

target_dir = "D:\\ZephyrAlpha\\\{按索引确定的路径}"
os.makedirs(target_dir, exist_ok=True)
