---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 C：提交链/队列基础设施审计 findings

> 审计对象：总包会话 st-mastertc（2026-10-06 夜~10-07）施工中被指派给车道 C 的 6 项。方法=只读；一切结论以 git HEAD（`649a8c93c7` 时点）+ `.runtime/commit_queue/` 运行时机器记录（非 HEAD，已注明）为准。审计全程零写操作。

## P0 候选

### P0-1 交付报告 DONE 面与 HEAD 落地面系统性不符 + HEAD 翻译册幽灵模块条目（注册表完整性缺陷）

**事实链**（全部 HEAD 实证）：

1. 交付报告 `docs/_working/master_tc_night/99_delivery/交付报告.md`（3f47dbd6d5 落册，de50314561 v2 修正仅涉 §八 5-7 条）三态总表将下列卡记 **DONE**，但其落地件经逐文件 `git cat-file -e HEAD:` 核验**不在 HEAD**：

| 卡 | 报告 DONE 自告 | HEAD 实况 | 承载死袋（现存 `.runtime/commit_queue/dead/`） |
|---|---|---|---|
| C232/L6 | "事件轴显式层已施工" | `src/zephyr/signal_ashare/limit_up/event_axis.py` 不存在 | q-20261007-st-mastertc-recover-0002 / -0005（GATE-PRECOMMIT-RUN / CREATE-GUARD MAP-MOUNTS） |
| C234/L6 | "摆动结构序列已施工" | `src/zephyr/signal_ashare/swing_sequence.py` 不存在 | 同上 |
| C235/L6 | "共振定义器已施工" | `src/zephyr/signal_ashare/resonance_pair.py` 不存在 | 同上 |
| C75/L6 | "tech_factor_pipeline+10 测绿" | `src/zephyr/factor/analysis/tech_factor_pipeline.py` 不存在 | q-20261007-st-mastertc-recover-0003（CREATE-GUARD 无 token） |
| C233/L7 | "前视注入红证尺 16/16 绿" | `tests/backtest/test_lookahead_injection_red_ruler.py` 不在 HEAD（盘面 `??` untracked，未 staged） | q-20261007-st-mastertc-mini-0002（ALGO-FLOW-LINK 锚断裂） |
| C107/L7 | "Fill 单一写者落地，8/8 绿" | `_PaperFillJsonlWriter` 在 HEAD 全仓零命中（仅 workbook 文档提及）；`scripts/start_paper_session.py` 写者腿未落 | q-20261007-st-mastertc-mini-0003（GATE-PRECOMMIT-RUN） |

2. **更硬的一条**：HEAD `docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml` L67723-67747 存在 **4 条幽灵模块条目**（tech_factor_pipeline / event_axis / swing_sequence / resonance_pair，含 plain_zh 简介与 domain_id），指向的 .py 文件在 HEAD 树**全部不存在**。条目由 st-mastertc-l6 的 docs 袋 **45c1f0b224** 落地（"翻译册对齐"），而对应代码袋（l6-0001/0002、recover-0002/0003/0005）全部死于队列——注册表与代码面反向漂移（已注册未落地），与 TRANSLATION-COVERAGE 门"新建 .py 须登记"的立法意图构成镜像漏洞。

3. **C107 特别注记**：HEAD 确有 `tests/trade/ex_core/test_fill_jsonl_single_writer.py`，但由 **st-cure-p05b-20261006** 于 85896a0485 落地（另一战役、另一路径），非本战役成果；且该测试的静态尺断言"全仓写者集合=={start_paper_session.py}"在 HEAD 面必红（写者不存在）。

**减轻情节**（如实列出）：L7 workbook 自己披露"内容袋死信待维护班（袋快照=零丢失承诺）"；交付报告 §七.3 与 close 班台账披露 dead=45 归维护班"禁盲投"；死信 blob 保全在案（`blobs/` 24061 对象）。即：**施工与测试在会话面真实发生、无捏造，但终局三态总表逐卡记 DONE 无"未落 HEAD"限定，Owner 消费面失真；注册表幽灵条目是客观 HEAD 状态缺陷**。

**建议定性**：交付报告三态总表须增"死信在途未落 HEAD"列或逐卡加限定；4 条幽灵翻译条目须随代码落地或显式退役注记。

## 逐项 verdict（1~6）

### 1. C02 死信分诊抽 10 复核 —— **真完成（含 2 处计数虚增 P2 + 1 处内表自相矛盾 P1）**

分诊清单核实：HEAD 版 `docs/_working/master_tc_night/lanes/L3_commitchain/00_workbook.md` 载 45 封分诊表（机械计数=45 行 ✓），三态=1 复活/44 需属主/0 被取代。真实存档路径找到：`.runtime/commit_queue/dead/`（在册死信）+ `.runtime/commit_queue/dead_archive_20261007/`（归档袋，manifest.jsonl 213 条）。抽样 10 封（1 复活+9 需属主），逐封用信体内 per-file `blob_sha256` 对 HEAD 内容哈希对拍：

