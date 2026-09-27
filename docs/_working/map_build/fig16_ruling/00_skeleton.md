---
ttl: task_bound
completes_when: 图16 立项三选一裁定（建图/扩层/不建）由 Owner 认可，且本件 §6 重开触发条件与 §7 封顶声明被总包并入收官台账后，本件退役为归档参考
title: 图16 治理立法流图·环节总骨架（00_skeleton，本图唯一收敛基准；结论=不建）
owner: st-mapbuild-20260924
---

# 图16 治理立法流图 00_skeleton

> 一句话域：**一条架构裁定从"待裁面收拢"到"入册生效并被引用"的时间序**（呈报→取号→登记→同 commit 原子落地→执行→取代链→对账）。
> 状态纪律=`sop/mining_sop/skeleton_mining_policy.md` §5：**✅ 必附实查路径/命令/行号**，凭印象标 ✅=审计事故。
> 本件所有行号/数字均为 2026-09-24 在 worktree `D:\ZephyrAlpha\.aidrafts\st-mapbuild-20260924` 上实测（§8 全命令可复跑）；标注「主区」的少数路径只在 `D:\ZephyrAlpha` 存在（worktree 不共享 `.runtime`），已单独注明。
> 环节编号 `D16-*` 一经定稿即为契约；即便结论为不建，编号仍作为引用锚（本图若重开，编号不得改义）。
> 裁定引用纪律：本件只写**已实测在册**的裁定号；未登记的字面号一律去前缀书写（避免自触 REFERENCE-INTEGRITY 簇的 RULING-REFERENCE 子台）。

## §0 结论先行

**结论=③不建（真源已在册，流程语义以政策+gate 承载）**。三条最硬证据：

| # | 证据 | 坐标 |
|---|---|---|
| E1 | **门④字面过，但被宪章 §8.2.4「机生优先律」反噬——"有可执行真源"在这里是约束而非资格**。ruling_registry 实测 228 条 entries 确属可执行真相源 ⇒ 依 §8.2.4「有可执行真相源的流程图必须生成器产出」，图16 只能机生；而该真源**不含流程位置维度**：`stage/phase/环节` 类字段 **0 命中**，可机械生成的只有"引用图"（`related_rulings` 填充 64.0%、`related_arch` 22.8%），流程链的三个关键面全是残件——`superseded_by` 填充 **1.8%（4/228，其中 2 条还误指 #ARCH 议题）**、`affected_files` 1270 条边中 **62.8%（798）路径在本仓不存在**、`status` 声明四值实测出现六值（新增 decided/void 共 9 条，`deprecated` 存量 0）。⇒ **机生=只能生成引用网（画不出 14 格流程）；手画 14 格=违 §8.2.4 与根宪法 §9 条目 5**。两难无解，此即决定性证据 | `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:42-56`（unique_key/entry_schema）+ §8-C2/C3 实测；宪章 `system_charter.md:228`（§8.2.2 四道门，④原文="有机生真源**或**可建结构校验器"，是选言式）/`:230`（§8.2.4 机生优先）/`:229`（§8.2.3 净零对价义务） |
| E2 | **门③的另一面：GOMAP 扩层结构性不通（不是"没做"，是"做了也买不到"）**。GOMAP 只有 12 个顶层键、层位字段仅 `id/name_zh/desc_zh/mounts/disconnected/config_refs`——**全图无 edges/sequence/next 任何流程边字段**；`mounts` 由 `_gomap_resolve_spec()` 强制解析为 `.py` 磁盘路径，非模块资产（裁定册/裁定书/待裁清单）**根本挂不上**；立法流 8 个 actor 模块逐个喂进生成器的 `classify_family()` 实测 **8/8 返回 None**（即机生 families 层永远不会出现它们）。实测 GOMAP 对立法流的**节点覆盖率=0/8（0%）**，全 2706 行里"裁定"二字只出现在 2 条 `note_zh` 变更说明中（L98/L104），不是节点 | `config/governance_operations_map.yaml:1-26`；`scripts/governance/d5_architecture/generators/align_all.py:143-217`；§8-C5 |
| E3 | **真痛点是"取号无工具"，不是"流程看不清"**。撞号实证 **6 起**：`#264/#265→#266`（册内 L2254 注记+取证报告）、`#290-294 被并发窗口整体覆盖后重取 #296-301`（L3602）、`#304→#331`（L3766）、`#305→#332`（L3782）、`#293→#386`（L4256）、**`#404` 双挂**（同日夜两会话取号窗口重叠，L5531-5540，`#408 status: void` 专设 tombstone）。最后一起的后果可机读：携带裁定册的队列批 **结构性必死**——主区死信 `.runtime/commit_queue/dead/q-20260923-st-ibt-remedy-cf-20260923-0023.json` 的 `dead_reason` 原文："`[landing] 注册表三向合并失败…ruling_registry.yaml: ours 同侧身份键重复: ruling_id=裁定#404——身份不唯一，死信回人工`"。而全仓**零取号工具**（`find scripts src -iname "*ruling*"` 只命中两个 gate + 一个归档迁移件；`grep next_ruling|max_ruling` 零命中），现行取号纪律只是 4 行散文（该节 L193-196） | `docs/_working/e2e_integration/w0_ruling_404_collision_fix.md`（全文，含取号三源并集口径与复核命令）；`docs/01_policies_and_standards/sop/construction_sop/lane_construction_discipline_policy.md:192-196`；§8-C6 |

**判定链（避免误读，先把话说准）**：宪章 §8.2.2 四道门**字面全过**——门①（独立触发+终点）过、门②（跨模块交接）过、门③（不被现有图覆盖）过（GOMAP 实测 0%，无第二张图声明此域）、门④按其**选言式原文**（"有机生真源**或**可建结构校验器"）也过：ruling_registry + 门禁链确属可执行真相源。**但四道门是必要条件、不是建图许可证**：宪章 §8.2.4 与 §8.2.3 是叠加义务——①因"有可执行真源"，图16 就被**强制**要求机生（E1 的两难）；②因"新图须声明替代/合并了什么"，图16 给不出净零对价（能机生的 3 个环节已由 RULING-REFERENCE + `check_governance_bidirectional` 看着，其余额外 8 个环节**无源可生**，把它们画进图=复制 permanent 政策册=造第二真源）。⇒ 判**不建**。
普查 §4 L60 的先验理由（"流程仅约 7 步、收益中等"）**实测被推翻**：真实环节 **14 个**（§2）。环节数上升不改变结论，但**理由必须换成 E1/E2/E3**——用"步骤少"当理由是站不住的。

## §1 四道门逐条实证

### 门① 独立触发与终点 —— 过

| 项 | 实证 |
|---|---|
| 触发（人路） | Owner 拍板带宽消耗：`docs/01_policies_and_standards/sop/governance_sop/deep_adjudication_method_policy.md:169-176`（§2.5 消费纪律："不许直接替 Owner 拍——A/C/E 类与全部 V 类产出一页式裁定书草案，一份一条"）；门位注册表 `risk_tier_registry.yaml:85-87` `domain: D_GOVERNANCE tier: high human_gate: *high_human_gate` |
| 触发（AI 路） | 代裁/自裁两条子路径实存且有留痕：①**代裁**——`ruling_registry.yaml` 条目 `#404` title="TC-06 四卡代裁定版（Max 代裁 Owner 全批，随批登记）"；②**自裁**——`#305` title="日度编排器 BT-P1-031 八条批准点保守默认自裁"，先例案卷 `docs/_working/2026-09-18_vocab_consolidation_campaign/w2_ruling/w2_self_ruling_335.md` |
| 终点 | 双重终点，均已机读：①**入册**=entries 出现该 `ruling_id`（`unique_key: [ruling_id]`，L42）；②**同 commit 原子落地**=RULING-REFERENCE 子台 L2 `RULING_ATOMICITY_VIOLATION` 硬阻断（`src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py:9` 头 INVARIANTS："**阶段2 hard block 已启用**（`_MANUAL_STAGE=False`）——新增未登记引用直接阻断"） |
| 有独立状态机？ | **有语义、无面**：状态字段存在（`status`），但实测词表分叉——册顶 L28 声明"四值 active/superseded/deprecated/draft"，条目实测六值 `{active 215, decided 7, superseded 3, void 2, draft 1, deprecated 0}`；`decided` 与 `active` 的语义差（已拍未生效？还是新词表？）全仓无定义件。⇒ 状态机**不可机判**（详见 §2 D16-09） |
| 终点是否与图11 共享 | **是**——"同 commit 原子"的执行体就是提交链（图11 D11-C05 门禁链 / D11-C10 真落盘）。这是本图与图11 的天然交接位，不是缺陷，但意味着本图终点段只能做引用节点（§4 O2） |

### 门② 跨模块交接 —— 过

