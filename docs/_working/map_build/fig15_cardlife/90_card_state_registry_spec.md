---
ttl: task_bound
completes_when: experiment_registry 扩枚举落地（card_state 词表 + 卡条目）+ generate_card_lifecycle_map.py + config/strategy_card_lifecycle_map.yaml + validate_card_lifecycle_map.py + card_lifecycle_gate 子台 + 挂轴 六件同批跑完红绿两轮后，本件退役为图15 施工档案
title: 图15 卡状态登记面收敛·施工规格（90_card_state_registry_spec，块B）
owner: st-mapbuild-20260924
---

# 90 卡状态登记面收敛施工规格（块B）

> **为什么必须先有它**：图15 的四道门第④门当前**不过**——实测「卡状态三处分裂」的真面目是**三处零交集 + 七套状态词汇 + 0 个可 join 的键**（数字与口径见 `00_skeleton.md` §3：68 张卡中 29 张无 status 头、status 串 22 种且 0 张在受控词表内；experiment_registry 11 条与卡交集 0；CH 三判定表 1,456 行判决中带卡号 0 行）。普查的判定原文=`docs/_working/map_census/00_panorama_map_census_v1.md:59`「先立卡状态登记面（或挂 experiment_registry 扩枚举）再建图」。**登记面是这张图从"不可建"变"可建"的唯一路径**，不是图的附属品。
> **写给谁**：波3 施工会话。照本规格逐节做即可落地；本件不含实现代码，只含契约。
> **形态母版**：图9 四件套坐标全部实测在盘（`config/strategy_production_map.yaml` + `validate_strategy_production_map.py`（CLI/exit 母版，`:36-42` 枚举与必填键、`:170-201` exit 语义）+ `strategy_factory_map_gate.py:114-139`（`_check` 形态）+ `panorama_alignment_gate.py:295-302`（subs 聚合台））；校验项条文体裁照 `fig14_construction/90_step_anchor_validator_spec.md` §4。
> **纪律前提（本规格的每一处取舍都受这两条约束）**：AGENTS §4.1 全资产净零 + §4.2 内收判据四句（同真源可派生→必并｜零触发零消费→退役｜同域重复簇→收敛唯一｜跨域不同对象→不并）。**因此"新建一本卡状态册"默认是被否的**，须先穷尽既有面。

## §1 真源选型：六个候选面实测，五否一选（含被否方案与理由）

**判据**：状态真源必须满足①有 unique_key 面可放 card_id；②有 FK/pending_fk 治理面可承接跨册引用；③在 ROOR（`docs/registry_of_registries.yaml:881 total_registries: 76`）在册；④不是 gitignored/换机即断；⑤不与已有字段撞语义。**同时**：卡的**参数正文**（考窗/阈值/桶/N_eff/机制陈述）**必须继续留在卡 md**——把正文搬进册=造第二真源，100% 漂移（本骨架 §3 已示范漂移速度）。所以本规格是**"状态与正文分离"**的收敛，不是"把卡塞进某张表"。

