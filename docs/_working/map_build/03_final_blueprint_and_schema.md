---
ttl: task_bound
completes_when: 六图全部按本件 schema 定稿落地且 align_all 三节判硬 0，本件退役转归档
title: 六图终局全貌与统一字段规范（总包裁定 v1）
owner: st-mapbuild-20260924（总包）
---

# 六图终局全貌 + 统一字段规范（v1 裁定）

> 本件回答两件事：**这六张图建成后长什么样**，以及**字段该是什么**。
> 立论依据：宪章 §8.2 一域一图与四道门、D38 新图必挂总线、TDM 节点规范 v1.5（layering policy §2.2）、
> `config/trading_decision_map.yaml` 文件头 INV-1 与 confidence 语义、`skeleton_mining_policy.md` §5/§6。
> 触发本裁定的三条实测缺陷：①三图 `module_id` 全空＝D38 总线未挂 ②三图各造字段名（`mech_note_zh`/`semantics_zh`/`clock_semantics_zh`）
> ③图12 `confidence: verified` 25/26 与其挖矿态（✅5/🔨12/⬜1）口径不一致。

## §1 裁定一：字段分三层，**同语义必同名**

三张图自造字段不是错，**各造一名才是错**。定三层：

### L0 通用层（六图必用同名，缺字段＝校验器判红）

| 字段 | 必填 | 语义 | 备注 |
|---|---|---|---|
| `map_id`/`schema_version`/`name_zh`/`effective_from`/`markets` | 顶层必填 | 图元数据 | `effective_from` 取 PIT 生效日，禁 `datetime.now()` |
| `laws` / `boundary` | 顶层必填 | 全图铁律 / 明确不做边界 | 防手痒，图9 先例 |
| `node_id` | 必填 | 图内稳定编号（D11-/DSC-/D13-/D14-/D15-） | 骨架一经定稿即契约 |
| `name_zh` | 必填 | 环节名 | |
| `stage`/`segment`/`lane`/`state` | 四选一必填 | 图内分组轴 | 图11=lane 三车道，图12/13=segment，图14=stage，图15=state |
| `node_type` | 必填 | `stage`/`lane`/`gap`/`aggregation`/`state` | gap 与聚合点是合法节点，但须带 `red_reason` |
| `decision_question` | 必填 | 这一格回答什么问题 | ≤120 字（图9 判据） |
| `note_zh` | 必填 | **机制/语义注解（统一用这名）** | 废止 `mech_note_zh`/`semantics_zh`/`clock_semantics_zh` 三个别名 |
| `module_id` / `module_ref` | 见 §2 | MOD-* 总线号 / 实现代码路径 | |
| `source_anchors` | 必填 | 真源锚（`file:line` 或可复跑命令） | 至少 1 条 |
| `doc_refs` | 可空 | 政策/spec 指针 | 废止 `design_refs` 与 `doc_ref` 并存，留 `doc_refs` |
| `data_refs` / `store_refs` / `runtime_refs` | 按需 | 数据资产 / 存储载体 / 运行时对象 | 只放标识符，禁复制条目正文（INV-1） |
| `evidence` | `verified` 时必填 | 支撑该断言的复跑证据 | 必含命令或 file:line |
| `confidence` + `verified_scope` | 必填 | 见 §3 | |
| `build_status` | 必填 | `built`/`partial`/`pending` | `built` 必有 `module_ref` |

### L1 纵轴流程专有层（六图共用同一套名，各图按域取用）

