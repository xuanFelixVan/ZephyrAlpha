---
ttl: task_bound
date: 2026-09-17
---

# P2-1 ALGO_FLOW 出仓战役 — 环境与治理面发现登记（不改判，只留账）

<!-- creation_token: algo-flow-externalize-p21-algo-flow-link-findings-2026-09-17 -->

> 口径：本文件登记**出仓链路之外**在战役执行期实测到的环境/门禁/工具缺陷。凡"改一行就能让
> 本战役变绿"的处置一律不做——弱化门禁换绿灯是把病藏进墙里（AGENTS.md §4 第 2 条 退役审计靠触发率，
> §3 第 3 条新 gate 必 own-scope 是同一价值观）。每条给：实测证据 / 影响面 / 建议处置 / 归属。

## 0. 战役本体状态（对照用，非本文件主题）

- `src/zephyr/**` 死块（module docstring 之外机器块）实测 **0 处**；判据与 ALGO-FLOW-LINK
  门禁第 3 判据同源函数 `algo_flow_dead_block_spans`，不是另起一套口径。
- 尾池 143 件（69 件作者欠账除外）全量落地：t00 `af2f1ebbd3` / t01 `d99c7068c2` /
  t02 `76e376b3e3` / t03 `aabbde6575` / t04 `3c4e3cb2d0` / t05 `984728c6a3`，
  逐批 landed_id 反查 `git log -1 --name-only` 得 in_commit=expected、extra=0、missing=0。

## 1. 提交序列化 worktree 的双写者不变量无强制（P1，#ARCH-317）

- 实测：`scripts/governance/commit_queue_landing.py` 每次消费条目起手
  `_sync_worktree()` = `git reset --hard refs/heads/dev` + `git clean -fd`。两个进程同时排空队列时，
  后者起手即把前者"已 apply 未 commit"的新文件连抹——本战役 3 个批次（t00/t01/t02 + cga）
  整批报 `ALGO-FLOW-LINK：12 处 yaml 不可读（已删除?）` 与 `no changes added to commit`。
- 监视器取证（`.runtime/tmp/bt_wt_watch.py`，2s 采样）：02:27 那次快照 24/24 在场且 staged 全程未掉，
  下一帧归零——排除"快照写坏"与"门禁误判"两条假设。
- 对照实验（决定性）：同批内容原封 `requeue`、只让常驻 `commit_belt_daemon` 消费 → `af2f1ebbd3` 24/24
  干净落地。**凶手是自家脚本补的那次 drain**，不是环境。
- 根因结构：`SerializerLease` 用 O_EXCL + TTL=300s，`acquired_at` 只写一次、**不续约**；
  超 TTL 后任何进程都可合法接管，而单批 gate 链实测 3–7 分钟，与 TTL 同量级 → 长批必被抢。
- 建议：lease 心跳续约（消费循环内每 60s touch `acquired_at`）+ 接管前强制读 processing/ 判活；
  或把"新文件快照 apply→commit"做成同进程内不可打断的临界区。
- 归属：队列落地器（非出仓器）。我方已自改规避（`bt_land_queue._wait` 只在守护 PID 判死时才 drain）。

## 2. 全索引扫描型门禁连坐无辜提交人（P1，#ARCH-318）

- 实测：`NO-LONG-PARAM-LIST` 等 `own_scope: false` 门禁扫的是**整个 git index**，
  他会话在途 staged 的 `src/zephyr/strategy_pipeline/fw_backtest.py` 违规，把我这批
  一个字节都没碰它的提交拦死；红蓝探针 R2/R4/R5 三轮 verdict=wrong_gate 皆因此。
- 与裁定#279/#ARCH-316 同族，但那批只治了 4 个**内容扫描**门（HEAD 基线差分），
  结构扫描面（跨文件参数/行长统计类）未覆盖。
- 建议：按 #ARCH-316 同一配方补 HEAD 基线差分（NOW−BASE 只阻断本次新增，NOW∩BASE 存量降级
  warn 并归属责任人），或强制走队列（serializer worktree 净暂存区结构性免疫）。
- 归属：gate_engine。我方规避=战役后续全部改走提交队列（AGENTS.md §2 第 6 条）。

## 3. 未提交工作在共享主区可被整片吞掉（P1，#ARCH-319）

- 实测：2026-09-17 02:59:14 主工作区 **214 个在途脏文件同一分钟被改写**（mtime 聚类），
  其中本会话 4 个未提交工具件被还原到 HEAD，丢失 +290/−13；`externalize_algo_flow.py`
  于 02:59:14 落盘为 HEAD 内容，03:06 的队列快照因此抓到的就是 HEAD → 队列项 `q-…-0049`
  落 `noop@2436f92c`（in_commit=0 missing=4）。
- 排除项：`.runtime/workspace_alerts/stash_notice.json` 当夜只有 1 个文件、属
  `st-skeletonaudit-20260916` 的 pre_merge_clean，非本事件通道；无文件锁在场（`lock_files.py status`
  = CLEAN）；本会话未跑过任何 mutating git 命令。
