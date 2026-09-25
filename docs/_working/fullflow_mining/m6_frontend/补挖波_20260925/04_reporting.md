---
ttl: task_bound
session: st-ailayer-fullflow-frxc
date: 2026-09-25
---

# M6 前端API链 · 补挖波 · 分册 04 · 报告生成族三态（F115，src/zephyr/reporting/ 全域收口）

> 挖矿会话 st-ailayer-fullflow-frxc ｜ 2026-09-25 ｜ 只读挖矿+本目录零 commit。
> 分工册口径"41 模块"实测澄清：模块册 `module_translation_registry.yaml` 42 行（src 31 行+tests 11 行）；扣 `__init__.py` 与 1 条幽灵行（§四-5）＝**盘面 29 实模块**；tests/reporting/ 盘面 27 测试文件（注册仅 11）。
> 能力反查留痕：`CapabilityLookup.find('reporting', session_id='st-ailayer-fullflow-frxc')` → 3 命中（MOD-PF-007 / tca_engine / MOD-RPT-009）。

## 一、环节定义与边界
一句话：把归因/风险/合规三类盘后分析加工成报告并分发归档（M0 定义"投资/风险/合规三类报告生成分发"）——**库件层成熟（29 模块全有码+27 测试文件），链路层零触发**：全仓无任何生产入口调用报告引擎，报告从未生产给 Owner。
- 供料方：F50 pf_core 归因引擎（analytics_base 基类）、risk.core.daily_auditor（日复盘上游，已接 post_settlement 管线）、plan_engine 预测日志（prediction_log_writer 的数据源）、F102 gov_audit（re-export shim 双轨）。
- 消费方：**设计上**=Owner（三类报告）与 F111 前端；**实测**=api_server 47 路由零投影（`grep reporting api_server.py` 零命中）、自动化班底/计划任务零引用（scripts/config/cmd_ledger/ai_layer/orchestrator 五处 grep 零命中）。

## 二、六向台账
| 向 | 实测证据 |
|---|---|
| 上游输入 | 归因基类消费=pf_core/core/performance_attribution_engine.py:58（AttributionEngineBase）；日复盘上游=review_orchestrator.py:69-73（DailyAuditor/AuditRequest）；预测日志写入=data/intraday_sentiment_loop.py:67 + plan_engine 六件（auction_hit_recorder:63 等）；退役评估=governance/lifecycle_governance/strategy_retirement_evaluator.py:62（ReportPublisher） |
| 下游消费 | **有外部 import 的仅 6/29 模块**（机扫实证）：prediction_log_writer×10、prediction_calibration_monitor×1（scenario_plan_recorder.py:76）、analytics_base×2（pf_core 引擎+governance shim）、default 双引擎×2（仅 shim re-export，无真消费）、report_publisher×2（retirement_evaluator+shared/alerts/alert_senders.py 注入位）→ 归类 **绿 4 件生产消费+黄件 25**；api_server 零路由、零页面消费 |
| 自动化触发 | **零**。无计划任务（resource_profile_registry 零 reporting 条目）、无 daemon、自动化班底零引用；review_orchestrator.py:48 铁律"事件驱动零定时器——run_daily/run_weekly/run_monthly 由调用方在日终/周末/月末事件触发"，**该调用方全仓不存在**（grep 仅 tests/reporting/test_review_orchestrator.py） |
| 真源与注册表 | 模块册 42 行（domain=D_REPORTING 30 src+11 tests）；幽灵行=performance_attribution_report.py 登记在 reporting/ 而真身=`src/zephyr/shared/contracts/performance_attribution_report.py`（pf_core/__init__.py:50、analytics_base.py:53 实证）；能力册 tca_engine 判 status=dead（"no disk candidate matches"）而盘面 default_tca_engine.py 活+shim 在——**双登记漂移**；域册=docs/03_modules/_domain_reporting/（14 卡+blueprint+algo_flow） |
| 门禁与质量尺 | 无报告域专项门；通用面=ALGO-NOTE-SYNC（头注算法锁）+TRANSLATION-COVERAGE+CloneGuard；ReportPublisher 自带 verify_chain() 哈希链完整性校验（report_publisher.py:386-430）——但校验对象是**进程内存 list**（§四-2） |
| 当前运行状态 | **链路级红**（29 模块库件绿/测试绿，但全链零触发=三类报告从未生成）；组件级：绿 4（+__init__ 导出面）/黄 25；口径漂移 3 处（§四-5） |

