---
ttl: task_bound
title: L11 案卷 F115 — 报告生成（29 实模块库件绿/链路红零触发；归档=内存态；三层断点 R1-R3 本日复证）
session: zc-l11-20260927
---

# F115 报告生成（L 段 F5，骨架态=partial/P1——M6 补挖项，两册已挖干，本卷=独立复核+收口）

## 一、六向台账（2026-09-27 实证；真源=M6 补挖波 04_reporting.md+90_backfill_wave.md，本日抽验全过）

| 向 | 实测证据 |
|---|---|
| 上游输入 | pf_core 归因引擎（analytics_base AttributionEngineBase）；risk.core.daily_auditor（review_orchestrator.py:69-73 接线）；plan_engine 预测六件→prediction_log_writer；F102 gov_audit（shim 双轨） |
| 下游消费 | **生产消费 6/29 模块**（04 册机扫）：prediction_log_writer×10、prediction_calibration_monitor、analytics_base×2、default 双引擎 shim、report_publisher×2（retirement_evaluator+alert_senders 注入位）——其中 25 件建成零生产调用；**api_server 零投影（本日 grep "reporting"=0 命中复证）** |
| 自动化触发 | **零**：review_orchestrator 铁律"事件驱动零定时器，由调用方在日终/周末/月末触发"而调用方全仓不存在（90 册 grep 穷尽复证：包外出现面仅头注/注释文字非 import）；无计划任务/无 daemon/自动化班底零引用 |
| 真源与注册表 | 模块册 42 行（src 31+tests 11）；幽灵行=performance_attribution_report.py 真身 src/zephyr/shared/contracts/（04 册锚）；能力册 tca_engine status=dead 与盘面活件双登记漂移；域册 docs/03_modules/_domain_reporting/（本日 ls=17 条目）；config/review_templates.yaml 在盘（本日 ls 证实，90 册 R5 存在性收口维持） |
| 门禁与质量尺 | 无报告域专项门；通用面=ALGO-NOTE-SYNC+TRANSLATION-COVERAGE+CloneGuard；ReportPublisher.verify_chain() 哈希链校验——但校验对象=**进程内存 list** |
| 当前运行状态 | **链路级红维持**：库件层 29 实模块全有码+27 测试文件（盘面 36 .py 本日 find 实数）；三类报告（投资/风险/合规）从未生产给 Owner；上板/分发/归档三通道全断 |

## 二、子模块三级枚举（29 实模块三态=04 册 §三全景，本卷列骨架+本日抽验锚）

1. **绿（生产消费在）5 件**：prediction_log_writer（append-only 落库，10 消费方）、prediction_calibration_monitor、analytics_base（OCP 扩展点）、report_publisher（唯一归档出口，半绿）、__init__ 导出面。
2. **黄（建成零调用）24 行**：review_orchestrator（日/周/月三频编排，触发链断根）、risk_report_engine（四类风险报告）、regulatory_report_generator（监管 4 类）、ashare_performance_audit（5 类绩效审计）、attribution 四件套、decision_trace_chain、strategy_explainability_reporter、trading_review_engine、realtime_pnl_dashboard、version+watermark 双链、review_template_engine+registry、ai_review_summary（消费页 GAP-F-40 不存在）、alert_aggregator（消费页不存在）、miniqmt_order_link_probe（ex 域件寄居）、default 双引擎、reconciliation_schema。
3. **断点三级（90 册 R1-R6 本日锚点抽验）**：R1 触发链（调用方缺位）｜R2 归档链（report_publisher.py:261 `self._archive: list`、:262 `_archive_by_id: dict`、:335-336 append、:310 prev_hash 取内存尾——**本日行号逐一实读吻合 90 册订正版**）｜R3 投影链（/api/reports 缺位，grep 零命中复证）。
4. **登记漂移 3 处**（04 册 §四-5）：幽灵契约行/能力册 dead 误标/MOD-EX-058 寄居。

## 三、接线四态独立复核

- **预测日志支线：已接线**（prediction_log_writer×10 生产消费+plan_engine 六件；F115 域内唯一真活面）。
- **复盘/报告主体：未接线**——R1 触发宿主三选一待裁（F74 汇总器/骨架体检班/api_server 侧班；90 册建议骨架体检班，零新班次）。
- **归档：半接线（易失）**——内存 list+"基础版不含持久化"头注自认；DDL 真源已备（reconciliation_schema.py），落库施工 1-2 天跨 data 域。
- **分发：停用态**——WEBHOOK/EMAIL 恒 PENDING+飞书/SMTP 撤通道裁定未对齐（与 F114 缺口同窗）。

### 骨架勘误
1. 总册 partial 判定成立（维持），但模块计数口径收口：**29 实模块**（模块册 42 行−tests 11−幽灵 1−init 等；"41 模块"旧口径废弃）；盘面 36 .py（含壳包）。
2. M6 04 册行号已由 90 册订正（_archive :331-334→:261-262/:335-336），本日第三方的实读与 90 册订正版吻合——引用以 90 册为准。
3. partial 的红度须显式：不是"部分接线"而是**三类报告生产=空集**（连"生成后无人看"都不成立）；总册 §二 断链点清单未列 F115，建议补列（归 L00 骨架定版窗）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | R1 触发宿主缺位（三类报告零生产） | 待裁三选一（建议骨架体检班 generate_skeleton_health.py 零新班次） | P1 |
| 2 | R2 归档内存态易失 | 按 54号 §7 落库施工（DDL 已备，跨 data 域协同） | P1 |
| 3 | R3 /api/reports 投影缺位 | 只读投影路由 0.5 天（复用 _yaml_map_cache 范式；不等 R2 即可交付） | P1 |
| 4 | R4 分发语义悬置（PENDING+撤通道未对齐） | 与 F114 缺口#1/#2 同窗裁定 | P2 |
| 5 | 登记漂移 3 处+6 空壳子包 | 机生对账批同窗；壳包净删=Owner 门 | P2 |
| 6 | R5 review_templates 内容逐字段核 | 随接线批（0.1 天量级） | P2 |

## 五、自审闸三态

**挖干（两前册收口+本日三方锚点抽验：_archive 行号/零路由/模板在盘全过）✅；待裁（R1 宿主选择、R4 分发语义、壳包净删=Owner 门）；待挖（config/review_templates.yaml 内容面=随接线批并核）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
find src/zephyr/reporting -name "*.py" | grep -v __pycache__ | wc -l   # 36 盘面
grep -n "_archive\b\|_archive_by_id" src/zephyr/reporting/report_publisher.py | head -5   # :261/:262/:310/:335/:336
grep -c "reporting" src/zephyr/frontend/dashboard/api_server.py        # 0 零投影
ls config/review_templates.yaml                                        # 在盘
grep -rn "review_orchestrator\|ReviewOrchestrator" src scripts --include="*.py" | grep -v __pycache__ | grep -viE "test_|review_orchestrator.py:" | head -3   # 包外仅注释
ls docs/03_modules/_domain_reporting/ | wc -l                          # 17
```
