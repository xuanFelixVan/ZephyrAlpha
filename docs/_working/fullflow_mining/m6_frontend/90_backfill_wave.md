---
ttl: task_bound
title: M6 前端API链 补挖波 · 报告生成链路
session: st-fflead-m1m6-backfill
---

# 90_backfill_wave — M6 补挖波（报告生成，2026-09-25 本会话复跑增量）

> 接续册：01_dashboard / 02_api_server / 03_panel_caches ＋ 补挖波_20260925/04_reporting.md（该册已完成 29 模块三态全景，本册做两件事：①对其关键断言逐条**本会话复跑**并订正 2 处行号漂移；②补其登记之"待挖"面=review_templates 承载现状）。硬口径：报告域=src/zephyr/reporting/ 29 实模块；"上板通道"=api_server 路由或 dashboard 页面消费。

## 一、环节定义与边界
一句话：把归因/风险/合规盘后分析加工成报告→归档→分发/上板给 Owner。供料方=pf_core 归因引擎/risk.daily_auditor/post_settlement 管线；消费方（设计态）=Owner 三类报告＋F111 前端（实测零）。断点判定口径=触发链/归档链/投影链三层各有无 file:line 实连接。

## 二、六向台账（本会话复跑态）
| 向 | 实证（本会话 2026-09-25） |
|---|---|
| 上游输入 | review_orchestrator 上游=DailyAuditor（review_orchestrator.py:69-73，04 册锚，其 post_settlement 上游本会话未复跑=引 04 册）；模板真源承载 config/review_templates.yaml **在盘实存**（本会话 ls 证实，04 册 §六待挖项之存在性收口；内容逐字段核仍未做）；docs/03_modules/_domain_reporting/ 14 卡目录本会话 ls 证实 |
| 下游消费 | 有外部 import 的 6/29 模块（04 册机扫，本会话抽验 prediction/review 面）：review_orchestrator 的包外出现面本会话 grep 穷尽=**仅头注/注释**（strategy_retirement_evaluator.py:5/:204、strategy_deviation_monitor.py:5 皆 `[CONSUMERS]`/docstring 文字，非 import）＋包内 review_template_engine.py:32 import WEEKLY_REVIEW_SECTIONS＋__init__.py:60-63/:73/:79 re-export → **生产触发调用方=不存在**，04 册"调用方全仓不存在"判定复证成立 |
| 自动化触发 | 零：04 册五处 grep（scripts/config/resource_profile_registry 等）零命中在册；本会话 src+scripts 全树 *.py 复跑同关键词，tests 外零调用方（同上） |
| 真源与注册表 | 模块册 42 行/幽灵行=performance_attribution_report.py 真身 shared/contracts/（04 册 §四-5，本会话未重复 ls 复跑，登记引其锚）；四段模板段标题单一真源=review_orchestrator.WEEKLY_REVIEW_SECTIONS（review_template_engine.py:8 INVARIANTS 本会话实读） |
| 门禁与质量尺 | 无报告域专项门（04 册）；ReportPublisher 自带 verify_chain 但校验对象=进程内存 list（本会话实取行号见 §三） |
| 当前运行状态 | **链路级红**维持：29 模块库件绿/测试绿、三类报告生产=空集；api_server 投影面本会话复跑：`grep -n "reporting\|report_" api_server.py` 仅 3 命中且全为财报日期**列名**（:1824 report_date、:3554/:3997 report_period），非报告域路由 → "47 路由零投影"复证成立 |

