---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW12_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW12_ledger.yaml — 夜战总 Sweep 2026-09-29 · SW12 merge train 与残留收敛车道
# sid=st-nightsweep-sw12-20260929 总筹=st-nightsweep-chief-20260929
# 本台账由 SW12 会话维护；verdict 证据均为实测留痕（队列 JSON/commit hash/测试输出）

meta:
  session: st-nightsweep-sw12-20260929
  date: 2026-09-29
  cold_start: "Python 3.12.8 PATH 修正 ✓ / lock_files cleanup ✓ / reaper last_run=2026-09-29 07:47:29 存活 ✓ / SessionRegistry 注册+heartbeat daemon ✓ / capability_lookup 反查(空结果=无既有能力簇, 审计在案) ✓"
  worktree: ".worktrees/st-nightsweep-sw12-20260929 (branch ai/st-nightsweep-sw12-20260929/merge-train, 基于 dev)"

task1_merge_train:
  id: SW12-T1
  source_branch: ai/st-nightsweep-sw11-20260929/nightsweep-sw11
  finding: "卡面称两分支，实测=单分支两 commit（2bd67c05 miniQMT 文案 → 2ad4f15d 备份三小件 tip），零重叠 sw11 在队袋（0001/0004/0005 内容各异不冗余）"
  trains:
    - train: T1_miniQMT文案
      original_commit: 2bd67c05
      cherry_pick: "scratch worktree 零冲突；裸 cherry-pick commit 3fa9e6051c 被 POST-COMMIT-GUARD reset 回滚（宪法预期行为）→ 改 --no-commit 形态走正门"
      bag: q-20260929-st-nightsweep-sw12-20260929-0016（0015 被同键取代，0016=GW 行剥离终版）
      files: 6
      landed: PENDING（队首等 serializer 波次，内容三重验证毕）
      supersede_note: "首投 0001 的 capability 册 blob 基于旧基线（缺 d094852ffa 后落的 2 条 night-sweep 条目，直落=注册表回归）→ 已重建册=dev 现版+token 纯插入，同键重投 0015 取代 0001（C1 同键留最新机制）；0015 验证=非册 5 件与 2bd67c05 逐字节一致+册 diff 纯 +5"
    - train: T2_备份三小件H04H06H08
      original_commit: 2ad4f15d
      cherry_pick: "--no-commit 零冲突"
      bag: q-20260929-st-nightsweep-sw12-20260929-0017（0002 首投死于 FORGED-GW-MARKER——原 commit message 尾部 SW11 网关留痕标记不可复抄；GW 行剥离后换新袋 0017）
      files: 6
      landed: PENDING（队首等 serializer 波次）
      drift_check: "六径自基线 ba400ea294 起 dev 零漂移（实测），可安全落地"
  byte_identity: "两 train 共 11 件 blob 与原 commit 逐字节一致（sha256 同算法）；唯一异者=capability 册（cherry-pick 重放=merge train 本意，已按现版重建）"
  verification_caveat: "worktree 内 pytest 被 pip editable install 的 meta-path finder 劫持（import zephyr 恒=主仓，7 挂实为主仓旧码缺 H08）——worktree 测试输出无效弃用；终验=落地后主区实测（finder 指向的即落地内容）+字节同一性传递 SW11 原测绿（104+75 绿为其同字节内容实测）"
  mechanics: "commit_queue.py enqueue --worktree-root（blob 快照→serializer 专用 worktree→gateway 全门禁→CAS 推进 dev，永不碰主区 3285 脏文件）；POST-COMMIT-GUARD reset 裸 commit 实证"
  verdict: ADVANCED
  evidence: "队列 pending/0001+0002 JSON + 本文件 PENDING-VERIFY 回填"