## 三、子模块清单（29 实模块三态；盘面×模块册×全仓消费扫描三源交叉）
### 3.1 绿——有生产消费方（5 件）
| 模块 | 是什么 | 消费方实测 | 蓝图 |
|---|---|---|---|
| prediction_log_writer | 每日预测类输出统一落库（append-only SQL） | intraday_sentiment_loop.py:67 + plan_engine 六件 + warroom.py:65（共 10） | MOD-RPT-028 |
| prediction_calibration_monitor | 预测→参数校准评审建议（永不自治改参） | plan_engine/scenario_plan_recorder.py:76 | MOD-RPT-029 |
| analytics_base | AttributionEngineBase/TCAEngineBase OCP 扩展点 | pf_core 归因引擎 :58 + governance/observability_governance shim（2026-07-06 双定义收敛） | MOD-L07-001 |
| report_publisher | 报告域唯一归档出口（D-RPT-D05）+3 分发渠道 | retirement_evaluator.py:62 + alert_senders.py 注入位（**但其上游链自身零入口**，半绿） | MOD-RPT-003 |
| __init__ | 包导出面（5 符号） | risk/core/__init__.py:137 经惰性导出规避循环导入（W1d 2026-08-25 实证） | MOD-L07-001 |

### 3.2 黄——建成零生产调用（25 件 24 行，default 双引擎合并 1 行；全部有码+有测试）
| 模块 | 一句话 | 自述消费方（未接线） |
|---|---|---|
| review_orchestrator | 日/周/月三频复盘编排（55号§3.6，周复盘四段模板） | "日终/周末/月末事件调用方"缺位=触发链断 |
| risk_report_engine | 日报/周深/月治理/事件快报四类 | 仅 review_orchestrator 内部 |
| regulatory_report_generator | 监管 4 类报告（程序化/异常/持仓/绩效） | "zephyr.reporting"（无外部实件） |
| ashare_performance_audit | A股 5 类绩效审计+优化建议 | 同上 |
| ashare_trade_record_template | A股交易记录 11 必填模板 | 同上 |
| attribution | 对账归因函数级（54号 G25，fill_id 幂等+FIFO+求和不变量） | StrategyPnlAccountant 全仓仅 registry_mapper 内部引用 |
| attribution_calculator | BHB/Carino 链式归因 | attribution_result_store（落库件亦零调用） |
| attribution_result_store | 归因落库+查询（append-only） | 零 |
| attribution_registry_mapper | 归因→experiment_registry 映射（62号 #4） | 零 |
| attribution_meta_iteration | 归因反哺元级评审建议（评审制铁律） | 零 |
| decision_trace_chain | 决策溯源链四段落痕+全链反查 | "运行时装配批"（未装配） |
| deviation_attribution_decomposer | 回测-实盘偏离四因子分解（BM-BT-05-H） | MOD-RK-23/MOD-RPT-009 名义消费方 |
| strategy_explainability_reporter | SHAP+LIME 双归因报告+门控降级 | "运行时装配批" |
| trading_review_engine | A股交易四模式审查 | "运行时装配批" |
| realtime_pnl_dashboard | 实时盈亏仪表盘（Decimal-only） | 自述"zephyr.frontend"实为零 |
| report_version_manager | 报告版本链（prev_hash 链式） | 零 |
| report_watermark_tracker | 报告水印链 | 零 |
| review_template_engine | 周复盘四段模板引擎（纯函数） | review_orchestrator 可选升级位 |
| review_template_registry | 模板注册表（config/review_templates.yaml 双向一致锁） | ai_review_summary 供给位 |
| ai_review_summary | LLM 战报摘要（网关抽象+模板兜底） | "盘后复盘页一键生成战报"GAP-F-40 消费位（页面不存在） |
| alert_aggregator | 三源告警聚合（封闭词表+确定性 id） | "总览页今日告警卡"（页面不存在） |
| miniqmt_order_link_probe | miniQMT 下单链路探针（**MOD-EX-058 ex 域件寄居 reporting 包**） | "系统健康总览看板"（未建） |
| default_attribution_engine / default_tca_engine | 归因/TCA 默认实现 | 仅 governance re-export shim（双轨收敛件） |
| reconciliation_schema | 对账/归因 DB schema 定义（仅定义不执行 DDL） | 54号落库施工批次（未施工） |

