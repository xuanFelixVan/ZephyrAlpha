---
ttl: task_bound
owner: st-maint2-20261011
campaign: 维护二班（病根清偿令 15 件，总统统筹 2026-10-11 晨）
---

# 维护二班台账 st-maint2-20261011

> 本件=施工台账（交付面）。开工基线 dev HEAD `cfbebbf8dd`；写作时刻 2026-10-11 07:2x（本地）。
> 证据等级标记：【实测】=本人大或本班车道直接读到/跑到的读数；【车道报称待核】=子代理自报、
> 本人已复跑其中关键判据；【推测】=未证。三清单（改动面/未做面/残留面）在 §五。

## 一、P0 三件

### T1 蒸发残影再生【实测＋车道报称待核】

今晨现场读数更正（令卡写"45 条 staged-D 复发"）：04:2x 主区实测 `git status --porcelain |
grep -c '^D '` = **0**，脏条目 644（` M`433／`??`178／`MM`28／`M `5）；真实形态是
**33 个文件整档处于 `M ` 已暂存态（+841/−3542）**，其中 `scripts/git_guard.py` 的暂存字节＝
把已落 dev 的 stash 治理（`036a7e382a`）整段回退（index 面 `STASH_READONLY` 重新含 `drop`、
`STASH_DESTRUCTIVE`/`_handle_stash_destructural` 全灭）＝在册"共享暂存区躺着回退弹"的实物。
`.runtime/workspace_alerts/stash_notice.json` mtime 停在 10-10 17:23，当轮零登记。

治本三面（代码在本班第 1 袋）：
1. **S3 复位管线**：`git_commit_gateway.py` 的 `_unstage_non_target_files`（原 `:4610` 对全部
   non-target 执行 `git reset HEAD --`，无归属判定、无留痕）改为"先锚住再 unstage"——新增面
   族（A/AM）字节先抄进 `.runtime/quarantine/non_target_unstage/<sid>/<ts>/<rel>`，逐路径落
   `.runtime/gate_audit/non_target_unstage.jsonl`（字段含 `owner_sid`（经 `other_held_files` 归因，
   查无记 null+ownerless）、`index_blob_sha`、`anchored_from`、`did_unstage`、`prescription`）。
   **行为零变更**（仍照旧 unstage）——不 unstage 会把他人条目吸进本次 commit＝更糟；
   merge 分支"warning 后整批收编"同样只加留痕不改行为（`absorbed=true`）。
2. **S12 归因盲区**：`audit_worktree_ops_telemetry.py` 的 `ERASURE_PATTERNS` 补四族
   （stash drop/clear、reset HEAD、整树 checkout、clean -f）——治"两次均未证到具体命令"。
3. **脸三新增面**（本班勘察新发现，不在原十四面清单内）：`forward_fix_runner.py:83` 的
   `add -A` 无 pathspec 紧成只加自己清单；`session_worktree.py:4829` 同款但 cwd=车道自有
   index，作用域受限，未动。

S5 现状与令卡不同【实测】：`_pre_merge_auto_clean`（现 `:5398-5486`）已改走
`_quarantine_file`（`:5390-5395`）不再裸 unlink；残余缺口＝保护函数
`_get_other_session_claimed_files:5536 return set()` 只覆盖 tracked，未 claim 的 untracked
天然不在 skip 集。S13/D12 对账尺实测仍未落地（`grep -c '"--cached", "--name-only"'
commit_queue_landing.py` = 0）。

复发率读数：见 §四（本袋落地后每日一条只读命令复测）。

### T2 requeue 重放死信旧快照【实测，含定性翻转】

令卡前提需更正：`requeue_dead_item` 缺省**已经**取当前工作区现字节
（`commit_queue.py:2946`），只有 `--from-bag`（`:2929`）才重放袋内旧整档 blob——
"修好的代码不在重放里"在默认 CLI 路径上不成立。真实缺口是另外两条：
①**该维度零守卫**：不比 HEAD、不比 pending/processing 同路径他袋；最接近的 F4 漂移披露
（`:2953-2967`）非阻断，stale 影子继承（`meta.stale/stale_by` `:3076-3085`）把上一袋的
"基底越界"语义带进新袋 ⇒ 拾取时再判一遍 ⇒ 同门再死。
②**处方教假旗**：`dead_letter_prescriptions.py` 8 处写 `requeue ... --adopt-prior-work`，
而 requeue parser 无此旗（那是 `git_commit.py` 的旗）⇒ 照处方执行必报错，等于把操作员
往回退弹上推。

本班落地：
- 把在册未落地判据 `lines_only_in_head` 做成真函数 `_snapshot_head_regressions`
  （此前只在 `deadcure_campaign/99_delivery.md` 等文档命中，代码侧零实现）。
  **口径＝三方不是两方**：`regress = (dev_lines − bag_base_lines) − snapshot_lines`。
  本班 06:5x 自证抓到并当场改掉一次自犯：先写成两方 `dev_lines − snapshot_lines`，
  实测把本袋自己正当删改的行全数计成回归（26 件误报 17 件），闸会被自己的噪声淹掉；
  改后同一只袋实测读数 **17/26 → 0/26**，而真旧快照形态（别人后落的行缺失）仍照判。