| 候选 | 实测证据 | 判定 |
|---|---|---|
| **A. `experiment_registry.yaml`（REG-EXP-001）扩枚举 + 扩条目类**（简报先验指向的方案） | ①在册：`docs/registry_of_registries.yaml:693 physical_path: .../experiment_registry.yaml`；②有 `unique_key: [experiment_id]`（`:43`）与 `pending_fk` 治理面（实测 1 条已 resolved 的 UNI-BASKET-001 记录，`:20` changelog）⇒ ①②③齐；④**已经在管预注册语义**：`pre_registered: bool`（`:98`，注"实验前声明假设/指标/样本量/止损规则（git commit 时间戳为证）"）+ `viability_verdict: enum supported/refuted/inconclusive`（`:102`）+ `n_trials/dsr_value/pbo_value/is_overfit` 齐；⑤实测 11 条中 `pre_registered=True` 6 条⇒ **有真实触发**（非零触发零消费）；⑥`status` 四值 `running/completed/failed/archived`（`:78`）与卡状态是两个轴但同域同簇（都在登记"一次考试/一份契约"）⇒ 内收判据"同域重复簇→收敛唯一"要求并进来而非另立 | **选 A（附改造）**：见 §2/§3。**注意**：`viability_verdict` 三值枚举**恰好就是** `exam_policy.md:60-66` 三态出口的直译（supported=达标 / refuted=不达标 / inconclusive=判死或不足），且实测 11 条全 null 从未回填 ⇒ 不是"新建语义"，是**启用一个已存在但闲置的字段**（净零最有利的一点） |
| **B. 卡 md frontmatter `status` 升为唯一真源** | 模板确已写 `status: frozen`（`factor_mining_sop_policy.md:108`）；但实测四宗硬伤：①68 张卡中 **29 张无 status 头**（42.6%），status 串 **22 种自由文本**；②`status` 字段值域受 `_registry/vocabularies/status_vocabulary.yaml` 三值 `{draft, active, deprecated}` 管辖，**抽样 4 张卡全部 `in_vocab=False`**（实跑 `load_vocabulary_values`）⇒ 以 md 为真源=以一项既有违规为真源；③`frontmatter_field_registry.yaml` 实测 58 个字段条目中**无任何 card/state/lifecycle 字段**（`grep "field_name: card"` 零命中），新增要改共享面且需新词表；④拦违规的 `validate_frontmatter_values.py` **已退役**（在 `scripts/_archive/`，见 §5 考古链），现存 `validate_ssot.py:55-62,241-250` 的 P1-1 只是报告面；⑤卡 md 无 unique_key/FK 面、`docs/_working/` 是 `ttl: task_bound` 工作区且禁 .json（DCR-005/008），不是登记面形态 | **否**：可作**证据面**（卡是正文真源），不可作**状态真源**。本规格因此规定：卡 frontmatter 增加 `card_state:` 只读镜像字段（由登记面派生、校验器判"镜像==真源"），**方向是册→md，不是 md→册**（否则又回到 29 张无头 + 22 种串的局） |
| **C. 新建 `strategy_card_registry.yaml` 挂 ROOR** | 76 本 catalogs 实测无卡宿主（§3-A）；技术可行 | **否**：违 AGENTS §4.1 全资产净零 + §4.2「同域重复簇→收敛唯一」——REG-EXP-001 与它同域同对象（都在登记一次考试/一份契约），并 ROOR 行、+ registry_master_index 行、+ 双真源同步义务、+ 一张新册的 gate/对齐/一致性契约成本。**只有当总包否决 A 时才启用**，且启用时必须同批把 REG-EXP-001 的 `pre_registered/viability_verdict` 两字段判为"引用新册"（否则出现两个预注册字段） |
| **D. `backtest_backlog.yaml`（SOP-A Step A0 预注册台账）** | 文件头注释逐字自称："预注册=可审计真源（验收阈值跑前写死，禁事后挪门柱；threshold_status=draft 的数值为 AI 提案，批次决策点确认冻结后才可跑）"——**语义看起来正是本域** | **否（实为陷阱）**：①实测 142 条对象里 **`threshold_status` 键出现 0 次**（骨架红条目 F-09：注释承诺的字段不存在）；②`unique_key` 缺失，对象键=`object_id`（TDM 节点派生，`generated_by: scripts/backtest/generate_backtest_backlog.py`，机生件被生成器覆盖）；③对象=**地图节点的回测行为**，不是契约文档（`node_ids/layer/map_layer/flow` 占满字段）⇒ 挂上去=把节点台账改成品种台账 |
| **E. run 档案面（`data/backtest_artifacts/runs/` + `src/zephyr/backtest/run_archive.py`）** | 形态高度契合：`run_archive.py:53-61 _STEP_FILES`（含 `verdict.md`、`errata.md`）、`:67-72 _REQUIRED_STEPS`（四 kind 各必选步骤集）、`:275 log_iteration()`（只增不改迭代留痕，喂 DSR）、`:311 finalize_run()`、`content_sha256/safe_write_text`；`sop_d_run_archive_naming.md:28` 三原则之"只增不改…发现错误追加 errata.md" | **否作真源 / ✅借形态**：`data/backtest_artifacts/` 被 `.gitignore:586` 整目录忽略（F-11），本 worktree 该目录**不存在**（`git ls-files` 仅 1 件）⇒ 判据 ④ 不满足（换机即断、非版本资产、ROOR 不可能在册）。**借三点**：run 的 `{run_id, object_id, steps{}, verdict_ref, snapshot_commit, attempts}` 结构 = 本规格 §2 卡条目 `runs[]` 子结构的母版；errata「追加不改写」= S3→S4 附录迁移的机验形态；`content_sha256` = 禁止边 X02（静默改 frozen 参数）的指纹工具 |
| **F. `task_card_meta_registry.yaml`（PS-REG-017）** | 有现成的"元层登记表"形态：`migration_rules[]`（rule_id/description/applies_to）+ `state_machines_note` + `systems{}` 四套并行体系 | **否（跨域不同对象→不并）**：对象是**任务卡**（legacy 143 估/v2_staging 3/sqlite_task_db 20/高层规划），其 MR-05 明文"四套并行体系数量永久锁定为 4"——塞策略卡即违例；SQLite `data/databases/governance.db` + `task_repo.py` 才是它的活体后端，与卡无关。**借一点**：`migration_rules[]` 的三字段结构正是本图 §3.3 禁止边机读表要抄的形态（AGENTS 术语/先例复用优先于新造） |
| **G. 复用 `contract_status_vocabulary.yaml`（draft/frozen/deprecated）** | 词表 `active`，且其注释逐字写「契约状态与文档状态是不同词表…frozen 表示合约已冻结锁定」+「validate_interface_contracts.py 必须从本词表动态加载，禁止硬编码」——**卡的 frozen 就是这套词汇** | **否**：①它的宿主册 `interface_contract_registry.yaml` **已归档**（`capability_canonical_file_registry.yaml:7799` 路径已指 `_archive/`；退役裁定见 `ruling_registry.yaml:2046` 僵尸处置批 R3"interface_contract 使命完成或真源已移位"）⇒ 一个 active 词表挂在一个退役册上，本就是一处待收的孤儿；②值域缺 SEALED/RED/GREEN/INSUFFICIENT/SUSPENDED/VOID 六态，扩它=把接口契约词表改成研究诚信词表（跨域污染）。**结论**：本规格新建 `card_state_vocabulary.yaml`（§3.1），并把 contract_status 孤儿面列为总包收口诉求（X-6），不与其合并 |

**选定方案的净零论证（AGENTS §4.1 要求声明替代/合并）**：
- **未新增注册表**（选 A）、**未新增 gate 台**（进 `MAP-ALIGNMENT` subs）、**未新增数据库表**、**未新增卡片文件**（卡 md 是既有物）。
- 新增物只有：1 个受控词表（`card_state_vocabulary.yaml`，13 值）+ 1 个图 YAML + 3 个代码件（生成器/校验器/gate 子台）+ 1 个测试件 + REG-EXP-001 的 schema 2.1→2.2 扩字段。
- **声明替代（对价）**：① 替代卡 md frontmatter 的 **22 种自由文本 status 串**（改判为受控 `card_state` 只读镜像）→ 词表化后散文串进 `status_note` 附注位，语义不丢；② 替代 `factor_mining_sop_policy.md:105-126` 模板里"人记 N_eff 账 + 人记是否冻结"的隐性状态（模板 `status: frozen` 一行改为引用 `card_state`）；③ 激活一个在册但从未使用的字段 `viability_verdict`（11 条全 null）取代"新建三态出口枚举"的需要 → **零新枚举**覆盖 S6/S7/S8 三态；④ 替代 `docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md` 等 7 本战役台账里"状态"列的**卡相关行**（台账继续存在，但卡态不再是它的职责，只留指针）。
- **净删项**：无（挖矿期无权删；F-09 的 `threshold_status` 注释漂移、F-08 的字段册计数漂移交总包统一纠）。

## §2 卡条目登记面（REG-EXP-001 schema 2.1→2.2 的具体改法）

### 2.1 两类条目共存，一类一个语义

| 条目类 | 键形态 | 对象 | 现有/新增 |
|---|---|---|---|
| **契约条目（新增类）** | `experiment_id` 保持 unique_key 不破，取值 `CARD-<card_id>`（如 `CARD-T0-PRERG-02`）；业务键另存 `card_id`（如 `T0-PRERG-02`） | 一张预注册卡（含单假设卡 / 族卡 / 窄化裁定书三种 `entry_kind`） | 新增 |
| **运行条目（现有类）** | `EXP-{TYPE}-{NNN}`（不变） | 一次跑数实例 | 现有 11 条，**新增 `card_id` 外键指向契约条目**，形成 卡 1 : N run |

