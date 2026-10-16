---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
owner: st-maint4-20261013
campaign: 维护四班（接维护三班交接令：落地核验／死信对症重投／①丙／四案卷提案／gate-errcode 窗口令／死信 1+2）
---

# 维护四班施工账 · st-maint4-20261013（2026-10-13 02:08 接令 → 03:0x 自收，本机时间为准）

> 接令＝Owner 转维护三班交接令（理由栏写"维护三班上下文耗尽"）。前任班账＝`docs/_working/maint3_campaign/00_ledger.md` §十一–§十三；
> 四案卷＝`.runtime/tmp/maint3_night/`。**本班最大一条账面纠正见 §二：交接令的三条前提被实测推翻。**

## 〇、工区声明与一处自我更正（先认自己的）

1. 本班按 RULE-WORKTREE 默认隔离施工：`session_worktree.py create st-maint4-20261013 task-maint4-night` →
   `.worktrees/st-maint4-20261013`（分支 `ai/…`，HEAD 取当时 dev 尖 73af6d0404），会话已登记、心跳 daemon pid 24940（30s 一跳）。
2. **自纠一条**：①丙 的三件我先写进了**主区**路径（`src/zephyr/data/ch_writer.py`、`config/flags.yaml`、新测试件），才发现违隔离默认。
   已当场搬迁：三件 cp 进车道并逐件 sha256 记录（`cb453a07cc92`/`e39b99ce1255`/`1c79f3536f38`），主区两件用 `git show dev:<路径>` 覆回 dev 字节、
   新测试件从主区删除；主区 `git status` 对该三路径复测＝空（干净）。**未碰共享 index**（index 本就等于 dev，故只写盘面即可归零）。
3. 冷启动第 1/2/4 步实测留痕：python 3.12.8；`process_reaper --status` source=live、killed=0、reported=3、commit_pct 61.24%、
   worktree_changes=718（>50 阈值，他班并行漂移，本班不代修）；`capability_lookup.find` 已落 2 条审计
   `.runtime/lookup_audit/st-maint4-20261013.jsonl`（第一次入队被 CAPABILITY-LOOKUP-REQUIRED 拦，补反查后重投——门是对的，是我漏步）。

## 一、交接令逐条对账（判据只认实测与 dev 面读回，不信自报）

