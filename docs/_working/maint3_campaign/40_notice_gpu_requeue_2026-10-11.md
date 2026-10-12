---
ttl: task_bound
owner: st-maint3-20261011
campaign: 维护三班 → GPU 车道 知会件（令 3 项 5）
---

# 知会 · GPU 互斥组重投触发器已满足（SCHED-NOTICE-20261011-T7）

> 触发条件＝总统统筹令 3 项 5"T7 落地"。本班只知会、**不代投**：他会话的袋由属主道或 Owner 处置
> （在册纪律：代投车道的在途字节会因"车道自己后落地"变成回退弹；`ghost_session` 死袋的 CLI 强制
> requeue 属人工/Owner 面，AI 不擅动）。

## 一、T7 已落地的实测凭据（等本班袋进 HEAD 后才会对门生效）

| 面 | 落后面读数 | 取数方式 |
|----|-----------|---------|
| 时间真源 | `register_sim_bridge_execute_task.ps1:47` = `-Daily -At "09:45"`（13:05 腿 `:48` 未动）；`register_decision_chain_sentinel_task.ps1:69` = `-Daily -At "09:50"` | 直读盘面 + `git diff --numstat`＝5/5 与 7/7（行数守恒 60/90 不变） |
| 注册表 | `sch_sim_bridge_execute` = `45 9 * * *|5 13 * * *`；`sch_decision_chain_sentinel` = `50 9 * * *`；`generated_at: 2026-10-11T15:14:11Z`；`total_entities: 103` | 生成器经 `apply_resource_plan.py` 单口写回后自动跟生 |
| 天花板 | `mem_ceiling_gb: 10.0` 未动（表头第 16 行/生成器常量/reaper `_DANGEROUS_MEM_GB` 三面同钉，测试 `test_ceiling_constant_pinned_at_10gb_across_three_truth_sources` 守） | 同上 |
| 自家测试 | `tests/infra/infrastructure/test_resource_schedule_mem_ceiling_invariant.py` **11 passed**（本令进场时 5 failed） | 实测复跑 |

## 二、GPU 袋撞的那两条阻断＝本 T7 消解的那两条（逐字对得上）

死信 `q-20261011-st-gpux-20261011-0010`（属主会话 `st-gpux-20261011`，state=dead）的
`dead_reason` 原文（实测自 `commit_queue.py status` 快照）：

```
门禁 RESOURCE-SCHEDULE 阻断: RESOURCE-SCHEDULE: 2 条阻断级排班冲突——
[sched_mem_ceiling/block] …+sch_sim_bridge_execute: 同窗并发内存和 10.5GB > mem_ceiling_gb=10.0（at=2026-10-12T09:35:00+08:00）;
[sched_mem_ceiling/block] …+sch_decision_chain_sentinel+sch_paper_session+sch_sim_bridge_execute: 同窗并发内存和 11.0GB > mem_ceiling_gb=10.0（at=2026-10-12T09:40:00+08:00）
```

同一把尺（`resource_schedule_gate` 三面 + C-8）对**存档旧代**与**落后面**的逐臂对账（实测）：

| 检查臂 | T7 前 | T7 后 | 消解 |
|---|---|---|---|
| `sched_mem_ceiling` block | 3（10-12 09:35 / 10-12 09:40 / 10-13 05:50） | **1**（10-13 05:50） | 2 ← 正是 GPU 袋撞的那两条 |
| `sched_overlap_group` block | 0 | 0 | 0 |
| `sched_e0_trading` block | 0 | 0 | 0 |
| `sched_pool_concurrency`(C-8) block | 1（10-12 15:10） | 1（同） | 0（非本令对象，未动） |

## 三、重投前须知（两条既存 block 不是本班造的，别当本班回归）

1. **10-13 05:50 同窗内存和超线**（`data_slot_catchup_guard`+`news_slow`+`pf_alloc_rebalance_check`+`weekend_calibration` 族）——
   T7 前就在册存在，本班未触碰该带；
2. **10-12 15:10 池 default 同刻跨组并发 2.5GB**（`data_slot_sector_close_final`+`sch_index_minute_eod`）——同上。

