---
ttl: task_bound
---

# BM-PLAN 盲点登记归位——架构师裁定报告

> 日期：2026-08-05
> 主题：明日预案引擎等 6 个盲点如何登记进作战地图
> 方法：第一性原理分析 + 全文档调研 + 长远战略考虑 + 100% AI 开发适配

---

## 一、要解决的问题（大白话）

### 1.1 背景

我们挖出了 6 个作战地图的真盲点（详见 `2026-08-05_battle_map_completion_before_alignment_plan.md` §A3-B）：

| 盲点 | 性质 |
|---|---|
| BM-PLAN-01 明日预案引擎 | 跨买卖仓风的新枢纽环节（有完整 6 件套） |
| BM-PLAN-02 盘前加载 | 新环节（有 6 件套） |
| BM-PLAN-03 尾盘决策 | 新环节（有 6 件套） |
| BM-SEL-04-补 盘中微观节奏 | 已有 BM-SEL-04 的维度补充 |
| BM-SEL-04-补2 涨跌质量 | 已有 BM-SEL-04 的维度补充 |
| BM-SEL-03-补 全市场涨跌停情绪 | 已有 BM-SEL-03 的维度补充 |

现在要把它们登记进作战地图，让作战地图 MD 能显示出来，方便继续讨论。

### 1.2 卡住的点

6 个盲点里，3 个"补维度"的简单（改现有环节的参数就行），但 **3 个 BM-PLAN 新环节归哪个阶段（flow_stage）** 卡住了——因为：

**作战地图有两种"环节"，走两条完全不同的轨道：**

```
轨道 A：battle_map_steps 表（DB）
  ├── 有 6 件套（触发/消费/参数/数据流/降级/代码）
  ├── 归属于 11 个 flow_stage 之一（研究/训练/回测/仿真/选股/买/卖/仓/风控/执行/对账）
  └── DB 有 CHECK 约束：flow_stage 只能填这 11 个值，没有"横切"

轨道 B：battle_map_cross_cutting 段（YAML）
  ├── 横切视图，编号 12
  ├── 结构是"漏斗/事件/冲突矩阵/四模式开关..."这种视角说明
  ├── 不属于任何 flow_stage，是独立第 12 类
  └── 真源是 module_translation_registry.yaml
```

**关键矛盾**：BM-PLAN 是跨买卖仓的横切能力（按性质该走轨道 B），但它有完整 6 件套（按结构该走轨道 A）。两条轨道都不完全匹配。

### 1.3 为什么不能随便选

这是 100% AI 开发的项目。如果归位规则不清晰，后面的 AI 会：
- 看到模式不一致 → 不知该学哪个
- 横切内容乱放 → 4 图对齐失败
- 新增能力时反复争论归位 → 沟通成本爆炸

所以必须**一次定清楚，立规矩**。

---

## 二、调研发现（事实，非推断）

### 2.1 现有"横切"环节是怎么处理的

查 DB，现有 layer='横切' 的 battle_map_steps 只有 2 个：

| step_id | step_name | flow_stage | layer |
|---|---|---|---|
| BM-BUY-06 | 外部指令盯盘 | buy_flow | 横切 |
| BM-BUY-07 | 微信互动中心 | buy_flow | 横切 |

**关键事实**：这两个横切环节**没走轨道 B（YAML），走的是轨道 A（battle_map_steps），flow_stage 填 buy_flow，layer 标记'横切'。**

也就是说——**现有项目已经有"横切环节归到某个 flow_stage + layer 标横切"的先例。** 这不是我发明的，是项目已有的模式。

### 2.2 轨道 B（YAML 横切段）的真实定位

查 `battle_map_12_cross_cutting.md`（57KB）和生成器代码，轨道 B 的 17 个 category 全是**视角/说明类**内容：

