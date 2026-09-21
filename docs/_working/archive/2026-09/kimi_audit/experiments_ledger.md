---
ttl: task_bound
rule_form: data
verifiability: manual
title: Kimi 深度裁定班次·实验台账（每启动一行，判据启动前写死）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
---

# 实验台账（Kimi 深度裁定班次 2026-09-17）

> 协议=主案 §5.1：脚本 + 产物路径 + 机读判据 + 预计耗时全部启动前写死；哨兵 `.runtime/tmp/exp/<id>.done`；每战场收尾扫一次本表。
> 脚本全部在 `.runtime/tmp/exp/`，日志同目录 `<id>.log`，产物 `<id>_result.json`。reaper 白名单已登记（data/runtime/process_reaper_keep.txt）。

| id | 战场 | 启动时刻 | 命令 | 日志 | 产物 | 机读判据（什么算红） | 预计耗时 | 状态 | 结论 |
|---|---|---|---|---|---|---|---|---|---|
| S2-exp | S2 做T v2 最小毛边际 | 2026-09-17 15:50 | `python .runtime/tmp/exp/exp_s2_tv2_margin.py` | s2.log | s2_result.json | 15min 级 100k/500k 档 required_capture_h1 全 >0.50=战役红；15min 覆盖 <400 交易日=数据红 | 分钟级 | **done** | 数据够（15min 471 日/3464 日全史）；指数分钟源全级别 EMPTY 坐实；15min 中位振幅 26bp，100k 档 RT 成本 6.7-11.3bp → 所需捕获率 0.26-0.43（黄），压力滑点档 0.70（红）→ 进 S2 裁定 |
| S6-exp | S6 组队复算 | 2026-09-17 15:50 | `python .runtime/tmp/exp/exp_s6_team_recalc.py` | s6.log | s6_result.json | 复算 Sharpe 距 1.541/1.568 两口径均 >0.05，或 maxDD 差 >0.01，或 ρ̄ 差 >0.02 => 报告数字不可信 | 秒级 | **done** | 数字全真：复算 1.566（vs 1.541/1.568 两口径都在差 0.025 内）、maxDD -0.13014 分毫不差、ρ̄ 0.165；新发现=FACT-4db4c41e 零换手 ann_ret 60%=beta 嫌疑、CAND-e3da6fa7 危机窗全零收益 → 进 S6 经济解释 |
| S7-exp | S7 成本敏感性 | 2026-09-17 15:50 | `python .runtime/tmp/exp/exp_s7_cost_sens.py` | s7.log | s7_result.json | 池均成本落 [2.3,3.1]bp/日 之外=口径红；成本×1.5 存活数腰斩=成本脆弱红；组队 m1.5 Sharpe<1.0=组队成本脆弱 | 秒级 | **done** | 池均 2.695bp/日（年化 6.79%）口径真实；×1.5 存活 17→16 不腰斩；组队 m1.5=1.34/m2.0=1.11 不脆弱 → 进 S7 裁定 |
| S14-exp | S14 前视探针回放 | 2026-09-17 15:50 | `python .runtime/tmp/exp/exp_s14_lookahead_probe.py` | s14.log | s14_result.json | pit=-1 产物与 pit=0 逐字节相同=门卫静默吞负值红；sharpe(B)−sharpe(A) <0.05=探针不敏感（记无效非无前视） | 分钟级×3 跑 | running（首轮脚本 bug 已修，二轮跑中） | — |
| S12-exp | S12 历史极端日反证 | 2026-09-17 15:50 | `python .runtime/tmp/exp/exp_s12_extreme_windows.py` | s12.log | s12_result.json | 危机窗 ρ̄>0.50=分散失效红；窗 maxDD>1.5×全样本=红；组合跑输指数 10pp=红 | 秒级 | **done** | PASS 无红，但 W2/W3 窗 ρ̄=NaN（CAND-e3da6fa7 全零收益致方差 0）=信息遮蔽点，进 S6 追查 |

## lane 合并台账（v4 总代理协议，2026-09-17 晚班）

