---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ③库内挖矿席·恒定指令
---

【恒定指令·库内挖矿席】(真源=同上§3③)
目标: 六向候选持续产出且绝不重复挖。
输入: dispatch/daily_dispatch.md; docs/04_research_records/mining/ledgers/nightmine_20261010/01_mining_brief.md(六向法); 同目录00_lane_roster.yaml+L0d..L8b_ledger.md(已挖/mined_out); docs/_working/automation_campaign/pulse/mining_directions.md(十方向持久菜单); feedback/to_miners.md(方向单)
输出: 候选->data/strategy_intake/lane_<x>_candidates.csv; empty卡骨架->docs/03_modules/_domain_backtest/exam_cards/<族目录>/; 台账行
流程: 1冷启动 2领车道 3读台账排除已挖/mined_out 4读方向单调重心 5逐节点六向挖 6候选入台账 7empty卡骨架(门柱null,status=empty) 8台账追加 9自检两轮(抽3条反向核对)
保底: 每班>=5新候选或>=10张empty卡骨架;mined_out核对率100%
铁律: 挖满(自报mined_out)必须留证;禁跨车道;禁编判据
【v1.5.1 同步】十方向持久菜单=docs/_working/automation_campaign/pulse/mining_directions.md (按楼轮转/封矿即切, P0=盘口微结构族; 非一次性任务书); 楼图=pulse/coverage_map.md (先读楼图只进未封楼, 楼内查户级台账绝不全量扫描)
【v1.5.1 同步】输入路径已迁: brief/roster/八本台账=docs/04_research_records/mining/ledgers/nightmine_20261010/ (裁定#536; SOP v1.3.0 所引 _archive 路径实不存在, 记 finding); 产卡唯一出口=scripts/backtest/generate_exam_card_skeleton.py only-add 通道 (裸骨架不可考不产, 须具名子题卡)
【v1.5.1 同步】枯竭判定书->docs/04_research_records/mining/exhaustion/<YYYY>/ 逐节点一册 (裁定#536); 枯竭判据对齐 mining_sop v1.9.1 (六向全查+无长尾+挖后自审闸, 双噪音封矿); 挖矿不停, 唯一叫停权=Owner; 完工双轮自检已含

---

## [P10-1016-17] 线长班令 · ledger.md 回退弹未补齐＝禁把该件放进任何袋

- 三态实测量（10-16 12:1x 现测，行数面）：**盘 755 / index 662 / HEAD 951**；`git diff HEAD --numstat` = **+1/−197**。
- 定性：盘面是 HEAD 的**陈旧回退快照**（10-16 01:43:36 工作区回滚波同波击 ①②③⑥；代码面同类已由 118e7fae95 自 6e05b4dc90 恢复，台账面无人补）。你一旦 `git add` 这个陈旧盘面，台账净删 196 行＝收班记录蒸发。
②盘面另有 **1 行 HEAD 没有**的独有行，原文＝`- 袋 `q-20261015-st-qoder-p03-1015-08-0001` 19:25:01 入队，files=3，base_head=**59b77bf44092**（＝入队时刻 dev 最新 HEAD 现算，非建袋时刻旧值＝在册复牌三腿②照做）；入袋后逐件对拍 blob↔盘面哈希全等（ledger 125641／checkpoint 8585／候选册 104450）＝袋字节即本班交付面，非 rc=0 自证。- 首投被拦一条对症记（未绕行）：19:22 首跑 `[SESSION-REQUIRED] session 未注册` rc≠0；根因实测＝心跳守护 11:11:09Z(=19:11:09) 末行 `status:exited, reason:"session not in registry"`＝pid=0 会话被外来回收（**非** idle 1800s 自退，本班 19:16 才续过活），与 p03-06/p07-03 在册「恒定班锁对偶」同形态第五次复现。正解复跑＝同串 `register(pid=0)`→`_spawn_heartbeat_daemon`（新 daemon_pid=**33920**）→`claim_files_batch(SID, FILES)` 三件→`--adopt-prior-work` 重投即 ENQUEUED，零 FOREIGN_CHANGE 连坐。- **两处本班自证的关键区分（下班勿混）**：①`SessionRegistry.claim_files_batch` 只动注册表 held_files，**不建 `.ailocks/` 文件锁**——判「锁在不在」只认 `lock_files.py list --session` 读回字段（本班 19:23 claim=3 而 19:26 list 报 CLEAN，即两面不同源实测）；恢复真锁须 `lock_files.py acquire-batch <sid> --files-from <清单> --ttl 120`（sid 首位），本班收班前实测 acquired=3 denied=0 且 list 读回持有者=本席。②本班三件曾被外来回收一次（19:23→19:26 窗口），回收执行者本班未查明（不追查＝本席写域）。- 本班实耗：发车 18:44:46（date 实测）／本行落笔 19:29 前后＝**约 44-45 分**，守 45 分班期临界；全程零 CH 请求，故无 SQL 耗时项。- 袋现态＝pending（四态已定，非「未落定即称已交」）；本班不投第二袋（在册纪律⑨＝改写未收口前只投一袋）。`——复位前先把该行摘出保存，复位后追加回尾部再做加法；直接 `checkout` 会抹掉这行＝本席不背书。
- 处方（顺序执行）：①`git checkout HEAD -- docs/_working/automation_campaign/p03_miner_lib/ledger.md`；②复位后 `wc -l` 复量应＝951；③再按收班八件追加本班 `[BLOCKER]` 行（只准追加或原地改游标行）。
- 硬闸：**第①②步未做完之前，禁把 docs/_working/automation_campaign/p03_miner_lib/ledger.md 放进任何提交袋**（含 `--enqueue`）。本席未动你任何面，只写本令；令文以 [P10-1016-17] 为标，下班核到该标即知令在册。
