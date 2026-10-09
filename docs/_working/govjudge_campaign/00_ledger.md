---
ttl: task_bound
completes_when: 治理判据班六件（R9/R10/R11/R4/R5②③/R6）全部落地+99_delivery 终报呈总统统筹+release 全部 claim+reaper keep 退订，即随批归档
title: 治理判据班台账（st-govjudge-20261010）
owner: ZephyrAlpha-Owner
session: st-govjudge-20261010
---

# 治理判据班台账（00_ledger）

> 六件：R9（ghost 拾取闸+宪法§0袋）/R10（CAS 告警取证）/R11（政策 v2.2.0）/R4（CWM 回边）/R5②③（情绪快照器三册）/R6（ADR/RFC 对表）。随做随记；收尾 99_delivery 逐件哈希+复核命令+红证清单。

## R9 ghost 拾取闸同源化 + 宪法 §0 袋解锁（最高优先）

### R9① 判死分支实锤（完成）
- 死袋族：`.runtime/commit_queue/dead/q-20261010-st-regsolo-20261010-0028/0029/0030`（read-only 取证，未碰一字节）。三袋皆 `meta.ghost=true`，dead_reason=canned 文案；0030 袋内容=depends-on 件（已被 fd3ccee5c1 另道落地，与本班无涉）。
- 三源谁说了算：`scripts/commit_queue.py::_session_ghost_dead` 第一分支=heartbeat.jsonl 末可解析行 `status=="exited"` 即短路判死；注册表在册性只在心跳文件**缺失**时兜底；90s 心跳新鲜度**全链不参与**。
- 事故形态：regsolo 守护 06:31:28 idle 自退（末行 `exited, reason=idle timeout`）→ 属主手工心跳刷新至注册表 0s 新鲜仍被判死——exited 残留被当会话终审=判定面与会话分片真值脱节（第四块拼图）。
- keeper 侧既有守卫（同源化目标）：`session_worktree._ensure_heartbeat_daemon` + `heartbeat_daemon.heartbeat_last_status`（统筹增补令③①）——"exited 残留=前代守护自退的死亡证明，mtime<900s 不得当活证"。

### R9②③ 治本+红证（完成，工作树已改，待提交）
- 改法：exited 短路降为「残留非终审」→ 落注册表活性终审 `_registry_session_alive`（S4-D 分片读+`session_concurrency._is_session_alive` 90s/TTL/pid 单一口径，禁私设第四套活性）；册设施缺席时 残留→死 / 无心跳信号→活（fail-open 原语义不变）；活心跳快路放行不问在册性。
- 红证 4 例（`TestGhostGatePickupAndBootstrap`，tests/gov/governance/test_commit_queue_integration.py）：
  1. `test_pickup_exited_residue_with_fresh_registry_passes`——事故形态复刻：exited 残留+0s 新鲜册→放行（未修码**红**）；
  2. `test_pickup_live_heartbeat_unregistered_still_passes`——R9③ 命名红证：活心跳+无册→放行（unregister 后合法重投通道；对 #459 原码即绿=防"活性终审化"矫枉过正的锁）；
  3. `test_pickup_exited_residue_with_stale_registry_entry_dead`——真幽灵不漏判（对原码绿=同判，锁新真源路径）；
  4. `test_pickup_registered_stale_entry_without_heartbeat_dead`——在册但过期→死（未修码**红**：原闸只看键存在不看新鲜度）。
- 判别力自证：`git stash push -- scripts/commit_queue.py` 后跑全类=2 红 5 绿；恢复后 7 绿。
- 回归：ghost 类 7/7+活性/belt/幽灵pending/pool 四套 69 passed；整文件 integration 见下。
- 施工注记：worktree 车道内显式队列根被 `_strip_lane_prefix`（修3，Owner 批 2026-10-05）重定向主仓同构路径——测试须 `--basetemp` 指主仓 `.runtime/tmp` 才能使 heartbeat/registry 夹具与闸读同根（主仓跑套件无此差异）。

