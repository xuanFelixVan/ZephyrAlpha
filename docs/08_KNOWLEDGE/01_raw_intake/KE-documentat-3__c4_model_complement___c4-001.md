---
module_id: KE-documentat-3__c4_model_complement___c4-001
title: 3. C4 Model complement / C4 模型补充
category: documentation
---

# 3. C4 Model complement / C4 模型补充

3. C4 Model complement / C4 模型补充

TOGAF resolves "vertical layering". C4 Model (Simon Brown) resolves "how to visualize the inside of Application Architecture":

TOGAF 解决"垂直分层"，C4 Model（Simon Brown）解决"应用架构内部如何可视化"：

| Level / 级别 | Focus / 关注点 | Usage in this project / 本项目用法 |
|-------------|--------------|----------------------------------|
| **L1 — System Context** | System's position in the external world / 系统在外部世界中的位置 | ✅ Required / 必画 → `diagrams/c4-l1-system-context.mmd` |
| **L2 — Container** | Independent deployable units inside the system / 内部可独立部署单元 | ✅ Required / 必画 → `diagrams/c4-l2-containers.mmd` |
| **L3 — Component** | Components inside a container / 容器内部组件分解 | 🟡 As needed / 按需，在蓝图中画 |
| **L4 — Code** | Class/function level / 具体类/函数级别 | ❌ Not drawn / 不画（代码本身即文档）|

**TOGAF + C4 = the most mainstream combination in industry for complete enterprise architecture expression.**
**TOGAF + C4 = 工业界最主流的完整企业架构表达组合。**

---
