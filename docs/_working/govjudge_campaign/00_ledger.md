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

### 事故二：本班自己踩中 R9 同款形状（复刻实证）
- R9 袋拆两笔提交期间，本班心跳守护（PID 17052，锚主区 .runtime）idle>1800s 自退（23:17:42Z，末行 exited reason=idle timeout）→ TAKEOVER-PENDING 闸把 st-govjudge-20261010 判死挡提交——与宪法§0袋三死袋完全同款：守护自退残留→会话被终审。
- 处置：SessionRegistry(worktree).register（W-29 chief-form 核验 fail-open 降级 logical=False，pid=0+90s 心跳轨）+`_spawn_heartbeat_daemon`（exited 残留守卫无条件重 spawn 正道）重锚 pid=46332 写 worktree .runtime。owner 会话在岗，非接管场景，无需 --resolve。
- 注：守护当初锚主区系 session_worktree create 时 cwd 在主区所致；重锚后锚定 worktree 与提交闸同根。收尾时主区残留 exited 心跳+陈册条目随 TTL/清理通道自然退场（台账备记）。

## R10 TrialLedger CAS ×10（完成·纯取证，零改码）
- 真身定位：告警源=`n_trial_ledger.py::_cas_update`（retry 上限恰 10，无 sleep——永久模块禁时间触发）；告警落点=Python logger（未持久化），**非**分数册字段——统筹令"已如实入分数行"系 examchief campaign ledger 叙事转述，册面实证（HEAD 及 10c78ff933 提交时点）rows 内均无 ledger_warning 键，本台账勘误。
- 判别（机制面证据链）：×10 恰等于重试上限=**确定性病灶签名**（瞬态 sha 冲突不会次次撞满）；真因=TrialLedger safe_dump 往返丢注释/空行 → safe_write_text 注册表族 mass-edit 保护**确定性误拒**（examchief campaign ledger 亦自述"撞注册表族保护"）——非双写竞态、非 R9 热册物化竞态同根（trial_ledger_registry 为直写 CAS 册非投影册，ROOR/册头双证）。
- 修复在码：增补令 2026-10-10 条目级无损基线（`_entry_fingerprints` 旧⊆新零蒸发断言 + allow_mass_edit 放行）已在 HEAD；tests/backtest/test_n_trial_ledger_t0_family.py + tests/gov/governance/test_registry_write_guards.py 共 13 passed 实证。
- 无丢写：无损断言兜底零条目蒸发；最终记账成功（分数行无告警残留）。
- 双 PID 精确时窗：日志面无落盘+二号会话日志域禁碰，不可考；机制判别已闭环，不阻收敛结论。
- 处置：零新改码（修复已在位）；本结论入台账+99_delivery。

## R11 政策 v2.2.0（完成）
- adjudication_routing_policy.md：frontmatter version 2.1.0→2.2.0；§2.4 后插 §2.5 Gate A（五判据 A1-A5+判定问句+任一假出通道+保留面边界+裁定#505 判例+机检化路线，全文按令逐字）；切换记录增 v2.2.0 行（含净零声明+测试声明）。
- 测试：tests/gov/governance/test_adjudication_routing_gate_a.py 4 例（章节/五判据/边界/版本+切换记录存在性锁）全绿；tests/ 豁免 creation token。
- 权源口径：Owner 直令凌驾月度合并窗，按 v2.1.0 先例直落（切换记录即权源载体，无新裁定号）。

## R4 CWM 回边判据（进行中）

## R5②③ 情绪快照器三册（进行中）

## R6 ADR/RFC 对表（进行中）
