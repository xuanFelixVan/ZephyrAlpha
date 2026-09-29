---
ttl: task_bound
gate_selfdoc: GIT-DANGEROUS
---

# 红蓝对抗报告——提交链鲁棒性组场景①②③（2026-09-26，车道 csx-s1）

> 注：本报告为红蓝对抗交付件，正文第 63 行的 `git reset --hard` 为被测危险命令的文档化引用（非执行指引），按总包裁定 A3（2026-09-28）加 gate_selfdoc 豁免声明。

执行仓：worktree `.worktrees/csx-s1`。全沙盘：repo=pytest tmp_path（basetemp=`.runtime/tmp/csx_rb_bt`），
队列根一律 `.runtime/tmp/csx_rb_qroot/<uniq>`（自建自清）；未触生产 `.runtime/commit_queue/`、
主区 index/staged、生产 belt 守护。证尺：`tests/governance/test_redblue_robust.py`（18 测试），
每场景=绿尺（钉住修复后不变量）+红证尺（monkeypatch 开倒车/对照形态断言坏结果确实发生，证明尺敏感）。
GitCommitGateway 全程桩化（与 test_commit_queue_landing 同款约定）。稳定性：连续多轮全绿（含与
test_commit_queue_pool / test_commit_queue_ghost_pending / test_s1_immutable_tree_wire 同批跑）。

## 一、结论速览

| 场景 | 攻面 | 判据 | 结果 |
|---|---|---|---|
| ①杀工复活 | 工②桩异常死亡（BaseException 进程崩溃语义 / RuntimeError 在途异常语义） | D3 工不早退、余工消化完、死工项波首 `_recover_orphans` 回收、done 恒等于投入数 | ✅ 3/3（红证：`_WORKER_ERR_STREAK→0` 首错即 GIVEUP；发现 F2 契约分流） |
| ②双写者同路径 | 两线程同根并发 claim 同一文件；done 幽灵副本 | 原子 rename 恰一胜、败者重扫收 None；done 终态复查弃幽灵、done 无重复 | ✅ 4/4（红证：剥掉 done 复查的旧形 claim 必认领幽灵） |
| ③a index.lock/锁 | worktree index.lock 占用；全局提交锁 LOCK_TIMEOUT | 瞬态环境类退回 pending 绝不死信，锁释放自愈 | ✅ 4/4（红证：关瞬态分类→裸 RuntimeError＝死信入口） |
| ③b 盘满 | `os.replace` 抛 OSError(28) 打在 done 记账点 | 非死信、不丢失、幂等短路重入 done、每 qid 恰落地一次 | ✅ 3/3（红证：幂等判定失明→同件 dev 二次落地标记×2；发现 F1） |
| ③c import 崩 | gate 装载 ImportError→GateAutoRegistrationError | M5.2 分流：fresh fail=死信带处方 / fresh pass=退 pending 自愈；进程不崩 | ✅ 4/4（红证：分流失存→确定性册坏滞留 pending 活锁形态；发现 F4） |

## 二、场景① 杀工复活（D3）

**绿尺 1a（进程崩溃语义）**：工②首次 commit 抛 BaseException（码内契约：BaseException=进程崩溃，
项留 processing 等回收）。断言：done==8、dead==0、排空后 processing 空、**崩溃时在手项**经下一波
波首回收恰落地一次（标记恰一次+内容在 dev）、全部件内容零丢失。
**红→绿证据**：同构造下 `monkeypatch.setattr(cql, "_WORKER_ERR_STREAK", 0)`（旧码形态：首错即收工），
崩溃实例按 (worker_id, gen) 实例记账 commits==0（永不复活续做），而 done==N 依旧成立——证明
「done 恒等」单独不构成判别（死一工被余工掩盖的历史盲区），实例级 revival 断言才是真尺。

**绿尺 1b（RuntimeError 在途异常，任务书字面注入）**：工②抛 RuntimeError 后**实例复活续做**
（commits[崩溃实例]>=1），在手项按码内契约进死信（dead==1，dead_reason 含病灶、带处方，内容不混入
dev），其余 7 件全落。
**发现 F2（契约澄清，非缺陷）**：任务书「RuntimeError 模拟异常死亡→`_recover_orphans` 回收」与码内
契约不符——`_pool_process_item` 的泛化 `except Exception` 把 landing 内异常**就地转死信**（不卡队），
到不了工层 err_streak/`process_raised` 记账；只有**逃逸异常**（认领段 FileExistsError、记账段 OSError）
和 BaseException（进程崩溃→orphan 回收）走工层路径。杀工复活链（orphan 回收）仅 BaseException 形态
成立。已按真源分尺钉住两种语义。

