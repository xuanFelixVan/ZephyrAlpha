---
ttl: task_bound
---

# lane-datapipe 车道日志（数据断供修复五件）

> 会话=st-ffchief-20261001｜车道=lane-datapipe｜日期=2026-10-01｜本文可并入 LEDGER.md
> 输入=docs/_working/fullflow_chief_20261001/data_pipelines_survey.md §2/§4（12 断供+12 断点）
> 自裁授权=Owner 总包令（堵死→登记跳过，禁提问禁停）

## 13:3x 冷启动

- Python 3.12.8 PATH 修正 + process_reaper 存活（scanned=20 whitelist=17 killed=0）——写操作前提在岗。
- 精读 survey §2/§4：12 断供清单+12 代码断点带证据指针；按 P1→P5 优先级施工。

## P1 macro_data_incremental RepoRate 'frValueMap' KeyError（215 连败）——已修，qid 0009 done

- **根因（实测取证，非上游结构变更）**：akshare 1.18.75 `repo_rate_hist` 内部对
  start_date/end_date 做 `[:4]/[4:6]/[6:]` 紧凑切片拼参（site-packages/akshare/rate/repo_rate.py:72），
  provider 原传 `%Y-%m-%d`（"2026-09-01"）被拼成 `"2026--0-9-01"`，chinamoney FrrHis 接口对
  非法日期返回空/兜底 records，`pd.DataFrame(records)` 后无 `frValueMap` 列 → KeyError。
  上游结构未变（records[].frValueMap 实测仍在）：**变的是参数格式容忍度，病根=provider 日期格式**。
- 实弹对照：dashed 格式实调 `KeyError('frValueMap')`（复现连败）；紧凑 `20260901..20261001`
  实调 shape=(22,7) 22 行全期限。
- 修法：`_fetch_repo_rates` 日期改 `%Y%m%d` 紧凑格式（src/zephyr/data/implementations/akshare_provider.py）。
- 验证：新增 tests/data/implementations/test_akshare_repo_rate.py **4 passed**（紧凑格式断言/
  新结构 transform/空 df 降级/dashed 拼参病根文档化断言）；真调 dry-run：22 日×6 期限=132 rows
  （FR001/FR007/FR014/FDR001/FDR007/FDR014 全恢复，2026-09-30 档在列）。
- 提交：`--files akshare_provider.py,test_akshare_repo_rate.py --enqueue` →
  **q-20261001-st-ffchief-20261001-0009 = done**（git log 已核真实归属）。

## P2a strategy_pipeline pending_events.jsonl.tmp 多进程竞争——内容已落共享工作区，见 §队列交缠

- **根因**：`_rewrite` 固定名 `pending_events.jsonl.tmp`，DataScheduler 唤醒 drain/CLI drain/
  c4+intake 落账钩子多进程互踩 → WinError 5（拒绝访问）/32（共享冲突）/2（tmp 被他进程
  replace 消费）三种错混发；且读-改-写无跨进程锁=丢更新风险。
- 修法（复刻仓内 confirm_gate._byte_lock 先例，零新依赖）：
  ①`_byte_lock`（msvcrt LK_LOCK/flock，锁文件只建不删，拿不到 TimeoutError fail-closed
  对齐本件 ERROR_CONTRACT）；②tmp 名带 pid+uuid 唯一 + `os.replace` 原子替换 + 失败清残骸；
  ③record append 与 drain 选取/出队/计数三窗口持闸，**handler 子进程在锁外**（重活不持闸）。
- 验证：tests/strategy_pipeline/test_pipeline_events.py **48 passed**（含 4 新增：唯一 tmp 零残骸/
  锁互斥与无 stale/record×drain 并发 20×20 零 WinError 零丢失）。
- 提交交缠（如实报）：本车道 qid 0012 快照**死于 IMPORT-INTEGRITY gate**（`import fcntl`
  Windows 不可解析——gate 要 `# noqa: import-integrity` 豁免标记，gov_audit/writer.py 先例；
  修法已打：两处 noqa 改 `import-integrity`，48 测复绿）。lane-f82 同文件在飞（13:58/14:00/14:05
  三连改，其增量基于本车道 P2a 之后的文件态）——按宪法 §3.4 不硬闯不吸收，P2a 内容将随 f82
  的 pipeline_events 提交自然落地（其 worktree 基底含 P2a 全部修改+noqa 修复），落地后由 chief
  在 git log 归属核验时双记。

## P2b local_replay technical_indicator 毒丸（09-21 卡死）——根因机制已修

- 现场核实：**文件本体已由 st-storageswap-20260930 于 `data/local_fallback/_quarantine_20261001/`
  隔离留证**（361,499 行 0921 批次 + README：回灌结构性必败=cols_clause null→活表序截 206 列
  vs writer 序错位；恢复路径=重算非回灌，`.runtime/tmp/ti_minute_recalc.py` 直驱 ReplacingMergeTree
  幂等覆盖）；manifest 已空、全库 fallback .tsv 仅剩隔离区 4 件——"备份+清"前班已毕，不重复搬运（自裁）。
