---
ttl: task_bound
owner: st-maint7-20261014
lane: worktrees-B
campaign: 维护七班（承接维护六班未竟＋两枚新缺口：P0-甲 m10 声明解析对称化／P0-乙 CREATE-GUARD 瞬时态加固／P1 挂死地雷／P2 接管条目刷新出口＋P-9 设计面）
---

# 维护七班 · 车道B 收口账（2026-10-14 00:42 接令 → 当班自收）

> **为什么这本账叫 laneB 而不写 `00_ledger.md`**：本会话号 `st-maint7-20261014` 下**存在并发实例**
> （车道A `.aidrafts/st-maint7-20261014`，00:54 已投 P0-甲 七件套）。同号两会话共写一本账＝后写整档覆盖
> （在册"共享追加型文件禁 Write"铁律）。本班落自己的面并在 §一 把两实例的袋账合起来算，
> 避免下一班按半本账判全局。

## 〇、冷启动与工区

- RULE-ENV 3.12.8；`setup_dev_env.py --check` usercustomize exists+installed 指 D:\\ZephyrAlpha；
- 工区＝`session_worktree.py create st-maint7-20261014 task-maint7-gate-symmetry`
  → `.worktrees/st-maint7-20261014`（分支 `ai/st-maint7-20261014/task-maint7-gate-symmetry`）；
- **自纠（在册坑复踩）**：首袋被 `SESSION-REQUIRED` 判"session 未注册"——车道 create 只登记车道根、
  网关读主区面（记忆档 `lane-session-registers-in-lane-root-gate-reads-main-root`）。
  处置＝按正门 `session_worktree_start(allow_workspace_drift=True)` 在主区面登记＋心跳守护确认，
  不加旗不绕行；此后三袋全部正常入队。

## 一、本会话号袋账（两实例合并算，尺＝manifest 本体）

| 袋 | 投者 | 内容 | 态 |
|---|---|---|---|
| 0001 | 车道A | P0-甲 m10 声明＋同族正则单点治本（7 件，含 `_diff_helpers`/`syntax_validation_gate` 及其测试） | **dead**（GATE-PRECOMMIT-RUN／hook=gate-test：101 collected / **1 collection error**，未修因） |
| 0002 | 车道B（本班） | P0-甲 本班实现版（2 件） | **dead（自撤避让**，理由见 §二） |
| 0003 | 车道B | P1 挂死地雷修复（test_t3a_grid_s_wiring.py） | pending |
| 0004 | 车道A | P0-乙 CREATE-GUARD 撕裂读改读 HEAD（4 件） | pending |
| 0005 | 车道A | P0-乙② 投影双向一致性对账（2 件） | pending |
| 0006 | 车道B | P2 接管条目刷新出口（3 件：模块＋测试＋t1 文档同批） | pending |

⇒ **P0-甲 当前无在飞袋**（A 版死因未修、B 版已避让）。本班不再补投（见 §二 的唯一纠正出口建议）。

## 二、并发避让：本班为什么撤掉自己那袋 P0-甲

- 本班按令做完 P0-甲：门内补 `_M10_NOQA_PATTERN`＋`_has_m10_exemption`，新增件/修改件两条路径各一次豁免早退，
  `[INVARIANTS]`＋docstring 设计权衡第 5 条同批改；测试追加 11 支（三态判别：有声明放行／无声明拦／畸形拦）。
  读数＝零突变基线 112 passed（自家 37＋m11 邻尺 30＋合并门 7＋msg-exposure 38），
  套件级突变两条各红（正则放宽成单空格→1 failed；豁免恒真→10 failed），逻辑级三突变全红，
  突变后按 sha 复原（pristine `726575d467e62e1da4b44dc9` 复验同值）。
- 入队前最后一秒逐件对读 base==dev／他袋字节：发现车道A 的 0001 **已实现同一需求且面更宽**
  （把 m10/m11 的同族正则收进 `_diff_helpers._make_noqa_pattern` 单口＝在册内收铁律"同真源可派生→必并"），
  而本班版是在自己件内内联一份＝次优面。两袋件面重叠且字节不同，**本班是后袋**
  ⇒ 若照排空，按在册坑"同会话后袋静默超前"会把 A 版实现与 A 版测试面洗掉＝毁他人成果。
- 处置＝**自撤 0002**（mv 通道＋机生台账行 `dead_triage_20261014_maint7.jsonl`，
  记 overlap_files／own_blob_shas／可逆说明），车道B 那两件按 dev 字节复原；
  不投、不改 A 版、不代修 A 版死因（那是 A 实例的当日四态分诊义务）。

## 三、P1 挂死地雷（接维护六班 §十.5 处方，本班落地＝袋 0003）

- 处方两选一**两条都取、各司其职**：展开面（逐格性质断言）走"冻结窄批"，名义格点锚走真源册
  `count_n_raw`（O(维数) 零展开）。
- 病根实测：真源册 16 维，phase>=3 上下文名义 **13,063,680** 格（phase=2 面 725,760、phase=1 面 362,880）；
  标定 compile(362,880)＝**5.20 秒** ⇒ 单格 14.3 µs ⇒ 13,063,680 外推 **187 秒**；
  在册 pytest-timeout＝120s 且 `timeout method: thread`（Windows 杀不掉工作线程）。
  改前实跑两支（node id 逐条）：`test_grid_expansion_x_dims_phase_gating` --timeout=60 → **Timeout**，
  栈＝`position_recipe_compiler.py:276 _expand` → `_canonical` → `json/encoder.py:258 _iterencode`；
  `test_t3b_context_injection_phase3_activates_x` --timeout=45 → 同型 Timeout。
  ⇒ 维护六班册里"json.dumps 栈"与"_expand 展开"是同一病灶的两段栈，本班补齐 node id 与实测数（六班账当时未记 node id，本班已认此缺）。
- 窄批尺的合法性依据是实测不是宣称：`_evaluate_active` 命名空间＝`_SAFE_PREDICATE_BUILTINS + ctx`
  （只读 context 变量，不读其他维取值）⇒ 冻结非受测维不改变任何维的激活/折叠判定；
  受测维值集原样⇒"取值集合恰等于在册集"仍逐格实测。**故意不钉 ×6**：
  实测真源 phase2→3 比值＝18（除 X_stop×X_breaker=6 还有 X_sector 同闸），把窄批比值当真源锚＝自造假判据。
- 改后两支耗时 0.05s／0.02s（原 60s/45s 超时），全文件 32 passed、消费者面 65 passed。
- 登记未动的一处：同文件 `test_grid_expansion_phase2_j_legs_string_semantics` 仍走真源面＝实测 **14.57 秒**
  （725,760 格），未超闸不挂死；按最小爆炸半径本班不动，helper 已在册，下一班三行可收。
