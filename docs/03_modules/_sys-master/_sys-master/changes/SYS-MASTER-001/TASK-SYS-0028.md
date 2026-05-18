---

task_id: "TASK-SYS-0028"
source_blueprint: "SYS-MASTER-001"
source_section: "§41 订单执行与风控(OMS) + §88 状态机形式化与正确性验证 + §93 会话并发与文件完整性防御"

title: "OMS三层风控(Pre-Trade/At-Trade/Post-Trade)+状态机(PENDING→ACK→PARTIAL_FILL→FILLED/REJECTED/CANCELLED) + 状态机YAML统一规范(自动测试生成+崩溃协调) + 会话并发ZephyrLock(文件锁/冲突检测/预分配)体系搭建"
description: |
  将 §41 订单执行与风控 + §88 状态机形式化 + §93 会话并发与文件完整性防御三合一落地为执行层完整性锚点。
  §41 定义：
  （1）三层风控时间线——Pre-Trade（仓位上限/风险敞口/资金充足/熔断暂停→拒绝下单）· At-Trade（价格偏离度/秒级频率限制→撤单+ALARM）· Post-Trade（PnL归因/TCA/累计滑点追踪→写入日报 §61）。
  （2）Production Shadow——订单同时发往实盘+虚拟盘→对比滑点→校准（§64）。
  （3）OMS 状态机——[FIX_NewOrderSingle] → PENDING → ACK → PARTIAL_FILL → FILLED → [FIX_ExecutionReport]· 任何 → REJECTED/CANCELLED → 自动重试。
  §88 定义：
  （1）统一状态机 YAML 描述规范——states（PENDING/ACK/PARTIAL_FILL/FILLED/REJECTED/CANCELLED）/initial（PENDING）/terminal（FILLED/REJECTED/CANCELLED）/transitions list + invariants（max one transition per event/no transition from terminal states/order_id unique across all live states）。
  （2）从 YAML spec 自动生成测试——for each valid transition: test_CAN + for each invalid: test_CANNOT + 边界: test_no_transition_from_terminal。
  （3）崩溃后状态协调——WAL/Journal读取最后已知合法状态→查询经纪商回执真实状态→对比（一致→恢复/不一致→broker为准+写入事故日志 §二十）→检查所有活跃实体状态一致性。
  §93 定义：
  （1）四种并发冲突场景——两session改同一文件（后写入覆盖）/session-A改imports session-B移除依赖/重构函数签名vs旧签名调用/改蓝图vs按旧蓝图施工。
  （2）ZephyrLock 文件锁——写入前 MUST acquire EXCLUSIVE lock· lock TTL 30min超时自动释放+session通知· Owner有 force_unlock 权限。
  （3）冲突检测——保存前检查磁盘文件mtime>上次读取mtime→文件已被其他session修改→同一语义域自动合并(git merge-file风格)/不同语义域暂停Owner决定/自动合并失败两session都暂停Owner手动解决。
  （4）预分配策略——Session启动声明本次将修改的文件→调度器检查活跃锁→无锁分配/有锁排队或拒绝。
  本卡搭建 oms_risk_engine.py + fsm_verifier.py + session_concurrency.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\lock_files.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\oms_risk_engine.py"
    description: "§41 三层风控(Pre/At/Post) + Production Shadow + OMS状态机(PENDING→ACK→PARTIAL_FILL→FILLED)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\fsm_verifier.py"
    description: "§88 YAML统一规范+自动测试生成+崩溃状态协调(broker为准)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\session_concurrency.py"
    description: "§93 ZephyrLock EXCLUSIVE锁+冲突检测4场景+预分配策略"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\oms_risk_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\fsm_verifier.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\session_concurrency.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\scripts\\lock_files.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§41 OMS三层风控+状态机 + §88 YAML规范+自动测试+崩溃协调 + §93 ZephyrLock+冲突检测+预分配"
  - file_path: "D:\\ZephyrAlpha\\scripts\\lock_files.py"
    reason: "现有 lock_files.py——session_concurrency.py 复用其原子目录锁逻辑，不直接修改"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 80

acceptance_criteria:
  - "oms_risk_engine.py 实现 RiskLayer 枚举（PRE_TRADE/AT_TRADE/POST_TRADE）——PreTrade（position_limit/exposure/cash/circuit_breaker→reject）· AtTrade（price_deviation/freq_limit→cancel+ALARM）· PostTrade（PnL_attribution/TCA/cumulative_slippage→daily_report §61）"
  - "oms_risk_engine.py 实现 ProductionShadow——order→LiveBroker+VirtualBroker 双发→compare slippage→calibrate §64 FF model"
  - "oms_risk_engine.py 实现 OMSStateMachine——6 states（PENDING/ACK/PARTIAL_FILL/FILLED/REJECTED/CANCELLED）· initial=PENDING· terminal=[FILLED,REJECTED,CANCELLED]· transitions: PENDING→ACK(broker_ack)/ACK→PARTIAL_FILL(partial_exec)/PARTIAL_FILL→FILLED(remaining_exec)/PENDING→REJECTED(broker_reject)/[PENDING,ACK,PARTIAL_FILL]→CANCELLED(cancel_request)"
  - "fsm_verifier.py 实现 YAMLSpecLoader——parse statemachine YAML→ validate invariants(max_one_transition/no_terminal_transition/unique_order_id)· auto_gen_tests(per_valid→CAN + per_invalid→CANNOT + terminal_boundary)"
  - "fsm_verifier.py 实现 CrashReconciler——read WAL last_state· query broker external state· compare→一致(resume)/不一致(broker为准+log incident §二十)· check_all_active_entities"
  - "session_concurrency.py 实现 ZephyrLock——acquire(file_path,session_id)→EXCLUSIVE lock(.ailocks/{sanitized}.lock/owner.json)· TTL 30min→auto release+notify· force_unlock(owner_only)"
  - "session_concurrency.py 实现 ConflictDetector——save前 mtime check→同一域(merge-file)/不同域(pause+Owner通知)/merge失败(两session暂停+Owner手动)· PreAllocator——session启动声明文件→调度检查→分配/排队/拒绝"
  - "script_manifest.yaml 注册全部 3 个 .py"

rollback_instructions: |
  1. 删除 oms_risk_engine.py / fsm_verifier.py / session_concurrency.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0027"
blocked_by: []
status: "done"
tags_fn:
  - "trading"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
blueprint_id: DOM-GOV-001
---
