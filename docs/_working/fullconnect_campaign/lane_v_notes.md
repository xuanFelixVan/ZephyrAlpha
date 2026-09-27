---
ttl: task_bound
title: "V 线施工进展台账"
session: zc-lane-v-20260927
completes_when: "V1~V3 三件全部落地，战役收官后随 docs/_working 归档"
---

# [BLUEPRINT] | docs/_working/fullconnect_campaign/lane_v_notes.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

V 线施工进展台账（全流通战役 zc-lane-v-20260927）：三件治理面红证/对账闭环，逐件记录/测试读数/落地哈希。

## V1 F98 门名册三账对账闭环

- 改动：`scripts/governance/generators/generate_gate_registry.py` 扩 `three_account_diff()` +
  `format_three_account_report()` + `--diff` 只读 CLI（F98 卷 §四 G1 / M3 03 G1 修法落地）。
  净零：并入既有生成器（替代人工周审计动作），不新增脚本不新增门；generate() 编排段字节兼容
  （输出键面 11 键不变，测试 `test_generate_output_has_no_diff_section_byte_compat` 守卫），
  对账纯只读（`test_cli_diff_never_writes_registry` 守卫 mtime+内容不变）。
- 三账口径：gate_registry.active ↔ in_process.enabled ↔ pre-commit hooks。
- 测试读数：tests/governance/generators/test_generate_gate_registry.py 21 passed（新增 10：
  绿样/红样三向漂移/虚报镜头/悬空镜头/真源册冒烟/报告确定性/字节兼容守卫/CLI 三态）。
- 三账差集读数（2026-09-27 实跑，RED exit=1，全量=.runtime/tmp/lane_v_diff_report_20260927.txt）：
  账1 active=169｜账2 enabled=100｜账3 hooks=55｜三账交集=0；账1−账2=74、账2−账1=5、
  账1−账3=114、账3−账1=0、账2−账3=100、账3−账2=55；虚报 4（ALGO-FLOW-LINK/CAPABILITY-OVERLAP/
  GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER）；悬空 16；字段自洽 181/181、104/104 均 OK。
  已写 05_f98 卷尾附记 §七（只读报告不修册；修册归名册 owner 域）。
- 落地：见 git log（本文件同批）。

## V2 F101 RULING-REFERENCE 红证

- 病根勘误：RULING-REFERENCE 旧单门工厂已并入 REFERENCE-INTEGRITY（dangling_reference_gate.
  make_reference_integrity_gate）且不再注册；既有 test_ruling_reference_gate.py 18 测全绿但挂的
  是退役工厂，活聚合台仅有构造冒烟（test_p4_merged_gates.py）——"裸裁定引用不登记可红"在活
  执法通道上零配对。
- 改动：tests/governance/commit_gates/test_ruling_reference_gate.py 追加
  TestReferenceIntegrityUnionRedProof 5 测（tmp_path 备齐 AGENTS.md/architecture_issue_registry/
  ruling_registry 三真源）：活台裸引用红（[RULING-REFERENCE]+RULING_REFERENCE_VIOLATION）、
  DANGLING 定向性不混淆、已登记绿、tests/ 豁免绿、registry 缺失 fail-closed 红。
- 测试读数：23 passed（18 既有 + 5 新增）。

## V3 F05 判重尺红样

- 改动：新建 tests/governance/scripts_governance/test_check_tick_duplication.py（判据件
  scripts/governance/data_quality/check_tick_duplication.py 此前 [TESTS] 头为空=零配对，
  M5 census C 类疑似失效 3 件之一）。ch_reader.query 全程 monkeypatch 替身，tmp_path 隔离，
  零生产数据触碰。
- 红样两例（卷面 D1 处置令）：①真重复（14 字段全同 -> dup_group_cnt=1 -> exit 1）；
  ②边界串位（同排序键不同价位，2026-07-16 事故形态 -> dup_group_cnt=0 -> exit 0），
  并留对照测试证明禁用判据 count()-uniqExact(排序键) 在同场景误报 1。
- 测试读数：18 passed（判据 SQL 构造 4 + 真重复 3 + 边界串位 3 + 解析报告 8）。

## 回归批

- tests/governance/generators/ 全目录 + test_check_gate_inventory_drift + commit_gates 引用族
  （p4_merged/arch/dangling/ruling）：88 passed。
- test_regen_clean_check.py：30 passed。
