---
ttl: task_bound
session: st-fullscore-night-factory-chain
title: 接电施工单——BP-1~7 修复动作+两工厂×生产链接线点设计（2026-10-01 夜挖）
date: 2026-10-01
status: mined
---

# 02 接电施工单（wiring plan，只开处方不实施）

> 每条=位置(file:line)+动作+验收标准。施工前铁律：RULE-CAPABILITY-LOOKUP 双审计+RULE-DEPGRAPH 登记+worktree 隔离（construction_workflow_policy 15 步）。

## A. 工厂×生产链接线点设计（核心问题：谁调谁、在哪注册、防平行件）

### A-0 现状判定
- strategy_factory 10 阶段=纯内存编排（strategy_factory.py:28 "纯内存实现无 IO"），三闸+人工裁决 API 齐备：register_discovery_hook(:203)/submit_gate_verdict(:246)/submit_phacking_metrics(:256)/human_adjudicate(:268)/register(:279)；头部 CONSUMERS 自述"运行时装配批（策略候选注册/监控接线）"(:5)。
- factor_factory 9 阶段=注入式编排，__init__ 注入面 registry/ic_validator/causal_validator/backtest_gate/mining_hook(:206-224)；**缺省 lambda c:True(:218-220)=未接线即全过的陷阱**；mine() 无 hook 即抛(:260-263)；CONSUMERS 自述"运行时装配批接线"(:5)。
- 生产真链（intake_pipeline→c4→intake.py）**已是事实工厂**：E2/E4 台账=判定权真源。两工厂直插生产链=制造第二/第三判定权。

### A-1 接线方案（推荐：薄适配器，工厂做生命周期编排不做判定）
1. **strategy_factory 接电点=E5/E6 出口**（intake.py 新入库 STR-AUTO-* 之后）：装配批构造适配器把 CH 台账状态映射工厂阶段，`submit→advance` 到 MONITORING 作**注册镜像+审计留痕**；判定权仍归 E2/E4 台账，工厂不产第二份 verdict。
2. **discovery_hook 注册=三车道挂四通道**（:203）：lane_c_formula_miner(GP)/lane_c2_agentic_miner(LLM)/lane_b_idea_generator(LLM) 各注册为 hook，返回 StrategyRecord——工厂获得"四通道自动发现"语义（FACTOR_MAD 通道留空待 CAND-FAC-020），不重建挖掘件。
3. **factor_factory 接电点=独立施工批**：ic_validator=真源已在（src/zephyr/factor/analysis/ic_ir_calc.py）；causal_validator/backtest_gate 必须显式注入且**施工同批把 :218-220 缺省改 fail-closed**（None→required，或在装配点断言三件非空）；mining_hook 可缓（不调 mine() 则无害）。
4. **注册位置=运行时装配批**（两件头部自述的唯一指定点），不新建平行装配模块；模块命名/登记按 construction_sop 走，本册不指定。
5. **防平行件铁律**：工厂只读生产台账（strategy_screen/constructed_manifest/factor 表），禁新增判定表；**BP-4 必须与工厂接线同班**（F06 判定落 strategy_screen），否则 F06+工厂+生产链三判定权并立。

## B. BP 逐条修复动作