## 三、子模块清单（生成器→断点逐条，本会话行号订正版）
### 3.1 生成器面（29 模块全景=04 册 §三，此处只列"报告产出动作件"）
| 件 | 入口 | 本会话状态 |
|---|---|---|
| review_orchestrator | src/zephyr/reporting/review_orchestrator.py（日/周/月三频复盘编排） | 黄——run_daily/weekly/monthly 无调用方（grep 穷尽见 §二） |
| risk_report_engine | src/zephyr/reporting/risk_report_engine.py（日报/周深/月治理/事件快报四类） | 黄——唯一上游=review_orchestrator（同断） |
| regulatory_report_generator | src/zephyr/reporting/regulatory_report_generator.py（监管 4 类） | 黄——外部实件零 |
| ai_review_summary | src/zephyr/reporting/ai_review_summary.py（LLM 战报摘要，网关抽象+模板兜底） | 黄——消费位 GAP-F-40"盘后复盘页一键生成战报"**页面不存在**（04 册 §三.2） |
| alert_aggregator | src/zephyr/reporting/alert_aggregator.py（三源告警聚合） | 黄——"总览页今日告警卡"未建（04 册） |
| report_publisher | src/zephyr/reporting/report_publisher.py:238 `class ReportPublisher`、:273 `def publish` | 半绿（被 retirement_evaluator/alert_senders 引用）但归档=**内存态**：:261-262 `self._archive: list / _archive_by_id: dict`、:310 prev_hash 链自 :261 内存 list、:335-336 append、:357 查询走 _archive_by_id——**进程重启全丢，verify_chain 校验内存对象**（本会话实取；04 册记 :331-334/:386-430 系行号漂移，以本册为准） |
| realtime_pnl_dashboard / trading_review_engine / strategy_explainability_reporter / ashare_performance_audit / attribution 四件套 / version+watermark 双链 | 见 04 册 §三.2（黄 25 件全清单，本册不复制） | 黄 |
### 3.2 前端上板通道判定（断点③）
- api_server 47 路由：报告域**零路由**（本会话 §二复跑证：3 处 'report' 字面皆为财报列名）。
- dashboard 页面：本会话 `grep -rn report src/zephyr/frontend/dashboard/*.py` 及 pages/ 面：除 api_server 上述列名外**无消费位命中**（查无；搜索面=dashboard/*.py + pages/ + 关键词 report/报告/战报——"战报/复盘"页面不存在与 04 册 GAP-F-40 一致）。
- 结论：**无任一报告上板通道**，24 黄件对 Owner 完全不可见（连"生成后无人看"都不成立——从未生成）。

## 四、堵点与病灶（三层断点，精确锚点）
| # | 断点 | 锚（本会话实取/复跑） | 修法草案 | 工作量 | 本车道 |
|---|---|---|---|---|---|
| R1 | 触发链断：三频复盘编排无事件调用方 | §二"自动化触发"行（grep 穷尽）；04 册 :48 铁律"由调用方触发"而调用方缺位 | 触发宿主三选一=待裁（04 册 §六-③：F74 转正汇总器/骨架体检班/api_server 侧班），本车道不选 | 随宿主 | 提请 |
| R2 | 归档链断：ReportPublisher 唯一出口=易失内存 | report_publisher.py:261/:310/:335（本册 §三.1） | DDL 真源已备=reconciliation_schema.py（04 册 §四-2），落库施工=54号 §7，1-2 天跨 data 域 | 1-2 天 | 是（落库后 R3 才有可投影物） |
| R3 | 投影链断：/api/reports 缺位 | §二/§三.2 | 增只读投影路由（复用 03 册 _yaml_map_cache 范式；publish 后内存 list 即可投影，不等 R2） | 0.5 天 | **是（本车道最薄一刀）** |
| R4 | 分发语义悬置：WEBHOOK/EMAIL 恒 PENDING＋飞书/SMTP 撤通道裁定未对齐 | report_publisher.py:206-208（04 册 §四-3） | 待裁（涉既有裁定口径对齐=Owner/总筹） | — | 待裁 |
| R5 | 承载面：config/review_templates.yaml 在盘但**内容面/与 review_template_registry 双向一致锁逐字段核**未做 | 本会话 ls 证实存在；逐字段核未做=04 册遗留待挖 | 随接线批并量核（量小） | 0.1 天 | 是 |
| R6 | 登记漂移 3 处＋空壳子包 6 个 | 04 册 §四-4/5（含 execution_simulation 壳包标 production） | 机生对账批同窗；壳包净删=门位 | — | 待裁（净删） |

## 五、提速与合并机会
1. R3 投影先于 R2 落库即可交付（Owner 当日可见当日报告），两刀可拆批不等；29 件中 13 件共享"哈希链+append-only"骨架→抽 shared 基类（04 册 §五.1）在 R2 施工时顺带。
2. ai_review_summary/alert_aggregator 两个"页面不存在"消费位与 R3 同页承载（复盘战报卡+今日告警卡=/api/reports 投影页两区块），禁第三处模板源（review_template_registry 单一真源锁，本会话复核其 INVARIANTS 在案）。

## 六、自审闸三态
**挖干可施工**：R3（0.5 天只读投影，本车道最薄一刀）、R5。R2 可施工但跨域需协同排期。
**待挖**：无新增缺口（04 册唯一待挖=review_templates 内容面，本册收口其存在性并把逐字段核挂 R5）。
**待裁 3 条（不自裁）**：①R1 触发宿主选择（选项=F74 汇总器/骨架体检班/api_server 侧班；建议骨架体检班——已交付 generate_skeleton_health.py 零新班次）；②R4 分发渠道语义与飞书/SMTP 撤通道裁定对齐（建议=仅上板投影为唯一出口，废弃外发渠道语义）；③R6 空壳子包+幽灵登记行净删（Owner 净删门位；建议随机生对账批）。

## 七、复核命令（本会话全跑通）
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"   # 3.12.8
# 1. review_orchestrator 包外零调用（应只见 __init__.py re-export + review_template_engine 包内 import + 头注/注释行）
grep -rn "review_orchestrator\|ReviewOrchestrator" src scripts --include="*.py" | grep -v __pycache__ | grep -viE "test_|review_orchestrator.py:"
# 2. api_server 报告域零路由（应仅 3 处财报列名 :1824/:3554/:3997）
grep -n "reporting\|report_" src/zephyr/frontend/dashboard/api_server.py
# 3. 归档内存态（应见 :261-262 声明、:335-336 append、:357 查询，无 sqlite/parquet 落盘）
grep -n "_archive\b\|_archive_by_id" src/zephyr/reporting/report_publisher.py | head -8
# 4. 模板承载在盘 + 单一真源锁
ls config/review_templates.yaml; sed -n '8p' src/zephyr/reporting/review_template_engine.py
# 5. 29 模块全景/绿黄件逐件=04_reporting.md §三+§七命令（本册不复制）
```