| category 类型 | 例子 | 特征 |
|---|---|---|
| 流程视角 | funnel（筛选漏斗）/ intraday_events（盘中事件） | 描述多个环节怎么串 |
| 时序视角 | timeline（计算节奏） | 描述时间安排 |
| 仲裁视角 | conflict_matrix（冲突仲裁） | 描述冲突怎么裁 |
| 体系说明 | four_modes（四模式开关）/ emergency_degradation（应急降级） | 描述系统级机制 |
| 治理说明 | signal_lifecycle / factor_governance | 描述治理流程 |

**轨道 B 的本质是"系统级说明文档"，不是"决策环节"。** 它没有 6 件套（没有触发条件/参数/降级这些字段），结构是 plain_zh + mechanism_zh + levels。

### 2.3 生成器对横切的注释

`generate_battle_map_diagram.py:92` 明确写：
> 横切视图（cross_cutting）单独处理，编号 12（**非 flow_stage**，来自 YAML battle_map_cross_cutting 段）

### 2.4 kimi3 指令文档的规则

`docs/_working/kimi3_battle_map_merge_instructions.md:331-350` 写：
> 横切机制（battle_map_12 cross_cutting）≠ 新 flow_stage（重要区分）
> 横切内容走的是 YAML 轨道（battle_map_cross_cutting 段），不是 flow_stage 步骤

### 2.5 flow_stage CHECK 约束

DB 约束只允许 11 个值，没有 cross_cutting。这是**设计**不是 bug——因为横切视图本就走 YAML，不该进 battle_map_steps。

---

## 三、BM-PLAN 的真实性质判断

### 3.1 BM-PLAN-01 明日预案引擎

| 维度 | 表现 |
|---|---|
| 有 6 件套吗 | ✅ 有（触发=盘后/盘中/盘前；消费=市场状态/次日预测/主力行为；参数=箱体边界/仓位上限/纪律线；数据流=边界生成→加载→实时推演；降级=边界坏=致命；代码=MOD-PLAN-001） |
| 是决策环节还是视角说明 | 决策环节（产出 TomorrowBoundary 契约，驱动实际买卖操作） |
| 跨阶段吗 | ✅ 跨买卖仓风（横切） |
| 类比现有横切环节 | 像 BM-BUY-06 外部指令盯盘（也是横切但有 6 件套，归 buy_flow + layer=横切） |

### 3.2 BM-PLAN-02 盘前加载

同理——有 6 件套，是决策环节（产出 ConstraintState 初始化），跨阶段（驱动买卖仓的初始状态）。

### 3.3 BM-PLAN-03 尾盘决策

同理——有 6 件套，是决策环节（产出尾盘加仓/减仓指令），跨阶段（影响买入+卖出+仓位）。

### 3.4 三个补维度（BM-SEL-04-补/补2、BM-SEL-03-补）

这些不是新环节，是给现有 BM-SEL-04/BM-SEL-03 的 indicators.params 加几个参数。**走 update-step，不走 add-step。**

---

## 四、从第一性原理推导归位规则

### 4.1 核心第一性原理：归位看"结构"不看"语义"

**判定标准：这个东西有没有 6 件套？**

```
有 6 件套（触发/消费/参数/数据流/降级/代码）
  → 是"决策环节" → 走 battle_map_steps（轨道 A）
  → flow_stage 选最贴近的阶段，layer 标"横切"表示横切性质

无 6 件套（只有 plain_zh + mechanism_zh + levels）
  → 是"视角说明" → 走 battle_map_cross_cutting（轨道 B）
```

**为什么用结构不用语义判？** 因为这是 100% AI 开发项目。AI 判"语义横不横切"会主观漂移，但判"有没有 6 件套"是二元可判的（符合项目铁律：规则必须二元可判，灰度规则必死）。

### 4.2 BM-PLAN 走轨道 A 的依据

BM-PLAN-01/02/03 都有完整 6 件套 → 按第一性原理走轨道 A（battle_map_steps）。

### 4.3 flow_stage 选哪个——选 position_management

3 个候选：A=position_management / B=加 cross_cutting 到 CHECK / C=走 YAML

#### 排除 C（走 YAML）

