---
ttl: task_bound
volume: 92_coverage_triage_20260926
session: st-ailayer-final-20260924
creation_token: fullflow-w4a-coverage-triage-20260926
---

# 92 覆盖分诊册（W4-A 车道 · 机生对账尺 22 未覆盖环节逐格定性）

> 工作面=worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`；零提交零入队。
> 尺=`00_skeleton/91_machine_crosscheck.yaml`（生成器 `scripts/governance/fullflow/generate_fullflow_crosscheck.py`）。

## 〇、尺的判据（先说清它按什么 grep，作为定性基准）

`build_coverage()`（生成器 592-650 行）逐 F 环节判"覆盖"：
- 扫描 `docs/_working/fullflow_mining/**/*.md`，**排除** `NON_WORKBOOK_RELS`（总册/分工册/90交叉验证/91机生/指挥册/裁定册/编排/05_missing_p0/91_notes）；
- 一个 F 号算"covered" ⟺ 该号 **字面出现**在任一非排除簿的正文（`F\d{2,3}` 大写）**或**文件名（`_f\d{2,3}_` 小写）；
- ⇒ "uncovered" = 全仓作业簿正文+文件名都没写过这个 F 号，**不代表没有承载件**，只代表没挂锚。这正是本分诊要二分的地方。

## 一、22 格逐环节二分定性表（每格两证：尺判据 / 实际承载件）

| F | 环节 | 定性 | ①尺判据（为何判未覆盖） | ②实际承载件（路径 / file:line） | 承载充分度 & 该不该放宽尺 |
|---|------|------|------------------------|-------------------------------|--------------------------|
| F09 | 备份 3-2-1 双链 | 有簿未挂锚 | 全簿正文无"F09"字面 | `m5_scheduling/补挖波_20260925/03_backup_coldstore.md` §一（backup.ps1 六 STAGE+CH 双链） | 充分；锚补该册 |
| F62 | 合规门与程序化报告 | 有簿未挂锚 | 无"F62"字面（06 册正文用"C-002/ReportGate"未写号） | `m7_live_execution/06_compliance_gates.md` §一 | 充分；锚补该册 |
| F64 | 回测三件套(universe/benchmark/cost_model) | 有簿未挂锚(部分) | 无"F64"字面 | `m2_backtest_sim/05_cost_gates.md`(cost_model 门)+`02_backtest.md`(回测入口契约) | 半充分：cost 侧充分，universe7/benchmark9 册号未在 m2 明挖；**建议另派三件套注册表取证工单**，不放宽尺 |
| F68 | GPU 矩阵/工厂格子 | 有簿未挂锚 | 无"F68"字面 | `m2_backtest_sim/04_gpu_matrix.md` §一（factory_grid_executor 三层矩阵） | 充分；锚补该册 |
| F69 | T0/成本门/IBT | 有簿未挂锚 | 无"F69"字面 | `m2_backtest_sim/05_cost_gates.md`+`06_ibt_backtest.md` | 充分；锚补 05 册 |
| F77 | 数据调度常驻(integrator/tick/槽位) | 有簿未挂锚 | 无"F77"字面 | `m1_data/01_ingest.md` §一+§二(自动化触发行 23：DataScheduler/TickSubscriber 常驻+29 槽位) | 充分；锚补该册 |
| F78 | belt daemon 提交传送带 | 有簿未挂锚 | 无"F78"字面 | `m5_scheduling/02_inrepo_daemons.md` §一（commit_belt_daemon 专章） | 充分；锚补该册 |
| F83 | 自动化班底(双引擎两班制) | **真缺簿** | 无"F83"字面 | 仅 `m6_frontend/补挖波_20260925/04_reporting.md`/`m8_bottlenecks/…/f122`**顺带**提"双引擎"，无专册挖 automation_crew_policy 九席排班 | 缺六向→待派取证；不开假簿 |
| F87 | AI 红线 negative_list/年审 | 有簿未挂锚 | 无"F87"字面 | `m4_ai_layer/01_ai_layer_six_families.md` §8 redline（NL-1..6/三 gate 149/150/151） | 充分；锚补该册 |
| F89 | 本地模型与嵌入(ollama/router/reranker) | **真缺簿** | 无"F89"字面 | 四张 capability_card + `m5_scheduling`排程**顺带**，无专册统挖"模型源族" | 缺六向→待派取证；不开假簿 |
| F97 | commit 侧门禁链(引用不重挖) | 有簿未挂锚 | 无"F97"字面 | `m3_governance/01_runtime_guards.md` §一(边界行 8-9)+`04_coverage_gaps.md` §一——**本战役显式声明引用外部 commit_speedup 战役 23 环节/115 子环节** | 簿在他营（fullflow_mining 外）；锚补 01 册以登记引用面；尺判"未覆盖"对 fullflow 面成立，勿放宽 |
| F98 | GateEngine 运行时门禁 | 有簿未挂锚 | 无"F98"字面 | `m3_governance/03_registry_families.md` §三/§四(gate 三册 91/102/180)+`04_coverage_gaps.md` | 充分；锚补 03 册 |
| F99 | 漂移检测(gov_drift 30 检测器/双 watchdog) | 有簿未挂锚(邻接) | 无"F99"字面 | `m3_governance/02_reconcilers.md` §三(drift_* reconciler)+`01`(worktree_drift_watchdog)——**注意 gov_drift/ 30 检测器本体未被专挖** | 邻接：post-commit 漂移对账有簿；检测器本体缺→锚补 02 册并**派 gov_drift 本体取证工单**，不放宽尺 |
| F100 | 红蓝对抗(adversarial_validation) | **真缺簿** | 无"F100"字面 | 仅 `04_knowledge_supply/f36`/`m2/06`顺带"红蓝"字样，无专挖 adversarial_validation 包 | 缺六向→待派取证；不开假簿 |
| F103 | 代码质量与克隆守卫(clone_guard) | **真缺簿** | 无"F103"字面 | 全簿零命中（宪法提及但无作业簿） | 缺六向→待派取证；不开假簿 |
| F104 | 会话并发治理(session_concurrency/lock) | 有簿未挂锚 | 无"F104"字面 | `m3_governance/01_runtime_guards.md` §3.6（SessionRegistry/session_concurrency.py:295/lock_files） | 充分；锚补该册 |
| F105 | 密钥治理(secrets.py 三道 gate) | 有簿未挂锚(邻接) | 无"F105"字面 | `m3_governance/04_coverage_gaps.md` §三(密钥门+secret_registry_drift)+`02`(reconciler)；secrets.py 生命周期本体未专挖 | 邻接：门+事后对账有簿；生命周期本体缺→锚补 04 册+**派 secrets 生命周期取证** |
| F106 | 术语三层翻译体系 | 有簿未挂锚 | 无"F106"字面 | `m3_governance/03_registry_families.md` §四(术语/域/模块三册 279/94/7776) | 充分；锚补 03 册 |
| F107 | 回滚恢复(infrastructure/rollback 四级) | **真缺簿** | 无"F107"字面 | `m7/02_kill_switch`/`04_知识总述`顺带"rollback"(异对象)，rollback 包本体无专册 | 缺六向→待派取证；不开假簿 |
| F108 | 人机门位(risk_tier 18 条四类) | 有簿未挂锚 | 无"F108"字面 | `m3_governance/03_registry_families.md` §四(risk_tier 门位册)+宪法 §5 | 充分；锚补 03 册 |
| F114 | 通知路由(notification_router/OpsAlert) | 有簿未挂锚 | 无"F114"字面 | `m6_frontend/02_api_server.md`（`/api/ops-notifications` :4423 OpsAlertFeed 通知唯一前端出口） | 充分；锚补该册 |
| F116 | SOP 方法论族(九族真源) | **真缺簿** | 无"F116"字面 | 各簿顺带引用 sop/ 路径，无专册挖九族方法论本体（横切元层） | 缺六向→待派取证；不开假簿 |

### 计数汇总
- **有簿未挂锚＝16 格**（补锚后从 uncovered 消失）：F09 F62 F64 F68 F69 F77 F78 F87 F97 F98 F99 F104 F105 F106 F108 F114。
- **真缺簿＝6 格**（保持 uncovered，不开假簿）：F83 F89 F100 F103 F107 F116。
- **尺误判＝0**——本尺"字面 F 号 grep"判据自洽，未覆盖=确无锚，非尺 bug；差异全在"承载件未写号"，属补锚可解，不需放宽尺判据。
- 13 个承载册完成补锚（F97+F104 同入 m3/01；F98+F106+F108 同入 m3/03；F69+F64 半面同入 m2/05）。

### 补锚后尺实测（本车道重跑）
- `uncovered`：补锚前 **22** → 补锚后 **6**（`covered` → 116）。
- 剩余 uncovered_ids 恰＝{F83 F89 F100 F103 F107 F116}＝真缺簿集，无假绿。
- 防自造假绿：本分诊册正文枚举全部 22 F 号，若被尺当作业簿扫会把 uncovered 直接判 0；已按 `90_crosscheck_link_census` 同法在生成器 `NON_WORKBOOK_RELS` 登记为**非作业簿面**（只加排除条目，未动 grep 判据/阈值）。

## 二、补锚动作清单（最小改动：仅在 §一 补一句"本册覆盖 Fnn"，禁改正文/结论）

| 册（绝对路径略前缀 `docs/_working/fullflow_mining/`） | 补入的 F 锚 |
|---|---|
| m5_scheduling/补挖波_20260925/03_backup_coldstore.md | F09 |
| m7_live_execution/06_compliance_gates.md | F62 |
| m2_backtest_sim/02_backtest.md | F64 |
| m2_backtest_sim/04_gpu_matrix.md | F68 |
| m2_backtest_sim/05_cost_gates.md | F69 |
| m1_data/01_ingest.md | F77 |
| m5_scheduling/02_inrepo_daemons.md | F78 |
| m4_ai_layer/01_ai_layer_six_families.md | F87 |
| m3_governance/01_runtime_guards.md | F97 F104 |
| m3_governance/02_reconcilers.md | F99 |
| m3_governance/03_registry_families.md | F98 F106 F108 |
| m3_governance/04_coverage_gaps.md | F105 |
| m6_frontend/02_api_server.md | F114 |

（F64/F99/F105 为"邻接/部分充分"锚——补锚只承认册内**已实挖子面**，未挖本体另列取证工单，见 §四。）

## 三、真缺簿处置（6 格，一律**不开假簿**）

> 关键反假绿逻辑：作业簿一旦落盘且正文写 F 号，尺即判该格 covered。故对未挖干的 6 格**先开占位/待挖簿＝自造假绿**（把"其实没承载件"洗成"已覆盖"）。唯一诚实态＝保持 uncovered，直到六向齐证后由取证车道开真簿。此即本车道**不**为其开册的理由，非偷懒。

按任务"挖干判据=六向每向有实证；缺任一向判待挖"+宪法 §4 内收判据，6 格在落盘窗口内**未取得六向齐证实物**，故不套模板开簿（开=虚报挖干，比不报更糟）。逐格缺向：

- F83 自动化班底：缺"自动化触发/门禁与质量尺"向——automation_crew_policy.md 九席排班与 automation_master_plan 无 file:line 级对账实证。
- F89 本地模型与嵌入：缺"上游/下游/门禁"向——四张 capability_card 是消费画像，未连到 router/reranker 调度码路径。
- F100 红蓝对抗：全六向缺——adversarial_validation 包（53 场景/44 条款）零作业簿。
- F103 克隆守卫：全六向缺——clone_guard/code_dedup 包零作业簿（宪法硬规则却无簿）。
- F107 回滚恢复：全六向缺——infrastructure/rollback（双轨 checkpoint/四级/G0 自愈）零作业簿。
- F116 SOP 方法论族：全六向缺——横切元层，无专册。

## 四、派单建议（待总筹裁，本车道不自裁裁定号）

1. **三件套注册表取证工单**：universe_registry/benchmark_registry 的"每测 MUST 指定"执法面（F64 缺的半面）。
2. **gov_drift 30 检测器本体取证**（F99 邻接外的本体面）。
3. **secrets.py 生命周期本体取证**（F105 本体面）。
4. **四枚零簿子系统**（F100/F103/F107/F89/F83/F116）各派一挖矿车道开六向簿。

## 五、改尺建议（**不放宽判据**）

尺的 `build_coverage` 判据（字面 F 号 grep）自洽、无误判，**不动**。可选增强（留总筹裁）：
- 在 coverage_matrix.definition 追加一条"承载件邻接面"观测项（记 file:line 但**不计入 covered**），使"F64 半充分/F99 邻接"这类可被机械区分，而非仅靠人读分诊册。此为**加观测面不改判据**，无假绿风险。

## 六、复核命令

```bash
# 补锚后重跑尺（本车道已跑，见 §七计数）
python scripts/governance/fullflow/generate_fullflow_crosscheck.py
# 只看未覆盖清单
python -c "import yaml;d=yaml.safe_load(open('docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml',encoding='utf-8'));print(d['coverage_matrix']['totals']);print(d['coverage_matrix']['uncovered_ids'])"
```