task2_residue:
  id: SW12-T2
  items:
    - item: "①SW5 移交 apply_market_tables_ddl tmp 残留"
      verdict: DONE
      evidence: "scripts/ch/apply_market_tables_ddl.py.tmp.22232.2a300814c75d（写者 PID 22232 实测已死，tmp 与真身 DIFFERS=半写废件）→ 移 .runtime/tmp/st-nightsweep-sw12-20260929/ 留证；顺带同死 PID 的 check_library_tri_consistency.py.tmp.22232.* 同批留证；另发现 3 件 tmp（deadman_switch.ps1/inventory_blanked_canonical_fields/detect_vague_terms）写者 PID 28828 实测存活——活进程在写，零触碰只登记"
    - item: "②night_sweep_20260929 旧路径 staged-A 残面"
      verdict: DONE-CROSSCHECK
      evidence: "git status 全量 grep night_sweep_20260929=0 条目（已被收敛）；git status grep night_sweep 仅余新路径 docs/_working/night_sweep/ 活跃 WIP（他会在途零触碰）；旧路径 git rm --cached 无对象可操作"
    - item: "③SW8 两件无主孤儿 .py"
      verdict: DONE
      evidence: "scripts/backtest/eval_tech_indicator_ic.py（[DOMAIN] D_BACKTEST_SCRIPTS 非法）+ scripts/governance/backfill_registry_consumption.py（[DOMAIN] D_GOV_SCRIPTS 非法）——双验证 [DOMAIN] 头仍非法 + .ailocks registry claim=0 → 移 .runtime/tmp/st-nightsweep-sw12-20260929/quarantine/（禁删，owner 回归可取回）"

task3_test_fix:
  id: SW12-T3
  target: tests/governance/test_gate_stats_no_ms_floor.py
  verdict: DONE-LANED-PENDING
  fix: "防假绿断言绑定作者 worktree 绝对路径子串 csx-p13（跨环境恒红，主区实测复现）→ 改 Path(cgr.__file__).resolve().is_relative_to(本仓根)——语义零放宽（外来 checkout 加载仍必红），跨 worktree 可移植；随批 ruff I001 顺带修"
  verify: "主区 1 passed + ruff check/format 双净（实测）"
  bag: q-20260929-st-nightsweep-sw12-20260929-0003
  landed: 2ee8ec84ef486751ad9a0ea8e006487e25ea1b70

