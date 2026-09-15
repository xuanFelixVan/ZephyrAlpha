---
ttl: task_bound
completes_when: >-
  加减乘除清单（§5）每一项均有终态（commit 落地 / 裁定保留 / 裁定废弃归档）；
  机械验证 = 本文件 §5 各条目被逐条标注处置 commit hash 后，由工作文档清理批
  reconciler 按 GATE-WORKING-DOCS 语义判定结案归档。
---

# 治理守护模块挖矿 SOP 方案地图（2026-09-15 立项）

> 创建：2026-09-15 ｜ 会话：qoder-gov-patch-20260915 ｜ 状态：**减法批+全景图前端页已落地，加法/乘法待逐项施工**
>
> 落地凭据（2026-09-16 回填）：减法批=1ddcd089（25 文件：8 死模块+11 vms_ri 归档脚本+6 死测试
> +ZA-IF-0010 deprecated）；GOMAP disconnected 更新=b1334ae3ff（GOMAP 生成器会话同批带入）；
> 治理全景图前端页=85e39614（govm.js/govm.html/api_server 路由/导航/冒烟测试 2 例）。
>
> 起因：2026-09-15 提交内存耗尽事故（9 个孤儿 llama-server ≈12GB，commit 71.2/79.9GB
> 触顶 → 800705AF 弹窗 + 全系统卡死/黑屏）。Owner 指令：先把项目里已有治理模块全部
> 挖出来入地图（不管死活），再做加减乘除（删/接/升/通），避免重复建设。

## 1. 挖矿方法与纪律

- 方法论真源：`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md`
  （v1.3.0：矿脉枯竭结构判据 + 世界地图完备优先）。本篇是该 SOP 在"治理域"的一个战役实例。
- 死活判定说明：§3 各条目的 ✅/⚠️/🧪 标记是 2026-09-15 grep 快照（反查 import/注册/测试），
  **处置前必须逐项人工复核**（注册表装配、插件式发现机制会造成假孤立）。
- 纪律：处置一律走正常施工流（claim→补丁→测试→GitCommitGateway），禁一次大爆破。

## 2. 事故复盘（本战役直接动因）

| 环节 | 事实 |
|------|------|
| 根因链 | boot detached spawn `ollama serve` → 每实例按需加载 2 模型(llama-server) → 多次 boot 堆出 9 实例 ≈12GB → commit 触顶 |
| 孤儿机制 | `_OllamaProcessManager.terminate_proc` 裸 terminate 只杀父；reaper 只管 cmdline 含项目根路径的 python 进程 → llama-server 两头不管 |
| 已落地 | ①杀 9 孤儿(commit 71→31.5GB)；②E: 页面文件 16GB→32/64GB(重启生效)；③terminate_proc 树杀 + reaper 判定矩阵第 10 条(项目衍生孤儿族)，commit `8aaede05cb`，49 测试绿+实机 dry-run 零误伤 |

## 3. 模块地图（75 src + 25 scripts + 38 文档/配置资产）

标记：✅=有生产引用 ｜ ⚠️=疑似断线/孤立(处置前需复核) ｜ 🧪=仅测试/CLI ｜ 🔁=重复实现组

### A. 进程收割/孤儿/幽灵（src 9）
- ✅ `trading/process_reaper.py` — 收割主力，Task Scheduler 10min one-shot；本战役已扩第 10 条
- ✅ `trading/orphan_detector.py` — 孤儿进程检测(status_dashboard/auto_runtime_core 消费)
- ✅ `security/access_control/orphan_judge/` — 安全域孤儿判定(注意：管文件/引用不管进程)
- ⚠️ `infrastructure/auto_fix_engine/zombie_cleaner.py` — 疑经 fixer 注册表装配
- ⚠️ `feedback_loop/diagnosers/reliability/zombie_fle_detector.py` — 疑经 diagnosers 装配
- ⚠️ `governance/security_governance/ghost_scan.py` — 未见 import
- ✅ `gov_drift/orphan_scanner.py` — 文件/文档孤儿(非进程)
- scripts 孤儿修复器族：`fix_orphan_all.py`、`governance/d1_structure/detect_orphan_py.py`、`check_wiring_orphan.py`、`d9_knowledge/detect_orphan_documents.py`

### B. 看门狗（5）
- ✅ `infrastructure/system_telemetry/watchdog.py` — 三冗余互检+Panic+Dead Man 1800s
- ⚠️ `governance/resilience_governance/last_resort_watchdog.py` — 蓝图声明 CONSUMERS=escalation 但无 import（断线候选 B1）
- ✅ `gov_enforcement/rule_bridge/worktree_drift_watchdog.py` — git_commit_gateway 消费
- ✅ `risk/core/drawdown_watchdog.py` — 交易域
- ✅ `scripts/governance/meta/governance_watchdog.py`

