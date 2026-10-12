---
ttl: task_bound
---

# 【移交单·总队（worktree 域）】两枚初始化死锁棚（2026-10-09）

Owner 裁定 #6＝这两件登记移交总队。本战役**未对它们做任何写操作**。

| 棚 | 体积 | git 现场原文 | 我可确认的 | 我不可确认的（请总队定） |
|---|---|---|---|---|
| `.aidrafts/st-mx07-W2` | 0.26 G | `fatal: cannot remove a locked working tree, lock reason: initializing` | 分诊判据给的是**态①**（HEAD `is_ancestor_of_dev=True`、零脏件、`--ignored` 递归展开后无增量件、属主会话判死）；`git worktree list` 中仍在册 | 是否为**半途 abort 的 `worktree add`**（若是，棚内内容可能就是检出中，删除无损失）；还是有人在用 |
| `.aidrafts/st-tclose-fwire-20261004` | 0.25 G | 同上 | 同上（态① 全套证据在 `03_evidence_summary.yaml` `per_item_disposition`） | 同上 |

## 处置选项（按 git 自己的处方，非我发明）

```bash
# git 对该状态的官方处方（错误信息原文即此）：
git -C D:/ZephyrAlpha worktree remove --force --force .aidrafts/st-mx07-W2
git -C D:/ZephyrAlpha worktree remove --force --force .aidrafts/st-tclose-fwire-20261004
# 之后清 admin 元数据（只删目录已不存在的条目，安全）：
git -C D:/ZephyrAlpha worktree prune --dry-run --verbose
```

## 为什么我不自己按下去

1. 根宪法 §1 条 3 / §3 条 4：**他会话在途违规不代修**，`initializing` 锁＝有人开过 `worktree add`，
   我无法证明那一刻不是**正在发生的施工**（我只能证明我的会话启动那一刻它已卡着）。
2. 接管台账（`session_takeover_ledger`）对 worktree 的处方明确写着
   `Rx: owned worktree ...：先核成果 merge 回主区或 abort 放弃；worktree remove 走裁定通道登记，`
   **`禁裸 git worktree remove`**——双 `--force` 正是被禁的裸删形态之一，需登记后执行。
3. 体量小（合计 0.51 G），对本战役 26.4 G 的结论无影响，不值得用一次不可逆误删去换。

## 佐证材料位置

- 逐件判据：`docs/_working/dexp_campaign/03_evidence_summary.yaml` → `per_item_disposition`
  （含 `path/branch/head/size_gb/result/rollback`）。
- 第二道闸（≥20MB 非 tracked 件反查）：两棚均在 91 件态① 清单内，审计结论 0 命中。
- 回滚不需要：两棚 HEAD 均为 dev 祖先且零脏件，重建命令已入账
  （`git -C D:/ZephyrAlpha worktree add .aidrafts/<名> session/<名>`）。