| 字段 | 值域 | 用途 |
|---|---|---|
| `slot_source` | `schedule`/`schtasks`/`event`/`dloop_stage`/`manual`/`none` | 时点从哪来；声称 schedule/schtasks 者须在真源查到（在册实存校验） |
| `slot_refs`/`schtasks_refs` | 列表 | 具体槽名/任务名 |
| `cadence_zh` | 文本 | 声明节拍 vs 实测节拍（图13 用 `declared`/`observed` 双子键） |
| `wiring_status` | `wired`/`unwired_slot_hollow`/`unwired_no_caller`/`partial` | **"槽挂着但没跑"的表达位**——三图统一走这一个字段 |
| `downstream_action` | `auto_remediate`/`alert_only`/`detect_only`/`none` | 区分"谁看着"与"谁动手"；配 `failure_visibility_zh` 说检出后痕迹去哪 |
| `fallback` | 文本/null | 降级路径（统一用这名；废止 `miss_fallback_zh`/`degradation`/`silent_failover` 三名） |
| `invalidation` | 文本/null | 什么条件下本节点结论作废 |
| `ready_gate` | bool + `no_ready_gate_reason_zh` | 就绪门是否成节点（图13 D13-09 建议升格） |
| `tdm_refs` | 列表 | 与 TDM 的交叉引用；**本层禁出现 `judgment_basis`/`factor_refs`/`strategy_refs`**（决策判据归 TDM，违者判红＝越域挂载） |
| `gap_refs`/`red_reason` | 列表/枚举 | 缺口显性化；`terminal`/`unwired`/`broken_supply`/`ghost_ref` |

### L2 图专属层（各图自留，但须在图头 `ssot_note_zh` 声明字段清单）
- 图11：`exit_codes`（提交门退出码全谱）、`gate_cluster`、`deadletter_class`
- 图12：`task_family`（271 任务归簇）、`freshness_evidence`（max(date) + 滞后交易日数）
- 图13：`dloop_stages`（16 段清单）、`machine_facts`（空转槽/落空对象台账）
- 图14：`verifiability`（auto/semi/manual）、`anchor_kind`
- 图15：`from_state`/`to_state`、`edge_kind`（`permitted`/`forbidden`）

## §2 裁定二：`module_id` 必挂，来源唯一，禁自造

1. **凡 `module_ref` 非空 ⇒ `module_id` 必填**，值取 depgraph 在册 `MOD-*`（经 `sync_panorama_module.py` / depgraph 查得）。
2. 无实现代码的节点（纯结构、终点聚合、gap 节点）⇒ `module_id: null` **且 `red_reason` 必填**（TDM `red_reason: terminal` 现例）。
3. 校验器加一条 **CV-BUS**：`module_ref 非空而 module_id 空`、或 `module_id` 非 `MOD-*` 形态 ⇒ error；depgraph 存在性走 DB，**不可达时降 warn**（学图8/图9 PG fail-open 先例，别让环境异常打死无辜提交）。
4. 挂轴 §3 三行的口径同步改准：对齐键 = **`module_id`（真挂总线，两跳互通）+ `node_id`（图内轴）**；在 CV-BUS 落地前，那三行不得声称"挂 module_id"（我此前写谎了一句，本条即纠）。

## §3 裁定三：`confidence` 拆两轴，杜绝"口径混用即粉饰"

单值 `verified/proposed/untested` 不足以表达"结构对≠在产数"。改为**两字段正交**：

| `confidence` | `verified_scope` | 允许的挖矿态对应 | 语义 |
|---|---|---|---|
| `verified` | `production` | ✅（三证齐：产数新鲜+任务在策+执行留痕） | 该环节**真在产/真在跑**，且 evidence 可复跑 |
| `verified` | `structure` | 🔨 或 ⬜ 的结构性事实 | 仅"这条边/这个文件/这个槽名存在"已核 |
| `proposed` | null | 🔨 待验假设 | 主观或二手，未复跑 |
| `untested` | null | ⬜ | 空壳占位 |

**硬判据（进校验器）**：`verified_scope: production` 而该节点对应的挖矿状态标不是 ✅ ⇒ error；反之 `verified/production` 必须带 `freshness_evidence`（图12）或 `exec_evidence`（图11/13）。
⇒ 按此重标后图12 现状应是 **5 个 production + 20 个 structure**，不是现在的 25 个 verified 混成一坨。

