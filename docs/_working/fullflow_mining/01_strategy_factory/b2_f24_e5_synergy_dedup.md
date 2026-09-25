---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F24 E5 协同去重——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F24 · E5 协同去重

> 组 SF·策略工厂供给链 B 后半册 2/7。上游 F23（bothwin 及格集），下游 F25（簇首入库）。
> 环节真源：config/strategy_production_map.yaml FAC-E5（build_status: built；真身=MOD-BT-086 + C6 管线内聚类）。

## 一、环节定义与边界

一句话：单因子好看没用——加进池子能涨分吗？及格集按日收益相关性聚类，簇首准入、簇成员标 redundant_of 留档；BH-FDR 门族=当批及格全集（防选择偏差）。
供料方：E4 考试（strategy_screen bothwin 及格行）。消费方：E6 入库（intake 只收簇首+差异化论证）、E8 组装（相关性闸 MOD-PA-004 复用同阈值体系）。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | ①strategy_screen 及格行（bothwin tested=85/passed=16 实测）；②日净收益相关矩阵（screen_source：及格集两两 ρ，重叠<60 日=0 不聚类——宁漏勿误）；③p 值=t 双侧解析式（簇首=证据最强） |
| 下游消费 | ①intake.run_intake_auto ③步 cluster_heads→注册表入库（intake.py:274）；②差异化工件（报告 md：簇首/absorbed 列表 intake.py:227）；③StrategyScreener3D 三轴差异化评分（pf_alloc/core/strategy_screener_3d.py，新条目挂图类别初值） |
| 自动化触发 | 无独立触发——作为 c4_batch_completed（轻 kind）→run_intake_auto 的第③步内联执行；无计划任务、无常驻 |
| 真源与注册表 | 图节点 FAC-E5；MOD-BT-086（src/zephyr/pf_alloc/core/synergy_dedup.py）；管线实现=zephyr/strategy_pipeline/intake.py:86 cluster_heads＋screen_source.py MOD-BT-191；BH 门=zephyr/strategy_pipeline/bh_fdr.py；F06 车道去重=f06_survivors.csv `dedup` 列（"E5 同族剔除 fbfed6a29a5a（仅差 A2=ic_ir）"） |
| 门禁与质量尺 | ρ 阈值 0.70（两实现同值）；重叠<60 日不聚类；确定性序（intake=sid 字典序+并查集；MOD-BT-086=Sharpe 降序贪心）；BH q≤0.10（sim 流转三条件之一）；簇成员只标 redundant 不删除（两实现同则） |
| 当前运行状态 | **黄（引擎绿、生产链零运转）**。证据：①tests/backtest/test_synergy_dedup.py 4 用例绿（同簇合并/独立分离/单例/簇首最强）；②F06 车道 1 次真实去重记录在案（f06_survivors.csv dedup 列）；③C6 全链生产运行=0（docs/_working/pipeline-research/reports/ 6 份 intake 报告全部是 pytest 泄漏件，grep -L "pytest_" 结果为空）→详见 F25 册；④bothwin 16 及格在账待消费 |

## 三、子模块清单

| 模块 | 是什么 | 入口 | 状态 |
|------|--------|------|------|
| MOD-BT-086 synergy_dedup | 相关性聚类+簇首（贪心 O(n²)，簇首=Sharpe 最高；纯函数无 IO） | src/zephyr/pf_alloc/core/synergy_dedup.py:27 | built（测试钉死；**生产链路未调用**——消费面只有 C5 差异化分析与测试） |
| intake.cluster_heads | C6 管线内第二套聚类实现（并查集，簇首=p 值最小=证据最强） | src/zephyr/strategy_pipeline/intake.py:86 | built（管线实装；同为纯函数） |
| screen_source MOD-BT-191 | 及格集/ρ 矩阵/p 值/三轴初值只读数据源（两职分离：批次身份 parity+活估计动态窗） | src/zephyr/strategy_pipeline/screen_source.py | built（tests/strategy_pipeline/test_screen_source.py） |
| bh_fdr | BH 假设族 FDR 门（q≤0.10） | src/zephyr/strategy_pipeline/bh_fdr.py | built |
| StrategyScreener3D | 三轴差异化评分（收益清晰度/参数稳定性/互补性） | src/zephyr/pf_alloc/core/strategy_screener_3d.py:128 | built |
| F06 车道 E5 去重 | f06_e4_wfa_exam 侧对同族配方（仅差单参数）按 dedup 列剔除 | data/strategy_intake/f06_survivors.csv | built（1 次实跑在案） |

## 四、堵点与病灶

1. **同语义双实现并存**（现象=MOD-BT-086 与 intake.cluster_heads 两套聚类；根因=C6 管线施工时按"确定性+簇首=证据最强"重写，未复用 086 的 Sharpe 簇首口径；修法=按内收判据 w5_1"同真源可派生→必并"：保留 intake 版为生产真源，086 退役或改为 intake 的测试对照件；工作量=S；本车道可修=是，须裁定登记）。**待裁**：簇首准则 Sharpe 最高（086/图上法注）vs p 值最小（intake 实装）——两准则在弱信号段会选出不同簇首。
2. **图上法注与实建两张皮**：FAC-E5 algo_note 写"对称正交化后增量 IC 显著才准入+IC_IR 加权禁朴素等权"——全仓 grep 无工厂链路实现（唯一正交化实件在 alt_data_signal_extractor，另类数据域，与工厂无关；ic_ir 仅 limit_up 打分器，无关）。实建=相关性聚类准入。修法：production_map algo_note 标注"演进方向（未建）"，或立项增量 IC 准入件。**待裁**（图语义级，须 Owner/总筹裁）。
3. **生产链零运转**：及格集 16 条躺在台账，无一次真跑 intake 消费（根因在 E6/BP-5，非本环节代码缺陷）。

## 五、提速与合并机会

- 双实现合并（堵点 1）本身即提速：消一处测试维护面。
- screen_source 相关矩阵与 E8 strategy_correlation_gate（MOD-PA-004）同为"今日相关结构"消费，可共用一次快照计算。

## 六、自审闸三态

**挖干**（证据齐）；**两项待裁**：①簇首准则与双实现归并方向；②"对称正交化+增量 IC"图上法注降级为演进方向还是立项施工（差件=增量 IC 对基准因子回归器+准入闸）。按总筹册模板本应写 pending_rulings.md——本战役纪律为零 commit/只写本目录，两案随本册呈总筹代转。

## 七、复核命令（10 分钟）

```bash
sed -n '80,120p' src/zephyr/strategy_pipeline/intake.py      # 管线聚类实现
sed -n '16,45p' src/zephyr/pf_alloc/core/synergy_dedup.py    # 086 契约头
python -m pytest tests/backtest/test_synergy_dedup.py -q     # 4 用例
python scripts/backtest/strategy_screen_query.py bothwin     # 及格集 16
grep -L "pytest_" docs/_working/pipeline-research/reports/intake-*.md  # 生产报告=0
grep -rn "正交" scripts/backtest src/zephyr/pf_alloc --include="*.py" # 工厂链无正交化
```