> 为什么保留 `experiment_id` 作主键：册的 `unique_key: [experiment_id]`（`:43`）被 `registry_consistency_contract.yaml` 与 ROOR 消费；改主键=牵动全册 FK，成本远高于加前缀。`CARD-` 前缀与既有 `EXP-` 前缀天然互斥，无重号风险（实测现有 11 个 id 均为 `EXP-*`）。

### 2.2 契约条目字段集（✔必填 / ○选填 / ▲新增键）

| 字段 | 必填 | 语义与机械判定 |
|---|---|---|
| `experiment_id` ✔ | `CARD-` + card_id，全册唯一 |
| `card_id` ✔▲ | 卡业务号，正则 `^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){1,4}$`；实测在用品种：`T0-PRERG-01/02`、`T0-CONDITIONAL`、`P3-E1C-09`、`P3-B-EXP-01..06`、`P3-B-NARROWING`、`ALGO件③` 无号（⇒ 回填时给新号并在 `legacy_ref` 记文件名） |
| `entry_kind` ✔▲ | 枚举 `single_hypothesis \| family \| narrowing_ruling`（案例 B 实测三粒度；语义真源=`factor_mining_sop_policy.md:100`「每批考试 N_eff 封闭」） |
| `card_state` ✔▲ | 枚举动态加载 `_registry/vocabularies/card_state_vocabulary.yaml`（13 值，见 §3.1）；**禁在校验器里写死中文/英文枚举字典**（AGENTS §9.9） |
| `status_note` ○▲ | 原卡片自由文本（如"考试启动前写死；启动后任何字段不得改动，改动即作废重开"）——**收纳 22 种串的语义，不丢弃** |
| `lives_in` ✔▲ | `path_history[]`：`{path, first_seen}` 清单（**一张卡允许多版本文件**，实测 M03 活例 v0→v1 两文件并存，见 §5 案例 C；单键 `path` 会把正常升版误判为重复） |
| `family_id` ✔ | 既有语义，实测仅 22/68 卡有头 ⇒ 回填时按 `card_id` 前缀推导并标 `derived: true` |
| `n_eff` ✔ | 封闭族声明（实测 19/68 有头，缺者标 `unknown` 并计红账，禁默认 1） |
| `credential` ✔(状态非 S1/S2/S3 时✔)▲ | 迁移凭证数组 `{to_state, ruling_id 或 flag: none, date}`；`ruling_id` 必须在 `ruling_registry.yaml` 在册（X12 的机验落点） |
| `rejudge_used` ✔▲ | bool，全局一次性令牌（M10）；true 后再有重判请求=X03 红 |
| `revives` ○▲ | 复活指针：`<旧 card_id>`；`entry_kind` 为新卡且 `family_id` 命中已 SEALED/condemned 族时**必填**（X13） |
| `revived_by` ○▲ | 反向指针（旧卡侧，可由 revives 派生生成，禁手填双写=造第二真源） |
| `runs[]` ○ | 派生自运行条目的 `card_id` 反查（**生成器现算，不手填**）：`{experiment_id, verdict, dsr, at}` |
| `exam_policy_refs` ○ | `{threshold: "exam_policy.md#§1", template: "factor_mining_sop_policy.md#§4"}` 引用不复制（INV-1） |
| `conclusion_tier` ○ | `final \| 暂定（复权链断供）`（`exam_policy.md:46-50` §4 的引用位；**不映射进 card_state**，见 §7 拒绝增态理由） |
| `body_fingerprint` ✔▲ | `{path, content_sha256, frozen_at}`：卡正文（尤其 frozen 段）指纹，X02 的机验原料；工具复用 `run_archive.py` 已用的 `src/zephyr/shared/io/file_utils.content_sha256` |
| `history_from` ✔▲ | 登记面生效日；此前迁移不计（诚实声明 🌑L-1，禁假装全史可查） |

## §3 状态与迁移的机读定义（图 YAML 的 `laws/boundary/states/transitions/forbidden_edges`）

### 3.1 `card_state_vocabulary.yaml`（新，13 值）

值名与 `00_skeleton.md` §1 状态编号一一对应：

```yaml
values:
  - {value: draft,             map_state: D15-S1,  definition: 卡已立、判据未写死}
  - {value: candidate,         map_state: D15-S2,  definition: 机器筛出未升格，禁出任何 PASS 语义}
  - {value: frozen,            map_state: D15-S3,  definition: 考窗/阈值/桶/N_eff 写死，参数不可再改}
  - {value: frozen_amended,    map_state: D15-S4,  definition: 只增不改：带日期附录追加，frozen 参数零改动}
  - {value: executing,         map_state: D15-S5,  definition: 试验台账行已开、执行件跑数中}
  - {value: green,             map_state: D15-S6,  definition: 预注册阈值全过且 DSR 校正后仍显著, legacy_field: viability_verdict=supported}
  - {value: red,               map_state: D15-S7,  definition: 阈值未过, legacy_field: viability_verdict=refuted}
  - {value: insufficient,      map_state: D15-S8,  definition: 样本/功效不足或 fail-closed 存疑, legacy_field: viability_verdict=inconclusive}
  - {value: suspended,         map_state: D15-S9,  definition: 裁定延后重考且带触发条件，禁被读成通过}
  - {value: sealed,            map_state: D15-S10, definition: 终态：不再重开、不再改参重跑, terminal: true}
  - {value: condemned,         map_state: D15-S11, definition: 终态：机制证伪/数据面不可修，入死矿账, terminal: true}
  - {value: graduated,         map_state: D15-S12, definition: 终态：结论已回写因子/策略册, terminal: true}
  - {value: void,              map_state: D15-S13, definition: 终态：挪门柱/加条目/N_eff 破/卡被改, terminal: true}
```

- **三个值不新造**（green/red/insufficient 直译在册的 `viability_verdict`）⇒ 净零。
- 词表头须带 `module_id` 与治理锚（照 `contract_status_vocabulary.yaml:1-11` 形态），且校验器**必须动态加载**（照其"禁止硬编码字面量"注释）。

### 3.2 迁移边表（17 条，图 YAML `transitions[]`）

每条：`{transition_id: D15-M01..M17, from: [states], to: state, actor: human|ai|machine, credential_required: ruling|test_green|none|owner_sign, description(≤120 字), source_refs[]}`——逐条值取 `00_skeleton.md` §2.1 表，不重写语义（骨架=契约）。

