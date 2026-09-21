---
ttl: task_bound
title: 深度审查作业簿——C4 DSR runner
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：C4 DSR runner（B17）

- 状态: **已审**
- 级别: P2｜类型: 管线
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/regime_validation/c4_deflated_sharpe_runner.py:62`（C4VariantDSR）/:86（run_deflated_sharpe_batch）
- 生产调用方：脚本消费真实存在=scripts/backtest/f06_e4_wfa_exam.py:259-264（单变体+外部台账 N）、c4_batch_screen.py:145,303-306（批级 modules 数-试点为 N）；src 内经 regime_validation/__init__.py 导出。[MATURITY]=design 与"封装+测试、真实跑批待排期"声明一致
- 测试文件: tests/backtest/test_c4_deflated_sharpe_runner.py（8 用例实跑全绿）
- 变更热力: 4 commits/3.5 月
- 备注: 零新计算声明核实为真——DSR 数学全委托 MOD-SIM-024（SSoT），本件纯编排

## 1 对象快照

- 审查范围：全文件 165 行——批输入清洗、逐变体 DSR 计算编排、最优变体裁定、批报告。
- 排除项：DeflatedSharpeCalculator 内部数学深审（MOD-SIM-024 他件对象）；本轮按"消费正确性"口径核其衔接（n_trial 读数、退化态、阈值语义）。
- 材料包缺项声明：c4_batch_screen 的台账落库记录未拉（脚本侧）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **DSR 折扣消费正确性（任务指定问）**：trials = n_variants if num_trials is None（:107-108），逐变体 `calc.calculate(rets, num_trials=trials)`——同批 N 变体共享同一 N 折扣，与 B&LdP "同一试验族统一折减"一致 ✓。**n_trial 台账读数口径**：默认=本批变体数；两个真实调用方均显式传台账 N（f06 传外部 num_trials；c4_batch_screen 用 len(results)-试点数且对历史行 dsr_num_trials 做一致性回收）——消费端实践正确；跨批/历史试验**不自动累计**（B&LdP 原意 N=研究全程全部独立试验数），memo §0.6.3 裁定口径背书下的已接受简化 | c4_deflated_sharpe_runner.py:96,107-108,124-125; f06_e4_wfa_exam.py:259-264; c4_batch_screen.py:300-306 | P2（已接受限制，防线=调用方约定） | 读三处；对照 Bailey & López de Prado 2014 §DSR 定义（SR0 项用全试验数） |
| A | 最优裁定按年化 Sharpe 降序取 [0]，passed=该变体 is_significant（:136-138,152-154）——"折减测最好的"是 DSR 标准用法 ✓。语义保留：同 N 下 DSR 最大者未必=raw Sharpe 最大者（V[SR] 随偏度/峰度/样本数差异），passed=False 时可能存在 DSR 达标的次优变体被掩盖——**保守方向**（不放过假显著），记录语义而非缺陷 | :136-154 | 通过（语义登记） | 构造两变体（高 Sharpe 厚尾 vs 低 Sharpe 薄尾）对照 |
| A | 内核衔接正确性：委托 DeflatedSharpeCalculator，其 DSR=Φ(SR/√V[SR]−E[max Z_N])、E[max] 用论文闭式（非渐近式）、峰度超额→Pearson +3 转换（SDC-3）、退化态 fail-closed dsr=0 不判显著（SDC-4）——**本轮抽查 SSoT 头部与内核函数，与论文口径一致** | deflated_sharpe_calculator.py:33-40,254-282,324-364 | 通过 | 读 SSoT 公式注释与机检锚点（iid 正态 V[SR] 边界） |
| B | 输入清洗 Fail-Closed：空 map/单变体<3 样本/含 NaN/Inf/num_trials<1 全显式抛 ZA-BT-0032 ✓（边界四问：空批✓单样本✓全 NaN✓零方差→委托层退化态 dsr=0✓） | :105-119 | 通过 | 单测覆盖 |
| B | **str(name) 键碰撞静默覆盖**：cleaned[str(name)]=... 使键 1 与 "1" 合并，后者静默覆盖前者，且 n_variants 取原始 len（:107）→ 报告 variants 数与实际计算数不一致、num_trials 相应虚高。Mapping 键通常为 str，实害低但属静默丢数据面 | :112-119,107 | P3 | `run_deflated_sharpe_batch({1: r1, "1": r2})` 观察 num_variants=2 vs variants 长度 1 |
| C | 输出消费方：C4BatchReport.passed → 11 号 memo §5 C4 统计显著性门（效果不显著=可能运气）+脚本落库（c4_batch_screen notes/num_trials 列）；爆炸半径=策略变体晋级裁定（当前人工审查轨） | :82,146-155; c4_batch_screen.py:67,152 | 说明 | — |
| D | 兄弟实现：全仓 DSR 三处（本件消费的 SSoT / overfitting_adjudicator / metrics.calculate_full_metrics）——SSoT 治理已在 calculator 头部声明"他处只准委托"（SDC-3/SDC-4 治理），本件零公式 ✓ 无口径分叉 | deflated_sharpe_calculator.py:22-40 | 通过 | grep 全仓 DSR 公式复写无 |
| D | 阈值语义：significance 0.95 / 运气中值 0.5 常量 SSoT 在 calculator（#14 裁定），本件 :139 读 config 默认而非复写 ✓ | :139; calculator:58-62 | 通过 | — |
| E | 五问：无静默失败（SimulationError 转抛带变体名 ✓）；幂等（确定性纯编排）✓；无时序/并发面 ✓；"假装已计费"风险由委托层退化态 fail-closed 兜住 ✓；**cherry-pick 攻击面**：调用方可只喂幸存者变体使 N 被低估——离线工具固有信任边界，靠人审+c4_batch_screen 台账行留痕缓解 | :124-127,105-119 | 说明（登记） | 读 c4_batch_screen 台账字段 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| DSR 多重比较修正本体 | **对等已有**：本件消费的 MOD-SIM-024 与 Bailey & López de Prado 2014 原文公式一致（含 2020s 社区修正：E[max] 闭式替代渐近式、非正态 V[SR]） | Bailey & López de Prado, "The Deflated Sharpe Ratio"（davidhbailey.com/dhbpapers/deflated-sharpe.pdf, JPM 2014）；SSRN 2460551（2014） |
| num_trials=全部试验数的台账纪律 | **对等已有且项目实践达标**：消费端教导"记录所有试过的变体"是 DSR 实施核心纪律（QuantDare/ML4 Trading）；本项目 c4_batch_screen 显式读台账 N、f06 显式传 N，本件默认=批内变体数是文档化简化 | ML4 Trading DSR 文档（ml4trading.io, 2020s）；QuantDare "Deflated Sharpe Ratio: how to avoid being fooled by randomness"（quantdare.com, 2018） |
| E[max Z_N] 闭式 vs 精确积分偏差 ≤0.045z | **对等已有（自 awareness）**：calculator 头部自带对拍偏差表，诚实标注"仍是近似"——优于一般开源实现 | deflated_sharpe_calculator.py:254-274 自证注释；Harvey-Liu-Zhu（2021, JF）多重检验族对照 |

## 4 缺陷清单

1. **P2（已接受限制+防线确认）｜num_trials 默认=批内变体数，跨批不累计**：B&LdP 口径 N 应为研究全程独立试验数；本件默认只覆盖本批，历史上多批筛选后的"最优"若按默认口径算会**折扣不足→DSR 偏高→假显著放行**。当前两个调用方均显式传台账 N（防线在），但默认值对未来的调用方是坑。
   - 现状→证据：:96,107-108 默认逻辑；f06:264、c4_batch_screen:303-306 显式传 N。
   - 影响与爆炸半径：变体晋级裁定（C4 门）——误放行假策略，非直接错账，P2。
   - 建议修法：num_trials 必填化（去默认），或默认改读 c4 台账行数；docstring 加"跨批必须传累计 N"警告。
   - 验证法：对比 num_trials=批内 N vs 累计 N 同一序列的 dsr 差（N 越大 dsr 越低，单调）。
2. **P3｜str(name) 键碰撞静默覆盖**（:112-119）：建议抛重或保留原名类型。
3. **P3｜passed 语义边角**：DSR 最大者与 raw Sharpe 最大者可能不同（保守向），建议报告同时披露 max-DSR 变体名。

## 5 挂起疑问

- MOD-SIM-024 的完整数学深审（V[SR] 非正态、track_trend 滚动窗）归属他件对象，本轮只做了消费正确性抽查（口径锚点核对通过）。
- c4_batch_screen.py:304-306 的 dsr_num_trials 回收逻辑（`if dsr_n: num_trials=dsr_n.pop()`）对多值集合只取其一的行为是脚本侧问题，未深查（脚本非本对象）。

## 6 完备性自评

- 六轴全查：A（折扣消费逐点验证+最优裁定语义）✓ B（清洗边界四问+键碰撞）✓ C（脚本消费方+台账列）✓ D（SSoT 三处委托关系）✓ E（五问+cherry-pick 信任边界）✓ F（3 条带源对照）✓。
- 长尾：MOD-SIM-024 全量数学（他件）；c4_batch_screen 台账 SQL 侧质量；真实跑批数据（memo §10.5 待排期）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 n_trial 默认口径+键碰撞: 挂起登记。B&LdP 2014 消费端纪律达标确认。
- 修复提交: q-0024（B11 冲击腿）。
