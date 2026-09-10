---
ttl: task_bound
---

# 提交通道性能优化调研方案（已审定 · P0 已执行 · 收尾移交下一会话）

- **task_bound**：临时工作文档，Owner 审定后按"正式施工清单"逐项销项后归档；会话 st-perf-plan-20260910 单写手
- **创建**：2026-09-10；creation_token=`commit-pipeline-perf-plan-20260910`（capability_canonical_file_registry.yaml creation_tokens 段，插 di_seam_exemptions 行之前）
- **纪律**：本任务只做只读调研+计时取证；允许的最小施工=打点日志与 --wait 参数化原型验证（已做，沙箱零风险，验证后未触碰任何 tracked 源码文件）；本文档 Owner 审定前不施工
- **结论速览**：三条根因全部坐实并有实测数据；**第一约束=功能效果严格不变、只提速提效**（§2.7 逐项等价性自审）；P0 三项（--wait 参数化 / 死信 triage / 文档纠偏）全部严格行为等价可立即施工；P1 三项（own-scope 扩充 / 子进程税治理 / 队列运营收尾）；P2 三项 flag 门控需 Owner 拍板；echo_guard 超时下调涉及检测语义权衡，已从 P0 摘出改为 Owner 明示项

---

## 0. 背景与现象（实测）

ZephyrAlpha 多 AI 会话并发共享工作区，唯一合法提交入口 `python scripts/git_commit.py` → GitCommitGateway（`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`，3020 行）。

### 0.1 本次调研实测数据（2026-09-10）

| # | 观测项 | 实测值 | 取证方式 |
|---|--------|--------|---------|
| 1 | 单次提交占全局锁时长 | **≥221 秒（3分41秒）确认下界**，上限约 14 分钟（16:46:06 持锁，17:00:08 前释放） | 活体观测 `.ailocks/git_commit_global.lock`（PID 27828） |
| 2 | 106 gate 全链耗时 | **41.4 秒**（当前共享暂存区含他人 WIP 真实混合场景，2 文件 commit 范围） | 只读计时 harness 逐 gate 实测（§6.2） |
| 3 | echo_guard 30s 超时 | **23 次** "EchoGuardAdapter degraded: echo-guard check 超时(30s)" | 全量 gw_*.log grep |
| 4 | 最重单 gate | DECISION-MAP **8.24s**（其头部自述"毫秒级"严重失真）；ENCODING-SAFETY 5.37s；RULE-FOUR-WAY-ALIGN 3.82s；TTL-METADATA 3.34s；DIRECTORY-CONTRACT 2.96s | 计时 harness |
| 5 | 子进程启动税 | **68 个** gate 呈 0.15-0.25s 均匀分布 = `run_checker_script` 每次 spawn python 解释器（~0.18s/个），**合计 12.52s/次提交** | 计时 harness + commit_gate_registry.py L222-277 |
| 6 | 队列运行时 | pending/processing/done=0（compaction 生效）、**dead=856**、blobs=2086 | `.runtime/commit_queue/` 清点 |
| 7 | 队列覆盖范围 | 仅 `_commit_auto`（reconciler 自动提交）改道；**交互式提交（占锁痛点主体）不走队列** | gateway L2613-2633 + flags.yaml L82 |
| 8 | CloneGuard 快路径 | 0.44s（本次实测）；30s 超时为尾部场景 | 计时 harness + gw 日志 |

### 0.2 三条根因（复核确认）

1. **全局锁临界区 = 整条门禁链 + git 操作**。TRAE-079 铁律1（2026-09-03 防 TOCTOU 有意设计）：L1779 `with _GlobalCommitLock(...)` 内执行【merge 二次校验 + ita 清扫 + 全量 106 gate 链（`_check_gates_with_drift_watch`：tracked 区指纹快照 → registry.check_all → 指纹比对+漂移归因）+ `_commit_locked`（git add + commit）】。reconciler 已在锁外异步 post-commit（P2-3 治本），锁内时间主体就是 gate 链。
2. **锁等待 60s 硬编码，无透传链路**。`_LOCK_TIMEOUT_DEFAULT = 60.0`（L145）；`_GlobalCommitLock.__init__` **已有 timeout 构造参数**（L248）但两处调用点（L1779/L2712）均不传；`commit()` 签名（L1658-1670）无 timeout 参数；CLI（scripts/git_commit.py）无任何等待参数。超时抛 GatewayError → exit 2，AI 会话只能盲目重试轮询（昨夜单会话 20+ 轮、多会话互锁 2 小时的直接成因）。
3. **无门禁结果缓存**。`CommitGateRegistry.check_all`（commit_gate_registry.py L370-411）按 priority 升序**全量执行、无失败短路**——每次提交付全部 106 gate 成本；同一文件反复提交（失败重试/连续小改）门禁全量重算。

---

## 1. 调研方法与证据清单

- **代码取证**（只读）：gateway 锁类/主流程/_commit_auto、CLI 全文、commit_gate_registry、in_process_gate_registry.yaml（106 gate）、clone_guard 全包（orchestrator/config/engines）、commit_queue_landing.py、architecture_issue_registry.yaml #ARCH-COMMIT-QUEUE-MVP-001 条目、_diff_helpers.py own-scope 三件套
- **日志取证**：.runtime/tmp/gw_*.log（31 个）全量 grep 降级/超时统计
- **实测取证**：①106 gate 逐 gate 计时 harness（只读调用 spec.check()，结果落 .runtime/tmp/gate_timing_results.json）；②--wait 参数化零风险沙箱原型（导入生产 `_GlobalCommitLock` 类，锁文件指向 .runtime/tmp/lockproto 沙箱，验证 timeout 透传）；③活锁观测（4 时点采样）
- **运行时取证**：.runtime/commit_queue 各目录清点、.ailocks/registry.json、.echo-guard/ 索引目录、flags.yaml

**最小施工合规说明**：两个沙箱脚本（gate_timing_harness_st_perf_plan.py / wait_proto_st_perf_plan.py）均在 gitignored 的 .runtime/tmp/ 下，未改任何 tracked 文件，未获取真实全局锁。

---

## 2. 六项调研

> 每项结构：现状取证 → 方案选项 → 工作量 / 风险 / 灰度 / 回滚。

### 2.1 锁等待参数化（--wait）

**现状取证**
- `_GlobalCommitLock`（L231-336）：O_CREAT|O_EXCL 原子文件锁；锁文件锚主仓根（B22⑤ worktree 剥离，全项目唯一串行锁不变量）；TTL 30min（L144）+ 僵尸 PID 零窗口检测；轮询 0.1s（L146）；**timeout 构造参数已存在**（L248）。
- 调用点 L1779（交互式）与 L2712（_commit_auto）均 `with _GlobalCommitLock(self.project_root)` 不传 timeout → 恒 60s。
- CLI：`gw.commit()` 调用（git_commit.py L686-697）无 timeout；argparse 无等待参数。
- MODIFY-GUARD（gateway L9）保护清单：锁 TTL、锁文件名、GW 标记格式、env 名——**timeout 参数不在保护清单**，加参数不触碰 MODIFY-GUARD。
- OSError fail-open 分支（L1808-1837/L2752-2771）无锁执行，不受 timeout 影响。
- **沙箱原型已验证**：timeout=3.0 → 3.09s 抛 GatewayError；默认 60.0s 复核通过；锁自清后可重获（§6.1）。

**方案选项**

