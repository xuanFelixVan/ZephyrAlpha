---
ttl: task_bound
title: "P 线施工进展台账"
session: zc-lane-p-20260927
completes_when: "P1~P5 五项全部落地或登记，战役收官后随 docs/_working 归档"
---

# [BLUEPRINT] | docs/_working/fullconnect_campaign/lane_p_notes.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

P 线施工进展台账（全流通战役 zc-lane-p-20260927）：逐项修复记录/测试读数/落地哈希

证据真源：docs/_working/chain_fullflow_20260926/mine_pipe_blockage_substages.md（§3/§7 C1）+ mine_pipe_false_green_census.md。

## P1 str/date 共因修复（#30/#34 + _repaired 第三实例）

- 定位：FetchPayload.start/end 注记实测 datetime.date（provider_base:72-73），compute 核
  行字段一律 ISO str，provider→compute 交接处契约无人执行：
  - consensus_daily_compute.build_consensus_rows:155 `td_iso > hi_iso`（崩 '>'）
  - financial_derived_compute.run_compute:397 `row["announce_date"] < start`（崩 '<'）
  - consensus_daily_repaired_compute.run_compute_repaired（同形状第三实例，经 A 段同核）
- 修：provider_base.py 新增 `norm_boundary_date`（None/空→None；str→截前 10 位；date→
  isoformat），一处规整覆盖三实例；三处边界比较前统一调用。反例护栏：pattern_win_rate
  不同根，未打包同修（census §3 反例在案）。
- 测试：三测试文件先红后绿（红=逐字复现 task_runs 原文 TypeError），
  tests/scripts/test_build_consensus_daily.py + tests/zephyr/data/test_financial_derived_compute.py
  + tests/scripts/test_build_consensus_daily_repaired.py 合计 44 绿；
  另 provider 契约/内部 provider 回归 19 绿。
- 落地：commit 入队 q-…-0001 → GATE-ALGO-FLOW 拦（三 impl 模块缺 ALGO_FLOW 锚，P2-1 口径
  补块+externalize_algo_flow.py 出仓后）requeue → q-20260927-zc-lane-p-20260927-0006（7 文件）。

## P2 l2_tick_snapshot "未知 capability: tick_snapshot"

- 考古定案：FAILED@2026-07-22 根因已于 2026-09-09 8981a53f29 修复（capability
  tick_snapshot→l2_tick 改名 + 自引用 fallback 清理）；当前 tasks.yaml `l2_tick` 在
  miniqmt provider `_DIRECT_ROUTES`(:239) + `CapabilityContract`(:536) 双登记。
- 只读复核：真实 tasks.yaml 271 任务过 validate_task_capability_contracts = 0 违规
  0 ERROR；表 0 行现状=disabled:true（L2 付费权限 + miniQMT 09-18 退役冻结），非活性 bug。
- 修（测试面）：validator 原单测全合成任务、真配置无护栏——新增
  TestRealTasksYamlConsistency 两测试（真配置 271 任务零 ERROR 同启动判据 +
  l2_tick_snapshot 盲钉：disabled 被 validator 跳过的防改名回归钉）。
  tests/zephyr/data/test_capability_validator.py 50 绿。
- 落地：commit 入队 q-…-0002 → ruff-format 拦（reformat 后）requeue →
  q-20260927-zc-lane-p-20260927-0005。

## P3 etf_benchmark date 列 ALL_NULL

- 只读 DESCRIBE c1_market.etf_benchmark 实核：publish_date/base_date 皆 Date；
  task 块此前无 date_col → census 新鲜度探针读 "-"（ALL_NULL 面）。
- 修：tasks.yaml etf_benchmark_refresh 增 `date_col: publish_date`（公告日=新鲜度锚；
  base_date=指数基日非新鲜度）。写后核实：271 任务数不变、契约 0 ERROR、validator 50 绿。