| 令 | 本班处置 | 证据/读数 |
|---|---|---|
| q-0035 落地核验（wt_fast_forwarded 须带 pid/sid/pre/post） | **前提已失效**：0035 于 02:0x 前判死（dead_reason＝GATE-PRECOMMIT-RUN→gate-rules-integrity exit 2），C10–C12 从未落地 | 实跑 C12 静态判据尺：dev 面 6 项判据全 BAD、`MISSING` 六项齐；另量 `main_workspace_sync.jsonl` 全 7,520 行的动作词表＝skipped_dirty 3,669／index_shadow_clear 3,084／error 477／index_skip_staged_wip 243／skipped_missing 47，**历史零条快进写盘事件** ⇒ C12 的落地判据只能是"读落地面源码键集"，不能等运行事件（存在性≠内容判据）。**注：实现用的键名是 `sid` 不是交接令写的 `session_id`**，同批还带 qid/ts/base_blob/landed_blob/bytes/sid_missing |
| q-0036/0037 盯落 | 0037 **已落地**（①甲 pre-commit 两支钩子注沙箱 env＋测试件改道 rule_bridge，landed_id 71ea74220122…）；0036（台账 §13.5 docs-only）**已死**（非族件双侧皆改真冲突） | `commit_queue.py status --session st-maint3-20261011` 逐袋读态 |
| 0032/0034 对症新袋重投（不 requeue 不 --force） | 先做死因机制定案（§四），再按 blob 逐件验 sha 重投两袋；**随后因"前任其实活着"主动撤袋让路**（§五） | 两袋全部 blob 盘上健在且 sha256 逐件对上袋记；base_blob 与 dev 现值逐件 SAME ⇒ 可整档 verbatim 重投（无需 delta 重放，量过才敢写） |
| ①丙 执行（写口 reader 闸） | **本班完成并入队 q-20261013-st-maint4-20261013-0003**（3 件：ch_writer 判定口＋四写入口接线／flags.yaml 新旗 mode=shadow 出厂／新测试 9 例） | 车道实跑 `PYTHONNOUSERSITE=1 pytest tests/data/data/db/test_ch_write_guard.py tests/legacy_zephyr/data/test_ch_writer.py` → **54 passed**（新 9＋存量 45 回归零破坏）；ruff check 全过、format 已整；测试当场抓出本班一处真缺陷（`_SQL_TARGET_RE` 把 `CREATE DATABASE IF NOT EXISTS c9_meta` 的 target 取成 `IF`，已补 `IF [NOT] EXISTS` 跳过子句＋断言）。**未跑任何连 CH 的动作**（件内 `_NoTransport` 断言 HTTPConnection 零调用；当时处 01:00–04:00 让路窗） |
| 乙 维持与考试班沙箱化并案 | 照办：本班未动"禁模块级写库硬门"任何一面 | — |
| 死信 1+2（env 258 整批定性归档＋三长链 153/128/102 行集差判 superseded） | **令内前提被逐条实测证伪，故未执行任何归档**（§六 J-死信） | 只读普查车道产物 `P6_dead_letter_census.md`＋8 张逐件表：env 桶现算**恰 258 袋**（口径锚在 `scripts/commit_queue.py:3908 classify_dead_reason`）＝死因标签非内容标签，其中 **243 袋仍揣着 dev 没有的 842,867 行**、1 袋整袋是唯一副本 ⇒ 不可整批归档；三链＝153/128/102 逐袋集合关系实测 `strict_superset=0`，全是 **disjoint 批次序列**（86/117/93）⇒ 链级 superseded 不成立 |
| gate-errcode-consistency 窗口令（先独立跑，绿则修路径进关键路径，红则出分诊案卷；禁直接修了就跑） | 照令执行**只跑到"读数级"即停**：结果＝**红** ⇒ 走"出分诊案卷呈统筹"分支，未修任何东西、未把任何测试送进任何关键路径 | 车道在干净 HEAD（73af6d0404）跑 `pytest tests/governance/test_error_code_consistency.py -q --tb=line -p no:asyncio --import-mode=importlib` → 8 collected／**7 passed／1 failed**，三次复跑稳定；唯一红＝`::TestRegistryToCode::test_active_entries_have_live_definition`（stale_entry 4 条，全指 2026-10-04 `f4b2c6029df` data_eng 净删批未改注册表；其中 ZA-DE-0006 的码其实是活的，`sla_breach_predictor.py:65`＝纯路径迁移遗留）。另量到**"关键路径"在仓内查无对应机械结构**（GateSpec 只有 gate_id/check/priority/files_trigger 四字段），最接近的三候选已附证据入 `P5_errcode_window_reading.md` |
| 四案卷逐份出实施提案呈统筹（只出提案不动手） | **四份提案全出**，且每份都做了"案卷论断 vs 当前 dev 面"逐条复核——四份里有三份把前任案卷的结论**改判**了（见 §三） | 产物 `.runtime/tmp/maint4_night/proposals/P1…P7.md` |
| 纪律：开工判活三查／同件多轮并一袋／投前真钩子／既定裁定不变 | 判活三查促成 §五 的让路（否则本班会撞件）；投前真钩子＝三次入队预检各给全违规（COMMIT-SCOPE＋CAPABILITY-LOOKUP 一次、其余通过）；C10–C13 既定裁定内容一字未改（逐件 verbatim 取自前任 blob） | 见 §五、§〇.3 |

## 二、三条账面纠正（交接令本身有错，先纠再干）

1. **"q-0035 落地核验／q-0036 0037 盯落"不成立**：0035、0036 已死（0037 才是落了的那枚）。四裁 C10–C13 在接令时刻**一笔未落**。
2. **"超时乙丙并未生效"这条交接令说对了，但理由要说全**：不只 0032 死了——主区**盘面**已带着乙丙两组改动（thresholds 三档 15/60/30＋`decision_chain_sentinel.commit_queue_landing_pool_workers: 4`），而 dev 面实测＝`git_operations` 无这三键、k 仍为 6。
   即"盘上超前于库"形态：运行面读主区磁盘，所以前任 §13.4 账5 想要的"一夜 k=4 读数"，真实起点是**该袋落地之时**，不是 10-12 夜。
