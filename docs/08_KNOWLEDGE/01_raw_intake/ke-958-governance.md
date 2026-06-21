---
module_id: KE-880
status: active
title: 4. 违规响应流程
category: governance_rule
---

# 4. 违规响应流程

4. 违规响应流程

```
发现违规 → 判断级别 → 执行响应

V1 阻断：
  1. 阻止当前操作
  2. AI 记录违规到 Session Log
  3. 修复问题后重新提交

V2 警告：
  1. 允许继续操作
  2. AI 记录警告到 Session Log
  3. 同类型警告 3 次 → 升格为 V1

V3 审查发现：
  1. 记录到审查报告
  2. 分类：立即修复 / 下次修复 / 记入 Backlog
  3. Owner 裁定优先修复顺序

V4 抽样发现：
  1. 产出审计报告
  2. 向 Owner 提出系统性改进建议
```

---
