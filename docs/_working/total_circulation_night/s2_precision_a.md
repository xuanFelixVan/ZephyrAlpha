---
created: 2026-09-30
ttl: task_bound
title: 第2批精度施工簿 A2 车道（st-circ-a2-20260930）
session: st-circ-a2-20260930
---

# 第2批精度处方 top10 · A2 车道施工台账

> 骨架=00_skeleton.md 第2批（A2/A3）前三项。能力反查审计：capability_lookup.find ×3
> （precommit_decide_failure/mutable_const/commit_block_events，session_id=st-circ-a2-20260930，
> 审计账=.runtime/lookup_audit/st-circ-a2-20260930.jsonl）。claim 七件在册。

## T1 PRECOMMIT 存量债 warn 棘轮化 — 已落地

- 处方：`_precommit_decide_failure` foreign（warn-only）通道加基线棘轮——首扫全量入基线
  （grandfather）；基线只降不升（债务消失即出册）；净增键（基线外新债）升级阻断；
  参照 fms_deadref_baseline 棘轮模式。
- 落点（src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py）：
  - `:447-505` 模块级：`_PRECOMMIT_DEBT_BASELINE_RELPATH`（.runtime/gate_audit/
    precommit_global_debt_baseline.json）、`_DEBT_PATH_TOKEN_RE`、
    `_precommit_debt_ratchet_enabled()`（env ZEPHYR_PRECOMMIT_DEBT_RATCHET=0 一键回退）、
    `_precommit_evidence_text()`（own 归因与键提取共用证据剥离真源）、`_precommit_debt_keys()`
    （键粒度=hook|文件锚，行号不进键防行漂移虚报；无路径行折叠 <noanchor>）。
  - `:3973-4005` `_precommit_decide_failure` foreign 分支接线棘轮；warn 事件补
    debt_ratchet/debt_keys/debt_baseline_hit/debt_net_new 字段（jsonl 消费方兼容）。
  - `:4007-4143` `_debt_baseline_path/_load_debt_baseline/_save_debt_baseline/
    _precommit_debt_ratchet_decide`：首扫建册审计 baseline_created；损坏 fail-open 不自动重建
    （防棘轮静默重置，审计 corrupt）；净增阻断审计 debt_ratchet_blocked+消息带处方与回退手柄；
    债消失出册审计 baseline_shrunk；原子写（tmp+os.replace）。
- 测试：tests/git/test_precommit_debt_ratchet.py 新建 13 例全绿
  （生命周期 7+键提取 4+own 路径回归 2；含 env 手柄/基线只降不升/损坏 fail-open 钉）。
- 落地账：本车道内容经 04a3097869（G1 车道按调度指令 FOREIGN→adopt 通道收编）+
  5a48e1baea（st-commitfix 维护班 own/foreign 锚级拆分细化）两棒接力落地 HEAD；
  本车道锚级验收=棘轮生命周期 13 例行为钉在册（tests/git/test_precommit_debt_ratchet.py）。

## T2 MUTABLE-CONST-WITHOUT-FINAL 增量化 — 交叉验证：挖掘情报过期，已落地于出生

- 判定：该门自出生（d0bfe67f5b9，2026-07-23 ARCH-WARN-TO-HARD-GATE-BATCH）即
  `_get_added_lines` 增量判定（blueprint_format_gate.py:144 同款 grandfathered 模式的
  AST 变体）：mutable_const_without_final_gate.py:143-145 取 added 行集、:154
  `node.lineno not in added_line_numbers → continue（存量违规由 M25 监控）`。
- 钉证：tests/governance/commit_gates/test_mutable_const_without_final_gate.py
  `TestAddedLinesOnly.test_existing_violation_not_added_passes`（存量非 added → 通过）在册，
  本车道实跑 18/18 绿。零代码变更（内收原则：已有行为不重建）。

## T3 R5-DIGIT-SUFFIX 遥测归因 bug — 已落地（双写手同批修）

