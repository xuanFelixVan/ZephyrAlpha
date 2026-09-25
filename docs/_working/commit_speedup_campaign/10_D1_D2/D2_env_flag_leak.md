---
ttl: task_bound
---

# D2 手术单 — 进程全局 env 旗 `ZEPHYR_COMMIT_GATEWAY` 跨工线程泄漏（安全边界，非性能项）

> 立档：2026-09-24 ｜ 车道：`10_d1_d2`（设计-only，本文件不附代码，施工 lane 按本单写）
> 变量单一真源名：`_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"`
> 出现处：`scripts/governance/commit_queue_landing.py:146`、`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:215`（对外别名 `GATEWAY_ENV` 见 `:312`）、`scripts/git_guard.py:107`、`scripts/ops_guard.py:139`

## 1. 现象

k=4 落地池的**同一进程**内，落盘主入口在调网关前后直接改 `os.environ`：
`commit_queue_landing.py:1577-1578` 置 `"1"`，`finally` 段 `:1641-1645` 视前值 pop 或还原。
四个工线程共享一个 `os.environ` 字典。同型改写另存在于网关内部（详 §2.2 表 B）。

后果不是快慢问题：该旗是「此 commit 确经 GitCommitGateway」的**凭据**，
被 post-commit 防伪守卫与一批破坏性操作护栏消费。A 线程的 `finally` 可以在 B 线程仍需要它时
把旗摘掉；A 线程的置位也可以把旗**多送**给 B 线程派生的非 commit 子进程。两个方向都是安全边界破口
（一个偏「误判伪造 → `git reset --soft HEAD~1`」，一个偏「误判授权 → 真删/真 reset」）。

## 2. 机理（file:line 与实测/核实数字）

### 2.1 表 A：消费者分类（决定「线程本地是否可行」的关键）

