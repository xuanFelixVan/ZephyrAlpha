---
module_id: KE-documentat-2_4-000
title: 2.4 为什么是三平面而不是两平面或四平面
category: documentation
---

# 2.4 为什么是三平面而不是两平面或四平面

2.4 为什么是三平面而不是两平面或四平面

| 切法 | 业界采纳度 | 优点 | 缺点 |
|---|---|---|---|
| 两平面（Hot + Cold）| 少数（早期 HFT）| 简单 | 忽略"异步决策 / AI 推理"这类中频场景，被迫挤进 Hot 或 Cold 都不合适 |
| **三平面（Hot / Warm / Cold）✅ 采纳** | **主流**（Citadel / Jane Street / Two Sigma / Jump / Renaissance）| 覆盖高 / 中 / 低三档延迟预算，匹配量化系统三类实时性需求 | 对 < 100µs 超低延迟场景描述不够细（可未来增补 "Ultra-Hot" 子档）|
| 四平面（Ultra-Hot / Hot / Warm / Cold）| 少数（纯 FPGA 做市商如 Jump HF desk）| 对超低延迟有独立预算 | 当前 ZephyrAlpha 无 FPGA 预算 → 过度抽象 |

**结论**：**三平面是业界共识最佳点**（5/5 家顶级机构采纳），ZephyrAlpha 采纳三平面 + 预留未来 "Ultra-Hot" 下钻能力（§5.4）。

---
