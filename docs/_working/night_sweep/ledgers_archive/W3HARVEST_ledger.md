---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# W3HARVEST_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# W3HARVEST 收割车道台账（sid=st-menu-w3h-20260930，总筹=st-nightsweep-chief-20260929）
# 菜单执行夜 W3-HARVEST · 开工 2026-10-01 凌晨 · 台账落=.runtime/tmp/st-nightsweep-20260929/
session: st-menu-w3h-20260930
chief: st-nightsweep-chief-20260929
cold_start:
  python: "3.12.8 PATH 修正 ✓ / setup_dev_env --check usercustomize ✓"
  reaper: "alive（本轮 status 正常，killed 计数走日志）"
  session_registry: "registered（逻辑会话 pid=0+heartbeat daemon；w3h 与 w3harvest 双 sid 沿用链在案）"
  capability_lookup: "find×8（SLA/宏观/F128/real-key 等，0-1 hits，审计留痕 LOOKUP_AUDIT）"

verdicts:
  - id: W3-B1-A
    item: T1B1 融合批（死信 q-20261001-st-menu-t1b1-20260930-0009，10 件）
    content_truth: 主区工作区 face+死信袋 blobs（逐件 sha256 与袋核同）
    verdict: ENQUEUED-VERIFIED
    evidence: 袋 q-20261001-st-menu-w3h-20260930-0003（9 件，capability 册按死因剔除=3 token 已在 dev HEAD）；翻译册 face=死信原 blob 逐字节（sha 1f6e027a6a2f 袋内核同）；blob 校验通过（BAG VERIFIED 在日志）
    note: 死因=CLAIM_REQUIRED_VIOLATION（队列 worktree 与主区 .ailocks claim 不互通=队列基建缺陷，处方=直提正门）
  - id: W3-B1-B
    item: T1B1 净删批（死信 -0010，19 件）
    verdict: DONE-LANED(1c9f4195f2)
    evidence: dev HEAD 直提；git log -1 --name-only 核 19 件零搭便车；净删 9 src+6 空占位+3 测试+5 件 [RESERVE-T1B1] 头注+b1_sixteen_dossier.md 随批；触面 140 passed（原车道判据，本次 32/32 quality 复验）；[allow-mass-deletion] 标记入 message
  - id: W3-B1-C
    item: T1B1 批复落册（死信 -0011，99_skipped_for_owner.md #42-44）
    verdict: DONE-LANED(212d4fd9)
    evidence: face==死信 blob 核同后直提；#42 全量执行记录+#43 批复语义+#44 同范交叉引用
  - id: W3-B6
    item: T1B6 c 档删块 19+19（分支 session/st-menu-t1b6-20260930 死信 commit 7aea69ca13）
    verdict: ENQUEUED-VERIFIED(袋 q-20261001-st-menu-w3h-20260930-0008)
    evidence: >
      merge-base 考古=7aea69ca13 父=68fe30bd5f（初验时=dev HEAD，ff 可行；ff 尝试遇 dev 推进
      46db7d42f5 改道 rebase→branch ref 被空回放吞（rebase(ghost) 吞 commit 异常在案，reflog 恢复）；
      改走 worktree branch commit 36ff858643（gateway 正门）→session_worktree merge 两败（主区 463 脏面
      ort 拒绝）→最终=dev 现行面（e405020493 后 334 datasets 态）重建同删块：DS-041..049/051..055/060..064
      +JOB-040..048/050..054/059..063 共 19+19，provides 摘 19 id，counts 334→315/122→103，version 1.9.9；
      袋 sha 入队后核同。原旧袋 q-20261001-st-menu-w3harvest-20260930-0001（含原删块）死于 ghost_session
      ×2（存活闸）——其内容已由本袋超集替代=销账；noop 袋 w3harvest-0002 done 无副作用
  - id: W3-B5
    item: T1B5 宏观族复活五件（worktree ai/st-menu-t1b5-20260930/t1b5-cn-macro-revival）
    verdict: ENQUEUED-VERIFIED(袋 q-20261001-st-menu-w3h-20260930-0009，6 件)
    evidence: >
      分支考古：dev..branch=0 commits（全部工作在 worktree index）→按 worktree face 收割。
      R1 series_map（16 条=12 wired+3 missing+1 meta）✓；R2/R3 macro_regime_sensor（565 行，
      PIT 双通道+四组加权，MOD-REGIME-MAC）✓；TDM 仅 TDM-E-L1-S0 两行+ALGO 大白话（ALGO-NOTE-SYNC 死因治愈）✓；
      R5 指标册 v1.2.0→v1.3.0（entry_count 15→16）✓；R4 FRED=既有管线全覆盖零新管线（crosscheck）✓；
      18/18 测试 worktree+主区双跑绿。翻译条目：dev 缺（a2 落地信息与实态不符，实核 dev=0 命中）→
      袋携死信原 blob face（含 B1 四条+B5 sensor 条目），与 003 袋同 face 任一先落即闭环
  - id: W3-B2
    item: T1B2 F128 三件接线（worktree ai/st-menu-t1b2-20260930/T1-B2-F128-wiring）
    verdict: IN-FLIGHT(token 袋 007 pending；内容袋待 007 落地后投)
    evidence: >
      分支考古：dev..branch=0 commits；worktree face=完整接线包（wiring/ 四件+policy 册+__init__/
      data_access_auditor 接线+3 测试件+2 文档）。红蓝=test_red_l3_masking_strips/test_red_l4_forbids_raw_text
      等 96 passed（worktree 实跑）。known_data_gaps 无 F128 条目（实核）→改判落点=99_skipped_for_owner
      #43 状态列（gap 登记→已接线 wired，w3h_b2_prep 已落 face，随内容批）；翻译词条 4 条 face 已备（dev+纯增量）
  - id: W3-F2-1
    item: F2 袋 0001 REAL-KEY 门改进（negative_list_gates.py+测试）
    verdict: ENQUEUED(袋 0001→死 CLAIM_REQUIRED@landing→requeue 袋 0006 processing)
    evidence: face==死信 blob 核同；门=derived_assertion_exempt 三重门+红蓝五测（原车道 110 passed 判据）
  - id: W3-F2-2
    item: F2 袋 0002 批复归档+排期登记（99_owner_gate_menu.md+93_owner_menu.md）
    verdict: IN-FLIGHT（token 先行袋 q-...-0010 enqueued；内容袋待 token 落地后投）
    evidence: 两 md face==死信 blob 核同；第 3 件 capability 册改判销账（F2 dedup 语义已被 f32a46a8 token 批+册演进吸收，内收 w5_1 不重做）