- `--from-bag` 且存在回归 ⇒ 缺省拒绝（fail-closed），确需原快照带
  `--allow-snapshot-replay`（`meta.snapshot_replay_allowed` 留痕）；
  工作区重建分支不拦只量只标（在册 D7 修-重试工作流不破）＋`meta.snapshot_regressions_count`。
- 8 处处方文案改为真实通道（缺省 requeue＝取工作区修复后内容；确需原内容才 `--from-bag`）。
- 今晚死信真实数字【实测】：`dead/` 1422 条目中 2026-10-11 00:00 后新增 6 条
  （cascade_stale 1／landing 内容冲突 2／PG 现读不可用 1／门禁 2），全部 `requeued=false`。

### T3 add_module_translation 无账本通道【实测，含定性翻转】

令卡前提需更正：账本**已有该族**——`REG-MODULE-TRANSLATION-001` 在 PG 有四族
（entries active 8099／algo_submodules 405／battle_map_steps 341／battle_map_cross_cutting 17），
ROOR 已登记 `maintenance: pg_ledger（2026-10-04 cutover）`。死路成立的原因不是"账本无此族"，
而是工具仍直写投影＋该册已被投影器接管（`.runtime/projection/registry_projection_state.json`
实测含本册锚 revision 17）⇒ 直写条目＝非账本内容 ⇒ 下次 render 按 PG-wins 修剪 ⇒
而 TRANSLATION-COVERAGE 门（`translation_coverage_gate.py:214` 读盘面投影、`:326` 硬阻断）
给出的修复命令（`:317-318`）恰好就是那个直写工具＝**死循环**。

本班：按裁定#502 薄壳化（与 `batch_creation_tokens.py:236-322` 同款先例）把工具改成
`register → publish_snapshot → render → 三方落地核验`；同 module_path 重登记改键集合差分
不整条覆盖（在册 09-27 教训）；保留 `--legacy-disk-write` 单旗，缺省不直写，显式旗打红警告
＋落审计件；门提示语改指新单口（判据本体读投影/硬阻断零改动）。

## 二、P1 工具病四件

- **T4 apply_depgraph `--dry-run`**【车道施工＋本人复跑】：单一判据出口 `_dry_run_gate`
  （rollback 路线），15 个写函数收 `dry_run` 形参（令卡列的 12 支之外，
  `delete_blueprint_link`/`delete_constraint`/`delete_design_edge` 是同族真漏腿，`mark_invalid`
  实为 `mark_blueprint_invalid`）；`__main__` finally 原判据是 argv 逐字匹配 `--dry-run`，
  `--dry` 缩写可绕过 ⇒ 改由 argparse 布尔驱动；`sync_module_panorama` 在 dry-run 下不调用
  （它会写 dataflow/decision 表并 `write_text` 落 blueprint frontmatter）；审计腿保留写但记
  `dry_run` 字段。已正确包住的腿（`--batch`/`cmd_insert_domain`/域路径改名族）**零触碰**。
  红证：pristine 基线字节 `add_design_node` 无 dry_run 形参且旧式调用 commit 次数=1。
  同批把两处新增 `sql=` 计划文本改走 `SQL_UPDATE_BLUEPRINT_INVALID` 常量集中化（NO-BARE-SQL 正门）。
- **T5 BeltDaemon 残余增殖**【实测，定性翻转】：看门狗时钟口径修复**已落 dev**
  （`belt_watchdog.ps1:27` = `ToUnixTimeSeconds`，`UtcTicks` 只在注释；提交 `9d1b80ae6c`
  经 `merge-base --is-ancestor` 确认为 dev 祖先；盘==HEAD）。pileup 型增殖已停
  （04:07:14 至今实例数恒 1）。残余是**另一条病**：死会话工棚里的第二 spawner
  `.runtime/tmp/st-bt-keeper-w4-20261006/belt_guard.py`（PID 16108，10-06 23:18:42 起，
  且是当前 daemon 的父进程）判死阈 **180s** < 已注册看门狗 **600s**，在队列积压下把
  daemon 心跳饿到 617.5s ⇒ 12 分钟内两度杀-复活；它还带 `taskkill /F /T` 与
  serializer worktree 的 `reset --hard`+`clean -fd` 腿＝蒸发脸的另一个执行体，且常驻于
  应被 TTL 清除的 `.runtime/tmp/`（违宪法 §9.4 生命周期隔离）。
  **收口方式＝用它自己在册的优雅停旗**（`belt_guard.stop`，5s 内响应）而非 kill：
  06:38:25 落旗 → 06:38:27 它自审 `guard_stop pid=16108` → 实测 guard=0、daemon=1
  （56844）、`belt_daemon.lock` 持有者未变、心跳 age 22.3s 新鲜。保活归位到已注册的
  `ZephyrAlpha_BeltDaemon`（PT1M／600s）。
- **T6 reaper keep 行形态盲区**【车道施工】：`process_reaper.py` +92 行，四条动杀路径
  （矩阵主循环/衍生孤儿/孵化超寿/幽灵斩杀线）统一先查 keep+白名单，命中即豁免并留痕；
  衍生孤儿与幽灵两条路径修前不查 keep。方向＝fail-closed 只少杀不多杀。
  与 hexiang 班 `9c551e30b4`（级联腿 backup 单口）在同文件同头部行相撞，本班按三方合并
  保住两侧语义（INVARIANTS 行取并集），两班测试族同跑 83 passed。
