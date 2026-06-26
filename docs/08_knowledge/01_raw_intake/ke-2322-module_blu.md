---
module_id: KE-2227
status: active
title: 4.2 四阶段预检
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.2 四阶段预检

4.2 四阶段预检

```
A0 查重   →  检查 scripts/governance/ 下是否已有功能等价脚本
             $ python scripts/governance/run_all.py --list
             有 → 扩展；无 → 继续

A1 定位   →  确定目标位置：
             审核/校验类   →  scripts/governance/{dimension}/
             核心逻辑类    →  src/zephyr/lXX/
             测试类       →  tests/

A2 例外论证 →  不在以上三处的 .py 文件
             必须在 Session Log 中论证：
             "为什么不能放入标准位置" + "为什么是真正的一次性"
             论证不充分 = 入库失败
```
