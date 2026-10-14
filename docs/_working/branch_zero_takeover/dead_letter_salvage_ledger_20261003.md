---
ttl: task_bound
session: st-deadletter-cure-20261003
date: 2026-10-03
title: 死信清算力缺陷根治台账（1235 只死袋全量归因 + Owner 三问裁定）
completes_when: 归因引擎/回魂闸落地（commit 3514117725），239 可销待 --execute，996 护留台账移交 doctor/requeue 循环
resources:
  mining_data: docs/_working/deadletter_cure_20261003/10_mining/
created: 2026-10-03
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


---

## 四十六·10-14 收口审计（Owner「对话能否关闭」之问的实读答复）

> 全部结论来自 2026-10-14 当场命令取证，不凭记忆断言。
> 详版四件：`docs/_working/deadletter_cure_20261003/{00_skeleton,20_design,30_construction,40_acceptance}/`
> （10-14 重建；原五子册未入 git 于工作区重置中丢失，故本批先以本章入 git 保底，四件随后随行）。

### 1. 五笔提交：全在，零回退

`3514117725`（回魂根治+史实归因）／`cce0dcd2a4`（裁定#479 文档批）／`ced3a79a63`（翻译册先行批）／
`2b28c6fbf1`（车道 BCD 合流）／`d254a52656`（测试改名补丁）——逐笔 `git cat-file -e` 核验对象存在，
`git log --since=2026-10-03` 检索 revert/回退/回滚 **零命中**。
代码面现读：`session_concurrency.py` 命中 `reincarnation_count` **14 处**、
`session_takeover_ledger.py` 命中归因引擎符号 **18 处**，主改动仍在 HEAD 正身未被覆盖。

### 2. 机制活着

回魂拦截审计 `register_reanimation.jsonl` **18,634 行**（末次 10-14 14:57）；
doctor 通道 `doctor_audit.jsonl` **223 条**（10-05 实跑，非纸面）；
现存死信袋 `base_head` 已是真 commit 值而非 `dev` 占位 ⇒ Layer4 强制 base_head 生效。

### 3. 战果：1235 → 98（但执行主体不是本对话）

`dead/` 1,235→98、`done/` 795、`pending/`=0、`processing/`=0。
**如实记明**：这 1,137 袋的消化由 10-05~10-14 后续多支施工队
（`st-cure-p0*`／`st-deadcure*`／`st-deadmass2,3,3b-20261014`／`st-wkcure*`／`st-deadclean-20261013`）接力清偿，
本对话建的归因引擎与 doctor 通道是被他们接过去用的工具。**结果达成，不冒领执行。**

### 4. 资产损失（本战役自己的教训）

`docs/_working/deadletter_cure_20261003/` 五个子册原稿 10-03 写出后**从未入 git**
（`git log --all --name-only` 全窗仅 `r5_exemption.md` 一条），在多次工作区重置与
AUTO-ENQUEUE stash 隔离中清出且无版本可恢复——**正是本战役自己写进记忆的那条教训**。
纪律：文档产物写完当批即入 git，不留未跟踪过夜。

### 5. 13 项待办真实状态

完成/被消化 5 项（孤儿认领、sweep 沉降、doctor 生产、base_head 回填、本次审计）；
部分 1 项（文本误报门：仍靠 noqa/改名绕行，源码未根治）；
**未完成 7 项**：doctor 自愈升级、登记合一、会话活性状态机统一、**红蓝极限对抗**、
记忆问题库清账、**堵点本清账**、归因体系自修（并发全量覆写/cat-file 注入面/cascade_diff 基线）。

### 6. 堵点本：不是没清，是更堵了（本次实读）

10-03 记录 TOP 为 `GATE-PRECOMMIT-RUN ×50`／`QUEUE-LANDING ×36`；
10-14 实读 **近 24h 共 293 次：QUEUE-LANDING ×154、GATE-PRECOMMIT-RUN ×79**。
**堵点计数 11 天翻了约 3 倍**——这是本次审计最硬的负面结论。

