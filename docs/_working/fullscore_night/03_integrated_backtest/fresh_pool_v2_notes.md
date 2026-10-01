---
ttl: task_bound
campaign: fullscore_night/03_integrated_backtest
created: '2026-10-01'
session: st-fullscore-20260930
pool: fresh_pool_v2.yaml
---

# fresh_pool_v2 再生成对账说明（池被盗后复原）

> 复原优先序：CH 台账（机器真源）> recovery2 blob（证词）> 交接记忆（证词）。
> 池文件本体=`fresh_pool_v2.yaml`（同目录），格式合同=`scripts/backtest/ibt/ibt_runner.py`
> `_apply_pool_override`（v1.1：`members: {sid: 翻译件文件名}` + `note`）。

## §1 名单对账（三源逐一核对）

**机械真源**：`strategy_screen_query.py bothwin` 只读实测（2026-10-01）＝
`tested=85 / passed=14`，及格门=IS>0 且每段样本>0 且年衰减率<0.5（键=strategy_id+source_file）。

| # | sid | 翻译件 | 类别 | bothwin | 交接记忆 | 盘上翻译件 |
|---|-----|--------|------|---------|----------|-----------|
| 1 | FACT-4f749668 | c4_fact_4f749668.py | 留任 | ✓ | ✓ | ✓ |
| 2 | FACT-4228020a | c4_fact_4228020a.py | 留任 | ✓ | ✓ | ✓ |
| 3 | FACT-e293e217 | c4_fact_e293e217.py | 留任 | ✓ | ✓ | ✓ |
| 4 | FACT-e831084c | c4_fact_e831084c.py | 留任 | ✓ | ✓ | ✓ |
| 5 | FACT-4b200528 | c4_fact_4b200528.py | 留任 | ✓ | ✓ | ✓ |
| 6 | CAND-8d000bf3ccc3 | c4_8d000bf3ccc3_pb_poe.py | 留任(8d00) | ✓ | ✓ | ✓ |
| 7 | CAND-e3da6fa71af1 | c4_e3da6fa71af1_panic_rebound.py | 留任(e3da) | ✓ | ✓ | ✓ |
| 8 | CAND-29eb91dbaf60 | c4_29eb91dbaf60_crash_dodge.py | 留任(29eb) | ✓ | ✓ | ✓ |
| 9 | CAND-dc5b80aa3614 | c4_dc5b80aa3614_tsmall100.py | 新进 | ✓ | ✓ | ✓ |
| 10 | FACT-4db4c41e | c4_fact_4db4c41e.py | 新进 | ✓ | ✓ | ✓ |
| 11 | CAND-5301c5d9d7c8 | c4_5301c5d9d7c8_small_cap_hl.py | 新进 | ✓ | ✓ | ✓ |
| 12 | CAND-8664521af1a0 | c4_8664521af1a0_snake_cap.py | 新进 | ✓ | ✓ | ✓ |
| 13 | CAND-7f7e5f935dfc | c4_7f7e5f935dfc_dmi_timing.py | 新进 | ✓ | ✓ | ✓ |
| 14 | CAND-9ce75aa27ce5 | c4_9ce75aa27ce5_bluechip_ma.py | 新进 | ✓ | ✓ | ✓ |

**对账结论：14/14 三源相符，零出入，无硬凑。** FACT 族员数=6（#1-5 留任 + #10 新进），
与 prereg 附录 A"简报口径=6"一致（不触发"不符即停"）。
留任 8 ⊂ v1 冻结池 15 员；新进 6 ∩ v1 冻结池 = ∅（机械核对）。

## §2 剔除与失败案底（与 v1 池 15 员差集核对）

- 剔除 7（有案，均不在 bothwin 及格集）：CAND-c4ec6332c07f、CAND-4440d07f973f、
  CAND-eaddc3f9db4e、CAND-d06cab686cef、CAND-a4543012b464、CAND-bd42540f86e4、
  CAND-6a6ec8869ddb（OOS 负）——与交接记忆"剔除 7 有案（5 件 IS 负/6a6e OOS 负/4440 新窗负）"相符。
- 新窗翻转入局失败 2（批 C4-OOS3-20261001，窗=2024-01-01/2026-09-26）：
  CAND-4440d07f973f（IS=-0.233，与裁定 blob"CAND-4440d07f973f 判死"一致）、
  CAND-c72318f2da1c（IS=-0.064）——与交接记忆"2 件新窗翻转入局失败"相符。

## §3 源数据形态披露（池源数据 1 与简报不符，如实记档）

- 简报称 `.runtime/tmp/fullscore_recovery2/fresh_pool_member.yaml`="268KB 考试报告 blob，
  含 14 员名单与成绩"。**实测不符**：该文件现盘 410KB、内容=裁定中央登记表
  （REG-RULING-001，无 YAML 文档分隔符、单一 module_id），仅含池决策的**裁定痕迹**
  （#322 死刑名单/#326 污染重考/4440 判死等 5 处 CAND/FACT 提及），**不含 14 员名单与成绩表**。
  同目录 `ibt_redproof.py` 亦与名称不符（实为消费面普查红证测试）。
  → 故名单复原改走池源数据 2（CH bothwin 台账），上表即其产物。
- NIGHT_STATE "tested=85/passed=14 台账"与 CH 实测完全吻合（tested=85/passed=14，
  passed_ids 逐字对上），台账真源地位成立。

## §4 FACT-4db4c41e 出处张力（披露，不替判据做主）

- 裁定#322（2026-09-17）：旧窗"零换手 ann_ret 60%=伪装买入持有"判死，剔出**旧核心池**。
- 裁定#326（2026-09-17）：翻译件污染处置，命 85 件全量重考（重考前及格集底座冻结）。
- 本夜 bothwin 机械台账（PIT 修复后口径）中 FACT-4db4c41e 双窗及格在册；
  交接记忆名单亦含（新进 6 之一）。本池按机械台账纳入；#322 与台账的出入如实披露，
  是否追溯处死属 Owner 裁定域，本代理不改判据、不增删员。

## §5 复原可逆性

池文件为新建（原文件无 git 痕迹，被盗未遂复原件）；sha256 于 prereg_v2.md 附录 A 锁箱。
回滚=删除本两件+revert prereg 附录 A 填写，零其他副作用。
