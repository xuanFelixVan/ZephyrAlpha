---
ttl: task_bound
completes_when: 八波全部落地且落地面连续两轮回归零问题+红蓝两轮零 FAIL
---

# 施工方案 · 八波排产册（W 册）

> **上位**：环节全集=`00_master_skeleton.md`；判定=`01_adjudication_master.md`（Z 编号在此复用，不另发明口径）；证据=`dossier_A..H`。
> **排产律**：线内先挖后干（每包先补六向台账与能红判据再动码）、线间并行流水（波内多道并发、波间硬依赖串行）、内收原则施工（新增件必声明替代/合并对象，禁第二真源）。
> **本方案与交接书叙事的三处关键改道**（全部由实测驱动，非偏好）：
> 1. **撤下"own-scope 治本是落地前置"**——六图役 7 袋实测死于 13 类不同死因（TRANSLATION-COVERAGE 11、CREATE-GUARD 8、GATE-PRECOMMIT-RUN 2、基底不可知 2、RULING-REFERENCE 2…），被点名的两袋一个是 `WorktreePunchThroughError`（EV-02 reset 打穿主仓）、一个的死因文件就在它自己的 38 件清单内。全 dead 文本含"外来 staged"仅 2 封。⇒ 波 1 不再花预算改 own-scope，改为"新建件三件套补齐 + 悬空裁定号清除"这条机械通道（Z-07 降级为观察项 W-22）。
> 2. **新增一条 P0 执法洞**——进程内 `auto_register_gates` 实载 **99** 台，名册声明 **103**：**4 台门静默不装载**＝提交面空转（与"配置只被一条路径消费"同族病）。这比任何提速都优先。
> 3. **（外部审查新增）先建"可信层"再施工**：审查判定本仓的系统性病是**声明面与强制面脱钩**（状态用散文承载、规则在册却无门禁或指向死库、门在名册却不在装载面/触发面）。故新增 **波 1A**（交付状态迁回既有 73 列机读 `tasks` 表、交付判据从 `COMPLETED` 改 `VERIFIED`、触发面三列对账、规则↔执法面对账、死库与死指针清理、散文交接书退役），排在一切施工之前；原波 1 顺延为 **波 1B**。详见 `review_ext_verdict.md`。
> 4. **抢救优先级高于一切施工**——六图车道分支基点落后 dev 237 个 commit、**零自有 commit**、脏项 272；波2 车道 169 件同理。它们一旦被外部重置抹掉就是永久损失（本仓已发生多次）。故波 0 只做一件事：把全部在途字节固化成"清单+sha256+双镜像"。

## 波 0 · 现场固化与安全垫（1 道，串行，最先做，零门禁风险）