### 7. 本次提交链的实证（与 10-03「八连死」完全同构）

一次纯文档提交（4 件 .md + 1 件 registry）连撞：
WORKTREE-REQUIRED → SESSION-REQUIRED → CREATE-GUARD（token 读 HEAD 的鸡生蛋）→
TAKEOVER-PENDING ×N（**每次重投都留下新死 sid，register 受 V5 频率护栏降级致活性锚冻结，
同 sid 重投必撞自身 stale claim，形成自循环**）→ 他人死 sid `st-infoaxis-land-20261014`
stale claim 挡道（其 worktree dirty=35 有在途成果，本会话不越权接管，改走 `allow_overlap` 留痕）。

**结论：11 天过去，提交链路的堵点没有减少，八连死的病灶仍在原处。**
这也直接说明 §5 中「红蓝极限对抗 / 堵点本清账」两项未做，代价是持续的。

### 8. 结论：本对话不能宣告零遗留关闭

- 已收口：五笔提交零回退、核心代码在 HEAD、机制持续生效、车道 tmp 已清、
  暂存区无本战役残留（现 staged 37 件全为他人产物）、1235→98。
- 未收口：待办 7 项；文档资产有真实损失（已补救）；4 个裁定点待 Owner。

### 9. 待 Owner 裁定（4 条，不自批）

1. 是否授权弱化 TTL／R5／VOCAB 三门（改 warn）？
2. 文本误报门：源码根治（改 AST 判定）还是维持 noqa 绕行？
3. 未完成 7 项是否现在开 `st-deadletter-closure-20261014` 车道一次做完？
4. 本战役是否签封矿令、后续死信工作全转 `st-deadmass*`／`st-wkcure*` 常设班？


---

## 四十七·一键指令（新对话自含版，10-14）

> 独立件：`docs/_working/deadletter_cure_20261003/00_skeleton/01_一键指令_死信战役收口_20261014.md`
> 因 CREATE-GUARD 鸡生蛋（门读 HEAD 的 registry，token 须先行一批入 HEAD，而该批被他人死会话
> `st-infoaxis-land-20261014` 的 stale claim 挡在热册上，不越权接管）暂未独立入 git，
> 故先以本章全文追加保底。**新对话复制 BEGIN~END 之间整段即可冷启动。**

# 死信战役收口 —— 一键指令（新对话自含版）

> **用法**：新对话里把 `BEGIN` 与 `END` 之间整段复制粘贴进去即可冷启动。
> 本文件自含：项目背景 / 上下文浓缩 / 必读文件全路径 / 已完成清单 / 遗留 7 项 /
> 待裁定 4 条 / 环境坑 / 硬红线。**桌面副本会消失，仓库件才是真源。**

---

## BEGIN（以下整段复制）

### §0 启动块

你是接手 **ZephyrAlpha 仓库（D:\ZephyrAlpha，分支 dev）**「死信治理战役收口」的调查型施工 AI。
**本轮任务定位：先调查核验，不施工、不改 src/。** 输出带证据指针的《现状核验表》，
待 Owner 裁定后再动工。

当前 dev HEAD：`81ee2e9c427222197cd3cbff3e0ef9d49ddf9412`（2026-10-14）
Python 解释器（**必须用这个**）：`C:/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe`

开工第一步：读下面 §5 的 A 级文件，然后**复验 §6 已完成清单里的每一条是否仍成立**（磁盘面 + HEAD 面双查，
不凭本指令的文字断言）。发现与本文不符的，**以现读为准并更正本文**。

---

### §1 项目背景（30 秒版）

ZephyrAlpha 是一个 **100% AI 开发**的量化交易 + 治理单体仓。仓库自带一整套"AI 自治治理体系"：
提交要过几十道门禁（gate）、会话要注册、文件要登记 creation_token、死信要进队列复活。

**死信队列** = `.runtime/commit_queue/`：提交失败时把"当时想提交的文件快照"打包成一只**袋（bag）**存起来，
等修好问题再重投。2026-10-03 接手时积压 **1,235 只死袋 / 12,798 文件条目 / 2.81GB**，
本战役（session `st-deadletter-cure-20261003`）的目标就是根治这条链路。

