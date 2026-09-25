---
ttl: task_bound
title: M1 数据链 补挖波 · 清洗三引擎零接线 + 影子表退役/CH三数互斥
session: st-fflead-m1m6-backfill
---

# 90_backfill_wave — M1 补挖波（清洗三引擎接线面 + 影子表退役/三数互斥，2026-09-25 全部本会话复跑实证）

> 接续册：02_cleaning.md（C1）/03_ch_warehouse.md（W1）/补挖波_20260925/08_f04_cleaning_zero_wiring.md。本册增量：①三引擎逐件入口 file:line（本会话 grep -n 实取）＋零调用方穷尽反证（含 schedule/tasks/cmd_ledger 任务真源逐一复跑）＋最小改动面与风险；②CH 三数**本会话实测复测**（c1_market 已 201→202 再漂移，即计数漂移活证）＋影子表 8 张逐表行数＋退役通道现存三件兵器实证与判据草案。

## 一、环节定义与边界
- 任务1（三引擎）：写前/哨兵质量面的**建成未接线兵器**三台（02 册 §三点名 cleaning_rule_engine / cleaning_anomaly_engine / data_anomaly_alerter；08 册增补第四件 expectation_governance，本册一并复核）。上游应喂点=ch_writer 写路径（现挂四门禁，本会话复跑 ch_writer.py:1006 `from zephyr.data.quality_gate import apply_quality_gate`）；下游应产出=拦截报告/分级告警（现零消费）。
- 任务2（影子表+三数）：真源文件 business_data_categories.yaml（品类册）× CH system.tables 实测 × 该 YAML 头注释三数互斥；影子表=WO-004 hfq 复权重算留观表族。退役通道属**表净删=Owner 门位**（waste_table_scanner 头注 INVARIANTS 明文，见 §三）。

## 二、六向台账
| 向 | 实证（本会话 2026-09-25 复跑） |
|---|---|
| 上游输入 | ch_writer.py:1006-1021 现行四门禁（apply_quality_gate，flagged 仅 WARN 不阻断，:1008-1021 逐行复核在案）；三引擎无人喂 |
| 下游消费 | 三引擎输出=run_quality_gate InterceptionReport（cleaning_rule_engine.py:264）/alert_sink 告警（cleaning_anomaly_engine.py:107 default_alert_sink）；全仓生产消费=零（§三 grep 穷尽） |
| 自动化触发 | 零，四任务真源逐一反证：src/zephyr/data/config/schedule.yaml+tasks.yaml `grep -inE "cleaning_rule|cleaning_anomaly|data_anomaly"` → **无命中（rc=1）**；docs/_working/cmd_ledger 同关键词 → 无输出；config/ 全树（含 quality_sentinel_tables.yaml）同关键词 → 无命中（§三计数表无 config 文件）；计划任务面 resource_profile_registry.yaml 亦入扫描面零命中 |
| 真源与注册表 | 三引擎真身见 §三；承载缺口=config/ 实列仅 alert_rules/cleaning_policy/context_rules/iteration_guide_rules/quality_sentinel_tables 五件，**无 cleaning_rules*.yaml / 无期望套件 YAML**（ls 实查）；品类三数真源=docs/03_modules/_cross_layer/database/business_data_categories.yaml:11（头注"114 条"）vs 同文件 category_id 实数 vs CH 实测 |
| 门禁与质量尺 | 写前现行=四门禁（ohlc/change/swing/adj）；退役面=RULE-DATA-OPS 三步验证+archiver 三阶段原子（export→verify→drop，scripts/ch/archiver.py:7-10 头注）+waste_table_scanner"只登记+报警永不自动删，退役须 Owner 批（裁定 #380①/#382 逐表批制）"头注 :8 |
| 当前运行状态 | 三引擎=**红**（1574+ 行兵器+65 例测试封存，且 cleaning_rule_engine.py:5 头注虚标 `[CONSUMERS] zephyr.data.ch_writer`、:7 虚标 `[MATURITY] production`，与 grep 事实相反）；影子表=黄（8 张 ~2,150 万行在库无 TTL）；三数=事故态（宪法 §4.3 文档矛盾；本会话实测 c1_market=**202**，03 册 09-25 记 201，**一天再漂移 +1**，计数生成器化义务活证） |

## 三、子模块清单（逐件入口 file:line，本会话实取）

