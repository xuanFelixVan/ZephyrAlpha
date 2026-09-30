---
created: 2026-09-30
ttl: task_bound
title: 第2批精度施工簿 A3 车道·重发（st-circ-a3r-20260930）
session: st-circ-a3r-20260930
---

# 第2批精度处方 B 面 · A3 重发车道施工台账

> 骨架=00_skeleton.md 第2批 A3 五项（重发；未建簿，本簿即车道簿首建）。
> 能力反查审计：capability_lookup.find ×6（commit_queue requeue dead_reason /
> BLUEPRINT-FORMAT gate / CAPABILITY-OVERLAP gate / SSOT-REDEFINITION gate /
> ORPHAN-MODULE gate / HOT-FILE-BASE-FRESHNESS，session_id=st-circ-a3r-20260930，
> 审计账=.runtime/lookup_audit/st-circ-a3r-20260930.jsonl）。claim 八件在册
> （三 gate + 三测试册 + T2 验收测试 + 本簿）。
> 核现状结论：前次 A3（st-circ-a3-20260930，会话已故）遗产分布——T1 landing 侧+
> A1 瞬态收编面 staged 在索引未落；T2 gateway 主体已随 04a3097869（G1 收编袋）
> 落 HEAD 只缺验收测试（untracked）；T3/T4/T5 零动工。

## T1 热册三连自动改道 — 让位登记（他会话在途，零重做）

- 判定依据（2026-09-30 22:1x UTC 实测三连）：
  1. **enqueue 侧已落 HEAD**：fb357faa611（st-commitfix-20261001 C2，"A3 任务1 遗产
     抢救"）——FOREIGN-CHANGE/HELD-OVERLAP 专用 status + COMMIT_FAILED 带
     HOT-FILE-BASE-FRESHNESS 标记 → AUTO-ENQUEUE 自动改道入队（scripts/git_commit.py
     `_contention_auto_enqueue` 判据+`_enqueue_mode` claim 续租挂钩）。
  2. **landing 侧在途**：scripts/governance/commit_queue_landing.py 的
     HotRegistryContentionError（A3 原作 staged 未落）+ scripts/commit_queue.py 的
     A1 瞬态收编面（_drain_env_requeue/_transient_env_failure_of）——本会话核验时
     st-commitfix-20261001 刚以活 pid（36308/37928）RE-CLAIM 两文件（claimed_at
     1790806776/777，TTL 30min），在飞无疑。按纪律②让位：不共件、不代落、不重做。
  3. 两热册本体（module_translation_registry/capability_canonical_file_registry）
     同时段被 st-menu-w3h-20260930 持 claim——处方判断（等让位即自愈）与 T1 语义
     互证。
- 遗留边界（登记给后续班次）：landing 侧 staged 袋若 st-commitfix 终不落，死信侧
  `_DEAD_REASON_ENV_MARKERS` 对 HotRegistryContentionError 文本无 env 标记兜底
  （attempts≥5 耗尽死因会归 other 无人 requeue）——建议收编时同 commit 补
  "热册并发阻断" env 标记（_DEAD_PRESCRIPTIONS 同步），本车道不越权代改。

## T2 BLUEPRINT-FORMAT 连击升级 — 交叉验证：主体已落 HEAD，本车道补落验收测试

- 核现状：gateway 主体（detail 全量落盘不截断 + 同签名 sha1 二次阻断起
  repeat_count 递增 + escalated=true + 尾窗 400 行计数）已在 HEAD——
  src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:2050
  （_count_recent_block_signature）/ :2069-2115（_audit_commit_block_event，detail
  字段全量、record 带 sig/repeat_count、≥2 带 escalated）。与处方两要点逐条对上
  （"detail 不截断"=record["detail"]=blocked.message 全文；"同签名二次阻断升级"=
  repeat_count+escalated）。挖掘情报"未落地"部分过期。
- 本车道零重做，补落其验收测试：tests/git/test_commit_block_event_combo_a3.py
  （前次 A3 untracked 遗产，逐字收编+claim 认领；4 例=detail 全量含 file:line/
  首投不升级/同签名 1→2→3 单调 escalated=false,true,true/不同 detail 独立签名/
  尾窗损坏行容忍）。复测 4/4 绿。

## T3 CAPABILITY-OVERLAP 样板指纹排除 — 已落地

