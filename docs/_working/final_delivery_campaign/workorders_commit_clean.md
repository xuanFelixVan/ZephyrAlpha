---
ttl: task_bound
title: 终局交付战役·提交链(29卡)+清洁卫生(12卡) 分诊工作单（M3 矿道）
session: st-finaldel-m3-20260929
---

# workorders_commit_clean — 提交链+清洁卫生 41 卡分诊工作单

> 核验基线：HEAD `31c38c5205`（dev），核验窗 2026-09-29 13:0x-13:3x。
> 方法：清单《未完成任务施工清单_2026-09-29.md》三/四章提取提交链 ❌15+🔶14、清洁卫生 ❌10+🔶2 共 41 卡，逐卡按卡内复核命令对 HEAD 重验后判六态。
> 六态：READY / DONE_BY_SIBLING / SUPERSEDED / CONFLICT_INFLIGHT / OWNER_GATE / BLOCKED。
> 纪律：本单只盘点与登记；一切删除类动作（tmp/worktree/死信/blob gc）只列清单不执行，归总筹。

## 〇、时敏项实况（先看这里）

### 0.1 队列三袋核销现状（`python scripts/commit_queue.py status` @13:1x）

队列总览：pending=12 / processing=4 / done=823 / **dead=440**（总 1279）。pending 12 袋全是当晚活跃会话新袋（chieflease/boardidx/chief7-0453/0493/gpup1/matrix-revive6/nightclean/tailwork6/zcloseout×3），三袋目标均不在 pending。

| 袋 | 现状 | 死因/证据 | 字节落地抽查（bag blob_sha256 vs `git show HEAD:` sha256） |
|---|---|---|---|
| q-0213 = q-20260929-st-chief7-20260928-0213（40 件 RMCode 抢救袋） | **dead**（02:04 建，03:19 死） | 快照基底冲突：base `1dd6c70c74e9` 后 dev 推进触及 `AGENTS.md`、`src/zephyr/ai_layer/redline/negative_list_gates.py`，逐文件快进判定失败，死信回退属主会话 | 抽 5 件（archiver.py/deadman_switch.ps1/negative_list_gates.py/test_dead_letter_eviction_canary.py/detect_git_dangerous.py）：**5/5 在 HEAD 但内容≠袋字节**（袋字节完整保存在 `.runtime/commit_queue/blobs/` 可 from-bag 取回） |
| q-0167 = q-20260929-st-commitspeed-tbl-20260924-0167（红蓝报告 2 件） | **dead** | GATE-PRECOMMIT-RUN 拦截：`gate-detect-git-dangerous` 命中 redblue_robust.md:63 的 `git reset`+`--hard` 连写字面量（ABS-27 文档触发，非真实命令） | redblue_governance.md **LANDED-BYTE-EQUAL**（已落）；redblue_robust.md LANDED-DIFF-CONTENT（HEAD 版行 63-64 仍含同串，直接重投仍会被拦） |
| 107 件 fullconnect 战役文档袋（C40） | **已消化** | 盘面 `docs/_working/fullconnect_campaign` =159 件 = HEAD 159 件，staged-only=0；lane_t_notes.md/lane_q_notes.md 均@HEAD | 唯一例外：`docs/_working/wiring_gap_inventory_20260927.md` 盘面与 HEAD 与全仓 git 历史（--all）**三处皆无**（蒸发候选，见 §3 登记 R-1） |

### 0.2 死信终局处置 + blob 归档现状（C02/C11 关联）

- **dead_archive_final/ 已存在**（清单称"不存在"已过时）：`.runtime/commit_queue/dead_archive_final/` 内 **743 袋**归档；dead 活跃区余 **440 封**（1079→440，净消化 639+）。
- **blob 归档已动**：`.runtime/commit_queue/blobs_archive/` 已建；blobs 现 **18270 块**（清单 23217→净减 4947）。C11 的 --archive 已非"从未实弹"。
- 另在案归档目录：dead_archive_20260830/20260914_closeout/20260919_x1(x1b)/metaq_gc_20260926/ulib3_zombie/w8 等族。