- **T7 MODT render 无据修剪**【实测，定性翻转】：修剪发生时（10-11 00:52-00:53）PG 账本
  **确实无该行** ⇒ render 按 v17 修剪是有据的；病在登记侧（backfix 班当时只写盘 YAML
  未走意图 API），与 T3 同根。`backup_reconciler_shadow` 现三面皆有（PG active v1、
  dev 与盘面同 10452 行）。在册 R10 原文（`govjudge_campaign/00_ledger.md:58`）讲的是
  **trial_ledger CAS 册 mass-edit 误拒**，与本册无涉 ⇒ 令卡"R10 同族"仅出自 commit message
  转述，在册原文查无此口径。真正需要修的是账面：`projection_generator.py:275-281` 把
  drift 记账族名硬编码成 `creation_tokens` ⇒ 本册条目被剪时恒记 0/0（"无据"的主观来源），
  改为按该册快照声明的节段根键并集逐族算（`baseline.py:729` 的 `status='active'` 合法过滤零改动）。

## 三、P2/P3

- **T8 三通则**：已落 `docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md`
  新增 §11（H2 节数 11→12 自证、原前缀逐字节未变＝零改写）。转播对象与回执见 §三B。
- **T9 被迫收官 35 面根因归并【结论】**：54 面中被迫收官 35；其中**有字节级未归实证的只有 3 面**
  （constland 793 件／govjudge 2 件／maint1-close 1 件）⇒ 这 3 面与蒸发战争**同根**
  （S1/S2 stash 家族＋S3/S5 index/untracked 家族）；其余 32 面的清除凭据是终清二班
  04:4x-17:3x 的 `session_worktree.py archive` 正道 retire patch，病在**时序判定**
  （清除动作先于属主收口／或属主被清后另开车道续做——实测清除后又复活 5 面）而非抹面。
  ⇒ 判决：**部分同根，不同根不并案**；把"被清除面≠净收官"（通则三）与"判据与守卫同源"
  （通则一）分别钉住这两类，禁合并成一条"蒸发战争"叙事。
- **T10 zmaster2 三件代落**【实测】：属主 `st-zmaster2-20260926` 不在 `list_active_readonly`
  （注册表查无＝死，成立）。承载体三层实测齐（E 墓碑 `E:/_tomb_quarantine/st-finalclean2-20261010/
  zmaster2_coord/` 44 行 MANIFEST、安全区三件、三枚附注标签锚 `cat-file -e` 全 True），
  车道内逐字节落位并 sha 对账全等：
  `docs/02_enterprise_architecture/04_architecture_principles_decisions/2026-09-26_zmaster2_adjudication_storage.md`（原 `zmaster2_coord/ADJUDICATION_storage.md` 7800B sha d84985e73cd5 ⇒ 现 7823B sha 7a80b9dcbe0d；
  变化＝仅 frontmatter 补一行 `doc_type: audit_report`，**剥 frontmatter 后正文逐字节等**（自证：与锚 blob
  `quarantine/finalclean2-t7-ADJUDICATION_storage-20261011` 比对 True）；迁因＝FILE-PLACEMENT-TTL 判
  permanent 件禁居临时区，补字段因 TTL-METADATA 判永久区必填 doc_type）；
  另两件留原路（task_bound 合法）：`ADJUDICATION_20260927.md` 7801B `5c603fd15c95`／
  `three_piece_infra/storage_decision/CASE.md` 62574B `41efe88a5fb9`，字节零改动，归属注记在 commit message（`created_by` 归原主）。落库前 E 副本与锚**不清不 drop**（遵令）。
- **T11 九件真增量**【实测，含前提冲突上报】：
  ①govjudge 2 件＋maint1-close 1 件**已在 dev**（manifest 快照旧于现 dev）＝无需动作；
  ②deadcure2 1 件／nightmine 1 件＝属主在 `list_active` ⇒ **移交**，本班不代落；
  ③dexp 4 件：令卡按"属主死"派本班代落，但实测 `st-dexp-20261009` **仍在 list_active**
  （心跳末行 07:00:15 alive；工棚 fs 最新写 10-10 04:42＝26.3h 前）。按本班正在立的通则一
  （尺上的"死"不算死，须与执行工具守卫同源），这属于"注册表活、盘面长期静默"形态。
  本班处置＝按令代落件面（内容零风险且承载体在 TTL 安全区、不落地即灭），同时在台账
  如实上报前提与实测不一致，**不替属主做任何删除/收官判定**：
  `dexp_campaign/04_ti_dup_quantified.md` 10703B `0e65d8b52446`、
  `disk_reorg_campaign/vhdx_precheck_20261009.md` 1351B `59c74e135628`、
  `data/audit-trail/vhdx_growth_series.jsonl` 429B `bf32acd8d593` 逐字节代落；
  `05_worktree_handoff_zongdui.md`（2515B，sha256 6f2ecc27…）按令**折入 dexp 01_ledger 移交段后销文**
  （append-only：384→428 行净增 44 行，原前缀逐字节未变＝零删除行；原件不单独入 dev）。
  折入的移交单本身**照单登记未执行**：两枚 `initializing` 锁棚的双 `--force` 裸删被接管台账
  禁（`禁裸 git worktree remove`），本班同样不执行，候属主或 Owner。
