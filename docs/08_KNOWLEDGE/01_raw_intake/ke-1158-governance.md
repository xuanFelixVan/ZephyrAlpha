---
module_id: KE-1073
status: active
title: ✅ 正确（真正不确定类型时，用显式 Any 而非裸写）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# ✅ 正确（真正不确定类型时，用显式 Any 而非裸写）

✅ 正确（真正不确定类型时，用显式 Any 而非裸写）
from typing import Any
def deserialize(raw: bytes) -> Any:  # 至少表态"我知道这里是动态类型"
    ...
```