### 3.3 禁止边表（13 条，图 YAML `forbidden_edges[]`，形态抄 PS-REG-017 的 `migration_rules`）

每条：`{edge_id: D15-X01..X13, pattern: [from, to], rule_zh(≤120 字), credential_source（在册 ruling_id 或 policy 锚）, checker: CV-08}`。骨架 §2.2 是语义真源，图 YAML 是机读镜像，**CV-13 判两者一一对应**（漏一条即红——禁止边的覆盖度是本图的核心 KPI）。

## §4 图 YAML schema（`config/strategy_card_lifecycle_map.yaml`，生成器产物 + 人工语义层）

顶层 REQUIRED_TOP（CV-01）：`schema_version, map_id, name_zh, laws, boundary, states, transitions, forbidden_edges, instance_key_space, counts`
与图9 差异：无 `layers/nodes/edges/products`（实例轴无环节）；`states` 替 `nodes`、`transitions` 替 `edges`、新增 `forbidden_edges`。

```yaml
schema_version: '0.1'
map_id: strategy_card_lifecycle_map
name_zh: 策略卡生命周期图
generated_by: scripts/governance/d5_architecture/generators/generate_card_lifecycle_map.py
derived_from: docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml   # 单向派生，禁手编实例层
laws:            # CV-15 非空
  - 状态真源在 REG-EXP-001 契约条目；卡 md 是判据正文真源，图与镜像字段都是派生件
  - 图的 states/transitions 只存标识与引用，禁复制 exam_policy / factor_mining_sop / 卡正文（INV-1）
  - 封卡即终：任何就地复活边一律非法，复活=新 card_id + revives 指针
boundary:        # 逐字引用，不得意译（CV-16 校验引文在源文件可命中）
  - "工厂图三铁律之一：运动员不兼任裁判，考试权只在 E4 咽喉（config/strategy_production_map.yaml:20）"
  - "轴区分：本图 state_id=D15-S*、对象键=card_id；策略工厂 node_id=FAC-*、build_status 是工序进度不是契约地位"
  - "不含：考试判据正文（exam_policy）｜裁定产生流程（图16）｜提交机制（图11）｜数据供料（图12）"
instance_key_space:
  card_id: "T0-PRERG-* / T0-CONDITIONAL / P3-* / <lane>-<family>-<NNN>"
  disjoint_with: [candidate_id(CAND-*), strategy_id, node_id(TDM-*), step_id(BM-*), step_id(D14-*), module_id(MOD-*)]   # CV-11 判值域不互撞
counts:
  total_states: 13            # 必须 == len(states)（CV-14）
  total_transitions: 17
  total_forbidden_edges: 13
  terminal_states: 4
  cards_total: <现算>
  by_state: {draft: <现算>, frozen: <现算>, sealed: <现算>, ...}   # 全由生成器现算
  machine_readable: {yes: 0, partial: <现算>, no: <现算>}
pending_registration: []      # 未入账卡的显式白名单（非空即 warn 计数，禁"忘了就绿"）
```

**禁手编声明**：`counts` / `by_state` / `pending_registration` / 契约条目集合由生成器覆盖写（宪章 §8.2.4 机生优先 + AGENTS §9.5 静态清单禁手工维护）；`laws/boundary/transitions/forbidden_edges` 是人工语义层，生成器保留不覆盖（照 GOMAP 的 effective_from 保留策略）。

## §5 校验项逐条（CV-01…CV-18，照图9 十项风格）

实现约束：校验逻辑唯一真源 = 新校验器 `validate_structure(data) -> list[str]` + `check_registry(registry, data) -> tuple[list[str], list[str]]`（两函数两入参；gate、align_all、CLI **三方同源动态 import，禁复制**，先例=`strategy_factory_map_gate.py:129` 懒加载注释、`validate_strategy_production_map.py:132-167 check_stores(data, root)` 传仓库根防 CWD 漂移）。