- 恢复：23 条编辑从会话记录（sidechain `agent-ageneral-purpose-e1464ec45783daa2.jsonl`，
  01:10–01:24）逐条重放，`old_string` 全部唯一命中、零模糊匹配，自 pristine HEAD blob 二次重放
  得同 sha256；重发批 `tl1b` → `2bdc9f074a` 4/4 干净落地。
- 建议：①"每轮修改即 git add"（RULE-GIT-SAFE 第 12 条）在直改主区模式下必须真执行——staged
  内容不会被 `reset --hard` 之外的批量改写吞（对象库有 blob）；②长战役工具链改完即出小批落地，
  不攒到收尾；③批量改写类工具（blueprint 归一化/生成器全库刷）应限定自身产出面，
  不做 `git checkout`/整片回写。
- 归属：共享主工作区并发模型（结构性，非单一会话过失）。

## 4. `apply_depgraph.py --add-design-node` 对 MOD-* 蓝图恒发假告警（P3，#ARCH-320）

- 实测：`scripts/governance/apply_depgraph.py:1097` 按 `docs/03_modules/{blueprint_id}/blueprint.md`
  推路径判存在，而 DB 触发器 `check_blueprint_id_three_track()`（裁定#208 三轨制）只接受
  `MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER*`——两个口径不可能同时满足：MOD-* 必然"文件不存在"，
  填目录名（如 `_cross_layer/gov_scripts`）则被触发器拒绝（本轮两次调用分别撞中，第二次
  `add_design_node失败: nodes.blueprint_id format violation`）。
- 影响：设计态登记要么带假告警、要么直接失败；`blueprint_path` 机械推导对 MOD-* 也是错的
  （写成 `docs/03_modules/MOD-GOV_ALGO_EXTRACTOR/`）。
- 建议：路径推导改查真源（module→blueprint 映射注册表），别拿 id 当目录名。
- 归属：apply_depgraph（登记侧）。本轮结果：node_id=14462964 以 `MOD-GOV_ALGO_EXTRACTOR`
  注册成功、带 missing 标记（既有先例同形态，非新造偏差）。

## 5. ALGO-FLOW-LINK 读暂存区的方式恒失败 + scope 外存量（P2，#ARCH-321）

- `src/zephyr/gov_enforcement/commit_gates/algo_flow_link_gate.py::_read_staged` 调
  `gateway.read_staged_file`——**该方法不存在**，异常后回退 `(root/rel).read_text()` 读磁盘。
  后果：门禁判的是工作区内容而非 staged blob，与 #ARCH-316 治的"观测面错位"同一病（staged≠磁盘
  时会误判/漏判）。修法=改用 `git show :<path>` 或补 gateway 该方法（**不能反过来放宽门禁**）。
- scope：门禁只覆盖 `src/zephyr`，`scripts/`+`tests/` 实测 **28 处死块 / 24 件**在覆盖外。
  其中 ≥9 处是**自指夹具**（`code_algorithm_extractor.py` 2、`check_algo_flow.py` 1、
  `test_algo_flow_link_gate.py` 2、`test_code_algorithm_extractor.py` 3 等——解析器/门禁的测试
  数据本就必须内联，出仓它反而毁测试），其余 19 件（regime/backtest/data 测试与两个 resource
  生成器）属真存量。**结论不是"清仓"而是"分家"**：自指夹具要显式豁免口径，真存量要逐件判
  该搬该删——两条都需要算法作者语义输入，工具无权代判（伪造边=错图冒充已验证）。
- 归属：gate 实现 + 门禁 scope 定义。

## 6. `safe_write_text` 残留 `.tmp.<pid>.<ms>`（P3）

- 实测：`scripts/**` 下 9 个 `.tmp.<pid>.<ms>` 残留，owner PID 35264（Qoder CN）/31816（ZCode）
  **均存活**——即宿主工具进程的中断写入残片，不是本会话可判死的孤儿。按"存活进程的文件不动"
  处置：本轮不清理，只登记（清理需其属主会话或 Owner 判定）。
- 建议：`safe_write_text` 在 rename 失败的 finally 里自清 `tmp`；或写入端加启动期清扫（属主 PID
  判死才清）。

## 7. #ARCH-319 通道二次发作：CAS 写成功的热文件仍能被整片盖回（P1 复现，同 #ARCH-317 家族）

- 实测：04:0x 本会话以 `safe_write_text(expected_base_sha256=…)` 对 `ruling_registry.yaml` 完成
  CAS 写入并**工作区读回核过**（entries=110，尾条 `裁定#292`）；04:4x 复核时工作区该文件已回到
  `HEAD + 1` 形态——尾条是他会话的 `裁定#291`，`#292` 整条消失（非本会话所为：本会话期间对该文件
  只有那一次写入）。即"以陈旧内存副本整文件改写"能盖掉别人的**已落盘**内容，CAS 只保证写入瞬间
  的基线，不保证事后不被回退。
- 与 §3 同一通道，但本次目标物是热注册表，危害更高：注册表条目是裁定/门禁/令牌的唯一真源。
- 本轮处置（不改判、不追归属，AGENTS.md §3 第 4 条）：重贴 `#292`（号位钉死，因
  `#ARCH-317..321` 的 `related_adjudication` 已反向引用 292）+ **当分钟即出小批**落地，
  把"未提交窗口"从小时级压到分钟级；建议治本同上：热文件写入后应立刻 staged（对象库留 blob），
  或由注册表写入器统一"写→add"闭环。
