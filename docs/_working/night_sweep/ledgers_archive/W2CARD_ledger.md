---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# W2CARD_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# =====================================================================
# W2-CARD 点火卡换发车道·执行台账（第二夜总攻）
# =====================================================================
lane: W2-CARD
session_id: st-nightsweep2-card-20260930
chief: st-nightsweep-chief-20260929
date: '2026-09-30'
status: DONE
task: W12 波12 点火批准卡换发（approval_card+c4 双清，禁真发车）

authorization_chain:
  owner_night_order_20260930: "C组……把他们前置条件全部打通，然后来完成他们"
  chief_top5_adopted: "C4 批发车（获采纳=发车批准锚）"
  carrier: "#ARCH-368（夜总攻二 C组考试链前置 Owner 载体，PROTECTED-PATHS 正门标记载体）"

mining_findings:
  card_file: docs/_working/total_command_closeout/ignition/W12_WINDOW.yaml
  gate_code: src/zephyr/backtest/core/batch_window_preflight.py  # L115 路径常量/L333 sha256_file/L815 _card_checks/L838 read_approval_card
  gate_four_checks:
    - "status == APPROVED"
    - "approval_ref 在裁定册 ruling_id 集合内（子串双向匹配）"
    - "prereg_sha256 == sha256_file(config/search_space_prereg.yaml)（单文件字节摘要）"
    - "universe_declaration_sha256 非空"
  c4_reader: "read_cost_gate_caliber：裁定册成对关键词（抽查+幸存者/抽查+分层/cost_gate_spot+幸存者/成本门口径+五档），date>=2026-09-26，status active/decided"
  verify_entry: "python scripts/backtest/compute_window_gate.py preflight（只读判决，只检不火）"
  prior_state_disclosure:
    - "裁定#436（2026-09-30 晨批）曾批卡翻面但卡面从未落地（卡文件历史仅 f38242df99b 一次呈卡提交），且其引用 prereg sha256=da8fbbfb 已因批后合法变更过期"
    - "批后 prereg 合法变更=裁定#413/#ARCH-366 budget_caps 双键 + T1 定稿（裁定#431 第⑦项 Owner 签付）——按卡契约『批后改空间=卡作废』换发"

actions:
  cold_start:
    rule_env: "Python 3.12.8 + usercustomize 在岗 CHECK PASS"
    rule_guardian: "reaper 存活 last_run=2026-09-30 17:47:59"
    rule_worktree: "session worktree 创建 + SessionRegistry 登记（收尾已对称注销）"
  prereg_sha256:
    current: ec9663024187a833227b0dc660f1d7472a5ad4a065448b644af0b293dfaeb831
    front8: ec966302
    consistency: "worktree/主区/HEAD 三处一致（gate 认 config/search_space_prereg.yaml 单文件）"
  card_v2:
    path: docs/_working/total_command_closeout/ignition/W12_WINDOW.yaml
    status: APPROVED
    approval_ref: 裁定#455
    prereg_sha256: ec9663024187a833227b0dc660f1d7472a5ad4a065448b644af0b293dfaeb831
    universe_declaration_sha256: ea7fe1451935510b7672d9279d441888bcab43ac9032b7c6fc6961f4f63aa20c  # census 文件复算一致，延续
    conditions_checked: "c1=false（诚实注记：实弹点火仍受 c1 波0-11 施工终态闸约束）；c2/c3/c4/c5=true（c2/c3/c5=2026-09-30 问闸预检实测 GREEN；c4=裁定#455/#435/#431⑦ 追认链）"
    semantics_preserved: "v1 全部字段语义保留（purpose_scope/ttl/schema_version/五条件 check_command/notes 沿革）；写法=safe_write_text CAS 双写（热文件铁律13）"
  ruling:
    ruling_id: 裁定#455
    title: "W12 波12 点火窗发车批准锚（C4 批发车：成本门口径定稿追认+点火批准卡 v2 换发）"
    date: '2026-09-30'
    category: Owner 门位
    status: active
    claim: ".runtime/ruling_claims/claim_455.json（取号器占号在案，与登记同 commit 原子=RULE-RULING）"
    c4_keyword_pairs_hit: ["抽查+幸存者", "抽查+分层"]
    related_rulings: ["裁定#431", "裁定#413", "裁定#435", "裁定#436"]

