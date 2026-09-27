---
ttl: task_bound
completes_when: 总包按本件 §2 批次表把 P1-P3 三批外科改完并跑绿 CR-007 与 check_governance_bidirectional（悬空清零）、§3 的 ROOR+ENTRY_SPECS 两条同批落地、§4 五项"不该做"逐条签署认可或驳回，本件即退役为施工档案
title: 图16 裁定域·词表与 entry_schema 回写清单及 ROOR 补条提案（复算版，交总包执行）
owner: st-mapbuild-20260924 车道 L-NUM16
---

# 91 词表与 ROOR 提案（图16 三项微创的第二、三项）

> 本件是**提案不是成果**——热册（`ruling_registry.yaml` / `docs/registry_of_registries.yaml`）本车道禁写，实际登记由总包执行。
> 第一项（取号器 `scripts/governance/next_ruling_id.py` + 27 项单测）已由本车道交付，本件只覆盖第二、三项。
> **所有数字本车道重算过**（复算命令见 §5，全部只读可复跑）；与 `fig16_ruling/00_skeleton.md` 不一致处逐条标 ⚠ 并说明原因。

## §0 结论先行

| # | 判据 | 结论 |
|---|---|---|
| 1 | 词表回写该不该做 | **该做，但方向要改**——`status` 不是"声明四值实测六值"，而是"**声明四值、实测五值、另有一个声明值零使用**"；更要紧的是 `category` 声明四值实测 **50 值**（骨架只报"50"未与声明对比），这是最大的一处失守 |
| 2 | `entry_schema` 回写该不该做 | **该做**——声明 10 键 / 实测 15 键，5 个未声明键使用量 41/6/3/1/1 非零（不是历史残渣）；另实测两类骨架未覆盖的偏差：**声明键缺失**（`affected_files` 缺 25 条、`related_arch` 缺 14 条、`superseded_by` 缺 5 条）与**类型漂移**（`date` 3 条是 YAML date 对象非 str、`affected_files` 3 条是 str 非 list、`evidence` 41 条全 str） |
| 3 | ROOR 补条该不该做 | **该做，但骨架给的理由不成立**——"未挂 ROOR=不存在于系统"被高估：裁定册经 `REG-CATALOG-001` → `registry_master_index.yaml:394` **两跳可达**（实测 11/14 个"ROOR 未列"册都属此类）。补条的**真实理由只有一条**——ROOR 在册才会被 `check_registry_consistency.py` CR-007 纳入 `entry_count` 实测对账，不在册=计数永远无人核（实测 `registry_master_index.yaml` 自身对裁定册记的 `entry_count: 196`，真值 **229**，已陈旧 33 条且无人报警） |
| 4 | 五项该不该做 | **不该做的照直写**——见 §4：手工改 `registry_master_index.yaml` 数字、为 `category` 立刻出词表件、`affected_files` 批量修路径、取号器配套新立 gate、把 `superseded_by` 从 1.7% 强填到骨架 §6.2 R-3 的 30% 阈值 |

## §1 复算基准与偏差总账（本件唯一计分面）

**基准**：worktree `D:\ZephyrAlpha\.aidrafts\st-mapbuild-20260924`，2026-09-25 实测。
**关键前提**：本 worktree 的 `ruling_registry.yaml` 已被他会话（图14/15 车道）追加原编 裁定#411 一条（`git diff` = +34 行未提交；L-INTEG 收口时与已落地 裁定#411 撞号，战役侧让号重编为 裁定 414 号（HEAD 册查无，落地后经取号器在正式通道补登），见 裁定 415（未登记，非在册引用）⑨），故**本车道复算值 n=229 而骨架为 n=228**——不是骨架错，是册在两批之间长了。凡分母敏感项逐条标注。

