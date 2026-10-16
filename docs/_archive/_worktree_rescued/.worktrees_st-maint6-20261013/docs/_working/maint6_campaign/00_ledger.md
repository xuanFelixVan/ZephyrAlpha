---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-maint6-20261013
title: 维护六班班账（令三 v2·维护六班）
---

# 维护六班班账 st-maint6-20261013

令源＝统筹令（2026-10-13 20:1x，令三 v2 维护六班开场，按优先级 P0×2／P1×6／P2×4＋一条条件件）。
本账是本班唯一交付叙述面；每条含"实测数字＋证据位置＋复核命令"，复核命令均可从正文原样跑出。

## 一、冷启动三闸（实测）

| 闸 | 命令 | 读数 |
|---|---|---|
| RULE-ENV | `python --version` / `python scripts/setup_dev_env.py --check` | 3.12.8；usercustomize exists=True points to D:\ZephyrAlpha |
| RULE-GUARDIAN | `python scripts/lock_files.py cleanup` + `python -m zephyr.trading.process_reaper --status` | 清 2 枚死锁（scripts/backtest/fexam/card_binding.py、tests/backtest/test_card_binding.py）；回收 2 个死会话遗物（st-condaxis/st-maint5，merge=skipped）；计划任务 ZephyrAlpha_ProcessReaper=Ready；last_run 与查询同秒；水位 commit_pct=59.75 ram_avail=29.89G |
| RULE-WORKTREE | `python scripts/session_worktree.py create st-maint6-20261013 task-maint6-sixshift` | 车道 D:\ZephyrAlpha\.worktrees\st-maint6-20261013 分支 ai/st-maint6-20261013/task-maint6-sixshift；心跳 daemon PID 30480 |
| RULE-CAPABILITY-LOOKUP | `CapabilityLookup().find(kw, session_id=...)` | 审计 .runtime/lookup_audit/st-maint6-20261013.jsonl（6 行）；正对照 `commit_queue`＝1 命中／`gate`＝184 命中（先验尺有效，中文多词查询 0 命中系词面而非尺坏） |

主区进场脏面＝776 件（reaper 亦报 worktree_changes=776>50）。本班全程在车道内改，未触他班在途面。

## 二、P0-1 投影追齐（两本账本册）

判据前置＝统筹令原文"重渲染优于投旧袋（PG 真源已前进；旧袋 blob 1e63cfba 仅备查）"。

**翻译册 REG-MODULE-TRANSLATION-001**（袋 q-20261013-st-maint6-20261013-0002，已 done）
- 三面对账（账本 active／最新快照／HEAD 投影）＝8114／8114／8105，C-B=0（投影无幽灵行⇒render 不丢字节），B-C=7。
- 6 条测试夹具（src/zephyr 下 degraded/layered/lying/new_mod/orphan/with_extras）`fetch_entry` 逐条实查 status=**retired**，投影零命中＝令面"retired 状态入投影"核对达标，无需动作。
- 渲染净增 9 条（快照在本班对账后又前进 2 条：src/zephyr/regime/formreg/__init__.py 与 ps_chronology.py，属条件轴 formreg 车道在册登记），diff＝+48/−0。
- 复核命令：`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -c agg8_series_materialize` 期望 ≥1（本班落地后实测＝1）。

**裁定册 REG-RULING-001**（袋 q-20261013-st-maint6-20261013-0008）
- 入袋前三面对账＝331／325／325；A-B=6＝号 509・510・511・512・513・514 在账本 active 而快照停在 v19（止于 508）；C-B=0。
- 处置＝意图 API 三步正门：`publish_snapshot(REG-RULING-001, repo_root=车道根)` → v20（entry_count=331，content_sha256=6a0f5f1f91c0…，noop=false）→ `registry_projection_generator --render`。diff＝+127/−0。
- 后并入 M-3 补签（见 §五）→ v21（entry_count=332）→ 再 render，最终袋 diff＝+142/−0、净增 7 条 ruling_id（509–515）。
- 复核命令：`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -c "裁定#514"` 期望 ≥1；`git log -1 --name-only` 核归属。
- 同件双袋规避：首投 q-…-0007 在 M-3 占号后按"袋内字节退出物化＋同会话同件后袋静默超前"两条在册坑自撤（dead_reason 已写，pending 原件存证 .runtime/tmp/maint6_20261013/withdrawn/，可逆＝mv 回 pending）。