3. **前任会话没死**：`.runtime/sessions/st-maint3-20261011/heartbeat.jsonl` 末拍 age 28.6s、pid 17020、status=alive，且 02:42/02:46/02:46 自开 0038/0039/0040 三袋。
   接令称"上下文耗尽"＝已过期。按宪法 §3.4 与在册纪律"同件只投一袋"，本班执行了 §五 的让路。

## 三、车道并发结构与四案卷改判（6 条只读车道全并行，产物在 tmp）

派法＝只读类 6 路并行＋写盘类本班独走（同文件跨车道禁并发）。回报要点（**均为车道实测，非案卷转录**）：

- **P1 三方冲突合并器**：案卷行号在当前 HEAD 面**零漂移**（漂移发生在工作区/索引面，+64 行 staged）；今夜实际死亡三口径 35/11/4，全池累计 231 枚（松散串 246）；
  处方件 21_ 正文的"甲"已被作者自己两次证伪并作废旧口径，实装判据只在 `.runtime/tmp/st-examrun-20261012/maint3_prescription_patch_v2.diff`（73 行，只动 landing 一文件两 hunk）；
  **本班独立复跑盖章两条**：该 patch 在主区面与"含 C12 的车道面"`git apply --check` 均 exit 0（⇒ 与 q-0001 无排序依赖）。
  政策落差核到行：`merge_conflict_resolution_policy.md:53-79` 的 A 类（叠加型双方都保留）在机生通道**无对应分支**。
- **P2 CH 容量**：案卷把 15:13:11 那次 `MEMORY_LIMIT_EXCEEDED` 归给"面板装载"——**归因错**，实为 `scripts/data/backfill_technical_indicator_dwm.py:117-122` 一条 SQL 取全 215 个 Nullable(Float64) 列的比对基（`system.errors.last_error_time` 与 probe6 同刻读数双证对齐）；
  "24 列一次同查 0.77"是**错算式得到的对量级**（案卷 `8.93M×254B≈2.75 GiB` 实为 2.11 GiB；本班另用 raw 自标定 49.55 B/行得 4.47 GiB／比值 0.63）；
  真瓶颈案卷漏了＝**宽取死在主机侧 TSV 整读传输**（`ch_data.py:101` 把整张 TSV 读成一个 str，24 列一条≈9.38 GiB/份 ≥2 次复制）；
  "0.9×RAM⇒加内存就抬上限"经不起复算（0.9×9.13 GiB=8.22≠观测 7.20，反推基数 8.00 GiB 整⇒像 cgroup/systemd 配额；raw 可证漂移域 6.59–7.20 GiB）⇒ **扩容（Owner 门位）在 V-1/V-2 出数前批准＝可能白花**。
- **P3 schemas 遮蔽断裂**：案卷引的在册先例**裁定号记错**——reconcile_worker 自装仓根 sys.path 的真在册治本是 **#ARCH-104**，案卷写的 #ARCH-264 在册但内容＝授权面收窄/WriteAudit，无关；
  炸面比案卷更大（新增 3 条静默/降级面：`add_module_translation.py` register_asset 步骤②、`create_guard.py:847-872` PG 正证腿在遮蔽环境恒静默失明退投影、`commit_queue_landing.py:2345-2352` 入账本册判定静默 fail-open）；
  "正门脚本形态必断"最小复现已给（`schemas__file__=None`＋`No module named 'schemas.categories'`）。
- **P4 午夜指纹**：**方向反了的最大一条**——案卷"两笔危害（daily 少跑／always_on 重跑）"经跨 00:00 实证不成立（凌晨窗内成功在业务上本就记前一交易日的账，现行 UTC 折日恰好等价）；
  251 支对账任务中 60 支 last_run_at 处折日态、**判据分歧恰 6 支**（block_trade／dragon_tiger×2／kline_us_daily／money_flow／us_index，全 daily 桶）；
  案卷首推修法 F1（:154 改上海日）**今晚就会把这 6 支翻成假"已跑过"**⇒"少跑"事故是修法引入的，不是现状的；已改建议默认＝F5 收盘锚（显式 `ZoneInfo("Asia/Shanghai")`＋daily 判据≥L 日 15:00），对 6 支零翻转且顺带修掉两尺共有的"收盘前假通过"。