| 包 | 内容 | 判据（可跑） | 车道 |
|---|---|---|---|
| 0.1 | 车道现场快照（**必带 worktree 守卫**：`git rev-parse --show-toplevel` 必须等于该目录，否则 git 向上解析到主仓、把主区脏面记成车道脏面——本班首版就踩了这个，25 个 `.aidrafts/*` 普通目录全被染成同一组数）| 原 11 条车道现场快照：对 `.aidrafts/lane_ff_*`、`.aidrafts/st-mapbuild-20260924`、`.aidrafts/st-audit-fix-20260924`、`.worktrees/st-ailayer-final-20260924` 等逐个出"文件清单+每文件 sha256+`git status --porcelain`+落后 dev 的 commit 数"，落 `docs/_working/total_command_closeout/snapshot/`（机生禁手改）并镜像 `.runtime/tmp/` + `G:\zephyr_cold\`（G 侧实测 1454 GiB 可用） | 快照件数 == 各道脏项数；抽 3 件 `sha256sum` 复算一致 | 1 |
| 0.2 | 热件盘-HEAD 键集合差自检（capability/ruling/issue/gate/translation/ROOR 六册）：缺即按"HEAD 为基纯插入"修（本册 §配方 R-1，已实跑：capability 册补回 16 条被陈旧快照抹掉的条目、他人 1 条在途保留、YAML 复解析过） | 六册 `盘缺HEAD == 0`；写后进程外 `yaml.safe_load` + 条目数复算 | 1 |
| 0.3 | 磁盘安全垫：D 现 41G/95%。零风险回收=git worktree prune + dead 归档 tar（不删）+ pack gc；**定熔断阈值**：可用 <25G 停大批落地、<15G 停一切写批（Owner 默认已生效，见 ⚑-6-9） | 回收前后 `df` 读数入台账；无删除动作 | 1 |
| 0.4 | 登记"备份护甲落后"新案：`D:\zephyr_t1_backup` 侧 `strategy_intake` mtime=02:49 早于 T1 产物 07:47 ⇒ 声称的 10 分钟 robocopy 镜像未覆盖后段（E 册）；只登记不定性 | 镜像 mtime vs 产物 mtime 对比表 | 1 |
| 0.5 | 登记"sleep-loop 保活进程"与宪法第 9 节第 3 条对撞（PID 37548 每 300s re-register，持 3 个业务文件 claim；T1/做T 真身 PID 3584/33548 已亡）⇒ **它不是工作会话**，避让判据要从"活会话"改判为"活 claim" | `tasklist` + claim 台账对照 | 1 |

**出口判据**：任何一条车道的字节都有可复算清单+双镜像；六册键集合差为 0；波 1 可开工。

## 波 1A · 可信层（外部审查后新增，**排在一切施工之前**）

> **为什么插这一波**：外部审查（`review_ext_verdict.md`）判定本仓的系统性病是**"声明面与强制面脱钩"**——规则/名册/判据/状态/交接全都写下来了，但缺少让它们必然被执行、被消费、被对账的那一层。原方案 122 个 W-xx 绝大多数在治**表现**（某册漂移、某门未装载、某件未落地），没有一条在治**脱钩本身**；照原方案做完，下一轮仍会长出第 12、13 份互相矛盾的交接书。
> **本波只做三件事，全部内收（不新造册、不新造库、不新增门禁台数）**：

| 包 | 内容 | 出口判据（可机械复算） |
|---|---|---|
| 1A.1 | **交付状态迁回既有机读真源**：`data/databases/governance.db` 的 `tasks` 表（实测 **73 列 / 2546 行**，最近 5 行是 09-23 测试夹具、近 7 日仅 41 行变动）已含 `acceptance / deliverables / artifact_paths / files_in_scope / depends_on / blocked_by / claimed_by / session_id / verification_status / construction_status / completed_gates / blocked_gates / rollback_instructions / allowed_touch / forbidden_touch / approval_required / requires_rb_check / safety_level / ai_autonomy_level / idempotent / root_cause_analysis` 等列 ⇒ **分两步建卡**（第一步只建需施工追踪的约 30 个包，21 必填字段齐；其余等对账器机生视图后再迁。实测建卡有 GOV-TASK-001 v3.2.0 强制校验，缺 `source_blueprint/source_section/directive/applicable_rules/allowed_touch` 直接拒建）（入口＝`TaskRepository.create_and_ready()`，`task_repo.py:1290`；`DB_PATH` 实测＝`data/databases/governance.db`）。**Owner 门位项一律 `approval_required=True`**，从源头杜绝 AI 自裁高险项 | 第一步卡数 == 波 1A/1B/2 的包数（约 30）；每张卡 21 必填字段非空且路径为绝对路径（建卡器自检）；`PYTHONPATH=scripts/governance python scripts/governance/_tasks/task_summary.py --json` 一条命令出分布 |
| 1A.2 | **交付判据从 COMPLETED 改 VERIFIED**：`TaskStatus` 实测 14 态里**早已区分** `COMPLETED`（自称完成）与 `VERIFIED`（独立核验）⇒ 规定：`COMPLETED` 不算交付；升 `VERIFIED` 必须①`artifact_paths` 非空②逐件 `git cat-file -e HEAD:<path>` 为真③涉判据者 `requires_rb_check` 有红蓝证据锚。这把 `92` 册的 G-05 从"散尺"升级为**状态机约束**（净零对价：G-05 并入，不另立） | 抽 20 张 `COMPLETED` 卡复算：无 HEAD 证据锚者必须**升不了** `VERIFIED`（红证） |
| 1A.3 | **触发面三列对账表**（生成器产出，禁手工维护）：每台门一行＝`名册声明 / 进程内实载 / files_trigger 在 HEAD 树的命中文件数`；任何"声明有、实载 0 或命中 0"的门自动进红名单。**一张表同时收敛三个悬案**：名册 103 vs 实载 99、`CREATE-GUARD` 因 `files_trigger=''` 每链全跑（实测 1519 次/19186s）、三台密钥门因 `files_trigger` 是**路径子串**匹配而恒零命中（预跑器自己就打印 `files_trigger 死触发（HEAD 树零命中）`） | 表可复算；红名单非空即报；新增门必须三列齐才准入 |
| 1A.4 | **规则↔执法面对账尺**：规则号有两种写法（册内 `TRAE-060`／门禁文案 `trae_060`）⇒ 别名归一后覆盖率实测 **80/86＝93.0%**（naive grep 只给 76.7%，不可用）；6 条零匹配＝`trae_057/066/074/076/078/083`，其中 **074 worktree 基底新鲜度、076 worktree 提交持久化**正是本战役反复失血的域。二级判定必须区分"被提及"与"真执法"（进程内调它的判据函数能否改变结果） | 覆盖率进 ROOR 派生字段；6 条逐条定性（补执法面／改判据面／退役） |
| 1A.5 | **死库与死指针清理**：`data/zalpha_metadata.db`（`trae_034` 永久规则明文指向它）实测 **0 字节**，而活库是 `governance.db`（203MB，今日 16:01 仍在写）⇒ **同批改规则里的库路径**（禁留死指针）；`data/databases/` 下另有 `depgraph.db`（0 字节但被 **34 个 .py 引用**）、`integrator_progress.db`、`progress.db`、`scheduler_progress.db` 全 0 字节 ⇒ 逐个判"复活／改指活库／退役"，判据＝消费者数 + 有无活替代；`data/backups/zalpha_metadata_*_pre_close.db` 有 6+ 份 6–7 月备份（该层被反复 pre_close 过，取证时读它） | 0 字节库数 → 0（复活或退役）；34 处 `depgraph.db` 引用逐条有归属；读侧探针失败必抛（禁静默降级） |
| 1A.6 | **交接书退役**：自 1A.1 落地起，跨会话交接＝"卡集合 + 一条查询命令"（按 `session_id`/`blocked_by`/`verification_status` 出视图）；散文只允许承载**为什么**（裁定理由），不允许承载**是什么状态** | 下一次多会话合并的人工归并工时 ≤1 小时（本轮实测约 3.5 小时、40+ 处叙述与盘面不符、21 簇重复立案） |

**本波与"内收原则"的关系**：1A 全部复用既有资产（`tasks` 表、`TaskStatus.VERIFIED`、`task_summary.py`、ROOR、既有门），**净增脚本 1 个**（触发面/规则面两张对账表的生成器，可合一），**净零对价**＝替代 G-05 散尺 + 替代 11 份散文交接书这一整类工件 + 替代三处各自为政的门禁排查。

## 波 1B · 提交链解毒（原波 1，2 道并行，串行于波 1A）

| 包 | 内容 | 死因对症 / 判据（先证能红） | 车道 |
|---|---|---|---|
| 1.1 | **（W5 复算后重写）不是装载缺口**：`enabled:false` 恰 4 台且 `103−4=99`==实载 ⇒ 无装载失败。本包做三件事：①四台（`CAPABILITY-OVERLAP`/`GATE-VOCAB`/`ALGO-FLOW-LINK`/**`PERMANENT-SYSTEM-TRIGGER`**）逐台定性"为何禁用、禁用期间有无违规落地、该不该恢复"（**恢复属 ⚑-6-3，禁自裁**）；②`PERMANENT-SYSTEM-TRIGGER` 单独立案（它与"永久系统四要素"红线直接相关）；③把"名册 vs 实载 vs 触发面命中"做成**常设**对账表（不是修一次就算） | 对账表三列可复算；四台各有归因行；红证=人为把一台改成 `enabled:false` 而对账表不点名 ⇒ 尺必须红 | 甲 |
| 1.2 | **同 id 双条册**：`candidate_module_registry.yaml` 的 `CAND-GOVTEST-005`（HEAD 实测 2 条异体；全册扫出同 id 双条仅此 1 组）。做法=保留信息更全者＋并入对方独有字段＋被并者改号或降级为议题条目（Z-05，语义零删除） | ⚠盘上该册处于 `MM`（他道在途）⇒ 必按 R-1 配方以 HEAD 为基重放，禁整册覆写。红证=合并器对该册的三向合并能过（先复现死：改一条内容→必报身份键冲突） | 甲 |
| 1.3 | **priority 撞号的真身**：两册条目根本无 priority 字段（真源=GateSpec）；实载层撞号 0 簇，代码层 6 簇全是"源台+聚合台 `_union_check`"同值对（2 簇靠 `enabled:false` 才不并存）。⇒ 只补"聚合台与其吸收台不得在实载层同号"的断言尺 + 把这 6 对显式注为设计内同值（禁改数值） | 红证=人为让两台实载门同号，尺必须红 | 甲 |
| 1.4 | **REGISTRY-CODE-ANCHOR 漂移** 文档串 106 vs 代码 129；**GATE-21 FAIL 真红点**=`script_manifest.yaml` 磁盘 461≠516 | 生成器重算（禁手改机生册）；红证=删一行清单→尺红 | 甲 |
| 1.5 | **CREATE-GUARD 触发面**：`files_trigger=''`+`always_run:false`，成本源=`create_guard.py:527` 每类一次全树 `git grep`。实测 1519 次/19186s/均 12.63s（09-25 后均 24.09s，占全部门 141565s 的 13.6%）⇒ 登记 files_trigger 或改 own-scope 差分（**不退役**，Owner 明令） | 红证=新文件缺 token 时必拦（现状已能红，改后须仍能红）+ 重放 100 笔 verdict 全等 | 乙 |
| 1.6 | **flag 三态读**（Z-10）：读到 ON／读到 OFF／读不到必报红点名 | 红证=把 flag 文件改坏→必须报红而非当 OFF 拒投 | 乙 |
| 1.7 | **入队预检旁路**：`requeue` 与 `enqueue_item` 直调补 `run_enqueue_preflight`；28 件纯格式类落地侧自动修，20 件必拒类点名 | 红证=直调旁路投一件缺 token 新文件→必被拦 | 乙 |
| 1.7b | **队列「失败摘除 + 后继袋重建」**（R-L）：一袋死掉后其后各袋必须继续前进并按新组合重跑（对标 GitHub Merge Queue／GitLab Merge Trains／Zuul gate 三家同构）；与既有 B5 毒药熔断合并，不新造机制 | 红证：造一袋必死者，现状整链停摆（实测 pending=0/dead≈700），改后其后各袋必须落地或各自具名死因 |
| 1.7c | **死信属主制 + 复发熔断**（R-M）：每封死信落 `owner_session` 与 `first_dead_at`；同签名复发 3 次即熔断并升级为根因工序（禁继续重投） | 新死信 24h 内有属主与归因签名 |
| 1.8 | **从未入库件的捞回**：红蓝两件测试（`test_redblue_governance.py`/`test_redblue_robust.py`）、`dead_triage.yaml`/`dead_triage_r2.yaml` 在**全部分支历史零 commit**，`DEEP_DIVE_R1.md` 仅盘上未跟踪 ⇒ 先按 path+blob_sha256 反查队列 blobs 与 `.runtime/tmp`，双证齐才定"缺失" | 四态核对表（未落地件唯一存活处=队列 blobs） | 乙 |
| 1.9 | **不做**：通用逐文件三方合并（封矿在册）；own-scope 大改（证伪，仅保留 W-22 观察） | — | — |
| 1.10 | **W-180.1/.2/.4（外部终审新增红线，一切判据类读数的前置）**：`ch_reader.query()` 返回的是 **TSV 字符串**，按下标取值取到的是真实值的**首位数字**（病样本 7/7 全对上：4←467、1←128、3←375、7←729、5←5217、8←89,586）；`count()` 失败返回 0 会伪装成"空表"；交接令要求的"会抛错的 reader"在数据层**根本不存在**（全仓 grep `query_strict/strict_query` 零命中）。⇒ 建 `query_rows()`（返 `list[tuple]`，失败 raise）+ `count_strict()`（把"查询失败"与"真 0 行"分成两态）+ `scripts/data/ch_probe.py` 标准探针（查询原文/传输路径/耗时/行数/时间戳 JSONL）+ 静态扫描尺（`query(...)` 返回值下标或 for-in＝违规，own-diff 作用域）。**不改 `query()/count()` 现行为**（12+ 存量消费者零迁移成本，内收） | 红证=去掉 raise 尺必红；塞一个 `ch_reader.query(x)[0][0]` 的文件尺必红；存量 12 文件（变量名 `tsv` 的正确用法）零误报；探针跑 §7.1 三病样本各一次给正确态 |

**出口判据**：`gate_prerun` 对任一 38 件袋可跑出"内容硬阻断 0"；装载台数==名册数；两本热册键集合差 0。

## 波 2 · 存量成品抢救落地（4 道并行，串行于波 1）

> 统一配方（本方案已实跑验证，见 `11_rescue_playbook.md` §配方 R-2）：三件套（token+翻译+depgraph 节点+15 字段头注）与件**同袋**；袋 ≤38 件；一袋一域，跨域袋写 `--allow-multi-domain` 留痕；入队前 `gate_prerun` 跑到硬阻断 0；落地只认 `git show HEAD:`；每袋落地后 `git log -1 --name-only` 核归属。

| 包 | 现场 | 件数（实测） | 专属死因处方 |
|---|---|---|---|
| 2.1 六图役 | `.aidrafts/st-mapbuild-20260924` | 30 施工件 **HEAD 命中 0/30**、33 件 `??`、脏项 272、零自有 commit | ①先补 creation_token（8 袋里 8 封死于 CREATE-GUARD）②TRANSLATION-COVERAGE 11 封＝`add_module_translation` 必须**在主仓跑**且 plain-zh ≥8 字 ③`alignment_checklist.md` 里 `裁定 414 号（HEAD 册查无）/#415` 是 HEAD 查无的悬空号（dead 0040 就死在这）⇒ 改成"六图战役采认/六图 schema 总裁"文字，落地后由取号器在正式通道补登 ④基底不可知 2 封＝enqueue 必带 `--base-head $(git rev-parse dev)` |
| 2.2 波2 役 | `.worktrees/st-ailayer-final-20260924` | 声称 169 件（D 册实测为准） | ①新 .py 三字段（`[TTL]`/`[STARTUP]`/`[CONSUMERS]`，scheduled 已废须写 scheduled_task；`[TTL]` 在前 30 行；module_id 禁照抄兄弟件）②ORPHAN-MODULE 要求零消费者新件与接线同袋（confirm_gate/registry_state_vocab/ai_secret_exposure 三件）③DEPGRAPH-ENFORCEMENT 要 `apply_depgraph.py --add-design-node` ④YAML 禁回填门禁取样字面量（ENCODING-SAFETY 打死整袋）、禁 CRLF |
| 2.3 全流通成品 | `.aidrafts/lane_ff_door`/`_books`/`_replay`/`st-audit-fix-20260924`、`.runtime/tmp/campaign_hold/` | 三批（A 册逐件列） | 门侧拒投类先补预检；账簿 §11–§13 是热台账追加⇒ 键集合差自证删除集==∅ |
| 2.4 CH 大声失败 + 灾备处方件 + 回测哨兵 | `.aidrafts/lane_ff_chfail`、灾备线、`scripts/backtest/t1_t2_handover.py`（`AM` 在 index 不在 HEAD）+ 其测试 `??` | — | ①CH-FINAL-GATE 会拦自家裸 `ch_writer.query`⇒ 先换会抛错 reader 再投 ②改名/换目录须重绑 creation_token ③哨兵 **cc=52/31/16 三函数 >15**（"52 层嵌套"是口径错名，实测最大嵌套深度 5）⇒ 拆模块级 helper（参数 ≤7），**禁调阈值** ④补 quant_methodology 号文 01~08、12（HEAD 与盘面双向皆无，N-1 洞） |