## 三、附袋：受保护路径审批归一第四形态（q-…-0001，已 done）

- 现象：车道内携裁定册的袋在锁外预检被 PROTECTED-PATHS 判 `no approval channel matched`，而号 479 活跃裁定（expires_at=2026-11-03）approved_paths 明文覆盖该册＝有授权也审批不过。
- 复现（零写）：`resolve_approval([<车道绝对路径>], None, <车道根>)` → approved=False/source=none；剥完主仓根后命中路径仍带 `.worktrees/<sid>/`。
- 定位：`approval_resolver._strip_worktree_prefix` 认 serializer 单数/复数两形态与 `.aidrafts/<sid>/`（09-30 实测补），独缺 `session_worktree.py create` 现势落地的 `.worktrees/<sid>/`＝在册同病家族第四形态。
- 修法只补输入指向：加第四形态＋嵌套车道循环剥（实测 `.worktrees/<sid>/.aidrafts/<sid>/` 套叠存在于 st-examunlock-20261013）；判据/阈值/白名单/豁免面零改动。
- 双向自证：车道面 `test_approval_wiring.py` 11 passed；同测试打在未修面（PYTHONPATH 指主区 src）3 failed/2 passed。

## 四、P0-2 甲-0：GATE-INTEGRITY own-diff 收窄（q-…-0003，已 done）

- 现状核账：门在 head 态已有 own 解释位（`_staged_change_set` 读网关临时索引），缺的是"非本袋外来漂移"仍判 TAMPERED/MISSING→exit 2。实耗在册＝维护三班 0032/0034/0035 三枚＋四班主动撤两枚。
- 修法＝与 in-process 60+ 台同一份共享原语（`_build_own_scope`/`_norm_rel`/`_audit_foreign_staged`，自写拆分必撞 FUNCTION-DUP/CAPABILITY-OVERLAP）；非 own 的 TAMPERED/MISSING 降为 FOREIGN_WIP/FOREIGN_MISSING（critical=False、不计数、逐件留审计）。own 件判定式、阈值、exit code 一字未动。
- 三道 fail-closed 不收窄：①通道外（缺 ZEPHYR_COMMIT_GATEWAY=1 或缺 GIT_INDEX_FILE）②mode=snapshot 回滚态 ③原语不可用/抛异常。
- 验收①own_scope 翻 true＝机生非手改：车道内复跑 `generate_gate_registry._derive_own_scope_for_entry("python scripts/governance/meta/validate_rules_integrity.py")` 回 **True**；册面 diff 严格 1 行。
- 验收②治理面袋实测解堵（真环境同输入 A/B）：临时索引只放本袋一件、主区外来 WIP 原样不动、跑完即删（主区真 index 141 条在册面零污染）——未修面 tampered=1/clean=False；修后 clean=True，3 项转 warn+审计，审计行 `foreign_count=3` 逐件留名于 `.runtime/gate_audit/gate_integrity_foreign_staged.jsonl`。
- 测试：`tests/gov/governance/audit/test_validate_rules_integrity_fold.py` 9 passed（原 4 支零回退＋新 5 支）；连带 test_integrity_head_baseline＋test_integrity_audit_reconciler 共 52 passed 零回退。basetemp 走仓外 D:/tmp/maint6。
- 刻意不并入的两处他役漂移（零自拟、见 §七呈批）：total_gates 191→189 两枚幽灵条目；RULES_MANIFEST 内 `tests/governance/{generators,shared}/` 两枚已失效锚点。

## 五、P1-1 M-3 裁定补签（并入 §二 裁定册袋）

