---
ttl: task_bound
title: F24 E5 协同去重（簇首准入）——L03 接线矿道案卷
session: zc-l03-20260927
---

# F24 · E5 协同去重

> 挖矿基册=01_strategy_factory/b2_f24_e5_synergy_dedup.md（SF-B）。本卷=09-27 独立复核，双实现/两待裁维持，零态变。

## 一、六向台账
| 向 | 实证锚点（09-27 实测） |
|----|------|
| 上游 | strategy_screen bothwin 及格行 **tested=85/passed=16 维持**（本日实跑）；及格集两两 ρ（重叠<60 日不聚类）；p 值=t 双侧解析式 |
| 下游 | intake.run_intake_auto ③步 cluster_heads→注册表（生产零运转=BP-5 维持）；差异化工件报告；StrategyScreener3D 三轴初值 |
| 自动触发 | 无独立触发——c4_batch_completed 轻事件→run_intake_auto 内联第③步；无计划任务；本日 pending 队列无 c4_batch_completed（上游 BP-3 未 drain，E5 入口从未生产触发） |
| 真源注册表 | 图 FAC-E5 built；MOD-BT-086（src/zephyr/pf_alloc/core/synergy_dedup.py）与 intake.py:86 cluster_heads 双实现并存维持；bh_fdr.py q≤0.10；screen_source MOD-BT-191 |
| 门禁质量尺 | ρ 阈值 0.70 两实现同值；确定性序；簇成员只标 redundant 不删除；BH 当批及格全集 |
| 运行状态 | **黄（引擎绿、生产链零运转）维持**。tests/backtest/test_synergy_dedup.py **4 passed 本日复跑**；F06 车道 1 次真实去重在 f06_survivors dedup 列；生产 intake 报告 **8/8 全 pytest 泄漏（6→8，见 F25 卷）** |

## 二、子模块三级枚举
1. **代码面**：synergy_dedup.py（Sharpe 簇首贪心，纯函数；intake.py=并查集 p 值簇首——两准则并存待裁①）；screen_source.py（批次 parity+动态窗两职）；bh_fdr.py；strategy_screener_3d.py。intake.py 与 HEAD 一致（无在途改动）；promotion_advisory.py 工作树有改动（F74 域，与 E5 无涉）。
2. **注册表/文档面**：FAC-E5 algo_note"对称正交化+增量 IC 禁朴素等权"**全仓无工厂链路实现维持**（待裁②：降级为演进方向或立项）；MOD-BT-086 注册真源。
3. **数据面**：bothwin 16 及格在账待消费（CAND×10+FACT×6）；f06_survivors dedup 列 1 例；报告面 docs/_working/pipeline-research/reports/ 8 对 md+yaml 全泄漏。

## 三、接线四态独立复核
- 总册 built → **维持 built（引擎级）/生产链零运转**——与基册一致，无态变无勘误。
- 图 FAC-E5 节点状态与实建（相关性聚类）的语义差（正交化法注）维持待裁②。
- L02 交叉：E5 上游=16 及格在账无消费，与 BP-5 一致。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 双实现双准则并存（Sharpe vs p 值簇首） | 两文件并读 | 待裁①：归并方向（w5_1 内收判据：保 intake 版，086 转测试对照） | P1（待裁） |
| 2 | 图上法注（正交化+增量 IC）无实件 | grep 工厂链无实现 | 待裁②：法注降级或立项增量 IC 件 | P2（待裁） |
| 3 | 及格集 16 条堆积无消费 | bothwin+0 生产报告 | 根因在 BP-5（F25 卷处置），本环节随动 | P1 |
| 4 | 生产报告泄漏增量 6→8 | 09-25 11:57/12:19 两对新泄漏 | F25 卷缺口 2 同案（REPORT_DIR 注入） | P1 |

## 五、自审闸三态
**挖干（复核维持，含 2 待裁）**。引擎测试本日复跑绿；两待裁（簇首准则/正交化法注）随册呈总筹；本环节零代码缺陷新发现。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -m pytest tests/backtest/test_synergy_dedup.py -q      # 4 passed
python scripts/backtest/strategy_screen_query.py bothwin      # 及格 16
sed -n '80,120p' src/zephyr/strategy_pipeline/intake.py       # 并查集实现
grep -L "pytest_" docs/_working/pipeline-research/reports/intake-*.md | wc -l  # 0=全泄漏
grep -rn "正交" src/zephyr/pf_alloc scripts/backtest --include="*.py" | grep -v test | wc -l
```
