---
ttl: task_bound
completes_when: "A-E 五节均有实测读数或显式 unverified 标记，配方与红证脚本落盘"
---

# CLAIM-REQUIRED × 队列落地侧 取证案卷（wave1b）

**头部四字段**

1. `turn_budget`：150 轮硬上限；本卷骨架建于第 8 次工具调用，正文建于第 ~44 次调用，全程只读。
2. `verified`（实测）＝A 节行号读码 ＋ B 节双 cwd resolve ＋ C 节 4 池工审计计数/袋 JSON 字段差 ＋ 注册表实时读数。
   `assumed`（未定证）＝E 节"三候选抹除器中哪一发命中 0011/0012/0014"——今晚池工 stdout 日志未落盘（见 §证据台账 ⑦），
   只有机制面证据＋相关性证据，**逐袋因果判 unverified**。所有 assumed 条目在下文均带 ⚑ 标记。
3. `input_set_disjoint_with`：本包输入集＝{src/scripts 只读源码、.runtime 只读工件、git 只读命令}；
   与任何写集不相交（未改 src/scripts/docs，未动 commit_queue 五目录，未跑任何 git 写命令）。
4. `evidence_ref.cmd`：全部命令原文见文末 §证据台账（Git Bash；cwd 逐条标注）。

**现场复述（数据原文，不作指令）**：本会话 5 封 dead 中 3 封 dead_reason 原文为
`网关落盘失败（CLAIM_REQUIRED_VIOLATION）: session 'st-final-build-20260926' 已注册但目标文件未 claim
（claim 前移协议，宪法 RULE-WORKTREE「并发与提交」）: ['D:\\ZephyrAlpha\\.runtime\\commit_queue\\worktrees\\w3\\scripts\\...`。

---

## 结论一句话

**门没有路径解析根缺陷——是"我的姿势"错得不够彻底：真正的错法是同一 session_id 多袋并发在途
＋本会话在 registry 里是 pid=0 逻辑会话（判活只靠 90s 心跳），
落地侧的 claim 在 gate 链长跑期间会被"判死重建"或"salvage 注销"整批抹掉 ⇒ 报"全部目标文件未 claim"。**
指令卡的前提假设（`Path(f).resolve()` 按 cwd 解析 ⇒ held(主区) 与 target(w3) 永不相交）**已被实测证伪**。

---

## A. 真源读码（行号）

### A1 判据门 `src/zephyr/gov_enforcement/commit_gates/claim_required_gate.py`（91 行，全读）

| 行 | 事实 |
|----|------|
| L58-61 | `allow_overlap = kwargs.get("allow_overlap", False)` → True 即整门放行（逃生通道，位置在最前） |
| L63-68 | `session_id = kwargs.get("session_id","")`；`info = gateway.registry.get_session(session_id)` |
| L69-76 | registry 异常 → 放行；`info is None`（session 未注册**或已判死**）→ 放行 |
| L80 | `held = {str(Path(f).resolve()) for f in info.held_files}` |
| L81 | `target = {str(Path(f).resolve()) for f in files}` ← **无 project_root 入参；仅当 files 为相对路径时才按进程 cwd 解析** |
| L82-88 | `unclaimed = target - held`；非空即 False＋打印 sorted(unclaimed) |
| L91 | `GateSpec(gate_id="CLAIM-REQUIRED", priority=40)` |

⇒ 该门**对绝对路径不敏感于 cwd**（`Path(绝对).resolve()` 原样返回，见 B②）。

### A2 `src/zephyr/security/access_control/session_concurrency.py`