- 落点（src/zephyr/governance/../../commit_gates/capability_overlap_gate.py）：
  - `:286-291` 病根注释+_BOILERPLATE_BASENAMES（__init__.py/main.py）与
    _WRAPPER_MAX_LINES=5；`:8` [INVARIANTS] 补排除断语。
  - `:294` _is_reexport_body（纯 import/pass/别名直返）；`:305`
    _is_delegating_body（import/pass/别名或调用直返/单表达式调用）。
  - `:318` _is_boilerplate_function 纯函数面（①入口面重导出：basename∈集合∧体纯
    重导出；②任意文件 ≤5 行∧去 docstring ≤2 语句∧纯委托）。
  - `:348` _is_boilerplate_finding（读 staged blob→定位 finding.source_lineno 所在
    函数；读不到/解析不了/定位不到一律 False=fail-closed 照常阻断，裁定#273 同款）。
  - `:448-464` 阻断管线接线：cosmetic 豁免后按指纹分流，命中 warn 留痕（计数+N 条
    照常阻断），剩余照常硬阻断。
- 测试：tests/governance/commit_gates/test_capability_overlap_gate.py
  :382 TestBoilerplateFingerprintExemption 7 例（__init__ 重导出/main 委托/任意文件
  薄 wrapper 豁免；真逻辑/读不到/解析不了 fail-closed 阻断；纯函数面钉）。

## T4 SSOT-REDEFINITION 处方直给+同符号复读升级 — 已落地

- 落点（src/zephyr/gov_enforcement/commit_gates/ssot_redefinition_gate.py）：
  - `:183` _canonical_to_module（canonical 路径→dotted module，机械派生非新真源）。
  - `:199` _scan_file_violations 返回结构化 (py_file, symbol, canonical, content)
    元组（消息拼装后移到 _format_violations 单点）。
  - `:233-263` _format_violations 重写：逐符号计数——≥2 处者条目带【复读×N】标记、
    消息头升级（"硬阻断·升级：同符号复读 'X'×N——结构性分裂必须收敛"）；尾部处方
    直给可执行语句 `from <dotted_canonical> import <符号>`（去重后逐符号列举）。
  - `:8` [INVARIANTS] + docstring 治本节同步登记。
- 测试：test_ssot_redefinition_gate.py :507 TestImportPrescription（阻断消息含
  `from zephyr.governance.rule_patterns import PIICategory` 全句+处方字样；dotted
  派生四型钉）/ :534 TestRepeatEscalation（两文件同符号→升级头+复读×2 标记；单发
  不升级）。

## T5 ORPHAN-MODULE 头引用证据 — 已落地

- 落点（src/zephyr/gov_enforcement/commit_gates/orphan_module_gate.py）：
  - `:88-99` _REF_EVIDENCE_HEADER_RE（`[ \t]+\S` 刻意不跨行——裸空头不算证据）+
    _has_reference_evidence_header；`:8` [INVARIANTS]/`:52` docstring 设计权衡 6。
  - `:252-254` _detect_orphans 接线：入口豁免后，带非空 [CONSUMERS]/[DEPENDENCIES]
    头的模块直接豁免（头声明接线=活模块证据，动态加载/延迟接线不再误判孤儿）。
- 测试：test_orphan_module_gate.py :264/:277/:290/:299（[CONSUMERS] 头 grep 零匹配
  仍放行/[DEPENDENCIES] 同/裸空头照判孤儿/纯函数面五断言）。

## 复测读数与纪律留痕

- 五套件 109 passed（combo_a3 4 + capability_overlap 32 + ssot_redefinition 33 +
  orphan_module 40 + orphan_same_bag 3，pytest -q，含回归既有例全绿）。
- ruff 0.15.10 双净：check（2 处 I001 已 fix）+ format 通过，七文件 All checks passed。
- 提交走 scripts/git_commit.py --session st-circ-a3r-20260930 --files 八件
  （--allow-multi-domain 留痕：src gate+tests+docs 簿混合，宪法 §2.4 同批合法形态）；
  commit 后 `git log -1 --name-only` 核归属（索引中他会话 A1/A3 队列袋 staged 面以
  pathspec 提交天然隔离，不随行——核实时逐一对名）。
- 让位登记：T1 landing 侧 → st-commitfix-20261001（在飞 re-claim 实证）；本车道
  只取 T2 验收测试收编 + T3/T4/T5 三件施工。

## 偏差披露

1. T1 未施工（让位）：处方要求的"queue/landing 侧自动 requeue 退避"中 enqueue 侧
   已由 st-commitfix C2 落地、landing 侧 staged 袋在他人 claim 下在飞——重复施工
   必制造 T1 所治的并发本身。补 env 标记的收编建议已登记（上节遗留边界）。
2. T2 验收测试为他会话（前次 A3）untracked 遗产逐字收编，未改动断言面；文件头
   "test_git_commit_gateway.py 由 st-circ-a2 持 claim 在飞"注记已时过境迁（A2 已
   落），保留原文不改判历史。
3. 新建 .py 仅 tests/git/test_commit_block_event_combo_a3.py（tests/ 豁免面：
   CREATE-GUARD/TRANSLATION-COVERAGE 均豁免，无需 creation_token/翻译条目）；
   本簿新建 docs/_working/ 下（临时区，task_bound）。
