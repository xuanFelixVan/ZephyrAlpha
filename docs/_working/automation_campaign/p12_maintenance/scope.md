---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑫后勤席·输入清单与写域
---

# ⑫ 后勤席 · 输入清单 / 写域 / 分母在册

## 1 写域（本席可写，改前 claim、毕后 release）

- `docs/_working/automation_campaign/p12_maintenance/instruction.md`
- `docs/_working/automation_campaign/p12_maintenance/scope.md`
- `docs/_working/automation_campaign/p12_maintenance/checkpoint.md`
- `docs/_working/automation_campaign/p12_maintenance/ledger.md`
- 本班在 `.runtime/tmp/p12_<NN>/` 的临时件（收班前必须清零）

**禁写面（越界即归属篡改/挪门柱）**：他席四件套与信箱面（`dispatch/`、`pulse/`、`feedback/`）、判据门柱与冻结值、分数册 only-add 面（`docs/04_research_records/backtest/scores/`）、SOP 本体、`config/` 图与判据 YAML、`scripts/` 与 `src/` 码面（工具修复一律开修改单转⑤席/工具班，本席不自改）。

## 2 输入口与实测分母（1016-01 班起手现测，date 2026-10-16 11:0x）

| 输入口 | 尺 | 起手读数 |
|---|---|---|
| 11 席台账 [BLOCKER] 全量 | `grep -rn "\[BLOCKER\]" docs/_working/automation_campaign/p*/ledger.md \| wc -l` | 188 行（⑤8／⑨13／⑩167／其余八席 0） |
| 当日（2026-10-16）[BLOCKER] | 同上再筛日期 | 尺 B（同行含 BLOCKER 且含 2026-10-16）＝157 行，全属⑩155＋⑤1＋⑨1（尺与⑩1016-13 班在册两尺同源） |
| ⑩晨报点名项 | `docs/_working/automation_campaign/dispatch/daily_dispatch.md` | 在册最新单＝2026-10-15 首单＋第十二单段（⑩按班追加） |
| 断链台账 | `docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.yaml`（字段 file/line/target/batch/suggest/note，无 target_new） | 本班实测见台账 §3 |
| 队列四态 | `.runtime/commit_queue/{pending,processing,done,dead}` | 起手实测见台账 §4（⚠目录条目数受 0 字节残留污染，一律按 .json＋袋内 dead_at） |
| **提交链堵点报表（1016-01 班新发现，指令卡原未挂）** | `python scripts/governance/commit_perf_report.py --hours 24`（堵点溯源 `.runtime/audit/commit_block_events.jsonl`） | 本席首班在正门等待 27 分 05 秒后才从网关自打印话里看见这个入口；工具实测＝IN_HEAD（`git cat-file -e` 成）＋`--help` 可跑＋被 `git_commit_gateway.py` 引用 3 处＝在册已落地基建，而本席 instruction/scope 原零引用（grep 命中 0）⇒ 本班起列为常设输入口（修复时延/等待分账的直接数据源）。**本面新增行待 1016-02 班随其袋入库（本席不另起袋）** |

## 3 巡检四维权重（合规巡检每班至少跑满一维全量）

1. 会话名规范：尺＝`session_registry.json` 条目 sid ∪ 队列袋 sid ∪ 台账自报 sid，正则 `^st-qoder-p(0[1-9]|1[0-2])-<MMDD>-<NN>$`；跑者位（非 p 前缀 sid）单独列册不自罚。
2. 输出内容格式：[BLOCKER] 行是否符合 §8-A-2 七段式（日期|席+班号|类型五选一|描述|证据锚点|要谁做什么|严重度）与零问题"无"行。
3. 存放位置合规（04 vs _working 两问制）：Q1 是否研究资产（成绩/卡/结论）→04；Q2 是否任务期运行面→`_working`；frontmatter `ttl` 只允许 permanent/task_bound，禁 doc_type。
4. 收班八件完成度：逐席按可观测面量（pid 文件／heartbeat.jsonl 末行／tmp 残留／worktree／[BLOCKER] 行有无）。
   - **⑧零 worktree 自证尺谓词（1016-02 改正，1016-01 犯漏）**：本席禁建面，收班⑧须分层量三态并逐面点名——(a) `git worktree list` 全行数为分母；(b) 命中 `.worktrees/st-*` 车道枚数（历史遗留 opsv/perfz1/prevw 系⑩开班志整批交清理专班，本席不自删）；(c) 命中 `.aidrafts/st-qoder-p12-<当日班号>` 会话壳——壳由网关提交期分配（git_commit_gateway 阶段3），非本席主动建面但会随本席提交自增，故 1016-01 只 grep `.worktrees` 得出「p12 命中 0」系分母不全（实测 31→37 行、p12 命中 0→1）。正解＝班前班后各测一次壳面行数差，如实报「本班主动建 worktree=0；网关为自家袋分配 aidrafts 壳 1 枚（属历史壳族，交清理专班不自删）」。

