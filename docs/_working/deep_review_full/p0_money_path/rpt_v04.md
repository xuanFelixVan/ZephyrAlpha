---
oid: V04
对象: N-trial 台账（TrialLedger，DSR 多重测试修正分母真源；漏记试验=DSR 虚高）
入口: src/zephyr/backtest/core/n_trial_ledger.py:179（TrialLedger）
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 本对象零漂移）
材料包: 源码+测试全读；churn；消费方 grep（metrics/c4_batch_screen/dsr_recalc_backfill/factory_grid_executor）；运行时证据=logs 抽查
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V04 N-trial 台账（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：TrialLedger（读/写/CAS L191-279、record_run L307、sync_screen_counts L361）+ compute_effective_rank L135-176 + REGISTRY_SKELETON。
- checklist#1（统计口径单点漂移——DSR 分母批内 N→累计 N 翻案）专项：本件即翻案后的真源落点；存量重算链已核实存在（scripts/backtest/dsr_recalc_backfill.py:229-243 经 cumulative_trials 重算）；下游 metrics._resolve_n_trials 优先账本、fallback 强制 dsr_degenerate=True+is_overfitting=True（metrics.py:351-355，S1-A4）——**口径闭环已查无新漂移**。
- 测试：tests/backtest/test_n_trial_ledger.py 17 用例（含 CAS 重试/幂等/11h 对齐回归钉），实测全绿。
- 变更热力：3 commits（f4d1ea4f42 A1 落库→654e58ac7b N_eff→cd4b4afd41 对齐修复）——修复型热区，方向健康。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | count 口径=screen_runs.total_trials+Σbatch_records，manual_population 只入 known_floor 不入 count（裁定边界）实现与文档一致 | n_trial_ledger.py:32-39,214-220 | 已查无 | tests:60-97 |
| A | **读数缺失静默记 0，违反自身 fail-closed 不变量（机验实证）**：`_count_of`/`snapshot` 用 `int(rec.get("n_trials") or 0)`——batch_records 中任一行 n_trials 为 null/缺失时**静默按 0 计入**，分母缩水→DSR 欠折减（放水方向）；而文件头不变量明写"数字口径读数缺失时 fail-closed（拒猜测）"（L12）。触发剧本：手编 YAML 漏字段/半截批量登记 | n_trial_ledger.py:12 vs 217-219,227 | **P2** | `int(None or 0)==0` 机验 + YAML 造一行 `n_trials:` 空值看 cumulative_trials 不抛错 |
| A | compute_effective_rank：外连接对齐+dropna 共同窗（11h 白跑根因已钉死）、特征值截负、熵广度 1e-9 规整后 ceil（浮点噪声防御）、clamp [1,N]——数学健全 | :135-176 | 已查无 | tests:181-229（含独立/全相关/短窗边界） |
| A | corr 矩阵 `fillna(0.0)`：零方差（常数收益）序列的 NaN 相关被当作**完全不相关**→系统性抬高 N_eff→折减偏狠（保守向，但语义应为"无法判定相关"） | :166 | P3 | 造含常数序列对拍 |
| B | 上游①：strategy_screen 证据行 SQL 带 `is_sharpe IS NOT NULL`（deferred_c4/未考行不计，裁定口径，测试钉死）；上游②：grid_*/summary.json 自动发现（evaluated→n_sampled 回退） | :385-417 | 见下 | tests:100-145 |
| B | **n_sampled 回退混口径**：evaluated 缺失时把"采样了"当"实跑了"计入 N——采样未评的格点不是一次试验；方向=多计→DSR 过折减（保守向，不放大放行），但口径漂移与 checklist#1 同族 | :407-410 | P3 | 造 summary 只有 n_sampled 对拍 |
| C | 消费方全列：metrics._resolve_n_trials（DSR 分母真源，钱闸核心）、c4_batch_screen:143/417（读+回写）、dsr_recalc_backfill:229-243（存量重算）、factory_grid_executor:745-747（set_effective_trials）。账本不可读时 metrics 强制退化态（fail-closed 已核）——**漏记试验仍是本件最大残余风险：SQL 只数 is_sharpe 非空行，台账外自研批量不落 summary.json 即漏计**（设计上以显式 record_run 补登兜底，依赖纪律） | metrics.py:240-260,351-355 | 爆炸半径=全部 DSR 判定 | grep 全列已核 |
| D | 双口径披露位 n_trials_raw/n_trials_effective 预注册（N=effective_rank 随批次 B 落地）；无兄弟重复实现（effective_rank 全仓唯一） | :28-30,283-305 | 已查无 | grep compute_effective_rank |
| E | CAS+10 次退避重试+YAML 预检+写后核读 ✓（热文件纪律合规）；无 sleep（永久模块铁律合规）；账本缺失读数 fail-closed ✓（cumulative_trials 抛 TrialLedgerError） | :247-279 | 已查无 | tests:148-166 |
| E | 静默失败面=上 P2（null→0）；其余路径响亮 | 同上 | 见上 | — |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| effective_rank（相关阵特征值熵广度） | 对等已有（谱系同源：特征值法估有效检验数是成熟家族，本件取熵广度变体）；立卡候选：与 Nyholt/Li&Ji 公式对拍 + Marchenko-Pastur 去噪后估计 | Nyholt (2004) Nature Genetics（特征值 Meff 开山）：https://www.nature.com/articles/6800717 ；poolR::meff 四法对照：https://search.r-project.org/CRAN/refmans/poolr/html/meff.html ；Bailey & López de Prado (2014) DSR 论文明载"非独立试验 N 应换有效试验数（聚类分析）"：https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 ——本件即该指引的落地 |

## 4 缺陷清单（按严重级）

1. **P2｜读数缺失静默记 0（违反自身 fail-closed 不变量）**：现状=`or 0` 吞掉 null 缺失；证据=n_trial_ledger.py:12 vs 217-219/227 + 机验；爆炸半径=DSR 分母（漏行→欠折减→放水方向，恰是历史事故方向）；建议=读数缺失抛 TrialLedgerError（或至少 warning+known_floor 披露），null 值应让 CAS 写入端拒绝；验证法=账本 YAML 手造 `n_trials:` 空值行，调 cumulative_trials 现不报错。
2. **P3｜n_sampled 回退混口径**：:407-410；建议=回退值带 provenance 标记（kind=n_sampled_fallback）披露位区分。
3. **P3｜corr fillna(0) 把不可判相关当独立**：:166；建议=常数序列计入 meta 并降 N_eff 或标 boundary。

## 5 挂起疑问

- 台账外自研批量的"漏计"残余风险依赖 record_run 纪律——是否值得加"strategy_screen 行数 vs 台账读数"周期对账告警（事件触发），转挖矿子节点。
- n_trials_effective 披露位目前单值覆盖语义（最新批次），跨批次比较需读 previous 链——够用与否待批次 B 实战判。

## 6 完备性自评

六轴全查。长尾：①真实账本 YAML 现值未读（生产读数口径未实证，审查者只验机制）；②CH strategy_screen 真实行数与台账读数的偏差（漏计率）无数据画像=缺项。运行时证据：近 3 日 logs 无本对象 error。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 or-0 fail-open: 确认→治本(缺 n_trials raise)+回归。复检 28/28。
- P3 corr fillna(0) 语义: 挂起登记。
- 修复提交: 队列 q-20260918-st-deeprev-20260918-0007。
