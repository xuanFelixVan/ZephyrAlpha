---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——CPCV切分
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：CPCV切分（B09）

- 状态: **已审**
- 级别: P1｜类型: 切分内核（切分泄漏重点专项）
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/cpcv.py:64`（CPCVSplit）；generate_cpcv_splits :104；compute_pbo :202
- 生产调用方: backtest/core/strategy_cpcv_matrix.py:57,179（打分矩阵，t1/embargo 透传默认 None/0）；regime/validation/overfitting_guard.py:36（CPCV N=10,k=2→45 组合）
- 测试文件: tests/backtest/test_cpcv.py（184 行 21 测试，本批运行全绿；含精确索引级 purge/embargo 断言——本批 9 对象中测试强度最高）
- 备注: —

## 1 对象快照

- 范围：generate_cpcv_splits（组合切分+purge+embargo）、expected_n_splits、compute_pbo（含平均秩实现）、_group_bounds。
- 排除项：strategy_cpcv_matrix 逐折打分逻辑（消费侧，长尾）；overfitting_guard 组装链。
- 材料包缺项声明：无（纯 numpy 注入式对象，材料自足）。
- 变更热力：5 commits，末次 2026-09-16。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **purge 数学逐条件核验（通过）**：overlap=(i<=e-1)&(t1[i]>=s) 恰当剔除"自身在 test 前且标签伸入 test 区间"的 train 样本；多 test 组（k_test=2）时各组独立 purge 交叉覆盖——组间空隙样本的标签伸入后一 test 组由后组条件剔除，无漏网；drop_mask=test_mask 起步保证 train∩test=∅ | cpcv.py:164-174 | 通过 | test_purge_overlapping_labels（精确到 14/15 剔除、13 保留）复核+手算 k_test=2 场景 |
| A | **embargo 方向核验（通过）**：drop_mask[e:e+embargo) 剔 test 末端**之后**的 train 样本（串行相关隔离带），与 LdP embargo 定义方向一致；末组越界由 min(n_samples,) 截断 | cpcv.py:170-172 | 通过 | test_embargo_excludes_after_test（20/21/22 剔除、23 保留） |
| A | **PBO 数学核验（通过）**：ω=平均秩/(M+1)（防 0/1 logit 爆炸）、同值平均秩、logit<0 计 PBO——与 Bailey et al. (2014) 定义一致；方向隐含 higher-better（见轴D） | cpcv.py:186-257 | 通过 | test_ties_average_rank/test_fully_overfit_pbo_one |
| A | **缺省口径=无保护**：t1=None 退化为点标签无 purge、embargo=0 无隔离带——API 不强制、不 warn；生产消费方 strategy_cpcv_matrix cfg.t1/cfg.embargo 默认 None/0 原样透传（strategy_cpcv_matrix.py:98-99,179）——调用方不显式传=名义 CPCV 实为裸组合 CV | cpcv.py:109-110,142-143;strategy_cpcv_matrix.py:98-99,179 | P2 | 以 t1=i+5 标签默认参数调 generate_cpcv_splits，观察 train 仍含标签泄漏样本且无告警 |
| A.3 | 测试审查：21 项含精确索引断言+PBO 边界（全过拟合=1/全稳健=0/平局 logit=0 不计入）+参数校验——**信任度高**；缺口=k_test=2 多组 purge 交互、t1 跨组标签（样本 i 在组 A、标签伸入组 C）场景无测试 | test_cpcv.py:77-96,130-160 | P3 | 补 k_test=2 标签跨组用例（勿动源） |
| B | 输入校验完备：n_samples/n_groups/k_test/embargo/t1 长度/单调性/t1>=i 全 raise CPCVError（fail-closed）；compute_pbo 拒 NaN/Inf/形状不一致/trial<2 | cpcv.py:134-151,225-237 | 通过 | test_invalid_t1/test_nan_raises |
| C | 消费方两处均生产在册（strategy_cpcv_matrix/overfitting_guard）——非孤儿；但消费方默认参数使保护缺位（轴A第4条即消费面爆炸半径） | cpcv.py:5 | P2（同轴A） | grep 调用点参数 |
| D | **PBO 无 metric 方向参数**：higher-better 硬编码——传损失类/回撤类（lower-better）指标 PBO 反向（稳健判 1-真实 PBO）；docstring 未警示 | cpcv.py:209-211,243-246 | P3 | 以负 Sharpe（等价 loss）入参对比 PBO 翻转 |
| D | embargo 单位=样本数（非时间/标签窗口比例）：LdP 建议 embargo≈标签前瞻窗口的比例，样本数口径要求调用方换算、无文档换算指引 | cpcv.py:126,170-172 | P3 | docstring 审读 |
| E | 组合数 C(6,2)=15 与 split_id 枚举确定性（itertools.combinations 顺序稳定）✓；纯函数无副作用/无 IO ✓（重跑幂等） | cpcv.py:157,28-33 | 通过 | 两次调用输出全等 |
| A(亮点) | _average_ranks_ascending 纯 numpy 实现（去 scipy 依赖）且 O(n²) 平局循环对 n_trials 量级（<1000）无性能问题 | cpcv.py:186-199 | — | — |

## 3 SOTA 对照

- CPCV（N 组取 k 组全组合+purge+embargo+多路径）：**对等已有**——与 López de Prado《Advances in Financial Machine Learning》(Wiley, 2018) Ch.12 及 "Backtest Overfitting in the Machine Learning Era"（SSRN 4686376，2024）的 CPCV 定义一致；该 SSRN 文实证 CPCV 优于 K-fold/WF/单次 OOS 的抗过拟合性——本项目已采用正确范式。（来源：SSRN https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376 , 2024；paperswithbacktest.com CPCV course, 2026）
- PBO：**对等已有**——ω=rank/(M+1)+logit<0 频率即 Bailey, Borwein, López de Prado, Zhu (2014) "Pseudo-Mathematics and Financial Charlatanism" 的 PBO 定义；平均秩平局处理与 sklearn rank 惯例一致。（来源：PBO 原文经 quantresearch.org 出版面与 paperswithbacktest PBO 课程页交叉核对，2026）
- 实现对照：**对等已有**——eslazarev/purged-cross-validation（github, sklearn 兼容）同为 purge+embargo+CPCV 结构，本实现参数校验更严（t1 单调性）。缺 embargoo 时间窗口口径换算指引（见轴D）。

## 4 缺陷清单

1. **[P2] 缺省参数=裸组合 CV 无告警**（t1=None/embargo=0 且生产消费方默认透传）：名义 CPCV 实际无净化，"切分泄漏"防护在场外空转。建议修法：t1=None 且标签窗口声明>0 时 warn；或 strategy_cpcv_matrix 层强制要求显式 t1/embargo（fail-closed 声明）。验证法：§2 轴A 第4条。
2. **[P3] PBO 无方向参数**：lower-better 指标反向。建议修法：加 higher_better: bool=True 参数或 docstring 红字警示。
3. **[P3] embargo 样本数口径无换算指引；k_test=2 标签跨组测试缺口**。

## 5 挂起疑问

- overfitting_guard 的 45 组合 CPCV 是否传 t1/embargo（其 :36 仅声明组合数，参数面未核）——若也未传，与 axis A 第4条同根，PBO 结论的可信度依赖此参数。
- CPCV 头注释 CONSUMERS 标"预留（52 号 §6 重评触发后接线）"与实际已有两处生产调用不符——文档漂移（P3 级，随收口更正）。

## 6 完备性自评

六轴全查。长尾：①strategy_cpcv_matrix 逐折打分与 overfitting_guard 组装链细审（挂起疑问①）；②PBO 对 n_splits=1 退化场景的统计意义（代码放行 n_splits>=1，单折 PBO∈{0,1} 无分布意义——是否 raise 待裁定）；③CPCV 多路径（LdP 的 path-based 评估，每样本归属 C(n-2,k-2) 条路径）未实现——本实现是 per-split 评估而非 path-based，与原文献的完整形态有差距（对照 SOTA 结论仍判"对等已有"，因 PBO 判定不受影响，但 Sharpe 分布估计能力缺位——立卡长尾）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