| # | 校验项 | 级别 | 判定式（可直译代码） | 本仓实测会命中它的样本 |
|---|---|---|---|---|
| CV-01 | 顶层必填键齐全 | error | 遍历 REQUIRED_TOP 缺键即 error 并提前返回（照 `validate_strategy_production_map.py:55-58`） | — |
| CV-02 | **状态枚举合法且动态加载** | error | `card_state ∈ load_vocabulary_values('card_state_vocabulary.yaml')`；图 `states[].value` 与词表集合双向闭合（图有词表无 / 词表有图无 均 error）；校验器源码含硬编码 `"sealed"` 字面量 ⇒ error（AGENTS §9.9） | 卡头 22 种串若被照抄进图，全部现形 |
| CV-03 | card_id 合法 + 全册唯一 + `experiment_id` 前缀互斥 | error | `re.fullmatch(r"[A-Z][A-Z0-9]*(-[A-Z0-9]+){1,4}", card_id)`；`len(ids)!=len(set(ids))`；契约条目 `experiment_id.startswith('CARD-')` 且 `== 'CARD-'+card_id`；运行条目必须以 `EXP-` 开头 | 68 张卡现无号可查（29 张无头 + 无 id 面）⇒ 回填期首批必红，属预期 |
| CV-04 | **迁移边合法**：每个实例 `from→to` ∈ transitions | error | 对 `credential[]` 逐条：`(from,to)` 不在图 transitions 集 ⇒ error；缺 `to_state` 的 credential 记 error | F-04（V2 作废只在脚本注释里）一旦回填即为无据迁移 |
| CV-05 | **SEALED 卡禁就地改状态** | error | `card_state ∈ {sealed, condemned, graduated, void}`（词表 `terminal: true` 动态取）⇒ 其后任何 credential 的 to_state ≠ terminal 集内值即 error；终态卡任何字段变更（除 `revived_by`/`status_note`/`lives_in.path_history` 追加）⇒ error | #390 实弹（"任何会话禁以 #389 为凭重跑两卡"）的机验形态 |
| CV-06 | **复活必须指向新卡 id** | error | 出现 `revives: X` ⇒ 本条目 `card_id != X`；同 card_id 的 `lives_in.path_history` 追加允许，但 `card_state` 从终态回到非终态 ⇒ error；`entry_kind` 新卡且 `family_id` 命中终态族而 `revives` 缺省 ⇒ error（X13） | F-05（复活新卡只有散文 parent_context，无指针）实测 1 例 |
| CV-07 | **禁边出现即红** | error | 实例流水 + 图 `forbidden_edges[]` 做笛卡尔匹配，命中任一 pattern ⇒ error（错误串必须点名 X 号）；`forbidden_edges` 为空或条数 ≠ 骨架 §2.2 声明数 ⇒ error（CV-13 联动） | X01（red→green）、X05（候选卡出 PASS）、X09（同假设双卡） |
| CV-08 | 同一假设双卡（N_eff 双重计分） | error/warn | 同 `family_id` 且 `entry_kind=single_hypothesis` 的活跃（非终态）条目 >1 ⇒ error；`n_eff` 为 `unknown` ⇒ warn 计数 | **F-07 活例**：T0-PRERG-01（t0_regime）与 ALGO件③（algo_mining）同族两卡；实测 68 份中 `family_id` 仅 22 ⇒ 回填期 warn 面很大 |
| CV-09 | 每条迁移必有凭证；凭证必须可验 | error | 非 S1/S2/S3 的 credential：`ruling_id` 须命中 `ruling_registry.yaml` 的 `ruling_id` 值集；`flag: none` ⇒ warn 并计数；凭证含未在册号 ⇒ error（同 RULE-RULING gate74 的语义，勿造第二套引用判据） | **F-01 活例**：#389 `related_rulings` 引 '裁定#304' 而 #304 是 Regime 重校准 ⇒ 在册但语义错绑，本条只能判 warn，须总包勘误（收口 X-1） |
| CV-10 | **三处一致性（派生面不得与真源冲突）** | error | ①卡 md `status_note`/`card_state` 镜像 == 册 `card_state`（不一致 error）；②图 `counts.by_state` == 册现算值（不等 error，防散文写死数）；③运行条目 `card_id` 指向的契约条目存在（悬空 error，允许 `pending_fk` 形态的 forward-ref 但须登记）；④`viability_verdict` 与 `card_state ∈ {green,red,insufficient}` 的映射一致 | 现状直接全红：29/68 无头（①）、22 种串（①）、REG-EXP 与卡交集 0（③）、`viability_verdict` 11 条全 null（④） |
| CV-11 | 键空间不互撞（防撞第二真源） | error | 各 `disjoint_with` 值域正则互斥；`CARD-*` 不得出现在 candidate_id/strategy_id/node_id 集内 | 实测 CH 三表 + 两册均无卡号 ⇒ 现状通过，回归价值在将来 |
| CV-12 | INV-1 反复制（判据正文不得抄进图/册） | error | 图任一字符串字段 `len>120` ⇒ error；对 `exam_policy.md`+`factor_mining_sop_policy.md`+全部卡正文做 40 字滑窗，命中即 error（豁免：`boundary[]` 逐字引文须标 `verbatim: true`；`status_note` 位豁免，因为它就是收纳原串的地方） | 图9 先例 `validate_strategy_production_map.py:90-91`；X11 |
| CV-13 | 迁移/禁边覆盖度与骨架一致 | error | 解析 `00_skeleton.md` §2 两表的 `D15-M\d\d` / `D15-X\d\d` 串集合，与图 `transitions[].transition_id` / `forbidden_edges[].edge_id` 比对，差集非空即 error（骨架=契约，改号须总包回写） | 波2 若作业簿新增 M18 而图未跟 ⇒ 立即现形 |
| CV-14 | 计数不落地在散文 | error | `counts.total_states==len(states)`、`total_transitions==len(transitions)`、`total_forbidden_edges==len(forbidden_edges)`、`terminal_states==count(terminal)`、`sum(by_state.values())==cards_total`；图/册任一处出现「13 态/17 边/68 张卡」类写死数字（非注释行）⇒ error | 宪章 §4.3；F-08（字段册 `total_registered: 53` vs 58 条）为同类先例 |
| CV-15 | laws/boundary 非空 | error | `if not data.get('laws') or not data.get('boundary')` ⇒ error（照 `:60-61`） | — |
| CV-16 | boundary 逐字引用可回源 | error | boundary 每条含 `（<路径>:<行或锚>）` 时，须在该文件命中引号内原文（同 `fig14 §4 CV-15` 的加强版：这里带行号也允许，但行号偏了要 warn，因 §0 门② 已证行号锚系统性失效） | 工厂 `:20` 三铁律原文引用 |
| CV-17 | 指纹防静默改（X02 机验） | error | `card_state ∈ {frozen, frozen_amended, sealed, condemned, graduated, void}` ⇒ `body_fingerprint.content_sha256` == 现算 `content_sha256(卡 frozen 段)`；不等且无 `frozen→frozen_amended` 或 `→void` 的 credential ⇒ error | **F-10 关联**：两张被 production 脚本引为判据真源的卡**根本不在盘**（`docs/_working/t0_matrix/t0_ceiling_prereg_card.md`、`t0_conditional_v3_prereg_card.md`，实测 `git log --all` 从未出现）⇒ 指纹无从计算即 error，真源缺失必须显性红 |
| CV-18 | 文件生命周期不冒充状态 + 判重 | warn/error | `lives_in.path_history[]` 内同字节内容（sha256）跨条目重复 ⇒ error（双真源）；同条目内重复 ⇒ error；卡文件位于 `docs/_working/` 且 `ttl: task_bound` 属正常，但图节点不得因"文件进了 archive/"而派生状态（归档=属性，非状态） | **F-12 活例**：2 组同字节双份（`2026-09-07-tdm-backtest-protocol.md`、`2026-09-15-neff-estimator-preregistration.md`）+ `tdchain_mine` 与 `tdchain_mine_closeout` 等值重复台账 |

告警面（不阻断，只计数打印）：`pending_registration` 非空、`n_eff=unknown` 卡数、credential `flag:none` 数、CV-08 同族多卡、CV-10 的回填期红转黄窗口（施工批 P2 之前允许 warn）。

## §6 CLI 契约（照抄 `validate_strategy_production_map.py:170-201`）

```
python scripts/governance/d5_architecture/validators/validate_card_lifecycle_map.py \
    --map config/strategy_card_lifecycle_map.yaml \
    [--registry docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml] \
    [--repo-root .] [--structure-only] [--skip-live] [--json]
```