- 归属：共享主工作区并发模型（同 #ARCH-319）。

## 8. 端到端核销器判据分家：硬缺陷 vs 半径外吸收（不需白名单）

- 旧判据在"AST 指纹变了但字节码流也变了"时一律记 `ast_semantic_drift`（硬缺陷），
  round4 因此留下 2 件需人查；人查结论=他会话在途代码被整文件快照带进本批（`retain_ratio`
  字段+`__post_init__`、`slippage_bps` 三元式），非出仓器所为。
- 新判据（`.runtime/tmp/bt_diff_radius.py`，收口后随临时件一并删除，机制侧候选转正见 §5 归属）：
  出仓器对 `.py` 的**全部**编辑半径被几何限定=机器块跨度 + 裸字符串语句内散文 + 一行 external
  锚 + 注释空行；差异里出现"半径外的可执行语句增删"即不可能由出仓器产生 → 记
  `info_foreign_absorbed_code` 并附证据行；半径内仍变指令流才是工具缺陷，保持硬判据不放宽。
- round5 结果（58 批 / 2342 个 .py / 2339 有锚 / 2177 图对比）：硬缺陷 **0**，
  `info_foreign_absorbed_code` 2 件（即上述两件，证据行现为纯指令行，散文噪声已剔除）。
- 台账侧同步收口：`docs/_working/reports/algo_flow_author_debt.md` 由已落地生成器
  （`29e7dafce0`）现扫产出，恒等式 47+17+5（作者欠账 69）+ 可机械 5 + 其他 0 = 池 74 自证成立。

## 9. 红蓝实弹第一发打死一只哑火门禁：锚+内联块并存零拦截（P1，#ARCH-322，已修）

- 实测：ALGO-FLOW-LINK 的"体内多块"判据在 **锚已在场 + 体内再写一块** 这一形态完全不设防。
  红蓝探针 R2 注资 7 行（锚行紧随处一份 `# [ALGO_FLOW]` 块，同处 module docstring 内），走
  生产链路 `commit_queue → serializer worktree → 真门禁链` → **未阻断**，落 `b873ee71d3`，
  死内容进 HEAD。此前战役每一批都"干净通过"，等价于该门禁从未在真批次上开过火。
- 为什么纯单测覆盖不到：单测直接调 `GateSpec.check`/`algo_flow_dead_block_spans`，把三段全短路
  ——①网关是否真把本门挂进链、②own-diff 作用域是否真覆盖镜像、③阻断后是否真不产生 commit。
  三段都要真跑才看得见（本轮 R2 恰好死在第 1、3 段之间：链是通的、判据是哑的）。
- 根因（几何口径缺了一类载体）：`extractor._algo_flow_block_spans` 的起标记候选显式排除含
  `external:` 的锚行（2026-09-15 为防锚行字面量误判而加，本身必要），于是
  `duplicate_inline_algo_flow_spans` 在"锚+一块"只数到 1 块，`inline[1:]` 为空即判合法。
  而"锚+块"正是**出仓战役自己制造的新向量**：锚已在场外指真源，体内再写回的块永不被任何读卡路径
  消费=第二真源，比"块+块"更常见（出仓后任何人补写机器块即可复现）也更坏（yaml 与体内块会各自漂移）。
- 已处置（不放宽、只收紧）：判据从"体内第 2+ 块"升级为 **module docstring 载体唯一**——锚与内联块
  同为载体；锚在场时全部内联块报出、与行序无关；无锚维持"首块合法、第 2 块起报"原口径
  （报出首块=一次性连坐全仓未出仓件，正是判据分家要防的方向性错误）。
  零存量核验：新判据全量重扫 `src/zephyr` 3576 件命中恰 1 件=探针注资本件。
  HEAD 注资走 Edit 清偿 + fix-forward（历史只追加不改写，AGENTS §12），并落 3 条测试
  （体内并存正反序 / 门禁并存阻断 / GateSpec staged 指纹回归）。
- 归属：extractor 判据 + 门禁（本战役自家件）。同时清偿 #ARCH-321 的 ① 半边（staged 读取器
  改 `_diff_helpers._read_staged_file`），#ARCH-321 ② 半边（scope 外 28 处分家）仍 open。

## 10. 自家交付物把自家测试炸了：断"生产文件不存在"是定时炸弹（P3，已修）

- 实测：`tests/governance/generators/test_report_algo_flow_author_debt.py::test_main_writes_report_and_json_without_touching_repo`
  末行断言 `docs/_working/reports/algo_flow_author_debt.md` **不存在**——本战役把该台账交付并进
  `77bbf6011b` 之后，这条测试对每一个后来者永久失败（本轮跑全量 governance 套件才撞见；单件跑没跑过）。
- 病根形态：把"当前不存在"当成"永远不该存在"。零写入类判据的正确写法=**跑前后字节指纹一致**，
  与文件在不在无关；已按此改写（断言消息保留"--out 未生效"这一失败语义）。
