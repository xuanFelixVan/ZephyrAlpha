---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑫后勤席·游标
---

# 游标

<!-- P12-1016-03-CURSOR -->
cursor: 1016-03 班（本席当日第 03 班）＝职责1-4 全跑：当日登记行两谓词同读 154 枚（严式 `^- [BLOCKER]` 且首字段=2026-10-16＝⑩140＋⑫14；⑤⑨两席各 1 枚用反引号形态而本谓词不计），点名归⑫当日 2 枚全经窗口（dispatch:1095 三席死信分诊＝本班已执行；dispatch:1056／p10 ledger:850 ⑧尺谓词＝1016-02 已销）、合规四维全量复跑（dim1 当日新违 0＝仅 4 枚 1015 遗留 lane／dim2 全角 `｜` 致 15 枚尾段切分不足＝异常 12 枚全在⑩台账／dim3 战役目录 64 件 frontmatter 全绿／dim4 心跳 46→47 面中末行 alive 17→16 而说谎面两瞬时同值 15）、**职责3 结构性工单实执行＝`dead-archive --content-level --execute` 归档 diskp0 6 枚＋perfz1 2 枚 A_LANDED（mv 可逆、manifest 机生 8 行、n_evidence_lost=0）**、复发防控四族清点（SIGTERM-exited 第 4 观测**根因坐实**＝Windows psutil.terminate() 走 TerminateProcess 不派发 Python 信号故收班②必留 alive，正向对照＝⑩1016-17/18 手工 append exited／主区 claim 两腿第 5 载体＝起手 .lock 腿未 acquire 态／异形件计数族第 5 载体＝`dead/_recurrence_state.json`／新案三族＝守护 CLI 无 sid 校验・keepalive `daemon_pid` 记写手・dead-archive 归档袋无互斥）；**本班不推"全线可恢复"结论**（判据归⑩）。本班 [BLOCKER] 追加 8 枚（高1/中4/低3），零写他席面、零主动建 worktree、GPU 未 acquire 如实免、零 spawn 子代理。
last_run: 2026-10-16 13:17:52 起手（冷启动三步 date 现测）／防重入闸开 13:36:08（＝上班末写 checkpoint mtime 13:11:08＋25 分，本班全程只读先行不写短报行）／本段落笔 13:4x:xx（date 现测，见台账 §13.7）；`.lock` 腿 13:30:44 acquire 四面、registry 腿 13:22:20 claim 四面 True；收班四件（release 两腿／三拍心跳绕行 append exited→按 PID 39932 终止→pid 复测／清 .runtime/tmp/p12_03／三面读回）在本袋落地后执行，本班终态与"末行是否诚实"由下班按落地面复量，本席不预签
last_batch: st-qoder-p12-1016-03（今日第 03 班；袋内容＝p12_maintenance/{ledger,scope,checkpoint}.md（instruction.md 本班未改不随袋）；起手队列＝pending 0（1016-02 所记被 TAKEOVER-PENDING 挡的那枚 `q-20261016-st-opsv-20261015-0003` 已定态 done・landed_id 81f8839365f302930b7dcfe7d45399ef344f01aa）／processing 1（`q-20261016-st-prevw-20261015-0006` 13:31:20 建，属已终态会话）／done 885–890（三瞬时 885・886・890＝有界修剪面随时刻变动）／dead 511（异形件 `dead/_recurrence_state.json` 令目录 `.json` 计数恒 512）→ 本班归档 8＋并发第二跑 84 后＝419 袋（420 文件）；当日死信 256 枚 max dead_at 13:26:32；磁盘 D: 100.6G 空闲／C: 25.6G 空闲，ram 86.8%・avail 8.4G＝ALERT-SYS-004 续现＋ALERT-SYS-005 本班新破）
notes: 下班（1016-04）首查五件＝①本袋四态（判落地一律 `git log -1 --name-only -- docs/_working/automation_campaign/p12_maintenance/scope.md`＋blob 内容级复量，勿用 done 计数；CRLF/LF 归一差勿误判"袋没吃全"，本席在册律）②**本班收班②三拍绕行是否留下诚实末行**（尺＝`.runtime/sessions/st-qoder-p12-1016-03/heartbeat.jsonl` 末行 status 是否 `exited`＋reason 含 `final shift-close deregistration (p12-1016-03)`，并 `psutil.pid_exists(39932)` 须 False；若仍 alive＝SIGTERM-exited 族第 5 观测且本席绕行失败，直接升⑩不再等⑤席）③并发第二跑 `dead-archive`（13:30:04–13:30:07 全量 84 枚）归因（尺＝`dead_archive_20261016/manifest.jsonl` 该时段行的 tool/archived_at 与在跑进程表；若系某班手工跑则其应自报，若无＝存在自动归档腿未在册，本席 dim 面须补）④`st-prevw-20261015-0006` 定态（该 sid 心跳末行 exited 于 2026-10-15T19:41:13Z，其袋 13:31:20 仍在 processing＝代投腿不看会话死活的直接检验；尺＝该 qid 现处 done 或 dead，若 dead 记族签名与 recurrence_count）⑤断链台账是否入库（现值仍＝盘上 19921 行／`git ls-files` rc=1／`git log` 该件无／目录 status `??`，第 4 班未成）。判前任死活按三证（pid 文件面＋锁面＋袋定态面），禁以 registry held／heartbeat 末行作主证；心跳面另加一警＝`.runtime/sessions/--help/` 假会话面必须剔除后再算 dim4 分母。
<!-- P12-1016-03-CKP -->