| 交接边 | 上游→下游 | 证据（文件:行） |
|---|---|---|
| J1 | 政策→册：裁定登记语义的**唯一**真源指向 | `deep_adjudication_method_policy.md:20`（净零声明逐字："裁定登记语义仍归 RULE-RULING + `ruling_registry.yaml`，人机门位仍归宪法 §5"）；`deep_adjudication_method_policy.md:181`（§3："本册'草案→Owner 签'流程不得绕过它们"） |
| J2 | 裁定册→议题册（双向闭合，**有硬校验**） | `src/zephyr/gov_enforcement/registry_alignment.py:449-490`：`_ruling_arch_errors`（ruling.related_arch→issue 存在性）+ `_issue_ruling_errors`（issue.adjudication 内"裁定#N"→ruling 存在性）；调用面 `align_all.py:107,516`；实测悬空 **0 条**（52 条 related_arch 全部命中）——立法流最强的一条机读边 |
| J3 | 裁定册→门禁册：引用完整性 | `ruling_reference_gate.py`（RULING-REFERENCE，priority=74，`gate_registry.yaml:1680-1690`）；**拓扑已变**：st-gslim P4 七簇合并后它不再是独立注册项，而是聚合台 `REFERENCE-INTEGRITY`（`in_process_gate_registry.yaml:122-127`，`module_path: …dangling_reference_gate`，`files_trigger: ["docs/"]`）的第 4 个子台（`dangling_reference_gate.py:232` 子台清单逐字列 RULING-REFERENCE）——本图施工期若要挂 gate，必须先知道这件事 |
| J4 | 裁定册→执行器：落地合并 | `scripts/governance/commit_queue_landing.py:313`（合并器复合身份键）+`:450-457`（"身份判不了/同侧键重复→死信方向错误串"）+`:348`（"其余族（unique_key 元数据…）→默认复合键"）；**身份键就是册内 `unique_key: ruling_id`**——这是"登记"环节真正的机器契约（也是 E3 死信的判据来源） |
| J5 | 裁定册→规则目录（机生入册） | `rule_catalog_registry.yaml:3477-3482`（`path: …ruling_registry.yaml` / `module_id: REG-RULING-001` / `version: 1.1.1`）；生成器=`scripts/governance/d3_metadata/generate_rule_catalog.py:101,226`（把 `superseded_by` 纳入扫描字段） |
| J6 | 裁定册→尺子册（作为**证据源**被消费） | `scripts/governance/standards_governance/generate_standard_family_registry.py:29`（"历史被毙/重考证据=`ruling_registry.yaml` 对本册 STD-* 的提及计数"）、`:71-73`（RULINGS_SOURCE 常量）、`:79-80`（`REJECTED_PATTERNS`：否决/打回/驳回/毙/reexam/重考/作废） |
| J7 | 裁定册→前端面板 | `src/zephyr/frontend/dashboard/api_server.py:4326`（注释级引用："裁定登记（ruling_registry 同 commit 原子）由主会话收尾补登"）——**注意**：这是注释，不是数据接口；实测面板无"列出裁定"端点（api_server 内 `ruling_registry` 仅 1 处命中）⇒ 消费面比普查假设的薄 |
| J8 | 裁定册→ROOR（**断**） | `docs/registry_of_registries.yaml` 实测 `grep ruling_registry` **0 命中**、`grep -c registry_id:`=77 项中无 REG-RULING。宪法 §0.6/§1-RULE-REGISTRY 明文"查注册表先读 ROOR""每个注册表必须在此登记，否则不存在于系统"（ROOR 自述 L12-13）⇒ **tier_1 治理册未挂发现入口**，立法流最大的交接缺口（红条目 R-16-05） |

### 门③ 不被现有图覆盖 —— 过（但与"已有政策承载"不是一回事）

| 检查 | 实测 |
|---|---|
| GOMAP 是否已覆盖立法流？ | **0%**。①节点级：8 个 actor 模块 `classify_family()` 全 None（`#264` 等 gate/merger/aligner 一件都不在 families 427 模块内）；②层位级：GOM-L0..L6 七层语义=孵化/监控/水位/熔断/收割/自愈/审计，无一层含"立法/裁定/呈报/取代"语义（`config/governance_operations_map.yaml:28-136` 全量 name_zh/desc_zh 扫读+grep 复核）；③引用级：`out_of_scope_refs` 四项（L17-25）列了"提交门禁体系/数据治理/代码质量治理/交易决策治理"，**未列治理立法流**——既没覆盖也没声明排除，属图10 的盲区而非本图的豁免 |
| 规则 YAML 是否已有立法流程规则文件承载同一语义？ | **无**。`docs/01_policies_and_standards/rules/trae_*.yaml` 实测 86 本，`grep -l ruling_registry` **0 本**；55 本提到"裁定"二字但均为引用性提及（举轨某次裁定作依据），非"裁定该怎么产生"的流程规则。易混点已逐一排除：`trae_072_cross_commit_atomicity.yaml`（scope: cross_commit_atomicity，L34）管的是 **Phase N 提交夹带 Phase N+1 import**，与"引用与册同 commit"同词不同物；`trae_060_inward_consolidation.yaml` 管内收判据，不含取号/入册步骤 |
| 那"谁"承载了流程语义？ | **三份散文件 + 两台 gate**：①`ruling_registry.yaml:22-40`（册顶"裁定编号分配铁律"10 条，逐条覆盖 D16-05/06/09/10/11/12 五个环节的判据）；②`deep_adjudication_method_policy.md` §1-§2（呈报侧全链：收拢→核实→打包→成文→门位→入册，182 行）；③`lane_construction_discipline_policy.md:192-196`（并发下取号/登记四条纪律）；④RULING-REFERENCE（引用+原子）；⑤RULING-COMMIT-VERIFIED（priority=109，"已完成（commit hash）"真实性）。⇒ **散文层的覆盖度远高于图层的必要性**——这是"不建"的正面理由，不是"没挖到"的托辞 |
| 附带发现（该铁律本身自相矛盾） | 册顶注释块列 **10 条**铁律（L24→L39，含第 9 条 superseded_by 链、第 10 条跨表引用），而其中前 8 条的**来源裁定** `#20-D`（title L1315）自述 **"裁定编号分配铁律（8 条规则）"** 且 summary 只枚举到第 8 条 ⇒ 立法流自己的"母法"与其执行面已漂移 2 条，且**没有任何校验器能发现**（红条目 R-16-03） |

### 门④ 机生真源 —— **字面过（选言式第一支成立），但与 §8.2.4 机生优先律互斥 ⇒ 这才是决定性一票**

| 项 | 实测 | 判定 |
|---|---|---|
| 条目规模 | entries=**228**，`ruling_id` 全集唯一（重复 0），纯数字号段 max=**410**，数字干唯一值 217，1..410 空洞 **193**（铁律#1"连续分配禁止跳号"实测大面积不成立；铁律#7 的 `RULING_GAP_WARNING` 只 WARNING，`ruling_reference_gate.py:212/244`） | 规模够，但号段语义已不可反推 |
| 能当"流程节点"的字段 | **0**。无 stage/phase/segment/owner_step 类字段；最接近的 `category` 实测 **50 个自由值**（架构/治本/门禁/尺子/Owner 门位…），与 L28 声明的四值枚举完全脱钩，也无词表件（`_registry/vocabularies/` 下无 category 词表） | 不可建 |
| 能当"边"的字段（四候选实测） | ①`related_rulings`：**146/228=64.0%** 填充、306 条边、悬空 4（1.3%，且 4 条全因把散文塞进该字段：`#275` 值="外审遗留㉑…"、`#276` 两条值="裁定#NNN（…）"、`#302` 值="裁定#257⑤"）→ **可用但需清洗**，生成的是"裁定↔裁定引用网"，不是流程；②`related_arch`：**52/228=22.8%**、0 悬空（被 J2 硬校验兜住）→ 可用，同样是引用网；③`superseded_by`：**4/228=1.8%**，其中 `#165→#ARCH-016`、`#201→#ARCH-045` **指向议题而非裁定**（字段类型误用，铁律#9 明文要求"新裁定 ID"）→ 取代链**不可机生**；④`affected_files`：**175/228=76.8%**、1270 条路径边、**798 条（62.8%）在本仓不存在**（含 `d:\ZephyrAlpha\…` 绝对路径反斜杠形态与已删模块）→ 执行面**不可机生** | 边只有"引用网"，没有"流程链" |
| schema 一致性 | `entry_schema`（L45-56）声明 **10** 字段；实测条目出现 **15** 个键，未声明 5 个：`evidence`（41/228=18.0%）/`related_files`（5）/`renumber_note`（3）/`evolution_note`（1）/`related_branch_refs`（1）；声明字段全部有人填（无缺项）⇒ 漂移方向是"加字段没改 schema" | 生成器契约不稳 |
| 排列纪律 | 铁律#8"按裁定时间顺序追加"实测**不成立**：date 序列逆序 **6 处**（`#304` 前一条 2026-09-18→本条 09-17、`#386`、`#165`、`#19`、`#218`…）⇒ 若生成器依赖物理序推时序，必错 | 不可依赖 |
| 结论（三段论，勿跳步） | ①**门④本身过**：228 条结构化册 + 两台 gate + 一个双向对账 checker 确属宪章 §8.2.4 括号里点名的"注册表/门禁链"型**可执行真相源** ⇒ 选言式第一支成立；②**正因如此触发 §8.2.4 强制**："有可执行真相源的流程图 MUST 生成器产出（根宪法 §9 条目 5 对地图加倍适用）"；③**但该真源不含流程位置维度**（上表第 2 行=0 字段、第 3 行=边只有引用网）⇒ 合规的机生图只能画出"裁定↔裁定引用网"（而这张网已由 checker+gate 双重看着，无可视化必要），而 14 格流程图只能手画 ⇒ 违反②。**死结不在"有没有真源"，在"真源里没有图要表达的那个维度"** | **过 → 反成阻断**（不可用"先立校验器"绕开：图14 缺的是锚的实存性可补，本图缺的是维度本身，补=手工造新语义层=第二真源） |