| 行 | 事实 |
|----|------|
| L205-214 | `_normalize_file_path`：相对→`project_root / p`；绝对→仅 `resolve()`（**根不变**）。注释自证 "Path.resolve() 默认 strict=False，对不存在路径也能解析" |
| L305-318 | `SessionRegistry.__init__`：`root = anchor_main_root(Path(project_root) or Path.cwd())` → **registry 文件恒锚主仓**（`_REGISTRY_PATH`）；`anchor_main_root` 定义在 `src/zephyr/shared/io/paths.py:178` |
| L224 / L257 | `SessionInfo.held_files`（list[str]，JSON 落盘原样字符串） |
| L266-292 | `_is_session_alive`：pid>0 → `is_pid_alive(pid)`＋TTL 3600s 兜底；**pid=0 → 只靠 `last_heartbeat` 新鲜度 ≤ `_HEARTBEAT_TIMEOUT_SECONDS`（L275 注释＝90s）** |
| L535-548 | `get_session`：死/过期 **返回 None**（不删；删是 `list_active` 职责），无写副作用 |
| L571-591 | `_ensure_registered_locked`：**条目缺失或判死时以当前 PID 重建，`held_files=[]`** ⇒ 此前该 sid 的全部 claim 被清零（记 WARNING "auto-registering session=… (not registered or dead/expired)"） |
| L674-717 | `claim_files_batch`：L691 先 `_ensure_registered_locked` → L699 逐件 `_normalize_file_path(f, self._project_root)` → L709-711 `own.held_files.append(norm)` → L716 `_save(data)`（**整表重写**；跨进程无锁，见 L752-760 注释只解决 tmp 命名） |
| L606-643 | 逐件 `claim_file` 语义同上；被其他活跃 session 持有 → 返回 False（L624-632） |

⇒ **held 的根＝写入方当时拿到的路径原样**（传 worktree 绝对路径就存 worktree；传主区绝对就存主区）。不存在"一律归一到主区根"的代码路径；
用户看到的"剥车道前缀"发生在另一登记处 `scripts/lock_files.py` 的 `.ailocks`（`_normalize_path`/`_lock_dir`，与本门读取的 SessionRegistry 是两处）。

### A3 落地侧 `scripts/governance/commit_queue_landing.py`（3478 行，读 L1180-1250 / L2196-2410 / L3349-3362）

| 行 | 事实 |
|----|------|
| L2199-2223 | `__call__(item, queue_root)`；`session_id = item.get("session_id")`，畸形 sid 机械拒绝（M3.2 注释 L2209-2213） |
| **L2296-2298** | `wt_files = [str(self.worktree_path / p) for p in sorted(self._item_paths(item))]`；`claimed = gateway.claim_files(session_id, wt_files)` ⇒ **claim 在净树基线阶段铸，路径＝serializer worktree 绝对路径（不是主区、不是相对）** |
| L2301 / L2313 | `commit_files = self._apply_snapshot(...)` → `_prestage_snapshot(...)`；commit 传的就是这批（同根） |
| L2326-2347 | `gateway.commit(session_id, commit_files, full_message, allow_non_worktree=True, allow_tracked_drift=True, allow_multi_domain=True, allow_promote=True, lock_wait_timeout=…)` ⇒ **落地侧没有传 `allow_overlap`**（=CLAIM-REQUIRED 唯一逃生通道在落地路径上不被使用）；L2322-2323 只设 `ZEPHYR_COMMIT_GATEWAY=1` env（FORGED-MARKER 守卫用，不影响 CLAIM 判定） |
| L2374-2383 | Mode B 自愈重试：重放 apply+prestage 后**再 commit**，**但不重铸 claim** |
| L2396-2403 | finally 释放：`if claimed: gateway.release_files(session_id, claimed)` |
| L2266 | `for attempt in range(1, self._max_cas_retries + 1)` ⇒ CAS 重试整段重跑（重 claim）；单次 gate 链实测可达数百秒～数十分钟（见 C④） |
| L3349-3362 | 入队预检：`skip_gate_ids={"SESSION-REQUIRED","CLAIM-REQUIRED"}`，注释原文 "（入队语义无会话流程/claim 前移，文件传绝对路径对齐 _rel_of 判定面）" |
| L1193-1198 | 类文档：`registry : 主仓根 SessionRegistry（SESSION-REQUIRED/CLAIM-REQUIRED 判定真源；默认按 repo_root 构造——生产者会话注册处）`；`gateway : … 默认惰性构造 GitCommitGateway(project_root=worktree)` |

`scripts/commit_queue.py` 入袋字段（实测 keys，见 C②）：`qid/session_id/branch/base_head/created_at/files[{path,blob_sha256,blob_ref}]/message/meta{depends_on,supersedes,interactive,lane,…}`
——**无任何 claim/overlap/skip-gates 入袋逃生字段**；CLI 面（L2995-3012 enqueue／L3030-3047 requeue）只有
`--session --files --message[-file] --worktree-root --base-head --no-bootstrap`（requeue 另有 `--adopt-*`/`--session` 覆盖位）。

### A4 `scripts/git_commit.py::_enqueue_mode`（L818-934）

