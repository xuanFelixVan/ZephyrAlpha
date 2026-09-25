---
ttl: task_bound
volume: 03_promotion_gate
session: st-ailayer-fullflow-pr-b
creation_token: fullflow-prb-f74-gate-20260925
---

# 03 · F74 转正建议书汇总器（全链唯一人工门）

## 一、环节定义与判定修正

总册口径：F74=四件产出→一页报告+组合门打分=全链唯一人工门，状态 **missing（汇总器缺位=全流通最大单点）**。
本册实证修正（2026-09-25 挖矿当日复核）：**missing 判定过时**。汇总链四件在 09-15~09-18 已由 S12 C4（promotion_advisory MOD-BT-199）+L2（promotion_combo_gate MOD-AUTO-L2-001）+C5/S13 前后端两端点交付，campaign 挖矿簿 `docs/_working/automation/campaign/mining/08_模拟盘转正门/工段作业簿.md` §9 已判 8.5 转正门"挖干封矿"。现态=**partial**：件齐链通，但①零运行实证（处女链）②combo gate 未切 v2 frozen 尺③无事件入口④带外通知缺位（详见 §五）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | 四路证据全只读：①SCR-SIMGOV 治理档案 `data/backtest_artifacts/runs/SCR-SIMGOV-*/04_wide/sim_governance_advice.json`（实测 46 runs，最新 09-25 02:52，2 条 sim 态策略 recommendation 均=null 观察期不足）②SCR-DEV 月度偏离（最新 09-25 02:52）③整装证据 `data/backtest_artifacts/fw-auto/latest.json`（在盘；fw 文件最新 09-16）④sim_memo 月档 `docs/_working/pipeline-research/sim-memos/sim-memo-202609.json`（在盘，两策略 stats.error=CH TCP 不可用带伤）；PA-1 三条件实据源：strategy_screen §8 双窗（screen_source.fetch_bothwin）/intake 批报告 fdr_keep（`docs/_working/pipeline-research/reports/intake-*.yaml` 最新 09-25）/衰减台账 `data/runtime/strategy_decay_ledger.json`（574 行全 probation，09-21） |
| 下游消费 | pipeline_events OPTIONAL_DUE_KINDS（pipeline_events.py:173-175 挂 run_promotion_advisory_due）；组合门 promotion_combo_gate 消费 advisories/*.json（I1）；api_server GET /api/promotion-advisories（:4329）+POST /api/promotion-decide（:4375，注释自证"第四获准写端点"）；前端 #promotion 页拍板；**拍板后** FSM sim→production →注册表 lifecycle → daily_decision_orchestrator S4"已毕业包集"（现 v1 包集=空→安全态，裁定#305 第 2 点）——这是转正真正流入交易日的消费端 |
| 自动化触发 | sim_governance._emit_promotion_advisory_event（sim_governance.py:133，**仅当存在 promote/demote 建议才 record+drain**）；实测 `.runtime/strategy_pipeline/pending_events.jsonl` 中 promotion_advisory_due 计数=**0（事件从未入队——两 sim 策略月判均 null）**；combo gate=CLI 手动无事件入口；上游 PaperSession 任务实测 Ready+09-24 09:25 exit 0（NextRun 09-25 09:25）——**M2 册"DISABLED→Ready 转换无登记"疑点本日实证：任务已启用且日跑绿**；SimBridgeExecute 09-24 LastResult=4294770688（M5 S3 断链仍活，归 M2/M5 车道） |
| 真源与注册表 | strategy_registry.yaml（163 条目；schema:58 注释八态词表 candidate/backtest/sim/paper/live/monitoring/decayed/retired；实测 sim 态 2 条）；config/standards.yaml（STD-SIM-ACCESS-001 v1 frozen+suspect 注记 :10-23；**STD-SIM-ACCESS-002 v2 frozen 2026-09-18 裁定#337，E6 双尺重考达标 81 覆盖/55 翻转零不可解释**）；campaign 簿 mining/08+blueprints/promotion_combo_gate_blueprint.md；裁定#305/#306/#315/#337/#365；骨架 v1.1 §1⑧/§4 P0/§7/§8 |
| 门禁与质量尺 | PA-1 晋升预授权 fail-closed：三条件（双窗/BH-FDR/无未决衰减）逐条 {ok,reason,source} 落台账，缺证=拒绝且**不写 decision 墓碑**（可重试）；token 三态校验（:576，未配置=全拒 fail-closed，常量时间比对）；KillSwitch 探针（:594 非 normal=拒）；注册表 CAS 手术+术后语义复核（:531/:549，仅目标条目两字段可变）；建议包幂等同日覆盖、hold 不产包、已决重复 decide 拒绝；建议≠决定双保险（combo INVARIANTS+Owner 门）；v1 尺 suspect（#306：DSR>0@N=4562 需 SR≥2.68 与 OOS≥1.5 数学互斥） |
| 当前运行状态 | **黄（件绿链未转）**：四件代码+测试全在（tests/strategy_pipeline/test_promotion_advisory.py、tests/backtest/test_promotion_combo_gate.py）；但 `data/strategy_intake/promotion_advisories/` 目录**不存在**（零建议包）、promotion-reports/ 空（combo 从未跑）、journal 0 事件——全链自 09-15 建成后**零实弹**；黄因=处女链+v1 尺硬编码，非断链 |

## 三、子模块清单（4 件）

| # | 子件 | 入口 file:line | 状态 |
|---|---|---|---|
| 3.1 | 建议包生成器（四路证据合流+词表兜底）：governance promote_paper→promote/demote_decayed→demote；缺治理建议按月度判定史兜底（pass≥2∧breach=0→promote；breach≥2→demote；hold 不产包） | promotion_advisory.py：证据①-④读取 :116/:129/:152/:177；兜底 _decide_recommendation :378；build_advisories :415（hold 跳过 :428） | 绿（代码+测试） |
| 3.2 | 事件入口：OPTIONAL_DUE_KINDS 契约 run_promotion_advisory_due→生成建议包+promote 包经 Alerter 推送（飞书已裁撤→实际落 data/failures/+前端 ops-notifications 横幅）；发射方=sim_governance 治理建议产出后（仅 actionable recs） | promotion_advisory.py:445；pipeline_events.py:173-175；sim_governance.py:133-144 | 绿（接线在）/黄（零触发实证） |
| 3.3 | 组合门打分+一页报告：四条腿（OOS Sharpe≥1.5/回撤≤15%/容量≥30 笔成本计提/DSR>0）→promote_ready/reject/borderline 三态；render_report 一页 markdown | scripts/backtest/promotion_combo_gate.py：THRESHOLDS 硬编码 :56-61、score_candidate :139、render_report :178、OUT_DIR=promotion-reports/ | **partial**：仍钉 v1 尺（v2 已 frozen 未切）；缺 v2 第三腿（ρ̄≤0.7/capacity/turnover 12×）；无 suspect 注记（WO-08-04）；无事件入口 |
| 3.4 | Owner 拍板执行器：decide=token 校验→KillSwitch→FSM 流转（promote 须先 PA-1 实据过 candidate→sim）→注册表 CAS→decision 台账（token 指纹）→回执；HTTP 投影两端点+#promotion 页（approve/reject 按钮+decision badge+运营横幅） | promotion_advisory.py:655（_token_check :576/_kill_switch_clear :594/_transition_lifecycle :614/CAS :549/台账 :723/回执 :733）；api_server.py:4329/:4375；web/features/promotion/promotion.js | 绿（代码+前端+端点全在） |

## 四、运行证据（挖矿当日实测 2026-09-25）

```text
ls data/strategy_intake/promotion_advisories/          # 不存在 = 零建议包
grep -c promotion_advisory_due .runtime/strategy_pipeline/pending_events.jsonl   # 0
cat data/backtest_artifacts/runs/SCR-SIMGOV-20260925-025209/04_wide/sim_governance_advice.json
# → 2 entries（STR-E-TIMING-001 月判0 / STR-VREV-025 月判1），recommendation 均 null
Get-ScheduledTaskInfo ZephyrAlpha_PaperSession    # LastRun 09-24 09:25 Result=0（已启用）
Get-ScheduledTaskInfo ZephyrAlpha_SimBridgeExecute # LastRun 09-24 13:05 Result=4294770688（M5 S3 仍断）
python -c "json.load(open('data/runtime/strategy_decay_ledger.json'))..."  # 574 行全 probation
```

## 五、堵点与缺口工单（红面五条，均有实证）

| # | 堵点 | 实证 | 修法归属 |
|---|---|---|---|
| 1 | **combo gate 未切 v2 frozen 尺**：THRESHOLDS 硬编码 v1（dsr_min=0.0 累计 N 口径），v2（dsr_min 0.5+family N_eff+ρ̄≤0.7+capacity+turnover 12×）已于 09-18 frozen（#337）；现跑 combo 对任何策略按 v1 suspect 口径输出无注记的 reject/borderline=误读风险 | promotion_combo_gate.py:56-61 vs standards.yaml:10-23/:55-69 | 施工（原 WO-08-01 残件+WO-08-04；v2 frozen 前置已满足，纯代码切换+测试钉值） |
| 2 | **combo 无事件入口**：CLI 手动（[STARTUP] manual），advisory 产出后无钩子调 combo 渲染一页报告——"汇总器"两半（建议包/一页报告）中间断链 | combo_gate 头注 STARTUP=manual；OPTIONAL_DUE_KINDS 无 combo kind | 施工（事件传动，宪法 §9.3 禁 cron：挂 promotion_advisory_due 执行体尾或新 optional kind） |
| 3 | **唯一人工门无带外通知**：飞书/SMTP 09-15 裁撤后，通知唯一出口=前端 #promotion 页横幅+data/failures/ 落文件——Owner 不开屏=建议无限期滞留（fail-safe 但无人知，M5 册横断模式 3 同构） | alerter.py:10/:34；promotion.js:150-152 | **Owner 门位裁定**（补邮件/死件开关/晨报承接，三选一） |
| 4 | **处女链零实弹**：建成 10 天零建议包零拍板（sim 观察期需连续 2 月，自然时间最早 11 月中）；期间端点/FSM/CAS 手术路径未经生产流量检验 | §四 运行证据 | 施工（advisory_dir 注入 tmp 目录做 e2e 彩排，不污染生产；decide 幂等+不写墓碑语义可安全重试） |
| 5 | 上游带伤：sim_memo 证据④ stats.error=CH TCP 不可用；SimBridgeExecute 断链（M5 S3）威胁账本数据源新鲜度；A/B 联赛（F73）未建→汇总器无联赛维度（ρ 相关性闸/冠军对照列缺位） | sim-memo-202609.json；Get-ScheduledTaskInfo 实测 | F72/F73 组+M2/M5 车道 |

## 六、F74 施工前置清单（汇总器真正转 built 需要什么——逐条）

### 6.1 输入源（五路+三实据，逐条核收）

| 输入 | 真源路径 | 现状 | 前置动作 |
|---|---|---|---|
| ①治理建议 | data/backtest_artifacts/runs/SCR-SIMGOV-*/04_wide/sim_governance_advice.json | 在产（46 runs，日/月班活） | 无 |
| ②月度偏离 | 同目录 SCR-DEV-*/04_wide/deviation_report.json | 在产（09-25） | 无 |
| ③整装证据 | data/backtest_artifacts/fw-auto/latest.json | 在盘但 fw 文件停于 09-16 | 核 fw_backtest_due 触发节奏是否合期（未自动=补发射方，pipeline_events 既有"消而不产"前科） |
| ④sim_memo | docs/_working/pipeline-research/sim-memos/sim-memo-202609.json | 在但 stats 全 error | CH 连通性修复后重跑月档 |
| PA-1a 双窗 | strategy_screen §8 双窗行（screen_source.fetch_bothwin） | 依赖 §8 台账班次 | 无（读不到=fail-closed 拒，安全向） |
| PA-1b FDR | docs/_working/pipeline-research/reports/intake-*.yaml fdr_keep | 在产（09-25 两批） | 无 |
| PA-1c 衰减 | data/runtime/strategy_decay_ledger.json | 在（09-21，574 全 probation） | 核 decay_certifier 周扫是否持续（台账停更=全量"无巡检记录"拒批） |
| 注册表 | docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml（lifecycle_status 真源） | 163 条目，sim 2 条 | 无（CAS 双写者=⑥intake，互斥已建） |

