---
ttl: permanent
doc_type: architecture_view
status: draft
version: "0.2.0"
date: 2026-08-01
---

# 交易决策作战地图能力定位书（第四全景图 / battle_map）

> 版本：V0.2.0（草案，待 Owner 评审）| 2026-08-01
> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）
> 写法：大白话为主，配表格和 ASCII 图。变更历史见文末。
> **文档责任范围**：定义**交易决策作战地图**（`battle_map`）——项目第四全景图——的能力定位、数据模型、真源分工、双向对齐机制、迁移策略。它是 `07_trading_decision_architecture/` 人类视图背后的真源。

> **取代声明**：本文档升级并取代 [trading_flow_panorama.md](trading_flow_panorama.md) V1.0.0。
> 旧定位书的核心裁定"**07_ 不是新图、全景图只有三个**"作废；升级为"**07_ 背后有第四全景图 `battle_map` 作真源，07_ MD 是它的派生人类视图**"。旧文档有价值的内容（三态展示机制、SSoT 铁律、06_/07_ 区别）已提取融合到本文档。

---

## 一、作战地图是什么？（一句话）

**交易决策作战地图（battle_map）是项目的第四全景图——一张以"决策环节"为节点、以"钱怎么赚"为流程主线、把 decisiongraph / depgraph / 候选池 / 蓝图 / 数据流按业务流程串联起来的索引层真源图。**

它回答的问题不是"决策怎么分层"（那是 decisiongraph 的事），也不是"模块依赖谁"（那是 depgraph 的事），而是：

> **"我这个赚钱流程的每一个环节，到底落在哪些模块/候选/蓝图章节上？落地没有？谁来承载？"**

它存在 PostgreSQL（`battle_map_*` 三张表）里，由 `apply_battle_map.py` 写入，由 `generate_trading_flow_diagram.py` 派生成 `07_/` 目录下的人类视图 MD。

**和现有三图的关系**：

| 图 | 视角 | 节点粒度 | 回答 |
|---|---|---|---|
| depgraph | 依赖 | 模块（.py 文件） | 模块依赖谁 |
| dataflowgraph | 数据流 | 数据集/作业 | 数据怎么流 |
| decisiongraph | 决策零件 | 决策节点（细） | 决策怎么分层 |
| **battle_map（新）** | **作战环节** | **环节（粗，聚合多节点）** | **钱怎么赚、每环节落在哪** |

**和 07_ 视图的关系**：07_ MD 是 battle_map 的派生人类视图（只读）。battle_map 是真源，07_ 改了不算数，battle_map 改了重跑生成器更新 07_。

---

## 二、它解决什么问题？

它解决三个老毛病，前两个是 AI 开发的，第三个是旧定位书没覆盖的：

| 毛病 | battle_map 怎么治 |
|---|---|
| **AI 写决策时不知道落在哪** — 人说"加个买入信号融合"，AI 不知道这个环节现有哪些模块承载、是 design 还是没建 | battle_map 每个环节挂载锚点（modules/candidates），AI 查环节就知道落地情况，不凭记忆推断（防幻觉） |
| **零件和装配脱节** — decisiongraph 有 2758 个细粒度节点，没有"业务流程"的聚合视图 | battle_map 是装配图+故事线，把零件按"钱怎么赚"串起来；decisiongraph 是零件手册，两者互补 |
| **模块和作战目的脱节** — 看着 depgraph 某个模块，不知道它服务于赚钱流程的哪个环节、哪个阶段 | battle_map 双向查找：从模块能反查它在作战地图的位置（第几阶段、第几环节），看模块时就知道它的作战使命 |

**本质**：给人类一张作战指挥图，给 AI 一个"写决策时先查落地"的防漂移锚点，给所有模块一个"为什么而建"的作战使命归属。

---

## 三、它不是什么？（边界要画清楚）

