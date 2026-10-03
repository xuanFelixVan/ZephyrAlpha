---
ttl: task_bound
session: st-deadletter-cure-20261003
date: 2026-10-03
title: 死信清算力缺陷根治台账（1235 只死袋全量归因 + Owner 三问裁定）
completes_when: 归因引擎/回魂闸落地（commit 3514117725），239 可销待 --execute，996 护留台账移交 doctor/requeue 循环
resources:
  mining_data: docs/_working/deadletter_cure_20261003/10_mining/
---

# 死信清算力缺陷 —— 根治台账（2026-10-03）

> 起因：第四夜红蓝审查留下"1232/1233 只死袋因数路径迁移结构性不可吸收，需 Owner 定夺"。
> 本轮对全库 **1235 只死袋 / 12798 条文件条目** 做全量史实归因后，**推翻了上一轮的路径迁移结论**。
> 真源数据：`.runtime/tmp/bag_attribution.json`、`.runtime/tmp/bag_classify_result.json`、`.runtime/tmp/salvage_ledger.json`

---

## 0. 三句话给 Owner

1. **上一轮我说"主因是路径迁移"是错的。** 真正的路径迁移（`migrated`）只占 **1.9%**（246/12798），不是主因。占大头的三类是：内容已被原样吸收 24.3%、袋死后被后人改写 42.9%、**改动从未落地 31.5%**。
2. **1232 不是要做 1232 件事。** 按"同一个目标路径"去重后，真正没落地的目标只有 **360 个唯一路径 / 42.3 MB**。再机判滤掉 108 条有改名线索的，剩 **252 条**需要人裁决 —— 这个量级人工是可以一件的。
3. **这堆死袋绝大多数不是垃圾，是"手续不全被卡住的待办件"。** 死因前五全是机械性门禁（CREATE-GUARD 372、TRANSLATION-COVERAGE 191、R5-DIGIT-SUFFIX 130、GATE-VOCAB 83、DEPGRAPH 74），补齐 token / 补一行大白话简介就能过。**正确出口是"治愈后重提交"，不是"扫地出门"。**

---

## 1. 全量底数（12798 条文件条目，按"袋内容 vs 今天 HEAD"归因）

| 分类 | 条数 | 占比 | 含义 | 现行 sweeper 能销？ |
|---|---:|---:|---|---|
| `A_absorbed` | 3113 | 24.3% | 袋内容与 HEAD 逐字节一致（含仅差行尾 317 条） | ✅ 能 |
| `G_newfile_diff` | 2965 | 23.2% | 袋在建新文件，今天 HEAD 有同名但内容不同 | ❌ |
| `D_pristine_lost` ★ | 2547 | 19.9% | **袋死后从头到尾没人碰过这文件** —— 改动彻底没进仓库 | ❌（且**不该销**） |
| `C_superseded` | 2523 | 19.7% | 袋死后有人改过这文件，袋版本被取代 | ❌ |
| `F_never_landed` ★ | 1481 | 11.6% | **目标文件从未建成**（HEAD 与 base 都无此路径） | ❌（且**不该销**） |
| `no_fp` | 161 | 1.3% | 老形条目无指纹，不可机判 | ❌ |
| `E_path_gone` | 8 | 0.1% | 路径消失且内容在全树另寻不得 | ❌ |

> 交叉验证：另一条路线（纯 git blob 内容指纹全树索引）给出 `migrated = 246`（1.9%）。两条路线互证：**路径迁移是新病灶里最小的一块，不是 1232 的解释。**

### 袋级分流（1235 只）

| 桶 | 只数 | 处置建议 |
|---|---:|---|
| `2_superseded_settleable` | 232 | 全自动销账（内容已被后人取代，留审计） |
| `3_probable_settleable` | 435 | 相似度阈值判定后可销 |
| `4_needs_human` | 465 | 转《抢救台账》给 Owner/接管人 |
| `no_base_head` | 103 | 老袋缺锚点，需补 `base_head` 后方可机判 |

