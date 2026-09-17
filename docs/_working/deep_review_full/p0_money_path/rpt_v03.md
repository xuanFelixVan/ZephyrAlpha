---
oid: V03
对象: BHY/BH FDR 双实现（bhy_fdr.py 与 bh_fdr.py，两实现一致性为显式审查项）
入口: src/zephyr/factor/analysis/bhy_fdr.py:79 与 src/zephyr/strategy_pipeline/bh_fdr.py:42
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 两对象零漂移）
材料包: 两源码+两测试全读；churn；消费方 grep（intake/certifier/decay_monitor/factor_lifecycle_runner）；运行时证据=logs 抽查
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V03 BHY/BH FDR 双实现（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：canonical `bhy_fdr`（BHYFDRResult/bh_qvalues L58-76/bhy_fdr L79-134）+ intake 契约 `bh_filter`（L42-90，决策核已单源委托 bhy_fdr）。
- 显式审查项（任务书）：两实现同概念同结果吗？——**结论：决策等价，已查无漂移**（见 §2 D 行）。
- 测试：tests/factor/test_bhy_fdr.py（9）+ tests/strategy_pipeline/test_bh_fdr.py（7），实测全绿（含 c(5)=137/60 手算锚与红蓝条款）。
- 变更热力：bh_fdr 4 commits（44d3fcc575 收敛→1db71906d7 BHY 默认翻转→f8002ed83d 钱闸批）；bhy_fdr 5 commits——两件都处活跃收敛带上。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | bhy_fdr 数学正确：crit=i·q/(m·c(m))，k=max 通过 rank，前缀拒绝，掩码经 `rejected[order]=rejected_sorted` 正确映射回原序；c(m)=Σ1/i 与 BH(c=1) 开关齐备 | bhy_fdr.py:111-127 | 已查无 | tests:25-58 手算锚全过 + m=5 阈值复算 |
| A | bh_qvalues step-up q 值正确（自底 running min），并列 p 值经 running-min 自动同 q；与 bhy_fdr(arbitrary_dependence=False) 的拒绝集**决策等价**（q_(i)≤q ⟺ i≤k，单调性成立） | bh_qvalues bhy_fdr.py:58-76 | 已查无（一致性显式结论） | 对拍脚本：同一批 p 两路拒绝集相等（单调性解析保证） |
| A | **bh_qvalues 对 NaN p 值零防御且静默出貌似合理的错数（机验实证）**：`bh_qvalues([nan,0.5,0.1])`→[0.15,0.5,0.15]（NaN 被排到 0.1 与 0.5 之间并产出"正常样子"的 q）；`[0.5,0.1,nan]`→[0.75,0.30,1.0]。同族 bhy_fdr 有 NaN 校验（L106-107），canonical q 值函数没有——ERROR_CONTRACT 只挂在 bhy_fdr 头上 | bhy_fdr.py:58-76 vs 106-109 | **P2** | python 一行复现（已机验）；上游 binomial_ge_pvalue 现无 NaN 出口故未爆发，属 canonical 件裸奔 |
| A | bh_filter 校验完备（空族/q 越界 (0,1]/bool 与非有限值拒绝）；q≥1 退化短路已文档化 | bh_fdr.py:50-69 | 已查无 | tests:63-74 |
| A.3 | 红蓝条款到位（纯 H0 族全拒/挑尾拒/步进连续段）；无 NaN 用例（对应上 P2） | tests/strategy_pipeline/test_bh_fdr.py:38-61 | P3 | 读测试 |
| B | 上游 p 值来源：intake 传 candidates（p 值族预注册同批全入族，防选择偏差条款在 INVARIANTS）✓；certifier 传 binomial p（无 NaN 出口）✓ | intake.py:79-82 + certifier:228-230 | 已查无 | 读调用点 |
| C | 消费方：strategy_pipeline/intake（fdr_gate=BH_Q=0.10 预授权，intake.py:59,80-82）、pattern_evidence_certifier（bh_qvalues）、decay_monitor、factor_lifecycle_runner。误放行→伪策略入库（钱路径闸门）；误拒绝→策略饿死（fail-closed 向，可接受） | grep 全列 | 爆炸半径=全自动入库管线+图形认证 | grep |
| D | 双实现一致性（显式审查项）：canonical 单一决策核、bh_filter 零自有统计（仅 dict 接口+步进报告）——**已查无口径漂移**；报告字段 `bh_threshold`=k/m·q 是 BH 阈值而决策用 BHY（c(m)>1 更严），字段名有误导但 `bhy_family_threshold` 并列披露 | bh_fdr.py:77-84 | P3（字段名） | 对比 report 两阈值字段 |
| E | 静默失败面=bh_qvalues NaN（P2）；重复触发纯函数幂等 ✓；bh_filter 末行 assert 校验可被 -O 禁用（与前置校验重复，无害） | bh_fdr.py:89 | P3 | 读码 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| BHY 任意依赖 FDR（c(m)=Σ1/i） | 对等已有（公式逐项一致，默认开启=比文献基线更保守，2026-09-15 Owner 对账④裁定） | Benjamini & Yekutieli (2001), Annals of Statistics 1165-1188：https://www.researchgate.net/publication/38348313_The_control_of_the_false_discovery_rate_in_multiple_testing_under_dependency ；BH 原始 (1995) 同源 |
| 因子多重检验语境（t≥3.0 / 单批>100 因子 t 升 2.8） | 对等已有 | Harvey, Liu & Zhu, "...and the Cross-Section of Expected Returns", RFS 29(1):5-68：https://academic.oup.com/rfs/article/29/1/5/1843824 （2016）。**注意**：仓内文档把 E[max] 同式记作 "Harvey-Liu-Zhu 2021"（deflated_sharpe_calculator.py:247）——HLZ 主文是 RFS 2016；2021 应为 Harvey & Liu "A Census of the Factor Zoo"，年份/篇名引用建议核准（P3 文档 nit，挂 §5） |

