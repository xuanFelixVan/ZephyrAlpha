---
ttl: task_bound
title: "策略孤岛挂载反查作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine_20261001
---

# L13 策略孤岛挂载反查作业簿（§9A Q2 策略问 · 129 卡分族三态）

> **车道铁律**：全部产出停"挂载登记面"（TDM strategy_mounts 登记+证据链）；实弹转正/上线=Owner 北极星门位（宪法 §5/§6），本车道零触碰 flag/部署/实弹开关。
> **方法论**：data_source_onboarding_sop §9A Q2（反查 strategy_registry 全卡 + TDM 十职能逐族扫）+ mining_sop §2 六向寻路 / §6 挖后自审闸 / §9C 三态出口。
> **事实源**：REG-STR-001（161 卡）/ census 台账（129 岛）/ TDM（182 节点）/ CH c1_backtest 三表（只读）/ REG-EXP-001（67 试验卡）/ data/strategy_intake。

## 1. 总读数

| 项 | 读数 | 源 |
|---|---|---|
| REG-STR-001 总卡 | 161（status: candidate 139/active 19/deprecated 3；lifecycle: candidate 151/backtest 8/sim 2；algorithm_status: quantized 19/pending_backtest 142） | strategy_registry.yaml |
| census 孤岛 | 129=VREV 24/DABAN 19(004~022)/MULTIFACTOR 56/MOMTREND 28/SECTOR 1/E-TIMING 1；why_zero=no_declared_demand+doc_mention_only | consumption_census_ledger.json(2026-09-29) |
| 接线补集 | 32=129 严格补集；其中 29 张 STR 已挂 TDM（islands∩mounted=∅ 交叉验证），余 3 张经其他消费面治愈（EVENT-001 代码消费/MF-090 deprecated/MF-097 intake 簇首） | TDM×census 对账 |
| TDM 挂载面 | 182 节点/4 流（entry132/position18/exit19/portfolio13）；19 节点已有 mounts（37 refs=29 STR+8 kebab 代码策略）；孤岛对应职能挂点全空=工单本体 | trading_decision_map.yaml |
| 册内证据（129 岛） | evidence 非空 14 张 / 空卡 115 张 | python 全读 |
| CH 考试实证 | strategy_screen 1,389 行/574 CAND（screened_in 381/deferred_c4 321/rejected 216/translated_c4 206/oos_tested 160/sim_deviation 101/obsolete 4）；sim_trade_log 85 行（STR-E-TIMING-001 17 笔 sim_daily 在考）；node_verdict 58 行（TDM-E-L1/L4-* valid/pending） | CH c1_backtest（DatabaseService reader 只读） |
| 卡↔考试键桥 | strategy_screen 主键=CAND-* 非 STR（574 中仅 1 个 STR 形态）；桥两条=①卡 evidence 台账键（5 张命中）②code 文件名十六段（MF-098/099 命中）——合计 7 张有 CH 考试行 | 本件 §3 |
| card_state 13 态 | 宿主=REG-EXP-001（67 试验卡：frozen 51/red 2/suspended 1/sealed 1/candidate 1/未标 11）；策略卡 0/161 携带 card_state、试验卡 0 张 target STR-*——契约对策略卡未启用=盲点 B4 | card_state_vocabulary.yaml+experiment_registry.yaml |
| strategy_intake | 29 个 grid 目录（27 时间戳+2 专项）+normalized/ 6 年度精选；constructed_manifest.csv 仅 1 行——grid↔卡映射未建=盲点 B5 | data/strategy_intake/ |

## 2. 六族 × 三态表

三态判据：**A**=CH 有考试行（CAND 键桥）→出挂载工单｜**A'**=有考试但成绩无效（弱分）→重考队｜**B**=有回测/施工证据无 CH 考试→E4 考试队列｜**C**=无证据空卡→挂账 defer（90 天门计龄）或退役复核。

| 族（→TDM 职能） | 岛数 | A 出工单 | A' 重考 | B 进 E4 队 | C defer | 退役复核候选 |
|---|---|---|---|---|---|---|
| F1 DABAN-004~022（→执行成交/个股） | 19 | 0 | 0 | 1（022 代码落地明示未回测） | 18 | 0 |
| F2 MOMTREND×28（→大盘判断/个股） | 28 | 2（002/019） | 1（020 考分 0.0） | 0 | 25 | 1（022 无 tags） |
| F3 MULTIFACTOR×56（→组合反馈/持仓） | 56 | 2（098/099） | 0 | 2（069/096 施工锚定未回测） | 52 | 5（053/068/085/087/093 无 tags） |
| F4 VREV-001~024（→个股/离场） | 24 | 1（001） | 0 | 4（017/018/019/024 代码锚定未考） | 19 | 1（005 无 tags） |
| F5 SECTOR-001（→板块赛道） | 1 | 0 | 0 | 0 | 1 | 0 |
| F6 E-TIMING-001（→大盘判断） | 1 | 1（001 三窗全绿+sim 在跑） | 0 | 0 | 0 | 0 |
| **合计** | **129** | **6** | **1** | **7** | **115** | **8** |