## 4 复发族登记册（同类第二次=立法候选报⑩，禁第三次）

| 族签名 | 首次在册 | 第二次 | 本席处置 |
|---|---|---|---|
| scaffold 裁定通道 CLI 缺失（alias 碰撞阻断新 .md，无 --force-override 腿） | 1016-01 本席直证 | 待下班复量 | 修改单转⑤席＋本席在册绕行（批量 token 通道） |
| heartbeat「注销」面与进程本体脱节 | ⑩1016-10（高）／1016-11（中） | 1016-10 与 1016-11 连续两班＝已第二次 | 立法候选，报⑩进 SOP 收班②措辞 |
| 主区 index 落后 HEAD 快照（落地收尾不回写） | ⑩1016-12 §30.2 | 1016-13 第十八件复现＝第二次 | 立法候选，报⑩；本席不代复位 |
| POOL-REGRESSION-DIRECTION 同签名跨席成串判死 | ⑩1016-02（14 枚/18 分） | 1016-04（18 枚/10 分「双侧皆改」）＝同域续现 | 已升级⑩呈批面，本席复量登记（本班全族 25 枚/今日累计） |
| 主区 claim 锁文件腿不承重（pid=0 会话 .lock 被当死锁自跳） | ⑩1016-01（p10_line_lead/ledger.md:468，中） | **⑫1016-01 直证（第三种载体）**＝acquire 四面全回 ACQUIRED 后同批 `check` 立报"FREE — 的死锁已被自动清理"，而 registry held_files=5 在场且袋照常落地 588f96ed7d | 立法候选成立；WO 转⑤席定口径＋请⑩写进通令（台账 §11 第 9 枚 [BLOCKER]） |
| 停守护后 heartbeat.jsonl 末行仍 alive（SIGTERM 无 exited 收尾腿） | ⑩1016-11（中，"末行说谎"形态） | **⑫1016-01 本席自证**＝12:04:0x  terminate 自家 keeper pid 41508 并核 NoSuchProcess、自家 pid 文件已删，而 sessions/st-qoder-p12-1016-01/heartbeat.jsonl 末两行仍 status:"alive"（04:03:56Z） | WO-12-03 补件＝⑤席给 SIGTERM/末袋后强制写 exited 的收尾钩子；**本面改动待 1016-02 班随其袋入库（本席不另起第三袋＝避同件并存在途律，如实挂待办并已向 Owner 报）**｜**⑫1016-03 第 4 观测＋根因坐实**＝Windows 下 `psutil.terminate()` 走 TerminateProcess 不派发 Python 信号，`heartbeat_daemon.py:575-588` 的 interrupted/exited handler 永不被调用⇒"收班②按 PID 精确终止"这条在册做法必然留下末行 alive；正向对照＝⑩1016-17/18 由收班方主动 append `exited` 行后终止（两班末行诚实）；立法提案已随本席台账 §13.6/§13.8 报⑩（SOP 收班②改三拍：append exited→按 PID 终止→pid 复测），⑤席守护侧治本（terminate 前 revoke＋收尾，或改 `CTRL_BREAK_EVENT` 派发）续挂 WO-12-03/05 不变 |
| 心跳守护 CLI 无 sid 校验（`--help` 等任意 argv 被当会话名建档） | 13:0x 他班首现（本席起手读到该面 age 28.3 分） | **⑫1016-03 直证第二载**＝本席 13:21:28 亲跑 `--help` 后 `.runtime/sessions/--help/heartbeat.jsonl` mtime 0.17 分・末行 `exited` pid 37488・面共 34 行 | 立法候选成立（同签名第二载）；修改单转⑤席补 `_run_cli` usage 分支与 sid 形态校验（锚点 heartbeat_daemon.py:816）；全线 dim4 分母须先剔该假面 |
| keepalive grant 的 `daemon_pid` 记写手进程而非守护 | **⑫1016-03 首载**＝本席 grant 落 `daemon_pid=48512`（13:23:46 现测已 NoSuchProcess），真 keeper＝39932 在跑 | 待下班复量 | 转⑤席定字段语义（改记守护 pid 或更名 `writer_pid`）；收班②"守护 pid 唯一来源＝heartbeat.jsonl 末行"须⑩写进通令；本席不改码 |
| `dead-archive` 归档袋目录无互斥＋`dead/` 内非袋异形件 | **⑫1016-03 首载**＝本席 13:29:36–37 限 3 席 8 枚与并发第二跑 13:30:04–07 全量 84 枚同写 `dead_archive_20261016/manifest.jsonl`（92 行、qid 零重复）；异形件 `_recurrence_state.json`（572460 字节）使 `len(dead/*.json)` 恒比 `health.counts.dead` 大 1 | 同班复量同值（13:33 与 13:35 两读一致） | 转⑤席给归档袋加锁或按 sid 分目录并把非袋件移出 `dead/`；全线计数一律读 `health` 字段或"必有 qid/dead_at"谓词 |
| PID 复用使"按记录 pid 判活"失真 | **⑫1016-03 首载**＝gpux2 pid 文件 9260 现属 `svchost.exe`；p07-1015-07 末行 exited 所记 28084 现属 `E:\同花顺远航版\bin\modules\performance\hxperformance.exe` | 待复量 | 判活与终止须叠 create_time＋cmdline 双校（与在册"禁按镜像名杀"互为一对）；转⑤席在 ghost 判定与收班②工具面加双校腿，WO-12-01 同批评估 |


