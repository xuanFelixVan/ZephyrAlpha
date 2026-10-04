---
ttl: task_bound
---

# 90 红蓝对抗（重建版）

R1 PASS（NULL list_date 注入→ifNull 兜底 2000-01-01，四表 DEFAULT 生效）；R2 PASS（真值保护：09-09 295,983 行 tdx 日拒写）；R6 PASS（0929 回填重跑 todo=0 全跳过/计数不变）；R7 PASS（auction derive 重跑 FINAL 5,572 精确复原）；R8 PASS（TableRegistry 正确+未知 key fail-closed）；R5 改判 HOLD→解冻（批9/批10 契约演进考古翻案，v2 深窗抽验健全）；R3/R4 时点终验移交晨检（cffex 死信归零/internal_eqw 首跑）。
