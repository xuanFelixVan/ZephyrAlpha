---
gate_selfdoc: GIT-DANGEROUS
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW6_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW6 FMS图书馆退役车道台账（失联车道考古+续作）
# 由 SW8 代录（sid=st-nightsweep-sw8-20260929，总筹=st-nightsweep-chief-20260929）
# 录入时间: 2026-09-29 06:2x；考古对象=SW6（st-nightsweep-sw6-20260929）超时失联遗留
ledger_author: SW8-代录
archaeology_time: 2026-09-29T06:00-06:30+08:00

bags:
  done_0001_trae032:
    qid: q-20260929-st-nightsweep-sw6-20260929-0001
    state: done → HEAD eb2df8bf28（05:54 落地）
    semantics: trae_032 六处死册指针 module-id-registry.json→architecture_model/module_id_registry.yaml（#ARCH-361 通道）
    crosscheck: HEAD grep 死指针=0（SW8 复核 06:2x）
    verdict: DONE-CROSSCHECK
  done_0002_retirementA:
    qid: q-20260929-st-nightsweep-sw6-20260929-0002
    state: done → HEAD c2ec2ff87a（05:57 落地）
    semantics: module_id_registry 三条退役条目归位（MOD-INF-003 retired→deprecated+superseded_by 等）
    crosscheck: 落地 message 自带 validate_module_lifecycle 35→32 违规证据；IFC-007 契约级联零动作
    verdict: DONE-CROSSCHECK
  processing_0003_library_hygiene:
    qid: q-20260929-st-nightsweep-sw6-20260929-0003
    state: processing 孤儿（04:26 起，04:26-04:45 serializer 崩溃窗口遗留；现行 serializer 长跑未重启故未回收；下次 drain 自举 _recover_orphans 自动重入 pending）
    files: 4（library_hygiene.py blob 3ac37067 base 6cf1fa75==HEAD；tests/library/test_library_hygiene.py 新件 blob b5cfde77；CCFR blob 28d522fa base 74236511==HEAD；module_translation blob 098db79a base 0babec92==HEAD）
    verify: 盘面 library_hygiene.py==袋 blob 逐字节同（sha 3ac37067f315dda4）；盘面测试件==袋 blob 逐字节同；pytest tests/library/test_library_hygiene.py 17 passed（SW8 06:2x 实测）；tests/library 全目录 194 passed+1 环境性红（import 面预算 298>220ms，负载抖动，复跑绿）
    semantics: created 轴治本（判龄轴 mtime→frontmatter created；undated/missing_on_disk 单列；ttl 走 YAML 解析）
    verdict: ADVANCED（袋完好待队列自举回收落地）
  processing_0004_report:
    qid: q-20260929-st-nightsweep-sw6-20260929-0004
    state: dead（06:14 serializer 取走落地失败转 dead）
    files: 1（99_delivery_report.md blob d18955a8 base b47c8fc4==HEAD）
    semantics: 99 报告 §十七-廿八 640→633 行合并去重落库（原署 st-fms-chief-20260927）
    dead_reason: GATE-PRECOMMIT-RUN/gate-detect-git-dangerous——正文 450/462 行取证引文含 "git reset --hard" 字面量（§廿二 16.7h 陈锁毒锁案卷），2 命中
    worktree_vs_blob: 逐字节相同（632 行零 diff）
    cure: detect_git_dangerous.py 自带 GATE-SELFDOC 行级标记豁免（[GATE-SELFDOC:GIT-DANGEROUS]，总包裁定 A3，≤10 行）——SW8 对 2 行加标记后 requeue，引文内容零改
    verdict: ADVANCED
  pending_0005_backfill_b1:
    qid: q-20260929-st-nightsweep-sw6-20260929-0005
    state: pending（05:26 入队，946 件）
    semantics: created 回填批 1/3（docs/_working tracked .md frontmatter created 回填；源=文件名 ISO/紧凑日期+VCS 首次入库日；manifest=.runtime/tmp/st-nightsweep-sw6-20260929/backfill_created_manifest.jsonl 全量 1752 件分 3 批）
    note: 袋 message 内"本批 584 件"为早期拆分残文（袋实载 946 件，946+400+400=1746≈1752-6 bad frontmatter）
    verdict: DONE-LANED(pending 在队)——任务书所谓"SW6 未做的最大件"实为已做已入队，SW8 不重做（防双投）
  pending_0010_backfill_b2:
    qid: q-20260929-st-nightsweep-sw6-20260929-0010
    state: pending（05:48 入队，400 件）
    verdict: DONE-LANED(pending 在队)
  pending_0011_backfill_b3:
    qid: q-20260929-st-nightsweep-sw6-20260929-0011
    state: pending（05:48 入队，400 件）
    verdict: DONE-LANED(pending 在队)
  stale_0004:
    path: pending/.stale/q-20260929-st-nightsweep-sw6-20260929-0004.json
    note: stale 影子指令（append-only 旁路），随 0004 重投被新袋取代，队列机制自洽

