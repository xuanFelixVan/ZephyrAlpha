---
ttl: task_bound
owner: st-maint2-20261011
---

# 九令回执（总统统筹 2026-10-11 13:3x 裁定包 · 本班当班执行）

> 时刻基线：本机 `date` 实测 2026-10-11 13:49:34 +0800（班初 04:13 起跑，非体感钟）。
> 证据等级：【实测】=本人或本班车道直接读到/跑到；【查无对象】=四探针皆空；【未做】=如实点名。

## ① 评级序=B（Owner 直裁）——已钉，卡仍 blocked（未硬考）

- 钉法＝**引用式**（防第二真源）：`docs/_working/mineloop_campaign/sector_lane_spec.yaml:438`
  由 `rating_score_map: "__TBD_BY_OWNER__"` 改为指向 `zephyr.nlp.research_rating.RATING_SCORE`
  （真源 `src/zephyr/nlp/research_rating.py:38-49`，抄录时刻 2026-10-11），同处记裁文与 A 案弃因。
- ⚑ 实测更正一条**机械事实**：`rating_score_map` 全仓**零代码消费**（纸面 4 处：spec `:291/:438`、
  `17_sector_line_closeout.yaml:45`、`tests/meta/scripts/test_build_consensus_daily.py:116` 系 A 案自测）。
  意图消费方＝算子 `rating_upgrade_cluster_share`，而 OPS 册 `scripts/backtest/fexam/card_binding.py:769-814`
  **无此键**（dev 亦无）。⇒ 钉序不会自动让卡出分。
- 该卡 `TDM-E-L2-09__calibration__03_评级上调聚集.yaml` 受 **G4-5 冻结约束**（dev `27_five_card_freeze_protocol.yaml:57-66`
  列第五支"五支全走新版本卡，禁原地改"）⇒ 本班零改母卡，只钉 spec/evidence。
- 红配对拍两出口独立计数（未宣布通过）：`{skipped: table_not_in_recipe_book:c3_fundamental.research_report}`
  ＋ `{error: "op_not_in_ops_book:rating_upgrade_cluster_share"}`，两次 `scored=0`。
- **CH 面更正**：本班车道一度判"此刻在 Owner 10:5x 令 4.5h 取数禁窗内"。我核 `99_checkpoint.md` §15 标题
  与该班 commit 时序后判该令出自 **2026-10-10 10:5x**，窗应已于当日 ~15:2x 结束 ⇒ "窗内禁取数"这一条**前提不成立**；
  但卡仍不出分的真因（缺 OPS 算子＋表未入 `_REGISTERED_TABLES`＋无 v2 卡）与窗无关，故结论不变。
- 待总包/属主：v2 卡（须 token＋明标辅轴 `industry_excess_next5d` 本次不考）＋OPS 算子补册。

## ② 暂存区 33 件回退弹——已发属主移交单

- 移交对象与归属（本班 04:2x 现场实测）：33 个整档 `M ` 已暂存文件，含
  `scripts/git_guard.py` 的暂存字节＝把已落 dev 的 stash 治理（`036a7e382a`）整段打回
  （`STASH_READONLY` 复含 `drop`、`STASH_DESTRUCTIVE`/`_handle_stash_destructive` 灭），
  连带 `tests/gov/governance/audit/test_stash_lifecycle.py` −112 行。
- 处置时序（照裁定②执行）：**先移交，24h 无人认领本班再逐路径复位**。
  认领截止＝**2026-10-12 13:5x**（本件写作时刻 +24h）。
- 复位口径（禁整池，逐路径）：`git restore --staged --worktree --source=dev -- <单路径>`；
  复位前须按在册"池内条目若为其 HEAD 版真子集则告警/拒纳"巡检（即本件候件 C-1）。
- 为何此刻不动手：宪法 §3.4「他会话在途违规不代修：owner 责任制」＋在册教训
  「代投车道在途字节会成回退弹，让它死勿 requeue」。

## ③ 历史审计件 113MB——并入季度打包批（本班零删除）

- 写侧已治（第 1 袋）：六处裸 append 过 `audit_jsonl_writer.rotate_if_oversized` 同一道体积闸，
  移位轮转 `.1/.2/.3` 保留非删除，判据复用 `DEFAULT_MAX_BYTES/BACKUP_COUNT` 零新配置册。
- 存量面按裁定③：**不现在删**，与 C6 第 1 批同窗（复活窗 2026-11-10 满）由 Owner 一次批。
  呈批输入＝`docs/_working/maint2_campaign/14_audit_growth_dossier.yaml`（机生，自带生成器，零手工清单）。