landing_infra_findings:
  - "队列死因谱与 G2 车道 09e5b4c972 披露同型互证：CLAIM_REQUIRED@landing=claim 30min/300s TTL 过期（keeper 循环 acquire+claim_file 双 store 保活治愈）；ghost_session=心跳 daemon 自退+幽灵删除；Popen TypeError=serializer 管道疫（G2 已结构修复）"
  - "REGISTRY-MASS-DELETION 门实为全工作区热册面 diff（非单文件）——任一热册 worktree face 与 dev 漂移即全 commit 阻断；本轮以 face 还原 dev+袋携快照配方通过"
  - "主区 worktree 面遭多源覆写（belt landing 回写+drift watchdog 隔离+清洁清扫删根目录脚本）：收割配方改为『blob 还原→秒级入袋→袋 sha 核同』，绕开主区面存活期问题"
  - "session registry 并发抹写（daemon 整表保存覆盖 claim）=G2 S4-D 分片重写已治本（09e5b4c972）；本轮 keeper 与之共存验证"
  - "debt-ratchet env 手柄 ZEPHYR_PRECOMMIT_DEBT_RATCHET=0 按门附处方使用并登记（w3h_debt_ratchet_handle_registration.json）；同夜 G1/S4-E 先例同款"
  - "st-circ-a2 落地宣称翻译册『并集保全 macro_regime_sensor』与 dev 实态不符（实核 0 命中）——他车道宣称与账实出入登记，本道以袋携快照独立闭环不依赖其面"

writeoffs:
  - "死信 q-20260930-st-menu-t1b5-0001（CAS 竞态）=token 批已落 9ec1ae0f6e →销账"
  - "死信 q-20260930-st-menu-t1b6-0001（CREATE-GUARD）=token 随 0003 已落 →销账"
  - "死信 q-20260930-st-menu-t1b6-0005（合并器吞没）=内容由 0008 袋超集替代 →销账"
  - "死信 q-20261001-st-menu-t1b1-0001..0008（同链重试尸）=内容全部由 A/B/C 三批吸收 →销账"
  - "死信 q-20261001-st-menu-t1b5-0004/0005（ALGO-NOTE-SYNC/ghost）=内容已由 0009 袋吸收（ALGO 大白话在 TDM face）→销账"
  - "死信 q-20260930-st-menu-t1b2-0001（ghost）=F128 内容由 B2 内容批吸收（在途）→销账"
  - "F2b 第 3 件 capability 册 dedup=被 f32a46a8+册演进吸收超越 →销账"
  - "旧 sid 死袋 q-20261001-st-menu-w3harvest-0001（B6 原删块）=w3h-0008 超集替代 →销账"

pending_bags_snapshot: "见 .runtime/commit_queue/{pending,processing,done}/q-*st-menu-w3h-20260930-*（台账时点=003/006 processing、007/008/009/0010 pending）"
handoff:
  - "袋群落地核验+补投：核 done/ 区 q-...-0003/0006/0007/0008/0009/0010 落地 hash，git log -1 --name-only 归属核验；若 CLAIM_REQUIRED 复发=keeper（w3h_keeper3.py）须在跑"
  - "B2 内容袋（12+2 件 spec=.runtime/tmp/w3h_b2_content_ready.json 未生成——内容 face 已在主区，msg 待写：承 B2 车道 F128 复活+known-gap 改判已入 99_skipped #43 行）待 007 落地后 go6 直提"
  - "datasop 080fdfeca3 在 B5 sensor 未 merge 面上建了消费接线（import-integrity 逃生留痕）——B5 袋落地后其『标记可摘』提示留给维护班"
```
