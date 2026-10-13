---
ttl: task_bound
title: 开考执行回执（统筹 15:0x 令③：20 张反向卡开考、判分、入账、负结果入册）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 一、一句话结果

**开考面从 0 变成 20**：本班按已落地的登记袋（`3d136da494` 序列＋`20 卡登记袋`）跑完 20 张反向卡，
分数册 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 由 **46 行 → 66 行**（+20 行，只追加、旧行零改写），
20 张**全部判 fail**，负结果如实入册；`pass` 行数仍 0 ⇒ 没有可入池的新格，本班不造池条目。

# 二、跑批顺序（三件在册前置都在场，不是本班口头保证）

| 令的三件 | 本班实际做到的面 |
|---|---|
| 判据预登记 | 卡面状态登记**先落地**（`20 卡登记袋` done 于 15:5x，`git show dev:` 实测 status=preregistered），本班才跑数——顺序不可逆，登记袋与跑批袋是两个袋 |
| 看数后禁改 | 跑批前后对 11 个判据键（`JUDGMENT_KEYS`）做 yaml 规范化 sha256 比对：**20/20 全等**；跑批唯一写入的是 `status` 与 `lineage`（逐键 diff 实测，非 status/lineage 的顶层值变动＝0 处） |
| 每试次入账 | N 账本 `docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml` 新增 20 条 `examcard:<卡号>:2026-10-13`（kind=exam_card，n_trials=1，note=verdict=fail）；对 dev 面＝**+120 行 / −0 行**，`dev 记录集 ⊆ 新记录集` 断言通过 |

跑批命令（先干跑零 CH 验接线，再实跑）：

```bash
PYTHONNOUSERSITE=1 PYTHONPATH=. python scripts/backtest/fexam/card_binding.py --mode run \
  --approve-list .runtime/tmp/st-examunlock-20261013/approve_list_20.txt \
  --binding-book docs/_working/examunlock_campaign/03_binding_book_event20.yaml \
  --scores docs/03_modules/_domain_backtest/exam_scores_v1.yaml \
  --out .runtime/tmp/st-examunlock-20261013/exam_dryrun_1555.yaml --tag 1555 --dry-run
# 干跑：20 张全部 class=BOOK / recipe=binding_book:event_flag_rolling_pctile，零 CH、零写册
# 实跑同命令去 --dry-run、tag=1556、--out 改 exam_run_1556.yaml
```

# 三、判分内容（为什么是 fail，不是"跑挂了"）

每张卡分数行含 `metrics`（t_stat / gap_bp / n_event / mean_event vs mean_none / oos 子块）与 `fails` 清单，
20 张的失败原因都是**同一族的统计不显著**，样例（逐字取自分数册新行）：

- `17_ind_volume009_high_event`：`t_stat 0.111 > -2.0（负向命题要求更显著）`；
- `19_ind_mom030_high_event`：`is_gap_bp 3.86bp > 0.0（负向命题要求更负）`；
- `36_ind_mom031_high_event`：`n_event 275`、`oos.n_event 120`，gap 为正 ⇒ 命题方向反了。

⇒ 这批卡是"高波动/高动量次日走弱"类**负向命题**，实测方向不成立或显著性不够。
这是**真负结果**（可复算、有 run_id 钉档、进 DSR/PBO 分母），不是失败降级；
本班未调任何阈值、未换窗口、未重跑求 pass（判据面 sha 前后全等即证）。

# 四、判官会重写卡面本身——本班按在在册形态处理，不装作没发生

`calibration_exam.run_card` 出分后把卡面 `status` 改 `examined`、写 `lineage.run_id` 与 `lineage.score_row`，
并用 yaml 全量重 dump 卡面（在册 `judge-run-card-rewrites-card-face`）。
后果如实登记：20 个卡面对 dev 的**字节**差远大于两行（本袋 30 文件 +236/−668，含在途复合族件），
但**语义**差只有 status 与 lineage（逐键 diff 已验）。本班不为此手写卡面去"美化 diff"——
那是绕过判官的第二真源。

# 四之补、卡面实际落地形态＝三行外科式改写（预改方案未采纳，理由与实测都在本节）

上面 §四 写的是"判官重 dump 整张卡面"的**原始产物**——本班一度打算连它一起落地（那会是 20 文件 +1,532/−672 量级）。
入队预检 `[POOL-REGRESSION-DIRECTION]` 拦下，理由＝dev 上这些卡面有他班随后落的行，整档重排在字节面上表现为删除。
本班**先算账再决定**（在册 `pool-regression-l3-rebase-then-ack` 的正解）：