## ④ 两枚 initializing 死锁棚——【查无对象】四探针全空

| 探针 | 命令 | 实测 |
|---|---|---|
| 目录 | `ls -d .aidrafts/st-mx07-W2 .aidrafts/st-tclose-fwire-20261004` | 两者 No such file |
| 登记 | `git worktree list --porcelain \| grep -iE "mx07\|tclose"` | 空 |
| 元数据 | `ls .git/worktrees \| grep -iE "mx07\|tclose"` | 空 |
| 分支 | `git branch -a --list "*mx07-W2*" "*tclose-fwire*"` | 空（`rev-parse session/st-mx07-W2` = fatal） |

`git worktree prune --dry-run --verbose` 亦**零输出** ⇒ 无残元数据可清。
结论：裁定④的"批，走接管正道 rescue tag→resolve→archive"**此刻无对象可执行**；
dexp 移交单在册记载两棚 `HEAD 为 dev 祖先 ∧ 零脏件`（字节可由 dev 重建），故无损失申报。
本班不造动作、不代签"已处置"。若统筹手上另有同名面的现势读数，回一句我即按 archive 正道跑。

## ⑤ 心跳保活正门——已落（且是补一条"已批未落"的裁定）

- ⚑**我先更正自己给 Owner 的转述错误**：班初我把"govjudge R9 已把 exited 短路降级"报给您，那是**读提交信息**得来的。
  本班实读 dev 字节：`scripts/commit_queue.py` 的 `_session_ghost_dead` 区仍是
  `return isinstance(last, dict) and last.get("status") == "exited"`（即 exited 短路**在岗**），
  且函数体 blob 自裁定#459 引入至 dev tip 全等 ⇒ **"账面已裁定、运行码未落地"**。
- 在册裁定核实（我逐条读到，非转述）：`ruling_registry.yaml:4523` 起
  `裁定#507`＝"幽灵存活闸判定面同源化：exited 残留=前代守护死亡证明非会话终审，注册表活性为终审"，
  `approved_paths` 含 `scripts/commit_queue.py`；X-R1-03 护盘那条是 **`裁定#508`**（非撞号，#507 引用成立）。
  ⇒ ⑤ 的实现＝**补 #507 欠的那一半**，不是新立判据。
- 落法（甲＝登记式保活正门）：`heartbeat_daemon.py` 加 `register_heartbeat_keepalive/revoke_/read_active_keepalive`
  （名目<8 字或匿名→ValueError；TTL 缺省 1800s、上限 7200s 硬钳制），idle 支多一条**只在有账本且未过期时**才赦免的腿；
  `commit_queue.py` 侧按 #507 把 exited 短路撤下，结论真源收敛到 `_session_ghost_verdict`，
  三调用点语义零改（`_session_ghost_dead` 变薄壳），出口清册＋逐出口计数经 `ghost_gate_counts()` 可断言。
- 红证：新件 `tests/gov/session/test_session_keepalive_ghost_gate.py` **28 passed**（含反向钉桩 5 条：
  未登记保活／旁证不成立时**仍照旧判死**）；pristine 内容寻址读数：dev 版 `register_heartbeat_keepalive` 命中 0/0，
  dev 原版函数体 exec 后对"exited 残留＋注册表判活"＝**误判死 True**，本班同场 False（赦免）。
- 既有回归：tests/gov/session 307 passed/17 xfailed；belt+takeover+concurrency 126 passed；
  基线红已 A/B 归因（换回 dev 原版字节逐条同败＝车道基线红，非本班造成）。

## ⑥ T12 import 面测试降敏——已落（选甲：按目录分片）

- 实测分母：整库 `--collect-only` **867.4s**（墙 877.1）vs 带 `-k` 全跑 850.6s ⇒ **收集期占全部**，
  执行期落在噪声内。Top 分片：gov 148.5s/3 错、meta 51.4/1、research 39.9/2、ai 29.9/1、**trade 19.5s/10 错**。
- 19 条 collection ERROR 根因分类＝**真断链 19／环境性 0**（其中 `zephyr.orchestrator.lifecycle` ×12，
  模块被搬进 `_archive/`；另 6 条为 map_gate/t0_condition_pack/fexam arm_protocol_binding/两个不存在模块/未注册字段）。
  ⇒ 乙案（环境性隔离）**前提不成立**：若按"环境跳过"处理就是把真断链判绿（在册假绿主形态），故弃。
- 落地：`scripts/governance/generators/generate_collection_shard_manifest.py`（`--emit/--shard N|dir/--list`）
  ＋机生册 `docs/_working/t12_import_sharding/collection_shard_manifest.yaml`（派生自 tests/ 树，非手工）。
