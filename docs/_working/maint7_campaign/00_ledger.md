---
ttl: task_bound
---
# 维护七班班账（st-maint7-20261014）

承接维护六班未竟＋统筹三枚新缺口＋今晚两轮增补（P2 扩面/新查项、事故专项两条）。
本账口径＝实测计数与文件字节，非自报；每条结论后附复核命令。

## 一、P0-1 甲案：perm_trigger 补 m10 逐件声明解析（已施工，落地状态见 §一.4）

数据班 st-datalane2-20261012 §四十一 实证缺口：同一聚合门下 m11 有逐件声明通道、m10 不解析，
而 m10 标记生态已用 70+ 处（grep 实测 src/ 面 71 行命中）。真源在册面复核：
`noqa_exempt_registry.yaml` 的 m10-time-trigger 条目 scope=per-file／reason_required=true／
reason_min_length=10 —— **写法既有、门不认**，属"门的输入识别"缺口，非新豁免。

施工（四件＋测试三件，均复用既有单点，零新门零新册）：
1. `perm_trigger_gate.py`：`_has_m10_exemption`（照 m11 模板：门 id 精确匹配＋同行 2+ 空格＋
   reason≥10 字），new 与 modified 两路同口径；`[INVARIANTS]` 与 docstring 治本方案同袋更新。
2. `_diff_helpers._make_noqa_pattern` 单点治本（施工中新挖到的缺陷，当班修）：分隔符原用
   空白类通配，**该类通配含换行**——全文 finditer 的消费方会把"只有码、同行无理由"的畸形
   声明的下一行代码借成 reason ⇒ 通配豁免真实开孔处。实测三例：
   `码后无理由(同行结束)` 命中且 group=`next_line_code()`；`码后只有空格` 命中且 group=`y = 2`。
   修法＝分隔符限水平空白。行级消费方（`_extract_noqa_lines` 逐行 search）本就无此通道，零影响。
3. `manual_only_permanent_gate.py`／`syntax_validation_gate.py`：两处内联同形正则收编到共享
   单点（§4.2 同真源可派生→必并），继承上述修复。资产面净减 2 副本。

### 一.1 验收面＝数据班在册探针原文（不自写判据）
修前基线（主区未修面，`probe_perm_trigger_fix_acceptance.py` 直跑）：拦／拦／拦，RC=1。
修后（车道码面，探针原文经"清 zephyr.* 缓存＋摘 DistutilsMetaFinder＋车道 src 置首"绑定，
驱动打印实际命中文件）：拦（无声明）／拦（畸形声明）／放（合规声明），RC=0，
"是 ⇒ 可复投六件套"。跑探针不经管道、退出码直取（在册坑：管道后 $? 量的是 tail）。

### 一.2 判别力自证（同采集面红绿对）
163 passed（perm_trigger＋diff_helpers＋m11 noqa＋syntax_validation 四件）；
突变自证＝把 `_make_noqa_pattern` 还原旧形态后 **6 failed / 140 passed**（m10 借道面、
helper 两条、m11 两条各自咬红），复原后全绿、四件字节哈希与备份全等。
爆破面＝commit_gates 全目录 2614 passed／15 failed，且 15 条红在**纯 HEAD 面**（临时还原
4 件后同面复跑）逐条复现 ⇒ 属 HEAD 级既有红，非本班引入（归因不靠"看起来无关"）。
ruff check＋format 七件净。

### 一.3 验证面一条环境事实（影响一切"车道内跑门码"的结论）
`REPO_ROOT` 由模块自身位置推导；解释器启动时 usercustomize 已预热 206 个 zephyr.* 模块，
且 `DistutilsMetaFinder` 把包名 zephyr 硬绑主区 src（finder 先于 sys.path）。故车道内
直接跑 pytest/探针量的仍是**主区码**（在册坑"worktree 裸 python 导主区包＝假绿"实测复现：
本班第一轮"修后跑探针"给出的畸形声明=放，正是量了未修面的假信号）。本班改法＝清 zephyr.*
缓存＋摘该 finder＋车道 src 置首，并让驱动打印实际命中文件；PG 相关用例一律打桩（零真连），
真源面另用主区为根进程回放取证。

