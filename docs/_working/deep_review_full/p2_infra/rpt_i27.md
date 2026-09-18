---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——运维控制台面板
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：运维控制台面板（I27）

- 状态: **已审**
- 级别: P3｜类型: 前端
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/frontend/dashboard/app_panel.py:170`（DashboardPanelApp）
- 生产调用方: panel serve / python 直跑（端口 5006）；components/* 14 个组件头注声明消费者=本件
- 测试文件: 组件级测试散布；本件主入口无专项测试
- 备注: 头注自述 **DEPRECATED（2026-08-29 Owner 裁定 R22/R23）**，正式家=web/（41 页）；保留不删（Owner 指令：确认涵盖后才能删）

## 1 对象快照

- 审查范围：`app_panel.py` 全文 574 行：DashboardPanelApp 组装 14 Tab（作战室+5 治理+8 交易/回测）、create_dashboard 装配（TaskRepository 默认注入+QMT 桥自动装配）、main/panel serve 钩子。
- 排除项：components/* 各 Tab 组件实现（14 个独立文件）；web/ 新版前端。
- 测试覆盖概况：无主入口测试；组件测试未逐一核。
- 材料包缺项：无运行证据（面板是否仍在被 Owner 使用——决定下述发现的实际权重）。
- 变更热力：23 次提交，中热区；**但最近一次（3b25f73aed miniQMT 退役过渡前端四批）仍在给"已废弃"面板加注入参数**——弃用声明与开发现实矛盾（见 D-1）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D 旁系 | **宪法 L0 §7 核心系统速查表仍指本件为仪表盘入口**（AGENTS.md："仪表盘=src/zephyr/frontend/dashboard/app_panel.py"），而头注 DEPRECATED+正式家=web/——L0 真源指针过期，所有 AI 会话按宪法会找到弃用件 | AGENTS.md §7 vs app_panel.py:5-10（DEPRECATED 头注） | P2 | 对照两文件即证 |
| D 旁系 | **弃用声明与开发现实矛盾**：2026-09-17 前后的 3b25f73aed（miniQMT 退役四批）仍在本件加 F2/F3 注入参数——新旧双前端并行演进，组件级功能双份承载（模式 #4 温床：web/ 版若漏移植 F2/F3 语义，两面板显示口径分叉） | app_panel.py:219-226（position/quote_broker_source 注入）+ git log 3b25f73aed | P2 | diff web/ 版持仓/盘口源是否具备同等 broker_source 语义 |
| A 深度 | **import 即建仪表盘**：模块尾 `if pn is not None: _DASHBOARD = create_dashboard()`——import 副作用含 init_db()（写生产 governance.db）+ TaskRepository 实例化+ QmtFileBridgeAssembly 自动装配（OrderManager+connect_all）；任何测试/工具 import 本件即触碰生产库与桥 | app_panel.py:561-570 + create_dashboard :503-547（init_db/QMT 装配） | P2 | `python -c "import zephyr.frontend.dashboard.app_panel"` 观察 governance.db 初始化与桥装配日志 |
| B 上游 | create_dashboard 默认 qmt_auto_assemble=True 且 enable_real=False/enable_sim=True 硬编码——注释"默认仅模拟环境，安全"；但 enable_real 硬编码意味着该入口永远不会装配实盘（正面确认防呆） | app_panel.py:527-535 | — | code review |
| E 对抗 | 单 Tab 失败降级为 Alert 面板（:476-479）——不影响其他 Tab，设计正确；但 broad except 把编程错误也静默成红框（栈不落日志） | app_panel.py:474-479 | P3 | 造一个 builder 异常观察 traceback 是否留痕 |
| C 下游 | components/* 14 个组件头注 [CONSUMERS] 全指向本弃用件：组件消费者声明未随 web/ 迁移更新——组件的真实消费者现在是双前端，头注单写旧件 | components/knowledge_overview.py:5 等 14 处 | P3 | 抽查 web/ 是否 import 同批组件 |
| A 深度 | docstring 内 "11 个 Tab" 与实际 14 Tab 计数漂移（v3.4/v3.5 增补后未同步标题行） | app_panel.py:11 vs :14-34 | P3 | 对照 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| Panel/HoloViz 数据 app 组装模式（依赖注入+回调编排+可选依赖 try-import） | 对等已有：与 HoloViz 官方推荐模式一致（pn.extension/servable/serve 分离） | HoloViz Panel 官方文档（user-guided apps / servable）, panel.holoviz.org, 2025（文档域常规入口，未实时核验——本轴 F 受限流批次影响） |
| 弃用模块治理（deprecation policy） | **立卡候选**：业界弃用件惯例=不再接受功能新增+入口指针同步改+明确的退役判据与期限；本件"保留不删"但仍在收新功能、宪法指针未改——三条惯例均未执行 | Python 弃用惯例（PEP 562/deprecation warning 生态）与主流框架 deprecation policy（如 React 弃用周期文档）, 各官方域, 2025（同上受限流口径） |
| import 副作用治理 | 立卡候选：库设计惯例=import 无副作用（side-effect-free import），.servable() 钩子应限 panel serve 执行路径（如 `if __name__` 或环境哨兵），防测试/工具链误触生产装配 | 受限流口径（PyPA 打包指南 import 惯例） |

## 4 缺陷清单

1. **D-1（P2）双前端并行承载+弃用声明失真**
   - 现状→证据：头注弃用（:5-10）但最近功能批仍触达本件；web/ 与本件并行维护，组件消费者头注单写旧件。
   - 影响：迁移断点（Owner 裁定"确认新版完全涵盖后才删"）因持续双改而永不确定——退役判据被现实破坏；两前端数据口径漂移难察觉。
   - 建议修法：①Owner 裁定补刀：功能冻结（本件只收 bugfix）或立即停止双改；②宪法 §7 指针改 web/；③组件头注消费者改双列。
   - 验证法：下一波前端功能批 diff 是否仍触达本件。
2. **D-2（P2）import 副作用链**：生产 DB init + QMT 桥装配+OrderManager 构造全部前置到模块导入；建议 create_dashboard 副作用仅 main/serve 路径执行（参数化 lazy），测试隔离红线 §9.6 的邻接风险（import 侧通道）。
3. **D-3（P3）文档小漂移**：11 vs 14 Tab、组件头注消费者、Tab 异常无栈日志。

## 5 挂起疑问

- Owner 实际还在用哪个前端（web/ 41 页 vs 本件）？决定 D-1 是"治理性"还是"现实性"问题。
- web/ 版是否已完整承载 14 Tab 语义（"确认涵盖"的验收记录在哪，未查到）。

## 6 完备性自评

- 六轴全查：A（装配链/防呆）、B（数据源注入链）、C（组件消费者群）、D（宪法指针+双前端+迁移台账）、E（降级链）、F（受限流批次影响，来源口径如实标注）。
- 长尾：14 个组件逐个未审（独立对象群）；web/ 前端未审（不在本轮对象清单）。