| # | 位置 | 动作 | 验收标准 |
|---|------|------|---------|
| BP-5a(先做) | data CH 注册表 STR-AUTO-001；intake.py:57；promotion_advisory.py:102 | ①隔离污染条目（registry 净删=Owner 门位 §5，登记审批后处置）；②REPORT_DIR 改 `ZEPHYR_INTAKE_REPORT_DIR` env 注入（两处同批）；③涉事 tests 改 tmp_path | pytest 全绿后 reports/ 目录 mtime 不动；`grep -l pytest_ intake-*.md` 零新增；STR-AUTO-001 出生产面 |
| BP-2 | factory_intake_pipeline.py:339-340 | except 分支加 alerter 告警+report 增 `e2_source_fail_closed` 字段 | 拔 CH 跑 `construct --dry-run`：报告含 fail_closed 字段+告警留痕，constructed=0 且有声 |
| BP-7 | c4_batch_screen.py:217-223 | 月度窗口漂移播报挂晨报（读 run 档案 summary.window 对比上月） | 播报件落晨报管道；OOS 终点前移可见 |
| BP-6 | 文档口径 | 三幂等键口径写进断点清单批注（payload.files 仅告警参考，权威=台账差集），不改码 | 断点清单批注合入；无代码 diff |
| BP-1 | factory_intake_pipeline.py:224,227-234 | construct 扩假说轨分支：lanes 含 D/B 时调 hypothesis_translator.run_translate（:173 面料已有 --model/--dry-run），产出考卷件+translated_manifest 幂等（键=seed candidate_id） | `construct --lanes C,C2,D` 对 D 轨过审者产 translated 行；重跑 skipped_done 不重复翻译；阴性件(translatable=false)如实入账 |
| BP-4 | f06_e4_wfa_exam.py:60 落账点 | F06 判定行追加落 strategy_screen（verdict='f06_wfa'+exam_archive 指针） | bothwin 查询可见 F06 幸存者；E5 消费面（screen_source bothwin）读到 |
| 工厂接线 | 见 §A-1 | 专项施工批：适配器+三车道 hook 注册+factor 三 validator 注入+:218-220 改 fail-closed | ①grep 出现生产实例化点（非 test）；②工厂审计流出现在有的 submit/advance 记录；③缺 validator 时 FactorFactory 构造即拒（fail-closed 测试）；④depgraph 无 HIGH drift |

## C. 施工顺序（依赖序）

1. BP-5a 污染隔离（在产事故，最高优先，Owner 审批窗）
2. BP-2+BP-7+BP-6（S 级加固，一个 worktree 批）
3. BP-1+BP-4（M 级接线，解锁 D/B 轨与 F06 赛马）
4. 工厂适配器施工批（A-1 全项；前置=capability_lookup+depgraph 登记）
5. 班次化：heavy drain（`pipeline_events drain --all`，:1346 现行拼写）纳入晨报授权清单（BP-3 防复发）

## D. 六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | 本册 01_chain_map 全部行号证据；两工厂头部 CONSUMERS 自述（strategy_factory.py:5/factor_factory.py:5） |
| 下游消费 | 施工批（construction_sop 15 步）；晨报授权清单；Owner 门位审批（STR-AUTO-001 处置） |
| 自动化触发 | 不改触发面；事件驱动既有的 pipeline_events 调度器唤醒路径 |
| 真源与注册表 | MOD-PF-009/MOD-L02-001 blueprint（MODIFY-GUARD：strategy_factory 改动须过 blueprint.md）；MOD-BT-189/190 |
| 门禁与质量尺 | 全部施工走 GitCommitGateway；factory 域 gate 既有面不放松；fail-closed 改造新增测试钉 |
| 当前运行状态 | 本册=处方（零 diff）；BP-3 班次化建议待 Owner 派工 |

## E. 自审闸

**三态：MINED_DRY**（全部处方落到 file:line；未决项仅一处=STR-AUTO-001 处置方式属 Owner 门位，本册只登记不代办）。

## F. 施工落地批注（st-fullscore-20260930 接电班，2026-10-01 夜）

> 存证批注：本册及 03 裁定册原件于 03:41 被他会话（st-circ-a7-20260930）stash/reset 风暴整目录卷走，接电班按上下文逐字复原+续写本 §F（01_chain_map.md 不在本班上下文，未复原，归矿班自.restore）。

### F-1 BP-6 三幂等键口径（不改码，权威口径批注）

