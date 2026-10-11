---
ttl: task_bound
owner: st-maint2-20261011
campaign: 维护二班 → 维护三班 交接包
---

# 交接包 · 指向维护三班 st-maint3-20261011（统筹收口令第 2 项）

> 出处＝总统统筹 2026-10-11 收口指令"候件清单随 §八 一并写入交接"。
> 证据等级：【实测】＝本班今跑过的读数；【指针】＝统筹口中项、本班**无实测账**，不代为立项内容。

## 一、本班未结清的落地面（三班第 0 项：先核这两袋，勿重写内容）

| 袋 | 内容 | 现势 | 死因/处置 |
|---|---|---|---|
| `q-20261011-st-maint2-20261011-0016` | §八 台账追加＋19_ 工单结单段＋pristine 探针钉基线修复（3 件） | **dead** | `ghost_session`＝属主心跳守护 idle>1800s 自退被存活闸判死（本班正治的病，班内第 4 次咬自己）。复投配方＝按 §0 正门重注册(pid=0)＋重拉 heartbeat_daemon 后**重新 enqueue 新袋**（勿 `--from-bag`） |
| `q-20261011-st-maint2-20261011-0013/0014/0015` | 治理面＋代码袋＋保活正门追加袋 | **done** | 已落 dev（`4cc45d7f07`／`c869c0a3b5`／`01513460c2`） |

核账命令（进程外可验）：
```bash
git show dev:docs/_working/maint2_campaign/00_ledger.md | grep -c "^## "         # 应 8（§八 落地后）
git show dev:docs/_working/maint2_campaign/00_ledger.md | grep -c "0 增 / 11 删"  # 应 ≥1
git show dev:docs/_working/maint2_campaign/19_chief_ruling_receipt.md | grep -c 工单结单段  # 应 1
git show dev:tests/gov/session/test_session_keepalive_ghost_gate.py | grep -c _PRISTINE_REF # 应 ≥1
```

## 二、C-1 巡检闸（暂存池"HEAD 真子集回退弹"）——两个实物样本

**判据方向**：入队预检/落地侧对每条 staged/袋面条目做**删除行归因**——若该条目字节是其
HEAD 版的**真子集**（工作区独有 0 行、HEAD 独有 N 行）⇒ 告警或拒纳；落地侧另可强制三方合并。
本班已备可复用零件：`commit_queue._snapshot_head_regressions`（三方 `lines_only_in_head` 尺，
行尾先归一防第四把口径假案）＋`ghost_gate_counts()` 逐出口计数写法。归属＝队列/落地车道。

| # | 样本 | 实测两把尺 | 状态 |
|---|---|---|---|
| 1 | `scripts/git_guard.py`（主区暂存那份把已落 dev 的 stash 治理整段打回：`STASH_READONLY` 复含 `drop`、`STASH_DESTRUCTIVE`/`_handle_stash_destructural` 灭） | 04:2x 实测：33 件整档 `M ` 已暂存（+841/−3542），通告 `stash_notice.json` 停在 10-10 17:23 零登记 | **移交中**（Owner 裁定②：认领截止 2026-10-12 13:5x，逾期逐路径复位 `git restore --staged --worktree --source=dev -- <单路径>`，禁整池） |
| 2 | `scripts/governance/session_takeover_ledger.py`（`extra_death_evidence` 三证配套面被纯删） | numstat **0 增/11 删**；行集合法 盘独有 **0** 行、HEAD 独有 **9** 行；`grep -c` 盘 0／HEAD 5 | **已结**：总统筹 06:5x 授权、由总统筹池面按 HEAD 复位（旧字节归档 `.runtime/tmp/pool_rollbackbomb_20261011/code_drift/`）；本班只读复核盘 0→**5** 证实恢复。损害已发生＝`_salvage_takeover_ledger()` 显化腿今日 **0/4** 覆盖（06:26 尚带三证字段、08:56 起 4 条全无），日志 write failed 10 次 |

⇒ 样本 2 已被本班落的**合同闸**试件覆盖（调用方实参 ⊆ 被调方形参，且"手工剥形参⇒精确红"的有牙自证）；
　 样本 1 仍待闸门化——它没有"形参合同"可校验，需要的是**池面删除行归因**本身，这正是 C-1 的剩余价值。

