---
ttl: task_bound
title: 深度审查报告——LPPL顶部探测（D07）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：LPPL顶部探测（D07）

- 状态: **已审**
- 级别: P1｜类型: 算法（LPPL 线性化网格拟合+五维评分）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/features/lppl_detector.py:123(lppl_blowoff_score)`（186 行全文通读，随机游走误触发率实机实测）
- 生产调用方: **查无**——全仓 grep `lppl_blowoff_score/lppl_detector` 仅模块自身；头栏自认"独立函数，未接入 TRANSITION_CONFIG（T4 已有多维信号兜底）"——与 D03/D04 类似的未接线态，但本模块头栏 `MATURITY=production` 与"未接入"自相矛盾（注册表漂移）
- 测试文件: `tests/regime/features/test_lppl_detector.py`（8 个测试）

## 1 对象快照

- 审查范围：单窗口网格 lstsq 拟合 + 五维评分映射全文件。排除项：10 号 spec §4.8.1 原文（材料包缺项）；T4 评分链其他维度。
- 材料包缺项声明：无运行时证据包；国金宏观 2026-06-14 实证（docstring 引）未回读。
- 测试覆盖概况：8 测试（基本拟合/退化/非正拒绝）；**无随机游走对照、无评分结构（维度恒给分）测试**。
- 变更热力：5 次。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **评分维度空洞化：valid≥1 ⟹ score≥40 ⟹ 恰达 T4 触发门槛**——有效窗口定义已排除边界解，故有效窗口的 m/ω 必落在网格内部点，`m_range[0]<m_med<m_range[1]` 与 ω 同理**恒真**（+20+20 无条件给分）；T4 门槛 LPPL≥40（docstring :34）→"任一窗口非边界 B<0"即触发，实际信息维度只剩 tc 邻近 25+稳健 15+集中 10。实测：纯随机游走 30 次，score≥40 触发率 **13.3%**（无泡沫结构也 7 天里 1 天过线） | lppl_detector.py:165(有效窗定义),176-179(恒真给分),34(门槛)；实测 30 次随机游走 | P1(接线前债务) | 本报告复现脚本（30 次随机游走统计）；接线 T4 前必修：m/ω 维改非平凡判据（如 m<0.5 偏快加速加权）或门槛抬至 45+ |
| A | F-A2 线性化拟合数学正确：log 域、Ccos 展开 C1cos+C2sin、dt>0 恒成立、lstsq+残差 fallback；tc_ahead 网格过滤到空时静默返回零解（b=0 不可用）不崩——防御可接受但无告警 | :97-120,156 | P3 | tc_max_ahead=1 跑单窗口 |
| A | F-A3 网格粒度粗糙：m 9 点/ω 11 点/tc 10 点——tc 中位的标准差（集中度 +10）由 3 个窗口的中位 tc 计算，n=3 的 std 统计意义薄弱；ω 分辨率 1.0 在 ω∈(5,15) 文献典型区间尚可 | :153-156,170-173 | P3 | 加密网格对拍 score 稳定性 |
| A | F-A4 边界解比例信号半消费：§4.8.1"边界解比例"只体现在 valid_ratio 的补数，未参与评分（大量边界解=拟合不稳的警示丢失）；`is_boundary_solution` 判定用精确网格端点比较（浮点网格值精确相等——linspace 端点生成值精确，成立） | :113-118,182 | P3 | 构造边界密集解检查 valid_ratio |
| A | F-A5 输入防御好：非正/NaN 显式 ValueError（fail-closed，:146-147 双检——NaN 比较 False 单独 isnan 捕获）；短序列 degraded 不抛 ✓ | :145-150 | 已查无 | tests 锁定 |
| B | F-B1 输入契约：pd.Series 正价格、index 无谓（不校验日期连续性/等间隔——LPPL 假设均匀 t 网格，停牌跳日会使 t 轴失真，A 股个股停牌常见；指数级使用影响小） | :98(t=arange) | P2 | 造含跳日序列对比 tc 偏移 |
| C | F-C1 孤儿+成熟度漂移（同 D04 家族）：零调用方但 MATURITY=production；爆炸半径暂为 0，接线日 F-A1 激活 | 头栏 vs grep | P2 | grep 复核 |
| D | F-D1 无第二 LPPL 实现（grep 无兄弟）；docstring 声明与代码一致（线性化路线/五维映射/边界解语义逐条可对上） | 全仓 grep | 已查无 | — |
| E | F-E1 静默失败面：全负拟合结果→score=0 不告警（正常语义）；tc 网格空→静默零（F-A2）；无 except 吞噬、无时间副作用，幂等成立 | :150,168 | 已查无 | — |
| E | F-E2 时序面：t=arange 等间隔假设（见 F-B1）；windows 交叠（60/90/120）非独立样本，中位/std 的独立性假设弱——影响集中度维可信度 | :125,159-161 | P3 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | LPPL 模型与拟合路线 | **对等已有（实现）/立卡候选（标定）**——线性化网格是已知简化路线；学界标准为非线性 LS+混合遗传（粗糙景观），本项目网格 990 点/窗无全局优化，可能漏真解；立卡：接入前对标 lppls 开源包（约束非线性拟合）做 A/B | [Johansen, Ledoit & Sornette 2000, Int. J. Theoretical & Applied Finance（LPPL 原始文献族）](https://www.worldscientific.com/doi/abs/10.1142/S0219024900000115)（World Scientific，2000）；[arXiv 2510.10878 (2025) LPPL 系统化识别](https://arxiv.org/html/2510.10878v1)（arXiv，2025） |
| 2 | LPPL 可靠性批评（sloppiness） | **立卡候选（评分校准）**——Chang & Brée 2011"参数 sloppiness 使 tc 预测不可靠"、Brée 2013"11 次崩盘仅 7 次参数落入区间"直接支持本项目"边界解不计分"的谨慎设计，但也警示 tc 邻近维（+25）权重过高；建议接线前用 A 股历史泡沫段（2007/2015/2021）回放定阈值 | [Chang & Brée 2011, Prediction accuracy and sloppiness of log-periodic functions](https://sonar.ch/documents/302953/files/cha_pas.pdf)（Swiss PDF 档案，2011）；[Brée 2013, Testing for financial crashes using the LPPL](https://www.sciencedirect.com/science/article/abs/pii/S1057521913000719)（ScienceDirect，2013） |
| 3 | 近期扩展（AI+LPPL） | **驳回（当前阶段）**——Lee 2025 AI 集成路线依赖大样本标注，与本项目单函数定位不匹配；驳回理由=投入产出不成比例，保留观察 | [Lee 2025, Nature Humanities & Social Sciences Communications](https://www.nature.com/articles/s41599-025-05920-7)（Nature HSSC，2025） |

## 4 缺陷清单（按严重级）

- **F-A1（P1，接线前债务）评分结构空洞+门槛可由噪声达成**：现状=valid≥1 ⟹ +40 恒给分=恰过 T4 门槛，随机游走 13.3% 触发 → 证据=代码路径推演+30 次实测 → 影响=若按 docstring 预告接入 T4（门槛 40），赶顶信号 7 天 1 天假阳；爆炸半径=T4 评分链（当前未接线=半径 0）→ 建议修法=m/ω 维改条件判据或拆分门槛（如 ≥50 才触发），接线前经配置评审（docstring 自己也要求"接入 T4 评分链需经配置评审"——把本发现带入该评审）→ 验证法=本报告随机游走脚本。
- **F-B1（P2）t 轴等间隔假设 vs 停牌跳日**：建议个股级使用前按交易日历重排或声明仅限指数 → 验证法=跳日构造对比。
- **F-C1（P2）MATURITY=production 与零调用方矛盾**：改 trial/design 或登记接线计划 → 验证法=grep。
- **F-A2/A3/A4/E2（P3）**：网格空/粒度/边界信号半消费/窗口独立性——常规队列。

## 5 挂起疑问

1. "国金宏观 2026-06-14 实证 KOSPI/SOX"（docstring 引）支持 LPPL 在指数级的可用性——原文未回读，其实证参数范围与本模块 m_range/omega_range 是否同源未核。
2. T4 接入评审时点——F-A1 修复义务应挂到该评审的前置条件。

## 6 完备性自评

- 六轴全查：A（线性化数学/网格/退化/评分结构逐项+噪声实测）、B（价格契约+t 轴假设）、C（零调用方核实）、D（无双实现+文档一致）、E（幂等/静默面/时序假设）、F（3 条带来源，含反对文献）。
- 长尾清单：①10 号 spec §4.8.1 原文未回读（评分表↔代码逐行对账完成度 90%，边界解比例维消费判定基于 docstring 转述）；②随机游走实测样本 30 次较小（触发率 13.3% 的置信区间宽，量级结论可信）；③np.linalg.lstsq 数值行为在近奇异设计矩阵下的表现未压力测试。