## 本班首次游标留档（同班推标，四行逐字取自落地面 blob，删除集=0）

cursor: 首班开档已投袋待落地（本席四件套 2026-10-16 由 1016-01 班建，creation_token 4 条同册）＝当日 [BLOCKER] 全量 164 行三态分流（本席可自修 2／跨域修改单 7 单／需Owner 呈批 1 件，点名归⑫在册行 0 枚）、合规巡检四维全量首跑（13 席四件套齐、命名零 BAD、当日登记行 163/164 可解析、E 维唯一 no_frontmatter 命中＝本席自家已当班修）、复发族登记册建 6 族（心跳族本班第三现＝立法候选成立）；**本班不推"全线可恢复"结论**（判据归⑩）；本班头号新案＝SOP 在册输入口"断链台账"整目录未入库且无生产者脚本（2490 处断链唯一存活面只在盘上）。
last_run: 2026-10-16 11:00:25 起手（冷启动三步 date 现测）／11:25:46 投袋前落笔（date 现测）＝班期 25 分 21 秒；本席体感钟曾估成 50 分＝按在册律现测改正；收班四件（release／停 keeper pid 41508／清 .runtime/tmp/p12_01／三面读回）投袋后即执行，本班终态由下班按落地面复量，本席不预签
last_batch: st-qoder-p12-1016-01（今日第 01 班＝本席首班；袋内容＝四件套 4 件＋capability 总册（该册 git diff --numstat HEAD＝+20/−0，恰本席 4 条 token×5 行，删除集 0）；起手队列＝pending 0／processing 17（全 0 字节 tmp 残留，真 0）／done 874／dead 511（500 .json＋11 非 json 全 0 字节）／今日死信按 dead_at 244 枚 max 11:17:22；本班 [BLOCKER] 追加 8 枚（严式谓词 8、宽松谓词 9））
notes: 下班首查五件＝①本袋四态（判落地一律 `git log -1 --name-only -- docs/_working/automation_campaign/p12_maintenance/ledger.md`＋blob 复量，勿用 done 计数）②scaffold 裁定通道缺旗是否已由⑤席补 `--force-override` 到 md/yaml/json/rule 四子命令（尺＝`python scripts/scaffold.py md --help` 是否出现该旗，现值＝无）③断链台账 `docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.yaml` 是否已入库或已补生产者脚本；两者皆无则每日复量 `wc -l`（现值 19921）并留案 ④心跳族是否第四次出现（现＝第三次，出现即直呈 Owner）⑤WO-12-01..07 是否有回话面。判前任死活按⑩1016-11 在册三证（pid 文件面＋锁面＋袋定态面），禁以 registry held／heartbeat.jsonl 末行作主证；防重入尺另加一腿＝本席 ledger 写痕＋pulse 末行（在册：短报班只写 ledger 不写 pulse 会造成 pulse 无碰撞却在途假象）。
<!-- P12-1016-01-CKP-FIRST -->