| 方案 | 内容 | 评价 |
|------|------|------|
| **A（推荐）** | CLI `--wait`（float，缺省 60.0=现状兼容）→ `gw.commit(..., lock_wait_timeout=...)` → 两处 with 语句 `timeout=lock_wait_timeout if lock_wait_timeout is not None else _LOCK_TIMEOUT_DEFAULT` | 纯管道改动 2 文件 ~15 行；缺省行为零变化 |
| B | env var `ZEPHYR_COMMIT_LOCK_WAIT` 兜底（CLI 不改也可用） | 可发现性差；可作为 A 的补充项一起做（可选） |
| C | flags.yaml 全局默认等待配置 | 行为变更属 Owner 窗口，且掩盖真实争用，不推荐为主路径 |

设计要点：
- `--wait 0` 语义 = 立即失败（快速探测锁状态）；`--wait` 上限建议钳制 ≤1800s（=TTL，超过无意义，TTL 兜底会清锁）。
- 默认值**保持 60.0 不变**（不改变现有会话行为；是否调默认值属 Owner 决策）。
- exit code 契约不变（LOCK_TIMEOUT 仍 exit 2）；`_COMMIT_RESULT_MAP` 的 LOCK_TIMEOUT 行 help_text 增补引导："如需等待更久用 --wait 900；建议对 exit 2 做指数退避重试（5s→15s→45s…）而非固定轮询"——把昨夜 20+ 轮无效轮询的教训固化进提示。
- `_commit_auto` 路径（L2712）不在本批透传（施工偏差：后台 reconciler 无 CLI 通道，默认 60s 即其语义；见 §7-2 偏差记录）。

**工作量**：0.5 人时，2 文件（scripts/git_commit.py、gateway commit 签名+两处 with），测试 3 例（默认 60 / 自定义超时 / --wait 0），入 tests/test_git_commit_gateway.py。
**风险**：极低（缺省=现状；原型已验证锁机制）。
**灰度**：无需求（缺省行为不变，按需显式传参）。
**回滚**：单 commit revert。

### 2.2 门禁结果缓存

**现状取证**
- 无任何缓存层；check_all 全量执行无短路；同一文件反复提交门禁全量重算（实测 41.4s/次）。
- 关键结构事实：**CLI 每次调用是独立 python 进程**——"单次 commit 会话内"缓存对"跨重试"无效；跨重试缓存必须持久化（.runtime/）。
- gate 语义异质：内容扫描型（staged 内容的纯函数）、信号型（依赖 session registry/锁状态/HEAD/时间）、结构校验型（读全局注册表/地图，部分"恒跑"设计）。降级态存在（CloneGuard degraded、DB 离线 fail-open、worktree skip）。
- 失败短路缺失放大重算成本：gate 失败后后续 gate 照跑，全部结果一起返回。

**方案选项**（分三层，可独立落地、递进组合）

| 方案 | 内容 | 实测收益估算 | 评价 |
|------|------|-------------|------|
| A1 共享输入 memoization（进程内） | commit() 一次调用内，把 `git diff --cached` 输出、staged 文件清单、per-file blob sha 等共享输入 memoize，供全部 in-process gate 复用 | 消除链内重复 git 子进程调用（数十次 → 数次），约 2-5s | 零语义风险（只是输入去重，不改任何判定） |
| A2 checker 合并执行（消子进程税） | 新增 checker supervisor：单个 python 进程顺序/并行跑完全部子进程 checker 脚本，替代 68 次 spawn | **12.5s → <2s**（启动税归零，checker 实际工作时间保留） | 改动面 = run_checker_script 基建 + 各 gate 调用方式；需保持 CREATE_NO_WINDOW 与超时语义；**故障隔离需重设计**（单 checker 崩溃/内存膨胀不得影响他者，逐 checker 超时改为 supervisor 内调度） |
| A3 持久化结果缓存（白名单子集，flag 门控） | key = `gate_id × own_scope_set_hash × staged_file_content_sha × HEAD_sha`；落 .runtime/gate_cache/；**只缓存 passed=True 且非降级态**的结果；TTL 10min + HEAD 移动即失效 | 重试场景（同文件反复提交）单次省 30-40s | 见下方语义交互设计 |

**A3 失效正确性设计**（Owner 关注点逐条回应）：
- **staged 内容变化必须全失效**：key 含全部 staged 涉检文件的 blob sha 集 + `git write-tree` 指纹，任一变化 → key 不命中（等效全失效）。
- **生命周期**：TTL 10min + HEAD_sha 进 key（HEAD 移动 → 全失效）+ flags.yaml mtime 进 key（配置变更失效）。
- **fail-open/fail-closed 交互**：
  - 只缓存 `passed=True` 且缓存条目记录引擎健康状态；**降级态（CloneGuard degraded / DB fail-open / worktree skip）产生的 PASS 一律不缓存**——防止把"检测器失效的侥幸通过"洗白成可信 PASS（fail-open 语义不被缓存放大）。
  - `passed=False` 不缓存（AI 修复内容后 sha 变化 key 自然失效，缓存失败结果无意义且危险）。
  - 白名单准入：仅"staged 内容纯函数"gate 可入白名单（§2.6 分级清单中内容扫描型）；信号型禁入；结构校验型恒跑类（DECISION-MAP 等）暂不入（其输入含全局注册表，hash 成本>收益）。**准入前置=逐 gate 输入面分析**：凡输入超出 `staged 内容 ∪ own_scope ∪ HEAD` 的 gate，须把其全部输入文件 sha 纳入 key 方可入池——确保缓存命中 ≡ 现算（2026-09-10 复审补强）。
- **与 own-scope 组合**：key 含 own_scope_set_hash——同一文件换会话/换 claim 范围提交时不误命中。
- **与 TOCTOU 组合**：缓存命中在锁内校验指纹后采信（与 §2.3 同一指纹机制）。

**工作量**：A1 0.5 天；A2 1-2 天；A3 1.5 天 + 灰度设计（flag `gate_result_cache` 默认 OFF，Owner 窗口开）。
**风险**：A1 低；A2 中（基建改动，需回归 68 gate 语义等价）；A3 中（语义设计已收敛如上，剩余风险=白名单误纳，需逐 gate 审批准入）。
**灰度**：A1/A2 随下批 gate 治理直接上（行为等价）；A3 flag 门控，先灰内容扫描型 top5（ENCODING-SAFETY/TTL-METADATA/DIRECTORY-CONTRACT/NO-BARE-SQL 族），观测一周误命中率。
**回滚**：A1/A2 revert；A3 flag OFF 即回退（缓存目录可整删）。

### 2.3 重引擎出锁可行性（锁外预跑 + 锁内指纹采信）

**现状取证**
- 锁内耗时主体（实测）：DECISION-MAP 8.24s + ENCODING-SAFETY 5.37s + RULE-FOUR-WAY-ALIGN 3.82s + TTL-METADATA 3.34s + DIRECTORY-CONTRACT 2.96s + ARCH-REFERENCE 1.76s + 子进程税 12.5s + 其余零散 ≈ 41.4s（+ commit git ops + drift-watch 指纹快照 ×2）。
- 信号型 gate（SESSION/CLAIM/HELD-OVERLAP/FOREIGN-CHANGE/WORKTREE-REQUIRED/RECONCILER-HEALTH/HOT-FILE/FORGED-GW-MARKER/GATE-PRECOMMIT-OFFLINE 等）实测 0.000-0.27s——**锁内保留成本可忽略**。
- CloneGuard 内部已并发（ThreadPoolExecutor+asyncio，嵌套事件循环才回退顺序），单引擎超时 30s 为尾部上界。
- 09-03 TOCTOU 设计动机（L1775-1777 注释原文）：gate 检查在锁外时，另一 session 可在 gate 通过后、commit 前修改文件（搭便车/FOREIGN_CHANGE）——治本=串行化整个 [gate → stage → commit] 不可分割。

