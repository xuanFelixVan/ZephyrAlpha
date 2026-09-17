---
oid: V07
对象: DSR 计算器（deflated_sharpe_calculator，MOD-SIM-024；历史事故=分母批内N→累计N 口径翻案，checklist#1 重点）
入口: src/zephyr/simulation/deflated_sharpe_calculator.py:327（deflated_sharpe_from_moments）
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 本对象零漂移）
材料包: 源码+测试全读；churn；消费方 grep；分母口径链（V04/V05 交叉）；运行时证据=logs 抽查
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V07 DSR 计算器（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：全仓 DSR 唯一数学真源——variance_of_sharpe（L280-310）、expected_max_sharpe_z（L242-273）、sharpe_variance_is_degenerate（L317）、deflated_sharpe_from_moments（L327-371）、DeflatedSharpeCalculator.calculate/track_trend（L417-564）。
- 专项（checklist#1 统计口径单点漂移）：DSR 分母批内 N→累计 N 翻案（e58d28df99/5548b45ca4）后的现状=①分母真源=TrialLedger（V04 已审，metrics._resolve_n_trials 优先账本）；②账本不可读→N=10 fallback 强制 dsr=0+degenerate=True+is_overfitting=True（metrics.py:351-355，S1-A4 裁定）；③存量重算=dsr_recalc_backfill 经 ledger.cumulative_trials()。**口径闭环三件齐，已查无新漂移。**
- 历史两病灶（SDC-3 峰度口径/SDC-4 退化态）已于 c88d5e33db（裁定#291）治本，本审以修复后代码为准复核。
- 测试：tests/simulation/test_deflated_sharpe_calculator.py 约 40 用例（含 NormalDist 独立预言机全链对拍、Lo(2002) 边界机检锚、解析真值 E[max] 锚、三实现收敛锁），实测全绿。
- 变更热力：8 commits；近两笔为口径治本批（0cbf503a8f/c88d5e33db）——事故后热区，修复方向与文献一致。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | V[SR]=(1−γ·SR+(κ_p−1)/4·SR²)/(T−1)，超额峰度恒 +3 转 Pearson——与 Lo(2002)/Bailey-LdP(2014) 原式一致；iid 正态锚 V=(1+SR²/2)/(T−1) 有 rel=1e-12 机检（tests:289-312） | deflated_sharpe_calculator.py:280-310 | 已查无 | tests:282-323 复算 |
| A | E[max(Z_N)] 闭式 (1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(Ne)) 与论文一致；渐近式已退役且有回归锁（N=2 旧值 0.8469 不得复活）；测试按解析真值+容差对拍（N=2 真值 1/√π） | :242-273 + tests:127-163 | 已查无 | tests:144-146 复算 |
| A | DSR=Φ(SR/√V[SR]−E[max])：非年化 SR 与 V[SR] 同量纲自洽；年化仅展示（×√252，A股日频口径 ✓） | :334,370-371,463 | 已查无 | 读码+tests oracle |
| A | 退化态 fail-closed（SDC-4）：V[SR] 非正/NaN（`not (var>0)` 防 NaN 漏判）、零方差、n<4 矩不可估→dsr=0.0+degenerate=True+WARNING 出声；退化优先于阈值（threshold→0 也不显著，测试钉） | :87-92,317-324,354-371,478-492 + tests:412-467 | 已查无 | tests:436-442 |
| A | NaN 收益序列路径机验推演：std=NaN→sr 占位 0→_return_side_degeneracy 捕获→degenerate ✓；四问边界（空/单样本/全 NaN/除零/溢出）全有显式归宿 | :374-385,438-449 | 已查无 | 构造 [nan]*n 复现 |
| A.3 | 测试预言机独立（statistics.fmean/pstdev/NormalDist 与实现不同码路）；"实现即真值"旧断言已废除并留档注释；三实现收敛锁（官方件/裁定器/metrics）防再分叉 | tests:347-529 | 已查无 | 读测试 |
| B | 上游：returns（调用方切片）、num_trials（V04 账本链，见 §1 专项）、rf（metrics 按 rf/periods_per_year 换算成每期 ✓） | metrics.py:336-340 | 已查无 | 读换算点 |
| C | 消费方：sharpe_calculator_fixer、result_analyzer、metrics.calculate_full_metrics（→fw_backtest S11 验收→evaluate_dsr 闸）、overfitting_adjudicator（委托）。错值→晋级判定错（钱闸直达）；退化态出声+degenerate 字段双保险 | 文件头 CONSUMERS + grep | 爆炸半径=全策略晋级判定 | grep 全列 |
| D | 全仓 DSR 三处实现已单源收敛（c88d5e33db），收敛测试三把锁；峰度入参全仓超额口径约定有专文（KURTOSIS_PEARSON_NORMAL 注释块） | :29-44,73-78 | 已查无 | tests:476-507 |
| E | 五问：静默失败=无（退化必 WARNING+字段）；假阳性=退化态永判非显著 ✓；断了没人知道=logger 命名空间清晰可采 ✓；重复触发=纯函数 ✓；时序=无状态 ✓ | 全文件 | 已查无 | 读码+tests caplog |
| E | 小口径瑕疵：calculate docstring 说"样本不足(<3)抛错"，实际 n=3 被接受但落退化态（n<_MIN_OBS_FOR_MOMENTS=4）——行为正确（保守），注释与行为有半格差 | :440-444 vs :89-92,383-385 | P3 | `calculate([r1,r2,r3])` 返回退化而非抛错（tests:452-459 已钉行为） |
| E | track_trend 退化窗口 dsr=0.0 落在趋势序列里，画图消费方可能读成"DSR 跌到零"——已有 DSR_UNDECIDABLE 语义注释，但序列本身不带 degenerate 标记 | :520-564 | P3 | 读 DSRTrendPoint 字段（无 degenerate 位） |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| DSR 本体（V[SR]+E[max]+Φ） | 对等已有（三式逐项与论文一致） | Bailey & López de Prado, "The Deflated Sharpe Ratio" (2014, Journal of Portfolio Management)：SSRN 2460551 https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 ；全文 PDF https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf |
| 有效试验数 N'（非独立 trials） | 对等已有（论文以聚类分析换算 N'，仓内以 V04 effective_rank 落地——同指引不同估计器，属合理选型） | 同上论文 §multiple testing；估计器家族对照见 V04 §3（Nyholt 2004/poolR） |
| 峰度口径（Pearson vs 超额） | 对等已有（Lo (2002) 修正 SR 方差原式即 Pearson 口径，+3 转换正确） | Andrew Lo (2002), "The Statistics of Sharpe Ratios", Financial Analysts Journal（通行引文，本轮 URL 未实证记部分受阻；公式经 iid 正态边界机检自洽） |

