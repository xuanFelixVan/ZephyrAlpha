---
ttl: task_bound
title: e4_code_fix (20261001 删除事故后重建)
note: 重建件
---

# E4/E5 事件系统代码治本环节簿（e4_code_fix）

> **20261001 删除事故后重建**：原落点主区 `docs/_working/lane_c_chain_night_20261001/e4_code_fix.md`
> 被他队清理事故删除，本文按施工会话上下文原文重建于 worktree（内容与原版一致，含原笔误订正）；
> 原主区路径如恢复可径直搬回。重建会话=st-lanech-20261001（E4/E5 代码部分施工代理）。

- 会话: st-lanech-20261001（E4/E5 代码部分施工代理）| 日期: 2026-10-01
- 施工区: `D:/ZephyrAlpha/.worktrees/st-lanech-20261001`（worktree 隔离，未 commit——提交走总包 GitCommitGateway）
- 基线: dev HEAD=68fe30bd（含 st-circ-a7 F82/F27 已提交改动）
- 病根真源: e4_journal_surgery.md（总包手术记录 §遗留）+ 00_skeleton.md §一 E4/E5 行
- 触碰文件（纪律内，零越界）:
  - `src/zephyr/strategy_pipeline/pipeline_events.py`（+126/-9）
  - `tests/strategy_pipeline/test_pipeline_events.py`（+199，追加 5 个 Test 类 18 用例，未动既有 38 用例）

## 0. 自审闸三态结论：**挖干**

B1/B2/B4/B4'/B5 五病根全部修复且红绿证据闭合；B3 按总包设计裁定**不施工**（登记，见 §1.6）；
真实 journal 只读验证通过（`repair --list` 活体跑通 n=0，零副作用）。残余风险三条登记移交（§5）。

## §1 逐项修复表

| # | 病根 | 修法 | 红证据（修前实测） | 绿证据（修后实测） |
|---|------|------|--------------------|--------------------|
| 1.1 | **B1** `_rewrite()` 固定 tmp 名 `pending_events.jsonl.tmp`：多进程（DataScheduler 宿主/c4_batch_screen 钩子/CLI/intake 嵌套）并发互踩=撕裂行+WinError 32 | 新增 `_journal_tmp_path()`：tmp 名含 `os.getpid()+uuid4().hex[:8]`（正解先例=confirm_gate.py:655 `_atomic_write`、factor/offline_store.py:272）；`_rewrite()` 改走唯一 tmp+`os.replace` 原子换入，失败 `contextlib.suppress` 清理 tmp 残留 | `test_rewrite_cleans_tmp_on_replace_failure` 红：replace 抛 PermissionError(32) 后 `*.tmp` 残留 1 件；`test_tmp_name_contains_pid_and_uuid` 红：`_journal_tmp_path` 不存在（AttributeError） | 同两用例绿：无残留/名字含 pid 424242 且连续两次不撞；`test_rewrite_leaves_no_tmp_on_success` 绿 |
| 1.2 | **B2** `pending()` 逐行 `json.loads` 零容错：一行坏全队死（实证：10 条事件 attempts 恒 0 无法消费） | per-line try/except：坏行跳过+`log.error`+`alert(level="ERROR")`（进程级指纹去重 `_TORN_LINE_ALERTED` 防 drain 循环告警风暴）；返回签名不变 `list[事件]`；坏行被后续 `_rewrite`/repair 顺带剪除（原件留备份） | 直接探针（旧码）：`old pending() raises JSONDecodeError - Expecting value: line 1 column 10 (char 9)`；红跑 `TestE4JournalTornLineTolerance` 3 error | 3 用例绿：中间撕裂行→`pending()` 返回全部好行+ERROR 告警 1 条；坏行不阻断 drain（2 件全消费+坏行被剪除）；空行豁免语义不变 |
| 1.3 | **B4** 毒丸告警 `level="ERROR"`：`alert_webhook_dispatch` 只转发 CRITICAL failure 文件→毒丸到不了人（告警断链） | 一行改动：`drain()` 毒丸留档告警升级 `level="CRITICAL"`（语义=毒丸是需要人处置的致命态），留痕注释写明断链依据 | `test_poison_alert_level_is_critical` 红：`[('ERROR', '管线事件毒丸留档: ...')] and 'ERROR' == 'CRITICAL'` | 同用例绿：3 轮失败后毒丸告警 level=="CRITICAL" |
| 1.4 | **B4'** 毒丸处置工具缺失（docstring 说"人工处置后删行"无工具，总包手术只能手搓） | 新增 `repair(action, event_id)` + `_backup_journal()`；CLI 新增 `repair` 子命令：`--list`（列毒丸，只读）/`--drop <id>`（删毒丸/废件）/`--unpoison <id>`（摘 poison+attempts 归零，last_error 留档）；drop/unpoison 落改前自动备份 `.bak-repair-<ts>-<uuid>`；目标不存在=零副作用不备份；互斥参数组 | 红跑 `TestE4RepairCli` 6 failed（`repair` 函数不存在） | 6 用例绿：list 只列 poison/drop 带备份且备份含原件/drop 未知 id 零副作用/unpoison 后 attempts=0 且 drain 重放消费/CLI 三态派发 rc=0/非法动作 ValueError |
| 1.5 | **B5** `emit_sim_wallet_due` 无幂等闸（同文件其他 emit 均查重）：intake 多宿主并发同批重复开户事件 | emit 前查 `pending()`：同 kind+同 strategies 集合（strategy_id 排序比较，与次序无关）的**非 poison** 在队事件→不重复入队返回 `{"already_pending": True}`（对齐 scan_translated_backlog 查重模式；毒丸不算已入队=月度档 C2/X2 同款裁定）；intake 调用方只读 `out.get("event")`（intake.py:392），返回兼容 | `test_duplicate_emit_skipped` 红：重复 emit 落了 2 条（`already_pending` 键不存在）；`test_same_strategy_set_different_order_deduped` 红 | 4 用例绿：重复 emit 只记 1 条/集合乱序去重/不同集合照发/毒丸不堵重发 |
| 1.6 | **B3** heavy drain 全仓 0 调用 | **设计裁定不施工**（总包明示）：重活显式 drain 语义保留，不新增调度消费者；本轮补的是毒丸/坏行处置工具（1.4）而非自动 heavy 消费。E8 挖干佐证：85/85 已入账无积压 | —（裁定登记） | INVARIANTS 新增行留痕："heavy drain 消费者缺位为显式裁定" |

