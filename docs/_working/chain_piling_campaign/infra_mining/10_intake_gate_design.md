---
ttl: task_bound
completes_when: 本文档随定桩战役归档即完成
title: 入库闸骨架设计
owner: ZephyrAlpha-Owner
session: st-chainpile-20260922
date: 2026-09-22
---

# 入库闸骨架设计（meta_question_registry · 基建四件套之一）

> 输入真源：`00_piling_minutes.md`（唯一输入，引用格式 [纪要§N]）。
> 定位：W1 设计件，W2 才施工（施工顺序立法见 [纪要§8.5]）。
> 工程名=**meta_question_registry**（原问题中央登记表）；使命=把"值得问的问题"变成受治理资产（对标 AEA 注册中心 / OSF 预注册 / 图书馆馆员蓝图 [纪要§5]）。
> 四件套边界：**入库闸=问题进门**（字段完备性校验+查重+五要素机检+洪水防线+盲册通道）；模板生成器=问题展开；未答看板=排队消费；考试回填闭环=答案落账。本文不代写姊妹件内容。

## §0 骨架总览

| 章 | 一句话 |
|----|--------|
| §1 定位与边界 | 入库闸只管"进门"，落点 PG 同实例+写入 API+YAML 机生快照+ROOR 登记 |
| §2 字段完备性校验 | 对标 AEA/OSF 生命周期字段映射 18 字段底稿，产出 A 必填/B 条件必填/C 可后补三级表 |
| §3 五要素机检规则 | 每要素给出可机械判定判据；不可机判部分显式交人工初审，禁伪装成机械 |
| §4 查重 | 归一化+simhash+layer/line_ref 约束，高拒/中人工/低过三分流；62 条 v1 骨架期按 ID 挂载核对 |
| §5 洪水防线 | 限流三参数+质量门槛+两级定案审（机械层自动/语义层 Max 前置）+Owner 例外+初始建库批量通道 |
| §6 盲册区 | 不合格但值得养的问题入册，晋级/复查/退役闭环；结论=status 体系特例 |
| §7 写入 API 契约 | 校验顺序+状态流转端点+snake_case 错误码+审计事件清单（词表 SSOT=总册 §2.1），W2 按此实现 |
| §8 外部锚点对标 | AEA/OSF 入库闸机制对照与本设计取舍得 |
| §9 本件盲点自查 | 11 维逐维表态，禁留白 |
| §10 schema 增补提案 | 新字段只提案"待 W1 评审"，禁直改 18 字段底稿 |

## §1 定位与边界

1. 入库闸的唯一职责：把候选问题判定为【入库/入盲册/拒】三态之一，并留全量审计痕。
2. 技术落点（W2 施工）：PG 与 depgraph 同实例（通道先例 `get_depgraph_pg_connection`，定义于 `src/zephyr/governance/depgraph_schema.py`）+ DDL-as-Code（仿 `scripts/ai_layer/apply_ai_intake_ddl.py`）+ 写入 API（`src/zephyr` 新模块，基建 src 新件在 [纪要§10] 写域白名单内）+ YAML 机生快照（仿 `scripts/ai_layer/gen_intake_ref_snapshots.py` 的幂等机生先例）+ ROOR 登记（`docs/registry_of_registries.yaml`）。
3. RULE-SSOT 判向 [纪要§8]：问题库属数据资产→**DB 为真源，YAML 快照=只读机生镜像，禁手改**；快照再生成即对账（幂等）。治理规则（闸门参数、限流数）属规则数据→YAML 真源同步 DB。
4. 既有治理接口挂接清单：裁定#NNN 登记册（闸门参数变更走裁定）、gate 体系（如增提交期 gate 必须 own-scope 登记）、能力卡 `data/capability_cards/`（W2 登记）、净零铁律（本件新增须声明替代——见 §1.5）、`safe_write_text` CAS（`src/zephyr/shared/io/file_utils.py`，快照落盘唯一通道）、多会话 claim 制（q_id 分配与批量提交须 claim）、时间分层铁律（今日输出→明日输入，同一时戳禁循环 [纪要§8.2]，入库闸做环检测见 §3.6）。
5. 净零声明：入库闸四能力（校验/查重/防线/盲册）**替代**"问题散落于对话即丢、无资格线、无查重"的口口相授现状；查重机检**合并复用** `src/zephyr/ai_layer/intake/dedup.py`（normalize_text/simhash64/content_fingerprint）与 `gate.py` 的拒因风格，不另起炉灶。

## §2 字段完备性校验（18 字段分级表）

### §2.1 外部生命周期字段映射

