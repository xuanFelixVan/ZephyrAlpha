---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# L11 测试重收编作业簿（st-mastertc-l11）

> 车道：总包夜战 L11｜卡：C263 C16 C56 C155 C10｜基线：HEAD 014ccf5b18（开战时点）
> 协调前提（铁律①）：2026-10-07 03:40 实测——st-tests-chief 锁表零持有 + 最后 tests/ 提交 e824a7ff9e（02:55，45min 前）=判不在飞，走全量重收编；st-cure-p10-20261006 三枚**已过期**锁（rb14/wave3×2）经 `lock_files.py release` 精准释放后重 claim（其会话 04:01 复活落 trade/trading 面，与本车道九件零撞，git 实证 a121bb5465）。
> 通道备注：正门两度被共享暂存区他会话 A 态 725 件连坐（MUTABLE-CONST 拦外来件 gpu_layered_spread_kernel.py 等）+ FOLDER-CAPACITY-HARD-LIMIT 判据漂移（tests 豁免已收窄至深度≤1，tests/gov/governance 根盘面 212>120 结构性超限）→ 宪法§2.6 改走提交队列（worktree 净面结构性免疫），三袋 q-20261007-st-mastertc-l11-0001/0002/0003。

## C263 test_commit_preflight_registry_cache.py

- **六向台账**：①处方=8a6353976a8 原 156 行按新家规范落 rule_bridge 域；②HEAD 实证=旧路径 tests/governance/rule_bridge/ 已被 87cb48bf0e5 补刀删除，新路径 `tests/gov/governance/rule_bridge/` 存 st-cure-p10 materialize 未跟踪副本；③上游=zephyr.gov_enforcement.rule_bridge.commit_preflight（在册）；④消费者=pytest 自动发现；⑤冲突面=p10 过期锁已释放；⑥残余=无。
- **字节核验**：盘面副本 sha256=6919…（见 JSON）vs `git show 8a6353976a8:tests/governance/rule_bridge/...` 旧字节 diff 仅两处=①[BLUEPRINT] 行删（2413fa3efc 格式治本既定动作）②module_id MOD-TEST-001→MOD-TEST-001-TEST_COMMIT_PREFLIGHT_REGI（e824a7ff9e 撞号治本既定动作）→判 materialize 权威副本，采用。
- **自审闸**：GREEN。
- **施工记录**：新路径落定；pytest=**8 passed**；随队列袋 0001 落 HEAD。

## C16 test_rb14_s7_cross_lane.py

- **六向台账**：①处方=8b6c351c58c 落过的 37 例含 S7 件取回重落；②实证=旧路径 tests/governance/red_blue_pkg14/ 已删，新路径 `tests/gov/governance/red_blue_pkg14/` 存 materialize 副本；③上游=_diff_helpers own-scope+commit_queue_landing 池化两车道（在册）；④消费者=pytest；⑤冲突面=p10 过期锁已释放；⑥残余=无。
- **字节核验**：对 8b6c351c58c 旧字节 diff 仅 [BLUEPRINT] 行删一处 → 权威副本采用。
- **自审闸**：GREEN。
- **施工记录**：pytest=**5 passed**（现袋演进为 5 例；37 例为 8b6c 时代全包计数，后续拆袋属 chief 口径）；随袋 0001 落 HEAD。

## C56 残件（test_wave3_dual_source_guard.py + map_adversarial）