**方案 A（推荐）：锁外预跑 + 锁内指纹校验采信**

流程设计：
1. commit() 拿锁**前**：跑 gate 链的"可预跑子集"（内容扫描型 + 触发式结构校验型，§2.6 白名单），同时记录指纹 `F = {staged_tree_sha(git write-tree), HEAD_sha, own_scope_set_hash, gate_inputs_manifest_sha}`——第四项为**白名单 gate 全部外部输入文件**（各注册表/配置 YAML）的内容 sha256 清单，防止预跑→拿锁等待窗口内注册表变更导致陈旧采信（等价性关键补强，2026-09-10 复审加入）。
2. 拿锁后：重算指纹 F′。**F′==F → 采信预跑结果**，锁内只跑信号型 gate + drift-watch + commit；**F′≠F → 丢弃预跑结果，锁内全量重跑**（现行路径，正确性永不依赖指纹）。
3. 预跑任何异常/降级 → 直接走现行锁内全量链（fail-safe to current behavior）。

**安全边界论证（对 09-03 TOCTOU 设计的等价性）**：
- 原设计消除的窗口：gate 通过后、commit 前 staged 内容被改。方案 A 中，采信的前提是锁内重验 `git write-tree` 树 sha 与预跑时逐字节一致（O_EXCL 锁保证此刻无并发写入者持有锁在写 index；树 sha 对 staged 内容完备敏感，任一字节变化 sha 必变）。
- 内容 gate 是 staged 内容的纯函数 → 指纹相等 ⇒ 判定必然相同 ⇒ 采信无损。原不变量"被提交的树必须通过全部门禁"保持成立：预跑与采信针对的是**同一棵树**。
- HEAD_sha 进指纹：部分 gate 以 HEAD 为 diff 基线（added-lines 判定），HEAD 移动则重跑，杜绝基线漂移。
- gate_inputs_manifest_sha 进指纹：白名单 gate 读取的注册表/配置文件内容 sha 清单——预跑与锁内采信之间任何输入变化都触发重跑，保证"采信结果 ≡ 锁内现算结果"。
- 残余窗口 = 锁内"算指纹 + 比对"两步（毫秒级原子读），相比原设计"整链执行期"收窄两个数量级。
- 信号型 gate 不参与预跑：其判定对象是会话/锁/健康运行态，本质必须在锁内以最新状态判定。
- **drift-watch 交互**（预跑引入的新语义面）：tracked 区漂移监视在预跑段与锁内段分别执行——预跑段发现的漂移只记审计（不阻断，窗口内写入方尚无 lock 归属）；**硬阻断语义只归属锁内段**（维持现行 CAND-GATEMECH-004 行为），锁内段指纹比对前后同样做快照监视。

**方案选项对照**

| 方案 | 内容 | 锁内时间预估 | 风险 |
|------|------|-------------|------|
| A（推荐） | 锁外预跑子集 + 锁内指纹采信，不一致回退全量重跑 | ~45-50s → **~5-8s**（-85%） | 中：白名单分类错误=漏检，需 §2.6 分级清单逐 gate 审批 + 红蓝测试 |
| B（最小改） | 仅 CloneGuard 出锁预跑 | -0.4~-30s（尾部场景收益大） | 低 |
| C（不出锁） | 仅靠 §2.2 缓存 + own-scope 减负 | ~30s（-40%） | 低 |

**工作量**：A 约 2-3 天（预跑编排器 + 指纹工具 + gate 白名单机制 + 红蓝测试：预跑后篡改 staged→指纹不一致重跑 / HEAD 移动→重跑 / 预跑异常→回退现行 / 降级不采信）。B 约 0.5 天。
**风险**：A 中（最大风险=gate 分类遗漏其隐性全局依赖；缓解=白名单默认空集逐个准入 + 不一致即重跑的兜底路径永不拆除）。
**灰度**：flag `gate_preflight` 默认 OFF（出厂安全默认）；Owner 窗口开启后先灰 docs 域提交（低危），观测指纹命中率与零漏检证据，再放 src 域。
**回滚**：flag OFF 即回现行（预跑代码不删，留作下次启用）。

### 2.4 commit_queue_serializer 启用评估

**现状取证（重心：已 ON 运行 8 天的运营评估，而非是否启用）**
- MVP 完成度：A 段（队列协议 + scripts/commit_queue.py CLI + 自举排空 + 死信 + compaction，41 测试）与 B 段（commit_queue_landing.py：专用 worktree 真落盘 + 全门禁零适配 + dev update-ref CAS + assert_single_writer_dev_history，32 测试）**均已落码**；#ARCH-COMMIT-QUEUE-MVP-001 登记完整。
- flag：2026-08-22 Owner 裁定翻开，当前 ON（出厂默认 ALWAYS_OFF；读取唯一点 fail-closed）。
- 覆盖边界（关键）：**仅 `_commit_auto`（reconciler 自动提交）改道入队**（L2613-2633，batcher 优先 → flag 判定 → 异常降级直提+warning）；交互式提交不走队列 → **1-4 分钟占锁痛点主体不受队列影响**。
- 运行时实况：pending/processing/done=0（compaction 生效）、**dead=856**、blobs=2086、per-source .seq 计数器正常。
- 已知缺口（登记在案的残余 + 本次新发现）：
  1. 死信 856 项无 triage 流程（task_board 联动属 P1 未做）——CAS 冲突/基底冲突死信回退给人，但"人"侧无可见入口；
  2. **队列路径 CloneGuard 实质缺位**：WorktreeLanding 专用 worktree 内无 .echo-guard 索引（gitignored 运行时目录不随 worktree 创建）→ echo_guard 恒降级 warn-only，克隆检测在队列落盘路径上是空转；
  3. 可观测性：队列深度/死信率/落盘时延无 metrics 埋点与告警。

**方案选项**

| 方案 | 内容 | 评价 |
|------|------|------|
| 4a 运营补强（推荐，立即） | ①死信 triage：`python scripts/commit_queue.py status --dead` 汇总报表 + 人工处置 CLI（retry/purge 带 reason 审计）+ task_board 标签联动补上；②worktree 内 echo-guard：serializer worktree 共享主仓索引（env 指向主仓 .echo-guard）或显式登记"队列路径克隆检测降级"为已知限制并落审计；③队列指标接 metrics flag（queue_depth/dead_rate/landing_latency） | 不改行为语义，纯补强 |
| 4b 交互式提交入队（Owner 决策项） | `scripts/git_commit.py` 增加 `--enqueue` 模式：快照入队即返回 qid，AI 会话轮询 `status <qid>` 而非占锁重试——**釜底抽薪解 1-4 分钟占锁与无限轮询** | 提交语义从同步变异步（所有 AI 会话用法要改）；serializer 成为 dev 唯一写者后全局锁仅剩其持有，争用归零 |
| 4c 维持现状 | auto-commits 已出队，交互式靠 §2.1/2.2/2.3 缓解 | 保底路线 |

**4b 前置条件清单**（若 Owner 立项）：①4a 完成（死信清零机制+可观测性）；②AI 会话侧提交协议改造（qid 轮询/回调）；③serializer worktree 的 CloneGuard 索引方案落地（否则队列路径克隆检测缺口扩大到全部提交）；④压测：入队→落盘 P95 时延 < 现行同步 P95；⑤灰度：仅 docs 域会话先走队列两周，assert_single_writer_dev_history 日检；⑥回滚：flag（commit_queue_interactive）OFF，队列存量 drain 完毕后关闭。

