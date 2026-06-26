---
module_id: KE-1150--------1-000
status: active
title: IRN-001：编码扫描（铁律1）
category: governance
ttl: permanent
---

# IRN-001：编码扫描（铁律1）

IRN-001：编码扫描（铁律1）

所有 YAML/Markdown 文件写入后，必须运行编码扫描确认文件为 UTF-8 编码。

- 验证方法：`python scripts/hooks/check_encoding.py`
- 违反后果：阿拉伯文乱码，双重编码损坏