| # | 消费方 | file:line | 读取形态 | 分类 | 旗从哪来 |
|---|--------|-----------|---------|------|---------|
| C1 | POST-COMMIT-GUARD（判定 `[GW:*]` 标记是否伪造；未置旗 → `git reset --soft HEAD~1`） | `scripts/governance/git_hooks/post_commit_guard.sh:134`，正/反文案 `:206/:223`，经 `.git/hooks/post-commit` 末段 source | shell 读子进程环境 | **子进程**（由「同线程的 `git commit`」再生） | 实际由 `run_git` 每次注入（见 C5），与全局旗**无必然关系** |
| C2 | REFERENCE-TRANSACTION-GUARD（`update-ref`/`commit-tree` 侧漏检测，`gw_env` 写入报告并决定 warn_only） | `scripts/governance/git_hooks/reference_transaction_guard.sh:210/:213`，经 `.git/hooks/reference-transaction` source | shell 读子进程环境 | **子进程**（git plumbing 再生，plumbing 由落地侧 `_trusted_git_env()` 起：`commit_queue_landing.py:714-719` = `dict(os.environ)`，**不注入本旗**） | 取决于调用瞬间全局字典里有没有人留下的 `"1"` ← **跨线程污染入口** |
| C3 | pre-commit 通道（整条 gate 链子进程） | `git_commit_gateway.py:3243-3246` `env = {**os.environ, "ZEPHYR_COMMIT_GATEWAY": "1", …}` | 显式 per-spawn 注入 | **子进程**（同线程） | 已显式，不依赖全局 |
| C4 | `session_worktree` 直提路径 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:3849-3859`（`commit_env["ZEPHYR_COMMIT_GATEWAY"]="1"`）；`_make_wt_run_git` 传参见 `:3643/:3651/:6083/:6171` | 显式 per-spawn 注入 | **子进程**（同线程） | 已显式 |
| C5 | 网关 `run_git`（所有 git 子进程的公共同一条通道，含 `git commit --no-verify` 于 `_commit_with_file_message`（def `:3657`）内经 `self.run_git(...)` 起） | `git_commit_gateway.py:4238`（def）→ `:4276-4277` `env = os.environ.copy(); env[_GATEWAY_ENV] = "1"` | **per-spawn 注入（现成正确范式就在同一文件）** | 子进程 | 自身 |
| C6 | GIT-GUARD 破坏性 git 授权位（`reset --hard` `git_guard.py:433`、文件恢复/unlink `:503`、`clean` `:571`、`stash` `:619`） | `scripts/git_guard.py:107`、判定 `:140 return os.environ.get(FORCE_STASH_ENV)=="1" or os.environ.get(GATEWAY_ENV)=="1"` | 读进程环境（作为 hook 子进程时=继承；作为库被 import 时=**进程内**） | **两态**（hook 子进程 + 可 in-process import） | 全局旗（**过授权方向的实际消费方**） |
| C7 | ops_guard 提交域标记判定 + 派生 env 消毒 | `scripts/ops_guard.py:577-583 _is_gateway_marked()`；`:587-599 sanitized_spawn_env()`（显式 `env.pop(GATEWAY_ENV)`）；`:656` 注明删除域授权已只认 `FORCE_ENV` | 进程内读 + 环境副本剔除 | **进程内** | 全局旗 |
| C8 | 队列守护进程内的 in-process 护栏 | `scripts/commit_queue.py:2281`、`scripts/git_commit.py:969`、`scripts/session_worktree.py:640` 调 `install_inprocess_enforcement()` | 进程内拦截文件操作 | **进程内** | 全局旗（守护进程存活期 = 池的存活期） |
| C9 | FORGED-GW-MARKER gate（进程内 gate） | `src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py:21/:35-36/:55/:168` | **已不再读 env**（码体内无 `os.environ` 取用，核实过） | 无 | 2026-09-14 已废 env 逃生，理由原文即本缺陷：**「os.environ 是进程级全局，并发 commit 线程间可互相污染，不可作凭据」** |

**关键判定（决定修法可行性）**：
`os.environ` 在 `subprocess` 起子进程时被快照继承 → 用 `threading.local()` 存旗**无法**被子进程看到，
所以「改成线程本地」单独不成立；正解是 **per-call 显式传参 + 仅在起子进程那一刻用 `env={**os.environ, FLAG:"1"}`**
（C3/C4/C5 已是该形态，本方案是把 C 类的依赖从「全局字典恰好有旗」彻底改写成「起子进程处注入」）。

**同时必须诚实**：`commit_queue_landing.py:66-69` 模块 docstring 仍写「落盘在调 `gateway.commit()` 期间置该 env」
以喂 FORGED-GW-MARKER 的 env 逃生——该逃生已于 C9 被废除 → **这段理由是过期文档**，
是本次「明明已不需要全局旗、却仍在全局改字典」的成因。手术含同步订正该 docstring。

### 2.2 表 B：写方站点（逐处，含 task 交办「两处」的核实结果）

| 站点 | file:line | 形态 | 池化后可达性 |
|------|-----------|------|-------------|
| W1 | `commit_queue_landing.py:1577-1578` 置位 / `:1641-1645` 还原（`prev_env is None → pop`，否则回填） | **一个** try/finally 区域，包住**两次** `gateway.commit` 调用（`:1580` 正常支、`:1623` pathspec 自愈重放支）——task 所说「两处」经核实=**同区域的两个 commit 调用点**，不是两处独立 env 区域 | 是（跨线程摘旗） |
| W2 | `git_commit_gateway.py:3510` 置位（函数 `_resolve_commit_result`，def `:3453`） | 提交成功后置位，供同函数后续的派生挂账/审计段消费 | 是 |
| W3 | `git_commit_gateway.py:3557` **无条件 `os.environ.pop(_GATEWAY_ENV, None)`**（函数 `_commit_locked_finalize`，def `:3523`，由 `:3005` 收尾调用） | **不还原前值、不看谁置的**——A 工收尾即把 B 工 W1 刚置的旗抹掉，这是本缺陷最锋利的机械面 | 是 |
| W4 | `git_commit_gateway.py:3973` 与 `:4025` 置位（函数 `_commit_auto`，def `:3845`；两条 = 正常支与 fail-open 降级支） | **全程无还原**：该函数唯一的 `finally`（`:4039-4043`）只删 pathspec 临时文件 → 任何一次 auto-commit 之后，该进程内此旗**永久留 "1"** | **否，池化前即可达**（单线程守护进程同样中招）→ 见 §6 定年 |
| W5 | `:3243-3246`、`:4276-4277`、`session_worktree.py:3859` | **per-spawn 注入（正确形态，不是缺陷）** | n/a |

### 2.3 实测/核实数字

- 现码 `os.environ` 写点在本仓 git 提交链上共 **7 处**（W1/W2/W3/W4 的四处 = 5 条语句，加 W5 三处 per-spawn 注入）；
  读点 **6 处**（C2/C6/C7 + `post_commit_guard.sh` 内 3 处 shell 读 + `concurrent_commit_test.py:416` 自检读）。
- 暴露窗口量化：W1 区域 = 一次完整 `gateway.commit`（门禁链 + CAS 前置）时长。按同战役既有实测（单件落地 p50 分钟级），
  k=4 池内任一时刻「某线程正持 W1/W2 旗」的概率接近 1 → **W3 的抹旗事件预期在每波多次发生**，
  即 B 线程子进程看到「无旗」的窗口 ≈ 全波。这不是偶发，是结构常态。
- 泄漏方向实测旁证（历史事故同型）：`docs/_archive/2026-08-27-owner-leftover-adjudication.md` 记录
  pytest 进程继承 `ZEPHYR_COMMIT_GATEWAY=1` → `_is_authorized()` 恒真 → 红队护栏 0% 拦截并致真删（三起）。
  池化把「一个进程只跑一条链」变成「一个守护进程内四链并行 + 常驻 reconciler 派生」，同型暴露面在进程内被连续化。
- C2 方向已核实为**读全局**：落地侧 plumbing 的 env 构造器 `_trusted_git_env()`（`commit_queue_landing.py:714-719`）
  只放 `ZEPHYR_SERIALIZER_MODE` 与 `ZEPHYR_GIT_GUARD_FAST_PATH`，**不放本旗** →
  reference-transaction 守卫看到的旗值完全由别的线程此刻留了什么决定。

## 3. 影响面

| 面 | 说明 |
|---|---|
| 安全（偏保守向） | W3 抹旗 → 合法网关 commit 的子进程（C1/C2）在无旗判定分支上被记 `forged_gw_marker` / `unregistered_gw_sid`；C1 的文案面即 `git reset --soft HEAD~1`（POST-COMMIT-GUARD 红线，宪明「标记不可伪造」条） |
| 安全（偏宽松向） | W1/W2/W4 置旗 → 同进程内非 commit 子进程与 in-process 护栏（C6/C7/C8）被**过授权**（`git_guard` 认旗放行 `reset --hard`/`clean`/`stash`） |
| 可诊断性 | 事后取证无法从队列项/审计判定「那一刻是哪条线程的旗被子进程继承了」——泄漏无留痕（与 D1 的「遥测黑洞」同族） |
| 吞吐 | 无直接影响（本单不为性能） |
| 门禁/阈值 | 零改动：不新增、不放宽、不删除任何判据；仅改变「凭据的传递方式」 |

## 4. 手术方案（逐处改动点与意图，禁止贴整段新代码）

**取向：参数显式传（threading.local 不足喂子进程，见 §2.1 关键判定）；环境只在「起子进程那一瞬」按 per-call 注入（W5 已是仓内既有范式）。**

1. **网关开一个显式内部调用形参**（`GitCommitGateway.commit`，签名层）
   - 意图：新增布尔形参（建议 `internal_call: bool = False`，或沿用仓语境的 `allow_forged_gw_marker` 口径命名，
     二选一由施工 lane 按现有参数命名纪律定），把「调用者确为网关内部链路」这件事**沿栈传**而非**沿环境传**。
     与既有的 `allow_non_worktree` / `allow_tracked_drift` / `allow_multi_domain` / `allow_promote` /
     `lock_wait_timeout`（落地侧传参见 `commit_queue_landing.py:1580-1602`）同族，参数列表已是既定扩展点。
   - 消费点：`internal_call` 只允许影响「是否在某次 spawn 的 env 里注入该旗」，
     即 `run_git`（`:4238`，已有 `:4276-4277` 注入语句）与 `_run_precommit_channel`（`:3243-3246`）——**这两处已经注入，
     所以第 1 步的真实作用是给第 2 步「删全局写」提供可证明的替代**。
2. **删除 W1**（`commit_queue_landing.py:1577-1578` 与 `:1641-1645` 的还原 `finally`）
   - 意图：落盘不再碰全局字典；两个 `gateway.commit` 调用点（`:1580` 正常支、`:1623` 自愈重放支）
     **各自加 `internal_call=True`**（两处都要，漏一处即回归）。
   - 同时订正 docstring `:66-69`（现文案以「FORGED-GW-MARKER env 逃生」为存在理由，该逃生 2026-09-14 已废，
     见 C9）→ 改为如实说明「网关内部调用经显式参数声明，凭据不走环境」。
3. **删除或降级 W2/W3**（`git_commit_gateway.py:3510` 置位 / `:3557` 无条件 pop）
   - 优先方案：**整对删除**。前提=用 §5 T2 证明 `_resolve_commit_result`→`_commit_locked_finalize`
     段内没有任何 in-process 消费者（当前勘察：C7/C8 只读该旗做**诊断/提交域**判定，
     且 `ops_guard.py:656` 已声明删除域不认此旗；C9 不读）。
   - 若 T2 发现确有 in-process 消费方：改为「**prev-snapshot 的 try/finally 还原**」（`:3557` 现是裸 pop，
     必须至少先修成还原前值——这一步单独就是止血，可作为第一批落地）。
4. **必修 W4**（`git_commit_gateway.py:3973`、`:4025`，函数 `_commit_auto` def `:3845`）
   - 意图：两处置位各自配 prev-snapshot 还原（放入 `:4039-4043` 那个 finally，或就近包一层），
     终结「auto-commit 之后该进程永久持旗」。
   - 这条**与池无关、现在就在漏**（§6），因此它应作为**第一个 commit**，独立于 D2 其余改动，
     便于单独回滚与单独验收。
5. **消毒面补强**（不改判据）
   - 任何非 commit 的派生 spawn 一律走 `ops_guard.sanitized_spawn_env()`（`scripts/ops_guard.py:587-599` 现成）；
     施工 lane 只需 grep 复核 `commit_queue*.py` / 网关里 `env=dict(os.environ)`（`commit_queue_landing.py:714-719`）
     是否需要剔除本旗——注意 plumbing 侧（C2）期望的是**确定性**，无论有无旗都该由代码显式决定，不该「看当时谁留了什么」。
     → 意图：`_trusted_git_env()` 显式决定是否注入本旗（读 reference-transaction 守卫判据后定，
     保持现行为=不改判据结果），从而把 C2 从竞态里摘出来。
6. **守护进程 fail-fast 自检**（可选，5 分钟量级）
   - 队列守护入口（`scripts/commit_queue.py:2275-2285` 附近，紧接 `install_inprocess_enforcement()`）
     断言启动环境不含本旗（含则拒绝启动并留痕）；与红队 fixture 的隔离纪律同型
     （`tests/governance/test_ops_guard_red_team.py:53-57 _AUTH_ENV_VARS`）。

**禁止项（写进施工令）**：不得用「池级锁包住 env 区域」草草收工——那会把门禁段重新串行化，
直接吃掉 k=4 的全部收益；不得给 `forged_gw_marker_gate` 重新接回 env 判据（那是已废逃生通道）；
不得为让测试通过而删/改 `tests/governance/test_git_hooks_marker_forgery.py` 与
`test_forged_gw_marker_gate.py` 的断言口径。

## 5. 语义等价性自证方案（D2 的「等价」= 子进程可见性等价）

逐字段差分不适用（本单不改数据），改判据为**凭证可达性矩阵**：

- T1 站点覆盖表：把 W1–W5 与 C1–C9 做成机器可跑的清单（`scripts/governance/repair/concurrent_commit_test.py:407-416`
  已有 scenario_10 读旗自检，复用它当基线），逐格断言「修前修后，该消费方在该路径上看到的旗值相同」。
- T2 消费者穷举：`grep` 面 = 变量名 `ZEPHYR_COMMIT_GATEWAY` + 符号 `_GATEWAY_ENV`/`GATEWAY_ENV`
  （含 `.git/hooks/*`、`scripts/governance/git_hooks/*.sh`、`src/`、`tests/`）→ 结果集必须与 §2.1 表 A 一致
  且**每条都有分类标注**；未分类 = 不许删写点。
- T3 真实钩子端到端：在 `tmp_path` 真仓 + 真 hooks（复用 `tests/governance/test_git_hooks_marker_forgery.py`
  的 harness，其 `:88/:96` 已示范 per-spawn 注入 env 起 commit）跑三条：
  合法网关 commit → HEAD 前进且无 `forged_gw_marker` 报告；手写 `[GW:*]` 裸 commit → 报告为 forged 且被 reset；
  两条口径在修前/修后**逐字节同结论**（这就是 D2 的等价性证）。
- T4 反查无残留：修后全仓 `grep -n "os.environ\[_GATEWAY_ENV\]\|os.environ.pop(_GATEWAY_ENV"`
  命中数必须等于设计值（§4 步 3/4 全删时=仅 W5 的 per-spawn 形态，即 `:4277`/`:3244` 两处赋字典键，无裸 mutate）。

## 6. 红测方案（必须先证红）

新增 `tests/governance/test_gateway_env_thread_isolation.py`（tests 目录 CREATE-GUARD 豁免）。
用 `threading.Barrier` 造确定性交错，零 sleep 赌博：

- **R-D2-a（摘旗方向 = W3/W1 之错）**
  1. 线程 A：进入「被测 env 区域」（对现码即复用 `commit_queue_landing.py:1577-1578`/`:1641-1645`
     的等价最小片段，或用桩替换 `gateway.commit`，见下）→ 置旗 → 等 barrier-1 → 线程 B 跑完它的一轮
     → 等 barrier-2 → **A 起真实子进程** `sys.executable -c "import os;print(os.environ.get('ZEPHYR_COMMIT_GATEWAY'))"`
     → 断言子进程 stdout == `"1"`。
  2. 线程 B：等 barrier-1 → 置旗 → 起同样子进程并断言 `"1"` → **执行 W3 形态的收尾（裸 `os.environ.pop`）** → 等 barrier-2。
  3. 现码必红：B 的收尾把 A 的旗抹掉 → A 的子进程打印 `None`。修后（A 的旗不再活在 `os.environ`，
     而在 per-spawn env 构造里）→ 绿。
  4. 反向断言（同测第二条）：B 的 exit 不得改变 A 的可见性；且 A 的 exit **不得给 B 留下旗**
     （过授权方向，喂 `git_guard.py:140` 那类消费方）→ 现码同样红（W1/W2 的置位是全进程可见）。
  5. 取证要求：把「现码跑出红」的 pytest 输出贴进施工 PR 描述（本车道不跑码，故列为施工第一步交付物）。
- **R-D2-b（永久留旗方向 = W4）**
  单线程即可红：桩掉真 commit，调 `_commit_auto` 形态路径一次 → 断言调用返回后 `"1" not in os.environ`。
  现码必红（`:3973`/`:4025` 置位、`:4039-4043` 的 finally 不还原）→ 这条同时是「池化前即可达」的证明件。
- **R-D2-c（子进程真钩子方向）**：T3 的三条在**双线程交错**下各跑一遍，断言报告文件里 `gw_env` 字段
  与单线程基线一致（现码预期出现 `gw_env=0` 与 `1` 抖动 → 红）。

红测不许改成「容忍」或「放宽断言」；若 R-D2-c 因钩子环境不可注入而难跑，降级为 R-D2-a/b 加严，
**不许删断言**（判据口径不得由施工侧改动）。

## 7. 必绿测试清单

- `tests/git/test_git_commit_gateway.py`：全量；特别 `:431 test_commit_sets_gateway_env` ——
  **本测现为空断言**（`:438` 语句尾为 `or True`，等于永真）→ 本单要求**把它补成有牙齿的断言**
  （返回后旗不残留 + 子进程可见性），属「加严不放宽」，不许反向删除。
- `tests/governance/test_git_hooks_marker_forgery.py`（`:88`/`:96` 真钩子 + env 注入范式，POST-COMMIT-GUARD 面）
- `tests/governance/commit_gates/test_forged_gw_marker_gate.py`（`:122`/`:135`/`:227`/`:284` setenv/delenv 四组）
- `tests/governance/test_ops_guard_red_team.py`（`:53-57 _AUTH_ENV_VARS`、`:231` 反架空条——
  这条是「旗不得成为删除授权」的判据，修后必须仍 100% 拦截）
- `tests/governance/audit/test_git_guard_bypass_reconciler.py:59`（清理三旗的 fixture 口径）
- `tests/governance/audit/test_file_ops_enforcement.py:593`（`monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY","1")`）
- `tests/governance/rule_bridge/test_dual_lock_unification.py`、`scripts/governance/repair/concurrent_commit_test.py`
  （scenario_10 `:407-416`）
- 队列全家：`tests/governance/test_commit_queue_pool.py`（全量，尤其 `:316` k=1 与旧路字节级全等）、
  `test_commit_queue_landing.py`、`test_commit_queue_landing_nightfix.py`、`test_commit_queue_integration.py`、
  `test_commit_queue.py`
- 新增：`tests/governance/test_gateway_env_thread_isolation.py`（§6）

## 8. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | **最大风险**：删掉全局置位后，某个仍依赖「继承全局字典」的子进程拿不到旗 → POST-COMMIT-GUARD（C1）把合法网关 commit 判伪造并 `git reset --soft HEAD~1`，**把已落地的 commit 吃掉**（安全边界翻向最坏一侧） | 顺序不可颠倒：先落 W4 止血（步 4，独立 commit）→ 再确认/补齐 per-spawn 注入面覆盖 C1/C2/C3 三类（步 1/5）→ T3 真钩子端到端 + R-D2-c 双线程绿 → **最后**才删 W1/W2/W3 的 `os.environ` 写点；并在 canary 队列项上真跑一次 drain 验 HEAD 不被回退 | C2（reference-transaction）是 plumbing 侧、`run_git` 注入不覆盖它 → 必须按步 5 显式决定其 env，不许「继承看运气」。此项判据未定死前，W1 只允许改成 prev-snapshot 还原、不允许删 |
| 2 | 参数形参扩散：`internal_call` 被误当成「万能逃生」，绕过防伪 | 语义严格限定为「影响 env 注入」，不许触达任何 gate 判定（C9 判据一行不动）；文档写明 | 低 |
| 3 | 与 D1 改在同一函数区域（`_pool_process_item` / `WorktreeLanding.__call__`）冲突 | 两单不同函数面（D2 在 `__call__:1577-1645`，D1 在 `:2196-2216`）；仍建议**不同 commit**，见 README 序 | 低 |
| 4 | 测试侧曾靠「进程继承旗」隐式过测（红队事故即此型） | §7 的 `test_ops_guard_red_team.py:53-57` fixture 隔离必须先绿；删全局写会顺带暴露这类隐性依赖=**好事，不许用 setenv 掩耳** | 中（可能牵出额外修复量） |

回滚：D2 各步按独立 commit 推进（W4 止血 / 注入面补齐 / 删全局写 三段），任一段可单独 `git revert`；
零数据迁移、零队列项 schema 变更、零 flag 出厂翻转。回滚后行为=现网行为。

## 9. 施工估时

| 步 | 内容 | 估时 |
|---|------|-----|
| 0 | §6 R-D2-a/b 红测先跑现码取红证（含截图/日志入 PR 描述） | 1.0 h |
| 1 | 步 4（W4 止血，独立小 commit） + `test_commit_sets_gateway_env` 补牙 | 0.5 h |
| 2 | 步 1（网关 `internal_call` 形参）+ 步 5（注入面复核/`sanitized_spawn_env` 接线） | 1.5 h |
| 3 | 步 2/3（删 W1、W2/W3）+ docstring `:66-69` 订正 + 步 6 fail-fast | 1.0 h |
| 4 | T1–T4 自证 + §7 全量必绿跑（含队列全家 + 钩子 + 红队） | 1.5 h |
| 合计 | | **≈ 5.5 h**（不含 gate 连坐返工；gate 返工预留 1 h） |