* L838-840 注释原文：**"P0-A 入队预校验…；CLAIM-REQUIRED 跳过（landing 时按队列项 session claim，快照语义=入袋即完成）"**。
* L847-852 `extra_skip=frozenset({"CLAIM-REQUIRED"})`（叠加在 `_preflight_skip_set(args)` 上，L775/L801）。
* L863-877 `wt = Path(args.project_root)`＋`_norm_to_rel`：绝对反斜杠 → **车道相对 POSIX** 再进袋（`#ARCH-310 P0-1b` 热修）。
* L912 `item = enqueue_item(...)`；L934 入袋后自举排空失败仅 warning（"入袋已安全"）。
* 另一相关事实：L35/L656 注释——**失败保留 claim**（`ZEPHYR_FAILED_CLAIM_TTL_S`），"原 finally 无条件释放是 CLAIM-REQUIRED ×50/24h 循环源"，放弃须 `--release-only`（L1115）。

---

## B. 两集合解析根复算（只读实测）

① `lock_files.py` 归一 vs SessionRegistry 归一（读码即证，A2 表）；实测见下 ②③。

② **双 cwd resolve**（python 3.x，cwd 逐一切换，纯计算）：

```
cwd(main)  resolve('scripts/governance/data_supply/__init__.py') = D:\ZephyrAlpha\scripts\governance\data_supply\__init__.py
cwd(w3)    resolve(同一相对串)                                   = D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w3\scripts\governance\data_supply\__init__.py
cwd(w3)    resolve(该文件的 w3 绝对路径)                          = D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w3\scripts\governance\data_supply\__init__.py
exists in w3 (测量瞬时): False      ← 文件不存在时 resolve 仍原样返回（strict=False），不发生根翻转
```

⇒ 指令卡假设的"cwd 致偏"**只在 target 传相对路径时成立**；落地侧 L2297/L2301 传的都是绝对 worktree 路径，
故 **held 与 target 的解析根相同**，"永不相等"前提证伪。

③ **held 实际前缀**（`.runtime/session_registry.json`，02:01 与 02:05 两次读数，同 sid）：

```
02:01  st-final-build-20260926  pid=0  held=26  前缀 .runtime\commit_queue\worktrees\w2 ×19 ／ \w0 ×7
02:05  st-final-build-20260926  pid=0  held=7   前缀 \w0 ×7            ← 19 条 w2 路径 4 分钟内消失
```

⇒ 三条硬事实：(i) **落地侧确实把 serializer worktree 绝对路径写进 held_files**（不是主区根，也不是车道 `.aidrafts\…`）；
(ii) 同一 session_id 的多个池工路径**混写进同一行 held_files**（w0 与 w2 同表项并存）；
(iii) **在途 claim 会被整批抹掉**（02:01→02:05 实测 26→7；本会话此后仍在 processing 0017＝w0 的 7 条）。
抹除者身份未定证 ⚑（候选见 E①）。

④ 相对路径的 cwd 依赖是**真实现象但不是本案病根**——它正是本包复算脚本自身踩到的：
`os.chdir(w3)` 后 `.runtime/session_registry.json` 相对读失败 `FileNotFoundError`（实测报错原文），改绝对路径后成功。

---

## C. 成功样本 ↔ 本会话 dead 袋 字段比对

### ① 样本集（全部只读 JSON）

| 类别 | qid | 结论字段 |
|---|---|---|
| 同会话成功 | `q-20260926-st-final-build-20260926-0001`（n=11） | 20:38:57→**20:40:57 landed**（landed_id 3eeb935743…，dev 可见） |
| 他会话车道→成功 | `q-20260926-st-chief3b-20260926-0005`(n=2) / `-0006`(n=1) | 00:33:06 / 00:11:46 landed（6813b000d6、82fa353669） |
| 他会话车道→成功 | `q-20260926-st-zmaster2-20260926-0008`(n=1) | 23:06:35 landed（noop@4d09c5b155…，幂等空转也算成功出口） |
| 他会话车道→成功 | `q-20260927-st-zmaster2-20260926-0015`(n=35) | 01:15:15→01:40:42 landed（d2507ecb80…） |
| 他会话批量全成 | `st-zmaster-20260926-0001..0008`(n=18/2/20/1/7/26/25/1) | **8/8 done**，15:27→18:08 |
| 本会话 dead | `-0002..-0010` | 死于 **COMMIT_FAILED**（非 CLAIM），每袋间隔 ~5-10min |
| 本会话 dead | `-0011`(n=18) / `-0012`(n=19) / `-0014`(n=8) | 死于 **CLAIM_REQUIRED**；另 `-0013` 死于 `git reset` 异常、`-0015` 死于 CREATE-GUARD |