## 4 缺陷清单（按严重级）

1. **已查无（P0/P1 级新缺陷）**——历史口径翻案与两病灶（SDC-3/SDC-4）修复态经全链复核成立，三实现收敛有测试锁。
2. **P3｜docstring "<3 抛错" vs n=3 落退化的半格差**：:440-444；建议=注释改为"<3 抛错；3≤n<4 落退化态"；验证法=同 §2 E 行。
3. **P3｜track_trend 序列无 degenerate 标记**：:520-564；建议=DSRTrendPoint 增 optional degenerate 位（消费侧兼容）；验证法=读 dataclass 字段。

## 5 挂起疑问

- HLZ 引用年份（:247 "Harvey-Liu-Zhu 2021 同式"）与 RFS 2016 主文之辨——同 V03 §5，统一核准后改。
- DSROverfittingFloor=0.5 的"运气中值"语义是仓内约定（#14 裁定），文献无同数——保持预注册即可，不立缺陷。

## 6 完备性自评

六轴全查；checklist#1 专项闭环结论=已查无新漂移（分母链真源/回退/存量重算三件齐）。长尾：①Lo(2002) 原文 URL 未实证（限流），以公式机检锚自洽兜底；②真实生产 DSR 读数分布（多少行落 fallback/degenerate）无数据画像=缺项。运行时证据：近 3 日 logs 无本对象 error。