**工作量**：4a 约 1-2 天；4b 约 3-5 天 + 会话协议改造。
**风险**：4a 低；4b 高（语义变更，需完整灰度）。
**灰度/回滚**：4a 无灰度需求；4b 见前置条件清单，回滚=flag OFF。

### 2.5 CloneGuard 引擎优化

**现状取证**
- L1 pre-commit 引擎集**实为两引擎**：echo_guard（外部 CLI，AST 哈希 Tier1 + duckdb 索引 + embeddings，30s 超时）+ ast_grep（**仅 4 条异常处理规则**：no-bare-except / no-broad-except / no-duplicate-try-except / no-pass-in-except，src/zephyr/clone_guard/rules/）。redup 2026-09-05 已显式禁用（本机未装 CLI，此前 enabled:true 期间每次恒静默降级，B22② 治本）。
- **检测面重叠度结论**：ast_grep ∩ echo_guard ≈ **零重叠**（ast_grep=异常反模式规则，echo_guard=克隆检测；不同关注点，合并无收益）；redup ∩ echo_guard = 高重叠（同为语义克隆 T3/T4），redup 保持禁用直至 CLI 安装（避免复活静默降级）。
- 尾部风险实证：echo_guard 30s 超时 23 次（gw 日志）；快路径实测仅 0.44s → 超时属异常场景而非常态负载。
- 可疑根因：`.echo-guard/rescan.signal` 残留（Aug 7，月龄未消费）——疑似索引陈旧触发重扫路径导致超时；embedding 跨进程 FileLock 60s（_EMBEDDING_LOCK_TIMEOUT）为次生等待源。
- CAPABILITY-OVERLAP gate（priority=200）扫**全部 staged .py（AM 过滤，含共享暂存区他人 WIP）**——own-scope 改造的直接目标。
- acknowledged 聚合器级豁免已实现（orchestrator._suppress_acknowledged，2026-09-10，staged 未提交）：echo-guard.yml acknowledged 段对全部引擎报告生效，severity 降级不阻断，fail-open。
- fail_closed=false：全引擎降级=warn-only 放行（语义保持）。

**方案选项**

| 方案 | 内容 | 工作量 | 风险 |
|------|------|--------|------|
| 5a（⚠️ 检测语义权衡，**移出 P0**） | `clone_guard.yml pre_commit.timeout_sec: 30 → 10`（快路径 0.44s，常态余量充足；但 10-30s 可完成的扫描将由"完成检测"变为"降级 warn-only"——**尾部场景检测覆盖收窄，非严格行为等价**） | 1 行配置 | 中（语义）——须 Owner 明示接受；建议先 5b 根因治理观察超时是否自然消失，再决定是否调参 |
| 5b | rescan.signal 消费机制取证与健康检查：确认 CLI 是否因 signal 触发重扫；补索引刷新例程或删除陈旧 signal 的清理步骤；echo-guard index 健康度纳入 RECONCILER-HEALTH 观测 | 0.5 天 | 低 |
| 5c | 检测面整理：ast_grep 4 规则保留（零重叠不合并）；redup 维持禁用并在 clone_guard.yml 注明安装后翻回流程（已有注释）；echo_guard 与 ast_grep 的聚合语义不变 | 0（仅文档） | 无 |
| 5d | CAPABILITY-OVERLAP 纳入 own-scope 推广批次（机械活，随已派批次走）：只查本 session staged .py，外来 staged 落 _audit_foreign_staged 审计 | 随 own-scope 批次 | 低 |
| 5e | CloneGuard 出锁预跑：随 §2.3 方案 A/B 联动 | 随 §2.3 | 中 |

**交互评估（Owner 关注点）**：
- **×缓存**：缓存层若位于 check 返回之后（§2.2 A3 设计），天然缓存的是 post-suppression 结果——acknowledged 降级已被吸收，不会因缓存复活为阻断；缓存准入条件"非降级态"确保 echo_guard 超时降级的 PASS 不会进缓存。
- **×队列**：serializer worktree 内 echo_guard 恒降级（索引缺位）→ acknowledged 豁免在该路径无消费对象；按 §2.4-4a-② 处置（索引共享或登记已知限制）。
- **×own-scope**：5d 完成后 CloneGuard 扫描集缩到本会话文件，扫描成本随并发会话数解耦。

**灰度/回滚**：5a 为配置值调整（Owner 知会后直接生效，回滚=改回 30）；5b/5d/5e 随各自主批次灰度。

### 2.6 106 gate 分级清单

**分类判定准则**
- **内容扫描型**：对 staged 文件内容做正则/AST/编码/哈希扫描（diff 驱动，违规是逐文件局部属性）→ **own-scope 适用**（只查自己文件集语义等价且更准：外来 staged 本就是他人 WIP，替他人跑检测既慢又可能误伤）。
- **信号型**：读会话/claim/锁/健康/时间等运行态信号，判定对象是"当前并发态势"而非文件内容 → **own-scope 不适用**（无文件集可缩；信号本质是全局状态，缩小读取范围=检查失效）。
- **结构校验型**：校验跨文件/跨注册表的结构一致性（地图对齐、引用存在性、放置规则）→ 大多不适用 own-scope（断链可能由任一文件引起，"恒跑"是防静默断链的有意设计）；其中"触发式"子类（staged 未触及地图/注册表即快路径）的优化方向是**触发条件收窄**而非 own-scope。

**own-scope 已完成 5 gate**（用户简报核对一致）：IMPORT-INTEGRITY、SCRIPTS-IMPORT-INTEGRITY、NO-HIGH-COMPLEXITY、UNDEFINED-NAME、NO-GOD-CLASS；共享 helper `commit_gates/_diff_helpers.py`（_norm_rel L435 / _build_own_scope L456=files∪session held_files，None 退化全量保守 / _audit_foreign_staged L498 逐 gate jsonl 审计）。

**实测分级总表**（2026-09-10 harness，106 gate 全量；"快路径"=0.000s 无涉文件早退；★=own-scope 已完成；☆=own-scope 推荐候选；时间单位秒）

