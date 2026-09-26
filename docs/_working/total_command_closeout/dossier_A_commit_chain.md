---
ttl: task_bound
---
# 案卷 A — 提交链 / 队列 / 门禁 实测读数（环节A）

本册覆盖 环节A

> 取证基线：分支 `dev`，HEAD = `54622bbbf4`（`[st-audit-fix-20260924][全流通战役 09-26 案卷入册…]`）。
> 判据铁律：落地只认 `git show HEAD:<path>` / `git ls-tree HEAD`；队列回执、commit message 自述、交接书叙述均不作证据。
> 取证时间：2026-09-26（机时）。所有临时探针脚本位于 `.runtime/tmp/total_command_closeout/`，未写入项目根。

## 1. 主表：逐条实测

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---------|------|---------|-----|
| 1a | 总筹指令 环节A-1「队列现状」 | `python scripts/commit_queue.py status` → `.counts` | `pending 0` / `processing 0` / `done 741` / `dead 700`，`total 1441` | 实测读数 |
| 1b | 同上（盘上互证） | `ls .runtime/commit_queue/{pending,processing,dead,done} \| wc -l` | `pending 0` / `processing 0` / `dead 701` / `done 741` / `archived 0` | 实测读数 |
| 1c | 交接书称 daemon 在线 / lease | `status` → `.daemon` / `.lease` | `daemon.online = true`；`lease.present = false`；`head = null` | 实测读数 |
| 1d | 追 1b 的 701≠700 | `find .runtime/commit_queue/dead -maxdepth 1 -type f/-type d` | dead/ 顶层 700 个 `*.json` + 1 个子目录 `archive_flashbiz_superseded_20260918`；递归共 714 个 json。**1b 差 1 的成因=该子目录被 `ls \| wc -l` 计入**，status 的 700 与顶层 json 实数一致 | 已澄清（无冲突） |
| 2a | 总筹指令 环节A-2「dead 签名聚类」 | `.runtime/tmp/total_command_closeout/probe_A.py`（walk dead 顶层 700 json，`dead_reason` 折叠空白后取首 60 字符为签名） | 700 封全部可解析（parse_fail=0）；**distinct 60 字符签名 = 110 簇**。Top 5：①`网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断` 85 封；②`landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）` 71 封；③`门禁 CREATE-GUARD 阻断: 无 creation_token` 48 封；④`门禁 TRANSLATION-COVERAGE 阻断` 47 封；⑤`landing 异常: LandingEnvironmentError: landing 环境不可用` 36 封。完整 top 20 见本文 §2 附表 | 实测读数 |
| 2b | 交接书称"注册表三向合并失败 CAND-GOVTEST-005 ours 同侧身份键重复"这一签名占 X 封 | 同上脚本 TARGET CHECK | **签名口径不成立**：`注册表三向合并失败` 家族 71 封，但该家族签名的**首 60 字符内不含 `CAND-GOVTEST-005`**（60 字符截断点在 `…（死信回退人工）: docs/`，身份键在第 ~150 字符之后）→ 按"首 60 字符签名"聚类，CAND-GOVTEST-005 单列簇 = **0 封**。改按全文匹配：`dead_reason` 同时含"注册表三向合并失败"与"CAND-GOVTEST-005"的袋 = **7 封**（含 `q-20260926-st-qmine-20260925-0042/0043/0044`） | 证据冲突（声称的签名颗粒度与实测聚类口径不符；家族 71 封 vs 指名身份键 7 封） |
| 2c | 涉及 session 分布 | 同 2a | dead 顶层按 session 计数 top 10：`st-cmd-20260924` 115、`st-commitspeed-tbl-20260924` 88、`st-mapbuild-20260924` 33、`st-stress-20260923` 31、`st-sweep-tail-20260923` 30、`st-chainpile-20260922` 27、`st-qmine-20260925` 26、`st-audit-fix-20260924` 25、`st-wm1-wave0-20260924` 22、`st-metaq-20260923` 21（第 11 名 `st-combine-20260923` 18、`st-library-final-20260924` 18） | 实测读数 |
| 3a | 总筹指令 环节A-3「HEAD 双条 CAND-GOVTEST-005」 | `git show HEAD:docs/…/candidate_module_registry.yaml \| grep -c "id: CAND-GOVTEST-005"` | **2**（复述总筹已实测值，本机复核一致）；同一命令对**工作区**文件 = **1** | 已落地（HEAD 层缺陷确认）+ 工作区已 ≠ HEAD |
| 3b | 同上（两条目差异） | `probe_B.py`：yaml 解析 HEAD entries，过滤 `id=="CAND-GOVTEST-005"` | HEAD 该 id 双条：条1 `name=commit queue P1 级联+P2 监控（66号②③，随 MVP 验收后）` / `status=promoted` / `promoted_to=commit_queue.py P1 三件套（级联/死信 requeue/TTL 清理）`；条2 `name=测试上下文 commit 泄漏主仓——tests 身份穿透隔离边界实证堵源`（sub_layer=测试隔离，status/promoted_to 见 §2 附引文）。**工作区同一册现只剩条1**（`grep -c` 工作区=1） | 已落地（HEAD 缺陷）+ 修复未落地（工作区已改，HEAD 未收） |
| 3c | 全册"同 id 双条"总数 | `probe_B.py`（entries 全量 Counter） | HEAD：`entries` 623 条、distinct id 622、**dup id 组 = 1（仅 CAND-GOVTEST-005×2）**；工作区：entries 623 条、distinct id 623、**dup = 0** | 实测读数 |
| 4a | 交接书称 gate_registry 派生标量曾/现不自洽 | `git show HEAD:…/gate_registry.yaml` + yaml 解析 | HEAD：`total_gates` 声明 **181**，`gates` 实数 **181** → 相等；工作区同 181/181。册结构=顶层 `total_gates` 标量 + `gates` 列表（181 个 dict），键含 gate_id/name/entry/files_trigger/own_scope/always_run/enforcement_channel/source/status/category/description | 未复现（HEAD 现值自洽） |
| 4b | 交接书称 in_process 册曾 102≠103 | `git show HEAD:…/in_process_gate_registry.yaml` + yaml 解析 | HEAD：`total_gates` 声明 **103**，`gates` 实数 **103** → 相等；工作区同 103/103。102≠103 的历史证据仍在死信袋 `q-20260926-st-qmine-20260925-0038`：`roster entries 103 != declared total_gates 102`（该袋 dead_reason 原文，属队列回执类证据，不作落地判据） | 未复现于 HEAD（历史态可见于死信） |
| 5a | 交接书称两门 priority 撞号 | `git show HEAD:src/zephyr/gov_enforcement/commit_gates/blueprint_format_gate.py` L179-233 | `BLUEPRINT-FORMAT` 现值 **priority=130**；注释原文：`priority=130：原 77 让位给 DOC-HEADER-SUITE 聚合门（后到者让位先例；本薄工厂已出名册…）`；同文件 `DOC-HEADER-SUITE` 薄工厂 **priority=77**（注释：`priority=77（BLUEPRINT-FORMAT 原槽位…）`）→ 两台现**不撞**，且 77 槽位是"已让位"的历史撞点 | 未复现（该二门现值不同） |
| 5b | 两册内 priority 字段 | `git show HEAD:` 两册 + yaml 解析（priority dist） | **两册条目均无 `priority` 字段**（gate_registry 181 条 0 命中、in_process 103 条 0 命中）。`gate_auto_registrar.py` L54-55 原文：`不覆盖 priority：priority 从 GateSpec 读取…YAML 的 priority 字段仅 informational` → priority 真源在代码 GateSpec，不在名册 | 实测读数（声称的"名册 priority 撞号"层级不成立，须按 GateSpec 枚举，见 5c） |
| 5c | 全量 priority 撞号枚举（代码真源） | `.runtime/tmp/total_command_closeout/probe_C.py`：`git ls-tree -r HEAD src/zephyr/gov_enforcement/commit_gates/`（122 个 .py）+ `git show HEAD:<f>` 正则抽 `GateSpec(gate_id=…, priority=…)` | 119 个 (gate_id,priority,file) 去组、116 个 distinct gate_id；**代码层 priority 撞号簇 = 6**：`70→[DANGLING-REFERENCE, REFERENCE-INTEGRITY]`、`79→[BLUEPRINT-AMODULE-CONSISTENCY, BLUEPRINT-HEADER]`、`80→[GATE-VOCAB, VOCAB-HARDCODE]`、`82→[PERM-TRIGGER, PERMANENT-SYSTEM-TRIGGER]`、`92→[COMPLEXITY-GUARD, NO-HIGH-COMPLEXITY]`、`113→[DEPGRAPH-ENFORCEMENT, DEPGRAPH-PRE-REGISTRATION]`；另有 `REGISTRY-CODE-ANCHOR` 一个 gate_id 在 HEAD 代码里出现两个 priority 值（106 与 129，不同文件/不同 GateSpec） | 实测读数 |
| 5d | 同 5c（进程内实载口径） | 进程内 `auto_register_gates(CommitGateRegistry(), Path("D:\\ZephyrAlpha"))` | **未抛异常**，返回 failures=`[]`；注册台数 **99/103**（log 原文：`registered 99/103 gates successfully (roster reconciled: 99 unique enabled gate_id, declared total_gates=103)`）；跳过 4 台 disabled：`CAPABILITY-OVERLAP / GATE-VOCAB / PERMANENT-SYSTEM-TRIGGER / ALGO-FLOW-LINk`（实值 `ALGO-FLOW-LINK`）。**实载集合内 priority 撞号 = 0 簇**（5c 的 6 簇中 `80/82` 两簇因 GATE-VOCAB、PERMANENT-SYSTEM-TRIGGER 处于 disabled 而不同台并存；其余簇的成员台不在实载 99 台内） | 未复现（实载层无撞号） |
| 5e | 装载过程的 files_trigger 体检 | 同 5d（registrar 自带告警流） | 装载时输出告警 28 条：`超宽（命中 8892 文件 ≥ 阈值 1000，近 always-fire）` 计 15 台（含 `COMPLEXITY-GUARD: '.py'`、`ASYNCIO-RUN-IN-CONTEXT: '.py'`、`BLOOD-FLESH: '.py'`、`FILE-COPY/FUNCTION-DUP/GATE-DOMAIN-FK/STATE-VOCAB-REGISTRY/UNSAFE-DICT-SPREAD: '.py'`、`R5-DIGIT-SUFFIX: 'docs/'`=8067、`REFERENCE-INTEGRITY: 'docs/'`=8067、`META-TESTS-COVERAGE: 'tests/'`=3873、`MAP-ALIGNMENT: 'docs/03_modules/'`=4790 等）；`死触发（HEAD 树零命中）` 计 6 项（`BARE-SUBPROCESS`/`NO-BARE-GETENV`/`NO-SECRET-HARDCODE` 的 `api_key`/`password` 模式） | 实测读数（新增事实：CREATE-GUARD 不在这两类告警名单内，见 7） |
| 6a | 交接书称 q-20260926-st-mapbuild-20260924-0029 死于 `src/zephyr/ai_layer/heritage/heritage_events.py 缺 TTL（外来 staged）` | 读 `.runtime/commit_queue/dead/q-20260926-st-mapbuild-20260924-0029.json` 的 `dead_reason`+`files` 原文 | **该袋 dead_reason 与声称无关**：原文=`landing 异常: WorktreePunchThroughError: [landing] EV-02 打穿复核拦截：worktree 破坏性操作 \`reset\` 疑似打穿主仓——主仓 HEAD 93e55f2f46 → 16d58a652d（worktree=.runtime\\commit_queue\\worktrees\\w0，审计 .runtime/audit/landing_guard.jsonl）`；袋内 files 共 17 件（config/×6 图 + scripts/governance/d5_architecture/×11），**不含 heritage_events.py** | 证据冲突（声称死因与袋内原文不符） |
| 6b | 交接书称 q-20260926-st-mapbuild-20260924-0034 死于 `docs/_working/registry_migration/stress/lane_01.md 快照不符（外来 staged）` | 同 6a | **亦不符**：原文=`网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 无 creation_token，禁止造第二真源（trae_060 §2）: ['docs/_working/map_build/03_final_blueprint_and_schema.md', 'docs/_working/map_build/fig12_datachain/12_扩行提案与封顶重宣.md']`；袋内 38 件 files **包含**这两个被点名的文件 → 属自有文件违规，非外来 | 证据冲突 |
| 6c | 上述两个"真死因"实际落在哪些袋 | 全文检索 700 封 dead 顶层 json | `heritage_events` 命中 13 袋，其中 `q-20260923-st-ailayer-p1-20260923-0029`（session `st-ailayer-p1-20260923`）dead_reason=`门禁 CREATE-GUARD 阻断: 字段头部不完整（ARCH-031）: src/zephyr/ai_layer/heritage/heritage_events.py 缺失字段: ['TTL']`，**该袋自己 files 清单 46 件内含该文件** → 非"外来 staged"；`lane_01.md 快照不符`命中仅 1 袋=`q-20260923-st-stress-20260923-0034`（session `st-stress-20260923`，files 仅 1 件正是 lane_01.md），dead_reason=`NOTHING_TO_COMMIT 但快照未真应用 (blob 与 old_dev 不符: […lane_01.md])——应用静默丢失，死信回退重新入队（2026-09-15 q-0003 假落地事故防线）`，亦非"外来 staged" | 证据冲突（两例真实死因的违规文件都属袋主自己的 files 清单；"死于外来 staged"的归因在两袋上均不成立） |
| 6d | 全 dead 里真正文本含"外来 staged"的袋 | 同 6c 检索 | 仅 **2** 袋：`q-20260926-st-commitspeed-tbl-20260924-0136`、`-0140`（与交接书点名的两袋不同 session、不同 qid） | 实测读数 |
| 6e | own-scope 是否真剔外来 | 读 `src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py` L536-651 | `_build_own_scope`（L536-555）：范围=本次 commit `files` ∪ `SessionRegistry.get_session(sid).held_files`，两者皆空返回 `None`（L540-541 契约=退化为扫全量），registry 读取异常 fail-open 退 files-only（L553-554）。`_split_own_foreign`（L607-651）：把 `staged` 按 own_scope 切成 (own, foreign)，foreign 走 `_audit_foreign_staged`（L578-601，写 `.runtime/gate_audit/<gate_name>_foreign_staged.jsonl`）+ `logger.warning`（L645-650），**返回 own 侧供扫描**（L651）→ 结构上外来件不产生违规；但两处 fail-open（L631-632 own_scope=None 全量、L640-642 拆分异常全量）。docstring L617-621 自述口径：`全暂存内容扫描台扫「全暂存区 ∩ 本 session 范围」…31 台若各自内联本拆分即触发 FUNCTION-DUP` | 实测读数（"剔出本会话范围"代码在册，但依赖 files/held_files 两输入非空） |
| 7a | 交接书称 CREATE-GUARD 名册无 files_trigger 登记 | `probe_B.py`（读 gate_registry CREATE-GUARD 条目全键） | gate_registry 内 CREATE-GUARD 条目**含 `files_trigger` 键，值为空串 `''`**；同时含 `always_run` 键；in_process 册的 CREATE-GUARD 条目**无 files_trigger 键**（键仅 enabled/factory_function/gate_id/module_path/register_line/source） | 证据冲突（"无登记"不准确：有键但空值＝无触发面过滤） |
| 7c | 交接书称 CREATE-GUARD 成本=`4488 次 × 23.4s ≈ 105154s，最大单项耗时` | 实测账本 `D:\ZephyrAlpha\.runtime\audit\gate_execution_stats.jsonl`（1964 行，机时 2026-09-15T18:19 → 2026-09-25T23:21；口径=每行 `ms` 字典按 gate 累加） | CREATE-GUARD：**1519 次调用**、累计 **19186.1s**、均 **12.63s/次**；账本内**排名第 1**（第 2 CAPABILITY-OVERLAP 7619.3s/1490 次，第 3 BLUEPRINT-HEADER 7565.9s/465 次）。全账本所有 gate 累计 `total_ms` 之和 = **141565s**（1964 runs）。仅取 09-25 之后窗口：CREATE-GUARD 105 次、2529.8s、均 **24.09s/次**（与声称的 23.4s 均值同量级）。**"4488 次"在本账本不出现**（本账本最长 gate 调用数=1519；105154s 超过本账本全部门累计 141565s 的 74%） | 证据冲突（"最大单项耗时"成立；"4488 次×105154s"在本账本不可复现，次数与总量均对不上） |

