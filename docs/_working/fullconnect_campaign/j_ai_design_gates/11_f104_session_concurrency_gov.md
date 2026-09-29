---
ttl: task_bound
title: F104 会话并发治理——挖干案卷
session: zc-l10-20260927
updated: 2026-09-29
---

# F104 · 会话并发治理（session_concurrency+lock claim+worktree 四证）

> 总册行（00_全环节总册.md:179）：built｜上游 —｜下游 提交链｜P2｜G8
> 第一证据源：fullflow_mining/m3_governance/01_runtime_guards.md §3.6＋src/zephyr/security/access_control/session_concurrency.py＋scripts/git_commit.py

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 会话注册/心跳/claim 请求＋宪法 §2 并发队列协议（commit_queue 正门/--adopt-prior-work/释放-重 claim 序列） |
| 下游消费 | 提交链全族：git_commit.py 网关（1332 行）→commit_queue.py serializer→worktree 四证清理面；M3 04 矩阵"会话 claim/锁=双侧覆盖范例面" |
| 自动化触发 | 事件/调用触发（register/heartbeat/claim/release）；staleness 判活 `_is_session_alive`；锁文件 TTL+stale 判定（`_is_stale`:161/`_claim_expired_and_idle`:225 死会话回收+审计）；无 cron |
| 真源与注册表 | src/zephyr/security/access_control/session_concurrency.py（**902 行**，M3 01 §3.6 逐件锚）（已过时，见刷新批注——W-29 后现 935 行）＋lock_files.py（1659 行）＋scripts/session_worktree.py（S2 四证，:338/:347/:468 本日 grep 实证，真源 worktree_cleanup_sop.md） |
| 门禁与质量尺 | WORKTREE-REQUIRED/CLAIM-REQUIRED 门（C1 卷宗"并发毁伤面，有效拦截榜"）；SessionConflictDetector（:861）；依赖登记 find_breaking_change_session |
| 当前运行状态 | built（黄）：结构+范例面地位成立；但 session_claim 守护件被 §1.6 判"疑似判据失效（有调用方零测试）" |

## 二、子模块三级枚举（M3 01 §3.6 锚+本日复证实证）

1. **SessionRegistry（session_concurrency.py:295）**：register/heartbeat/unregister｜claim_file/claim_files_batch/release_files/release_files_batch｜other_held_files｜staleness 判活（:266）｜依赖登记 register_dependency/find_breaking_change_session。
2. **配套三件（同文件）**：SessionHandoff 交接包（:786）｜SessionConflictDetector（:861）｜ConcurrencyManager/pre_allocate（:108）。
3. **锁文件族 lock_files.py（1659 行）**：claim/acquire/release/cleanup/salvage＋TTL＋stale 判定（死会话回收+审计）＋registry mutex（:116）＋批量 acquire/release（:674/:722）；死会话 stale claim 挡道→`gateway.release_files('<死sid>', files)` 精准释放（宪法 §2.7）。
4. **worktree 四证（scripts/session_worktree.py）**：S2 四证检查（2026-08-14 wipe 事故治本；:338 merge 场景豁免证 1 会话活跃仍走证 2/4 快照；:468 主检；--force-skip-checks 落审计 :478）。
5. **提交链消费面**：scripts/git_commit.py（1332 行，唯一合法 commit 入口的并发侧）＋commit_queue.py（--enqueue 队列正门/serializer worktree 干净暂存区结构性免疫连坐）＋_trusted_git_env 双定义（session_worktree.py:406 与 commit_queue_landing.py:727，FUNCTION-DUP 约束在案，M3 01 §3.5）。

## 三、接线四态独立复核

- 总册判 **built**：结构面成立（M3 04 矩阵将"会话 claim/锁"列为双侧覆盖范例面：门侧 WORKTREE/CLAIM-REQUIRED＋运行时 SessionRegistry/lock_files TTL/stale/salvage）。
- 独立复核打折点（§1.6）：**session_claim 列 C 类守护件"疑似判据失效（有调用方零测试）"**——运行态健康（本会话冷启动 cleanup CLEAN 惯例在案，M3 01 §3.6 运行态行）但判据无红证测试。
- 关联缺陷在案：B5 env 单因子信任（FAST_PATH_ENV 等 warn 不阻塞，#64 裁定 fail-visible）＋_trusted_git_env 双定义漂移风险（B4）——两处均"运行可用、判据未闭环"型。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | session_claim 零测试（判据失效嫌疑） | stale 抢占/salvage/死会话回收三场景配对红证 | P1 |
| G2 | _trusted_git_env 双定义（FUNCTION-DUP 约束） | 收敛单一真源+re-export（M3 01 B4 修法，S 工作量） | P1 |
| G3 | FAST_PATH_ENV/SERIALIZER_MODE 单因子 env 信任 | "仅网关进程可设"审计对账扩面（B5，与 F105 待裁同源） | P2 |
| G4 | 四证检查 --force-skip-checks 审计面无消费方对账 | skip 事件落审计后接周审计视图 | P2 |

## 五、自审闸三态

**结构面=挖干可施工**（902/1659/1332 行三件+四证锚行号全实证）；**判据红证=待施工**（G1/G2）；**env 信任绑定=待裁**（G3，Owner 门位，与 F105 合并呈批）。

## 六、复跑命令

```bash
wc -l src/zephyr/security/access_control/session_concurrency.py scripts/git_commit.py  # 902/1332
grep -n "S2 四证\|force-skip-checks" scripts/session_worktree.py | head -4
grep -n "_is_session_alive\|find_breaking_change_session" src/zephyr/security/access_control/session_concurrency.py | head -4
grep -rn "_trusted_git_env" src/zephyr/gov_enforcement/rule_bridge/session_worktree.py scripts/session_worktree.py | head -4  # B4 双定义
python scripts/lock_files.py cleanup  # 冷启动惯例核验（只读清理）
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更
- `48aa677f7f`（09-29 W-29 心跳守护修复·chief3 碰撞根因处方落地）：session_concurrency.py（+33，902→935 行）新增 logical 逻辑长会话标志（SessionInfo 字段+register(logical=) 形参+mark_logical() 原地翻转零触碰 held_files/last_activity）+heartbeat_daemon.py（+72）idle 超限逻辑会话豁免（keepalive 留痕不自退）+run_daemon max_iterations 测试接缝；tests/rule_bridge/test_heartbeat_daemon.py（+97）两态红绿测试。

### 缺口清单状态修订
- G1（session_claim 零测试）：**部分收敛**——心跳侧两态红证已落（idle 非逻辑会话自退／idle 逻辑会话 keepalive 存活+mark_logical 不丢 claim）；stale 抢占／salvage／死会话回收三场景配对红证仍未见，维持待施工。
- G2（_trusted_git_env 双定义）／G3（env 信任）／G4（skip 审计消费）：零改动，维持。
- 新增已闭：chief3 碰撞根因（活会话被判死丢 claim）——挖矿时点未立案，W-29 闭合。

### 自审闸三态
- **结构面=挖干可施工（维持）**；行数锚 902→935（勘误）；"判据红证=待施工"**部分翻面**（心跳侧已落，claim 三场景维持待施工）。