| 指标 | 骨架原值 | 本车道复算 | 判定 |
|---|---|---|---|
| entries 条数 | 228 | **229** | 一致（+1 来自在途 411） |
| `ruling_id` 重复 | 0 | **0** | 一致 |
| 在册最大号 | 410 | **411** | +1 同上 |
| 数字干唯一值 | 217 | **218** | +1 同上 |
| 号段空洞（1..max 未在册） | 193 | **193** | 一致，铁律#1"禁止跳号"实测破口 47% |
| 越法 `ruling_id` 形态 | 未测 | **0**（11 条子裁定全为单字母后缀，合规） | 骨架 R-16-04 的"多字母后缀"只在**引用侧**（`tests/strategy_pipeline/test_pipeline_events.py`），登记侧干净 |
| `status` 值集 | "声明 4 值 / 实测 6 值，含 deprecated 0 条" | **声明 4 值 / 实测 5 值** `{active 215, decided 8, superseded 3, void 2, draft 1}`；`deprecated` 声明但 **0 使用** | ⚠ 口径修正——"6"是"声明∪实测"并集，不是实测值数；且 decided 已由 7 涨到 **8**（411 又用了它） |
| `category` 值集 | "50 个自由值" | **50 值 vs 声明 4 值**（`架构/治本/命名/流程`），命中声明集的只有 架构 36 + 治本 35 = 71/229=**31.0%** | ⚠ 骨架漏报严重度——真正的大头在这（status 偏差涉及 10 条，category 偏差涉及 158 条） |
| `entry_schema` 声明键 | 10 | **10** | 一致 |
| 实测出现键 | 15 | **15** | 一致 |
| 未声明键使用量 | evidence 41 / related_files 5 / renumber_note 3 / evolution_note 1 / related_branch_refs 1 | **evidence 41 / related_files 6 / renumber_note 3 / evolution_note 1 / related_branch_refs 1** | ⚠ `related_files` 5→**6**（411 也用了它） |
| 声明而无人填的键 | 无 | **无**（10 个声明键使用量均 ≥1） | 一致；但"有人填"≠"人人填"，见下两行新指标 |
| **声明键缺失面**（新） | 未测 | `affected_files` 缺 **25** 条 / `related_arch` 缺 **14** 条 / `superseded_by` 缺 **5** 条 / `related_rulings` 缺 **1** 条 | 新案——册内条目字段集不齐，生成器按 schema 取值会 KeyError |
| **类型漂移**（新） | 未测 | `date` 有 **3** 条是 YAML date 对象（schema 声明 str）；`affected_files` 有 **3** 条是 str（声明 list）；`evidence` **41** 条全 str（若入 schema 须定标 list 还是 str） | 新案——`related_files` 6 条全 list，与 `affected_files` 同形，是重复语义 |
| `related_rulings` | 146/228=64.0%，306 边，悬空 4 | **147/229=64.2%，309 边，悬空 4** | 一致；4 条悬空全因把散文塞进列表值（#275/#276×2/#302），**非**指针失效 |
| `related_arch` | 52/228=22.8%，**悬空 0** | 52/229=**22.7%**，103 条边；**权威 checker 实报悬空 3 条** | ⚠ **骨架此数为错**——见 §2 批次 P3（这不是"最强机读边"，是当前在红的边） |
| `superseded_by` | 4/228=1.8%，2/4 误指 `#ARCH` | **4/229=1.7%**，误指仍为 2/4（#165、#201） | 一致 |
| `affected_files` | 175/228=76.8%，1270 边，缺 62.8%（798） | 175/229=**76.4%**，1270 边，缺 **798=62.8%**（逐字复现）；改按主区 `D:\ZephyrAlpha` 解析仍缺 **783=61.7%** | 一致，且**换基准也救不回来**⇒ 不是 worktree 假象，是真失效。形态分型：仓内相对 1026 / 盘符绝对 189 / 根绝对 55 |
| 铁律#8 时间序逆数 | 6 处 | **6 处**（#19/#165/#218/#304/#385/#386） | 一致 |
| 册内 `commit <hash>` 提及 | 14 处 | **14 处**（全文正则复现） | 一致 |
| ROOR 在册项数 | 77（字段写 76） | **77** 实条目 / `summary.total_registries: 76` | 一致——ROOR 自己的计数字段已漂 1 |
| 裁定册挂 ROOR | 0 命中 ⇒ 不存在于系统 | 0 直接命中，**但经 REG-CATALOG-001 两跳可达**（`registry_master_index.yaml` L394 有 REG-RULING-001） | ⚠ 理由改写，补条结论不变（见 §4-A1） |
| 主索引对裁定册记的 `entry_count` | 未测 | **196（真值 229，陈旧 33）** | 新案——机生索引自己就过期了 |