**到 2026-10-14 的战果**：死袋 **1,235 → 98**、`done/` 795、`pending/`=0、`processing/`=0。
但**这 1,137 袋的消化不是本对话亲手做的**，是 10-05~10-14 后续多支施工队
（`st-cure-p0*` / `st-deadcure*` / `st-deadmass2,3,3b-20261014` / `st-wkcure*` / `st-deadclean-20261013`）
接力清偿的 —— 他们把本战役建的**归因引擎**和 **doctor 通道**接过去用了。**结果达成，不冒领执行。**

---

### §2 上下文浓缩（14 条，读完即懂全貌）

1. **bag/base/head 三元组**：`bag_content`=会话当时想提交的字节；`base_content`=建袋时的 HEAD（字段 `base_head`）；
   `head_content`=今天的 HEAD。三者对拍才能判断这只袋到底"吸收了没有"。
2. **八类史实归因**：`absorbed`(已吸收) / `migrated`(路径迁移) / `superseded`(被新版本取代) /
   `newfile_diff`(新建文件内容不同) / `pristine_lost`(原字节丢失) / `never_landed`(从未落地) /
   `no_base`(缺 base_head) / `no_fp`(缺指纹)。
3. **不变量 SV（铁律）**：`pristine_lost` / `never_landed` / `newfile_diff` / `no_base` / `no_fp`
   这五类**永远不许自动销账**（仓内无第二份就等于永久丢失）。
4. **我 10-03 的误诊，已更正**：我初判"1232/1233 袋卡住是因为路径拆簇/搬迁"，全库归因后
   `migrated` 仅 **1.9%**；真实大头是 `newfile_diff 23.2%` / `pristine_lost 19.9%` /
   `superseded 19.7%` / `never_landed 11.6%`。**教训：判"口径不行"之前先排除实现缺陷。**
5. **回魂（reanimation）病根在仓外**：一条仓外 bash 死循环 `while true; sleep 25; register`
   不断重注册，把死会话"救活"。证据 `register_rate_guard.jsonl` 14,494 行、约 105 秒节奏。
   **修法是机制层**（加 `reincarnation_count` 上限 + 存活时长上限），不必杀进程。
6. **为什么用 `reincarnation_count` 当主判据而不是年龄**：因为 `start_time` 本身会被那个循环改写，
   用年龄判断会循环论证（实测 c10 条目 `age=0.0h`）。
7. **doctor 三道铁闸（设计红线，禁止弱化）**：①只动注册元数据，绝不碰业务字节；
   ②绝不直接 requeue（处方末尾永远是命令，由人决定）；
   ③同 (session, family) 只自愈一次（`dead_letter_doctor_state.json`）。
8. **八连死标本**：同一批文件从入队到落地连死 8 次，每次不同门，其中**至少 4 次是"文本误报假门"**
   而非真问题 → 证明**链路成本的大头不在真门**。
9. **F 组四道假门（真身是 bug，只做字符串匹配）**：变量名含 `TOKEN` → 判硬编码密钥；
   出现 `.wait(timeout=` → 判常驻轮询；noqa 理由 <10 字 → 判无效；测试头继承模块 module_id → 判冲突。
   现状**全靠人工绕行**（改名 / 补 noqa / 改号），每遇一次付一次学费。
10. **资产损失（本战役自己的坑）**：`docs/_working/deadletter_cure_20261003/` 五子册原稿
    10-03 写出后**从未入 git**，在多次工作区重置 / AUTO-ENQUEUE stash 隔离中清出且无版本可恢复。
    **纪律：文档产物写完当批即入 git，不留未跟踪过夜。**
11. **判"资产不存在"的正确姿势**：本仓 100+ worktree，在途资产常以**未跟踪文件**躺在
    `.worktrees/` `.aidrafts/` `.qoder/` 等**点开头目录**里。`Glob` 默认忽略点开头目录、
    `git ls-files` 只列已跟踪 ⇒ **两者为"无" ≠ 资产不存在**。先 `git worktree list` 再跨区深扫。
