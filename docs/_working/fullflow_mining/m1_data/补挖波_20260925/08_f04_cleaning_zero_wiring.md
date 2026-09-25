---
ttl: task_bound
lane: M1 数据链（补挖波，接续 st-commitspeed-tbl-20260924）
segment: F04 清洗校验与坏数修复——清洗三引擎零接线取证（总册 P0 断链点）
mined_at: 2026-09-25
session: st-ailayer-fullflow-d
---

# 08_f04_cleaning_zero_wiring — 清洗三引擎零接线取证册（F04 深挖）

> **与既有册关系**：02_cleaning.md C1 已记"三引擎建成未接线"（2026-09-24 grep 粗证）；本册补挖其取证面——逐件出生史/调用面/DSL 能力/承载缺口/头注虚标，并**矿脉增补第四件**。R-M1-06（排期申报）在案不重复登记。

## 一、环节定义与边界

一句话：清洗规则引擎/清洗异常引擎/数据异常告警器（+期望治理套件）四件已建兵器**零生产接线**的司法级取证；现行写前质量面=四门禁（ohlc/change/swing/adj）单点。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入（应喂） | ch_writer 写前写路径（:1006-1021 现行挂的是 data/quality_gate→gov_enforcement 四门禁）+哨兵班（quality_sentinel/supply_sentinel）——四件引擎**无人喂** |
| 下游消费（应产出） | run_quality_gate 输出 (rows, stats) 对齐 apply_quality_gate 形态（拦截报告 intercepted/by_rule/pending_approvals）；alerter 输出分级告警（alert_sink+merge_window 去重）——**零消费方** |
| 自动化触发 | **零**：src/scripts 全树无任何班次/写路径/CLI import 四件（grep 全仓实证，仅 __init__.py re-export+tests+注释提及） |
| 真源与注册表 | 蓝图锚：MOD-L00-004（data_source_integrator_blueprint § cleaning_rule_engine）/MOD-DATENG-001（data_anomaly_alerter blueprint）；ALGO_FLOW 外锚 yaml 三件在档（docs/03_modules/_domain_data*/algo_flow/）；出生=#ARCH-220 DIGEST P0 W1a/W1b（2026-08-25）+#ARCH-253 P1 R6W24（2026-08-26）三候选晋升批 |
| 门禁与质量尺 | 现行门禁=四门禁（FailureReason ohlc/change/swing/adj，失败不阻断 :923-925 WARN :976）；cleaning_policy.yaml=AI L3 判净考尺（washer 抽验协议 v0，治理层尺子 OBJ_R 通道）——**考尺空转**：AI 判净上游无流量（02 册 §五.3 同案） |
| 当前运行状态 | **红（接线缺位）但有替代覆盖**：检测面由 quality_sentinel（四检测器 9 表）+supply_sentinel（58 腿）实际承担；四件引擎=建成封存态。最后触碰=a9b3e039db（2026-09-18 silent-defects 收口批） |

## 三、取证明细（逐件台账，2026-09-25 实核）

| 件 | 路径（行数） | 出生 | 能力 | 调用面实证 | 测试 |
|---|---|---|---|---|---|
| cleaning_rule_engine | src/zephyr/data/cleaning_rule_engine.py（417 行） | d205a6f450e 2026-08-25（CAND-DAT-007，#ARCH-220） | 规则 DSL op∈{gt,lt,between,rolling_quantile}×action∈{flag,block}+滚动分位阈值护栏内自进化（adopted/pending_approval/approve 三态）+run_quality_gate 拦截报告 | 全仓仅：自身文件+data/__init__.py:33 re-export+tests/**；**run_quality_gate 零调用**；**头注虚标**：`[CONSUMERS] zephyr.data.ch_writer`+`[MATURITY] production`——ch_writer 实际 import 的是 quality_gate 四门禁（:1006），头注与事实相反 | 16 例（test_cleaning_rule_engine.py） |
| cleaning_anomaly_engine | src/zephyr/data_eng/cleaning_anomaly_engine.py（404 行） | 2435e55803 2026-08-25（CAND-DATENG-001，#ARCH-220） | 帧内异常：前值填充≤3 根/剔除必人工审核/静默窗 Fail-Closed | 仅自身+data_eng/__init__.py:7 re-export+tests+两处**注释提及**（incremental_update_engine.py:25/alerter 头注查重分工） | 13 例 |
| data_anomaly_alerter | src/zephyr/data_eng/data_anomaly_alerter.py（458 行） | d160eb68f9 2026-08-26（MOD-DATENG-001，#ARCH-253） | 六检测器（跳变/量价背离/缺口/覆盖率等，DataAnomalyAlerterError 契约）+alert_sink 分级+merge_window 去重 | 仅自身+re-export+tests（含 test_silent_latch_before_delivery.py 直测 evaluate） | 23 例 |
| **expectation_governance（矿脉增补）** | src/zephyr/data_eng/expectation_governance.py（295 行） | 同批 2435e55803（CAND-DATENG-002） | 期望套件 YAML（schema/非空/值域/分布/时效）+suite_from_ctr001 契约联动+load_suite | 仅自身+re-export+tests+一处注释（next_day_probability_gate.py:22 域名列举，非 import）；**套件 YAML 无一在盘**（与规则 DSL 同病） | 13 例 |