### 3.1 三引擎+第四件（行号=本会话 grep -n 输出）
| 件 | 入口 file:line | 零调用反证 |
|---|---|---|
| cleaning_rule_engine | src/zephyr/data/cleaning_rule_engine.py:274 `class CleaningRuleEngine`；:312 evaluate；:376 `def run_quality_gate`；:213 parse_rules；:88 RollingQuantileThreshold | 全仓 import 仅 data/__init__.py:33/:74 re-export；run_quality_gate 生产零调用（§七命令 1） |
| cleaning_anomaly_engine | src/zephyr/data_eng/cleaning_anomaly_engine.py:123 `class CleaningAnomalyEngine`；:154 detect；:107 default_alert_sink | 仅 data_eng/__init__.py:7 re-export + incremental_update_engine.py:25 **注释**提及（本会话 sed 复核="data_eng 既有 cleaning_anomaly_engine / expectation_governance"文字） |
| data_anomaly_alerter | src/zephyr/data_eng/data_anomaly_alerter.py:300 `class DataAnomalyAlerter`；模块级检测器 :154 detect_price_jumps / :189 detect_missing_rate | 仅 data_eng/__init__.py:8/:50 re-export |
| （第四件）expectation_governance | src/zephyr/data_eng/expectation_governance.py（08 册 §三：295 行） | 08 册实核=仅 re-export+tests；套件 YAML 零在盘（本会话 config ls 复证） |

**穷尽反证计数表**（本会话命令 1 输出，排除 tests/__pycache__ 后按文件计行）：data_anomaly_alerter.py:29（自身）/ cleaning_rule_engine.py:10（自身）/ cleaning_anomaly_engine.py:4（自身）/ data_eng/__init__.py:4（re-export）/ data/__init__.py:2（re-export）/ incremental_update_engine.py:1（注释）→ **生产调用面=零**，与 08 册判定一致。

### 3.2 CH 三数（本会话 DatabaseService 只读实测）
| 数 | 值 | 出处 |
|---|---|---|
| ① CH 物理表 | 四库合计 253=c0_meta 1 + c1_backtest 16 + **c1_market 202** + c3_fundamental 34 | `system.tables` 计数（§七命令 4），03 册 09-25 记 201→今 202 |
| ② 品类在册 | category_id **338** | `grep -c "category_id" business_data_categories.yaml`=338 |
| ③ YAML 头注 | "合计 114 条 category_id 全唯一（2026-08-15 实测校正）" | business_data_categories.yaml:7-11 |
互斥文件=**business_data_categories.yaml 自身**（头注③ vs 册内②）且与 CH 实测①三方不合。修法=三数改生成器单源产出（宪法 §9.5 静态清单禁手工）。

### 3.3 影子表（本会话逐表 total_rows 实测，均属 c1_market）
kline_daily_hfq_legacy_20260924 **8,431,745**｜kline_daily_hfq_preversion_20260925 **10,079,242**｜kline_daily_hfq_quarantine_20260925 10,475｜kline_weekly_hfq_legacy_20260924 2,127,400｜kline_weekly_hfq_legacy_r1_20260924 1,856,392｜kline_monthly_hfq_legacy_20260924 502,496｜kline_monthly_hfq_legacy_r1_20260924 524,476｜index_valuation_daily_quar_20260920 8,125。合计≈2,154 万行。核心=**WO-004 hfq 复权重算影子表族**（02 册 C5"quarantine 表留观中"；03 册 W1"留观后无 TTL/退役通道"）。

### 3.4 退役通道现存兵器（本会话实核）
| 件 | 现状 |
|---|---|
| scripts/ch/archiver.py | 表/分区级三阶段原子：export Parquet→verify 行数+抽样比对→drop（头注 :7-10；`export --table ... --partition` 纯备份模式 :23）——**分区级 DROP PARTITION（:144），表级退役需逐分区遍历或改造**，先例宿主=tick_data 冷归档 |
| scripts/ch/waste_table_scanner.py | 垃圾/影子表登记册：INVARIANTS"只登记+报警永不自动删(裁定#380①/#382 逐表批制)｜登记册条目只增不删(退役须 Owner 批)"（头注 :8）＝退役门位已在码层固化 |
| scripts/ch/rolling_archive_reconciler.py | 备份成功钩子+五重安全阀+shadow 只读禁 drop（头注 :8）＝归档对账可复用 |
| CH 备份双链 | 宪法 §7：F 主/G 二（INFRA-STORE-003）＝可逆通道第二腿 |

**退役判据草案（五步）**：①全仓 grep 表名零消费反证（WO-004 文档引用除外）；②正身表行数/覆盖≥影子表；③archiver export→verify 全过（Parquet 落 E 盘）+CH 备份双链在册；④waste_table_scanner 登记＋Owner 逐表批（#382 批制，不自裁）；⑤drop 后 7 天留观计时→可逆=Parquet/备份链回灌（drop 前原备份不删即结构可逆）。