* `--map`（默认值=DEFAULT_MAP 常量）=图 YAML；`--registry`=册路径（对抗测试可指 fixture）。
* **exit 语义逐字照搬**：`0`=PASS（打印 `PASS: 卡生命周期校验通过（states=13 transitions=17 forbidden=13 cards=<现算>）`）；`1`=结构违规（stderr 逐条 `ERROR:` + `FAILED: N 个结构违规`）；`2`=文件不存在 / YAML 解析失败 / 顶层非对象。
* `--structure-only`=只跑 CV-01..03/12/14/15（不读册、不读文件系统）；`--skip-live`=跳过磁盘/CH 实存类检查（CV-10③、CV-17 的现算指纹），**gate 走这条**——同 FACTORY-MAP 把仓储存在性排除在 gate 外的口径（其头 INVARIANTS + `alignment_checklist.md` 图9 行"CH 环境异常不误伤提交"）。
* `--json`=机器可读，供 `align_all.py` 内联复用（禁 subprocess 自调）。
* 文件头 15 字段（真源=`docs/01_policies_and_standards/rules/trae_047*.yaml §A_full`；战役共识件 §5④ 写的"14 字段"与实测不符，**以 trae_047 为准**，先例见 `fig14_construction/00_skeleton.md` 红条目 R-18）；`[ERROR_CONTRACT]` 必须写 `SystemExit(1)=结构违规; SystemExit(2)=文件/解析失败`。
* 依赖红线：全程只读（禁写任何文件，照校验器头 INVARIANTS"台账只读（本工具禁写）"）；路径一律以 `--repo-root` 解析，**禁 CWD 漂移**（`check_stores(data, root)` 就是为此扩的 root 参数）。

## §7 生成器契约（`generate_card_lifecycle_map.py`）

1. 读 REG-EXP-001 契约条目 + 卡 md frontmatter + 骨架 §2 两表 → 覆写图 YAML 的 `counts/by_state/instance 视图/pending_registration`；`laws/boundary/states/transitions/forbidden_edges` 保留不覆盖（人工语义层）。
2. 派生方向恒为 **册→md 镜像**：可回写卡 frontmatter 的 `card_state:`（一行），但必须由 `--write-mirror` 显式开启且走 `safe_write_text`（AGENTS 硬规则 13 热文件 CAS）；默认只打印 diff。
3. **禁 `datetime.now()`/`time.time()`**（RULE-SCHEMA-TZ 硬规则 10）；时间戳经 `--as-of` 注入，比对时忽略该字段（GOMAP"忽略 generated_at/counts"先例）。
4. 新 .py 模块 ⇒ 施工同批：`add_module_translation.py` 登记大白话简介（TRANSLATION-COVERAGE gate）、creation_token（CREATE-GUARD）、`apply_depgraph --add-design-node`（RULE-DEPGRAPH 先登记后施工）。
5. 未入账卡进 `pending_registration[]` 而非报错退出——生成器要能在半成品状态可跑（防施工期一次性大爆炸 diff，图14 规格 §6.4 同策）。

## §8 与 gate 的接法（**不建独立 gate**）

* 共识件 §5④ 明令 st-gslim P4 已把六张图门并入聚合台。动作=在 `src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py:295-302` 的 `subs` 列表追加**一行**（实测现 6 行；图14 车道同批申请第 7 行 ⇒ 本图排第 8）：
  `("CARD-LIFECYCLE-MAP", "card_lifecycle_gate", "_check")`
* 新文件 `src/zephyr/gov_enforcement/commit_gates/card_lifecycle_gate.py` 只暴露 `_check(gateway, files, **kwargs) -> tuple[bool, str]`，形态逐条照 `strategy_factory_map_gate.py:114-139`：
  1. `_TRIGGER_FILES` 六件（2026-09-26 L-HOST15 宿主落地后由四件扩至六件）=
   {`config/strategy_card_lifecycle_map.yaml`, 校验器, 生成器, 91 号口径档案,
   `_registry/catalogs/experiment_registry.yaml`, `_registry/vocabularies/card_state_vocabulary.yaml`}；
   未触发 ⇒ `return True, "skip: ..."`；**注意 normcase 归一**（该文件 `:105-109` 注释实录：绝对路径朴素反斜杠替换恒 miss=实弹断边放行事故）；
   registry 期的装载点是宿主词表与宿主册（图头 `anchor_source=registry`），91 号件降为语料口径/
   别名规则/分裂面档案——它仍留在触发面（改分母必须重校），但 `_check_anchor_block` 在 registry 期
   只验其可解析与口径块在位，词表与实例两面的实载性由校验器 CV-HOST 硬腿负责（禁两处判据打架）；
  2. 校验逻辑动态 import `validate_structure`（`sys.path.insert(0, _VALIDATORS_DIR)`），**禁复制校验代码**；
  3. 图 YAML 解析失败 / 校验器不可达 ⇒ **fail-closed 阻断**；
  4. error>0 阻断；warn 面只呈报。
* 注册面：`in_process_gate_registry.yaml` 的 `MAP-ALIGNMENT` 条目 `files_trigger`（`:301-307` 形态）追加本图触发面。**不新增 gate_id、不动 `total_gates`** ⇒ 净零。
* own-scope：本校验器是结构校验型（读两文件 + 词表），按 AGENTS §3.3 登记 own-scope 或"全仓扫描理由"——本图需扫 `docs/_working` 卡正文指纹（CV-17），**这是全仓扫描**，理由须登记：「卡正文在 `_working` 散文中，无中心册可替代指纹源」；缓解=只在触发面命中时扫、单次上限 200 文件、超阈值降级为 `--skip-live`。
* gate 文件需 15 字段头（见 §6 口径纠偏）。

## §9 挂轴（第⑤件，施工期由总包落）

| 面 | 动作 | 坐标 |
|---|---|---|
| `alignment_checklist.md` §3 | 加"策略卡生命周期图（图15）"行：真源=`config/strategy_card_lifecycle_map.yaml`（派生自 `experiment_registry.yaml` 契约条目）、对齐 key=`state_id(D15-S*) + card_id`、规则=CV-01~18、时机=commit 前（触发式）/ align_all 新节、工具=本校验器 + MAP-ALIGNMENT 子台 CARD-LIFECYCLE-MAP、处置=error>0 阻断 | 照 `:87`（图9 行）与 `:88`（图10 行）形态；§3 标题行的张数用字段不写死 |
| `alignment_checklist.md` §6 时机矩阵 | 加一行 | `:178`（§6 章首）起，照图 9/图 10 行形态 |
| `align_all.py` | 新增一节（照抄第八节 `:581-612` 形态：内联 import 校验器 + 传仓库根 + 硬>0 计入 exit 1）。节号取决于图12/13/14/16 车道同批排产顺序 | `scripts/governance/d5_architecture/generators/align_all.py:581` |
| 宪章 §8.3 导航 | 纵轴目录动态来自 §3，无需改宪章 | `system_charter.md:217-234` |
| ROOR / `registry_consistency_contract.yaml` | REG-EXP-001 扩 schema 2.2 后须同步：unique_key 不变、新增 `card_id` 为业务键、`pending_fk` 允许 `CARD-*` forward-ref | `experiment_registry.yaml:20` changelog 纪律 + `:43` unique_key |