| 不是这个 | 为什么不是 |
|---|---|
| decisiongraph 的副本 | battle_map 环节 ≠ decisiongraph 节点。一个环节聚合多个 decision_node + 多个 depgraph 模块 + 候选 + 蓝图章节。battle_map 引用这些图，不复制节点 |
| 07_ 视图本身 | 07_ MD 是 battle_map 的派生人类视图。battle_map 在 DB，07_ 在 docs |
| 策略参数文档 | battle_map 的 `indicators` 字段记录"指标方案的结构化引用"（trigger/threshold/source_module），不是策略参数清单。具体参数值在策略蓝图/代码里 |
| 新造的孤立图 | battle_map 是索引层，所有锚点指向已有四图+候选池的现存节点。不 invent 新模块 |
| 替代 trading_flow_narrative.yaml | 叙事职责移交给翻译真源 `battle_map_steps` 段，narrative.yaml 逐步退场（不立即删） |

---

## 四、和旧定位书的关系（取代声明）

[trading_flow_panorama.md](trading_flow_panorama.md) V1.0.0 的核心裁定"**07_ 不是新图、全景图只有三个、07_ 不进四图对齐**"在 V0.1 升级中**作废**。新裁定：

- 全景图从三个升级为**四个**：depgraph / dataflowgraph / decisiongraph / **battle_map**
- 07_ MD 从"decisiongraph 的视图"升级为"**battle_map 的派生人类视图**"
- 07_ 通过 battle_map 间接进对齐体系（battle_map 进，07_ 作为派生视图跟随）

**旧文档有价值内容提取**（已融合到本文档）：
- 三态展示机制（production/design/候选）→ 本文 §九
- SSoT 铁律（改真源不改派生物）→ 本文 §六
- 06_/07_ 区别（零件 vs 装配）→ 本文 §一、§二
- 四模式开关 + 应急保命降级 → 仍由翻译真源横切层承载，battle_map 环节引用

**旧文档处置**（Owner 已定：删除重建）：
- 本文档（`battle_map_panorama.md`）定稿后，直接删除 `trading_flow_panorama.md`，git log 留痕
- 旧文档有价值内容已提取融合到本文档（见上文），删除不损失信息

---

## 五、数据模型（三张表）

对标 `apply_depgraph.py` / `apply_decisiongraph.py` 模式，新建 `apply_battle_map.py` 写入 PostgreSQL。三张表：

### 5.1 battle_map_steps（作战环节表）—— 真源核心

每个环节一行。环节是"钱怎么赚"流程上的一个业务步骤（如"流动性过滤""四轨融合""风控审批"）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `step_id` | TEXT PK | 环节主键，格式 `BM-<阶段缩写>-<序号>`，如 `BM-BUY-03` |
| `step_name` | TEXT | 环节中文名（如"四轨融合"），与翻译真源 `name_zh` 一致 |
| `flow_stage` | TEXT | 所属阶段（stock_selection/buy_flow/sell_flow/position_management/execution/reconciliation） |
| `layer` | TEXT | 映射层（L0/L1/L2A/.../横切），与 decisiongraph layer 对齐 |
| `sort_order` | INT | 环节在流程中的顺序（同 flow_stage 内排序） |
| `narrative_ref` | TEXT | 指向翻译真源 `battle_map_steps` 段的 step_id（叙事真源在外部 YAML） |
| `indicators` | JSONB | 结构化指标（trigger/threshold/source_modules/source_ref），见 §十二 |
| `source_ref` | TEXT | 出处（草图 §1.4 / 现有模块代码），可追溯 |
| `design_maturity` | TEXT | production / design（环节本身是否已在实盘主链路） |
| `created_at` / `updated_at` | TIMESTAMP | 审计 |

### 5.2 battle_map_anchors（双向对齐关系表）—— 双向查找的核心