## §4 六图终局全貌（验收即以此为准）

| 图 | 终局形态 | 节点规模 | 必备 L1 字段 | 专属层 | 终局验收判据 | 还差的活 |
|---|---|---|---|---|---|---|
| **图11 交付流水线** | 三车道 DAG（会话/提交/死信） | 28 | `wiring_status`、`exit_codes`、`runtime_refs` | 退出码全谱矩阵 | ①28 格全挂 `module_id` ②死分支码 4 与回滚旗失效两条以 gap 节点显性化 ③gate 子检查在 MAP-ALIGNMENT 内可红可绿 | CV-BUS 补挂；S07「pre-merge 门整体短路」加注 |
| **图12 数据供给链** | 五段链 + 终点缺口显性化 | **21**（现 18→扩 3，待扩） | `slot_source`、`data_refs`、`freshness_evidence`、`downstream_action` | 任务归簇表 | ①骨架扩行后图本体再生 ②`terminal_gap` 必须真指向 gap 节点（现满足）③5 处"消费方在等未产表"+1 处幽灵引用全部成 `gap_refs` | **未封矿**：消费端反查已跑但增量非 0，需扩行+重宣封顶 |
| **图13 交易日循环** | 一日四段时序脊 | 44 | `slot_source`、`cadence_zh`、`ready_gate`、`invalidation`、`tdm_refs` | dloop 16 段 + machine_facts | ①2 空转槽与 16 落空对象全在 `wiring_status` 里可查 ②无一条 `judgment_basis`（越域即红）③D13-09 就绪门升为一等节点 | `tdm_refs` 填充 <1/3 须补；外部对标表A 7 条逐条落字段 |
| **图14 AI施工升级流** | 15→**17** Step 段闭环（含回边） | ≥17 | `verifiability`、`anchor_kind`、`fallback` | 步骤锚登记面 | ①步骤锚校验器上线且能红 ②9 条"文档说有实则没有"以 gap 节点入图 ③政策内嵌机读锚块为真源、图为其派生 | **未施工**：前置校验器先立；39 件幽灵脚本引用面待清 |
| **图15 策略卡生命周期** | **状态机**（状态+迁移+禁止边三类节点/边） | 状态 N + 迁移 M + 禁止边 K | `edge_kind: forbidden` 必可枚举 | 卡状态登记面 | ①登记面唯一宿主选定（扩 `experiment_registry` 优先，禁第二真源）②六处分裂的差值可被校验器判红 ③SEALED 就地复活＝必红 | **未施工**：规格两处判据缺陷（CV-08 误伤 36 张、CV-06 抓不到唯一复活链）先回炉 |
| **图16 治理立法流** | **不建图**（本役终态即合格态） | — | — | — | 三项微创落地即闭环：①取号器（防今晚 6 起同类撞号）②词表/entry_schema 回写 ③ROOR 补 1 条 | 重开触发条件已登记在册（出现流程位置字段即重议） |

## §5 六图共同的终局判据（一张图算"完成"的充要条件）

1. **结构面**：validate_<map> PASS + 对抗测试含**能红**用例（每图 ≥14 例，含伪造/断链/越域/INV-1/冒充 verified 五类）。
2. **总线面**：CV-BUS 硬过（所有有代码的节点挂 `module_id`），`align_all` 对应节判硬 0。
3. **口径面**：每节点 `confidence` + `verified_scope` 双字段齐，且 production 数 **＝** 该图 ✅ 数（不多不少，少了算欠、多了算谎）。
4. **落地面**：五件同袋（图 YAML + 生成器 + 校验器 + gate 子检查 + 两份测试）+ 挂轴 §3 行 + `align_all` 消费方 + token/翻译/裁定三册原子。
5. **诚实面**：`gap`/`red_reason` 覆盖所有已知不可证项（终点不可证、未接线、幽灵引用、断供静默用旧值），**不许用删判据或降状态的方式让图变干净**。
