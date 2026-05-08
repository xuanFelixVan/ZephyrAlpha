---
module_id: KE-documentat-5_2_p0-000
title: 5.2 P0 短板集中诊断
category: documentation
---

# 5.2 P0 短板集中诊断

5.2 P0 短板集中诊断

**4 项 P0 短板（G-1 ~ G-4）都集中在 T1 真实资金接入路径上**：风控 → 执行 → 合规 → 数据 是**真实资金上线的四大硬基石**，四项都需要从 L1/L2 跳到 L4。这与 09-GOV T1 触发器完全一致（T1 触发 L04/L06/L10/L00 的治理 Runtime 层全部激活）。

**施工建议**：
- **Sprint 9（发布守卫）**：G-4 数据（PIT/Lineage 落地）+ G-3 合规（09-GOV L3 三件套 + L4 fitness functions）
- **Sprint 10（施工 + AI Safety）**：G-1 风控（kill switch + limits hard cut）+ **G-10 CC-3 AI 自治**（D-01 AISG scaffold 硬闸门，Sprint 0 启动前已过）
- **Sprint 11（业务运行时）**：G-2 执行（OMS + SOR + 券商接入）
- **Sprint 12（T1 接入前 gate）**：G-1/G-2/G-3/G-4 全部到 L4 才解锁 T1
