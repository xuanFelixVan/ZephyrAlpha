---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# W2MERGE2_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# W2MERGE2_ledger.yaml — 夜战总 Sweep2 2026-09-30 · W2-MERGE2 合并收编续作车道
# sid=st-nightsweep2-merge2-20260930 总筹=st-nightsweep-chief-20260929
# 前棒=st-nightsweep2-merge-20260930（超时，计划/撞号核订/死袋修复留台账 W2MERGE_ledger.yaml，本车道执行续作）

meta:
  session: st-nightsweep2-merge2-20260930
  date: 2026-09-30
  cold_start: "Python 3.12.8 PATH ✓ / setup_dev_env --check ✓ / lock cleanup SALVAGED×2 + reaper 存活(scanned=21 killed=0) ✓ / SessionRegistry 注册+heartbeat ✓ / capability_lookup.find('merge train registry ruling renumber')=0 hits 审计留痕 ✓（首投被 CAPABILITY-LOOKUP-REQUIRED 预检拦后补跑）"
  worktree: ".worktrees/st-nightsweep2-merge2-20260930 (branch ai/st-nightsweep2-merge2-20260930/merge-train, 基于 dev 71b7c9cbd1)"
  mission: "三分支 13 commits 收编进 dev（NB2=6 / NF=6 / NB1=1）；前棒计划现成执行为主"
  inheritance: "前棒 scratch(.worktrees/st-nightsweep2-merge-20260930) 留 NB2 六文件已解决 staged 现场（对照参考）；其裁定号占号 claim_449/claim_450.json 在案（.runtime/ruling_claims/，2026-09-30T05:36 原子占）本车道继承使用；前棒落地器死袋修复 q-0002 已落地=249ed58bb3"

bags_enqueued:
  FIFO_order:
    - {qid: q-20260930-st-nightsweep2-merge2-20260930-0001, files: 6,  content: NB2 内容袋}
    - {qid: q-20260930-st-nightsweep2-merge2-20260930-0003, files: 2,  content: q-0002 修复重放袋（前置）}
    - {qid: q-20260930-st-nightsweep2-merge2-20260930-0004, files: 16, content: NF 内容袋}
    - {qid: q-20260930-st-nightsweep2-merge2-20260930-0005, files: 7,  content: NB1 内容袋}
    - {qid: q-20260930-st-nightsweep2-merge2-20260930-0006, files: 1,  content: F5 钉值测试随批翻转袋}
  total_files: 32
  q0002_note: "前棒修复袋编号 q-…-merge-20260930-0002；本车道袋号 0002 缺号（0001 后直接 0003 起，enqueue 顺序使然无影响）"

critical_finding:
  q0002_fix_regressed: "q-0002 修复（249ed58bb3 _noop_absorption_verdict_inner 直通族先剔后索）被后行 D1 stats_lock 手术 4bab350d77 覆盖回退——dev HEAD 实测其自带回归尺 TestNoopVerdictPassthroughOrder 双红（主区+scratch 双验证=dev 存量破面非本车道引入）。若不治本，本车道全部热册袋复演 q-0001 型死信。处置=原 hunk 逐字重放（+2 行覆盖史注记）随袋 q-0003 前置落地，回归尺随袋（进程外 2 尺绿+ruff 双净）。D1 手术归属道（st-gate-rationalize-20260929）应对齐知会。"

branch_commits_mapping:
  nb2: "6 commits：8954523b7f(B8 翻译册净删)/b7c3aa0a81(B10 排班)/ae952d32c9(B11 deprecated)/7bdf98e8dc(B13 F56 销账→裁定#449)/f3030556bc(B15 挂账)/a8697815ab(B17 #439+#440) → 袋 q-0001（6 文件）→ 落地 hash 待回填"
  nf: "6 commits：112f5b0c48(F4a token)/1012518572(F4b bundle 契约+72h 卷)/ef9f22130b(F1 L09-C01 追认→并入#437)/7194643e4b(F5 通电→裁定#450)/0260526fac(F3 EV-02/04)/4cef321180(F6 F04 三门) → 袋 q-0004（16 文件）+q-0003（landing.py+测试 2 文件）→ 落地 hash 待回填"
  nb1: "1 commit：1a5521db4f(B 组挖矿卡六件) → 袋 q-0005（7 文件）→ 落地 hash 待回填"
  local_merge_commits: "scratch 分支收口：NB2 merge=f68a2b05b7（gateway --merge-finalize）；NF 本地收口被 TRANSLATION-COVERAGE 阻（门读 REPO_ROOT 主区真源，翻译册条目未落地前不可过）——NB1 改内容级并集（git apply --3way+checkout 六新件）不入本地 merge 拓扑；袋投递与 dev 落地不受影响（快照袋语义）"