| gate | priority | 实测 | 分类 | own-scope |
|------|-------|------|------|-----------|
| DECISION-MAP | 138 | 8.239 | 结构校验（恒跑） | 不适用（可选"按触发文件降频"见 §5 决策项） |
| ENCODING-SAFETY | 42 | 5.368 | 内容扫描 | ☆ 高优（现扫全 staged 含外来） |
| RULE-FOUR-WAY-ALIGN | 76 | 3.818 | 结构校验（恒跑） | 不适用 |
| TTL-METADATA | 32 | 3.343 | 结构校验（触发式） | ☆（逐文件 TTL 头，可只查自己） |
| DIRECTORY-CONTRACT | 30 | 2.958 | 结构校验（触发式） | ☆（逐文件放置规则） |
| ARCH-REFERENCE | 75 | 1.755 | 结构校验 | 不适用 |
| RULING-REFERENCE | 74 | 0.615 | 结构校验 | 不适用 |
| CREATE-GUARD | 60 | 0.559 | 结构校验（触发式） | ☆（逐新增文件 token） |
| CAPABILITY-OVERLAP | 200 | 0.441 | 内容扫描（CloneGuard） | ☆ 高优（现扫全 staged .py 含外来） |
| FRONTEND-MAP | 137 | 0.412 | 结构校验（恒跑） | 不适用 |
| FILE-PLACEMENT-TTL | 33 | 0.371 | 结构校验（触发式） | ☆ |
| NO-HIGH-COMPLEXITY ★ | 92 | 0.488 | 内容扫描 | 已完成 |
| RECONCILER-HEALTH | 64 | 0.266 | 信号型 | 不适用 |
| DOC-REF-BROKEN | 91 | 0.226 | 结构校验 | 不适用 |
| FOLDER-CAPACITY-HARD-LIMIT | 112 | 0.228 | 结构校验（全局计数） | 不适用 |
| FILE-COPY | 85 | 0.219 | 内容扫描 | ☆ |
| NOQA-VALIDATION | 71 | 0.209 | 内容扫描 | ☆ |
| ORPHAN-MODULE | 89 | 0.204 | 结构校验（全仓 grep 引用方） | 不适用（查引用方非被查文件） |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | 72 | 0.200 | 内容扫描 | ☆ |
| GATE-DOMAIN-FK | 78 | 0.206 | 结构校验 | 不适用 |
| RELATIVE-PATH-LITERAL | 115 | 0.203 | 内容扫描 | ☆ |
| NO-IMPORT-SIDE-EFFECT | 103 | 0.184 | 内容扫描 | ☆ |
| CONSUMERS-ACCURACY | 116 | 0.197 | 结构校验 | 不适用 |
| UNDEFINED-NAME ★ | 106 | 0.198 | 内容扫描 | 已完成 |
| ASYNCIO-RUN-IN-CONTEXT | 122 | 0.197 | 内容扫描 | ☆ |
| GIT-CALL-BUDGET | 105 | 0.190 | 信号型（预算计数） | 不适用 |
| IMPORT-INTEGRITY ★ | 107 | 0.195 | 内容扫描 | 已完成 |
| BARE-SUBPROCESS | 108 | 0.194 | 内容扫描 | ☆ |
| NO-LONG-PARAM-LIST | 95 | 0.193 | 内容扫描 | ☆ |
| DEPGRAPH-WRITE-PATH | 100 | 0.190 | 内容扫描 | ☆ |
| NO-UPWARD-IMPORT | 97 | 0.190 | 内容扫描 | ☆ |
| UNSAFE-DICT-SPREAD | 66 | 0.188 | 内容扫描 | ☆ |
| VOCAB-CHAIN | 73 | 0.198 | 内容扫描 | ☆ |
| NO-GOD-CLASS ★ | 93 | 0.186 | 内容扫描 | 已完成 |
| BLUEPRINT-AMODULE-CROSS-CHECK | 119 | 0.189 | 结构校验 | 不适用 |
| BLUEPRINT-AMODULE-CONSISTENCY | 79 | 0.208 | 结构校验（触发式） | 触发条件收窄 |
| STASH-ACCUMULATION | 118 | 0.192 | 信号型 | 不适用 |
| REGISTRY-MASS-DELETION | 140 | 0.190 | 结构校验（触发式 diff） | 触发条件收窄 |
| BLUEPRINT-FORMAT | 77 | 0.177 | 结构校验（触发式） | ☆（逐文件格式） |
| TABLE-NAME-REGISTRY | 120 | 0.178 | 结构校验（触发式） | 触发条件收窄 |
| TEST-SOURCE-CONSISTENCY | 102 | 0.189 | 内容扫描 | ☆ |
| FUNCTION-DUP | 90 | 0.214 | 内容扫描 | ☆ |
| DANGLING-REFERENCE | 70 | 0.189 | 结构校验 | 不适用 |
| PURE-ASSERTION | 69 | 0.186 | 内容扫描 | ☆ |
| EMPTY-HANDLER | 84 | 0.179 | 内容扫描 | ☆ |
| NO-BARE-SQL | 94 | 0.182 | 内容扫描 | ☆ 高优 |
| MUTABLE-CONST-WITHOUT-FINAL | 123 | 0.176 | 内容扫描 | ☆ |
| OPEN-WITHOUT-WITH | 124 | 0.178 | 内容扫描 | ☆ |
| ZEPHYR-ENV-DIRECT-ACCESS | 125 | 0.178 | 内容扫描 | ☆ |
| SECRET-REGISTRY-CONSISTENCY | 127 | 0.171 | 结构校验（触发式） | 触发条件收窄 |
| REGISTRY-CODE-ANCHOR | 129 | 0.167 | 结构校验（触发式） | 触发条件收窄 |
| NO-SECRET-HARDCODE | 128 | 0.165 | 内容扫描 | ☆ |
| PERM-TRIGGER | 82 | 0.173 | 内容扫描 | ☆ |
| TRANSLATION-COVERAGE | 59 | 0.165 | 结构校验（触发式，docs） | 触发条件收窄 |
| NO-HARDCODED-URL | 98 | 0.199 | 内容扫描 | ☆ |
| CAP-CONSISTENCY | 101 | 0.176 | 结构校验 | 不适用 |
| SCRIPTS-IMPORT-INTEGRITY ★ | 104 | 0.185 | 内容扫描 | 已完成 |
| MCP-VERSION-FIELD | 126 | 0.176 | 内容扫描（触发式，MCP 文件） | 触发条件收窄 |
| FRONTEND-TRUTH-SOURCE | 136 | 0.163 | 结构校验（触发式，前端文件） | 触发条件收窄 |
| DEPGRAPH-PRE-REGISTRATION | 113 | 0.195 | 结构校验（PG 依赖） | ☆（逐 staged .py）+DB |
| NEW-FILE-DEPGRAPH-ENFORCEMENT | 58 | 0.174 | 结构校验（触发式） | ☆（逐新增文件） |
| RENAME-DEPGRAPH-SYNC | 39 | 0.167 | 结构校验（触发式） | 触发条件收窄 |
| DERIVATION-ANNOTATION | 114 | 0.195 | 内容扫描 | ☆ |
| BLUEPRINT-NODE-ID-HARDCODE | 57 | 0.167 | 内容扫描（docs） | ☆ |
| TEST-RESIDUE-SSOT | 56 | 0.168 | 内容扫描 | ☆ |
| SNAPSHOT-DRIFT | 63 | 0.167 | 结构校验（触发式） | 触发条件收窄 |
| SSOT-REDEFINITION | 65 | 0.158 | 结构校验（触发式） | ☆ |
| PURE-SHIM | 68 | 0.155 | 内容扫描 | ☆ |
| DERIVED-FILE-DELETION-PROTECTION | 46 | 0.148 | 结构校验（触发式） | 触发条件收窄 |
| VOCAB-HARDCODE | 80 | 0.165 | 内容扫描 | ☆ |
| NO-BARE-GETENV | 81 | 0.170 | 内容扫描 | ☆ |
| MSG-STYLE | 96 | 0.198 | 信号型（message） | 不适用 |
| MSG-EXPOSURE | 83 | 0.173 | 信号型（message） | 不适用 |
| MANUAL-ONLY-PERMANENT | 43 | 0.168 | 结构校验（触发式） | 触发条件收窄 |
| ALGO-NOTE-SYNC | 62 | 0.177 | 内容扫描 | ☆ |
| EXEMPT-ZONE-FM | 87 | 0.171 | 结构校验（触发式） | ☆ |
| COMMIT-SCOPE | 48 | 0.176 | 结构校验（commit 范围） | 本来只查 files 参数 |
| CH-BATCH-SIZE / CH-FINAL-GATE / CH-VERSION-COL | 36/37/38 | 0.166 | 内容扫描 | ☆ |
| DATETIME-NOW-FORBIDDEN | 34 | 0.164 | 内容扫描 | ☆ |
| HOT-FILE-BASE-FRESHNESS | 47 | 0.000 | 信号型 | 不适用 |
| DEPGRAPH-FRESHNESS | 67 | 0.047 | 信号型（DB/staleness） | 不适用 |
| HELD-OVERLAP | 50 | 0.001 | 信号型 | 不适用 |
| FOREIGN-CHANGE-DETECTION | 45 | 0.017 | 信号型 | 不适用 |
| WORKTREE-REQUIRED | 44 | 0.002 | 信号型 | 不适用 |
| SESSION-REQUIRED | 31 | 0.000 | 信号型 | 不适用 |
| CLAIM-REQUIRED | 40 | 0.000 | 信号型 | 不适用 |
| FORGED-GW-MARKER | 29 | 0.000 | 信号型（message） | 不适用 |
| PROTECTED-PATHS | 28 | 0.002 | 结构校验（路径保护） | 不适用（全局保护语义） |
| R5-DIGIT-SUFFIX | 35 | 0.000 | 结构校验（命名） | 本来只查 files |
| RULE-EXECUTION-PAIRING | 61 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| DATA-TASK-COMPLETENESS | 41 | 0.000 | 结构校验 | 不适用 |
| ID-UNIQUENESS | 86 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| MODULE-ID-CONSISTENCY | 88 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| GATE-PANORAMA-ALIGNMENT | 830 | 0.181 | 结构校验（触发式） | 触发条件收窄 |
| META-TESTS-COVERAGE | 99 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| RULING-COMMIT-VERIFIED | 109 | 0.000 | 信号型（message 裁定标记） | 不适用 |
| CAPABILITY-LOOKUP-REQUIRED | 110 | 0.000 | 信号型（message 标记） | 不适用 |
| GATE-PRECOMMIT-OFFLINE | 111 | 0.000 | 信号型 | 不适用 |
| RECONCILER-FILE-OPS | 117 | 0.000 | 内容扫描（触发式，删除/移动原语） | ☆ |
| ISSUE-RESOLVED-INTEGRITY | 130 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| GATE-ERRCODE-CONSISTENCY | 131 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| SCHEMA-FILE-EXISTS | 121 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| BUSINESS-REGISTRY | 139 | 0.000 | 结构校验（触发式） | 触发条件收窄 |
| GATE-BATTLE-MAP-ALIGNMENT | 833 | 0.000 | 结构校验（触发式） | 触发条件收窄 |

