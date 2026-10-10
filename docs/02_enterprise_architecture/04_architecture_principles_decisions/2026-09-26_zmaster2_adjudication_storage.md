---
ttl: permanent
doc_type: audit_report
completes_when: the four per-authority dispositions below are each either implemented or superseded by a newer measured ruling in this same file
---

# 存储裁定（总筹签署 · 2026-09-27）：总台账不搬 PostgreSQL，按"逐件定策 + 先修写手"执行

> 案卷＝`docs/_working/three_piece_infra/storage_decision/CASE.md`（st-p17-storage 道，895 行，
> 四方案成本/保护面/外部对标/翻案证据表全在该册）。本文件只放**裁定与依据**，不放调研过程。
> Owner 门位不变：本裁定＝**不搬**（零生产写、零迁移动作），任何未来 cutover 仍走 Owner（AGENTS §5 高档位）。

## 一、裁定

**净结论：不搬。** 四件权威各自定策，拒绝"一次大迁移"式回答。

| 件 | 现形态 | 裁定 | 第一步（已排产） |
|---|---|---|---|
| A1 `capability_canonical_file_registry.yaml` | 多段容器文件（2.95MB，含 `creation_tokens`/`capabilities`/`di_seam_exemptions`…） | 保留文件；把**每新建文件必写的 `creation_tokens` 段拆成独立册**（Option 1a， crates.io 同型先例）；配合"重取基底而非处死"改造 | 波13 包 23（re-base）→ 后接 1a |
| A2 `module_translation_registry.yaml` | 同上（3.62MB） | 保留文件；**先修写手**（见二.1），再谈分册 | 包 24（canonical 合并修 + 非空→空哨兵） |
| A3 `.ailocks` + `.runtime/session_registry.json` | 逐文件锁已分片；会话册单文件 | `.ailocks` 不动（已按文件分片＋机器级互斥索引）；`session_registry.json` 是**唯一真正的搬迁候选**（须跨 worktree 实时读），但**独立立项、独立呈 Owner**，不夹带进任何大迁移 | 只修读侧口径（半截主锚定），搬迁留 Owner |
| A4 试验台账（`n_trial_ledger`） | 环境 glob 扫 `grid_*/summary.json` | 不是存储病：改成**声明式批次键 + 执行器边界必记**（漏记的机制在"没人调用"，不在"存在文件里"） | 包 21（在跑） |

## 二、判据（全部本窗盘面亲读，非转述）

1. **病因不在存储层。** 本战役实测事故分布：内容门禁不合规 77%、并发/基底 13.5%、基础设施 7%。
   换存储引擎最多动那 13.5%，且其中"整档快照撞车"这一前提对 `_registry/catalogs/*.yaml` **已经不成立**
   ——2026-09-22 起落地侧就是**条目级三向合并**（`scripts/governance/commit_queue_landing.py:199-226`
   注释 + `is_registry_mergeable:222` + `three_way_merge_registry_yaml:874`）。
2. **PG 那条路已经铺好了，而且它现在不能搬。** W-M1 双轨实测（`.runtime/registry_ledger/dualtrack_20260926_234814.json`，
   本窗复算）：7 本权威里 **5 本 `zero_unexplained_drift: true`**（rule_catalog 294/294、arch_issue 805/805、
   errcode 794/794、candidate 623/623…），而**恰好是并发最高的两本不合**：
   `REG-CAPCAN-001` yaml 11891 / pg 11892（pg_only 1），
   `REG-MODULE-TRANSLATION-001` yaml 8603 / pg 8605，**`identity_collisions 567`（且 567 条 payload 互异）**。
   ⇒ 今天 PG 是"在并发最热处对不上账的滞后影子"。在这种状态下 cutover＝把 567 条未解释身份撞车**升格为真源**。
   翻案前置条件（机械可判，写死在此）：**连续 7 份双轨报告 `identity_collisions==0` 且 `zero_unexplained_drift: true`**，
   且投影页能自己落地（见下条 5）。
3. **四个反复出血的 bug 全是写手 bug，搬了照样带过去。**
   ①`add_module_translation.py:408-416` 合并时**跳过 `_CANONICAL_KEYS`**，而 `:294-300` 输出用
   `entry.get(k,'')` ⇒ 重复登记同一 `module_path` 会把在册的 `name_en/desc_zh/desc_en` **静默清空**
   （本窗实测确认，比"整条覆盖"更窄也更阴：字段级蒸发）；正确合并语义其实已在 `:575-587`（只在 `--dedupe` 分支）。
   ②判活不对称（`session_concurrency.py:227`）＋ `.ailocks` 未主锚定而会话册已主锚定（`lock_files.py:97` vs
   `session_concurrency.py:290-315`）⇒ 这是"半截修好"，不是"缺一个数据库"。
   ③试验台账 17.2% 漏记＝记录函数只有一个调用点且能被绕过。④令牌工具拒重复登记**早已实现**
   （`batch_creation_tokens.py:96-108,503-508`），无需新存储。
