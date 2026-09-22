---
ttl: task_bound
completes_when: 本文档随定桩战役归档即完成
title: 模板生成器骨架设计
owner: ZephyrAlpha-Owner
session: st-chainpile-20260922
date: 2026-09-22
---

# 模板生成器骨架设计（W1 基建挖矿·五姊妹之一）

> 输入唯一真源：[00_piling_minutes.md](../00_piling_minutes.md)，引用格式 [纪要§N]。
> 共享基线：工程名=meta_question_registry（原问题中央登记表）；基建四件套=入库闸（问题进门）/**模板生成器（问题展开）**/未答看板（排队消费）/考试回填闭环（答案落账）+管理办法总册；使命=把"值得问的问题"变成受治理资产；对标 AEA 注册中心/OSF 预注册/AlphaForge(AAAI2025)/Sakana AI Scientist [纪要§5]。
> 本件只管模板生成器；接口处引用姊妹件名（入库闸设计/未答看板设计/考试回填闭环设计/管理办法总册/盲点专项），禁代写其内容。

## §0 骨架总览

| 章 | 一句话 |
|----|--------|
| §1 定位与边界 | 生成器是四件套中的"问题展开"件：62 条 v1 ID 骨架按模板机械展开成 250-400 条候选 [纪要§6/§9]。 |
| §2 模板语法 | 模板=参数化问题骨架，五构件（变量槽/常量面/取值域/生成约束/输出映射），附源线类与图谱类两个完整示例。 |
| §3 生成-筛选分工 | 生成=面展开（笛卡尔+枚举+容量上限公式），筛选=五要素机检→查重→容量截断；终审权在入库闸，生成器只产 draft 候选。 |
| §4 模板自身治理 | 模板也是资产：登记/版本/退役/净零声明，YAML 真源+ROOR 登记，62 条 ID→模板族映射表。 |
| §5 生成-入库通道 | 候选经入库闸唯一通道入 PG（draft 态+provenance），禁绕闸直插；限流衔接闸的洪水防线。 |
| §6 N_eff 塌缩防线 | 组合空间预注册编码进模板（预注册/锁定/禁事后扩）；E1C 三轨只留接口不设计因子 [纪要§4]。 |
| §7 外部锚点对标 | AlphaForge 与 Sakana AI Scientist 的自动假设生成机制拆解，本设计取与舍。 |
| §8 本件盲点自查 | 11 维逐维表态：有办法或显式登记盲点待裁，禁留白。 |
| §9 schema 增补提案 | 模板追溯所需新字段提案表，标"待 W1 评审"，禁直接改 18 字段底稿 [纪要§7]。 |

## §1 定位与边界

- 职责：模板语法、展开-筛选分工、模板自身治理、生成-入库通道、N_eff 防线的模板层落地。
- 不管：五要素机检实现（入库闸）、看板排序（未答看板）、考试设计（考试回填闭环）、因子本身（E1C 业务轨，且 [纪要§10] 禁业务施工）。
- W2 施工落点（本波只设计）：生成器=src/zephyr 新模块（建议 `src/zephyr/governance/question_gen/`）或治理脚本；生成物=YAML 机生快照；新建 .py 走 CREATE-GUARD（`scripts/scaffold.py`，[台账§6]）+新模块登记大白话简介（TRANSLATION-COVERAGE）+depgraph 先登记后施工（RULE-DEPGRAPH）。

## §2 模板语法：结构定义

模板=参数化问题骨架。五构件：

| 构件 | 定义 | 硬约束 |
|------|------|--------|
| 变量槽 slot | pattern 中的 `{var}`，带 `domain_ref`（取值域真源）与 `mode`（cartesian=参与笛卡尔积 / enumerate=小集合枚举配比） | domain_ref 必须可解析到 ROOR 登记的注册表/清单具名子集，禁内联游离清单（静态清单禁手工维护 [宪法§9.5]） |
| 常量面 constants | 不参与展开的固定字段（layer/status_out 等） | status_out 恒=draft（§3） |
| 取值域 domain_ref | `<registry>#<subset>` 形式；`tpl_builtin#`=模板内建小枚举（≤4 值，随模板版本冻结，属模板资产一部分） | 取值域扩缩=模板 minor 版升级+留痕 |
| 生成约束 constraints | 跨槽依赖/PIT 前置/容量上限/预注册要求 | 任一约束机检不过=该模板禁开跑 |
| 输出映射 output_map | 槽值+派生值→18 字段 schema [纪要§7] | 18 字段逐一显式（渲染值/派生值/缺省规则三选一），禁暗默认 |

