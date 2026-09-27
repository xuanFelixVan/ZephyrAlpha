---
ttl: task_bound
title: F25 E6 入库监控（台账只增+判死）——L03 接线矿道案卷
session: zc-l03-20260927
---

# F25 · E6 入库监控

> 挖矿基册=01_strategy_factory/b2_f25_e6_intake_monitor.md（SF-B）。本卷=09-27 独立复核+增量（sim 态 1→2/泄漏报告 6→8/sim_observe 毒丸遗迹）。

## 一、六向台账
| 向 | 实证锚点（09-27 实测） |
|----|------|
| 上游 | 簇首集（intake ③步）；decay 输入=strategy_screen is_sharpe/oos_years_decay 行（bothwin tested=85）；E4 档案 run 指针 **data/backtest_artifacts/runs/ 154 项**（SCR-C4-*/SCR-20260912-192909/E4-F06-38b453ca 等在盘本日 ls 实证） |
| 下游 | strategy_registry.yaml **strategy_id 键 162（列表项 161+1）**；**lifecycle=sim 2 条**（基册 1 条→新增 CAND-e3da6fa71af1 panic_rebound/MOD-BT-068/bothwin 及格榜首，09-13 生成的注册条目；与 PR 组 F74 卷"sim 态 2 条"交叉一致）；decay ledger updated_at **09-21 维持未再更新** |
| 自动触发 | c4_batch_completed→run_intake_auto 建成未投产维持（本日 pending 队列 0 条 c4_batch_completed）；sim 日件链 **绿至 09-26**：sim_ledger_daily/sim_journal_daily 09-26T00:42、sim_observe_daily 09-26T21:27、attribution_daily 09-26T00:42（last_audit.json 实读） |
| 真源注册表 | 图 FAC-E6 built；MOD-BT-078/187/188/189/192；MOD-SIG-150 衰减台账（strategy_decay/2，574 键全 probation 维持）；promotion_advisory 三条件（工作树在改=F74 域在途） |
| 门禁质量尺 | CAS only-add+写后复核；decay 公式与 c4 OOS 批一字不差；EVIDENCE 缺失 fail-closed；终裁=Owner |
| 运行状态 | **黄维持**。STR-AUTO=0（grep 实证）；生产 intake 报告 **8/8 全 pytest 泄漏（基册 6→8：09-25 11:57/12:19 又泄 2 对）**；**新遗迹：pending 队列 sim_observe_daily PIPE-20260925-105718 attempts=3 poison**（last_error="未知事件 kind"——执行体接线曾随快照回退丢失，st-ec2-p0 已按 HEAD 测试契约补落于工作树未提交，marker 09-26T21:27 证明补落后跑通；毒丸=事故窗口遗体不重试） |

## 二、子模块三级枚举
1. **代码面**：intake.py（六步编排；REPORT_DIR 未注入缺陷维持，intake.py 与 HEAD 一致=未修）；registry_writer.py（CAS）；lifecycle_fsm.py（8 态）；strategy_decay_certifier.py；strategy_lifecycle_advisor.py；strategy_screen_query.py（五命令）。
2. **注册表/文档面**：strategy_registry.yaml（162 键/sim 2/candidate 151 本日实数）；strategy_decay_ledger.json；FAC-E6 节点；管线研究报告目录。
3. **数据面**：runs/ 154 项（E6 evidence 指针源）；衰减台账 09-21 版；泄漏报告 8 对；last_audit.json 日件 marker 全表。

## 三、接线四态独立复核
- 总册 built → **维持 built（台账/判死/监控引擎）/自动入库链未投产**，无态变。
- **骨架勘误**：①"registry sim 1 条"→**2 条**（panic_rebound 已在册 sim 态；为 E7 前哨考核对象池补了 1 条米，但非自动链产物，出生证=人工路径）；②F74 卷"163 条目"与本卷 162 键差 1（口径漂移，以机器实数 162 记，待 F74 域对表）。
- L02 交叉：BP-5 前置（清泄漏→首跑）**未执行且泄漏反向增长**（6→8）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 自动入库链生产零运转，及格 16 在账堆积 | STR-AUTO=0+8/8 泄漏 | BP-5：清泄漏→REPORT_DIR 注入修→一次 drain 验证首条自动入库 | **P0** |
| 2 | 泄漏报告持续增长 6→8 | 09-25 午后 2 对新泄漏 | 同上+纪律：测试写生产路径违反 §9.6 | P1 |
| 3 | decay 台账 6 天未再更新（09-21 止） | updated_at 字段 | 核 decay_watch 触发班次；建议器与台账合并一班（基册提速项） | P2 |
| 4 | sim_observe 毒丸遗体占队 | PIPE-20260925-* poison=true | 队列卫生：确认补落版本后清遗体（drain 侧 poison 过滤已在，:329） | P2 |
| 5 | 反馈环 FL2（E6→E1）无实件 | 全仓无配额消费者 | 与 F28 回灌环（FL1）同案立项 | P1 |

## 五、自审闸三态
**挖干可施工（复核维持+三增量）**。引擎全 built；增量=sim 池 1→2（E7 前置 1 部分缓解）、泄漏 6→8（BP-5 恶化）、sim_observe 接线丢失-补落事故全程实证（工作树未提交态）。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -c "strategy_id:" docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml   # 162
grep -c 'lifecycle_status: "sim"' docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml  # 2
grep -c "STR-AUTO" docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml       # 0
grep -L "pytest_" docs/_working/pipeline-research/reports/intake-*.md | wc -l                     # 0
ls data/backtest_artifacts/runs/ | wc -l                                                          # 154
cat .runtime/strategy_pipeline/last_audit.json | tr ',' '\n' | grep -E "sim_|attribution" | tail -6
```