> **与图14 的差别（为什么图14 判"先立校验器"、图16 判"不建"）**：图14 的 17 个 Step 段有 7 个统一粗体字段、100% 结构覆盖，缺的是"字段值指向的实体是否实存"→ 校验器可补。图16 的 228 条 entries **没有一个字段说"我处在流程第几步"**→ 补校验器等于手工造一层新语义，那正是手画图换了个载体，净零不成立。

## §2 流程环节全集（14 环节，D16-01 起；结论为不建仍全量挖，编号即引用契约）

**列口径**：
- **状态**：✅=该环节的机制/真源在本仓实存且在册可查（附坐标）；🔨=有真源但断链、无工具或语义分叉；⬜=只有散文声明，无任何机器面。
- **机读否**：yes=该环节的存在与状态可由脚本/门禁直接判定；partial=部分子项机读；no=结构性无机读面。
- 「段」=五段分层（§2.1）。

| 环节编号 | 环节名 | 段 | 状态 | 真源映射（文件:行 / 字段 / gate） | 机读否 |
|---|---|---|---|---|---|
| D16-01 | 待裁面收拢（全仓穷举扫描） | 呈报 | ✅ | `deep_adjudication_method_policy.md:139-147`（§2.1 分工+§2.2 五分区：策略回测/治理门禁/数据层/模块蓝图与减法/配置与管线；§2.3 十六标记词，主词命中面逐字：待裁 135 文件、需 Owner 170 文件、挂单 139 文件、HELD 95 文件）；先例规模 137 行→净 96 条/≈190 决策点 | no（清单落 `docs/_working/` 战役件，无常设登记面；本册 §2.3 还自证先例"只报'另 N 词'"留痕不全） |
| D16-02 | 逐行核实与入表闸（六步） | 呈报 | ✅ | 同册 `:150-158` §2.4 六步（命中逐行 Read／去重归并四元组／**裁定号核验**／锚点双程抽检／低置信单列／可信度声明随表发布）；第 3 步原文即立法流可核证据："在册 121 条、最大号 #303"（先例值），并记载该法捕获 V-01 悬空 / V-02 内容不符 | no（人工六步，零 checker；"裁定号核验"这一步有数据面但无脚本——与 §6 R-3 触发条件同因） |
| D16-03 | 打包裁定（按族 vs 按条） | 呈报 | ✅ | 同册 `:163` 逐字："Owner 拍板带宽按条消耗需 96 次，按族打包只需 ≈14 次批文"；八类分类 A-H 见 `:160-162`（A 资金 16｜B 尺子 19｜C 存亡 18｜D 门位 14｜E 晋升 9｜F 外推 12｜G 选型 5｜H 机制 3） | no |
| D16-04 | 门位判定（Owner 亲裁／代裁／自裁） | 呈报 | ✅ | 门位：`risk_tier_registry.yaml:30`（"升 high/medium 须 Owner 裁定登记（ruling_registry 关联）"）+`:85-87` D_GOVERNANCE=high；代裁实例=`ruling_registry.yaml` 条目 `#404` title；自裁实例=`#305` title + 案卷 `docs/_working/2026-09-18_vocab_consolidation_campaign/w2_ruling/w2_self_ruling_335.md`；三问边界=同政策 §1.4 | partial（"是否 Owner 亲裁"不可机判；"条目存在"可机判） |
| D16-05 | **取号** | 登记 | 🔨 | 铁律#1-#3（`ruling_registry.yaml:24-27`：连续分配／不回收／子裁定格式 `\d+(?:-[A-Z]+)?`）；执行纪律=`lane_construction_discipline_policy.md:194` 逐字："取号**先实测 max+1**（`git show dev:<ruling_registry>` 重算，不是读工作区）；并发风暴下会撞号吞条目"；实操口径唯一成文处=`docs/_working/e2e_integration/w0_ruling_404_collision_fix.md:28-36`（**三源并集**：HEAD 册+工作区册+全队列袋四态 blob 内 `裁定#(\d+)` 并集 max；先例值 HEAD max=406、去重 213 号位）；外科脚本 `.runtime/tmp/e2e_20260924/fix_ruling_404.py` 依 TTL 已消失（24h） | **no**——**全仓零取号工具**（`find scripts src -iname "*ruling*"` 只命中 `ruling_reference_gate.py`/`ruling_commit_verified_gate.py`/`_archive/migration/apply_rulings.py` 三件，无一是分配器；`grep -rn "next_ruling\|max_ruling" --include=*.py src scripts` 零命中）⇒ **本图唯一真正的无机验硬环节**，见 §6 R-1 |
| D16-06 | 登记入册（条目写入热文件） | 登记 | ✅ | 册体：`ruling_registry.yaml:57` 起 `entries:`，实测 228 条；`unique_key: [ruling_id]`（L42-43）、`entry_schema`（L45-56）；热文件写律=宪法 §13 `safe_write_text`（`src/zephyr/shared/io/file_utils.py`）；先例执行凭据=`w0_ruling_404_collision_fix.md:59` 逐字 `WRITTEN cas_ok=True base=d39cbb1149ef`，"外科脚本四道前置拒绝（双挂前提不成立／待迁锚点不唯一／目标号已被占／改后仍有重复），任一不满足即零写入"（`:46-47`） | partial（CAS 写+前置校验是**一次性外科脚本**，非可复用面；无 `add_ruling.py` 之类正门） |
| D16-07 | 同 commit 原子（引用↔册） | 登记 | ✅ | RULING-REFERENCE 子台：`ruling_reference_gate.py:9` 头 INVARIANTS（L1 存在性 + L2 `RULING_ATOMICITY_VIOLATION` 硬阻断，`_MANUAL_STAGE=False` 阶段2 已启用，出处 `#20-G`）；priority=74（`gate_registry.yaml:1680-1690`，`own_scope: false`）；**运行时拓扑**=并入聚合台 REFERENCE-INTEGRITY（`in_process_gate_registry.yaml:122-127` `files_trigger: ["docs/"]`；子台清单 `dangling_reference_gate.py:232`）；来源铁律=册顶 L31-32（铁律#6） | **yes** |
| D16-08 | 落地（队列三向合并+身份键判定） | 落地 | ✅ | `commit_queue_landing.py:313`（W2 热修复合并身份键）/`:348`（`unique_key` 元数据族→默认复合键）/`:450-457`（"同侧身份键重复…死信回人工"原文 return 串）；死信实证（主区）：`.runtime/commit_queue/dead/q-20260923-st-ibt-remedy-cf-20260923-0023.json` `dead_reason` 全句已录 §0-E3，同件前道死信 `-0013`；机制真源归图11 D11-C10（`fig11_delivery/00_skeleton.md:85`） | **yes** |
| D16-09 | 生效（状态推进 decided→active） | 生效 | ⬜ | 声明=`ruling_registry.yaml:28` 铁律#4"status 四值"；实测六值分布 `{active 215, decided 7, superseded 3, void 2, draft 1, deprecated 0}`；`decided` 全部集中在 `#403/#404/#405/#406/#407/#409/#410`（2026-09-23 起），`void` 集中在两条 tombstone（`#265`/`#408`）；`deprecated` **存量 0**；全仓无 status 词表件、无 checker、无 reconciler（`grep -rn "superseded_by" --include=*.py src scripts` 命中 5 件：`generate_rule_catalog.py:101,226`／`d3_metadata/__init__.py:40`／`detect_ruins_references.py:138`／`validate_module_lifecycle.py:114-160`／`validate_adr_frontmatter_consistency.py:147-152`——**全部作用于规则/模块/ADR 三类资产，无一作用于裁定册**） | no——**新词表于 2026-09-23 静默诞生，schema 未改**（R-16-01） |
| D16-10 | 取代链（superseded_by） | 生效 | 🔨 | 声明=册顶 L37-38 铁律#9（"旧裁定 status=superseded + 填 superseded_by=新裁定ID；新裁定 entries 中 reference 旧裁定"）；实测：**4/228=1.8%** 填充，`#199→#200`/`#265→#266` 合规，`#165→#ARCH-016`/`#201→#ARCH-045` **误指议题**；`status=superseded` 仅 3 条 ⇒ 铁律#9 的满足率≈1%，普查把它列为本图核心卖点之一（"取代链"），实查结果是该链**几乎不存在于数据中** | no |
| D16-11 | 引用面回写（改号后同步引用方） | 生效 | 🔨 | 留痕面=`renumber_note` 字段（**未声明于 entry_schema**）实测 3 条：`#331`/`#332`/`#386`（L3766/3782/4256，后者逐字"引用面以本注记为准"）；tombstone 面=`#408`（L5540 title："撞号处置留痕（tombstone，非裁定）"）+ 取证件 `w0_ruling_404_collision_fix.md:42-43`（"堵住'改号后有人以为 #404 空了再占一次'的复用缺口，样式先例=`#265`"）；**无扫描器**：改号后谁在引用旧号，须人肉 grep；误引用已造成下游事故（`docs/_working/archive/2026-09/kimi_audit/adjudications/p7a_ac_family_rulings.md:31` 红证："总包指令'`#304` 已裁砍'系旧口径…做T 砍真身=#331"） | no |
| D16-12 | 存量对账（议题↔裁定双向 + 空洞检测） | 对账 | ✅ | 双向：`registry_alignment.py:473-490` `check_governance_bidirectional`（docstring 逐字："commit 时 RULING-REFERENCE gate 管增量；此处管存量全量对账"）→ `align_all.py:516` 第五节；空洞：`ruling_reference_gate.py:212/244`（`RULING_GAP_WARNING` 不阻断）；实测引用网规模=全仓 `裁定#N` **3287 处 / 708 文件 / 233 个不同号**，悬空仅 5 个号（其中 4 个为占位形态字面 888/901/999/999-Z）⇒ 增量面治理**极有效**，这正是"不必建图来管它"的证据 | yes（双向存在性）／no（空洞不阻断，193 洞无处置） |
| D16-13 | 消费（尺子／家族册／目录／面板） | 消费 | ✅ | `generate_standard_family_registry.py:29,71-80`（把裁定册当"否决/重考"证据源机读）；`generate_rule_catalog.py:101,226` → `rule_catalog_registry.yaml:3477-3482`；`api_server.py:4326`（仅注释级，无端点）；另全仓引用面 D16-12 所列 708 文件 | partial（生成链机读；面板与"哪条裁定被谁消费"无面） |
| D16-14 | 季度合并审计／退役观察 | 对账 | ⬜ | 要求面=宪法 §4.1-4.2（全资产净零＋内收判据 w5_1：同真源可派生→必并／零触发零消费→退役／同域重复簇→收敛唯一）＋`trae_060_inward_consolidation.yaml`；**针对裁定册的审计面不存在**：无 script 扫"零消费裁定""重复裁定簇""可内收条目"；ROOR 未收录该册（J8）⇒ 季审连册都不在发现入口里 | no |