| 6f | 门禁读 index 还是 worktree（决定"工棚含他会话件"后果） | 读 `_diff_helpers.py` L285-341 + `scripts/governance/commit_queue_landing.py` L1349-1363/L1817-1860/L2609-2632 | 内容扫描台的输入面全部是 **index**：L298-301 `git diff --cached --name-only --diff-filter=AM(R)`、L335 `git diff --cached --unified=0 --ignore-cr-at-eol -- <py_file>`、L381 `rev="" → git ls-files --cached`（HEAD 侧才是 `ls-tree`）；CREATE-GUARD 同样读 index：`create_guard.py` L350 `git diff --cached --name-only --diff-filter=A`、L373/L468 `--name-status --diff-filter=R`。落地工棚侧：每袋处理前 `reset --hard refs/heads/dev` + `clean -fd`（L1363，注释 L1360"残留 untracked 不可能混入提交…reset --hard + pathspec 双保险"），预暂存用 `git add --pathspec-from-file`（L1850）/`git rm --cached --ignore-unmatch`（L1860），plumbing 通道另有 `read-tree refs/heads/<branch>` 纯 index 置换（L2632）。→ 工棚 index 逐袋重建，own-scope 的"剔外来"生效前提是袋内 files 清单完整；`_build_own_scope` 在 files 与 held_files 双空时返回 None（L540-541）→ 该态下内容台退化为扫全 index（含任何他会话残留件） | 实测读数 |
| 6g | "能红的最小复现"设计（仅设计，未执行） | 设计描述（零破坏动作） | 前置：独立 worktree + 独立 `GIT_INDEX_FILE`。步骤：①工棚内 `git add` A 会话件 `a.py`，内容含一台 own-scope 内容台的违规（如在 `src/zephyr/**` 新 .py 缺 15 字段头部的 `# [TTL]`）；②以 B 会话身份提交，`commit_files=[]`（空清单）且 session 未 claim 任何 held_files → `_build_own_scope` 返回 None（L531 契约），`_split_own_foreign` 走 L631-632 分支返回 `(staged, [])`，A 的违规被判给 B = 连坐红；③对照组：B 提交时 `commit_files` 非空且不含 `a.py` → 走 L636-651 拆分为 foreign，只 warn+写 `.runtime/gate_audit/<gate>_foreign_staged.jsonl`，不红。判定读点：第②步 exit=红、第③步 exit=绿即为"own_scope 空输入退化"复现。反证位（若③仍红）＝某台内容门未接 `_split_own_foreign`，需逐台点名（本次未做全 31 台接线核对，见 §6 缺口） | 设计-only |
| 7d | CREATE-GUARD 每次链上跑的成本来源 | 读 `src/zephyr/gov_enforcement/commit_gates/create_guard.py` L343-545 | 成本构成（按代码路径）：①L350 一次 `git diff --cached --diff-filter=A` 全暂存新文件枚举；②L373/L468 两次 `--name-status --diff-filter=R` rename 枚举；③L432-446 对 staged_new 逐件按 7 扩展名分流；④L504-542 `_check_class_uniqueness`：对**每个新增 .py 的每个 ClassDef 节点**起一次 `git grep -l "^class <name>\\b" -- src/zephyr/`（L527）＝全树 grep × 类数，git grep 故障 fail-closed 直接阻断（L536-542）；⑤L288-320 reconciler 标记核对读 `git show :<registry>` 与 `git show <main_ref>:<registry>` 两遍。名册侧：CREATE-GUARD `files_trigger=''` + `always_run=false` + `own_scope=false`（gate_registry 在册值，见 §4 附） → 无触发面裁剪，每链按上列全跑 | 实测读数（成本源=④的类级全树 grep 与①②的全暂存枚举） |
| 11a | 总筹指令 环节A-11「主区 index 现状 141 件 staged 删除」 | `git status --porcelain` + 前缀计数 | 共 465 行：`??` 188、**`D ` 141**（staged 删除，与指令给定值一致）、` M` 88、`MM` 28、`AM` 13、`A ` 3、`M ` 2、` D` 2。`git diff --cached --name-status --diff-filter=D` 亦 141 行；`git ls-files`=17780 而 `git ls-tree -r HEAD`=17903（差 123） | 实测读数（未动任何条目） |
| 11b | staged 删除按顶层目录分组 | 同 11a + 路径分组 | `scripts/governance` 69、`tests/governance` 25、`src/zephyr` 15、`docs/03_modules` 14、`docs/_working` 10、`docs/01_policies_and_standards` 1、`scripts/backtest` 1、`scripts/ch` 1、`scripts`（根）1、`tests/backtest` 1、`tests/data` 1、`tests/frontend` 1、`tests/scripts` 1；扩展名：.py 96 / .yaml 27 / .md 17 / .ps1 1 | 实测读数 |
| 11c | 141 件删除的"盘上实况" | 逐件 `git cat-file -e HEAD:<p>` + `os.path.exists` + 与 `??` 集合求交 | 状态矩阵：**77 件 `HEAD=1, disk=1, untracked=N`**、**54 件 `HEAD=1, disk=1, untracked=Y`**（=同一路径既在 index 删除又在 untracked 出现，语义=index 摘除而文件仍在盘，形同 `git rm --cached`）、**10 件 `HEAD=1, disk=0`**（全部落在 `docs/_working`，盘上亦已不存在）。141 件全部在 HEAD 有 blob | 实测读数（无一件是"HEAD 无此件的孤儿删除"） |
| 11d | 归属会话反查 | 遍历 `.runtime/claim_snapshots/*.jsonl`（866 个）文本命中 + 遍历 dead/done 顶层 1441 个袋的 `files[].action=="delete"` | claim_snapshots：**0/141 路径被任一快照提到**；队列袋：以 `action=="delete"` 精确匹配 **0/141**（若仅做子串粗匹配则 141/141 命中，因这些路径散见于历史袋的其它清单，不足以定归属）；`.runtime/workspace_alerts/stash_notice.json` **不存在**，`git stash list` 为空 → 排除"被 stash 保存"的解释。现存旁证仅一条：`.runtime/audit/landing_guard.jsonl` 1 行 `{"ts":"2026-09-26T01:04:47+08:00","event":"gitwt_punchthrough","verb":"reset","worktree":"…worktrees\\w0","main_head_before":"93e55f2f46…","problems":["主仓 HEAD 93…"]}`（该 worktree `reset` 打穿主仓的事件，与 0029 袋 dead_reason 同刻） | 无法判定（141 件删除无现存在册归属证据；只有同刻 punch-through 事件可作时间邻接旁证） |