- **自纠（在册坑复踩）**：第一次做完突变自证后用 `git checkout -- <件>` 复原，把**未提交的本班修复**一起打回
  dev 面（记忆档 `claim-recovery-copy-not-checkout-and-attribute-by-sid` 禁的就是这个）。
  已重贴全部改动并**先落盘外备份**（`E:/_tmp_m7/t3a_fixed_backup.py`），此后突变一律 cp 备份复原、不再用 checkout。

## 四、P2 接管条目刷新出口（本班落地＝袋 0006）＋当班执行读数

- 病根实测：`--scan` 候选集＝注册表判死轨＋在盘孤儿轨。open 条目一旦"除名＋资源清完"就再不进任何候选集
  ⇒ 带立案当天旧数永久挂 open，L3 按 `entry_match_surface` 逐件挡无辜袋。
  本案场＝`st-deadclean-20261013`：处方三项 23:4x 复验均已归零，条目仍报 `held=3 worktrees=1 heartbeat=1`，
  把维护六班袋 0011 挡成死信（当时只能人工 `--resolve` 绕行）。
- 出口三条硬约束：默认 **dry-run**（与 blob_gc --archive／--sweep-absorbed 同哲学）；
  **五类全零才收口**（含死袋＝有残留一律留 open）；写回带 `force=True` 越 600s 节流窗
  且 **death_evidence 沿用立案原文**（刷新不许改写历史证据）。判零口径与 L1 `collect_resources` 同源。
- 判别力：新测 6 支。零突变 32 passed。突变 1（去掉 force）→ 1 failed，
  读数 `{'held':1,'worktrees':1,'staging':2,'bags':1,'heartbeat':2}`＝旧数没缩掉＝挡道面还在；
  突变 2（`all(v==0)`→`any(v==0)`）→ 2 failed（残留被误收口）。
  **本班自纠一条**：突变 1 第一次跑**没红**——我那条测试当时走的是归零支、不经写账＝无判别力；
  改成残留支才拿到牙（记忆档 `mutation-selfproof-zero-collection-is-not-red` 的同族形态）。
- 同批面（纪律）：模块头 `[INVARIANTS]`＋`[MODIFY-GUARD]`（钉 force 的同批面与测试 node id）＋
  `docs/_working/branch_zero_takeover_20261002/t1_takeover_infra.md` §7 三件同袋。
- 当班执行（令面点名两条，读数如实）：
  - `st-cband-20261012` → **REFRESH: no open takeover entry**（已被别班收口；本班不代做、不造条目）；
  - `st-fclean4-20261012` → EXECUTE `{held:0,wt:1,staging:0,bags:0,hb:1}` → `{held:0,wt:1,staging:0,bags:3,hb:0}`
    ＝旧账把**幽灵心跳记成 1、把 3 只死袋漏记**；留 open（有残留）不越判据收口。
    读回 `refresh_count=2`、death_evidence 原文保留。
  - **全体 193 条一次性刷不当班跑**：`collect_resources` 对每条跑 `git status`，实测 600 秒未返＝IO 风暴。
    出口按 sid 点名为准；要全量请下一班配窗口或另立限速面（此条入 §六 呈批）。

## 五、P-9 设计面（本班只出案卷不出裁定）

实测三数（尺＝`.runtime/takeover_ledger.jsonl` 全行 ＋ `resolved/*.json` 全集）：
- open 行 **193**（唯一 sid 193，无重复立案）；resolved 件 **529**（唯一 sid 253）；
- **同时挂 open 与 resolved 的 sid ＝ 38**，样本 `st-backup-cold-20260924`／`st-acure-r1`／`st-backfix3-20261011`；
- 逐条对读"资源面指纹"：`st-backup-cold-20260924` 10-04 与 10-06 两次 resolve 的资源面都是
  `{wt:1, hb:1}`，而 10-08 **又一次** open，面仍是 `{wt:1, hb:1}`＝**同指纹复开**；
  `st-acure-r1` 同形（10-07 两次 resolve，10-08 再 open 同面）。

⇒ 定性：`resolve` 不是终态——`_scan_orphan_resources` **从不查 resolved 归档**，
只要死车道的 `.aidrafts/<sid>` 目录还在盘上，每次全量 scan 就把该 sid 重新 open 一遍
（10-08T17:47:2x 那一簇时间戳＝同一次 scan 批量复开的痕迹）。
后果＝已被人收过口的会话会反复重新挡道，而挡道面（worktree dirty 文件）由车道残留支撑。

两案（带代价，**未取舍——取舍属统筹/判据面**）：
- 甲＝scan 侧加"同指纹不复开"：对已在 resolved 的 sid，比对资源面指纹（五类计数＋dirty 文件集），
  相同则跳过、不同才新开并注记 `reopened_fingerprint_changed`。
  代价＝指纹口径要钉死（dirty 集是否含 `excluded_dev_identical` 缩窄面），钉错＝真新增资源被吞＝新的静默；
  且需要 resolved 侧留可回读的指纹位（写盘面扩大）。
- 乙＝把"车道目录残留"本身当根因收：死车道退场时目录必须真删（在册"收班即清"），
  orphan 轨自然无从复开。代价＝那是清理执法面不是台账面，且现盘上确有他会话车道（不代删）。
- 本班建议（不自裁）：先乙后甲——乙是既有纪律的执行，甲是给"执行不彻底"兜底的第二把尺；
  两把尺同时上要先证指纹口径，否则甲会把乙该暴露的问题盖住。

## 六、呈批与上报（不代签）

1. **ESCALATION（工具健康自检，令 AI MUST 上报）**：`session_worktree_start` 健康度自检报
   `失败项: ['lookup_audit dir writable']`。实测：主区 `.runtime/lookup_audit` 与
   车道B `.worktrees/.../.runtime/lookup_audit` 均 exists＋writable=True，而自检指向的
   **车道A 根** `.aidrafts/st-maint7-20261014/.runtime/lookup_audit` **不存在**（absent）。
   ⇒ 自检的锚面与登记的工作树根不一致（同号两车道场景下尤甚）；本班未加旗未绕行，如实上报待裁。
2. **会话号并发碰撞需统筹定则**：同一 `st-maint7-20261014` 两实例并存、共用 claim 面与袋序，
   已经造成"后袋洗前袋"的实际风险（本班据此撤袋）。建议＝一班一号，或令面显式分派
   "A 做 P0-甲＋乙／B 做 P1＋P2"（本本班已按此默认分工自洽执行）。
3. **P0-甲 现无在飞袋**：A 版死因是 GATE-TEST 收集错（101 collected / 1 error，具体文件在其七件套测试面内），
   修因属 A 实例；若 A 不复投，建议统筹指定唯一纠正出口（避免 B 再投造成双份）。
4. **`--refresh` 全量面**：193 条逐条 `git status`＝实测 600 秒未返；要常态全量刷新须先立限速/分批面。
5. 主区 index 现含他人 staged 面（车道A 未提交件 7 支）；本班零碰主区 index，全部走队列正门。