> 注：★=已 own-scope；☆=推荐进入 own-scope 推广批次（约 30+ 个内容扫描/逐文件触发式 gate——与用户简报"余下约 9 个"的口径差异说明：简报所指 9 个应为 `_diff_helpers` 既有消费方族的直接迁移；本表 ☆ 为按实测数据扩展的完整候选池，**准入仍需逐 gate 审批语义等价**，机械活执行时以 _build_own_scope None→退化全量的保守语义为底线）。完整 106 行明细（含 detail/error 字段）见 `.runtime/tmp/gate_timing_results.json`。

**耗时量级结论**（JSON 精确统计）：0.000-0.05s（信号/快路径）= 24 个；0.15-0.25s（子进程税带）= **68 个，合计 12.52s**；0.3-1s = 6 个；1-5s = 4 个；>5s = 1 个（DECISION-MAP）；另有 0.047-0.27s 零星信号 gate。子进程税带是"数量 × 单价"型成本（68×~0.18s），重 gate 是"单价"型成本（前 5 合计 23.73s，占全链 57%）——两类治理手段不同（A2 合并执行 vs A3/预跑/触发收窄）。

### 2.7 功能等价性审计（Owner 复审回应：功能效果不变、只提速提效）

本方案第一约束=**行为等价**：所有优化不得改变门禁的判定语义、阻断语义、fail-open/fail-closed 边界与审计留痕。逐项自审结论：

| 工作项 | 等价性判定 | 说明 |
|--------|-----------|------|
| ①--wait 参数化 | ✅ 严格等价 | 缺省 60s 不变；锁的串行化/TTL/僵尸清理/O_EXCL 语义全部不动，仅等待时长可配 |
| ②死信 triage | ✅ 严格等价 | 纯运营工具，不触碰提交路径 |
| ③文档纠偏 | ✅ 严格等价 | 注释纠偏 |
| ④own-scope 推广 | ✅ 群体等价（检测主体转移） | 从"任一提交者扫全量 staged"改为"各提交者扫各自+外来落 jsonl 审计"；覆盖保证=每个文件必然随其归属会话过闸（全部提交走唯一入口）；项目既定方向（#ARCH-GATE-OWN-SCOPE-001，前 5 gate 已落地先例） |
| ⑤A1 输入 memoization | ✅ 严格等价 | 同一调用内相同输入只算一次，判定逻辑零改动 |
| ⑤A2 checker 合并 | ✅ 等价（需验收） | 同一脚本同参数执行；验收=改造前后逐 gate 结果 diff（计时 harness 复用为验收工具） |
| ⑥队列运营收尾 | ✅ 严格等价 | 运营补强/可观测性/索引共享，不改任何判定与阻断语义 |
| ⑦预跑+指纹采信 | ✅ 严格等价（补强后） | 指纹四元组含 gate 输入清单 sha：任何 staged/HEAD/own_scope/注册表输入变化→锁内全量重跑；**兜底路径保证最坏=现状（更慢但永不更错）** |
| ⑧A3 持久缓存 | ✅ 有条件等价 | 输入面分析准入 + 输入 sha 入 key + 降级态不缓存；默认 flag OFF |
| 5a echo_guard 超时 10s | ❌ 检测行为变化 | 尾部场景检测覆盖收窄——**已移出 P0**，改为 Owner 明示的语义权衡项 |
| ⑨交互式提交入队 | ❌ 语义变更（同步→异步） | 本就列为 Owner 决策项，不属于"功能不变"范畴 |

**防漏检三道保险**（针对预跑/缓存两项）：
1. 指纹/key 不命中 → 锁内全量重跑（永远保底，最坏=现状）；
2. 降级态（CloneGuard degraded / DB fail-open / worktree skip）结果一律不缓存、不采信——防"检测器失效的侥幸通过"被洗白；
3. 白名单默认空集，逐 gate 输入面分析后准入，信号型永不准入。

---

## 3. 总体实施路线图

```
P0（严格行为等价，建议本周）
  ├─ ①--wait 参数化（§2.1 方案A，0.5h，含 LOCK_TIMEOUT 退避引导文案）
  ├─ ②队列死信 triage 启动 + 可观测性（§2.4-4a，1-2 天）
  ├─ ③文档纠偏：DECISION-MAP 头注释"毫秒级"→实测 8.2s（防再误判，随①同批）
  └─ 附注：own-scope 推广批（已在派）照常推进——群体等价+审计留痕（§2.7）；
     echo_guard 超时下调已移出 P0（检测语义权衡，§2.5-5a / §5-2）

P1（1-2 周，行为等价类优化）
  ├─ ④own-scope 推广批扩充：_diff_helpers 族 9 个 + CAPABILITY-OVERLAP/ENCODING-SAFETY/NO-BARE-SQL 三个高优候选
  ├─ ⑤A1 共享输入 memoization + A2 checker 合并执行（§2.2，消 12.5s 子进程税）
  └─ ⑥队列运营补强收尾（worktree 内 CloneGuard 索引方案 / task_board 联动）

P2（Owner 决策后立项，flag 门控）
  ├─ ⑦锁外预跑+指纹采信（§2.3 方案A，flag gate_preflight，指纹含 gate 输入清单 sha）
  ├─ ⑧门禁结果持久缓存白名单子集（§2.2 A3，flag gate_result_cache，输入面分析准入）
  └─ ⑨交互式提交入队（§2.4-4b，flag commit_queue_interactive）
```

**预期收益量化**：锁内时间现状 ~45-50s → P0/P1 后 ~30s（-40%）→ P2 全量后 ~5-8s（-85%）；AI 会话侧从"60s 超时 × N 轮盲目重试"变为"--wait 一次等待到位（或队列 qid 异步）"；多会话互锁 2 小时类事故的复发面收窄至 signal gate 毫秒级窗口。