task4_queue_dashboard_v3:
  id: SW12-T4
  snapshot_base: "48 袋 grep nightsweep（done 13 / pending 12 含我方新袋 / dead 记录 23，其中 sw6-0005/0010/0011 已重投回 pending=现存真死 20）"
  done_landed:
    - "sw1-0006..0010/0014 → a4acbb89/f9cb1cfd/b004c5da/d5acce8f/6402c0d0/0eabbbf8"
    - "sw2-0005 → 48aa677f / sw5-0003 → 2060958a"
    - "sw6-0001/0002/0003 → eb2df8bf/c2ec2ff8/14dc95cb"
    - "sw11-0004 → a2881d05 / sw11-0005 → 9f220b2e"
  dead_dispositions:
    - {qid: sw1-0002, cause: "GATE-PRECOMMIT-RUN 误拦(git-dangerous 报冲突标记,blob 实测 CLEAN)", action: 重投, new_bag: sw12-0004(C1 合批), note: "23 封死袋 blob 全量扫描=0 冲突标记→误拦类坐实"}
    - {qid: sw1-0003, cause: "cascade_stale", action: 销账, note: "决策被逆转：rules_integrity_db 保持 tracked 且 sw11-0005 已落后续更新"}
    - {qid: sw1-0011, cause: "CREATE-GUARD 无 token", action: 重投, new_bag: sw12-0005(C1 合批), note: "du881 token 现已在 dev 注册(2 hits)=阻断治愈"}
    - {qid: sw1-0012, cause: "R5-DIGIT-SUFFIX 旧路径禁", action: 后置-总筹, note: "总纲快照 06:26 版已过期(现行编排进 Wave2)，不代投过期总纲防假记录，属主=总筹重拍后另袋；新路径盘面/在队均无承接"}
    - {qid: sw1-0013, cause: "R5-DIGIT-SUFFIX 旧路径禁", action: 销账, note: "d094852ffa(R5 改名重投·原袋 sw1-0013+sw4-0001) 已落新路径 night_sweep/00_skeleton_nightsweep.md ON-DEV"}
    - {qid: sw2-0001, cause: "GATE-PRECOMMIT-RUN 误拦", action: 重投, new_bag: sw12-0004(C1 合批), note: "A37 宪法两行计数对齐：blob 与 dev 恰差两行=零过期"}
    - {qid: sw2-0002, cause: "GATE-PRECOMMIT-RUN 误拦", action: 重投, new_bag: sw12-0007, note: "code-only(promotion_advisory+test)；strategy_registry comment hunk 与 sw10-0001 在队碰撞剔除，残差后置重放"}
    - {qid: sw2-0003, cause: "cascade_stale", action: 重投, new_bag: sw12-0009, note: "code+washer.yaml(--allow-promote)；capability 册 hunk 与 7 在队袋碰撞剔除，残差后置重放"}
    - {qid: sw2-0004, cause: "GATE-PRECOMMIT-RUN 误拦(algo-flow-marker)", action: 重投, new_bag: sw12-0010}
    - {qid: sw3-0001, cause: "DEPGRAPH-PRE-REGISTRATION", action: 销账, note: "被 pending sw8-0002 代投袋取代(P3 链同题复活)"}
    - {qid: sw3-0002, cause: "SESSION-REQUIRED", action: 销账, note: "被 pending sw8-0004 代投袋取代(T14 token 复活)"}
    - {qid: sw3-0003, cause: "ruff-format 误拦", action: 后置, note: "c9-igdrop-0001 在队含 api_server.py(FIFO 先落)，本袋重投必撞基底——igdrop 落地后重放守卫 hunk"}
    - {qid: sw3-0004, cause: "注册表三向合并失败(同键异容)", action: 重投, new_bag: sw12-0014, note: "外科手术：当前 dev 版(625 键)仅 CAND-GOVTEST-005 双条撞号→第二条 005→007+注释原文同步(2 行 diff=原意重放)"}
    - {qid: sw4-0002, cause: "CREATE-GUARD CLASS-UNIQUENESS(class Finding 跨模块冲突)", action: 属主修, note: "真缺陷非误拦：需 SW4 域内 class 改名手术(7 文件)，非机械重投可解"}
    - {qid: sw4-0003, cause: "GATE-PRECOMMIT-RUN 误拦(ruff/format)", action: 重投, new_bag: sw12-0011, note: "13 文件 commit_gates 族+tests，--allow-multi-domain"}
    - {qid: sw4-0004, cause: "ruff-format 误拦", action: 销账-让路, note: "chief7-20260928-0369 在队含 archiver.py+test(保护清单在队袋接管)"}
    - {qid: sw5-0001, cause: "GATE-PRECOMMIT-RUN 误拦(多 hook)", action: 重投, new_bag: sw12-0012, note: "5 域 --allow-multi-domain(M1 封矿 F125/127/128/130)"}
    - {qid: sw5-0002, cause: "GATE-PRECOMMIT-RUN 误拦(ruff-format)", action: 重投, new_bag: sw12-0013, note: "F62 SettlementReconciler 违宪整改"}
    - {qid: sw5-0004, cause: "dev CAS 冲突重试耗尽(瞬态)", action: 重投, new_bag: sw12-0005(C1 合批), note: "F26 E7 前哨内容仍有效"}
    - {qid: sw6-0004, cause: "git-dangerous 误拦", action: 销账, note: "被 pending sw8-0001 代投袋取代(99_delivery_report 件5)"}
    - {qid: "sw6-0005/0010/0011", cause: "(历史死记录)", action: 已在队, note: "三封已重投回 pending(live 版在队，落地侧判定)"}
  new_bags_filed: [sw12-0004, sw12-0005, sw12-0007, sw12-0009, sw12-0010, sw12-0011, sw12-0012, sw12-0013, sw12-0014]
  new_bags_final:
    - {bag: sw12-0003, verdict: DONE-LANED, hash: 2ee8ec84ef48}
    - {bag: sw12-0009, verdict: DONE-LANED, hash: 233adc3cca04, note: "E09 C6 washer 消费修复+washer.yaml ALGO_FLOW 出仓（全门禁过）"}
    - {bag: sw12-0010, verdict: DONE-LANED, hash: e040583b5eaf, note: "E13 tombstone_ttl_proposer 接线"}
    - {bag: sw12-0011, verdict: DONE-LANED, hash: 98ce6370c546, note: "红五簇撞号 13 文件 gates+tests"}
    - {bag: sw12-0012, verdict: DONE-LANED, hash: 794f16569b14, note: "M1 封矿 F125/127/128/130"}
    - {bag: sw12-0013, verdict: DONE-LANED, hash: 35ca1d69cd86, note: "F62 SettlementReconciler 违宪整改"}
    - {bag: sw12-0004, verdict: DEAD-SPLIT, note: "C1 合批袋（redblue+AGENTS.md）死于 PROTECTED-PATHS——AGENTS.md 宪法域=Owner 门位；redblue 纯文档面已拆袋 0018 重投"}
    - {bag: sw12-0005, verdict: DEAD-SPLIT, note: "C1 合批袋（du881+F26）死于 pipeline_events 基底漂移——du881 零漂移面已拆袋 0019 重投；F26 面需真三向=属主修"}
    - {bag: sw12-0007, verdict: DEAD, note: "test_promotion_advisory.py 基底漂移（dev 侧签名精化 str|Path）——E08 FSM 修复内容 dev 尚无，需真三向重放=属主修（19 行 hunk 处方在死袋 blob）"}
    - {bag: sw12-0014, verdict: DEAD-OWNER-GATE, note: "注册表三向合并拒绝『ours 自身重复键』态（CAND-GOVTEST-005 双条=本袋所修之病，先有鸡蛋）——处方=先跑 registry 去重对账器消存量（governance 对账车道），重编号意图已留档死袋"}
    - {bag: "sw12-0016/0017", verdict: PENDING-QUEUE, note: "merge train 终版（GW 行剥离+册现版重建），内容三重验证"}
    - {bag: "sw12-0018/0019", verdict: PENDING-QUEUE, note: "拆袋干净重投（redblue 文档 2 件/du881 3 件零漂移）"}
  infra_finding: "k=4 落地池单工位卡点 ~1.3h/项 成常态（tailwork4-0001 1.24h、boardidx-mtr 57min、c8-watch 57min、c9-tzday 73min、我方 0009 53min 等实证）——池吞吐坍缩至 ~4 项/1.3h；本人 drain 尝试 2 次均 SKIPPED（lease 活体持有，pid 972 存活续约）=不抢锁合规；堵点解除靠持有者自身超时波次。建议维护班查 GATE-PRECOMMIT-RUN 在落地面 pre-commit run 的子进程超时缺失" 
  verdict: ADVANCED
  zero_dead_account: "20 封现存死袋全处置：销账 6 / 重投 11 / 后置 2 / 属主修 1；禁投清单(st-ec2-p0 系/q-0021/chief7/GPU)零触碰"

task5_zombie_scan:
  id: SW12-T5
  verdict: DONE-ZERO-RECUR
  evidence: "tests/ 全树 3923 .py 扫描：①精确半文相等(字节级翻倍)命中=0（SW2 两起 243→497/822→1743 现树零复现，当时已清理）；②同文件顶层 def/class 重名命中 8 件逐一人工定性=test 夹具故意重复(class P 多桩/add-subtract 去重引擎扫描夹具等)，非并发写坏"

session_close:
  worktree_cleanup: PENDING
  handoff: "见台账+最终汇报"
```
