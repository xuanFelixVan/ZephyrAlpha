---
ttl: task_bound
completes_when: 全流通战役交付后归档
---

# R 表裁定草案 — risk_mitigation.py R1~R16 六 GAP + 五 partial 独立复核（含 CT-4 与 CT-1~3 核查）

> 班次：fullcirculation_campaign_20261008 / 01_dtable_rulings
> 对象：`src/zephyr/infrastructure/capacity_assurance/risk_mitigation.py`（395 行/41 方法，R1~R16，从未接线，去留评估中）
> 输入证据表：`docs/_working/map_census/gomap/capacity_eval_evidence.yaml`（census CAPACITY-EVAL-EVIDENCE-001，2026-10-05）
> 性质：裁定**草案**——供 chief 终裁；本文档零代码/零配置改动。

## 方法论

对证据表标记的 6 个 GAP（R3/R4/R12/R14/R15/R16 + CT-4）与 5 个 partial（R6/R7/R10/R11/R13）逐项**独立复核**：不信任原表的 grep 结论，每项在 src/ 与 scripts/（排除 capacity_assurance 自身、排除 tests/）重跑符号检索 + 同义词二轮（如 R12 补 cumulative/consistency/running_total；R7 补 setrlimit/RLIMIT/max_memory_mb；R3 补 alerter/feishu/outbox/journal 全链）。复核超越原表的关键动作：**沿调用链追一层**——原表为平面符号 grep，本班对每条候选命中读上下文确认语义（对象、方向、是否真执行），因此发现多处原表漏检（R7 的 RLIMIT_AS、R3 的 alerter 生态、R15 的 gateway 路径归一、CT-4 的 REDUCE_ONLY 闸门）。裁定三选一：a) 伪GAP=活机制已覆盖（引 文件:行号），归档 risk_mitigation 无吸收必要；b) 真GAP-吸收=功能有价值且缺失，指定在编吸收目标；c) 真GAP-登记接受=风险真实但概率/影响低，登记风险台账不实现。附带核查：CT-4 的 iguana 契约时效性、CT-1~3 现役路径属实性、以及证据表自身引用的 `capacity_assurance/schema.py`/`sli_instrumentation.py` 现状（两者已被移入 `_archive/`——评估期内对象面仍在收缩，原表部分引证已过时）。

## R 表逐项裁定