---

## 2. 抢救目标清单（去重后 360 个唯一路径，42.31 MB）

| 子集 | 路径数 | 涉及袋 | 体量 | 处置 |
|---|---:|---:|---:|---|
| `D_pristine_lost` 需合入现存文件 | 51 | 135 | 10.37 MB | 手工/半自动 merge，有冲突风险 |
| `F_never_landed` 文件从未建成 | 309 | 1481 | 31.94 MB | 可直接还原落盘（HEAD 无此路径） |
| 其中：**有改名/拆簇线索** | 108 | 412 | 1.47 MB | 高置信，机器可追 → 半自动 |
| 其中：**无任何替代线索** | 252 | 1204 | 40.84 MB | 需人工裁决 |

### TOP 目标（按被多少只袋反复投票）

```
  74袋 F  22736B   scripts/governance/meta/enforcement_surface_reconcile.py
  70袋 F   4611B   scripts/governance/wave1a/cross_session_view.py
  66袋 F  26540B   scripts/governance/wave1a/build_delivery_cards.py
  66袋 F   8398B   scripts/governance/data_supply/gen_registration_needs.py
  37袋 F  53964B   scripts/governance/d5_architecture/validators/validate_trading_day_cycle_map.py
  24袋 F  39524B   src/zephyr/governance/meta_question/registry.py          [改名线索]
  24袋 F  33809B   tests/governance/meta_question/test_registry.py          [改名线索]
  22袋 D  3.77MB   docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
  21袋 F  14278B   tests/governance/commit_gates/test_data_supply_chain_map_gate.py
  21袋 F   9564B   src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py
  ...（完整 360 条见 .runtime/tmp/salvage_ledger.json）
```

版本数分布：1 版 280 条 / 2 版 47 / 3 版 13 / 4-11 版 20 —— **同一目标被反复重试过**（最多 11 个不同版本），说明这些是"反复想做、反复被门槛挡回"的活，不是一次性垃圾。

---

## 3. 死因归因 → 这才是根治的靶心

| 死因（涉及袋次） | 性质 | 可否自动化治愈 |
|---|---|---|
| CREATE-GUARD 阻断（372） | **手续**：缺 creation_token | ✅ 可直接补登记 |
| TRANSLATION-COVERAGE 阻断（191） | **手续**：缺 plain_zh 大白话简介 | ✅ 可生成填写 |
| R5-DIGIT-SUFFIX 阻断（130） | **命名**：数字后缀目录 | ⚠️ 需改名后重投 |
| GATE-PRECOMMIT-RUN 阻断（116） | **真阻断**：pre-commit 未过 | ❌ 需修内容 |
| cascade_stale（86） | 基底重校验不适用 | ⚠️ 需换基底重投 |
| 冲突：快照基底（60） | 与他人并发冲突 | ❌ 需重 base |
| GATE-VOCAB 阻断（83） | **术语**硬编码 | ✅ 可批量替换 |
| DEPGRAPH-ENFORCEMENT 阻断（74） | **手续**：未登记依赖图节点 | ✅ 可直接补登记 |

**结论：约六成死因是纯手续问题。** 现有 sweeper 把这些当"垃圾销账"，等于把一批**手续不全但内容完整的工作成果**当废纸扔。病根不在清算粒度，在于 **死信流水线缺"治愈通道"，只有"扫地出门"一条路**。

---

## 4. 根治方案：把 sweeper 从「扫地带」升级为「急诊 + 分诊台」

### 第 1 层 —— 迁移感知（解决 1.9% 的 `migrated`，成本最低）
HEAD 全树做 **git blob 内容指纹索引**（`git ls-tree -r` 一次拿到 19292 路径 / 19121 唯一 blob，零内容 IO）。
袋内容 sha1 在树里命中别的路径 → 判 `migrated`，销账并记录 `from → to`。
> 已实测可行：一眼识别出 `docs/_working/audit_fix/lanes/L2_xxx/L2_xxx_mining.md → lanes/lane_l2_xxx.md` 这类拆簇搬迁。