**计分板（本图唯一计分面）**：

| 维度 | 计数 | 明细 |
|---|---|---|
| 环节总数 | **14** | 普查 §4 L60 先验"仅约 7 步"实测低估（+7 来自呈报侧 4 步与生效侧 2 步） |
| ✅ | **9** | D16-01/02/03/04/06/07/08/12/13 |
| 🔨 | **3** | D16-05（取号无工具）/10（取代链 1.8%）/11（引用回写无扫描） |
| ⬜ | **2** | D16-09（状态词表分叉）/14（季审无面） |
| 机读 yes | **3** | D16-07/08/12 |
| 机读 partial | **3** | D16-04/06/13 |
| 机读 no | **8** | D16-01/02/03/05/09/10/11/14 |
| 段分布 | 呈报 4／登记 3／落地 1／生效 3／对账 2＋消费 1 | §2.1 五段+消费段（MECE：每环节唯一归属） |

> 口径提醒：✅ 与"机读 yes"两列独立——D16-01 有政策真源实存（✅）但完全无机读面（no）。**不建图的理由正是第二列**：14 环节里 8 个 no，能机生的 3 个恰好是**已有 gate/checker 覆盖**的那 3 个（登记原子性／落地合并／存量对账），也就是说"机器能看清的部分已经被机器看着了"。

### 红条目点名册（本图实查所得，只点名不修）

| # | 类 | 断点 | 实测 |
|---|---|---|---|
| R-16-01 | 词表分叉（静默改语义） | `status` 声明四值 vs 实测六值 | 2026-09-23 起新增 `decided`（7 条，含本战役母法 `#409`/`#410`）与 `void`（2 条 tombstone）；`deprecated` 归零；无 schema 更新、无词表件、无 checker ⇒ 任何按四值枚举写的下游（含未来图16 生成器）必然误判 |
| R-16-02 | 字段类型误用 | `superseded_by` 2/4 指向 `ARCH-XXX`（此处是占位写法，表示该 superseded_by 指向的议题号本身缺失/未登记——正是本行要报的病） | `#165→#ARCH-016`、`#201→#ARCH-045`（铁律#9 要求"新裁定 ID"）；取代链填充率 1.8% ⇒ 普查 §4 把"取代链"当建图卖点的依据不成立 |
| R-16-03 | 母法自相矛盾 | 铁律条数 10 vs 8 | 册顶 L24-40 十条；来源裁定 `#20-D`（L1314-1325）title 自述"（8 条规则）"且 summary 只枚举 8 条 ⇒ 第 9/10 条为后补而未回写母法，无校验面可发现 |
| R-16-04 | 引用格式越法 | 子裁定后缀格式 | 铁律#3 正则 `\d+(?:-[A-Z]+)?`（单字母）；实践中出现 `392` 的多字符子项写法（`tests/strategy_pipeline/test_pipeline_events.py:187/252/409/448` 四处），按 gate 正则会被截成"392-D"→未登记⇒**存量已 5 个悬空号中唯一真号即此类**（其余 4 个是占位形态字面值）；该形态一旦进 staged 即触发阻断（与 MEMORY 记录的 REFERENCE-INTEGRITY 自触死信同因） |
| R-16-05 | 发现入口缺失 | 裁定册未挂 ROOR | `grep ruling_registry docs/registry_of_registries.yaml` **0 命中**（该册自述 L12-13"每个注册表必须在此登记，否则不存在于系统"，实测 77 个 registry_id 无 REG-RULING）；对照：`rule_catalog_registry.yaml:3477` **有**——两册要求不一，ROOR 侧缺 |
| R-16-06 | 执行验证覆盖面缺口 | RULING-COMMIT-VERIFIED 不覆盖裁定册 | `ruling_commit_verified_gate.py:103-107` `_TRIGGER_PATTERNS` 只含 `docs/_archive/ruling_`／`docs/02_enterprise_architecture/ruling_`／`architecture_issue_registry.yaml`；**ruling_registry.yaml 不在内**；影响量已实测：册内 `已完成…commit <hash>` 声明仅 **1** 处、`commit <hash>` 提及 **14** 处 ⇒ 缺口真实但小，非紧急 |
| R-16-07 | 排列律违反 | 铁律#8 时间序 | date 序列逆序 **6 处**（`#19`/`#165`/`#218`/`#304`/`#386` 等）⇒ 生成器不可依赖 entries 物理序推时序 |
| R-16-08 | 号段不可反推 | 铁律#1"禁止跳号" | 1..410 空洞 **193**（47%），`RULING_GAP_WARNING` 只 warn；空洞究竟是"曾登记后删"还是"从未使用"无审计面可判（铁律#2"永不回收"与之冲突，见 §7 L-5） |
| R-16-09 | schema 漂移 | entry_schema 10 vs 实际 15 键 | 未声明：`evidence`(41 条)/`related_files`(5)/`renumber_note`(3)/`evolution_note`(1)/`related_branch_refs`(1) |
| R-16-10 | 计数漂移（册外） | gate 册自述字段 | `gate_registry.yaml:10 total_gates: 174` vs 实测条目 `grep -c '^- gate_id:'`=**180**（独立复证图14 R-17，非本图新案，登记以避重） |

## §3 并入 GOMAP 扩层的可行性评估（本图第二核心）

**结论：技术上可做、语义上无用，不推荐；若 Owner 仍要"看得清立法流"，推荐 GOMAP 只加一条 `out_of_scope_refs` 引用行（零新层，1 行 YAML）而非扩层。**

### 3.1 扩层要动哪些代码（逐处实测）