- 残余（登记 99_skipped_for_owner #19）：`_fetch_etf_benchmark` 为恒空 yield（rows=[]，
  SUCCESS 假绿本体），且实调 index_stock_info(symbol=000300) 与声明
  fund_etf_fund_info_em 不符——修须实弹验证 akshare 通道，禁实弹，呈 Owner。
- 落地：commit 入队 q-20260927-zc-lane-p-20260927-0003。

## P4 restricted_shares 前瞻值 2035-10-29 污染新鲜度尺

- 病灶：supply_sentinel._check_date_leg 的 max(date_col) 上界受条目 past_only 门控；
  未开的表（restricted_shares unlock_date 合法含未来解禁排期）前瞻行垫高 max → lag
  为负 → 判据永绿失明。
- 修：新鲜度腿恒追加 `{date_col} <= toDate(today)` 谓词（past_only 保留给行数地板/
  填充率腿口径）；已含上界不重复拼。
- 测试：tests/zephyr/data/test_supply_sentinel.py 24 绿（含新增两件能红测试：
  前瞻行垫高不得掩盖真实停更 max 剔前瞻=2026-06-01 lag=118 必红；过去侧真新鲜剔除不误伤）。
- 落地：commit 入队 q-…-0004 → GATE-ALGO-FLOW 拦（supply_sentinel 缺锚，补块出仓后）
  requeue → q-20260927-zc-lane-p-20260927-0007。

## P3 补记 / ALGO_FLOW 出仓附记

- P3（tasks.yaml date_col）已 DONE：q-20260927-zc-lane-p-20260927-0003。
- GATE-ALGO-FLOW 补块出仓共 4 件：consensus_daily_compute / financial_derived_compute /
  consensus_daily_repaired_compute（随 0006）+ supply_sentinel（随 0007）；
  机器块 yaml 落 docs/03_modules/_domain_data/algo_flow/{implementations/,data/}，
  4 yaml + 本台账 + 99_skipped_for_owner #19/#20 随收尾批入队。

## P5 suspend 三腿 + realtime_snapshot_incremental 0 行（只读诊断）

- realtime_snapshot_incremental：c1_market.realtime_snapshot 实测 0 行（max=1970 纪元）。
  data/failures 112 个降级件全数归属本任务（08-26~09-21），错误一致=
  `Can not decode value starting with character '<'`——sina 源（stock_zh_a_spot）返
  HTML 反爬页。历史链条：原东财 stock_zh_a_spot_em 因 IP 级 TCP RST 封锁被
  #ARCH-AKSHARE-ANTICRAWLER-001 弃用切新浪；现新浪同遇反爬。修复=换源/多源兜底
  （东财冷却复用、腾讯源、qmt_bridge 三候选），**选定与验证均须实弹调 akshare**，
  禁实弹 → 登记 99_skipped_for_owner #20。
- suspend 三腿：c1_market.suspend 复测（09-27 只读）36 行、max=2026-09-23——
  census 探针时点（09-24 三腿 SUCCESS+0 行）为双源（东财 stop_em+百度兜底）同时段
  反爬空返的暂态，非持久断裂；映射层已防御式解析（akshare_provider:9185 候选列名）。
  09-24 交易日快照缺席与双源反爬同因，无静态可修面；持续性观察归哨兵（P4 修后
  新鲜度尺不再被骗），登记 #20 附记。
- 结论：两项均为活源可用性问题，静态证据不足以安全改码（改错源=写路径污染），
  按纪律登记跳过。

## 通用纪律留痕

- 每项改前 git status 核无他会话在飞修改 + lock_files.py acquire（全数 ACQUIRED）。
- RULE-CAPABILITY-LOOKUP：施工前 capability_lookup.find 会话审计已留（date boundary
  compare / tick_snapshot capability 两查，0 命中即无既有规则挡道）。
- 提交全走 git_commit.py 窄清单（--allow-non-worktree=2026-08-13 裁定 AI 可默认；
  --allow-overlap=SESSION-REQUIRED 逃生），锁忙自动入队 4 件（qid 尾号 0001~0004）。
