---
ttl: task_bound
completes_when: 在途占用已核（多会话队列活跃+串行器在跑）→ 本环节按纪律登记不硬闯；串行器/占用窗让位后由持有净窗者落地
title: W2 — 落地索引滞留 + qid 幂等（先查在途占用）
owner: ZephyrAlpha-Owner
session: st-anchorfix-20260918
date: 2026-09-18
---

# W2 — 落地索引滞留 + qid 幂等

## 在途占用先查（判据： occupied → 登记不硬闯）

实测 `commit_queue.py health/status`：
- 串行器**活跃**（pid 28400，`serializer.lease` 秒级续租），非死锁；
- 多会话在飞：st-tdchain / st-crisis-gate / st-flashbiz / st-sopfix / st-cfg-check 等
  队列项 pending/processing/dead 混流；belt daemon 亦在。

→ 结论：W2（落地成功即同步索引 + qid-done 短路 + claim 路径空间统一）涉及
改 `commit_queue.py`/`git_commit.py`/`commit_belt_daemon.py` 提交链承重件，在
串行器活跃 + F1~F4 提速车道在飞的窗口硬改 = 与并发落地互踩。**登记不硬闯**。

## 已实证并缓解的现象（本会话内）

- **MM index 滞留假象**：队列在隔离 worktree 落地后，主树 git index 仍持 HEAD^ 旧 blob
  → 落地文件显 `MM`。缓解（按交接令 §2 临时自保）：commit 后 `git diff HEAD`（本
  人文件）为空即纯滞留，`git add -- <本人文件>` 刷新 index 即清零。本会话 9 件已如此处理。
- **qid 幂等**：done/dead 目录以 `q-<date>-<sid>-<seq>` 命名，`-0002` 未与 `-0001` 冲突，
  seq 文件 `.runtime/commit_queue/<sid>.seq` 单调。

## 待净窗落地的治本候选（登记，勿自行拍）

1. 落地成功后把 worktree 落地面 blob 回灌主树 index（消 MM 假象根因）；
2. qid 命中 done 即短路返回 landed_id（免重复入队重排）；
3. claim 路径空间统一（登记主树相对路径 vs 落地读 worktree 绝对路径的错配，#ARCH-324 实证④）。