### 0.3 心跳守护 W-29（C88 关联）：**已修（DONE_BY_SIBLING）**

`src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py@HEAD`（48aa677f7f，2026-09-29）已实现 `_session_is_logical()`（:258-273）：`SessionRegistry.logical=True` 逻辑长会话不再被 idle>1800s 判死，daemon 写 `alive(keepalive=logical)` 留痕后继续；非逻辑会话自退治本零回退。chief3 碰撞处方已在码。

### 0.4 .runtime/tmp 与 scratch worktrees 盘点（只盘不删）

- `.runtime/tmp/` 共 769 项，其中 `csx_*` **136 个**（与清单数一致，未清）。
- `.worktrees/` 共 **118 目录**，注册 worktree **181**（`git worktree list`，prunable=0），其中 `csx-*` **18 个**：b5,d4,m1c1b,m3c1,m5s1,m6c1,p13,p3b,pkg5,pkg5b,pkg7,pkg8,pkg9,replay,s1,t14b,w4,w4b。
- `.runtime/tmp/csx_t13_wt`、`csx_t14_wt` 两 scratch 工棚在。
- **取证保留件已消失**：T17 要求保留的 `.runtime/tmp/cs-tbl/` 与 `csx_t10_hook_timing.log` 均已不存在（谁删的待查，登记 R-2）。
- claims：`.ailocks/registry.json` 活跃锁仅当前在飞会话（nightclean/finaldel-m2/m4），csx 族锁=0，无 stale claim。

### 0.5 T17 清单四项现状（99_FINAL_REPORT.md:54-59）

| T17 项 | 现状 |
|---|---|
| tmp csx_* 清理（留 cs-tbl 取证） | 未清（136 个在）；且 cs-tbl/与 csx_t10_hook_timing.log 已消失（取证件反而不在，R-2） |
| scratch worktrees remove+prune | 未做（csx-s1/p3b/w4/d4/b5/p13/replay 等 18 个 csx-* 仍在 + csx_t13_wt/csx_t14_wt） |
| claim 释放 | **已达成**（活跃锁=在飞会话自有，无 csx stale claim） |
| 死信处置（呈批后） | 主体已做（743 袋归档，余 440）；"分批≤10 封"终局处置仍在途 |

## 一、提交链 ❌未完成（15 卡）