| 改动点 | 坐标 | 性质 |
|---|---|---|
| ①让立法流模块进机生 families | `scripts/governance/generate_governance_map.py:72-80` `_FAMILY_PATTERNS`（优先级序元组，`classify_family` 首命中即定族，L114-119）——需新增一行如 `("L7_legislate", r"ruling|adjudicat…")`；且 `scan()` L313-316 只按**路径**分类（不看头文本），当前 8 个 actor 路径 8/8 None ⇒ 不改此表则机生层永远空集 | 生成器改动 + 需重跑（`families` 层全量重建，L35/L362） |
| ②新层位命名落法 | `config/governance_operations_map.yaml:28-136` `pipeline.layers`（人工语义层，`build_document` L367-371 明示"生成器保留不动"）⇒ 直写 YAML 即可存活重跑；但命名须与既有 `GOM-L0..L6` 一致 ⇒ 建议 `GOM-L7`（"立法与规则供给"） | 人工层，1 处 |
| ③**必改代码白名单**（否则硬阻断） | `align_all.py:143` `_GOM_VALID_LAYERS = {f"GOM-L{i}" for i in range(7)}` + `:208-214` `_gomap_check_layers` 报 `人工层非法层位 GOM-L7（合法=GOM-L0..L6）`（hard 级→align_all exit 1）⇒ `range(7)` 改 `range(8)` 并同步 4 处散文（`:35-36`、`:141`、`:209`、`:214`）与生成器 `_PIPELINE_DEFAULT`（`generate_governance_map.py:102-110`） | **两处共享面（config + scripts/governance）= 本车道禁写**，须总包排产 |
| ④机生层比对是否要改 | **不用改**：`_gomap_diff_families`（`align_all.py:167-178`）按 `set(rebuild) | set(existing_fams)` 取并集逐族逐模块比对，族名不硬编码 ⇒ 新族自动纳入 | 零改动 |
| ⑤挂载类型天花板 | `_gomap_resolve_spec`（`align_all.py:148-164`）三态解析 `src/<dots>.py`／包 `__init__.py`／symbol（要求 token 出现在父模块源码文本）——**只认 Python 模块**；`_gomap_check_mounts`（:181-185）对不存在的 spec 判 hard。⇒ 立法流的核心对象（`ruling_registry.yaml`、裁定书 MD、待裁清单、ROOR）**一个都挂不上**；可挂上限=当前 actor 实测 8 个 .py | 结构性 |

### 3.2 成本-收益对比（含独立建图五件套）

| 路线 | 新增资产 | 共享面改动 | 能买到什么 | 判据 |
|---|---|---|---|---|
| **扩层 GOM-L7** | 0（YAML 加 1 层 + 生成器加 1 族） | 2 文件（align_all.py + config/governance_operations_map.yaml，均本车道禁写） | 一张"立法相关模块清单"：最多 8 个 import spec。**零流程语义**（GOMAP 无 edges/sequence 字段，实测 12 个顶层键内无任何边容器）、**零撞号防护**、**零状态语义修复**；副作用：新族正则会顺带吸进 `dangling_reference_gate`/`arch_reference_gate` 等非立法件（`classify_family` 首命中制，`_FAMILY_PATTERNS` L73-79 优先级序需重排） | 收益≈0，成本含 2 处高危共享面 ⇒ **不划算** |
| **独立建图（五件套）** | 5 件：`generate_ruling_flow.py` + `config/ruling_flow_map.yaml` + `validators/validate_ruling_flow.py` + `ruling_flow_gate.py` + `tests/governance/commit_gates/test_ruling_flow_gate.py`，另挂轴 1 行 + `align_all.py` 第十节 | 2 文件（`in_process_gate_registry.yaml` 的 MAP-ALIGNMENT `files_trigger` + `alignment_checklist.md` §3/§6） | 一张 14 格图，但生成器**无源可生**（§1 门④：源数据无流程位置字段）⇒ 只能是手画 YAML。根宪法 §9 条目 5 + 宪章 §8.2.4 双禁；且 14 格里 3 格语义已由 gate/checker 承载（D16-07/08/12），2 格是图11 域（D16-08 落地机制）⇒ 净零对价说不圆 | **机生优先律阻断（§1 门④三段论），不可合规施工** |
| **不建 + 三项微创**（推荐） | 1 件新脚本（取号器）+ 3 处既有面回写（`entry_schema` 补 5 字段、`status` 词表入 `_registry/vocabularies/`、ROOR 加 1 条 REG-RULING） | 与本车道无关 | 直击 🔨/⬜ 五个环节：D16-05（取号工具化，消 6 类撞号）、D16-09（状态语义定一）、D16-11（改号后引用扫描）、D16-14（册进 ROOR 即被季审发现）、D16-10（取代链要么补填要么退役该铁律） | 净增 1 脚本、0 新册、0 新 gate、0 新图 ⇒ 满足宪法 §4.1 净零；收益落在**风险**上而非**可视化**上 |

**为什么不建却仍算把四道门走完了**：宪章 §8.2.2 四门只是**准入**判据（必要条件），§8.2.3 净零对价与 §8.2.4 机生优先才是**充分性**闸门。本域四门字面全过（含④——裁定册确属可执行真相源），但**恰恰因为④过**才强制"图必须机生"，而真源里没有流程位置维度（§1 门④三段论）⇒ 合规的流程图表达不出来、表达得出来的那部分（引用网）已被 gate + `check_governance_bidirectional` 双重看着。落点与普查 §5 判据同形：本域=真源已在册、语义由政策+gate 承载、**观察**——这是"挖完之后判定不需要图"，不是"没挖到"。

## §4 重叠判定（旁轴，处置五选一：吸收/融合/扩展/废弃/引用）

| # | 撞车面对象 | 撞什么 | 处置 | 依据与落地要求 |
|---|---|---|---|---|
| O1 | GOMAP（图10） | "治理运行流"名义相近；普查 §5 明确建议"治理周/日批处理、基础设施守护循环归 GOMAP 扩层" | **引用（且写入 GOMAP 排除声明）** | GOMAP 是运行时**模块装配**视图（`counts: total_modules 427/wired 251`，L11-16），零流程边（§3.1⑤）；建议总包在 `out_of_scope_refs`（L17-25）追加一行"治理立法流 / ref=`ruling_registry.yaml` / note=裁定登记为治理脚本侧输入非运行时流水线节点"——把立法流**明确**置于图10 域外，同时修掉门③里"既没覆盖也没声明排除"的盲区（GOMAP 自身的"代码质量治理"项同理可参照） |
| O2 | 图11 交付流水线图 | D16-07（同 commit 原子）+ D16-08（落地合并）两环节的**执行体**就是图11 的 D11-C05 门禁链与 D11-C10 真落盘；`commit_queue_landing.py:313/450-457` 两图都要引 | **引用（不吸收）** | 分工线：**图11 管"改动如何到达 dev"（机制），图16 域管"裁定如何成为制度"（语义）**。若未来重开本图，D16-07/08 只能是 `role: handoff` 节点，只存 gate_id/脚本名，禁复制 claim/lock/queue/merge/三向合并的机制描述（同图14 O2 纪律，宪法 §4 内收判据"同真源可派生→必并"）。图11 骨架已实测在 `fig11_delivery/00_skeleton.md:80-88` 承载这些机制，双向认领成立 |
| O3 | RULING-REFERENCE 子台（priority=74，现属 REFERENCE-INTEGRITY 聚合台） | 它就是 D16-07 的实现体；建图会把"引用存在性+原子性"再画一遍 | **引用（不建第二张）** | 增量面已由机器全权看管且 fail-closed（`ruling_reference_gate.py:9`），实测引用网 3287 处/708 文件/233 号，悬空 5（其中真号 1、占位 4）⇒ 图对这条边**零增量信息**；但施工期需注意拓扑：新 gate 一律挂 `panorama_alignment_gate.py::make_map_alignment_gate()` 的 `subs`，而 RULING 系现在挂在 `dangling_reference_gate.py` 的聚合台（`in_process_gate_registry.yaml:122-127`），两个聚合台别混 |
| O4 | RULING-COMMIT-VERIFIED（priority=109） | 管"已完成（commit hash）"声明真实性=本图 D16-09 生效验证的**唯一**自动面 | **引用 + 覆盖面缺口点名** | 实测触发清单（`ruling_commit_verified_gate.py:103-107`）不含裁定册本身（R-16-06，量级小：册内 1 处声明/14 处 hash）；其注释自述的 `docs/02_enterprise_architecture/ruling_*.md` 兼容路径实测**0 个文件**（`ls` 空），主路径 `docs/_archive/ruling_*.md` 实测 **9 个**且 `ttl: permanent` ⇒ 建议总包把该行标"历史兼容位，实测零命中" |
| O5 | `deep_adjudication_method_policy.md`（governance_sop） | 该册 §2 已把 D16-01/02/03/04 四环节连同判据写全（182 行，`ttl: permanent`，2026-09-21 正典化，净零声明"不新增 gate/注册表/脚本/硬规则"） | **引用（严禁吸收）** | 该册 L20 逐字声明"裁定登记语义仍归 RULE-RULING + `ruling_registry.yaml`"——政策自己已经划了不承载登记语义的线，同时 §1-§2 又确实承载了呈报侧流程语义 ⇒ 任何图16 若把呈报侧四环节写进节点，就是与 permanent 政策册造第二真源（该册 §0 刚因"两原册升格合并、原册退役归档"做过一次净零对价，再加图=破净零） |
| O6 | `lane_construction_discipline_policy.md` §5 | 唯一成文的**并发取号/登记纪律**（4 条 bullet，L192-196），本图 D16-05/06 的判据真源 | **引用 + 升工具化** | 该节是图14 车道沉淀出来的纪律件，"先实测 max+1（`git show dev:` 重算）"这类判据**天然该是脚本**（§6 R-1）；若做取号器，须在该节加一行指向新脚本，否则纪律与工具再次分叉 |
| O7 | 规则 YAML 族（`trae_*.yaml`，86 本） | 门③要求之一：是否已有规则文件承载同一语义 | **不存在（域空白证明）** | 实测 `grep -l ruling_registry docs/01_policies_and_standards/rules/trae_*.yaml`=0 本；`trae_072`（跨 commit 原子性）是 import 时序原子性非登记原子性、`trae_060`（内收）不含取号步骤。⇒ 立法流**没有规则 YAML 承载**，但这是"缺一本规则文件"的问题，不是"缺一张图"的问题（宪章 §8.2 是图的准入判据）；如需补，走 `rule_catalog_registry` + `trae_047` 文件头 15 字段既有形态 |
| O8 | 图14 施工流图 / 图13 交易日循环 | 都含"引用裁定"这一动作（图14 已多处引 `#409`；图13 实测 `grep ruling_registry\|取号\|立法` **0 命中**） | **不并（无连接点）** | 图14 的裁定引用是**依据引用**（为什么这么做），不是**流程交接**（谁把裁定变成制度）；图13 与本域实测零交集。宪章 §8.2.1"域间无连接点才分图"在此表现为"不构成同一域"，无需处置 |