| # | 死信 | 分诊 | 死因核验 | landed 复核（工作簿 vs 实测） |
|---|---|---|---|---|
| 1 | q-20260923-st-chainpile-20260922-**0041**（复活） | 已复活+已归档 | GATE-PRECOMMIT（protected-paths）✓ 与台账"GATE-PRECOMMIT"相符 | 1/1 vs **1/1 且内容 sha256 逐字节 identical** ✓（manifest 08:50:57 archived 1 封 ✓，"spot_check identical"属实） |
| 2 | q-20260922-st-chainpile-0031 | 需属主 | TRANSLATION-COVERAGE ✓（与前任抽样定性相符） | 4/7 vs 4/7 ✓ |
| 3 | q-20260923-st-xhs-full-20260922-0043 | 需属主 | LandingEnvironmentError ✓ | 9/16 vs 9/16 ✓ |
| 4 | q-20260923-st-combine-20260923-0001 | 需属主 | LandingEnvironmentError ✓（"09-23 05 时簇"相符） | 5/9 vs 5/9 ✓ |
| 5 | q-20260923-st-nightfix-20260923-0006 | 需属主 | LandingEnvironmentError ✓ | **10/13 vs 9/13（+1 虚增）** |
| 6 | q-20260923-st-nightdata-20260923-0001 | 需属主 | prestage RuntimeError（.gitignore 快照路径）✓ env 族相符 | 1/2 vs 1/2 ✓ |
| 7 | q-20260923-st-e2e-20260924-0008 | 需属主 | CREATE-GUARD ✓ | 13/17 vs 13/17 ✓ |
| 8 | q-20260923-st-k4-20260923-0006 | 需属主 | GATE-PRECOMMIT-RUN ✓ | **7/10 vs 6/10（+1 虚增）** |
| 9 | q-20260923-st-wm1-buildB-20260923-0001 | 需属主 | TTL-METADATA ✓ | 10/13 vs 10/13 ✓ |
| 10 | q-20260923-st-regfix-lane0b-20260923-0015 | 需属主 | FILE-COPY（AST 克隆）✓ | 2/4 vs 2/4 ✓ |

- **+1 虚增根因锁定**：两封虚增信各含一条 `delete src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py`，该文件 HEAD 树**仍在**（`git ls-tree` 命中 blob d28e41c0），delete 未落地却被计入 landed。三态分类不受影响（仍为部分落地=需属主）。
- **内表矛盾（P1）**：chainpile-**0066**（同 0041 的 trae_087 单件批，2026-09-23T22:09 创建）实测 **1/1 全件落地且 identical**，工作簿自己的表也写 landed=1/1，却归入"44 需属主"；按其自订判据应为第 2 封"已复活"。与台账"批 2/3=零封可归（三闸 pass 名单耗尽）"相抵——**待证**（无法从留痕重建 08:5x 时点三闸为何放行 0041 却不放行 0066）。0066 最终于 20:21:09 被后续批归档（见证据块 3），终态收敛无内容损失。
- 附带发现：前任 l3 班抽样定性"0031 三件 meta_question 已在 dev 树"有误（`registry.py` 实测 MISSING），l3b 班全样本复扫（4/7）予以纠正——分诊质量实为提升。

### 2. 恢复班 6 袋逐文件 HEAD 核实 —— 3 袋**落地（真完成）**，3 袋**死袋（未落地）**

| 袋 | 自告内容 | verdict | HEAD 证据 |
|---|---|---|---|
| 袋B（abed5f7a1f） | G-D 引擎四件 | **落地** | `scripts/backtest/grid_stats_engine.py`、`scripts/backtest/lead_lag_validator.py`、`tests/backtest/test_grid_stats_engine.py`、`tests/backtest/test_lead_lag_validator.py` 四件全在 HEAD（commit 实测 4 文件 +1103 行；注：两引擎 .py 当前工作区有他会话 M 态，本审计以 HEAD 为准）；docstring 含 DSR/SPA（`spa_reality_check`、L49）=C239/C251"随 C238 批"的引擎面主张成立 |
| C237（90d8e3b33c） | chart_resonance_prereg.yaml | **落地** | `config/chart_resonance_prereg.yaml` 在 HEAD |
| C324（a6ae287dab） | reaper 现算化 | **落地** | `src/zephyr/trading/process_reaper.py:1332 _compute_live_report`（:1348 调用）在 HEAD |
| recover-0005（+同内容 recover-0002） | 信号三模块 event_axis/swing_sequence/resonance_pair | **死袋** | `git log --all --grep recover-000X` 零提交；三模块+三测试 HEAD 全树零命中（内容 grep 亦零）；袋存 dead/（CREATE-GUARD MAP-MOUNTS / GATE-PRECOMMIT-RUN） |
| recover-0003 | tech_factor_pipeline | **死袋** | 文件 HEAD 不存在；袋存 dead/（CREATE-GUARD 无 token） |
| mini-0002 / mini-0003 | 红证尺测试 / fill writer（mini-0004=reaper 现算化已落地见上） | **死袋** | mini-0002：红证尺测试不在 HEAD（盘面 untracked）；mini-0003：`scripts/start_paper_session.py` 写者腿不在 HEAD。两袋存 dead/。`git log --all --grep "st-mastertc-mini"` 仅 2 笔提交（mini-0001=90d8e3b33c、mini-0004=a6ae287dab），mini-0002/0003 查无提交 |