## 七、本班未办（自带理由，非遗漏）

- **P0-乙（CREATE-GUARD 瞬时态加固）**：车道A 脏面含 `create_guard.py` 且其袋 0004/0005 已在飞＝
  并发实例正在做，本班不占同一面（纪律：不代修他会话在途件／并发避让是硬约束）。
- P-9 的**修法代码**：本班只出 §五 案卷与两案代价，取舍未获裁，故未动码。

- 署名：st-maint7-20261014（车道B）。本班对 `G:\\backup`／`F:` 零写；未杀停任何进程；
  未 `--force` 越闸、未 `--skip-preflight`；改前 claim、毕后 release。

## 八、统筹四选项裁毕后的补做（③+① 组合＋②＋自检＋三疑点）

### 8-A P0-甲 兜底：做完发现"更宽的那版已在飞"，两袋按内容级自撤
- 本班独立完成甲案（门内 `_M10_NOQA_PATTERN`+`_has_m10_exemption`＋两条判死路径各一次豁免早退
  ＋门自述同批＋11 支三态测；零突变 112 passed；两条突变各红 1／10；按 sha 复原）。
- 逐件对读结论：并发实例的严格超集袋 0010（15 件，含 `_diff_helpers._make_noqa_pattern` 单口收编）
  与本班 7 件**逐件同 sha256**（1e78e665b17a／f8fb2a85a612／6fcd7fbcd88b／43f6c128712e／
  a8bbc9be4468／520ac18557fc／2b7b7d5fb527 七对七全等）⇒ 本班袋零独有条款，照排空只会
  撞 NOTHING_TO_COMMIT 或按"同会话同件后袋静默超前"洗掉超集袋其余 8 件面 ⇒ **自撤 0013**。
- 同理自撤 0012（收集错解堵）：两版机制等价——他们是 module-level `find_spec` 判空 skip，
  我是 `pytest.importorskip`；实测都解掉整目录收集错（我版 2615 passed/1 skipped，他们版
  2630 collected/0 error，同目录同尺）。他们袋在前（0008/0010），本班零独有条款 ⇒ 弃投，
  本班版本存 `E:/_tmp_m7/my_guard.py` 备查。两次自撤均走 mv 通道＋`dead_triage_20261014_maint7.jsonl` 台账行。
- **本班对甲案的两条独立新证据**（超集袋不含）：
  ① 生态声明实测＝全仓 `git grep -l "noqa: m10-time-trigger"` 73 支，逐件喂 A 版尺（装载自车道绝对路径，
     `__file__` 打证避主区预导入假绿）：**认可 72／拒 1**；拒因＝`create_guard` 那件第 795 行把标记写成
     `… m10-time-trigger — 注册表撕裂读失败重试…`——分隔符是破折号且缺 `M10豁免:` 前缀＝在册
     reason_format 意义上的**畸形声明**；该件现靠 `commit_gates/` 路径自豁免才没被挡，属"看着像声明其实不算"
     的潜伏面（该件正被并发实例 P0-乙 持有，本班不代修，只显形）。
  ② 同目录另 11 支红经**同面 A/B 对拍**判为存量红：把 A 版七件回退成 HEAD 纯净面再跑同一批 →
     仍 11 failed（其余 4 支未逐一对拍，如实记"未归因"）。
- A 版死袋 0001 的销账：其死因（整目录收集错）已由 0008/0010 侧解堵，内容面由 0010 逐件承接；
  本班待 0010 落地后按内容级四态分诊销账（判据＝袋字节 vs 落地面 sha，禁按条数估）。

### 8-B 自检误红的真因更正（本班把"锚面 bug"改判为"上报面缺 detail＋并发建道竞态"）
`run_startup_health_check` 在三处根面（车道A／车道B／主区）逐一带 detail 复跑＝**三项全过、status=ok**，
即当时那次 failed **不可复现**；该自检自带 mkdir＋写＋删（会自愈），所以事后必绿。
⇒ 令面"锚到车道A 根而登记根不一致"不成立（三处根面都能写）。真正可复现的缺陷只有一个＝
`[ESCALATION]` 只打检查项名字、不打异常原文 ⇒ 任何瞬时故障（本例＝两实例同一分钟并发建车道的竞态）
都变成永久悬案，两班各报一次却谁都无法定性。修法＝失败项随行走 `name=detail`（扩既有上报面，
检查项／阈值／warn-only 语义零动），并加断言"detail 必须出现在上报行"的测试：
突变（把 detail 摘出 logger.error 参数）→ 1 failed，且当场打出的正是旧的不可定性形态；复原后 7 passed。

### 8-C 三疑点一次定性（尺＝活体读数，不采信任何一方自述）
1. **logical 降级**：机制成立且**已造成真实损害**。`_REREGISTER_MIN_INTERVAL_SECONDS=1860s` 窗内重复注册
   会把 `last_activity` 锚**冻结**（日志原文：`entry alive, logical=False … liveness anchors frozen`）。
   活体读数＝本班会话 `logical=False idle_activity=14.4min 而 idle_hb=0.1min`——心跳在跳、活动锚不走；
   而台账判死用的正是 `last_activity > 7200s` ⇒ **一个只巡检不写盘的长会话会被判死**，
   deadclean 的 5 只 `ghost_session` 死袋与维护六班袋 0011 的 TAKEOVER-PENDING 挡道都是这条链的下游。
   在册解法＝常驻面用 `mark_logical`（日志同一句话已写明），属"谁用谁没读告警"，
   建议统筹在派工令里把"长批/值守会话必须 mark_logical"写成一条硬措辞——这是**措辞缺失**不是代码缺陷。
2. **claim TTL 9-10 分**：**未定性为缺陷，因为那个数在代码里不存在**。四层 TTL 实测各自为政：
   文件锁 `DEFAULT_TTL_S=1800`（30min，`expires_at` 优先）、全局提交锁 `_LOCK_TTL_SECONDS=1800`
   且**只在有人抢锁时惰性判定**、入队续租打印 `ttl=7200s`、session 生命周期 3600s；
   而 `.ailocks/registry.json` 的 34 条活 claim **无一条带 ttl 字段**（读数面缺字段），
   实测最老三条 age=79/103/105 分钟仍挂册（>1800s 也照样在，因为没人来判）。
   ⇒ 能定性的是**观察不可复核**（缺 expires_at＋惰性清理），"9-10 分钟"更像是一次被抢占时刻的旁观读数；
   要钉死需给 claim 落 `expires_at` 并让巡检打印 age/剩余——属放量班面，本班不扩。
