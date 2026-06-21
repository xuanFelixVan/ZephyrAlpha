---
module_id: KE-2504
title: 9. 渐进路线
category: module_blueprint
---

# 9. 渐进路线

9. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范 + ADR-0020 | status=Active |
| **experimental** | `InProcessLSG` + L1-L4 四层基础 + MCP Server 前置接线 + pre-commit hooks | ① §12 P0 用例通过<br>② 红队 corpus bypass 率 < 5%<br>③ secret 泄漏 0 件 |
| **beta** | FLE 接入（指标 + bump_strictness） + Orchestrator/CE/VMS 全量接入 | 闭环：bypass 尖峰自动提升严格度 |
| **beta** | `RemoteLSG`（多进程策略共享） + SBOM 全流程 | 企业合规触发 |
| **stable** | 策略中心 + 多环境统一 + ML 补充分类器 | 规则漏报 > 10% 触发 |

---