- **P5 errcode 窗口令读数**：见 §一 该行。
- **P6 死信普查**：见 §一 该行＋§六。
- **P7（本班自挖，非令内）**：GATE-INTEGRITY 读错面＝今夜全仓落地堵死的真凶，见 §四。

## 四、本班最大发现（一条机制，两支班各自独立量到）

**只要主工作区磁盘带着任何一枚金-hash 受保护件的未提交改动，任何含 `scripts/governance/` 或 `AGENTS.md` 的袋必死。** 三段机制＋逐件对账＋控制组＋"为什么单改 cwd 无效"的实测都在
`.runtime/tmp/maint4_night/proposals/P7_gate_integrity_ownscope_face.md`。要点三条（此处只落结论，证据在件内）：

1. 判据面＝`mode=head`（`config/flags.yaml` 实读），参考面是 HEAD blob，基线库 `rules_integrity_db.json` **已退出判定链** ⇒ 前任"未及时 add+--register 基线库"这条**不能解释** 0032/0034/0035 三连死；
2. `check()` 的工作树面读磁盘，而磁盘根 `REPO_ROOT` **恒等于主仓**（`zephyr.shared.io.paths.find_repo_root` 自述 S4 治本 2026-08-14：pip editable `.pth` 把 `import zephyr` 锚在主仓）⇒ 池工 w0–w3 与序列化器工作树的 thresholds 盘面全＝dev 值 aa4988d4、唯主区≠dev，且**注入在册 env `ZEPHYR_WORKTREE_ROOT` 才改得动向**（实测：不设 root=主仓/changing 5；设之 root=w0/changing 0）；
3. 归因器 `_own_hit` 做子串匹配，把门自己打的 `[CHANGING_IN_COMMIT] <袋内路径>` 信息行当"本文件违规" ⇒ 宪法 §3.1"外来违规只 warn 不拦无辜人"在这一族失效。
   逐件重算的"计数违规枚数"与两支 dead_reason 的 `3 个文件被修改/缺失` **逐笔对上**（0032＝recon/takeover/CAPCAN；0034/0035＝thresholds/gateway/CAPCAN）。

建议默认＝甲-0（注入在册 env，零判据变更）＋次选甲-1（证据面剥离非计数行），**不建议**乙-1（给门加 own-scope 判定＝翻 head-mode docstring 的在册设计意图）。
待随批验的一条＝env 注入点须在池工对齐本袋 base 之后，否则把"袋 vs 落后基线"读成新假红——这条只有落地实测能定，本班不代签。

## 五、与活班 maint3 的撞件处置（含一条手法教训）

- 本班 02:33/02:35 投了 C10+C11+C12（6 件）与 C13+超时乙+超时丙（5 件）两袋；02:5x 判活发现 maint3 已自行重投同件（其 0039 还含测试件 `parents[3]→parents[4]` 修正）。
- **硬理由**：落地链非族件分支只有 `theirs==base／ours==base／否则 raise` 三支 ⇒ 本班袋先落地会让 dev==其袋字节而 base≠dev ⇒ 其 0039 必判"双侧皆改真冲突"死信，且 0039 的唯一增量（测试修正）丢失。
  ⇒ 两袋主动撤入 dead（`dead_reason` 写明让路理由，`dead_letter_family=manual_yield`），内容归原作者。C10–C13 归 maint3。
- **手法教训一条（自纠，写死在册防再犯）**：撤袋第一次只做了 `write tmp → os.replace 进 dead/`，**没删 pending 原件** ⇒ 同一 qid 同时出现在 pending 与 dead（队列会照排落地，等于没撤）。
  补齐＝先逐件比对 dead 副本与 pending 原件的 files/message/base_head 全等，再把原件 cp 到 `.runtime/tmp/maint4_night/withdrawn/` 存证、然后从 pending 删除；复测态＝0001/0002 dead、0003 pending ✓。
- 已把上述全部事实＋两条请求（勿清主区面、0039 base 钉当下 dev 尖）经 `send_message_to_chat_session` 送 maint3 会话（session 3cb98046…，标题"执行三班维护令"，runtimeState ready）。本班未替它签任何判定。