### 6.2 输出落点（汇总器三产物+回写）

| 产物 | 落点 | 语义 |
|---|---|---|
| 建议包 | data/strategy_intake/promotion_advisories/ADV-<yyyymmdd>-<sid>.json（+.decision.json 墓碑） | 目录首包时自建（mkdir exist_ok）；幂等同日覆盖 |
| 一页报告 | docs/_working/pipeline-research/promotion-reports/promotion-report-<ts>.md | combo 渲染；须补 v2 尺出处+suspect 注记（堵点 1） |
| 拍板回写 | 注册表 lifecycle_status（CAS 手术）+decision 台账+FSM 流转回执+alerter failures/ | token 只留 sha256 前 12 位指纹 |
| 下游交接 | approve→production 态进入 daily_decision_orchestrator S4 已毕业包集 | 当前包集空=安全态；转正首例前须核 S4 消费面接线（归 TD/日编车道） |

### 6.3 人工门交互面（Owner 拍板四要件）

1. **页面**：#promotion（web/pages/promotion.html+features/promotion/promotion.js）——建议卡+批准/驳回双按钮+decision 徽章+ops-notifications 横幅；已建成。
2. **端点**：GET /api/promotion-advisories（只读）/POST /api/promotion-decide（第四获准写端点，token=None→服务端自取密钥=点击即授权）；已建成。
3. **凭据**：ZEPHYR_OWNER_APPROVAL_TOKEN（secrets.py 通道）；未配置=全拒 fail-closed。**前置核点：生产 secrets 是否已配该键**（未配则拍板面永远 reject——彩排时一并验）。
4. **触达**：唯一缺口（堵点 3）。Owner 须裁定带外通道（晨报消费 promotion-advisories 清单为最小改）；裁定前 F74 不得宣 built——"唯一人工门"的门铃没接铃铛。

