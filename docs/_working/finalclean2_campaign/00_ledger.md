---
ttl: task_bound
completes_when: 波二终扫四面零残留且两轮分诊对账自洽，墓碑打包清单已呈 Owner
gate_selfdoc: GIT-DANGEROUS
---
# 终清二期循环班 · 台账（sid=st-finalclean2-20261010）

> 两波制：波一=立即清死面（本册 §三/§四）；波二=六线收官后终扫（§六 触发器）。
> 本班不收口直到波二完成。adjudicator=st-finalclean2-20261010。
> 四态判据真源=`docs/_working/final4_campaign/99_delivery.md` §七；死信域（提交队列 blobs 与其 dead 子区）一字节不碰。

## 〇、冷启动与在岗证据（11:43-12:2x 实测）

| 序 | 项 | 实测 |
|---|---|---|
| 1 | RULE-ENV | `python --version` = 3.12.8（`C:\Users\fanzi\AppData\Local\Programs\Python\Python312`）；`setup_dev_env.py --check` → usercustomize installed=True |
| 2 | RULE-GUARDIAN | `lock_files.py cleanup` 清 10 枚死锁；`process_reaper --status` source=live（计划任务在岗），scanned=37 whitelist_hits=31；水位 commit_pct=80.24%（故并发按内存收着起） |
| 3 | RULE-WORKTREE | 车道 `.worktrees/st-finalclean2-20261010`（分支 `ai/st-finalclean2-20261010/task-finalclean2-loop`），SessionRegistry 已登记，心跳守护 PID 36528（30s） |
| 4 | RULE-CAPABILITY-LOOKUP | `capability_lookup.find('worktree', session_id=st-finalclean2-20261010)` → 14 命中；审计落 `.runtime/lookup_audit/st-finalclean2-20261010.jsonl`（中文单词查询 0 命中=词表按 ASCII token 匹配，非索引未加载，`list_all`=391 已验） |
| 5 | reaper keep | `data/runtime/process_reaper_keep.txt` 追加式登记本班 sid 一行（写前 claim、写后 release） |

## 一、角色与并发结构（Owner 循环令 §一 + 本令通用四条款）

1. 本班=终清二期总包，自决并发结构：只读扫描并行（本次 3 路取证车道 + 主线程 4 线程扫描器）；写盘/入队串行一次一件；同文件跨车道禁并发（claim 管）。
2. 每车道首件小步校准：本班第一把尺跑完即发现两处读数缺陷（`git -C <孤儿目录>` 回溯主仓产生 1514 条假脏读数；`git status` 回写 worktree 的 index 使"最近写"被自污染成 2.7 分钟），修正后才放量。
3. 一口气执行到底，中途不问 Owner；业务资产判死/花钱/实盘/物理不可逆/出域=登记呈批例外（本班唯一物理删面=墓碑区，呈 Owner 批 C6）。
4. 本班负责协调检验各车道、裁定、端到端收尾。

## 二、判据（两把尺，写死在生成器里，散文不另设第二套）

- **第一把尺**（`scan_dirs.py`）：HEAD 是否 dev 祖先 / ahead / 跟踪脏件 / 未跟踪价值件 / 注册表+心跳+fs 三源活性。
- **第二把尺**（`scan_dev_delta.py`）：车道磁盘字节 vs **dev blob** 逐件 sha256 对拍（含行尾归一口径）。⚠ 只有它能把"车道基线落后 dev 造成的假脏"和"真独有字节"分开——例：某夜矿车道 273 件"脏"中 250 件与 dev 逐字节全等。
- **两大坑**（在册）：本仓 `.gitignore:265` 是 `/*`（根白名单模式）⇒ 必须显式给 value pathspec；孤儿目录无 `.git` 时 `git -C` 会向上回溯主仓 ⇒ 必须先验 toplevel==该目录。
- 四态：①hash==HEAD 铁证才删｜②有增量价值先救后清｜③判死四元联言（本班零件达此级）｜④在飞/存疑零动作记表。默认动作=留。
- 属主判定按 **sid** 而非目录：同一 sid 的 worktree 面与工棚面视为同一属主，避让与处置同批（实测例：治理判据班 sid 同时挂两幅面孔，波一两避让）。

