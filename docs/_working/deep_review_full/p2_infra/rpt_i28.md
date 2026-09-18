---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——旧版dashboard装配
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：旧版dashboard装配（I28）

- 状态: **已审**
- 级别: P3｜类型: 前端
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/frontend/dashboard/app.py:74`（DashboardApp）
- 生产调用方: **无**（grep 全仓仅 tests/governance/observability/test_dashboard_unit.py 消费 create_app）
- 测试文件: tests/governance/observability/test_dashboard_unit.py（消费方即测试）
- 备注: 自述"已弃用 v3.1.0"（Streamlit→Panel）；无副作用 import，全文件纯薄层

## 1 对象快照

- 审查范围：`app.py` 全文 143 行：DashboardApp 编程式门面（5 个 fetch/render 委托 components/*）+ create_app 工厂 + main 弃用提示。
- 排除项：components/* 五个被委托组件；app_panel/web 两级后继前端（I27）。
- 测试覆盖概况：test_dashboard_unit 直接测本件（唯一消费者=测试）。
- 材料包缺项：无（对象极小，全部代码已读）。
- 变更热力：17 次提交，低热区。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C 下游 | 生产调用方为零，唯一消费者是测试——弃用门面的事实孤儿（模式 #8；保留价值=编程式 API，但无生产编程方） | app.py 全仓 grep 仅测试引用 | P3 | grep 命令见备注 |
| D 旁系 | **弃用链三级接力失真**：app.py 弃用文案指引"请用 panel serve app_panel.py"（:28-30, :136-138），而 app_panel.py 自身 2026-08-29 已弃用指向 web/——跟随指引落到第二个弃用件；且本件头注 MATURITY=production 与正文"已弃用"直接矛盾 | app.py:7 vs :22-30, :136-138 + app_panel.py:5-10 | P3 | 三文件头注对照 |
| A 深度 | render_page 用 if/elif 字符串路由返回 dict（:108-125）：未知页返回 {"error": ...} 而非抛错——编程式契约温和，无安全面；无路由注册表（新增页须手改两处） | app.py:108-125 | P3 | code review |
| B 上游 | fetch_* 委托未注入 repo/engine 时依赖组件内部默认（如 fetch_knowledge_overview() 无参）——上游默认行为归组件对象群，本件无校验无防御（薄层设计如此，可接受） | app.py:93-106 | — | — |
| A 深度(测试) | 测试即消费者的自指结构：弃用后测试仍在维护（tests/dashboard_unit 17 次 churn 的一部分）——退役决策需连测试同批 | tests/governance/observability/test_dashboard_unit.py:26,161-172 | P3 | 收口方退役时同批处理 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 弃用入口治理（deprecation pointer chain） | **立卡候选（治理动作）**：业界惯例=弃用件直接指向当前正式家（不留中间跳）；本件指向的"正式家"自身已再弃用——建议一次性把弃用文案与头注直指 web/ 并改 MATURITY=deprecated | 受 WebSearch 限流批次影响（本对象无外部算法可对照，惯例类来源=Python deprecation 惯例/各框架 BREAKING 文档），如实记 |

## 4 缺陷清单

1. **D-1（P3）弃用件三处文档失真**：MATURITY=production vs 正文弃用；指引链经 app_panel 二跳；[TESTS]/[INVARIANTS] 头注空。修法=一次性改头注+直指 web/。
2. **D-2（P3）孤儿门面**：无生产消费者，建议随前端收敛裁定退役（连测试同批），或明确"编程式 API 保留"的预期消费者。

## 5 挂起疑问

- 是否存在仓外脚本/Notebook 消费 DashboardApp（仓内不可证）——退役前建议 Owner 确认。

## 6 完备性自评

- 六轴全查（对象仅 143 行薄层：A/B/C/D/E 逐条有结论；无并发无重入无幂等面；F 无外部算法对照可做，如实记）。
- 长尾：无。