cards:
  B24_trae032死指针:
    verdict: DONE-CROSSCHECK (HEAD eb2df8bf28)
  B20_退役A路:
    verdict: DONE-CROSSCHECK (HEAD c2ec2ff87a)
  I5_I32_library_hygiene:
    verdict: ADVANCED（processing 袋完好+测试 17 绿实测，待队列自举）
  I5_I33_created回填:
    verdict: DONE-LANED(3 袋 pending 在队；manifest 在案；不重做)
  I5_I44_报告落库:
    verdict: ADVANCED（dead 袋 selfdoc 豁免后 requeue，SW8 施行）
  B09_FMS判据改写:
    verdict: DONE-CROSSCHECK (HEAD 984c1787f8 04:38：翻 block 判据改连零棘轮+mode 保持 warn+35 测试绿)
  B15_FRONT_DOOR:
    verdict: DONE-CROSSCHECK (HEAD 9abbe6f1bc 04:42：ROOR front_door 指针+index.md 导航)
  B12_B10_P2:
    verdict: DONE-CROSSCHECK (HEAD 9a2c6402d4 04:46：.pre-commit-config.yaml 挂 validate_module_lifecycle warn-only)
  件9_S5簿附录A:
    verdict: DONE-CROSSCHECK (HEAD 06dc31b719 04:48，超计划交付)

leftover_files:
  trae_032_module_lifecycle:
    state: MM 幻影（工作树==HEAD；index=6a7787c4 陈旧快照）
    verdict: 落地已完成；index 陈旧快照由 SW8 git add 归零
  module_id_registry:
    state: MM 幻影（工作树==HEAD；index=f074de31 陈旧快照）
    verdict: 同上归零
  candidate_registry:
    state: MM+盘面 2 hunk 真差异（scripts/data 路径前缀属 qmine 战役① WIP）
    verdict: 袋 0004 在队为准；.bak_pre_one_question 移 .runtime/tmp 处置
  api_server_py:
    state: MM 幻影（工作树==HEAD CRLF 幻影；index=33626402 回退性旧版快照，会吞 schedulegate confirm 特性=危害物）
    verdict: index 归零；袋 0003 在队为准
  library_hygiene_py:
    state: M（工作树==袋 blob 3ac37067）
    verdict: 完整可投，待 processing 袋自举
  algo_flow_api_server_yaml:
    state: D+??（暂存删除+盘面 09-25 旧代版 2899B；HEAD 为 09-27 新口径版 1514B 且被 HEAD api_server.py:20 external 锚引用）
    verdict: 暂存删除=错误快照（删除将断 ALGO-FLOW 锚），SW8 git restore HEAD 版归零双态
  test_api_server_schedulegate_confirm:
    state: D+??（暂存删除+盘面副本==HEAD 逐字节同）
    verdict: 按令只登记不代清（SW2 提到的可疑现场）

_SW8_continuation:
  record_time: 2026-09-29 06:2x-07:0x
  selfheal_witness:
    - processing 孤儿 sw6-0003（library_hygiene 4 件）已被队列 _recover_orphans 自举回收并落地=14dc95cb05（06:33）——失联车道机制自愈实证，SW8 只补 17 测绿+盘面 blob 同一性证据
  I5_I44_报告落库复活:
    verdict: ADVANCED
    evidence: 死袋 0004（06:14 二死=gate-detect-git-dangerous 误拦 §廿二 450/462 行取证引文）；SW8 走门禁自带 GATE-SELFDOC frontmatter 豁免通道（gate_selfdoc: GIT-DANGEROUS，总包裁定 A3），引文内容零改；detect 复测 0 findings（2 处豁免留痕）
    landed: requeue→q-20260929-st-nightsweep-sw8-20260929-0001（在队 FIFO）
  I5_I33_created回填:
    verdict: DONE-LANED 确认（3 袋 946+400+400 件在队；SW8 零重做防双投；袋 message"584 件"=早期拆分残文已记台账）
```