- 本班治**产生根因**（survey §4-4 失败计数上限+毒丸隔离区）：src/zephyr/data/local_replay.py
  ①manifest 条目增 `failures` 计数；②连续失败 ≥`POISON_QUARANTINE_THRESHOLD=20` 且
  `_ch_reachable()` 探针通过（文件级结构性失败判据）→ 自动搬 `_quarantine_<date>/`+README 台账
  +manifest 除名，防单文件无限重试堵队；③CH 全局断连（探针不过）**不隔离**防长断连误伤整批；
  ④`_adopt_orphans` 显式跳过 `_quarantine*`（隔离件永不收编回灌）。
- 验证：tests/zephyr/data/test_local_replay.py **35 passed**（含 5 新增：err_sink/隔离搬移+README/
  达阈值隔离+manifest 归零/断连不隔离/孤儿收编跳过隔离区）。
- 提交：`--files local_replay.py,test_local_replay.py --enqueue`（git_commit 后台在途=网关锁排队中，
  qid 待补记；staged 快照已入袋）。

## P2c pf_alloc 09-29 毒丸（rc=1）——调查结案，零代码改动

- 毒丸事件 PIPE-20261001-003352-9028f3（pf_alloc_daily trade_date=2026-09-29）已不在 journal
  （pending=0，他班/drain 清场）。
- 根因（scheduler_run.log 00:36:47 全栈捕获）：`allocation_orchestrator.py:1058
  AttributeError: 'BaseWeightTable' object has no attribute 'sleeve_phases'`——**会话期主区代码
  版本错位**（sleeve_phases 供件增量当时未提交、消费侧先行；st-c9-f34 提交注记
  "他会话 sleeve_phases 供件增量尚在主区未提交的基线既有红"在案）。
- 现状自愈实证：`--no-write --date 2026-09-29` 影子复跑 **rc=0**（regime r3@0.9998/source_date
  09-29 滞后 0 日，分配计算全链健康）；alloc_budget_daily **09-29 已有 2 行**、全表 max=09-30
  ——无数据缺口，无需补跑（补跑=只增表同日双写风险）。
- 处置：登记结案不改代码。

## P3 hk_connect_flow 僵尸任务——登记已齐（裁定#257 先行），零操作

- tasks.yaml 两任务（hk_connect_flow_incremental/full）均已 `disabled: true`+disabled_reason
  （2026-09-16 通宵总包 GW4，裁定#257，止于 2024-08-16 源级终止论证在案）；今日 scheduler log
  零执行实证。known_data_gaps.yaml `hk_connect_flow_source_discontinued` status=accepted
  （2024-08-17 起永久缺口，不补历史）。无独立 schtasks 任务（经 DataScheduler daily_capital
  槽 in-process 跑，disabled 旗标即停）——`schtasks /disable` 无对象，CR-5 退役+缺口登记两态俱备。

## P4 catchup_guard overdue=44 补 15 截断 29——设计如此，登记说明

- catchup_guard.py:66 `MAX_RERUN_PER_RUN = 15`（INVARIANTS §8 在册："单批补跑≤15顺延收敛"）：
  每日 05:30 必跑（国庆假期 05:38 照跑实证），截断 29 项入 `cap_deferred` 落 progress_store，
  次日按 cadence 优先级（monthly→weekly→daily→intraday）自然重排补跑，3 日内收敛。
- 假期背景复核：daily 桶 overdue 判据=last SUCCESS < 最近已收盘交易日（09-30），盘后批全绿
  不新增；always_on 桶（event_driven 每 3 分钟在跑）自我治愈。**非 bug，不做修改。**
- 假期后动作（移交）：如需未补清单，从 progress_store 读 catchup_guard 档 cap_deferred 导出即可。

## P5 index_valuation_daily_v2 空表——接不动，处方已在册（登记强化）

- 全仓 grep 复核：src/ scripts/ tests/ **零写入方**（唯一引用=空表普查 census
  scripts/governance/wave3/recheck_empty_tables.py:80）；**零消费方**；CH 实读 count()=0。
- 本质：v2=旧 index_valuation 演进**平行件**，采集腿从未建。v1（index_valuation_daily）已于
  2026-09-20 重建+验收（ReplacingMergeTree(ingest_ts)+日频 compute 腿 `index_valuation_daily_compute_daily`
  在产，survey 口径 09-30 绿；隔离副本=index_valuation_daily_quar_20260920 8125 行）。
- 处方（与 known_data_gaps.yaml `index_valuation_daily_v2_no_collector` status=open 一致）：
  净零原则 §4"零触发零消费→退役"——v2 退役候选（#311/#328 rename 隔离 7 天再 DROP 通道）；
  若建腿，先裁 v1/v2 口径归属（Owner 门，数据源候选=akshare 指数估值接口）。**假期不接新链**
  （禁真跑回填），登记移交 Owner 裁。