- **wave3**：①处方=q-0213 捞回件被删面重收编；②实证=旧路径 tests/data/ 被 6324c9e0f6f 删除后**盘面回灌僵尸**（?? 未跟踪）与新家 `tests/data/data/` materialize 副本并存，两副本字节全等；③新家映射规范=旧 tests/<组>/<件>→新 tests/<组>/<组>/<件>（gov/governance 同构实证）；④字节核验=对 f577545c5c4 旧字节 diff 仅 [BLUEPRINT] 删；⑤pytest=**5 passed + 3 xfailed**；⑥残余=旧路径僵尸 tests/data/test_wave3_dual_source_guard.py 未物理删（纪律：不删物理文件，留清理班按标记制处置）。
- **map_adversarial 家族盘点**（新家 tests/gov/governance/d5_architecture/）：
  - test_governance_legislation_map_adversarial.py：fig16 批 caffd260345（10-06 12:04）落旧路径漏收编件=**本车道唯一 git mv 真搬移**（新家适配 parents[3]→[4]、id TEST-MOD-GOVERNANCE-TEST_GOVERNANCE_LEGISLATION_M、BLUEPRINT 删）；pytest=**15 passed**（先决=CV-05 counts 回灌：账本 305 vs 图 304，重跑 generate_governance_legislation_map.py 对齐，随 config 袋）。RENAME-DEPGRAPH-SYNC 义务=generate_project_depgraph.py --force 已重建。
  - test_strategy_card_lifecycle_map_adversarial.py：q-0213 捞回件 #16（33854B，blob 3daa7c5b…）被删件，materialize 副本字节核验=对 87cb^ 祖先仅机械三改（BLUEPRINT 删/TEST- id/parents[4]）→采用；pytest=**67 passed / 3 failed**——三红全为生产真债被尺如实点名：①D15-S1 真源锚 docs/_working/sector_line|emotion_line/prereg_exam_cards_v0.md 被 014ccf5b18d（总包统筹役归档批）git mv 进 archive 未重指；②CV-HOST 宿主注册欠账 unregistered_declarable=10。图 counts 已回灌（generate_strategy_card_lifecycle_map.py，cards=105），锚重指归 fig15 车道、欠账归工厂车道=**RED 移交不白洗**。
  - construction_workflow/data_supply_chain/dev_delivery 三件=materialize 副本在位（非本卡清单，未动，留 cure 车道随袋）；trading_day_cycle=已在册。
- **自审闸**：wave3/legislation=GREEN；strategy_card=GREEN(收编)+RED(3 红移交)。

## C155 evaporation + snapshot_selfconsistency

- **test_evaporation_cure_lane_ev.py**：①字节考古=从未入 git 史（git log --all 全空），唯一遗物=pyc（co_filename=旧路径 tests/governance/，2026-09-28 编译，先红版）——pyc 全骨架倾倒还原三类九测；②现行接缝考据=原稿断言的"动词钉死 --git-dir/--work-tree + landing_guard.jsonl 审计"经考**从未按该形态落地**（.tmp 孤儿件零 EV-02 标记实证），09-30 F 组夜班落地形态=入口门（_git_wt 前置硬校验）+`_verify_wt_integrity_post` 执行后复核（_sync_worktree 1750/1758、1753/1771 接线）+内收死信链路；ops_guard 的 POSIX sh_rm_recurse 原语已退役（实测 `rm -rf` 不判递归），现行拦截面=powershell_recurse（`Remove-Item -Recurse docs/...` 阻断+FORCE 放行双向实测）；③重写=按 pyc 骨架+现行接缝忠实重建（docstring 留考据），落 `tests/gov/governance/resilience/`（根散位容量门不可落，按域归位）；④pytest=**7 passed**；ruff format 双清。
- **test_commit_queue_snapshot_selfconsistency.py**：materialize 副本（对 dbf5ee8a6c7 旧字节 diff 仅 parents[3]→[4]）落 `tests/gov/governance/resilience/`；pytest=**2 passed / 5 failed**——五红同型=见证层 `_stale_carry_candidate_blobs` 对现行 enqueue 契约返空（dangerous=[]/safe=[]），assert_snapshot_selfconsistent/_witness_stale_carry 函数在册且签名兼容，判为**跨车道契约漂移案**（09-26 尺 vs 10-06 st-cure-p0 落地模块），RED 移交不白洗（H1/H2 案卷语义仍有 2 尺在守）。
- **自审闸**：evaporation=GREEN；selfconsistency=GREEN(收编)+RED(5 红移交)。

## C10 test_api_server_route_guard_order.py

- **六向台账**：①处方=重写最小回归尺（路由注册先于 __main__ 守卫）；②实证=materialize 副本即 17ead261fe8→3d0c5fcdf01 全量 62 行版（对 3d0c5fcdf01 diff 仅 BLUEPRINT 删+parents[3] 修正），**优于重写**——含 mount 序与守卫尾三尺；③首跑 2绿/1红=**真回归实证**：api_server.py mount("/") 块（5366）在 AI 层四路由（5374+，09-24 追加）之前，违其自载铁律注释"mount 必须在全部 /api 路由注册之后"=Starlette 注册序吞路由（前端 404 病灶，[FIX 2026-10-01] 注所述复发）；④治本=src/zephyr/frontend/dashboard/api_server.py mount 块外科移回最后路由之后、main 之前（[FIX 2026-10-07] 注留痕），api_server.py 空闲无主实证后动刀；⑤复跑=**3 passed**+SW3 哨兵尺 tests/frontend/test_api_server_main_guard_order.py 绿+**运行时序实证**（budget/schedulegate×4=idx[54-57] 先于 mount=idx[58]）；⑥归位=tests/frontend/（D_FRONTEND 本域，根散位容量门绕行）。
- **自审闸**：GREEN（含产线治本随队列袋 0002）。