conflict_resolutions:
  - bag: NB2(q-0001)
    items:
      - "ruling_registry.yaml 两侧册尾追加错位（dev 265 条 vs 分支三笔）：dev 全保+分支尾三笔追加；#438→#449 改号（撞 dev 在册 NC #438 706752aa00，依 #419→#420 先例+claim_449 继承）+编号核订注记；#439/#440 原号。safe_load 268 条零重复，尾序 #454→#429→#449→#439→#440"
      - "99_skipped_for_owner.md 行 34-36：dev 现状优先（Owner 2026-09-30 夜批回执注记为超集）+行 36 补正式裁定改指注记（裁定#449，原分支 #438 撞号改订）"
  - bag: NF(q-0004+q-0003)
    items:
      - "ruling_registry.yaml 两处错位冲突：dev 全保（含 NB2 三笔+#446 NC/#447 NC）+分支 #447→#450 改号册尾追加（title 编号沿革更新+summary 编号核订注记，claim_450 继承）；分支 #446 不落册=同源并入 dev 在册 #437（宪法 §4.2 内收）：#437 summary 补 ⑥F1 追认注记。safe_load 269 条零重复，尾序 #449→#439→#440→#450"
      - "architecture_issue_registry.yaml：#ARCH-368（dev 新增）保留+#ARCH-369 related_rulings 改指 ['裁定#437','裁定#450']+描述两处核订注记+所涉袋行同步（813 条 parse 过）"
      - "tests/governance/test_commit_queue_landing.py：q-0002 回归尺（TestNoopVerdictPassthroughOrder）与 NF EV-02/04 测试类文件尾并集+ruff format 接缝"
      - "引用面改指：L09_review/SKEL.md（非日期副本）6 处 #446→#437+行 150 并入注记（与 nf2 9938b2ed8b 已落日期副本双副本一致）；schedule_gate_policy.yaml 2 处 stale #436→#450"
  - bag: NB1(q-0005)
    items:
      - "capability_canonical_file_registry.yaml 与 NF 共触：内容级三向并集（git apply --3way 干净施加，NF +8 与 NB1 +30 共存，parse 过六条目全在册）；六新件 .md checkout 落位（CREATE-GUARD token 六件实测已在册免登记）"

skipped_items:
  - "NF2 车道四笔直提（0e39637418/9938b2ed/f8198b8fc3/6ab478e326）与 NF 分支触面逐件对照：仅 ruling_registry/SKEL.md 两文件交叠，无一件被 HEAD 完全超越需跳过——9938b2ed 落 SKEL 日期副本与分支非日期副本互补（双副本一致由本 train 补齐），0e39637418/f8198b8fc3 的裁定册增量（#448/#451-454）在 dev 全保留并入并集。跳过件=0，CROSSCHECK 记录于各袋 message"

tests:
  nb2: "test_module_translation_loader+test_next_ruling_id+data_supply/test_supply_conservation = 41 passed/1 skipped"
  nf_nb1: "test_quarantine_manifest+test_cleaning_disagreement_stats+test_registry_ledger_baseline+test_ai_secret_exposure = 38 passed/7 skipped（PYTHONPATH 指 scratch src，zephyr 包 usercustomize 解析主区所致环境处置）"
  landing: "test_commit_queue_landing 全量 84 例：修复重放后 TestNoopVerdictPassthroughOrder 2 尺绿（修前 dev 存量双红）；合批 ruff check/format 双净"
  env_notes: "翻译册/裁定册/架构议题册/capability 册/秘钥册 yaml parse 全过；5 个 .py py_compile 过"

nf_debt_compensated:
  pin_flip: "NF 7194643e4b8 落 ai_exposure 106 条时漏改钉值测试 test_ai_secret_exposure.py 二用例（其自携处方'须随 YAML 块落地同批改'）——本车道 q-0006 机械翻转（forbidden 7 键白名单断言+guard_active/baselined），1 文件袋，归属披露在 message"

open_items:
  - "落地 hash 回填：袋 q-0003/0004/0005/0006/0007 → dev 落地 commit（队列 serializer 侧，落地后 git log 核对）——本车道收尾时队列仍在消化（全夜多会话拥堵，0002 处理中）"
  - "q-0001 死信已定案（见 merger_bug_finding）；migration_registry.yaml retirement_schedule 22 行排班面待合并器修复后另投或由总筹裁直提"
  - "q-0002 袋定性：16:50 merge-finalize 遇锁自动改道入队所成杂袋（内容=scratch 内生成器刷新 blueprint.md 族，非本车道计划内容）——已在 processing，若落地=衍生注册表刷新面（与 dev 407 脏面同源生成物）；若死信=无害清退，均不阻断本 train"
  - "scratch worktree 保留（.worktrees/st-nightsweep2-merge2-20260930+分支 ai/st-nightsweep2-merge2-20260930/merge-train 含 NB2 本地 merge 收口 f68a2b05b7），重投/对照能力保持至总筹裁"
  - "TRANSLATION-COVERAGE 门读 REPO_ROOT 主区真源与 worktree 施工语义不适配（NF 本地 merge 收口被阻）——登记为门改进候选，非本车道处置"

merger_bug_finding:
  id: "MERGER-TOPKEY-SWALLOW（本车道呈报值班/维护班，处方②）"
  symptom: "three_way_merge_registry_yaml 对 theirs 新增顶层 map 族整族丢弃：migration_registry.yaml retirement_schedule（registered_at/registered_by 排班块）在无漂移快进 case（ours==base）被吞，merged 仅余 {ttl, entries}（仿真复现脚本=本台账附录；q-0001 死因全文在 .runtime/commit_queue/dead/）"
  verdict_side: "落地前自证读回吞没检测正确拦截（'内容被合并器吞没'死信）——q-0002 修复重放（q-0003）后该检测链路健康，非误杀"
  scope: "is_registry_mergeable=_registry/catalogs 前缀 yaml；config/src yaml（known_data_gaps/schedule_gate_policy）不走合并器无此险（已仿真/分类双验证：gaps 73=73 增量存活）"
  suspect_site: "_plan_insert_splices 只规划条目级插入未规划新顶层族级插入（族含多行 map 块非 entry block）"
```