### ② 字段逐列比对（done vs dead，同会话也同表）

```
done  键集 = ['base_head','branch','created_at','files','landed_at','landed_id','message','meta','qid','session_id']
dead  键集 = done 键集 ∪ ['dead_at','dead_reason'] ∪ ['owner_session','prescription'] ∪ (可选 ['attempts','last_failure','last_retry_at'])
files 形态：两类完全一致 = list[dict(path=<仓内相对 POSIX>, blob_sha256, blob_ref=blobs/<sha>.bin)]
meta   形态：两类完全一致 = {"depends_on":[],"supersedes":[],"interactive":"true","lane":"interactive"}（dead 另带 env_retry/compacted_partial/compacted_at）
flags / allow_overlap / allow_non_worktree / skip_gates / claim 相关元数据：两类 **均不存在于袋 JSON**（实测键枚举）
```

⇒ **入袋侧输入面零差异**（同 sid、同 base_head `ffc3ce5f49`、同 files 形态、同 lane）。
`owner_session`/`prescription`/`dead_at` 是死亡工件字段，不构成因。

### ③ 唯一系统性差异（实测）＝**在途并发形状 ＋ 会话判活方式**，不是路径、不是字段、不是内容

```
会话           pid 判活      成功段在途形状                CLAIM 死
st-zmaster     未留存        8 袋严格串行（前一袋 ended 后才 created）   0
st-zmaster2    未留存        0001/0002/0005/0006/0007/0008/0015 串行   0（另有 0003 COMMIT_FAILED / 0004,0009,0012 cascade/COMMIT）
st-chief3b     pid=33160     最多 2 袋重叠，n=1/2/8                     0（0001,0003,0004,0008 COMMIT_FAILED；0007 cascade_stale）
st-final-build pid=0         0011/0012/0013/0014 **4 袋重叠 23:54→01:35**，
                             被 w1 与 w3 两池工分别捞走            → 3 袋 CLAIM_REQUIRED，且 unclaimed = 该袋 100% 文件
```

同会话内两池工并发命中（w1/w3 各自 worktree 本地审计 `commit_block_events.jsonl` 原文时间戳，UTC）：

```
w1  2026-09-26T16:15:30Z  CLAIM-REQUIRED  files_count=18   ← 本会话 0011（dead_at 00:15:31 本地＝同刻）
w3  2026-09-26T16:20:38Z  CLAIM-REQUIRED  files_count=19   ← 本会话 0012（00:20:38）
w1  2026-09-26T17:34:56Z  CLAIM-REQUIRED  files_count=8    ← 本会话 0014（01:34:56）
```

### ④ 该门对"worktree 袋"不是必然死（base rate 实测，直接证伪指令卡推论）

```
池工 worktree 自有审计行数（全史）： w0 287 行 / CLAIM 3 ； w1 274 / 6 ； w2 378 / 2 ； w3 156 / 2
⇒ 4 工合计 1095 条 gate 阻断行中 CLAIM-REQUIRED 仅 13 条（1.2%），
  而同期从各自 worktree 投的袋成功落地数以十计（含 35 件大袋）。
主区审计 .runtime/audit/commit_block_events.jsonl 的 58 条 CLAIM 行 detail 全为主区路径（0 条含 worktrees）
⇒ 落地侧阻断写进"该池工 worktree 自己的 .runtime"（gateway.project_root＝worktree，见 A3 L1199），主目只收直连提交。
gate 链时长实测（同文件 gate_chain_ms）：17.4s ~ 179.0s（直连），池工袋整段在途 5~78 分钟（0014 created→dead=78min）
```

---

## D. 可抄配方：从 session worktree 投袋 → 能落地

> 每条断言标【实测】（本包命令＋读数）或 ⚑unverified（机制推断／配方来源）。