- 影响面：不止本件——凡"新生成器的输出路径恰好是被断言对象"的测试都可能带同一枚炸弹。
  收口动作=本轮把治理套件全量跑（而非只跑改到的单测）列为落地前必做，本轮起执行。
- 归属：出仓战役工具链测试（自家件），无外部责任人。

## 11. 常驻守护的旧判据缓存把三条判据整体关掉：门还在、牙没了（P0，#ARCH-323，已修）

- 实测（serial 轮，真串行 stage→judge）：同一条 ALGO-FLOW-LINK 在 R4/R5 正常开火
  （q…0064/q…0065 死信，原文逐字命中），而 **R1_dead_block（q…0066→`e10ac5acc4`）与
  R3_no_edges（q…0067→`2924601305`）双双落地**。五场景中把落地的两个与拦住的两分开的
  唯一变量：R1/R3 的判据取自 `_load_graph_rules`，R4/R5 的两条（锚指向 yaml 实存、
  source_of_truth 实存）不取自它——"部分失效"是门禁最坏的失效形态：全绿，但牙已掉。
- 根因两半：
  ① **判据装载吃 sys.modules 缓存**。旧写法 `from _shared.code_algorithm_extractor import
  algo_flow_dead_block_spans …`，常驻进程若在符号诞生前 import 过 extractor，之后每次装载
  都撞 ImportError → `rules=None` → 死块/体内多块/图可达三条判据静默关闭。时间线闭合：
  belt 守护 PID 28552/28648 自 **09-16 07:17** 常驻，而 `algo_flow_dead_block_spans`
  **09-16 21:58**（`787fd269d5`）、`duplicate_inline_algo_flow_spans` **09-17 00:52**
  （`834c5ffb9c`）才进 extractor。
  ② **纪元自检只测门禁子树**。裁定#281 的 re-exec 判据是 `HEAD:src/zephyr/gov_enforcement`
  tree sha，而判据真源住 `scripts/governance/_shared/`——判据侧治本对常驻守护永不可见，
  守护不会重启。①是病灶，②是让病灶长期不愈的麻药。
- 影响面（诚实口径）：战役 ~90 个经队列落地的批次，其死块/图可达判据在**落地瞬间**未被执行。
  结论"存量语料干净"另有独立证据：离线复验波（`bt_verify_wave`，每批 fresh import、逐件
  复算剪枝 AST 指纹 + 字节码 tie-break）覆盖同一判据链且 defects=0——不是假设；
  但"门禁在生产路由上确实开过火"此前被高估，本轮起以红蓝实弹为唯一效力证据。
- 已处置（三层，只收紧不放宽）：
  ①判据**按盘上文件直载**（`importlib` 独立模块名，不污染他人在用的 `code_algorithm_extractor`
  条目），按 (判据目录, 两源文件 mtime_ns+size) 指纹缓存——判据语义恒等于提交时刻的仓库内容，
  不受进程寿命摆布；②`rules=None` 拆成两态：**判据源不在盘上**=环境降级（结构性兜底仍在，
  维持放行），**在盘上却加载不出**=仓库自身缺陷 → fail-closed 阻断并指名判据源；
  ③守护纪元扩到 `scripts/governance`，判据侧治本也走安全点 re-exec（单侧无证据不废另一侧）。
  HEAD 两件注资走 Edit 清偿 + fix-forward，机证=与 pre-probe 版本**逐字节相同**
  （`MATCH-pre-probe`，40897/3878 两长度一致）。测试：stale sys.modules 不再能关判据 /
  在盘不可载必阻断 / 判据子树单独变更也 re-exec；既有 3 条 epoch 测试补判据子树 stub
  （`tmp_path` 落在真仓内，不 stub 会取到真 sha 造出假"纪元变更"）。
- 探针侧教训（**非仓缺陷**，留此防重踩）：
  ①`commit_queue.py enqueue` 的**同键覆盖**是有设计依据的行为（`(session_id, path)` 键、
  pending 内仅留最新，见其 # [INVARIANTS] 与 66 号 §6.2），一次全 stage 多场景时共用同一目标件
  的先发项会被后发项整体移除（本战役 0056/0058/0061-0063 三次"项消失"皆此，非数据丢失）
  ——多场景探针必须真串行（已加 `serial` 模式）；②落地后主仓常年 `MM`（受限收敛只写工作区、
  index 留旧 blob），用 `git status --porcelain` 判"工作区干净"会把探针自己拦下（serial 轮
  R2 首枚即 `skip_dirty`）——判据改为工作区字节 == `git show HEAD:<rel>`。
- 归属：ALGO-FLOW-LINK 判据装载（本战役自家件）+ belt 守护纪元（裁定#281 同家）。
  与 §9 同族但机制不同：§9 是判据几何口径缺一类载体，本条是判据**装载**在常驻进程里失能。


## 12. 落地回执与"谁来判"这一层（#ARCH-324，待窗）

- #ARCH-323 修复批落地：`95f1832aeb`（05:21:40，8/8 文件，`git log -1 --name-only` 核实
  extra=0 missing=0），前置=治理套件 `3364 passed / 46 skipped / 1 xfailed / 0 failed`
  （8 分 08 秒）+ 定向 38 passed。落盘后 HEAD 复核：`strategy_book.py` 内 `[ALGO_FLOW]`
  计数=1（仅 external 锚），`strategy_book.yaml` 边段 8 行回位。
