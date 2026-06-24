---
module_id: KE-271
title: 3.2.3 protocol vs policy 的区别
category: documentation
---

# 3.2.3 protocol vs policy 的区别

3.2.3 protocol vs policy 的区别

| 维度 | policy | protocol |
|------|--------|----------|
| 主体 | 单方约束 | 多方交互 |
| 核心问题 | "必须/禁止什么" | "谁先做什么，然后谁做什么" |
| 例子 | "密钥必须加密存储" | "交接协议：发出方 → 审核方 → 接收方" |
| 判断标准 | 只涉及一方 | 涉及两方以上的交互时序 |

**简单判断**：如果文件描述的是"谁→谁→谁"的交互流程，用 `protocol`；如果只是"必须/禁止 X"，用 `policy`。