| 卡号 | 六态 | 证据（HEAD 实测） | 文件 | 处方 | 预估 | 依赖 |
|---|---|---|---|---|---|---|
| C02 死信终局处置 | DONE_BY_SIBLING（主体） | dead_archive_final/ 743 袋；dead 1079→440 | .runtime/commit_queue/{dead,dead_archive_final} | 残留 440 封按新规分批≤10 封续消化（复活→归档/废弃→终验/可回队→裁剪/需属主→代投）；含 st-cmd-20260924 115 封甄别 | 持续性 | 死信新规（已批）；blob gc 必须排在其后 |
| C04 S1 验收台账 | DONE_BY_SIBLING | 90_verification/s1_acceptance_20260929.md@HEAD：100/100 台双口径 verdict 全等、6000 行、selfcheck100 无回归；flags.yaml:52 immutable_tree=true | docs/_working/commit_speedup_campaign/90_verification/s1_acceptance_20260929.md | 无（已由 st-nightsweep-sw8 终验）；64s→<25s 实测数已在台账 | 0 | - |
| C05 R2 复测 | BLOCKED | .runtime/tmp 下 csx_deep_01..09 脚本**已消失**（被先行清理）；deep_dive_r1.md@HEAD | docs/_working/commit_speedup_campaign/60_deep_dive/deep_dive_r1.md | 先从 r1_data/*.yaml+r1 记录重建脚本集→重跑全集→落 DEEP_DIVE_R2.md 对照；无可回收>5min/天=达标 | 0.5 天 | 脚本集重建；R2→解锁 C147 |
| C14 P3 链 ORPHAN↔IMPORT 互锁 | READY（带前序） | `git grep _MIN_DYNAMIC_GATES HEAD`=0 命中（暗雷仍在）；处方只在盘面编排册 §十/§十三，HEAD 版止于 §九 | scripts/governance/meta/validate_rules_integrity.py；docs/_working/fullflow_mining/00_orchestration.md | ①先把盘面 §十三处方批落 HEAD（token 先行）②再按处方 2/3 拆包施工；落地判据=_MIN_DYNAMIC_GATES 进 HEAD | 0.5 天 | 前序=处方册落 HEAD（文档批） |
| C15 0139/T14 五件重投 | READY（涉热册→defer 施工） | .worktrees/csx-t14b 在：M 热册×3（capability/gate/module_translation）+?? reconcile_gate_rosters.py+t14_roster_report.md/.yaml | .worktrees/csx-t14b/scripts/governance/d3_metadata/ | 从 worktree 取件重审基底→换新袋号 enqueue；热册 hunk 需先对照 HEAD 剔除反向差异（X-02 教训） | 0.5 天 | 热注册表（本矿道 defer）；平静窗 |
| C16 红蓝场景⑦ | DONE_BY_SIBLING | tests/governance/red_blue_pkg14/test_rb14_s7_cross_lane.py@HEAD（8b6c351c58c，2026-09-26，包14 全 37 例绿含 S7 跨道连坐 own-scope，能红证据在册） | tests/governance/red_blue_pkg14/ | 无 | 0 | - |
| C30 域架构大文件入库 | READY | docs/02_enterprise_architecture/02_domain_architecture_docs 盘 **151 件** vs 整树 HEAD 53 件 | docs/02_enterprise_architecture/02_domain_architecture_docs/ | 按 S8 §⑤14 配方分袋入库（先核 I5 幻影区判据错案撤记录；大文件过容量门+LFS 评估）；袋≤38 件 | 1 天 | 容量门；D 盘 89% 高水位 |
| C143 CloneGuard 工厂化 | DONE_BY_SIBLING（主体） | git_commit_gateway.py@HEAD:492 GatewayError(ErrorCodeRuntimeError) 收编注记（st-nightsweep-sw8）；两文件 status 干净 | src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | 余量=0120（internal_call 声明位）重投+0121（landing W1）退役，走死信 blobs 反查 | 0.5 天 | 死信 blobs 对账 |
| C147 R3 复测第二轮 | BLOCKED | decisions_log 无 R2 达标记录；C05 未完 | docs/_working/commit_speedup_campaign/90_verification/decisions_log.md | C05 达标后做第二轮确认，连续两轮=终止 | 0.5 天 | C05 |
| C152 InvariantCulture 时区修 | BLOCKED | HEAD 与盘面 scheduled_task_reconcile.py 均无 InvariantCulture；死袋 grep=0（字节不在队列） | scripts/governance/scheduled_task_reconcile.py | 先在 .aidrafts/.worktrees 车道反查"盘面字节"（清单声称存在）；查无则按现状重修（InvariantCulture 解析补丁） | 0.5 天 | 字节定位 |
| C153 deadman 第6路 | READY | HEAD deadman_switch.ps1 无 DEADMAN_DASHBOARD_PORT；**字节在 q-0213 死袋 blob** 9fcfe69d…（2 命中） | scripts/deadman_switch.ps1 | from-bag 取回整文件→.ps1 纯 ASCII 红线自查→换新袋号重投（enqueue 即落） | 0.5 小时 | q-0213 死信代投通道 |
| C243 W-164 LOG-TRD-001 定性 | READY | dr_chain_report.md@HEAD 无 W-164/LOG-TRD-001 段；registry_of_logs.yaml:539 在册 | docs/_working/total_command_closeout/wave4/dr_chain_report.md | 波4 域补一案卷定性：schema 侧血缘/写者/消费三问，追加进 dr_chain_report 并随批落 HEAD | 2 小时 | - |
| C248 m1_data 两车道合并 | CONFLICT_INFLIGHT | docs/_working/fullflow_mining/m1_data/（10 件）单点在；同名对账涉及他道与热册追加 | docs/_working/fullflow_mining/m1_data/ | 先裁真源（技术对拍 hash）再并；涉热册 CAS。defer 至他道平息 | 0.5 天 | 真源裁定 |
| C444 dead_archive 89 件定策 | OWNER_GATE | .runtime/commit_queue/ 下 9 个 dead_archive* 归档目录在册 | .runtime/commit_queue/dead_archive* | 列 Owner 定"入库 or 封矿"；AI 只呈报 | 呈报即止 | Owner |
| C482 主区磁盘==HEAD 常驻尺 | READY | scripts/ 无该尺（grep 0）；处方=L58286 §廿五 | scripts/commit_queue.py；scripts/git_commit.py（参照） | 新建事件触发尺（禁 cron）：落地回执后校验主区磁盘==HEAD，漂移即 workspace_alert；新 .py 需 token+翻译登记（非本矿道自开工面） | 1 天 | - |

## 二、提交链 🔶部分完成（14 卡）

| 卡号 | 六态 | 证据（HEAD 实测） | 文件 | 处方 | 预估 | 依赖 |
|---|---|---|---|---|---|---|
| C01 q-0167 红蓝落库 | CONFLICT_INFLIGHT | 袋 dead；redblue_governance.md 已字节全等@HEAD；redblue_robust.md@HEAD 行63-64 仍含 `git reset`+`--hard` 连写字面量（重投必再被 GATE-detect-git-dangerous 拦）；70_redblue/ 有他会话 staged 在途（index.md 'A'） | docs/_working/commit_speedup_campaign/70_redblue/redblue_robust.md | 在途清空后：改写行63 字面量（如 `git reset` + `--hard` 拆写或加 ABS-27 白名单标记）→ 换新袋号重投报告 1 件（另一件已落） | 0.5 小时 | 70_redblue/ 在飞清空 |
| C10 api_server 路由守卫序 | **READY→本矿道已自开工** | HEAD api_server.py：main() 5094、`__main__` 5108、AI 层路由段 5112-5214（budget-advisories/schedulegate-queue/skeletons/confirm）在守卫后=直跑模式永不注册 | src/zephyr/frontend/dashboard/api_server.py | 路由段整体移到 def main() 之前+守卫顺序静态回归尺（详见 §4 自开工 B） | 0.5 小时 | 已施工 |
| C12 队列侧②CLAIM-REQUIRED 处方 | BLOCKED | 处方未执行（52 tokens/六图 yaml 仍卡）；依赖 M3.4 生产者规约合流 | docs/_working/qmine_campaign/03_queue_robust/workbook.md | 等规约合流后排 depends_on 锁；影子文件 MVP 若未落按作业簿补 | 1 天 | M3.4 合流 |
| C56 q-0213 40 件落地 | CONFLICT_INFLIGHT | 袋 dead（快照基底冲突）；5/5 抽样 HEAD≠袋字节；袋 message 显示 C1 合批语义 | .runtime/commit_queue/dead/q-20260929-st-chief7-20260928-0213.json | 属主（chief7）同步工作区后重投；或按死信新规内容驱动代投：from-bag 逐件恢复→与 HEAD 冲突件（AGENTS.md/negative_list_gates.py）人工合并→拆小袋重投；blob 全在可取回 | 1 天 | 死信代投批；AGENTS.md 在 M2 锁下 |
| C150 k=6 试轮结论 | READY | thresholds.yaml:288 仍 k=4 默认；decisions_log 无 k=6 试轮结论条目 | scripts/governance/commit_queue_landing.py；scripts/governance/_shared/thresholds.yaml | 采样近 24h 链耗时+watermark→写试轮结论入 decisions_log；反升则按预案回 4 | 1 小时 | 24h 样本窗 |
| C155 N1 snapself+EV 护栏 | CONFLICT_INFLIGHT | test_commit_queue_snapshot_selfconsistency.py@HEAD；但 tests/governance/test_evaporation_cure_lane_ev.py 盘面有、git 历史 0（未入库，qmine 车道字节） | tests/governance/test_evaporation_cure_lane_ev.py | 车道属主收编（tests 免 token）走窄袋；铁尺先证能红 | 0.5 小时 | qmine 车道归属确认 |
| C202 文件群10 双接线 5 件 | READY | src/zephyr/ex_sor/ 模块在 HEAD；5 缺件需对账 | src/zephyr/ex_sor/ | 按 dead/ 袋 blobs 清单反查缺件→接线成效以 CNS 复算为准 | 0.5 天 | 死信 blobs 对账 |
| C270 merge train 不变式 | CONFLICT_INFLIGHT | 10_wave_plan.md:55 1.7b 在册；scripts/commit_queue.py 无"快照失效强制重建"不变式（grep 0）；**该文件现被 st-nightclean-20260929 持锁在飞** | scripts/commit_queue.py | 锁释放后 serializer 侧落一条不变式：袋死→后继 pending 袋快照失效强制重建 | 2 小时 | st-nightclean 锁释放 |
| C304 T3 CREATE-GUARD files_trigger 登记 | READY（热册→defer） | gate_registry.yaml 无 create_guard files_trigger 段（grep 0）；全册 files_trigger=183 处 | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | 逐台核登记完备（簇3 防复发）；热册 safe_write_text CAS | 0.5 天 | 热注册表（defer） |
| C330 QMine 收尾① | CONFLICT_INFLIGHT（热册） | candidate_module_registry CAND-GOVTEST-001..003 在册（:6814-6884），005 撞号/007 重编号未动 | docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml | 平静窗 gateway 直连治标批（重编号件）；=C09 同袋 | 0.5 天 | 热注册表（defer） |
| C338 RECONCILER-FILE-OPS diff 化 | READY | reconciler_file_ops_gate.py 无 _get_added_lines/own-diff 痕迹（grep 0） | src/zephyr/gov_enforcement/commit_gates/reconciler_file_ops_gate.py | 按 LEDGER_three_piece 处方 own-diff 化（_get_added_lines 行号集合，新文件才全文）+8 条尺 | 0.5 天 | - |
| C355 会话保活判活语义 | OWNER_GATE | W-29 豁免（logical 判活）已落 HEAD（48aa677f7f）——判活侧已治本；余"队列等待>TTL⇒落地期 SESSION-REQUIRED 处死"改造+七件延后袋低峰投 | src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py | 判活语义改造呈 Owner；七件延后袋（含 commit_queue.py）择低峰单袋投 | 呈报+时窗 | Owner |
| C408 夜裁#2 79 件追认 | OWNER_GATE | 需 ruling_registry 正式条目（5 项套餐批准），现 0 命中 | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 用取号器补登；未登前下一班按未批处理 | 呈报即止 | Owner+热册 |
| C450 波1B 提交链解毒七件延后袋 | READY（时窗） | dead_letter_census.yaml/prescription_matrix.md@wave1b；700 死信 63 族处方在册 | docs/_working/total_command_closeout/wave1b/ | 七件延后运行时面袋按日班低峰投（96 册处方+红证已留） | 时窗依赖 | 低峰窗 |

## 三、清洁卫生 ❌未完成（10 卡）

| 卡号 | 六态 | 证据（HEAD 实测） | 文件 | 处方 | 预估 | 依赖 |
|---|---|---|---|---|---|---|
| C07 T17 终局清洁 | READY（盘点完成） | §0.4/§0.5：tmp csx_* 136、worktree csx-* 18+2 scratch、claims 已清、取证件 cs-tbl 已消失 | .runtime/tmp；.worktrees | git worktree remove+prune（先 byte_ledger 归账，OPS-GUARD 拒 in-process 属正常）；**删除动作全部列清单归总筹执行**（本矿道不删） | 0.5 天 | 总筹执行窗 |
| C08 多车道会话收尾 | READY（盘点完成） | .aidrafts 32 车道树在（ff_*/lane_*） | .aidrafts；.runtime/tmp；.worktrees | 逐文件 hash 相等判据（`git hash-object`==`git rev-parse dev:<f>`）分批清理；任一不等或不在 dev=禁删；列清单归总筹 | 1 天 | 总筹执行窗 |
| C26 scripts/ 根容量治理 | DONE_BY_SIBLING（红线已回退） | scripts 根实测 **116 件**（清单 148→116，已回落 120 红线内） | scripts/ | 余量=子目录化治理方案呈批（防再恶化）；缓行件 generate_manifest.py 已由他会话落 | 呈报 | - |
| C59 雷-1 next_ruling_id 可疑删除 | DONE_BY_SIBLING | 暂存区无 D 标记（status 干净）；文件@HEAD 在 | scripts/governance/next_ruling_id.py | 无（雷已排） | 0 | - |
| C101 178 blueprint 双写手 | READY（调查类→defer） | .aidrafts maxdepth2 无 blueprint 目录（或已被清退）；根因定位未做 | docs/_working/wave13_chief3/LEDGER_chief3.md §6.2 | 按 LEDGER §6.2 定位带漂移 worktree 根的生成器/对账器调用源（同 I40 蒸发族）；先对账清退面是否已完成 | 0.5 天 | chief3 车道记录 |
| C105 untracked+index 双清蒸发定位 | BLOCKED（归属维护班） | watchdog auto-derived-sync 假说待实证；本矿道无审计面 | docs/_working/ai_layer_vision/LEDGER_final.md | 维护班审计 serializer/守护进程/schtasks 日志定位执行源 | 1 天 | 维护班 |
| C161 fix_map 412 行清偿 | READY | deadref_fix_map.csv 实测 **412 行**（与清单一致，0 清偿） | docs/_working/fms_overhaul/_data/deadref_fix_map.csv | 按 S1 簿批改写清偿；_working 陈化处置（已 3571 件）另立波次 | 1 天 | - |
| C174 lane_q tmp 清理 | READY（登记制） | .runtime/tmp/lane_q_20260927 **仍在**；lane_q_notes.md 已@HEAD（要点已抄录） | D:/ZephyrAlpha/.runtime/tmp/lane_q_20260927 | 抄录已完成（notes@HEAD）；剩余=24h TTL 外显式删除→列破坏性登记 R-3 归总筹 | 登记 | 总筹 |
| C225 补丁C.3 一行追加 | **READY→本矿道已自开工** | 91_flash_one_click.md status 干净无锁；无 final_review_chartlib 豁免行 | docs/_working/total_command_closeout/91_flash_one_click.md | 波8 清洁清单补一行豁免（详见 §4 自开工 A） | 5 分钟 | 已施工 |
| C455 波0.1 车道现场快照 | SUPERSEDED | snapshot/ 目录不存在（连目录未建成）；波 0.1 现场已被波 1-8 覆写，快照对象时效消失；94_ledger 现仅存 141 staged 删除注记 | docs/_working/total_command_closeout/94_ledger.md | 不再补拍（拍=拍错宇宙）；94_ledger 挂一行"0.1 快照失效"注记即可 | 5 分钟 | - |

