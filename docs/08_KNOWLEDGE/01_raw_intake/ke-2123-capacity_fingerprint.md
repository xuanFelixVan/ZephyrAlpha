---
module_id: KE-2031---000
status: active
title: 3.1 #39: CapacityFingerprint (M-36)
category: module_blueprint
ttl: permanent
---

# 3.1 #39: CapacityFingerprint (M-36)

3.1 #39: CapacityFingerprint (M-36)

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_fingerprint.py`

实现 `CapacityFingerprint` 类：
- `fingerprint(module_path)`: 生成模块容量指纹（loc/import数/class数/function数/依赖数/AST深度 + 运行时import_time/memory_delta）
- `compare(old, new)`: 比较新旧指纹，检测退化：
  - 内存用量 > 2× → Warning
  - 导入时间 > 3× → Warning
  - 代码行数 > 1.8× 但函数数 ≤ 1.1× → 过度设计警告
- 集成到 G5 门禁（合入前容量指纹检查）