## OPEN_QUESTIONS（移交 L10/维护班）

1. strategy_card_map D15-S1 锚重指（archive/2026-10/ 路径）——fig15/生成器车道；CV-HOST 10 卡注册欠账——工厂车道。
2. snapshot_selfconsistency 五红=见证层×enqueue 契约对齐案——queue/landing 治理车道（附诊断锚：assert_snapshot_selfconsistent@commit_queue_landing.py:4199、_witness_stale_carry@:1881、_stale_carry_candidate_blobs 返空）。
3. FOLDER-CAPACITY-HARD-LIMIT 判据漂移（门卡"tests/ 豁免"vs 实现"深度≤1"）+ tests/gov/governance 根 212 平铺结构性超限——tests 治理战役后续窗。
4. 旧路径盘面回灌僵尸（tests/data/test_wave3_dual_source_guard.py、tests/governance/ 旧树 90 .py 等）——清理班按"标记+隔离制"处置。

## CONFLICT_LEDGER

| 对象 | 性质 | 处置 |
|---|---|---|
| st-cure-p10 三枚过期锁 | 已过期（TTL 尽） | lock_files release 精准释放→重 claim（其复活后落袋与本车道零撞，git 实证） |
| 共享暂存区他会话 725 件 A 态 | 连坐拦截（MUTABLE-CONST 等） | 不代修（owner 责任制），本车道全量改走队列 |
| st-cure-p05 04:20 depgraph 重刷 | 时序竞争（在我 --force 之后） | 无害（幂等全量重建），freshness 以落地时点为准 |

## DONE_SUMMARY

**九件测试全数落 HEAD（队列通道）**：
- `44f445c47e`（06:5x，袋 0008）=C263/C56/C155/C10 七件（rb14 除外）
- `b20899c870`（袋 0009）=C16 rb14 单件（块首 noqa: I001 双配置压制后落地）
- `e5f0f9a5ee`（袋 0003）=C10 产线治本：api_server mount 序归位
- `cdd1246dc6`（袋 0004）=两图 counts 回灌（CV-05/D15 现算面对齐）

**队列战史**（维护班堵点本已自动登记）：0001/0002/0005/0006/0007 五死=同一签名（落地侧 GATE-PRECOMMIT-RUN 的 ruff 对 rb14 import 块判 I001——本地 bare/isolated/pre-commit 三态全绿而落地侧必红，判序列化器 ruff 环境判据分歧，属"ruff 通道占全史 46%"已知堵点族）；0007 带修后字节仍红=排除字节面；拆袋（0008 去 rb14）即过=**病灶收敛于 rb14 单件 import 形态**；0009 noqa 压制落地=全链闭环。副产品发现：requeue 重建快照曾捕获零字节 blob（0006 时代），已用全新 enqueue 规避——requeue 通道的快照竞态疑点留维护班。

**残余（应移交，非本车道可裁）**：
1. legislation 旧路径删除半边（git mv 的 R 暂存残影在共享索引）——正门两度被他会话 725/3518 件 A 态连坐（MUTABLE-CONST 扫全暂存面），留收尾班随批。
2. strategy_card 3 红（D15-S1 锚重指+CV-HOST 欠账 10）→ fig15/工厂车道。
3. selfconsistency 5 红（见证层×enqueue 契约漂移）→ queue/landing 治理车道。
4. 旧路径盘面回灌僵尸（tests/data/test_wave3_dual_source_guard.py、tests/governance/ 旧树）→ 清理班。
5. FOLDER-CAPACITY 判据漂移（卡面"tests/ 豁免"vs 实现"深度≤1"）+ tests/gov/governance 根 212 平铺 → tests 治理战役后续窗。

**claims 终态**：12/12 released（gateway verified + lock registry CLEAN）。bytes/pytest 读数见交付 JSON。