- **新暴露的一层**：队列路由上"判"的宿主是常驻守护，而它启动于 09-16 07:17:43
  （`.runtime/commit_queue/belt_daemon.lock` mtime 与 `psutil.create_time` 同刻=未曾
  re-exec），其时代源码 `c3729434ac` 里根本没有 `_check_and_reexec`——**纪元自愈无法
  追溯**：能自检的代码只存在于新进程里。故 #ARCH-323 的第二层对这一具实例无效，红蓝实弹
  若被它消费仍会按旧判据放行。裁定#281③ 明文"8 会话并发期禁自行 kill 常驻进程"，
  本战役遵守并**改为**：注资变异不再投经该守护（0069 由同键覆盖撤换，HEAD 零注资），
  队列路由的效力证据改由"新进程侧 drain + 字节核实"给出；守护重启处置登记
  **#ARCH-324**（A=静默窗/Owner 门位重启一次即闭合；B=每项起短命子进程=结构根治但动
  lease 单写者语义，须独占基建窗）。

## 13. 新码效力证据（FRESH5）+ 两条操作性教训

- **FRESH5**（`.runtime/tmp/bt_rb_fresh5.py`，scratch worktree 生产形态复刻）：判定入口用与
  `GitCommitGateway` 同形的 `check_algo_flow_links(files, root, read_staged=...)`，判据真源从
  **该 root 的盘上**直载（#ARCH-323 第一层），五发变异 = R1 体外死块 / R2 体内多块 /
  R3 图无边 / R4 锚指向不存在 yaml / R5 `source_of_truth` 断链 →
  **`blocked_ok=5/5`，每条都命中本场景门禁原文**，`criteria loaded from disk: OK`。
  单测侧同族证据：`test_stale_sys_modules_criteria_does_not_disable_gate`（把 `sys.modules`
  灌成"只有旧符号"的假 `_shared` 后，判据仍可得且死块照样硬阻断）。
- **为什么不再往默认队列根投注资变异**：那台上（#ARCH-324）按旧码消费，注资极可能再进
  HEAD；而"开第二个 Serializer"直接违反单写者不变量（66 号 §9.7 / lease TTL 竞态在案）。
  队列路由已有的生产证据不撤回：R4/R5 真死信（q…0064/0065）+ 本役 90+ 批次全经该路由落地。
- 教训①（探针侧）：`enqueue` 的自举 drain 只在 lease 空闲时生效，守护持 lease 期间项由它
  消费；`judge` 对已被同键覆盖撤换的 qid 会一路干到 `_wait` 超时（本轮 0069 即手动停表）。
- 教训②（claim 生命周期，AGENTS §2.3/§1 第 3 条同源）：`lock_files` 单把 claim **TTL=30 分钟**，
  且落地 `finally` 会释放本批文件的 claim（95f1832aeb 落毕即释放 8 件）——随后 q…0070 仍投
  同两件 → `CLAIM_REQUIRED_VIOLATION` 死信；`requeue`（重建快照=重新走落地侧 claim）后
  q…0072 正常落地（aade2d4fef）。**口径：跨批续投同一文件必须重新 claim，勿沿用上一批的锁；
  死信先看是否 claim 类，是则直接 requeue 而非改内容。**本条成因不硬判"旧守护"：
  落地侧 pre-claim 源码在 09-16 07:17 版（e926198085:743）与当前版逐字相同，故更可能是
  TTL/配额类瞬态，未取证前不下结论。
- 归属留痕：79da32493a（#ARCH-324 登记）把他会话 staged 的 **#ARCH-325** 一条（31 行完整条目）
  一并带进 commit——AGENTS §2.5 记录的暂存区吸收常态，条目完好无损，此处仅为归属可追溯。

## 14. 两轮零缺陷核销 + 一次"缺陷"其实是空命题：退役批次不清镜像（#ARCH-326）

- **第 8 轮唯一 `defects=1` 的归因**：`wt_unreadable: src/zephyr/infrastructure/model_capability_exam/__init__.py`
  ——该路径已**不在 HEAD**：他会话退役批 6a0eca4700（st-govmap，09-17 05:35，P4-β 死壳退役）把整棵树删了。
  对一条已不存在的路径复验"本批落地后的工作区内容"是**空命题**，不是本战役的断链。
- **核销器判据精确化**（scratch 工具，非门禁，只收紧不放松）：`FileNotFoundError` 且路径不在 HEAD 树内
  → 记 `info_foreign_retired` 只报数；仍在 HEAD 却读不出（占用/权限/损坏）才算硬缺陷 `wt_unreadable`。
- **两轮零缺陷达成**：第 9 轮（判据修正后，全 60 批）`VERIFY defects={}`，覆盖
  `py=2342 / anchored=2338 / yaml_ok=2338 / compared=2176`；第 10 轮同判据重跑（期间 HEAD 又被他会话推进）
  仍 `defects={}`，逐项计数与第 9 轮逐位相同。**"连续两次测试问题=0" 判据满足。**