| 生命周期阶段 | AEA 注册中心机制/字段 | OSF 预注册机制/字段 | 映射到 18 字段底稿 [纪要§7] |
|----|----|----|----|
| 登记/注册 | 唯一 trial ID（AEARCTR-*）、title、abstract、PI/机构、干预描述、主要/次要结局、资助 | draft 模板驱动（Standard/ASPredicted 等）；register 动作→**不可变时戳快照+DOI** | q_id、title、provenance（出处=注册时戳+来源） |
| 在库更新 | status 变更记录、amendment 留痕版本链 | new version=后继版本，原注册保留 | status、parent_id（OSF 组件树→一问一考拆问 [纪要§3]） |
| 评审/分析 | 结果 embargo（分析完成前封存） | view-only 匿名链+封存期 | exam_plan、pit_proof（先注册后分析的时戳=无前视证明机制，本设计直接取用） |
| 发布/结果 | linked publications（前/后结果挂接） | 注册页挂接产物与文件 | chain_refs、evidence_refs、last_exam |
| 撤回/退役 | withdrawal 留原因、记录不删除（墓碑） | withdraw 留 stub 说明 | merged_into、status 退役态、q_id 墓碑不复用 [纪要§7] |
| （仓内自有，无外部对应） | — | — | layer、line_ref、graph_ref、consumers、frequency、net_zero_note |

### §2.2 分级表（闸门判定依据）

| 级 | 字段 | 判定 |
|----|------|------|
| **A 入库必填**（缺一即拒） | q_id（闸门机生）、title、layer、data_sources、exam_plan、consumers、frequency、pit_proof、status、provenance、net_zero_note | 五要素支撑字段全在 A 级 [纪要§2]；provenance 对标 OSF 注册时戳；net_zero_note 是仓内净零铁律的载体 |
| **B 条件必填**（触发条件出现才必填） | line_ref（layer=L1/L3 或声明依赖源线时）、graph_ref（声明依赖图谱时）、parent_id（声明为拆出子问时）、merged_into（status=合并时） | 非该层问题不强填，避免空值噪音 |
| **C 运行期可后补**（入库时留空合法） | chain_refs、evidence_refs、last_exam | 对标"发布/结果"阶段字段：入库时问题尚未开考，自然为空；后补动作由考试回填闭环（姊妹件）负责 |

## §3 五要素机检规则 [纪要§2]

| # | 要素 | 机械判据（可判定部分） | 不可机判部分→人工初审 |
|----|------|------|------|
| 1 | 能被数据回答 | data_sources 非空 **且** 每项在数据源登记中可命中（命中真源=W4 源线谱；未建成前的降级判据=非空+格式合法，显式降级并在审计事件标 `degraded_check`） | "该源数据是否真能回答该问题"是语义判断→Max 复审抽检 |
| 2 | 能被考试证伪 | exam_plan 同时含**判定字段**（判定方法/比较对象）与**阈值字段**（数值阈值或判别规则）非空（结构存在性可机判，对齐仓内"verdict 非空"式检查） | "阈值是否合理、是否真可证伪"→Max 复审必审项 |
| 3 | 有明确消费方 | consumers 非空 **且** 每项命中消费方登记（真源=functional_domain_registry 单一真源；四件套消费清单为 W2 立项产物，建成前不参与判定；未命中→转人工） | "消费方是否真会消费"→Max 复审；A 因子虚标列入红蓝抽卷固定项 |
| 4 | 有更新频率 | frequency ∈ 枚举 {realtime, daily, weekly, monthly, quarterly, event_driven, static}（枚举机判）；event_driven 须事件源引用非空（A 级机检，对齐《考试回填闭环设计》§3.1 拒收判据） | "枚举选得对不对"→抽检 |
| 5 | PIT 安全 | pit_proof 非空 **且** 其引用的每个 data_source 声明含可用时戳列（as-of/公告日；结构可机判）；W4 源线谱未建成期降级判据=非空+声明载体格式合法，显式标 `degraded_check` | "是否真无前视"是领域判断→Max 复审必审项，禁伪装为机检 |

降级口径声明：`degraded_check` 降级检查计入"五要素机检 100%"验收但必留降级痕，该验收口径随 W2 裁定批呈 Owner 确认。

3.6 时间分层环检测（[纪要§8.2] 铁律的入库侧落点）：入库时校验 exam_plan/data_sources 引用不构成"同一时戳自循环"（引用图 DFS 无环）——结构可机判，归要素 5 的机检部分。

## §4 查重