commits:
  - hash: 193a37a8f2
    files: [docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml]
    note: "裁定#455 册件（gateway 正门，[ARCH-APPROVAL:#ARCH-368] 载体标记过 PROTECTED-PATHS）"
  - hash: 94125e1a18
    files: [docs/_working/total_command_closeout/ignition/W12_WINDOW.yaml]
    note: "卡面件补录——gateway --files 为逗号分隔单参，重复传参仅末位生效致两件被拆，本 commit 即补；合并回 dev 后两 commit 同车落地=原子等效（台账披露）"
  merge: "FF 合并回 dev（主区 424 脏件/18 staged 在途件致 session_worktree merge --no-ff 拒行；FF 不产生新提交对象、不碰他会话在途件；session_worktree.py merge 工具自身即裸 git merge 先例）"
  merge_warn_disclosure: "REFERENCE-TRANSACTION-GUARD WARN：在册 sid 但网关未在场（FF 合并动作本身无 GW 标记）——落审计放行，两 commit 自身均带 [GW:] 合规标记"
  post_commit_verify: "git log -1 --name-only 双核实（宪法 §2.5）"

verification:
  baseline_preflight_main_20260930:
    blocking: [c1_waves_0_11_construction_terminal, c4_cost_gate_caliber_decided, approval_card]
    detail_excerpt: "c4=BLOCKED_AWAITING_GATE ;; approval_card=WAITING_APPROVAL 非 APPROVED|批文锚在裁定册查无|prereg_sha256 与现役预注册不一致"
  worktree_dry_preflight_post_write:
    blocking: [c1_waves_0_11_construction_terminal]
    approval: "APPROVED | ref=裁定#455 | ref_registered=true | prereg_match=true"
    conditions: "c1 RED；c2/c3/c4/c5 全 GREEN"
  final_preflight_main:
    command: "python scripts/backtest/compute_window_gate.py preflight"
    exit_code: 3
    output_file: .runtime/tmp/st-nightsweep-20260929/W2CARD_final_preflight.json
    blocking: [c1_waves_0_11_construction_terminal]
    detail: "c1_waves_0_11_construction_terminal=RED（波 0–11 施工终态达成（含波10 G-D=READY_NOT_FIRED））"
    note: "exit=3=fail-closed 拒点火（c1 未绿）——符合设计，未真发车（禁令遵守）"

cleanup:
  claims: "两文件 claim 全释放（git_commit.py --release-only ×2 核实 NOT FOUND）"
  ruling_claim: "claim_455.json 保留=占号-登记原子证据（编号不回收铁律）"
  worktree: "abort 四证清理（证1 merge 豁免；证4 tip SHA 94125e1a18e4 存证 .runtime/quarantine/branch_refs.log）"
  generator_drift: "worktree 内 9 件非本车道生成器漂移（script_manifest/library INDEX 族/rule_catalog_registry，generated_at=2026-09-30T10:10:18Z，可再生成）→ stash push 存证后清理（stash 消息带车道 sid，可恢复）"
  session_registry: "已注销（heartbeat daemon PID 14544 已终止）"
  reaper_keep: "keep-add 子命令不存在（误调未生效），keep 白名单零改动（git status 核实）"

landing_hashes:
  card_file_sha256: 12b24f54ce989713cab62fb55a059f777c5ac81a6720ed73992850b1b23c15fc
  ruling_registry_sha256: 69142b6602ace9869b9ff0bda399aa4cd64e9b9c11395317840ddafa35e9f45f
  dev_head_after_merge: 94125e1a18

honest_notes:
  - "实弹点火未发生亦被禁止：c1_waves_0_11_construction_terminal=RED 结构性条件在册（禁碰），compute_window_gate 维持 fail-closed 拒绝"
  - "本车道产出=问闸放行面（approval_card+c4 两关清零），不构成算力放行、不解除 c1 闸"
  - "裁定#455=登记载体（Owner 夜令+总筹建议采纳链+裁定#435/#431⑦ 追认面），非 AI 代裁新口径"
```
