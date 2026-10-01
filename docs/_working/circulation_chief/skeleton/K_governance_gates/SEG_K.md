---
ttl: task_bound
title: K 段·治理门禁链挖矿档（W3-3，含红线 V1-V5 交叉）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# K 段·治理门禁链（F97-F110+F124+F128，16 环节；F125 交界归 A 段档）

> 方法同 SEG_I。**本档 §V 为自动化全景红线 V1-V5 与 K 段环节的代码级交叉核定**（任务书第 3 条）。
> F124 本轮翻案：登记面已建成（见 F124.md）。

## 六向台账

| 环节id | 名称 | 上游 | 下游 | 生产者路径:行 | 消费者 | 自动化态 | 运行态 | 三态复核(骨架→本轮) |
|--------|------|------|------|--------------|--------|----------|--------|--------------------|
| K-01(F97) | commit 侧门禁链 | — | 提交链 | src/zephyr/gov_enforcement/commit_gates/ **119 py**（ls 实测）；注册真源=rule_bridge/commit_gate_registry.py（外部锚 docs/03_modules/_domain_gov_enforcement/algo_flow/rule_bridge/commit_gate_registry.yaml:1-3 source_of_truth） | git_commit.py 提交面 | 事件（提交时） | 每次提交实跑 | 挖干→挖干（骨架"23 环节引用"口径维持，门件规模 119 实测补记） |
| K-02(F98) | GateEngine 运行时门禁 | 规则 | 全链 | src/zephyr/gov_enforcement/rule_enforcement/（adaptive_threshold/admission/anti_pattern_guard/audit_chain_verifier/breaking_change_detector 等 30+ 件）；册=docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | 全链动作→GatePipeline | 事件 | 实跑（提交面/工具面双载） | 挖干→挖干（**规模漂移：骨架"91 门 canonical" vs 实测 gate_id 181 条/own_scope 143**，机生口径待生成器定版） |
| K-03(F99) | 漂移检测 | F98 | 告警 | src/zephyr/gov_drift/（70 项，detector/drift_ 前缀 15 件实测；scan_mutex.py 互斥） | 告警/审计 | 骨架称"常驻（双 watchdog）" | **双 watchdog 未获直证**：gov_drift 域内 "watchdog" 仅 scan_mutex 命中；全景 WorktreeDriftWatchdog 属 RULE-WORKTREE 非本域 | 挖干→挖干（运行态注记待核，勿凭任务名误认） |
| K-04(F100) | 红蓝对抗 | — | F98 | src/zephyr/security/adversarial_validation/ 27 件（ls 实测）；_scenario_registry.yaml（**场景 53 条 grep 实证**，骨架口径吻合） | 宪法/gate 加固 | 定时（对抗批次；C4Exam Weekly 14:00 全景 §1.1） | 任务 Ready | 挖干→挖干 |
| K-05(F101) | 规则与裁定体系 | Owner 门 | 全链 | docs/01_policies_and_standards/rules/trae_*.yaml=**86 册**（ls 实测，骨架吻合）；ruling_registry.yaml | 全链治理 | 事件（裁定登记） | 在用 | 挖干→挖干（**V1 交叉主位之一**：MetaqAuditReconcile 豁免主张引用"裁定先例"，见 §V） |
| K-06(F102) | 审计体系 | 全链 | 报告/L-05 | src/zephyr/gov_audit/ 63 件（ls 实测）；merkle_hourly.py:19（MOD-INF-020 每小时 Merkle 聚合）/merkle_audit.py | 审计报告/L 段 | 定时（Merkle 小时链）+任务 GateFullTreeAudit Daily 03:30（全景 §1.1） | 在跑 | 挖干→挖干（**V1 交叉主位之二**：meta_question 对账件行政归属在本面，见 §V） |
| K-07(F103) | 代码质量与克隆守卫 | F98 | 施工 | src/zephyr/clone_guard/（orchestrator.py/mcp_server.py/engines/rules/strategy_fingerprint.py）；__init__.py:8/:13/:25（L0 MCP check_before_write=advisory 不阻断；orchestrator.check 永不抛） | 写前预查（宪法 RULE-CLONEGUARD） | 事件（写前预查） | MCP L0 在用 | 挖干→挖干 |
| K-08(F104) | 会话并发治理 | — | 提交链 | src/zephyr/security/access_control/session_concurrency.py（L8 分片真源 invariants；:152 心跳 30s；:166-173 _ACTIVITY_IDLE_TIMEOUT_SECONDS=1800；:254 logical 豁免；:492 register/:520 last_activity=time.time()；:587/:823 真实治理操作刷新） | scripts/git_commit.py:24-46（--session/--enqueue）；heartbeat_daemon | 事件（claim/release） | 守护在跑但 9/10 会话活性不可信（全景 §2.1）——**V2/V3/V4/V5 主位**，见 §V | 挖干→挖干（V 交叉标注在案） |
| K-09(F105) | 密钥治理 | — | 全链 | src/zephyr/shared/security/secrets.py:184(get_secret_fail_closed)/:168(is_secret_shaped_key)/:100(rotation) | 全链密钥调用 | 事件（调用时三 gate） | 在用 | 挖干→挖干（信任绑定待裁注记维持） |
| K-10(F106) | 术语三层翻译体系 | 模块册 | 生成器 | docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml（module_id 字样 1049 处实测） | 三层 loader/生成器 i18n | 机生+gate | 在用 | 挖干→挖干（条数三口径 7686/7776/1049-grep 漂移已在骨架 §4-5 登记，禁散文写死） |
| K-11(F107) | 回滚恢复 | F84 | 全链 | src/zephyr/infrastructure/rollback/（auto_rollback_trigger/checkpoint_gc/cascade_failure_simulator/_manifest/agent_cooldown/budget_tracker…，8+ 件实测） | 故障恢复 | 事件 | 事件态（无常驻任务，合理） | 挖干→挖干 |
| K-12(F108) | 人机门位 | REG-RISK-TIER-001 | 全链门位 | docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml（tier/human_gate 字样 46 处实测） | 四类 Owner 门 | 事件（high 域拦截） | 在用 | 挖干→挖干 |
| K-13(F109) | 注册表族治理 | 全注册表 | 全链 | docs/registry_of_registries.yaml（:926 total_registries=**76**；"registry_id"字样 83 处粗 grep 含引用） | ROOR 发现入口 | 定时（一致性审计） | 在用 | 挖干→挖干（76/77 漂移已在骨架 §4-3 登记，本轮粗计 83 系含引用非纯条目，禁混写） |
| K-14(F110) | 契约冻结与错误码 | — | 全链 | src/zephyr/shared/contracts/freeze_manifest.yaml（397 行，contract_id **38 条**实测，骨架口径吻合） | 全链契约引用 | 静态册+gate | 在用 | 挖干→挖干 |
| K-15(F124) | 状态词表册生命周期 | GATE-VOCAB | K 段 | **册已建成**：docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml（634 行，status: active，registry_id REG-STATE-VOCAB-001，created_by_lane W3-E st-ailayer-final-20260924，ruling_basis 裁定#398/#399）；执法门=commit_gates/library/state_vocab_registry_gate.py:8（**warn-only**，STATE_VOCAB_GATE_MODE） | 词表 SSOT 执行 | gate 在拦（warn） | 观察期在岗 | 盲区(P0)→**登记面建成（翻案）**——详见 F124.md |
| K-16(F128) | data_security 数据安全 | K 段 | A 段数据面 | src/zephyr/data_security/ 实测 12 py=实件 5（ai_masking_pipeline/data_access_auditor/data_masking_engine + wiring/{audit_sink,data_exit_guard,lsg_masking_front}）+空包 7 | LSG 消费面 grep 含 data_security 域（lsg_masking_front 接线线索） | 未挖 | 部分接线线索 | 盲区(P1)→盲区收窄——详见 F128.md |

