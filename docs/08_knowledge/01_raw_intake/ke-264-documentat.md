---
module_id: KE-242
title: 3.1 三轴定义
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 三轴定义

3.1 三轴定义

| 轴 | 取值 | 判定规则 |
|----|------|---------|
| **温度** | 热（Hot） / 温（Warm） / 冷（Cold） | 热 = 实时读写，分钟级访问；温 = 当日/近期，分钟到小时；冷 = 历史，按需重载 |
| **节奏** | 流（Stream） / 批（Batch） | 流 = 持续到达，无明确边界；批 = 周期性快照或夜间任务 |
| **来源** | 外（External） / 内（Internal） / 派生（Derived） | 外 = 外部 vendor；内 = 系统自产事件；派生 = 由其他实体计算得出 |