**红尺 1c**：注入点取认领段（`_pool_claim_item` 对 w2 抛 FileExistsError×2）+`_WORKER_ERR_STREAK→0`
→ w2 首错即 GIVEUP（pool_wave.log 有 `claim_raised … GIVEUP`），而队列仍被余工+新波排空——
「并发度塌缩不在账面显形」的历史病灶形态可被本尺捕获。

**方法注**：按工**编号**记账会把下一波全新实例的作业误记成死工复活（伪绿盲区根源），账本按
`(worker_id, gen)` 实例键记账。

## 三、场景② 双写者同路径（D4）

**绿尺 2a（原子 rename 互斥）**：barrier 对齐两线程并发 `_pool_claim_item` 同一单项——恰一胜者
（文件落 processing 恰一份），败者 FileNotFoundError 重扫收 None，pending 清空。
**绿尺 2b（done 终态复查）**：pending 活副本 + done 同名并存（幽灵形态）→ 认领必须弃置（收 None、
不进 processing、清扫 pending 侧幽灵），done 恒 1 份。
**红尺 2b'（能红证明）**：monkeypatch `_pool_claim_item` 为「剥掉 done 终止性复查」的 D4 之前形态
→ 幽灵被认领成 processing、与 done 同名并存（双落地入口重开）——绿尺对该防护缺失敏感。
**绿尺 2c（双写者 enqueue 面）**：两线程同会话同路径并发 enqueue → 会话锁内 compaction 收敛恰一件，
排空后 done 文件数==1（无重复）。

## 四、场景③ 故障注入三小态

### 3a index.lock 占用 / 全局提交锁
**绿尺**：工棚私有 gitdir 真造 `index.lock`（git reset --hard 真撞锁，stderr 含
`Unable to create '…index.lock': File exists`）→ `_is_transient_git_error` 命中 → LandingEnvironmentError
（retried_key=env_retry 计数闸在位）→ 项退回 pending；锁释放后下一轮排空自愈落地（dead==0）。
全局提交锁面：桩 gateway 返回 `CommitStatus.LOCK_TIMEOUT` → landing 转环境专类、项退回 pending
（env_retry 记账），锁释放重排落地；附真源行为尺：持锁者健在时 `_GlobalCommitLock(timeout=0.5)`
按期抛 GatewayError（网关转 LOCK_TIMEOUT 的原料，快速失败 <5s）。
**红证**：`_is_transient_git_error→False`（2026-09-10 治本前形态）→ 同一撞锁错误以裸 RuntimeError
逃逸 `__call__`（池化泛化分支会判物品死信）——「环境类绝不死信」尺对分类缺失敏感。
**注**：env_retry 计数允许 1..2 的良性竞态（env_aborted 置旗前他工可再拾取同件一次），断言取 ≥1。

### 3b 盘满（OSError 28）
**绿尺**：一次性故障打在 `processing→done` 记账 rename（OSError 28, No space left on device）→
件不死信、不丢失：留 processing→下一波 `_recover_orphans` 回收→`_already_landed` 幂等短路
（landed_id 已在故障前持久化）→重入 done；终态判据全部锚**盘面**：done/ 文件==3、processing/pending
清空、每 qid dev 标记恰一次（不双落）、内容零丢失。
**红证（幂等失明）**：`_already_landed→None`（landed_id+标记 grep 双证皆废的旧态）→ 同件重放被放行、
`--allow-empty` 桩真产生第二次提交、dev 标记×2——「done 恒等于投入数」尺对幂等缺失敏感。
对照绿尺：幂等在位时重放短路返回已落 sha（与生产同款 `-F --grep` 口径），标记恒 1。

### 3c gate 装载 import 崩
**绿尺（M5.2 两支，参数化）**：`builtins.__import__` 对哨兵模块抛 ImportError→`_get_gateway` 包成真
GateAutoRegistrationError（复刻 auto_register_gates fail-closed 出口）：
- fresh probe **fail**（确定性册坏）→ 死信带处方（修册），pending 不滞留；
- fresh probe **pass**（纪元陈旧/瞬态 IO）→ 退 pending 记 env_retry（fail-open），自愈轮落地。
两支 drain 均正常返回（进程不崩），撤注入后链路仍可消化新件。
**红证**：`_is_gate_auto_registration_error→False`（分流失存=旧码形态）→ 确定性册坏走泛化 env 分支
滞留 pending（dead==0）——「死信+处方」尺对分流缺失敏感（活锁形态可见化）。
**绿尺（设施自崩 fail-open）**：`builtins.__import__` 对 registrar 模块本身抛 ImportError →
`_is_gate_auto_registration_error` 按类型名兜底仍 True（分流不错、判定不崩），且不扩大命中面
（普通 RuntimeError 仍 False）。