### 示例模板 1：源线通用六问族（U1-U6 参数化）

```yaml
template:
  tpl_id: TPL-U-001            # 墓碑不复用（对齐 q_id 精神 [纪要§7]）
  version: 1.0.0               # semver：pattern/槽结构变更=major
  family: TPL-FAM-U
  layer: L1
  status: active               # active/deprecated/retired
  net_zero_note: "替代'W6 人工逐线手写六问'作业法；入册即视为替代声明"
  pattern: "源线{line}在窗口{window}的{signal}信号能否领先{lead_days}日预测{target}的{direction}？"
  slots:
    line:
      domain_ref: source_line_registry          # 真源：W4 源线谱正式注册表，目标 ≥20 条 [纪要§9]
      mode: cartesian
    q_intent:                                   # U1-U6 六问意图槽（六问全文 W6 补全 [纪要§6 注]）
      domain_ref: piling_minutes#U1-U6          # 真源：纪要§6 ID 骨架（过渡期，随战役目录登记）；切换前置=meta_question_registry 建成且 U 族六问全文入表，届时切 meta_question_registry#U 族
      mode: cartesian
    signal:
      domain_ref: source_line_registry#signal_vocab   # 真源：源线谱信号词表（每线子集）
      mode: cartesian
    target:
      domain_ref: target_registry               # 真源：[待裁] 推荐挂 W4 源线谱附表，勿另建注册表
      mode: cartesian
    window:   { domain_ref: tpl_builtin#window,   mode: enumerate }   # 内建枚举 1d/5d/20d/60d
    lead_days:{ domain_ref: tpl_builtin#lead_days,mode: enumerate }   # 内建枚举 1/3/5/10
    direction:{ domain_ref: tpl_builtin#direction,mode: enumerate }   # 内建枚举 涨跌/波动/流动性
  constants: { layer: L1, status_out: draft }
  constraints:
    cross_slot: "signal ∈ line 的信号词表子集；线未上线=该线不展开"
    pit_guard: "lead_days ≥ 1 且 window 与 lead_days 无前视重叠；回执写入 pit_proof"
    cap_template: 200
    preregistered_space: required               # 首跑前须登记组合空间（§6）
  output_map:                                   # →18 字段 [纪要§7]
    title: "pattern 渲染结果"
    layer: "constants.layer"
    line_ref: "{line}"
    data_sources: "line.data_sources（源线谱派生）"
    exam_plan: "q_intent→考试族引用（考试回填闭环件定义，本件只留 exam_ref 接口）"
    consumers: "line.consumers（源线谱派生）"
    frequency: "line.frequency（源线谱派生）"
    pit_proof: "pit_guard 机检回执"
    status: "constants.status_out"
    provenance: "tpl=TPL-U-001@{version}; space_hash={space_hash}; slots=<七槽值>"
    # 其余字段（parent_id/merged_into/graph_ref/chain_refs/evidence_refs/last_exam 等）显式空值过闸，必填性由入库闸判
```

### 示例模板 2：图谱传导族（W5 图谱谱系×组合层新问）

```yaml
template:
  tpl_id: TPL-GRF-001
  version: 1.0.0
  family: TPL-FAM-GRF
  layer: L2
  status: active
  net_zero_note: "替代'人工逐图谱逐节点对手写传导问'；与 TPL-FAM-GV（治理族）无对象重叠"
  pattern: "图谱{graph}中节点{node_a}到节点{node_b}的传导路径是否在{t_days}日内体现在{target}价格上？"
  slots:
    graph:   { domain_ref: graph_registry,          mode: cartesian }  # 真源：W5 图谱谱系注册表，≥3 张 [纪要§9]
    node_a:  { domain_ref: graph_registry#nodes,    mode: cartesian }  # 真源：图谱原料评估节点清单（每图子集）
    node_b:  { domain_ref: graph_registry#nodes,    mode: cartesian }
    t_days:  { domain_ref: tpl_builtin#horizon,     mode: enumerate }  # 内建枚举 5/10/20/60
    target:  { domain_ref: target_registry,         mode: cartesian }  # 取值域真源同例 1 [待裁同上]
  constants: { layer: L2, status_out: draft }
  constraints:
    cross_slot: "node_a ≠ node_b，且图内须存在 a→b 有向路径；无边对不生成（组合爆炸主闸）"
    pair_dedup: "(node_a,node_b) 无序对指纹去重，防 a→b 与 b→a 双计"
    cap_template: 100
    preregistered_space: required
  output_map:
    title: "pattern 渲染结果"
    graph_ref: "{graph}"
    line_ref: "路径途经源线（图谱谱系派生，可空）"
    exam_plan: "考试族引用（考试回填闭环件）"
    status: "constants.status_out"
    provenance: "tpl=TPL-GRF-001@{version}; space_hash={space_hash}; slots=<五槽值>"
```