| 1e | daemon 与 lease 实况（补 1c） | 读 `.runtime/commit_queue/belt_daemon.heartbeat` mtime + `belt_daemon.lock` | heartbeat 内容 `{"pid": 33160, "wall_ts": 1790404746.225}`，采样时刻 mtime 距现在 **17.0 s** → daemon 在跳；`lease.present=false` 与 `processing=0` 互洽（无在途袋） | 实测读数 |
| 3d | CAND-GOVTEST-005 修复位的落地态 | `git status --porcelain -- <candidate_module_registry.yaml>` / `-- <gate_registry.yaml>` | 该册状态 **`MM`**（index 与 worktree 双侧均有未提交改动）→ 去重后的字节不在 HEAD；`gate_registry.yaml` 无 status 行（工作区/index/HEAD 三面一致） | 在途（修复未落地） |
| 9c | 交接书称"现声明已是 181" | HEAD grep + 解析（见 §4 附读） | HEAD `gate_registry` 声明=181/实=181（一致）；GATE-21 台在 HEAD 已含 `_book_surface`=2、`F-AUDITFIX-SELFREAD-01`=1 的"暂存优先、次 HEAD"两面判代码，另有 `disk_text = p.read_text`=1（工作树面仍并存判） | 已落地（"读盘不读 dev 册"的旧缺陷在 HEAD 已被两面判取代；174/180 历史态无法在 HEAD 复现） |