每个"环节 ↔ 模块/候选/蓝图/数据流/决策节点"的关联一行。**这是双向查找的真源**（见 §七）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `anchor_id` | SERIAL PK | 锚点主键 |
| `step_id` | TEXT FK → battle_map_steps | 所属环节 |
| `target_graph` | TEXT | 目标图：depgraph / dataflowgraph / decisiongraph / candidate / blueprint |
| `target_id` | TEXT | 目标图里的节点 id（module_id / candidate_id / blueprint_section / decision_node_id / dataflow_node_id） |
| `target_role` | TEXT | 这个目标在该环节扮演的角色：primary（主承载）/ supplement（补充）/ degradation（降级兜底） |
| `status_snapshot` | TEXT | 快照 depgraph.build_status（production/planned/deprecated），给生成器上色用 |
| `created_at` | TIMESTAMP | 审计 |

### 5.3 battle_map_edges（环节流转表）

环节之间的流转关系（数据流/触发/降级）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `edge_id` | SERIAL PK | 边主键 |
| `from_step_id` | TEXT FK → battle_map_steps | 上游环节 |
| `to_step_id` | TEXT FK → battle_map_steps | 下游环节 |
| `edge_type` | TEXT | data_flow / trigger / degradation |
| `label` | TEXT | 边标签（如"候选池""portfolio_target"） |
| `created_at` | TIMESTAMP | 审计 |

### 5.4 环节粒度标准（6 件套）—— 作战地图的灵魂

每个 `battle_map_steps` 环节**必须带 6 件套**，写到"能和代码交互"的细度（比草图 §1.2-§1.6 注解更细）。这是防幻觉的核心——不写清楚，AI 没法和代码交互，人也看不出参数对不对。

| 要素 | 内容 | 例子（分批建仓环节 BM-BUY-04） |
|---|---|---|
| ① 触发条件 | 用什么判定、N/M 阈值 | 满足 2/3：调整周期到位 / 二次回落 / 缩量 |
| ② 消费的数据/因子 | 具体清单 + 来自哪个层/模块 | §6.6进度、§6.7阶段、§6.1.3轮动序列、量比 |
| ③ 参数 | 默认值 + 可配置范围 + **代码当前实际值** + 状态 | 分批数=2(2-4)、间隔=1交易日、满足阈值=2/3 |
| ④ 数据流 | 输入→处理→输出→下游环节 | 进度+阶段+轮动→条件判定→L3.5仓位→L4执行 |
| ⑤ 代码映射 | 实现模块 + 参数在代码位置 | MOD-xxx / src/zephyr/.../xxx.py:L120 |
| ⑥ 降级/中止条件 | 什么情况降级或中止 | 跌破前低→暂停后续批次→止损评估 |

**③ 参数字段支持双向**（代码↔地图双向反馈的核心）：

| 参数状态 | 含义 | 方向 | 用途 |
|---|---|---|---|
| `implemented` | 代码已实现，带 `current_code_value` | 代码→地图 | 把代码实际参数反馈到地图，人看到能提修改建议 |
| `proposed` | 代码没有，人在地图提参数 | 地图→代码 | 先提参数，再验证建代码测试 |
| `testing` | 提议参数正在回测验证 | 地图→代码 | 参数在回测中，未定稿 |

**粒度量化**：按 6 件套标准，6 阶段 × 8-15 环节，预计 **50-100 个环节**（比草图 §1.2-§1.6 的 5 段注解细很多）。6 件套的结构化部分（①②③④⑤⑥）进 DB 的 `indicators` JSONB，大段解释文案进翻译真源 `indicators_zh`。

---

## 六、真源分工（SSoT）

按项目 SSoT 分类铁律（TRAE-062），battle_map 的数据分两类真源：