- 降敏前后背靠背（同机同态）：整库单窗 877.1s → 最大分片(gov) 119.8s ≈ **7.3× 降**。
- 红证：`tests/gov/governance/generators/test_collection_shard_manifest_redpin.py` **8 passed**，
  含反向钉桩（真断链 tmp 样例仍报红、环境标签永不从红面剥离、未知→real 即 fail-toward-red）。
- ⚑ 更正本班此前报给 Owner 的一条读数口径：`pytest tests/ -k <kw>` **不带 `--continue-on-collection-errors`
  时首错即 Interrupted(rc=2) 中止**，能读出"19 errors/66468 deselected"的全收集面必须带该旗。
- 分片降算(18<19)一条如实入册：跨目录 import 污染型错误仅整库单进程可复现 ⇒ 错峰须**周期补跑整库**作权威计数。

## ⑦ 排班超限——【裁文按字面不可满足】，已登记知会并交回决法

- 真源图：上限常数 `config/resource_profile_registry.yaml:16`（10.0，生成真源
  `generators/generate_resource_profile_registry.py:298`，红线引用 `process_reaper.py:197`）；
  求和消费 `resource_schedule_gate.py:332-338/399-437(:432)`、`runtime_admission.py:142-175,364`。
  09:35 档＝`sch_sim_bridge_execute`（表 `:2132-2141`←真源 `register_sim_bridge_execute_task.ps1:47`）；
  09:40 档＝`sch_decision_chain_sentinel`（表 `:1672-1681`←`:69`）。闸自带实算 **09:35=10.5 / 09:40=11.0**，与裁文一致。
- 两档同池同刻并发属实（`schtasks` 实测），非异池/错开伪影。**但**：除去这两档后的带内基线**恒＝10.0 零余量**，
  把这两档 `peak_mem_gb` 降到 0.1 仍然红，唯一变绿值是 0.0＝编造申报（且 P5 校准器会回写真值）。
  ⇒ 裁定⑦"下调那两条档"**在这张册的口径下无解**；可行动作只有**错峰**（09:35→09:45、09:40→09:50，
  沙箱实测两红清零且 overlap/e0/C-8 三面 block 逐面对拍无新增），而写回须落真源经 `apply_resource_plan.py` 单口
  （表头 `:2-5` 禁人填 `window_expr`）。
- 另两条实测伪影登记：带内 6 枚 `data_slot_*` 同一宿主（实测算 `python -m zephyr.data.scheduler` pid=53372
  WS=**126.2MB**，册内自注"N 倍重复计数宿主"）；而真实占用 11.5975GB 的常驻体 `sch_ollama_serve`
  因 `window_expr=null` **永不入任何求和** ⇒ 名义账与物理账两套数，10.5/11.0 属前者。
- 本班未动别人的档（属主＝`st-sim-launch-20260923`／`decision_map_campaign_20260924`），
  知会件＝`docs/_working/maint2_campaign/16_slot_notice_20261011.md`（锚 `SCHED-NOTICE-20261011-R7`，含原值→新值与一句撤销式）。
- 红证：`tests/infra/infrastructure/test_resource_schedule_mem_ceiling_invariant.py` **11 passed**
  ——旧值臂 10.5/11.0 恰 2 条 block（红），调后臂 max=10.0 零 block（绿）；反空自证（只翻两处期望值⇒恰 2 failed）。

## ⑧ 环境债台账——落点已定，首条入账

- 落点＝`docs/_working/maint2_campaign/18_env_debt_ledger.yaml`；一条债＝一对"在册申报值 vs 本机实测值"，
  条目由件内 `generation_command` 现算（禁手工清单，宪法 §9.5）。
- 首条 ENV-001：`requirements.txt:5-10` 在册裁定 **#ARCH-TORCH-CPU-ONLY**（要求 `2.13.0+cpu`，
  registry 锚 `architecture_issue_registry.yaml:9858-9864`）vs 本机实测 **2.13.0+cu126、cuda.is_available()=True**
  ⇒ **版本号相同而构建后缀相反**，判据必须取后缀（这条正是"存在性判据≠内容判据"的环境版）。
- 净零申报：本件不搬版本常数，真源仍是 requirements.txt 与该裁定；修好或改判时在本件写 `disposition`＋指回真源。

## ⑨ 两枚新候件（登记，本班不自建闸门）