## 四、清洁卫生 🔶部分完成（2 卡）

| 卡号 | 六态 | 证据（HEAD 实测） | 文件 | 处方 | 预估 | 依赖 |
|---|---|---|---|---|---|---|
| C60 .worktrees 大扫除 | READY（盘点完成） | .worktrees 118 目录（清单 100→118 不降反升）；注册 181/prunable 0；csx-* 18；G:/zephyr_cold/90_tmp/chief4_diskrescue_20260927 镜像在案 | .worktrees | byte_ledger 归账→逐目录 unlock→remove（禁裸删）；清单归总筹 | 1 天 | 总筹+磁盘窗 |
| C262 主区回退弹丢弃 | DONE_BY_SIBLING（半） | commit_preflight.py status 干净、diff HEAD=空（陈旧副本已消）；commit_queue.py 现被 st-nightclean 持锁在飞（' M'）复核顺带 | src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py | nightclean 落地后复核 commit_queue.py 半场 | 锁释放后 10 分钟 | st-nightclean |

## 五、本矿道自开工成果（≤5 张授权内，实际 2 张+工作单本体）

### A. C225 补丁C.3 一行（清洁卫生）

- 文件：`docs/_working/total_command_closeout/91_flash_one_click.md`（改前 status 干净、无锁）
- 动作：波8 清洁清单追加 final_review_chartlib 永久豁免行，防 dossier 案卷库被清洁波误清
- 验证：`git show HEAD:docs/_working/total_command_closeout/91_flash_one_click.md | grep -c final_review_chartlib` ≥1
- 回滚：revert 该 commit（纯插入一行，零逻辑）