```
规则数据真源（YAML）                    架构数据真源（PostgreSQL）
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│ module_translation_registry.yaml │    │ battle_map_steps   （环节表）    │
│   §battle_map_steps 段（新增）    │    │ battle_map_anchors （锚点表）    │
│   - name_zh/name_en/plain_zh     │    │ battle_map_edges   （流转表）    │
│   - mechanism_zh（机制说明）      │    │   + indicators JSONB（结构化）   │
│   - indicators_zh（指标文案）     │    │   + status_snapshot              │
└──────────────┬──────────────────┘    └──────────────┬──────────────────┘
               │                                      │
               └─────────────────┬────────────────────┘
                                 ▼
                    generate_trading_flow_diagram.py（改造）
                                 │
                                 ▼
              ┌────────────────────────────────────────┐
              │ 07_trading_decision_architecture/       │（派生产物）
              │   9 MD + 7 HTML（人类视图，带颜色标注）  │
              └────────────────────────────────────────┘
```

| 数据类型 | 真源 | 写入工具 | 说明 |
|---|---|---|---|
| 环节元数据（step_id/flow_stage/layer/sort_order/design_maturity） | DB | `apply_battle_map.py` | 架构数据 |
| 双向锚点（step↔target 关联） | DB | `apply_battle_map.py` | 架构数据，双向查找真源 |
| 环节流转（edges） | DB | `apply_battle_map.py` | 架构数据 |
| indicators 结构化字段（trigger/threshold/source_modules） | DB | `apply_battle_map.py` | 架构数据，要和模块代码联动 |
| 环节叙事（中英文名/大白话/机制/指标文案） | YAML 翻译真源 | 手工编辑 `module_translation_registry.yaml` | 规则数据，可被多视图复用 |
| 07_ MD + HTML | 派生产物 | `generate_trading_flow_diagram.py` | 只读，禁止手编 |

**SSoT 铁律**：
- 改环节叙事 → 改翻译真源 `battle_map_steps` 段 → 重跑生成器
- 改环节结构/锚点/指标结构化字段 → 用 `apply_battle_map.py` 改 DB → 重跑生成器
- 禁止直接改 07_ MD（派生产物，会被覆盖）
- 禁止在生成器代码里硬编码叙事（必须读翻译真源）

---

## 七、双向查找机制（核心，本文档的灵魂）

这是作战地图区别于其他三图的核心能力。所有模块最终都是为了实现作战地图上的某个功能——所以必须能双向查找。

### 7.1 两个方向

**方向 A：环节 → 组成模块**（写决策时用）
> "这个买入环节由哪些模块组成？这些模块在全景图还是候选池？是 production 还是 planned？"

```
battle_map_steps.step_id
        │ 查 battle_map_anchors WHERE step_id=?
        ▼
target_graph + target_id + target_role + status_snapshot
        │
        ├─ target_graph=depgraph     → 已决定要建的模块（看 build_status）
        ├─ target_graph=candidate    → 候选池模块（deferred/candidate）
        ├─ target_graph=blueprint    → 蓝图章节（设计意图）
        ├─ target_graph=decisiongraph→ 决策零件节点
        └─ target_graph=dataflowgraph→ 数据流节点
```

**方向 B：模块 → 作战位置**（看模块时用）
> "depgraph 里这个模块，它服务于作战地图的哪个阶段、哪个环节？它的作战使命是什么？"

```
depgraph/candidate 的 module_id
        │ 查 battle_map_anchors WHERE target_graph=? AND target_id=?
        ▼
step_id → battle_map_steps.flow_stage + step_name
        │
        ▼
"这个模块是【买入阶段·四轨融合环节】的主承载模块"
```

### 7.2 为什么用 anchors 表做单一真源，而不在全景图模块上加独立字段

Owner 倾向"在三个全景图+候选池都给模块加一个 battle_map_position 字段"。这个直觉是对的（看模块时一眼看到作战位置），但直接加独立写入字段有**漂移风险**：anchors 表和模块字段两处要同步，一旦不一致就不知道哪个对（违反项目防漂移铁律）。