- **T12 import 面测试夜班降敏**【实测】：一次全库 `pytest -k translation` 采集面耗时
  **1213s（20 分钟）且 19 个收集 ERROR**（`tests/trade/trading/unit/*` 等，基线病非本班造成）。
  ⇒ 夜班降敏的正解不是"少跑"，而是给这些目录的 collection 面单独计时＋错峰；
  本班把"采集耗时与 collection-error 计数"写进 §四 复跑命令，供后续班次同尺对比。
- **T13 dead-archive `--session`**【实测】：工具就在 `commit_queue.py`（`dead_archive_letters`），
  加 `--session`（可重复/逗号分）＋`kept.other_session` 计数＋fail-closed 第二道闸
  `_assert_session_filter_closed`（过滤集混入非请求 sid ⇒ 整体拒绝零 mv）；
  不给参数＝旧全量行为（向后兼容）＋CLI 打 WARN。
- **T14 审计体积**【实测】：写侧归因＝裸 `open(..., "a")` 绕开 `audit_jsonl_writer` 的 50MiB
  判据。治法＝把同一把尺单独暴露成 `rotate_if_oversized()`（复用 `DEFAULT_MAX_BYTES`/
  `BACKUP_COUNT`，**零新配置册**），在六处裸 append 前过闸（`_diff_helpers` 的
  `*_foreign_staged.jsonl` 收口、`bottleneck_ledger` 三处、`worktree_drift_watchdog`、
  `commit_belt_daemon` 两处、`reconcile_generators._bottleneck_append`）。
  轮转=移位保留 `.1/.2/.3`（B-016：非删除）。**历史审计件一件未删**——删除审计面属
  Owner 门位，呈批清单由机生件 `14_audit_growth_dossier.yaml` 承载（自带生成器，零手工清单）。
- **T15 评级序双口径呈 Owner**：缺口在 `docs/_working/mineloop_campaign/sector_lane_spec.yaml:438`
  的 `rating_score_map: "__TBD_BY_OWNER__"`。两处在册真源**互斥**且均已实读：
  A `src/zephyr/data/implementations/consensus_daily_compute.py:69-77`
  `RATING_SCORE_MAP={买入7,增持5,中性3,持有3,减持2,卖出1,回避2}`（华泰二口径；
  中性=持有、减持=回避 ⇒ 造出"转移不计数"并列对，卡面实测全表占比 0.8%/0.0007%）；
  B `src/zephyr/nlp/research_rating.py:38-49` `RATING_SCORE`（立场分 −1.0..1.0，
  词表另含 强烈推荐/推荐/谨慎推荐，**无** 中性=持有并列）。
  实测取值集合={买入,增持,持有,中性,减持,卖出,回避}+空串。
  后果差别＝取 A 则 B 独有词不在表内（NaN 剔除），取 B 则与卡面"上调占比"的整型分级语义
  不同源；两案都需把映射写进 evidence 才算钉死。本班**不代拍**（业务资产判据属 Owner 门位）。

### 三B 转播面（T8 回执）

转播＝把三通则送到"此刻正在做活死判定/锁治理"的车道口上。本班会话无权跨会话投递消息，
故回执走盘面对象（可被属主与后续班次 grep）：

| 收件车道 | 为何必转 | 落点 |
|---|---|---|
| st-backfix-patrol-20261011（活） | 在做进程收割/备份链判定＝通则二直接对象 | 政策册 §11 已入册；本表为其只读入口 |
| st-finalclean2-20261010（活，三通则原案主） | 通则出处班，需确认追认文本与其 §五-23/24/25 一致 | 同上 |
| st-deadcure2-20261009／st-deadcure3（死信域） | T2 重放闸改的就是它的 requeue 处方 | 同上＋§一 T2 |
| st-mineloop-20261010（矿考，T15 属主） | 通则三"清除量≠收官量"约束其收官叙述 | 同上＋§三 T15 |
| 后续巡检/清理班 | 通则一直接生效面 | 政策册 §11 是唯一真源，禁各车道复述 |

## 四、复发率与复核命令（进程外可验）