| 5f | 撞号的历史回执（补 5a-5e） | 全 700 袋 `dead_reason` 正则扫 `GateRegistrationError: priority=… 冲突` | 含撞号注册失败的袋 = **6 封**：4 封 `priority=77 DOC-HEADER-SUITE × BLUEPRINT-FORMAT`、2 封 `priority=110 CAPABILITY-LOOKUP-REQUIRED × BLUEPRINT-FORMAT`；HEAD 现值 BLUEPRINT-FORMAT=130 已同时避开 77/110（详见 §4b 表） | 在途→已解（回执态 vs HEAD 态） |
| 9d | GATE-21 现判（补 9a-9c） | 主区实跑 `python scripts/…/validate_static_manifest_drift.py --check` | `gate_registry.yaml (declared total == section length)` = **PASS**；整台 = **FAIL**，唯一红点在 `script_manifest.yaml`：`磁盘 461 脚本 ≠ 实际 516 脚本`、`104/516 个脚本缺少 __manifest__ 块`（原文见 §4c） | 实测读数 |

（主表毕。以下 §2~§7 为附表与读点原文）

## 2. 附表：dead 签名 top 20（首 60 字符聚类，700 封顶层袋）

| 名次 | 袋数 | 签名（首 60 字符，空白折叠后） | 主要 session（袋数） |
|---|---|---|---|
| 1 | 85 | `网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-com` | st-sweep-tail-20260923:16 / st-commitspeed-tbl-20260924:16 / st-qcure-20260925:6 |
| 2 | 71 | `landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/` | st-library-final-20260924:10 / st-align-dirty-20260924:7 / st-k4-20260923:6 |
| 3 | 48 | `网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 无 creation_token，` | st-cmd-20260924:11 / st-commitspeed-tbl-20260924:9 / st-mapbuild-20260924:8 |
| 4 | 47 | `网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATI` | st-mapbuild-20260924:11 / st-commitspeed-tbl-20260924:7 / st-sweep-tail-20260923:5 |
| 5 | 36 | `landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root` | st-cmd-20260924:11 / st-commitspeed-tbl-20260924:9 / st-combine-20260923:8 |
| 6 | 30 | `网关落盘失败（COMMIT_FAILED）: 门禁 TTL-METADATA 阻断: FAIL: .runtime\co` | st-cmd-20260924:21 |
| 7 | 29 | `NOTHING_TO_COMMIT 但快照未真应用 (blob 与 old_dev 不符: ['docs/_workin` | st-stress-20260923:29（单会话独占簇） |
| 8 | 22 | `网关落盘失败（COMMIT_FAILED）: 门禁 GATE-VOCAB 阻断: [VOCAB-HARDCODE] 新增` | st-chainpile-20260922:8 / st-ailayer-final-20260924:5 |
| 9 | 18 | `网关落盘失败（COMMIT_FAILED）: 门禁 COMPLEXITY-GUARD 阻断: [NO-HIGH-COMP` | st-cmd-20260924:6 |
| 10 | 16 | `网关落盘失败（COMMIT_FAILED）: 门禁 R5-DIGIT-SUFFIX 阻断: R5 数字后缀目录禁止: d` | st-cmd-20260924:7 / st-qmine-20260925:3 |
| 11 | 15 | `网关落盘失败（COMMIT_FAILED）: 门禁 IMPORT-INTEGRITY 阻断: IMPORT-INTEGR` | st-commitspeed-tbl-20260924:8 / st-wm1-wave0-20260924:3 |
| 12 | 14 | `cascade_stale: 基底重校验不适用 ['docs/01_policies_and_standards/_re` | st-audit-fix-20260924:5 / st-commitspeed-tbl-20260924:3 |
| 13 | 10 | `网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 字段头部不完整（ARCH-031）` | st-ailayer-p1-20260923:4 / st-cmd-20260924:4 |
| 14 | 10 | `网关落盘失败（COMMIT_FAILED）: 门禁 BLUEPRINT-FORMAT 阻断: BLUEPRINT-FOR` | st-cmd-20260924:4 / st-chainpile-20260922:2 |
| 15 | 10 | `网关落盘失败（COMMIT_FAILED）: 门禁 ORPHAN-MODULE 阻断: 孤儿模块在代码库中无任何 imp` | st-commitspeed-tbl-20260924:4 / st-ulib3c-20260923:2 |
| 16 | 9 | `网关落盘失败（COMMIT_FAILED）: 门禁 TEST-SOURCE-CONSISTENCY 阻断: TEST-S` | st-sweep-tail-20260923:3 / st-commitspeed-pkg8-20260925:3 |
| 17 | 9 | `网关落盘失败（COMMIT_FAILED）: 门禁 DIRECTORY-CONTRACT 阻断: [GATE-DIREC` | st-cmd-20260924:5 / st-pipeline-final-20260924:2 |
| 18 | 9 | `网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH` | st-ulib3c-20260923:6 / st-cmd-20260924:3 |
| 19 | 9 | `网关落盘失败（COMMIT_FAILED）: 门禁 MAP-ALIGNMENT 阻断: [FRONTEND-MAP] F` | st-audit-all-20260924:2 / st-library-final-20260924:2 / st-mapcensus-20260924:2 |
| 20 | 9 | `网关落盘失败（COMMIT_FAILED）: 门禁 ALGO-NOTE-SYNC 阻断: ALGO-NOTE-SYNC：` | st-cmd-20260924:6 |

