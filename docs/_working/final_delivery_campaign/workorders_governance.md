---
ttl: task_bound
title: "终局交付战役·分诊矿道 M2——治理门禁 33 卡六态工作单（❌17+🔶16）"
session: st-finaldel-m2-20260929
---

# 治理门禁 33 卡六态工作单（M2 分诊矿道）

> 审计窗：2026-09-29（清单=桌面《未完成任务施工清单_2026-09-29.md》第三章"治理门禁 17 条"+第四章"治理门禁 16 条"）。
> 落地判据=HEAD（git ls-tree/show/grep HEAD），非工作树。会话=st-finaldel-m2-20260929。
> 六态：READY（可施工）/ DONE_BY_SIBLING（他会话已修，附 hash）/ SUPERSEDED / CONFLICT_INFLIGHT（他会话在飞，defer）/ OWNER_GATE / BLOCKED。
> 自开工授权边界：docs/_working/ 或 tests/ 新文件、或单文件小修且 git status 干净；热注册表一律 defer。

## 〇、特别核验四雷（总筹点名）

| 雷 | 现状判读 | 证据 |
|---|---|---|
| C09 candidate 册撞号双条 | **仍在 HEAD，未修**：`CAND-GOVTEST-005` 双条（L7707 队列 MVP 条目 + L20231 测试身份泄漏条目），007 重编号未落；工作树同值且该册 M 脏=他会话在飞 | `git show HEAD:...candidate_module_registry.yaml \| grep -n CAND-GOVTEST` |
| 红五簇 GateSpec priority 撞号 | **已由他会话修复落 HEAD**：98ce6370c5（st-nightsweep-sw12，2026-09-29）"红五簇撞号修复（实为六簇）"——6 个 legacy 单门工厂迁 152-157 空带（含 79 簇 BLUEPRINT-AMODULE-CONSISTENCY→153 让位先例），新增全册唯一性机械校验 TestWholeBookPriorityUniqueness，修后 134 passed+in_process 名册装载零撞号。**4 台 disabled 遮蔽现状**：CAPABILITY-OVERLAP/GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER/ALGO-FLOW-LINK 在 in_process_gate_registry.yaml 仍 `enabled: false`（临时禁用 Owner B 方案）——撞号病灶已除，翻 enabled 技术阻力已消，但翻转本身=Owner 门位（W-114） | commit 98ce6370c5；in_process_gate_registry.yaml 各条 `enabled: false` 注释 |
| P3 链 ORPHAN↔IMPORT 互锁（C14） | **前置已消失**：卡面称"处方只在盘面编排册 §十、HEAD 止于 §九"——实测 HEAD 的 fullflow_mining/00_orchestration.md 已有 `## 十、P3 链最后一关（ORPHAN↔IMPORT 循环互锁）——下一棒处方`（三选一处方全文在 HEAD）；但落地判据 `_MIN_DYNAMIC_GATES` 全仓 git grep 仍 0 命中=互锁本体未施工 | `git show HEAD:docs/_working/fullflow_mining/00_orchestration.md` L94+；`git grep _MIN_DYNAMIC_GATES HEAD`=空 |
| T14 五件重投（C15） | **车道在、件未投**：.worktrees/csx-t14b 存活，车道内 `t14_roster_report.md/.yaml`、`reconcile_gate_rosters.py` 均为 untracked 未投态；d3_metadata 其余件已在 HEAD。换新袋号重投即过（belt 缓存窗口病已被包 8 换血治愈） | `git -C .worktrees/csx-t14b status --porcelain` |

## 一、❌未完成·治理门禁（17 卡）