## §3 笛卡尔面生成-筛选分工

**生成=面展开**（生成器职责）：

- 笛卡尔维（cartesian）：彼此正交、高区分度的少量维（如 line×q_intent、graph×node_a×node_b）；枚举维（enumerate）：小集合常量（窗口/天数/方向），是否与笛卡尔维全积以各模板 space 定义（§6 预注册）为准。
- 容量上限公式：`N_expand = ∏|cartesian 槽| × |enumerate 槽|`（经 cross_slot 过滤后）为展开上限的**理论值**，实际产出 = min(理论值, cap_template)，即 `cap_template = min(N_expand, 200)`；枚举维是否全积以各模板 space 定义为准（示例 1 全积 57,600 → 五要素+查重筛选后 ≤200）。建议值：单模板单次展开 ≤200，单批全模板合计 ≤600（对齐 250-400 目标留余量 [纪要§9]；600/批为生成器侧候选批量上限，与入库闸入库分批解耦——入库批量与限流豁免见《入库闸设计》§5.4 初始建库批量通道）。
- 超限截断序：先降枚举维 → 再按 line/graph 分层配额均衡 → 同层按槽值稳定哈希序截断。禁随机截断（保可复现）。

**筛选=三步定序**（顺序不可换）：

| 步 | 内容 | 责任方 |
|----|------|--------|
| 1 五要素机检 [纪要§2] | 能数据回答/可证伪/有消费方/有频率/PIT 安全逐项核 | 入库闸（终审）。生成器只备料五项派生值，不自判通过（防既当运动员又当裁判） |
| 2 查重 | 生成器做模板内槽值指纹粗去重（机械自裁级）；入库闸做跨模板/跨批次全库查重（终审）。语义级同义查重未定→§8 维 10 | 两层分责 |
| 3 容量截断 | 生成器侧 cap 只是预限流；全库容量复核与截断执行在入库闸 | 入库闸 |

**铁声明**：生成器产出的是候选（draft），不是已入库问题——候选不带 q_id（PQ-NNNN 由入库闸登记时分配，墓碑不复用 [纪要§7]），draft 态对未答看板不可见（看板只消费已登记问，[判读] 归未答看板件定稿）。

## §4 模板自身治理

- **登记**：模板注册表 YAML 真源，位置 [待裁] 推荐 W2 落地为 `docs/01_policies_and_standards/_registry/catalogs/template_registry.yaml`，W1 期暂随战役目录；同时在 ROOR（docs/registry_of_registries.yaml）登记条目（登记前比对无同域重复，净零）；新模板 .yaml 走 CREATE-GUARD；条目计数由生成器自产，禁手写（静态清单禁手工维护）；注册表写入必经 safe_write_text CAS（宪法硬规则 13）。
- **版本**：semver。major=pattern/槽结构变更（旧展开产物不回溯改，provenance 可辨）；minor=取值域/约束收紧；patch=文案。
- **退役**：复用净零判据 w5_1——零触发零消费即退役；退役保 id 不复用；退役生效时已展开未入库的 draft 候选按 batch 粒度作废并留审计痕（禁退役模板的在途候选继续入库）；涉"注册表净删"级登记上报不擅动 [纪要§10]，版本冲突/翻案走裁定#NNN（#400 起，同 commit 原子 [台账§6]）。
- **净零声明**：每模板必须带 net_zero_note 声明替代/合并对象（见两示例）；新增模板须指明退役或合并哪个旧模板。

**62 条 v1 ID 骨架→模板族映射** [纪要§6]：

