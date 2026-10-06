---
ttl: task_bound
---
# L2 裁定册 related_arch 复燃清除 · 挖矿簿

> 环节=E06 ｜ 子环节=3（HEAD 面 / 加害批面 / 防复燃面）｜ 状态=**已闭环（由属主批吸收，本包让路未投该册）**
> 闭环读数：`git show HEAD:ruling_registry.yaml | grep -c "MOD-L00-004\|PS-CTR-003\|MOD-INF-043"` = **0**【亲验，落地笔 `f53316c6f9`】
> 本包施工过程实测过同一修法（worktree 内净 2改2、零残留），在得知属主袋 0009 载荷即为同一修法后
> **主动撤回投递**——同修不同抢，避免制造一次 noop 假落地。下文保留取证与判据（对"复燃会再来一次"仍有效）。

## 子环节 1｜现状三态实测（本包亲验，非引述）

册=`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（下称 RR）：

| 面 | `裁定#383`（行 5096） | `裁定#387`（行 5172） | 结论 |
|---|---|---|---|
| HEAD | `['MOD-L00-004']` | `['PS-CTR-003', 'MOD-INF-043']` | **带病**（3 硬） |
| git index | 同上 | 同上 | **带病 + 另有 36 行陈旧删除**（含 `第 411 号裁定/#412` 两条会被整删） |
| 工作树 | `[]` | `[]` | 干净（修法在属主工作树，从未进 HEAD） |

尺子无罪证明：`_ruling_arch_errors`（`src/zephyr/gov_enforcement/registry_alignment.py:459-466`）把值经
`_normalize_issue_ref`（缺 `#` 则补 `#`）后与 `architecture_issue_registry.entries[].issue_id` **原样集合**比对；
`git grep` 三个值在议题册中零命中（只在 10159/10181/10186/16124 行的散文里出现）⇒ 判悬空成立，非假红。

## 子环节 2｜加害批锁定（为何会"复燃"第二次）

- 首次修复=`a74e9a6c48`（09-24 04:36，numstat `2 2`，两行置空）；
- **加害批=`2608b45148`（09-24 11:13，`[GW:st-mapcensus-20260924:q-...-0006]`，numstat `25 2`）**
  ——同两处 hunks 把 `[]` 又写回成旧值；该袋 `base_head=None`，`meta.requeued_from=…-0001`（0001 是 04:35 的陈旧会话工作树快照）。
- 机制＝L1 的 `_merge_registry_file` 缺 base 时兜底 `old_dev^`，把"陈旧快照不含 `[]`"读成"theirs 主动删除 `[]`"并执行；
  保留侧拼接规则 `landing:499-502`（`base==ours → 采纳 theirs`）使"我方只改 2 行"必然输给他方陈旧袋。
- **⇒ 本 lane 与 L1 是因果序：先修 L1，L2 的修复才守得住。** 这也是本包把 ① 排最急的实证理由。

## 子环节 3｜"置空是否丢信息"的独立复核（不照抄案卷）

案卷称"真身已在 affected_files，无信息损失"——本包复核为**部分失真**：
`affected_files` 记的是**文件路径**，三个 id 在这两条裁定的**任何字段里都不再现**，册内指针确实会丢。
处置裁定（不改 Owner 令的"置空"方向，因其符合字段契约且 align 判据以议题 id 为唯一语义）：
把可追溯性**外置**到本挖矿簿（上表已记三值与其真身：`MOD-L00-004`→`storage_tiering.py:1,15`；
`PS-CTR-003`→`data_retention_contract.yaml:42`（另见 `rule_catalog_registry.yaml:3808`）；
`MOD-INF-043`→`infrastructure_registry.yaml:223`），不改条目结构、不动字段 schema、不新增字段
（新增 `related_modules` 属注册表 schema 变更＝高门位且非本包授权面）。

## 落地与判据

- 施工=本包 worktree 内**逐行等值替换 + 三处断言**（旧值命中数必须==1、上下文必须落在对应 `ruling_id` 块内），
  净 diff=`2 2`，落盘后 `grep -c 'MOD-L00-004\|PS-CTR-003\|MOD-INF-043'` = 0。
- 通道=队列（RR 属 `is_registry_mergeable` 前缀 ⇒ 走条目级三向合并，非整档覆盖）；
  审计班第 8 轮已用盘上合并器纯函数验过 `merged_ok=True 且精确吸收两处 []`，本包复核其反证（注入真冲突必死信）成立。
- 判据（E11 复跑）：`git show HEAD:RR | grep -c 'MOD-L00-004\|PS-CTR-003\|MOD-INF-043'` == **0**，
  且 L5 的 HEAD 锚点读数 `治理双向=0`。

## 遗留风险（已定性，非本包可闭）

主区 index 里 RR 的**陈旧 staged 层**仍在（0 增 / 36 删，含删掉 第 411 号裁定/#412）。
按 §3.4「他会话在途违规不代修」本包不动他包 staged 面；
风险面：任何吸收该 index 的落地会把 3 硬 + 2 条裁定一起带回。
缓解=① L1 已修（新袋必带基底）② 唯一在途含 RR 的 pending 袋 `st-cleanup-final-…-0009` 载荷实测
`BAD=0 / EMPTY=166`（干净，其落地反而采纳 `[]`）③ 本包已把该 index 风险登记进 LEDGER 待裁清单首条。