### B. C10 api_server 路由守卫序（提交链）

- 文件：`src/zephyr/frontend/dashboard/api_server.py`（改前 status 干净、无锁）+ 新增 `tests/governance/test_api_server_route_guard_order.py`（tests 免 token）
- 动作：AI 层路由段（budget-advisories/schedulegate-queue/schedulegate-skeletons/schedulegate-confirm+`_SCHEDULEGATE_UI_ACTOR`）自 `__main__` 守卫后（5112-5214）整体前移至 `def main()` 之前；补守卫顺序静态回归尺（路由段起始行 < `__main__` 守卫行，防复发）
- 验证：`python -m py_compile src/zephyr/frontend/dashboard/api_server.py`；`python -m pytest tests/governance/test_api_server_route_guard_order.py -q`；ruff check/format
- 回滚：revert 该 commit（纯位置移动，零语义改动）

### 工作单本体

- `docs/_working/final_delivery_campaign/workorders_commit_clean.md`（本文件，token 经 batch_creation_tokens.py 官方通道登记 capability=final_delivery_campaign）

## 六、defer 与破坏性登记清单（移交总筹）

| # | 类型 | 内容 | 建议执行窗 |
|---|---|---|---|
| R-1 | 蒸发候选 | `docs/_working/wiring_gap_inventory_20260927.md` 盘面/HEAD/git 历史（--all）三处皆无——C40 声称随 107 件袋入库，实际独此件蒸发；关联 C400 关键路径失效 | 立即查 stash_notice.json/死袋 blobs 反捞 |
| R-2 | 取证件失踪 | T17 明令保留的 `.runtime/tmp/cs-tbl/` 与 `csx_t10_hook_timing.log` 已消失（与"仅留取证"要求相反） | 查 G:/zephyr_cold 镜像或 90_tmp/diskrescue |
| R-3 | 破坏性·tmp | `.runtime/tmp/csx_*` 136 个+`lane_q_20260927`+`csx_t13_wt/csx_t14_wt` 删除（要点已抄 lane_q_notes.md@HEAD） | 总筹清洁窗，先 hash 对拍 |
| R-4 | 破坏性·worktree | 18 个 csx-* worktree+csx_t13_wt/csx_t14_wt `git worktree remove --force`+prune（先 byte_ledger 归账） | 总筹清洁窗 |
| R-5 | 破坏性·死信 | 残留 440 封 dead 分批≤10 封终局处置（先捞缺失件，再 blob gc） | 死信新规批；blob gc（18270 块，blobs_archive 已建）排最后 |
| R-6 | 热注册表 | C15/C304/C330/C408（gate_registry/candidate_module_registry/ruling_registry 相关 hunk）一律 defer 给属主通道 | 平静窗 |
| R-7 | 在飞冲突 | C01（70_redblue/ 有他会话 staged index.md）、C270（commit_queue.py 被 st-nightclean 锁）、C56（AGENTS.md 被 M2 锁涉及） | 锁释放后按处方 |

## 七、统计

41 卡 = READY 19（含已自开工 2：C10/C225；删除登记类 4：C07/C08/C60/C174 删除面归总筹；其余 READY 处方已细化待属主/排产）｜ DONE_BY_SIBLING 7（C02/C04/C16/C143/C26半/C59/C262半）｜ CONFLICT_INFLIGHT 6（C01/C56/C155/C248/C270/C330）｜ OWNER_GATE 3（C355/C408/C444）｜ BLOCKED 5（C05/C12/C105/C147/C152）｜ SUPERSEDED 1（C455）。
时敏项：队列三袋=两 dead 一已消化（fullconnect 107 件已全落 HEAD）；死信 1079→440（归档 743 已做）；blob 23217→18270（archive 已建）；W-29 已修@HEAD；T17 四项=claims 达成/死信主体达成/tmp+worktree 未清/取证件失踪。