（F125 data_governance=A/K 交界，骨架计 A 段档，本档不重挖。）

## §V 红线 V1-V5 交叉核定（任务书第 3 条）

| 红线 | 全景指控 | 归属环节 | 本轮代码级交叉证据 | 自动化态标注 | 处置 |
|------|----------|----------|--------------------|--------------|------|
| V1 MetaqAuditReconcile | 计划任务 Daily 03:50 驱动 reconcile 语义件，违 §9.3 | **K-06（行政面）+ K-05（裁定面）+ I-01（任务载体）** | scripts/register_metaq_audit_reconcile_task.ps1:16 自辩"this is an audit scan, NOT a reconciler (precedent: ruling for ZephyrAlpha_GateFullTreeAudit)"；**同文件 :25 又自称 "reconciler is read-only end to end"——自辩自相矛盾**；对账件 scripts/governance/check_meta_question_audit_reconcile.py:18 明写"审计双轨对账（PG 审计表 vs JSONL）" | 定时（Daily 03:50 计划任务，Ready） | **Owner 裁定二选一**：①依 GateFullTreeAudit 先例正式豁免登记（消 V1）；②改事件触发（审计写入钩子）。禁维持"无豁免的在跑违规" |
| V2 c10 keeper ×4 | bash while-true sleep 25 伪造活性 | **K-08**（register 活性面） | 攻击面=session_concurrency.py:520 register 每调用无条件 `last_activity=time.time()`，无频率护栏 | 进程级违规在跑（PID 3788/18848/21020/31196，全景 §2.2 建议杀） | 撤 keeper；走 heartbeat_daemon 官方通道 |
| V3 chief7 session_keepalive.ps1 | Start-Sleep 60×8h sleep-loop | **K-08** | 件在=.runtime/tmp/st-chief7-20260928/session_keepalive.ps1（523B，10-01 09:29 ls 实证）；调用面=session_worktree_start | 进程级违规在跑（PID 31236，8h 到 17:29 自灭） | 撤或改事件续期 |
| V4 heartbeat_daemon idle 自退失效 | 7 实例超 1800s 仍跑 | **K-08 + heartbeat_daemon**（src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py） | 自退机制在码：:106-115（_MAX_IDLE_SECONDS 与 session_concurrency 同源 1800）/:317-344(_session_idle_seconds)/:387(run_daemon)/:406(退出条件 5b)；**失效根因=两条豁免通道**：:9 MODIFY-GUARD 明记"W-29 logical 豁免 + C355 队列等待双豁免"（st-circ-g2 全景 §2.1 正是 logical=True），叠加同会话多实例互不知晓（w3h ×3） | 常驻（设计内）但豁免通道被滥用 | 杀僵尸实例（全景 §2.2 名单）+豁免通道审计化（logical 授予留痕） |
| V5 活性真源失真 | 9/10 会话活性不可信 | **K-08** | 同 V2 攻击面：register()/claim 外无第三刷新源；heartbeat 有意不刷 last_activity（:8 invariants、:243-244 注记）=设计正确，被 keeper 借 register 旁路 | 活性锚点失真在案 | 收敛 keeper 通道到 heartbeat_daemon 单一机制+register 频率护栏（同 sid 高频 register 不刷活性） |

> V2/V3/V5 处方落在 K-08 一个点：`register()` 增加调用方频率护栏即可同时封堵两类伪造——这是本轮交叉核定后收敛出的最小施工面。

## 段内小结

- 环节 16：挖干 14 + 翻案 1（F124 登记面建成，剩 warn→block Owner 门）+ 盲区收窄 1（F128）。
- V1-V5 全部落位：V1=K-05/K-06/I-01 三环节交叉；V2/V3/V4/V5=K-08 单点收敛。
- 新口径漂移登记：K-02 门数（91→181 gate_id/143 own_scope）、K-13（76/77/83 三读数）、K-03 双 watchdog 未证。