合计：700 袋、110 个 distinct 签名簇、top 20 覆盖 483 袋（69%）。

## 3. 附引：注册表三向合并死信家族的按册分解（71 袋）

按 `dead_reason` 内被点名的册路径 + 身份键二次分解（`probe_B.py` §2b 输出）：

| 袋数 | 目标册 | 身份键可读性 |
|---|---|---|
| 20 | `module_translation_registry.yaml` | dead_reason 内无 `decl\|id=`（文本被截在键名前） |
| 19 | `capability_canonical_file_registry.yaml` | 同上 |
| 8 | `in_process_gate_registry.yaml` | 同上 |
| 5 | `ruling_registry.yaml` | 同上 |
| 5 | `fail_open_register.yaml` | 同上 |
| 4 | `candidate_module_registry.yaml` | 同上 |
| 3 | `candidate_module_registry.yaml` | `decl\|id=CAND-GOVTEST-005` |
| 2 | `infrastructure_registry.yaml` | 同上 |
| 2 | `registry_master_index.yaml` | 同上 |

→ `candidate_module_registry.yaml` 合计 7 袋（3 袋可读出 CAND-GOVTEST-005 身份键，4 袋 dead_reason 被截断在身份键之前），与 2b 全文匹配读数一致。

## 4. 附读：名册与门条原文位

- HEAD `gate_registry.yaml`：顶层标量 `total_gates: 181`，`gates` 段长 181；`generated_by: scripts/governance/generators/gate_registry.py` 路径下的生成器，`generated_at: 2026-09-22T22:18:47Z`（工作区同）。
- HEAD `in_process_gate_registry.yaml`：`total_gates: 103`，`gates` 段长 103，`unique_key: gate_id`。
- CREATE-GUARD 在 gate_registry 的完整在册条目（工作区=HEAD 同读）：