**D0 认知前提（省 5 封 dead）**
落地侧**自己铸 claim**（`commit_queue_landing.py:2298`【实测读码】），入袋侧**不需要也不应该**为落地铸 claim；
`git_commit.py --enqueue` 的预检**本就跳过 CLAIM-REQUIRED**（L852【实测读码】）。⇒ 你**无法**用 `--allow-overlap`
救这类死（落地 commit 不传该参数【实测 A3 L2326-2347】），袋 JSON 也**没有** skip-gates 字段【实测 C②】。

**D1 投袋前——基底必须与 dev 实况同一枚（防 cascade_stale 死）**

```bash
git -C "D:/ZephyrAlpha" rev-parse dev           # 只读：取入袋 base_head 用（commit_queue.py:3006 注释"A 段显式传入"）
git -C "D:/ZephyrAlpha" status --short | head    # 只读：主区是否被别会话占坑
python "D:/ZephyrAlpha/scripts/commit_queue.py" status --session <sid> --no-bootstrap   # 只读语义（--no-bootstrap 不触发排空）
```
实测：`cascade_stale: 基底重校验不适用`  kills 了 chief3b-0007 / zmaster2-0004 / zmaster2-0009【C①③】；
机制真源 `commit_queue.py:1368-1409 _mark_cascade_stale`（同 base_head 的后续项互标 stale）【实测读码】。
⇒ **同一会话的多袋不要共用一枚 base_head 排在一起**；后一袋投前先 `rev-parse dev` 重取基底。

**D2 投袋（车道读字节，两条等价入口）**

```bash
# 入口 A（推荐，带预检）：--project-root 指车道，袋内 path 自动归一为车道相对 POSIX（git_commit.py:865-877【实测读码】）
python "D:/ZephyrAlpha/scripts/git_commit.py" --enqueue \
  --session <sid> --project-root "D:/ZephyrAlpha/.aidrafts/<sid>" \
  --files <相对路径逗号清单> --message-file <utf8 msg>
# 入口 B（低层等价）：commit_queue.py enqueue --worktree-root <车道绝对路径>
python "D:/ZephyrAlpha/scripts/commit_queue.py" enqueue --session <sid> \
  --worktree-root "D:/ZephyrAlpha/.aidrafts/<sid>" --files <相对> --message-file <msg> --base-head <D1 取到的 dev HEAD>
```
【实测】本会话 0001（入口 A 语义）与他会话 chief3b/zmaster/zmaster2 全部袋都走这两条入口之一，均成功过
⇒ **"从 worktree 投袋"本身不需要任何额外入袋字段**。哪个入口对应哪封袋在 JSON 里无留痕 ⚑unverified（键集已枚举，无来源字段）。

**D3 ★核心★ 同会话一袋一在途（本案唯一系统性差异 ⇒ 第一优先配方）**

```bash
# 投下一袋前必须等到本会话队列清空（pending+processing 均空）：
python "D:/ZephyrAlpha/scripts/commit_queue.py" status --session <sid> --no-bootstrap
# 判据：输出中本 sid 无 pending/processing 项，再投下一袋
```
【实测】`st-zmaster` 8/8 串行全 done；`st-zmaster2` 成功段严格串行；本会话 4 袋重叠 ⇒ 3 袋 CLAIM 死（C③）。
⚑unverified：并发是"必要条件"还是"充分条件"未逐袋定证（chief3b 有 2 袋小袋重叠仍成功）。
  → **已由 §F 前瞻对照升格为受控前后对照**（0017 单袋在途 ⇒ done；4 袋重叠 ⇒ 3 袋 CLAIM 死）。
⇒ 保守做法：**大袋（n≥8）绝不并投**；小袋（n≤3）重叠未见事故。

**D4 ★核心★ claim 存活窗口：别让会话条目被判死**

```bash
# 读自己会话条目的判活方式（pid=0 只靠 90s 心跳；pid>0 靠进程存活）：
python -c "import json;d=json.load(open(r'D:/ZephyrAlpha/.runtime/session_registry.json',encoding='utf-8'));print([(k,v['pid'],len(v.get('held_files') or [])) for k,v in d.items()])"
```
【实测】本会话条目 `pid=0`，`held` 由落地池工写入 worktree 绝对路径；02:01→02:05 之间 held 由 26 → 7（19 条被整批抹掉）。
【实测】`.ailocks/salvage_audit.jsonl` 09-26 **22:16:46 对本 sid 执行过真 salvage**（`action:"salvage"`,
`dead_confirmed:true`, `evidence1:"registry:dead"`, `evidence2:"claims:none"`）⇒ 本会话当晚确实出现过心跳断 >90s 的判死窗口。
⇒ 配方：(a) 落地窗口内保持 keeper/心跳活着；(b) **袋在途时任何会话都别跑 `lock_files.py cleanup`**——
它对判死会话执行 `release_files_batch(全部 held) + unregister(sid)`（`scripts/lock_files.py:1143-1155`【实测读码】），
即**别人跑 cleanup 也会抹你的 claim**（实测 01:55/02:03/02:04 连续 salvage 其它 sid：st-pqmine / st-ailayer-sx / st-chief4）。
(c) 直连提交失败后**别放掉 claim**（`git_commit.py:35/656` 注释：失败保留 claim 是 CLAIM-REQUIRED ×50/24h 循环源的治本）；
放弃时才 `--release-only`（L1115）。