**推荐方案：单一真源 + 派生展示**
- **真源**：`battle_map_anchors` 表（唯一写入点，由 `apply_battle_map.py` 维护）
- **派生展示**（后置增强，battle_map 建起来后再加）：
  - 全景图模块节点加 `battle_map_step_ids` 字段（数组）——由 `apply_battle_map.py` 单向 sync 写入（anchors→各图字段），**只读缓存，禁止独立写入**
  - 生成器（generate_domain_doc 等）读这个字段，在模块节点上标注"📍 作战地图：买入·四轨融合"
  - 类比：depgraph 的 `gate_reason` 字段也是这种"真源在别处、模块上带快照"的模式（见 visualization_view_template §7.4）

这样既满足"看模块时一眼看到作战位置"，又保证单一真源不漂移。

### 7.3 查询工具

新建 `battle_map_reader.py`（对标 `DecisionGraphReader`），提供两个方向查询接口：
- `get_modules_by_step(step_id) -> list[anchor]`（方向 A）
- `get_steps_by_module(target_graph, target_id) -> list[step]`（方向 B）

### 7.4 不变量

- **BM-INV-001**：每个 `battle_map_steps` 必须至少有一个 `battle_map_anchors`（环节无锚点 = 悬空决策 = 幻觉风险，君子协定告警，跑顺后升级硬阻断）
- **BM-INV-002**：`battle_map_anchors.target_id` 必须能在 `target_graph` 对应的图/仓库里找到（防幽灵锚点）
- **BM-INV-003**：环节叙事必须来自翻译真源 `battle_map_steps` 段，禁止在生成器硬编码
- **BM-INV-004**：全景图模块的 `battle_map_step_ids` 字段是派生只读缓存，禁止直接写入（真源在 anchors）

---

## 八、与全景图对齐体系的关系

### 8.1 第四全景图

battle_map 和 depgraph / dataflowgraph / decisiongraph 并列，是第四个全景图。**图名 `battlemap`**（对标 depgraph/dataflowgraph/decisiongraph 的 Xgraph 复合形式），**表前缀 `battle_map_*`**（对标 `decision_*` 的"全词_功能"形式）。在 `panorama_registry` 登记为 `PAN-BATTLE-MAP-01`。

### 8.2 两套对齐，正交不冲突

| 对齐 | 轴 | 回答 | 用途 | 工具 |
|---|---|---|---|---|
| 现有四图对齐 | `module_id` | 一个模块在4张图里一致吗 | 建模块时 | `align_panoramas.py`（保持不动） |
| 作战地图对齐（新） | `step_id` | 一个环节都落地了吗、落在哪 | 写决策时 | `align_battle_map.py`（新建） |

两套对齐正交：module_id 轴管"模块一致性"，step_id 轴管"环节落地性"。互不干扰。

### 8.3 align_battle_map.py（新建）

检查项（先君子协定，跑顺后升级硬阻断）：
- 环节无锚点（孤儿环节）→ 悬空决策告警
- 锚点 target_id 在目标图找不到（幽灵锚点）→ 告警
- 环节 flow_stage 与 anchors 目标模块的 domain 不匹配（域漂移）→ 告警

### 8.4 候选池挂载

候选池模块（`candidate_module_registry.yaml`）通过 `battle_map_anchors`（target_graph=candidate）挂到具体环节。不再只躺在附录2表格里，而是有明确的作战位置。候选 entry 可选加 `panorama_position.battle_map.step_id` 字段（派生展示，由 anchors sync）。

---

## 九、三态展示机制（沿用旧定位书，扩展为四态）

07_ MD 按模块状态颜色标注（生成器 join depgraph.build_status 产出）：

