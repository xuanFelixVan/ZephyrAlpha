---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# W2MERGE_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# W2MERGE_ledger.yaml — 夜战总 Sweep2 2026-09-30 · W2-MERGE 合并收编车道
# sid=st-nightsweep2-merge-20260930 总筹=st-nightsweep-chief-20260929

meta:
  session: st-nightsweep2-merge-20260930
  date: 2026-09-30
  cold_start: "Python 3.12.8 PATH 修正 ✓ / setup_dev_env --check usercustomize ✓ / reaper last_run=2026-09-30 13:17 存活 ✓ / SessionRegistry 注册 ✓ / capability_lookup.find 留审计（0 hits，merge train 收编无既有能力簇）✓"
  worktree: ".worktrees/st-nightsweep2-merge-20260930 (branch ai/st-nightsweep2-merge-20260930/merge-train, 基于 dev)"
  mission: "三分支 13 commits 收编（NB2=6 / NF=6 / NB1=1）；NC/NE4 实测零未收编 commit 跳过"

branch_analysis:
  merge_base: d2446aff07（三分支同基；dev 侧当时 +31 commits 漂移，收编窗口内 dev 持续推进）
  nc_ne4_check: "session/st-nightsweep2-nc-20260930 与 ai/st-nightsweep2-ne4-20260930/NE4-landing-bottleneck 实测 rev-list dev..br=0（NE4 主体 10aca61f22 已直提 dev）——按卡面跳过"
  nb2: "6 commits（8954523b7f B8 翻译册净删/b7c3aa0a81 B10 排班/ae952d32c9 B11 deprecated/7bdf98e8dc B13 F56 销账/f3030556bc B15 挂账/a8697815ab B17 #439+#440）"
  nf: "6 commits（112f5b0c48 F4a/1012518572 F4b/ef9f22130b F1/7194643e4b F5/0260526fac F3/4cef321180 F6）"
  nb1: "1 commit（1a5521db4f B 组挖矿裁定卡六件）"

collision_findings:
  ruling_numbers:
    - "NB2 分支裁定#438（F56 销账）vs dev 在册裁定#438（NC 车道 C9 三小件，706752aa00 落）——撞号 → 改号核订 #449（claim_449 原子占号，#419→#420 先例），99_skipped #36 引用面同步改指"
    - "NB2 分支 #439/#440 无撞号原号保留（claim_439/440 系 NB2 车道原占）"
    - "NF 分支裁定#446（L09-C01 追认）vs dev 在册 #437（同源裁定，#ARCH-367 载体已落+nf2 9938b2ed8b 同判『不另取新号防同源重复立法』）——同源不另立新号（宪法 §4.2 内收）：F1 追认注记并入在册 #437 summary，SKEL/ARCH-369 引用面改指 #437"
    - "NF 分支裁定#447（F5 通电）vs dev 在册 #447（NC 车道 C8 W-178 落冻）——撞号 → 改号核订 #450（claim_450 原子占号）；schedule_gate_policy 两处 stale #436 引用同步改指 #450"
    - "取号器实况：在册最大 #448；本车道 claim_449/claim_450 独占；nf2 F9① 后占 #451/#452 不冲突"
  arch_369: "#ARCH-369 两侧逐字节一致（dev 侧系 ND 706752aa00 主区吸收），自动合并去重；本车道改其 related_rulings 与描述的裁定号指向"

conflict_resolutions:
  - file: docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
    mode: "热注册表并集+计数复验"
    detail: "dev #435-#448 全保留 + NB2 三笔（#438→#449 改号+编号核订注记/#439/#440 原号）；NF 一笔（#447→#450 改号+编号核订注记）；NF #446 不落册（并入 #437 追认注记）"
    verify: "yaml safe_load 265 条零重复（NB2 阶段）；尾序 #448→#449→#439→#440"
  - file: docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
    mode: "dev 现状+NB2 净删 3 条（wo001_003 悬空指针，Owner 已批）+NF 新增 1 条（cleaning_disagreement_stats）"
    verify: "NB2 阶段 7944 条（dev 7947-3）；wo001_003=0"
  - file: src/zephyr/data/config/known_data_gaps.yaml
    mode: "分支追加（dev 零漂移）"
    verify: "gaps 71→73（index_valuation_daily_v2+reconciliation_differences），parse 过"
  - file: docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml
    mode: "分支追加 retirement_schedule（dev 零漂移）"
    verify: "parse 过+retirement_schedule 在册"
  - file: src/zephyr/trading/windows_service.py
    mode: "分支追加 [DEPRECATED] 标记（dev 零漂移）"
    verify: "py_compile 过"
  - file: docs/_working/fullconnect_campaign/99_skipped_for_owner.md
    mode: "自动合并+#438→#449 引用改指"
  - file: docs/_working/decision_map_campaign/links/L09_review/SKEL.md
    mode: "分支 SEALED 封矿+#446→#437 引用改指（nf2 已落 _20260924 副本同语义 9938b2ed8b，非日期副本由本 train 补齐，双副本一致）"

infra_finding_and_fix:
  dead_bag: "q-20260930-st-nightsweep2-merge-20260930-0001（NB2 内容袋 6 文件）"
  dead_reason: "module_translation_registry.yaml 自证读回无法判别（ours 存在身份判不了的条目）"
  root_cause: "落地器 _noop_absorption_verdict_inner 顺序缺陷：_index_all_sides 先于 _split_passthrough_and_drift 剔除——热册 unique_key 标量元数据族（非 dict 块身份判不了）在主合并路径（先剔后索）正常产出 merged==ours，读回路径（先索后剔）撞『身份判不了』死信。merged==ours 的合法袋（纯删/纯增，theirs==base 常态）触任意含 unique_key 族的册全量误死；实测裁定册同雷复现=本夜热册袋共性阻塞（c9-final2 在飞袋同面）"
  fix: "scripts/governance/commit_queue_landing.py verdict 路径与主合并同序对齐（先 _split_passthrough_and_drift 剔直通族再索引）；零语义放宽（结构漂移 fail-closed 仍在剔除函数内先行；_header_level_absorption 幂等重算）"
  fix_bag: "q-20260930-st-nightsweep2-merge-20260930-0002（commit_queue_landing.py+test_commit_queue_landing.py 2 文件）"
  fix_verify: "真实死袋 4 册 blob 复验 verdict 修前全灭→修后全 PASS；新增回归尺 2 例（纯删/纯增）先红后绿；test_commit_queue_landing.py 全量 76 例绿（进程外实测）；ruff check/format 双净"
  ownership_disclosure: "该文件系 NF 分支在途触面（F3 EV-02/04 +98 行）——修复块位于 _noop_absorption_verdict_inner 与 NF 增量（EV 函数+测试）不同区域，NF merge 三向可干净并集；非避让图在册领地"

landing_plan:
  mode: "SW12 配方：scratch worktree 逐支 git merge --no-ff --no-commit → 冲突解决 → git_commit.py --enqueue 快照袋（serializer 落地不碰主区 407 脏面）"
  train: "q-0002 修复袋 → NB2 内容袋（6 文件重投）→ NF 内容袋（18 文件）→ NB1 内容袋（7 文件），FIFO 顺序落地"
  message_discipline: "原分支 [GW:] 尾行不可复抄已剥离；message 注 [merge train·原分支=<名>]+撞号治愈全录；净删册带 [allow-mass-deletion] 原批语义标记"

hash_mapping: "落地后回填（原 commit hash → 袋号 → 落地 hash）"
```