- 对每张卡取 **dev 现字节**为基，只改三行：`status: preregistered → examined`、`lineage.run_id`、`lineage.score_row`；
- 改写后整张卡做**字典级全等断言**：除这三处外与 dev 面**逐键逐值相等**（20/20 过，一处不等即整件拒写）；
- 实测足迹＝每卡 **3 加 / 3 删**（20 卡合计 +60/−60），而非整档重排；
- `score_row` 的行号不是本班跑批时算的那个数：本班**等分数册落地后**按 dev 现册用 `run_id` 回查真实下标再写
  （实测 dev 分数册 66 行、本班 20 行落在 rows[46]–rows[65]，与本地序号一致，但**写法上必须先取 dev 现册**才成立）；
- 一条坑记下来：`exam_scores_v1.yaml#rows[46]` 这个值**不能裸写**——`#` 与 `[` 在 PyYAML 的 dump/load 两面不对称
  （dump 出裸标量、load 时 `#` 被当注释、报 `expected '<document start>'`）。本班第一版就栽在这里，
  现统一加单引号标量（`'exam_scores_v1.yaml#rows[46]'`），改完 20/20 parse 通过。

⇒ §四 描述的是判官的**设计行为**（它确实会整档 dump），本节描述**本班落地的行为**（把足迹压到三行）。
两段都留着，是为了让接班知道"判官会重写"与"落地不该照抄它的大 diff"是两件事。

# 四之续、车道落后面（本班不碰，只登记）

本班车道基底是 13 小时前的 dev，`exam_cards` 目录下另有 **11 张卡面 dev 新于车道**（`40-47_agg_*_fwd*` 等聚合族）。
它们**不在本班任何袋里**（本袋文件清单逐条点名，不做目录级 add）——登记在此是为了让接班明白：
"diff 里有它们"是车道旧，不是本班改的，更不是要合的车道差。

# 五、N 账本这条差点被本班自己写坏（护栏救了一次，记下来）

本班一度想用 `yaml.safe_dump` 把整本 N 账本重排后写入（以为要"手工并入 20 条"），
被 `safe_write_text` 的 **RegistryMassEditRefused** 拒了：删除行 12 ＞ 阈值 `max(1, ceil(0.5%×327))=2`。
复查后发现**根本不需要动它**：车道这本就是执行器单口写出来的，对 dev 天然是 +120/−0 纯追加，
`dev 有 / 车道无` 的记录数＝**0**。
⇒ 教训：热册要先验"是不是单口已经写对了"，再谈手工合并；重 dump 只会把别人的行重排成"被删除"。
另记一条归属事实：20 条试次的 `recorded_by` 落的是执行器常量 `st-mineloop-20261010`（不是本班 sid），
本班不改他人代码面的署名常量，只把这个事实登记在这里供核。

# 六、CH 与让路窗读数（query_log 反查，非背数）

本次跑批＝**20 条完成态 SELECT**（`type=2`，过滤掉含 `query_log` 的自家探针语句），
首条 15:55:37／末条 15:55:42（本地），内存合计 177,556,788 B（≈170 MB，单查询远低于在册 7.14 GiB 共享上限）；
让路窗（01:00-04:00）内本班查询＝**0**（同一把尺 `countIf(event_time < 17:00Z)`＝0）。
底座序列走本地 CSV（20 枚 ti_ew），CH 只取目标面收益——这正是本班 04:0x 物化省下的那一整块装载。

# 七、还没做完的（不藏）

1. **13 张复合族**：共键/对齐规则已登记（`composite_join_rules` 块，+492/−0 纯插入，classify 前后同为
   `U:multi_table_needs_composite_recipe`），但执行器无复合入口（`classify_card` 多表分支只返回 U）
   ⇒ 这 13 张**没算进开考面**，等矿考二班 CW-MINELOOP-001（本班 07 号协调单）。
2. **1 张缺真源**（`L2-09/calibration/04_业绩预增催化剂腿`）：按统筹 03:1x 原裁**未登记**，等数据域补 DDL 真源。
3. **骨架 4 张"接线即可考"**（L1-S0/03、L1-S0/04、L1-S2/07、L1-S3/02）：缺的是 `data_binding` 的表/列/派生式声明，
   属命题作者面，本班不代填；已备待声明单内容（缺哪三件＋卡面原文引用位），随下袋出给挖矿二班。
4. 复核命令（任何接班可原样跑，零 CH 除注明）：
   - `PYTHONNOUSERSITE=1 python -c "import yaml;d=yaml.safe_load(open('docs/03_modules/_domain_backtest/exam_scores_v1.yaml',encoding='utf-8'));print(len(d['rows']),sum(1 for r in d['rows'] if r['verdict']=='pass'))"`
     期望 `66 0`；
   - `git log dev --oneline -3 -- docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1`（看登记与 examined 两笔落地笔）；
   - 试次面：`python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml',encoding='utf-8'));r=[x for x in d['batch_records'] if str(x['batch_id']).startswith('examcard:')];print(len(r))"` 期望 ≥20。