| R项 | 设计意图 | GAP复核结论 | 证据(文件:行号) | 裁定 | 吸收目标 |
|-----|---------|------------|----------------|------|---------|
| R3 AlertLinkIsolator | 告警链路隔离：fire-and-forget+线程池+队列满丢弃+contextvars 传播 | **GAP 声称不实**。隔离语义已在真实发送点三层落地：(1) `data/alerter.py:176`"告警落盘异常不回抛"、`:207`"外发面全炸也不反噬告警器，但必须出声"，且带失败文件 journal+日失败率/连续失败检查(:227,:249)；(2) `strategy_pipeline/pipeline_events.py:246-254` alert()——try/except 包裹 Alerter.notify，注释原文即 R3 意图："告警通道故障不反噬管线主流程"；(3) `frontend/implementations/feishu_bot_sender.py:166-168` 发送 best-effort"client 异常不阻断"+回执跟踪。另 `system_telemetry/metrics_bridge.py:204-206` 有 put_nowait+queue.Full 丢弃（遥测面同语义）；`shared/infra/outbox.py:33-37` 事务性 Outbox（至少一次，强于 R3 的有损丢弃）+`:57` trace_id 传播修复（同 contextvars 关注点）。线程池+队列的具体形态缺席，但核心价值（告警失败不反噬主流程）全覆盖 | src/zephyr/data/alerter.py:176,207,227,249；src/zephyr/strategy_pipeline/pipeline_events.py:246-254；src/zephyr/frontend/implementations/feishu_bot_sender.py:159-168；src/zephyr/infrastructure/system_telemetry/metrics_bridge.py:204-206；src/zephyr/shared/infra/outbox.py:33-37 | **伪GAP** | 无需吸收 |
| R4 SchemaVersionGuard | Pydantic config 版本漂移防护：版本双向等值校验+字段存在性检查 | **GAP 部分属实**。版本等值校验（config_version==expected）确无对位——`config/capacity_slo.yaml:15` 有 `schema_version:"1.0"` 字段但无消费者校验它（grep schema_version 于 arch_guard 全无命中）。但 R4 的第二半（字段存在性）有活对位：`scripts/arch_guard/fitness_functions/check_capacity_slo_ssot.py:73-76` 对缺失 `max_latency_ms` 等字段显式 FAIL（SSoT 闭环，manifest.yaml:11 默认全 active）。风险面低：config 在仓内受 git 版本控制+热文件 safe_write 纪律；pydantic 加载处缺必填字段会显式报错；arch_guard 数字对齐已闭环。硬编码 expected_version 的模式本身脆弱（正是漂移源） | scripts/arch_guard/fitness_functions/check_capacity_slo_ssot.py:73-76；config/capacity_slo.yaml:15；scripts/arch_guard/manifest.yaml:11 | **真GAP-登记接受** | 不实现；风险台账登记"capacity_slo.yaml schema_version 字段无校验消费者" |
| R6 KillSwitchSafeguard | Kill Switch 误触发保护：脉冲过滤（持续时长≥sustain）+多条件非AND（≥2 计数） | **partial 属实但核心已覆盖**。防误触发的承重机制=计数确认制在编：`security/access_control/kill_switch.py:90-94` TriggerDefinition(default_threshold=5)、`:282-304` count>=threshold 才 block；另有 `:72,:97` cooldown_seconds 冷却字段。缺席维度：触发前持续时长（sustain）与多条件组合逻辑。属增强细化而非缺口——单信号计数过 5 已滤脉冲；SEV 路由侧另有多信号聚合（redline/sev_router.py:105 aggregate_open_events） | src/zephyr/security/access_control/kill_switch.py:72,90-94,97,282-304；src/zephyr/ai_layer/redline/sev_router.py:105 | **伪GAP**（sustain/多条件两细化以登记接受级注记） | 无需吸收 |
| R7 SandboxHardener | Sandbox 硬边界：memory/execution_seconds/fd 三项硬限**校验**（dict 值比对） | **partial 判定被推翻——原表漏检**。原表称"memory/fd 硬限（setrlimit 类）无 grep 命中"，实则有**真执行**的进程级内存硬限：`trading/__main__.py:36-57` `_set_memory_limit()`——RLIMIT_AS 4GB（容器 cgroup 外的 OS 级兜底，超限抛 MemoryError 而非 OOM 静默杀），main() 首行调用(:61)；这**强于**原设计（原 enforce() 仅返回违规字符串不执行任何限制）。timeout 维度原表已认（process_sandbox.py:50,159-162）。memory 声明面另有 resilience_governance/engine_sandbox.py:93,135 与 gov_drift/resource_guard.py:77。fd 维度确无对位（登记接受级）。注：RLIMIT 为 Unix-only（Windows 静默跳过，:40-42），与容器部署目标一致 | src/zephyr/trading/__main__.py:36-57,61；src/zephyr/governance/resilience_governance/engine_sandbox.py:93,135；src/zephyr/gov_drift/resource_guard.py:77 | **伪GAP** | 无需吸收（fd 维度登记接受） |
| R10 input_pattern_whitelist | 输入白名单：allowed_patterns 子串匹配放行 | **partial 属实，但不吸收**。现役输入防护=LSG L1 黑名单拦截制（`security/llm_defense/llm_security/layers/l1_input.py:203` blocked=jailbreak_hits>0∨direct_hits>0∨total_hits>=3∨score<0.5；`:228` 阻断）。白名单放行语义缺席且与现役设计方向相反——放行制在对抗面下更危险（白名单外的合法输入被误拒、绕过面更大），LSG 黑名单+评分是经过红蓝对抗的现役口径 | src/zephyr/security/llm_defense/llm_security/layers/l1_input.py:203,228 | **伪GAP**（黑名单制即终态设计，白名单语义不引入） | 无需吸收 |
| R11 kill_switch_channel_arbiter | KS 双通道竞争仲裁：文件信号优先，env 降级为缓存 | **partial→伪GAP：歧义已被架构消除**。现役设计中不存在"双信号竞争态"：`security/access_control/kill_switch.py:423-435` `_resolve_state_path` 单一确定性优先级链（显式参数>env `ZEPHYR_KILL_SWITCH_STATE_PATH`>None 纯内存态），信号本体=该单一路径的文件内容——env 只决定"状态存哪"，不构成第二信号源。R11 针对的"两通道值不一致"场景在单 SSOT 路径解析下结构性不可达 | src/zephyr/security/access_control/kill_switch.py:61,423-435,437-443 | **伪GAP** | 无需吸收 |
| R12 error_budget_reconciler | Error Budget 不变式：聚合值 vs 分窗和 tolerance 校验 | **GAP 属实**。独立复跑检索（reconcil/per_window/cumulative/running_total/consistency/invariant/tolerance）于 budget_engine.py、feedback_loop/error_budget.py、error_budget_burst_limiter.py、burn_rate_alerter.py：零命中。记账（record_consumption）、突发限流、burn rate 告警在编，但聚合一致性校验缺席。且 R12 原目标对象 feedback_loop/error_budget.py ErrorBudgetManager 本体为 orphan（src 内零构造调用——SSOT 实为 ops_governance/BudgetEngine）。价值真实点：BudgetEngine 有 shutdown 落盘快照+恢复链路（budget_engine.py:255-293），恢复路径是聚合漂移最可能发生处，加一道不变式断言便宜且有据 | src/zephyr/governance/ops_governance/budget_engine.py:255-293（吸收点）；src/zephyr/feedback_loop/error_budget.py:37-74（orphan 记账件） | **真GAP-吸收** | `governance/ops_governance/budget_engine.py` recover_from_snapshot()：恢复时校验 snapshot 分项和==聚合值（tolerance 1%），不符 fail-closed 重建——约 10 行，随下一次 budget_engine 变更批落地 |
| R13 slo_config_sanitizer | SLO 配置脱敏：敏感键（threshold/target/budget/limit/secret）数值替换 *** | **partial→伪GAP：风险对象实际不存在**。真正敏感的配置值=密钥，按宪法 RULE-SECRETS 走 secrets.py 三道 gate（`shared/security/secrets.py`），不落 config dict——脱敏对象缺位。数值阈值（target=1000、target_ms=2000 等）非敏感信息，且 capacity_slo.yaml 本身是机读 SSoT 注册表（arch_guard 消费），打 *** 反而破坏机器可读性。数据面脱敏已有规则册 `config/data_masking_policy.yaml`（role→field→kind，data_security/wiring/data_exit_guard.py:29,67 消费）与文本面 ai_masking_pipeline.py:163-188 | src/zephyr/shared/security/secrets.py；config/data_masking_policy.yaml；src/zephyr/data_security/wiring/data_exit_guard.py:29,67 | **伪GAP** | 无需吸收 |
| R14 MigrationCrashRecovery | ContractBus 迁移崩溃恢复：checkpoint 文件记录已完成批次 | **GAP 属实但对象已消亡**。ContractBus"三批迁移（15+15+14）"是**静态一次性代码搬运**——capacity_assurance/contracts/contract_bus.py:36-56 ContractBusLoader 仅 import 三批 pydantic 模型类字典，无任何运行时批次执行过程，不存在"跑到一半崩溃"的态；且该 Loader 包外零消费者（orphan，证据表 DD-9 注记属实）。checkpoint-resume 模式本身在编有先例（scripts/backtest/t0_rule_engine.py:596-620 manifest["batches_done"] 逐批落盘断点续跑+切面漂移防呆），未来真有长批迁移可直接复用该模式，无需预置吸收 | src/zephyr/infrastructure/capacity_assurance/contracts/contract_bus.py:36-56（静态加载无运行时态）；scripts/backtest/t0_rule_engine.py:596-620（现役 checkpoint 先例） | **真GAP-登记接受** | 不实现；台账注记"长批迁移断点续跑复用 t0 manifest 模式" |
| R15 unicode_path_normalizer | Unicode 路径规范化：NFC+斜杠统一+casefold | **GAP 部分不实**。"同对象（路径）无对位"被推翻：`gov_enforcement/rule_bridge/git_commit_gateway.py:3704-3706` `path.replace("\\","/").casefold()`——路径斜杠统一+大小写归一正在全仓并发最敏感的提交门路径匹配里承重（与 git status :(icase) 语义对齐）。三要素中仅 NFC 规范化缺席；Windows+NTFS 保留精确形态且仓内路径来源单一（Python API/git），NFC/NFD 分歧面实际趋零（该风险主要属 macOS HFS+ 生态）。文件路径逃逸防护另有 shared/io/file_utils.py:654-698 resolve+前缀判定 | src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:3704-3706；src/zephyr/shared/io/file_utils.py:654-698 | **伪GAP**（NFC 维度以登记接受级注记） | 无需吸收 |
| R16 ChromaDBThreadGuard | ChromaDB 线程池泄漏防护：任务计数达阈值回收重建 executor | **GAP 声称的威胁模型不成立**。R16 防的是"自建 ThreadPoolExecutor 提交 chroma 任务导致泄漏"，但现役 chroma 消费**不经过任何自建线程池**（grep ThreadPoolExecutor 于 integration/vector_memory/*.py：零命中）：PersistentClient 均为缓存单例（bridge_layer.py:170 `self._kb_client`、collection_manager.py:296 `self._client`），无逐任务创建。线程/连接治理在编：in_process_vector_memory.py:215-230 维护线程 stop_event+join(5.0) 完整生命周期；sqlite_metadata_store.py:121-158 threading.local 连接+_all_conns_lock 全连接跟踪；faiss_collection_manager.py:100 写锁。且 migrate_chroma_to_faiss.py:79 在编表明 chroma 处于退位迁移轨道，长周期投入不经济 | src/zephyr/integration/vector_memory/bridge_layer.py:167-170,248-250；src/zephyr/integration/vector_memory/collection_manager.py:294-296；src/zephyr/integration/vector_memory/in_process_vector_memory.py:215-230；src/zephyr/integration/vector_memory/sqlite_metadata_store.py:121-158；src/zephyr/integration/vector_memory/migrate_chroma_to_faiss.py:79 | **伪GAP** | 无需吸收 |

## CT-4 专项裁定（iguana 禁开仓闸门）

| 项 | 设计意图 | 复核结论 | 证据 | 裁定 | 处置 |
|----|---------|---------|------|------|------|
| CT-4 iguana-rebalancer 禁开仓闸门 | 资本容量告警→禁止新开仓；OTel: capacity.capital_check→iguana.rebalance.gate | **半不实**。"iguana" 全仓仅存在于待评估退役件自身内部（cross_module_integration.py:24,184,187,219 与 contracts/batch3_integration.py:77 的 CtCt4 dataclass）——iguana-rebalancer **从未作为模块存在**，契约指向不存在的消费方。但"禁开仓闸门"动作语义在编且已接线：trading_kill_switch.py:76 POSITION_LIMIT 级 action=**"REDUCE_ONLY: 禁止开仓, 允许平仓"**（五级熔断之一），经 autonomy_core/kill_switch_orchestrator.py:161,336 注册为 trading 域适配器，且 redline/sev_router.py:38 已有"SEV-2 资金异常→trading_kill_switch 五级任一触发"的资本侧联动。缺口仅剩"capacity 子系统的资本容量告警"作为触发源——该源随 risk_mitigation 一同在退役评估中 | src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:71-76；src/zephyr/autonomy_core/kill_switch_orchestrator.py:161,334-336；src/zephyr/ai_layer/redline/sev_router.py:38 | **伪GAP**（闸门在编；iguana 契约过时） | iguana 术语随 capacity_assurance 评估件一并退役；CtCt4 dataclass 同批处置 |

## CT-1~3 现役路径核查（对照表称 partial/wired/partial）

| 项 | 对照表声称 | 核查结论 | 证据 |
|----|-----------|---------|------|
| CT-1 Error Budget L3+→自动模型路由切换 | partial：路由组件 wired、联动链无实证 | **路径属实**：model_router.py:70,127（ModelRouter.route，benchmark/cost/complexity 驱动）+ llm_gateway.py:366-390 `_perf_aware_route_fields`（懒加载调用 route，perf-aware enrichment 字段，故障兜底 router-unavailable）。**联动缺口属实**：route 无 budget level 入参；grep budget L3→router callback 零命中；EngineDegradationManager（engine_degradation.py:110-151）管的是 agent/engine 访问降级，非模型路由。**判读：联动缺口=登记接受**——预算耗尽自动切模型有错切风险，现役 perf-aware enrichment+model_routing_policy.yaml 手册制已提供成本感知，不吸收自动联动 |
| CT-2 KS→高风险通道暂停、低风险通道（国债/货币市场）豁免 | partial：五级熔断 wired、通道级豁免无对位 | **属实**。五级熔断+编排挂接+SEV 联动三路径全真（trading_kill_switch.py:52-116；orchestrator.py:161-189 空目标=全部五级=**全量暂停**；sev_router.py:38）。treasury/money_market 通道豁免 grep 零命中（本班复认）。**判读：豁免缺口=登记接受**——通道级豁免是降低保守性的设计，全量 REDUCE_ONLY 更安全；若未来需要，落点在 orchestrator 适配器加 scope 过滤，现不实现 |
| CT-3 Token Budget 耗尽→RATE_LIMITED 不崩溃 | wired | **属实**。BudgetEngine 消费链真：gov_enforcement/rule_enforcement/pre_flight_gate.py:53-54 `self._engine = engine or BudgetEngine()`；限流降级真：behavioral_admission/admission_controller.py:276-292 双桶耗尽→AdmissionDecision.RATE_LIMITED+retry_after_ms；admission_response.py:46 RATE_LIMITED→**QUEUED**（入队不崩溃）。无缺口，无需裁定 |

## 裁定分布统计

| 裁定 | 项 | 数量 |
|------|----|------|
| 伪GAP（归档无吸收必要） | R3、R6、R7、R10、R11、R13、R15、R16、CT-4 | **9** |
| 真GAP-吸收 | R12（→ops_governance/budget_engine.recover_from_snapshot） | **1** |
| 真GAP-登记接受 | R4、R14 | **2** |
| 附带判读（不计 R 表主统计） | CT-1 联动缺口=登记接受；CT-2 豁免缺口=登记接受；CT-3=wired 属实无缺口 | 2+1 |

## 遗留注记（供 chief）

1. 证据表自身引证漂移：其引用的 `capacity_assurance/schema.py:57,108` 与 `sli_instrumentation.py` 已在评估期内被移入 `_archive/`（本班 2026-10-08 核实）——R8/R9 所依赖的 ai_provenance 表 SchemaManager 同在归档之列，chief 终裁 R8/R9 时应以 _archive 现状为准。
2. R12 吸收以"下一次 budget_engine 变更批"为载体（净零增长纪律：并入既有变更，不开新件）。
3. 原表 partial 判定整体可信度尚可（方向全对），但平面 grep 漏检三处（R7 RLIMIT_AS、R15 gateway 路径归一、CT-4 REDUCE_ONLY 闸门）——凡"零命中"结论均需调用链复核后方可入裁定，此为本次裁定与原表结论差异的方法论根源。
