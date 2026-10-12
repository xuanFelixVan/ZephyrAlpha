---
ttl: task_bound
completes_when: W-1 序列化器工作树 transient 面被清到与 dev 可比对（判据见 §4）＋W-2 TEST-SOURCE-CONSISTENCY 的 own_scope 由册主车道定性入账；两件各有落地读回证据
---

# 工单——落地面污染与内容型门的扫描面定性（统筹裁定②授权转维护三班／册主车道）

> 出单：统计合法性班 st-statsgov-20261012（判据 owner，2026-10-12 夜）。
> 接单：**维护三班**（W-1，落地链与序列化器工作树）＋**册主车道**（W-2，门注册面与 own_scope 机生重打）。
> 本班边界：**不动那道门、不改他班文件、不加白名单、不弱化判据**——按 Owner 在册固定正解，
> 已批之闸误杀合法路径时改的是"**喂给闸的输入指向**"，本单两件都属输入面/装载面，不属判据面。

## 1. 事实（全部本班亲手取证，命令随件附）

签名：`门禁 TEST-SOURCE-CONSISTENCY 阻断 … tests/pf_alloc/test_allocation_team_wiring.py:41 …
符号 REGIME_TO_SEGMENT / SOURCE_NOT_IN_TEAM 在源码 allocation_inputs.py 中未定义`
——**报的文件不是本班的**，本班袋内只有 `docs/_working/statsgov_campaign/` 下 7 个 .md/.yaml。

| # | 取证 | 结果 | 复核命令 |
|---|---|---|---|
| ① | 该件是否在 dev | **不在** | `git cat-file -e dev:tests/pf_alloc/test_allocation_team_wiring.py` ⇒ 非零 |
| ② | 主区工作树是否有此件（含未跟踪） | **无**，目录只剩编译残留 | `git status --porcelain tests/pf_alloc/`（空）；`ls tests/pf_alloc/`（只有 `__pycache__`） |
| ③ | 全 git 历史是否出现过该路径 | **从未**（增删日志皆空） | `git log --all --oneline --diff-filter=AD -- tests/pf_alloc/test_allocation_team_wiring.py` |
| ④ | 谁携带过这个路径 | 只见于 **st-combine-20260923 的 10＋ 枚旧死袋**（队列 blob 第四态），活跃队列（pending/processing）无一携带 | `grep -l test_allocation_team_wiring .runtime/commit_queue/*/q-*.json` |
| ⑤ | 两次落地读到的**行号不同** | 0009 报 `:41`（2 个符号）；0010 报 `:54 / :87 / :232`（3 处） | 读两袋 `dead_reason` |
| ⑥ | 序列化器工作树现况 | `tests/pf_alloc/` 下只剩 `__pycache__`，.py 已不在 | `ls .runtime/commit_queue/worktree/tests/pf_alloc/` |

⇒ **定性（据①–⑥）**：落地瞬间序列化器工作树里存在过一份该件的历史字节，之后消失；两份读到的字节还不同版本。
这不是内容冲突，而是**落地输入面（工作树）与 dev 不同源／残留 transient 面**，
使内容扫描型门读到"当前 dev 里根本不存在的文件"，从而拦住与本件无关的提交人。
连带后果：本班 **0009／0010／0011 三袋连死**，其中 0011 已换成 ghost_session 死法（§3）。

## 2. W-1 请维护三班办：序列化器工作树的输入面

| 项 | 内容 |
|---|---|
| 对象 | 队列 serializer 工作树（`.runtime/commit_queue/worktree`，分支 `serializer/commit-queue`，另有 `serializer/commit-queue-w1/w2` 两台并发） |
| 症状 | 树内出现"dev 无、历史无、活跃袋也不携带"的 .py 残留（本例 `tests/pf_alloc/…`），导致 `TEST-SOURCE-CONSISTENCY` 一类门读到幽灵文件 |
| 请做的判据动作 | 核该工作树的**装配来源**：是哪一步把非 dev、非袋内的字节放了进去（旧袋 blob 展开？失败袋回滚不彻底？多工位共用一棵树？）。**先定源再清面**，别只删不看来源——来源不清就会复发 |
| 不许做 | 不在未定源前对该树做整树级破坏性清理；不动 `locked` 状态（该树带 lock）；不代 requeue 他班死袋 |
| 完成证据 | 用 §1 的①–⑥ 复跑一遍：`ls .runtime/commit_queue/worktree/tests/pf_alloc/` 无 .py，且本班同类文档袋能一次过门 |

## 3. W-1b 顺带一条同家问题：存活闸把活会话判成幽灵（本班已自救，但根因未定源）