- C 族 115 张画像：100% doc_ref=29_factor_strategy_extraction.md（潘潘课纲提炼卡）、0 code_path、107 有 tags、status 全 candidate——有设计意图非空壳，**全部判 defer 不判退役**；判死走 §10 需机制证伪证据，当前仅"未考"不足判死。
- B 族证据含金量注记：VREV-017/018/019/024+MF-069 的代码本体（kebab：intraday-surge-fall/vwap-reversion/orderbook-imbalance/multifactor 伞条）已是 [MATURITY] production 且挂 TDM-E-L3/TDM-P-P2——缺的是**卡级**考试成绩，非代码能力。

## 3. 挂载工单清单（登记面——A 族 6 张逐条）

条目 schema=TDM 现行惯例 `{strategy_ref, confidence, evidence}`；置信度=D5 语义（verified=回测归因支撑必带 evidence/proposed=待验证/untested）。落库=safe_write_text+既有 gate 链追加式登记，不动 19 节点既有 37 refs。

### 3.1 STR-E-TIMING-001「恐慌反弹分布预测」→ TDM-E-L1 大盘总闸（verified）

```yaml
- strategy_ref: STR-E-TIMING-001
  confidence: verified
  evidence: "三窗全绿 IS1.15/OOS0.83/S3 0.98 run=SCR-C4-OOS2-20260913；CH strategy_screen 7行 oos_tested(CAND-e3da6fa71af1)；sim_trade_log 17笔 sim_daily 2026-09-15~10-01 在考"
```

### 3.2 STR-VREV-001「情绪回暖干超跌」→ TDM-E-L3 个股选择 + TDM-X-FLOW 离场信号（proposed）

```yaml
- strategy_ref: STR-VREV-001
  confidence: proposed   # 家族替身证据：考试主体=同族代表（同台账键），卡级独立回测未跑
  evidence: "家族替身 Sharpe=1.15 DSR=0.5309 run=SCR-C4-20260913-002056；CH strategy_screen 7行 oos_tested(CAND-e3da6fa71af1 同键)"
```

### 3.3 STR-MOMTREND-002「双均线交叉趋势」→ TDM-E-L1（proposed）

```yaml
- strategy_ref: STR-MOMTREND-002
  confidence: proposed   # 家族替身（pilot_002 MA5/10金叉）
  evidence: "家族替身 IS Sharpe=1.08 run=SCR-C4-20260913-002056；CH strategy_screen 2行 screened_in(CAND-b1ab42050d68)"
```

### 3.4 STR-MOMTREND-019「突破型第一买点」→ TDM-E-L1（proposed）

```yaml
- strategy_ref: STR-MOMTREND-019
  confidence: proposed   # 家族替身（趋势交易5.0），替身 IS 负分但 CH 复考正分
  evidence: "CH strategy_screen 7行 oos_tested(CAND-a4543012b464) max is_sharpe=0.795；替身 IS -0.308→以 CH 复考为准"
```

### 3.5 STR-MULTIFACTOR-098「small_cap_hl」/ 3.6 STR-MULTIFACTOR-099「snake_cap」→ TDM-F-FLOW 组合信号 + TDM-P-FLOW 持仓信号（proposed）

```yaml
- strategy_ref: STR-MULTIFACTOR-098
  confidence: proposed   # 双窗及格但 BH-FDR 未过，candidate 留观
  evidence: "IS SR=0.518/OOS SR=0.156 run=C4-OOS-2024-2026；CH strategy_screen 5行 oos_tested(CAND-5301c5d9d7c8)"
- strategy_ref: STR-MULTIFACTOR-099
  confidence: proposed   # 双窗及格但 BH-FDR 未过，candidate 留观
  evidence: "IS SR=0.397/OOS SR=0.404 run=C4-OOS-2024-2026；CH strategy_screen 5行 oos_tested(CAND-8664521af1a0)"
```

注：MOMTREND-020「回踩确认第二买点」有 CH 考试（CAND-1970782c2adb，6 行 oos_tested）但 is_sharpe=0.0=无超额——**不出挂载单**，转 §4 重考队。

### 3.7 B/C 族按族汇总（不出挂载单）

