---
ttl: task_bound
title: "F05 判重与数据审计——tick 14 字段判重正门+产业链审计循环复飞案卷"
session: zc-l01-20260927
---

# F05 判重与数据审计（复飞案卷）

> 前序：M1 册 02_cleaning.md D5 面；本卷=独立取证（check_tick_duplication 本日实核+M5 接线普查新发现），首次单独立卷。

## 一、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游 | tick_data 8.95B 行写入流（F10→F06 链）；产业链数据修复循环上游=ig_chain 族图谱数据（F12） |
| 下游 | F12 产业链审计修复闭环；integrity_check 班报告；数据审计专项（data_audit_sop 族） |
| 自动触发 | integrity_check 17:xx 日批 subprocess 唯一自动触发（integrity_checker.py:54-66）；manual 判重 CLI |
| 真源注册表 | 判重判据=scripts/governance/data_quality/check_tick_duplication.py:18-23（**14 字段全同才算真重复，禁 count-uniqExact**——2026-07-16 误删 21 个月 tick 事故治本件，357 行）；审计 SOP=data_audit_sop/industry_chain_data_audit_policy.md；RULE-DATA-OPS=trae_063（判重禁聚合数=宪法硬规则 7） |
| 门禁质量尺 | 14 字段全同判据+FINAL 引擎去重语义；M5 接线普查新发现：check_tick_duplication 列"**疑似判据失效 3 件**（有调用方零测试）"（wiring_gap_inventory §1.6 C 类）——执法件自身无配对红证 |
| 运行状态 | **绿带疤**：判重正门在岗（integrity_check 班自动）；疤=①判据件零测试（M5 机判）②产业链审计循环=手工 SOP 驱动无自动编排 |

## 二、子模块三级枚举

1. tick 判重：check_tick_duplication.py（14 字段铁律 :18-23；ch_reader 依赖）+integrity_checker.py（动态发现 tasks.yaml 全表）
2. 去重族：news_dedup（标题 MD5，MOD-L00-004 §4.3）；alert merge_window 去重（alerter）
3. 产业链审计：industry_chain_data_audit_policy.md（审计修复循环真源）+scripts/industry_graph/（fix_s6_s7_nodes.py/execute_r1_chain_plans.py 等修复件 8+）
4. 数据审计面：docs/_audit/data_utilization_audit_2026-08-24.csv（63 号审计，59/106 零引用分母真源）；chain_fullflow census 族（假绿/守卫普查）
5. 治理链：RULE-DATA-OPS 三步验证（破坏性操作）+waste_table_scanner 门位（退役 Owner 批制）

## 三、接线四态独立复核

- 总册：built/P2/D5。独立复核：**built 成立但降级风险在案**——判据件有调用方（integrity_check 班）零测试（M5 census C 类疑似判据失效 3 件之一），宪法 RULE-DATA-OPS 四执法件落"疑似判据失效/半接线"名单（wiring §1.6 末）。
- 骨架勘误⑦：总册 F05 上游列仅 F01，实际完整性检查上游还含派生 build 任务族（consensus_daily_build 等整表重算件的判重/新鲜度面）——census NOT_GREEN 25 腿为其工作面。
- 关联：姊妹定版卷 F125（data_governance P0 新环）与本环节"数据治理本体"相邻——审计循环的治理侧落位归 F125，本卷登记待裁勿改总册。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| D1 | check_tick_duplication 零配对测试（判据回退无红证） | 施工：采红样 2 例（真重复/边界串位）挂 replay harness（M5 43 门红样采集同批） | P1 |
| D2 | 产业链审计修复循环手工驱动 | 施工：审计循环事件触发化（宪法 §9.3 禁 cron 常驻，事件源=审计报告落盘） | P2 |
| D3 | 59/106 零引用表的审计闭环 | 挂起+解锁=F06 卷空壳表处置批（同账不重复） | P1 |
| D4 | news_sentiment_score 值级假绿（冻结 2025-09-09） | Owner 门（wiring §2.3-4：Ollama 11434 恢复仅凭 Owner 显令） | P1 |

## 五、自审闸三态

挖干可施工（判据件本日实核 sed :18-23+调用链 integrity_checker.py:54-66 双源）；D1/D2 可施工；D3/D4 挂起/Owner 门。

## 六、复跑命令

```bash
sed -n '18,23p' scripts/governance/data_quality/check_tick_duplication.py   # 14 字段铁律
sed -n '54,66p' src/zephyr/data/integrity_checker.py                        # 唯一自动触发
find tests scripts -name "*tick_dup*" 2>/dev/null | grep -v check_tick_duplication.py | head   # 配对测试=零
ls scripts/industry_graph/ | head -12
```