## 4 缺陷清单（按严重级）

1. **P2｜canonical bh_qvalues NaN 裸奔**：现状=无校验、NaN 参与排序静默产出貌似合理的 q；证据=bhy_fdr.py:58-76 + 机验两组输入；爆炸半径=凡 future 消费方喂入含 NaN 的 p 族（今天上游无 NaN 出口，属埋雷）；建议=bh_qvalues 开头复用 bhy_fdr 同款 `isnan→ValueError`（或逐元素过滤+审计）；验证法=`bh_qvalues([float('nan'),0.5,0.1])` 现返回 [0.15,0.5,0.15] 而非报错。
2. **P3｜report 的 bh_threshold 字段名与 BHY 决策不一致**：bh_fdr.py:77-84；建议=改名 bhy_threshold 或注明两阈值含义。
3. **P3｜HLZ 年份引用口径**：见 §3。

## 5 挂起疑问

- "Harvey-Liu-Zhu 2021 同式"引用（deflated_sharpe_calculator.py:247、bh_fdr.py:26）是否指 Census of the Factor Zoo——需 Owner/主力会话核准后统一年份引用（checklist#15 邻类：引用不核真源，低危版）。
- BH_Q=0.10 与认证闸 q=0.05 两套预注册阈值并存——已在 V02 登记，此处不重复立缺陷。

## 6 完备性自评

六轴全查（显式审查项"两实现一致性"有独立结论=决策等价已查无）。长尾：①未对 statsmodels 数值逐位对拍（非项目依赖，语义等价由手算锚保证）；②decay_monitor/factor_lifecycle_runner 两个消费方的族构造口径只核了存在性未逐行审。运行时证据：近 3 日 logs 无相关 error。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 NaN 零防御: 确认→治本(bh_qvalues raise ValueError)+回归。复检 28/28(含 bhy_fdr 族)。
- P3 bh_threshold 字段名/HLZ 年份: 挂起。
- 修复提交: 队列 q-20260918-st-deeprev-20260918-0007。