12. **堵点本更堵了**：10-03 TOP `GATE-PRECOMMIT-RUN ×50` / `QUEUE-LANDING ×36`
    → 10-14 17:4x 实读近 24h **共 293 次**（`QUEUE-LANDING ×154`、`GATE-PRECOMMIT-RUN ×79`、`? ×19`）
    → 10-14 18:0x 再读仍在涨（`QUEUE-LANDING ×155`、`GATE-PRECOMMIT-RUN ×107`、**`TAKEOVER-PENDING ×22`（P50 49s）**）。
    **11 天翻约 3 倍，且 TAKEOVER-PENDING 已进 TOP3。** 这是最硬的负面结论，数字随时间变化，调查时自己重读。
13. **AUTO-ENQUEUE 会 stash 工作区**（宪法 §2.8）：提交锁忙转队列后工作区编辑会消失，
    属 stash 隔离而非丢失；死信 requeue 若工作区已还原会重建空差异 → 必再死信。
    正确姿势＝重做改动后直连重提。
14. **ReplacingMergeTree 读侧必须 FINAL**：`c1_market` 全系表日更重灌后双行可共存数日，
    裸查会读到双份（假收益）。跨列时区比较禁 `Date+INTERVAL` 裸写法。

---

### §3 必读文件（A/B/C/D 四级，全路径）

**A 级（必读，先读这 3 件）**
- `D:\ZephyrAlpha\docs\_working\branch_zero_takeover\dead_letter_salvage_ledger_20261003.md`
  ← **§四十六 10-14 收口审计**在这（已入 git，commit `5e2d831fc3`，最可靠的现状真源）
- `D:\ZephyrAlpha\docs\_working\deadletter_cure_20261003\40_acceptance\20261014_closure_audit.md`
  ← 收口审计**详版**（含 13 项待办逐项定级表、六道门实证；**未入 git，磁盘件**）
- `D:\ZephyrAlpha\docs\_working\deadletter_cure_20261003\00_skeleton\README.md` ← 骨架册索引

**B 级（战役设计/施工，要动工前必读）**
- `D:\ZephyrAlpha\docs\_working\deadletter_cure_20261003\20_design\commit_map_and_slimming_plan.md`
  ← 48 道提交环 → 7 组地图、F 组四道假门、三套瘦身方案
- `D:\ZephyrAlpha\docs\_working\deadletter_cure_20261003\30_construction\20261003_construction_log.md`
  ← 五笔提交施工账、85 新增测试、doctor 三铁闸、八连死标本
- `D:\ZephyrAlpha\docs\_working\deadletter_cure_20261003\r5_exemption.md` ← 目录名数字后缀豁免标记

**C 级（代码真源，改前必读）**
- `D:\ZephyrAlpha\src\zephyr\security\access_control\session_concurrency.py`
  ← 回魂根治本体（`reincarnation_count` / `_is_reanimation` / `_REINCARNATION_LIMIT=5` / `_MAX_SESSION_LIFETIME_SECONDS=6h`）
- `D:\ZephyrAlpha\scripts\governance\session_takeover_ledger.py`
  ← 史实归因引擎（`GitBlobReader` / `head_blob_index` / `classify_entry` / `triage_bag` / `sweep_with_attribution`）
- `D:\ZephyrAlpha\scripts\governance\dead_letter_doctor.py` ← doctor 通道（MOD-GOV-048）
- `D:\ZephyrAlpha\scripts\commit_queue.py` ← 队列（三次重试告警 / `backfill-base-head` 子命令）
- `D:\ZephyrAlpha\scripts\governance\commit_queue_landing.py` ← 落地器（`_pool_seal_dead_letter`）

**D 级（其他会话的交接包，与本战役互补，建议并读）**
- `D:\ZephyrAlpha\docs\_working\external_review_20261014\01_一键指令_新对话自含版.md`（25.8KB，十节自含）
- `D:\ZephyrAlpha\docs\_working\2026-10-14-HANDOFF-MASTER-PROMPT.md`（十一节，09-18 尽调线视角）

