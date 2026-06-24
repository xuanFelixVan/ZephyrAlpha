---
module_id: KE-562
title: 7.5.4 与 `runtime_planes.md` 的同步规则
category: documentation
---

# 7.5.4 与 `runtime_planes.md` 的同步规则

7.5.4 与 `runtime_planes.md` 的同步规则

| 当发生这些变动时 | 必须联动更新 |
|----------------|------------|
| 新增前端 App | 本节 §7.5.1 加一行（标注 Warm / Hot-adjacent / Cold）+ `04bis` §3.4 前端平面归属表同步 |
| 前端某模块延迟预算从 Warm 升级到 Hot-adjacent（或降级） | 本节 §7.5.2 Hot-adjacent 表更新 + `04bis` §5 跨面通信协议章节同步 + KB 决策记录审批（如果是 Hot-adjacent 首次引入一整类场景）|
| SSR 报表或批处理导出服务启用 | 本节 §7.5.3 + `04bis` §3.4 + 04-TA Cold Path 技术栈章节同步 |

**硬约束**：任何前端模块若自称 "Hot Path 原生"（< 10ms + kernel-bypass + 不可中断）均属**伪 Hot 声明**——浏览器技术栈无法满足 04bis 定义的 Hot Path 硬门槛，PR reviewer 必须驳回。前端所有低延迟需求的上限都是 Hot-adjacent。