```yaml
gate_id: CREATE-GUARD
name: 'CREATE-GUARD: CREATE-GUARD（CommitGate, priority=60）'
entry: in-process (GitCommitGateway)
description: CREATE-GUARD
files_trigger: ''
always_run: false
category: commit_gate
status: active
source: commit-gate
own_scope: false
enforcement_channel: commit-gate
```

- priority 真源在代码 GateSpec：`gate_auto_registrar.py` L54-55 `不覆盖 priority：priority 从 GateSpec 读取…YAML 的 priority 字段仅 informational，不覆盖代码真源`；`blueprint_format_gate.py` L184 `return GateSpec(gate_id="BLUEPRINT-FORMAT", check=_check, priority=130)`、L233 `return GateSpec(gate_id="DOC-HEADER-SUITE", check=_union_check, priority=77)`。
- GATE-21 自洽台读面（HEAD 已含修复）：`validate_static_manifest_drift.py` L261-288 `_book_surface()`（docstring L264-266 原文点名 `F-AUDITFIX-SELFREAD-01（2026-09-26）：本台此前只读工作树字节…实测：dev 上 gate_registry 声明 174 而 gates 段 180 时，主区 --check 绿、干净树 rc=1`；L276-281 先 `_git_show_text(rel,"")`=index、再 `_git_show_text(rel,"HEAD")`），`_run_selfcheck()` L296 口径 `判两面：工作树面 + 提交绑定面（暂存/index 优先，否则 HEAD）`。HEAD grep：`_book_surface`=2、`F-AUDITFIX-SELFREAD`=1、`disk_text = p.read_text`=1。pre-commit 侧 hook `id: gate-21-manifest-drift`（`.pre-commit-config.yaml:688-696`，`args: ["--check"]`，`files:` 已含 `src/zephyr/gov_enforcement/commit_gates/.*\.py`）。
- `heal_derived_scalars` 三处同调在册：定义 `src/zephyr/shared/io/yaml_utils.py:729`；检测/修复通道 `validate_static_manifest_drift.py:178,197`；落地侧 `commit_queue_landing.py` 的 `_heal_derived_totals`（HEAD 命中 1 处定义 + L1732 调用，且该文件 `assert_snapshot_selfconsistent` HEAD 命中 3）。

## 4b. 附：HEAD priority 声明的机械核类（代码 vs 文档串）与撞号簇成因

对 5c 的 6 个撞号簇 + 2 个单例逐条回读 HEAD 原文行（`git show HEAD:<f>`），全部为 `return GateSpec(...)` 实代码声明，且**每簇两台同处一个文件**（"源台"与"聚合台 `_union_check`"）：

| priority | 源台（行号） | 聚合台（行号） | 同文件 |
|---|---|---|---|
| 70 | DANGLING-REFERENCE（`dangling_reference_gate.py:218,223`） | REFERENCE-INTEGRITY `:257` | 是 |
| 79 | （`blueprint_amodule_consistency_gate.py:209` 为文档串引用） | BLUEPRINT-HEADER `:282` | 是 |
| 80 | VOCAB-HARDCODE `vocab_hardcode_gate.py:212` | GATE-VOCAB `:244` | 是 |
| 82 | PERM-TRIGGER `perm_trigger_gate.py:382` | PERMANENT-SYSTEM-TRIGGER `:414` | 是 |
| 92 | NO-HIGH-COMPLEXITY `high_complexity_gate.py:197` | COMPLEXITY-GUARD `:231` | 是 |
| 113 | DEPGRAPH-PRE-REGISTRATION `depgraph_pre_registration_gate.py:318` | DEPGRAPH-ENFORCEMENT `:372` | 是 |
| 110 | CAPABILITY-LOOKUP-REQUIRED `capability_lookup_required_gate.py:359` | — | — |
| 130 / 77 | BLUEPRINT-FORMAT `blueprint_format_gate.py:184` / DOC-HEADER-SUITE `:233` | — | 同文件但 priority 不同 |

- 文档串与代码不同值的一处：`registry_code_anchor_gate.py` L177 文档串写 `GateSpec(gate_id="REGISTRY-CODE-ANCHOR", priority=106)`，L251 实代码 `priority=129`，文件头注释 L33 亦写 129。
- 死信账上的真实撞号回执（`dead_reason` 原文，属队列回执类证据）：**6 袋**含 `GateRegistrationError: priority=… 冲突`——4 袋 `priority=77 冲突——gate 'DOC-HEADER-SUITE' 与已注册的 'BLUEPRINT-FORMAT' 同 priority`，2 袋 `priority=110 冲突——gate 'CAPABILITY-LOOKUP-REQUIRED' 与已注册的 'BLUEPRINT-FORMAT' 同 priority`；回执原文并列"历史先例（后到者让位）：DATA-TASK 78->41 / RENAME-DEPGRAPH-SYNC 36->39 / ORPHAN-MODULE 86->89 / DOC-REF-BROKEN 88->91 / RULING-COMMIT-VERIFIED 77->109"。HEAD 现值 `BLUEPRINT-FORMAT=130` 同时避开 77 与 110。

## 4c. 附：GATE-21 主区 `--check` 实判（2026-09-26 现场）

`python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py --check` 在主区（脏盘）实跑输出：
`PASS [gate_registry.yaml]: OK` / `PASS [.importlinter forbidden_modules]` / **`PASS [gate_registry.yaml (declared total == section length)]`** / `PASS [rule_catalog_registry.yaml (declared total == section length)]` / **`GATE-21 FAIL: 1 static manifest(s) have drifted` → `FAIL [script_manifest.yaml]: WARNING: 104/516 个脚本缺少 __manifest__ 块`、`DRIFT: 磁盘 461 脚本 ≠ 实际 516 脚本`**。
→ 即：两册的派生标量自洽判据当前为绿；GATE-21 整台当前为红，红点在 script_manifest（与本册环节A的 gate 名册无关，但属"该台是否报 PASS"的现场读数）。

## 5. 附：12 项声称件的存在性矩阵（HEAD 之外补测）