配套：模块头 `[INVARIANTS]` 新增"journal 原语并发与容错三治本"块、`[CONSUMERS]`/CLI description/模块 docstring 用法补 `repair`、`drain()` docstring 处置指引改指 repair。

## §2 测试读数（红→绿全程）

| 阶段 | 读数 |
|------|------|
| 基线（HEAD，未动码） | `tests/strategy_pipeline/test_pipeline_events.py` = **38 passed** |
| 红（新 18 用例 vs 旧码） | **11 failed + 3 errors**（+7 既有用例绿=行为钉子）；直接探针：旧 `pending()` 抛 `JSONDecodeError` |
| 绿（修后同套件） | **56 passed**（38 基线回归全绿+18 新全绿，3.97s） |
| 全回归 | `pytest tests/strategy_pipeline/ -q` = **253 passed, 2 failed**；2 败=`test_decision_orchestrator.py::TestCalendarDormancy`×2，**换 HEAD 版 pipeline_events.py 复跑同败**（换文件复证）=既有日历用例问题（疑 2026-10-01 假日敏感），与本环节无关 |
| 旁证回归 | `tests/pf_alloc/test_pf_alloc_event_wiring.py` 31 用例第 18 个（`test_wake_hook_orders_alloc_before_ledger_and_journal`）挂起，**换 HEAD 版同挂**=既有（疑与本 worktree 他队在途改动相关），非本环节引入 |
| Lint/语法 | ruff check 通过（2 条 invalid noqa 警告=HEAD 既有 `# noqa: bare-sql` 旧行）；`ast.parse` 通过 |
| 活体验证 | `python -m zephyr.strategy_pipeline.pipeline_events repair --list`（ZEPHYR_ALPHA_ROOT=worktree，真实 journal 为活体 1 行）→ `{"n": 0, "poison_events": []}`，只读零副作用（无 .bak 产生、journal 原样） |

新用例清单（18）：撕裂行容错×4（跳坏行+告警/告警进程级去重/drain 不阻断+坏行剪除/空行豁免钉子）、tmp 唯一化×3（含 pid/成功无残留/replace 失败清残留）、repair×6、emit 幂等×4、毒丸 CRITICAL×1。