### 一.4 袋账与知会锚（落地与否只认 git log，不认本账自报）
- 首袋 `q-20261014-st-maint7-20261014-0001`（7 件）落地死于 GATE-PRECOMMIT-RUN→GATE-TEST
  收集错误，归因见 §三（非本袋内容）。
- **甲是否已落地，唯一判据**（本账写成条件句，防自报绿）：
  `git show HEAD:src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py | grep -c _has_m10_exemption`
  ＝1 ⇒ 甲已落地（数据班可复投六件套）；＝0 ⇒ 仍在飞/待重投，本班不算交付完成。
  落地后 sha 取 `git log -1 --format=%H -- src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py`
  并回填本行末（本账提交时刻该值＝0，本班交回时甲在飞，见 §七.1 排队位次）。
- 数据班复投前置三句：① 声明格式＝`# noqa: m10-time-trigger  <理由≥10 字>`（两空格分隔，
  同行，禁独占一行——跨行不计数）；② 判据本体未变，时间触发＋无订阅仍违规；
  ③ 复核命令见 §一.1（跑在册探针，不经管道取 $?）。

## 二、P0-2 落地读面两处加固（＋统筹增补第 2 条扩面）

### 二.1 ① CREATE-GUARD 撕裂读改读稳定面
在册审计实证（`.runtime/audit/create_guard_parse_fail.jsonl` 全 42 条，10-13 一晚 3 条同形态，
15:13/15:15/15:18 UTC 同一行 66087）：粘连样如 `created_by: st-fingov-20260912- file: src/zephy`
＝外来非 CAS 直改热册的半写窗口。数据班 0019 袋即死于该瞬时态。
写侧根因不在本班可修面：投影器自身走 `safe_write_text`（CAS 原子），撕裂源＝非 CAS 直改
（根宪法 §1 第 13 条执法面），登记呈报不代修。
修法＝B1 三次重试耗尽后不直接 fail-closed，先读 HEAD git blob（不可变⇒无撕裂窗口）兜底；
成功则 logger.warning＋审计 `STABLE_SURFACE_RESCUED`；HEAD 面也不可得/仍坏才照旧 fail-closed
（消息同时给两面死因）。方向性不动：盘面仍是首选即时真源（裁定#480 手术③在册结论），
测试 `test_healthy_disk_never_touches_head_surface` 钉住"健康盘面零 run_git 调用"；
HEAD 兜底内容不回填磁盘 stat 键缓存。

### 二.2 ② creation-token 门读真源（方向与令卡所述相反、病根同一）
真数定位（比"PG 已登未投影"更窄的事实）：10-13 夜 **6 只死信全被同一条点名**——
`docs/_working/tdm_goal_structure_research_2026_10_13.md` 的 token。查 PG 真源＝
`status='retired'`；而当时 HEAD 的 capability 册 YAML 还挂着这条**退役残留**，
新重打的投影已按真源剔除 ⇒ `REGISTRY-YAML-PARSE` 的 A-12 守门拿"相对 HEAD 少 N 条"当基准
＝以滞后面为真源，把无辜袋连杀多轮。三面现值实测：HEAD YAML 15432／盘上 YAML 15432
（对称差 0，已自清）／PG 全行 15652＝active 15471＋retired 181。
修法＝差集逐条问 PG（REG-CAPCAN-001／family_key=creation_tokens／键 `file=<路径>|token=<值>`）：
真源 active 命中者照拦（判据本体不松）；查无/retired＝HEAD 残留 ⇒ 放行并落审计
`head_token_lag_pg_cleared`（带 cleared 与 still_blocking 两清单）；同 file 有 active 而精确键
未命中（键形漂移）⇒ 保守照拦；账本不可达/查询异常/非复合身份 ⇒ 全条照拦
（禁"读不到账本"变放行，与 create_guard T4 同哲学）。SQL 与 registry_id 复用既有单点，零新增真源。

测试与自证（车道绑定，18 passed；含 create_guard T4 既有 4 支共 22 passed）：
突变自证＝还原两支门件后 **6 failed / 12 passed**，复原后全绿、哈希与备份全等。
真实字节回放（主区为根进程＝落地同构，PG 真连非桩）：今晚拦袋那条真实身份 ⇒ 判放行；
正对照＝从 HEAD 取 8 条在册复合键 ⇒ 8/8 判 active 照拦（尺未钝）。