## 三、波一四态表（机生）

<!-- BEGIN GENERATED table_fourstate (mk_ledger.py 机生 2026-10-10T13:10:27，禁手改) -->

扫描面共 **18** 件：态① 0｜态② 0｜态③ 0｜态④ 18

| 面/件 | 态 | 证据（实测） | 动作 | 回滚 |
|---|---|---|---|---|
| .worktrees/st-backfix-20261010 | 态④ | 六线·backfix；fs 写在避让窗内（7.2min≤90min）｜独有件: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml｜未并入 commit 文件: docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml, docs/_working/backfix_campaign/00_ledger.md, docs/_working/backfix_campaign/e1_reading_table_v2.md, docs/_working/disk_reorg_campaign/LEDGER_final.md, scripts/backup/backup_forensic_monitor.ps1, scripts/backup/backup_reconciler_shadow.py | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .worktrees/st-constland-20261010 | 态④ | 非车道目录，读数不适用 | 零动作记表 | n/a |
| .worktrees/st-datalane-20261010 | 态④ | 六线·数据车道；fs 写在避让窗内（1.5min≤90min）｜独有件: scripts/data/backfill_technical_indicator_dwm.py, tests/data/data/data/test_ti_backfill_value_skip_and_shard_windows.py｜未并入 commit 文件: docs/_working/datalane_campaign/00_ledger.md, docs/_working/datalane_campaign/02_t2_squeeze_wad_d7_application.md, docs/_working/datalane_campaign/03_t4_cascade_gate_plan.md, src/zephyr/data/implementations/internal_compute_provider.py, tests/legacy_zephyr/data/test_internal_compute_provider.py | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .worktrees/st-finalclean2-20261010 | 态④ | 本班自家车道（收尾按会话收尾序处置，不自清）；活性实测=alive（REGISTRY-FRESH）；fs 写在避让窗内（24.3min≤90min）｜独有件: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml, docs/_working/finalclean2_campaign/00_ledger.md | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .worktrees/st-govjudge-20261010 | 态④ | 属主 2 小时前仍在 dev 落 commit（1d5c0d36c4 govjudge R9），且其台账自陈本班心跳守护 idle 自退被 TAKEOVER 闸判死挡提交＝事故形状复刻；liveness=ghost 只证守护死，不证会话死 ⇒ 存疑留，波二复测｜独有件: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml, docs/_working/govjudge_campaign/00_ledger.md | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/.carry_list.json | 态④ | src/scripts 全量 grep 零消费者，但无重启条件证明未完成 → 态④记表 | 零动作记表 | 内容由 archive 标签/retire patch 可重建 |
| .aidrafts/st-constland-20261010 | 态④ | 六线·宪法班；活性实测=degraded（RATE-GUARD-DOWNGRADED）；fs 写在避让窗内（23.9min≤90min）｜独有件: AGENTS.md, config/search_space_prereg.yaml, docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml, scripts/tasks/run/run_f06_grid.ps1 | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-deadcure2-20261009 | 态④ | 六线·死信（且 blobs/dead 为其领地）；活性实测=alive（REGISTRY-FRESH）｜独有件: docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml, docs/_working/deadcure_campaign2/01_phase0_ledger.md | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-dexp-20261009 | 态④ | 活性实测=alive（REGISTRY-FRESH）｜独有件: data/audit-trail/vhdx_growth_series.jsonl, docs/_working/dexp_campaign/04_ti_dup_quantified.md, docs/_working/dexp_campaign/05_worktree_handoff_zongdui.md, docs/_working/disk_reorg_campaign/vhdx_precheck_20261009.md | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-final4-20261010 | 态④ | 活性实测=alive（REGISTRY-FRESH） | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-finalclean2-20261010 | 态④ | 本班自家车道（收尾按会话收尾序处置，不自清）；活性实测=alive（REGISTRY-FRESH）；fs 写在避让窗内（31.5min≤90min） | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-fullflow2-20261008 | 态④ | 活性实测=alive（REGISTRY-FRESH） | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-govjudge-20261010 | 态④ | 属主 2 小时前仍在 dev 落 commit（1d5c0d36c4 govjudge R9），且其台账自陈本班心跳守护 idle 自退被 TAKEOVER 闸判死挡提交＝事故形状复刻；liveness=ghost 只证守护死，不证会话死 ⇒ 存疑留，波二复测 | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-libfront-20261010 | 态④ | fs 写在避让窗内（46.0min≤90min） | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-nightmine-20261010 | 态④ | 六线·夜矿续战；活性实测=alive（REGISTRY-FRESH）｜独有件: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml, docs/03_modules/_domain_backtest/exam_cards/portfolio_flow/C2/TDM-F-C2-02__shadow__02_约束栈有vs无.yaml, docs/_working/nightmine_campaign/99_checkpoint.md, docs/_working/nightmine_campaign/L8b_ledger.md, scripts/governance/meta_question/wo_a2legs/build_news_sentiment_window.py | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-nightmine-20261010b | 态④ | 六线·夜矿续战 B；活性实测=alive（REGISTRY-FRESH）｜独有件: docs/_working/nightmine_campaign/99_checkpoint.md, docs/_working/nightmine_campaign/L8b_ledger.md | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-nightmine2-20261010 | 态④ | 六线·夜矿续战 2；fs 写在避让窗内（46.0min≤90min） | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |
| .aidrafts/st-regsolo-20261010 | 态④ | 指令卡点名：宪法正本载体，禁删｜独有件: docs/_working/regsolo_campaign/99_delivery.md, docs/_working/regsolo_campaign/lanes/t1_direct_write_callgraph.md, docs/_working/regsolo_campaign/lanes/t2_belt_materialization.md, docs/_working/regsolo_campaign/lanes/t3_hot_registry_inventory.md, docs/_working/regsolo_campaign/lanes/t4_ledger_debt_incidents.md | 零动作（波二复测） | archive/* 标签 + .runtime/quarantine/<sid>-retire-*.patch + .runtime/tmp/rescue/<sid>/（三重存证，30 天复活窗） |

<!-- END GENERATED table_fourstate -->

## 四、处置流水（逐件，追加式）

| 时刻 | 件 | 态 | 动作与实测回执 | 磁盘回收 |
|---|---|---|---|---|
| 12:34 | 主区投影册（capability_canonical_file_registry.yaml） | 设施事故 | 本班 token 条目命中数 **4→0**（size 4077285→4075167，mtime 12:34:14）＝外来快照压回旧基座；12:5x 又自复（命中回 4）。随批上报册主车道，本班未手工挪动该册任何一行 | 0 |
| 12:5x | 本班台账袋（首投） | 呈批件 | **未落地（挂账非失败）**：CREATE-GUARD 判"无 creation_token"，而 token 实测已在 PG 账本（意图 API register→publish→render 回执 OK）。三态对照定位＝门禁吃投影册的 **index/dev 面**（实测 index=0 命中／dev=0 命中＝本班条目不在，主区盘面=4 命中）。⇒ 已登记 token 在门禁眼里不存在，除非 dev 里先有该条目。正道=册主车道 `reconcile`+`registry_projection_generator --render` 净增袋；Owner 10-10 已裁**禁出"重打投影袋"**（那 1600+ 行是他人登记，混进本班 commit＝归属篡改）⇒ 本班不自造、不改判据、不用 --skip-preflight。台账内容已落主区盘面可核 | 0 |
| 12:40-12:50 | 波一·态① 六车道 | 态① | `session_worktree.py archive --execute` 全成：st-fflow-c2／st-fflow-c3／st-docs-e13（needs_rescue→patch 三分类 substantive=1）／st-examchief／st-fwin-exec／verify_v1；每笔④prune 核实=注册表消失，⑤branch -d 壳分支已删 | ~1.8GB |
| 12:41 | 波一·四孤儿面 | 态① | 空目录 `st-chiefzc-verify-20260928`／`st-cure-p03-20261006`（find 计数=0，safe_rmtree 后 exists=False）；断链 JUNCTION `st-mastertc-l8`（目标 .aidrafts/st-mastertc-l8 已不存在，其脏件 10-07 已存证 retire patch）；孤儿 235MB `st-menu-t1b6-20260930`（18827 价值件 hash-object 对拍 dev+两枚 archive 标签：18824 全等／0 差异／3 派生件） | ~2.7GB |
| 12:42-12:49 | 波一·态② 十五车道 | 态② | 同正道逐件归档：bcure-wt／bt-fast-w5／chief7z／cure-p0／fc-landing／fc-spm／fc-tdm／poscap-fix／tdm-chief／vm12w／govfix-g6／mastertc-mine／entrance-gate／gomap-b-04／gomap-b-06（每件①retire patch 落 `.runtime/quarantine/<sid>-retire-*.patch`，三分类 substantive 1~16；未并入 commit 者 ⑤禁 -D 落 `.runtime/quarantine/ahead_branches.log`：entrance-gate/gomap-b-06/mastertc-mine 三支留全量历史） | ~2.4GB |
| 12:44-12:49 | OPS-GUARD 撞闸四件 | 呈批件→已对症 | 工具 ② 步 in-process 搬未跟踪案卷被保护区闸拦（`vm12w/docs/_working/vmap12_intake`、`entrance-gate/.zcode`、`gomap-b-04\|06/docs/_working/fullcirculation_campaign*`）。对症=改 `--skip-rescue` 腿（字节仍由 ① patch 全量含未跟踪全文保全），12:48 在 vm12w 单件验真后再放量，四件全归档。**未放宽任何闸、未手删保护区任何文件** | — |
| 12:53 | 波一·残支清扫 | 态①/态④ 分流 | 217 枚 session/*+ai/* 逐支先验 dev 祖先性再 `git branch -d`（-D 全程未用，git 自拒未并入=第二道闸）：**删 177／留 27（真未并入）／留 13（在用 worktree 占用，git 拒删=正确）**；逐支 sha 存证=`.runtime/quarantine/finalclean2_branch_sweep_20261010T125335Z.jsonl`（回滚 `git branch <name> <sha>`，另有 90 天 reflog） | 0（引用面） |
| 12:36 | 本班自造面 | 态④ | 本班 11:44 用 CLI 开班后又于 12:26 用 API 复核注册，**多出一枚 `.aidrafts/st-finalclean2-20261010` 车道**（其分支被自身占用故 archive 正道自拒）。如实记表，按 §2.9 会话收尾序（abort 自清）处置，不自裸删 | — |
| 13:0x | 治理判据班两面（worktree+工棚） | 态④ 存疑留 | 复扫读数=独有字节 2 件／零独有，liveness=ghost 且 fs 写 133/151min>90 ⇒ 数值上够态①/②，但属主 2 小时前仍在 dev 落 commit（`1d5c0d36c4` govjudge R9），其台账自陈"本班心跳守护 idle 自退被 TAKEOVER 闸判死挡提交＝事故形状复刻"。本仓在册教训=**心跳停更只证守护死，不证会话死** ⇒ 判"存疑"回态④，零动作，波二复测（判据已写死进 mk_ledger.py 的 SUSPECT 面，非临时口头） | 0 |
| 13:05-13:08 | **本班台账文件被整树操作抹掉一次** | 设施事故（已复原） | 主区 `docs/_working/finalclean2_campaign/00_ledger.md` 于 12:31 后某刻至 13:08 间**从盘面消失**（目录也没了；该件全程 untracked，故 git 侧零痕迹：`git diff --cached`/`git stash list` 皆 0 命中）。唯一存活处=**本班车道 12:31 快照**（`cp -f` 那次入袋预投留下的 25199 字节），已 `cp -f` 回主区并二次存证到 `.runtime/quarantine/finalclean2_safety/00_ledger.1315.md`。归因线索：同窗在册的 transit 链（`git stash list` 现 4 枚，其中 `stash@{0} st-constland-20261010-T2-merge-transit`、`stash@{2} -T1-full-transit`、`stash@{3} -T1-merge-transit-isolation`，另有 `stash@{1} quarantine-st-regsolo-20261010-by-st-constland-20261010`）与 12:34-12:36 的 reset+merge 窗（T3 案卷 §13 实证 795 条在飞面被同一手法吞进 stash@{0}）。**未把该归因写成结论**——未证到具体命令，只报窗口与存活面。以后每班在车道留快照、主区件即时二次存证，是这类"未跟踪件无第四态"事故的唯一起效防护 | 0 |
| 13:07 | 循环巡检已挂 | 机制 | 本地自动化任务 `009d328a-ff16-489c-80a5-f28cb4c678e5`（每 3600s，merged 会话，权限档=Auto Approval 非 Full Access，workspace=D:\ZephyrAlpha）：每轮复扫四态+六线三源收官判定+台账追加，判得六线全收官即自动进波二 T6/T8 并出 T7"墓碑面现状"，波二终报落册后自行 remove | — |

**波一磁盘回收实测**：可用 48,038,154,240 → 54,240,026,624 字节＝**回收 6.20 GB**（`df --output=avail -B1 /d` 前后对拍；`.worktrees` 24→5 目录 1.4G，`.aidrafts` 15→12 目录 4.0G）。

## 五、移交与呈批面（本班不自签、不代裁）

0. **待册主车道/总统筹处置一条**：新资产（.md/.py/.yaml）在"token 已进 PG 账本而投影未净增到 dev"期间，凡走提交正门必死 CREATE-GUARD。本班三态证据见 §四 前两行。
1. **T3 移交（13 条 staged-deletion，属主皆活⇒按令不复位）**：取证面=`.runtime/tmp/st-finalclean2-20261010/t3_casefile/index_residue.md`（382 行 13 节，全程只读）。属主=st-deadcure2-20261009（6 条 tests/ai_layer/redline+compliance+meta）与 st-regsolo-20261010（7 条 commit_gates/queue/roor 测试面）。两属主皆"**fs 活**"：deadcure2 注册表 `alive`+心跳 0 分（工棚静默 359 分）；regsolo 注册表 `ghost` 而工棚 fs 写 **32 分** ⇒ 皆不满足"属主死"前置，本班只逐路径登记移交并附复位口径（`git restore --staged --worktree --source=dev -- <单路径>`，禁整池）：D 族"磁盘也偏离 dev"实测 **0 条**（10/13 盘↔dev raw 逐位等，3/13 盘上无副本而 dev 持全字节且属主工棚有同尺寸副本）⇒ 复位对属主是零字节损失动作。
2. **T3 一条卡面前提被证伪**：`architecture_issue`／`commit_queue` 两族在 index 面**无残影**（前者盘面不存在且 status 命中 0；后者 `scripts/commit_queue.py` 干净；`.runtime/commit_queue*` 被 `.gitignore:265 /*` 整棵排除，不可能成 index 残影）⇒ 与宪法班 T5 **零防撞点**。另纠一条卡面口径：主区检出分支就是 dev（`git symbolic-ref HEAD`=refs/heads/dev，三次实测 HEAD==dev），真实形态是 **index 落后于 HEAD**，不是"HEAD 落后 dev"。
3. **⚑上报（在飞重大单点）**：12:34:13 st-constland-20261010 打 `stash@{0} T2-merge-transit`→12:34:15 reset→12:36:06 merge，其间全池脏条目只剩 160 条 `??`，**795 条在飞面（786 `A `+7 `AM`+1 `AD`+1 R 新路径）既不在 HEAD 也不在盘上，只活在 `stash@{0}` 这一个 ref**；AM7 的独有增量已双证 blob size 与盘 size 全等（未蒸发但单点押注）。取回口径=`git checkout stash@{0} -- <path>`，**禁整包 pop**。治理缺口：`.runtime/workspace_alerts/stash_notice.json` 复测仍是 2026-09-30 旧条目，对吞掉 795 条的动作**零登记**（违宪法 §2 第 8 条告警预期）。另：13 条 D 是该链条的**周期性输出物**（9 分钟内复现一次，集合逐字相同），复位令与清 stash 令相撞会真造不可逆损失。
4. **T4 副产品批（零删动作=判据未满足，非偷懒）**：`rescue/*` 标签 22 枚逐枚验毕——**无一枚满 30 天复活窗**（最老 6.4 天，窗满日 2026-11-03~11-09），且其中 **10 枚是未并入字节的唯一持有者**（6 枚被在册裁定登记为回滚载体、3 枚被 HANDOFF 点名待 cherry-pick、1 枚属主在接管台账仍 open）⇒ 令卡"对应 worktree 已处置∧复活窗过→删"这一前置对 22/22 全部不成立，本班一枚未删。案卷=`.runtime/tmp/st-finalclean2-20261010/t4_casefile/byproducts.md`。
5. **⚑呈批（体积增长曲线，清=打包呈批面，本班未删一件）**：`.runtime/gate_audit/` 387 件 **1.22 GiB**（7 日实测 325,417 条/880.7 MB ⇒ 30 日外推 ≈3.77 GB）；`.runtime/audit/` 26 件 448 MiB，其中 **5 个文件破 50 MiB 轮转阈值（351 MB＝占该库 26.8%）而 `audit_jsonl_writer.py:59` 的 50 MiB 轮转未被这些写侧套用**；`.runtime/reconcile_reports/` 814 件 2.9 MB（≈74 件/日）；`logs/backup_report_*.json` 256 件 2.39 MiB（10.1 件/日，0 字节破损件=0）。
6. **⚑卡面前提证伪（影响波二 T7 可执行性）**：`E:\_tomb_quarantine` **不存在**（E: 盘可达，实测 NOT_FOUND）⇒ "判死先入墓碑区＋30 天复活窗"这条路径**当前没有物理载体**，§二 红线"只写不删"落不了地，波二 T7 因此**无源可清**。请 Owner/总统筹定：新建该载体（含备份策略）或改指另一处，本班不自造第六个墓碑落点。
7. regsolo 棚（宪法正本载体，禁删）实测有 5 件内容不在 dev（`docs/_working/regsolo_campaign/99_delivery.md` 等）——本班只记不删；且现测 `stash@{1}` 名头为 `quarantine-st-regsolo-20261010-by-st-constland-20261010`＝**他班已把该会话工作面 quarantine 一次**，本班未动该 stash，待属主/总统筹认领。
8. **本班台账落地面待处置**：本班全部账面动作现在只能活在盘面+车道快照两处（见 §四 末三行）；CREATE-GUARD 那条（§五-0）不通，本班台账就进不了 dev。请总统筹把"净增 token 投影袋"当班跑一次，或指定另一条正门。
9. 波二呈批：墓碑打包清单（逐件内容+sha+回滚命令+复活窗状态+引用计数）→ 请 Owner 批物理删（C6 首个季度窗）；因 §五-6 载体缺位暂缓，改呈"墓碑面现状"。
10. 死信域零触碰申报：本班全程未读未写提交队列 blobs 区（取证车道同样禁入，归属判定改走 dev commit 尾标）。
11. worktree 注册失配补记：`git worktree prune --dry-run` 零输出 ≠ 无失配——`.aidrafts_pool/pool-20260919202729-c433` 处于 `locked` 而目录已灭（git 静默放过），本班未动锁（删锁属队列/池领地）。

## 六、波二触发器（六线全收官）监测

| 线 | sid | 13:1x 现测（三源：注册表分片 mtime / 车道-工棚独有字节 / dev 尾标） | 收官判定 |
|---|---|---|---|
| 宪法班 | st-constland-20261010 | 注册表分片 13:10 新写；`.worktrees`+`.aidrafts` 双面孔，工棚独有字节 4 件；13:0x 前它刚做过 transit（§五-3）并 quarantine 了 regsolo（§五-7） | **未收官（在飞）** |
| 二号收口 | 最可能＝st-examclose-20261010 | 无车道无工棚；11:46 有能力反查审计；其 `docs/_working/examcard_campaign/99_delivery.md` 已落 dev（2h 内） | **疑已收官，名册待 Owner/总筹认**（本班不自裁） |
| 夜矿续战 | st-nightmine-20261010 / -10b / nightmine2 | 三棚注册表 13:10/13:10/13:00 新写；主棚独有字节 273+4 件、10b 未并入 commit 34 枚；nightmine2 近 3h 落 5+1 枚 dev commit | **未收官（在飞）** |
| 死信三期 | st-deadcure2-20261009 | 注册表 13:10 新写；工棚 ahead=2、独有 2 件；领地含 blobs/dead（本班红线） | **未收官（在飞）** |
| backfix | st-backfix-20261010 | 注册表 13:02 新写；车道 ahead=1／独有 1 件（7 件未并入文件）；fs 写在分内 | **未收官（在飞）** |
| 数据车道 | st-datalane-20261010 | 注册表 12:57 新写；车道 ahead=2／独有 2 件（5 件未并入文件） | **未收官（在飞）** |
| （另三张面孔，非六线） | st-final4 / st-fullflow2 / st-dexp / st-libfront / st-govjudge / st-regsolo | 注册表皆 13:10-12:50 新写；govjudge=存疑留（§四 末三行）；regsolo 被 quarantine 于 `stash@{1}` | **一律避让** |

附注（名册口径）：本班未拿到"六线"的正式 sid 名册，上表按三源实测逐一映射并把**无法证实的映射如实标为疑**；执行面按保守律="**凡注册表活性或有 fs 写者一律避让**"，故波二触发条件目前**未满足**（六线中 5 条在飞）。巡检轮（§四 末行）每轮复测此表。

## 七、自洽对账（机生，波二两轮同型）

<!-- BEGIN GENERATED selfcheck (mk_ledger.py 机生) -->

- 波一开局面：**41** 件（态①10/态②15/态④16），快照=`scan/decisions_wave1_open.json`
- 波一终扫面：**18** 件（态①0/态②0/态④18）
- 本班已处置并从盘面消失：**25** 件
- 复扫期间新再生面（他班新开车道，非本班动作）：**2** 件
- 对账式：消失 25 + 现存 18 = 43（开局面 41 + 新再生 2 = 43） ⇒ **平**

| 本班已处置（消失面） | 新再生面（避让中） |
|---|---|
| .aidrafts/st-examchief-20261009 | .aidrafts/st-finalclean2-20261010 |
| .aidrafts/st-fwin-exec-20261009 | .worktrees/st-constland-20261010 |
| .aidrafts/st-govfix-g6-20261007 |  |
| .aidrafts/st-mastertc-mine |  |
| .aidrafts/verify_v1 |  |
| .worktrees/st-bcure-wt |  |
| .worktrees/st-bt-fast-w5-20261006 |  |
| .worktrees/st-chief7z-20261009 |  |
| .worktrees/st-chiefzc-verify-20260928 |  |
| .worktrees/st-cure-p0-20261006 |  |
| .worktrees/st-cure-p03-20261006 |  |
| .worktrees/st-docs-e13-20261009 |  |
| .worktrees/st-entrance-gate-20261007 |  |
| .worktrees/st-fc-landing-20261008 |  |
| .worktrees/st-fc-spm-20261008 |  |
| .worktrees/st-fc-tdm-20261008 |  |
| .worktrees/st-fflow-c2-20261008 |  |
| .worktrees/st-fflow-c3-20261008 |  |
| .worktrees/st-gomap-b-20261004 |  |
| .worktrees/st-gomap-b-20261006 |  |
| .worktrees/st-mastertc-l8 |  |
| .worktrees/st-menu-t1b6-20260930 |  |
| .worktrees/st-poscap-fix-20261008 |  |
| .worktrees/st-tdm-chief-20261004 |  |
| .worktrees/st-vm12w-20261004 |  |

<!-- END GENERATED selfcheck -->

## 八、复核命令（整段可复制，只读）

```bash
cd /d/ZephyrAlpha
python .runtime/tmp/st-finalclean2-20261010/tools/scan_dirs.py --out .runtime/tmp/st-finalclean2-20261010/scan/dirs_v3.json
python .runtime/tmp/st-finalclean2-20261010/tools/scan_dev_delta.py .runtime/tmp/st-finalclean2-20261010/scan/dirs_v3.json
python .runtime/tmp/st-finalclean2-20261010/tools/mk_ledger.py
git worktree list | wc -l            # 处置前后对拍
df -h /d                            # 磁盘回收量前后对拍
git tag -l 'rescue/*' | wc -l
```