**出口判据**：`git ls-tree -r --name-only HEAD` 对每包点名的关键件命中数 == 计划数；`docs/_working/chain_fullflow_closeout/`、`map_build/`、`fullflow_mining/` 三处面在 HEAD 的件数写进台账并逐件抽验 sha。

## 波 3 · 数据与业务链治本（3 道并行）

| 包 | 内容 | 判据 |
|---|---|---|
| 3.0 | **W-180.3 + W-180.5（排在本波首位，先于 3.1）**：空壳表清单用 strict 通道复测重出（防 `count()` 失败返回 0 造出的**假空壳**——W-34 那份 9–10 张清单本身可能是 fail-silent 的产物）；并对 G 册与本终审所有 CH 直读结论行标注读数通道，高风险结论（空壳表／新鲜度／覆盖 gap）逐条 `ch_probe` 复测 | 复测表逐表给"strict 读数／传输路径／时间戳"三列，与旧清单逐行 diff 说明差异；W-34、W-178 的 gap 数以此刻 strict 读数为唯一口径（禁照抄 467/729/262 旧数） |
| 3.1 | `'str' > 'date'` 入口归一（Z-15）+ 两表回归 | 红证=喂 ISO 字符串与 date 两种入参都必须能跑通且比较结果一致 |
| 3.2 | 假绿交叉尺（Z-16）：`task_runs` 记账 ↔ 目标表真行数/最新业务日互证；不符报红并降级下游 | 自带反事实控制组：喂一行假 SUCCESS 到台账但目标表不动 ⇒ 尺必须红 |
| 3.3 | 供数守恒断言（EV-03 搬到数据链，内收不造第二套）+ 新鲜度用业务表 `max(date)` 不用 `system.` 面 | 同上，必须能红 |
| 3.4 | Fill 单一写者（按 D/G 册实测裁决后接线）+ 零样本必 WARNING | 消费者反查计数 >0 |
| 3.5 | 空壳表逐表三分（Z-17），登记 `known_data_gaps` 的补登记 | 登记数==缺登记数（键集合差） |
| 3.6 | 三处真源收敛（Z-18）：双源皆空不得判"空即干净" | 红证=一源有一行另一源空 ⇒ 必红 |
| 3.7 | miniQMT 四件口径回退修复（Z-19）**+ 口径回退哨兵尺** | 尺=grep 四件文案命中旧口径即红 |
| 3.8 | 35 个 HEAD 常红尺逐条修（Z-20）；四类假绿先修两条污染判据的 | 每条附 before/after；禁 skip/xfail/放宽 |
| 3.9 | hfq 族"来源独占"验证尺（Z-21 的自裁半） | 红证=写一条旧口径行→独占判据必红 |
| 3.10 | 图12 五处"消费方等一张没在产的表"补齐（Z-63） | 表实存且新鲜 |

