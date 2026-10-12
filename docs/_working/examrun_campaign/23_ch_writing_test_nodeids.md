---
ttl: task_bound
title: 触库测试 node id 名单（断源裁(a)今晚止血的输入，交维护三班）
created: "2026-10-13"
sid: st-examrun-20261012
family_id: EXAMRUN-CAMPAIGN-20261012
---

# 一、用途

统筹 2026-10-13 裁：断源＝**(a) 过渡（今晚止血，按 node id 排除已知触库测试）＋(b) 治本
（测试轮 CH 写口注入 fail-closed 护栏；在册 `ch_writer` 缺只读开关即新增它）；(c) 不采**。
(a) 的落法与排除点归**维护三班**，本件只交**输入名单**与取证口径，本班不代改任何落地链/测试。

# 二、名单（静态读码取得，零运行、零写入）

尺＝对 `tests/backtest/test_sim_daily_runner.py` 做 AST 解析，凡函数体内出现
`plan_bridge(`／`replay_one(` 即列（这两条路在生产侧对应 `INSERT INTO c1_backtest.sim_daily_report`）：

```
tests/backtest/test_sim_daily_runner.py::test_plan_bridge_unclassified_is_pending
tests/backtest/test_sim_daily_runner.py::test_plan_bridge_defense_state_translates_flat
tests/backtest/test_sim_daily_runner.py::test_plan_bridge_attack_state_is_unexecutable
tests/backtest/test_sim_daily_runner.py::test_plan_bridge_no_plan_no_write
tests/backtest/test_sim_daily_runner.py::test_replay_one_entry_math_and_fresh_wallet_funding
tests/backtest/test_sim_daily_runner.py::test_replay_one_flat_wallet_gets_notional_not_zero
```

- 定义行号（便于复核）：88／100／111／120／146／172。
- 本名单本班已**自验两遍**（交付件里的复核命令须自己先跑通）：
  `grep -nE "^def (test_plan_bridge|test_replay_one)" tests/backtest/test_sim_daily_runner.py`
  ⇒ 六行行号逐一对上；`pytest tests/backtest/test_sim_daily_runner.py --collect-only -q`
  ⇒ 六个 `<Function …>` 全部可被点名收集（排得掉）。
- 命名注意：`test_plan_bridge_no_plan_no_write` 顾名思义"无计划即不写"，但**本班不替它担保**——
  静态只证"它调了这条写路"，不证"它每次都真写"。列入是保守处置（宁可多排一支，勿漏一支污染源）。

# 三、动态佐证（已存在的生产侧痕迹，非本班当夜新增）

- `system.query_log`（服务器 `timezone()=Etc/UTC`，窗必须按 UTC 取）：
  本地 21:44:51／21:45:10／21:45:20 三笔，与考试班三次 pytest 调用对时；
  本地 **00:04:07／00:04:40** 两笔落在**队列排本班袋**期间（0032 于 00:04:42 判落定、0033 processing），
  本班当刻只跑只读 git。⇒ **落地链的测试轮也是触发者**，故 (a) 的排除点应在落地侧而非只在人工跑。
- 逐行归因可用 `run_id`：代码按写入时刻生成 `simwire-<UTC 时间戳>`
  （实测三行 `…134520`／`…160407`／`…160440`），不由测试传入，故不可伪造为测试夹具名。

# 四、实施后请这样自证（本班按裁不复删，只复测）

1. 排除生效＝落地链再排一次袋后，`c1_backtest.sim_daily_report` 内
   `judgment_id='SIMP-2026-09-21-plan_bridge-index000300.SH'` 仍为 0 行（当前状态：已删至 0，269→271→268）。
2. 反向对照（证明排除不是"整个测试目录被跳过"）：该文件的其余非触库用例仍被收集与执行
   （当前面：`18 passed / 2 failed`，两支红是日期地雷型存量红，已在 §廿四 三分表内登记，属主归 sim 班）。
3. 治本 (b) 的验收判据建议：新增写口护栏后，人为在测试里调用一次写路应**抛而非落库**。

# 五、本班纪律（与本案卷配套）

- 01:00–04:00 与 21:00–22:30 两段让路窗内不跑任何可能触 CH 的测试；
- 判"某测试是否触库"按 node id 逐只验，禁拿文件头 `[INVARIANTS]` 自述当保证；
- 04:00 窗毕复测该键是否又非零：**非零即报统筹重裁，不自建"反复删"循环**（统筹已照准）。

出处：班账 `docs/_working/examrun_campaign/00_ledger.md` §廿八／§廿九；
案卷 `docs/_working/examrun_campaign/22_landing_test_isolation_dossier.md`；
删行快照 `.runtime/tmp/st-examrun-20261012/pollution_rows_3_snapshot_20261013.json`。