1. 判重范围：库内全量（含 62 条 v1 骨架 [纪要§6]）。
2. 机械方法（复用 `ai_layer/intake/dedup.py` 既有件，禁重写）：①先查精确指纹 content_fingerprint（sha 级）→秒判重复；②title 归一化（NFKC+去标点+小写+全半角归一）后 simhash64；③约束条件：仅与**同 layer** 候选比对，line_ref 相同者距离阈值收紧一档。
3. 阈值分流（64bit simhash 汉明距离，建议值 **[待裁]**，推荐按仓内 dedup 既有阈值沿用）：

| 距离 | 判定 | 处置 |
|----|------|------|
| 精确指纹命中或 d≤3 | 高相似 | 拒（错误码 `dup_high_similarity`，附 duplicate_of 指向库内 q_id；提交方可改走 parent_id 拆问或 merged_into 合并流程） |
| 4≤d≤10 | 中相似 | 转人工（进 Max 复审队列；每会话日限 20 条，防零成本灌水 Max 队列，超限拒并留 dedup_hit 痕） |
| d>10 | 低相似 | 过（仅留 dedup 证据 `as_evidence` 痕） |

4. **62 条 v1 的特殊处置（显式登记）**：v1 仅有 ID 骨架无逐条全文 [纪要§6]，全文级查重客观不可行。骨架期降级判据=ID 挂载核对（新问题声明归属 M/U/线/S/D/E/G 组时校验 parent_id 挂载合法）；W6 展开后逐条补全文查重（复考机制回补）。此为降级检查，审计事件必标 `degraded_check`。

## §5 问题洪水防线

### §5.1 限流（建议值 **[待裁]**）

| 参数 | 建议值 | 依据 |
|----|------|------|
| 单批提交上限 | 12 条 | 对齐 Max 复审单批次注意力窗口（约半小时审一批），超批拆批 |
| 每会话每日入库上限 | 40 条 | 验收硬数字 250-400 条 [纪要§9] ÷ W6 挖干窗口约 5-8 施工日 ≈ 31-80 条/日；单会话 40 仅覆盖目标下限（250 条需 ≥7 日），中位及以上靠多会话并发或 §5.4 初始建库批量通道 |
| 全库每日入库上限 | 120 条 | 3 会话并发 × 40；覆盖 400 条目标的峰值冲刺，防单日灌库冲垮复审产能 |
| 盲册入册 | 不占入库配额，单列上限 20 条/会话/日 | 盲册是养问区不是资产库，防其变相成为侧门 |

### §5.2 质量门槛（过闸前置，全机检）

五要素机检全过（§3）+ 查重过（§4）+ A 级字段全非空（§2.2）+ 时间分层环检测过（§3.6）。任一不过即不入正库，符合条件者转盲册（§6）。

### §5.3 两级定案审（Owner 例外通道单列；与《管理办法总册》§1 行 2 对表一致）

| 级 | 审者 | 审什么 | 通过判据 | 超时处置 |
|----|------|--------|---------|---------|
| 定案一级：机械层（自动 registered） | 入库闸 API 内置 | §5.2 全部机检+限流+查重低相似 | 机检五查全过 **且** 查重低相似的纯机械层提交→**自动 registered**，无人工卡点；Max 周抽检兜底（总册 §1 行 2），异议走降级复核 | 即时，无超时 |
| 定案二级：语义层（Max 前置复审后 registered） | Max | 含不可机检语义层的提交：五要素真值（重点要素 2/5 不可机判部分）、一问一考拆并是否到位 [纪要§3]、B 级字段触发是否漏填；及查重中相似转人工件 | 逐条 pass/fail/转盲册，复审过即 registered；**fail-closed 不自动放行仅适用于本层** | **[待裁]** 推荐 72h 未审→批次顺延排入《未答看板设计》§2.2 Max 队列④超时顺延批，不自动放行（fail-closed） |
| Owner 例外（非审级，例外通道） | Owner | 仅例外事项：拒录申诉、跨层翻案、限流豁免、净删相关 [纪要§10] | 裁定#NNN 登记册原子留痕 | 超时维持原判（拒绝不自动翻案，fail-closed），例外通道不设自动放行 |

### §5.4 初始建库批量通道（仅限本战役 W6 初始入库使用，W6 结束即关）

- 豁免范围：常规限流（单批 12/会话日 40/全库日 120）对本通道豁免；模板候选同样豁免——候选≠已入库问题，**限流只计 registered 动作**（draft 候选与批次展开不占配额，晋级/入库才计）。
- 通道参数：总量 **≤400**（验收硬数字上沿 [纪要§9]）；单插入批 **≤100 行**；**须 Max 会签**；staging 暂存 **TTL 7 天**（常规 24h TTL 容不下批量重放窗口）。
- 边界：本通道仅本战役有效，不入常驻限流参数表；会签与批次留痕走 §7.3 审计事件。

