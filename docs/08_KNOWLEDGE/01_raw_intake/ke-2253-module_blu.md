---
module_id: KE-2159------7-003
title: 3.9.1 来源矩阵（7 条全自动管线）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.9.1 来源矩阵（7 条全自动管线）

3.9.1 来源矩阵（7 条全自动管线）

| # | 来源 | 触发方式 | 自动率 | 输出 | 频率 | Owner 角色 |
|:--:|------|---------|:---:|------|:---:|---------|
| 1 | **AGENTS.md / 治理标准变更** | git hook + L3 哨兵自动检测 | 100% | KO→KE（A3） | 每次 commit 含规则文件 | 无需介入 |
| 2 | **跨层契约（CTR）版本升级** | CTR-001~CTR-006 YAML version bump → `schema_version` 变更事件 | 100% | KE（A2） | CTR version bump 时 | 无需介入 |
| 3 | **蓝图版本升级** | bp version bump 事件 | 100% | KE（A2/A3/A5） | version bump 时 | 无需介入 |
| 4 | **Pre-commit / CI 阻断** | pre-commit hook 捕获 | 100% | KO→KE（A4） | 每次阻断 | 无需介入 |
| 5 | **Session Log 生成** | auto-handoff-log.py 完成 | 100% | KO→KE（A1-A8）| 每次 session 结束 | 无需介入 |
| 6 | **外部论文 / 开源项目** | Session Log 中出现了 arXiv/GitHub 链接 → 自动触发 D0 流水线 | 80% | KO→KE（B1-B7） | 按需（自动检测+自动触发） | **仅审批**：系统自动生成 KO 草稿 → 推送提醒 Owner "3 条新知识待审批，回复 yes/no" |
| 7 | **知识差距巡检** | APScheduler 每周 cron | 100% | KO（GAP）→ 推送 Owner 查看 | 每周一次 | **仅查看**：系统自动生成差距报告 → 推送 Owner "本周发现 2 个知识空白" |
| 8 | **CTR 运行时质量信号** | CTR-001 `quality_score` / CTR-002 `confidence` / CTR-005 `slippage` 连续 N 次超阈值（如 quality_score<0.3 连续10天）→ 自动触发 | 100% | KO→KE（B1/B3） | 异常事件驱动 | 无需介入 |

**关键设计**：来源 6（外部知识）和来源 7（差距巡检）是仅有的需要 Owner 参与的管线——但不是"Owner 记得启动"，而是系统自动检测→自动生成草稿→自动推送提醒→Owner 只需回复 yes/no（一个词）。来源 8（CTR运行时质量信号）是 100% 自动的——异常事件驱动，零Owner触发。