## 六、残余与待裁（交统筹／Owner，本班一律不自决）

1. **J-死信（要统筹或 Owner 定序，令内动作已停）**：env 258 不可整批定性归档（243 袋揣着 dev 没有的 842,867 行）；三链 disjoint ⇒ 链级 superseded 不成立，应改按 **path 级唯一副本面**处置——实测 **748 个 path＝136,375 唯一行，散在 145 枚 qid（P0 24 枚）**；
   时限当下未触发（`blob_gc` 只清 Z 类孤儿，归档袋 blob 转 D 类＝phase2 挂起禁碰），**真正的闸是那个未裁的 phase2**；另 账本 §20.2/§20.5 的 258＝"tests 族可解析件数"与 env 桶 258＝"袋"同数不同集合，需一句定谳。
   归档正门已给到可执行粒度＝`python scripts/commit_queue.py dead-archive --days 7 [--session SID] [--execute]`（默认 dry-run 零写、manifest 反向 mv 可回退），但两条知情提醒：`--session` 是**属主级过滤非 qid 白名单**；其自带 verify 只判 path 在不在 dev HEAD，**比普查判据宽**。
2. **J1–J6（P7 案卷 §七）**：GATE-INTEGRITY 的 env 注入裁定、证据面剥离裁定、乙-1 不建议采、陈旧锚点退役、窗毕复测归属、C12 尽快落地支持。
3. **P1–P4 的修法选择全部未批**（提案只出候选＋代价＋建议默认）；其中 P3 牵 pip 依赖面（卸 `safety_schemas` 被 `safety-3.7.0` 硬锁）、P2 的扩容＝Owner 门位花钱面、P4 的 F5 涉判据面须带裁定号同批。
4. **①丙 翻 enforce 的判据未收**（本班出厂态＝shadow，留痕面 `.runtime/gate_audit/ch_write_guard.jsonl`）：04:00 让路窗毕后应由任一班收一次 shadow 计数，若只命中在册已知触库测试且其写口已 monkeypatch/已移出测试轮，即可翻 enforce（回滚＝flags.yaml 一个 YAML 值）。
5. **本班未做**：主区 5 枚受保护件 WIP 的清理（thresholds 现值 4ba66f1b617b **在队列任何一袋都查无快照＝唯一副本**；CAPCAN 属活班 st-datalane2-20261012 且其 q-…-0006 在队）⇒ 谁清谁毁字节，本班只呈报不动手。
6. **维护三班 §13.5 那段班账（0036 袋内容）仍未落地**：其字节＝dev 现值的严格超集（startswith 实测 True，988 行 vs dev 975 行），但袋已死；归 maint3（其 0040 已带 §13.6 新袋在途），本班不再代投。
7. **本件班账自身的落地状态＝被挡，且本班不自解**（如实标价，防下一班重复踩）。链路四步实测：
   ①CREATE-GUARD 确实覆盖新 .md——`create_guard.py:188` `_OTHER_FORMAT_EXTENSIONS = (".md", ".sh", ".ps1", ".mmd", ".json")`（阶段 2，ARCH-TTL-DOC-001 全 7 格式覆盖）⇒ 本件需 creation_token；
   ②登记正门用**主区脚本**跑时回"前缀为空"——该工具 `_REPO = Path(__file__).resolve().parents[3]`（`batch_creation_tokens.py:75`）＝按**脚本自身位置**算根、既不看 cwd 也不看 `ZEPHYR_WORKTREE_ROOT`，所以从车道里调主区副本永远扫不到车道文件（与 §四 P7 的"zephyr 包被 .pth 锚主仓"是**两种不同机制**，本班先前把它记成同一条，此处更正）；
   ③改用**车道自己的脚本副本**跑 `--dry-run`＝计划登记 1 条、零写入 ✓（`docs/_working/maint4_campaign/00_ledger.md`）；
   ④**实跑当场炸**——`insert_block` → `from zephyr.governance.registry_ledger import api` → `registry_ledger_ddl.py:23 from schemas.categories…` → **`ModuleNotFoundError: No module named 'schemas.categories'`**。
   ⇒ 这就是 **P3 案卷"正门脚本形态必断"的现场第四例**，且它此刻正阻断的是**交付面本身**：任何新跟踪件（.md/.py/.yaml）的 creation_token 登记都进不来。P3 的修法候选（修 1a＝在 `registry_ledger_ddl` 起点自装仓根 sys.path，姿势同 #ARCH-104 在册先例）因此不是"性能议题"而是"治理交付通路是否活着"，请统筹按此升档。
   本班未做的事：不绕 `--skip-preflight`、不手改热册 YAML、不动 CAPCAN（此刻＝活班 st-datalane2-20261012 名下有锁、其 q-…-0006 在队、主区盘面 6bd8bb33a602 在队列四面查无快照＝唯一副本；任何 render 落主区都是"替他班改写热册＋可能毁无备份字节"双风险，且在册政策明写"禁出重打投影袋"）。
   ⇒ 处置＝班账**双抄存住**（车道 `docs/_working/maint4_campaign/00_ledger.md` ＋ `.runtime/tmp/maint4_night/00_ledger.md`），落地动作交统筹：P3 修 1a 批准并落地后，随正常班账袋投（只含本 .md，不含投影件）。**这不是本班能自决的面。**