3. **同号双实例**：已坐实并全程留痕（§一 袋账＋§八 两次自撤）。机制根＝`session_worktree_start`
   按 sid 幂等复用、**不检测该 sid 是否已被另一活进程持有**，且同一 sid 可对应两棵不同路径的车道
   （本例 `.aidrafts/st-maint7-20261014` 与 `.worktrees/st-maint7-20261014`，分支名规则也不同：
   `session/<sid>` vs `ai/<sid>/task-<x>`）⇒ 共享 claim 面、共享袋序、共享班账文件。
   后果已发生三次：0002 会洗 0001、0013 会洗 0010、0012 会洗 0008——全靠入队前逐件对 sha 才没成真。
   建议（不自裁）：派工令显式分车道（统筹已声明"今日起如此"），并把"同一 sid 只允许一棵车道根"
   做成 start 侧的一条硬校验（成本＝一次 is-dir 双根检测＋拒绝信息可复核）。

### 8-D P-9 甲案已落码（对 0006 严格超集，裁定#521 补签）
详见 `docs/_working/branch_zero_takeover_20261002/t1_takeover_infra.md` §8 与裁定#521 的 evidence 字段。
要点：判据只钉在 `_cmd_scan` 写账前的**唯一消费口**（中途先钉孤儿轨，端到端测试当场判回——
复开实际来自注册表轨，已挪位并撤掉孤儿轨钩子，不留两处实现）；`resolve_entry` 落终态件时同写
`fingerprint`；恒不挡突变→2 failed、恒挡突变→4 failed、复原→38 passed；
投影渲染对 HEAD **+49/-0**（缺 0 行＝零回退；新增行含他班在册行，属 PG 单源既有语义非本班改写）。

## 九、P1-6 调用侧接线：存证授权跨段覆盖 ③remove（本班落地＝袋 0019，与自家测试同袋）

统筹令点名"钩子已存在（`scripts/ops_guard.py:1310 tomb_verification`），缺的只是
`session_worktree.cmd_archive` 携带 MANIFEST 引用那一行接线"。**实测更正**：那一行不缺——
`_archive_rescue_phase` 早已按 `factory(man["manifest"], sid=sid)` 注入（维护六班件⑧落的面），
缺的是**覆盖范围**：ctx 在 rescue 段末尾就 `__exit__` 了，而 OPS-GUARD 真正拦死的是紧随其后的
③remove 段（git worktree 的强制移除，两枚强制旗都要给才删得掉脏树）——删整棵
   `.worktrees/<sid>` 命中的是 `_judge_protected`（PROTECTED_PREFIXES 含 .worktrees/.aidrafts），
PROTECTED_PREFIXES 含 .worktrees/.aidrafts）。授权只覆盖搬文件、不覆盖删树＝死锁原样复现，
这正是"接了线还卡"的观感来源。

改法（不弱化判据、不加旗、不开豁免）：`_archive_rescue_phase` 第三个返回值改成**未收栈**的 ctx
（四条返回路径全部对齐；rescue 自身炸了才 `__exit__(*sys.exc_info())` 就地收），
`_archive_one` 用 try/finally 把收栈点放在删除段之后（无论成败）。无合格存证行时照旧 None＝零授权。

判别力自证（两次变异，各自只红一支，复原按 sha 37914752512b4e9a…）：

| 变异 | 改动 | 读数（重基后复测） |
|------|------|------|
| M1 收栈点挪回 rescue 末尾 | `②b print` → `ctx.__exit__(...)` | 1 failed / 14 passed：`③remove 时无存证授权＝接线断在 rescue 末尾（死锁原样复现）` |
| M2 删掉 finally 收栈 | try/finally → 裸调用 | 1 failed / 14 passed：`删除段之后仍带授权＝收栈点没落在 remove 之后（悬挂豁免）` |
| 复原 | 两文件 cp 回存证面 | 15 passed（配对测试基线；红→复原→绿三步同一张尺，非沿用旧读数） |

⚠**M2 第一轮是假绿，被我自己抓到**：原先只在 `cmd_archive` 返回后读 `get_tomb_verification()`，
M2 变异仍全绿——CPython 引用计数在 `_archive_one` 帧结束时就把未收栈的 context manager 关掉
（生成器 GC 跑 finally），"函数返回后再读"这种写法对"忘收栈"零判别力。正解＝把取样点放进同帧的下一步
（再套一层 `_archive_branch_finish`  spy），才拿到上面那行红。此坑入记忆档。

 payoff 面（待落地面复测，勿在此自证）：接通后卡死车道退场应只需一条
`python scripts/session_worktree.py archive <sid> --execute`。本班不能自证——①主区磁盘码还没这行
（HEAD≠运行面，见记忆档），②自家会话活着时 archive 硬拒且无逃生旗。落地后由放量班/死信班对
四棵卡死车道（含 deadmass 自班）逐棵复测并回报命中面。

净零声明：0 新门 0 新脚本 0 新配置册——扩既有 gate 的执行面（把已存在的授权用到它该用的那段），
配对测试落在既有 archive 测试件（+2 用例 +1 helper，同文件）。

### 9-B 顺带实测到一枚 HEAD 级存量红（非本班件，只登记不代修）
`tests/gov/governance/audit/test_file_ops_enforcement.py::TestReconcilerContextEnforcement::test_undeclared_delete_blocked_and_critical_warn`
在**车道与主区两面同红**，两文件对 HEAD 零差异（`git diff HEAD --stat` 空），故与本班改动无关。
根因不是猜的——用打印壳量到实际读数：`_resolve_to_repo_rel('docs/important.md', cwd=None)` 返回
`E:/_tmp_m7/.../docs/important.md`（绝对路径），`_enforce_file_ops` 按批5b 的**仓外豁免**判"放行"
（ctx 确实在册=('EVIL', {'read','write'})，即上下文注入没失效，是豁免面把它吃掉了），
于是 `guard_remove` 正常执行、reconciler 返回 clean，测试期望 critical_warn 落空。
机理含义（供统筹定性，本班不自裁）：测试用 `monkeypatch.chdir(tmp_path)` 把 cwd 搬到仓外，
声明制对"仓外 cwd 下的相对路径"整体让路——若某 reconciler 真在仓外 cwd 里跑，未声明的删除也不受阻。
这条与本班 P1-6 同族不同件（那件是"授权面没覆盖到该删的那一步"，这件是"豁免面覆盖过宽"），
修法要动判据，须先枚举全部 reconciler 的 cwd 面再呈批，故只登记。

### 9-C 入队侧撞到的两件事（都是账面纠正，不动判据）
1. **CREATE-GUARD 把车道件当"新建 .py"**：走 `git_commit.py --enqueue` 时预检拿到的路径面带
   `.worktrees/<sid>/` 前缀（主区 HEAD 树里当然查无此路径）⇒判"无 creation_token，禁止造第二真源"。
   这不是判据错，是**喂给闸的输入指向**没剥前缀——与维护六班 M-3（PROTECTED-PATHS 拿带前缀的路径
   去查册⇒有授权也判查无）同族的第二个实例。本班不自裁修它（`create_guard.py` 正被车道A 的
   0010/0015/0018 三个在途袋整档持有，改它就是撞车），改走 `commit_queue.py enqueue
   --worktree-root <车道>` 的正门（该腿剥前缀），零豁免、零 token 注册、零加旗。
   呈统筹一条：这族病灶已复现两次，收敛点＝**入队侧统一做一次前缀归一**，而不是每条腿各修各的。