## 三、其余交接项（含两条无实测出处的指针，如实标注）

| 项 | 内容 | 出处与本班立场 |
|---|---|---|
| 预存红总账 | 本班跑出的基线红点名（非本班造成，勿当成本班债）：`tests/gov/git` 11 条（6＝`_GlobalCommitLock` 锁路径按设计锚主仓根⇒车道内必红；5＝`test_w5_gate_chain_parallel.py` 引用 dev 全仓查无符号 `cgr.SERIAL_EXECUTION_GATES`）；`tests/gov/session/test_session_conflict.py` collection error（`zephyr.orchestrator.lifecycle` 已搬 `_archive/`，属⑥实测 19 条真断链）；`tests/gov/governance/registry_projection` 外的 queue 家族 A/B 同败（integration 7f、pool+ghost_pending+belt 15f、其余 queue 14f——换回 dev 原版字节逐条同败） | 【实测】数字全在本班 `00_ledger.md §五` 与 `19_` 回执内，可复跑 |
| Welch 收编 | **本班无实测账**：`grep Welch` 在 `00_ledger.md` 与 dev 面均 0 命中，出处＝统筹收口令 | 【指针】请三班向统筹取原始工单句，再立项；本班不代为编造判据 |
| 环境债台账落点 | 已落 `docs/_working/maint2_campaign/18_env_debt_ledger.yaml`（净零申报；一条债＝一对"在册申报值 vs 本机实测值"；条目由件内 `generation_command` 现算） | 【实测】首条 ENV-001＝`requirements.txt:5-10` 裁定 `#ARCH-TORCH-CPU-ONLY` 要求 `2.13.0+cpu` vs 实测 `2.13.0+cu126`＋`cuda.is_available()=True`（判据取后缀）；**降级动作未做**（花钱/环境类且撞 GPU 班同机窗），待 Owner |
| T15 评级序 | 已按 Owner 直裁 B 落 dev（属主道 `import:zephyr.nlp.research_rating.RATING_SCORE`）；本班撤回自车 `ref:` 重复拼法（第二真源） | 【实测】卡仍 blocked：OPS 册无算子 `rating_upgrade_cluster_share`、`research_report` 未入 `_REGISTERED_TABLES`、母卡受 G4-5 冻结需 v2 卡 |
| 门分叉（本班新发现，建议入 C-3） | TRANSLATION-COVERAGE 门本体豁免 `tests/`，但**入队预检等价判定不豁免**⇒ 本班三枚测试件连烧两袋，最终靠给测试件补大白话简介才通 | 【实测】另有一条同类：`dead_letter_prescriptions` 8 处教不存在的 `requeue --adopt-prior-work`（本班已改）。归属＝门禁/预检同一性面 |
| 存证重贴通则（候选） | "存证重贴"前必须先比 dev 现值：未落地修复与已落地内容同名并存时，无条件覆盖＝自己回退自己的修复（本班 align 脚本末步踩过，3 红当场暴露后重贴修复） | 【实测】与 C-1 同族、方向相反（自家回退自家） |
| 心跳保活 | ⑤ 已落 dev（`01513460c2`＋`c869c0a3b5`）：`logical=True`＝register 1860s 频率护栏的**免降级钥匙**；mark_logical 授标已补 `_verify_chief_form` 核验（撤标恒放行）；具名保活账本 TTL≤7200s＋审计 | 【实测】本班班内该守护自退 **4 次**、每次咬掉一次提交；三班若续长班，仍须起袋前重注册＋重拉守护（直到保活账本被实际采用为默认口） |

## 四、本班边界与未做（勿替本班补成绩）

未做：C-1 闸门本体（队列/落地车道领地）；Welch 收编（无出处）；torch 降级（花钱/环境类）；
②33 件池面复位（等 10-12 13:5x 窗）；④两枚 initializing 死锁棚（四探针全查无，无对象）；
⑦排班调档（实算证字面不可满足，唯一可行＝错峰且须走 `apply_resource_plan.py` 单口，无代落授权）。
本班全程：未杀停进程（belt_guard 用它自己在册的 `belt_guard.stop` 优雅退出）、未删任何历史审计件、
未动他人在飞域、未新增 gate、未新立裁定号、未放宽任何判据阈值。