## §2 回写清单批次表（交总包，逐批可独立提交）

> 纪律：每批都是热册 `ruling_registry.yaml` 的**外科改**，必经 `safe_write_text`（CAS）+ 与引用方同 commit（册顶铁律#6）；**禁重排历史 entries**（铁律#8）。

### P1 词表层（改注释 + 出词表件，0 新裁定）

| # | 动作 | 坐标 | 内容 |
|---|---|---|---|
| P1-1 | `status` 值域从 4 扩到 6 并**逐值定义** | `ruling_registry.yaml:28`（铁律#4 注释）+ `:49`（entry_schema 的 status 行注释） | 六值 = `draft / decided / active / superseded / deprecated / void`，语义建议——`draft` 草案未生效；`decided` Owner 已拍但未完成执行面（当前 8 条全在 2026-09-23 之后，含战役母法 409/410/411）；`active` 生效中；`superseded` 被新裁定取代（须配 `superseded_by`）；`deprecated` 废弃无后继（**存量 0，保留为闭合枚举用**）；`void` tombstone 非裁定（2 条） |
| P1-2 | 新建受控词表件（**不新建校验器**） | 新增 `docs/01_policies_and_standards/_registry/vocabularies/ruling_status_vocabulary.yaml` | 照 `contract_status_vocabulary.yaml` 现形态（`schema_version/doc_type: vocabulary/module_id/title/vocabulary_name/total_values/depends_on/values[]（value+definition+ai_consumption+ai_keywords+lifecycle_constraint+next_states）/deprecated_values[]`）；`values[].next_states` 直接给出状态机：`draft→decided→active→superseded|deprecated`，`void` 为旁路终态。**理由**——同类先例已有 4 个分域 status 词表（contract/module_lifecycle/review/blueprint_refs），裁定域单独立件=补齐家族，非新增重复簇 |
| P1-3 | `category` 值域二选一处置 | `ruling_registry.yaml:48`（schema 注释声明 4 值）+ 实测 50 值 | **建议不立刻出词表**（见 §4-A2）。最低成本口径=把 schema 注释的枚举改成"`category` 为自由标签，非受控枚举（实测 50 值），受控收敛另案"——**先让声明不再说谎，再谈收敛** |
| P1-4 | 母法回写（骨架 R-16-03） | 册顶铁律条数 10 vs `裁定#20-D` title 自述"8 条规则" | 走**演进注记**（铁律#8 禁重排）：在 `#20-D` 条目补 `evolution_note`（该键实测已被 `#178` 用过一次，形态可照抄），声明"第 9/10 条由后补裁定并入，母法 title 的'8 条'为历史口径"。**不得**直接改 title 里的数字 |

### P2 `entry_schema` 层（纯声明补齐，不动任何条目）

| # | 动作 | 内容（建议直接粘进 `entry_schema:` 块） |
|---|---|---|
| P2-1 | 补 5 个未声明键 | `evidence: str`（41 条实测全 str；**定标为 str 不定标 list**，与实用形态一致）、`related_files: list`（6 条，全 list）、`renumber_note: str`（3 条，撞号改号留痕）、`evolution_note: str`（1 条）、`related_branch_refs: list`（1 条） |
| P2-2 | 把"可选"标注出来 | `affected_files`（缺 25）/`related_arch`（缺 14）/`superseded_by`（缺 5）/`related_rulings`（缺 1）标注 `(可选)`，并在注释里写"缺失=该面未主张"，避免下游按必填取值崩 KeyError |
| P2-3 | `related_files` 与 `affected_files` 关系定标 | 实测 6 条 `related_files` 全 list、与 `affected_files` 同形同义（例：`裁定#407/#405/#406/#409/#410/#411`）。**建议标 `related_files: list  # (deprecated 别名，等价 affected_files，禁新增)`**——内收判据"同真源可派生→必并"，但存量 6 条不动（铁律#8） |
| P2-4 | `date` 类型定标 | 声明 `str`，实测 3 条为 YAML date 对象 ⇒ 生成器侧须显式 `str(x['date'])`（本车道 `--verify` 即如此处理）；或把 3 条改回带引号形态。**建议前者**（改条目=动历史） |
| P2-5 | 消费端义务 | 回写后重跑 `scripts/governance/d3_metadata/generate_rule_catalog.py`（其 L101/226 已扫 `superseded_by`），使 `rule_catalog_registry.yaml:3477` 的 REG-RULING-001 版本行同步 |