## 1016-01 终态游标留档（1016-02 班补回：本顶块被 1016-02 活游标原地替换后，1016-01 终态游标逐字节取自 HEAD blob 存此，满足在册律"上一班游标行仍在/禁整档覆写"；下方四行为 1016-01 落地面终态）

<!-- P12-1016-01-CURSOR -->
cursor: 首班开档已投袋待落地（本席四件套 2026-10-16 由 1016-01 班建，creation_token 4 条同册）＝当日 [BLOCKER] 全量 164 行三态分流（本席可自修 2／跨域修改单 7 单／需Owner 呈批 1 件，点名归⑫在册行 0 枚）、合规巡检四维全量首跑（13 席四件套齐、命名零 BAD、当日登记行 163/164 可解析、E 维唯一 no_frontmatter 命中＝本席自家已当班修）、复发族登记册建 6 族（心跳族本班第三现＝立法候选成立）；**本班不推"全线可恢复"结论**（判据归⑩）；本班头号新案＝SOP 在册输入口"断链台账"整目录未入库且无生产者脚本（2490 处断链唯一存活面只在盘上）；**本班终态＝袋 0001 已落地 `588f96ed7d`（四面盘==HEAD blob 全等，判落地只认 git log＋blob）、袋 0002＝收班补录（台账 §11）、[BLOCKER] 追加 9 枚（严式谓词）、班期 59 分 03 秒含正门等待 27 分 05 秒；复发第二族本班达标＝主区 claim 锁文件腿不承重（⑩1016-01 同签名第二现）。**
last_run: 2026-10-16 11:00:25 起手（冷启动三步 date 现测）／11:25:46 投袋前落笔（date 现测）＝班期 25 分 21 秒；本席体感钟曾估成 50 分＝按在册律现测改正；收班四件（release／停 keeper pid 41508／清 .runtime/tmp/p12_01／三面读回）投袋后即执行，本班终态由下班按落地面复量，本席不预签／**补：11:59:28 收班补录落笔（date 现测）＝班期 59 分 03 秒，其中正门等待 27 分 05 秒（袋 0001 created_at 11:30:40→done 观察 11:57:45，子进程 `-m pre_commit run` 门禁长跑，与本席写面零相关）；分账 例行≈24／返工 0／等待 27.1 分**
last_batch: st-qoder-p12-1016-01（今日第 01 班＝本席首班；袋内容＝四件套 4 件＋capability 总册（该册 git diff --numstat HEAD＝+20/−0，恰本席 4 条 token×5 行，删除集 0）；起手队列＝pending 0／processing 17（全 0 字节 tmp 残留，真 0）／done 874／dead 511（500 .json＋11 非 json 全 0 字节）／今日死信按 dead_at 244 枚 max 11:17:22；本班 [BLOCKER] 追加 8 枚（严式谓词 8、宽松谓词 9））
notes: 下班首查五件＝①本袋四态（判落地一律 `git log -1 --name-only -- docs/_working/automation_campaign/p12_maintenance/ledger.md`＋blob 复量，勿用 done 计数）②scaffold 裁定通道缺旗是否已由⑤席补 `--force-override` 到 md/yaml/json/rule 四子命令（尺＝`python scripts/scaffold.py md --help` 是否出现该旗，现值＝无）③断链台账 `docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.yaml` 是否已入库或已补生产者脚本；两者皆无则每日复量 `wc -l`（现值 19921）并留案 ④心跳族是否第四次出现（现＝第三次，出现即直呈 Owner）⑤WO-12-01..07 是否有回话面。判前任死活按⑩1016-11 在册三证（pid 文件面＋锁面＋袋定态面），禁以 registry held／heartbeat.jsonl 末行作主证；防重入尺另加一腿＝本席 ledger 写痕＋pulse 末行（在册：短报班只写 ledger 不写 pulse 会造成 pulse 无碰撞却在途假象）。
<!-- P12-1016-01-CKP -->