- **顺带普查出的真问题不在这批**：镜像**反向悬挂**。全库 3227 件 ALGO_FLOW 镜像逐件读 `source_of_truth`
  对 dev 树判存在性 → 命中且仅命中 1 件（上述 `model_capability_exam` 镜像）；常驻终态检查器
  `bt_head_state_check.py`（3576 py + 3227 yaml 全量）独立复算同一件，其余三类判据零命中。
  盲区成因=两向都是 staged 作用域：退役批次删 `.py` 时其镜像天然不在同批清单，ALGO-FLOW-LINK
  判据②（yaml 的 source_of_truth 存在）永不触发，仓内也没有全库反向检测面
  （d5 `check_algo_flow.py` 只查 staged `.py` 标记，`algo_flow_applier --verify` 只按固定模块清单算覆盖率）。
- **登记与处置口径**（#ARCH-326，P2中/open）：本战役**不代删**——①AGENTS §3.4 他车道改动不代修；
  ②删除须同步从 `capability_canonical_file_registry.yaml` 摘其 creation_token 条目，
  注册表净删按 §5 属 Owner 门位。补救一条命令即够（`git rm` 该 yaml + CAS 摘 token 同批），
  机制侧建议=反向孤件普查并入 `d8_doc_sync` 事件触发对账（勿进 pre-commit：3227 件全库扫描属触碰税，
  perf 方案 §2.6 分级不允许）。
- **登记过程自身的一条教训**：首版写入把 `issue_id` 写成 `"#326"`（模板 `#{NID}` 只替换了数字，丢了
  `ARCH-` 前缀），读回复解析断言 `ids[-1] == "#ARCH-326"` 当场抓到并在同一工作区副本内改正——
  注册表是永久产物，**读回断言必须比"写成功"更严**，它抓到的正是这类事后 review 抓不住的错。
  机证：对 dev 纯追加 26 行、`cl[:len(dev)] == dev` 逐位相同（零删除），条目数 771→772 且 `issue_id` 全表唯一。

## 15. 双锁统一加固自落地即空转：一条被 fail-open 吞掉的 AttributeError（P1，#ARCH-327，已修）

- **线索来源不是评审而是"残留噪声"**：第 8 轮核销期间 `enqueue` 自举 drain 的 stdout 里夹着一条
  traceback（`src/zephyr/shared/io/paths.py:112 parts = root.parts` ← `git_commit_gateway.py:321`
  ← `scripts/governance/commit_queue_landing.py:600`），而 drain 照样报 `DRAIN: done=2`——
  "异常被兜底吞掉但业务仍成功"的典型形态。若无第 8 轮把 stdout 落盘复查，这条会一直沉在日志里。
- **机械归因**：`_advance_dev` 把 `str(self.repo_root)` 传给 `_GlobalCommitLock`——该类注解是 `Path`
  且内部 `strip_session_worktree` 要取 `.parts` → **每次 CAS 落地构造锁即 AttributeError** →
  被 `except Exception` 吞掉并写成"全局锁不可得（30s 超时），退化为裸 CAS"。措辞把代码缺陷
  伪装成环境噪声，"30s 超时"更是误导（构造期就炸，根本没等待）。
- **影响面**：该加固落地批（`e9381d33dc`，09-16 12:36 维护班；W4 孤魂提交 301a6ee82a 的防线：
  队列 CAS 与直连提交共用同一把全局锁）以来，**全部**队列 CAS 落地都在无全局锁下与直连提交
  竞争 dev ref。CAS 自身仍原子，故未观测到实际孤魂——属**防线失效**，非已造成损失（不夸大也不淡化）。
- **测试面同漏（更值得记住的一半）**：`test_dual_lock_unification.py` 两条用例都把
  `_GlobalCommitLock` 整体 patch 成 MagicMock——传什么都"通过"，验证加固的测试对加固本身零判别力。
- **治本三层，且只收紧**：①调用方改传 `Path`（根因）；②`_GlobalCommitLock` 入口把入参归一为
  `Path`（注解 `str | Path`）——让类型契约违背在这条"常被远端 except 包住"的路径上**不可能再
  伪装成锁竞争**；③告警正文带异常类型与消息（`exc_info` 保留），下次同类问题一眼可归因。
- **红蓝机证**：新钉 `test_cas_critical_section_really_holds_the_real_lock` **禁 mock 锁本体**——
  真锁 + `tmp_path` 作 `repo_root`，在 `update-ref` 临界区内当场断言全局锁文件存在、退出后已释放。
  预修复码复刻（scratch worktree @ dev `b5e72ff59f`）该钉 **FAILED 并打出同一条 AttributeError
  traceback**；修复后 dual-lock + landing 共 40 passed，gateway/daemon/ALGO-FLOW-LINK 共
  53 passed + 1 xpassed。
- **一般化教训（已进项目记忆）**：被 `except Exception` 包住的加固代码，必须至少有一条
  **"不 mock 该防线自身"** 的钉；否则 mock 掉防线的测试会让失效长期不可见。兜底日志
  **不得预设失败类别**（"超时/不可得"），必须打印异常类型——否则代码缺陷会被读成环境噪声，
  本役这条空转了 ~17 小时（09-16 12:36 → 09-17 06:00 复查）。


