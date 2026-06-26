---
module_id: KE-4231
title: 9. 渐进路线
category: module_blueprint
ttl: permanent
---

# 9. 渐进路线

9. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范定稿 | KBG-0015 Active + 本规范 Active |
| **experimental** | `InProcessContextEngine` 实现 + 默认权重 + Cursor 注入 | ① §12 P0 用例通过<br>② build 端到端 ≤ 1.5s（VMS 稳态）<br>③ Cursor 下 inject 成功率 ≥ 99% |
| **beta** | Trae / Claude-Desktop 通道适配 + Feedback Loop 接入 | 多 IDE 切换零重写 + `adjust_strategy` 动态生效 |
| **beta** | 服务化 `RemoteContextEngine` | 多 IDE 实例并发 build ≥ 3 时触发 |
| **stable** | 自适应 slot 预算（强化学习） | Feedback 数据量 > 10k 次 |

---