- 病根实证：堵点本 .runtime/audit/commit_block_events.jsonl 三笔（09-22/26/28）
  gate_id="UNKNOWN" 而 detail 明文「门禁 R5-DIGIT-SUFFIX 阻断」——正则字符类
  `[A-Z\-]+` 在数字处截断（R5 断在 "5"）→ 整条失配恒落 UNKNOWN（GATE-20 同族）。
- 落点：
  - git_commit_gateway.py `_audit_commit_block_event` 正则改 `[A-Z0-9_\-]+`
    （含 `_`，与门禁号族全型对齐）——已随 04a3097869 收编落地。
  - session_worktree.py `_wt_block_gate_id` message 正则同步改 `[A-Z][A-Z0-9_\-]+`
    （口径对齐，防 worktree 路径同病）——随本批续作件落地。
- 测试：tests/git/test_git_commit_gateway.py 新增 `test_block_event_digit_suffix_gate_extracted`
  （R5-DIGIT-SUFFIX/GATE-20/GATE-PRECOMMIT-RUN/MUTABLE-CONST-WITHOUT-FINAL 四型）；
  tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py 判定链补 R5/GATE-20
  两断言。网关册归因面全绿+worktree 审计册 13 绿。

## 全量验证

- tests/git/test_git_commit_gateway.py 103 绿；tests/git/test_precommit_debt_ratchet.py 13 绿；
  tests/governance/test_precommit_channel_out_of_lock.py + test_commit_chain_campaign_20260922.py
  41 绿；test_session_worktree_audit_wrapper.py 13 绿；test_mutable_const_without_final_gate.py
  18 绿。ruff check + ruff format --check 双净（改动文件）。
- 翻译登记：tests/git/test_precommit_debt_ratchet.py 经 add_module_translation.py 落册
  （module_translation_registry.yaml +1 条，plain_zh 大白话在册）。

## 偏差披露

1. T2 挖掘情报过期（门禁出生即增量），按骨架「他人已完成=交叉验证」处置，零改动+钉证在案。
2. 共享热册 capability_canonical_file_registry.yaml 落盘态 YAML 损坏（connection_matrix 条目
   merge_evaluation 引号被并发写截断未闭 + 17 条新token滞留 di_seam_exemptions 死区 +
   写前自检报基线缺条目）——本车道按 batch_creation_tokens.py 自带处方做增量修复：
   HEAD（健康 12404 条）+ 盘上独有 3 条（data/quality 三件，st-menu-t1b1 token，文件已
   tracked 故保留）=12407 条；CAS 写入（safe_write_text，一次成功）；connection_matrix
   截断引号就地闭合（该条为他会话 st-matrix-final 在途件，prose 尾部若干字不可考，登记人可自修）。
   修复后 token 批量登记通道恢复（本目录 11 文件 token 已登记，capability=night_campaign_work_book）。
   该册修复面已随他会话批次落地 HEAD（本簿 token night-campaign-work-book-s2-precision-a-20260930
   在册可查）。
3. 共享册落地拆分：module_translation_registry.yaml（+1 测件翻译条目，并集保全
   macro_regime_sensor/cost_model 两他会话新登记）随续作件同车。
4. 落地通道环境事件实录（内容零丢失铁律的实证）：多车道并发下本批袋历 ghost_session
   （裁定#459，心跳守护被环境回收——按 RULE-GUARDIAN 补 process_reaper_keep 白名单+
   重注册+看门狗自愈）/CLAIM_REQUIRED（claim TTL 与传送带 10-20 分钟级单袋时长竞速——
   周期性 acquire 续期）/快照基底过期（dev 同路径推进——重排队取新快照）/stale bag 物化
   （DOC-HEADER-SUITE 按旧 header 判）四类死因；期间工作面遭物化覆盖一次——即写即 add
   纪律使全部编辑常驻对象库（dangling blob：gateway=4c75670a、测件=da301cd7、翻译册
   f2dd8fdf 择新合并），按 blob 复原+三小编辑按上下文原文重放，复测全绿后重新入袋。
   主实现体（debt 棘轮+R5 gateway 侧+evidence 真源）经 G1 收编（04a3097869 披露一）与
   commitfix 细化（5a48e1baea）接力落地；本批续作件=session_worktree 正则+三测试件+
   翻译册条目。
