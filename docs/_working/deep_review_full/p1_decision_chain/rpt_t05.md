---
ttl: task_bound
doc_type: report
title: 深度审查报告——前向回测窗口/指纹（T05）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：前向回测窗口/指纹（T05）

- 状态: **已审**
- 级别: P1｜类型: 决策链回测验收闸
- 基线 commit: 2fa92002c3（工作树 bf65648609；基线后仅 docstring 变更 +3/-2@:180-182，代码锚点在 :182 之前双有效、之后 HEAD=基线行号+1——本报告锚点按 HEAD 标注）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/strategy_pipeline/fw_backtest.py:132(plan_fingerprint)/:790(_idempotent_skip)/:951(run_fw_backtest_due)`
- 生产调用方: scripts/backtest/auto_mount.py（挂图后 emit_fw_backtest_due）；CLI run；**下游 promotion_advisory.py:154 消费 latest.json（证据③）**
- 测试文件: tests/strategy_pipeline/test_fw_backtest.py（24 用例）
- 任务备注核验：":416 已知带 max_drawdown"——属实，fold 证据带 max_drawdown 且已喂 DecisionGate（:416/:476），在位无缺
- 材料包缺项: 引擎侧 run_framework_backtest 内部（禁改车道，另域）；walk_forward.split 内部数学信任既有件

## 1 对象快照

- 范围：指纹幂等闸、PIT 标的池组装、regime 日序供给、四道验收闸（风险/三段门控/组合完整性/现金闭合）、护栏降级账（H5-D）、事件 emit 消费环。排除：framework_composer/决策门 DecisionGate/DSR canonical（各自真源对象）。
- 变更热力：2026-09 一线演进（S11 断桥③桥件），任务备注确认 :416 已知带 max_drawdown。
- 测试覆盖概况：24 用例，负路径覆盖强（幂等键缺一即重跑×3/DSR 单源/门槛否决/护栏计数/生成器失败）；**窗口推进×指纹不变的幂等误跳场景无测**（P1-1 漏测点）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **滚动窗口×指纹幂等=证据窗冻结（P1）**：指纹=成员权重+tdm_sha12，**不含 start/end 窗口**（:132-150）；默认窗=滚动 12 个月 date.today()（:165-169）；幂等闸只比指纹+四闸键（:790-805）——TDM/权重不变时自动路径恒 skip，latest.json 窗口停在末次变更日。:980-981 注释"同指纹重跑结果必然逐位同——面板由同窗口同数据决定"前提在滚动窗下为假（窗口日日在变） | fw_backtest.py:132-150, :165-169, :790-805, :980-992 | **P1** | force=False 连续两日各跑一次（隐含窗口不同），第二次返回 skipped=true |
| A | 指纹输入面窄（同族 P2）：不含 framework_plans.yaml 全文（仅正则抽 source_sha256_12，缺失时=空串参与哈希 :143-144）、不含引擎/面板代码版本、不含数据版本——引擎修复或数据修正后同指纹照跳 | fw_backtest.py:138-149 | **P2** | 改引擎非权重文件后重跑观察 skipped |
| A | 三段门控证据口径=锁定账簿时间切片（非拟合 IS/OOS），IS/折切片边界清楚：IS=[0:seg]，折 test 互斥其后，OOS 含末段残样——全部自我披露（:377-381, :419-433 docstring+scheme），数学上诚实 | fw_backtest.py:392-434 | 已查无（自白面） | — |
| A | `_GATE_MIN_SEG_SAMPLES=61`=metrics.MIN_SAMPLES_FOR_SHARPE+1——实测 metrics.py:51 MIN_SAMPLES_FOR_SHARPE=60，引用属实（禁魔数声明兑现） | fw_backtest.py:383-385; metrics.py:51 | 已查无（正面） | grep 对照 |
| A | DSR/n_trials 单源复算：产物缺键→净值重算（同一 calculate_full_metrics+账本），失败=fail-closed 拒——与 P0 四闸同源不另造口径 | fw_backtest.py:323-366 | 已查无（正面） | tests:287 单源测试在位 |
| A | 换手 NaN 判定 `turnover==turnover`（:616）、组合完整性/现金闭合"无披露=拒"（:519-528, :568-575）——缺证据 fail-closed 方向一致 | fw_backtest.py:616, :519-528, :568-596 | 已查无（正面） | — |
| A | A 股口径：标的池 SCD-2 窗口并集（含期内调出/退市，旧 valid_to IS NULL 口径实证 300→331 差 9.4% 幸存者偏差已废）+涨跌停 PIT 提供器开关披露——反幸存者偏差机制在位且带量化披露 | fw_backtest.py:172-227 | 已查无（正面） | disclosure.since_exit_share 证据包可见 |
| A.3 | 24 用例覆盖幂等四闸缺键重跑/DSR 单源/护栏计数/组合阈值单源；缺"窗口推进仍 skip"负例（P1-1 的测试面） | test_fw_backtest.py:164-430 | P2（与 P1-1 同根） | 补两日窗口用例即红 |
| B | 上游：生成器 rc≠0=RuntimeError 留 journal 重试（瞬时）；CH 查询 get_client_strict；regime 加载失败→静态降级+披露不阻断（:291-293）——断供行为三态齐全 | fw_backtest.py:1055-1070, :274-293 | 已查无 | — |
| B | `_assert_iso_date` SQL 拼接前置闸（payload 外部可填 start/end）——注入面已封（:119-127）；SQL 全参数内插但日期已验、表名常量 | fw_backtest.py:119-127, :192-198 | 已查无（正面） | 喂 start="1' OR 1=1--" 观察 raise |
| C | 下游爆炸半径：promotion_advisory 读 latest.json 作证据③→晋升建议链——P1-1 的陈窗证据直接进晋升链输入；证据包写失败=RuntimeError 留档重放（:1073-1089） | promotion_advisory.py:153-173 | P1（并入） | 读 latest.json 窗口字段 vs 今日 |
| D | 证据消费双路径：latest.json 优先、退 glob 最新 fw-auto-*.json（promotion_advisory:154-156）——latest 写失败时退档语义=次新证据，可接受 | promotion_advisory.py:153-173 | 已查无 | — |
| E | emit 环：journal 先落→子进程消费→rc=0 出队/失败 attempts+1 毒丸告警（:1141-1196）——事件不丢语义兑现；但 `pe._rewrite` 与 drain 主环并发无锁（旁路消费 vs 调度 drain 同文件互写）→丢更新窗口（本班受"禁改 pipeline_events"约束的已知权衡） | fw_backtest.py:1169-1196 | P3 | 并发 drain+emit 压测 journal 行数守恒 |
| E | 护栏降级日志观测的诚实声明：引擎改文案→count=0="未听见非健康"（:774-779 note）——静默失败面已显式登记为语义边界，非缺陷但须 Owner 知悉 | fw_backtest.py:645-662, :774-779 | 已查无（自白面） | — |
| E | 证据落盘时间戳命名+fp8，latest 覆写无 CAS——同秒同指纹双跑互覆；事件链串行使窗口实际关闭 | fw_backtest.py:1073-1089 | P3 | 同秒双跑目录比对 |
| E | 幂等跳过路径不落任何新证据/不 touch 窗口字段——跳过事实只在返回值（:986-992），journal 出队后无持久跳过痕迹（审计断档） | fw_backtest.py:984-992 | P3 | 跳过后查 EVIDENCE_DIR 无新件 |

## 3 SOTA 对照

1. **walk-forward vs CPCV（立卡候选）**：本对象三段门控=单路径锚定 walk-forward 的时间切片退化考核。学界口径：单路径 WFA 仅检验一条历史路径，CPCV（combinatorial purged CV）以多路径+purgin+embargo 显著降低过拟合漏检——López de Prado《Advances in Financial Machine Learning》（Wiley，2018；实现汇编 https://github.com/Neyt/How-To-Backtest-Correctly）；实证对比 Arian, Norouzi & Seco《Backtest Overfitting in the Machine Learning Era》（SSRN 4686376，2024，https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376；正式版 Knowledge-Based Systems 2024，https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110）。**立卡理由**：本模块已诚实声明锁定账簿口径并登记 fit-window IS 欠账，CPCV 可作后续真 fit-window 评估的多路径升级——登记挖矿子节点，非立即可改。
2. **滚动窗口+幂等的正确组合（驳回现状）**：业界调度型回测（skforecast backtesting 指南，https://skforecast.org/0.15.1/user_guides/backtesting.html）以**固定 refit 窗口或窗口指纹进幂等键**——本对象指纹缺窗口正是 P1-1 病根，属偏离业界常规，判"立卡即改"（修法见缺陷 1）。
3. **引用勘误（checklist #15 同族，交叉 T02）**：bh_fdr.py:26 把 "SSRN 4686376" 挂在 "Harvey & Liu 2020" 名下——该 SSRN 号实为 Arian et al. 2024 CPCV 论文（见上），Harvey & Liu《Backtesting》实为 JPM 2015。引用错挂=文档级 P3，两报告同记。

## 4 缺陷清单

1. **[P1] 滚动窗口不在指纹内→自动路径证据窗冻结**
   - 现状：fingerprint=权重+tdm_sha12（:132-150），默认窗滚动 12 个月（:165-169），幂等闸不比窗口（:799 仅比 fingerprint）。
   - 证据：:980-981 注释前提"面板由同窗口同数据决定"在 date.today() 滚动窗下日日为假；promotion_advisory.py:154 消费 latest.json。
   - 影响：TDM/权重稳定期整装证据停在末次变更日的窗口，晋升建议器持续引用陈窗组合证据=决策系统性偏移（不报错只偏）。爆炸半径：sim→production 晋升链的证据③输入。
   - 建议修法：指纹加入 window（或 acceptance 记录窗口、幂等闸加"窗口相同"判据；或固定窗 refit 语义）。
   - 验证法：两日连跑非 force，第二次 skipped=true 即复现。
2. **[P2] 指纹输入面不含 plans 全文/引擎版本/数据版本**——证据 ：138-149；影响：引擎修复/面板修正后同指纹照跳（陈证据延续）；建议：source_sha256_12 缺失时禁幂等（fail-closed）+引擎侧 run_id/代码版本进证据；验证法：抽掉 plans 的 sha 行重跑。
3. **[P3] journal 旁路消费与 drain 并发无锁**（:1169-1196 vs pipeline_events drain）——建议：收口时把 fw_backtest_due 注册进分派表消除旁路（docstring 已预留）；验证法：并发压测。
4. **[P3] 幂等跳过无持久审计痕迹**（:984-992）——建议：跳过也追加轻量 evidence 或 journal 回执留痕；验证法：跳过后查目录。
5. **[P3] bh_fdr SSRN 引用错挂**（bh_fdr.py:26）——建议：改引 Arian et al. 2024 与 Harvey & Liu 2015 JPM 分列；验证法：SSRN 4686376 页面标题对照。
6. **[P3] latest.json 覆写无 CAS**（:1085-1088）——建议：safe_write_text 带 expected sha 或接受串行化前提注释；验证法：同秒双跑。

## 5 挂起疑问

1. 窗口语义 Owner 裁定：固定窗（如 2025-09~2026-09 冻结）还是滚动窗必须逐日重跑？两者成本/新鲜度权衡不同，P1-1 修法取决于此。
2. `_gate_fold_evidence` 的 IS 段与首个 fold 的 train 窗口重合（IS=[0:seg]）——DecisionGate 侧是否知晓"IS 非拟合样本"并相应放宽 is_stage 判据？需 DecisionGate 对象复核（另一域）。
3. ensure_regime_snapshot 的调度挂点（docstring 登记两方案）尚未落地——regime 日序供给实际由谁续期？

## 6 完备性自评

- 六轴全查：是。A（指纹四问/切片边界/常量引用实证/NaN 边界）、A.3（24 用例映射+漏测点指认）、B（生成器/CH/regime/SQL 注入面）、C（promotion_advisory 消费链实证）、D（latest 双路径）、E（事件环/审计断档/落盘竞态/观测语义五问）。
- 长尾：①WalkForwardAnalyzer.split 内部（信任既有件）；②DecisionGate 阈值本体（P0/独立对象）；③run_framework_backtest 引擎内部 fail-open 4 处只经日志观测未逐点核（禁改车道）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