---

## 5 尺面增补与族续册（1016-04 班追加；§1–§4 各行逐字不涂）

### 5.1 dim1 会话名尺改正（本席自犯假阳，旧尺行保留在 §3.1）

旧正则 `^st-qoder-p(0[1-9]|1[0-2])-<MMDD>-<NN>$` 不含子车道字母位，实测把合法 ⑦C 席会话名 `st-qoder-p07c-1016-01` 判成"当日新违 1 枚"＝**假阳**。改正尺＝`^st-qoder-p(0[1-9]|1[0-2])[a-z]?-<MMDD>-<NN>$`；跑者位仍单列不自罚。此改只扩"合法子车道形态"，不放松任何真实违规判定（非 p 前缀仍归跑者位、日期/班号缺位仍判违）。

### 5.2 新增输入口三面（1016-04 起常设，皆零写只读）

| 输入口 | 尺 | 1016-04 读数 |
|---|---|---|
| reaper 计划任务轮自报（系统腿实况，非手动 --status） | `python -c "import json;d=json.load(open('.runtime/process_reaper/last_run.json'))['safety_wires'];print(d['dead_archive'],d['git_gc_auto'])"` ＋顶层 `errors` | lane 腿 `ModuleNotFoundError("No module named 'scripts.session_worktree'")`；dead_archive rc=1 error；gc ok elapsed 240.8s |
| 死信自动归档腿审计 | `.runtime/audit/dead_archive_wire.jsonl`（每行含 wire/dry_run/days/status/rc/error/stderr_tail/audit_written） | 全册 2 行，全 error・archived=0・"serializer 租约存活（pid=46988）" ⇒ 自动腿今日零归档 |
| 裁定册账本 vs 投影漂移（零写象限判） | `python scripts/governance/registry_projection/registry_projection_generator.py --check --registry-id REG-RULING-001 --physical-path docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` | `ok=false, quadrant=private_edit, wrote=false`；diff 点名待删 #522–#539 共 18 条 ⇒ **禁直接 render**（第 2 载复现） |

### 5.3 复发族续册（同 §4 表头；首载记"首现"，第二载起记立法候选）

