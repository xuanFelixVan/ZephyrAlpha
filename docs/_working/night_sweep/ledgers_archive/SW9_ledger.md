---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW9_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW9 二期序列施工车道台账（F53 Saga + F04 清洗四引擎 + F92 序1 小件）
# sid=st-nightsweep-sw9-20260929，总筹=st-nightsweep-chief-20260929
# 录入时间: 2026-09-29 06:5x；施工区=D:\ZephyrAlpha\.worktrees\st-nightsweep-sw9-20260929（分支 ai/st-nightsweep-sw9-20260929/task-saga-cleaning）
ledger_author: SW9
session: st-nightsweep-sw9-20260929

bags:
  F53_saga_registry_sim_assembly:
    qid: q-20260929-st-nightsweep-sw9-20260929-0001（pending，files=15=本袋 7 + F04·2a 吸收 5 + F04·2b 吸收 3；C1 同会话合批 by-design，absorbed message 尾注存 meta.absorbed，drain 侧 allow_multi_domain=True 合法留痕）
    files_self: 7（src/zephyr/ex_core/order_execution_saga.py 修改 + saga_compensation_registry.py / sim_saga_assembly.py 新件 + tests/ex_core/test_saga_compensation_registry.py / test_sim_saga_assembly.py 新测试 + 两注册表 yaml 随批）
    semantics: Saga 六步补偿链编排器本体治本——①补偿动作注册表（步骤→动作注册面/逆序 LIFO/单动作异常捕获成 SagaCompensationRecord 不外抛/非幂等注册拒绝）②order_execution_saga 三补偿点接线（step5 失败/异常路径/超时终判 TIMEOUT，内建补偿后逆序执行+审计落账 reason=saga_compensation_registry，未注入=行为零变化）③sim 开箱装配入口 build_sim_saga（environment!='sim' 一律 SimAssemblyEnvError fail-closed=实盘接线物理不可达；OrderManager 五合规件零裸构造 F62 同口径 ReportGate/CancelRateGuard/ManipulationRealtimeMonitor/ProgrammaticTradingGuard(SIMULATION)/InfoAsymmetryManipulationDetector；SimulationBroker 装配即连接）
    三件套: add_module_translation ×2（7922/7923 条）+ apply_depgraph --add-design-node（node 15387757/15387758）+ creation_token（ex_core_saga_sim ×2）
    tests: 新增 30 用例（注册表三态 17 + sim 装配 12 + 回归锁 1），saga 域四套件 80/80 过（含既有 50 件零破坏），ruff/format 净
    verdict: DONE-LANED(6挖掘干复核：Saga core 894 行 built+68 用例在册，真缺口=补偿注册表缺失+sim 装配入口缺失，均已补；实盘切换未做=裁定口径)

  F04_cleaning_facade_quarantine:
    qid: 同上 q-0001（F04·2a 5 件 + F04·2b 3 件被 C1 合批吸收）
    files_2a: 5（src/zephyr/data/cleaning_engines.py / quarantine_manifest.py 新件 + cleaning_rule_engine.py 头注+DSL op 语义文档矫正 + tests/zephyr/data/test_cleaning_engines.py / test_quarantine_manifest.py 新测试）
    files_2b: 3（data_eng 三引擎头注 built-not-wired 矫正：cleaning_anomaly_engine/expectation_governance 空 CONSUMERS→显式声明；data_anomaly_alerter "运行时装配批"虚标→零调用方实证声明）
    semantics: ①统一入口 cleaning_engines.py（四引擎静态台账与 grep 复扫对账+四派发函数惰性 import+C6 AI 判净接口位 ai_adjudicate 一律抛 AiAdjudicationPendingOwnerGateError）②C4 隔离区 manifest 桥 quarantine_manifest.py（只读扫描台账/死信自动分拣登账 jsonl CAS/TTL 超期清单 report-only，回放清除=Owner 门不提供执行路径）③C2 四头注接线实况矫正④发现并矫正 cleaning_rule_engine DSL op 语义文档反向（码面/红测/config cleaning_rules.yaml 三方一致"必须方向"语义，docstring 单方漂移，零行为变化）
    挖矿增量发现: C1 已部分推进——chiefzc-rescue 波已落地 cleaning_rules_hosting.py（860 行，supply_sentinel L13 腿托管接线）+config/cleaning_rules.yaml（DSL 真源），F04 案卷"三引擎零接线"现状=DSL 引擎已读侧接线、data_eng 三件仍零调用方（09-29 grep 复证）
    三件套: add_module_translation ×2（7924/7925 条）+ depgraph（node 15387761/15387762）+ creation_token（data_cleaning_facade ×2）
    tests: 新增 25 用例（facade 11 + manifest 桥 14），F04 域七套件 127/127 过（含既有引擎+hosting 套零破坏），ruff/format 净；测试全走 tmp_path 零生产 data/ 写入
    verdict: DONE-LANED（可施工面 C2+C4+统一入口全落地；C1 三件接线=OWNER-GATE 未动；C3 幽灵行=OWNER-GATE 未动；C5 假绿尺=F01 同袋未动；C6 AI 判净=只留接口位未实现）

  F92_roor_entry_count:
    qid: q-20260929-st-nightsweep-sw9-20260929-0004（pending，files=1 docs/registry_of_registries.yaml）
    files: 1（ROOR REG-METAQ-001 entry_count 0→422，safe_write_text CAS before=2907be07 after=8c9c3934 进程外复核过）
    evidence: PG meta_question 主表行数 2026-09-29 经 MetaQuestionRegistry 默认通道实查 count=422（挖矿卡基线 76 已过期；09-22 机生快照 row_count=283 已陈旧；counting_rule 口径=主表行数）
    发现登记: meta_question/snapshot.py PG 导出通道 YAML RepresenterError(Decimal('100'))——快照机生链阻断，归治理车道（_coerce_row 缺 Decimal 规整），本车道未越界修
    一致性: check_registry_consistency METAQ 项与 HEAD 前等价（UNSPECIFIED 计数口径未登记=既有），CR-007 25 项 STALE=B10-2 回填批既有口径非本件新增
    verdict: DONE-LANED（序1 直干 0.2 天项落地；序2 治本对账=对账族车道；序3 带裁定=OWNER-GATE 未动）