### P3 引用面清账（复算新发现，**当前是活的红灯**）

| # | 问题 | 实测 | 处置 |
|---|---|---|---|
| P3-1 | `related_arch` 装进了非议题 id | `check_governance_bidirectional()` 现返回 **3 条 error**——`#383 → #MOD-L00-004`、`#387 → #PS-CTR-003`、`#387 → #MOD-INF-043` | 三条改指：模块类应进 `related_files`/`affected_files` 面，或另立 `related_modules` 键（与 P2-1 一并定标）。**这条比骨架"悬空 0"的判断更紧急**——它是 `align_all.py:516` 恒跑面上的硬 error，骨架把它当"立法流最强机读边"记载会误导后续车道 |
| P3-2 | `related_rulings` 装进散文 | 4 条（`#275`、`#276`×2、`#302`） | 值内嵌散文（"外审遗留㉑…"、"裁定#NNN（…）"）——把说明搬进 `summary`，列表只留 id；`#302` 的 `裁定#257⑤` 改成合法 id |
| P3-3 | `superseded_by` 类型误用 | 2/4 指向 `#ARCH-*` 议题（`#165`、`#201`） | 铁律#9 明文要求"新裁定 ID"。要么改指真裁定，要么把这 2 条挪进 `related_arch`——**本车道不裁**，属 Owner 门位（骨架 X-4 已提） |
| P3-4 | 主索引计数陈旧 | `registry_master_index.yaml` 对 REG-RULING-001 记 `entry_count: 196`（真 229），生成于 2026-09-20 | 重跑生成器即可，**禁手改**（见 §4-A2） |

## §3 ROOR 补条（第三项）——内容与锚点

**结论：补 1 条（不是骨架说的"1 行"那么小），且必须与 `ENTRY_SPECS` 同批，否则补条本身会把 CR-007 判红。**

真实理由（替换骨架 R-16-05 的"不存在于系统"）——`check_registry_consistency.py` 的 CR-007 只对**ROOR 在册**的 `registry_id` 做 `entry_count` 实测对账（其 `ENTRY_SPECS`/`ENTRY_MANUAL` 两张表的键都是 ROOR 里的 id；文件 L285-288 注释逐字："新增登记表时必须同步补 ENTRY_SPECS（可自动数）或 ENTRY_MANUAL（不可自动数+原因），否则 CR-007 报 UNSPECIFIED 阻断"）。裁定册不在 ROOR ⇒ 不在对账域 ⇒ 它自己的 `entry_count` 永远没人核——实测已印证：机生主索引记 196 而真值 229，**零报警**。

### 3.1 插入内容（tier: 1 的 `registries:` 数组末尾）

锚点：`docs/registry_of_registries.yaml`，`tiers:` 第 2 项（`- tier: 1` L145）→ `registries:`（L148）；建议插在 tier 1 末尾（tier 2 起始之前），与邻近条目的键序保持一致（实测该 tier 每条键序为 `registry_id / name / physical_path / format / maintenance / entry_count / counting_rule / status / description`）。

```yaml
      - registry_id: REG-RULING-001
        name: 裁定中央登记表
        physical_path: docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
        format: yaml
        maintenance: manual
        entry_count: 229
        counting_rule: entries 数组条目数
        status: active
        description: 架构裁定 裁定#NNN 唯一真源（SSoT）——tier_1 治理册，宪法 RULE-RULING 与 RULING-REFERENCE 门禁的共同数据源；取号经 scripts/governance/next_ruling_id.py
```