| 态 | 来源 | 颜色 | 说明 |
|---|---|---|---|
| 运营态 | depgraph build_status=production | 🟦 蓝色实线 | 已上线运行 |
| 设计态 | depgraph build_status=planned | 🟧 橙色虚线 | 蓝图阶段，代码未写 |
| 弃用态 | depgraph build_status=deprecated | 🟥 红色 | 已弃用 |
| 缺失态 | 环节无锚点 or 锚点 target 找不到 | ⬜ 灰色 | 这个环节压根没模块承载（BM-INV-001 告警） |
| 候选态 | target_graph=candidate | 🟨 黄色 | 在候选池里，未进全景图 |

**治理合规**：过度工程不进 depgraph（四问过滤铁律），只进候选池。battle_map 通过 anchors 把候选挂到环节，07_ 展示时用黄色标注"候选承载"。

---

## 十、可视化规范

遵循 [visualization_view_template.md](visualization_view_template.md)（三视图 + 可缩放 HTML + 节点四要素 + 预折行铁律）。battle_map 生成器（`generate_trading_flow_diagram.py` 改造版）必须复用：
- 灰色主题头 + `flowchart TD`
- 节点四要素（成熟度 + 双语名称 + 大白话 + 路径/标识），叙事来自翻译真源 `battle_map_steps` 段
- `_wrap_label_text()` 预折行（禁止 CSS max-width 二次折行）
- 四类 classDef + 颜色（§九 的五态映射到 classDef）
- HTML 联动生成到 `_zoomable_html/`

**作战地图特有的可视化**：
- 总指挥图：环节节点（按6阶段 subgraph 分层）+ 环节间流转边 + 每个环节挂载的模块小节点（用颜色标状态）
- 分阶段图：单阶段的环节 + 该阶段所有锚点模块
- 每个环节节点点击可展开"组成模块清单"（方向 A）

---

## 十一、生成器改造

`generate_trading_flow_diagram.py` 改造：

| 改造点 | 旧 | 新 |
|---|---|---|
| 主真源 | decisiongraph + narrative.yaml | **battle_map 三表**（steps/anchors/edges） |
| 模块状态 | 不查 depgraph | join depgraph（build_status→颜色） |
| 候选挂载 | 只进附录2 | join 候选池，通过 anchors 挂到环节 |
| 节点细节 | decisiongraph 节点 | join decisiongraph（环节聚合的决策节点） |
| 叙事 | narrative.yaml | 翻译真源 `battle_map_steps` 段 |
| 颜色标注 | 仅 production/design | 五态（§九） |

**narrative.yaml 退场计划**（Owner 已定：并行观察一段再删）：
- `trading_flow_narrative.yaml` 现在是 07_ MD 的"故事底稿"（每阶段大白话/ASCII框图/指挥AI提示/横切层四轨共享信号应急降级四模式）。battle_map 上线后这些叙事移交给翻译真源 `battle_map_steps` 段
- 退场分三步：① 迁移期 narrative 与翻译真源并行存在；② 翻译真源完整覆盖 narrative 全部内容、且生成器只读翻译真源跑通后；③ narrative.yaml 标 deprecated 删除
- 不立即删（风险大），也不永久并存（两处叙事真源会漂移）

---

## 十二、迁移策略（草图 v9.0 → 真源）

