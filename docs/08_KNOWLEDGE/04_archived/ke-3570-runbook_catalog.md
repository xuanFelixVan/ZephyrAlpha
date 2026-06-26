---
module_id: KE-3427
title: §9 Runbook Catalog / 操作手册目录
category: documentation
ttl: permanent
---

# §9 Runbook Catalog / 操作手册目录

§9 Runbook Catalog / 操作手册目录

> **本节为占位目录清单。** Runbook 文件将在各运维域激活时独立建档，统一存放于 `docs/19_development_workspace/runbooks/`（待创建）。

| ID | 域 | Runbook 名称 | 触发场景 | 状态 |
|----|---|--------------|---------|------|
| RB-D1-01 | 部署 | 标准发布 Runbook | 每次版本发布 | 🔲 待建 |
| RB-D1-02 | 部署 | 紧急回滚 Runbook | 发布后出现严重缺陷 | 🔲 待建 |
| RB-D2-01 | 监控 | 告警响应标准流程 | P0 告警触发 | 🔲 待建 |
| RB-D2-02 | 监控 | 监控巡检清单 | 每周日常巡检 | 🔲 待建 |
| RB-D3-01 | 备份 | 数据备份验证 Runbook | 每月备份验证 | 🔲 待建 |
| RB-D3-02 | 备份 | 数据恢复演练 Runbook | 每季度 DR 演练 | 🔲 待建 |
| RB-D4-01 | 灾备 | 主机故障切换 Runbook | 主机不可用 | 🔲 待建 |
| RB-D5-01 | 变更 | 变更后验证清单 | 每次变更发布后 | 🔲 待建 |
| RB-D6-01 | 事件 | Post-Mortem 模板 | 每次 P0/P1 事件后 | 🔲 待建 |
| RB-D7-01 | 容量 | 资源用量月度报告 | 每月容量复盘 | 🔲 待建 |
| RB-D8-01 | 成本 | LLM Token 费用报告 | 每月成本复盘 | 🔲 待建 |
| RB-SVC-01 | 6大核心服务 | 冷启动 Runbook（依赖 DAG 序）| 系统重启 | 🔲 experimental P0 |
| RB-SVC-02 | 6大核心服务 | VMS ChromaDB 重建 Runbook | 持久化损坏 | 🔲 experimental P0 |
| RB-SVC-03 | 6大核心服务 | LSG 策略表更新 Runbook | 红队发现新攻击模式 | 🔲 experimental P0 |
| RB-SVC-04 | 6大核心服务 | FLE SQLite 归档 Runbook | 数据量 > 100MB | 🔲 experimental P1 |
| RB-SVC-05 | 6大核心服务 | Agent Sandbox 逃逸响应 | 沙箱违规告警 | 🔲 experimental P0（→ IR-SEC-002）|

---