## §5 批次志（四类批次 + 增量曲线 + 三扫是否收敛）

| 批次 | 类型 | 视角/做法 | 本批产出 | 增量 |
|---|---|---|---|---|
| B1 | 需求批 | 从消费端反向挖：普查 §4 L60 与 §5 L64-65 的先验（"7 步/收益中等/归 GOMAP 扩层"）+ 图11/图14 骨架对裁定域的引用位 + 宪章 §8.2.2 判据 | 环节数 **7→11**（呈报侧四步与生效侧两步中，仅"登记/取代"两条被先验计入）；定五段+消费段 MECE | +4 环节 |
| B2 | 三重扫描批·①按生产者（源件逐件） | 立法流的六个生产者逐件实查：裁定册（字段/条目/号段）、RULING-REFERENCE、RULING-COMMIT-VERIFIED、commit_queue_landing 合并器、registry_alignment 双向 checker、deep_adjudication 政策 | 环节 **11→14**（补 D16-06 热文件 CAS 登记、D16-11 引用回写、D16-13 消费）；红条目 R-16-01/02/03/06/07/09 全部出自本批 | +3 环节，+6 红条目 |
| B3 | 三重扫描批·②按形态（节点→实体验证） | 把 14 环节逐个换算成"有没有机器面"：对 8 个 actor 模块跑 `classify_family()`、对 `mounts` 解析器试挂、对 `entry_schema` 与实测键求差 | **门④判词定稿（"字面过→反成阻断"三段论）+ GOMAP 覆盖率 0/8=0%** 的两个决定性数字；R-16-04（子裁定后缀越法）、R-16-10 | +0 环节，+2 红条目 |
| B4 | 三重扫描批·③按消费者 | 反向核谁读裁定册：`grep -rl ruling_registry --include=*.py` → 8 命中逐个定性（`generate_standard_family_registry` 机读证据源／`generate_rule_catalog` 目录入册／`align_all` 双向对账／`api_server` 仅注释／两个 gate 是**引用面**而非消费面／`_archive/migration/apply_rulings.py` 已退役件／`framework_composer`·`exp_ic_evidence`·`test_pipeline_events` 为同词不同物） | D16-13 定 partial；**发现 ROOR 缺失（R-16-05）**——消费者扫的最大收获不在图而在发现入口 | +0 环节，+1 红条目 |
| B5 | 案例批 | 拿 `#404` 撞号案当整案解剖（`docs/_working/e2e_integration/w0_ruling_404_collision_fix.md` 全文 + 主区死信 JSON `dead_reason` 原文 + `#408` tombstone 条目），把一条真实事故拆成 D16-05/06/08/11 四节点并逐个核状态 | 撞号风险**实测到实例并取到 verbatim 后果**（E3）；确认"图16 若建，其第一价值环节=取号，而取号无机读面"⇒ 反证门④ | +0 环节（4 节点归位） |
| B6 | 考古批 | 前代裁定书真源清产核资：`docs/_archive/ruling_*.md` 9 件（`ttl: permanent`，编号形态 `#ARCH-XXX 裁定 D`，早于册制）+ 铁律母法 `#20-D`（8 条）与册顶（10 条）比对 + 号段 193 空洞 + `deprecated` 存量 0 | R-16-03（母法漂移）、R-16-08（号段不可反推）、R-16-01 的时间起点（2026-09-23 才出现 decided/void）；确认"取代链"是**设计有、实践无**的环节而非被删环节 | +0 环节，+3 红条目 |

**增量曲线**：环节 7（先验）→11（B1/B2）→**14**（B3 前的 B2 末）→14→14→14（B3/B4/B5/B6 连续四批 **+0**）；红条目 6→8→9→12（B6 后仍在涨，但涨的全是"册内部一致性"，无一条指向"缺一张图"）。

**三扫是否收敛**：①按生产者 = **收敛**（六个生产者无遗漏，8 actor 全测）；②按形态 = **收敛**（14 环节逐个换算完，机读三分解 3/3/8 闭合）；③按消费者 = **未收敛**（只扫了 `.py` 侧 8 命中；708 个含 `裁定#N` 引用的 MD/YAML 文件未逐个分型，其中多少是"真消费裁定内容"vs"引用性提及"未量化）⇒ 见 §7 的**部分封顶**与 §6 R-4。

## §6 真源在哪 / 以后从哪三处读 / 重开触发条件（结论=不建）

### 6.1 本域真源地图（不建图之后，"看得清"靠这三处，按序读）

| 序 | 读什么 | 管哪几个环节 | 为什么是它 |
|---|---|---|---|
| 1 | `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` **L22-40 十条铁律 + L42-56 schema + entries** | D16-05/06/07/09/10/11/12 | 编号分配、不回收、子裁定格式、原子性、superseded 链、跨表引用——**流程判据全在注释里**；`unique_key: ruling_id` 同时是落地合并器的身份键（`commit_queue_landing.py:348`），即"册即协议" |
| 2 | `docs/01_policies_and_standards/sop/governance_sop/deep_adjudication_method_policy.md` §1.2-§1.4 + §2.1-§2.5 | D16-01/02/03/04 | `ttl: permanent`（2026-09-21 正典化，两原册已退役对价）；呈报侧的战场划分、六步入表闸、八类分类、裁定书格式、入册纪律**逐条可执行** |
| 3 | 两台 gate + 一个 checker：`ruling_reference_gate.py`（引用存在性/原子性/空洞 WARNING）、`ruling_commit_verified_gate.py`（"已完成 commit"真实性）、`registry_alignment.py:473-490 check_governance_bidirectional`（议题↔裁定存量对账，经 `align_all.py:516` 恒跑） | D16-07/08/12 | 这三件就是本域"能机读的 3 个环节"的全部实现；**读码即读流程** |

辅读（并发场景必读）：`sop/construction_sop/lane_construction_discipline_policy.md §5`（L192-196，取号/登记的并发四条）+ `docs/_working/e2e_integration/w0_ruling_404_collision_fix.md`（撞号修数的完整配方与前置拒绝条件，**唯一成文的三源并集取号口径**）。

### 6.2 重开触发条件（任一出现即重开本图，编号 D16-* 复用不改义）

