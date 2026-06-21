---
module_id: KE-555------6-002
title: 9.2 4 环境 × 6 维度矩阵
category: documentation
---

# 9.2 4 环境 × 6 维度矩阵

9.2 4 环境 × 6 维度矩阵

| 维度 | **Dev** | **UAT** | **Staging** | **Prod** |
|------|---------|---------|-------------|----------|
| **数据源** | 模拟/AKShare 历史 | 模拟+部分真实 | 真实行情（延迟 15min） | 真实实时行情 |
| **LLM** | Cursor IDE 内置 | IDE + 少量 Runtime API | Runtime API 完整配置 | Runtime API + 降级策略 |
| **资金** | 无（SimulationAdapter） | 无（纸盘交易） | 极小仓位 / Shadow | 真实资金（个人） |
| **监控** | 本地日志 | 结构化日志 + 基础告警 | 完整 OTel + Grafana | 全量 OTel + 实时告警 |
| **审批** | 无 | Architect Review | ADR + 回测验证 | 双重确认 + 回滚计划 |
| **回退** | `git checkout` | 重载上一版本 | 快照恢复 | Emergency Stop → 清仓 → 版本回滚 |
