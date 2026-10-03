---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# T1C1_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# T1-C1 施工终态核销车道（第一棒）· 台账
# sid=st-menu-t1c1-20260930  总筹=st-nightsweep-chief-20260929  日期=2026-09-30
# Owner 批文原文留痕："现在就可以并发开工，不需要立项"（c1 波 0-11 施工终态核销专项即刻开工）

session:
  sid: st-menu-t1c1-20260930
  registered: true            # SessionRegistry.register(logical=true) 实证
  cold_start: "Python 3.12.8 PATH ✓ / usercustomize 在岗 ✓ / lock cleanup CLEAN + reaper 存活(scanned=20 killed=2 reported=10) ✓"
  capability_lookup: "CapabilityLookup.find ×2（verification_status verified 打标/任务卡 verified，均 0 命中，审计已写）"

findings:
  - id: F1_表真源定位
    verdict: DONE-LANED
    evidence: |
      闸=src/zephyr/backtest/core/batch_window_preflight.py:372 SQL_WAVE_CARDS
      （SELECT title, verification_status FROM tasks WHERE title LIKE '波%' LIMIT 2000）。
      表真源=SQLite data/databases/governance.db tasks 表（2597 行，is_deleted 全 0），
      读通道=DatabaseService.get_governance_conn(read_only=True)（default_governance_rows :907）。
      绿判据：REQUIRED_WAVES(:94)=0,1A,1B,2,3,4,5,6,7,8,9,10,11 每波≥1 卡（_WAVE_RE :129，9.5 归 9）
      且全部卡 verification_status=verified（:130 小写比对，大小写通吃）；
      c1b 波10 引擎 READY_NOT_FIRED 子读数=GREEN（引擎件在 HEAD+账本无共振批次）。
  - id: F2_verified写入通道
    verdict: DONE-LANED
    evidence: |
      唯一合法生产路径=TaskRepository.verify()（task_repo.py:1927，"本方法是设置该字段的唯一合法生产路径"），
      前置=batch_review(:2642) 连续 2 轮 0 问题（7 维卡面审查持久化 task_reviews）。
      配套=建卡 create(:1682)/create_and_ready(:1785)；G7-ORC-VERIFICATION severity=error
      （src/zephyr/gov_enforcement/rule_enforcement/task/g7_orc_gate_engine.yaml:28）COMPLETED 须 verified。
      升态三判据尺=scripts/governance/wave1a/verified_promotion_check.py+canary 测试（均 HEAD 在册）。
      禁直接 UPDATE 生产表——本车道全程未跑裸 SQL 写。
  - id: F3_NC报告纠偏
    verdict: DONE-LANED
    evidence: |
      NC 称"tasks 表 verified 零命中=2597/2597"不成立：全表实测 verified=895+VERIFIED=2。
      闸口径真实缺口=①波次卡 20/20 全 unverified（LIKE '波%' 仅 20 行）②波 0/3-11 共 10 波零卡
      （gate_missing_waves 实测）。闸实测读数=c1a RED（复跑两次，打标后零 VERIFIED 项 6→4）。
  - id: F4_全量导出与分段
    verdict: DONE-LANED
    evidence: |
      .runtime/tmp/st-menu-t1c1-20260930/tasks_dump.yaml（789KB，2597 条全量：
      id/标题/ns/seq/status/construction/verification/wave 归属/时间戳）。
      分段：波1A=6 卡 波1B=10 卡 波2=4 卡 波0/3-11=0 卡；非波次卡 2577 条（unattributed_ids 全列）。
  - id: F5_证据底稿索引
    verdict: DONE-LANED
    evidence: |
      .runtime/tmp/st-menu-t1c1-20260930/evidence_index.yaml：语料 61 件带 sha256
      （A 审计 canonical.json 534 条+桌面 MD｜B 夜战台账族｜C 91/96/97/99+wave1a 案卷族｜D git log 1200 条）；
      card_evidence_mapping=20 卡关键词→文件+行号+摘要（每关键词每文件首命中，5-40 命中/卡）；
      canonical_audit_index=534 条 id 级指针。构建器 build_evidence_index.py 可复跑（改关键词可扩 2577 卡）。
  - id: F6_首段核销试点_波1A
    verdict: ADVANCED
    evidence: |
      三态全判（verification_triage.yaml）：verified×2+not_verified×4（差项逐条）。
      已打标：OPS-9260101（1A.1 建卡入表：20 卡在库可复算+案卷在 HEAD）
            OPS-9260102（1A.2 升态校验器：尺+canary+G7+verify() 四件在 HEAD，
            现场红证复现=sample20_live 20 张 COMPLETED 全 REJECT empty）。
      通道=各自 batch_review round1=0/round2=0 → verify() → verified+completed（DB 实读回证）。
      闸面复核：c1a 零 VERIFIED 项 1A 段 6→4（打标前基线 RED 同位对比）。
      诚实注记：两卡面 artifact_paths 指向 .aidrafts 陈旧指针（20/20 卡共性，交付实体另论，
      不构成拒打标理由；残记 triage residual_note）。
  - id: F7_并行分工包
    verdict: DONE-LANED
    evidence: |
      docs/_working/night_sweep/c1_sweep_playbook.md（CREATE-GUARD：night_sweep 前缀 token 已在册，
      batch_creation_tokens --dry-run=无待登记）。内含闸机制表/现势读数/L1-L4 分工
      （L1=1A 残 4 卡、L2=1B 10 卡、L3=波2 4 卡、L4=缺卡 10 波呈总筹裁建卡或判据改签）/复算命令/红线。

handover:
  to_chief:
    - "L4 需 Owner/总筹裁定：波 0/3-11 十波零卡=闸结构性 RED——建卡（1A.1 模式）或闸判据改签（REQUIRED_WAVES 收敛），禁 AI 自裁"
    - "0105 死库处置+0107 四台禁用门恢复属 Owner 门位（approval_required=True 卡）"
    - "后续车道照 playbook §三分工领卡；打标必须附 triage 底稿证据指针"
  worktree_note: "本车道主区只读+DB 行写（官方 API）+1 新文档；session_worktree_start 已注册（worktree=.aidrafts/st-menu-t1c1-20260930 未用，无代码施工面）"
  playbook_commit_pending:
    state: "docs/_working/night_sweep/c1_sweep_playbook.md 已写盘+已 staged+token 已登记（night-sweep-c1-sweep-playbook-20260930，registry 工作树在册）"
    blocker: "CREATE-GUARD 落地仿真态要求 registry∈files 同批；而 registry 被活跃兄弟车道 st-menu-t1b1-20260930 持 live claim（FOREIGN_CHANGE ×4 实证）——按'HELD-OVERLAP 不硬闯'纪律不硬闯"
    unlock: "t1b1 registry 批落地（HEAD 册含本车道 token 行）后，单文件 commit 即绿：python scripts/git_commit.py --session <sid> --files docs/_working/night_sweep/c1_sweep_playbook.md --message-file .runtime/tmp/st-menu-t1c1-20260930/playbook_commit_msg.txt --allow-non-worktree"
    commit_msg_file: ".runtime/tmp/st-menu-t1c1-20260930/playbook_commit_msg.txt（含同批注记）"
    audit_trail: "token 登记=capability_canonical_file_registry.yaml:57794（工作树）；4 次尝试全程留痕 .runtime/audit/commit_block_events.jsonl"
```