## 七、复核命令（每条本班都实跑过，期望值＝实测所得）

```
# ① 本班三袋终态（期望：0001/0002＝dead 且 dead_reason 以"主动让路撤袋"开头；0003＝pending）
python -c "import json,subprocess;d=json.loads(subprocess.run(['python','scripts/commit_queue.py','status','--session','st-maint4-20261013'],capture_output=True,text=True,encoding='utf-8').stdout);[print(i['state'],i['qid'][-4:],(i.get('dead_reason') or '')[:16]) for i in d['items'] if i['session_id']=='st-maint4-20261013']"

# ② C12 落地判据（静态面；期望＝MISSING 六项齐＝未落地，落地后应为 []）
python -c "import subprocess;src=subprocess.run(['git','show','dev:scripts/governance/commit_queue_landing.py'],capture_output=True,text=True,encoding='utf-8').stdout;need=['wt_fast_forwarded','\"pid\": os.getpid()','ev[\"sid\"] = item_sid','ev[\"pre_sha256\"]','ev[\"post_sha256\"]','wt_deleted'];print('MISSING',[k for k in need if k not in src])"

# ③ 超时乙丙"盘上超前于库"复算（期望：disk 有三键且 k=4；dev 无三键且 k=6）
python -c "import subprocess,yaml;t=subprocess.run(['git','show','dev:scripts/governance/_shared/thresholds.yaml'],capture_output=True,text=True,encoding='utf-8').stdout;d=yaml.safe_load(t);print('dev 三档',[ (d.get('git_operations') or {}).get(k,'ABSENT') for k in ('gateway_git_read_timeout_seconds','gateway_git_write_timeout_seconds','gateway_git_default_timeout_seconds')],'dev k',(d.get('decision_chain_sentinel') or {}).get('commit_queue_landing_pool_workers'))"

# ④ ①丙 落地判据（见 q-0003 袋内消息，未落地面实跑得 判定口 0 次＋四行 False＝尺有判别力）
```

## 八、收班终态（03:08 自收；Owner 已验收关班，统筹裁定交终版裁定接力班承接）