---

## 4. 风险登记与回滚总表

| 工作项 | 主要风险 | 缓解 | 回滚 |
|--------|---------|------|------|
| ①--wait | 极低；MODIFY-GUARD 不触碰（timeout 不在保护清单） | 原型已验证；缺省=现状 | revert 单 commit |
| ②死信 triage | 低（处置误删→retry/purge 双通道+审计） | 856 项先报表后处置，Owner 授权批量清理 | 死信文件不物理删（purge 移 .runtime/archive） |
| ④own-scope | 低（语义等价风险：某 gate 有隐性全量依赖） | _build_own_scope None→退化全量底线；逐 gate 红蓝用例；外来文件落审计不静默丢弃 | 逐 gate revert |
| ⑤A1/A2 | 中（A2 基建改动+故障隔离重设计） | 行为等价回归：106 gate 明细 diff 对比（harness 复用为验收工具） | revert |
| ⑦预跑 | 中（白名单漏分类=漏检） | 白名单默认空集逐个准入；指纹不一致永远回退全量重跑；红蓝四组用例 | flag OFF |
| ⑧缓存 | 中（降级态洗白） | 只缓存非降态 PASS；key 五元组；TTL+HEAD 失效 | flag OFF + 删缓存目录 |
| ⑨交互入队 | 高（提交语义变更） | §2.4-4b 六项前置条件；docs 域灰度两周；assert_single_writer_dev_history 日检 | flag OFF（存量 drain 后关） |
| 5a echo_guard 10s（语义权衡项，默认不做） | **检测语义权衡**：尾部扫描降级 warn-only，覆盖收窄 | 快路径 0.44s 实测余量充足；先 5b 根因治理再评估 | 配置改回 30 |

---

## 5. 待 Owner 决策事项

1. **P0 三项是否批准立即施工**（①②③，合计 ≤2 人天，零行为语义变更）。
2. **echo_guard 超时 30→10s（语义权衡确认）**：该项**非严格行为等价**（尾部检测覆盖收窄，§2.7），默认不做；若接受权衡，建议顺序=先做 5b 根因治理（rescan.signal/索引健康），观察 30s 超时是否自然消失，再决定是否调参。
3. **死信 856 项**：授权先出报表，批量清理（purge）需二次确认。
4. **DECISION-MAP 8.24s 恒跑**：接受现状（防断链设计）vs 立项"按触发文件降频"（staged 未触及 trading_decision_map/相关注册表时跳过——语义弱化为"触发式"，需 Owner 认可断链防护窗口收窄）。
5. **P2 三项是否立项**（⑦⑧⑨），及 flag 开启窗口安排（宪章 B-007）。
6. **--wait 默认值**：维持 60.0（推荐）vs 调整为 120/180（直接缓解轮询，但不解决占锁时长本身）。

---

## 6. 原型验证记录（最小施工合规）

### 6.1 --wait 参数化沙箱验证（PASS）
- 脚本：`.runtime/tmp/wait_proto_st_perf_plan.py`（gitignored，不入库）
- 方法：导入生产 `_GlobalCommitLock` 类（零改动），锁文件指向 `.runtime/tmp/lockproto/` 沙箱目录与真实锁隔离；子进程持锁 9s → 主进程 `timeout=3.0` 抢锁
- 结果：GatewayError 于 **3.09s** 抛出（期望 3.0s，0.1s 轮询粒度符合）；默认 60.0s 复核通过；锁释放后正常获取（自清正常）
- 结论：**timeout 透传机制已在生产类中存在且行为正确**；--wait 特性 = 纯管道改动（CLI argparse → commit() 签名 → 两处 with 语句），正式施工清单见 §7

### 6.2 106 gate 计时 harness（只读取证）
- 脚本：`.runtime/tmp/gate_timing_harness_st_perf_plan.py`；结果：`.runtime/tmp/gate_timing_results.json`
- 方法：构造 GitCommitGateway（只装配注册表，无锁无提交），逐 gate 调用 `spec.check(gw, files, **kwargs)` 计时；files=代表性文档+注册表 yaml；当时共享暂存区含 st-legacy-clear-20260910 的 WIP（真实混合场景）
- 结果：总计 **41.38s**（harness 外层计时；106 gate 逐项求和 41.37s，差值为循环开销），明细见表格与 JSON；该 harness 可复用为 ⑤A2 的验收工具（改造前后逐 gate 耗时对比）

### 6.3 未做的事（合规边界）
- 未修改任何 tracked 源码文件；未获取真实全局锁；未做打点日志落码（check_all 无逐 gate 计时埋点——harness 已达成同目的取证，正式打点建议随 ⑤A2 一并设计，避免两次改动）

---

## 7. 正式施工清单（Owner 批准 P0 后执行）

1. `scripts/git_commit.py`：argparse 增加 `--wait`（type=float，default=None→gateway 内部取 60.0；help 注明 0=立即失败、上限 1800）；`gw.commit(...)` 透传 `lock_wait_timeout=args.wait`；LOCK_TIMEOUT 行 help_text 增补指数退避引导。~10 行。
2. `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`：`commit()` 签名加 `lock_wait_timeout: float | None = None`（L1658-1670）；L1779 一处 `with _GlobalCommitLock(self.project_root, timeout=lock_wait_timeout if lock_wait_timeout is not None else _LOCK_TIMEOUT_DEFAULT)`。~8 行。**不触碰 L9 MODIFY-GUARD 保护字段**。
   **施工偏差记录（2026-09-10 开工实测）**：①L2712 `_commit_auto` **未**透传——其调用方为后台 reconciler（无 CLI 通道），默认 60s 即其语义，最小变更原则不引入无消费方的参数；reconciler 场景如需等待再单独立项。②测试实际落位 `tests/git/test_git_commit_gateway.py`（git/ 子目录，本文件 2415 行既有约定；方案原写 tests/test_git_commit_gateway.py 不存在）。③验收：新增 3 用例 + 既有 TestGlobalCommitLock 回归 6/6 绿 + commit 流程回归 7/7 绿 + `--help` 显示 --wait。
3. `tests/test_git_commit_gateway.py`：3 例（缺省 60s 常量 / 自定义 timeout 抛 GatewayError 时长 / --wait 0 立即失败语义）。
4. 同 commit 附带：DECISION-MAP gate 头注释耗时口径纠偏（③）。
5. （echo_guard 超时调整**不在本清单**——语义权衡项，待 Owner §5-2 明示后单独执行。）
6. 提交纪律：session st-perf-plan-20260910 走 `python scripts/git_commit.py`（禁裸 commit）；遇 FOREIGN_CHANGE→--adopt-prior-work；WORKTREE-REQUIRED→--allow-non-worktree；TRACKED-DRIFT→--allow-tracked-drift（按需逐个加，禁一把梭）。