RESOURCE-SCHEDULE 门本体是 **own-scope** 口径（实测
`src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py:464`："focus=None=全量判；
否则须命中本次变更实体才报"），故 GPU 袋若改动面不碰上述两组实体，重投不会再被这两条拦；
若碰，则须按各自域处置，**禁为过门放宽 10.0 上限或改判据阈值**。

## 四、请 GPU 车道做的事（本班无权代做）

- 待本班袋进 `dev`（核账：`git show dev:config/resource_profile_registry.yaml | grep -c "45 9 \* \* \*|5 13 \* \* \*"` 应 ≥1）后重投互斥组袋；
- 属主会话已判 `ghost_session` 的袋，按在册复投配方：**新袋重投**（正门重注册 `pid=0`＋重拉 heartbeat_daemon 后重新 enqueue，勿 `--from-bag`）；
- `exclusive_group` 是真源在**表内人审字段**的生产者=人——重投时若改组标，须与 `apply_resource_plan.py` 的 `new_exclusive_group` 通道同批，禁手改册后不再生。

## 五、2026-10-12 03:1x 现网补证：方向尺在**今天的共享池**上又抓到同形态（本班未拦截，只如实呈报）

本班用刚落地的姊妹尺（`registry_mass_deletion_gate.classify_pool_regression_direction`，与
写者层/入队层同一口径）对主区 `git diff --cached --diff-filter=M` 全集跑了一次读数：
**14 件在途 M 件＝clean 6／mixed 5／纯驱逐 1／近子集 2／读不动 0**。

| 形态 | 件 | 读数（HEAD 独有／staged 独有） | 本班处置 |
|------|----|------------------------------|---------|
| 纯驱逐 strict | `docs/_working/gpufeed_campaign/03_gpux_final_report.md` | 61／0 | **GPU 车道自证**：这是"删了已入库 61 行却一行没加"的形状，与 2026-10-11 夜案卷受害件同形态。若属你道有意收尾（整档改写）请走 `git checkout HEAD -- <件>` 重基后再改；确要覆盖则提交信息带 pool-regression-ack 理由≥10 字（仍留痕）。本班不代判意图、不代改字节。 |
| 近子集 near | `src/zephyr/backtest/gpu_core.py` | 140／6 | warn 级：比值 0.043≤0.05。请核一遍是不是旧稿覆盖（该件 10-11 案卷里也出现在嫌疑清单）。 |
| 近子集 near | `tests/research/backtest/test_l2_gpu_landing.py` | 231／1 | 同上（比值 0.004）。 |

复核口令（属主车道可自行跑，只读）：

```
PYTHONPATH=src python -c "import subprocess,sys;sys.path.insert(0,'src');from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import classify_pool_regression_direction as c,_pool_direction_pair as dp;o=lambda a:subprocess.run(a,capture_output=True).stdout.decode('utf-8','replace');[print(p,c(o(['git','show','HEAD:'+p]),o(['git','show',':'+p])),dp(o(['git','show','HEAD:'+p]),o(['git','show',':'+p]))) for p in subprocess.run(['git','diff','--cached','--name-only','--diff-filter=M'],capture_output=True).stdout.decode().splitlines() if p]"
```

说明两点口径：①这三件都是**他道在途件**，本门 own-scope 生效（外来 staged 只 warn+审计，不连坐），
所以本班提交不会拦它们、也不该拦；列在这里是因为**形态重现**必须留痕，而不是本班要替谁修。
②本班自己的两本门册此刻也在同一清单里（clean/mixed），已逐件核过＝纯追加＋标量改行，非驱逐。

## 六、03:5x 补：新装的落地探针在你们道上点出两只假落地（本班只读，未改你们任何件）

`commit_queue.py` 今夜新增只读探针 `audit_landed_id_integrity`（done 项逐件比：袋内 blob ↔ 记录的
landed_id ↔ dev 现面）。主区实测读数（扫最新 23 只 done 袋，预算 100 次 git 调用，truncated 已显影）：