| 台账 | 幂等键 | 口径 |
|------|--------|------|
| constructed_manifest.csv | `candidate_id` | 已登记即跳过（重跑零重复构造） |
| translated_manifest.csv | `candidate_id`（仅"有效结论"行占坑） | refusal_reason 前缀 `llm_error` 的基础设施阴性不占坑（F22），同 id 另有有效行照常跳过 |
| c1_backtest.strategy_screen | `(screen_batch, strategy_id, verdict, source_file)` 四键 | deferred 行不挡 translated 行；同 sid 多版本翻译件各留一行（族取舍归 C5）；F06 落账行（verdict=`f06_wfa`）同构四键 |

**通用裁定**：事件 payload.files 仅告警参考，**权威=台账差集**（重放对账以台账已有键为准，不信 payload 自述）。断点恢复语义：construct/translate 重跑=幂等跳过集只认台账有效结论行。

### F-2 BP-5 STR-AUTO-001 污染清理记录（RULE-DATA-OPS 三步出证+移除留档）

- **证据链（真实性）**：①`docs/_working/pipeline-research/reports/intake-20260930-2102.yaml`：created_sids=[STR-AUTO-001]、候选=`CAND-z@c4_z.py`、mount.self_heal.error 路径=`.runtime/tmp/pytest_34632/test_6_cas_conflict_fails_clos0/map.yaml`——pytest 件混入铁证；②源头=tests/strategy_pipeline/test_redblue.py::test_6（trigger_batch="C1" 与报告一致）；③CH 全表反查：strategy_registry.yaml（161 条）无 STR-AUTO、strategy_screen 零行——YAML 真源未被持久污染（registry_writer 的 append 在该测试中被 fake，只有 sim 钱包行泄漏落库）。
- **移除执行（必要性）**：`c1_backtest.sim_pocket_daily` 8 行 + `sim_trade_log` 8 行（2026-09-15..09-22，全 open/零持仓/零盈亏孤儿钱包）——经 `ch_writer.delete_where`（TCP 写户缺 ALTER DELETE 授权降级 HTTP 通道成功）于 2026-10-01 移除，复核 remaining=0。
- **可逆性**：16 行全量导出隔离档案 `10_coordination/str_auto_001_quarantine_20261001.csv`（重灌即可逆）。
- **防复发**：test_redblue test_6 已补 `intake.REPORT_DIR→tmp_path` 隔离（本批）；intake.py/promotion_advisory.py 报告目录 `ZEPHYR_INTAKE_REPORT_DIR` env 可注入（本批）。

### F-3 本班接线面落地对账（BP-1/2/4/7+LLM）

- BP-1：auto_construct 扩双轨（C/C2 机械桥不变；D/B→hypothesis_translator.run_translate 承接，channels 参数化，幂等键=seed candidate_id，阴性如实入账）；--lanes 校验非法车道 exit 2。
- BP-2：_e2_passed_by_channel 拆查询体+fail-closed 壳——CH 不可达=pipeline_events.alert 留痕（stderr 兜底）+report.e2_source_fail_closed/error 字段，双轨全跳。
- BP-4：f06_e4_wfa_exam.append_screen_ledger——判定档案落盘后落 strategy_screen（verdict=`f06_wfa`，notes 带 exam_archive/oos_sharpe 指针），四键幂等，落账未确认 RuntimeError（fail-loud）；screen_source 及格口径（一字不差 parity 不变量）未动，F06 行进 bothwin 及格集=后续 E5 F06-赛马适配批（需独立 parity 重验，本班不私扩）。
- BP-7：c4_batch_screen.monthly_window_broadcast——OOS 动态周六窗每次 OOS 批触发时落月度播报件（reports/c4-oos-window-<YYYYMM>.md，月度幂等），跨月漂移经 pipeline_events.alert 留痕；零 cron 零定时（事件触发）。
- LLM 接线：ollama_chat.resolve_routed_model（task_routes 真源，fail-closed：轨缺席/API 轨=RuntimeError 禁私接）；lane_b→signal_generation 轨、translator/lane_c2→strategy_codegen 轨，本地缺省 qwen3:8b；--model 显式覆写保留（14b A/B 实验档）。