**承载缺口双实锤**：①规则 DSL"可 YAML 承载"（引擎 docstring 原文）——config/ 实列仅 alert_rules/cleaning_policy(AI 考尺)/context_rules/iteration_guide_rules 四件，**无 cleaning_rules*.yaml**；②期望套件 YAML 零在盘。合计四件 **1574 行兵器+65 例测试**全绿封存。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| C1' | 四件零接线（原 C1 扩容为四件+双承载缺口） | 晋升批只交付模块+测试，宿主班次与 YAML 承载未随批（"建成"≠"接线"） | R-M1-06 排期申报升级：挂 supply_sentinel 宿主同款托管+config/cleaning_rules.yaml 承载（规则 DSL 先 flag 后 block 两档灰度）；expectation_governance 并批（suite YAML 三件起样） | 1-2 天+0.5 天 | 是（等排期） |
| C1'' | **头注虚标**：cleaning_rule_engine 头 `[CONSUMERS] zephyr.data.ch_writer`+`[MATURITY] production` 与 grep 事实相反 | 晋升时按设计意图填写，接线未跟进而头注未回改 | 头注修正：CONSUMERS 置空+MATURITY 改 built-not-wired（或 dormant），防后人按头注误判已接线 | 0.1 天 | 是 |
| C6' | 考尺空转连锁：cleaning_policy.yaml（AI L3 抽验）依赖三引擎接线后才有上游流量 | 接线未开工 | 与 R-M1-06 同批立项，考尺不单独先动 | — | 并批 |
| C7 | 增量防复发：同类"晋升即封存"模式在案两次（08-25 W1a/W1b 两批四件全未接线） | 晋升判据无"接线承诺"字段 | 候选晋升模板加"宿主班次+消费方"必填栏（治理侧提请，归 M3/K 段） | 0.2 天 | 提请 |

## 五、提速与合并机会

1. run_quality_gate 输出形态刻意对齐 apply_quality_gate（引擎 docstring 自述"接入 quality_gate 并输出拦截报告"）——接线是**插头对插座**设计，改造成本被出生时已压到最低，只剩宿主与承载。
2. 四件共享 data/__init__ 与 data_eng/__init__ 双门面，托管宿主一个即可全量挂载（哨兵班已单例，加检测器零新进程）。

## 六、自审闸三态

**取证挖干**（零接线判定双源实证：grep 调用面+git 出生史+config 承载盘查）；**待裁/排期**=R-M1-06 承接（本车道可施工，报总筹排期即开，非新裁定）；头注修正 C1''与晋升模板 C7 可直开/提请。

## 七、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
grep -rn "cleaning_rule_engine\|CleaningRuleEngine\|cleaning_anomaly_engine\|data_anomaly_alerter\|expectation_governance" src scripts --include="*.py" | grep -v __pycache__ | grep -v "__init__\|#"   # 生产调用面=零
grep -rn "run_quality_gate" src scripts --include="*.py" | grep -v __pycache__            # 仅引擎自身
sed -n '10,15p' src/zephyr/data/cleaning_rule_engine.py                                    # 头注虚标原文
sed -n '1006,1021p' src/zephyr/data/ch_writer.py                                           # 现行四门禁接线点
ls config/ | grep -i "clean\|rule"                                                          # 无 cleaning_rules 承载
git log --format="%h %ad %s" --date=short -1 d205a6f450e
```