- BM-PLAN 有 6 件套，YAML 段结构不匹配（YAML 是 plain_zh+levels，不是 6 件套）
- 强塞会破坏 YAML 段的结构一致性
- 后续 AI 看 YAML 段会发现结构混乱

#### 排除 B（加 cross_cutting 到 CHECK 约束）

- 按项目铁律，新增 flow_stage 要同步改 DB CHECK + 生成器词表 + 域白名单 + step_id 缩写
- 工作量大（3-5 天），且只为 3 个环节，性价比低
- 更重要的是：**这会破坏"横切走 YAML"的现有架构**。一旦 cross_cutting 进了 CHECK，后面的 AI 就会困惑"横切到底走 A 还是 B"
- kimi3 指令文档明确写了"横切 ≠ 新 flow_stage"，加 CHECK 约束违反这条

#### 选 A（position_management + layer=横切）

**5 条理由**：

1. **有先例**：BM-BUY-06/07 就是这么做的（横切环节归 buy_flow + layer=横切）
2. **不改 schema**：零风险，不动 CHECK 约束/生成器/词表
3. **语义最贴近**：明日预案直接影响仓位决策（加仓/减仓/仓位上限），归仓位管理语义通顺
4. **layer=横切 保留横切标识**：生成器会显示这个标记，不会丢失横切性质
5. **4 图对齐不受影响**：battle_map_steps 是 DB 数据，sync_panorama_module.py 能正常派生

### 4.4 长远战略考虑

#### 场景：未来还有更多横切决策环节怎么办？

按这个规则：**有 6 件套 → 归最贴近的 flow_stage + layer=横切；无 6 件套 → 走 YAML 横切段。**

这个规则的好处：
- **二元可判**（AI 不会漂移）
- **不限制数量**（不管多少横切环节都能归位）
- **保持架构稳定**（不用每次新增都改 schema）

#### 场景：100% AI 开发的适配

AI 冷启动时看到 BM-BUY-06 的先例（layer=横切 + flow_stage=buy_flow），就能学会这个模式。后续遇到横切决策环节，AI 会自动套用"归最贴近阶段 + layer 标横切"，不用每次问人。这符合"防幻觉/防漂移治本规则"。

---

## 五、裁定结果

### 5.1 最终归位方案

| 盲点 | 登记方式 | flow_stage | layer | 理由 |
|---|---|---|---|---|
| **BM-PLAN-01** 明日预案引擎 | add-step（新环节） | position_management | 横切 | 有 6 件套，跨阶段，归仓位管理最贴近 |
| **BM-PLAN-02** 盘前加载 | add-step（新环节） | position_management | 横切 | 同上 |
| **BM-PLAN-03** 尾盘决策 | add-step（新环节） | position_management | 横切 | 同上 |
| **BM-SEL-04-补** 盘中微观节奏 | update-step（改 BM-SEL-04 indicators） | — | — | 维度补充，不是新环节 |
| **BM-SEL-04-补2** 涨跌质量 | update-step（改 BM-SEL-04 indicators） | — | — | 维度补充 |
| **BM-SEL-03-补** 全市场涨跌停情绪 | update-step（改 BM-SEL-03 indicators） | — | — | 维度补充 |

### 5.2 同步登记 depgraph 节点

3 个 BM-PLAN 新环节对应的 depgraph 模块节点：

| module_id | path | domain | build_status |
|---|---|---|---|
| MOD-PLAN-001 | src/zephyr/plan_engine/tomorrow_boundary_planner.py | D_POSITION | planned |
| MOD-PLAN-002 | src/zephyr/plan_engine/premarket_constraint_loader.py | D_POSITION | planned |
| MOD-PLAN-003 | src/zephyr/plan_engine/closing_session_decision.py | D_POSITION | planned |

> domain 选 D_POSITION（仓位管理域），与 flow_stage=position_management 对齐。
> build_status=planned（设计态），不填 acquisition（等方案 A 落地后 backfill）。