### 6.4 建设顺序（依赖序列）

堵点 1（v2 尺切换，代码小改）→ 堵点 2（combo 事件入口）→ 堵点 4（tmp 彩排 e2e）→ 堵点 3（Owner 裁定触达）→ 自然等待 sim 满 2 月（预计 11 月）→ 首个真实 ADV 包落盘=F74 转 built 判定日。前置中**无一项依赖 F73 联赛**（联赛维度属增强，非阻塞）。

## 七、自审闸三态

**部分挖干可施工**（四子件 file:line+测试双源交叉；运行态五证实测——advisories 目录/journal 计数/SCR-SIMGOV 最新档案/双任务 LastResult/衰减台账状态分布；总册 missing 判定以运行证据+campaign 簿交叉推翻；五堵点全带实证无推测断言）。未挖面：fw-auto 停更根因（归 M2/XC）、S4 包集消费面细节（归 TD）、league 维度（归 F73）——均登记归属不在本册下钻。

## 八、三态结论

**F74 = partial**（总册 missing → partial 修正）。
差什么才算 built：①combo gate 切 v2 frozen 尺+suspect 注记（堵点 1，前置已满足）②combo 事件入口接通"建议包→一页报告"最后一跳（堵点 2）③Owner 触达通道裁定落地（堵点 3，Owner 门位）④e2e 彩排一次全链（堵点 4）⑤首个真实建议包走完"生成→推送→拍板→注册表流转"全程。五项中①②④纯施工、③Owner 门、⑤自然时间。
**回写总册建议**：§一 F74 状态 missing→partial；§四 断链点清单"F74 转正汇总器（缺位）"改判"已建成未转绿（堵点 1-3）"；口径漂移注记=总册骨架挖矿时点（09-25 前）早于/平行于 campaign 交付核验面。