4. **git _blob_本身是执法面，DB 行不是。** 三件保护没有 DB 等价物（本窗逐文件读到实现）：
   `REGISTRY-MASS-DELETION` 以 **HEAD 侧身份集合差**判定（`registry_mass_deletion_gate.py:32`）；
   `HOT-FILE-BASE-FRESHNESS`（`claim_head..HEAD`）；own-scope 差分是**整套门禁的作用域地基**
   （`_diff_helpers.py:262-312`）；外加 `RULING-COMMIT-VERIFIED` 与 revert 即回滚。
   任何写手都能 `UPDATE` 的审计链不叫审计链——Option 2 不是"重实现"这些保护，是**降级**它们。
5. **本仓"没落地的中间件"历史全是读侧切面卫生失败，不是选型失败。** 本窗复测：`data/databases/` 下
   0 字节壳库 **5 个**（`depgraph.db` 0B 仍被 **39 个 .py** 引用、`integrator_progress.db` 2 引用、
   `progress.db` 5、`scheduler_progress.db` 0、`zalpha_metadata.db` 3 且被永久规则 `trae_034` 明文指向），
   另有活库 `governance.db` 195MB 今日 01:44 仍在写。⇒ 教训＝**先立法"指针不得孤儿"**（每登记存储路径必验
   存在/非零/引擎与声明一致），否则搬进 PG 只会多一类新孤儿。
6. **工作量对价不成立。** 案卷 §4-§7 报价：Option 0＝36–54h（且**明说不解决撞车**）、1a＝24–40h、
   1b＝70–110h、Option 2＝160–240h、Option 3＝45–90h（其中可入账 ~30h）。按 AGENTS §4.1 全资产净零，
   Option 2 **说不出它替代了什么**；Option 0+1a 替代的是上面逐条点名过的失效面，且全程可 revert。
7. **当下窗口不适合引入新依赖。** D 盘实测可用 19.0→20.8 GB（本窗两次读数），已在"停大批落地"熔断线（<25G）
   之内；把提交门禁吊在 PG 可用性上（`state.py:100-101` 当年刻意选择"降级而非耦合"）在此窗口是净减稳。

## 三、什么证据会推翻本裁定（翻案表，须按条实测，不接受偏好）

| # | 证据 | 方向 |
|---|---|---|
| E3 | "重取基底而非处死"改造**没能**消掉大部分 `cascade_stale` 死信（四周普查） | 才谈得上 1b/2；现由包 23 先做再测 |
| E5 | 实测同一本册并发道次 **≥3 成为常态** | 向 1b/2 |
| E7 | 三件 git 保护在 90 天内**确有**拦截近失事件 | 强判 Option 2 出局（当前证据在此侧） |
| E8 | 三件保护被证明是装饰件（自家普查口径） | 打开 Option 2 |
| E9 | W-M1 投影**自己**连续零漂移落地且 STALE/CONFLICT 真拦 | Option 3 由"可选"升为"必答" |
| E15 | A3 证明确实无法以文件形态满足跨 worktree 实时读 | 单独为 A3 立项（与 A1/A2/A4 无关） |

## 四、无论最终选谁都立刻做的事（本波已排，不等裁定）

1. 修 `add_module_translation` canonical 合并（复用 `:575-587` 语义）＋ 加"非空→空必须显式旗"哨兵。
2. 执行器边界强制调用试验台账记录函数（包 21 在做）。
3. 修判活不对称（工作道不被判死）。
4. 引入 fence token（`lease_epoch`）——Option 0/1/3 都需要它；只有 Option 2 假装不需要。
5. `_rebase` 而非处死（包 23 在做）。
6. 指针不得孤儿：新建/登记任何存储路径必过存在性+非零+引擎一致三查。

> 净零对价：本裁定**不新增册族**（并入既有 `storage_decision/` 目录，替代案卷 §1-§2 的"待裁"状态散文）；
> 不新增门禁台数（哨兵与三查挂在既有 reconciler/门禁上）；无迁移动作。