| v1 组 | 层挂载 | 模板族 | 展开策略 |
|-------|--------|--------|---------|
| M1-M4 | L0 元问题 | TPL-FAM-M | 元问题禁纯机械展开：模板只做格式化+留痕，全文 Owner/总册定稿 [待裁，推荐半人工] |
| U1-U6 | L1 通用六问 | TPL-FAM-U（示例 1） | 六问×源线谱（≥20 条，与 W4 对齐后展开） |
| 十条线各 2 | L1 专属 | TPL-FAM-L | 每线 2 条专属问按线参数复用展开 |
| S1-S12 | L3 状态变量 | TPL-FAM-S | 大盘/情绪/板块三域×变量参数 [纪要§8.1] |
| D1-D8 | L4 决策 | TPL-FAM-D | 决策消费方×场景参数 |
| E1-E7 | L5 执行验证 | TPL-FAM-E | 考试方案参数化（挂考试回填闭环件接口） |
| G1-G5 | L6 治理 | TPL-FAM-GV | 治理问展开空间小，半人工+模板留痕 |
| （组合层新问） | 跨层 | TPL-FAM-GRF（示例 2）/TPL-FAM-CMB | 组合空间预注册，见 §6；目标 62→250-400 的增量主力 |

## §5 生成-入库通道

- 链路：生成器→YAML 机生快照（`.runtime/sessions/<sid>/staging/`，24h TTL [宪法§9.4]）→**入库闸唯一写 API**→PG meta_question_registry（draft 态）。生成器禁直连 PG/裸 duckdb（DatabaseService 唯一真源 [宪法§9.1]）；表通道沿 ai_layer intake 先例（DDL-as-Code+写入 API，[台账§6]）。禁绕闸直插。
- provenance 规范：`tpl=<id>@<ver>; space_hash=<h>; batch=<batch_id>; slots=<槽值>` 全机生禁手改——模板追溯锚点。
- 限流衔接（引用入库闸设计，不重复其参数）：生成器侧预限流 cap_template/cap_batch；入库闸洪水防线（闸侧姊妹件定义速率/容量）触发时向生成器返回退避指令，生成器凭 batch manifest 幂等重放只补差，禁全批重灌；闸侧 fail-closed 期间本侧 staging TTL 冻结（batch manifest 凭据不灭失，恢复后凭 manifest 只补差）。
- 时间分层：快照带单一生成时戳，今日生成→明日入库窗消费，同一时戳禁循环 [纪要§8.2]；生成器不自反消费自己的产物作问源。

## §6 N_eff 塌缩防线在模板层

组合层新问含"组合空间预注册/N_eff 塌缩防线"（共享基线）。模板层三机制：

1. **预注册字段**：模板 constraints.preregistered_space=required；首跑前把空间定义（各槽取值域快照+笛卡尔方案+容量上限+冻结时戳）注册并机生 space_hash，无 space_hash 不开跑。
2. **展开时锁定**：每次展开引用 space_hash；取值域变更（如源线谱新增线）→space_hash 变更→须走模板 minor 升级+登记留痕，旧空间产物不回溯。
3. **禁事后扩空间**：同 space_hash 二次展开只允许凭 batch manifest 补齐上次容量截断未完成的配额，禁止追加新维度/新取值——要扩=新 space_hash 新预注册（对齐 OSF 预注册精神 [纪要§5]：预注册后不可改，改动即新预注册）。此为 N_eff 防线核心：堵"事后挑选性扩张→有效样本量虚高"。

**E1C 三轨接口**（gplearn+智能体+MCTS [纪要§4]；只留接口，禁设计因子本身 [纪要§10]）：

- 积木接口：slots.domain_ref 允许指向任一 ROOR 登记注册表（如未来 `block_registry#<family>`）——解析器按 ROOR 查找，模板语法零改动即接入积木库。
- 考试链加固接口：output_map.exam_plan 落为 `exam_ref` 槽引用考试族 id（考试回填闭环件定义），模板不定义考试内容。
- GPU 燃料接口：模板 budget.compute_tag 只给候选打标（heavy/light），不调度算力；调度归 E1C 自建，且不碰 GPU 周五硬前置三件 [纪要§8.4]。

## §7 外部锚点对标

- **AlphaForge（AAAI2025）机制**：①公式化因子表达式序列化为算子序列，用生成网络（GPNet，LSTM 序列生成）从已知因子库学习分布、批量生成新表达式；②预测网络对候选做未来绩效（如 IC）快速预估，替代昂贵逐条回测，"生成-预测"协同；③语义融合模块对语义相近因子聚类去重并动态加权组合，挖掘与组合一体化。
- **Sakana AI Scientist 机制**：LLM 按 idea 模板头脑风暴批量产出研究假设→逐条做文献检索新颖性查重（Semantic Scholar）过滤重复→假设展开为实验计划，在代码模板上迭代"修改-运行-修错"自动完成实验→LLM 自动成文（LaTeX）并自动评审打分，评分反馈决定该线是否继续，形成"假设→实验→成文→评审"自主闭环。

