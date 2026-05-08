---
module_id: KE-governance-7_2_____src_zephyr_____c___or_-003
title: 7.2 新增 `src/zephyr/` 包（C 轨 or B 轨）
category: governance
---

# 7.2 新增 `src/zephyr/` 包（C 轨 or B 轨）

7.2 新增 `src/zephyr/` 包（C 轨 or B 轨）

1. 运行 §四 归属决策树，明确归属 C 轨或 B 轨
2. 若为 **C 轨新层**（L14+）：需要 ADR + 14 层总数变更的冲击评估
3. 若为 **B 轨新独立包**：需要 ADR + 接口合同 + Phase 路线
4. 在本文档 §三 记录新包
5. 创建骨架（`__init__.py` 带 docstring 说明轨道归属与架构真源）
6. Owner 批准后合入
