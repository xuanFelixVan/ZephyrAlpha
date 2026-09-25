---
ttl: task_bound
---

# T1 落地后三账读数 + D3 判定（分包1）

> 时刻 2026-09-24 ~21:1x ｜ 统筹 st-commitspeed-tbl-20260924
> 批一（装表 A1A2A3 + D3 熄火 + B4 排队键）已于 **20:27 经队列项 0005 落地进 dev HEAD**（实测 HEAD 内 landing_phase_stats/pool_wave/residual_ms/_run_pool_wave 俱在）。

## 一、三张新账——当前全部未产出（因守护未换血）

| 账本 | 期望路径 | 实测 | 含义 |
|---|---|---|---|
| A2 八段相位+residual_ms | `.runtime/commit_queue/worktrees/w*/.runtime/audit/landing_phase_stats.jsonl` | **不存在** | 新码未在活进程执行 |
| A3 工线程出口 | `.runtime/commit_queue/pool_wave.log` | **不存在** | 同上 |
| A1 快段计费 | `precommit_channel_stats.jsonl` | **不存在** | 同上 |

⇒ "slow_item 755 秒花在哪段"这一问，**要等守护加载新码、真实落一件后才答**（当前无从读）。

## 二、T2④ D3 判定：仍单路 w2（未证伪修复，是修复没被加载）

`gate_execution_stats.jsonl` 四工 mtime（21:1x）：
- w0 = 06:22（死）
- w1 = 06:22（死）
- **w2 = 21:11（唯一在动）**
- w3 = 06:00（死）

判读：**不是 D3 修复被证伪**（修复在 HEAD 内、逻辑成立），而是**承载旧码的 belt 守护进程（pid 41380，启动 05:14，早于 20:27 落地）尚未经 `_check_and_reexec`（裁定#281 安全点原地 re-exec）换血到新码**。

换血未发生的根因（实测推断）：
1. 队列 50+ pending 使守护**持续 drain、几乎不释放 lease**→到不了"两轮 drain 之间"的安全点→re-exec 不触发＝**鸡生蛋**（积压正是 D3 要清除的对象）。
2. 次要面：`_commit_queue_epoch` 注释自陈"改 scripts/ 根不触发换血"，但 gateway 在 `_PRIMARY_SUBTREE`（gov_enforcement）子树，理论可触发——故卡点是 (1) 非 (2)。

落地 20:27 → 判定 21:11 ＝ **超 44 分钟，过 §30 分钟线**。按分包1 指令此分支＝登记 max_ruling_queue 申请 Owner 重启窗（见 MQ-5）。**未 kill 守护**（红线）。

## 三、待守护换血/重启后的复检清单（接力执行）
1. 换血后落一件 → 三张新账应出现 → 读 residual_ms 归属答"755 秒在哪段"。
2. 四工 `gate_execution_stats.jsonl` mtime 应全部前进（真 4 路）；若重启后仍只 w2 动 → 才是真 D3 证伪，另案。
3. 恢复并发后启 D4 四探针巡检（pending∩done、同 qid 多份 done、processing 并发数、四工 mtime）。

## 四、附带事实
- 原 0001 死因＝stale 入队快照含 B905/B009（worktree 已事后修好）；requeue（→0007）因批一已由 0005 落地、基底漂移被 §6.4 重校验正确拒绝（修复在起作用，非事故）。
- 0002/0006（战役文档袋）死于 capability_canonical_file_registry 三向合并失败——纯文档批，低优先，待后处理。
- 0003/0008（钩袋 T6）0008 仍 pending 在排。

## 五、换血后复检（21:46 守护自解 —— 推翻上文"仍未换血"，此为终态）

21:46:31 belt 守护由 `_check_and_reexec`（裁定#281）原地 re-exec（旧 pid 41380→新 44656），**换血成功**：

- **四工 `landing_phase_stats.jsonl` 全产出**（w0 21:50 / w1 21:47 / w2 21:51 / w3 21:51），`gate_execution_stats` w1 亦回 21:52 前进 ⇒ **D3 四路并发实证生效（未证伪）**。MQ-5 自解。
- **A1 `precommit_channel_stats.jsonl` 已生成**（快段计费 live）。
- **A3 `pool_wave.log` 仍待**首次工线程"退出"事件写入（工在跑未退出，非缺陷）。

### "slow_item 755 秒花在哪段" —— 首份实测（非本役件，普通 3-file 落地 st-pipeline-final-0028）
`total_ms=286937`（287s）｜phases 归属：`snapshot=69297`(24%) `cas=30687`(11%) `sync=1843` `converge=1172` `baseline=1047` `worktree=78` `conflict=125` `prestage=218`｜`accounted=104467`｜**`residual_ms=182470`（63% 未归属）**。

判读：
1. **已归属最大项＝snapshot（69s，占 24%）** → 直指 分包4 衍生再生出窗 与 分包7 缓存键（快照重算）。
2. **cas 31s** → 锁内提交/CAS 段，关联 分包5 与 S6。
3. **residual 63% 是本轮最大靶**＝被计时相位之外吞掉（推断＝等全局提交锁/lease 的排队等待 + precommit 门禁链在相位外）。这正是 A2 装表设计预留的"下一轮装表靶子"。后续需再装一层把 residual 拆开（锁等待 vs 门禁链）。
4. 此件 287s 印证"单件分钟级"，与历史 p50 5.5 分同源。

⇒ 分包7（缓存键）/分包4（衍生出窗）/分包10（止血）的取舍现在**有实测底数可依**，不再凭猜。
