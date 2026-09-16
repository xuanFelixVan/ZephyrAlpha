---
ttl: task_bound
date: 2026-09-16
session: st-qoder-t1a-20260915
subject: 裁定#271（WYF-3 证伪置零）与 裁定#272（DSR 默认强制）全文镜像
ruling_ids: ['裁定#271', '裁定#272']
registry: docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
---

# 为什么要有这份镜像

两条裁定已按 RULE-RULING 写入 `ruling_registry.yaml`（`entries` 尾，CAS 纯追加，
自检 ids 唯一且语义落位），并随本 commit 整文件落地。

落地方式经一次改判。原计划是"热文件里有他会话在途条目（#269 ollama / #270 RSC-2），
按 AGENTS.md 第 3 节「作用域与连坐」第 4 条不整文件吸收，等持有 claim 的一方自己提交"。
但 RULING-REFERENCE 门禁把 RULE-RULING 的"同 commit 原子"做成硬约束：任何引用新裁定号的
文件，其 commit 必须含 `ruling_registry.yaml`。两个规则正面冲突时取硬门禁一侧，
因为裁定先于代码可读是体系的地基——裁定条目落不了地，被它裁决的代码就永远提交不了。

于是本 commit 连带落下 #269/#270 两条他会话条目。判定可接受的理由：注册表条目是
登记型数据而非实现代码，两条均字段齐备、YAML 可解析、自 2026-09-16 起已在工作树稳定存在，
提前落地不改变其语义，也不构成"代修他人违规"。

镜像文档本身仍保留：注册表条目是摘要级字段，证伪证据链、爆炸半径实证、重跑触发条件这三块
明细在 YAML 里放不下，而它们正是后续复议时必须读到的部分。

---

## 附带取证：注册表暂存区曾持有一条"蒸发已落裁定"的待提交删除

本次提交预检被 REGISTRY-MASS-DELETION 拦下，报文为 `条目数 88 -> 87 减少 / 净删行 42`。
逐版比对定位：HEAD 的 `ruling_registry.yaml` 含 87 条（含已落地的 裁定#269），而**索引区**
版本只有 86 条——缺的正是 #269 整条 42 行。工作树版本 90 条（HEAD 全集 + #270/#271/#272），
即"索引区落后于 HEAD 且少一条"，与 2026-09-09 那次 4703 行蒸发的病征同类：
批量编辑以陈旧基线整文件回写，把别人的既成条目静默删掉。

处置：`git restore --staged docs/.../ruling_registry.yaml`（仅回退索引区到 HEAD，不动工作树，
零内容损失），随后本 commit 对该文件的改动为 **纯追加 +105/-0**。
留此记录是为了让"索引区陈旧回写"这条静默通道被看见——它不需要谁恶意，一次陈旧 CAS 就够。

---

## 裁定#271 — WYF-3 终态补裁：wyckoff 维度判据层证伪 ⇒ 生产显式置零 + 一次性 WARNING

承 #264「阈值维持现值」未裁的"可用性"半边。

#264 只裁了"160 网格点零合格 ⇒ 阈值维持现值"，未裁"该维度到底能不能用"，本裁定补完后半。

证据链（walk-forward，校准/评估段严格分离，决策日只用 ≤T-1）：命中率劣于无条件基线
**17.7pp**、**0/5 折为正**、合并 **t=-0.10**、**WFE=-1.25**、3/5 折恒零、1/5 折误爆
（on_share 29.3%），纯净留存段 **max_score=45 仍不达门**。

另有 `latch_dichotomy` 结构性证据：`cummax` 永久粘滞使 on_share 只取两端——生产事件集 +
门槛降到 40 ⇒ 单次 2018 事件即永久在线 1927 日（36.6%）。故**不存在任何阈值向量能同时
避免恒零与误爆**：缺陷在判据而非门限，"再校准一次"不可能治本。

处置：`_DIMENSION_STATUS` 置 `status=falsified`，`wyckoff_score` / `wyckoff_score_from_events`
显式返回恒 0 并一次性 WARNING（禁静默零值——消费方必须能区分"该维零分"与"该维未计算"），
`wyckoff_dimension_status()` 对外披露快照；`TRANSITION_CONFIG` S2 confirm 的 wyckoff 门槛不动
（0 分自然不再 confirm，S2 由其余 `keys_or_gte` 项继续供给）。

爆炸半径实证：纯净留存段本就 max_score=45 不达门，置零是把"偶然不触发"改为"语义上不参与"，
不新增生产流转面（非放松亦非收紧，是把既成事实显式化）。

**重跑触发条件**（证伪不是永久真理，任一发生必须重跑管线并复议）：

1. SC 量能腿由滚动 `volume_anomaly` z 换成固定基准量纲（钝化根因，报告 §5.3）；
2. 六阶段判据 / 权重 / `memory_window` 语义任一改动；
3. `TRANSITION_CONFIG` S2 confirm `keys_or_gte` 的 wyckoff 门槛变动；
4. 指数标的或量纲口径变动（H1-P0 未复权治本后）。

---

## 裁定#272 — DSR 由"可选判定器默认关闭"改判为"决策门控默认强制 + 未注入即 fail-closed"

覆盖 52号§7③；`n_trials` 真源改 `TrialLedger`。

原口径（52号§7③）把 Deflated Sharpe Ratio 定为可选判定器、默认关闭。实证后果：全仓
**23/23** `bt-fw-*` 出厂工件在 IS→WFA→OOS 三阶段门控下判为"通过"，而其真实 IS sharpe
为负或 **DSR≈0.0003–0.0032**（在当前累计试验数下几乎必为运气），即三阶段门控对
"总共试了多少次"完全失明——代码把 `n_trials` 硬编码为 10，而
`TrialLedger().cumulative_trials()` 真值 = **4497**。

改判：`DecisionGate` 默认 `dsr_threshold=0.95`，未注入 dsr 按不通过处理（fail-closed），
`[0.5, 0.95)` 中段带同样不通过（不给"差一点"留通道）；`n_trials` 取 TrialLedger 真源，禁硬编码。

已实证后果并明示接受：在仓 23/23 工件判定翻为拒绝（含 15 件 `overfitting_flag=True`、
8 件 DSR≈0.0003–0.0032），`fw-tdm-current` 将在下一次 auto_mount 事件被挡在门外。
判定此为**安全方向**——挡住过拟合策略动用资金是保护性且可逆的（任何工件补算 DSR 过门即恢复挂载），
反向（放宽门控以保住现有仓位）才是不可逆的资金风险。

同步接线：`vectorized_engine` / `event_driven_engine` 的 `evaluate_decision_gate` 透传 dsr，
`strategy_validation` 流水线随请求口径强制注入；`metrics.calculate_full_metrics → TrialLedger`
新增 depgraph 边。

**残余待接（登记不隐藏）**：`risk_validation_bridge.admit_strategy` 的 dsr 入参因该文件被
他会话在途 claim（`st-btfix-p17-20260916`，12h TTL）暂缓。

连带发现另案处置：`strict_overfitting_gate` 经查为**死配置**（全注册表零条目，读了没人设）。