**总判**：6 袋中 3 落地、3 死袋；死袋部分与 P0-1 同根（交付报告 DONE 面失真）。blob 保全完好（袋 JSON 内 `blob_ref`+sha256 在案，可整袋取回）。

### 3. 死信 1548+ "官方归档子命令"闭环 —— **真闭环机制，非空壳**

- `scripts/commit_queue.py` HEAD L3106-3316 `dead_archive_letters`：三闸（serializer 租约存活整体拒绝 / 年龄 `--days` / revival 互斥）+落地校验 fail-closed（modify=树在、delete=树无，"判不了就不归档"）；同卷 `os.replace` mv 非删可逆；manifest.jsonl 逐件留痕（含 `tool: commit_queue.dead-archive`、`verify`、时间戳）；缺省 dry-run 零盘面变化，`--execute` 才动盘，`--no-verify-landed` 留 verify=off 痕。CLI `dead-archive --help` 实测子命令在册（--days/--no-verify-landed/--execute/--json）。
- 实效实证：dead_archive_20261004（599 封）、20261006（460 封）、20261007（213 封）三袋+manifest 在盘；blobs/ 24061 对象（B→D 类引用保全面真实）。
- **l3b 归属干净**：20261007 袋 manifest 中仅 **1 封**时间戳=08:50:57（chainpile-0041，与 l3b 台账逐字吻合）；其余 **212 封均为 20:21:09-11** 由 **st-closeout-basereq-20261006** 归档（其提交 79ccaf787e 20:23:21 落册自述"本窗 212 袋归档销案"，且先落了落地判据大小写不敏感回退）——非 st-mastertc 所为，不计入本审对象。该批含 l10 裁定#488 死信（q-20261007-st-mastertc-l10-0001）：l3b"禁代改未动"属实（其唯一归档=08:50 一封）；#488 内容已由 st-mastertc-close 6555113e56（10:07:28，ruling_registry.yaml +33 行，HEAD L4242 实证 `裁定#488` 在册）接管重落，归档满足其自订路径③"内容已被他 commit 覆盖"。
- **计数相容性**：3f47dbd6d5 自告（13:40 快照）done=521/dead=1684；本次只读 `status` 读数 pending=0/processing=1/done=536/dead=1516。核算：1684 − 212（20:21 归档）+ 44（其后新死信净增）≈ 1516，done 521→536（其后 +15 落地）——**相容**（方向与量级自洽；注意两者皆非 HEAD 态，系运行时快照）。`st-mastertc=172` 系 `status | grep -c` **行计数**（每 item 的 qid 行+session_id 行各计 1，≈2 行/件），非件数；当前件级实测 done41+dead29+archived25=**95 件**。指标口径已披露但易误读（P2）。

### 4. C152（4e43d191a3）—— **真完成**

- HEAD `scripts/governance/scheduled_task_reconcile.py:51`：`$i.LastRunTime.ToString('yyyy-MM-dd HH:mm:ss',[System.Globalization.CultureInfo]::InvariantCulture)` 在位（commit 实测 1 行改动）。
- HEAD `tests/governance/test_scheduled_task_reconcile.py:249` `test_last_run_format_pins_invariant_culture` 在位（断言 InvariantCulture 钉死+格式串成对正则）。17/17 绿系会话自述，本审计不重跑（避免写缓存）；HEAD 面文件与测试齐备。

### 5. C300（bb6a03f5c1）—— **真完成（纯注释）**

- commit diff 实测仅 +1 行注释（`config/flags.yaml` L114：`# [C300 销账 2026-10-07·总包夜战 master_tc_20261006 §六代裁基准] 维持现状（enabled=true production）；复核窗口=下维护窗…`）；HEAD 实测 `commit_queue_interactive: enabled: true`、`implementation_status: "production"` 语义零变更。销账注记+复核窗口在位。

### 6. C05 DEEP_DIVE_R2.md —— **真完成（RED 如实，无洗绿迹象）**