## 四、堵点与病灶
| # | 现象 | 根因 | 修法草案（最小改动面） | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| B1 | 三引擎零接线（承 02-C1/08-C1'） | 晋升批只交模块+测试，宿主班次+YAML 承载未随批 | 最小面两处：①新增 config/cleaning_rules.yaml 承载（DSL 先 flag 档）；②挂 supply_sentinel 同款托管（先例 quality_sentinel_tables.yaml:103-106 `wiring.host_schedule: data_supply_sentinel`，本会话复跑在案）——run_quality_gate 输出形态出生时即对齐 apply_quality_gate（插头对插座，08 册 §五.1）。**不动 ch_writer 热路径为第一档**（8.95B 行 tick 写路径 perf 风险），读侧哨兵班检测先行 | 1-2 天 | 代码面是；**接线启动=Owner 门位（总册 §四·补2 晨报名单"清洗三引擎接线"勿自动施工）→不自裁** |
| B1' | cleaning_rule_engine 头注虚标 CONSUMERS=ch_writer/MATURITY=production（:5/:7 实取） | 晋升时按设计意图填写未回改 | 头注改 built-not-wired（08-C1'' 同案，0.1 天）；风险=后人按头注误判已接线 | 0.1 天 | 是 |
| B2 | 三数互斥（202 vs 338 vs 114）且一天内 201→202 再漂移 | 计数手工写死在散文（违宪法 §4.3/§9.5） | 品类 YAML 计数+CH 表数改生成器产出、头注删手写数 | 0.5 天 | 是 |
| B3 | 影子表 8 张 2,154 万行无 TTL/退役通道 | WO-004 留观无到期机制 | §三 3.4 五步判据流水线（archiver 表级适配+waste_table_scanner 登记） | 2 天 | 流水线可施工；**净删=Owner 门位** |

## 五、提速与合并机会
1. 三引擎+第四件共享 data/__init__ 与 data_eng/__init__ 双门面（re-export 行号实证 §三）→ 单一托管宿主一次全量挂载，零新进程（08 册 §五.2 复证）。
2. 影子表退役与 macro_data 四表家族/index_valuation_v2 多版本收敛（03 册 §五.1）同批走同一五步判据流水线，一次批制呈 Owner。
3. 三数生成器与 table_registry/business_data_categories loader 打通=单计数源（B2 修法即 B3 判据②的行数对比底座）。

## 六、自审闸三态
**挖干可施工**：B1'/B2 直开；B1 流水线/B3 流水线代码面可预制。
**待裁 2 条（均 Owner 门位，本册不自裁，选项+建议）**：
1. **三引擎接线启动**（总册已列 Owner 晨报名单）——选项 A 读侧哨兵班检测先行（建议，风险最低）/B 直插 ch_writer 写前/C 继续封存。建议 A，flag 档灰度 30 天无再报误伤后评估 B。
2. **影子表族净删窗**（涉 8 表 2,154 万行）——选项 A 五步判据逐表批（#382 批制，建议）/B 整族一次性批/C 延后至 hfq 下游回归全绿。建议 A+B 混合：weekly/monthly 4 张 r1 小表先行试点。

## 七、复核命令（本会话全跑通）
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"   # 3.12.8 实测
# 1. 三引擎生产调用面=零（输出应仅：三自身文件+两个 __init__.py+incremental_update_engine.py:25 注释）
grep -rniE "cleaning_rule|cleaning_anomaly|data_anomaly_alerter|CleaningRuleEngine|CleaningAnomalyEngine|DataAnomalyAlerter|run_quality_gate" \
  src scripts config docs/01_policies_and_standards/_registry/catalogs/resource_profile_registry.yaml \
  --include="*.py" --include="*.yaml" --include="*.ps1" 2>/dev/null | grep -v __pycache__ | grep -viE "tests?/|test_" | cut -d: -f1 | sort | uniq -c
# 2. 任务真源零引用（应 rc=1）+ 现行写前挂点（应见 quality_gate import）
grep -inE "cleaning_rule|cleaning_anomaly|data_anomaly" src/zephyr/data/config/schedule.yaml src/zephyr/data/config/tasks.yaml
sed -n '1006,1021p' src/zephyr/data/ch_writer.py
# 3. 头注虚标+承载缺口
sed -n '5p;7p' src/zephyr/data/cleaning_rule_engine.py
ls config/ | grep -iE "clean|rule|sentinel"        # 无 cleaning_rules.yaml
# 4. 三数+影子表（DatabaseService 只读，实测 2026-09-25：253 表/c1_market 202；shadow 8 行清单）
python -c "
from zephyr.infrastructure.database_service import get_db_service
c=get_db_service().get_clickhouse_conn()
print(c.execute(\"SELECT database,count() FROM system.tables WHERE database LIKE 'c%' GROUP BY database ORDER BY database\"))
print(c.execute(\"SELECT name,total_rows FROM system.tables WHERE database='c1_market' AND (name ILIKE '%legacy%' OR name ILIKE '%preversion%' OR name ILIKE '%quar%') ORDER BY name\"))"
grep -c "category_id" docs/03_modules/_cross_layer/database/business_data_categories.yaml   # 338
sed -n '7,11p' docs/03_modules/_cross_layer/database/business_data_categories.yaml          # 头注 114
# 5. 退役兵器三件套头注（archiver 三阶段/waste 门位/rolling 安全阀）
sed -n '7,10p' scripts/ch/archiver.py; sed -n '8p' scripts/ch/waste_table_scanner.py
```