### C. 健康监控/心跳/探针（src 18）
- ✅ `trading/health_monitor.py`、`system_telemetry/health_probes.py`、`system_telemetry/health_aggregator.py`(boot_hooks 消费)
- 🔁⚠️ `infrastructure/health_monitor/health_aggregator.py` — 第二套 HealthAggregator，仅自身 `__init__` 导出（双胞胎死代码候选 C1）
- ⚠️ `orchestrator/agent_health_monitor.py` — 蓝图 CONSUMERS 空（C2）
- ⚠️ `feedback_loop/diagnosers/health/self_health_monitor.py`
- ✅ `vector_memory/index_health_monitor.py`、`semantic_audit/self_health.py`、`shared/lifecycle/healthcheck_service.py`、`health_discovery.py`、`longevity_monitor.py`、`data/redundant_source/heartbeat_monitor.py`、`gov_enforcement/rule_bridge/heartbeat_daemon.py`、`governance/ops_governance/burn_rate_monitor.py`
- ⚠️ `shared/alerts/heartbeat_server.py`、`shared/lifecycle/task_heartbeat.py`（C3/C4）
- ⚠️ `gov_code_quality/code_dedup/health_monitor.py`

### D. 资源监管（src 8）
- ✅ `gov_drift/resource_guard.py` — 512MB/2GB 硬限+四级降级，**但只护 gov_drift 自身扫描**
- ✅ `trading/resource_optimization.py` — 总调度(DaemonRegistry+进程池+ghost 扫描+GPU)
- ✅ `shared/infra/process_pool.py` — 隐藏 detached 孵化入口(60+ 消费方；**孵化不收割=本次事故结构性缺口**)
- ✅ `l5_resource_protection.py`(LLM 成本)、`gpu_monitor.py`、`gpu_resource_manager.py`
- ⚠️ `security/access_control/guards/memory_guard.py`(RBAC 内存访问守卫，非 RAM 监管)、`infrastructure/hot_plane_budget.py`

### E. 生命周期/守护/监督（src 14）
- ✅ `trading/lifecycle_manager.py`、`boot_hooks.py`(装配枢纽)、`stop_gate.py`、`windows_service.py`、`infrastructure/process_supervisor.py`(NSSM 散件)、`shared/infra/process_lifecycle_gateway.py`(**有 CI 强制门**，与 process_pool 🔁双轨=E1)、`shared/lifecycle/daemon_registry.py`、`infrastructure/runtime/startup_shutdown.py`、`a2a supervisor`、`checker_supervisor.py`、`task_lifecycle_manager.py`
- 🔁⚠️ `governance/ops_governance/startup_shutdown.py`(+cli) — 与 infrastructure 版几乎同名（E2）
- ⚠️ `gov_code_quality/code_dedup/shared_lifecycle_manager.py`、`gov_enforcement/rule_bridge/worktree_lifecycle.py`

### F. Kill Switch/熔断（src 20）
- 🔁 **KillSwitch×5**：`security/access_control`(✅boot)、`infrastructure/rollback`(✅)、`infrastructure/capacity_assurance`(✅，注释自认 shared 统一 SSoT 不存在)、`trading_contracts/risk`(✅)、`autonomy_core/kill_switch_orchestrator`(⚠️五域编排层无人 import=F1)+`killswitch_response_levels`(🧪)
- 🔁 **CircuitBreaker×8**：shared/api_client✅、infrastructure/reliability✅、resilience_governance✅、pipeline_manager✅、gate_engine CBG✅、data source✅、adversarial✅、交易域×2🧪
- ✅ `feedback_loop/resilience/deadman_switch.py`、`failover_coordinator.py`
- ⚠️ `orchestrator/fault_tolerance/degrade_cascade.py`
- scripts：`manage_kill_switch.py`、`check_kill_switch_latency.py`

### G. 自愈/Reconcile（src 8 + reconciler 9 + scripts 12+）
- ✅ auto_fix_engine/self_heal_agent、semantic_audit/self_healer、F5BootIntegration、audit reconcile_worker/runner/registry + 8 个 *_reconciler(测试全齐)
- ✅ scripts：vms_health_check(+🔁archive 一套)、ch_health_probe、run_boot_sla_probe、session_startup_health_check、architecture_health_dashboard、ops_guard 等