### 5.3 BM-SELL-07 的处理

**不改 BM-SELL-07 的归属**（它仍在 sell_flow），只在 BM-PLAN-01 的 indicators.code_mapping 里引用它作为"卖出侧边界提供者"。BM-SELL-07 的 step 本身不动。

### 5.4 6 件套内容（BM-PLAN-01 为例）

```json
{
  "trigger": {
    "condition": "盘后收盘/盘中每15分钟/盘前9:00",
    "threshold": "三层触发（B盘后边界/C盘前加载/A盘中推演）"
  },
  "consumes": [
    {"item": "市场状态", "source": "BM-SEL-03"},
    {"item": "次日预测", "source": "BM-SEL-04"},
    {"item": "主力行为", "source": "BM-SEL-05"},
    {"item": "情绪周期", "source": "BM-SEL-23"},
    {"item": "板块轮动", "source": "BM-SEL-08"}
  ],
  "params": [
    {"name": "箱体上沿", "range": "价格", "default": "昨日冷静算", "status": "proposed"},
    {"name": "箱体下沿", "range": "价格", "default": "昨日冷静算", "status": "proposed"},
    {"name": "加仓仓位上限", "range": "0-100%", "default": "30%", "status": "proposed"},
    {"name": "禁加仓价位", "range": "价格", "default": "接近上沿", "status": "proposed"},
    {"name": "必出止盈价位", "range": "价格", "default": "冲上沿必出", "status": "proposed"}
  ],
  "data_flow": {
    "input": "市场状态+次日预测+主力行为+情绪周期",
    "process": "双层架构：B盘后生成TomorrowBoundary→C盘前加载ConstraintState→A盘中推演在边界内执行",
    "output": "TomorrowBoundary/ConstraintState/BoundedActionAdvice",
    "downstream": "BM-BUY/BM-SELL/BM-POS 初始指令"
  },
  "degradation": {
    "action": "边界层(B/C)坏=致命，暂停操作；推演层(A)坏=可接受，机械执行边界",
    "condition": "边界比聪明更重要"
  },
  "code_mapping": {
    "module_id": "MOD-PLAN-001",
    "source_ref": "草图§明日预案（BM-PLAN 设计）+ BM-SELL-07 卖出侧边界提供者"
  }
}
```

### 5.5 执行步骤

```
1. apply_depgraph --add-design-node（3 个 PLAN 节点，planned，不填 acquisition）
2. apply_depgraph --add-edge（PLAN 依赖边：5 个进水管 + 3 个出水管）
3. apply_battle_map --add-step（3 个 BM-PLAN 环节，flow_stage=position_management，layer=横切）
4. apply_battle_map --add-anchor（3 个环节↔3 个模块的锚点）
5. apply_battle_map --update-step（改 BM-SEL-04/03 的 indicators，加补维度参数）
6. sync_panorama_module.py（派生其他 3 图）
7. generate_battle_map_diagram.py（重新生成 battle_map MD）
```

---

## 六、规则固化（写进项目记忆）

这次的裁定要固化成一条规则，防止后续 AI 重复争论：

> **横切决策环节归位规则（2026-08-05 裁定）**：
> - 有 6 件套的横切决策环节 → 走 battle_map_steps，flow_stage 选最贴近的阶段，layer 标"横切"
> - 无 6 件套的横切视角说明 → 走 YAML battle_map_cross_cutting 段
> - 判定标准二元化：看有没有 6 件套，不看语义横不横切
> - 禁止给 flow_stage CHECK 约束加 cross_cutting（会破坏横切走 YAML 的架构）
> - 先例：BM-BUY-06/07（横切归 buy_flow + layer=横切）、BM-PLAN-01/02/03（横切归 position_management + layer=横切）

---

## 变更日志

| 日期 | 变更 |
|---|---|
| 2026-08-05 | 初版裁定：BM-PLAN-01/02/03 归 position_management + layer=横切；3 个补维度走 update-step；BM-SELL-07 不改归属只改引用 |