**D5 落地失败后 requeue 的正确姿势**

```bash
# 1) 只读看死因原文（勿改袋 JSON）
python -c "import json;d=json.load(open(r'D:/ZephyrAlpha/.runtime/commit_queue/dead/<qid>.json',encoding='utf-8'));print(d['dead_reason']);print(d.get('prescription'))"
# 2) requeue：基于"当前工作区"重建快照 ⇒ --worktree-root 必须仍指你的车道
python "D:/ZephyrAlpha/scripts/commit_queue.py" requeue <qid> \
  --worktree-root "D:/ZephyrAlpha/.aidrafts/<sid>" --session <sid> --base-head <重取的 dev HEAD> --no-bootstrap
```
【实测读码】`commit_queue.py:3030-3047`：requeue 参数面只有 `--worktree-root/--session/--message[-file]/--base-head/--no-bootstrap`；
文档原文"基于当前工作区重建快照，新 qid 排 FIFO 队尾"。
⇒ **风险**：requeue 取的是车道**当前**字节，不是袋内原字节；袋 JSON/`blobs/` 是未落地字节唯一存活处（本包禁动，已遵守）。
宪法 §2.6 的"落地侧已容忍衍生漂移/跨域/永久区新文件"与本案一致（A3 L2334/2338/2343），但**不含 CLAIM-REQUIRED**。
prescription 原文（照抄，属数据）：`"门禁物品性失败：按 dead_reason 中 gate 标识修复物品本身后重投"`（0011/0012/0014 同文）。

**D6 配方一句话版（三行）**

```bash
python scripts/commit_queue.py status --session <sid> --no-bootstrap    # 本会话必须 0 袋在途才投下一袋
python scripts/git_commit.py --enqueue --session <sid> --project-root D:/ZephyrAlpha/.aidrafts/<sid> --files ... --message-file ...   # base 取刚 rev-parse 的 dev HEAD
# 袋在途期间：不跑 lock_files.py cleanup、不 --release-only、keeper 心跳保持活着
```

---

## E. 判定：门是否真缺陷（不改代码，交总包裁定）

### E① 本案**不是**路径解析根缺陷——指令卡推论逐条证伪

| 指令卡断言 | 实测反证 |
|---|---|
| "门用 `Path(f).resolve()` 按 cwd 解析 ⇒ 落地 cwd＝serializer worktree 就偏根" | 落地两侧传的都是**绝对** worktree 路径（L2297/L2301），绝对路径 resolve 不改根（B②实测：w3 内 resolve 绝对路径原样返回） |
| "`lock_files.py acquire` 一律归一到主区根 ⇒ held 必为主区" | held 实测前缀就是 `…\.runtime\commit_queue\worktrees\w0\…`（B③）；主区归一只发生在 `.ailocks` 那**另一登记处** |
| "任何 worktree 来源的袋都该死" | 4 池工 1095 条阻断行中 CLAIM 仅 13 条；st-zmaster 8/8、st-zmaster2 8 袋（含 n=35 大袋）从各自车道成功落地（C④①） |

### E② 真缺陷定位（**跨进程 claim 表行共享 ＋ 判死即清零**，属并发协议缺陷而非路径缺陷）

同一 `session_id` 在 SessionRegistry 里是**一行** `held_files`；而落地由 k 个短命池工进程为多袋并发铸/抹 claim，
存在三条"整批抹除"合法路径，且都无跨进程互斥（`_lock` 是 `threading.RLock`，`_save` 整表重写，L752-760 注释只处理 tmp 同名）：