## §10 红证要求（**判通过前必须逐条证明能红**；≥12 条，本规格给 18 条）

每个用例=一份临时图 YAML/册/卡 fixture（pytest `tmp_path`，禁写生产路径，AGENTS §9.6），断言 `validate_structure`/`check_registry` 返回**指定 error 串**且 CLI `exit==1`（解析类断 `exit==2`）。测试件形态照 `tests/governance/commit_gates/test_strategy_factory_map_gate.py`。

| # | 红证 | 构造 | 期望触发 | 对应实测事故 |
|---|---|---|---|---|
| RC-01 | 枚举非法 | `card_state: sealed_ish`（词表外值） | CV-02 | 22 种自由串现状 |
| RC-02 | 校验器硬编码词表 | 删掉 fixture 词表里的 `sealed` 值，图仍用 sealed | CV-02（必须仍判红，否则说明值集被写死） | AGENTS §9.9 |
| RC-03 | card_id 重复 / 前缀混用 | 两条契约条目同 `card_id`；或契约条目 id 不带 `CARD-` | CV-03 | 卡号↔文件当前无一一对应（v0/v1 双文件） |
| RC-04 | 非法迁移边 | credential 写 `{from: draft, to: sealed}`（不在 transitions） | CV-04 | F-04（作废只在注释里） |
| RC-05 | **SEALED 就地复活** | sealed 卡 credential 追加 `to: executing` | CV-05 + CV-07(X03) | **#390 实弹原样复现** |
| RC-06 | **AI 自行把 RED 改 GREEN** | 流水 `red→green` 且 credential 空 | CV-07(X01) + CV-09 | 三铁律 `:20`；X01 |
| RC-07 | 候选卡直接出 PASS | `candidate→green` | CV-07(X05) | #366 条件③ |
| RC-08 | 未冻结先跑数 | `draft` 条目挂 `runs[]` 且无 frozen 期 credential | CV-04/CV-07(X06) | `exam_policy.md:26`+`:28` |
| RC-09 | 无试验台账行的判绿 | green 卡但 `trial_ledger_registry.batch_records` 无对应 batch_id | CV-10③/CV-07(X07) | `exam_policy.md:31`「后补=造假」 |
| RC-10 | 复活指针缺失 | 新卡 `family_id` 命中 sealed 族、`revives` 为空 | CV-06(X13) | F-05 |
| RC-11 | 复活指向自己 | `card_id: X` 且 `revives: X` | CV-06 | X13 反向构造 |
| RC-12 | 派生面与真源冲突 | 册 `card_state=sealed` 而卡镜像 `card_state=frozen` | CV-10① | F-03（裁定说挂起、卡头说 frozen） |
| RC-13 | 散文计数漂移 | `counts.total_states: 6` 而 `states` 13 条；或 boundary 里写"13 态" | CV-14 | F-08 同类；宪章 §4.3 |
| RC-14 | 把判据正文抄进图 | `transitions[i].description` 填 `exam_policy.md:24-30` 整段（>120 字 + 40 字滑窗命中） | CV-12 | INV-1 / X11 |
| RC-15 | 禁止边被偷偷删 | 从 `forbidden_edges[]` 删 X03 | CV-13 + CV-07 | 骨架 §2.2 是契约 |
| RC-16 | 同字节双真源 | 两条契约条目 `lives_in` 指向内容完全相同的两个文件 | CV-18 | F-12 |
| RC-17 | 静默改 frozen 参数 | 改卡 frozen 段一个阈值字节，不改 `card_state`、不加附录 credential | CV-17 + CV-07(X02) | `factor_mining_sop_policy.md:108`；卡片头 34 处自述 |
| RC-18 | 判据真源不在盘 | 契约条目 `lives_in.path_history` 指向 `docs/_working/t0_matrix/t0_ceiling_prereg_card.md`（实测从未入库） | CV-17（指纹无从计算=error，禁静默 warn） | **F-10 原样** |
| RC-19 | YAML 损坏 / 顶层非对象 / 文件缺失 | 截断 YAML；写成 list；指向不存在路径 | CLI `exit 2`；gate 侧 **fail-closed 阻断** | 图9 头 INVARIANTS 同款 |
| RC-20 | 凭证引用未在册裁定号 | `credential.ruling_id: <未在册裁定号形态>`（不存在的号） | CV-09 | 宪法 RULE-RULING / gate74 同源，防第二套引用判据 |
| RC-21 | 聚合台子台被吃 | 把 `card_lifecycle_gate` 模块临时改名/不可 import | 聚合台 `subs` 分支 ⇒ `[CARD-LIFECYCLE-MAP] 子检查不可加载` 并阻断（`panorama_alignment_gate.py:310-312` 已实现该语义） | 防"台在但子台被吃" |

绿证要求：全部红证跑完后用真实图 YAML + 真实册跑一次；**允许的唯一剩余红**是未入账卡的 `pending_registration` 与 `n_eff=unknown`（warn 面），收尾报告的状态分布数字一律读 `counts`，禁手写。

## §11 施工批次 DoD（波3 排产参考，每批可独立提交）