## 1016-02 终态游标留档（1016-03 班搬回：顶块被本班会活游标原地替换后，1016-02 游标四行逐字取自落地面存此，满足在册律"上一班游标行仍在／禁整档覆写"）

<!-- P12-1016-02-CURSOR -->
cursor: 1016-02 班（本席当日第 02 班）＝职责1-5 全跑：当日 [BLOCKER] 全量 219 行/严式登记 170 行三态分流（自修 2／转⑤席 2／清理专班+⑤席共担 1／需Owner 0，点名归⑫当日 4 枚全出自⑩1016-17＋晨报 dispatch:1056）、合规巡检四维全量复跑（dim1 今日新违 0/仅 4 枚 1015 遗留 lane・dim2 168/170 可解析・dim3 64 件 frontmatter 全绿・dim4 心跳末行 alive 14 面中 13 面 pid 全 DEAD）、复发防控**SIGTERM-exited 族第三观测越红线升级⑩**＋主区 claim 两腿脱节族第四载体（diskp0 活-idle 过占后自愈）、承接 1016-01 明挂本班两件随袋入库（scope §3⑧谓词改正＋commit_perf 输入口＋SIGTERM 族行）、修⑧自证尺谓词入 scope §3.4；**本班不推"全线可恢复"结论**（判据归⑩）；本班头号＝13 面说谎心跳＝队列 ghost_session/TAKEOVER-PENDING 挡道燃料。本班 [BLOCKER] 追加 5 枚（高1/中3/低1），零写他席面、零主动建 worktree（网关为自家袋分配 aidrafts 壳属历史壳族交清理专班）、GPU 未 acquire 如实免、零 spawn 子代理。
last_run: 2026-10-16 12:47:49 起手（冷启动三步 date 现测）／写作段落笔 13:08:35（date 现测），正门等待由下班按落地面复量；收班四件（release 四面／停自家 keeper pid 22984 按 PID 精确核活／清 .runtime/tmp/p12_02／三面读回）投袋后即执行，本班终态由下班按落地面复量，本席不预签
last_batch: st-qoder-p12-1016-02（今日第 02 班；袋内容＝p12_maintenance/{ledger,scope,checkpoint}.md（instruction.md 本班未改不随袋）；起手队列＝pending 1（被 TAKEOVER-PENDING 挡）／processing 0／done 886／dead 511（零字节 0，前序 cleanup 已清 1016-01 所记 17 枚 0 字节）／当日死信 255 枚 max dead_at 12:41:33／custody=True 244 零误杀；磁盘 D: 101G 空闲/C: 25.6G，Out-of-diskspace 三枚死信全为 10-15 晚今日未复现）
notes: 下班（1016-03）首查五件＝①本袋四态（判落地一律 `git log -1 --name-only -- p12_maintenance/scope.md`＋blob 内容级复量，勿用 done 计数；CRLF/LF 归一差勿误判"袋没吃全"）②SIGTERM-exited 族是否已由⑤席补收尾钩子或⑩写进 SOP 收班②（尺＝新收班后 heartbeat 末行是否出现 exited；现值＝13 面全 alive 而 pid 已死）③pending 1 枚 TAKEOVER-PENDING 是否被清理专班按四 sid 接管处方 resolve（尺＝commit_queue status pending 是否归 0）④主区 claim 两腿脱节是否再现（起手必两腿都查：.lock 腿 lock_files list ＋ registry held_files，勿只信一腿）⑤断链台账 broken_records.yaml 是否入库（现值仍＝盘上 19921 行/HEAD 查无，1016-01 头号新案未销）。判前任死活按三证（pid 文件面＋锁面＋袋定态面），禁以 registry held／heartbeat 末行作主证（末行 alive 已证不承重）。
<!-- P12-1016-02-CKP -->