| # | 触发证据 | 重开后的第一动作 |
|---|---|---|
| R-1 | **取号器落地**（新脚本被写出来，例如 `scripts/governance/d3_metadata/next_ruling_id.py`：三源并集 max + 号段连续性断言 + 落盘重解析数条目，即 `lane_construction_discipline_policy.md:195` 散文的四行代码化） | 若同时决定"取号→登记→原子"全程工具化，则图16 的价值前提改变：D16-05/06 由 no→yes，此时重评为"图"还是"再加一台 checker"（默认仍是后者） |
| R-2 | 裁定册**新增流程位置字段**（`stage`/`phase`/`segment` 任一，或 `entry_schema` 被扩到能表达"呈报→登记→生效→取代"四态并有词表件） | 立刻可机生：生成器只读该字段即可产节点，§8.2.4 机生优先律首次与流程表达**同时**可满足（§1 门④三段论第③步死结解开） |
| R-3 | **`superseded_by` 填充率 > 30%** 或"取代链"被实填（当前 1.8%，且 2/4 类型错）；或 Owner 明令铁律#9 升硬 | 取代链成为可机生边，图16 至少可建"取代链子图"（局部建=普查 §4 图15 式"先立登记面再建图"形态） |
| R-4 | 消费者扫（③向）补齐后发现 **≥ 3 个非脚本消费者需要一张导航视图**（即 MD 侧引用经分型后确有"沿流程找上下游"的真实诉求） | 建图收益判据首次成立 |
| R-5 | Owner 对 H-02（`#264` 与 `#266` 双活合法性认定，`docs/_working/archive/2026-09/final3_campaign/w8_3_owner_signature_book.md:159`）作出终裁并要求把"撞号处置"制度化 | 撞号处置从一次性 tombstone 升为流程环节（D16-05 变 ✅+yes），此时流程有状态机可画 |
| R-6 | `affected_files` 路径失效（62.8%）被修到 <10% | 执行面成为可机生边，"裁定→改动文件"链可入图 |

### 6.3 总包收口请求（本车道禁直写共享面，逐条请总包落；均为"不建"路线的配套微创）

| # | 诉求 | 目标共享面 | 建议处置 |
|---|---|---|---|
| X-1 | 修 R-16-01：`status` 词表定一（`decided`/`void` 要么并入四值、要么扩 schema 并出 `vocabularies/` 词表件）；修 R-16-09：`entry_schema` 补 5 个未声明键 | `ruling_registry.yaml`（热册，**本战役由总包统一写**） | 一次外科批同 commit；改后重跑 `generate_rule_catalog.py`（L101 已扫 superseded_by） |
| X-2 | 修 R-16-05：ROOR 追加 REG-RULING-001 条目（宪法 §0.6/§1-RULE-REGISTRY 明文义务，77→78 用字段不写死） | `docs/registry_of_registries.yaml` | 一行 tier_1_governance 引用 |
| X-3 | 修 R-16-03：母法 `#20-D` 的"8 条"与册顶"10 条"对齐（**只能以注记/演进条目方式改，禁重排历史 entries**——铁律#8） | `ruling_registry.yaml` | 新立演进注记或修 title，二者择一并留痕 |
| X-4 | 请 Owner 处置 R-16-02（`superseded_by` 误指 #ARCH 两条）与 H-02 双活号（`#264`/`#266`）——本车道无权代裁 | 裁定册 + `w8_3_owner_signature_book.md` | Owner 门位（宪法 §5.2"注册表净删"high 域） |
| X-5 | 本图**不进波3 施工排产**：请总包在战役总账里把图16 标为"判定不建（四门字面全过，但 §8.2.4 机生优先律与 §8.2.3 净零对价不可满足）+ 六条重开触发"，并把 R-1 取号器立为**独立微创工单**（不是图，不与五件套挂钩） | `docs/_working/map_build/` 总账 | 净零收益：0 新图、0 新 gate、预计 +1 脚本 |
| X-6 | 若 Owner 仍要"立法流可视化"，最小成本方案是 §3 推荐的 **GOMAP `out_of_scope_refs` 加 1 行引用**（顺带修掉门③"既没覆盖也没声明排除"的盲区），**而非扩 GOM-L7 层**（扩层需动 `align_all.py:143` 白名单，收益为零流程语义） | `config/governance_operations_map.yaml` | 1 行 YAML，不触发 `_gomap_check_layers` |

## §7 封顶声明与🌑点名

**封顶声明（分层表述，不假装全封）**：

1. **结论层已封顶**：图16 的"建/扩/不建"三选一判定所需证据（四道门 + GOMAP 结构 + 取号工具面）全部实测完毕，**本件此后不因新增环节而改判**——因为改判唯一依赖的是"§8.2.4 机生优先律能否与流程表达同时满足"，而当前不可满足的根因是"源数据无流程位置字段"这一事实（§6.2 R-1/R-2 才是翻案路径，与环节数无关）。
2. **环节层封顶**：D16-01~D16-14 即为流程全集；此后增长=已点名红条目的处置（册内部一致性），**不再增枝**；增枝须过 `skeleton_mining_policy.md` §3 停止判据三问并留理由。经三问复核：本图若再细分（例如把"取号"拆成"读 HEAD 册/读工作区册/读队列袋"）只改参数不改生产者与验证口径 ⇒ **不拆**。
3. **扫描层未全封**：三扫之③向（消费者）未收敛（§5），故本件**不出具全量封矿声明**；封矿批承接时只需补 ③向一轮，若 +0 环节即整件封顶。

**🌑 点名（个人/当前形态不可得，留档不假装）**：

| # | 🌑 项 | 为什么不可得 | 处置 |
|---|---|---|---|
| L-1 | Owner 拍板带宽与"是否亲裁"（D16-04） | 人门位=设计上的不可自动化（宪法 §5.2、AGENTS §9.11"对话内口头 Owner 说不构成门禁豁免"） | 若重开图，节点标 `human_gate: owner`，校验器只验"条目实存 + category/summary 有代裁字样"，不验内容 |
| L-2 | 待裁清单（D16-01 的产物）无常设面 | 先例清单落在 `docs/_working/` 战役件（`ttl: task_bound`，会被 TTL 回收），政策 L140 自认"该清单即 S3 进度真源"——**进度真源是易失件** | 🌑 本期不可得；升格需新登记面（新册），触宪法 §4.1 净零对价，超骨架会话权限，仅点名 |
| L-3 | 193 个号位空洞的成因（D16-05） | 铁律#2"永不回收"与实测 47% 空洞并存；无"曾登记后删"审计面可反推（R-16-08） | 🌑 不可判；不建图亦不解决，属号段语义债 |
| L-4 | 裁定"是否真的被执行"（D16-09/10 的终极问题） | RULING-COMMIT-VERIFIED 只覆盖 9 份归档 MD + 议题册，裁定册不在触发清单（R-16-06），而 `affected_files` 62.8% 路径已失效（R-16-02 面）⇒ 语义上"执行验证"这一环**在本域结构性无面** | 🌑 永久（除非把 hash 验证扩到裁定册——但册内仅 1 处此类声明，扩面收益不明），仅点名 |
| L-5 | 主区 `.runtime` 死信原文 | worktree 不共享 `.runtime`（本 worktree 实测无 `.runtime/commit_queue/`）；E3 的 verbatim 取自 `D:\ZephyrAlpha\.runtime\commit_queue\dead\q-20260923-st-ibt-remedy-cf-20260923-0023.json`（只读） | 复核命令 §8-C6 已写成"主区路径"形态，换机不可跑 ⇒ 显式披露 |
| L-6 | H-02 未决（`#264`/`#266` 双活合法性） | Owner 门位认定（`w8_3_owner_signature_book.md:159` 明列候选 a/b），骨架会话裁不了 | 转入 §6.2 R-5 作为重开触发之一 + X-4 收口请求 |

## §8 实查命令附录（全部只读，在 worktree 根 `D:\ZephyrAlpha\.aidrafts\st-mapbuild-20260924` 执行；先设 PATH）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
R=docs/01_policies_and_standards/_registry/catalogs

# C1 册规模与号段（本件 228/410/217/193 四个数的来源）
python -c "
import yaml,re,collections
d=yaml.safe_load(open('$R/ruling_registry.yaml',encoding='utf-8'));e=d['entries']
ids=[x['ruling_id'] for x in e]; nums=[int(re.match(r'裁定#(\d+)',i).group(1)) for i in ids if re.match(r'裁定#(\d+)',i)]
u=set(nums); print('entries',len(e),'| unique id',len(set(ids)),'| max',max(u),'| stems',len(u),
      '| holes',len([k for k in range(1,max(u)+1) if k not in u]),'| dup',[k for k,v in collections.Counter(ids).items() if v>1])"

# C2 字段完备率（边可生性的五个百分比：64.0 / 22.8 / 1.8 / 76.8 / 18.0）
python -c "
import yaml,os
d=yaml.safe_load(open('$R/ruling_registry.yaml',encoding='utf-8'));e=d['entries'];n=len(e)
for f in ['related_rulings','related_arch','superseded_by','affected_files','evidence']:
    c=sum(1 for x in e if x.get(f) not in (None,'',[],{})); print(f, f'{c}/{n}={100*c/n:.1f}%')"