### 二.3 扩面：双向投影一致性巡检（统筹增补）
甲向＝PG 有行而 YAML 无行（滞后）实测现值 **39 条**；
乙向＝YAML 有行而 PG 无行/非 active（历史直写遗留）实测现值 **0 条**（今晚那一条自清后归零，
但直写通道还在就能再长出来；形态已被 6 只死信实证）。
交付＝`projection_generator.py` 加纯函数 `token_two_way_diff`＋`_warn_token_two_way_diff`，
在 run() 取到 rendered、self_check 后**说一次话**（此前只有门在拦的那一刻才说话）；
零阻塞（不改象限、不改写盘、异常全吞），不可比一律 comparable=False＋成因入 debug
（禁把"量不了"报成"零差异"）。测试 15 passed，含甲/乙各一发复现对照、同步面不误报、
不可比三形态、端到端（出声且 PG wins 写盘行为零变化）；
突变自证＝还原生成器后 **5 failed / 10 passed**，复原后 15 全绿、哈希与备份全等。

## 三、HEAD 级地雷拆雷（本班首袋死因，兼是过路袋公共拦点）

归因实测（非"看起来无关"）：本班袋内三只测试件单独收集＝**146 items / 0 error**；
整个 `tests/gov/governance/commit_gates/` 目录收集＝**2640 items / 1 error**，唯一 error＝
`test_strategy_card_lifecycle_map_gate.py` 的 ModuleNotFoundError，指向
`zephyr.gov_enforcement.commit_gates.map_family.strategy_card_lifecycle_map_gate`。
该台面件三面零命中且 `git log --diff-filter=D` 无删除记录＝**从未入册**（非被删），
只剩 `map_family/__pycache__/*.cpython-312.pyc` 一个陈旧编译物证明它曾在盘上
⇒ 测试随批入册、台面件从未入册的半程态。杀伤面不止自己：凡 staged 含该目录文件的袋，
落地钩子 GATE-TEST 目录级收集必 1 error 而被拦（在册死信族 GATE-PRECOMMIT-RUN 之一现场）。
处置＝模块级 skip 守卫：不删件、不改任何断言/阈值，只改"跑不跑"；台面件一入库
`find_spec` 命中即**自动失效**（写在注释与 `[INVARIANTS]` 面上，防后人当白名单用）；
依根宪法 §3.4 owner 责任制，本班不代投 STRATEGY-CARD 战役的台面件，只拆压在过路袋上的雷并呈报。
验证＝目录收集由 2640/1 error 变 **2640/0 error**；单件跑＝collected 0 items / 1 skipped；ruff 净。

## 四、事故专项（统筹 10-14 增补，只查不修）

### 四.1 杀伤窗半程态普查（00:45–01:00 全机 python 被 taskkill 误杀）
普查面＝`git worktree list` 全 61 个登记项＋`.ailocks` 在册 claim＋注册表活性，全只读。
1. **index.lock 残留＝0**（61 面全扫，无一枚）。
2. 半程态（AM/MM＝index 有字节而工作区又不同）非零面 12 处，最大两笔：
   主区 34 枚、`st-mineloop-20261010` 24 枚；其余 `w1` 4、`st-cband-20261012` 2、
   `st-gpux5` 2、`st-gpux-20261011` 2、`st-statsgov` 2、`st-bakdr` 3、`st-examrun` 3、
   `st-cdx-integ` 1、`st-datalane2` 1、`st-minedig2` 1。⇒ 这些是**内容门读 index 面**
   的陈旧字节风险位（在册坑同族），属主各自处置，本班不代修。
3. **worktree 注册指向已消失目录 1 处**：`D:/ZephyrAlpha/.aidrafts_pool/pool-20260919202729-c433`
   （branch=None）⇒ 需 `git worktree prune` 面处置，登记不代做。
4. `.ailocks` 在册 claim 22 枚，按属主：examchief 10、libstale 4、maint7 4、bakdr 3、
   **wkcure-chief 1（该 sid 已不在注册表）**⇒ 一枚无主 claim 待处置。