| 面 | 终态 | 备注 |
|---|---|---|
| 本班袋 | q-0003（①丙，3 件）**pending 在途**；q-0001/0002 **dead＝主动让路**（非门禁判死，dead_reason 全写明） | 撤袋可逆：dead 副本含 files+message+base_head 与原件全等（已逐件比对），pending 原件另存 `.runtime/tmp/maint4_night/withdrawn/*.dup` |
| claim | 本班名下 **0 条**（`lock_files.py list` grep maint4 零命中；`--release-only` 复跑＝NOT FOUND×3＋`RELEASED: 3 files (verified)`＝无主可放的幂等确认） | 收尾序列第 2 步已达 |
| 车道 | `.worktrees/st-maint4-20261013`（分支 `ai/st-maint4-20261013/task-maint4-night`，HEAD＝接令时 dev 尖 73af6d0404）**保留、本班不 archive** | 理由＝q-0003 未落地，且车道内有未跟踪新件（`tests/data/data/db/test_ch_write_guard.py`）＝在册第六态（被整树 transit 抹掉时 git 侧零痕迹）。真要撤车道须先确认三面：队列 blob ＋ `.runtime/tmp/maint4_night/deliverables/` ＋ 车道面 |
| 交付件三抄 | ①丙 三件另抄 `.runtime/tmp/maint4_night/deliverables/`（sha `cb453a07cc92`／`e39b99ce1255`／`f52b7afdf844`，与袋记及车道面逐字同）；本件班账双抄（车道 ＋ `.runtime/tmp/maint4_night/00_ledger.md`，sha `508a753a9c01`） | 七份提案＋8 张逐件表在 `.runtime/tmp/maint4_night/proposals/` |
| 会话协调 | 经 `send_message_to_chat_session` 向 st-maint3（session 3cb98046…）对账 → 它复算后**自作废其先前归因**（其 0041 袋消息原文引 `config/flags.yaml:127` mode=head、明写"DB 已退出判定链"）、自撤 0038/0039 并合并为 0041（11 件，测试件用修正版 `5e361f6dbdf9`） | 0041 与本班 q-0003 文件面零重叠（不含 ch_writer／config/flags.yaml／test_ch_write_guard.py） |
| 心跳与保活 | 车道 heartbeat daemon（pid 24940）随会话收尾自然失效；本班未加 `process_reaper_keep` 长批条目、未建计划任务改动 | 若下一班要复用本车道，先看 `list_active_readonly` 再定 |

主区遗留（**本班未清，也不该由本班清**）：5 枚受保护件带未提交 WIP，其中 `thresholds.yaml` 现值 `4ba66f1b617b` 与 `capability_canonical_file_registry.yaml` 现值 `6bd8bb33a602` 经逐件 sha 扫 `pending/processing/dead/done` 四面**皆查无快照＝唯一副本**；后者属活班 st-datalane2-20261012（锁在其名下、其 q-…-0006 在队）。⇒ 谁清谁毁字节；解堵只走 P7 的 env 注入那条裁定（§四）。

下一班该接手的六件（按"堵别人多少"排序）：

1. **P3 修 1a**（`registry_ledger_ddl.py:23` 起点自装仓根 sys.path，姿势同在册先例 #ARCH-104）——它此刻正堵着**交付通路本身**：本班班账落不了地就是其实证（新 .md 需 creation_token，而登记正门 `batch_creation_tokens.py` 实跑当场 `ModuleNotFoundError: No module named 'schemas.categories'`，见 §六.7）。
2. **P7 甲-0**（落地链调 GATE-PRECOMMIT-RUN 时注入在册 env `ZEPHYR_WORKTREE_ROOT`＝该袋真要落进去的那棵树）＋甲-1（证据面剥离非计数行）并批评估——不点则含 `scripts/governance/` 的袋持续连坐死。
3. **q-0003 落地后**：04:00 让路窗毕收一次 shadow 计数（`.runtime/gate_audit/ch_write_guard.jsonl`），若只命中在册已知触库测试且其写口已 monkeypatch 化或已移出测试轮 ⇒ ①丙 翻 enforce（回滚＝flags.yaml 一个 YAML 值，不动码）。
4. **C12 落地判据**：用 §七② 的静态键集尺，**不要等运行事件**（`main_workspace_sync.jsonl` 全 7,520 行的动作词表里历史零条快进写盘事件）；键名以 `sid` 为准，非交接令写的 `session_id`。
5. **超时丙"一夜观察"的起点**＝maint3 并袋 0041 落地之时，**不是 10-12 夜**（dev 面实测无 gateway 三档、k 仍 6；只有主区盘面带着 k=4＝"盘上超前于库"形态，见 §二.2）。
6. **死信 1+2**：按 P6 的 **path 级唯一副本面**切（748 path／136,375 唯一行，散在 145 枚袋，P0 24 枚）；env 258 整批归档与三链链级 superseded **两个前提均已证伪**（243 袋仍揣着 dev 没有的 842,867 行；三链 `严格超集=0`，全是不相交批次序列）。真正的时限闸是未裁的 `blob_gc` phase2。