## 队列交缠与治理事件（如实报）

- 会话号共用（st-ffchief-20261001 总包多车道同号）：commit_queue 死单 0001-0007 系他车道
  （ghost_session/各 gate 阻断）；0005 死因=CAPABILITY-LOOKUP-REQUIRED——本车道已于 14:0x
  补三笔 `CapabilityLookup.find(session_id=st-ffchief-20261001)` 审计（akshare/local_replay/
  journal 并发三关键词），后续入队单应过闸。
- 本车道死单：0012（P2a，IMPORT-INTEGRITY fcntl——noqa 豁免标记修复已打在工作区）。
- gateway 锁竞争：P2b 直连提交长时间等待网关锁（后台在途）；队列带Online 正常消化（done 4→）。

## 15:0x 总包裁定补丁二连执行（fcntl 可移植锁 + ch_reader 收口 + 目录迁移）

- 会话注册过期（ghost_session 死单族根因）：`session_worktree_start(allow_concurrent=True,
  allow_workspace_drift=True)` 重注册成功（WORKSPACE_DRIFT 293 件=多车道在飞，TRAE-079
  Phase 2 降级直走网关文件锁串行）。
- 补丁①（0012 IMPORT-INTEGRITY）：fcntl 分支整段移除——`_byte_lock` 改 msvcrt 单侧锁
  （生产平台=win32），POSIX 分支零锁直通（唯一 tmp 后缀+os.replace 原子替换兜底），
  两处 `# noqa: import-integrity` 一并撤除（无 fcntl import 即无悬空）。
- 补丁②（CH-FINAL-GATE，#ARCH-CH-007）：`_ch_reachable()` 探针 ch_writer.query 直读改
  `ch_reader.query("SELECT 1")`（FINAL 收口统一）；SELECT 1 无 FINAL 语义，
  以 `strip()=="1"` 判可达（ch_reader 失败返回 ""）。归因订正：0019 死单实为 t0 族
  （他车道）非本件，本件 ch_writer 直读系预防性同规则整改。
- 目录迁移遵令：本文已随战役整体迁移至 docs/_working/circulation_chief/logs/（R5 禁数字
  后缀；旧 fullflow_chief_20261001 目录已整体迁走）。
- 补丁后复验：local_replay 35 + pipeline_events 48 = **83 passed**，ruff check/format 双清。

## 15:3x-16:3x 重投三连与逐 gate 收敛（P2a 落地战）

- 0029（P2a 第一重投）队列异常失踪（pending/processing/done/dead 四态均无、git 无落痕）
  ——快照仍在袋 blob 零丢失，重投。
- 0036 死于 OPEN-WITHOUT-WITH（`fh = open()` 手动生命周期）→ `with open(...)` 句柄化
  （unlock 后即关，语义不变）。
- 0046 死于 GATE-ANY-ABUSE：收编的 f82 件 `_order_store_sink(journal: Any)` 裸 Any 参数
  → `journal: object`（鸭子类型 getattr state_dir，行为零变，收编件合规化披露在案）。
- **P2b 落地实锤：0030 done → commit f7bf5d7235**（local_replay.py +118/-21 + test +88，
  两文件归属已核，毒丸隔离机制入主线）。
- **P2a 落地实锤：0053 done → commit 75947a5c29**（pipeline_events.py +157/-31 + test +137，
  两文件归属已核，16:25:46 落主线；袋内含 f82 收编件 sink 接线，其权益随袋如实携带）。
- 本车道三件代码修复（P1/P2a/P2b）全部落地，车道收工。

## 交付态汇总

| 件 | 状态 | 验证 | qid |
|----|------|------|-----|
| P1 RepoRate | 落地 | 4 测+132 rows 实调 dry-run | 0009 done（commit 6d4177ec4d 归属已核） |
| P2a journal 串化闸 | 落地 | 48 测+ruff 双清 | 0053 done（commit 75947a5c29 归属已核；0012/0036/0046 逐 gate 收敛史在案） |
| P2b 毒丸隔离机制 | 落地 | 35 passed | 0030 done（commit f7bf5d7235 归属已核） |
| P2c pf_alloc 调查 | 结案零改动 | 影子 rc=0+CH 2 行 | N/A |
| P3 hk_connect_flow | 登记已齐零操作 | 零执行实证 | N/A |
| P4 catchup_guard | 设计如此登记 | 代码+INVARIANTS 在册 | N/A |
| P5 估值 v2 | 处方在册移交 | count=0+零消费 grep | N/A |

> 归档注：本文件=logs/ 族 gitignore 未跟踪工作笔记（lane-f04 同款），交付以本文件在盘+
> LEDGER 并入为准；commit 尝试被 .gitignore:234 拦属预期，非事故。