### R9④ 宪法 §0 落地（完成，待提交）
- `.aidrafts/st-regsolo-20261010` staged AGENTS.md 单行 diff 已取（worktree 存活，冷启动 SALVAGED=merge skipped 但遗物在）。
- 本班 worktree AGENTS.md 经 `safe_write_text`（CAS）落同内容；写后 sha256=`eaf8a77d7f61…fd21` 与死袋 0028/0029 `blob_sha256` **逐字节一致**；进程外复读核实行 6 升位原文。
- 裁定#504（owner_sign 在册，HEAD 册行 4480）同 commit 原子兑现；骑手件（generate_front_door lookup state 行+llms.txt）已在 HEAD 无待落。

### R9⑤ 两枚具名册 staged 残影（按令停手上报，一字节未动）
- `ruling_registry.yaml` staged 残影=**裁定#505**（adjudicator=st-examchief-20261009，R3 离场族，authority=总统统筹包令）——非 dev HEAD 覆盖面，属他会话在途条目→**禁吞，不 restore**。PG 账本真源已含 #505/#506（本班 render 快照 v18 实证 324 entries），本班投影批机械承载全量 PG 态（归属字段无损），落袋后该残影自然收线。
- `architecture_issue_registry.yaml` staged 残影=删投影 GENERATED-FILE 头+删 #ARCH-TRD-A10（HEAD 在册实条目）+#ARCH-381 挪尾——对 HEAD 实质回退，疑 stale/hand-edited render 变体→**禁吞，不 restore，停手上报**（四号战役 §三 C1/C2/C5 触发器+examchief/fullflow2 归属方自查）。
- 另记（非在册清单，同行同族取证发现）：主区 staged `scripts/commit_queue.py`=对 HEAD 的旧版回退（撤 depends-on 顶层序列化+_deps_unsatisfied 拾取闸+cleanup 审计）混 1 个 encoding 小补丁；staged 新增 `tests/gov/governance/test_commit_queue.py`（HEAD 无此文件，monolithic 2051 行）。他会话在途物，本班未碰。

### R9 登记
- 裁定#507 已取号（next_ruling_id --claim，禁预占）并 api.register 入 PG 账本（version 1，snapshot v18）→publish_snapshot(repo_root 必传)→--render 三步正门；投影已同步本班 worktree。
- 台账件 creation_token：batch_creation_tokens 薄壳 `_REPO` 锚主仓看不到工作树新件（"无待登记文件"×2）——改自走意图 API 等价三步（api.register REG-CAPCAN-001/creation_tokens → publish_snapshot → --render）；账本在账（sha b5f300ee…），publish 首打撞 snapshot_version 155 并发竞态（DuplicateKey），重打 noop=True 收线（内容寻址幂等）。

### 施工事故与修复（cwd 漂移，已原位复原）
- 本执行环境 Bash cwd 会在调用间漂移回主仓——部分相对路径操作落在主区。实害两处，均已修复并核验：
  1. AGENTS.md 升位行 safe_write_text 落主区且被 staging 吸收 → 主区已 `restore --staged`+`checkout` 回 HEAD（sha 954233c9…=写前 before_sha 实证零残差）；正身字节在本班 worktree（eaf8a77d…）随袋走正门。
  2. 判别力自证的 `git stash push/pop -- scripts/commit_queue.py` 有一发落在主区，把主区该文件的 staged 态降为 unstaged（内容未变）→ 主区已 `git add` 复原 `M ` staged 态。
- claim 卫生：主区 4 枚误落 claim 已全部 RELEASED；5 件袋文件 claim 重打在本班 worktree（status 计 5 实证）。
- 教训入册：worktree 会话的一切文件操作与 pytest 必须同调用内显式 `cd` 锚定；相对路径在本环境不可信任。

## R10 TrialLedger CAS ×10（进行中）

## R11 政策 v2.2.0（进行中）

## R4 CWM 回边判据（进行中）

## R5②③ 情绪快照器三册（进行中）

## R6 ADR/RFC 对表（进行中）
