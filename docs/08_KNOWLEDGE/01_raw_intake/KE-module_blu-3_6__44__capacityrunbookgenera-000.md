---
module_id: KE-module_blu-3_6__44__capacityrunbookgenera-000
title: 3.6 #44: CapacityRunbookGenerator
category: module_blueprint
---

# 3.6 #44: CapacityRunbookGenerator

3.6 #44: CapacityRunbookGenerator

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_runbook_generator.py`

- `generate_from_incident(incident)`: 产出诊断方法+修复步骤+预防措施
- `_score(incident)`: 自评Runbook质量(0-100)，Owner审核加分
- 存储：`data/runbook/` Markdown格式