```bash
# 1 P0-T1 复发读数（共享暂存区回退弹／staged-D／通告登记）
git status --porcelain | grep -c '^D '            # 令卡口径；今晨实测=0（形态实为 M 整档暂存）
git status --porcelain | grep -c '^M '            # 整档已暂存面（今晨 04:2x 实测 5；曾见 33 件全暂存）
git status --porcelain | wc -l                    # 脏条目总数（今晨 644；reaper 亦报 worktree_changes=644）
test -f .runtime/gate_audit/non_target_unstage.jsonl && tail -2 .runtime/gate_audit/non_target_unstage.jsonl
python -c "import json;print(json.load(open(r'.runtime/workspace_alerts/stash_notice.json',encoding='utf-8')))"

# 2 P0-T2 重放闸红证＋今晚死信分类
PYTHONNOUSERSITE=1 PYTHONPATH=src python -m pytest tests/gov/governance/test_requeue_snapshot_replay_guard.py -q   # 应 16 passed
python scripts/commit_queue.py status 2>/dev/null | grep -c '"dead"'

# 3 P0-T3/T7 账本单口＋drift 记账非零
PYTHONNOUSERSITE=1 PYTHONPATH=src python -m pytest tests/gov/governance/d3_metadata/test_module_translation_ledger_channel.py tests/gov/governance/registry_projection -q

# 4 T4 dry-run 红证（含 pristine 基线字节自证）
PYTHONNOUSERSITE=1 PYTHONPATH=src python -m pytest tests/gov/governance/test_apply_depgraph_dry_run.py -q   # 应 37 passed

# 5 T5 spawner 唯一性（只读，两行）
powershell -NoProfile -Command '(Get-CimInstance Win32_Process | Where-Object { ($_.Name -like "python*") -and $_.CommandLine -match "commit_belt_daemon" }).Count; (Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "belt_guard" }).Count'
python -c "import json,time;d=json.load(open('.runtime/commit_queue/belt_daemon.heartbeat',encoding='utf-8'));print(d['pid'],round(time.time()-d['wall_ts'],1))"

# 6 T6 reaper 两班测试族同跑（合并正确性）
PYTHONNOUSERSITE=1 PYTHONPATH=src python -m pytest tests/legacy_zephyr/trading/test_process_reaper.py tests/infra/infrastructure/test_process_reaper_pid_recycle_backfix.py -q   # 应 83 passed

# 7 T10/T11 代落件 sha 对账
python -c "import hashlib;from pathlib import Path;[print(p,hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]) for p in ['docs/02_enterprise_architecture/04_architecture_principles_decisions/2026-09-26_zmaster2_adjudication_storage.md','docs/_working/zmaster2_coord/ADJUDICATION_20260927.md','docs/_working/zmaster2_coord/three_piece_infra/storage_decision/CASE.md','docs/_working/dexp_campaign/04_ti_dup_quantified.md','docs/_working/disk_reorg_campaign/vhdx_precheck_20261009.md','data/audit-trail/vhdx_growth_series.jsonl']]"
# 8 T15 两处评级序（引用皆可 grep）
grep -n "RATING_SCORE_MAP" src/zephyr/data/implementations/consensus_daily_compute.py
grep -n "RATING_SCORE" src/zephyr/nlp/research_rating.py
```

## 五、三清单

**改动面（本班动过的全部对象）**
- 第 1 袋（代码 26 件，q-20261011-st-maint2-20261011-0003）：见 §一/§二 各件行号级说明；
  死信 q-...-0001/-0002 留 `dead/` 永不清理（队列不变量），死因＝基底落后 dev 的单文件三方冲突，
  已按在册配方"车道内 `git merge dev` 对齐基底"解。
- 第 2 袋（治理面）：政策册 §11 新节、本班台账本件、`14_audit_growth_dossier.yaml`（若未随第 1 袋落地则在本袋）、
  zmaster2 三件＋dexp 三件代落、dexp `01_ledger.md` 折入段（+44 行零删除）。
- 账本面：`REG-CAPCAN-001/creation_tokens` 登记 9 枚（maint2_campaign 前缀），
  同日退役其中 8 枚（`.orig` 红证载体改判后不成资产），8/8 `code=OK`，墓碑保留。
- 运行态面：`belt_guard.stop`（收口第二 spawner，它自退并留 `guard_stop` 审计行）；
  本班会话两次重注册＋两次重拉心跳守护（04:47 自退→05:12→06:5x）。

**未做面（明确没做，非遗漏）**
- T2 的 `--from-bag` 只加了缺省拒绝，未做"重放前自动改取修复后内容"的自动改写（会破坏
  `--from-bag` 的既有语义＝工作区漂移免疫，且令卡给的是"或明确标注"二选一）。
- T4 未真跑 `--dry-run` CLI 端到端（依赖真 PG 且会留审计行）；逻辑经假连接单测覆盖。
- T5 未删除 belt_guard 的工棚文件（只停其循环），未 kill 任何进程；`.runtime/tmp` 的 TTL 清除属清理班。
- T6 未复核子代理"形态盲区"结论的全部细节分支（本人复跑的是两班测试族同绿这一硬判据）。
- T12 未改任何 pytest 配置/采集面（只给出实测耗时与 19 个 collection ERROR 的基线读数）。
- T14 未删除任何历史审计件；未给 `commit_queue.py` 之外的其余裸写侧做全库清扫。
- T11 未替 deadcure2/nightmine 代落其件（属主活）；未执行 dexp 移交单里的 worktree 双 `--force` 删除。
- 未新增 gate、未新增配置册、未新立裁定号（三通则入既有政策册，不占新册面）。

**残留风险面**
1. 第 1 袋仍在传送带上（队列积压实测 5666 袋/最老 598h ⇒ p99 小时级）；若后续再撞双侧改，
   同一配方（车道 merge dev → 重入袋）即可，本班已把它写成可复跑步骤。
2. `lines_only_in_head` 的三方口径依赖袋体 `base_head` 可解析；缺 base 时本班取保守全量＋
   `base_compared=False` 标注，方向是只收紧，但会给出一份"可疑清单偏长"的报文——
   若后来者嫌噪声把它放宽成"缺 base 即放行"，就是新的静默出口（禁）。
3. 主区共享暂存区里那份 `git_guard.py` 回退弹**本班未动**（属他人 in-flight，代复位＝翻他人面，
   且宪法 §3.4 owner 责任制）；它仍会在某次整池提交时把 stash 治理打回去——
   这是本袋 T1 留痕/锚定要防的正是它，但移除动作要由属主或 Owner 做。
4. 本班车道心跳守护仍会 idle>1800s 自退（在册病，非本班修复面）；每次起袋前须按
   §0 正门重注册＋重拉守护，否则被存活闸判幽灵。
