---
ttl: task_bound
---

# chief_lease_protocol.md — 总指挥租约协议（裁定#415 机械化配套）

> 车道：st-chieflease-20260928 | 2026-09-28 | 语义目录（无 _NN 日期后缀，R5 合规）
> 真源工具：`scripts/governance/chief_lease.py`（MOD-GOV-CHIEFLEASE，纯 stdlib）
> 租约状态文件：`.runtime/chief_lease.json`（sid / claimed_at / last_heartbeat / ttl_seconds=600）

## 0. 一键模板替换行（Owner 专用）

把历次复制粘贴指令里的 `你是总指挥` 整行替换为下面这一行（逐字粘贴）：

> 「身份：本任务的车道施工队。在任总包以 `python scripts/governance/chief_lease.py status` 为准——有活租约=你是工序队；无租约=你先 claim，claim 成功才升格总包。」

为什么是这一行：旧措辞让每个会话都自命唯一总包（裁定#415 根因）。新措辞把"总指挥"
从自称断言改成可机判的租约查册——自称只是职位申请，任命以租约册为准。

## 1. 自动降格语义（裁定#415，册载 2026-09-28）

```
自称总指挥 = 职位申请，非任命；
查册有活租约 = 自动为工序队；
无租约     = 先 claim，claim 成功才升格总包。
```

- 活租约判定：`last_heartbeat` 距今 < TTL（默认 600s）。
- claim 被拒（`reason=lease_held`，回报 holder sid）≠ 事故 = 自动降格为工序队的机判信号，
  拿到 holder sid 后向其靠拢（对齐其战役/工序队列）。
- 在任总包义务：定期 `heartbeat <sid>`（建议 ≤TTL/3 间隔一次）；收尾必 `release <sid>` 交班。
- 过期自动让位：heartbeat 断供超 TTL，租约自动作废，先 claim 者接任。
- 损坏自愈：租约文件损坏自动备份 `.corrupt-*.bak` 后按空位处理，领导权仲裁不卡死。

CLI 速查（rc：0 成功 / 1 仲裁失败 / 2 用法错误）：

```bash
python scripts/governance/chief_lease.py claim <sid>      # 申请（无活租约才成功）
python scripts/governance/chief_lease.py heartbeat <sid>  # 在任心跳续期
python scripts/governance/chief_lease.py release <sid>    # 交班（收尾必做）
python scripts/governance/chief_lease.py status           # 查册：CHIEF: <sid> | NONE
python scripts/governance/chief_lease.py --json status    # 机读模式（CI/编排用）
```

## 2. 三层治理地图（措辞 → 租约 → 路径租约）

| 层 | 仲裁对象 | 机制/真源 | 粒度 |
|----|----------|-----------|------|
| L1 模板措辞层 | "谁是总指挥"的**身份语义** | 本协议 §0 替换行：自称=申请，任命=查册（`chief_lease.py status`） | 会话级（全军唯一） |
| L2 总指挥租约层 | **在任唯一性**的机判执行 | `scripts/governance/chief_lease.py` → `.runtime/chief_lease.json`（O_EXCL 锁 + os.replace 原子落盘，TTL 600s） | 全仓唯一在任总包 |
| L3 S5② 路径租约层 | **文件级写权**（谁改哪个文件） | `lock_files.py acquire/release` 文件锁 + GitCommitGateway 提交门 + worktree 隔离（RULE-WORKTREE） | 文件级（多工序队并行互不连坐） |

三层关系：L1 决定"谁敢自称"；L2 机判"谁是唯一在任总包"（裁定#415 单写入点）；
L3 保证"在任总包+各工序队"写文件不互踩。L2 失守（租约过期无主）时，L3 文件锁仍是
最后一道防连坐防线——两层正交，缺一不可。

## 3. 集成注记（未来战役接入）

- **未来战役会话 bootstrap 时第一件事**：`python scripts/governance/chief_lease.py claim <sid>`。
  rc=0 → 你是在任总包，承担总包义务（heartbeat 节律 + 收尾 release）；rc=1 → 读输出里的
  holder sid，你是工序队，向 holder 对齐并入其工序队列，不另立总部。
- 心跳节律：长批任务每 ≤3 分钟一次 `heartbeat`；会话收尾序列（merge/release claim 之后）
  追加 `chief_lease.py release <sid>` 交班。
- 排队语义：总包非终身制——在任者 crash/断供，TTL 到期后首个 claim 者无缝接任，
  无需人工撤销。
- 与提交队列关系：L2 定"谁是总包"，commit_queue（§2 并发正门）定"提交怎么排队落盘"，
  两者正交；总包不插队，队列不选总包。
