---
module_id: KE-2319
status: active
title: 5.5 编码铁律
category: module_blueprint
ttl: permanent
---

# 5.5 编码铁律

5.5 编码铁律

所有脚本文件开头必须：

```python
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

> Windows 终端默认 GBK 编码 → emoji/中文输出崩溃 → 强制 UTF-8
