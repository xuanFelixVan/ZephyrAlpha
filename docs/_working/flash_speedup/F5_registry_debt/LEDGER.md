---
ttl: task_bound
completes_when: 三项移交全部落地或被裁定作废后转 archived
---

# F5 registry debt LEDGER——三项移交补登（tc_04 卡步骤 3）

> 背景：landing-anchor-algo-flow-closeout 交接令 R2 项声称「三项移交全部登记且可机判核验」
> 并指向本文件；09-18 原调查班与 09-21 tc_04 卡两次实测本文件都不存在——**该声明不实**
> （三项实态见下表，均未落地）。本件由 st-taskcards-exec-20260921 按 tc_04 卡步骤 3 路由
> （Flash 登记）于 2026-09-21 补登：只登记实态+可机判判据，不自裁去留。

| # | 移交项 | 真源判据 | 实测状态（2026-09-21） | 可机判复核 |
|---|---|---|---|---|
| 1 | 落地成功后把 worktree 落地面 blob 回灌主树 index（消 MM 假象根因） | 归档 W2_commit_chain.md「待净窗落地的治本候选」① | **未落地**：无施工 commit；commit_queue_landing.py 落地面仍无主树 index 同步设计 | git log -S "回灌" --oneline -- scripts/commit_queue.py src/zephyr/gov_enforcement/rule_bridge/ 零命中 |
| 2 | qid 命中 done 即短路返回 landed_id（免重复入队重排） | 同上② | **未落地**：enqueue_item（scripts/commit_queue.py:593-702）无 done 查询分支 | 通读 enqueue_item 函数体无 done 短路 |
| 3 | claim 路径空间统一（主树相对路径 vs 落地读 worktree 绝对路径错配，#ARCH-324 实证④） | 同上③ | **未落地**：无施工 commit | git log -S "wt_files" --oneline 零命中 |

## 去留处置（已裁：裁定#392（D-3））

**裁定#392（D-3）（2026-09-21）**：三项随母题 #ARCH-324 **销项登记 known-limitation**（本 LEDGER
即登记面），不作施工立项；复发判据=同因摩擦一周内≥3 次再立项。此前的"交 Max 三选一"待裁态就此闭合。

母题 #ARCH-324 已被裁定 #377-G03 按 A 案实态 close（belt_daemon.lock mtime=2026-09-20
12:50:43 亲验=旧码常驻进程已重拉），本三项变成「对已关闭 issue 的孤儿施工候选」。
三选一待裁：随母题销项 / 另立 backlog 卡 / 授权施工。本 LEDGER 只登记，不预设立场。

## 附：ARCH-331 定义不可考（已裁：裁定#392 判幽灵号登记墓碑）

R2 项核查清单含「ARCH-331（09-18 实测未登记；未登记号不具合法井号引用形态，故不加 # 书写）」，但全源检索（桌面任务原文、
归档目录、architecture_issue_registry 全文、docs/_working 全文）零定义——在源可查的
#331 全部是**裁定号**（做T 砍，原 #304 撞号改号），非台账号。无定义内容禁凭空造册
（登记即虚构），ARCH-331 的真实含义须原交接令作者或 Max 补定义后再登记，已随 D 类
打包批补充材料呈报。
**收口（2026-09-21）**：裁定#392 判幽灵号——architecture_issue_registry 已登记 #ARCH-331
墓碑条目（status=resolved，related_adjudication=#392，禁补造定义），引用面自此有合法井号形态。