### H. 文档/配置资产（挖矿代理盘点 38 项，核心 12）
- ● `docs/03_modules/_domain_data/boot_autostart_architecture.md` — 永久服务 SSOT 清单(第一锚点)
- ● `docs/03_modules/_domain_infrastructure_runtime/process_supervisor/blueprint.md` — MOD-INF-066 NSSM 五进程(P1-P5 启停序/分级心跳)
- ● `docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md` — MAPE-K
- ● `docs/01.../ops_sop/emergency_runbook.md` — 保命轨 D-L1~D-L3
- ● `config/external_watchdog.yaml`(v2.6 飞书告警)、`config/nssm_p1_p5_service_definitions.yaml`(**DRAFT 未收口**)、`config/alert_rules.yaml`(OOM>8GB critical 已有!)、`config/resource_optimization.yaml`(MEM 70/80/90% 四级阈值已有!)
- ● capability_cards：daemon_registry、system-telemetry 九子系统

## 4. 体检结论（结构性发现）

1. **半套"总指挥部"已存在但断线**：NSSM P1-P5 服务定义、外部看门狗、OOM 告警规则、
   MEM 四级阈值、kill_switch_orchestrator 五域编排、last_resort_watchdog——蓝图/配置全有，
   多为 DRAFT/无人 import。缺的不是新系统，是**接线与收口**（回应 Owner"总指挥部"设想：
   全功能版=过度工程，OS 内核已是调度器；把断线资产接上=最小三件套的自然延伸）。
2. **孵化与收割分离**：process_pool(孵化，60+ 消费方)不管事后收割；reaper 只管项目路径内
   python。非 python 衍生进程两头不管（本次事故）。ProcessLifecycleGateway 有 CI 强制门
   但与 process_pool 双轨并存。
3. **无人做系统级内存看护**：resource_guard 只护 gov_drift、L5 只护 LLM 成本、watchdog 是
   心跳互检——提交内存水位无任何闸口（补丁只解决孤儿，没解决"水位高时照样启动重任务"）。
4. **重复实现 6 组**：CircuitBreaker×8、KillSwitch×5、orphan_detector×2、health_aggregator×2、
   startup_shutdown×2、api_lifecycle×2(gov_audit vs lifecycle_governance)。
5. **空白**：ops_sop 无"进程失控/内存耗尽"应急处置 SOP（本次靠人肉诊断）。

## 5. 加减乘除行动清单（每项处置后回填 commit hash）

### 减（清理，全部需先复核装配机制）

> **核验教训（2026-09-15 二次复核）**：子代理深度核验报告 3 处误判被动刀前 grep 复核拦下——
> source_circuit_breaker（data/scheduler.py:97 真引用）、circuit_manager（经 pipeline_orchestrator
> 被 auto_runtime_core.py:65 引用）、trading_kill_switch（kill_switch_orchestrator:331 惰性 import）。
> 教训：TEST-ONLY 判定必须区分「docstring/CONSUMERS 头提及」vs「真 import 语句」，且业务域模块
> （daban/trade_level 有域文档+TDM 落码背书）不适用治理死码标准。另 blueprint 对账发现 5 处头声明
> 漂移（health_aggregator/health_aggregator(tel)/watchdog/zombie_cleaner/kill_switch_latency 探针
> 指向不存在路径），后者已列入加法修复。

| # | 对象 | 动作 | 前置/验证 | 终态 |
|---|------|------|-----------|------|
| R1 | `infrastructure/health_monitor/health_aggregator.py`(双胞胎) | 删 | grep 确认仅 __init__ 自导出；跑 system_telemetry 全测 | ✅ 已删（1ddcd089，二次核验 CONFIRMED-DEAD，零外部 import） |
| R2 | `governance/ops_governance/startup_shutdown.py`+cli | 删或并入 infrastructure 版 | 查 governance/__init__ 导出链消费方 | ✅ 已删双文件+governance/__init__:287 桥接行+__all__ 条目（1ddcd089，消费方全走 infrastructure 版） |
| R3 | `scripts/governance/_archive/vms_ri/` 重复套件 | 归档删除 | 无引用 | ✅ 已删 11 脚本（1ddcd089，全仓零引用） |
| R4 | CircuitBreaker×9 / KillSwitch×5 收敛 | 长期战役，逐域向 SSoT 收 | 每次收敛独立裁定（涉及 F 域 human_gate？查 risk_tier_registry） | 部分执行（1ddcd089）：删 reliability/circuit_breaker+failover_coordinator+api_lifecycle×2+ghost_scan；**保留** source_circuit_breaker(data/scheduler:97 真引用,核验误判)/circuit_breaker_manager(pipeline_orchestrator 活引用,误判)/trading_kill_switch(MOD-INF-016+A3目标)/daban_instant(打板五件,24号§3.13)/trade_level(连续亏损熔断,42号§3.10 TDM 落码)/capacity_assurance+context_pipeline_auto 待裁；canonical=shared/resilience(通用)+access_control(系统级)；ZA-IF-0010 已标 deprecated（同批） |

