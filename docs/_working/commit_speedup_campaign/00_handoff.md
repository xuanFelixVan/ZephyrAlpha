---
ttl: task_bound
---

# 夜战交接状态（自动续跑用，Owner 醒后亦是进度表）

时刻 2026-09-24 ~19:1x ｜ 统筹会话 st-commitspeed-tbl-20260924 ｜ worktree `.worktrees/st-commitspeed-tbl-20260924`（已快进到 dev `fc039cc891` 并 3-way 重放）

## 一、已完工（代码＋判别测试＋红证，全在 worktree 未落地）
- **A1/A2/A3 装表**：pre-commit 通道真实计费（原恒写 0.0）／落地八段计时＋`residual_ms`／工线程出口 `pool_wave.log`（守护无 handler，stderr 全丢 ⇒ 熄火此前零证据）。
- **D3 池并发真身**：一波只在全部工线程返回后才结束 ⇒ 单工异常死亡后 straggler 把波无限开着 ⇒ 新波永不开、死工永不复活。排空 18→2-4 件/时、积压 83 件即此。修法＝认领/处理异常就地记档续跑，连错 20 次才收工（防活锁）。
- **B4 排队键**：`(created_at, qid)` 先来先服务；扫描界 64→400；`_head_snapshot`/`position_ahead` 同源修正。旧断言 `processed==sorted(qids)` 判为"把 bug 当契约"（零判别力），已换成自洽断言＋确定性专项测试。

## 二、进行中
- 八套合并全量回归：`/d/ZephyrAlpha/.runtime/tmp/cs-tbl/allbatch3.txt`（须 0 失败才入队）。
- 在跑车道：B0 衍生再生出窗设计（`40_b0_derived_offload/`）。
- 已收卷：骨架（23 环节/115 子环节）、D1+D2 设计、门禁普查卷宗、分区目标架构、批1 红归因（判 UNRELATED）。

## 三、下一步顺序（Owner 已全批，无需再点头）
1. 全量绿 → `commit_queue.py enqueue --worktree-root` 入队批一（message 已备 `.runtime/tmp/cs-tbl/msg.txt`；**不走 merge**：主区暂存区实测 20 个"INDEX<HEAD 回退弹"，merge finalize 会强制全量提交覆盖别人旧稿）。
2. **D4 幽灵 pending 双落地**（存量完整性缺陷，已建任务；与 B4 同文件，须批一落地后再改）。
3. D2 env 线程泄漏 → B0 衍生出窗（`slow_item` 均值 755 秒的宿主）→ B2 缓存键 → 门禁共册簇合并（簇1 六台同读 2.68MB 册，CREATE-GUARD 单次 `yaml.safe_load` 实测 3.6-4.2s）。
4. 分区落地上 S1 是最险一步（一次改 72 台门咽喉，失败模式＝静默假绿）⇒ 出厂判据必须＝重放 100→1000 笔判定逐笔全等＋`CommitTreeView` 读工作区绊线；15 台"故意读全索引"的门禁走分道校验，禁 own-tree。
5. 收尾：两轮全量零问题 → 红蓝极限对抗（7 场景，尺须先能红）→ 临时件清零 → release 自己 claim → `git worktree` 按规程处置。

## 四、纪律与红线（续跑必读）
不删门禁（Owner 令，只合并/降档/diff 化）；不改判据阈值凑绿；禁 kill belt 守护（靠纪元自检自行换血）；热文件 CAS＋写后进程外核实；测试落 `.runtime/tmp/csx_*`（禁落 `.worktrees/`）；`_working` 禁 `.json`；案卷禁 `裁定#<未登记>` 与裸 `AGENTS.md §N.M`。

## 五、我已被实测推翻的三次判断（防续跑者重犯）
1. "每件大头是门禁链" → 实为**衍生再生串行扇出**（slow_item 均值 755s vs 链 73-84s）。
2. "D1 stats_lock 是并发 1.000 真身" → 实测 133-152ms/次，**解释不了**；真身是 D3。
3. "批一的红是我补丁造成" → A/B 对照判 **UNRELATED**，真因是存量 D4。
另：外部说法（Bors≈4/时、Anthropic 拆有状态单点）各仅单来源，按防噪音四闸降为"待验证"，战役结论一律以本仓实测为第一依据。
## 六、批一已入队（18:2x）
- 八套合并全量回归 **253 passed / 0 failed**（519 秒）后才入队；
- `ENQUEUED: q-20260924-st-commitspeed-tbl-20260924-0001 (files=7)`，claim 7/7 在手（TTL 30 分）；
- DRAIN skipped＝守护持 lease，由 belt 正常消费（不入队不插队不绕门）；
- 落地后 A2/A3 才开始产账：`.runtime/commit_queue/worktrees/w{i}/.runtime/audit/landing_phase_stats.jsonl`
  与 `.runtime/commit_queue/pool_wave.log`；届时第一件该读的就是"三路工从哪个口退出"与 residual_ms 归属。

## 七、18:4x 优先级改判（覆盖第三节的 T1/T2 顺序）
D4 已由闭链实验升为**第一优先**（与 T1 并行，不再排在批一之后）：
  证据 `.runtime/tmp/cs-tbl/ghost_chain_demo.py`（未打补丁 dev 码，4/4 确定性）——
  幽灵复活 → 再认领抛 FileExistsError[WinError 183] → 旧码工死 → straggler 占波；
  且 `_pool_claim_item` 不查 done/ → 另一时序同件二次落地。
  ⇒ D4 是"熄火"与"done 膨胀"的共同上游；D3 属症状层止血。
  施工位置冲突提示不变（D4 与 B4 同改 scripts/commit_queue.py），做法：等批一落地后
  立即在 .worktrees/st-commitspeed-tbl-20260924 上快进 dev→重放→改 `_mark_cascade_stale`
  回写为"仅当 pending 仍是该 qid 的最新副本才写"（或写完立即核对 processing/done 同名并清幽灵），
  并在 `_pool_claim_item` 加终止性复查（done/ 有同名即弃该幽灵）。
  判据：ghost_chain_demo 第 2 步不再产双件；池测试 15 项全绿；blocked 构造下 done 恒等于件数。
Owner 已另给一条通用令：治理类小批（纯插入＋自带测试）优先处理——批一即属此类。