1. `session_concurrency.py:571-591` `_ensure_registered_locked` —— 条目判死即 `held_files=[]` 重建 ⇒ 抹掉其它池工刚铸的在途 claim；
2. `session_concurrency.py:674-717`+`L752` —— 跨进程 read-modify-write 丢更新（两工各自 load→append→save，后写覆盖前写）；
3. `scripts/lock_files.py:1143-1155` —— salvage `release_files_batch(全部 held)`＋`unregister(sid)`（**本案当晚已实测触发**，B④/C③）。

触发面被"gate 链时长"放大：claim 与 gate 判定之间隔着 `_apply_snapshot`＋`_prestage`＋数百秒～数十分钟 gate 链（A3 L2266/L2296/L2326）。
红证脚本 `claim_gate_repro.py` 只做**只读复算**：证明 (i) held 与 target 根一致（路径缺陷说立不住），
(ii) 一旦表项被"判死重建"或"注销"，则该袋 **100% 文件**报 unclaimed（与 0011/0012/0014 观测形状完全吻合）。

### E③ 建议修法（交总包裁定，本包不施）

| 方案 | 做法 | 影响面 | 风险 |
|---|---|---|---|
| 甲（最小、优先） | 落地铸 claim 改用 **item 专属子键**（如 `session_id` 不变但 claim 记录带 `qid`，或铸成 `queue-<qid>` 逻辑会话并把 `queue_marker` 的 sid 贯通到 gate kwargs）——袋之间不再共享同一行 held_files | `claim_required_gate`/`held_overlap_gate`/`_foreign_held_locked`/`import_integrity_gate` Phase2.5/`reconcile_worker` 三证（均经 `get_session`/`other_held_files`） | 跨会话防撞语义要重算：池工专属条目会被 HELD-OVERLAP 视为"另一会话"，可能反手制造 overlap 阻断；M3.2 的"审计按 sid 寻址"契约（landing L2209-2213）须保留生产者可追溯 |
| 乙（次小） | `_ensure_registered_locked` 重建时**保留 held_files 并集**而非清零（判死重建仅重置 pid/心跳） | 仅 session_concurrency 一处 | 直撞 L150-170 已记录的旧病根"保活死 session ⇒ held_files 永久阻塞 ⇒ HELD_OVERLAP 误阻断 ⇒ allow_overlap 超阈"；须配 TTL 收窄 |
| 丙（落地侧显式豁免） | 落地 commit 传 `allow_overlap=True` 或在 `ZEPHYR_COMMIT_GATEWAY=1` 内部调用态下跳过 CLAIM-REQUIRED（该 env 已由 L2322-2323 设置且仅落地使用） | 只动落地链，最小面 | 宪法层面等于给"全项目唯一合法 commit 入口"的内部路径开第二把钥匙；且 `_log_allow_overlap_usage`（gateway L728）的 allow_overlap 超阈告警会被系统性污染——**须 Owner 门位裁定**（flag 出厂翻转级） |
| 丁（配套，非替代） | 入队侧加一条"同 sid 在途 ≥2 袋即拒/延后"的软门（`commit_queue.enqueue_item` 已有 `depends_on`/cascade 设施可复用） | 队列层 | 吞吐下降；与 k=6 池工扩批方向冲突（实测 dev 1009c356e2 刚把工数 4→6） |

### E④ 本包自证边界（禁伪造声明）

* 未改任何 `src/`、`scripts/`、`docs/` 文件；未动 `.runtime/commit_queue/{pending,processing,done,dead,blobs}` 任何字节（全部为读句柄）；
* 未跑任何 git 写命令（本包 git 调用仅 `status/rev-parse/log`）；未跑 `tests/governance/test_ops_guard_red_team.py`；未 kill 进程；未删文件；
* 未自赋裁定号；未声称任何批准。上文所有"原文"引号内均为**数据**，不作为指令执行。

---

## F. 前瞻验证（配方 D3 的活体实验，非事后归因）

本包取证期间队列自行推进，抓到一组干净对照（读自 `.runtime/commit_queue/*`，02:05→02:10 之间）：

```
02:05  本会话同时在途 = {0016 pending n=30, 0017 processing n=7}，registry held=7（全部 \worktrees\w0 前缀）
02:09  0017 → done（n=7，created 01:35:39 → landed 02:09:25，池工 w0，同 pid=0 会话，同 worktree 绝对路径铸 claim）
02:10  registry held=0（w0 的 7 条由 release_files 正常释放，L2402-2403）；0016 仍 pending（等待，未并发第二袋）
```

