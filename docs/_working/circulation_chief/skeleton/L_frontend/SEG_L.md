---
ttl: task_bound
title: L 段·前端报告链挖矿档（W3-3）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# L 段·前端报告链（F111-F115，5 环节）

> 方法同 SEG_I。运行态源=automation_panorama.md（10-01 13:07-13:16 快照）。
> 本轮要点：**F112 三断点已代码级定位**（schedulegate/审批族端点全部"异常降级空态"）；**L 段全段快照无进程**（api_server/app_panel 均不在全景两表），常驻性依赖 I-10 启动链（其自身存疑）。

## 六向台账

| 环节id | 名称 | 上游 | 下游 | 生产者路径:行 | 消费者 | 自动化态 | 运行态 | 三态复核(骨架→本轮) |
|--------|------|------|------|--------------|--------|----------|--------|--------------------|
| L-01(F111) | Panel 仪表盘 | F112 | Owner 值守 | src/zephyr/frontend/dashboard/app_panel.py（574 行）；:50-53（panel serve --port 5006 使用注记） | Owner 浏览器 | 常驻（骨架） | **快照无 panel 进程**（全景 §1.2 零命中） | 挖干(退役时点待裁)→挖干（码面）+运行态空白注记 |
| L-02(F112) | API server | 全台账 | F111/L-03 | src/zephyr/frontend/dashboard/api_server.py（5490 行，**54 路由** grep 实测）；AI 尾部路由 :5373(budget-advisories)/:5389(schedulegate-queue)/:5417(schedulegate-skeletons)/:5445(schedulegate-confirm)/:4968(promotion-advisories)/:5014(promotion-decide) | app_panel/渲染器/Owner | 常驻（骨架） | **快照无 api_server 进程**；启动链=desktop shell ensureApi（register_desktop_shell_startup.ps1:7），而 I-10 自身存疑 | 挖干(AI 层两新页三层三断点=红点)→挖干（码面 54 路由）+**红点坐实并定位**——详见 F112.md |
| L-03(F113) | 可视化渲染器 | F112 | F111 | src/zephyr/frontend/{graph_view_renderer,lineage_view_renderer,domain_mapping_view,trace_waterfall_view,value_stream_view,compliance_dashboard}.py（≥5 件，ls 实测；**在 frontend/ 根不在 dashboard/**，骨架路径口径微偏） | app_panel 视图 | 事件 | 随 panel 进程 | 挖干→挖干（路径注记：渲染器族在 frontend/ 根） |
| L-04(F114) | 通知路由 | F81 | F111/外部渠道 | src/zephyr/frontend/notification_router.py:70(Severity)/:87(NotificationChannel)/:95(ChannelBinding)/:104(SilentWindow) | implementations/feishu_bot_sender.py（grep 实测唯一实现消费方） | 事件 | 随上游告警流（I-06 运行载体未证→本环输入端同悬） | 挖干→挖干（输入端联动注记） |
| L-05(F115) | 报告生成 | F102/F50 | Owner | src/zephyr/reporting/ 38 项（attribution.py:62/:72/:80 类族；ashare_performance_audit.py 在档） | Owner 报告 | 定时/手动 | 未见独立任务挂接（全景零命中）——按需手动/上游评审周期调用 | 存疑(M6 补挖)→存疑——详见 F115.md |

## 段内小结

- 环节 5：挖干 4（码面，F111/F112/F113/F114 各带运行态/路径注记）+ 存疑 1（F115）。
- **段级运行态风险**：快照时刻全段无进程；若 desktop shell 启动链（I-10/F85）未注册或未开机自启，L 段"常驻"口径整段失真——与 ../I_scheduler/F85.md 同办。
- F112 红点从"注记"升级为"代码级三断点定位"，处置处方见 F112.md。