## §6 盲册区设计

1. 入册条件：值得养但不合格=五要素机检有缺口 **或** 二审判"方向对但需拆并/换源"，且查重非高相似（高相似直接拒，盲册不收废品）。
2. 盲册字段：在 18 字段底稿之上**显式记缺口**——`blind_gaps`（缺失要素代码列表，如 `["exam_plan_no_threshold","data_sources_empty"]`）+ `blind_review_due`（下次复查日）。两字段为新增提案，见 §10 **[待 W1 评审]**。
3. 晋级条件（补齐即转正走正常入库）：缺口对应机检全过 + 查重过 + Max 复审核准；晋级=状态迁移留痕，不重发 q_id；晋级即 registered 动作，**计入常规限流**（防盲册囤积绕道，与 §5.4"限流只计 registered 动作"同口径）。
4. 复查周期：建议 **30 天 [待裁]**——战役 W1-W8 共约 8 周，30 天保证每条盲册问题在战役内至少被复查一次；复查由未答看板出清单触发（落地章节=《未答看板设计》§1 盲册复查区/§2.1 盲册复查清单）。
5. 退役出册：连续两次复查未补齐 **且** consumers 空 → 退役，q_id 入墓碑不复用 [纪要§7]，留退役原因（对标 OSF withdrawal stub）。
6. **盲册=status 体系特例，不建独立区**（推荐，**[待裁]**）。理由：①独立区=第二张表+第二套生命周期，违反净零铁律与 RULE-SSOT 单真源；②晋级/退役天然是状态迁移，复用 provenance 留痕与审计零成本；③q_id 墓碑制要求单 ID 空间，双区会造 ID 分叉。代价=需给 status 扩一个 `blinded` 枚举（§10 提案，不动字段结构）。

## §7 写入 API 契约（W2 按此实现）

### §7.1 校验顺序（失败即短路返回）

claim 鉴权（多会话 claim 制）→ 限流检查 → A 级字段完备性 → 枚举合法（layer/frequency/status）→ 五要素机检 → 时间分层环检测 → 查重 → 净零声明核对（net_zero_note 非空）→ q_id 机生（PG sequence 原子分配）→ PG 写入（同实例事务）→ YAML 机生快照（safe_write_text CAS）→ 审计落账 → ROOR 计数刷新。

### §7.2 错误码（对齐仓内风格：`ai_layer/intake/gate.py` 的机读 snake_case reject_reasons）

| 阶段 | 错误码（示例全集） |
|----|----|
| 鉴权/限流 | `claim_missing`、`rate_limit_session_exceeded`、`batch_limit_exceeded` |
| 字段 | `field_missing:<f>`、`layer_invalid`、`frequency_not_in_enum`、`status_invalid` |
| 五要素 | `data_sources_empty`、`data_source_unresolvable:<id>`、`exam_plan_no_threshold`、`consumer_unresolvable`、`pit_proof_missing`、`pit_timestamp_col_missing`、`time_layer_cycle` |
| 查重 | `dup_exact_fingerprint`、`dup_high_similarity`、`dup_pending_manual` |
| 净零/系统 | `net_zero_note_missing`、`qid_alloc_failed`、`pg_write_failed`、`snapshot_cas_conflict` |

### §7.3 审计事件清单（词表 SSOT=《管理办法总册》§2.1；风格对齐 `write_lookup_audit_log` 的 JSONL 留痕 + PG 表双写）

本闸九类事件全部映射到总册 §2.1 全族 SSOT 词表（intake 族+blind 族），本件不另立第二套枚举：

| 本闸事件 | 词表族 | 说明 |
|----|----|----|
| intake_submit / intake_reject / intake_rate_limited / intake_override / dedup_hit / degraded_check | intake 族 | intake_reject 含 reject_reasons 全集与 primary_reason；intake_override=Owner 例外必带裁定号；dedup_hit 附 duplicate_of；degraded_check=降级检查显式声明 |
| intake_blind_park / blind_promote / blind_retire | blind 族 | 盲册入册/晋级/退役三态 |

落点：PG 审计表（DDL-as-Code 一并建）+ `.runtime` 下 JSONL 镜像（会话维度，仿 lookup_audit 布局）。

### §7.4 状态流转端点（registered→mining→in_exam 执行口；权项=《管理办法总册》§1 行 10/11）