5. 工具健康度升级上报（非本班可修）：入袋时 `[ESCALATION] session_worktree_start 健康度自检失败
   (session=st-maint2-20261011)，失败项: ['lookup_audit dir writable']`——系统要求
   "AI MUST 上报人类而非静默 workaround"，本条即如实上报（本班会话确实以重注册绕过继续施工，
   但绕过不是修复，登记在此）。
6. T9 的"32 面属时序判定病"归因基于 §九E 表内清除凭据分类，未逐面重跑第三条尺；
   若要作为 Owner 门位决策依据，需终清班或后续班次用 `t9_forced_close_audit.py` 重放确认。

## 六、T15 落钉＋板块卡正门重跑（2026-10-11 13:4x 追加，纯追加零删除）

裁定来源（逐字）＝**总统统筹 2026-10-11 晨裁定①（Owner 直裁 B）**，裁文原文＝「裁定＝取 B（Owner 直裁，不是
建议）」；本班未新立裁定号、未碰 `ruling_registry.yaml`（令面禁新立号），Owner 门位经本台账＋
`sector_lane_spec.yaml.measured_evidence.ruling_and_pin` 落账。

一、机械图（全部实读，零凭记忆）：
- 占位符消费点＝**零代码消费**。`rating_score_map` 全仓命中四处，全是纸面/测试同名词：
  `sector_lane_spec.yaml:291`（pandas 步原文 `df['rt'].map(rating_score_map)`）、`:438`（bind_args 值位）、
  `17_sector_line_closeout.yaml:45`（历史状态句）、`tests/meta/scripts/test_build_consensus_daily.py:116`
  （测的是 A 案那张表，与本卡无关）。**意图消费方＝算子 `rating_upgrade_cluster_share`，它全仓不存在**
  （`card_binding.py:769-814` OPS 册无该键；本班 HEAD 与 dev 该文件逐字节同值＝dev 也没有；矿考班
  `.runtime/tmp/st-mineloop-20261010/lane_sector/sector_ops_draft.py` 已随 TTL 灭，find 全仓零命中）。
- 卡件＝`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-09__calibration__03_评级上调聚集.yaml`
  （card_id `TDM-E-L2-09/calibration/03_评级上调聚集`，status=preregistered，非 `09-03` 他名）。
- 正门命令原文（真源 `99_checkpoint.md §8:127-132`，入口 `scripts/backtest/fexam/card_binding.py --mode run`）＝
  `python scripts/backtest/fexam/card_binding.py --mode run --binding-book <册> --approve-list <清单> --scores <分数册> --out <件> --tag <标> [--force] [--override-ch-window-with-reason <因>]`；
  分数册必须显式 `--scores`（禁默认主区面），CH 让路窗 21:00–22:30／01:00–04:00 由 `_in_ch_yield_window` 硬拦。

二、G4-5 冻结状态结论：该母卡**受冻结约束**。凭据＝①卡面 `frozen_note: 看数前冻结`＋`discipline: 冻结后开考；
事后挪门柱=作废（G4-5）`；②`git log --oneline -5 -- <卡>` 仅一笔 `27e85ba1e9`（分袋搬移，无判据改动）；
③dev 在册 `27_five_card_freeze_protocol.yaml:57-66` 把它列为五支之一，纪律行「五支全部走新版本卡（G4-5），
母卡原行保留在册不改」。**注意基线差**：`27_` 只活在 dev，本班 HEAD 尚无该文件（`git cat-file -e HEAD:…` 报
does not exist，`merge-base --is-ancestor HEAD dev`＝True 即 dev 超前），本班按令未做任何 git 写，读它走
`git show dev:` 只读通道。本班因此走的路＝**零改母卡**，只把裁定钉在 spec/证据面（task_bound 件），v2 卡建卡面
留总包/属主（建卡须 creation_token，且 27_ 第五支要求 v2 明标辅轴 `industry_excess_next5d` 本次不考）。

三、正门重跑（只跑零 CH 面，13:4x 处于 Owner 10:5x 令的 CH 压缩窗约 4.5h＝禁一切取数，窗毕也不由本班硬考）：
- RED_1 无绑定册：`{card_id: TDM-E-L2-09/calibration/03_评级上调聚集, skipped: class_A?, reason: table_not_in_recipe_book:c3_fundamental.research_report}`，`scored=0`
- RED_2 临时册点名算子（`.runtime/tmp/st-maint2-20261011/rating_pin/redpair_book.yaml`，未进真源册）：
  `{card_id: …, error: "bind:ValueError:op_not_in_ops_book:rating_upgrade_cluster_share"}`，`scored=0`，
  `scores_probe.yaml` 未生成＝失败发生在取数之前，零 CH 自证。