> ⚠ **裸引用格式陷阱**——上面 `description` 里刻意写"架构裁定 裁定#NNN"（占位形态）而不写具体未登记号；本件与案卷若出现"裁定# + 未在册数字"会自触 REFERENCE-INTEGRITY 簇（本役已有死信先例）。总包落盘前用 `python scripts/governance/check_commit_message.py` 之外再跑一次引用自扫。

### 3.2 同批必改的两处（否则补条即引雷）

| # | 文件:锚点 | 改动 |
|---|---|---|
| 3.2-1 | `scripts/governance/d3_metadata/check_registry_consistency.py`，`ENTRY_SPECS` 字典（L297 起） | 加一行 `"REG-RULING-001": ("yaml_list", "entries", "entries 数组条目数"),`。缺此行 ⇒ CR-007 直接判 UNSPECIFIED FAIL（补条反而把 CI 弄红） |
| 3.2-2 | `docs/registry_of_registries.yaml:881` | `summary.total_registries: 76` → 78（补 1 条后）。**该字段实测已漂**（当前真实条目 77 而字段写 76），补条时一并纠 |

### 3.3 顺带账（同一批可清，也可另案）

实测 43 个带 `registry_id` 的册中 **14 个不在 ROOR**，其中 **11 个经 `REG-CATALOG-001 → registry_master_index.yaml` 两跳可达**（含裁定册），**3 个真不可达**：

| registry_id | 物理路径 | 判定 |
|---|---|---|
| REG-CHAIN-001 | `_registry/catalogs/chain_registry.yaml` | **索引器缺陷非登记缺陷**——该册 `registry_id: REG-CHAIN-001` 写在正文 L13，而生成器 `extract_registry_info()` 只读**注释头/代码头**（L112-130 的 comment_meta 通道），YAML 正文里的 registry_id 它不看。修向=补该册注释头 或 让生成器回读正文，**不是**手改主索引 |
| REG-TAGVOCAB-001 | `_registry/catalogs/library_tag_vocabulary.yaml` | 同上（created 2026-09-22，晚于主索引生成日 09-20，双因） |
| REG-CAND-HARVEST-ARCHIVE-001 | `_registry/catalogs/_archive/candidate_module_registry_harvest_archive.yaml` | **不该挂**——归档位，`catalogs/_archive/**` 本不在发现域内（`registry_master_index_exemptions.yaml` 即为此类而设） |

⇒ 这三条**不建议**在本役补 ROOR 条目（净零：先修索引器的正文 registry_id 盲区，一次改动覆盖一整类，好过三条手工登记）。

## §4 判"不该做"的项与理由（直说）

| # | 项 | 判 | 理由 |
|---|---|---|---|
| A1 | 以"不挂 ROOR=不存在于系统"为由补条 | **换理由后照做** | 实测 11/14 个 ROOR 未列册经主索引两跳可达，"不存在"说重了；但**CR-007 对账域**这条理由是硬的（§3），所以补，只是别拿发现入口当卖点 |
| A2 | 手改 `registry_master_index.yaml` 的 196→229 等数字 | **不做** | 该机生册手写 `禁止手编`，根宪法 §9 条目 5"静态清单禁手工维护"。唯一正解=重跑 `generate_registry_master_index.py`；且它连 `REG-CHAIN-001` 都还没收（索引器正文盲区），改数字治不了病 |
| A3 | 为 `category` 立刻立受控词表 | **暂缓** | 实测 50 值、命中现声明的仅 31.0%。收敛 50→N 是**语义合并作业**（需逐条判"治理/治理运维/治理架构"是否同物），不是一次回写；硬出词表=造一张第一天就与 229 条存量冲突的册，还会新增一个 CR-007 对账义务。先做 P1-3 的"承认自由标签"，把收敛列为季度合并审计（宪法 §4.2 同域重复簇）独立工单 |
| A4 | 批量修 `affected_files` 的 798 条失效路径 | **不做** | 复算换到主区基准仍缺 783 条（61.7%），说明多数指向**已删/已改名的历史实体**——修它们=伪造"当年就改了这些文件"的现场。铁律无此义务，且骨架 §6.2 R-6 把 <10% 设为重开触发，是**未来量**不是本轮工。建议只做增量纪律：取号器凭据 + 登记时现算路径存在性（新裁定 `affected_files` 必填且必须实存），存量原样留痕 |
| A5 | 给取号器配套新立一台 gate | **不做** | 骨架 §3.2 的净零账就是"+1 脚本、0 gate、0 新册、0 新图"才成立；宪法 §4.1 要求新增 gate 声明替代了什么——本件无可替代对象（引用存在性/原子性已由 RULING-REFERENCE 子台看管）。取号是**人触发的一次性动作**，工具化即达目的；扩 gate 只会把"未取号"变成新红灯面。若日后要执法，正确形态是给 `check_registry_consistency.py` 加一条"在册号段 vs 占号凭据目录"对账（复用既有件），不是新 gate |
| A6 | 为凑骨架 §6.2 R-3 的 30% 阈值回填 `superseded_by` | **禁做** | 那是重开触发**观测量**，回填=自己造触发条件。当前 1.7% 且 2/4 类型错（P3-3），先纠类型再谈率 |
| A7 | 本车道自称"Owner 要求建取号器" | **无此依据，不写** | 取号器的立项依据=骨架 E3 实测痛点（6 起撞号 + 一条真实死信）与 §3.2 净零账，属车道内技术判断；Owner 门位仅经裁定登记或正式通道生效。本件未新增任何裁定 |