### 四.2 st-gpux6-20261013 ghost 判定对照（结论＝未漏网，实测在活）
`repair.json` 的 `repair_v2.others_daemons_healed`（00:58:29）13 个 sid **含 st-gpux6-20261013**
（也含本班 st-maint7-20261014）⇒ 复起名单未漏。01:00:40 判 ghost 的实测反证：
该会话注册表心跳龄 4.1s、`heartbeat.jsonl` 527 行末行 `status=alive`（写于 4s 前，
pid=33472）、`reincarnation_count=4`（重注册 4 次＝事故窗内被摘又复起的痕迹）、
`keepalive.jsonl` 末条＝grant（ttl 7200s，名目"GPU 六班链路在飞与入袋前活性锚维护"）。
⇒ 无需补守护。其死袋 0004 按统筹令留属主复活后自投，本班不代投。

## 五、P2+ 新查项：会话注册表口径一次定性（三处矛盾，实测非推断）

1. **"逻辑 session" 是两名一词**：
   - 描述义＝`pid=0` 注册形态（跨多个 `python -c` 进程，活性靠心跳新鲜度/TTL 代持）——
     见 `session_worktree.py` L1353/L2876/L6948 三处注释与 `coordination_state_board.py:133`；
   - 标记义＝`SessionRegistry.logical=True`＝W-29 的 **idle 自退豁免 opt-in**，只能由
     `mark_logical`/周期 re-register 置位。
   实测：`session_worktree_start` 的返回契约 `StartResult`（L162-180）**根本没有 `logical` 字段**
   ⇒ "回执称逻辑 session"不来自回执，而来自 pid=0 这一描述义；本班与 gpux6 两条注册条目
   均为 `pid=0 且 logical=False`。**结论＝保活不能靠"是 pid=0"，只能靠在册正门**
   （`register_heartbeat_keepalive` 写 grant，缺名目/缺请求方 ValueError 拒）。
   本班已按正门登记 grant（01:27 前后，ttl_seconds=1800，daemon_pid=41696）留痕。
2. **claim TTL 三处口径分叉**（打印面只报 acquire 时的值，不报被改写后的实际过期点）：
   - acquire 默认 `DEFAULT_TTL_S=1800`（打印"TTL: 30 分钟"）；
   - **提交失败保留** → `shorten_claim_ttl(..., FAILED_CLAIM_TTL_DEFAULT_S=300s)`
     并打 `retention="commit-failed-retained"` ⇒ 失败后 claim 实际只活 5 分钟；
   - **入队续命** → `renew_claim_ttl` 拨到 now+30min 并打 `renewed_at`；
   - 旧格式锁回退分支＝`timestamp + DEFAULT_TTL_S`（**忽略任何续期**）。
   实测现面：4 枚本班 claim 全带 `renewed_at`、剩余 114.2 分钟；`retention` 枚数＝0
   ⇒ 数据班两次实录的"9–10 分钟即 expired"对应"提交失败→300s 收窄"再叠加排队观测窗，
   或旧格式回退分支；二者都不是 acquire 打印的那个 30 分钟。
   ⇒ 定性＝**打印口径与实际过期点不同源**，属可观测性缺口（打印面未反映 expires_at 被改写）。
   本班只报不改（改打印面属会话/锁族判据面，需与 `--failed-claim-ttl` /env 口径同批定）。

## 六、P2 未办与承重证据（不空口留白）

统筹原令 P2＝存量接管条目"刷新出口"立法化＋P-9 设计面。本班完成**前置取证**，
判定立法本体不在本班可自裁格，理由三条（带数）：
1. `.runtime/takeover_ledger.jsonl` 192 条 **status 全为 open（192/192，0 条关账）**＝
   "刷新出口"确属缺位，但也说明出口判据一旦立错，192 条历史条目全要过一遍——
   属跨班判据面，非本班袋内可原子完成。
2. 立案理由分布实证"看一眼就立案"放大器存在：`last_activity idle` 形态里出现
   **0.3s／34.6s／98.9s／155.1s／157.8s／229.0s** 等远小于心跳超时 90s 边界的条目
   （另有 `orphan_resources: .aidraft…` 100 条）；并且
   `.runtime/session_registry_audit/takeover_self_block.jsonl` 19 次命中里
   `liveness_state=alive` —— 即 TAKEOVER-PENDING 咬过**活着的**会话（在册病根原话）。