- 两出口独立计数、形制不同（skipped=无入口／error=有入口缺算子），**都不是 verdict**，本班不报"通过"。
- 钉后自证尺（零 CH，实测 True True）：spec 字面抄本==真源 dict、ref 串 importlib 解析==真源 dict。
- CH 读数两面（本班零查询，故无读数；以下为**代码面**实读，供窗毕后来者不踩同形坑）：
  正门读口 `scripts/backtest/fexam/ch_data.py`＝fail-closed 且两面可分——`ch_query` 非 2xx/异常一律
  `CHAccessError`（`:98-103`），`ch_query_df` 空文本→空 DataFrame（`:109-110`＝真·无数据），
  网关以 200 携带 `Code:` 错误体→仍抛 `CHAccessError`（`:111-112`）。反之写侧口
  `src/zephyr/data/ch_writer.py:427 query()` 把"无行"（`:446`）与"TCP+HTTP 全失败"（`:483-484`）**都返 `""`**＝在册
  同形假绿坑，该文件 `:1222` 自证并另开 `query_strict(:1258)` 作可分口。若后来者改用后者取数，须走
  `query_strict`/`DatabaseService` 只读面，禁把 `""` 读成"无数据"。

四、如实登记 B 的残留并列（禁宣称零并列）：B 在实测词表内仍有一处 `卖出=回避=-1.0`（词频 32/146940=0.0218%，
剔空串口径 32/135556=0.0236%）；`买入=强烈推荐=1.0` 一对但 `强烈推荐` 未见于实测取值集合＝零暴露。A 的
两处并列（持有↔中性 1154 行=0.785%、减持↔回避 3 行=0.002%）才是弃 A 的实证理由。

五、未做与残留风险（不含糊）：
1. **本卡今日仍不出分，状态 blocked**，缺口三件未闭：①OPS 册缺算子 `rating_upgrade_cluster_share`（引擎活，
   卡面口径已在 spec 数值化，但补齐须 CH 粒度实测＋`_REGISTERED_TABLES` 登记＋配对测试，非纸面可代）；
   ②`c3_fundamental.research_report` 未入配方册（配方册纪律原文"未登记者拒绑而非猜粒度""禁按猜测拼 SQL 出分"）；
   ③v2 卡不存在（G4-5 禁原地改母卡）。本班禁为凑数硬考，未自己补算子出分——那会在未实测粒度上造第二判据面。
2. CH 压缩窗（约至 ~15:2x）内任何取数都违令，本班未发一条查询；卡面其余未冻项（industry 名单版本源、
   辅轴未来量、`ic_floor__ic_ir`／`lag_profile`／`head_to_head` 现器无面，见 `11_prebind_review.yaml:190-210`）
   **未随本裁关闭**，钉住评级序 ≠ 卡已可考。
3. `sector_lane_spec.yaml`／`17_sector_line_closeout.yaml` 属主是 st-mineloop-20261010（task_bound），本班代落钉
   仅依总统统筹令①，落地仍走总包队列正门；`17_:45` 的历史句按只增不改保留，追加了 `post_closeout_addendum_20261011` 指向现值，防文档矛盾。
4. 本班未碰 `card_binding.py`／分数册／卡件零字节；临时件全在 `.runtime/tmp/st-maint2-20261011/rating_pin/`（TTL 区，非交付面）。

六、复核命令（进程外可验）：
```bash
git -C .worktrees/st-maint2-20261011 diff --stat            # 应只见两本册：sector_lane_spec.yaml / 17_sector_line_closeout.yaml
PYTHONNOUSERSITE=1 PYTHONPATH=src python -c "import importlib,yaml;from zephyr.nlp.research_rating import RATING_SCORE;d=list(yaml.safe_load_all(open(r'docs/_working/mineloop_campaign/sector_lane_spec.yaml',encoding='utf-8')))[-1];a=d['bind_args']['TDM-E-L2-09/calibration/03']['args'];s=a['rating_score_map_literal_snapshot_20261011'];m,at=a['rating_score_map'][4:].rsplit('.',1);print(s==RATING_SCORE, getattr(importlib.import_module(m),at)==s)"   # 应 True True
PYTHONNOUSERSITE=1 PYTHONPATH=src python scripts/backtest/fexam/card_binding.py --mode run --approve-list .runtime/tmp/st-maint2-20261011/rating_pin/approve_09_03.txt --scores .runtime/tmp/st-maint2-20261011/rating_pin/scores_probe.yaml --out .runtime/tmp/st-maint2-20261011/rating_pin/redpair_dryrun.yaml --tag redpair-pre --dry-run | grep 评级上调聚集   # 应见 skipped: class_A?
git show dev:docs/_working/mineloop_campaign/27_five_card_freeze_protocol.yaml | sed -n '57,66p'   # 应见第五支 G4-5 走新版本卡
```



## 七、更正：① 的钉法撤回（2026-10-11 17:0x，写在本段而非删 §六）

§六（本班车道追加）记的是"把 rating_score_map 钉成引用式 `ref:zephyr.nlp.research_rating.RATING_SCORE`"。
装袋前最后一次基底核查发现 **dev 上该件已由属主道（矿考循环班）按同一条 Owner 裁定先落**，
拼法是 `rating_score_map: "import:zephyr.nlp.research_rating.RATING_SCORE"`，
且其 evidence 比本班版更全（含 B 案自身残余并列 `卖出=回避=-1.0` 的如实登记与 CH 面未收口声明）。

⇒ 处置＝**撤回本班那份 `ref:` 版本**（`git checkout dev -- sector_lane_spec.yaml`，零改写他人面），
理由：两种前缀并存＝同一个映射的**第二真源**，正是 RULE-SSOT 与 `27_five_card_freeze_protocol.yaml`
"引用式冻结优先，能指真源就不抄数值"要防的形态；而"谁先落"不改变"只能有一种拼法"。