## 四、堵点与病灶
1. **【红】全链零触发——报告从未生产**：F115 环节定义的"三类报告生成分发"在生产线为空集。触发链断点三层：①review_orchestrator 事件调用方不存在（ops_alert_feed.py:18 自证同款病灶"规则引擎在、触发链断"）；②上游 DailyAuditor 虽接入 post_settlement 管线（scripts/run_post_settlement.py），但 M5 在案 order_daemon 建成未接线——上游本身在产线断链；③下游 api_server 零路由、自动化班底零引用。修法草案：①先决=补 F74 转正汇总器（归 PR 组）或 ⑨骨架体检（已交付 generate_skeleton_health.py 但未常态化）作为日/月频触发宿主；②api_server 增 /api/reports 只读投影（ReportPublisher.list_by_source，0.5 天，本车道可修）；③(retirement/screener 上层链零入口随 F50/F74 车道处置)。
2. **【红】归档出口无持久化**：report_publisher.py 基础版 `self._archive`＝**进程内存 list**（:331-334 append），头注自认"基础版不含 SQLite+Parquet 持久化/Merkle 树"（:30）——"唯一归档出口"（D-RPT-D05）实际是易失内存，进程重启全丢，哈希链 verify_chain 校验的是内存对象。修法：DDL 真源已备（reconciliation_schema.py 哈希链字段齐全"对齐 ReportPublisher 模式"），按 54号 §7 落库施工。1-2 天，跨 data 域协同。
3. **【黄】分发双渠道恒 PENDING**：WEBHOOK/EMAIL sender 未注入→恒 PENDING（report_publisher.py:206-208，54号 §3.7"双渠道实发裁定"未执行）；且 2026-09-15 已裁飞书/SMTP 通知通道裁撤（ops_alert_feed.py:16，前端 promotion 页=唯一出口）——报告分发渠道语义需与该裁定对齐后重裁（归 Owner/总筹）。
4. **【黄】6 个空壳子包假分层**：api/core/infrastructure/models/services/_extensions 六目录各仅 __init__.py（8 .py 中 7 个是壳）——模块册照登 8 行，"分层"纯登记态；execution_simulation 子包壳更标 maturity=production（§F121 证据册交叉引用）。修法：壳包降级或删除（净删门位），模块册行随删。
5. **【黄】三处登记漂移**：①模块册幽灵行 src/zephyr/reporting/performance_attribution_report.py——真身=shared/contracts/performance_attribution_report.py（契约件非报告件），登记路径指向不存在的文件；②能力册 tca_engine status=dead 而 canonical（reporting/default_tca_engine.py+shim）活着；③MOD-EX-058（ex 域下单链路探针）物理寄居 reporting 包、域册 _domain_reporting 无此卡。修法：模块册/能力册机生对账批（同 01_open_wounds A7 名册对账生成器同批）。
6. **【灰】复盘链上层整链零入口**：strategy_retirement_evaluator ← strategy_screener_3d / retirement_workflow ← **零调用方**（grep 实证）——月度退役评审建议链与报告链同断；归 F50/F74 车道，本册只登记连带关系。

## 五、提速与合并机会
1. 29 模块中 13 件共用"哈希链+append-only+frozen dataclass"骨架（publisher/version/watermark/attribution_store/schema），可抽 shared 基类（同宪法 §4.2 同域重复簇收敛）；先例=analytics_base 的 OCP 扩展点模式。
2. api_server 报告投影与 §四-1② 同批：一个 _yaml_map_cache 同款只读路由（复用 03 册缓存范式）即把 24 件黄件中的台账类（version/watermark/audit）变成 Owner 可见。
3. review_template_registry 的"config/review_templates.yaml 双向一致锁"是模板单一真源先例——ai_review_summary/复盘页两消费位可复用同一注册表，禁第三处模板源。

## 六、自审闸三态
**挖干可施工（组件级）**：29 模块逐个三态（绿 5/黄 24）、两源交叉（盘面×模块册）+全仓消费机扫；三处登记漂移带锚点。
**待挖**：config/review_templates.yaml 内容面与模板资产（weekly_review_template.md）逐字段核（量小，随消费方接线批一并）。
**待裁**：①分发渠道语义（§四-3，涉已裁飞书/SMTP 撤通道的口径对齐）；②空壳子包与幽灵登记行净删（Owner 净删门位）；③触发宿主选择（F74 汇总器 vs ⑨骨架体检 vs api_server 投影）归总筹排期。

## 七、复核命令（10 分钟）
```bash
# 1. 盘面×注册表差集（应 disk=36 .py；registry-only=[performance_attribution_report.py]）
python -c "
import yaml; from pathlib import Path
disk={str(p.relative_to('src/zephyr/reporting')).replace(chr(92),'/') for p in Path('src/zephyr/reporting').rglob('*.py')}
d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml').read_text(encoding='utf-8'))
reg={e['module_path'].replace('src/zephyr/reporting/','') for e in d['entries'] if str(e.get('module_path','')).startswith('src/zephyr/reporting/')}
print(len(disk), sorted(reg-disk))"
# 2. 前端/调度零投影复现（应均无输出）
grep -n "reporting" src/zephyr/frontend/dashboard/api_server.py | head -3
grep -rn "review_orchestrator\|risk_report_engine\|regulatory_report" scripts config/resource_profile_registry.yaml --include="*.ps1" --include="*.py" --include="*.yaml" | grep -v test | head -5
# 3. 归档内存态复现（应见 self._archive.append 且无落盘调用）
grep -n "_archive.append\|sqlite\|parquet\|to_parquet\|write_" src/zephyr/reporting/report_publisher.py | head -8
# 4. 生产消费方计数复现（应 6 件有消费、其余 0）
grep -rln "from zephyr.reporting.prediction_log_writer" src --include="*.py" | grep -cv reporting
# 5. 幽灵契约真身复现
ls src/zephyr/shared/contracts/performance_attribution_report.py; ls src/zephyr/reporting/performance_attribution_report.py 2>&1 | head -1
```