## 五、新发现问题（按严重度）

**F1（D4 残留竞态窗，建议 Owner 复核）**：`_mark_cascade_stale` 写后清扫（commit_queue.py:1311-1314）
与工线程认领 rename 存在竞态：回写重建 pending 副本后、清扫 `exists()` 检查前，若认领 rename 恰在
飞行中（processing 尚未可见），清扫双查皆 False→幽灵被保留→同件可被二次认领、二次完成。
红蓝实测复现 1 次（满载全套跑 ~1/10）：`stats.done=4 > 投入 3`，processed_qids 同 qid 两条
（q-…-df1-0001 ×2），即同件完成两次。语义面：幂等短路/标记 grep 使 dev 不至内容损坏，但
done 记账与 dev 提交数可能双计（若两副本都赶在首落前提交即真双落地）。处方建议：清扫改
「exists 检查后延时二扫」/ 以 mtime+内容比对仲裁 / `_mark_cascade_stale` 与认领共持 per-qid 路径锁。
测试侧处置：multi-item 池测以 `cq._mark_cascade_stale→[]` 隔离该窗（靶面注释留痕），3b 判据改锚盘面。

**F2（契约澄清）**：任务书口径「RuntimeError 异常死亡→orphan 回收」与码内 ERROR_CONTRACT 分流不符
（见场景①）；红蓝已按真源双尺钉住。后续任务书写码内契约名（BaseException=崩溃语义）可免歧义。

**F3（Windows 满载环境面）**：
- 单条 git 子进程可停顿 45s+（`_already_landed` 的 git log 实测挂起栈），落地链 120s git 超时
  兜底可自愈，但测试 per-test 预算需放宽——本尺按仓惯例对 6 个重池测加 `@pytest.mark.timeout(300)`。
- 刚被 rename 的项文件可被杀软/索引器短暂拒开（ERROR_ACCESS_DENIED 持续超 `_read_item` 的 1s
  重试窗，实测日志 `[drain] 队列项读取失败（疑似损坏，留待人工）`）→ 项退回 pending、本轮
  `wave_done==0` 提前收工。语义安全（下轮自举落地、绝不死信），但**单次 drain_queue_pool 不保证
  排空 pending**；生产由 belt 反复自举覆盖。测试以 `_drain_until_quiescent`/`_drain_with_stub`
  的「排空到盘面静止」重试壳对齐生产口径。
- 空仓起 k 工并发 `git worktree add` 会互踩（`fatal: failed to read .git/worktrees/w2/commondir`，
  env pending 自愈）——生产由常驻工棚规避，测试以 `_prewarm_worktrees` 串行预热对齐生产形态。

**F4（观察面小账）**：`_read_item` 整轮放弃会把项改名回 pending 且本轮 `wave_done` 不计，若该件是
队尾唯一件则本轮提前收工（F3 第 2 条的机制面）——下一轮自举恢复；旁路观测可留意「pending 非空但
wave_done==0」的形态频率，若生产频发可考虑 drain 内层对 pending 非空做有界续波。

## 六、未尽事项

1. F1 为真实生产竞态（低频、高后果面），未在本车道修生产码——建议 Owner 立修复单后，本尺
   `test_done_terminal_recheck_discards_ghost_no_duplicate` 家族可加「清扫窗二扫」判别构造。
2. 模块登记：新测试文件沿用 MOD-GOV-047 头（未走 add_module_translation.py 登记，未提交——
   提交前须过 CREATE-GUARD（tests/ 豁免）/TRANSLATION-COVERAGE 门禁核验）。
3. 报告与测试未走提交网关（本车道任务=落盘产物）；落库时按 RULE-WORKTREE 提交序列执行。
4. 恒绿尺自检：全部红证尺均以「开倒车/对照形态断言坏结果发生」实证敏感（1c/2b'/3a'/3b'/3c'），
   无两边都绿形态；3b 的盘面真相判据在 F1 修复后建议回归 `stats["done"]==n` 强断言。