| lane | 回收时刻 | 结论 | 采纳/否决 | 理由（一句话） |
|---|---|---|---|---|
| A1 提交税 | 17:5x | 24h 309 笔实测衍生税 25.6%、严格可消除 11%；integrity 复发根因=capability_canonical_file_registry 在 golden-hash 保护清单且 42 笔触碰→每 flush 派生一笔 | 采纳 | 逐笔 diff 取证，无编造 |
| A2 堵点本 | 17:5x | 974 次阻断多为语义型真触发；门禁链 P50 46.4s 是瓶颈；NOTHING_TO_COMMIT 快照漂移 ×87 为队列死信 TOP；CLAIM-REQUIRED 成因链实锤 | 采纳 | 五栏齐备、四 jsonl 全聚合 |
| A3 吞吐建模 | 17:5x | 系统上限 24 笔/h（serializer 单通道 S=149s 实测吻合）；N=50 需 ~100/h；提速序=claim 改制→门禁 diff 化→k 通道；watchdog 37% 零变化重复写自激实锤 | 采纳 | 模型假设逐条标实测来源，仅一例外已标注 |
| B1 前视取证 | 17:5x | 主引擎 PIT 防线扎实；破口在 C4 翻译件生态：V1 当前成分回灌历史(15/85)、V2 gftd 同bar(探针 RED)、V3 模板 assemble_weights 无 ≤T-1 平移(6 件全中,探针 RED)、CGO 排除险情(GREEN 守卫) | 采纳 | 双探针 RED 实锤+一反证 GREEN，有非空自检防空转 |
| B2 假绿清单 | 17:5x | 17 变异 13 杀 4 存活；钱闸与昨夜新件全真绿；假绿集中在老治理测试三病灶；5 文件 12 处断言已直改复跑 103 绿；新发现=S11 metamorphic 一件基线即红（全仓全绿说法不成立） | 采纳 | 变异全还原零残留，自测闭环 |
| B3 外推对账 | 17:5x | 6 断点全实锤：商品期货主力连续表 0 行（名实差最大）、北向静默加零 13 个月、399106 真源进料口仍死、regime 快照死窗伪观测两代并存；12 件已交付结论对账无辜 | 采纳 | CH 实测行数/日期锚全带 |
| C1 减法归类 | 17:5x | 542 蓝图四态=建83/合4/废12/挂192/保留251；注册表机器实算 74 件（空壳1/缺失2/僵尸18）；孤儿强候选 6 件；三处口径差异已标 | 采纳 | 全机器产出可复算，未越权决策 |
| C2 契约草稿 | 17:5x | 15 接缝裁定（10 新增/5 细化/1 冲突待裁 CD-01 暂缓）；缺口 7 条最大真空=回测产物可信度无人签发（GAP-01 归 E4）；重叠 5 条全判合理冗余 | 采纳 | 与在册 1389 行契约逐条对账，未推翻既有裁定 |

## 终局轮 lane 台账（2026-09-17 晚，授权升级轮）

| lane | 结论 | 采纳 |
|---|---|---|
| T 做T窄考试 | RED：共振组 +0.88bp/边 vs 对照 +0.87bp 不可区分（p=0.4997），净 -7.5bp——S2 砍裁定实证加固；附赠时区劈叉发现（移交数据线） | 采纳（裁定#304 证据链） |
| G1 网关手术 | R-10 死会话回收+R-04 claim 生命周期，镜像经 L0 审查 apply，22+301 测试绿 | 采纳已落地 351a7a1d |
| G2 R-05/R-06 | watchdog 状态机化+告警冷却 1800s，117 绿 | 采纳已落地 a6939367 |
| E 八件真跑 | E2 接线绿/E3 红(新抓第二处哨兵悬空)/E4 闸骨架/E6 双尺零不可解释翻转/E7 涨跌停引擎洞 2 件真红/E8 门禁静默通路钉扎 | 采纳 f6549823 |
| P1 组队重构 | 剔除双死刑件：新最优纸面 1.924/稳健 1.381；三笔账全线恶化（净 0.155）；alpha 供给论加固；新队全非放行档=观察档 | 采纳（裁定#322） |
| P3 alpha 点火 | E1C 13 候选 1 PASS（E1C-09 +6.82bp/日 DSR 0.7256）；B 撮合 20→6 首批 0 PASS 不捞；发现 consensus 表 2022-2026.07 整段 0 行 | 采纳（窄化裁定在 p3_prereg） |
| P4 S13 回验 | WIN：净 1.13>等权 0.38+0.1，九格全 WIN；maxDD -24.7% 代价+CRISIS 乒乓 83bp 附注 | 采纳（裁定#305 转正资格） |
| P5 V/B2 取证 | V-03~V-07 全坐实+分级处置单 | 采纳（裁定#323/324，回写已落 01fbfad1） |
| P6 L4/B0 | L4 执行族 15/15 过（滑点 2.56bp）；B0 15 条 14 valid+1 挂 | 采纳（Flash F01-F03 包） |
| E5 迟滞四臂 | 三方案全负（-37%/-60%/…）；迟滞臂 +5.5pp 方向确认（STD-SWITCH-001 迟滞条款实证），方案本体不可上线（S13 F-1 加固） | 采纳（证据入增补版） |
| RB/P2 压测 | 两度被中断（内存/人工）——单发低并发重启，极限档留 Flash | 待跑 |