0011 死因 `ghost_session: 属主会话已死（heartbeat=exited / 注册表无在册）`——**而本班当时正在跑**。
实测三面对得上：`.runtime/session_registry/st-statsgov-20261012.json` 在 22:05 **消失**；
心跳文件最后一行 `{"ts":"2026-10-12T14:05:32+00:00","status":"exited","reason":"session not in registry"}`；
而 `keepalive.jsonl` 里本班两次 `grant`（ttl=7200）都在。**保活批了，注册条目却先没了** ⇒ 守护因"session not in registry"自退。
请一并定源：**谁在 22:05 回收了在册条目**（`lock_files.py cleanup` / 注册表 TTL 回收 / 启动清扫 / 他会话 GC）。
本班按在册正门自救四步已完成：`register(sid, pid=0)` → 起 detached `heartbeat_daemon <sid> <root> 30 <wt>`
（模块入口 `python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon`，`scripts/heartbeat_daemon.py` 不存在，勿照旧配方找脚本）
→ `register_heartbeat_keepalive` 复批 → 用**门自己的尺**判活（`list_active_readonly` 命中＋hb_age≤90s）。
⚑ 一条通用坑给队列侧参考：`mark_logical` 会被 `MARK_LOGICAL_DENIED` 拒（W-29 形态核验），长班续命唯一正门是 keepalive 具名授权。

### 3.1 本案取证补强：物理回收**零审计行** ＋ 同案锚点与时刻差（00:1x 复测）

同案锚（Owner 2026-10-13 零点给锚，出处＝**项目记忆面**非仓内文档面：
`projects/D--ZephyrAlpha/memory/mutating-death-check-batch-reaps-foreign-shards.md`）：
`scripts/session_worktree.py archive`（在册车道退场正门）的死判内部调 `SessionRegistry.list_active()`＝**mutating**——
判死即写接管台账，并对心跳超宽限（900s）的分片做**物理收割**。在案实证：2026-10-12 终清波四 M2 退 10 棵死车道，
21:35 实测"13 片全未过 TTL ⇒ 该通道此刻零接管写入、零收割"，真正执行在 22:20（隔 45 分钟），
执行窗内 **8 个会话分片被收割（含该班自己 `st-fclean4`）**，后果＝树与字节零损失、**接管台账未新增**、
车道条目一度消失。与本案形态逐条同构。

| # | 面（本班 00:1x 亲手复测） | 读数 |
|---|---|---|
| 1 | 心跳 | 末行 `alive` 到 22:03:11；22:05:32 变 `exited, reason="session not in registry"` ⇒ 条目在 22:04–22:05 之间消失 |
| 2 | 接管台账 | `.runtime/takeover_ledger.jsonl` 总 173 行，**21:45–22:30 窗内新增 0 行**（按 `ts_epoch` 过滤，不按 `ts` 字符串猜） |
| 3 | 清扫日志 | `sweep_log.jsonl` 总 10 行、`sweep_attribution_log.jsonl` 总 4 行 ⇒ **窗内皆 0** |
| 4 | 退场账 | `.runtime/retired_lanes/` 仅 `20260927` 一项，窗内 mtime 命中 0 个；无任何条目点名 `statsgov` |
| 5 | 归档观察册 | `.runtime/archive_watchlist.json`（1,342B）**无 statsgov 条目** |
| 6 | 字节面 | 车道树与文件全在（两个 .py 的 sha 已录 91 号件），**只有注册分片没了** ⇒ 与在案"零损失、条目消失"同型 |

⇒ 请维护三班定性两件事（本班不代修、不改判据）：

- **(a) 时刻差**：本案 22:05 vs 在案 22:20。若 M2 是多批逐棵执行，22:05 可能是更早一批；
  但**现有任何审计面都无法证实也无法证伪**——这本身就是 W-1b 的落点：物理收割不落一行账。
- **(b) 第二条候选机制**：本案 22:05 恰在本班自己两次短命 CLI（约 22:03 的 `gate_dry_run` 与 `git_commit --enqueue`）
  之后 2 分钟内。在册已记该机制：短命 CLI 每次跑都带**自己的 pid** 触碰注册表，进程一退即被判 `pid dead`
  （项目记忆 `lane-claim-relative-path-silently-zero` 第 1 条）。两条候选指向同一条处方。