| 族签名 | 首次在册 | 第二载 | 本席处置 |
|---|---|---|---|
| 死信归档台账不可归因（manifest 行无 actor/session 列） | ⑫1016-04 直证（92 行字段集实测；13:30 全量 84 枚跑者至今不明） | 待下班复量 | 转⑤席加 actor 列＋全量模式硬要求 --session 或显式确认旗 |
| 降级态与未触发同形（手动轮腿 ok／计划任务轮腿恒死） | ⑩1016-19（gpu_watchman 路径与子命令写错致 rc=2 误记工具缺陷，非此族）→ 本席 ⑫1016-04 重定义为真族 | **⑫1016-04 第 1 真载**＝reaper `lane` 腿：计划任务轮 ModuleNotFoundError vs 手动轮 lane=ok scanned=32 同机两读 | 立法候选候选成立；要⑤席给"腿不可用"独立计数与告警消费面，禁再以手动轮绿自证 |
| 自动维护腿把正常互斥记 error（观测噪声掩真故障） | ⑫1016-04 首载（dead_archive 今日 2/2 error，均为排空租约存活＝设计行为） | 待复量 | 转⑤席给 skipped_lease_active 态＋占用分支出 JSON |
| CAS 审计面 session 归属恒空（热文件写入不可归因） | ⑫1016-04 首载（safe_write.jsonl(+.1) 对 ruling_registry 命中 300 行 session 全空；#450 涂改写手因此不可定位） | 待复量 | 转⑤席补归属腿（contextvar/env 取 sid，缺失记 unknown 而非空串）；本席不自改码 |
| 心跳守护多枚并存（正门/落地链每袋为同 sid 代起新守护） | ⑫1016-03 首载（第二枚 45428，pid 文件只记它） | **⑫1016-04 第二载**＝第三枚 34592（14:17:15/14:17:45 alive，14:18:15 由注销单口自退写 exited）⇒ 同签名第二次＝立法候选，报⑩进 SOP 收班② | ⑤席"已在册即复用"＋pid 文件按 sid 记全列表；⑩把收班②尺改为"release→unregister→读回末行"（本席 §13.9 提案续挂，本载为正向复验） |


### 5.2 1016-05 班改正尺与新增谓词面（15. 节同班实测，§5.1 及以前各行逐字不涂）

- **dim2 登记尺（改正，取代旧尺的"仅 `^- \[BLOCKER\]` "谓词）**：`^[-*]\s*\[BLOCKER\]` + 可选反引号 + `\s+<当日 YYYY-MM-DD>\|`。实测同框对照＝改正尺当日 372 枚 vs 旧尺 223 枚，失明 149 枚全为反引号/星号形态（⑤席 22 枚整体在盲区内）。旧尺读数与结论（1016-03/04 记"⑤⑨各 1 枚"）**保留不涂**，本条为改正条。
- **dim2 段数谓词**：合规＝日期之后恰 6 段（`班号|类型|描述|证据|要谁做什么|严重度`）；`||` 空尾记"缺严重度"，段数 <6 记"字段不足"，>6 记"描述内含竖线"（须人工判读，不自动定罪）。
- **dim1 命名尺白名单续挂**：子车道字母后缀（`p0[1-9]c?`、`p1[0-2]c?`）合法，承 §5.1；`--help` 假面一律剔出分母。
- **dim4 说谎面谓词（本席新立，供下班复用）**：`末行 status=alive` 且 `进程表无 cmdline 含 heartbeat_daemon＋该 sid 的进程` ⇒ 计一枚；分母剔 `.runtime/sessions/--help/`；须**两瞬时并报**（进程起停抖动实测使单点读数在 14/15 间摆）。
- **代注销执行前置（本席新立，写入操作序）**：删 pid 面前先做**三校**＝①`psutil.Process(pid)` 是否 NoSuchProcess（AccessDenied 带 name 者＝PID 复用，禁终止）②同 sid 是否仍有在跑守护（有则 HOLD，不写 exited）③heartbeat.jsonl 末行是否已 exited（是则只删面不写行）。三校缺一即降级为"只记录不动盘"。

- **追加型件手术自证项（1016-05 自犯后新增，收班/写后必跑）**：任何"替换游标块／搬移留档块"的组装式改写，改前改后各断言 ①`content[:3] == '---'` ②frontmatter 键集合与改造前**逐字节前缀相等**（取第一个游标标记前的整段作前缀，改造后新文件必须以该前缀原样开头）③一级标题行在。本席实测五项旧自证（标记配对／核心行逐字／行数增量／BLOCKER 谓词命中／禁串缺位）全部通过而文件头已被弃 ⇒ 结构计数必须含"头部前缀相等"这一条，否则假绿。