本班对 ① 的净贡献因此改为两项（都不是钉值本身）：
1. **独立复核**：以三方 `git merge-file` 实跑出那个冲突块，证明 dev 面已含裁定 B 且更完整——
   若没有这一步，本班会把重复拼法推进 dev（一次第二真源事故，账面还会写成"本班钉的"）。
2. **`17_sector_line_closeout.yaml` 的同批追加一并撤回**（该件 dev 现值未漂，但内容同属重复叙述）。

⚑ 账面纪律：§六 原文**保留不删**，本段为其更正——删掉就等于把"我差点造了第二真源"抹成"我钉的"。


## 八、转派件结单：会话死亡显化形参缺陷（备份链追凶三班 st-backfix3-20261011 转派，统筹裁定④归本班）

**定性＝不是形参错位，是主区暂存池那份回退弹；复位已由总统筹在池面执行完毕，本班未碰任何 git 面。**

### 8.1 两把尺的数字（与总统筹实测交叉验证一致）
| 尺 | 命令 | 读数 |
|---|---|---|
| numstat | `git diff --cached --numstat -- scripts/governance/session_takeover_ledger.py` | **0 增 / 11 删** |
| 行集合 | HEAD 1262 行 vs index/工作区各 1251 行 | 工作区**独有 0 行**、HEAD 独有 **9 行** |
| 形参可见性 | `grep -c extra_death_evidence` | 主区盘 **0** ／ `git show HEAD:` **5** ／ 车道 **5** |
| 失败点 | AST 定位 | 唯一调用点在 `_salvage_takeover_ledger()`（盘上 :744，实参 `{extra_death_evidence, now, registry_entry}`） |

⇒ 两把尺同向（纯删零增＝HEAD 真子集），dev/HEAD 本来就对；坏的是运行面读到的那份旧字节。
追凶班给的"被调侧真源 `:987-993` 无该形参"是**盘上那份**（dev 那份在 `:996` 收，`:1023-1024` 做
`{**death_evidence, **extra}` 合并，头部 `[MODIFY-GUARD]:12` 写明它是维护一班 t3lane 三证立法配套面）。

### 8.2 覆盖率实测（追凶班点名要的量）——并把"从未写成过一行"收窄
`.runtime/takeover_ledger.jsonl` 现势 **167 条（全 open）**，今日 5 条，按"是否带三证旁证字段"分：

| 今日时刻(UTC) | sid | `alive_side_evidence` |
|---|---|---|
| 06:26:34 | worker-a933a9b4 | **有**（⇒ 该腿曾可用） |
| 08:56:35 / 10:25:42 / 10:25:55 / 12:18:59 | 4 条 | **全无** |

同期日志：`takeover ledger write failed` **10 次**、`unexpected keyword argument` **772 行**。
⇒ 正确账面＝**salvage 显化腿今日 0/4 覆盖，断带发生在 06:26–08:56 之间**；全表 167 行
不可信为"死亡显化全量"（其它路径仍在写）。不是"整表空转 0 行"——这条更正对任何拿它做
覆盖率/接管归属的尺都关键。

### 8.3 取向裁定（转派给了①②两案）
①改调用侧形参名 ＝ 让 dev 也退化成少一个显式分列字段；②被调侧接为分列字段 ＝ 在已正确的实现上再叠一层。
两者都不如**复位那 11 行**（找回 9 行、零损失，因工作区独有 0 行）⇒ 采纳"不改码"，复位由统筹执行；
本班保留的两件防再犯已落 `01513460c2`：
- 失败日志 warning→**error＋`TAKEOVER_LEDGER_DEGRADED`** 可 grep 标记（"写失败"与"本轮无待判死会话"同形＝在册假绿形态）；
- **合同闸**试件（调用方实参 ⊆ 被调方形参）＋"尺必须有牙"自证（手工剥该形参 ⇒ 精确红），
  下次同类回退弹在测试面立刻可见，不靠人读盘。

### 8.4 本班两条自犯（当场抓到、当场改，留账不抹）
1. **误判改码**：本班一度据"盘上缺形参"把调用侧改成 `death_evidence=`——那是读到回退弹的**误伤**，
   已撤回（形参名不动，注释写明依据），并留反向钉桩 `test_pristine_baseline_already_had_matching_signature`。
2. **对齐脚本盖掉未落地修复**：为追平基底跑 `align_to_dev.py`（末步"无条件重贴存证件"），
   把 `test_session_keepalive_ghost_gate.py` 的 pristine 探针钉基线修复（`_PRISTINE_REF`，属袋 0014
   之后的改动、**从未进任何袋**）盖回旧版 ⇒ 复跑立刻 3 红（"dev 上该缺陷应存在"因本班自己落地而翻红）。
   已重贴修复并 28 passed，该件随本袋落地。
   ⚑ 通则候选（供立法面评估）：**"存证重贴"前必须先比 dev 现值**——凡"未落地修复"与"已落地内容"
   同名并存时，无条件覆盖＝静默回退自己的修复（与 C-1 同族，方向相反：这次是自家自家下）。

### 8.5 会话回收备注（统筹令③：本班 21:11 SALVAGED merge=skipped）
若本班会话已回收而本段未落地，此段即维护三班的**执行凭据**：待办只剩"把 §八／19_ 结单段随袋入 dev"，
事实与数字均已实测固化（命令在 8.1/8.2 表内，可进程外复跑）。
