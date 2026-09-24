---
ttl: task_bound
title: QCure作业簿·gate_chain
session: st-qcure-20260925
---
# gate_chain 作业簿
## 1 环节定义与边界
GitCommitGateway 提交面门禁全链：装载（gate_auto_registrar fail-closed）→ 调度（CommitGateRegistry.check_all：priority/files_trigger/缓存）→ 双轨执行（in-process gate + pre-commit hook 通道 GATE-PRECOMMIT-RUN）→ 锁外预检复用面（commit_preflight 白名单+内联适配）。边界：不含 landing 侧失败转死信的编排（landing 环节）、含 M5.2 改判影响评估。
## 2 六向台账
### ①上游输入
- 装载：GitCommitGateway.__init__ → auto_register_gates(self._gate_registry, roster_root)（src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1013）；roster=in_process_gate_registry.yaml（gate_auto_registrar.py:87 REGISTRY_REL_PATH）。
- 调度：gateway.commit(files,…,allow_* 旗组) → check_all（landing 调用点 LAND:1745）；files_trigger 由 auto_register_gates 从 YAML 注入 spec.files_trigger（gate_auto_registrar.py:221-223）。
- 预检：run_preflight(gateway,files,session_id,commit_message)（commit_preflight.py:411-495），白名单 PREFLIGHT_GATES:106-148+内联适配 _INLINE_PREFLIGHT_CHECKS:156,299-305。
### ②下游消费
- GateResult 非 OK → COMMIT_FAILED → landing 死信 "网关落盘失败（status）"（LAND:1878-1887）。
- 观测：.runtime/audit/gate_execution_stats.jsonl（n_specs/failed/reused/ms，commit_gate_registry.py:93-117）；.runtime/gate_audit/allow_overlap_usage.jsonl:140；preflight 审计 jsonl（PF:_write_audit）。
- 对账/漂移：make_in_process_gate_registry_drift_reconciler（src/zephyr/governance/audit/reconciliation_registry.py:8952，priority 831，warn-only，触发=册/gates/*.py）。
### ③机制现状（业界参照）
- 门禁前移=GitLab merged results pipelines / merge train（https://docs.gitlab.com/ee/ci/pipelines/merged_results_pipelines.html ）、GitHub merge queue（https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-merge-queue ）；写后读回校验=rsync --checksum（https://download.samba.org/pub/rsync/rsync.html ）。本仓 PF"预检=提前失败不是豁免"与 merge train 的"合并态模拟预演"同构。
- check_all 七段流水（commit_gate_registry.py:392-492）：files_trigger 短路:432（_files_trigger_hit:280-294=目录前缀/fnmatch/**子串**）→ skip_gates:442 → 结果缓存:418-429,452-464（gate_cache_preflight 白名单+own_scope_hash，只缓存 passed:489-490，flag 出厂 OFF）→ preflight_results 复用:465-472 → 现算:473-488（单 gate 异常 fail-closed passed=False:477-487，永不抛）。register 幂等+同 priority 异 gate_id 阻断 GateRegistrationError:369-390。
### ④代码面（实现/测试/调用方全集）
- 两册关系：in_process_gate_registry.yaml（total_gates:102，册头:40，条目 102 实测；注册真源，enabled 字段，files_trigger 为 st-gslim-20260923 P5 注释）vs gate_registry.yaml（total_gates:180，PS-REG-014，机生=generate_gate_registry.py，generated_at 2026-09-24，source=.pre-commit-config.yaml+commit_gates/*.py+MANUAL_GATES）——前者=in-process 注册面，后者=全渠道登记清单；Phase 6 计划并册（in_process 册头注）。漂移防护三道：auto_register 对账 fail-closed（gate_auto_registrar.py:237-259 条数↔total_gates/去重 id↔注册集）+ drift reconciler（warn）+ tests/governance/generators/test_check_gate_inventory_drift.py。
- fail-closed 精确路径（M5.2 对象）：任一 enabled gate 失败（YAML 损坏 _read_roster:97-123 / import:207-208 / factory:214-215 / register:226-227）逐台收集→统一抛 GateAutoRegistrationError:230-235；对账不一致同抛:256-259；名册缺失=0 门 warn 合法:169-175。上游包裹：landing __call__ LAND:1690-1698 → cq.LandingEnvironmentError → drain env 分支退 pending 不死信（CQ:1285-1296）；pool 同款 LAND:2411-2421。**现行代码已无 autoreg 死信出口**；实测 19 笔死因="landing 异常: LandingEnvironmentError: landing 环境不可用…GateAutoRegistrationError…"（dead/q-20260923-st-combine-20260923-0001.json:78，pool env 分支落地前旧路径）。
- GATE-PRECOMMIT-RUN 双轨：_run_precommit_channel（git_commit_gateway.py:3232-3500）flag 裁定#341（_precommit_run_enabled:413-425，flag 故障 fail-open OFF）；SKIP hooks=gate-commit-gw,gate-worktree-required,gate-protected-paths（:401-407，后者 09-24 四死信实证消息盲冤杀）；own-scope 临时索引 GIT_INDEX_FILE（:50,3298）；hook 改文件重跑仍变→阻断:3452；merge 跳过:3252。PRECOMMIT-HOOK 49 笔死信多为此通道检出冲突标记（真病灶=字节污染，M2.2 预扫）。
- 三门输入面：CREATE-GUARD=create_guard.py make_create_guard priority=60，staged diff-filter=A fail-closed（_get_staged_new_files），链=_run_file_registration_checks:831-858，registry_data 注入点=_check_creation_token:703-718（L856 传参处）；适配器 _check_inline_create_guard（PF:202-245）读**入队 worktree 盘面册**=会话口径（M2.1 缺口根因）。TRANSLATION-COVERAGE=translation_coverage_gate.py：git diff --cached --diff-filter=A:155，loader 不可达 fail-open:204，own 化 _split_own_foreign，未进预检白名单（PF:147"挂起待复测"=M2.3 面）。GATE-VOCAB=vocab_hardcode_gate.py make_gate_vocab_gate priority=80：staged 新增 .py，subprocess check_vocab_hardcode.py --files --ci（exit1 阻断/exit2 fail-open），own 化。
- 测试：tests/governance/rule_bridge/test_commit_gate_registry.py（19）、test_gate_auto_registrar.py（26）、test_commit_preflight.py（9）+test_commit_preflight_mass_deletion_message.py；tests/governance/commit_gates/test_create_guard.py（blocks_unregistered_new_py/registry_missing_blocks/registry_parse_error_blocks 等 12+）、test_translation_coverage_gate.py（src_zephyr_in_scope/scripts_tests_exempt 等）、test_p4_merged_gates.py（GATE-VOCAB 参数化:19）；跑法 `python -m pytest tests/governance/rule_bridge/test_gate_auto_registrar.py tests/governance/commit_gates/test_p4_merged_gates.py -x`。
### ⑤运维/呈现面
- gate_execution_stats.jsonl 复用态三值（ran/skipped/trigger_skip/cache_hit/preflight_reused）；ZEPHYR_PRECOMMIT_FAST_SUBSET（gateway:395-400）；flags.yaml 控缓存与 precommit；emergency_commit=裁定#351 唯一逃生；daemon 纪元吃启动代码——gate/装载逻辑改动须换血（DAEMON L643-713）。
### ⑥失败态与数据面
- GateAutoRegistrationError 五类成因：roster 损坏/空册:177-180/import 失败/factory 缺失/register 失败（含 priority 撞号 GateRegistrationError commit_gate_registry.py:309-322）/对账 mismatch。前两类可能瞬态（IO/纪元），后三类是确定性内容 bug。
## 3 缺陷与矿脉清单
已知→QCure 映射：M5.2（LANDING-ENV 19）、M2.1（CREATE-GUARD registry_data 注入点已存在）、M2.3（TRANSLATION 未进白名单）、M2.4（GATE-VOCAB）。
新矿脉：
1. **M5.2 改判已半落地，残余=活锁**：死信→env 退 pending 现行代码已闭环（见④），但 env abort 置 env_aborted 终止整轮（LAND:2414-2420）且无 per-item 重试计数——若 HEAD 上 gate 册真坏，每轮首项 abort、项无限回 pending、全队停摆，故障域从 1 项扩大到全队，比死信更糟。判别建议：异常时**子进程 fresh import 重跑 auto_register_gates**——fresh 同败=确定性 bug（坏 YAML/坏条目/撞号）应升级死信；fresh 成功=daemon 旧纪元/瞬态 IO，退 pending 合法（等 re-exec 自愈）。辅判：import failed 且模块不在 HEAD ls-tree=真 bug。必须配"有限次数后升级"。
2. files_trigger YAML 注入无 schema 校验（gate_auto_registrar.py:221-223 直接覆写 spec.files_trigger）且 _files_trigger_hit 子串语义（commit_gate_registry.py:292 `p in rel`）使 ".py" 命中一切含该串路径——册侧笔误即可静默扩/缩触发面，无 gate 把守（建议：generator 校验或并入对账）。
3. preflight 与落地口径分歧是 CREATE-GUARD 27+36 笔死因根（PF:202-245 读盘面册 vs 落地读 serializer HEAD 册）；M2.1 修复后 TRANSLATION-COVERAGE 可同模式复制（loader 读盘面 module_translation_registry vs 落地 HEAD 册——同构分歧待 M2.3 输入面审计确认）。
4. priority 唯一性阻断（:369-390）在 register 阶段才炸=全链冻结；可在预检/生成器侧对 in_process 册做 priority 预检前移（对齐 M1 思路，净零：复用 gate_registry 生成器）。
5. is_test_exempt 段匹配升级（commit_gate_registry.py:180-204 治本4）扩大三门豁免面（scripts/tests/ 等），是 golden hash 保护的高价值篡改目标——改动须过 RULES_MANIFEST C 层。
6. check_all 缓存白名单 CONTENT_SCAN_CACHE_WHITELIST flag 出厂 OFF（:415-429），开启后只缓存 own-scope 纯内容扫描门——QCure 预检扩容若误入非 own-scope 门会假阳性，准入铁律仍在 PF 逐 gate 输入面审计。
## 4 自审闸三态裁定
施工——M5.2 按"fresh 子进程判别+计数升级"补齐（改判本身对瞬态类正确，对确定 bug 类需防活锁）；M2.1/M2.3 适配面注入点现成；两册漂移已有三道防线，不新增。
## 5 长尾清单
- in_process 册 Phase 6 并入 gate_registry.yaml（机生化后可消 total_gates 手工对账面）。
- files_trigger schema/触发面校验 gate（P2）。
- priority 撞号前移检测（P2）。
- gate_cache_preflight 白名单开启评估（flag 出厂 OFF，待 perf 班）。
- preflight 白名单继续扩容前逐 gate 输入面审计（PF 在案铁律）。
- daemon 纪元与 gate 代码发布时序文档化（运维红线 9.3 事件触发约束下的换血规程）。