2. **L3 池面回退预筛拦下本班**：讯息面 `dev 在你基底之后新落的 47 行不在这份字节里`。实测分母更大——
   dev 面 280 行 vs 我基底 209 行：死信放量班（st-deadmass-20261013，1a19b080e9）在**同一测试件**尾部
   追加了 6 支 `_prune_session_shell` 用例＋1 支端到端。正解按在册处方"先重基再投"：以 dev 面为基
   重放本班改动（用存证副本 cp＋逐处 Edit，不用整树复位去覆共享 index），投前用**多重集**自证
   "我面缺 dev 行 shortfall=1（唯一那条是我自己扩写的 [INVARIANTS] 头）、新增 88 行"，
   然后 M1/M2/复原三步在同一张重基面上复测（§九 上表即复测读数：1/14、1/14、15 passed），
   不沿用旧读数。`scripts/session_worktree.py` 也单独量过：dev 1466 行＝我基底 1466 行，
   "我面缺的 13 条 dev 行"逐条都是我被替换掉的旧形态⇒该件无需重基（勿把"行数相等"当"内容相等"用，
   13 条是逐条读出来的）。

## 十、统筹增补令：序列化落地链导出 ZEPHYR_ALPHA_ROOT=worktree（本班落地，配对测试同袋）

### 10-A 归属判定（令面没写车道号，按实测三条判"接手"）
①队列 pending 中**无任何袋**碰 `scripts/commit_queue.py`／`scripts/governance/commit_queue_landing.py`
（只有一本 wkcure 的 plan 文档）＝未认领；②车道A 在途袋持 `commit_gates/*`＋`projection_generator.py`，
本班在途 10 只袋也不含本案面＝零撞车；③这病正是本班今晚自己被拦的那族（落地链跑的码面≠被落的码面）。

### 10-B 令面引用更正（一处查无，一处另有真源）
令写"A/B 实证在 **libstale 班账 §9**"。**dev 面与 libstale 车道面都只到 §7**，且 §6 讲的是
图书馆 title join，与此无关——该引用不成立。真证据在
`docs/_working/lane_c_chain_night/e1_mine_repair.md` §5.1（车道C 班原文实打）：
"不设该变量时 pytest 的 `zephyr.*` 导入全部命中主区旧代码（本次 MCGINLEY 测试先红后仍红即此因，
`find_spec` 与实际 import 分裂为实证）"。本班按实测证据施工，不按失效引用施工。

### 10-C 机理自证（两钮复测，只读零写入）
`usercustomize.py:26-34`（LSG 运行时网引导）实测只认这一个开关：`ZEPHYR_ALPHA_ROOT` 存在才把
`<root>/src` 放进 `sys.path[0]`，**缺省硬编码主区根**。在 serializer worktree
（`.runtime/commit_queue/worktree`，实测该处 HEAD=8e4c54ead5）里跑同一句 import：

| 钮 | 读数 |
|---|---|
| 不设 env（现状） | `D:\ZephyrAlpha\src\zephyr\shared\io\file_utils.py`＝主区磁盘码面 |
| 设 env 指 worktree | `D:\ZephyrAlpha\.runtime\commit_queue\worktree\src\zephyr\...`＝被落的那一面 |

后果链：落地→`git commit`→pre-commit 钩子→**子进程** pytest 读主区旧码面；"码＋测同袋"的合法提交
因新符号在子进程里查无而收集报错→被迫拆成"册先行袋＋代码后继袋"（深队列下必崩，已在册死因）。

### 10-D 修法与覆盖面
新增 `WorktreeLanding._code_face_env_scope()`（contextmanager，进入指 worktree、finally 复原：
调用者原本有值则**回填原值**、原本没有则**删除**），包住 `__call__` 里**两处** `gateway.commit`
调用段（主调用＋Mode B pathspec 自愈重试；两处都在同一函数内，legacy drain 与 k=4 池工共用此入口）。
方向＝只改**喂给子进程的码面指向**（与统筹在册正解同族：修输入指向，不弱化判据、不加白名单、不开豁免）；
门禁判据/阈值/豁免面零变化。子进程 env 经 `_trusted_git_env()=dict(os.environ)+2` 继承，实测已通。

⚑**实效条件声明（统筹 03:xx 裁定要求写入，防后来人当永久保证）**：本钮的生效面是
"**下一轮 drain 起**"——本班 2026-10-14 03:xx 实测**无常驻 python 守护进程**
（`Get-CimInstance Win32_Process` 按 `belt|daemon|drain` 过滤零命中），落地由短命进程自举，
故 0021 落地后下一轮 drain 即吃到；**若日后起了常驻 belt/serializer 守护进程，它内存里是旧码面，
必须重启才吃到这颗钮**（在册同族教训：HEAD 有修复而运行面读磁盘/内存旧码）。不要把"已落地"
读成"全链已生效"。

### 10-E 判别力自证（三向变异，各自只红该红的支路）
基线/复原＝3 passed；`_StubGateway` 缺 `allow_overlap` 形参这条**存量红**（见 10-F）会挡住端到端支路，
本班自家桩就地吸收该形参，不让新判别面挂在别人的红上。

| 变异 | 改动 | 读数 |
|---|---|---|
| M-A helper 建了但调用点没接 | 两处 `with self._code_face_env_scope():` → `if True:` | 1 failed / 2 passed：只红端到端那支（`test_gateway_commit_runs_inside_code_face_scope`） |
| M-B 出作用域无条件删 | finally 的分支回填 → `pop(...)` | 1 failed：只红原值回填那支（`..._restores_preexisting_value`） |
| M-C 钮指向主区＝修复前语义 | `str(self.worktree_path)` → `str(self.repo_root)` | 3 failed（三支全红，正是"码面指错地方"的应有面） |
| 复原 | 按 sha 6f571db28df5b384 对读，标记零残留 | 3 passed |

取样点全部落在**同帧内**（`commit` 被调用的那一刻读 env），沿用 §九 那条自纠——"函数返回后再读"
在这类作用域判据上零判别力（CPython 帧退出时 GC 会把未收栈的 context manager 关掉）。

### 10-F 零新增回归的对照面（同件改前/改后各跑一整轮）
| 跑面 | 采集数 | 读数 |
|---|---|---|
| 主区改前（HEAD 现面，不含本班 3 支新用例） | 99 | **27 failed / 72 passed** |
| 车道改后（含本班 3 支） | 102 | **27 failed / 75 passed** |

