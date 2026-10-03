---
ttl: task_bound
completes_when: chief 逐条消费（裁定/转呈/驳回）后本件退役
title: 图12 F2·需裁定与共享面发现呈批件
owner: st-vm12f2-20261003
session: st-vm12f2-20261003
date: "2026-10-04"
discipline: 勿自行处置——tests/**、生成器 _HUMAN 层均在本批红线外
---

# F2Z 呈批件（4 条）

- id: E-11
  title: 图12 gate 对抗测试 3 夹具相位瞬态（写死 f1_pending 旧相位）
  finding: tests/governance/commit_gates/test_data_supply_chain_map_gate.py 三用例依赖"真实图=f1_pending 且缺血肉"前提，F2 填满后转红：①test_f1_pending_blood_missing_downgrades_to_warns（真实图已无 warn 可断言）②test_f2_done_production_requires_trigger_facts（production 节点已带 trigger_facts，红前提消失）③test_gate_pass_on_real_map_with_notes（断言 detail 含"血肉未满"注记，现已无）。产品面无缺陷（validator exit0/warns0、gate _check ok=True、能红用例 10 个全绿）。
  prescription: 三用例改构造性夹具（各 1-2 行）：①对 _load_map() 深拷贝后 del 首个非 gap 节点四字段再置 f1_pending；②对 production 节点 pop('trigger_facts')；③改断言为 ok 且 '血肉未满' not in detail（或另立 fixture 缺字段版断言含注记）。改 tests/** 归 chief/维护班（本批红线外）。
  anchors: tests/governance/commit_gates/test_data_supply_chain_map_gate.py:53-66/:96-109

- id: E-12
  title: 三本合格病历无 CASEBOOK 册号（上户口缺口）
  finding: known_data_gaps.yaml（module_id 身份）、integrator_progress.db、archive_manifest.jsonl 均够格（表B 合格）但 casebook_registry.yaml 无号——casebooks 字段册号形态（E-6 裁定）容不下，本批以既有指针（source_anchor/module_ref/freshness）满足 SOP §3 规2。
  prescription: 下批上户口授 CASEBOOK-006~008（registry 条目增删须随裁定/挂图批，Owner 门位），随后把 DSC-14/16/20/10A/10B 的 casebooks 字段补挂册号。
  anchors: docs/01_policies_and_standards/_registry/catalogs/casebook_registry.yaml；docs/_working/vmap12_flesh/f2z_coverage_report.yaml §1红3

- id: E-13
  title: 表A 高置信 8 机制族孤儿（挂载权在机制挂载批）
  finding: source_circuit_breaker/tick_redis+h1_redis_hot/ch_parts_monitor/multi_timeframe_fusion/news_collector+news_taxonomy/market_breadth_collector/sector_intraday_aggregator/database_service 八族在图内无任何挂载面（module_ref/executors/source_anchors 全无）；error_classifier 仅 fallback 文述半挂。四字段批无权动总线（裁定二：module_id 真源推导，existing-wins 不得覆盖）。
  prescription: 机制挂载批（chief）按表A §2.1 落 _HUMAN 层 executors/source_anchors 或经 depgraph 投影挂 module_id；逐条建议落点见 F1 表A。
  anchors: docs/_working/vmap12_flesh/f1a_mechanism_mounts.yaml §2.1；f2z_coverage_report.yaml §1红1

- id: E-14
  title: DSC-18/DSC-SRC 等五节点 verdict 证据链时点差
  finding: trigger_facts as_of 统一 2026-10-04，但部分证据腿为 09-25 探针转录（freshness 六节点）与 cons12 09-24 实测（schtasks/backup_log）——双时点已在各 evidence 内注明，无冒充；但 DSC-18（周任务，上次实证 09-20）与 DSC-10B（manifest mtime 09-28）观测窗内无新留痕，下轮 regen 时建议顺带复测刷新。
  prescription: 无需裁定；登记为下批 regen 附带动作（维护班例行）。
  anchors: config/data_supply_chain_map.yaml DSC-18/DSC-10B trigger_facts.evidence
