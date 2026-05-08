---
module_id: KE-module_blu-6_6___--000
title: 6.6 文档-代码共演化
category: module_blueprint
---

# 6.6 文档-代码共演化

6.6 文档-代码共演化

```yaml
doc_code_coevolution:
  description: "代码改了但文档/蓝图没更新 = 反向漂移"
  checks:
    - name: "code_newer_than_blueprint"
      method: "max(代码文件 mtime) > blueprint.md mtime + 7 天 → 标记文档滞后"
    - name: "blueprint_interface_vs_code"
      method: "蓝图 §3 声明的接口列表 vs 代码实际公开接口——任一方向不一致 → 漂移"
```