## 16. 机械面清零（尾池最后 5 件）+ 一次门禁假判抓出双写者（#ARCH-328 / #ARCH-324 实证追加）

落地回执：批A `481aaed065`（12 文件，逐文件核实全为本 lane 自有内容）、批B `688bcffc6e`（2 文件）。

### 16.1 尾池 5 件机械出仓，池 74 → 69（机械面 0）

作者欠账台账 dry-run 判"可动"的最后 5 件全部出仓：`gov_audit/{integrity,log_rotation,secret_registry_drift,writer}.py`
+ `red_blue_validator/__init__.py`。5 镜像 creation_token 走官方通道 `batch_creation_tokens.py`
（CAS attempt 1，注册表纯追加 +20/−0），台账重生成后恒等式 **69 欠账 + 0 可机械 + 0 其他 = 69** 成立——
P2-1 的**机械可完成面自此清零**，残余 69 件全属作者语义欠账（47 五段式散文欠 `- id:` 行 /
17 零边图欠边 / 5 块不可解析零节点），补边补节点即臆造语义，禁工具代做。

### 16.2 "死边段归并"的取证与一次我自己的错判（教训：跨度必须与被检判据同读法）

出仓器把这 5 件 docstring 里 **落在 `# [/ALGO_FLOW]` 之后**的 `# 边:` 段一并收进镜像（33 行）。
我第一版复验用"起标记→止标记"的朴素跨度比对，5 件全报"镜像多出 6/8/5/10/4 行"，
我据此判成"工具臆造边"（伪造边=本战役红线）。实为跨度取错：正确跨度是**起标记→边段尾**，
按此重算 5/5 逐字节相同。再用真判据复核而不是相信自己的比对脚本——
`parse_algo_flow` 的契约是"边可从止标记后扫到文本尾"（`code_algorithm_extractor` 注释原话），
全量实测 3232 镜像中 **3218 件带止标记后边段，其中零边件 = 0**，
`integrity.yaml` 实测 nodes=5 / edges=4 齐全，门禁 `check_algo_flow_links` 判 **BLOCKED=False**。
结论：无回归、无伪造。**教训**：红线级判据（"是否臆造语义"）必须用被检方自己的解析器复算，
自制字符串跨度比对在边界处必然与判据不一致，误报方向恰好是指控最重的那一类。

### 16.3 #ARCH-328：一个"生产无缺陷"的确定性假红（同 #ARCH-327 族：隐式契约两端无钉）

3092 项治理批测试唯一失败 = `TestWorktreeSyncInvariant`（`?? activate_env.ps1`，单跑 3.84s 非竞态）。
判据分家：生产侧实测干净（`git check-ignore -v activate_env.ps1` → `.gitignore:262` 根规则 `/*` 命中，
真 serializer worktree 不受影响），缺陷在测试夹具 `tmp_repo` 只镜像了 `.runtime/` + `.ailocks/`
两条豁免，没跟上 `_provision_worktree_env` 第 3 步（`58aced8cbf`，08-14）新增的激活脚本
→ 该断言在夹具面上恒红一个月，被读成环境噪声未归因。处置=**收紧不放松**：clean 断言原样保留
（它正是防搭便车的判据），豁免表提为单一真源常量 `_WORKTREE_IGNORE_LINES`，新增
`TestProvisionedArtifactIgnoreContract` 三钉（备置根产物集合本身 / 真仓必须忽略 / 夹具表必须覆盖）。
机证=双向变异各 RED：删夹具条目 → "夹具侧漂移：缺 ['activate_env.ps1']"；喂未豁免名 `README.md`
→ "生产侧漂移"；原态 4 passed（含原红用例转绿）。已知弱点留痕：主仓 `/*` 会豁免任意根文件，
故生产侧钉防的是"规则消失"，不防"根目录堆料"（后者由 §9 根零临时文件纪律管）。

### 16.4 #ARCH-324 追加实证：双写者不止坏顺序，它会**伪造门禁结论**

批A 首次投递 `0076` 死信，报"5 处 algo_flow yaml 不可读（已删除?）"——而 5 个镜像**在盘、blob 全在库**。
机制：`enqueue` 默认自举 drain 与常驻 belt 守护（PID 28648，正是 #ARCH-324 点名那位无安全点自检的旧码守护）
并发；租约过期后自举 drain 合法成为第二写者，其 `_sync_worktree` 的 `git clean -fd` 删掉了
**尚未入库的新文件**，门禁于是把"在"判成"已删除"。独立旁证：同晨他会话提交 `69b17ece1a`
的标题即"红蓝 R5 修复批（直连落地——队列序列化器工作树污染转直连正门）"，同一污染第二次逼走直连。
危害等级据此从"顺序竞态"上调为"证据污染"（门禁假判会烧掉整批 claim 并把好件打成死信），
已追加进 #ARCH-324 档案；本 lane 临时防线=**enqueue/requeue 一律 `--no-bootstrap`**（批A 重投 0077
与批B 0078 即此口径，均由守护单写落地）。修法等 #324 的 A 案（重启窗）或 B 案（每项短命子进程）。

