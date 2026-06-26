---
module_id: KE-2124
status: active
title: 3.5 #36: CliffDetector (M-34)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.5 #36: CliffDetector (M-34)

3.5 #36: CliffDetector (M-34)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\cliff_detector.py`

实现 `CliffDetector` 类（蓝图 L3347-3411）：
- 三维检测：CPU/MEM/TOKEN × 二阶导数（acceleration）
- `compute_cliff_proximity() -> float`：0→1 近悬崖度
- `pre_empt_evacuate()`：撤离 = 渐进降低 AI 吞吐量
- 蓝图 L3347-3411 算法完整实现