**判据级请求（不要改判据，只要可观测面）**：凡"回收/除名注册分片"的动作，落一行可归因审计
（对象 sid＋判定输入＝心跳年龄与 pid＋动作＋来源通道）写进 `takeover_ledger.jsonl` 或 `sweep_log.jsonl` 任一面。
**落地判据**＝下一次同类回收能按 `ts_epoch` 在任一面查到一行。
现况下各班只能靠心跳文件时间戳反推，而该反推面留存只有几天（同族可观测性缺陷见 §7）。

## 4. W-2 请册主车道办：`TEST-SOURCE-CONSISTENCY` 的扫描面定性

| 项 | 内容 |
|---|---|
| 判据依据 | 根宪法 §3.1：内容扫描型 gate 默认 **own-diff 作用域**；外来 staged 违规 = warn＋审计（`_audit_foreign_staged`），**不阻断无辜提交人**。§3.4：他会话在途违规不代修 |
| 要办的事 | 核实该门在 `gate_registry.yaml` 的 `own_scope` 装载值与它实际读的扫描面是否一致；若它读全仓/工作树残留面而非本次 diff，则按 §3.3 要么改 own-scope，要么正式登记"全仓扫描"理由 |
| 硬约束 | `own_scope` 字段**机生勿手改**——须走 registrar/生成器重打；本单只提问题与判据，不代改 |
| 完成判据（可执行） | 造一个用例：某袋只含文档件，而工作树/他会话面存在一处符号漂移 ⇒ 该门应 **warn＋审计放行**，不是硬拦。用例过＝W-2 完成 |
| 为什么归册主 | 门的装载与分级是门机械面，非本班判据面；本班自改＝越权且会洗掉可见性 |

## 5. 影响面（为什么要现在办）

- 本班：0009（TEST-SOURCE-CONSISTENCY）／0010（同）／0011（ghost_session）三袋连死，
  批复①的收班条件"dev 显 E=399"因此迟迟未成就——E=399 是**自纠后的正确读数**，旧值 194 在 dev 上会误导预算册。
- 面不止本班：同一路径在 st-combine-20260923 的 10＋ 枚旧死袋里出现过；
  在册另有条目把"三方冲突簇"与"60s 提交超时簇"记为同家问题（见记忆 `lane-base-head-three-way-conflict-20261012`、
  `git-commit-60s-timeout-recurrence-fuse-20261012`）——本单的 W-1/W-1b 与它们同属"**落地输入面与 dev 不同源**"一家。
- 队列现况（本班 23:4x 实测）：pending 约 11、队首等待 3,100s＋，串行落地慢 ⇒
  每死一袋的代价是整轮重投＋他人排队，**定源比补投便宜**。

## 6. 本班侧已做的三件防复发（供接手人照抄，非请办项）

1. **重投基底钉 dev**：`commit_queue.py enqueue … --base-head $(git rev-parse dev) --no-bootstrap`，
   在**车道 cwd 跑主区脚本**（队列根锚脚本位置）；投前用 `git cat-file -e <base>:<path>` 与 `git cat-file -e dev:<path>`
   两面一跑，`N 且 Y`＝基底缺文件（须钉基底），`Y 且 Y` 才是真内容打架。
2. **入队前跑真钩子**（本本班前两次漏掉的一步）：在车道 `git add` 本袋件后跑 pre-commit 真钩子链，
   别只跑 in-process 预检——两面的钩子集合不同。
3. **多重集不丢行自检**：按当下 dev 逐件做行级 Counter 对拍，"仅 dev"必须逐条可归因为**本班自己被替换的旧字节**，
   并把这个结论写进袋内讯息（`[pool-regression-ack:…]`），不留"我看着像超集"。

## 7. 随单提出的一条可观测性诉求（两处同型，均不改判据）

| 现象 | 实测 | 诉求 |
|---|---|---|
| `gate-zr-zero-residue` 失败**零明细** | 车道暂存面手工跑真钩子：`Failed / - hook id: gate-zr-zero-residue / - exit code: 1`，**不打印任何违规行**；而同一扫描器直接调用可复现出 23 条 error 级条目（3 枚 10-02/10-11 的 `.tmp` 残留＋12 处已入库他班件的路径双重嵌套＋1 枚自身超时） | 失败时输出违规清单（或至少"条数＋前 N 条路径"），否则提交人只能自己再跑一遍扫描器才知道被什么拦住 |
| 注册分片物理回收**零审计行** | §3.1 六面：台账窗内 0 新增、两台清扫日志窗内 0、退场账与观察册无点名 | §3.1 判据级请求：动作落一行可归因审计 |

两者同族＝**"发生了什么"不可从系统面读出**，只能靠反推；反推面（心跳文件／扫描器手跑）留存短、且需要提交人自己会跑。
本单只提可观测面，不提豁免、不提降级、不提白名单。