owner_gate_registry:
  - F53: 实盘接线（TradingSession 切 Saga）=OWNER-GATE——总筹裁定只做编排器本体 sim 可用；build_sim_saga environment 参数 fail-closed 物理封死实盘路径，解锁须 Owner 裁定+独立实盘装配通道
  - F04-C1: data_eng 三件引擎（cleaning_anomaly_engine/expectation_governance/data_anomaly_alerter）生产接线=OWNER-GATE（总册晨报"勿自动施工"在案）；统一入口已就位，解锁后接线即插即用
  - F04-C3: daily_valuation 幽灵行/epoch 残留清理=OWNER-GATE（R-M1-02/03 在案），未动
  - F04-C6: AI 判净站（花钱点）=OWNER-GATE，接口位 ai_adjudicate 已留（fail-closed 抛错），零计费调用
  - F04-C4 执行面: 隔离区回放/清除动作=OWNER-GATE，manifest 桥只出 report-only 清单
  - F92-序3: campaign 带占位裁定=OWNER-GATE（PQ-0099 §4），未动

cross_checks:
  - 避让图复核: 未触碰 zc9-lane-p（matching_engine/vectorized_engine——Saga 只读依赖 broker_interface 无关）、zc9-lane-d（akshare_provider/data tasks.yaml）、zc9-lane-l（gov_audit/writer.py）、SW1 死信批次（C4 桥为隔离目录侧新件不碰 SW1 归档件）、F62 六裸构造点（sim 装配为新增第五口径合规构造，六处存量未动=F62 领地）
  - 他队已落地交叉验证: cleaning_rules_hosting+cleaning_rules.yaml=chiefzc-rescue 波 ae514cf5ec0 已落地（本车道只做消费侧矫正不重做）；SW6 ROOR front_door 批 9abbe6f1bc 已落地（本车道 entry_count 修改基于其上）
```
```