- 正门三段：`next_ruling_id.py --claim --session st-maint6-20261013` → 占号 claim_515.json（O_EXCL 原子）；`api.register(REG-RULING-001, entries, …, actor_kind="agent")` → code=OK、entry_pk=90065、status=active，`fetch_entry("…","entries","ruling_id=裁定#515")` 回读非空；`publish_snapshot` → v21 entry_count=332。
- 内容转录（判据数值零自拟）：SM≥70% 由 GPU 网格批**验收线**降为**披露线**（读数照旧逐进程 NVML sm_util_pct 采集并披露，不再参与合格判定）；N-1 验收线＝**吞吐≥3x（两序协议）＋实现等价零越线**。adjudicator=chief-coordinator-st-20261013（统筹对话通道 20:1x 裁定，非 Owner 亲笔数值）；登记执行=本班（§5.3 AI 代登记署名）。approved_paths 留空＝登记语义而非授权语义，不构成任何受保护路径写授权。
- 先例面实查：03_gpux_final_report.md §十七·E③ :2387-2402（:2401-2402 自陈"有口头准裁、无册面署名"＝本袋所补缺口）＋§十七·I P-4 :2487（**勘正注**：该行交叉引用写作 E②，算术实位于 E③；他班件不代改）＋§十七·E① :2358-2364＋§十七·D :2315-2321；呈裁原文 00_gpufeed_report.md :460-465。
- 时序纪律：register 之后立刻 publish＋render 并三面核验，否则引用新号即自触 RULING-REFERENCE/REFERENCE-INTEGRITY（在册反例＝architecture_issue_registry.yaml:9874 记 10-12 "不另立号 509"之由）。
- 前置依赖：号 479 授权通道在车道内命中，依赖 q-…-0001（§三）先落。

## 六、P1-2 base_head 字面量（q-…-0005）与 P1-5 MSG-STYLE（q-…-0006）

**P1-2**（二选一取"解析成 sha"腿，改在消费侧单点收口）
- 逃逸链实测坐实：非空⇒不走存量兜底；`'dev'≠<40位sha>`⇒不早退；`git cat-file -t dev` 回 **commit**⇒"非可判 commit"死信口不触发；`merge-base('dev', dev尖)`＝dev 尖⇒`diff(尖,尖)` 恒空⇒**恒不判冲突**。面积＝done 23 枚＋dead 12 枚袋体 base_head='dev'；全仓零 sha 形态校验。
- 修法＝`_trusted_base_head(item)` 三态 {sha, absent, live-ref}，仅 7-40 位十六进制可当锚；活引用一律 sha=None 退到既有兜底（判定走时间基底、合并走逐路径 base_blob，两者皆无⇒在册 fail-closed 死信回 requeue 处方）。刻意不在读侧把活引用 rev-parse 成 sha＝重演 resolve_base_head 已废除的旧口径（基底比快照字节还新，同样恒空，F-AUDITFIX-STALE-01）。
- 判别力双面跑（同三条判据）：车道面 3 passed；未修面 3 failed，红形态分类如实＝①AttributeError（分类器不存在，TypeError 级）②AssertionError"未修面应失明，实得 None"（断言级，§6.4 失明坐实）③Failed: DID NOT RAISE（断言级；旧面在此落 **noop 吸收**，被"快进拒绝＋条目级合并＋HEAD 面新鲜度复核"三道下游闸兜住，本构造未销毁条目——故本班只主张"把不确定基准换成可处方化死信"，不主张已止血整覆盖）。全文件 33 passed（27 存量零回退）。
- 自撞坑记录：车道内测试按 `__file__` 定位仓根，换 PYTHONPATH 做"未修面"对照＝零判别力（本班第一版即得 3 passed 假对照，作废后改显式主区路径重跑方得三面红）。证据面 `.runtime/tmp/maint6_p12_red/`。
- 入队侧另一腿不动：`scripts/commit_queue.py` 由活跃会话 st-deadclean-20261013 持有（session_registry held_files 实查含该件；心跳 mtime 21:40:56，距查询 8 秒＝活）⇒§3.4 owner 责任制不代修，其 :5100/:5231 直取 args.base_head 零校验列 §七 呈批。