**施工状态总账（2026-09-11 收工盘点，st-perf-plan-20260910）**
- P0① --wait 参数化：**已落地**（91d1ae4246，偏差见上条第②款施工偏差记录）
- P0③ DECISION-MAP 耗时口径纠偏：**已落地**（91d1ae4246）
- P0② 死信 triage：**已完成并超预期**——根因实锤=serializer worktree 的 .git 被红队测试改写指向已删除 pytest 临时仓（自愈校验只验存在不验有效，8 天漏检）；运营侧已清残骸重建复活；代码四连修复：LandingEnvironmentError 环境失败/物品失败分离（a4a6d7098e）→ 瞬态 git 锁争用转环境专类（53916fd13b）→ CLI drain 接真 landing 治"假 done"footgun（6e2d438467）→ 直跑 sys.path 补丁（53fa0b431a）；tests/conftest.py autouse 队列隔离 fixture（ZEPHYR_COMMIT_QUEUE_DIR）；回归 110/110 分文件全绿；requeue 试点 10 项（2 项成功重排队尾、6 项甄别 hot.txt 污染残留为 purge 候选）
- **移交下一会话**（交接指令已备）：dead/ 933 项分批处置（污染残留列 purge 清单报 Owner 批；正常项 requeue+drain 分批）+ 死信率告警最小落地（Owner 已裁定要做）
- P1④⑤⑥ / P2⑦⑧⑨：**均未施工**，待 Owner 批准（P2 全部 flag 默认 OFF）；echo_guard 超时 30→10s 维持不做（语义权衡项，待 §5-2 明示）

---

## 8. 附录：证据索引

- 锁类：git_commit_gateway.py L141-146（常量）、L231-336（_GlobalCommitLock）、L1775-1841（交互式临界区）、L2605-2771（_commit_auto + 队列改道）、L343-360（fail-open 审计）
- CLI：scripts/git_commit.py L8（INVARIANTS 禁裸 commit）、L13（exit code 契约）、L473-627（argparse 全参数）、L686-697（commit 调用）
- gate 基建：commit_gate_registry.py L308-433（GateSpec/check_all 无短路）；in_process_gate_registry.yaml（106 条真源）
- CloneGuard：clone_guard.yml（L1 配置：redup 禁用注释 B22②）、orchestrator.py L258-303（引擎集）/L305-344（_suppress_acknowledged）/L346-424（check）/L665-723（并发+顺序回退）、config.py L77-126（超时/降级默认）、echo_guard_adapter.py L96-97（embedding 锁 60s）/L229-275（detect 降级路径）
- 队列：flags.yaml L80-83（flag ON 8 天注记）、commit_queue_landing.py L1-17（不变量）、architecture_issue_registry.yaml L16893-16919（#ARCH-COMMIT-QUEUE-MVP-001 全条目）
- own-scope：_diff_helpers.py L435-523（三件套）
- 实测：.runtime/tmp/gate_timing_results.json（106 gate 明细）、.runtime/tmp/wait_proto_st_perf_plan.py（原型）、gw_*.log（23× echo_guard 超时）、.runtime/commit_queue/（dead=856/blobs=2086 清点）

---

## 9. 审查记录（循环审查日志）

> Owner 要求：循环审查直到**连续两轮零问题**，然后再加审一轮。每轮发现与处置全留痕。

**Round 1（2026-09-10 18:45，全文精读 + JSON 精确统计复核）：发现 19 处，全部修复**
1. 【数字】子进程税带 "~65 个/≈12s"（§0.1）与 "≈62 个"（§2.6）不一致 → JSON 精确统计：**68 个/12.52s**（0.150-0.250s 带），全文档统一
2. 【数字】"~20 个 0.000s" → 精确 **19 个**
3. 【数字】耗时量级结论四档计数修正（24/68/6/4/1，Top5=23.73s 占 57%）
4. 【数字】§6.2 总耗时 41.378s（外层）与逐项求和 41.373s 并存 → 标注口径差
5. 【引用】§0.1 "（§8.2）" → §6.2（附录无小节）
6. 【引用】§2.1 "（§8.1）" → §6.1
7. 【引用】§2.2 A3 "§4 分级清单" → §2.6
8. 【引用】§2.3 步骤1 "§4 白名单" → §2.6
9. 【引用】§2.3 对照表 "§4 分级清单" → §2.6
10. 【结构】§2.6 冗余占位行 "RULING-REFERENCE 以下零散…"（与前文重复+坏引用 §8.3）→ 删除
11. 【结构】GATE-PANORAMA-ALIGNMENT（0.181s）挤在"快路径族"行内矛盾 → 拆出单列
12. 【编号】§4 风险表用旧编号体系与 §3 新路线图不一致 → 全表按 P0①②③/P1④⑤⑥/P2⑦⑧⑨ 重排
13. 【缺行】§2.7 等价性表缺 ⑥队列运营收尾 → 补（严格等价）
14. 【缺行】§4 风险表缺 ⑥队列运营收尾 → 随 12 重排补入
15. 【规格缺口】§2.3 未写明 drift-watch 在预跑段/锁内段的归属 → 补"预跑段漂移只记审计，硬阻断语义只归锁内段"
16. 【设计补强】§2.2 A2 缺故障隔离要求 → 补"单 checker 崩溃不得影响他者，逐 checker 超时改 supervisor 内调度"
17. 【摘要】P0 "两项+文档纠偏" 歧义 → 统一 "P0 三项"；P1 "两项" → 三项
18. 【措辞】§6.3 "未修改任何 tracked 文件" → "tracked 源码文件"
19. 【一致性】"65 gate 明细 diff"（§4）→ 106 gate 全量 diff

**Round 2（2026-09-10 18:55，修复后全文重读 + 脚本核对表覆盖完整性）：发现 3 处，全部修复**
1. 【结构】§9 误插在 §6 与 §7 之间 → 移至文末（§8 之后）
2. 【完整性】§2.6 分级表缺 5 gate（脚本比对 JSON 全集发现）：TRANSLATION-COVERAGE(59/0.165)、NO-HARDCODED-URL(98/0.199)、CAP-CONSISTENCY(101/0.176)、MCP-VERSION-FIELD(126/0.176)、FRONTEND-TRUTH-SOURCE(136/0.163)；另 SCRIPTS-IMPORT-INTEGRITY(104/0.185,★) 仅在文字段出现无表格行 → 6 行全部补入，脚本复核 106/106 全覆盖
3. 【一致性】§2.3 现状取证 "子进程税 ~12s" → 12.5s

**Round 3（2026-09-10 19:00，脚本复核 106/106 逐行覆盖+章节顺序 + 全文精读）：发现 2 处，全部修复**
1. 【完整性】§2.6 快路径族合并行（10 gate 挤在一行）逐行级不可查 → 展开为 10 个独立行，脚本复核 **106/106 全覆盖**
2. 【措辞】头部纪律行 "未触碰任何 tracked 文件" → "tracked 源码文件"（方案文档本身即 tracked 交付物，与 §6.3 口径对齐）

**Round 4（2026-09-10 19:10，全量 grep 一致性清扫 + 表格结构复核）：零问题**
- 陈旧模式清扫（65个/≈62/~12s/41.378/41.373/§8.1/§8.2/§8.3/§4分级/§4白名单/⑥A2/⑩ 等 13 组模式）：9 处命中**全部位于本 §9 日志区的历史引用**（L449-472），活体内容零残留；表格 129 行结构完整；编号 ⑦⑧⑨ 各 5 处一致、无 ⑩ 残留

**Round 5（2026-09-10 19:15，独立重复清扫 + stdin 管道终检）：零问题——连续两轮零问题达成**
- 活体区（§9 之前 443 行）13 组陈旧模式零残留；分级表覆盖 **106/106**；章节顺序 0-8 正确；数字口径与 JSON 实测一致（总 41.37s / 税带 68 个 12.52s）

**Round 6（2026-09-10 19:18，按 Owner 要求加审——语义终审视角）：零问题——循环审查收敛**
- §2.7 等价性表 12 行逐行复核判定成立；§2.3 安全论证 6 条逻辑自洽（含 drift-watch 归属补强）；§5 六项决策与正文一致；§3 收益量化算术核对（45-50s → 30s → 5-8s）成立
- **收敛结论：R4+R5 连续两轮零问题，R6 加审零问题，满足"连续两次审查没有任何问题后再次审查"的 Owner 标准**