---

### §4 工作文件/数据全路径（调查要查的地方）

**队列**
- `D:\ZephyrAlpha\.runtime\commit_queue\dead\` （现 98 袋）
- `D:\ZephyrAlpha\.runtime\commit_queue\done\` （795）
- `D:\ZephyrAlpha\.runtime\commit_queue\pending\` （0）、`\processing\`（0）、`\dead_archive\`（0）
- `D:\ZephyrAlpha\.runtime\commit_queue\blobs\` （5,819 个 blob）
- `D:\ZephyrAlpha\.runtime\commit_queue\doctor_audit.jsonl` （223 条，doctor 实跑证据）
- `D:\ZephyrAlpha\.runtime\commit_queue\dead_letter_doctor_state.json`（自愈一次的状态位）

**会话/回魂审计**
- `D:\ZephyrAlpha\.runtime\session_registry.json`
- `D:\ZephyrAlpha\.runtime\session_registry_audit\register_reanimation.jsonl`（18,634 行）
- `D:\ZephyrAlpha\.runtime\takeover\resolved\`（已接管条目）

**堵点本**
- `D:\ZephyrAlpha\.runtime\audit\commit_block_events.jsonl`
- 溯源：`python scripts/governance/commit_perf_report.py --hours 24`

**注册表（改前必查，多方争抢热册）**
- `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\capability_canonical_file_registry.yaml`（creation_tokens）
- `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ruling_registry.yaml`（裁定册，**裁定#479** 在本战役加，含 `approved_paths` + `expires_at: 2026-11-03`）
- `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\module_translation_registry.yaml`（翻译册）

**测试（注意：目录已搬迁，不是 `tests/governance/`！）**
- `D:\ZephyrAlpha\tests\gov\governance\test_session_reincarnation_guard.py`（17 例）
- `D:\ZephyrAlpha\tests\gov\governance\test_dead_letter_attribution.py`（24 例）
- `D:\ZephyrAlpha\tests\gov\governance\test_dead_letter_doctor.py`（21 例，MOD-GOV-048）
- `D:\ZephyrAlpha\tests\gov\governance\test_commit_queue_backfill_lane.py`（14 例）
- 池化封袋测试（MOD-GOV-047）：**文件名待核实**，10-03 时为 `tests/governance/test_pool_dead_letter_seal.py`，
  现 `tests/governance/` 已不存在，疑似合并进 `tests/gov/governance/test_commit_queue_pool.py` —— **调查时先定位再断言**

**记忆**
- `D:\ZephyrAlpha\.workbuddy\memory\2026-10-14.md`（今日日志，含本战役收口记录）
- `D:\ZephyrAlpha\.workbuddy\memory\MEMORY.md`（长期备忘）

---

### §5 已完成清单（14 项，含完成概述 + 复验命令）

| # | 事项 | 状态 | 复验方式 |
|---|---|---|---|
| 1 | 五笔提交落地 | ✅ 全在 HEAD，revert 零命中 | `git cat-file -e <sha>^{commit}`；`git log --since=2026-10-03 --grep -i "revert\|回退\|回滚"` |
| 2 | Layer2 回魂根治（`reincarnation_count` + `_is_reanimation`） | ✅ 在 HEAD | `git show HEAD:src/zephyr/security/access_control/session_concurrency.py \| grep -c reincarnation_count` → 应 **14** |
| 3 | Layer1 史实归因引擎（八分类 + 迁移感知） | ✅ 在 HEAD | `git show HEAD:scripts/governance/session_takeover_ledger.py \| grep -c "_cat_spec\|classify_entry\|GitBlobReader"` → 应 **18** |
| 4 | Layer3 doctor 通道（MOD-GOV-048，三铁闸） | ✅ 已投产，**实跑 223 条** | `wc -l .runtime/commit_queue/doctor_audit.jsonl` |
| 5 | Layer4 三次重试告警 + 强制 base_head | ✅ 生效（袋 base_head 已是真 commit 值） | 抽查 `.runtime/commit_queue/dead/*.json` 的 `base_head` 字段 |
| 6 | 车道 B 池化封袋补齐 `_pool_seal_dead_letter` | ✅ 随 `2b28c6fbf1` 入树 | `grep -n "_pool_seal_dead_letter" scripts/governance/commit_queue_landing.py` |
| 7 | 车道 C `backfill-base-head` 子命令 | ✅ 在 `scripts/commit_queue.py` | `python scripts/commit_queue.py backfill-base-head --help` |
| 8 | 85 项新增测试 | ✅ 4 个文件已入 git（第 5 个待定位） | `git ls-files tests/gov/governance/` |
| 9 | 裁定#479 登记（含 approved_paths） | ✅ 入册 | `grep -n "479" docs/.../ruling_registry.yaml` |
| 10 | 翻译册补 doctor 词条 | ✅ 先行批 `ced3a79a63` | — |
| 11 | 165 孤儿 staged 认领 | ✅ **已被后续班消化**（现 staged 37 件全为他人产物，本战役零残留） | `git diff --cached --name-only` |
| 12 | 死信 1235→98 | ✅ 达成（执行主体为后续班） | `ls .runtime/commit_queue/dead/*.json \| wc -l` |
| 13 | 车道 tmp 清理 | ✅ 已清 | `ls .runtime/tmp/ \| grep -i "deadletter"` |
| 14 | 10-14 收口审计入 git | ✅ `5e2d831fc3`（台账 §四十六，纯尾追加零删除自证） | `git show --stat 5e2d831fc3` |

---

### §6 遗留 7 项（未完成，待施工）

| # | 事项 | 说明 | 入口 |
|---|---|---|---|
| E1 | **doctor 自愈升级** | 从"开处方"升级为"自动 apply + 自动 requeue 一次" | `scripts/governance/dead_letter_doctor.py` |
| E2 | **登记合一 `register_new_module`** | 4 个工具并存 → 收敛为 1 个；预检查磁盘而非 HEAD | `src/zephyr/gov_enforcement/` 内搜索 4 个登记入口 |
| E3 | **会话活性统一状态机** | A 组 7 个机制（pid/心跳/年龄/reincarnation/手持/看门狗/速率闸）→ 1 个 | `session_concurrency.py` |
| E4 | **红蓝极限对抗** | 多并发提交 / 中途 kill / 同文件并发编辑。**本对话只做过降级版**（6 次冻结 + 70 测试 + 8 袋实播） | 需新车道 |
| E5 | **记忆问题库清账** | 2026-10-02/03 记忆条目 + MEMORY.md 里记录的坑逐条销账 | `.workbuddy/memory/` |
| E6 | **堵点本清账** | `QUEUE-LANDING ×154` / `GATE-PRECOMMIT-RUN ×79` | `.runtime/audit/commit_block_events.jsonl` |
| E7 | **归因体系自修** | ①salvage_ledger 并发 `open("w")` 全量覆写 ②cat-file spec 注入面 ③cascade_diff 基线不稳 | `session_takeover_ledger.py` |

**另有 2 项磁盘资产待随行入 git（有丢失风险，优先级高）**
- `docs/_working/deadletter_cure_20261003/` 下 4 件（00/20/30/40）未入 git
- `capability_canonical_file_registry.yaml` 上已登记的 5 条 creation_token（目录级 1 + 文件级 4）未入 HEAD

---

### §7 待 Owner 裁定 4 条（**你不许自批**）

1. **减门授权**：是否授权弱化 TTL / R5 / VOCAB 三门（改 warn）？—— 弱化红线需人批。
2. **文本误报门**：`commit_queue_landing.py` 的 `proc.wait(timeout=…)`（第 1622/1627 行）
   是**源码根治**（改 AST 判定）还是**维持 noqa 绕行**（现状能活但要交学费）？
3. **E1~E7 是否现在开 `st-deadletter-closure-20261014` 车道一次做完**？
4. **本战役是否签封矿令**，后续死信工作全转 `st-deadmass*` / `st-wkcure*` 常设班？

---

### §8 环境坑（6 条，踩过）

1. **Python 必须用** `C:/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe`
   （managed 3.13 缺 `yaml` / `pydantic`，直接 `ModuleNotFoundError`）。
2. **pytest 必须带 `--basetemp` 指向系统 TEMP**（如 `C:/Users/fanzi/AppData/Local/Temp/xxx`）：
   仓内 `.runtime/tmp` 会触发安全删除批量守卫 → 假失败。且**不要**加 `-p no:cacheprovider`（会 INTERNALERROR）。
3. **`allow_non_worktree` 只是 `GitCommitGateway.commit()` 的 kwarg**，
   `scripts/commit_queue.py enqueue` **没有这个 CLI 参数**（预检 WORKTREE-REQUIRED 拦时只能用网关直调）。
4. **CREATE-GUARD 鸡生蛋**：门读的是 **HEAD 的** registry，新文件 token 尚未入 HEAD ⇒
   必须**两批法**（先单独提交 registry 让 token 入 HEAD，再提交新文件）。
5. **TAKEOVER-PENDING 自循环**（本次最耗时）：每次网关运行留 claim，进程退出后该 sid 的 pid 即 dead，
   而 `register` 受 **V5 频率护栏降级（活性锚冻结）** ⇒ **同 sid 重投必撞自身 stale claim**，逐次累积。
   解法＝**每次重投换唯一 sid** + 提交前用 `session_takeover_ledger.py --resolve <sid> --by <新sid>`
   清掉本前缀全部遗留 sid（脚本化一次做完）。
6. **他人死 sid 挡道**：`st-infoaxis-land-20261014` 的 stale claim 命中热册 registry
   （其 worktree dirty=35 有在途成果）⇒ **不越权接管**，走 `allow_overlap=True` 留痕；
   本次仍被拦 ⇒ registry 批未成。

---

### §9 硬红线（8 条）

1. **本轮只调查不施工**，不改 `src/`，不动他人文件。
2. **严禁代提交、代清理**他人改动（主区 porcelain 660+，约 400 为当日他人改动）。
3. **不变量 SV**：`pristine_lost` / `never_landed` / `newfile_diff` / `no_base` / `no_fp`
   五类**永不自动销账**。
4. **doctor 三铁闸**不得弱化（只动元数据 / 不直接 requeue / 同族只自愈一次）。
5. **不越权接管他人会话**（worktree dirty 有在途成果者尤其）。
6. **不自批 §7 的 4 条裁定**。
7. **判"资产不存在"前**必须 `git worktree list` + 跨 `.worktrees/` `.aidrafts/` 点开头目录深扫。
8. **文档产物写完当批即入 git**，不留未跟踪过夜（本战役已因此丢过 5 个子册）。

---

### §10 唯一合法停止点

完成以下**全部**才可停止并向 Owner 交账：
① §5 的 14 项逐项复验完毕并给出"仍成立 / 已漂移"结论（漂移项要给证据指针）；
② §6 的 E1~E7 定位到具体文件与行号；
③ 2 项磁盘资产（4 件文档 + 5 条 token）的入 git 阻塞原因查清并给出可执行处方；
④ 输出《现状核验表》落盘到 `docs/_working/deadletter_cure_20261003/40_acceptance/` 并**当批入 git**。

---

## END（复制到此为止）

---

## 附：本指令的生成与校验

- 生成时间 2026-10-14 18:0x，基于当场命令取证（不凭记忆断言）。
- 文中所有路径**已逐条 `[ -f ]` / `git ls-files` 核验存在**，唯一标注"待核实"的是
  MOD-GOV-047 池化封袋测试文件名（因 `tests/governance/` 已整体搬迁到 `tests/gov/governance/`）。
- 与 `docs/_working/external_review_20261014/01_一键指令_新对话自含版.md` 是**不同会话、不同视角**，
  两件互补，建议并读。