| 卡号 | 六态 | 证据（HEAD 实测） | 关键文件 | 处方（可施工级） | 预估 | 依赖 |
|---|---|---|---|---|---|---|
| C09 | CONFLICT_INFLIGHT | HEAD 双 `CAND-GOVTEST-005`（L7707/L20231）仍在；007 重编号未落；册 M 脏=他会话在飞 | docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml | 热册 defer 总筹：等在飞袋落地后复验；重编号件沿 W-133（candidate 007 与 5 处引用件同袋序，X-47）走 gateway 直连小袋，safe_write_text CAS+写后核实 | S（半小时级，含 5 处引用件 grep） | 在飞袋落地窗；W-133 袋序约束 |
| C25 | OWNER_GATE | `--update-entry-counts`/`update_entry_counts` 在 check_registry_consistency.py@HEAD 0 命中；文件干净 | scripts/governance/generators/check_registry_consistency.py | 卡面明说"Owner 批后"：批文下来按 S4 §4 B10-1 处方给既有 reconciler 挂 `--update-entry-counts` 触发（1 处接线） | S | Owner 批文（S4 §4 B10-1） |
| C88 | DONE_BY_SIBLING | **48aa677f7f**（2026-09-29，st-nightsweep-sw2）"E12 W-29 心跳守护修复"：SessionRegistry 新增 logical 标志+register(logical=)+mark_logical()；heartbeat_daemon idle 超限分支加 logical 豁免（keepalive=logical_session）；test_heartbeat_daemon 49 passed | src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py | 无余量；长会话接入面（opt-in 调 mark_logical）随各班自然采纳 | — | — |
| C97 | READY | `read_side_fms_hygiene_gate.yaml` 在 HEAD 树 0 命中（不存在），3 处 `[ALGO_FLOW] external` 锚仍指向它（read_side/__init__.py:26、fms_hygiene_gate.py:60、generate_fms_deadref_baseline.py:45） | src/zephyr/gov_enforcement/commit_gates/read_side/；docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/r/ | 按 LEDGER_chief3 §6.4 复跑命令清点 9 枚悬空全集→逐枚"补册（建锚 yaml，token 先行）或改指（删/换锚行）"；与 ALGO-FLOW-LINK 门 own-diff 判据联动 | M | LEDGER §6.4 清单核对；若建 yaml 需 creation token |
| C98 | OWNER_GATE | LEDGER_chief3 §6.4 N-3 在 HEAD（L119）：≥8 台 files_trigger 超宽（1,354-8,937 文件≥阈值 1000），例 REFERENCE-INTEGRITY 'docs/'、STATE-VOCAB-REGISTRY '.py'；gate_auto_registrar 每 commit 实况告警同证 | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | 收窄触发面/降级按需=注册表净删面→Owner 门位；AI 可先出超宽台账（generator 产出口径）供裁 | M（台账）+Owner | Owner 裁定收窄口径 |
| X01 | CONFLICT_INFLIGHT | 立案目标 architecture_issue_registry.yaml 现 MM 脏（他会话在飞）；creation_token 三方口径矛盾（预检索 .md token/工具回"已登记"/--wide-prefix 拒写）无回修记录；本会话实测 batch_creation_tokens.py 另现"陈旧整文件快照压盘"新病（写前自检拒写，capability 册缺 7 条基底） | docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | defer：等在飞袋落地后按 I2-06 原案立案进 architecture_issue_registry（含本次新发现的 stale-snapshot 病实证） | S | 在飞窗解除 |
| C157 | READY | `_timed_phase` 在 src/zephyr/gov_enforcement@HEAD 0 命中 | 门禁链装载面（gate_engine） | 按 qmine 05_observability/workbook.md 方案①：门禁链补 _timed_phase 相→重测残差（观测埋点，非执法变更） | M | workbook 方案①在册 |
| C217 | READY | `GATE-SELFDOC` 在 detect_git_dangerous.py@HEAD 0 命中；字节在 5 个死袋（q-20260928/29-st-chief7-20260928-0135/0213/0293/0069/0369 均含 detect_git_dangerous）+.aidrafts/st-chief7-20260928 车道 | scripts/governance/d6_security/detect_git_dangerous.py | 按死信新规捞袋：读 dead json 死因→修基底→换新袋号 enqueue（同 C02 分批小步≤10 封纪律）；禁盲 requeue | S-M | C02 死信终局处置流程 |
| C244 | READY（热册 defer 执行） | W-170 在 ruling_registry@HEAD 0 命中 | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 波 5 域按 RULE-RULING 登记：`next_ruling_id.py` 现取号（禁自赋#377）→登记同 commit 原子；热册走总筹单写者窗 | S | 热册空窗；取号器 |
| C245 | READY | wave7/ 在 HEAD 仅 index.md+redblue_rescued_findings；W-171 全量复跑记录 0 命中 | docs/_working/total_command_closeout/wave7/；scripts/governance/d5_architecture/generators/align_all.py | ①先定性 PG 配置缺口（产出 wave7/pg_gap_定性件）②align_all 全量实跑复验③复裁结论回写 wave7/index.md | M | PG 配置定性结论 |
| C263 | READY（**本会话已自开工**） | 测试件 untracked（`??`），impl 026fd1fbea 已是 HEAD ancestor；本地实跑 8 passed in 0.27s | tests/governance/rule_bridge/test_commit_preflight_registry_cache.py | 已按窄袋入队 q-20260929-st-finaldel-m2-20260929-0003（与 impl 同批原则收编） | 已干 | — |
| C308 | READY（**本会话已自开工**） | HEAD 台账止于 §10（413 行）；§11/12/13+S-27/S-28 块共 105 行只在 .aidrafts/st-audit-fix-20260924；草稿前 413 行与 HEAD 逐行全等已验 | docs/_working/audit_fix/audit_fix_ledger.md | 已按 safe_write_text CAS 整段追加（413→518 行）并入队 q-…-0002 | 已干 | — |
| C323 | BLOCKED | "L3 勘误"在 docs@HEAD 全文 0 命中——勘误裁定原文未入库（源=#指令.txt 桌面件 L718 块 F 总包第四棒） | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 先向移交方/桌面源件取 L3 勘误原文→再 RULE-RULING 取号登记（同 commit 原子） | S（拿到原文后） | **L3 勘误原文**（未入库） |
| C336 | READY | generate_connection_matrix.py 在 .worktrees/st-zmaster2-20260926 车道在（字节在）；HEAD 0 命中；capability 册条目已在 HEAD（L53329，capability=generate_connection_matrix） | scripts/governance/d5_architecture/generators/generate_connection_matrix.py + connection_matrix.csv | 从车道取件重审基底→B 袋配方落地生成器+机生 CSV（禁手维护清单）；落地后核册路径==实际路径+module translation 登记+depgraph | M | st-zmaster2 车道字节重审 |
| C409 | READY | RULING-REFERENCE 在 gate_registry/capability 册/ruling_registry 有声明，但 in_process_gate_registry 无条目、src 无 gate 实现=「声明在册无人装载」证实（空转） | docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml vs gate_registry.yaml | 跑 G-81 尺（92_acceptance_rulers.md）取差集→15 门逐个定性（该装载的装载/该退役的走退役三段式）；定性表产 docs/_working | M | 退役面=Owner 门 |
| C421 | READY（热册 defer 执行） | ruling_registry 尾部现至 #390+；W-56 空洞号 vs 工作树自赋号扫描无在册产物 | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 扫描册内空洞号与工作树自赋号→逐条消雷或登记豁免；热册走总筹窗 | M | 热册空窗 |
| C476 | CONFLICT_INFLIGHT | module_translation_registry.yaml M 脏（他会话在飞）；卡面明说 st-p1b 属主、他道在途不代修 | docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | defer：st-p1b 属主跑 `--dedupe` 清源（registry_ledger 族 2 组重复 module_path） | S | st-p1b 属主窗 |