## 波 4 · 灾备与冷存（2 道并行）

| 包 | 内容 | 判据 |
|---|---|---|
| 4.1 | **P-28 杀前身份复验**（Z-23）：比对登记时 name/cmdline/**create_time** 与活体；不一致记 `identity_mismatch` 跳过。⚠内收点：仓内 `kill_ghost_windows`（L717 一带）**已有 recheck 实现**，且快照里 `create_time` 现成未用 ⇒ 复用该判据，禁写第二套 | 3 例含红证：PID 复用/同 PID 换皮/正常命中各一，旧尺必在"PID 复用"场景误杀 |
| 4.2 | P-27 只读位（实测 `0o100444`）清位后打时间戳 + before/after 双证；**新案：单件失败拖垮整轮**（`code_backup.status=failed` 而 `robocopy_exit=0`）⇒ 改成"逐件失败记账+汇总判据"，不得一票否决整轮也不得静默忽略 | 台账记 failed 件数与轮态可分离 |
| 4.3 | **新案：`hardlinked` 近 5 轮恒 0**（声称的硬链去重从未生效）⇒ 定性是配置没接还是平台不支持，禁"写了就当有" | 硬链接数实测 >0 或明确退役该声明 |
| 4.4 | P-26 定性（Z-24）：`.worktrees` 实测占全树条目 **92.42%**（497798/538635），生效排除清单（config L34）确无它；336678 是 Mode B 增量 diff 计数 ⇒ 出"顶层目录分组复制清单"实测定论（结论直接喂 ⚑-3） | 分组占比表 |
| 4.5 | P-22 演练库 `LC_COLLATE 'C' TEMPLATE template0`；DR 可恢复性实证（Z-27，键名以实测为准：`last_backup_status`/`last_backup_log_verified`/`last_run_outcome=lock_skipped`） | 演练后计数对账 MATCH + 记录落 `logs/dr_drill_*.yaml` |
| 4.6 | keep 名单卫生（Z-28）+ 身份复验后的 shadow 记账（Z-29 前半） | 命中但被免死的清单产出 |
| 4.7 | 六图甲-1 已自裁部分：HEAD 侧 `ch_vm_backup` 已由 `3cdafddf1d` 再摘除 ⇒ 只剩**防回退锚**（再加回来即触门禁，属加严→自裁）；G 591.5 GiB vs F 600 GiB 差 7.4 GiB 无收敛通道 ⇒ 进 ⚑-3/⚑-5 事实披露 | 红证=模拟加回该目标→锚必须红 |

## 波 5 · 治理册派生化与安全线（2 道并行）

| 包 | 内容 |
|---|---|
| 5.1 | 六册派生化（Z-30/31/32/36：`entry_count`/`total_gates`/severity 变体/ssot_path↔covers）；`path_ownership_map.yaml:65` 的"未实现"改在册态（Z-62，磁盘 19191B 实存且 3 处直调：`daily_loop_master_switch.py:198`、`pipeline_events.py:1047`、`plan_engine/__init__.py:80`） |
| 5.2 | 取号器落地（Z-38，实测**不在 HEAD**）+ 悬空裁定号清雷（Z-33）+ 三把尺常设化（W-102） |
| 5.3 | 密钥门扫描面加严（Z-49，保持 warn）+ 注入防线立法（Z-50）+ 模拟盘账号按敏感处理（Z-51）+ 秘钥判别器前置件（Z-52 前半） |
| 5.4 | `10_d_data.md` 按分叉判据处置（Z-37）；`.gitignore` 判定书灭失风险改走"受控真源摘要"（不改保护面，⚑-6-6 的自裁半） |
| 5.5 | **新案登记**：`cmd_successor_20260925/` 51 件其实已在 HEAD（首入 `30505c93f6`，该 commit 标题自述"四门临时禁用+emergency 通道"）⇒ 不重做入库，改立**绕门审计案卷**：核该批是否符 emergency 通道使用条件（仅注册表/锁不可用），四门被禁的窗口内落了什么 |

## 波 6 · 死信终局与元问题收尾（2 道并行）

| 包 | 内容 |
|---|---|
| 6.1 | **（审查后降级）** 700 封死信**不做归档/废弃工程**——本仓挖矿 SOP §6 已有封矿先例：dead/ 的审计报告本就自动产出、Owner 对 dead/ 零参与，归档机制不消灭任何人工环节，反而要动「dead/ 永不清理」这条钉死不变量。本包**只保留一件事**：从死信袋与 `.runtime/commit_queue/blobs` 里**捞回"从未落地"的字节**（＝波 1B 的 1.8 与骨架 W-15），捞完即止；`blob_gc` 只允许 `--archive` 且必须排在捞回之后（blobs 是未落地字节的唯一存活处） |
| 6.2 | 283 问三态守恒复核（Z-44）；candidate 007 重编号（与 1.2 同根，须先后依赖）；api_server 心跳清障批 + 路由死代码一行修（Z-45）；snapself/EV 护栏按现 HEAD 重放（Z-46）；blob_gc `--archive`（Z-47）；VM/root 与临时目录按三段式隔离（Z-48） |

## 波 7 · 终验（1 道，冻结车道后）

- 7.1 逐目录 `python -m pytest`（**禁一次全量**：单进程收集必失败），带 `-p no:cacheprovider -W "ignore::pytest.PytestConfigWarning"`（只带前者会 INTERNALERROR），`--basetemp=.runtime/tmp/<独占>`；**在落地面复跑第二轮**（活树上两轮一致不算认证）。
- 7.2 五目录重点：`tests/ai_layer`、`tests/intelligence`、`tests/governance/fullflow`、`tests/gov_enforcement`、`tests/shared`（其中 20 个 Redis skip 记为覆盖洞不是绿）。
- 7.3 红蓝极限对抗补测：图14/图15 **从未被独立红队打过**；提交链场景⑦跨道连坐；灾备锁语义已有一轮（11 例）。攻击面=伪造节点/断链引用/越域挂载/INV-1 复制侵权/冒充 verified/绕过禁止边/PID 复用/热册整覆。发现即修，两轮零 FAIL。
- 7.4 表述纪律：**永不说"全绿"**，只说"该套件本轮检出 N 件通过，且已被证明能红（附变异/红蓝证据）"。

## 波 8 · 清洁与交付（1 道）

- 8.0 **先上原生锁，别靠自造补偿**（R-N）：波 0 固化时就对含未落地字节的车道 `git worktree lock --reason "unlanded bytes; see lane_rescue report"`——锁后 `prune`/`remove` 原生拒绝（即使目录已消失），`remove` 本身也拒绝不干净工作区；**自造的"逐文件 hash 对 dev"补偿要人工跑，原生的不用跑**。
- 8.1 逐文件 `git hash-object <f> == git rev-parse dev:<f>` 才 `worktree remove --force`；任一不等或不在 dev ⇒ 禁删（73 个 worktree 现数，`.worktrees` 目录项 52 是另一口径，两数勿并谈）。
- 8.2 `.runtime/tmp/*` 自有临时件清零（本战役目录：`total_command_closeout/`、`st-zmaster-20260926/`）；项目根与 `.runtime` 根零新增。
- 8.3 claim 全释放（判据只重读 `.ailocks/registry.json` 的 `locks` 键）、会话注销、死信归档路径确认。
- 8.4 终报 + Owner 一张菜单（`93_owner_menu.md`）+ 台账 `94_ledger.md` 定稿。

## 波 9 · 红队回流的补排产（原"编目有、排产无"的 21 件，W-140..W-162）

> 来源：两路独立红队攻击本班产出后的真漏清单（`02_field_corrections_and_new_cases.md` §六 X-64/X-65）。**本波与波 2–6 并行不冲突**，但 W-140/141 必须**先于** ⚑-1 呈报定稿（否则呈给 Owner 的前提不精确）。

| 包 | 内容 | 归位 | 出口判据 |
|---|---|---|---|
| 9.1 | **W-140 逐闸合规表**：把 12 个合规闸逐闸列"实现符号 / 消费者数 / 触发路径 / 是否 fail-closed"，已知起点：`programmatic_trading_guard` 与 `regulatory_report_generator` 非自身引用＝0，`manipulation_realtime_monitor` 仅 `order_manager.py:81` 的 TYPE_CHECKING 预接线，`compliance_rule_engine` 引用 1 | 先于 ⚑-1 | 表成文且每行给 grep 命令；"零消费者"清单可复算 |
| 9.2 | **W-141 盘后任务实态**：`schtasks /query /tn <task> /xml` 取 ACTION 原文，判"双入口分叉"真伪；伪则撤销该呈裁项 | 先于 ⚑-1 | 原文入台账（GBK 坑：取 xml 而非 csv） |
| 9.3 | ~~**W-142..W-151 波2 役 12 项逐件映射**~~ **（审查后删除：它是 G-05/R-I 对账器的一次性人工投影，对账器机生后这十二行自动产出，手工做＝造第二真源）** 原条目：波2 役 12 项逐件映射：E 双真源收敛／F 状态词表／G 价格笼子／H 清洗三引擎／I 权重单源／J Fill 写者／K confirm_gate 三雷／L 对账尺改硬／M 测试面／O 声明行归一，逐项给"实现件 / 在册态 / 消费者 / 缺口" | 波 2.2 前置 | 映射表 == 12 行；无表不算波 2.2 完成 |
| 9.4 | **W-152 HMAC 归属载体立项文档**（工程方案＋量级评估，非实施），落 `docs/_working/commit_speedup_campaign/80_hmac_proposal/proposal.md` | 新增 | 文件在 HEAD 且含量级评估节 |
| 9.5 | **W-153 红蓝场景⑦跨道连坐补跑**（两会话同域文件并发提交合并正确性，沙盘隔离，尺先证能红） | 波 7 追加 | 场景报告成文 |
| 9.6 | **W-154 机生 L↔F↔TDM 四向对账表**（治"环节两套编号并存"的手工漂移） | 新增 | 生成器产出＋`--check` rc=0 |
| 9.7 | **W-155 负结果台账与死矿登记落点内收**（并入既有宿主，禁第二真源） | 新增 | 宿主册出现该段且尺可判 |
| 9.8 | **W-156 孤儿件治理**：`11_rescue_playbook.md`/`repair_capability_tokens*.py` 等"被登记但零消费者/被 .gitignore 排除"件的定策 | 新增 | 三态表（保留/改道/退役） |
| 9.9 | **W-157 `.runtime/tmp/st-metaq-gc-20260924` 的 28 处硬编码引用改道工程**（改完才谈得上处置该目录，X-44 后续） | 新增 | 引用改道件全落，读侧无默认路径依赖 |
| 9.10 | **W-158 13 条 AI 代裁的追认单**（裁决归总令列的代裁 1–13，逐条给"是否被后续实测推翻"，Owner 只勾否项） | 并入 ⚑ 附录 | 13 行表 + 在册依据 |
| 9.11 | **W-159 15 门 P4 合并家族名册标注** 与 **W-160 T14 own_scope 十七条终态标注**（Owner 已给的口径落册，禁再漂） | 波 5.1 | 两册自洽 rc=0 |
| 9.12 | **W-161 L18 六册口径互斥清理**（同名册/异路径册并存导致的读侧错配） | 波 5.1 | ROOR 指向唯一真源 |
| 9.13 | **W-162 arbiter 令第二阶段④⑥ 收尾**（AGENTS.md 漂移修正走金哈希规程 + candidate 报告生成器刷新） | 波 5.2/6.2 | 在册议题 `#ARCH-AGENTS-SSOT-DRIFT-001` 状态推进有据 |

### 波 9 销账读数（2026-09-29，st-finaldel-cdocs-20260929，判定锚=当日 HEAD；C48）

| 项 | 销账读数 |
|----|----------|
| 9.3 W-142..W-151 | 审查后已删除（对账器机生替代，无账可销），维持删除态 |
| 9.4 W-152 | **✅销**——`docs/_working/commit_speedup_campaign/80_hmac_proposal/proposal.md` 在 HEAD，§六量级评估节在（L111，自标"波 9.4 验收必备节"，5 文件/150-300 行量级）；状态行"立项提案未批准开工"=文档交付面完整，实施面=flag 出厂翻转归 Owner 门另案 |
| 9.5 W-153 | 分流 C16（工单注记在案），本表不改判据 |
| 9.6 W-154 | 分流 C336（generate_connection_matrix，M2 工单 READY 待施工）；生成器在 HEAD 0 命中=**未销**，随 C336 落地 |
| 9.7 W-155 | **未销**——"负结果台账/死矿登记"全仓仅 SOP 散文提及（sop/mining_sop、exam_policy 等），宿主册专段与可判尺均无实证；需先定宿主再落段（候补=rule_catalog_registry 或 mining_sop，立处方后施工） |
| 9.8 W-156 | **未销**——三态表（保留/改道/退役）未见产出；`11_rescue_playbook.md` 本尊仍在 HEAD（孤儿件之一在册），`repair_capability_tokens*.py` 全仓 0 命中（去向无登记） |
| 9.9 W-157 | **未销**——`st-metaq-gc-20260924` 引用 src/scripts/config 三面实测 32 处仍在 HEAD（判据"读侧无默认路径依赖"未达；较卡面 28 处反增=X-44 病灶仍活） |
| 9.10 W-158 | **未销**——13 行追认单未见成表（01_adjudication_master.md 有 Z 系个案裁决但无"代裁 1-13"专表；93_owner_menu.md grep 代裁=0=⚑ 附录未并入） |
| 9.11 W-159/W-160 | **半销**——标注实体在册：gate_registry P4 七簇合并重定向锚多条（【已合并/重定向】Owner 2026-09-23 全批 E 口径落册）+ own_scope 机生字段 155 处 + t14_roster_report.md 在 HEAD；"两册自洽 rc=0"终验未复跑（热册核验面归总筹窗） |
| 9.12 W-161 | **未销**——ROOR 无 L18 互斥清理痕迹（ROOR=human_gated 热册，清理走 Owner 通道） |
| 9.13 W-162 | **半销**——AGENTS.md 漂移修正半已落 HEAD（st-finaldel-m2 金哈希规程，批文 #ARCH-AGENTS-SSOT-DRIFT-001 在册）；candidate 报告生成器刷新半涉热册在飞（=C09，defer） |

> 波 9 计 13 项：全销 1（W-152）｜半销 2（W-159/W-160、W-162）｜分流在飞 2（W-153→C16、W-154→C336）｜未销 8 行中的 5 项（W-155/W-156/W-157/W-158/W-161，其中 W-161/W-158 主属 Owner/⚑ 面，W-155/W-156/W-157 可施工面待立处方）。

## 波 9.5 · ⚑ 菜单补位批（W-163，外部终审新增；先于一切 ⚑ 呈报定稿）

> 真源＝`final_review_chartlib/ext_03_schedule_completeness_audit.md` §二 W-163 行与 §三 分类视图。**本波不复制判据，只补"呈得到"这一环**——原方案里 9 项裁定书已判"应呈"而 `93_owner_menu.md` grep 零命中（呈裁链断裂），属第三层遗漏。
> 出口判据：93 册"补位"节 9 行齐（C5 UNKNOWN=拒单／C7 exit 码拆分／EV-02~06 施工令／t0 甲位／L09-C01／emoreplay／修宪入口／时帽追认／AI 层 245 件批文），每行带大白话前因·选项·建议·不裁后果，9 关键词 grep 全命中。W-172 假日批同批呈（时间敏感，10-05 临近）。

## 波 10 · 图形信号接入与共振矩阵（外部终审新增，与波 3–6 可并行）

> 设计真源＝`final_review_chartlib/ext_01_revised_construction_plan.md`（波 10 设计节）与 `ext_02_one_click_directive_revised.md` 第三部分（G-A..G-E 全文）。**本表只登记排产位与出口判据，禁在此复制设计**（内收：同一内容两处写＝第二真源，必漂）。
> 实测底数（勿按旧口径施工）：蜡烛目录 83 条（PAT-CANDLE-001..083）／`signal_ashare` 62 信号模块／`strategy_signal` 19 链路模块／条件包 9 胞先例 ⇒ **缺口是"接线"不是"建库"**。
> 硬约束：图形信号只作考试条件轴、禁作独立信号（学术证伪基线）；DL 不替代规则库，只作 P3 观察轨。

| 包 | 内容 | 出口判据 |
|---|---|---|
| 10.G-A | 接线（既有 83+62+19 资产接进信号总线与考试条件轴） | 消费面反查计数 >0（装饰性接线不算） |
| 10.G-B ∥ 10.G-C | G-B 补强（趋势线通道／几何形态 ~15 族／A 股事件轴）∥ G-C 多周期共振引擎（`merge_asof` backward 防前视 + 摆动结构双峰检测） | 前视注入红证；双峰误判红证 |
| 10.G-D | 共振矩阵统计引擎，每格四件套（样本／夏普[Lo2002 自相关修正+ddof=0]／盈亏平衡成本 c\*[二分+单调校验]／DSR[有效试验数]） | **★READY_NOT_FIRED**：引擎+prereg 冻结+日频小样本冒烟通过即出口；**不点火、结果不入账本、不作策略结论**，正式跑全推迟到波 12 |
| 10.G-E | 分钟数据前置 | **DDL 只呈批不执行**（资金破坏性面属 Owner 门位） |

## 波 11 · 业务路线图收尾 + 板块宇宙完整性

| 包 | 内容 | 归位 |
|---|---|---|
| 11.1 | W-118 CNS-01~14 消费面接线（指标→因子 114 条零客／宏观双向断） | 施工 |
| 11.2 | W-119 退役策略重考 **prereg 起草**（聚宽 322 + 潘潘 159，同卷同纪；正式跑等波 12） | 起草不跑 |
| 11.3 | W-116 上岗规则 v1（等 ⚑-2 拍板后填 `state_matrix`） | 门后 |
| 11.4 | **W-178 板块宇宙完整性**：880 概念 gap=262 补齐或 `observational_only` 降级；`concept_board`(375/32,659) 与 `sector_constituent` 880 段(467/89,586) 两套并存口径须裁真源；881 段 128 与名册对账；`sector_constituent` 滞后 21 天在册 | **波 12 硬前置** |
| 11.5 | W-173 GPU 重写 L2 完成判据（共振矩阵单格耗时达标） | 波 12 前必须完成 |

## 波 12 · 统一跑批窗口（W-179；Owner 裁定"施工全做完再一起跑"）

> 理由三条（缺一不可）：①避免双重烧算力（T1 旧宇宙烧完后概念板块补进来要重跑）；②统计诚实——`dsr_denominator: n_trial_ledger cumulative_trials` 累计口径，分批跑会造成"分母切割"（每批都显得显著、合并全是假阳性）；③预注册纪律的正解——宇宙不完整时冻结＝冻结了一个错的宇宙。

```
触发条件（五条全绿才开窗）：
  ① 波 0–11 全部施工终态达成（含波 10 G-A..G-E 引擎就绪 = READY_NOT_FIRED）
  ② W-178 板块宇宙完整性完成（补齐或降级裁定留痕）
  ③ W-173 GPU 重写 L2 完成
  ④ ⚑-2 成本门口径已拍板（B 案/C 案）——T2 与共振矩阵共用该判据
  ⑤ W-64 T2 晋级池基落主区
窗口内容（一次预注册、一个统计账本、分批点火）：
  A. T2 终审（900 格，T1 幸存者选优）  B. 图形共振矩阵首批（G-D prereg 此时点火）
  C. 退役策略重考（W-119 同卷同纪）    D. 上岗规则 v1 激活（W-116 填 state_matrix）
统计纪律：各批独立 prereg，试验数统一入 n_trial_ledger 累计口径；每格四件套+30 日地板+分层维度；
          负结果如实入 negatives.csv（negative_result_promise）。
点火批准卡：一窗一卡（候选全集/宇宙声明 SHA-256/预算/样本外方案），Owner 批一次管全窗。
★ 唯一合法停点：本卡呈上后标 WAITING_APPROVAL 等 Owner，AI 不得自行点火。
```



## 附 · 并发道次与预算

| 波 | 道数 | 预计袋数 | 关键风险 |
|---|---|---|---|
| 0 | 1 | 0（不落地，只固化） | 快照不全 |
| 1 | 2 | 4–6 | 触核心落地件⇒ 必须重放 100 笔自证 |
| 2 | 4 | 12–20 | 新建件三件套漏一项即整袋死；热册连拒两次即停手 |
| 3 | 3 | 8–12 | ALGO-NOTE-SYNC 同批义务（改实现必同批改 `algo_note_zh` 键行） |
| 4 | 2 | 4–6 | CH/VM/计划任务只读探测窗；06:00 备份锁盘期禁动 |
| 5 | 2 | 5–8 | 热册与宪法金哈希规程 |
| 6 | 2 | 3–6 | 合并器缺陷未修前该册必死（依赖 1.2） |
| 7 | 1 | 1–2 | 冻车道窗口 |
| 8 | 1 | 1–2 | 误删（先验后删） |
| 9 | 2 | 3–5 | W-140/141 必须先于 ⚑-1 定稿，否则呈给 Owner 的前提不精确 |
| 9.5 | 1 | 1 | 呈裁链再断（补位节写了但菜单没接＝本波要治的病） |
| 10 | 3 | 6–10 | 前视注入／双峰误判／DSR 漏记；**G-D 只能 READY_NOT_FIRED，手滑点火＝污染统计账本** |
| 11 | 2 | 4–6 | W-178 两套板块口径若判错真源，波 12 烧的是错宇宙 |
| 12 | 1 | 1 | **唯一合法停点**：五触发条件未全绿禁开窗；点火批准卡呈上后 WAITING_APPROVAL 等 Owner |

全局子代理并发≈8–10，**起批前必读 `watermark.commit_pct`**（>82% 不起大批；本机曾崩在 `git add` 退出码 0xC0000142）。
