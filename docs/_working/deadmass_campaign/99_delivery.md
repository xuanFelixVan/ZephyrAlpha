---
ttl: task_bound
completes_when: 段二两腿在 dev 面复验落地＋C/D 放量袋落窗清账＋B 面 requeue 有账＋交接卡交接完毕
---
# 死信放量战役·收班册 99_delivery（sid=st-deadmass-20261013，2026-10-13 22:4x → 10-14 跨零点）

令据＝Owner 2026-10-13 统筹令「死信放量班开场」四条并发权限＋23:0x 追加令（段二两条腿落码／blob_gc phase2 存量即清）；
接手处＝前任 `docs/_working/deadclean_campaign/99_delivery.md` §四四条交接卡。
全过程账＝本目录 `00_ledger.md`（§一基线／§二卡①／§三自犯与发现／§四待办／§五两腿落地／§六附属面／§七 blob 与放量窗）。

## 一、终态（只认 dev 面与进程外读回）

| 项 | 终态 | 凭据 |
|---|---|---|
| 交接卡①（前任车道＋会话壳退场） | **完成**，序＝停守护→证 1 自然过期（registry 分片被收割、三件 claim 随之释放）→`archive --execute` | retire patch `.runtime/quarantine/st-deadclean-20261013-retire-20261013T145910Z.patch`（substantive=13）；worktree/分支/壳/pid 文件四处读回全空 |
| 拆壳器首次自清实测 | **两支都真跑到**：保留支（keepalive 审计未删）＋删除支（promote 入墓园后 `_prune_session_shell`→True） | 前任保活审计=墓园 INDEX 第 16 行（sha256 050fa9cc…／rollback／expires 2026-11-12） |
| 段二腿①当日四态分诊自动触发 | **已落码＋当班吃自家账**；dev 面待袋 q-…-0002 落地复验 | 真队列实跑 scanned=1587 triaged=1587，账本 `.runtime/audit/dead_letter_triage_ledger.jsonl`（C1376／B109／A57／D_MIXED43／D_LOST2） |
| 段二腿②主区暂存区无主 staged 巡检 | **已落码＋当班实清主区账**：165→37（TierA 128 全复位，工作区字节零改动） | 存证 `.runtime/quarantine/phantom_staging/20261014/`（MANIFEST 128 行＋128 枚 index 字节）；堵点本 `kind=phantom_staging` 行；三面对拍 HEAD==IDX==WT（AGENTS.md/.gitignore/config/flags.yaml） |
| C 类唯一 blob 存证 | **5,898 枚 / 1.034 GiB 全部入墓园**，逐枚回读 sha256 `mismatch=0 missing=0` | `E:/_tomb_quarantine/st-deadmass-20261013/C_unique_20261013/`（MANIFEST 5,898 行）；INDEX 第 17、18 行（rollback_cmd＋expires_at=2026-11-12） |
| 墓园备份覆盖（前任"未核"项） | **已覆盖且实时**：G 盘 23:18:56 那轮已镜像本班批次（5,899 件/1,061.8MB，与源侧字节等值） | `G:/backup/offrepo/tomb_quarantine/st-deadmass-20261013`；`scripts/backup/backup_config.yaml` L129-130 点名 |
| blob_gc phase1 | **已归档 6,129 枚 / 2,193.9MB**，blobs/ 27,186→21,059，竞态跳过 0 | `blobs_archive/manifest.jsonl`（可 `--restore` 逆向） |
| B 类 render 袋销账判定 | **判销账**（非 requeue）：整档 blob 尺给 C_UNIQUE_WOULD_REGRESS，行级尺 `lines_only_in_bag=0`、dev 反超 18 行＝已被维护六班重渲染取代 | `.runtime/quarantine/st-deadmass-20261013_render_bag_supersession/judgment.json` |
| 会话壳存量 | **507 → 27**（拆 480／留 15 有实质面／活会话跳 12） | 留存点名 `.runtime/tmp/deadmass_shell_kept.json`；全部走在册 `_prune_session_shell` 谓词 |
| `.runtime` 根散件＋嵌套壳 | 可证瞬态 **6 枚清零**，嵌套 `.runtime/.runtime` exists=False | 墓园 INDEX 第 19 行（逐件 sha256 等值回读）；持久态一律未动 |
| C/D 归档放量 | **未落**：判据表已 O(1) 成表（放行 1,477／B 剔 106），但 serializer 租约连续复持 ≥70 分钟无空窗，本班按红线不越闸 | `.runtime/tmp/deadmass_c_archive_log.json`／三轮退避轮询日志 |

## 二、净零申报

零新门、零新脚本、零新注册册。两腿全部落在既有 `commit_belt_daemon`（同一事件缝加探针）＋既有
`record_phantom_staging`（该 API 自建成为**零调用者**的装饰护栏，本批是第一个消费者）＋既有
`make_dead_letter_content_gate`（复用作判据，零新尺）。ALGO_FLOW 只补 A4/A5 节点不新建视图。
新建 git 面＝本班案卷两册（`00_ledger.md`／本册）＋新测试 13 支（tests/ 免 CREATE-GUARD）。

## 三、⚑ 本班自犯与更正（无一遮蔽）