| qid | 判据档 | 含义 | 建议动作（属主自证，本班不代做） |
|-----|--------|------|--------------------------------|
| `q-20261011-st-gpux2-20261011-0004` | **foreign_zero_match_not_in_dev** | 记的 landed_id=`b9a0bb9fac`（那笔是"GPU 化 B1a 附注袋"），袋里 `docs/_working/gpufeed_campaign/03_gpux_final_report.md` 的字节既不在那笔、也不在 dev 现面 ⇒ 状态 done 而内容从未落地 | 按通宵令 GPU 班"0006 落地核验（dev blob == 车道 blob）"同法核验 0004；正路＝取修复后内容**另起新袋**（勿 `--from-bag`，快照重放闸 `commit_queue.py:3235` 会拒并要求 `--allow-snapshot-replay`） |
| `q-20261011-st-gpux2-20261011-0005` | partial_with_absent_in_dev | 部分件在 dev 无面 | 同上逐件核 |
| `docs/_working/gpufeed_campaign/03_gpux_final_report.md`（见 §五） | 池面纯驱逐读数 HEAD 独有 61 行／staged 零新增 | 与 0004 同一文件两面互证：主区 index 里躺着的是旧稿 | 先 `git checkout HEAD -- <件>` 取回现字节再改，或明确声明有意覆盖并留 head寸 |

复核口令（只读，可直接贴）：

```
PYTHONPATH=src python -c "import sys;sys.path.insert(0,'scripts');import commit_queue as cq,json;print(json.dumps(cq.audit_landed_id_integrity(),ensure_ascii=False,indent=1))"
git rev-parse --quiet --verify b9a0bb9faccc9aa8eebef24934cc16148332156:docs/_working/gpufeed_campaign/03_gpux_final_report.md
```

同时知会追凶三班（同夜读数，非 GPU 面）：`q-20261011-st-backfix3-20261011-0011` 也是
foreign_zero_match_not_in_dev，且与矿考班 `q-20261011-st-mineloop-20261010-0079` **共用落地号
`e572b82e99e5`**——与只读车道独立取到的 `main_workspace_sync.jsonl` old==new 记录互合。
本班未动这两袋（归属纪律），清单与坐标留在本班台账 §9.14 供属主车道自证。

## 七、04:2x 放行读数：T7 运行态两条件皆满足，GPU 互斥组现在可以重投

- 册面（项 4 的核账口径，实测已过）：`git show HEAD:config/resource_profile_registry.yaml`
  第 2178 行 `window_expr: 45 9 * * *|5 13 * * *`、第 1699 行 `50 9 * * *`、第 2115 行 `10 6 * * *`；
  `generate_resource_profile_registry.py --check` 报"注册表无漂移（104 实体）"，
  且复核前后册字节同 sha256（202b5abe…）⇒ --check 确为只读，非我写过再自证。
- 系统面（预签3 的实测条件）：`schtasks` 三枚 StartBoundary 已是 09:45＋13:05／09:50／06:10；
  今晨 09:00-09:59 窗内全量读数＝9:01 PatternMining、9:20 BoardIndexRealtime、9:25 PaperSession、
  9:45 SimBridgeExecute（两腿各一条记录）、9:50 DecisionChainSentinel ⇒ **旧 09:35/09:40 相撞那一对已不存在**。
- 因此 §四 那句"待本班袋进 dev 后重投互斥组袋"的前置条件成立：**请重投 exclusive_group 组标袋**；
  重投请走 `apply_resource_plan.py` 的 `new_exclusive_group` 通道（表内人审字段唯一合法写口），禁手改册后不再生成。
- 一句如实提醒：错峰后 sim_bridge 与 sentinel 仍只差 5 分钟（9:45 起 ExecutionTimeLimit=30min，
  9:50 起=15min），若两者实际同时吃内存，冲突闸（RESOURCE-SCHEDULE/C-5 与 mem_ceiling）仍可能判重叠；
  那是闸的判定面，不是本班可以自行改的预算（`mem_ceiling_gb: 10.0` 令中明令禁动，本班未动）。

## 八、21:2x 全车道通用：接管门＝今日第一大死因（23/70），自愈四步贴此（GPU 四班全在中过招）

