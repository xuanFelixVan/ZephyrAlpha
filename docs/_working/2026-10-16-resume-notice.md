---
ttl: task_bound
title: 10-15 夜 D 盘事故与治理工程——被暂停会话的复工交接书
author: st-diskp0-20261015（总包）
created: 2026-10-16
---

# 致所有被暂停的会话：发生了什么、你的东西在哪、怎么继续干

## 1. 发生了什么（30 秒版）

10-15 白天 D 盘被占满（3.2MB 剩余，git 全堵）：结构层=HyperV 虚拟盘 569.8GiB 静态地板，触发层=当日 100+ 棵重试车道＋tmp/审计增量击穿仅剩余量。**已被治理**：现 101GB 可用；主区 5000+ 件死会话 WIP 已抢救落进 dev；死车道/死信/证据/审计全部清到机械地板；五条自动清理 wire＋九面遥测已上线（state=ok）。**完整报告**：`docs/_working/2026-10-15-diskp0-final-report.md`（事故与抢救）＋`docs/_working/2026-10-16-root-cure-plan.md`（治本方案，含九面/自动化/告警路由）。

## 2. 你的东西现在在哪（按状态对号入座）

| 你当时的状态 | 现在在哪 | 怎么确认 |
|---|---|---|
| 已经入队/已落地 | **已在 dev HEAD** | `git log --oneline --grep "<你的sid>"` |
| 提交到一半（staged/工作树改动） | **已被抢救批量落进 dev**（Bag1-7，commit message 带 [st-diskp0-20261015][WIP抢救]） | `git log --oneline --grep "WIP抢救"`；src/scripts 面约 530 件按 Owner 裁定留工作树未落 |
| 提交失败进了死信 | `.runtime/commit_queue/dead/`（袋内有 dead_reason 修因处方） | `python scripts/commit_queue.py status`；查袋 json 的 dead_reason |
| 死信已归档的 | `.runtime/commit_queue/dead_archive_20261016/`（manifest 可反向复原） | 同目录 manifest.jsonl |
| 车道/worktree 被清 | patch 存证＋rescue 在 `.runtime/quarantine/`（round2 台账=`.runtime/tmp/worktree_cleanup_round2_ledger.txt` 25 行 stash SHA 可复活）＋`.runtime/tmp/rescue/` | 查台账与你 sid 行 |
| 分支被清/被并 | 判定与证据=`.runtime/tmp/branch_triage_20261016.md`（每分支一行：判定/处置/哈希）；merge-train 台账=`.runtime/tmp/mergetrain_20261016.md` | grep 你的分支名 |
| stash 被"冻结" | 19:00 主面 stash 内容 99.8% 已吸收进 dev（登记在 `.runtime/workspace_alerts/stash_notice.json`，**禁 pop**） | `git log` 已含你的内容 |
| 你的 claim/接管条目 | 已全部释放/关闭（takeover 台账 0 open 遗留） | 无需处理 |

## 3. 复工怎么做（依次排队＋一次通过提交法）

### 3.1 复工四步
1. **冷启动**照旧（PATH 3.12＋reaper 检查），注册会话＋**起心跳**（防 SESSION-REQUIRED）：
   `PYTHONPATH=D:/ZephyrAlpha/src nohup python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <你的sid> &`
2. **先查你的遗留**（上表右列命令），确认你的成果是否已在 dev——已在就直接开新任务，**不要重做**。
3. 车道规则已变：**同岗位重试必须复用既有车道**（D1 闸会拒裂变）；磁盘地板 15GiB 以下拒绝新车道。
4. 提交一律走**队列正门**（--enqueue），串行器自动消化；失败自动进堵点本由维护班处理。

### 3.2 一次通过提交的"昨夜血泪清单"（每条都是真拦过人的门）
- **批量 ≤40 件/袋**（队列 R2 硬顶；确需大批判 `--allow-oversize-batch`）；文件清单显式列，禁 `git add -A`。
- **新文件先上户口**：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <路径> --created-by <sid> --capability <能力> --merge-evaluation <一句话>`（CREATE-GUARD 硬拦无 token 新件）。
- **frontmatter 三规则**：`docs/_working`、`docs/_archive` 内禁 `doc_type:`（改 `working_doc_type:`/`archived_doc_type:`）；`ttl:` 只认 `task_bound`/`permanent`；引用危险 git 命令样例的文档加 `gate_selfdoc: GIT-DANGEROUS`（≤10 行）。
- **实盘键名字样禁入任何文件**（REAL-KEY 硬门无逃生）。
- **每批提交前自清接管条目**（claim 绑短命 PID 会被立 open 条目反拦自己）：`python scripts/governance/session_takeover_ledger.py --resolve <sid> --by <sid> --note 自清`。
- **门禁提速了**：注册表共析＋并行化已上线，但 flag 默认 OFF——你的每轮门禁仍是分钟级，**一次写对远快于反复被拦**（Top 拦因=CREATE-GUARD 无户口/MUTABLE-CONST/TAKEOVER）。
- **总纲**：`docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md`（被拦时按 GUIDE 指路锚点查对应 GATE 卡片：判据/豁免/处方）。

### 3.3 禁止事项（昨夜教训）
- 禁 pop 旧 stash（913 件删除面会回灌制造冲突）；禁重建已被吸收的旧分支（查 triage 台账）；禁绕门禁（无逃生且必被 POST-COMMIT-GUARD 回滚）；禁在 merge 被拒后不管工作树（已修自动恢复，但仍先 `git diff HEAD` 自检）。

## 4. 系统现在的自动化（你只需要知道它存在）
死袋 7 天自动归档｜死车道 48h 自动收｜tmp 48h TTL｜审计 50MB 轮转｜gc --auto 自管｜九面遥测超限自动告警到 `.runtime/workspace_alerts/`（冷启动看到 nine_face_*.json 告警件=真超限，按件内 recover 处方处理或上报）。**盘余量红线 15GiB**（VHDX 压缩窗口=Owner 呈批中）。