- HEAD `docs/_working/commit_speedup_campaign/60_deep_dive/DEEP_DIVE_R2.md` 在位（83 行，随 0fed20a6cf 落册）。
- 如实性核验：§0 结论闸明写**"未达标（RED）"**；§3 裁决 RED（判据"无可回收>5min/天"，实测锁等待单项 ~110min/天、10-06 单日 181min）；§2 如实记"喂料饥饿未修复（claim_none 96.7%）、重试环 712 次/天恶化"；已修复 3 项（rc=-1 infra 超时归零/租约互斥/integrity 同步税）与残余 3 项分开陈述；C147 因前置不满足不落册的纪律执行在 workbook 与 R2 §4 双向一致。**未发现把 RED 写成 GREEN 的迹象**。83 行超卡面 ≤80 上限 3 行，l3b 已自报"记注不重做"（P2 以下）。

## 证据块

1. **死信存档**：`.runtime/commit_queue/dead/`（1520 封，运行时态）；`.runtime/commit_queue/dead_archive_20261007/manifest.jsonl` 213 条（08:50:57×1 + 20:21:09~11×212，全部 `tool=commit_queue.dead-archive, verify=on`）。信体结构含 per-file `path/blob_sha256/blob_ref/action`，本审计据此做内容级对拍。
2. **HEAD 对拍脚本口径**：`git show HEAD:<path>` 逐件取内容→sha256 对 `blob_sha256`；delete 件以"树无"为落地。10 封抽样原始读数见逐项 verdict 表。
3. **幽灵翻译条目**：`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml` L67723/67731/67739/67747 四 module_path 在 `git ls-tree -r HEAD` 零命中；落地提交=45c1f0b224（st-mastertc-l6 docs 袋，`git log -S` 双确认）。
4. **归档子命令**：`git show HEAD:scripts/commit_queue.py` L3106-3316（`dead_archive_letters`+`DeadArchiveError`）、L4408-4545（CLI）；`python scripts/commit_queue.py dead-archive --help` 输出在案；`status`/`health` 只读实测（pending0/proc1/done536/dead1516；dead 分类 item1010/env244/other261）。
5. **20:21 批归属**：79ccaf787e（2026-10-07 20:23:21，st-closeout-basereq-20261006）提交文自述"212 袋归档销案"+落地判据大小写回退；与 manifest 20:21 时间窗互证。
6. **裁定#488 落地**：6555113e56（10:07:28，ruling_registry.yaml +33）；HEAD L4242 `- ruling_id: "裁定#488"`。
7. **C152/C300**：4e43d191a3（2 文件，+266/-1）、bb6a03f5c1（1 文件，+1 注释）commit diff 实测；HEAD 行号见逐项 verdict。
8. **恢复班死袋原文**：dead/ 下 q-20261007-st-mastertc-recover-0002/0003/0004/0005、mini-0002/0003 六袋 JSON（死因+文件清单逐袋读取）；mini-0004/0001 为 done（GW 标记 `[GW:st-mastertc-mini:q-...-mini-0004/0001]` 在两提交 body）。

## 小结 + P1/P2 建议

**小结**：车道 C 六项中，C152/C300/C05 三项为干净的真完成；C02 死信分诊主体成立（三态分类与死因叙事 10/10 抽样相符、唯一"复活"封逐字节实证）；dead-archive 官方通道是带三闸+manifest+mv 可逆的真闭环且 l3b 归属干净（1 封）。**核心问题集中在"恢复班自告面"**：6 袋仅 3 袋真落地，信号三模块/tech_factor_pipeline/红证尺/fill-writer 四卡施工虽真、死信虽保全，但交付报告逐卡记 DONE 无未落限定，且留下 4 条 HEAD 幽灵翻译册条目——Owner 若按三态总表验收将高估战役实际落地面。

**P0**：仅 P0-1（见上），建议 Owner 门位裁决处置顺序：先清 4 条幽灵注册条目（或加速代码袋落地），再修交付报告三态总表限定词。

**P1**：
1. C02 分诊表 chainpile-0066 内表矛盾（1/1 landed 归"需属主"，"三闸 pass 名单耗尽"与其自表相抵）——建议维护班复核当日 dry-run JSON 留痕（若有）补记原因。
2. 交付报告"st-mastertc=172"为 grep 行计数非件数（真实件级=95），建议更正为件数口径。

**P2**：
1. 分诊表 landed 计数 2/10 抽样 +1 虚增（同源：delete registry_mass_deletion_gate.py 未落地被计入）；不影响三态分类，建议维护班接手时以信体 blob_sha256 重算。
2. DEEP_DIVE_R2.md 83 行超卡面 80 行上限（已自报，无需动作）。
3. 红证尺测试件在盘面为 untracked 态（`??`），属会话遗产，建议维护班随 mini-0002 死信处置一并收口，防误当在途 WIP 清理。