### 加（接线）
| # | 对象 | 动作 | 前置/验证 | 终态 |
|---|------|------|-----------|------|
| A1 | `nssm_p1_p5_service_definitions.yaml` DRAFT | 收口落地或裁定废弃 | Owner 窗口(蓝图自述) | |
| A2 | `config/alert_rules.yaml` OOM>8GB critical | 接通知通道实测一轮 | ~~飞书 webhook 真实告警一次~~ → 2026-09-15 Owner 裁定：飞书/SMTP 通道彻底删除，通知=前端 promotion 页 | A2 改口径=OOM critical 事件落到 promotion 页通知，待施工 |
| A3 | `kill_switch_orchestrator` 五域编排 | 挂 boot_hooks 或裁定废弃 | RBAC 测试+boot 冒烟 | ✅ 已接线（裁定#254 Owner 放行；1d6a206b 登记+49dde8fd 施工）：boot_hooks 启动链 _init_kill_switch_orchestrator 注册五域开关（system+skills/trading/rollback/capacity），get_orchestrator 进程级单例，注册失败仅告警不阻断启动；降级顾虑由 fail-open+测试兜底（tests/autonomy/test_kill_switch_orchestrator.py TestBootWiring） |
| A4 | `last_resort_watchdog` | 接 escalation_protocol 或废弃 | 蓝图声明 vs 现状对齐 | ✅ 已接线（裁定#254 Owner 放行；49dde8fd）：escalation_engine.escalate 升至 L4_EMERGENCY 且重试耗尽时 activate() 点亮旗标，emergency_shutdown 不得自动调用（watchdog 不得自触发）；单例 get_last_resort_watchdog；3 回归测试（tests/escalation/test_escalation_core.py TestLastResortWiring）93 全绿 |
| A5 | `agent_health_monitor`、`heartbeat_server`、`task_heartbeat`、`degrade_cascade` | 逐个接线或删除 | wiring 复核 | 核验修订：全为 TEST-ONLY；✅ 四件全删（Owner 裁定）：heartbeat_server/task_heartbeat/degrade_cascade=零生产引用+头注虚标 CONSUMERS+活替代已存在（reaper/boot_hooks 任务事件/fault_tolerance 真熔断），随减法批删除（9deb35e709）；agent_health_monitor=概念留档（三态+5 SLO+硬软双阈值，git 可溯），第三层 AI 自治期按届时需求重建（幻觉率 SLO 届时与 feedback_loop auto_evolution hallucination_interception 合一真源）；zombie_cleaner 从本单剔除（auto_fix_engine/engine.py:247 动态注册=活，挖矿误判）；ghost_scan 已删（与 reaper scan_ghost_windows 重复） |

### 乘（升级/打通）
| # | 对象 | 动作 | 前置/验证 | 终态 |
|---|------|------|-----------|------|
| M1 | process_pool × ProcessLifecycleGateway 双轨 | 合并为统一孵化入口，孵化即登记(父 PID/预期寿命/树) | 60+ 消费方渐进迁移，CI 门已有 | |
| M2 | 水位门禁 | 重任务 spawn 前查 commit 水位，>85% 排队/拒绝 | 挂 process_pool 统一入口后自然落位；阈值复用 resource_optimization.yaml | |
| M3 | 孵化-收割闭环 | process_pool 登记表落盘 → reaper 消费(替代 cmdline 特征猜测) | 与 M1 同战役 | |
| M4 | llama-server 崩溃稳定性 | 事件日志 0xc0000005×3 溯源(Ollama 版本/模型/VRAM) | 对照 `gguf_vram_budget.yaml` | |

### 除（终止/防复发，已完成 ✅）
- ✅ terminate_proc 树杀（8aaede05cb）
- ✅ reaper 判定矩阵第 10 条项目衍生孤儿族（8aaede05cb）
- ✅ E: 页面文件 16→32/64GB（2026-09-15，重启生效）

## 6. 新增 SOP 待写（空白填补）

- `ops_sop/process_runaway_incident_sop.md`：进程失控/提交内存耗尽应急处置
  （症状识别 800705AF/卡死 → commit 水位诊断 → 孤儿收割 → 页面文件核查 → 复盘登记）。
  本次诊断路径已验证可复用，待立项后从本篇 §2 抽取。

## 7. 未挖长尾（矿脉地图）

- F 域熔断收敛(R4)的逐域深挖；E1 双轨合并(M1)的消费方普查；autonomy_core 域
  (kill_switch_orchestrator 所在)整体死活判定；docs/02 企业架构侧治理蓝图与 src 实现的
  逐蓝图对账（本次只做了模块级，未做蓝图级）。