- **C-1｜暂存池"HEAD 真子集回退弹"巡检闸**（矿考班呈来的根因，本班 ② 的现场即是它的实物）：
  现正门合并器只判"袋内字节 vs dev 漂移"，不判"池内旧快照 vs HEAD 的回退方向" ⇒ 他袋此刻提交整池即会把
  我已落 dev 的面打回（`git_guard.py` 那次就是这么进池的）。处方候选＝入队预检对每条 staged 条目做
  **删除行归因**（若该条目字节是其 HEAD 版的真子集 ⇒ 告警/拒纳），落地侧另加三方合并强制。
  归属＝队列/落地车道（`commit_queue*.py` 属其领地）；本班已具备可复用零件：`_snapshot_head_regressions`
  （三方 lines_only_in_head 尺）与本袋 `ghost_gate_counts` 出口计数写法。
- **C-2｜GPU 班互斥组被排班册拦死的关联面**（随⑦解）：**实测未被拦死，但另有其病**——
  `gpu_default` 组 5 枚成员 `window_expr` **全 null**、4 枚 `planned`，`check_overlap_group` 全 horizon 实测
  **0 条 block** ⇒ 该互斥组是**惰性的**：既不锁死别人，也从未真正排产。同时 `heavy` 池 9 枚 active 申报和
  **28.0GB 对上限 10.0**。归属＝排班/资源册车道＋GPU 化班（st-gpux-20261011 此刻在 `list_active`）。
  登记为候件而非本班动作：改这两处属别人在飞域（红线"他会话在飞域"）。

## 本班袋面（本批）

| 袋 | 内容 | 件 |
|---|---|---|
| 第 3 袋 | ⑤ 心跳保活＋#507 补齐（heartbeat_daemon/commit_queue/新试件）＋⑥ 分片生成器/机生册/试件＋⑦ 试件＋知会件 | 代码 3＋测试 3＋机生册 1＋知会 1 |
| 第 4 袋 | ① spec/17_ 钉序＋evidence，⑧ 环境债台账，本回执，台账 §六 更正 | docs 5 |

未做/残留：v2 卡与 OPS 算子未补（①真卡点）；⑦ 写回未做（无代落授权＋裁文字面不可满足）；
④ 无对象；② 复位动作待 24h；⑧ 的 torch 降级未做（属花钱/环境类且撞 GPU 班窗口）；
depgraph 节点登记须总包收官跑 `generate_project_depgraph.py --force`（门拒手动 file-node）。


> ⚑ **①的最终处置更正（17:0x，写在本回执内）**：装袋前基底核查（三方 merge-file）发现
> dev 上 `sector_lane_spec.yaml` **已由属主道矿考班按同一条 Owner 裁定先钉**，拼法为
> `import:zephyr.nlp.research_rating.RATING_SCORE`，且 evidence 更全（含 B 案残余并列
> 卖出=回避=-1.0 的登记与 CH 面未收口声明）。⇒ 本班**撤回**自车的 `ref:` 版本与 17_ 同批追加
> （`git checkout dev --` 两件，零改写他人面）：两种前缀并存＝同一映射的第二真源，
> 正是 RULE-SSOT 与 27_ 工序单"引用式冻结优先"要防的形态。本班对①的净贡献因此＝
> 独立复核并拦下这次重复钉法，而非钉值本身。


## 工单结单段（转派件：会话死亡显化形参缺陷 · 追凶三班 st-backfix3-20261011 → 本班）

- 统筹裁定④转派＋附录 A 一句话裁定：**授权复位那 11 行，且复位已由总统筹在池面执行完毕**
  （动作＝按 HEAD 复位 `scripts/governance/session_takeover_ledger.py` 的 index＋盘面；
  双面旧字节先归档于 `.runtime/tmp/pool_rollbackbomb_20261011/code_drift/`＝可逆存证）。
- 本班随后只读复核：主区盘 `grep -c extra_death_evidence` 由 **0 → 5**（复位生效，salvage 腿恢复）。
- 本班**未再碰任何 git 面**（未 restore/checkout/reset/stash 主区；仅推进私有车道分支 ref 以追平基底）。
- 该台账五件（含 `00_ledger.md`）今晚也曾入回退弹被 staged-D、由总统筹按 HEAD 复位回盘 ⇒
  本班 §八 直接在现字节上续写（append-only，结构自证：H2 节数 7→8、原前缀逐字节未变）。
- 追凶班边界声明与本班边界声明互认：两班均未改 `session_concurrency.py`/`session_takeover_ledger.py`
  由本班落的那两处（error 级显化＋合同闸试件）之外的字节，均未新增判据/阈值，均未杀停进程。
- 工单状态：**结**（根因结论采纳入册；防再犯两件已落 `01513460c2`；复位由统筹完成）。