⇒ 失败集合与数量**一字未动**，本班新增的 3 支全绿＝零新增回归。

### 10-G 那 27 支 HEAD 级存量红（非本班件，只登记不代修）
两条实测死因（各举一支取到原文，非推断）：
1. **桩签名落后生产**：`_StubGateway.commit()` 无 `allow_overlap` 形参，而落地路径自 2026-10-05
   （二层⑤）起无条件传 `allow_overlap=True` ⇒ 凡真跑到 commit 的既有用例一律
   `TypeError: _StubGateway.commit() got an unexpected keyword argument 'allow_overlap'` 进死信。
2. **入袋基底缺位**：既有用例调 `cq.enqueue_item(...)` 不带 `base_head/base_blob`，而生产侧现在
   fail-closed——原文实打："注册表项基底不可知（base_head 与 base_blob 皆无）——拒绝以
   `<sha>^` 猜基底做合并（09-24 热册被吃病根）"。
两条都是**测试面落后于落地面**的漂移，修它＝给该件补 harness（并逐支核 27 支的期望语义是否仍成立），
属放量/治理班的事；本班不自裁（改它会把别人的失败"顺手改绿"，掩盖语义漂移）。
登记的用处：这 27 支正是"码面≠被落码面"族里的自家人——同一件事在测试侧的第二实例。

## 十一、统筹预警（0010/0015/0018 连投同带 perm_trigger_gate.py）——本班判定：不投，并更正三处口径

预警原文没标车道号，而"你名下"三字是**同号双实例**的产物：`session_worktree_start` 按 sid 幂等复用、
不检测该 sid 是否已被另一活进程持有（§8-C 第 3 疑点已坐实），于是车道A 的三只袋也挂在
`st-maint7-20261014` 名下。内容归属看文件面就能判清：0010/0015/0018 三袋同带
`perm_trigger_gate.py`（sha `6fcd7fbcd88b`）＋`create_guard.py`＋`registry_yaml_parse_gate.py`
＋投影生成器＝**车道A 的 P0-2/m10 面**；本班 12 只袋无一只碰这些件。

### 11-A 实测态（触发条件未成就，故本班零投）
| 袋 | 态 | 读数 |
|---|---|---|
| 0010 | **dead** | `cascade_stale: 基底重校验不适用 ['create_guard.py', ...]`——令面担心的形态确实发生了，只是先死的是队首那只 |
| 0015 | pending | base `9631a2e378`，**无 stale 标记**，15 件，含 perm_trigger 同字节 |
| 0018 | pending | 同上；守卫件是**另一版字节**（见 11-B③） |

令面处方写"死则把增量按当刻 dev 重基另投小袋"——**判据未翻**（0015/0018 仍在队）。此刻代投
＝把车道A 的在途字节变成回退弹（在册处方：代投车道的在途字节会因"车道自己后落地"而变弹，
让它死勿 requeue；代投前必须逐件做超集判定）。且车道A 实测 **15.8 分钟前仍在写盘**
（`.aidrafts/st-maint7-20261014` 最近文件 mtime），它会自己处置。本班动作＝零投＋读数回呈。

### 11-B 三处口径更正（都取到原文/实跑，非推断）
1. **"搁浅"是真的，但性质要说准**：m10 逐件声明解析的实现体**一行都没进 dev**——主区
   `perm_trigger_gate.py` 全文只有 1 处 `m10` 命中（它自己那行自免 noqa），而 0010 袋内同路径件含
   20 处（`_M10_NOQA_PATTERN`/`_has_m10_exemption`/两处消费点＋"与姊妹子检查 m11 对称化"甲案注记）。
   所以不是"可能搁浅"，是**目前只活在袋字节里**（死袋 `dead/blobs`＋两只在途袋）。
   可恢复性另有底：死信 blob 是永久备份，按 path＋sha 反查即可重放，不会真丢。
2. **令面把时序说反了**：担心的是"0010 先落、0015/0018 死于双侧皆改"，实测是 **0010 自己先死**
   （cascade_stale 的"基底重校验不适用"打在 create_guard.py 上），0015/0018 尚未被标 stale。
   真风险不是"增量随队首死"，而是"三只全死且无人重基"。
3. **"已知红的那支"现在就是红的**，不是将来的风险：主区实跑
   `tests/gov/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py` ⇒
   `ModuleNotFoundError: No module named 'zephyr.gov_enforcement.commit_gates.map_family.strategy_card_lifecycle_map_gate'`
   （1 error，死在收集阶段）。守卫字节只在 0015（blob `c5a2f649…`）与 0018（blob `26d2fae8…`）里，
   而两袋同 sid 同件 ⇒ **后袋 0018 静默超前**（已在册机制，无声明）——所以要保的是 0018 落地；
   单独救 0015 会白做。给统筹的推论：若 0018 也死，接手序是"按当刻 dev 重基投 0018 那一版守卫字节
   的超集"，而不是重放 0015。

### 11-C 若判据真翻（0015/0018 也死）本班的接手前置三条（先写死，免临时争辩）
①逐件超集判定（袋 blob 行多重集 ⊇ 当刻 dev，Counter 级，非条数级）；②车道A 活性三证齐
（该 sid 队列无新袋／worktree 无新写／commit 尾标无续投——只心跳停更不足以判死，在册教训）；
③统筹或 Owner 明示授权代投。三条不齐就不投，改报"增量的可恢复位置＋重放配方"。

## 十二、实袋复验的两端读数＋维护线 P2 backlog 登记（统筹 03:xx 裁定入账）

### 12-A 复验试车件＝本班自家袋 0014（天然的"码＋测同袋"形态，无需造假样本）
0014 的测试件 `tests/gov/governance/rule_bridge/test_session_worktree_health_check.py` 里
`test_escalation_log_carries_failure_detail` 做 `from zephyr.gov_enforcement.rule_bridge.session_worktree
import session_worktree_start`（**zephyr.\* 面＝正好归这颗钮管**），并断言**只存在于同袋代码面**的新行为
（上报行须带异常原文）。⇒ 它不需要新造样本，今晚就在队里排着。

| 钮 | 导入面（实跑打印 `m.__file__`） | 该面 `failed_detail` 出现次数 | 同一句测试读数 |
|---|---|---|---|
| 关（不设 ZEPHYR_ALPHA_ROOT，usercustomize 在岗） | `D:\ZephyrAlpha\src\zephyr\gov_enforcement\rule_bridge\session_worktree.py` | **0** | **1 failed / 6 deselected**，实打旧形态行：`失败项: ['lookup_audit dir writable']`（只有名字没有原文） |
| 开（ZEPHYR_ALPHA_ROOT=车道根） | `D:\ZephyrAlpha\.worktrees\st-maint7-20261014\src\zephyr\...` | **2** | **1 passed / 6 deselected** |