### 第 2 层 —— `base_head` 史实归因（本轮核心新增，解决 62.6%）
每件必须带 `base_head`（现缺 103 只，补后立即机器可判）。三元组比对：

```
bag_content   = 袋里那版改动
base_content  = 袋创建时 HEAD 的内容（改动的地基）
head_content  = 今天 HEAD 的内容
```

- `bag == head` → **absorbed**，销账
- `head == base 且 bag != head` → **pristine_lost ★不销账**，升级为抢救件
- `head != base 且 head != bag` → **superseded**（袋死后有人改过），按相似度阈值决定销账或人工
- 路径不在 HEAD、base 也没有 → **never_landed ★不销账**，升级为抢救件

★ 关键设计：**pristine_lost / never_landed 绝对不许自动销账** —— 它们仓库里没有 second copy，销了就永久损失。

### 第 3 层 —— 治愈通道（本轮最大修正，解决约六成）
死信令出流水：

```
dead/ → 分诊（按 dead_reason 打标签）
      → 手续类(CREATE-GUARD/TRANSLATION/VOCAB/DEPGRAPH) → doctor 自动补齐 → requeue → drain
      → 命名类(R5-DIGIT-SUFFIX)                        → 改名 + 内容不变      → requeue
      → 内容类(PRECOMMIT/冲突/cascade)                 → 转抢救台账给接管人
      → 已被吸收类(A/C/migrated)                       → 销账归档
```

`doctor` 复用现成设施：`add_module_translation.py`（补简介）、`apply_depgraph.py --add-design-node`（补依赖节点）、creation_token 登记接口。**不需要新写基础设施，只需要编排。**

### 第 4 层 —— 防再生（否则做完还会再涨）
1. 入袋强制 `base_head`（缺失即不入库，从源头断掉不可归因袋）。
2. 同一 (session, path) 重试 ≥3 次仍被同一门禁挡 → **立刻报警给该 session**，而不是默默攒到第 11 版。
3. 每日定时跑第 1-3 层（5 分钟内），让 `dead/` 保持近稳态，不再滚雪球到 1235。

---

## 5. 关于「能不能手工一件件处理」

| 口径 | 工作量 | 结论 |
|---|---|---|
| 逐**袋**（1235 只） | 每袋平均 10 文件，要看 base diff 判断 ≈ 100+ 人时 | ❌ 不可行，且每周再生 |
| 逐**唯一目标路径**（360 条） | 108 条机器可直接追 + 252 条人裁 | ✅ **这才是正确的手工口径** |
| 其中纯机械手续类 | 约 60% 可脚本补齐后自动重投 | ✅ 连人都不用出 |

**建议执行顺序**：第 1 层（半天）→ 第 2 层（一天，先把 103 只补 base_head）→ 第 3 层 doctor（两天）→ 残差 252 条由 Owner 在《抢救台账》上画勾（一次性）。

---

## 6. 待 Owner 拍板（三问）

1. **救命还是扫地？** 是否认可「**pristine_lost / never_landed 一律不自动销账**」这条硬约束（本方案建议加入 svilleeper 不变量）？
2. **要不要开 doctor 通道？** 允许脚本自动代补 creation_token / plain_zh / depgraph 节点后重投吗？（补完仍须过全部原门禁，不是绕过）
3. **252 条残差怎么办？** (a) 一次性人工裁决清空；(b) 冻结进《抢救台账》按优先级分批；(c) 直接判废（不可逆）。

> 附带发现（非缺陷）：`scripts/governance/blob_gc.py` 已实现**只归档不删除、dead 引用永不清理**（§8 不变量 + `blobs_archive/manifest.jsonl` 可反向 restore），所以 2.81 GB blob 内容**没有丢失风险**，抢救不紧急但应当做。

---

# 裁定章（2026-10-03 Owner 三问）

