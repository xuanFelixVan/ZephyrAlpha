---
ttl: task_bound
completes_when: Owner 逐项批复呈报清单后归档
---

# 模拟盘三步启动战役 交付报告（st-sim-launch-20260922）

> 通宵执行令 2026-09-22｜终态=模拟盘恢复每日运转+排班链接电+日报出格+币圈快线结论｜全程 env=sim，丁域只读，乙域零触碰

## §0 一句话总结

模拟盘平台四件全部验活并复活：五病灶三修两件（+接电新件）全部落地，判定台账
`sim_daily_report` 建表并落首批 10 行（全结算），首日日报样张已出，币圈快线评估
=数据通/回测通（负面证据）/纸面不通，三针红蓝注入全响，两轮 76 测全绿。

## §1 平台复活对照表（五病灶→处置→验证）

| 病灶 | 根因 | 处置 | 验证 |
|---|---|---|---|
| R1 空壳运转（钱包全 open 零成交，策略引擎未接线） | 注册表 sim 条目的翻译件重放从未实现 | **NEW MOD-BT-210 sim_daily_runner**：E4 观察档 c4_* 翻译件 build() 重放→方案C 收盘价模拟单（sim_observe 平面）；首批 5 候选实跑 1 entry+4 cash | e4-replay 09-21 实跑落单+09-18 历史注入回补成功 |
| R2 QMT 模拟账户腿断（09-17/18 SKIP，09-21 exit 1） | 09-17/18=XtMiniQmt 未开（Owner 晨间 ritual）；09-21=ps1 `$ErrorActionPreference=Stop`+`*>>` 把 python stderr（xtquant pkg_resources UserWarning 实证在）变 terminating NativeCommandError，exit 1 且输出全吞 | **FIX-3**：python 调用段局部放宽 EAP=Continue，真 exit code+输出全落 paper_session.log（纯 ASCII 校验 0 非法字节+语法 0 错） | `--dry-run` 实连 PASS（账户 8886156677，cash 9.99M，持仓 510300×1100+600036×100）——09-21 型失败根因即此 bug |
| R3 日刊 freshness 恒 false（09-15 起九连假阳） | 探针要求 kline max≥体检日 T，但事件链早间跑日刊，当日数据必未落 | **FIX-1**：探针时点感知——交易日北京 15:05 前→期望 T-1（交易日历感知）；收盘后/历史日/非交易日→期望 T（旧语义）；日历不可用不放宽 fail-closed | 四场景单测+live 09-21 fresh_ok=1 首绿；断供探针 09-30 注入 degraded=1 双异常真响 |
| R4 钱包额度回退 flat（分配链无快照行） | 分配链在跑（alloc_budget_daily 09-15..09-21 每日两策略行），错位来自链外手工开户跑在分配落地前 | 链内 FIFO 序设计本正确（alloc 先于 ledger）；不改丁域，仅报告披露 | 分配快照 09-21 实测（VREV 698K/E-TIMING 390K） |
| R5 孤儿钱包每日自我续开户 | STR-AUTO-001/STR-MULTIFACTOR-001 不在注册表（lifecycle=sim 仅 2 条）不在分配 universe，却被 intake 事件面每日续开 | **FIX-2**：ensure_wallet 注册表 SSOT 卫兵——mode=sim_daily 平面非在册条目拒开户（why=not_in_registry_sim）；逃生=--allow-unregistered 显式留痕 | 卫兵两路径单测+live 验证；平台日报哨兵抓到同两孤儿（见 §2） |

## §2 排班链接电证据（丁域只读消费，零写入）

- **plan 桥**：09-21 判定行落台账——计划 MOD-PLAN-030（asof 09-20）+盘中归类"进攻"→
  S1_attack→action=trend_follow_no_chase **无订单语义**→posture=unexecutable 如实记录
  （不伪造信号=平台铁律）；结算 posture_check=1.0（口径自洽）。
- **可执行子集**：防御（stand_aside_defense）→flat 是唯一可机械执行姿态；五态中低迷/亢奋
  不在计划三场景树，如实记 no_matching_scenario。
- 判定台账 `c1_backtest.sim_daily_report`：10 行=09-18 注入 2+09-19 疤 1（unresolvable，
  零 DELETE 纪律）+09-21 正式 7（plan 桥 1+E4 重放 5+平台 1），未结算行=0。

## §3 首日日报样张

[first_daily_report_20260921.md](first_daily_report_20260921.md)——平台总览（sim_daily 4 钱包+sim_observe 5 钱包）/
钱包明细/判定台账三平面/接电口径披露。数据层=sim_daily_report，日报=台账行渲染（无第二真源）。

## §4 币圈 7×24 快线结论

**不通（差距如实报）**：①数据 PASS（85 币/UTC 日界在轨无滞后/主流币 90 天全）；
②回测 PASS 但**日线 20 日动量 BTC/ETH 年化 Sharpe=-0.31/-0.30 胜率 49%**=无边际负面证据；
③纸面不通（ccxt 未装/QMT 不覆盖/无实时价源）。三选项呈 Owner：真 7×24 立项（需实时价源+通道）/
日频内部记账降级形态/不立项。详见 [crypto_fastlane_eval.md](crypto_fastlane_eval.md)。

## §5 验证记录

- **两轮 0**：新电池 17 例+受影响既有件（journal/paper_ledger/start_paper_session）=
  76 passed 连续两轮（`test_rebuild_matches_pocket` 为 **HEAD 既有红**（stash 对照实证，
  54vs53 行数据漂移），非本班引入不代修）。
- **红蓝一轮**：红①历史日注入回补（09-18 两候选落行）✓；红②无计划日（09-19）暴露
  非交易日误落行缺陷→当日修复（is_trading_day 门），误落行诚实结算 unresolvable 留疤✓；
  红③日刊断供探针（09-30 未来日）degraded=1 双异常真响✓。蓝=09-21 全链实跑✓。

## §6 停手项与呈 Owner 清单

1. **孤儿钱包存量处置**（R5）：卫兵已止血开户，存量 14 行保留零删除——归 Owner 定 lifecycle（retired/补登记）。
2. **plan 订单映射政策**：进攻/震荡两动作要变真模拟单需 Owner 批场景→订单映射（本班不伪造）。
3. **E4 观察档扩量**：现 5/51 候选（自裁 A3 控面），扩全量或选子集待令。
4. **日刊排程语义**：FIX-1 后早跑/晚跑皆健康，若要求"收盘后跑"的排期表调整归排期门位。
5. **QMT 晨间 ritual**：XtMiniQmt 需 Owner 交易时段开机（09-17/18 SKIP 根因）；FIX-3 后明早 09:25 首验真 exit code。
6. **币圈快线三选项**（§4）。
7. **HEAD 既有红**：test_rebuild_matches_pocket（54vs53）——数据面漂移，建议归数据线核查。

## §7 合规留痕

- 冷启动全序（Python 3.12.8/reaper 存活/worktree+心跳 daemon）；
- RULE-CAPABILITY-LOOKUP 反查留审计（回测→MOD-BT-001 等）；RULE-DEPGRAPH 设计节点
  MOD-BT-210/211+大白话翻译 3 条；CREATE-GUARD token 4 件；claim 3 文件+release 待提交后；
- 净零声明：新件 3 个（runner/schema/apply_ddl）替代对象=蓝图批 1-4 明示缺口
  "策略引擎未接线/翻译件重放/日报台账"（非重复建设）；临时产物全在 .runtime/tmp（TTL 自清）。