| 锚点机制 | 取 | 舍 |
|----------|----|----|
| AlphaForge 生成-预测协同 | "批量生成+廉价预筛"分层观：模板机械展开=生成层，五要素机检=预筛层，免逐条人审 | 神经序列生成表达式（不可复现不可审计，冲突"机械可证"纪律 [纪要§10]）；神经网络预评估因子收益（本工程预筛的是问题资格，非收益） |
| AlphaForge 语义融合组合 | 组合思想→查重+merged_into 合并闸 [纪要§7] | 动态加权组合因子（属 E1C 因子工程，禁越界） |
| Sakana 假设闭环 | 闭环观：问题→考试→回填→复考 对应 idea→实验→成文→评审；查重前置（§3 第 2 步） | LLM 自由假设直接进执行——本工程 LLM 产候选必须先过模板约束+入库闸 draft 态，LLM 调用必经 LSGSecurityGateway [宪法§7]；无人类门位的端到端自主 [宪法§5] |
| OSF 预注册 | §6 三机制（预注册/锁定/禁事后扩） | 形式主义走过场——本工程 space_hash 机生可验 |

## §8 本件盲点自查

11 维清单=五要素①-⑤ [纪要§2]+一问一考 [纪要§3]+时间分层 [纪要§8.2]+净零 [宪法§4]+容量/查重/可追溯三项工程维；清单定稿权在盲点专项姊妹件，[待裁] 推荐此 11 维为全战役共用版。

| # | 维 | 表态 | 处置 |
|---|----|------|------|
| 1 | 可数据回答 | 有办法 | data_sources 强制派生自源线谱/图谱原料评估；原料缺失过不了闸 |
| 2 | 可考试证伪 | 有办法 | exam_plan 必挂考试族引用；无引用不出候选 |
| 3 | 消费方明确 | 有办法 | consumers 派生自 line/graph 注册表，非手工填 |
| 4 | 更新频率 | 有办法 | frequency 派生自源线谱 |
| 5 | PIT 安全 | 有办法+登记盲点 | pit_guard 出"结构无前视"回执；数据层前视（供应商回填/时戳错位）在闸外——显式登记：归入库闸+数据侧联合处置，本件不代庖 |
| 6 | 一问一考 | 有办法+登记盲点 | 一 pattern 一考试族；拆并走 parent_id/merged_into；"同模板展开出近义变体"的拆并机检规则 W2 定——显式登记待裁 |
| 7 | 净零 | 有办法 | 模板登记强制 net_zero_note；退役复用 w5_1 判据 |
| 8 | 时间分层 | 有办法 | 生成物只含问题文本+单一快照时戳；生成器不自反作问源，同一时戳禁循环 |
| 9 | 容量爆炸 | 有办法 | §3 上限公式+截断序+§5 闸侧退避 |
| 10 | 查重 | 登记盲点 | 本件只做槽值指纹精确去重；跨模板语义级同义查重规则未定——登记待裁，归盲点专项+入库闸 |
| 11 | 可追溯/治理挂接 | 有办法 | provenance 机生含 tpl/version/space_hash/batch；裁定#NNN/gate/ROOR/safe_write_text 全挂现有体系不另起炉灶 |

## §9 schema 增补提案（待 W1 评审，禁直接改 18 字段底稿 [纪要§7]）

| 提案字段 | 类型 | 用途 | 来源章 |
|----------|------|------|--------|
| tpl_ref | varchar | 追溯展开模板 id@version | §2 |
| space_hash | varchar(64) | 组合空间预注册指纹（N_eff 防线锚点） | §6 |
| slot_values | jsonb | 槽值快照（重放/指纹查重基础） | §2/§3 |
| batch_id | varchar | 批次限流与幂等重放 | §5 |
| exam_ref | varchar | 考试族引用（考试回填闭环接口） | §2/§6 |
| compute_tag | varchar | E1C 算力/考试预算标（只打标不调度） | §6 |

推荐项：方案 A=六项全部内嵌 provenance jsonb 结构化（18 字段底稿零增量，最净零）；方案 B=独立列（闸检/查询高效）。推荐 A 起步、B 备选——均**待 W1 评审**，评审时同批追认 S-1 计数判读（机械计数 18 列 [台账§3]）。
