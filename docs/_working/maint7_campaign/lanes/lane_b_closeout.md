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