3. 出口判据的"属主已回魂/分支已消失"两支需要不同归属处置：实测 open 条目 192 条中，
   属主此刻仍在注册表的仅 2 条（condaxis/infoaxis）；抽样可查分支的 1 条，其分支在立案后
   又有新提交（＝条目早已过时却仍 open）——其余属主分支已不存在，"关账"与"墓碑"两条路
   属治理资产净删面（根宪法 §5 墓碑制），需 Owner/统筹择一，不宜由本班代拍。
⇒ 建议落点与判据草案进本账 §五-2/§六.2 取证面，立法本体交统筹派工（含
`session_concurrency.py` 判据面＋`test_takeover_pid_false_positive.py`＋
`scripts/governance/session_takeover_ledger.py` 的 `death_evidence` 字段面同批）。

**P-9 定义缺口（如实报，不编）**：统筹令所指"P-9 设计面"在维护六班册只出现一次
（`docs/_working/maint6_campaign/00_ledger.md:245`）且无定义；全仓 `P-9` 命中 6 个文件，
分属 5 个不相干战役（gate-identity 修复册／disk_reorg／fms_overhaul／fullflow 两册／
fullflow_mining）。⇒ 需统筹指明是哪一册的 P-9，否则任何"设计面"都是我替 Owner 猜题。

## 七、并发与归属呈报（两条，需统筹处置）

1. **同一会话号并发第二实例**：`st-maint7-20261014` 同时存在两条车道——
   本实例 `.aidrafts/st-maint7-20261014`（分支 session/…）与
   **`.worktrees/st-maint7-20261014`（分支 ai/st-maint7-20261014/task-maint7-gate-symmetry）**。
   后者 00:59:53 投过一袋 P0-1（qid 0002，2 件，内联一份 m10 正则的窄版实现），
   读到我 0001 后**自行撤袋**并改做独立复核（袋内死因原文可查），随后 01:14/01:34/01:39
   又投了 0003/0006/0007（其中 0003 是 `tests/research/backtest/test_t3a_grid_s_wiring.py`
   ＝统筹令 P1 那条 Cartesian 挂死地雷）。⇒ 后果：① P1 已有属主在飞，本班按并发避让
   **不双写**、不动那条；② 同 sid 的 claim/心跳/入队归属互相污染（本班 00:52 首投被
   SESSION-REQUIRED 判"未注册"，实测注册表当时确实没有本 sid 条目，重注册后才回），
   这类"两名同 sid"应经统筹归一（改名或明确分工），否则 `git log -1 --name-only`
   归属核实这道防线会被同 sid 双车道洗掉。
2. 他班在途/陈旧面（本班只登记不代修）：`tests/gov/governance/commit_gates/` 目录另有
   15 条 HEAD 级既有红（map_family 血肉/trigger_facts 14 条＋`test_doc_header_suite_gate.py::
   test_roster_triggers_wired`），已在纯 HEAD 面同面复现，属各自属主。

## 八、复核命令（交付即可跑，逐条从本账正文抽出）

```bash
# P0-1 三形态验收（在册探针原文，不经管道取退出码）
python .runtime/tmp/st-datalane2-20261012/probe_perm_trigger_fix_acceptance.py; echo "RC=$?"
# 落地判定（只信 git log）
git log --oneline -1 -- src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py
git show HEAD:src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py | grep -c _has_m10_exemption
# 目录收集地雷是否真拆（应为 0 error）
python -m pytest --collect-only -q tests/gov/governance/commit_gates/ | tail -1
# 接管台账存量面
python -c "import json,collections;rows=[json.loads(l) for l in open('.runtime/takeover_ledger.jsonl',encoding='utf-8') if l.strip()];print(len(rows),collections.Counter(r.get('status') for r in rows))"
# 杀伤窗普查（可重跑）
python .runtime/tmp/st-maint7-20261014/survey_kill_window.py
# GATE-SELFDOC 上限实测（v2 走门侧真入口＋正对照）
python .runtime/tmp/st-maint7-20261014/measure_selfdoc_cap_v2.py
```