**P1-5**（arm_protocol_binding.py:298）
- 真身路径＝`scripts/backtest/fexam/arm_protocol_binding.py`（令文只给文件名，find 实核）。
- 字面级违规恰 1 处＝:298 `卡面级别→仓位映射数值须整表传入`，码＝unicode_arrow（U+2192）；cn_period_end 零命中。
- 门看不见它：`msg_style_gate._is_exception_constructor` :80-98 要求函数名后缀 Error/Exception，本件四支异常（ArmParamUnfrozen/ArmQuoteNotFound/ArmBaseMissing/ArmFaceMismatch）全不后缀 ⇒ 用门自身 `_detect_msg_style` 扫本文件回 **0 处**。故"存量违规"成立仅到字面级。
- 处置＝改喂给门的输入（文案 → 改"到"），门判定式/阈值/豁免零动；`tests/backtest/test_arm_protocol_binding.py` 16 passed 零回退（该测试只断言异常类型，不锁文案，grep 实查）。文件余 15 处 U+2192 在注释/docstring/非 raise 赋值，出门作用域，不顺手清。
- 呈批面（不自裁、不扩门）：门对"非 Error/Exception 后缀异常类"结构性失明，且 `tests/gov/governance/commit_gates/test_msg_style_gate.py` 无该形态用例（grep `Unfrozen` 零命中）＝盲区既无尺也无检；扩判据牵全仓 raise 存量，列 §七。

## 七、M-4 采样键复核（两处在册结论定案）

缺陷坐实（非转述）：`.runtime/tmp/st-gpux3-20261012/b2_throughput_sm.py` :60 守卫用真键 `sm_util_pct`，:61 存值取 `r.get("sm_pct")`（该键在 `src/zephyr/backtest/gpu_core.py` :255-263 返回值面中**不存在**）⇒ :86 `sm=[]` 恒空、:87 `sm_unavailable` 恒等于总拍。

三面独立证据：
1. 同班自带尺自检件 `b2_sm_ruler_check.json`：同一 NVML 尺按真键读到 `sm_util_pct=90/91`（in_compute_table=true）⇒ **尺在岗**，坏的是采样器键名。
2. b2 两批 arms 汇总面：四臂全 `sm_samples: 0`，`sm_unavailable`=268/153/137/137（合计 695，与 ruler_rejudge.unavailable_reads=695 一致）⇒ 与负载形态无关的恒定 100% 不可用，正是空读签名。
3. 五班真尺复读（`g5_tp_n120.py` :65 取 `sm_util_pct`）三口径分计：GPU_r1 总拍 66／在表 50／非空 50（75.8%）中位 8.0 p90 11 max 22 ≥70 占比 0.0；GPU_r2 总拍 64／在表 55／非空 55（85.9%）中位 9 p90 21 max 31 ≥70 占比 0.0。

两处结论定案：
- **00_gpufeed_report.md :468-471（GPU四班 M-4 更正条）＝成立**："其 sm_unavailable 恒等于总拍数，那句'171／87 枚采样命中 0 枚'是尺的空读，不是现场事实"——本班三面证据支持；并补上该条当时缺失的真尺复读数（非空率 75.8%/85.9%、≥70 占比 0.0）。
- **03_gpux_final_report.md :853-863（§十三·补②，GPU三班）＝改写**：拍数记录（171/87）属事实可留；但"这不是尺坏"一句被证伪（正是采样器键名坏），其推论"依旧是'测不到'而不是'没达到'"随之前失效——真尺定性＝**测得到，且没达到**。同段"设备段占空比算术（0.2s/90–174s≈0.2%）"这条独立支撑不受影响，仍作"形态性不可达"支撑。
- 下游同数两处顺带定案：03:1296（已改判"测得到且没达到"）＝与本班实测一致，成立；03:876（交付判定引用"终局两线本袋未达"）＝结论方向不变，但"未达原因"须按上面改写后的定性表述。

改写归属：gpufeed_campaign 案卷是 GPU 五/六班资产，GPU六班现势仍活（lookup_audit 21:09 有写入），按 §3.4 不代修；本班把定案与证据落在本账，改写动作交该线。M-3 补签（号 515）已把"降为披露线"定形成册，正是这两处改写所依据的判定身份。

## 八、待办与残余

（本班进行中，逐条续记）