### 16.5 两条自伤留痕（工具误用 / 热文件写入）

1. `lock_files.py acquire` 是 `acquire <file> <session>` 位置参数式，我传了多文件 + `--session`
   → 第二个**文件路径被当成 session** 写进锁注册表（假 owner claim），且只锁了 1 个文件。
   多文件必须用 `acquire-batch <sid> --files-from`（本战役自家交付件）。查锁只认
   `.ailocks/registry.json` 的 `owner_id` 字段，CLI 回显的"持有者"行在误用时是误导源。
2. #ARCH-324 追加第一次落笔用 3 空格缩进插进 4 空格折叠块 → 整份注册表 YAML 解析炸。
   读回断言（`yaml.safe_load` + 条目数 + 唯一性）在 `git add` **之前**抓住，改 4 空格复写后
   774 条无重、#ARCH-324 status/severity 未动。热文件"写完立刻出进程重解析"这条纪律，
   本次是它第一次真拦住我自己的手——不是 #ARCH-326 那种写完才想起。

### 16.6 循环复验（第 12 轮，批A/批B 落地后的推进态）

`bt_verify_wave.py` 全 60 批复跑：**defects={}**，coverage
`{"py": 2342, "anchored": 2338, "prior_block": 2176, "compared": 2176, "yaml_ok": 2338, "backlog_inline": 2, "no_graph": 1}`；
`bt_head_state_check.py` 在批A 落地前的唯一新报项就是"5 镜像在盘未入 git=锚悬空"，落地后该项消解，
存量孤件 1（`model_capability_exam__init__.yaml`，#ARCH-326 待 Owner 门位）。


### 16.7 一次归属串位的实测定量（登记 #ARCH-329：队列正门第三形态吸收）

批A 落地后按 §2.5 跑 `git log -1 --name-only` 核实，暴露注册表 numstat **3636/28** 而我在这份
文件上只写了 +20/−0。逐行归属：883 条 `st-auction-bridge` + 12 `st-autolnk` + 7 `st-sharpe2gc`
+ 我自己的 5 条 + 2 条杂项；出进程 yaml 全集比对 **LOST=0 / GAINED=902**——他人令牌一条没丢，
被搬走的只是归属记账（28 行删除经查为令牌重排）。

机制是队列正门独有的**第三形态**：`enqueue` 把整份文件的当前工作区字节流快照进
`blobs/<sha256>`，落地按 blob 覆写且不经主区 index，于是 #ARCH-054（claim 基线快照）与
#ARCH-318/#ARCH-GATE-OWN-SCOPE-001（own-scope）两套防线在结构上都照不到它。据此登记
**#ARCH-329（P2中）**：零数据损失，害在可审计性与按 commit 归属的产能统计，并给出三案、
采"观测先行"（吸收行数升级为机生台账）。

自家口径更正：任务 #37 当年把这条风险的缓解记成"延后落地、等他会话 staged 清零"——对直连路径
成立，对队列路径**无效**（快照发生在 enqueue 瞬间，与 staged 状态无关）。教训并入 #ARCH-329 档案。


### 16.8 落地路径三度分家：队列假死信 → 直连被连坐 → 回到队列（#ARCH-324 追加实证②）

批C（报告+架构问题注册表 2 件）投递后死信 `0079`，dead_reason 是 `no changes added to commit`，
而同一份报错里列出 **15 个他会话未暂存改动**躺在序列化器 worktree（`framework_composer.py` /
`engine_base.py` / `screen_source.py`… 即 #ARCH-325 那批）。出仓核对：该 worktree 的注册表副本里
`#ARCH-329` 计数=0 —— 我的 blob 被并发 `reset --hard` 回滚成 HEAD 形态，网关于是把"有内容"判成
"无差异"烧成死信。这是 #ARCH-324 的**第二形态**（第一形态=门禁把在盘文件判成"已删除"）。

独立旁证把根因从"双 drain"扩到"锚点漂移"：主区 pre_commit 的 CRITICAL RECONCILER 日志同时出现
`.worktrees\st-sowner002-20260916\scripts\…` 与 `.runtime\commit_queue\worktree\scripts\…`
两种根路径的命令——post-commit reconciler 以漂移后的 REPO_ROOT 为 cwd 被拉起，正是
`session_worktree.py` 注释里警告过的"同一 worktree 树被 import 时 REPO_ROOT 指向该树自身"。
含义：A 案（重启窗）若不同步收紧 anchored-path，新守护照样被污染。

中途试过直连正门（同日先例 `69b17ece1a`），两道墙：①`WORKTREE-REQUIRED`（非 worktree + 多活跃会话，
裁定许可旗 `--allow-non-worktree` 可越）；②越过后被 **BLUEPRINT-FORMAT 全索引扫描**连坐——报的 6 个
违规文件（`generate_skeleton_health.py` 等 `MOD-AUTO-L*-001(暂编号)`）全是他会话 staged 在途件，
按 §3.4 不代修。结论：**队列仍是本役唯一不连坐的正门**，代价是要认 `--no-bootstrap` + 死信重投；
这也说明 #ARCH-318（own_scope:false 连坐面未覆盖）与本条是同一场病的两面。
