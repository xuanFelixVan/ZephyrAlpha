---
ttl: task_bound
session: st-ailayer-fullflow-sc
creation_token: m5sc-fbl-feedback-loop-20260925
---

# M5 补挖分册 01：FBL 反馈回路（F84）——两条回路、一个断点

> 证据：源码头注+全仓 grep 接线点+盘面实测，2026-09-25。只读挖矿。
> 家族规模实测：`src/zephyr/feedback_loop/` 340 个 .py（顶层 29 + actors 12 + collectors 20 + detectors 5 簇 + diagnosers 4 簇 + evolution 19 + gates 47 + resilience 9 + security 6 + verifiers 23 + forensic 17）；测试两目录 `tests/feedback/`、`tests/feedback_loop/`（分工册旧注 tests/feedback-loop/ 不存在）。

## 一、环节定义
F84 反馈循环 FBL：collectors→detectors→diagnosers→actors 四族 + SLO/error budget + 自动回滚，上游 F81 监控，下游治理/演进。总册标 partial（M5 补挖项）——**本册判定：标得准，且 partial 的"partial"集中在一条线上**。

## 二、两条回路拆解（同族两物，勿混）

### 回路 A：FLE 五段闭环（scheduler.py，814 行）
- **管线**：collect→detect→diagnose→act→verify（scheduler_collect_detect/act/health/safety 四分件 199/263/93/203 行）；动作优先级 NOTIFY_OWNER > ADJUST_THRESHOLD > REPAIR > DEPLOY > SELF_UPGRADE；安全门 67 层（gates/ 19 文件覆盖 L1-L67 段）。
- **触发（核心发现）**：`trae_053 v2.0.0` 废除 daemon 线程+30s 轮询——`start()` docstring 明文 "production auto-runtime MUST NOT call start()"（scheduler.py:477-483）；`tick()` 成为唯一生产入口（:558，单次 _run_once）。
- **断点**：`auto_runtime_core.py:1132` 仅实例化（`FeedbackLoopScheduler(poll_interval=30.0)`+log "daemon mode abolished"），**全仓 grep `.tick()` 对 FLE 调度器零生产调用方**（health_monitor.py:480-482 的 tick 是 HealthMonitor 自己的事件订阅 task.completed/failed/health.check.request，非 FLE）。即 trae_053 声明的"由 commit 事件/状态变更事件驱动"只有半句——废轮询施工了，接事件沿没施工。
- **体内证据链在**：publish 侧 `fle.anomaly`/`fle.action`/`fle.{phase}`（scheduler.py:788-805）、`fle.shutdown` 订阅优雅停（:496）、ExternalPersistenceWriter 三件（persist_metrics/persist_alert_and_log/persist_failure_pattern :192-295）、AlertDispatcher→orchestrator AlertHandler 生成 task_card+CRITICAL 级阻断相关任务（alert_dispatcher.py:96-129）。

### 回路 B：裁定驱动规则进化（core.py FeedbackLoop，106 行）
- **链**：pending entries→EvolutionProposal(DRAFT)→`data/feedback_proposals/PROP-*.yaml`→review→裁定登记。
- **接线实证（活的）**：consumers 四方——`gov_audit/feedback_bridge.py:126`（桥接 analyze/apply，头注"不实现反馈逻辑仅桥接"）、`governance/resilience_governance/f5_event_subscriber.py:443`（generate_proposals 实调）、auto_runtime_core.py:139、lifecycle_manager。
- **运行证据（冷）**：`data/feedback_proposals/` 仅 1 件 `prop_20260508200404.yaml`（2026-05-08 生成）——回路通但 4 个多月近零流量。

## 三、六向台账
- **上游输入**：F81 health_monitor 事件（task.completed/failed/health.check.request→HM 自身 tick，非 FLE）；MetricsCollector/FeedbackCollector（30s 指标→EMA 异常检测设计）；任务系统/门禁引擎/漂移引擎（blueprint depends_on MOD-TASK_SYSTEM/MOD-GATE_ENGINE/MOD-INF-023）；commit/状态变更事件（trae_053 声明源，**未接线**）。
- **下游消费**：orchestrator AlertHandler（告警→任务卡+CRITICAL 阻断）；通知板落盘；提案目录→裁定登记（回路 B）；进化族 evolution_engine/auto_evolution（dep 含 LSG gateway，LLM 调用合规）；`config/evolution_schedule_seeds.yaml` 消费方=ai_layer/scheduling/seed_writer（与 F82 排产的交叉轴，见 05 册）。
- **自动化触发**：**零**。无计划任务、无 schedule.yaml 槽、无 cron；start() 生产禁用；tick 零调用方；宿主=AutoRuntime Core 进程内（当前进程表无 zephyr.trading 进程＝宿主不活，FLE 自然不在跑）。
- **真源与注册表**：blueprint `docs/03_modules/_cross_layer/feedback_loop/blueprint.md` v0.35.20（Draft，MOD-FEEDBACK_LOOP）；各模块 algo_flow/*.yaml；`config/error_budget_config.yaml` v2.6.0（**注意归属**：module_id=MOD-INF-001，消费方=infrastructure/capacity_assurance/batch1_infra.py+arch_guard fitness，**feedback_loop/error_budget.py 并不读它**）。
- **门禁与质量尺**：PERM-TRIGGER gate（§9.3 事件触发宪法的技术面，驱动 start() 生产禁用）；safety_gate L1-L67；wireheading_prevention/self_modification_rate_limiter（自我放大闸）；MODIFY-GUARD=blueprint；error_budget.py 本体是纯内存状态机（ErrorBudgetManager._budgets dict，零文件 IO）——与 config 同名**双轨不同物**。
- **当前运行状态：红（回路 A）/黄（回路 B）**。回路 A 零生产触发（结构性，非故障）；回路 B 通但近零流量；`.runtime/tmp/feedback_audit_trail/` 空目录（落盘点住 tmp 区=04 册 S2 同族病第三例）。

## 四、堵点与修法
| # | 堵点 | 修法 | 归属 |
|---|------|------|------|
| 1 | FLE tick 无触发沿（trae_053 半句工程） | 选项 a：事件总线接线——在 commit 落地/状态变更 publish 点补 `scheduler tick` 调用（与 fle.shutdown 同模式）；选项 b：Owner 裁定收回 trae_053，恢复受控 start()（违 §9.3 精神，不荐） | 治理链+本车道施工 |
| 2 | audit 落盘住 `.runtime/tmp` | 迁 `.runtime/feedback_loop/`（持久区） | 施工小单 |
| 3 | error_budget 双轨同名 | 更名 FBL 侧（如 fle_budget）或声明消费关系，防 ROOR 反查误配 | 治理链 |
| 4 | 提案回路 4 个月 1 件 | 挖矿结论：非断链（consumers 实调在），流量缺位待 AI 层车道判读 | M4 接续 |

## 五、自审闸三态
**挖干可施工**：两条回路六向双源实证（file:line+盘面）；断点根因（trae_053 半句工程）有 grep 级证据；堵点 1 修法两选项成型。附待裁一项：堵点 1 的 a/b 选项需 Owner 裁（涉 §9.3 解释权）。