| 族 | 工单形态 |
|---|---|
| B 7 张：DABAN-022/MF-069/MF-096/VREV-017/018/019/024 | 进 E4 考试队列（§4 P2）——卡级考试通过后方可出卡级 mounts 单（卡与 kebab 代码挂载并存不互代） |
| C 115 张 | 全族 defer 挂账，defer_reason="§9A Q2 已反查：课纲提炼卡（29_factor §锚点）有设计无实现无考试；TDM 职能挂点在案（§2 映射列）；等 E4 批次排期"——90 天门照计龄；8 张无 tags（MOMTREND-022/MF-053/068/085/087/093/VREV-005/016）另列退役复核候选（仅登记，判死走 §10 另审） |

## 4. E4 考试队列建议（优先级序）

1. **P1 重考**：MOMTREND-020（有考试无有效成绩 0.0）。
2. **P2 卡级首考**：B 族 7 张——VREV-017/018/019/024+MF-069（代码 production 成熟度最高，只缺卡级成绩）；DABAN-022/MF-096（testing，先回测后考）。
3. **P3 留观复检**：MF-098/099（BH-FDR 未过，registry 自承诺"后续批次重检"）。
4. **P4 长尾**：C 族 115 张按 census value_score 降序分批（§9C 考古批纪律：批次号+批次日志+挖干判据，禁"一次全清"）。
5. 队列出口对齐 §9D：考试过→出 mounts 单落 TDM（unwired→wired 治愈）；实弹与否=Owner 门位，不入本队列语义。

## 5. 六向台账（mining_sop §2，逐向留痕）

| 向 | 动作与发现 |
|---|---|
| ①上游 | REG-STR-001 全读 161 卡+census 129 岛交叉（islands∩mounted=∅）；REG-EXP-001 67 卡无一 target STR（B4）；intake 29 grid/6 精选、manifest 1 行（B5） |
| ②下游 | TDM 182 节点逐点扫 strategy_mounts：19 节点 37 refs；孤岛职能挂点全空=工单本体；前端呈现面未触（登记面边界，见⑤） |
| ③算法/机制 | D5 置信度语义、card_state 13 态契约、90 天门（§9D）、家族替身证据语义（C5 聚类对质）——判级全按在册契约执行，无自造语义 |
| ④后端 | CH 三表实证走 DatabaseService.get_clickhouse_conn(reader) 只读；CAND 键双路径桥（evidence 台账键/code 文件名） |
| ⑤前端 | 查无——零前端动作，留痕防漏 |
| ⑥数据字段 | strategy_screen 主键=CAND 非 STR（桥接依据）；grid↔卡 manifest 断链（B5）；孤岛 why_zero=no_declared_demand 与"挂点空置"互证 |

盲点小结：B4=13 态契约未挂策略卡；B5=grid↔卡映射断链；B6=资讯/推演/新市场三职能在 TDM 无名点（§9A Q2 十职能仅七职能有落点）。

## 6. 挖后自审闸三态（mining_sop §6）

| 态 | 裁定 |
|---|---|
| 施工 | 本件=登记面工单交付（§3 六张 mounts 单+§4 队列），交总筹按 safe_write+gate 链落 TDM（safety=L/ai_autonomy=ai_modifiable，登记动作无需 Owner 门） |
| 挂起排期 | 实弹转正/上线逐卡=Owner 北极星门（宪法 §5/§6；mining_sop §6"Owner 只做四类事"之策略转正审批）——mounts 登记≠实弹，verified 亦只=回测归因语义；解锁条件=卡级考试过+BH-FDR 过+Owner 逐卡批 |
| 方案封矿 | 无——129 卡均属终局全貌核心资产（策略库），无一满足封矿单问；C 族 defer 计龄后仍零进展者走退役复核（§10），非本车道封矿 |

## 7. 挖矿日志与边界声明

- 批次：fullflow_mine_20261001/L13（Q2 策略问，census strategy 129 岛批）；读=policy 2+册/图/词表 4+CH 三表+intake；写=仅本件；CH 全程 reader 只读。
- 判定留痕：三态逐卡可复算（桥=CAND 键双路径，registry 字段×CH 行全对账）；查无亦留痕（⑤前端向、B6 三职能挂点、grid manifest 断链）。
- 边界声明：**全部工单停在"登记面"**——不改 flag、不触部署、不开实弹、不执行退役删卡（8 张退役复核候选仅登记）；实弹逐卡等 Owner 转正审批。
- 复算入口：.runtime/tmp/l13_*.json（strats/census_strats/island_ids/island_candkeys/mounted/ev_islands）。