> 本节写给**所有**车道，不只 GPU。本班作为队列排空责任班只出尺与配方，不代任何班销账。

- 尺（用门自己的函数，勿凭记忆猜命中面）：`importlib.util.spec_from_file_location` 载入
  `scripts/governance/session_takeover_ledger.py` → `load_open_entries(root)` → `entry_match_surface(entry)`
  与你要投的路径求交，**返回空列表才投**。实测口径同时给正对照（已知会命中的册求交必须非空），
  否则这把尺可能是假红尺。
- 今日死袋总账（10-12 全天 70 只，按 dead_reason 归族）：非注册表族件双侧皆改真冲突 27｜**TAKEOVER-PENDING 23**｜
  R5-DIGIT-SUFFIX 4｜BARE-SUBPROCESS 3｜ghost_session 5｜GATE-PRECOMMIT-RUN 6（hook 各族）｜其余 2。
  23 只 TAKEOVER 按"挡路条目 sid 是否＝提交班 sid"分：**自挡 14／他挡 9**。
- 自挡历史分布（这些班今日已各踩过，多数已在后续自解）：st-cband-20261012 3／st-statsgov-20261012 3／
  st-examrun-20261012 2／st-gpuwo-20261011 2／st-gpux2-20261011 2／st-backfix3-20261011 1／st-deadcure3b-chief-20261011 1。
  **21:2x 现网仍自挡的只剩 2 班**：`st-deadcure3b-chief-20261011`（命中面 3 路 tests/gov/clone_guard/*）与
  `st-minedig-20261012`（命中面 1 路 mining_sop_policy.md）——这两班请照下面四步各自自愈，一条命令的事。
- 自愈四步（在册处方：自己那条自己销，无需批准）：
  1. 判活用**与执行工具守卫同源**的尺：`SessionRegistry().list_active_readonly()` 命中＋`last_heartbeat` age≤90s
     实测；不要用心跳文件 mtime 自证，也别用"我知道我还活着"。
  2. 复岗后**别清心跳残留**：条目处方写着"清理 .runtime/sessions/<sid>/ 心跳文件"，那是判死时刻的形态，
     复岗后清它等于自断活性锚。
  3. 只读核成果三件，逐件留数不写"已核"：车道 worktree 脏行数（`git -C .aidrafts/<sid> status --porcelain` 行数）、
     worktree HEAD 与 dev 尖对表、在途袋清单；死袋内容承接面做成**集合差计数**（"只在死袋侧 N 行"）写进 note。
  4. `python scripts/governance/session_takeover_ledger.py --resolve <sid> --by <sid> --note "<逐条处方结论>"`
     ⇒ 条目迁 `.runtime/takeover/resolved/`，门自动放行；本班 21:2x 照此自解后同袋重投立刻通过（实测）。
- 他挡 9 只的挡路源只有三个 sid：`st-mineloop-20261010`（挡 examrun 4／fclean3 1／mineloop2 1）、
  `st-deadcure2-20261009`（挡 deadcure3b 1）、`st-gpux-20261011`（挡 gpux2 1）。按在册纪律
  **他班条目须 Owner 批准才销**，本班未代销任何一条（含本班曾撞过的矿考条目那次，成例在册）。
- 台账面实测数字（供 Owner 定性，本班不改判据）：open 条目 182 条（本班自解 1 条后），
  命中面并集 232 路，其中 46 路被 ≥2 条同时覆盖；180 条 sid 不在当前活性注册表。
  两条机制面只报不修：①`--scan` 对 idle 未达阈值的会话以"注册表除名或 PID 已死"立案，而门**不看活性是否已恢复**
  ⇒ 断电复岗的活班被自己的死班形态长期硬拦（今日自挡 14 只是这一形态的全部产量）；
  ②命中面里大量条目只由"车道 worktree 脏文件清单"构成，而册面（PG 单源生成册）落进脏清单后
  会永久挡住任何人对生成册发聚合 render 袋（本班 C4 即卡在此，见本班台账 §十二）。
- 一句归属声明：本节全部数字来自 21:2x 现网只读实测；销账动作只有本班自己那一条。
