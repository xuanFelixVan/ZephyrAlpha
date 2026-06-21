---
module_id: KE-3580
title: D-NOISE：噪音与冗余
category: documentation
---

# D-NOISE：噪音与冗余

D-NOISE：噪音与冗余

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 图表是否都有文字说明 | ✅ | 29 个 .mmd 全部在对应视图文档中有文字说明 |
| 视图间无冗余重复 | ✅ | 00-overview 与各分视图关系 additive，04bis/04ter 作为正交视图不重复 TOGAF 内容 |

**P1-003**：`runtime_planes.md` §3.1 的 14 层 × 三平面映射矩阵（70 行）与 `runtime_planes.yaml` 中的 `planes.hot/warm/cold.modules[]` 存在维护双源风险。**根因**：文档中表格为人类可读派生，YAML 为机器可读 SSoT，符合正交视图方法论 OV-P3。**修复**：非 bug，但建议在文档表格顶部增加"本表为 YAML 只读派生，如有冲突以 YAML 为准"的声明（已存在，但可强化）。

---