⇒ 这颗钮的唯一可证收益面就此闭合：**钮关时"码＋测同袋"的提交在钩子里必红**（今晚被迫拆袋的机理原样复现），
钮开即绿。落地后的收尾一步＝0021 先落，再看 0014 是否**以单袋（码＋测同袋）形态直接 done**
（而不是像今晚那样死于"新符号在子进程查无"）；该读数只认 `git log -- <两件>` 真落地，不看自报。

复现命令（两条都真跑过）：
- `cd .worktrees/st-maint7-20261014 && env -u ZEPHYR_ALPHA_ROOT -u PYTHONPATH python -m pytest tests/gov/governance/rule_bridge/test_session_worktree_health_check.py -q -k escalation_log_carries --basetemp=E:/_tmp_m7/bt_off` → 1 failed
- 同句前置 `ZEPHYR_ALPHA_ROOT=D:/ZephyrAlpha/.worktrees/st-maint7-20261014` → 1 passed

### 12-B 维护线 P2 backlog 登记（统筹裁定：27 支存量红**不修**，两根因入册）
1. `_StubGateway.commit()` 缺 `allow_overlap` 形参，而 `commit_queue_landing` 自 2026-10-05 起
   无条件传该实参 ⇒ 凡真跑到 commit 的既有 landing 用例一律 `TypeError` 进死信。
2. 既有 landing 用例调 `enqueue_item(...)` 不带 `base_head/base_blob`，被现生产侧 fail-closed 拒
   （原文"注册表项基底不可知……拒绝以 `<sha>^` 猜基底做合并"）。
两条同属**测试面落后于落地面**的漂移；修法＝补 harness＋逐支核期望语义是否仍成立＝属主面，
本班不自裁（顺手改绿会把语义漂移洗成"通过"）。建议派给 landing/队列属主班，判据面零变化。

**为什么这两条写在自家班账而不是 `maint7_campaign/00_ledger.md`**（实测理由，非偷懒）：该共享册
正被车道A 的在途袋持有领先面——dev 现面 224 行，而 0020 袋 280 行、0022 袋 286 行
（盘面缺该袋行 48/54）。我此刻往里追加＝把车道A **未落地的 48-54 行装进我的整档快照**＝归属篡改面
（在册红线：袋＝整档快照）。交接方式＝待 0022 落地后由任一后续班把 12-B 两条尾追加进该册 §六，
或直接以本节为源（本文件是我自有件，0019/0021/0023 三袋对同件均为严格超集链）。

## 十三、交接卡（统筹午间全线收口令 §③；本班收班时点＝2026-10-14 12:2x）

本节是**唯一交接真源**（新总指挥不依赖任何对话记忆）。每条都给"当刻实测读数＋复核命令＋判据"，
命令均可直接复制执行（本班已按"交付件复核命令必须从正文抽出原样跑到期望值"自查过形态）。

### 13-A 队列 9 小时后的实测态（本班收班前最后一轮，12:13 读）
| 袋 | 态 | 读数/死因原文（截） |
|---|---|---|
| 0003/0004/0005/0006/0007/0009/0011 | done | 维护七班 P1 挂死地雷／P2 刷新出口／U+0082 修复／班账 已落地 |
| **0014** | **done** | `73ea414a85bc`＝**代码＋自家测试同袋直接落地**＝§12-A 那颗钮的收益实证已在 |
| 0008/0016/0017/0019/0021/0023/0024 | dead | 两类死因：`cascade_stale: 基底重校验不适用 […]`／`非注册表族件双侧皆改真冲突（整文件三方…）` |
| 0010/0015/0018/0020/0022 | dead | 车道A 面（m10 甲案＋P0-2 读面加固＋共享册） |

**死因实测定性（重要，别再归错因）**：本班 12:13 逐件量过——我车道面 vs 当刻 dev（`b5e58bef79`）
在 9 只件上**全部是超集**（去缩进多重集 shortfall：landing 件 1／其测试 1／`scripts/session_worktree.py`
8（全是我被替换的旧形态）／archive 测试 1／takeover 册 1／其测试 0／t1 册 0／守卫件 0／本班班账 0）。
⇒ 袋不是"内容过期"，而是**基底取到车道旧 HEAD `63a1b437ab`** ⇒ 落地仲裁按"双侧皆改"判真冲突
（在册同族：`lane-base-head-three-way-conflict`、`enqueue-preflight-base-from-worktree-head`）。
正解＝以 **scratch@dev 为工作区根**复投（件面不变、基底=当刻 dev），本班已按此复投，
新 qid 见 13-B；复投后的地面核对命令也列在 13-B（勿只信"ENQUEUED"）。

### 13-B 复投件与落地核对（逐条给命令，判据只认落地面）
| 复投内容 | 死袋前身 | 落地核对命令 | 期望读数 |
|---|---|---|---|
| 落地链导出钮（`scripts/governance/commit_queue_landing.py`＋`tests/gov/governance/test_commit_queue_landing.py`） | 0021 | `git log --oneline -2 -- scripts/governance/commit_queue_landing.py tests/gov/governance/test_commit_queue_landing.py`；`git show HEAD:scripts/governance/commit_queue_landing.py` 数 `_code_face_env_scope` | 两件同批出现；计数 **≥3**（def 1＋两处调用点） |
| P1-6 存证授权跨段（`scripts/session_worktree.py`＋`tests/meta/scripts/test_session_worktree_archive.py`） | 0019 | `git show HEAD:scripts/session_worktree.py` 数 `tomb_ctx` | ≥4；`git show HEAD:tests/meta/scripts/test_session_worktree_archive.py` 数 `spans_remove_phase` ≥1 |
| P-9 甲复开防线（`scripts/governance/session_takeover_ledger.py`＋其测试＋t1 册） | 0016 | `git show HEAD:scripts/governance/session_takeover_ledger.py` 数 `settled_same_face` | ≥2（0＝未落地；12:13 实测 dev＝**0**） |
| 守卫件拆雷（`tests/gov/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py`） | 0008 | `git show HEAD:…测试件` 数 `importorskip`；再跑该件 | ≥1 且收集错误消失（12:13 实测 dev＝**0**，主区仍 `ModuleNotFoundError`＝活雷） |
| 本班班账（本件） | 0017/0023/0024 | `git show HEAD:docs/_working/maint7_campaign/lanes/lane_b_closeout.md` 行数 | ≥460（含 §九～§十三） |

**未随袋的一条（如实登记，勿误读成"已落"）**：P-9 甲的**裁定号那腿**（`ruling_registry.yaml`）
不在这次复投里——该册是 PG 单源＋投影面，12:13 实测我面与 dev 面的 **ruling id 集合零差**
（我多出的 81 行不是新裁定条目，是渲染位移），把整档快照投进去＝可能把他班未落地行吃进我的袋
（在册红线：袋＝整档快照＝归属篡改）。正解＝走 `api.register/publish_snapshot` 正门补号后
`registry_projection_generator --render`，再由门读投影验证；这腿交新总指挥派工。

