---
ttl: task_bound
title: L7 传承段——回流闭环 真源设计稿 v1
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L7 传承段真源设计稿：传承库（经验结构化回流，闭环的关键边）

> **一句话**：把 L6 切换终局、工单关单、红蓝发现、casebook 归并沉淀为**传承库**（PG 机读真源：
> 精英档案/判据档案/缺陷模式三类条目统一登记），机检喂回 L1 搜索先验、L2 查重基线与组合素材、
> L4 判据先验防重复考古；防近亲繁殖配比约束保证回流只调排序不缩搜索面；遗忘机制保证库只降级
> 压缩不无界膨胀。主文档锚点：ai_layer_vision_and_roadmap_v1.md §三 3.5（缺陷三字段/关单四闸/
> 业务层互喂首案）+ README.md §1 L7 行。施工另走 construction_workflow_policy。

---

## 一、六向寻路台账表

| 向 | 内部发现（真实路径） | 外部发现（URL/发布方/年份） | 判定 |
|----|---------------------|---------------------------|------|
| ①上游（谁喂 L7） | `L6_ab_switch/DESIGN.md` §③（L6→L7 契约已声明：{promotion_record, tombstone_entry, 判据档案, 回切历史}，事件名待定）；`L4_compare/DESIGN.md` §③（`comparison_archived_due` 已定名+C8 施工项）；主文档 §三 3.5（关单四闸=own-scope/gate 绿/回归绿/独立复核；缺陷三字段机检匹配命中带配方派工；互喂首案=2026-09-17 pathspec bug）；README.md §1.6 迁移清单②（事故案例库→L7 互喂）；`OBJ_R_rules_standards/DESIGN.md` §⑤（casebook 流程末步"回写 L7 传承"，casebook.md 未落地、首案内嵌）；`docs/01_policies_and_standards/sop/review_sop/defect_pattern_checklist.md`（**人读版缺陷模式库已有 14 条**：模式/历史案例/审查问句/轴+入册退役纪律）；`src/zephyr/autonomy_core/skills/skill_postmortem.py`（MOD-INF-019 追问到底归因器：输出根因+纠正+预防）；`src/zephyr/feedback_loop/evolution/failure_replay.py`（R77 自认"FLE forgets failure patterns; repeats same mistakes"=本段立项内证）；memory 目录 MEMORY.md（Owner 人读坑集，只读） | 上游全内部；无需外查（边界留痕非查无） | signal |
| ②下游（谁吃 L7） | `L1_perceive/DESIGN.md` §2.3 任务单 `trigger='l7_prior'`+`priority` 字段已预留"挂起默认 1.0"、§三 L7 行（vein priority 权重+排除词表，**声明态，解锁条件=本稿**，施工项 9 挂起）；`L2_intake_library/DESIGN.md` §2.3 比对面 5（`ref_family='L7'` 缺省跳过已预留）+§三（`dedup_query` 只读服务+`intake_heritage_baseline` 事件已声明）；主文档 §3.5（派工命中缺陷签名带配方）；`defect_pattern_checklist.md` 消费端=深度审查材料包（deep_review_policy §3 已挂接） | 下游全内部；已查无必要 | signal |
| ③算法机制 | 在档复用：DGM 代理档案库 archive 支持从任意祖先分支（V0-R3，arXiv 2505.22954）；MAP-Elites 精英档案防进化遗忘（V2-R2，arXiv 1504.04909）；AlphaEvolve evolutionary database（V0-R2，arXiv 2506.13131）；PDCA Act=改善不写回标准等于没发生（V2 报告 §1 映射行） | **CBR 四 REs**=Aamodt & Plaza 1994《CBR: Foundational Issues...》AI Communications 7(1):39-59（retrieve/reuse/revise/retain；交叉验证=de Mantaras et al. 2005 Knowledge Engineering Review, iiia.csic.es/~mantaras/RRRR.pdf + CEUR-WS 2019 综述；**纠正常见误引 Aamodt & Nygård**）；**案例库遗忘**=Smyth & Keane 1995《Remembering To Forget: A Competence-Preserving Case Deletion Policy》IJCAI-95 pp.377-382（coverage/reachability 竞争力模型，pivotal/spanning/auxiliary 三分、优先删 auxiliary；交叉验证=ijcai.org/proceedings/1995-1 + Wilson & Leake 2001 维护综述 cse.hkust.edu.hk/~qyang/Docs/2001/maintaincbr.pdf + AIJ 2016 case-base editing）；**经验回放优先级**=Schaul et al. 2016 Prioritized Experience Replay arXiv 1511.05952（TD 误差定优先+recency 互补；交叉验证=MathWorks rlPrioritizedReplayMemory 文档+MDPI recency 论文）；**防早熟收敛**=Lehman & Stanley 2011《Abandoning Objectives: Novelty Search》Evolutionary Computation 19(2):189-223（纯目标导向搜索早熟，novelty/行为多样性是抗衡轴，QD/MAP-Elites 谱系源头；交叉验证=pubmed.ncbi.nlm.nih.gov/20868264 + QD 教程 rl-vs.github.io）；**关单复盘三字段业界对应**=Google SRE blameless postmortem（SRE Book Ch.15 sre.google/sre-book/postmortem-culture/ + SRE Workbook Ch.5 sre.google/workbook/postmortem-culture/：impact/root causes/action items 且 action item 必须被跟踪落实）——五脉各自 ≥2 独立来源，交叉验证闸通过 | signal |
| ④后端 | `src/zephyr/infrastructure/database_service.py`（get_depgraph_conn=PG 唯一通道，禁裸连接）；`scripts/industry_graph/apply_industry_graph_ddl.py`+L2 施工项 1（DDL 登记器幂等模式）；`src/zephyr/strategy_pipeline/pipeline_events.py`（JSONL journal+轻/重 kind+KillSwitch 探针+幂等 marker，L2/L4 已声明对齐）；`src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py`（GateSpec 签名——关单机检 gate 立案走 OBJ_R 流水线的落点）；`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（判据留痕传统真源，#20-D 编号铁律）；L2 T4 `ai_intake_ref_snapshot`（ref_family='L7' 行的落点表，写入权划分见 §2.6） | 开源无需引入（传承库=薄登记层；CBR/竞争力模型自研 <200 行量级） | signal |
| ⑤前端 | `src/zephyr/frontend/dashboard/` OpsAlertFeed→`GET /api/ops-notifications`（通知板先例，坑集月报出口）；`web/features/reglib/reg-engine.js`（注册表浏览面板先例） | 同类呈现=库浏览面板惯例，内部先例已足；已查无必要 | signal（登记不施工） |
| ⑥数据字段 | L6 switch_registry 字段（promotion_record/tombstone/criteria_yaml_ref+criteria_hash/state_history）；L4 `ai_comparison_experiment` 字段（experiment_id/criteria_yaml/criteria_hash/verdict/evidence_ref）；OBJ_R casebook schema（case_id/root_cause/defect_pattern 受控词表/状态）；checklist 14 条字段结构（模式/案例锚点/审查问句/轴）；L2 T1 域字典 6 域（含工具域，红蓝 R1-B2 同步增补）+机制族 8 族词表；L2 T4 字段口径（ref_key/text_norm/simhash/refreshed_at）；任务书 schema 附录 A（pre_rulings 判据预注册） | 字段行业口径（postmortem: impact/root cause/action items；case: problem/solution/outcome）已由③行引文覆盖；已查无必要 | signal |

**受阻记录**：0 次（5 轮外部搜索全部一次成功）。noise 轮：0。

---

## 二、真源设计

### 2.1 边界总裁定（D-L7-01：五方地盘图，防双头登记）

**传承库登记的对象=进化循环自身的稳定经验（考后/关单后/切换后，模式级）**。按"时间点+对象级"切五方：

| 资产 | 管什么 | 管不管什么 | 与 L7 的接口 |
|------|--------|-----------|-------------|
| **L2 候选卡**（ai_intake） | **进货**：外部生材料（论文/repo/机制），考前状态机 L0→intake，拒=rejected 阴性卡 | 不登记自家踩坑；不登记考后经验 | L7 是其第 5 比对面（T4 ref_family='L7'）+组合素材供方；**rejected 卡≠缺陷模式**（前者=外部材料不适合我们，后者=我们自己的坑），L7 不收"某论文被拒" |
| **OBJ_R casebook** | **个案与尺子线**：事故个案归因→阈值提案→修标→重放验证（case 级，治理立案流） | 不承载跨案稳定模式的全量机读登记 | 流程末步"回写 L7"=同 pattern 归并后**模式落 L7（机读真源）、casebook 留 case+pattern_norm 引用**；个案只登一次 |
| **defect_pattern_checklist**（14 条） | **深度审查消费面**：审查问句+轴标签，人读 policy 文件（治理域资产） | 不是模式真源（14 条是精选投影） | **增量单向**：新模式先登记 L7（三字段），上 checklist 时引用 pattern_norm 并增补审查问句/轴（其特有字段）；checklist 不回灌 L7 |
| **ruling_registry** | 治理裁定留痕（制度语义） | 不管考卷与判优历史 | L7 判据档案条目 source_ref 可指 ruling_id；两库语义不同不并表 |
| **memory 目录**（Owner 人读坑集） | Owner 视角人读副本（项目外个人资产，无 schema 无 TTL） | 不作机检输入（库外文件不可机检）；L7 永不写入（硬边界） | 双轨不对称见 §2.7 |
| **OBJ_T 工具线** | 工具资产登记（工具注册/路由/配额/评测） | 不承载工具踩坑的机读登记——工具域坑集归 L7（H4 tool_id/scene 列+domain_id=工具域，红蓝 R1-B2） | **OBJ_T 只持只读视图**（读 V2 工具域缺陷条目），**写入权归 L7**（store.register() 唯一入口）——防双头登记；工具域词表已同步 L2 T1（六域） |

流向一句话：**L6/L4/工单/红蓝/casebook/checklist/memory/OBJ_T 工具坑集 → L7（只进一个真源）→ L1/L2/L4/L5（只从一个真源读；OBJ_T 持只读视图）**。

### 2.2 存储裁定（D-L7-02）

**裁定：PostgreSQL（depgraph 同实例）新 schema `ai_heritage`，全部读写经 `DatabaseService.get_depgraph_conn()`，禁裸连接。**

理由（逐条对红线，与 L2 §2.1 同构）：①duckdb 已废（database_service.py L37 在案）不复活；②ClickHouse 是行情 OLAP，登记条目是 OLTP 小行+状态机+UNIQUE，错配；③文件库会漂移（candidate_module_registry 并发覆写丢失史=病案），YAML 只放规则参数不放运行数据；④与 ai_intake 分 schema 而不并表——L2 是生食库（外部材料），L7 是经验库（自家沉淀），生熟之外再分"内外"，schema 级隔离各自独立演进；⑤时间戳一律 `TIMESTAMPTZ`（RULE-SCHEMA-TZ 同义执行）；⑥阈值/保留期数值类规则参数落 `config/heritage_policy.yaml`（对标 comparison_policy.yaml 先例：规则=YAML、运行数据=DB，RULE-SSOT 分界），改动走 OBJ_R 四步流水线。

### 2.3 传承库 schema（三类条目统一登记格式）

DDL 由幂等登记器 `scripts/ai_layer/apply_ai_heritage_ddl.py` 部署（照 apply_ai_intake_ddl.py 模式）。

**H1 `ai_heritage_entry` 条目主表**（三类共用——消费统计/查重指纹/遗忘状态必须跨类单点）

| 字段 | 类型 | 说明 |
|------|------|------|
| entry_id | TEXT PK | `HT-<yyyymmdd>-<NNN>`（UNIQUE 约束；kind 无关统一编号） |
| entry_kind | TEXT NOT NULL CHECK IN ('elite','criteria','defect') | 三类条目判别键 |
| title | TEXT NOT NULL | 一句话标题 |
| plain_zh | TEXT NOT NULL CHECK (length(plain_zh)>=10) | 大白话一句话（人读双轨基础，禁占位串；对齐 add_module_translation 精神） |
| domain_id | TEXT NOT NULL | 域标签，词表真源=L2 `ai_intake.ai_intake_domain`（只读引用，应用层校验，不建跨 schema FK） |
| source_kind | TEXT NOT NULL CHECK IN ('l6_switch','l4_experiment','work_order','redblue','casebook','checklist_seed','memory_digest','manual') | 来源通道 |
| source_ref | TEXT NOT NULL | 来源可溯锚点（switch_id/experiment_id/work_order_id/case_id/ruling_id/commit hash/DR-*/TP-*） |
| text_norm | TEXT NOT NULL | 归一化文本（title+核心字段拼接，simhash 输入） |
| simhash | BIT(64) NOT NULL | 指纹（自库防重登记 + 供 T4 快照；算法复用 L2 dedup.py 实现） |
| content_sha256 | CHAR(64) NOT NULL UNIQUE | 精确查重键（同文重复登记即拒） |
| status | TEXT NOT NULL DEFAULT 'active' CHECK IN ('active','archived','retired','compressed') | 遗忘状态机（§2.8）：只降级不物理删（删除红线三档） |
| hit_count | INT DEFAULT 0 | 被消费次数（dedup 命中/派工命中/先验引用；异步聚合回写——消费只记计数流水，月度体检窗 SUM 落库，裁定见 §2.4 红蓝 R1-B7——遗忘判据燃料，对齐 PER"被用才值得记"） |
| last_hit_at | TIMESTAMPTZ | 末次消费时间 |
| created_at / updated_at | TIMESTAMPTZ NOT NULL | |

索引：`(entry_kind, status)`、`(domain_id, status)`、`(simhash)`、`(last_hit_at)`。

**H2 `ai_heritage_elite` 精英档案扩展表**（胜者+判据+差异；1:1 FK entry_id）

| 字段 | 类型 | 说明 |
|------|------|------|
| entry_id | TEXT PK FK→H1 | |
| surface | TEXT NOT NULL CHECK IN ('code_module','gate_param','model','tool','rule') | 对象家族（对齐 L6 四家族+规则） |
| winner_ref / loser_ref | TEXT NOT NULL / TEXT | 胜者与败者的对象指针（module_id/策略 id/model_id/gate_id） |
| diff_summary | TEXT NOT NULL | **差异档案**：胜者与败者差在哪、为什么这一差赢了（≥30 字防占位） |
| evidence_ref | TEXT NOT NULL | 证据指针（experiment_id / SCR-C4 run 档案 / switch_id） |
| score_summary | JSONB | 分数摘要（双窗成绩/重放 Jaccard/双跑胜率等，考尺各异存 JSON） |
| mechanism_family | TEXT NOT NULL | 机制族（词表=L2 8 族；L1 富矿先验的格坐标） |
| gen | SMALLINT NOT NULL DEFAULT 1 | 代数 |
| parent_entry_id | TEXT FK→H1.entry_id | 祖先精英（DGM archive"从任意祖先分支"语义；NULL=开国代） |

**H3 `ai_heritage_criteria` 判据档案扩展表**（"当时为什么算它赢"）

| 字段 | 类型 | 说明 |
|------|------|------|
| entry_id | TEXT PK FK→H1 | |
| experiment_id | TEXT NOT NULL | L4 experiment 卡指针（criteria_yaml/criteria_hash 真源在那张卡，本表存快照+叙述，双真源防 L4 库重建后判据语境丢失） |
| criteria_hash | CHAR(64) NOT NULL | 冻结判据哈希（与 L4 卡一致性校验键） |
| venue | TEXT NOT NULL CHECK IN ('c4','replay','dual_run','tool_bench','other') | 考场 |
| verdict | TEXT NOT NULL | win/loss/tie/rejected_too_good |
| simhash | BIT(64) | 可空——仅 mechanism 族条目填（text_norm 派生指纹；comparison_prior_query 相似过滤轴，红蓝 R1-B4 补） |
| mechanism_family | TEXT | 可空——仅 mechanism 族条目填（词表=L2 8 族；comparison_prior_query 格过滤轴） |
| why_win | TEXT NOT NULL | **当时为什么算它赢**：判据口径+显著性结论+归因叙述（≥30 字；判据翻案后此字段仍是史实，不改写只标注） |
| still_valid | BOOL NOT NULL DEFAULT true | 判据现行有效性（判据翻案/考纲换版/修标重放否决时 L4 回写 false——防重复考古只查 true 行） |
| invalidated_by | TEXT | 翻案依据（ruling_id/experiment_id） |

**H4 `ai_heritage_defect` 缺陷模式扩展表**（主文档 §三 3.5 三字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| entry_id | TEXT PK FK→H1 | |
| root_cause | TEXT NOT NULL | **字段 1 根因**：追问到底的结构性原因（归因器=skill_postmortem MOD-INF-019 输出，人工复核后登记） |
| signature | TEXT NOT NULL | **字段 2 签名**：可机检的复发形态（可 grep 的代码形态/可正则的日志特征/可 simhash 的症状文本） |
| recipe | TEXT NOT NULL | **字段 3 配方**：修复配方+预防配方（命中带配方派工的供给端；固化进 gate 后写明 gate_id） |
| pattern_norm | TEXT NOT NULL UNIQUE | 受控词表 slug（checklist 模式名同源；如 `single_side_defense`——checklist #4"单侧防御"同型） |
| affected_surfaces | JSONB NOT NULL | 受影响面清单（模块/gate/注册表路径）——存活判定=遗忘判据（§2.8） |
| tool_id | TEXT | 涉事工具标识（工具域条目必填：工具名/CLI/MCP id；非工具域 NULL）——OBJ_T 工具坑集登记落点（红蓝 R1-B2 补） |
| scene | TEXT | 触发场景（工具域条目必填：调用形态/参数形态/环境约束；非工具域 NULL） |
| exclusion_keywords | JSONB DEFAULT '[]' | 排除词表贡献（供 L1 任务单 keyword_groups 过滤） |
| occurrence_count | INT DEFAULT 1 | 累计案发数（casebook 同 pattern 归并时累加，source_refs 追加） |
| first_seen / last_seen | TIMESTAMPTZ NOT NULL | 首末案发 |
| fused_into_gate | TEXT | 固化落点（gate_id/registry 条目；非空时消费端降级为"检查固化件是否被绕过"——对齐 checklist 退役纪律"已固化"） |

**视图**：V1 `ai_heritage_elites_active`（status='active' 精英，按 surface×mechanism_family——L2 组合素材/L5 祖先分支查询口）；V2 `ai_heritage_defect_hot`（active 且未 compressed 的缺陷模式——T4 快照源+派工签名匹配源）；V3 `ai_heritage_l1_prior`（domain_id×mechanism_family 格：active 精英数+近 90 天 hit 数→prior_factor∈[1.0,2.0] 与 rationale_refs——L1 富矿先验直接读）；V4 `ai_heritage_l1_exclusion`（active 缺陷的 exclusion_keywords 展开——排除词表直接读）；V5 `ai_heritage_kpi`（月度：新增/命中/降级/l7_prior 占比四数）。

### 2.4 回流接线：机检路径（条目→L1/L2/L4 全只读）

```
[写] L6/L4/关单/红蓝/casebook ──事件──▶ store.register() 过闸（2.5）──▶ ai_heritage.*
                                                                            │