1. **代投件差点漏投**：前任 99_delivery §一称"段三立法全落"，实测 dev 的 `tests/` 对
   `_content_dead_bag`/`_archive_ledger_evidence`/`_prune_session_shell` **零命中**＝判据裸奔；
   且 dev 历史 `81d5a0c6f1` 带 `[ARCH-APPROVAL:ARCH-DEADCLEAN-CONSTITUTION-001]` 而注册表查无此条。
   教训＝"已落地"叙述必须逐面重测（在册"终版裁定卡三条前提被实测改判"同族）。
2. **尺的字段错**：`git rev-parse dev:<path> | awk '{print $3}'` 取空列 ⇒ 13 件全判 DIFF 假读；
   改 `$1` 后 10 件 SAME_as_dev 才现形（在册"零命中尺必跑正对照"复证）。
3. **首袋死于正判**：capability 投影以 23:05 主区渲染字节为基，dev 23:07 又进一条 token ⇒
   REGISTRY-YAML-PARSE 拦整档覆盖是对的。行级"我只少=0"是**假安全**，必须比解析级集合差。
4. **尾追加吃掉顶部 import 改写行** ⇒ 实测 `NameError: timezone` 抓到；补回后定向 15 支复跑全绿。
   教训＝重基后必须真跑被改文件的配对测试，diff 计数救不了自己。
5. **归档腿首版设计错**：租约被持时每轮重算全量 blob（小时级空转 30 次未见窗）⇒ 改判据表一次成表＋
   小片抓窗。另 `python -m pytest -p no:cacheprovider` 触发 INTERNALERROR（本仓 pyproject 明令禁此组合）。
6. **车道 pytest 采集面歧义**：`import scripts.session_worktree` 落**主区**面（在册预导入病族）。
   本班以 `spec_from_file_location` 走车道面的测试真测车道码，另在主区面已对齐 HEAD 后复跑，两面同值；
   腿①②自证一律带 `PYTHONPATH=<车道>/src` 并打 `__file__`。
7. **一次 f-string 拼路径写崩台账脚本**：6 枚瞬态件已搬进入墓园但 INDEX 行没写成 ⇒
   从副本反查重建 MANIFEST＋INDEX（sha 由副本重算）。教训＝落账脚本禁把路径拼接塞进 f-string 表达式。

## 四、交接卡（下一班按此接手）

1. **C/D 放量收尾**（判据表可复用，勿重算）：`.runtime/tmp/deadmass_c_measure.jsonl`（1,583 行）＋
   墓园归宿集 ⇒ 直接跑 `python -u .runtime/tmp/deadmass_c_archive.py --execute --chunk 20 --attempts 200 --sleep 15`；
   放行集＝C_TOMBSTORED 1,376＋A_LANDED 56＋D_MIXED_TOMBSTORED 43＋D_CONFIRMED_LOST 2＝1,477；
   B_HOLD_FOR_REQUEUE 106 交 requeue 腿。**跑前先读 `.runtime/tmp/deadmass_c_archive_log.json` 修因**。
   ⚑ 若仍无空窗：呈批件=Owner 令"暂停 belt N 分钟做大批清账"（本班未自拍）。
2. **B 面 requeue**：106 袋（属主活跃者剔 9 sid）；render 袋已判销账随 C 面一起走，勿再 requeue（会删 dev 的 18 行）。
3. **blob_gc phase2**：`--phase 2 --archive`（D 类 5,086＋本班 C/D 归档后新增的 archive-only 面）；
   须"C 类归档推进后"再跑（Owner 定序）；仍只归档不删。
4. **段二两腿 dev 面复验**：袋 q-…-0002 落地后在 dev 面跑 `test_commit_belt_daemon.py`（50 支）＋
   真队列 `dead_triage_probe` 复跑一次；**注意运行面落后 HEAD 旧病**——belt 守护进程读的是磁盘码，
   落地后须换血（纪元变更自动 re-exec，或按在册手启一次）才算生效。
5. **主区投影被他道写坏一次**（5 行未缩进 `no_mount_reason:`，23:05:20）：已自愈，但若复发会拦**一切新建件**；
   根因待查＝带 `no_mount_reason` 字段的条目在渲染/手写时的缩进面（在册登记：`create_guard` 读该字段，
   而 `registry_projection/*.py` 零命中该词＝该字段无生成器读者，疑手写/旁路注入）。属维护班面。
6. **gate_audit 待裁**：总 1,214MB/293 件；轮转**确实在转**（11 个移位保留段），但存量最大两段
   120.3MB／65.3MB **超 DEFAULT_MAX_BYTES=50MB**＝有写侧未过 `rotate_if_oversized` 入口闸。
   删除属政策变更（非机械判据），本班只报不删。
7. **留存 15 壳**（§六-1 点名）：11 个只剩 `keepalive.jsonl`（可 promote 入墓园后拆），
   4 个含真成果（gpuux3v 的 staging 三稿＋handoff／maint3 的 archive plan／nightmine2 的 hash index／
   三枚 `heartbeat.jsonl.takenover-by-*` 取证改名）——promote 是各属主班或 Owner 的事，本班不动。
8. **worktree 池位**：`git worktree list` 52 条中仅 1 条目录已消失且 **locked**（`.aidrafts_pool/pool-20260919202729-c433`）；
   不自解他人 locked 池位。