## §3 与 st-circ-a7 F82/F27 的兼容性

- F82（spawn）/F27（尾段隔离）已提交进本 worktree HEAD=68fe30bd，本施工**叠加其上**：基线 38 用例（含 st-circ-a7 补的测试）修后全绿=零破坏实证。
- 改动面不重叠核查：F82/F27 落在唤醒链/spawn 侧（wire_data_scheduler 链与子进程派发），本轮只改 journal 原语区（`pending`/`_rewrite`/新增 `_journal_tmp_path`/`_backup_journal`/`repair`）、drain 毒丸告警一行、`emit_sim_wallet_due` 头部闸、CLI 派发段——唤醒链函数体一行未动。
- 唯一共享触点=`drain()` docstring（处置指引改指 repair）与模块头注释块，纯文档行。
- 若 st-circ-a7 尚有未落地在途编辑，冲突面=零（其改动不触 journal 原语区；以 git merge 时 diff 为准复核）。

## §4 六向台账

| 向 | 内容 |
|----|------|
| 上游触发 | `record()`←emit_c4_batch_completed（c4_batch_screen 落账钩子）/emit_sim_wallet_due（intake.py:390 钩子）/scan_translated_backlog·scan_c1_c2_backlog·maybe_emit_*（DataScheduler `task_completed` 唤醒链 wire_data_scheduler）/CLI emit；`repair()`←CLI repair（人工正门） |
| 下游消费 | `drain()`←唤醒链尾轻消费（allow_heavy=False）/CLI `drain --all`（重 kind 显式正门，语义保留）；毒丸/坏行→CLI repair 处置（本轮新增）；`alert()`→Alerter 落盘+webhook（仅 CRITICAL 出网=断链修复点） |
| 输入 | journal=`.runtime/strategy_pipeline/pending_events.jsonl`（活体，多进程写侧）；KillSwitch 状态探针；事件 payload（strategies/trade_date 等） |
| 输出 | journal 出队/毒丸留档；RECEIPT（last_receipt.json）；AUDIT_MARKER（date-marker 消费成功才落）；Alerter 告警（毒丸=CRITICAL、坏行=ERROR）；repair 自动备份 `.bak-repair-<ts>-<uuid>` |
| 真源锚 | 病根=e4_journal_surgery.md §遗留 B1-B5；修法先例=src/zephyr/ai_layer/scheduling/confirm_gate.py:655、src/zephyr/factor/offline_store.py:272；断链证据=src/zephyr/data/alert_webhook_dispatch.py（只扫 CRITICAL failure）；幂等模式先例=本文件 scan_translated_backlog/maybe_emit_monthly |
| 耗时账 | 施工全程约 45min（红测编写→红跑→实现→绿跑→归因复证）；新增常驻进程/cron/Timer=0（宪法 §9.3 合规，零新调度消费者）；套件耗时 56 tests≈4s，全目录 255 tests≈32s |

## §5 残余风险与移交（不阻断本环节交付）

1. **journal 跨进程无文件锁**（登记后续批）：tmp 唯一化消灭"互踩写坏/撕裂/WinError32"实证病灶；但 `record()` 追加与 `_rewrite()` replace 之间理论仍存丢更新窗口（A 追加后 B 以旧快照 replace）。修复需引入锁文件/合并重放机制=新机制，本轮裁定不扩面，登记移交。
2. `TestCalendarDormancy`×2 败=HEAD 既有（换文件复证），归属 decision_orchestrator 日历用例（疑假日日期敏感），建议总包另开小环节归因。
3. `tests/pf_alloc/test_pf_alloc_event_wiring.py` 第 18 用例挂起=HEAD 既有（换文件复证），疑与本 worktree 他队在途改动（internal_compute_provider.py 等）相关，归属总包归因，不在 E4/E5 范围。

## §6 纪律自查

- 禁 git add/commit/push：全程未做任何 git 状态变更（换 HEAD 复证用 `git show` 导出+cp，复证后原样恢复，`git diff --stat` 仅含本环节两文件）。
- worktree 起手核查：两目标文件与 HEAD 一致（不在他队 diff 清单）；他队改动（lane_c miner/factor indicators 等）零触碰。
- 活体 journal：测试全走 tmp_path 隔离（照抄既有 `state` fixture 模式），对真实 journal 仅 `repair --list` 只读验证一次。