| 件 | `git ls-tree HEAD` | 工作区盘上 | index | `git log --all -- <path>` 触达 commit 数 |
|---|---|---|---|---|
| `scripts/governance/replay_gate_verdicts.py` | IN-HEAD | — | — | — |
| `tests/governance/test_redblue_governance.py` | NOT-IN-HEAD | 不存在 | 不在 | 0 |
| `tests/governance/test_redblue_robust.py` | NOT-IN-HEAD | 不存在 | 不在 | 0 |
| `docs/_working/commit_speedup_campaign/99_FINAL_REPORT.md` | IN-HEAD | 存在 | — | — |
| `docs/_working/commit_speedup_campaign/60_deep_dive/DEEP_DIVE_R1.md` | NOT-IN-HEAD | **存在（未跟踪）** | 不在 | 0 |
| `docs/_working/commit_speedup_campaign/dead_triage.yaml` | NOT-IN-HEAD | 不存在 | 不在 | 0 |
| `docs/_working/commit_speedup_campaign/dead_triage_r2.yaml` | NOT-IN-HEAD | 不存在 | 不在 | 0 |
| `docs/_working/commit_speedup_campaign/90_verification/CAMPAIGN_STATE_SNAPSHOT.md` | IN-HEAD | 存在 | — | — |

（`git log --all -- <path>` 为 0 ＝ 全部分支历史中从未有任何 commit 触及该路径。）

## 6. 新增发现（交接书未提）

1. **`dead` 目录里混着一个子目录**：`.runtime/commit_queue/dead/archive_flashbiz_superseded_20260918/` 使 `ls|wc -l`=701 而真袋数=700（递归 714 件 json）。以 `ls` 计数为口径的"701 封"叙述偏 1，且 14 件历史归档袋被折叠。
2. **`status` 报的 dead 数与盘上顶层 json 数 700=700 一致** → 队列自身的账未坏，偏的是外层计数口径（见 1）。
3. **单会话独占死信簇**：签名第 7 名的 29 袋 100% 来自 `st-stress-20260923`，reason=`NOTHING_TO_COMMIT 但快照未真应用 (blob 与 old_dev 不符 …)`，全簇只指向 `docs/_working/registry_migration/stress/`；该目录族在 11b/11c 中另有 10 件 staged 删除且盘上已不存在。
4. **实载时装载器点名 28 条 files_trigger 病理**（15 台超宽 / 6 项死触发，见 5e），**CREATE-GUARD 不在任何一条里**——其 `files_trigger` 是空串而非模式，超宽与死触发两道体检都判不到它（与 7a/7d 连成一条完整链条）。
5. **实载 99/103 中跳过的 4 台 disabled 门里，2 台正是代码层 priority 撞号簇成员**（`GATE-VOCAB`@80、`PERMANENT-SYSTEM-TRIGGER`@82）→ HEAD 代码里这两组撞号靠 `enabled:false` 才未在链上并存。
6. **`REGISTRY-CODE-ANCHOR` 的 priority 文档串与代码不同值**：`registry_code_anchor_gate.py` L177 文档串写 `priority=106`，L251 实代码 `return GateSpec(…, priority=129)`（文件头注释 L33 亦 129）→ 名册生成/人工读注释皆会取到 106 这一不存在值。
7. **`immutable_tree` 与 `commit_immutable_tree` 两个键名并存于注释**（`_tree_view.py:5,8`、`git_commit_gateway.py:3015` 用后者；实际 YAML 键与 `_immutable_tree_enabled()` 读的是 `flags.git_operations.immutable_tree`）→ 注释真源与实际读键不同名。
8. **HEAD 里 `_heal_derived_totals` 与 `assert_snapshot_selfconsistent` 双在册**（HEAD grep 命中 2 / 3），配合 `heal_derived_scalars` 三处同调（§4 末条）→ 交接书所称"回补"在 HEAD 已是落地态而非待办。
9. **主区 index 净减 123 件**（HEAD 树 17903 vs index 17780），方向与 141 件 staged 删除 + 16 件新增一致：这批不是"HEAD 丢文件"，而是"index 主动摘除"，其中 131 件盘上文件仍在（11c）。

## 7. 我无法判定 / 需要人工看的事实缺口

1. **141 件 staged 删除的归属**：claim_snapshots 与队列袋的 `action=delete` 双路反查均 0 命中，stash 亦空 → 现存证据无法定归属，只有 `landing_guard.jsonl` 一条同刻 punch-through 事件（01:04:47，主仓 HEAD 93e55f2f46→16d58a652d）可作时间邻接旁证，人工看 `git reflog` / 该窗口的 worktree 现场。
2. **GATE-21 是否此刻 PASS**：HEAD 已含 `_book_surface` 两面判（L261-288），但"声明 174 vs 实 180 却报 PASS"的历史态无法在 HEAD 复现，未跑 `--check` 实判。
3. **daemon online=true 而 lease.present=false 的组合**：`status` 直读即如此（`head:null`），daemon 心跳源文件 `.runtime/commit_queue/belt_daemon.heartbeat` / `belt_daemon.lock` 存在，但"daemon 是否真在消费队列"须看 daemon 侧日志，本册未取。
4. **CREATE-GUARD "4488 次" 的数据源**：本册唯一可得的账本 `.runtime/audit/gate_execution_stats.jsonl`（1964 行，覆盖 09-15→09-25）最多单 gate 1519 次调用，无法复现 4488；若交接书另有一本（如 09-26 当天未落账窗口或另一仪器件），该件路径未定位。
5. **31 台 own-scope 内容台的逐台接线核对**：只读了共享原语 `_split_own_foreign` 的语义与 CREATE-GUARD/`_diff_helpers` 的 index 读点，未逐台确认是否都接了该原语（6g 复现设计的反证位需要这一步才能闭合）。
6. **priority 撞号 6 簇中"未实载"成员的定性**：`DANGLING-REFERENCE/REFERENCE-INTEGRITY(70)`、`BLUEPRINT-AMODULE-CONSISTENCY/BLUEPRINT-HEADER(79)`、`COMPLEXITY-GUARD/NO-HIGH-COMPLEXITY(92)`、`DEPGRAPH-ENFORCEMENT/DEPGRAPH-PRE-REGISTRATION(113)` 在实载 99 台集合内未构成同 priority 并存，但它们是"聚合台薄工厂同名保留"还是"两处独立注册"须人工看各文件 GateSpec 上下文。

## 附：探针与账本路径（复核用）

