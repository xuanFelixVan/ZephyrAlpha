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
> 3. **抢救优先级高于一切施工**——六图车道分支基点落后 dev 237 个 commit、**零自有 commit**、脏项 272；波2 车道 169 件同理。它们一旦被外部重置抹掉就是永久损失（本仓已发生多次）。故波 0 只做一件事：把全部在途字节固化成"清单+sha256+双镜像"。

## 波 0 · 现场固化与安全垫（1 道，串行，最先做，零门禁风险）

| 包 | 内容 | 判据（可跑） | 车道 |
|---|---|---|---|
| 0.1 | 11 条车道现场快照：对 `.aidrafts/lane_ff_*`、`.aidrafts/st-mapbuild-20260924`、`.aidrafts/st-audit-fix-20260924`、`.worktrees/st-ailayer-final-20260924` 等逐个出"文件清单+每文件 sha256+`git status --porcelain`+落后 dev 的 commit 数"，落 `docs/_working/total_command_closeout/snapshot/`（机生禁手改）并镜像 `.runtime/tmp/` + `G:\zephyr_cold\`（G 侧实测 1454 GiB 可用） | 快照件数 == 各道脏项数；抽 3 件 `sha256sum` 复算一致 | 1 |
| 0.2 | 热件盘-HEAD 键集合差自检（capability/ruling/issue/gate/translation/ROOR 六册）：缺即按"HEAD 为基纯插入"修（本册 §配方 R-1，已实跑：capability 册补回 16 条被陈旧快照抹掉的条目、他人 1 条在途保留、YAML 复解析过） | 六册 `盘缺HEAD == 0`；写后进程外 `yaml.safe_load` + 条目数复算 | 1 |
| 0.3 | 磁盘安全垫：D 现 41G/95%。零风险回收=git worktree prune + dead 归档 tar（不删）+ pack gc；**定熔断阈值**：可用 <25G 停大批落地、<15G 停一切写批（Owner 默认已生效，见 ⚑-6-9） | 回收前后 `df` 读数入台账；无删除动作 | 1 |
| 0.4 | 登记"备份护甲落后"新案：`D:\zephyr_t1_backup` 侧 `strategy_intake` mtime=02:49 早于 T1 产物 07:47 ⇒ 声称的 10 分钟 robocopy 镜像未覆盖后段（E 册）；只登记不定性 | 镜像 mtime vs 产物 mtime 对比表 | 1 |
| 0.5 | 登记"sleep-loop 保活进程"与宪法第 9 节第 3 条对撞（PID 37548 每 300s re-register，持 3 个业务文件 claim；T1/做T 真身 PID 3584/33548 已亡）⇒ **它不是工作会话**，避让判据要从"活会话"改判为"活 claim" | `tasklist` + claim 台账对照 | 1 |

**出口判据**：任何一条车道的字节都有可复算清单+双镜像；六册键集合差为 0；波 1 可开工。

## 波 1 · 提交链解毒（2 道并行，串行于波 0）

| 包 | 内容 | 死因对症 / 判据（先证能红） | 车道 |
|---|---|---|---|
| 1.1 | **装载缺口**：名册 103 vs 实载 99，找齐 4 台未装载门并修（判据：`auto_register_gates` 后 specs 台数==名册数，缺台点名报红） | 本仓先例：撞号+标量不等会让一整套台门集体装载失败且**零落盘**（假绿）。红证=故意塞一台引用不存在模块的门，尺必须红 | 甲 |
| 1.2 | **同 id 双条册**：`candidate_module_registry.yaml` 的 `CAND-GOVTEST-005`（HEAD 实测 2 条异体；全册扫出同 id 双条仅此 1 组）。做法=保留信息更全者＋并入对方独有字段＋被并者改号或降级为议题条目（Z-05，语义零删除） | ⚠盘上该册处于 `MM`（他道在途）⇒ 必按 R-1 配方以 HEAD 为基重放，禁整册覆写。红证=合并器对该册的三向合并能过（先复现死：改一条内容→必报身份键冲突） | 甲 |
| 1.3 | **priority 撞号的真身**：两册条目根本无 priority 字段（真源=GateSpec）；实载层撞号 0 簇，代码层 6 簇全是"源台+聚合台 `_union_check`"同值对（2 簇靠 `enabled:false` 才不并存）。⇒ 只补"聚合台与其吸收台不得在实载层同号"的断言尺 + 把这 6 对显式注为设计内同值（禁改数值） | 红证=人为让两台实载门同号，尺必须红 | 甲 |
| 1.4 | **REGISTRY-CODE-ANCHOR 漂移** 文档串 106 vs 代码 129；**GATE-21 FAIL 真红点**=`script_manifest.yaml` 磁盘 461≠516 | 生成器重算（禁手改机生册）；红证=删一行清单→尺红 | 甲 |
| 1.5 | **CREATE-GUARD 触发面**：`files_trigger=''`+`always_run:false`，成本源=`create_guard.py:527` 每类一次全树 `git grep`。实测 1519 次/19186s/均 12.63s（09-25 后均 24.09s，占全部门 141565s 的 13.6%）⇒ 登记 files_trigger 或改 own-scope 差分（**不退役**，Owner 明令） | 红证=新文件缺 token 时必拦（现状已能红，改后须仍能红）+ 重放 100 笔 verdict 全等 | 乙 |
| 1.6 | **flag 三态读**（Z-10）：读到 ON／读到 OFF／读不到必报红点名 | 红证=把 flag 文件改坏→必须报红而非当 OFF 拒投 | 乙 |
| 1.7 | **入队预检旁路**：`requeue` 与 `enqueue_item` 直调补 `run_enqueue_preflight`；28 件纯格式类落地侧自动修，20 件必拒类点名 | 红证=直调旁路投一件缺 token 新文件→必被拦 | 乙 |
| 1.8 | **从未入库件的捞回**：红蓝两件测试（`test_redblue_governance.py`/`test_redblue_robust.py`）、`dead_triage.yaml`/`dead_triage_r2.yaml` 在**全部分支历史零 commit**，`DEEP_DIVE_R1.md` 仅盘上未跟踪 ⇒ 先按 path+blob_sha256 反查队列 blobs 与 `.runtime/tmp`，双证齐才定"缺失" | 四态核对表（未落地件唯一存活处=队列 blobs） | 乙 |
| 1.9 | **不做**：通用逐文件三方合并（封矿在册）；own-scope 大改（证伪，仅保留 W-22 观察） | — | — |

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
| 6.1 | 700 封死信内容驱动四态处置（Z-13，全程零删除）+ 归档后统计入终报 |
| 6.2 | 283 问三态守恒复核（Z-44）；candidate 007 重编号（与 1.2 同根，须先后依赖）；api_server 心跳清障批 + 路由死代码一行修（Z-45）；snapself/EV 护栏按现 HEAD 重放（Z-46）；blob_gc `--archive`（Z-47）；VM/root 与临时目录按三段式隔离（Z-48） |

## 波 7 · 终验（1 道，冻结车道后）

- 7.1 逐目录 `python -m pytest`（**禁一次全量**：单进程收集必失败），带 `-p no:cacheprovider -W "ignore::pytest.PytestConfigWarning"`（只带前者会 INTERNALERROR），`--basetemp=.runtime/tmp/<独占>`；**在落地面复跑第二轮**（活树上两轮一致不算认证）。
- 7.2 五目录重点：`tests/ai_layer`、`tests/intelligence`、`tests/governance/fullflow`、`tests/gov_enforcement`、`tests/shared`（其中 20 个 Redis skip 记为覆盖洞不是绿）。
- 7.3 红蓝极限对抗补测：图14/图15 **从未被独立红队打过**；提交链场景⑦跨道连坐；灾备锁语义已有一轮（11 例）。攻击面=伪造节点/断链引用/越域挂载/INV-1 复制侵权/冒充 verified/绕过禁止边/PID 复用/热册整覆。发现即修，两轮零 FAIL。
- 7.4 表述纪律：**永不说"全绿"**，只说"该套件本轮检出 N 件通过，且已被证明能红（附变异/红蓝证据）"。

## 波 8 · 清洁与交付（1 道）

- 8.1 逐文件 `git hash-object <f> == git rev-parse dev:<f>` 才 `worktree remove --force`；任一不等或不在 dev ⇒ 禁删（73 个 worktree 现数，`.worktrees` 目录项 52 是另一口径，两数勿并谈）。
- 8.2 `.runtime/tmp/*` 自有临时件清零（本战役目录：`total_command_closeout/`、`st-zmaster-20260926/`）；项目根与 `.runtime` 根零新增。
- 8.3 claim 全释放（判据只重读 `.ailocks/registry.json` 的 `locks` 键）、会话注销、死信归档路径确认。
- 8.4 终报 + Owner 一张菜单（`93_owner_menu.md`）+ 台账 `94_ledger.md` 定稿。

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

全局子代理并发≈8–10，**起批前必读 `watermark.commit_pct`**（>82% 不起大批；本机曾崩在 `git add` 退出码 0xC0000142）。