## §5 复算命令（全部只读，worktree 根执行）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
export PYTHONPATH="$PWD/src"
R=docs/01_policies_and_standards/_registry/catalogs

# D1 规模/号段/越法形态（本件 229 · 411 · 218 · 193 · 越法 0）
python -c "
import yaml,re
d=yaml.safe_load(open('$R/ruling_registry.yaml',encoding='utf-8'));e=d['entries']
ids=[x['ruling_id'] for x in e]; p=re.compile(r'^裁定#(\d+)(-[A-Z])?\$')
n={int(p.match(i).group(1)) for i in ids if p.match(i)}
print(len(e),max(n),len(n),len([k for k in range(1,max(n)+1) if k not in n]),[i for i in ids if not p.match(i)])"

# D2 schema 与词表（声明 10/实测 15/未声明用量/缺失面/类型漂移/五值 status/50 值 category）
python -c "
import yaml,collections
d=yaml.safe_load(open('$R/ruling_registry.yaml',encoding='utf-8'));e=d['entries'];s=d['entry_schema']
act=collections.Counter(k for x in e for k in x)
print('declared',len(s),'observed',len(act));print('undeclared',{k:act[k] for k in set(act)-set(s)})
print('absent',{k:sum(1 for x in e if k not in x) for k in s})
print('types',{k:dict(collections.Counter(type(x[k]).__name__ for x in e if k in x)) for k in s})
print('status',dict(collections.Counter(str(x.get('status')) for x in e)))
print('category distinct',len({str(x.get('category')) for x in e}))"

# D3 四类边质量（引用网 309 边悬空 4 / 议题边 / 取代链 4 条含 2 误指 / 路径 62.8% 失效 + 形态分型）
python .runtime/tmp/recount_fig16.py            # 本车道复算件（tmp，TTL 可回收）

# D4 权威 checker 亲跑（本件最硬的一处——它报 3 条 error，骨架记 0）
python -c "
from zephyr.gov_enforcement.registry_alignment import check_governance_bidirectional as f
e,w=f(); print(len(e)); [print(x) for x in e]"

# D5 ROOR 与两跳发现链（77 实条目 vs 字段 76；主索引记裁定册 196）
python .runtime/tmp/roor_gap_scan.py
grep -n "REG-RULING-001" -A 8 $R/registry_master_index.yaml | head -12
grep -n "generated_at" $R/registry_master_index.yaml           # 09-20，晚于它的两个册未被收录
grep -n "total_registries" docs/registry_of_registries.yaml    # 881 行 = 76

# D6 CR-007 对账域（证 §3 的真实理由——不在 ROOR 即不在对账域）
python scripts/governance/d3_metadata/check_registry_consistency.py 2>&1 | tail -8
grep -n "REG-RULING" scripts/governance/d3_metadata/check_registry_consistency.py   # 空 = 不在 ENTRY_SPECS