[读·L1] V3 l1_prior ──priors.py 只读薄封装──▶ 任务单 priority 因子+trigger='l7_prior'       │
        V4 l1_exclusion ──同上──▶ keyword_groups 过滤（只滤词不灭矿脉）                     │
[读·L2] V2 defect_hot+V1 elites_active ──gen_heritage_dedup_snapshot.py──▶ L2 T4           │
        （ref_family='L7' 行，只写本 family；完发 intake_heritage_baseline 轻事件）          │
[读·L2] dedup_query（L2 侧服务）执行比对，命中只记计数流水（异步聚合，红蓝 R1-B7 裁定见下）        │
[读·L4] comparison_prior_query(simhash/mechanism_family) → H3 still_valid=true 行防重复考古 │
[读·L5] heritage_parents_query(surface, family) → V1 祖先精英（组合素材/分支起点）           │
```

- **L1 先验字段**：L1 §2.3 任务单 `trigger='l7_prior'`+`priority` 落地。`priors.py` 只做两件事：①按 domain×family 读 V3 得 prior_factor（富矿加权，见 §2.6 权力边界）；②读 V4 得排除词表。消费触发=每次开单时调用（纯只读，无事件依赖）；L1 施工项 9 随本稿解锁。
- **L2 查重基线**：T4 行写入权按 ref_family 划分——`gen_intake_ref_snapshots.py` 管 chart/indicator/algo_flow 三族，`gen_heritage_dedup_snapshot.py` 只写 `ref_family='L7'`（幂等重刷，refreshed_at 更新）。刷新时点=传承条目登记/降级后（`heritage_snapshot_dirty` 轻事件）+ 月度兜底。入快照面=V2 缺陷（已踩坑防再进）+V1 精英 top3（已有赢家防换皮进货）；L2 侧闸机检不变（五比对面全过才入库）。
- **L4 判据先验**：领考前 `comparison_prior_query` 查 H3（simhash+mechanism_family 过滤，still_valid=true）——同对象已考且判据未翻案=引用旧裁定，防重复考古（L4 §3 已声明本服务，本稿补数据面；H3 已补 simhash/mechanism_family 两列支撑本查询，红蓝 R1-B4）。
- **hit_count 回写裁定（红蓝 R1-B7）**：一律**异步聚合**——消费路径（dedup 命中/派工命中/先验引用）只写轻量计数流水，**月度体检窗一次性聚合回写 H1.hit_count/last_hit_at**（与 forget.py/坑集月报同节拍宿主）；消费路径同步回写=跨 schema 高频小事务写耦合，裁定为过度工程，禁止。

### 2.5 登记闸（写 H1 必须全过，store.register() 机检）

| 闸 | 机检规则 |
|----|---------|
| 来源可溯 | source_kind+source_ref 双非空；source_ref 格式校验（SW-*/EX-*/WO-*/CASE-*/HT-*/DR-*/TP-*；DR-*=OBJ_M 双跑记录、TP-*=OBJ_T 配对实验记录，与 L4 实验卡同构同通道，红蓝 R1-B3 补） |
| 类内完备 | elite：winner_ref+diff_summary≥30 字+evidence_ref；criteria：experiment_id+criteria_hash+why_win≥30 字；defect：三字段全非空且 recipe≠root_cause 复读（≥20 字差异校验） |
| 无案例不入册 | defect 条目必须 source_kind ∈ ('work_order','redblue','casebook','l6_switch')（对齐 checklist 入册纪律：教训带真实锚点，禁凭印象登记） |
| 自查重 | content_sha256 UNIQUE+simhash 全库汉明 ≤3 命中即拒（拒因 duplicate_of=既有 entry_id；同坑复发走 occurrence_count 累加不新登记） |
| 判据一致性 | criteria 条目 criteria_hash 与 L4 experiment 卡哈希比对，不一致=拒（防快照漂移） |
| plain_zh 非占位 | ≥10 字且非"待填/略" |

### 2.6 防近亲繁殖平衡规则（D-L7-03：回流不缩搜索面的四条配比约束）

业界依据：novelty search（Lehman & Stanley 2011——纯目标导向记忆会早熟收敛，多样性是抗衡轴）+ PER（Schaul 2016——回放权重再高也不删除经验池）。约束全部机检：

1. **L7 只调排序、永不碰配额**：prior_factor ∈ [1.0, 2.0] 只做加法（富矿加权）；**贫矿降级权完全留在 L2 KPI→L1 配额既有通道**（L1 §2.1 配额三闸），L7 无任何下调路径（防"传承记忆把贫矿判死"——贫矿判定的真源是入考率实数，不是历史印象）。配额真源=L1 源注册表，L7 零写权。
2. **l7_prior 触发单占比 ≤50%/日**：L1 任务单 journal 按 trigger 统计，超限=当日冻结 l7_prior 开单权+告警（外部节拍+内监保底 ≥50%——搜索面的一半永远留给"没有历史经验的地方"）。
3. **排除词表只滤词不灭矿脉**：V4 词表过滤 keyword_groups 时每单至少保留 1 组关键词（priors.py 机检）；矿脉封矿=结构判据（L1 §2.5.4：六向全查无+无未挖长尾），**L7 先验不参与封矿判定**。
4. **多样性保底体检**：月度体检核查 L2 行为格覆盖率（48 格 v0=6 域×8 族，含工具域，红蓝 R1-B2 后重计）——覆盖率 <60% 或连续 2 个月下降 → 全局 prior_factor 上限冻结 1.0（只留排除词表防换皮，停富矿加权）直到恢复。冻结状态写 V5 kpi 并进月报。

### 2.7 人读-机读双轨（D-L7-04：不对称双轨）

| 轨 | 载体 | 地位 | 流向 |
|----|------|------|------|
| 机读（强制） | ai_heritage schema（PG） | **唯一机检真源**：T4 快照/排除词表/派工签名/L4 先验全部只认它 | 登记走闸（§2.5），消费留痕（hit_count，异步聚合回写 §2.4/B7） |
| 人读（自愿） | memory 目录（Owner 坑集）+checklist（审查面）+月度 digest | 参考与消费面，不作机检输入 | 见下 |

- **机读→人读**：生成器 `gen_heritage_human_digest.py` 每月从 V2/V5 导出**坑集月报**（plain_zh 一句话+案例锚点+配方摘要），推通知板（OpsAlertFeed 先例）+落本目录 `digests/YYYY-MM.md`（生成器产出禁手工维护，宪法 §9.5）。会话**可自愿**引用月报补写 memory 目录（人读通道零强制——memory 是 Owner 个人资产，L7 永不写入，硬边界自守）。
- **人读→机读**：单向补登——checklist 14 条与 memory 坑集中未被收编的模式，由一次性迁移工单按 §2.5 登记闸补入 L7（checklist_seed/memory_digest 通道）；此后增量只走 L7→checklist 方向（§2.1 边界）。
- **不对称的本质**：机检链路的每一环必须可 SQL 可机检（库内），人读链路只为 Owner 体验服务（可散可乱可自愿）——两轨不互为真源，漂移无害。

### 2.8 遗忘机制（D-L7-05：库不能只进不出；只降级压缩、永不物理删）

裁定依据：Smyth & Keane 1995（删 auxiliary 保 pivotal/spanning——按"对系统竞争力的贡献"而非按年龄删）；本仓先例=墓碑制/L6 墓碑 2 体检窗/checklist"已固化退役"。**物理删除永远不自动执行**（删除红线三档：物理删除=Owner 门位）；遗忘=降 status+移出机检快照，全留痕。数值进 `config/heritage_policy.yaml`（首轮数据后按 OBJ_R 流水线修订）。

| 类 | 保留规则（active） | 降级触发（→archived） | 压缩触发（→compressed） |
|----|-------------------|----------------------|------------------------|
| **缺陷模式**（保留期最长——坑不因时间遗忘） | 受影响面存活即 active，不按时间遗忘；常驻 T4 快照+排除词表+派工签名 | affected_surfaces 全部退役/删除（模块删/gate 退役机检查得）→ retired 墓碑 | retired 且**连续 4 个季度零新案+零 hit** → compressed：移出 V2 快照与词表，月报年度册保留一行；复发（新案命中签名）→ 一键 un-retire 回 active |
| **精英档案**（随战局代谢） | 同格（surface×family）**保 top3**（对齐 L2 保优 3=格内候补）；被现役 champion/evidence 引用即保 | 格内跌出 top3，或对应 L6 对象进 tombstone 满 2 体检窗（L6 §②-D 同款）→ archived；archived 条目仍可被 heritage_parents_query 作祖先分支起点（DGM 语义：退役≠不可借鉴） | archived 满 12 个月且 diff_summary 已被后代条目吸收（parent 链核验）→ compressed：保留 entry_id/title/lineage/一行差异，正文转年度册 |
| **判据档案**（随考纲代谢） | still_valid=true 全保留（防重复考古的燃料） | 判据翻案（重放否决/修标/ruling）→ L4 回写 still_valid=false+invalidated_by → archived；考纲换版（comparison_policy/exam_suite_version 变更）时全旧代批量 archived | 同 venue 保留最近 3 代全文，更早 compressed（保留 experiment_id+hash+verdict 摘要；yaml 全文仍在 L4 卡不丢） |

执行件：`forget.py` 挂月度体检窗（L1 §2.6 同一节拍宿主，**日历节拍+每次点火实闸复核**——对齐 L1 §2.4 合规裁定，禁 sleep-loop）；输出 `heritage_forget_due` 轻事件+降级报告进月报。任何 compressed 条目 10 年内可由 entry_id 反查全量（DB 不删，只是字段摘要化）。Owner 不追认外扫裁定（L1 §2.4 双前置）时的降级路线=月度体检由高模型维护班人工开会话执行（排班表登记人工任务），自动化宿主解锁顺延。

### 2.9 关单强制登记机检（对接主文档 §三 关单四闸）

- **位次裁定**：传承登记是**关单四闸全过之后的产出检查**，不是第五道放行闸（四闸管质量，登记管沉淀；登记缺失不放行工单=阻塞修复主线，故作关单后置校验+月度对账双保险）。
- **机检规则**（`closure_check.py`，工单流 P2 落地时挂进关单链；落地前由月度体检对账代行）：工单 kind ∈ {incident_fix, defect_fix, redblu_finding} 的关单回执必须携带 `heritage_ref: <entry_id>`（新建缺陷模式）**或** `no_new_pattern` 声明，声明理由枚举三选一：`known_pattern: <entry_id>`（命中既有模式，occurrence_count+1）/ `mechanical_debt`（机械债无新根因）/ `dup_of: <case_id>`（个案已归并）。缺两者=关单回执校验失败→告警+工单重开。
- **读路径（先于写路径存在）**：工单生成器派工前机检匹配 V2 缺陷签名（signature 字段正则/关键词匹配），命中即把 recipe 附进工单（主文档 §3.5"命中带配方派工"的落地）。
- **gate 立案**：closure 校验进 commit gate 体系时走 OBJ_R 四步流水线（L4 C7 同款先例），本稿只出规则不立 gate。

---

## 三、接线图（契约）

| 对端 | 契约 | 方向 | 载荷 |
|------|------|------|------|
| **L6 切换** | 事件 `switch_archived_due`（L6 §③ 已声明边未定名，本稿提名，实施时两稿对齐）：L6 终局态转换（promote→champion / aborted / retire→tombstone）时 emit | L6→L7 | {switch_id, object{family, ref}, outcome, winner_ref, loser_ref, diff_summary, criteria_ref+criteria_hash, tombstone_entry?}——L7 消费：胜局→elite+criteria 双条目；aborted 带根因→defect 条目；retired→elite 降级信号 |
| **L4 对比** | `comparison_archived_due`（L4 §③ 已定名）：experiment 卡 archived 时 emit；反向 `comparison_prior_query` 只读服务 | L4↔L7 | 回写：{experiment_id, criteria_hash, venue, verdict, why_win 归因, too_good 出口}→criteria 条目（+win 时 elite 条目）；查询→H3 still_valid=true 历史裁定列表 |
| **工单流** | `work_order_closed_due` 关单事件+派工前签名匹配读调用（§2.9）；红蓝对抗发现经 redblu_finding 类工单同通道进 | 工单流→L7 | 关单：{work_order_id, kind, heritage_ref \| no_new_pattern{reason}}；派工查询：{symptoms}→{entry_id, recipe, signature} |
| **L1 感知** | `priors.py` 只读服务（V3/V4）；L1 施工项 9 挂起随本稿解锁 | L7→L1 | {domain, mechanism_family}→{prior_factor, rationale_refs, exclusion_keywords[]} |
| **L2 收集** | T4 快照（ref_family='L7'，生成器直写本 family 行）+`intake_heritage_baseline` 轻事件（L2 §三 已声明）；`heritage_parents_query` 组合素材服务（V1） | L7→L2 | baseline：{baseline_ref, kind:'elite'\|'pattern', count}（**裁定（红蓝 R1-B5）**：只发 elite\|pattern 两 kind+count、不收阴性——negative 留 L2 自用 KPI 不入传承，系对 L2 侧的契约要求，L2 稿同批对齐）；parents：{surface, family}→[entry_id, diff_summary, evidence_ref] |
| **L5 排产** | 命中缺陷签名的工单自带 recipe；祖先精英可作为施工任务书的参照素材（pre_rulings 引用 entry_id） | L7→L5 | {recipe, entry_id, pattern_norm} 附进工单 payload |
| **OBJ_R casebook** | 归并动作：case 状态→patterned 时经 store.register() 建/累加 defect 条目；casebook.defect_pattern 字段引用 pattern_norm | casebook→L7 | {case_id, root_cause, signature, recipe, pattern_norm} |
| **月度体检（L1 内监慢周期）** | forget.py+digest 生成器+多样性覆盖率核查同窗执行 | L1 节拍→L7 | 遗忘报告+坑集月报+prior 冻结状态 |

---

## 四、施工项清单（全部为设计交付，施工另走 15 步闭环）

| # | 项 | 文件/模块 | 验收标准 |
|---|----|----------|---------|
| 1 | DDL 登记器 | 新 `scripts/ai_layer/apply_ai_heritage_ddl.py`：建 schema ai_heritage + H1-H4 + V1-V5；`config/heritage_policy.yaml` 规则参数初值落盘 | 幂等执行两次零错；CHECK 值域与 2.3/2.5 一致；TIMESTAMPTZ 全覆盖 |
| 2 | 传承库服务 | 新 `src/zephyr/ai_layer/heritage/store.py`：register() 登记闸+状态机降级+hit_count 月度聚合回写（异步，红蓝 R1-B7），全经 DatabaseService | 五类拒收样本（缺锚点/占位/自查重命中/哈希不一致/无案例）全部被拒且拒因正确 |
| 3 | L2 快照生成器 | 新 `scripts/ai_layer/gen_heritage_dedup_snapshot.py`：V1/V2→T4 ref_family='L7'（只写本 family） | 幂等重刷 refreshed_at 刷新；不触碰其他 family 行；登记/降级后快照 24h 内刷新 |
| 4 | L1 先验服务 | 新 `src/zephyr/ai_layer/heritage/priors.py`：V3/V4 只读薄封装+每单保 1 组关键词机检 | 解锁 L1 施工项 9；factor 越界 [1.0,2.0] 被拒；词表过滤保底有单测 |
| 5 | 回写事件消费件 | 新 `src/zephyr/ai_layer/heritage/events.py`：switch_archived_due/comparison_archived_due/work_order_closed_due 消费（JSONL journal 对齐 pipeline_events 语义，施工前 clone_guard.check_before_write 预查） | 三事件各注入合成载荷→正确生成 elite/criteria/defect 条目；KillSwitch 非 normal 停消费全量保留；毒丸 MAX_ATTEMPTS=3 |
| 6 | 关单登记机检 | 新 `src/zephyr/ai_layer/heritage/closure_check.py`：§2.9 规则+no_new_pattern 理由枚举+月度对账器 | 合法关单（带 ref/三种理由）全过；缺登记样本被拦+告警；签名匹配命中带出 recipe |
| 7 | 遗忘执行器 | 新 `src/zephyr/ai_layer/heritage/forget.py`：§2.8 三类降级/压缩机检+heritage_forget_due 报告，挂月度体检窗 | 构造数据触发三类降级各 1 例；零物理删除断言；compressed 可反查 |
| 8 | 人读月报生成器 | 新 `scripts/ai_layer/gen_heritage_human_digest.py`：V2/V5→通知板+digests/YYYY-MM.md | 生成器产出零手工；plain_zh 全非空；prior 冻结状态可见 |
| 9 | 登记套件+测试 | 施工班走 15 步闭环：add_module_translation×新模块、apply_depgraph --add-design-node、capability card、gate 立案（如需）走 OBJ_R；`tests/ai_layer/heritage/`（test_store/test_priors/test_events/test_closure_check/test_forget） | 全部登记器零报错；TRANSLATION-COVERAGE/CREATE-GUARD/DEPGRAPH gate 全绿；测试全绿零生产路径写入 |

依赖序：1→2→(3,4,5,6,7)→8、9 随项并行。外部依赖：L6/L4 事件未落地不阻塞（events.py 声明态消费，合成载荷先行）；checklist 14 条+memory 坑集补登=一次性迁移工单（攒首批 defect 条目，T4 快照面非空才对 L2 生效，此前 ref_family='L7' 维持缺省跳过——L2 已预留）。

---

## 五、挖矿日志与自审闸

### 5.1 挖矿日志

| 轮次 | 矿脉 | 内/外 | 判定 | 关键产出 |
|------|------|-------|------|---------|
| L7-R1 | ①上游：L6/L4 回写契约+主文档 §3.5+casebook/checklist 现状 | 内 | signal | 三条输入边全有声明态契约；checklist 14 条人读版在档；casebook 未落地（首案内嵌）→ 边界三分裁定素材 |
| L7-R2 | ②下游：L1 挂起施工项 9+L2 ref_family='L7' 预留 | 内 | signal | 回流接线全部是"接预留"，零新发明 |
| L7-R3 | ③CBR 四 REs 与案例登记格式 | 外 | signal | Aamodt & Plaza 1994 双源；**纠正误引**（4REs 归 Aamodt & Plaza 非 Aamodt & Nygård）——retain=传承环的业界名 |
| L7-R4 | ③案例库遗忘/竞争力删除 | 外 | signal | Smyth & Keane IJCAI-95 双源；删 auxiliary 保 pivotal→§2.8 压缩判据 |
| L7-R5 | ③经验回放优先级 | 外 | signal | Schaul 2016 双源；hit_count 消费统计+recency 遗忘燃料 |
| L7-R6 | ③防早熟收敛/多样性 | 外 | signal | Lehman & Stanley 2011 双源；§2.6 四条配比约束的理论锚 |
| L7-R7 | ③关单复盘三字段业界对应 | 外 | signal | SRE Book Ch15/Workbook Ch5 双源；root cause/action items 结构与三字段同构 |
| L7-R8 | ④存储与事件机制对齐 | 内 | signal | PG 同实例新 schema 裁定；pipeline_events 语义收编 |
| L7-R9 | ⑥数据字段核对（L6/L4/casebook/checklist/T4） | 内 | signal | 主表+三扩展表字段全部有真源锚点 |
| L7-R10 | ①skill_postmortem/failure_replay 既有件反查 | 内 | signal | 归因器（MOD-INF-019）复用+R77"忘坑重踩"自认=立项内证 |

429 受阻：0 次。在档复用：DGM/MAP-Elites/AlphaEvolve/PDCA（V0/V2 报告同源多消费，交叉验证闸满足）。

### 5.2 自审闸三态裁定：**施工**

- **主判据（一票放行）**：L7 是七段闭环唯一缺失边——现状经验沉淀全靠会话自觉写 memory 目录（人读、库外、无 schema、不可机检）+checklist 14 条手工精选；每代换会话=重踩（failure_replay R77 自认在案）。L1 施工项 9 与 L2 比对面 5 双双挂起等本稿——不定形则下游两处预留永久空转。消灭三段人工：①每班人工攒坑入册（关单机检代劳）②重复考古（L4 先验查询代劳）③同坑重踩与换皮进货（签名匹配+T4 快照代劳）。
- **终局全貌位置**：PDCA Act 环=改善不写回标准等于没发生；DGM archive=开放式进化标配。Owner 四类事终局里，L7 直接服务"转正审批从考古变裁决"（判据档案=历史判优可查）。
- **反驳者三问**：①与 memory 目录重复？——双轨裁定（§2.7）：机检真源只能库内，memory 是 Owner 人读副本，不对称不冲突。②库会不会变成没人查的死库？——hit_count 消费统计+遗忘机制保证只留被用的；L2 比对面/L1 排除词表/派工签名是三条被动消费线（不依赖任何人主动查询）。③过度工程？——薄登记层：一张 DDL+四个薄模块+两个生成器，零新框架零新前端页零物理删除机制；OB/R casebook、checklist、ruling_registry 全部引用不吞并。
- **时序**：DDL+store 可先行；事件消费件随 L6/L4 施工批接线；casebook 起步批（OBJ_R S5）与本稿施工项 6 同批办（首案 pathspec 一次登记两头引用）。

### 5.3 待 Owner（3 项）

1. **数值预注册确认**：`config/heritage_policy.yaml` 全部初值（遗忘：defect 4 季度/elite top3+tombstone 2 体检窗/criteria 3 代；防近亲繁殖：factor ≤2.0、l7_prior ≤50%/日、格覆盖 60% 冻结线）——设计定值非实测标定，首轮数据回来后按 OBJ_R 流水线提案修订（L4/L6 同款处置）。
2. **checklist 增量登记纪律增补**：`defect_pattern_checklist.md` 入册纪律增补一行"新模式先登记 L7 传承库再上本清单（引用 pattern_norm）"——治理域 policy 文件修订，需 Owner/治理流程确认。
3. **creation_token 补登**：本班硬边界"禁登记 token"，本 DESIGN.md 的 creation_token 由主会话/Owner 补登（OBJ_R/L4 稿同款先例）。

---

## 修订记录

| 日期 | 版本 | 变更 | 批准 |
|------|------|------|------|
| 2026-09-17 | 1.0.0 | 初稿：六向台账（7 外内轮 signal/0 受阻）+五方边界裁定（对 L2/OBJ_R/checklist/memory 划界）+PG ai_heritage 真源设计（4 表 5 视图三类条目统一登记）+三条回写边四条读边+防近亲繁殖四约束+双轨不对称+三类差异化遗忘+关单机检+9 施工项+自审闸=施工 | 设计稿（status: design_v1，施工立项另走 15 步闭环） |

## 红蓝 R1 修复记录（2026-09-17，红队 B 发现，修复组 1）

| 编号 | 修复内容 | 落点 |
|------|---------|------|
| B2 | H4 补 tool_id/scene 两列（工具域条目必填、非工具域 NULL）；§2.1 补 OBJ_T 边界行（OBJ_T 只持只读视图，写入权归 L7，防双头登记）；工具域词表已同步 L2 T1（v0 六域），行为格重计 48 格（6 域×8 族） | §2.1/§2.3 H4/§2.6.4/§六向⑥ |
| B3 | §2.5 source_ref 白名单补 DR-*（OBJ_M 双跑记录）、TP-*（OBJ_T 配对实验记录）两前缀，注明与 L4 实验卡同构同通道；H1 source_ref 字段说明同步 | §2.5/§2.3 H1 |
| B4 | H3 补 simhash/mechanism_family 两列（可空，仅 mechanism 族条目填），解锁 L4 comparison_prior_query(simhash/mechanism_family) | §2.3 H3/§2.4 |
| B5（L7 侧） | 契约声明：intake_heritage_baseline 只发 elite\|pattern 两 kind+count、不收阴性——negative 留 L2 自用 KPI 不入传承（对 L2 侧的契约要求，L2 稿同批已改 payload） | §三 |
| B7 | hit_count 同步回写裁定为过度工程、改异步：消费路径只记计数流水，月度体检窗聚合回写（与 forget.py/月报同节拍）；§2.4 加裁定行 | §2.3 H1/§2.4/§2.7/施工项 2 |

## 红蓝 R2 修复记录（2026-09-17，红队 R2 发现）

| 编号 | 修复内容 | 落点 |
|------|---------|------|
| R2 | 月度体检宿主补降级路线：Owner 不追认外扫裁定（L1 §2.4 双前置）时，月度体检由高模型维护班人工开会话执行（排班表登记人工任务），自动化宿主解锁顺延——消解 T3 双前置射程张力（forget.py/坑集月报不因外扫未追认而悬空） | §2.8 |