# C3 两类边的质量：引用网（4 悬空/306 边）+ 执行面路径实存率（62.8% 失效）+ superseded 目标类型
python -c "
import yaml,os,re
d=yaml.safe_load(open('$R/ruling_registry.yaml',encoding='utf-8'));e=d['entries']
ids={x['ruling_id'] for x in e}
dg=[(x['ruling_id'],r) for x in e for r in (x.get('related_rulings') or []) if str(r).strip() not in ids]
print('related_rulings dangling:',dg)
af=[f for x in e for f in (x.get('affected_files') or [])]
print('affected_files edges',len(af),'missing',sum(1 for f in af if not os.path.exists(str(f).strip())))
print('superseded_by:',[(x['ruling_id'],x['superseded_by']) for x in e if x.get('superseded_by')])"

# C4 schema/词表漂移（10 vs 15 键、status 六值、category 50 值、date 序 6 处逆序）
python -c "
import yaml,collections,re
d=yaml.safe_load(open('$R/ruling_registry.yaml',encoding='utf-8'));e=d['entries']
dec=set(d['entry_schema']); act=set(k for x in e for k in x)
print('declared',len(dec),'observed',len(act),'undeclared',sorted(act-dec))
print('status',dict(collections.Counter(x['status'] for x in e)))
print('distinct category',len({x.get('category') for x in e}))
dt=[str(x['date']) for x in e]; v=[e[i]['ruling_id'] for i in range(1,len(dt)) if dt[i]<dt[i-1]]
print('铁律8 逆序',len(v),v)"

# C5 GOMAP 对立法流覆盖率 = 0/8（把生成器的 classify_family 直接喂给 8 个 actor；None 即不可挂）
python -c "
import importlib.util as u
s=u.spec_from_file_location('g','scripts/governance/generate_governance_map.py');m=u.module_from_spec(s);s.loader.exec_module(m)
for a in ['src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py',
 'src/zephyr/gov_enforcement/commit_gates/ruling_commit_verified_gate.py',
 'src/zephyr/gov_enforcement/registry_alignment.py',
 'src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py',
 'scripts/governance/commit_queue_landing.py',
 'scripts/governance/d5_architecture/generators/align_all.py',
 'src/zephyr/gov_enforcement/commit_gates/_reference_helpers.py',
 'scripts/governance/generate_governance_map.py']: print(m.classify_family(a), a)"
grep -c "id: GOM-L" config/governance_operations_map.yaml                       # 7 层
grep -n "裁定\|立法\|呈报\|取号" config/governance_operations_map.yaml            # 仅 2 处 note_zh 变更说明
grep -n "^  [a-z_]*:" config/governance_operations_map.yaml | sort -u -k2 | head  # 层位字段：id/name_zh/desc_zh/mounts/disconnected/config_refs（无边容器）
grep -n "_GOM_VALID_LAYERS\|def _gomap_resolve_spec\|mount 路径不存在" scripts/governance/d5_architecture/generators/align_all.py  # 143/148/185

# C6 取号面=零工具 + 撞号实例 + 死信 verbatim（末条为**主区**只读路径）
find scripts src -iname "*ruling*"                                              # 仅 2 gate + 1 归档迁移件
grep -rn "next_ruling\|max_ruling" --include=*.py src scripts                    # 空
grep -n "撞号\|renumber_note" $R/ruling_registry.yaml | head -12                 # 6 起实例（L2254/3602/3766/3782/4256/5531-5540）
python -c "import json;print(json.load(open('D:/ZephyrAlpha/.runtime/commit_queue/dead/q-20260923-st-ibt-remedy-cf-20260923-0023.json',encoding='utf-8'))['dead_reason'])"
sed -n '190,197p' docs/01_policies_and_standards/sop/construction_sop/lane_construction_discipline_policy.md   # 取号纪律 4 行散文
sed -n '28,47p' docs/_working/e2e_integration/w0_ruling_404_collision_fix.md     # 三源并集取号口径

# C7 交接面：双向 checker + 合并器身份键 + gate 拓扑
grep -n "def check_governance_bidirectional\|def _ruling_arch_errors\|def _issue_ruling_errors" src/zephyr/gov_enforcement/registry_alignment.py  # 473/449/460
grep -n "check_governance_bidirectional" scripts/governance/d5_architecture/generators/align_all.py            # 107,516
grep -n "同侧身份键重复\|unique_key 元数据\|def _merge" scripts/governance/commit_queue_landing.py | head      # 457/348
grep -n "gate_id: RULING" $R/gate_registry.yaml $R/in_process_gate_registry.yaml                                # 74 在册；109 在 inproc
grep -n "RULING-REFERENCE" src/zephyr/gov_enforcement/commit_gates/dangling_reference_gate.py                  # 232 = 聚合台子台清单
grep -n "_TRIGGER_PATTERNS" -A 6 src/zephyr/gov_enforcement/commit_gates/ruling_commit_verified_gate.py         # 103-107 不含裁定册

# C8 规则 YAML 与发现入口（门③域空白证明 + R-16-05）
ls docs/01_policies_and_standards/rules/trae_*.yaml | wc -l                     # 86
grep -l "ruling_registry" docs/01_policies_and_standards/rules/trae_*.yaml | wc -l   # 0
grep -c "registry_id:" docs/registry_of_registries.yaml                          # 77，其中无 REG-RULING
grep -n "ruling_registry" docs/registry_of_registries.yaml                       # 空 = R-16-05
grep -n "ruling_registry.yaml" -A 4 $R/rule_catalog_registry.yaml | head         # 3477 在册（对照面）

# C9 引用网规模与悬空（D16-07/12 的"机器已经看着"证据）
python -c "
import re,os
pat=re.compile(r'裁定#(\d+(?:-[A-Z])?)'); ids=set(); occ=0; files=0
for r,ds,fs in os.walk('.'):
    if '.git' in r or '__pycache__' in r: continue
    for fn in fs:
        if not fn.endswith(('.md','.yaml','.yml','.py')): continue
        try: t=open(os.path.join(r,fn),encoding='utf-8',errors='replace').read()
        except OSError: continue
        m=pat.findall(t)
        if m: occ+=len(m); ids.update(m); files+=1
import yaml; d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml',encoding='utf-8'))
reg={x['ruling_id'].replace('裁定#','') for x in d['entries']}
print('occ',occ,'files',files,'ids',len(ids),'dangling',sorted(ids-reg))"

# C10 政策侧真源（呈报四环节的原文位）
grep -n "净零声明\|裁定登记语义\|入册纪律\|裁定书格式\|按族打包\|标记词" docs/01_policies_and_standards/sop/governance_sop/deep_adjudication_method_policy.md
grep -n "tier: high" -B 2 docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml | grep -A 2 "D_GOVERNANCE"
ls docs/_archive/ruling_*.md | wc -l ; ls docs/02_enterprise_architecture/ruling_*.md 2>&1 | tail -1   # 9 / 无（gate 兼容路径实测空）
```

---

**自审裁定（六向台账 + 一行结论）**：

| 向 | 落点 |
|---|---|
| 上 | 谁触发本域=Owner 门位（`risk_tier_registry.yaml:85-87`）+ 代裁/自裁两子路径（D16-04，条目实测 title）；输入=待裁清单（D16-01，政策 §2.2 五分区） |
| 下 | 输出给：门禁引用网（D16-07/12，3287 处/708 文件）、尺子家族册（D16-13，`generate_standard_family_registry.py:29`）、规则目录（`rule_catalog_registry.yaml:3477`）、队列落地合并器（D16-08，`commit_queue_landing.py:450-457`） |
| 内 | 14 环节逐个含自动化程度（§2 状态列+机读列，三分解 3/3/8）；红条目 10 条（R-16-01~10） |
| 旁 | 8 个撞车面对象逐个五选一（§4 O1-O8），核心两条：GOMAP=引用+排除声明（O1）、图11=交接锚（O2）；与 `deep_adjudication_method_policy` 的"严禁吸收"（O5） |
| 史 | 考古批 B6：9 份前代裁定书（`docs/_archive/ruling_*.md`，`#ARCH-XXX 裁定 D` 编号形态早于册制）+ 母法 `#20-D` 8 条 vs 册顶 10 条 + `deprecated` 存量归零 + decided/void 词表于 2026-09-23 静默出现 |
| 新 | 外部对标一句话结论：本域同型物=ADR/MADR（Architecture Decision Records）的 `status` 生命周期与 supersession 链，业界成熟做法是**轻工具（`adr new` 分配序号+目录约定）+ 词表校验**，而非可视化流程图——与本件 §3 判"取号器优先于建图"独立收敛，故不建图结论与同业实践一致 |

**结论行**：干（判定所需四道门证据齐、GOMAP 覆盖率与取号面实查齐、六向无缺）；**欠一项**=三扫③向消费者 MD 侧 708 文件未逐个分型（§5 已计入"未收敛"，转 §7 扫描层未全封 + §6.2 R-4）。溢出条目：无（14 环节未溢出新枝；域宽矛盾类问题以 X-1~X-6 收口请求形式外提，未改他车道骨架）。