## Flash 业务施工班台账（st-flashbiz-20260918，2026-09-18 凌晨；作业簿=docs/_working/flash_biz/）

| id | 战场 | 启动时刻 | 命令 | 日志 | 产物 | 机读判据（什么算红） | 预计耗时 | 状态 | 结论 |
|---|---|---|---|---|---|---|---|---|---|
| biz4 | E1C-09 E4 完整考试 | 2026-09-18 01:58 | `python .runtime/tmp/exp/flashbiz/biz4_e1c09_e4_exam.py` | biz4_e1c09_e4_exam.log | data/backtest_artifacts/runs/E4-E1C09-P3-E1C-09/{summary.json,verdict.md}+哨兵 biz4.done | 双自检 IC 偏差>5e-4=作废；登记对照(sharpe±0.05/DSR±0.02)超限=作废 | 分钟级 | **done** | verdict=**存疑**(fail-closed)：IS 1.469 过/WFA 2/3 折(折2 mining 段 -1.95 灾难)/OOS 2.027 但 DSR 0.732 落 review 带+过拟合检出(CV1.83+灾难折)；对照三值全容差内=考试有效；can_deploy=false 放行权 Owner |
| biz2 | F02 做T配对重跑 | 2026-09-18 02:05 | `python .runtime/tmp/exp/p6/cost_trio_exam.py` | stdout | .runtime/tmp/exp/p6/cost_trio_result.json（P6 基线快照 *.p6snapshot.* 留档） | 配对数≥30 才出结论 | 秒级 | **done** | 24<30 维持 insufficient_samples：0/24 毛价差≥30bp 前置、净 mean −45bp；与裁定#304 相互印证无翻案；披露报告=biz2 作业簿，零状态变更 |
| biz1 | F01 L4 批落库 | 2026-09-18 01:54 | `run_validation(batch='L4')` 非 dry | — | c1_backtest.node_verdict run_id=VAL-20260918-015408 + runs/ 档案 finalize | 预期 [('valid',15)]；落库前快照 41 pending+2 valid | 秒级 | **done** | 15 行全 valid（slip 2.56bp/triggers 1467）；B0 15 条全部收尾（终态表=biz1 作业簿） |
| biz3 | E7 涨跌停闸 | 2026-09-18 02:15 | `pytest tests/backtest/test_c4_limit_gate.py` | — | _c4_engine 闸+测试 7 件 | 两真实反例(601162@0925/000016@0410)不被拦=红 | 秒级 | **done** | 7/7 绿+既有守护 58 绿 1 xfail；闸默认开、gate_limits=False 反例通道；详见 biz3 作业簿 |
| biz5 | ETF 分钟族时区劈叉 | 2026-09-18 02:20 | `python scripts/ch/repair_etf_minute_tz_split.py`（dry-run） | — | 修复件+known_data_gaps 条目+工单 biz5 | dry-run 前置核验任一不过=拒绝 | 分钟级 | **staged（--execute 等 Owner 门位）** | 缺陷扩面=T lane 15min 一表→全 ETF 分钟族五表 4.12 亿行（93-95%）；边界零违例/trade_date 零错日/修复零碰撞；三步验证全过，破坏性操作按指令停下登记 |

## 修正案（2026-09-21，st-taskcards-exec-20260921）

- biz5 行（ETF 分钟族时区劈叉）状态停「staged（--execute 等 Owner 门位）」已过时：执行终态=
  60ed3aa49c（09-18 07:22，4.12 亿行转正+五表 *_tz_bak_20260918 备份在库），本班重跑
  git merge-base --is-ancestor 60ed3aa49c HEAD 验证 PASS。历史行不改写，以本修正案为准。
  三处登记面收口明细见 docs/_working/recovered_task_cards/tc06_ruling_cards/tc06_r1_closeout.md
  （known_data_gaps 改册归甲线 WO-3 的 A15 批顺路执行，按今夜避让令不代改）。
