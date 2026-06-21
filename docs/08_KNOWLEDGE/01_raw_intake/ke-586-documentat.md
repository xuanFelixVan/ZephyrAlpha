---
module_id: KE-527
status: active
title: §8.2 激活监控机制
category: documentation
---

# §8.2 激活监控机制

§8.2 激活监控机制

**何时应当 Review 一次 Runway？**

| 触发类型 | 频率 | 动作 |
|---------|------|------|
| **季度例行 Review** | 每 3 个月（对齐 technology-landscape.md 刷新周期）| 对照 `p3-blueprint-index.md §6 激活监控清单` [待创建] 逐项检查触发条件 |
| **重大里程碑后** | 事件驱动 | 接入真实资金 / P0 流水线稳定运行 3 个月 / 因子库突破 100 条 / 团队规模扩展 |
| **架构重大变更后** | 事件驱动 | 新增技术选型（ADR 新增）/ 撤回某条 P1-P2 能力 / 合规要求改变 |

**如何判断是否应激活某条 Runway？**

1. **检查触发条件**：对照该条目 "激活触发条件" 列，所有条件是否已满足（AND 逻辑）
2. **更新 activation_status**：在 `p3-blueprint-index.md` [待创建] 中将该条目 `activation_status` 从 `deferred` 改为 `ready`
3. **人工拍板**：发起架构评审（Architect + AI Operator），确认资源预算（参考 04-TA §11/§12）
4. **记录决策**：激活决策写入 KB decisions namespace（替代原 adr/ 目录）
5. **Runway 条目归档**：激活后将该条目从视图 Runway 章节移除（或标注 `activated`），避免堆积

**不应激活的信号（Hold 住）**：
- 触发条件未满足，但希望"先做准备"→ **不激活**，可在 P3 条目附注研究计划
- 激活成本（人月）> 当前阶段 ROI → **推迟**，下季度重评
- 依赖基础能力（P0/P1）尚未稳定运行 → **阻塞**，先修底层

---