`POST /questions/{q_id}/transition {to_status}`——本端点辖前半段机械流转（registered→mining 开工 / mining→in_exam 开考）；in_exam 之后流转归《考试回填闭环设计》§1.5。校验链（顺序短路）：①认领鉴权（claimed_by==请求会话，Max/Owner 可越过）→②目标态合法（按状态机合法边）→③审计事件（§7.3 词表落账）。

## §8 外部锚点对标 [纪要§5]

| 机制 | AEA 注册中心 | OSF 预注册 | 本设计取舍 |
|----|----|----|----|
| 进门闸 | 自助登记+注册管理员轻审核；Data Editor 逐项核查清单（发表前验证报告） | 零门槛自服：draft→register 即时生效，无 curration | **取 AEA 的 Data Editor 式事前核查**（=五要素机检+Max 复审）；**舍 OSF 零门槛**——库内是受治理资产，无防线即洪水 |
| 不可变与版本 | 原注册不可变，amendment 版本链留痕 | register=不可变时戳快照+DOI；new version 保留原件 | **取 OSF 不可变快照**→YAML 机生快照+CAS；修改=新版本留痕不覆写 |
| PIT 证明 | 结果 embargo（分析前封存） | **先注册后分析的时戳=无前视证明** | **取 OSF 时戳先行逻辑**作为 pit_proof 的证明范式；取 AEA embargo 思想→未过审问题对消费者不可见 |
| 撤回/退役 | withdrawal 留原因不删记录 | withdraw 留 stub | **全取**→q_id 墓碑不复用 + 盲册退役留因（[纪要§7] 已定，外部先例佐证） |
| 唯一 ID | AEARCTR-* 登记 ID | DOI+GUID | 已有定案 PQ-NNNN [纪要§7]，不另采 |
| 模板 | 登记表单固定 schema | 模板库（Standard/ASPredicted 等） | 模板生成器（姊妹件）职责，本文仅引用不展开 |

## §9 本件盲点自查

| 维度 | 表态 |
|----|----|
| 权限 | 有办法：claim 制鉴权+Owner 例外仅 Owner 门位 [纪要§10]；W2 API 逐会话校验 sid |
| 审计 | 有办法：§7.3 全事件清单，PG+JSONL 双写，拒因机读 |
| 并发 | 有办法：q_id 走 PG sequence 原子分配；批量提交走 claim；快照走 safe_write_text CAS |
| 质量 | 有办法：五要素机检 100% 硬数字 [纪要§9]；机检不可判部分显式交 Max 复审，无伪装（§3） |
| 容量 | 显式登记盲点待裁：与 depgraph 同实例共享 PG 容量，未做容量评估与增长预估，待 W2 施工前补容量方案 |
| 生命周期 | 有办法：status 状态机+盲册晋级/退役闭环（§6）；复考周期随未答看板姊妹件定 |
| 退役 | 有办法：q_id 墓碑不复用 [纪要§7]+退役留因（OSF stub 先例） |
| 冲突 | 有办法：双会话同题并发提交→先到先得，后到被查重拒并附 duplicate_of；跨会话争议走 Owner 例外+裁定登记 |
| 对账 | 有办法：YAML 快照幂等机生，再生成即全量对账（gen_intake_ref_snapshots 先例） |
| 升级 | 有办法：schema 演进只走 §10 提案+DDL-as-Code 增量迁移；枚举扩展向后兼容 |
| 降级 | 显式登记盲点待裁：PG 不可用时闸门 fail-closed（拒收，禁降级直写 YAML——快照只读禁手写）；灾备写入通道是否需要，留 Owner 裁 |

## §10 schema 增补提案（**待 W1 评审**，禁直改 18 字段底稿 [纪要§7]）

| # | 提案字段/变更 | 类型 | 提案理由 | 状态 |
|----|----|----|----|----|
| 1 | status 枚举扩展：新增 `blinded` | 枚举值 | 盲册=status 特例（§6.6），不动字段结构 | 待 W1 评审 |
| 2 | `blind_gaps` | json | 盲册缺失要素代码列表（§6.2），晋级判定的机读依据 | 待 W1 评审 |
| 3 | `blind_review_due` | date | 盲册复查到期日（§6.4），未答看板出复查清单的驱动字段 | 待 W1 评审 |
| 4 | `intake_batch_id` | text | 限流与审计的批次键（§5.1/§7.3） | 待 W1 评审 |

> 全文完。Owner 未定案处均标 [待裁] 并附推荐项；本文随定桩战役归档即完成。