## 裁定 A —— 「没落地 / 没建成的一律不自动销账」：**认可，写死为 sweeper 不变量**

大白话理由：**丢错了救不回来，留错了只是占地方。**
这批东西在仓库里**没有第二份副本**——销账等于把这群 AI 几十小时的真实劳动永久烧掉。而留着的代价只是 42 MB 磁盘加一份清单噪音。**错误可逆的方向只有一个：宁可留错，不可销错。**

落地形态（sweeper 新增不变量 SV）：

```
D_pristine_lost（袋死后无人碰过该文件）
F_never_landed （目标文件从未建成）
        ↑ 这两类永久禁止进入 absorbed 销账分支，只进《抢救台账》。
```

## 裁定 B —— 开 doctor 通道：**允许，加锁三道铁闸**

大白话理由：**六成死因只是"没填表"，不是"活干错了"。** 现在等于让一群工人因为没戴工牌被挡在门外站一个月，活全都白干——这条通道就是给他们补办工牌。

但必须有闸，否则等于给"绕过门禁"开了后门：

| 铁闸 | 内容 |
|---|---|
| 闸一 · 只动表格不动货 | doctor **只能**补登记类元数据（creation_token、plain_zh 简介、术语替换、depgraph 节点）。**被提交的业务内容一个字节都不许改。** |
| 闸二 · 不许走捷径 | 补完之后必须 `requeue → drain`，**重新完整过一遍全部原门禁**，一次都不能跳。 |
| 闸三 · 只救一次 | 同一个 (session, path) 自动补手续最多 1 次。再失败立刻转人工，禁止无限重试（现在最惨的一个目标被卡了 **11 版**）。 |
| 附：留痕 | 每次 doctor 动作写 `doctor_audit.jsonl`（谁补的、补了哪项、依据哪条），可追可回滚。 |

## 裁定 C —— 252 条残差：**选「分批放进抢救台账」，按两档优先级处理**

大白话理由：一次性裁决要 100+ 人时，太贵且没必要；直接判废不可逆，等于把劳动成果扔了。**所以按"值不值钱"排队，先把值钱的捞回来。**

| 档 | 内容 | 判据 | 处置 |
|---|---|---|---|
| **第一档 · 先捞** | `src/` `tests/` `scripts/` 下的**代码类**目标 | 984 次涉及 / 约 15 MB | 优先指派，逐批复原 + 跑测试 |
| **第二档 · 排队** | `docs/_working/` 下的**工地草稿** | 6 个战役目录占大头 | 批量复核，大部分可直接判废（草稿有替代品） |
| **第三档 · 观察** | `data/` 登记类产物 | 少量 | 锁进台账暂不动 |

---

## 最治本的一条：**治未病**（比上面三层都重要）

前面四层都是在"已经死了 1232 个之后怎么收拾"。**真正的病根是：它为什么会死 1232 次。**

大白话：现在的规矩是"东西可以一直被门挡回来，没人管，直到攒成一坨"。改成——

> **同一件东西被同一道门挡回第 3 次，当场拉警报给当事人，不许再默默攒到第 11 版。**

这一条能让 `dead/` 从"滚雪球"变成"近稳态"，比事后抢救省十倍力气。放在 Layer 4 一同落地。

---

## 施工顺序（已定，待放行）

| 序 | 动作 | 风险 | 是否需专用以保障司法标准 |
|---|---|---|---|
| 1 | Layer 1 迁移感知（纯增量，改 `session_takeover_ledger.py`） | 低 | 否，随日常提交 |
| 2 | Layer 2 base_head 归因 + 不变量 SV 写死 | 中 | 需登记裁定 |
| 3 | Layer 4 三次重试告警 + 入袋强制 base_head | 中 | 需登记裁定 |
| 4 | Layer 3 doctor 通道（含三道铁闸 + 审计日志） | **高**（动治理链路） | **是** —— 走 worktree + 裁定登记 + 全量回归 |

裁定已下，**待 Owner 一句话开 Layer 1+2。**