### 13-C 车道A 面的三件遗物（新总指挥须派复投，本班不代修）
1. **m10 逐件声明解析**：dev 面 `perm_trigger_gate.py` 全文 `m10` 命中 **1** 处（仅其自免 noqa），
   实现体（`_M10_NOQA_PATTERN`/`_has_m10_exemption`/两处消费点）**只活在死袋 blob 里**
   （0010/0015/0018 同 sha `6fcd7fbcd88b`，`dead/blobs` 为永久备份，按 path＋sha 可反查重放）。
2. **B 版守卫**：`0015`（`c5a2f649…`）与 `0018`（`26d2fae8…`）同 sid 同件双版并存——后袋静默超前，
   要保的是 `0018` 那版；本班复投的守卫件即 B 版文本（统筹裁定"守卫文本取 B 版"）。
3. **共享册 `maint7_campaign/00_ledger.md`**：dev 面 224 行，而 0020（280 行）/0022（286 行）持有
   领先面且均已死 ⇒ 该册有 56-62 行只活在 blob 里。谁接手谁先按 path＋sha 反查再重基，
   勿从主区盘面起写（盘面＝224 行旧面）。

### 13-D 待他班前提/待批项（本班不自裁，全部带判据）
- **四棵卡死车道退场**：P1-6（0019）落地后逐棵跑 `python scripts/session_worktree.py archive <sid> --execute`；
  若仍撞保护区死锁＝钮未吃到或该袋未落，**留一条命令交下一班，禁硬闯、禁加旗**。
- **27 支 landing 存量红**（§12-B 两根因）＝属主面，建议派放量/队列班。
- **`_resolve_to_repo_rel` 仓外豁免覆盖过宽**（§9-B，实测原文在册）＝动判据面，须先枚举全部
  reconciler 的 cwd 面再呈批。
- **入队侧前缀归一**（§9-C，同族第二实例：CREATE-GUARD／lock_files N-06 各一次实测）＝收敛点在
  入队腿统一剥 `.worktrees/<sid>/`，不是每条腿各修各的。
- **P2 刷新出口立法本体**：出口判据两支涉及 192 条历史 open 条目与治理资产净删面（根宪法 §5 墓碑制），
  需 Owner/统筹择一，非本班可拍。

### 13-E 本班收班动作清单（12:2x 实做，做到哪记到哪，未做的写明为什么未做）
①**复投**：以 scratch@dev（`.worktrees/st-maint7-reship`，HEAD=b5e58bef79）为工作区根重投，
件字节与死袋 blob 逐件全等（sha 对读：`d08563e72799`/`8b69ca725741`/`37914752512b`/`1f8912963621`/
`8282e11d188f`/`a975c3cf80ba`/`8134e0a2be35`/`26d2fae8acb6`/本件）；新 qid 与 base_head 实测见 13-F。
②**逐字读回**：复投袋的 bag blob == 盘面字节（本班逐件核过）；**落地后读回未做**＝要等队列排空，
本班不待，核对命令在 13-B。
③**release claim**：未做。原因带判据——见 ⑤ 的 ghost_session 链条，claim 随袋一起在飞；
本班离场后这些 claim 会随 TTL（入队续租 7200s）自然过期，下一班若要抢同一件按在册处方用
`gateway.release_files('<sid>', files)` 精准释放即可（死会话 stale claim 挡道的处方在册）。
④**守护按 PID 精确停**：本班未起任何常驻守护（12:2x 实测 `Get-CimInstance Win32_Process` 按
`belt|daemon|drain` 过滤零命中），无可停对象；自造物仅一枚本地一次性时程
`189f8070-5716-43b5-b9c5-9f2ceb3c90eb`（原定 04:20 跑落地后复验），12:2x `qoder_cron list` 实测
**已不存在**（`deleteAfterRun=true` 到期自删），其独立会话输出本班读不到 ⇒ 复验改由 13-B 命令交下一班。
主列表内另两枚 `53a70da1…`/`d39ddeb6…` 属备份线（st-bakdr），**非本班造物，本班不动**。
⑤**注销会话＋⑥归档车道**：未做，且**故意不在本班做**——判据实测：`scripts/commit_queue.py:2110
_session_ghost_dead`→`_mark_ghost_dead_fields` 的 dead_reason 原文为
"ghost_session: 属主会话 <sid> 已死（heartbeat=exited / 注册表无在册），自动重投被存活闸拒绝"
⇒ **会话先注销＝把 13-B 那五只复投袋在 drain 拾取点直接打成 ghost_session 死**（在册教训
`heartbeat-idle-exit-makes-queue-mark-bag-ghost` 同一链条）。归档同理：车道在档＝复投袋的
盘面存证面消失，且本班 0019 那颗钮尚未吃到，归档会撞保护区死锁（令面要求＝留一条命令交下一班，
禁硬闯）。⇒ 交下一班的两步命令（待 13-B 各袋 done/dead 定型后按序跑）：
`python scripts/git_commit.py --release-only --session st-maint7-20261014 --files <13-B 清单>`
→ 注销会话 → `python scripts/session_worktree.py archive st-maint7-20261014 --execute`
（scratch 那棵一并 `git worktree remove .worktrees/st-maint7-reship`；若报保护区死锁＝钮未吃到，
按 §九 的接线判据定位，勿加旗硬闯）。
⑦**reaper keep 行**：本班未向 `data/runtime/process_reaper_keep.txt` 登记过任何行（未起长批），
复核命令见 13-F；若他人袋名撞进该文件属他班面，本班不删别人行（在册红线）。
⑧**终账**＝本节。

### 13-F 收口取证（新总指挥可逐条原样复跑）
- `python scripts/commit_queue.py status --session st-maint7-20261014`（Python 3.12 先上 PATH）
  ⇒ 12:2x 实测复投首袋 `q-20261014-st-maint7-20261014-0026` 的 `base_head = b5e58bef791d`
  ＝**当刻 dev**（对比死袋 0021 的 `63a1b437ab`＝车道旧 HEAD），两件 blob sha 与死袋逐字全等
- `python scripts/lock_files.py list`（期望：本班名下 claim 为 13-B 九件，分布于两棵车道根）
- `python -m zephyr.trading.process_reaper --status` ＋ `Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'belt|daemon|drain' }`（期望零命中＝本班未留守护）
- `Select-String -Path data/runtime/process_reaper_keep.txt -Pattern 'maint7'`（期望零命中＝本班未登记 keep 行）
- `qoder_cron list`（期望无 `189f8070` 条目；备份线两枚 `53a70da1`/`d39ddeb6` 属他班，勿动）