草图 [交易决策架构.md](file:///d:/临时工作区/架构图/交易决策架构.md)（v9.0，1.4MB，30章）是作战地图的内容来源。分三批迁移：

| 批次 | 草图章节 | 迁移到 | 产出 |
|---|---|---|---|
| 第一批（骨架） | §1.1 主流程 + §1.2-§1.6 五段环节注解 | battle_map_steps + 翻译真源 battle_map_steps 段 | 作战地图骨架（约 20-30 个环节） |
| 第二批（锚点） | §2-§12 层详解里的模块 | battle_map_anchors | 每个环节挂载承载模块 |
| 第三批（横切） | §13 漏斗 / §16 冲突矩阵 / §30 缺失模块 | battle_map_edges + anchors | 流转边 + 缺失环节标灰 |

**迁移原则**：
- 草图里的过度工程（KAN/Mamba/Kronos 等）不进 battle_map，归候选池（沿用旧定位书四问过滤）
- 草图里的实盘主链路进 battle_map_steps（design_maturity=production）
- 每个环节的 indicators 从草图注解结构化 + 从现有模块代码提炼大白话

---

## 十三、字段详细定义（附录，施工依据）

### 13.1 翻译真源 battle_map_steps 段 schema

在 `module_translation_registry.yaml` 顶层（与 `entries:` 平级）新增 `battle_map_steps:` 段：

```yaml
# 顶层段示例（与 entries: 平级）
battle_map_steps:
  - step_id: BM-BUY-03              # 与 DB battle_map_steps.step_id 一致
    name_zh: 四轨融合                # 环节中文名
    name_en: Four-Track Fusion       # 环节英文名
    plain_zh: |                      # 大白话（做什么/解决什么），可被多视图复用
      把模型驱动轨、数据驱动轨、人工指令轨、应急保命轨的信号
      按优先级融合成一个统一信号。人工>模型>数据，应急压制其他。
    mechanism_zh: |                  # 机制说明（怎么运作）
      四轨信号进仲裁器，按优先级表裁决。人工指令轨最高，应急保命轨
      触发时压制其他三轨。融合后产出 buy_signal 进 L3 策略组合层。
    indicators_zh: |                 # 指标文案解释（大段，结构化字段在 DB）
      融合权重：人工0.5/模型0.3/数据0.2。应急触发条件见 Kill Switch 配置。
      置信度低于0.4时降级到模型驱动轨单跑。
```

> **说明**：这就是"顶层段"——YAML 文件顶层除了已有的 `entries:`（模块条目），新增一个平级的 `battle_map_steps:`（环节条目）。复用同一个翻译真源文件和加载器（`_shared/module_translation_loader.py` 扩展），但不和模块条目混。环节级叙事和大白话可被作战地图视图、未来其他视图复用。

### 13.2 indicators JSONB 结构（DB battle_map_steps.indicators）—— 6 件套 + 双向参数

对齐 §5.4 的 6 件套标准。`indicators` 用灵活 JSONB（不同环节结构不同），定义推荐 schema 但允许扩展。结构化部分进 DB，大段解释文案（`indicators_zh`）进翻译真源。

```json
{
  "trigger": {
    "condition": "满足N/M即激活，默认2/3",
    "items": ["调整周期进度≥80%", "二次回落确认", "成交量萎缩(量比<阈值)"],
    "threshold_n": 2,
    "threshold_m": 3
  },
  "consumes": [
    {"name": "调整周期进度", "source_layer": "L2C", "source_module": "MOD-xxx"},
    {"name": "行情生命周期阶段", "source_layer": "L2C", "source_ref": "草图§6.7"},
    {"name": "轮动序列", "source_layer": "L2B", "source_ref": "草图§6.1.3"},
    {"name": "量比", "source_layer": "L0"}
  ],
  "params": [
    {
      "name": "分批数",
      "default": 2,
      "range": "2-4",
      "current_code_value": 2,
      "status": "implemented",
      "code_location": "src/zephyr/.../batch_buy.py:L42"
    },
    {
      "name": "批次间隔",
      "default": "1交易日",
      "current_code_value": "1交易日",
      "status": "implemented",
      "code_location": "src/zephyr/.../batch_buy.py:L58"
    },
    {
      "name": "满足阈值",
      "default": "2/3",
      "status": "proposed",
      "proposed_by": "Owner",
      "proposed_date": "2026-08-01"
    }
  ],
  "data_flow": "进度+阶段+轮动→条件判定→L3.5仓位(分批方案)→L4执行(分批下单)",
  "code_mapping": {
    "primary_module": "MOD-L05-001",
    "file": "src/zephyr/.../batch_buy.py",
    "function": "evaluate_batch_buy_condition"
  },
  "degradation": "跌破前低→暂停后续批次→触发止损评估",
  "indicators_zh_ref": "翻译真源 battle_map_steps.BM-BUY-04.indicators_zh"
}
```

**字段说明**：
- `params[].status`：`implemented`（代码已实现，带 `current_code_value`+`code_location`）/ `proposed`（代码没有，人提议）/ `testing`（回测中）。这是代码↔地图双向反馈的核心。
- `consumes[]`：消费的数据/因子清单，带来源层和模块，可追溯到具体数据源。
- `code_mapping`：主实现模块 + 代码文件 + 函数，AI 能直接定位到代码。
- `indicators_zh_ref`：指向翻译真源的大段解释文案（机制说明、参数讨论、业务逻辑叙述）。

### 13.3 battle_map_anchors.target_graph 值域

| target_graph | target_id 含义 | 来源 |
|---|---|---|
| depgraph | module_id | depgraph.nodes |
| dataflowgraph | dataflow_node_id | dataflow_datasets/jobs |
| decisiongraph | decision_node_id | decision_nodes |
| candidate | candidate_id | candidate_module_registry.yaml entry id |
| blueprint | blueprint_section | docs/03_modules/ 章节锚点 |

---

## 十四、已定决策汇总 + 剩余开放问题

### 14.1 已定决策（V0.2 拍板）

| # | 问题 | 决策 |
|---|---|---|
| Q1 | 环节粒度 | 6 件套标准（§5.4），50-100 个环节，比草图 §1.2-1.6 更细 |
| Q2 | 双向查找实现 | anchors 单一真源 + 全景图模块加派生只读字段（§7.2） |
| Q3 | 旧 trading_flow_panorama.md 处置 | 删除重建，battle_map_panorama.md 替代 |
| Q4 | align_battle_map 门禁强度 | 先君子协定，跑顺再升级硬阻断 |
| Q5 | 表前缀 / 图名 | 图名 `battlemap`（对标 depgraph/dataflowgraph/decisiongraph），表前缀 `battle_map_*`（对标 `decision_*`），不用 `bm_*` 缩写 |
| Q6 | narrative.yaml 退场时机 | 并行观察一段，翻译真源完整覆盖后删除 |

### 14.2 剩余开放问题（待 Owner 拍板或施工时定）

1. **第一批环节清单**：50-100 个环节具体是哪些？需从草图 v9.0 逐章挖掘（§1.1主流程 + §1.2-1.6注解 + §2-12层详解），按 6 件套标准登记。这是施工第一步，建议蓝图定稿后专门做一次"草图→环节清单"的挖掘评审。
2. **panorama_registry 登记**：battle_map 登记为 `PAN-BATTLE-MAP-01`，确认登记号。
3. **battlemap schema 归属**：三图各有 schema 文件（depgraph_schema.py / dataflowgraph_schema.py / decisiongraph_schema.py），新建 `battlemap_schema.py`，确认放 `src/zephyr/governance/persistence/` 下。
4. **indicators 6 件套的必填校验**：哪些件是必填（如 trigger/consumes/code_mapping），哪些可选（如 degradation）？影响 BM-INV 校验。

---

## 十五、变更历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V0.1.0 | 2026-08-01 | 草案：第四全景图 battle_map 设计。三表数据模型 + 翻译真源 battle_map_steps 段 + 双向查找机制 + 取代 trading_flow_panorama.md V1.0.0。 |
| V0.2.0 | 2026-08-01 | Owner 评审反馈落地：① 环节粒度升级为 6 件套标准（§5.4），50-100 个环节，indicators JSONB 扩展为 6 件套 + 双向参数（implemented/proposed/testing）；② 图名定为 battlemap，表前缀 battle_map_*（对标 decision_*）；③ 旧文档处置定为删除重建；④ narrative.yaml 退场定为并行观察；⑤ 双向查找确认 anchors 单真源 + 派生只读字段方案；⑥ 门禁君子协定。 |
