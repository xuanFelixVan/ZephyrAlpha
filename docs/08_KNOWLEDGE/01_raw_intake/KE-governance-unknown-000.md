---
module_id: KE-governance-unknown-000
title: 目录创建模板
category: governance
---

# 目录创建模板

目录创建模板

当索引中已有定义（Step ② → 是）时，按以下模板创建目录后写入文件：

```python
import os

target_dir = "D:\\ZephyrAlpha\\\{按索引确定的路径}"
os.makedirs(target_dir, exist_ok=True)