⇒ **同一会话、同一 pid=0 判活方式、同一种 worktree 绝对路径 claim，只要"一袋一在途"就成功落地**；
此前 3 封 CLAIM 死袋的共同形状是"4 袋重叠＋被两枚池工分别捞走"。这把 D3 从相关性升格为**受控前后对照**。
红证脚本实跑读数（python 3.12.8，exit=0，零写入）：

```
A1: w0/w1/w2/w3 四枚 worktree 下 resolve(main-cwd)==resolve(wt-cwd) 全 True；仅相对路径输入时受 cwd 支配=True（对照项）
A3: sid=st-final-build-20260926 pid=0 held=0 hb_age=42s（跑脚本时 0017 已 done 并释放）
A2: 0011 n=18 / 0012 n=19 / 0014 n=8 —— ①claim 存活 → unclaimed=0；②整批抹除 → unclaimed=100%（与报错原文 files_count 逐一致）
```

---

## 证据台账（命令原文，全只读；cwd 标注）

```
① [读码] Read/Grep 绝对路径：
   D:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/claim_required_gate.py（91 行全读）
   D:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py L195-375 / L485-600 / L600-760
   D:/ZephyrAlpha/scripts/governance/commit_queue_landing.py L1180-1250 / L2150-2410 / L3349-3362 + grep claim|allow_overlap|chdir
   D:/ZephyrAlpha/scripts/git_commit.py L834-883 + grep -n "extra_skip|_enqueue_mode|CLAIM-REQUIRED|allow_overlap|enqueue"
   D:/ZephyrAlpha/scripts/commit_queue.py L2990-3058（CLI 面）+ L1368-1409（cascade_stale）
   D:/ZephyrAlpha/scripts/lock_files.py L1100-1174（_force_release_session_registry / salvage 主入口）
   wc -l 读数：91 / 902 / 3478 / 3066 / 1332
② [B resolve] cwd=D:/ZephyrAlpha → os.chdir(.runtime/commit_queue/worktrees/w3) 后 python 纯计算 resolve（读数见 B②）
③ [B held 前缀] python -c 读 D:/ZephyrAlpha/.runtime/session_registry.json（02:01 held=26 [w2×19,w0×7]；02:05 held=7 [w0×7]；pid=0，hb_age 8.2s/27.1s）
④ [C 袋字段] python 读 .runtime/commit_queue/{done,dead}/q-2026092[67]-st-{final-build,chief3b,zmaster,zmaster2}*.json
   （键枚举、files 形态、meta、base_head、dead_reason、prescription 原文）
⑤ [C 比对] 0014 的 unclaimed 集合 vs 袋内 path 集合：8/8 全中（strip 'worktrees\wN\' 后逐条比对）
⑥ [C base rate] python 读 .runtime/commit_queue/worktrees/w{0,1,2,3}/.runtime/audit/commit_block_events.jsonl
   （行数 287/274/378/156，CLAIM 行数 3/6/2/2，含 w1 16:15:30Z n=18、w3 16:20:38Z n=19、w1 17:34:56Z n=8）
   另主区 .runtime/audit/commit_block_events.jsonl（2222 行，58 条 CLAIM 全主区路径，0 条含 worktrees）
⑦ [缺口] 今晚池工 stdout/drain 日志未落盘：grep -rls "q-20260927-st-final-build-20260926-0014" .runtime/logs → 0 命中；
   .runtime/logs/belt_daemon_csx.log 末次写于 09-24 23:15（其中同型 CLAIM 死 st-mapbuild-20260924 与
   "claim_file auto-registering session=… (not registered or dead/expired)" WARNING 并存，为机制旁证，非当晚直证）
⑧ [E 触发面] python 读 .ailocks/salvage_audit.jsonl 尾（762 行；本 sid 4 行：
   09-26 22:16:46 action=salvage dead_confirmed=true evidence1=registry:dead；
   09-27 01:46:12 / 01:55:22 / 02:04:54 action=salvage-skip evidence1=registry:alive evidence2=claims:0/7 expired）
⑨ [git 只读] git -C D:/ZephyrAlpha rev-parse --abbrev-ref HEAD（dev）；git log --oneline -15（done 袋 landed_id 对账）
```
