---
module_id: KE-3508
title: 17. 变更记录
category: governance
---

# 17. 变更记录

17. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-06 | 2.1.1 | 对齐 `registry-master-index.yaml`：移除误用的「24 张」常数，改为 `total_registries` 真源 + MRS-001 分类说明；自检清单同步。 |
| 2026-05-02 | 2.0.0 | **重大扩展**：MRS-001 操作矩阵从 3 列（仅模块登记表）扩展到 14 列（覆盖 registry-master-index.yaml 的下全部可登记分类）。新增 8 种操作类型（创建规则/脚本/ADR/知识/目录/门禁/任务卡/字段）。MRS-004 禁止行为从 4 条扩展到 6 条（新增 SearchReplace 误匹配 + 新登记表不注册）。depends_on 新增 registry-master-index.yaml。Token 预算更新（2000→3000）。 |
| 2026-05-02 | 1.0.0 | 初始版本——定义 MRS-001~004 四条核心规则，仅覆盖模块登记表（module-registry.yaml + blueprint_registry.yaml + 物理 blueprint.md） |