# D7 撞号史与在途号主张（取号器三源并集的现场依据）
python scripts/governance/next_ruling_id.py --verify --queue-root "D:/ZephyrAlpha/.runtime/commit_queue"
```

> D5/D6/D7 里出现的 `REG-RULING-001` 在册（`ruling_registry.yaml` 自身的 `registry_id`），非新造锚点。
> `--verify` 只读：扫主区队列仅用 `json.loads` 解析，禁跑 `commit_queue.py status/drain`（会触发自举排空）。

## §6 交总包的执行序

| 序 | 动作 | 面 | 批次关系 |
|---|---|---|---|
| 1 | P2 `entry_schema` 补 5 键 + 可选标注 | 热册注释区 | 与 P1-1 同批（同文件，一次 CAS） |
| 2 | P1-1 铁律#4 四值→六值 + P1-2 新词表件 | 热册 + vocabularies/ | 新册件须同批声明净零——**它替代的旧条目**=热册 L28 的散文枚举（声明从"册内注释"上移到"受控词表"，注释改为指针，不双写） |
| 3 | P3-1/P3-2 引用面纠值 | 热册 | 单独一批（改的是条目内容，跑 `check_governance_bidirectional` 从 3 红→0 才算完） |
| 4 | §3 补条 + 3.2-1 ENTRY_SPECS + 3.2-2 计数字段 | ROOR + check_registry_consistency.py + 热册无关 | **三条必须同批**（拆开必红） |
| 5 | P1-3 承认 category 自由标签 + P1-4 母法演进注记 | 热册 | 收尾批，A3 的收敛工单另立 |
| 6 | `lane_construction_discipline_policy.md` §5（L192-196）加一行指向取号器 | 政策册 | 骨架 O6 已判定义务——"取号先实测 max+1"四行散文的代码化落点；**不同批改=纪律与工具二次分叉** |

**§6-6 的口径建议措辞**（供总包直接粘贴，避开引用陷阱）：并发取号一律 `python scripts/governance/next_ruling_id.py --reserve`（在册面 + 队列在途面 + 占号凭据面三源并集 max+1，O_EXCL 独占），禁手工读数占号；在途面除提交信息声明外**还含队列袋里的整册快照**——死信袋的号主张仍然有效（本役死信实测）。

## §7 未复算/🌑 项（如实报）

| # | 项 | 状态 |
|---|---|---|
| L-1 | 骨架 §1 门④ 的 22.8% 我复算为 22.7%、76.8%→76.4%、1.8%→1.7%、64.0%→64.2% | **纯分母漂移**（228→229），骨架在当时是对的 |
| L-2 | `category` 50 值的语义等价簇未做合并判定 | 本件只出"自由标签承认"，收敛是 §4-A3 的另案；**没做**不代表不需要 |
| L-3 | 3 条 `related_arch` 悬空应改指到哪个真源 | 需读 `#383/#387` 三条裁定正文才能判"议题/模块/PS 契约"三选一——本车道不代裁（P3-1 只点名） |
| L-4 | `related_files` 与 `affected_files` 的语义差 | 从 6 条样本看是**同义重复**，但样本太小且跨 405/406/407/409/410/411 一批会话，可能是某批的有意区分——P2-3 按"疑似别名"提，措辞留给总包定 |
| L-5 | 队列在途面的完整覆盖面 | 本车道取号器实测扫 469 袋（pending/processing/dead），`blobs/` 20191 个内容寻址文件**未逐个解析**（只解析袋 files[] 指向册的那 13 个）。若要"blob 全域并集"口径（`docs/_working/e2e_integration/w0_ruling_404_collision_fix.md` 的三源并集原文），需另加一轮扫描——当前实现是有意的窄口径 |
| L-6 | worktree 无 `.runtime/commit_queue` | 取号器在 worktree 内跑在途感知=0 并显式 warn（单测 `test_missing_queue_dir_degrades_with_disclosure` 锁此行为）；生产取号必须在主区根跑，本车道未替主区做任何写 |
