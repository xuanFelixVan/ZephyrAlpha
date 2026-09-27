---
ttl: task_bound
title: "F04 清洗校验与坏数修复——三引擎零接线+假绿/FAILED 质量面复飞案卷"
session: zc-l01-20260927
---

# F04 清洗校验与坏数修复（复飞案卷）

> 前序：M1 册 02_cleaning.md+补挖波 08_f04_cleaning_zero_wiring.md+90_backfill_wave.md（取证挖干）；本卷=四态独立复核+今日 census 增量。

## 一、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游 | F01 FetchResult 流+存量脏数（1970 残留/时区偏移/幽灵日/零值行）+known_data_gaps 63 条 |
| 下游 | ch_writer 写前门禁（ch_writer.py:1006-1021 四门禁 apply_quality_gate，flagged WARN 不阻断）；integrity_check 班 subprocess 调 check_tick_duplication（integrity_checker.py:54-66） |
| 自动触发 | 三班哨兵挂 06:50 data_supply_sentinel 槽（supply_sentinel 58 腿托管 quality_sentinel 9 表）；integrity_check 17:xx；weekend/daily_backfill；catchup_guard 05:30；consensus_crosscheck；eod_reconciliation 15:40；停摆总闸=data/runtime/quality_sentinel.disabled |
| 真源注册表 | quality_sentinel_tables.yaml（9 表实数）/data_supply_sentinel.yaml（58 腿实数）/cleaning_policy.yaml（AI L3 考尺）/RULE-DATA-OPS=trae_063 |
| 门禁质量尺 | 写前四门禁（ohlc/change/swing/adj FailureReason）；supply_sentinel 六维判据（:31-40）；AI 判净考尺**空转**（上游无流量） |
| 运行状态 | **黄绿双色**：现行哨兵面绿（发现能力在案：rate_decision_calendar 435 行 epoch/daily_valuation 77,668 幽灵行均被捕获）；四件引擎面红（1574 行兵器+65 例测试封存零接线；cleaning_rule_engine.py 头注虚标 CONSUMERS/MATURITY 与 grep 事实相反） |

## 二、子模块三级枚举

1. 写前门禁：data/quality_gate.py→gov_enforcement 四门禁（唯一生产接线点）
2. 三引擎+第四件（全零接线，08 册 file:line 取证）：cleaning_rule_engine.py（417 行 DSL gt/lt/between/rolling_quantile）/data_eng/cleaning_anomaly_engine.py（404 行）/data_eng/data_anomaly_alerter.py（458 行六检测器）/data_eng/expectation_governance.py（295 行期望套件）
3. 哨兵班：quality_sentinel.py（903 行四检测器）/supply_sentinel.py（555 行六维）
4. 修复链：check_tick_duplication/backfill_checker/auto_backfiller/catchup_guard/integrity_checker/consensus_crosscheck/recon_runner
5. 修复兵器 7 件（manual 事故驱动）+隔离区 data/local_fallback_quarantine（手工，无代码桥）
6. 承载缺口：config/ 无 cleaning_rules*.yaml、期望套件 YAML 零在盘（08 册双实锤）

## 三、接线四态独立复核

- 总册：partial（清洗三引擎零接线）/P0/D4。独立复核：**partial 成立**（08 册 grep 穷尽反证+本日 config/ 实列无规则 YAML 复证）。
- 今日增量（wiring_gap_inventory §2.2 接驳）：F04 质量面与 census 三张假绿榜直接相关——①FALSE_GREEN 5 腿（值级假绿另含 news_sentiment_score 冻结 2025-09-09+restricted_shares 2035 前瞻污染）；②FAILED 8 腿中 str/date 共因 2 腿=清洗/派生 build 代码缺陷（consensus_daily_build/financial_derived_build→一处 _norm_date 覆三实例）；③观测补强面：reconciliation_differences 心跳元表（C6）+告警尺缺失（两 build 崩停 8-12 天无人知）。
- 骨架勘误⑥：总册 F04 写"清洗三引擎零接线"，实数=**四件**（expectation_governance 同批封存，08 册矿脉增补），册行量词建议改"四件"。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| C1 | 四件引擎零接线+双承载缺口 | 挂起+解锁=Owner 门（总册晨报名单在案"勿自动施工"）；方案 A 读侧哨兵班托管先行（建议） | P0 |
| C2 | 头注虚标（cleaning_rule_engine CONSUMERS=ch_writer/MATURITY=production） | 施工：改 built-not-wired | P1 |
| C3 | daily_valuation 幽灵行/epoch 残留清理 | Owner 门（R-M1-02/03 在案，dry_run 先行） | P1 |
| C4 | 隔离区无自动分拣/TTL | 施工：死信链↔隔离目录 manifest 桥 | P1 |
| C5 | str/date 共因+假绿交叉尺（C1/C4 收口卷编号） | 施工：与 F01 G1/G2 同袋 | P0 |
| C6 | AI 判净考尺空转 | 挂起+解锁=C1 接线后同批 | P2 |

## 五、自审闸三态

取证挖干（08 册+90 册）；C1/C3/C6=挂起+Owner 门（解锁条件在案）；C2/C4/C5 可施工。沿用总册判定处已注明。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -c "^  - table:" config/quality_sentinel_tables.yaml; grep -c "^  - table:" src/zephyr/data/config/data_supply_sentinel.yaml
sed -n '5p;7p' src/zephyr/data/cleaning_rule_engine.py
grep -rniE "CleaningRuleEngine|run_quality_gate" src scripts --include="*.py" | grep -v __pycache__ | grep -viE "tests?/|__init__" | wc -l   # ≈自身
ls config/ | grep -i "clean"   # 无 cleaning_rules.yaml
```