| 批 | 内容 | DoD（可判） |
|---|---|---|
| P1 | 词表 `card_state_vocabulary.yaml`（13 值）+ REG-EXP-001 schema 2.2 扩字段（`entry_schema` 加 9 键，**先不回填条目**）；`frontmatter_field_registry` 登记 `card_state`/`card` | 词表可被 `load_vocabulary_values` 读到；`validate_structure --structure-only` exit 0（图上无实例） |
| P2 | 语料回填：68 份卡 → 契约条目（`card_id`/`entry_kind`/`family_id`/`n_eff`/`lives_in`/`status_note`/`body_fingerprint`），首批允许 `card_state` 保守取 frozen | 生成器产出 `cards_total`；`pending_registration` 为空或逐项有理由 |
| P3 | 图 YAML + 校验器结构面（CV-01/02/03/12/14/15/16） | RC-01/02/03/13/14 全红 |
| P4 | 迁移面 + 禁边面（CV-04/05/06/07/08/09/13） | RC-04..12/15 全红 |
| P5 | 一致性与指纹面（CV-10/11/17/18）+ 卡 frontmatter 镜像回写 | RC-12/16/17/18/19 全红；镜像 == 真源 100% |
| P6 | gate 子台接 `subs` + `files_trigger` + 对抗测试全量 | RC-20/21 红；触发面外 skip 放行；提交不连坐 |
| P7 | 挂轴（§9 五处）+ align_all 新节 | align_all exit 0；与图9/图10 节并存不冲突 |
| P8 | 治理纠偏批（§12 未决 + 骨架 F-01..F-12 逐条闭环或降级留痕） | 每条 F 号要么闭环、要么在图里可见为 warn 计数；**禁"删判据句子让校验变绿"** |

## §12 未决与本规格**不能**自己解决的部分

1. **F-01 引用错号**：在册裁定 #389 正文与 `related_rulings` 误引 #304（应为 #331）。CV-09 只能判 warn（号在册、语义错绑），需总包勘误（收口 X-1）。
2. **历史流水不可回溯**（骨架 🌑L-1）：卡状态变更史不存在任何 append-only 面，git 提交史无法区分"迁移"与"改文案"。规格以 `history_from: <P1 落地日>` 诚实截断 ⇒ 13 态中 S4/M05 这类"曾经发生过几次"的问题**只能向前可查**。
3. **人门位凭证的对话原文**（🌑L-2）：#389/#399 的授权链部分是"对话原文为凭"。宪法 §1.11 明令对话内口头"Owner 说"不构成门禁豁免 ⇒ 图里 `credential: none` 是**诚实状态**，不是 bug；是否要求补裁定属 Owner 决定。
4. **是否给卡专建生成式视图（前端/Panel）**：`experiment_registry` 描述里提到展示层=`experiment_history.py`（51 号工作流 B）。本规格不含 UI；若要做，属图15 封矿后的消费端增量，须走另一批。
5. **词表归属**：`card_state_vocabulary.yaml` 挂 `_registry/vocabularies/`（与 `contract_status_vocabulary.yaml` 同目录）——但 contract 那个词表的宿主册已归档（§1-G）。若 Owner 判"词表也要净零"，退路是**把 13 值直接内联在图 YAML 的 `states[]`**（图9 的 `STAGES/BUILD_STATUS` 即此先例，`validate_strategy_production_map.py:39-42`），代价=CV-02 的"动态加载"红证（RC-02）不再适用、卡 frontmatter 镜像字段失去词表可指性。**本规格默认走词表**，因其与 `verifiability/contract_status` 的既有受控词表范式一致。
6. **卡与 E7/E8 的引用闸**（骨架 X10 跨图检查）需要图9 侧配合（`strategy_production_map.yaml` 挖矿期全域禁碰）⇒ 本规格只登记 `human_gate` 字段位，不实现跨图判红。

## 总包收口请求（本件诉求，共享面禁本车道直写）

| # | 诉求 | 面 |
|---|---|---|
| V-1 | 批准块B 选定的宿主=**扩 `experiment_registry.yaml`（REG-EXP-001）schema 2.1→2.2**（§1-A 五项判据实测 + §11 净零对价），并批准新建 `card_state_vocabulary.yaml`（13 值，其中 3 值复用在册 `viability_verdict`）；若 Owner 否决，退路见 §12-5 | catalogs + vocabularies + ROOR |
| V-2 | §12-1 引用错号勘误（#389 误引 #304，普查行同步改写） | ruling_registry + `map_census/00_panorama_map_census_v1.md:59` |
| V-3 | `panorama_alignment_gate.py:295-302` `subs` 加一行（本图排第 8，图14 排第 7，请总包定序）+ `in_process_gate_registry.yaml` MAP-ALIGNMENT `files_trigger` 追加触发面；**不新增 gate_id、不动 total_gates** | src + gate 册 |
| V-4 | `alignment_checklist.md` §3 图15 行（key=`state_id(D15-S*)+card_id`）+ §6 时机矩阵行 + `align_all.py` 新节（节号由总包统一排） | docs + scripts |
| V-5 | token：`validate_card_lifecycle_map.py` / `generate_card_lifecycle_map.py` / `card_lifecycle_gate.py` / `config/strategy_card_lifecycle_map.yaml` / `tests/governance/commit_gates/test_card_lifecycle_gate.py` / `card_state_vocabulary.yaml` 六件 + 本车道 2 份 MD | creation_tokens |
| V-6 | 施工期新 .py 三件的模块大白话简介登记（`add_module_translation.py`）+ depgraph 设计态登记（`apply_depgraph --add-design-node`）须同批 | module_translation + depgraph |
| V-7 | F-02/F-07（已封卡被批准开测的治理事故 + 同假设双卡与 #390 的卡号↔文件↔判决错绑）请排"卡号谱系补齐"专项；本校验器上线后这些**会持续判红**，属预期行为不是噪声 | 裁定册 + 卡语料 |
| V-8 | F-06（负结果台账/死矿登记无面）与 F-10/F-11（判据灭失、判定书不在版本控制）跨线修复授权；本图不擅自新建专册 | catalogs + `.gitignore` + depgraph |
| V-9 | 词表孤儿：`contract_status_vocabulary.yaml` 的宿主册已归档但词表 active，且 `validate_interface_contracts.py` 仍在盘。请判"退役"或"改指新宿主"——本图已实测**不复用它**（§1-G 两条理由），但其孤儿态会误导后续会话再来复用 | vocabularies + validators |
| V-10 | 与图9/图12/图16 车道的轴-键互认（谁存 card_id、谁存 run_id、谁存 DS-*、裁定凭证归谁解释）：请总包在波2 组织会签，勿留到波3 现编 | 各车道骨架 + alignment_checklist §3 |

**自审裁定**：干（本件为规格件，六向台账要求的适用面是作业簿；规格自身已含真源调研七证：A 七个候选面逐个实测并给被否理由、B 字段集与在册 schema 对齐、C 母版坐标逐行引、D 校验项 18 条各配本仓活体样本、E 红证 21 条、F 施工批 DoD、G 未决项不擅裁）。