## 二、🔶部分完成·治理门禁（16 卡）

| 卡号 | 六态 | 证据（HEAD 实测） | 关键文件 | 处方（可施工级） | 预估 | 依赖 |
|---|---|---|---|---|---|---|
| C13 | READY（**本会话已自开工**） | AGENTS.md@HEAD 三处旧值（L104 队列 4 op/L109 集成器 7 子命令/L110 仪表盘 app_panel）；git status 干净（盘面 MM 态已灭失）；批文=#ARCH-AGENTS-SSOT-DRIFT-001 在册（architecture_issue_registry L22528，in_progress）；实测 commit_queue.py 6 add_parser（含 cleanup/health）、zephyr.data 8 子命令、api_server.py 在 HEAD | AGENTS.md | 已按金哈希规程落盘（safe_write_text CAS+行数守恒）并入队 q-…-0001，commit msg 挂 [ARCH-APPROVAL:#ARCH-AGENTS-SSOT-DRIFT-001]（PROTECTED-PATHS 逃生，C44/1cf01067f53 先例同款） | 已干 | — |
| C27 | OWNER_GATE | 判据改写**已由他会话落 HEAD**：984c1787f8（st-nightsweep-sw6）FMS-HYGIENE 翻 block 判据改写=棘轮本征判据（连零 20 笔机读 fms_hygiene.jsonl，BLOCK_FLIP_CLEAN_STREAK=20），35 passed；mode 仍 warn——翻 block=OWNER-GATE 卡面明示 | src/zephyr/gov_enforcement/commit_gates/read_side/fms_hygiene_gate.py | Owner 门位：判据达成（连零 20 笔）后一行翻转 mode；存量清偿看板独立推进 | S（翻转本身） | Owner 门位+连零计数达成 |
| C41 | READY | W140_f62_wiring_table.md+checklist_evidence.py 均在 HEAD | docs/_working/qoder_legacy_closeout/W140_f62_wiring_table.md；src/zephyr/compliance/ | 模拟侧余闸对照 12 行表逐行补齐（SettlementReconciler 周时钟违宪整改/F34 DDL/退役批零 commit）；实盘腿绑 TRD-A10=Owner 等待 | L | 实盘腿=Owner |
| C44 | DONE_BY_SIBLING | **1cf01067f53**（2026-09-29，st-zc9-lane-a）"件1·trae_034 死指针修复"：三处死库指针→data/databases/governance.db（行 40/212/560），PROTECTED-PATHS 通道 [ARCH-APPROVAL:#ARCH-361] Owner 批文③；修复前两红→6 passed；HEAD 实读三处已指 governance.db | docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml | 无余量（本卡面）；零字节库家族 5 库=S-02/03 另案（wave1a/store_liveness_census.md 在 HEAD） | — | — |
| C48 | READY | 10_wave_plan.md §波9 在 HEAD（L136-154）：W-152..W-162 十三项带验收判据 | docs/_working/total_command_closeout/10_wave_plan.md | 按 §9 表逐项销账（W-152 HMAC 立项文档优先）；注意分流：W-153=C16、W-154=C336、W-162⊃C13（本会话已干） | L（批量） | 各子项独立 |
| C115 | OWNER_GATE | wave5/registry_derivation_report.md 在 HEAD；SKIP-6 自动发现器已治 total_gates 一项 | docs/01_policies_and_standards/_registry/ 各册+yaml_utils.py | 8 条错配列 Owner 裁定（卡面明示）；按 report 改生成器部分=AI 余量，涉 ROOR 族走总筹 | M+Owner | Owner 裁定 8 错配 |
| C163 | OWNER_GATE | ROOR@HEAD 头部已含 `front_door: docs/library/FRONT_DOOR.md` 指针（FRONT_DOOR.md+generate_front_door.py 均在 HEAD），但头部散文未切；ROOR=human_gated | docs/registry_of_registries.yaml | 走 Owner 通道按 S4 §2.4/B5-1 规格删头部散文换 FRONT_DOOR 指针 | S | Owner 门位（human_gated） |
| C268 | READY | P2-24..28 三件套（tests 写权限分离/断言 diff 复审门/held-out 复跑）在 HEAD 无落地痕迹 | tests/（新件）+ruling_registry（预登记，热册） | 三件套立项施工（tests/ 新文件可先行）；晋升门判据预登记进 ruling_registry=热册归总筹 | L | 预登记部分=热册窗 |
| C311 | READY | 96_final_report_wave2.md §七已被 SW11 回填（2026-09-29，qid↔commit 映射+死袋+直连实录在 HEAD），但「两轮循环检查读数」复选框未勾（"队列实录不可推，待原会话口径"） | docs/_working/fullflow_mining/96_final_report_wave2.md | 落地面复跑两轮→回填 §七末格（红蓝完整轮次+落地面两轮一致） | M-L | 原会话口径或实跑两轮 |
| C322 | READY | 99_pending_owner.md 在 HEAD 但乙-1..乙-9 补裁回写 0 命中 | docs/_working/map_build/99_pending_owner.md | 接手班按 03_final_blueprint 逐条补裁并回写裁决卷（总包自裁权限域） | M | 总包班接手 |
| C346 | READY（收编半场已由兄弟落） | 收编进 CREATE-GUARD **已落 HEAD**：be62505961（st-zcloseout B2 件①）create_guard 查重批量化+逐探针 CapabilityLookup.find+create-guard-not-dup 豁免标记；CAPABILITY-OVERLAP 本体仍 enabled:false；"已被取代"注释未带；禁用期回溯核查无产物 | src/zephyr/gov_enforcement/commit_gates/create_guard.py | ①补一次只读回溯核查（禁用窗内新建 .py 有无漏判重）产出案卷入 docs/_working ②注释随下次合法触碰带上 | M | — |
| C420 | READY（并 C409 族） | next_ruling_id.py 在 HEAD（blob ba421c4e）；RULING-REFERENCE 空转证据同 C409 | scripts/governance/next_ruling_id.py | 与 I24 合并施工：装载（取号器执法接进 RULING-REFERENCE 门）或退役；定性归 C409 差集表 | M | C409 定性结论 |
| C427 | OWNER_GATE | in_process_gate_registry@HEAD：4 台（CAPABILITY-OVERLAP/GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER/ALGO-FLOW-LINK）仍 `enabled: false`（临时禁用 Owner B 方案）；红五簇修复后技术阻力已消（98ce6370c5）；对账生成器不在 HEAD | docs/_working/total_command_closeout/wave1a/enforcement_surface_reconciliation.yaml | 恢复/退役 4 台=Owner 定（⚑-6-3）；常设对账生成器 AI 可施工（wave1a 车道字节→HEAD，机生禁手工） | M（生成器）+Owner | Owner 门位 |
| C428 | READY | wave1a 6 件文档全在 HEAD（delivery_cards_report/enforcement_surface_*/dead_store_triage/store_liveness_census/read_shape_violations） | docs/_working/total_command_closeout/wave1a/ | 把 wave1a 生成器/校验器从车道落 HEAD（enforcement_surface_reconcile 等 0 命中）+补 1A.3-1A.6 四包（97 册 Top 优先序） | L | 车道字节定位 |
| C443 | READY | 02_field_corrections_and_new_cases.md L87 骨架行在 HEAD（W-133..W-136 定义齐全） | docs/_working/total_command_closeout/02_field_corrections_and_new_cases.md | 逐件补：W-133=C09（defer 在飞）、W-136=C444（提交链卡）；W-134/W-135 按号文施工 | M | W-133/W-136 各归其卡 |
| C451 | READY | enforcement_surface_tables.md 在 HEAD；生成器（enforcement_surface_reconcile）在 scripts@HEAD 0 命中 | scripts/governance/（新生成器） | 落生成器进 HEAD（机生禁手工）：从 wave1a 车道取字节或按 tables.md 反推重写+登记 | M | 车道字节定位 |

## 三、统计（六态计数）

| 六态 | 计数 | 卡号 |
|---|---|---|
| READY | **21** | ❌：C97 C157 C217 C244 C245 C263◆ C308◆ C336 C409 C421（10）｜🔶：C13◆ C41 C48 C268 C311 C322 C346 C420 C428 C443 C451（11） |
| DONE_BY_SIBLING | **2**（另特别核验 C57 计 1） | C88=48aa677f7f、C44=1cf01067f53（+C57=98ce6370c5） |
| CONFLICT_INFLIGHT | **3** | C09、X01、C476 |
| OWNER_GATE | **6** | C25、C98、C27、C115、C163、C427 |
| BLOCKED | **1** | C323（依赖=L3 勘误原文未入库） |
| SUPERSEDED | **0** | — |
| 合计 | 33 | ❌17+🔶16 |

## 四、本会话自开工成果（3 卡，均走队列正门）

| 卡 | 袋 qid | 内容 | 验证 |
|---|---|---|---|
| C13 | q-20260929-st-finaldel-m2-20260929-0001 | AGENTS.md 宪法 §7 三处漂移修正（批文 #ARCH-AGENTS-SSOT-DRIFT-001；[ARCH-APPROVAL] 标记过 PROTECTED-PATHS；safe_write_text CAS+行数守恒） | 写后进程外复核三行全中；直连两败于他会话外来 staged 违规（MUTABLE-CONST foreign indicator_usage_audit.py）改道队列 serializer |
| C308 | q-20260929-st-finaldel-m2-20260929-0002 | audit_fix_ledger.md §11-13+§10 尾 S-27/S-28 块补入（413→518 行，草稿前缀逐行全等已验） | grep §11/12/13 三节齐 |
| C263 | q-20260929-st-finaldel-m2-20260929-0003 | 孤儿测试收编（impl 026fd1fbea 已在 HEAD，测试件 untracked→窄袋） | pytest 8 passed in 0.27s |

> 三袋落地态以 `python scripts/commit_queue.py status --session st-finaldel-m2-20260929` 为准（入队时点 pending=传送带消化中）。

## 五、热注册表 defer 清单（给总筹）

- **C09**（candidate_module_registry.yaml，M 脏在飞+撞号双条未修）
- **C476**（module_translation_registry.yaml，M 脏在飞+registry_ledger 族重复）
- **C244/C421**（ruling_registry.yaml 登记面，需取号器+热册单写者窗）
- **C98/C427**（gate_registry/in_process 名册：收窄与翻 enabled 均 Owner 门位）
- **C163**（registry_of_registries.yaml human_gated 瘤切）
- **C115**（8 条派生错配列 Owner）
- **C323**（ruling_registry，且勘误原文未入库=BLOCKED）
- **X01**（architecture_issue_registry.yaml MM 脏在飞；另附新实证：capability 册盘面基底相对 HEAD 缺 7 条 token=陈旧快照病，batch_creation_tokens.py 写前自检拒写——与 I2-06 三方口径矛盾同案卷立案）
- **C268 晋升门预登记半场**（ruling_registry）
