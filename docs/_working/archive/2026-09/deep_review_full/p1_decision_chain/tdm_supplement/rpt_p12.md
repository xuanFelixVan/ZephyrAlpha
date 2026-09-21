---
ttl: task_bound
title: 深度审查作业簿——动量活跃度排名（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：动量活跃度排名（P12）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/data/sector_ranking_engine.py`
- TDM 节点: TDM-E-L2-01-2
- 生产调用方: sector_snapshot_collector.py（push_pool 真消费方）+ sector_factor_manager / sector_intraday_aggregator / concept_factor_mapper / sector_report_builder / sector_strength_aggregator（grep 实证，活件）
- 测试文件: tests/zephyr/data/test_sector_ranking_engine.py（合批 39 passed）

## 1 对象快照
MOD-L00-004 全文件（283 行）：880xxx 板块 5 因子百分位复合排名→Top99 推送池，含默认池回退。排除项：sector_snapshot_collector 上游采集。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | **相对强度因子方向反转（P1）**：因子 5 设计="板块-大盘强弱差…反映相对强度"（强于大盘=高分），代码 `abs(板块涨跌幅 − 大盘涨跌幅)` 取绝对值后升序百分位——偏离大盘越大分越高，**弱于大盘的板块同样高分**。实测：强板块(+5%)得分 0.325 垫底，弱板块(−5.26%)得分 0.6 居首——推送池系统性纳入弱势板块 | :24,146；实测见验证法 | **P1** | `python -c "import sys; sys.path.insert(0,'src'); rows=[('880001.SH','3200.0','3168.32','3195.0','1e9','100','200'),('880301.SH','10.5','10.0','10.4','5e8','10','20'),('880302.SH','9.0','9.5','9.45','5e8','10','20')]; from zephyr.data.sector_ranking_engine import compute_ranking; print(compute_ranking(rows))"` |
| A 深度 | **并列不处理+无 ORDER BY（P2）**：_pct_rank 对同值元素按输入行序赋不同名次（0.4/0.6），SQL_LATEST_SNAPSHOT 无 ORDER BY→CH 行序不确定→并列时同输入不同输出，池边界成员可跨次翻转（INVARIANTS"同输入必同输出"被违反） | :95-111,65-70 | **P2** | 构造两行完全相同因子值跑两次看池差异 |
| A 边界 | NaN：float('nan') 经 _pct_rank 排序行为未定义（NaN 比较无全序），score 可 NaN 入池；last_close=0/before_5min=0 除零守卫返回 0（好）；空表→默认池回退 | :114-125,215-217 | P3 | snapshot 行含 'nan' 字符串观察排名 |
| A A股 | 880001.SH（同花顺大盘基准）缺失回退全板块均值（口径切换无留痕标记）——大盘跌时全跌，均值基准使相对因子全体压缩，方向 bug（上条 P1）叠加后语义进一步失真 | :158-165 | P3 | 删 benchmark 行对比池 |
| B 上游 | ch_reader FINAL 去重+只读账号（审计治本留痕）；快照无数据→回退默认池（成分股数量 Top99）仅 log——checklist #6 变体：断供时静默换口径，池质量降级无人知 | :81-92,213-217,233-235 | P3 | 停 snapshot 写入观察回退日志 |
| C 下游 | push_pool 被 sector_snapshot_collector 真消费（采集范围=爆炸半径：弱板块入池→采集→L2 板块分析全链被污染方向性偏置） | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 5 因子权重硬编码常量（无配置外置）；与 P11 sector_analyzer 强度口径异构（见 rpt_p11 轴 D）——无换算文档 | :57-62 | P3 | — |
| E 对抗 | 五问：①异常→默认池仅 log（断供面）②方向反转=系统性假阳性（弱当强）③无监控面 ④重跑受行序非确定影响（见 A-2）⑤无时序面 | 全文件 | 已查无 | — |
| F 新鲜度 | **已检索**（MA/动量族共享）：MA 交叉与动量规则证据——"Optimal trend-following with transaction costs"（IRFA/ScienceDirect 2023）支持趋势规则有效性与交易成本敏感；共识=动量因子需方向正确的前提。结论：对等已有（5 因子百分位复合=常见多因子做法），但因子 5 实现违背其自身定义（见 P1），不属"业界也这样" | https://www.sciencedirect.com/science/article/pii/S1057521923004441 | — | — |

## 3 SOTA 对照
多因子百分位复合排名：对等已有（业界常规做法）；因子 5 的 abs() 实现与任何文献口径不符——纯实现缺陷。

## 4 缺陷清单
1. **P1 相对强度因子方向反转**：去掉 abs()（保留符号，升序百分位=越强越高分）或改语义文档；修复后需重算推送池存量。爆炸半径=推送池→采集→L2 全链偏置。验证法：单行复现见轴 A。
2. **P2 并列名次非确定**：_pct_rank 补并列同分（average ranking）；SQL 加 ORDER BY sector_code 兜底。验证法：见轴 A。
3. P3 NaN 防护（isfinite 过滤+notes）。
4. P3 回退默认池仅 log 无 degraded 标记外透。

## 5 挂起疑问
- 修复 P1 后推送池成员将系统性变化（弱板块出局）——存量快照对比与新旧行为差异需 Owner 知情后施工。

## 6 完备性自评
六轴全查。长尾：5 因子权重（30/25/20/15/10）无标定产物锚（与 P10 premium_factor 同型问题，登记未展开）；测试对方向性断言缺失（39 条未含相对强度方向用例——测试盲区实证）。