- 临时探针（本册唯一写入的仓库外产物，位于 .runtime 临时区）：`D:\ZephyrAlpha\.runtime\tmp\total_command_closeout\probe_A.py`（dead 签名聚类）、`probe_B.py`（三册结构/去重/CREATE-GUARD 条目/家族分解）、`gate_priority_head.json`（HEAD GateSpec 枚举落盘）。
- 读账：`.runtime/audit/gate_execution_stats.jsonl`（口径=每行 `ms` 字典按 gate 累加，1964 行 / 09-15T18:19→09-25T23:21）、`.runtime/git_performance_log.jsonl`（4.2MB，`elapsed_s` 口径，本册未用于 gate 归因）、`.runtime/audit/landing_guard.jsonl`（1 行）。
- 全程未跑 pytest；ClickHouse 未被本册任何探针访问。
| 8a | 交接书称 immutable_tree 现值 | `git show HEAD:config/flags.yaml \| grep -n immutable_tree` | HEAD L52 `    immutable_tree: false`（工作区 L52 同值 false）；注释 L50-51 原文：`两棵不可变树（HEAD^/index 树），出厂 OFF=现行为；ON=重放 verdict 全等判据达标后 由 Owner 门位翻转（宪法 第 5 节）` | 已落地（现值 OFF） |
| 8b | 消费面 | `git grep -n "immutable_tree" HEAD -- src scripts config` | 判定读点：`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:218 def _immutable_tree_enabled()`，调用点 `git_commit_gateway.py:2935`（`if not _immutable_tree_enabled(): …`）与 `:3015`（`flag commit_immutable_tree=ON 时，门禁链跑在 CommitTreeView(HEAD, index树)`）。其余在册引用：`commit_gates/_tree_view.py:5,8`（CONSUMERS/INVARIANTS 注释：`生产影响面=flag commit_immutable_tree 单点门控（出厂 OFF=零门禁导入路径；ON=门禁链整体跑替身，15 台全索引门经 SHARED_INDEX_WITHOUT_OWN_SCOPE 分道回本体 gateway）`）、`commit_gates/_diff_helpers.py:33,242`、`rule_bridge/gate_cache_preflight.py:49,321`。注：注释里出现两个键名（`immutable_tree` 与 `commit_immutable_tree`），实际 YAML 键为 `git_operations.immutable_tree` | 实测读数 |
| 8c | 交接书称"一次入队 flag 被读成 OFF 而盘上与 HEAD 都 enabled: true，重试即通过"（疑静默降级） | 读 `git_commit_gateway.py` L218-236 源码 | **静默降级路径在册**：函数体 `try: … yaml.safe_load((_root/"config"/"flags.yaml").read_text(...)) … return bool(git_ops.get("immutable_tree", False))` / `except Exception:  # noqa: BLE001 — fail-closed OFF` `return False`（L235-236）。任一次读盘/YAML 解析异常（含并发写截断、编码、临时锁）都回落 OFF 且**零日志、零异常上抛**；docstring L223 自述口径为"fail-closed OFF：任何异常都回退现行为（门禁输入源不动）"。另有 L232 `or {}` 与 L233 `(data.get("flags") or {}).get("git_operations") or {}` 两级默认空 dict → 结构缺键同样返回 False | 已证实（存在"读失败即当 OFF"的静默降级，代码在册；单袋复现性无法由现存证据判定） |
| 9a | 交接书称 GATE-21 自洽台读盘不读 dev 册（曾声明 174 vs 实 180 报 PASS） | `git grep -n "GATE-21" HEAD -- docs/01_policies_and_standards/_registry` | GATE-21 = `scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py`（在册线索：`capability_canonical_file_registry.yaml:541` "调用者：GATE-21（validate_static_manifest_drift.py --check 调本生成器检测漂移）"）。HEAD 两册现值：gate_registry 声明 181/实 181、in_process 声明 103/实 103（见 4a/4b），**当前无"声明≠实数"残留可测**；读盘/读 HEAD 的取数路径见 §4 附读 | 部分取证（现值自洽，历史 174/180 态不在 HEAD） |
| 9b | 交接书称 heal_derived_scalars 在册并被两侧同调 | `git show HEAD:src/zephyr/shared/io/yaml_utils.py \| grep -c "def heal_derived_scalars"`；`git grep -n heal_derived_scalars HEAD` | HEAD 定义存在：**1** 处（`src/zephyr/shared/io/yaml_utils.py:729`）。HEAD 消费方仅 1 文件：`scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py` L172（注释指真源）/ L178（import）/ L197（`out, changes = heal_derived_scalars(text, pairs)`）。docstring L737 自述"落地侧（`commit_queue_landing._heal_derived_totals`）与检测侧同调" → 落地侧是否真调用本函数须查 `_heal_derived_totals`（见 §4） | 已落地（函数在 HEAD，检测侧调用在册） |
| 10a | 总筹指令 环节A-10 四把对账读数 | 见命令列（HEAD 层 grep -c） | `scripts/governance/commit_queue_landing.py` `assert_snapshot_selfconsistent` = **3**；`scripts/commit_queue.py` `old_item.get("base_head")` = **1**；`src/zephyr/shared/io/yaml_utils.py` `def heal_derived_scalars` = **1**；`scripts/commit_queue.py` `W17 治本` = **1** | 已落地（四符号全在 HEAD 有在册命中） |
| 12a | 交接书称 replay 台与红蓝两件测试"从没跑过/未入册" | `git ls-tree HEAD -- <path>` 逐件 | `scripts/governance/replay_gate_verdicts.py` = **IN-HEAD**；`tests/governance/test_redblue_governance.py` = **NOT-IN-HEAD**；`tests/governance/test_redblue_robust.py` = **NOT-IN-HEAD** | 见 §5（工作区/分支侧存在性另测） |
| 12b | 交接书称 commit_speedup_campaign 五件在册 | `git ls-tree HEAD -- …` 逐件 | `99_FINAL_REPORT.md` = **IN-HEAD**；`60_deep_dive/DEEP_DIVE_R1.md` = **NOT-IN-HEAD**；`dead_triage.yaml` = **NOT-IN-HEAD**；`dead_triage_r2.yaml` = **NOT-IN-HEAD**；`90_verification/CAMPAIGN_STATE_SNAPSHOT.md` = **IN-HEAD** | 见 §5 |

（表后续条目 6/7/11 追加中）
