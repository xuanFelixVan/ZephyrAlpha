---
module_id: KE-2306
status: active
title: 5.3 覆盖率仪表板
category: module_blueprint
---

# 5.3 覆盖率仪表板

5.3 覆盖率仪表板

```yaml
coverage_dashboard:
  views:
    - name: "detector_coverage_matrix"
      description: "漂移维度 × 检测器 矩阵——哪些维度已有检测、哪些是盲区"
    - name: "module_health_index"
      description: "每个模块的综合漂移评分 = velocity × severity × resolution_rate"
    - name: "drift_heatmap"
      description: "按时间轴的漂移事件热力图——一眼看出哪个时段/模块最不稳定"

  export:
    - format: "MCP Tool call → 返回 JSON 摘要（< 500 token）"
    - format: "CLI 报告 → 文本表格"
```
