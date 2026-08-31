---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=design_draft · owner=ZephyrAlpha-Owner · status=draft_pending_review · version=0.2.0 · date=2026-08-31 · topic=frontend_governance_four_piece。
>
> **文档性质**：**草案（待 Owner 审）**。Owner 裁定转正后按性质分流——前端技术手册/模块契约/验收单模板 → `docs/03_modules/_domain_frontend/`；前端全景图定位书 → `docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/`（与另五张全景图定位书同区）。
>
> **背景**：前端（含实盘交易/量化回测/未来 AI 反馈）工作量不亚于后端，AI 会话间出现"前脚做完后脚忘、同一功能反复返工、踩过的坑重复踩"三类实证事故（成本线七返工、图标消失无人发现、priceLine 三小时试错）。本草案定义四件治理件：**技术手册（怎么做）+ 全景图（在哪）+ 模块契约（边界）+ 验收单/冒烟测试（做对没有）**，目标=让弱模型也能"查表代替猜路径、查坑代替试错、对单代替发挥、测试兜底"。
>
> **v0.2.0 说明**：按新《文档审查与优化 SOP》（document_review_and_optimization_sop.md）对 v0.1.0 执行了七轮循环审查，本轮=第 1~7 轮全量过一遍，发现已修订入正文，审查日志见 §七。

# 前端治理四件套草案（讨论稿 v0.2）

## 〇、四件套关系一句话

| 件 | 管什么 | 类比 | 开源对应物结论 |
|---|---|---|---|
| 前端技术手册 | 怎么做（事实/坑/做法） | 施工手册 | 自建（ADR 工具不合项目，ADR 已全删） |
| 功能验收单 | 什么样子算对（冻结标准） | 质检单 | 单自建 YAML；执行引擎搬 Playwright（Python 版） |
| 前端模块契约 | 边界（散件化、单文件功能） | 零件标准 | 自建薄契约（微前端框架=过度工程，只借 VS Code 插件 manifest 思想） |
| 前端全景图 frontend_map | 在哪（页面→功能→代码→后端） | 地图 | 自建（第六全景图，接入既有 panorama_alignment_gate 对齐门禁） |

---

## 一、前端技术手册（fe_handbook）草案

### 1.1 定位与边界
- 记"**怎么做**"的**事实库**：内置能不能做、坑是什么、正确做法、代码锚点。
- **不是决策记录**：与裁定（ruling_registry，可推翻、superseded_by 链）/设计备忘录（可修订设计）严格分家。手册条目是事实，不存在"推翻"，只有"补充/修正"，**直接改原文**。
- 与 KB 决策记录的关系：手册只收前端施工事实；凡涉及"为什么这么选"的决策归属裁定体系，手册条目可附裁定号引用但不复制内容。

### 1.2 形态
- 目录：`docs/03_modules/_domain_frontend/fe_handbook/`，**按库分文件**（防单文件臃肿——实证依据：AI_review_instructions 单文件 142KB 已超 Read 工具 128KB 上限，单文件路线在条目增多后会撞同一堵墙）：
  - `klinecharts.md`（K 线图库）、`dockview.md`（布局引擎库）、`native_browser.md`（浏览器原生：缓存/事件/CSS）、`project_conventions.md`（项目自有约定：破缓存、overlay 分组、图标栏等）
- 每文件内条目用固定小标题结构，**编号永久稳定不回收**（同裁定号纪律）。
- **编号库代码对照表**（条目号第三段，新增库时扩表不改动号）：

  | 代码 | 指代 | 对应文件 |
  |---|---|---|
  | KLC | KLineChart（K 线图库） | klinecharts.md |
  | DV | Dockview（布局引擎库） | dockview.md |
  | NB | 浏览器原生（缓存/事件/CSS） | native_browser.md |
  | PC | 项目自有约定 | project_conventions.md |

### 1.3 条目 schema（每条条目字段）
```
### FEH-KLC-001｜价格横线类 overlay（priceLine）
- 触发词：成本线 / 价格线 / priceLine / overlay 横线 / 价签      ← AI 按任务关键词命中即读
- 想做什么：画一条横跨主图的价格水平线，不要任何价签/文字
- 内置能否：❌ 内置 priceLine 模板的蓝底价签删不掉（实证：3 小时试错后放弃）
- 坑：①内置模板部件不可单独隐藏 ②points 传 timestamp 会锚定异常不渲染，只传 {value}
- 正确做法：自注册纯横线模板（plainLine），代码锚点 app1.js:5934 注册处
- 代码锚点：src/zephyr/frontend/dashboard/web/core/app1.js#L5934
- 来源：commit 51915c64a8 · 2026-08-31
```

### 1.4 积累机制（铁律延伸）
- **踩坑解决即入册**：任何"试了两次以上才解决"的前端问题，解决当次 commit 必须带手册条目（随码提交）。
- **更新触发**：①踩坑解决时；②每个前端功能 commit 前自检"本次有没有试两次以上的坑"；③既有条目做法失效时（库升级/换方案）。
- 条目只增改不删；做法过时→改原文+更新日期，旧做法一句话留痕（"曾用 X，因 Y 废弃"）。

---

## 二、功能验收单（acceptance checklist）草案

### 2.1 定位
- 冻结"**什么样子算对**"。成本线七返工的根因=标准从未冻结，AI 有自由发挥空间。验收单冻结后，改完逐条对，**全过才算完**。
- 每条验收项两种校验方式之一：`目检`（截图人工/AI 视觉对）或 `机断`（DOM 断言，可进冒烟测试）。
- **修订权限**：验收单是冻结标准，**只有 Owner 能改**；AI 可提议修订（写在草案/对话里），不可自改已冻结条项。

### 2.2 形态与 schema
- 目录：`docs/03_modules/_domain_frontend/acceptance/`，每功能点一个 YAML：`ACC-<功能id>.yaml`
```yaml
feature_id: F-STOCKQ-COSTLINE        # 与 frontend_map 功能点 id 互挂
feature_name: 持仓成本线
frozen_at: 2026-08-31                # 冻结日期；修订=Owner 批准+改原文+revision 链留痕
revision: 1
items:
  - { id: 1, text: "黄色虚线横跨主图，线色=琥珀/黄", check: 目检 }
  - { id: 2, text: "y 轴与线端均无价签、无文字", check: 目检 }
  - { id: 3, text: "¥ 开关独立控制显隐，不影响其他 overlay 组", check: 目检 }
  - { id: 4, text: "悬停显示琥珀色提示框（成本/数量）", check: 目检 }
  - { id: 5, text: "overlay 已注册（chart 上存在 cost 组 overlay）", check: 机断 }
  - { id: 6, text: "¥ 按钮存在于工具栏且图标渲染非空", check: 机断 }
```

### 2.3 执行纪律
- 任何 UI 改动 commit 前：起本地服务 → 截图 → 逐条对验收单 → 全绿才走 GitCommitGateway。
- 新功能上线 = 代码 + 验收单 + （涉前端时）frontend_map 条目，三件套同 commit。
- **过渡态说明**：Playwright 冒烟（施工第 5 步）落地前，"机断"条款由人工/AI 在浏览器控制台手动执行等价断言；落地后转自动跑。过渡期"机断"不免验，只是手动验。

---

## 三、前端模块契约（fe_module）草案

### 3.1 定位与边界（重要）
- 功能散件化：**代码组织层面的隔离，不是运行时隔离**——KLineChart 是单 canvas 实例，所有模块共享 chart 对象。不引入微前端框架。
- 每个功能=一个独立文件 `web/features/<id>.js`，共享大文件（app1.js）只留一行注册。

### 3.2 契约 schema（manifest 条目）
- 注册表：`web/features/manifest.yaml`（兼作 frontend_map 数据源之一）
```yaml
- id: cost-line
  name: 持仓成本线
  file: features/cost-line.js          # 单文件全包：模板注册/绘制/开关/样式自注入
  page: stockq
  init: "init(chart, ctx)"             # 入参：图表实例 + 上下文（事件总线/数据口）
  destroy: "destroy()"
  depends: [klinecharts]               # 显式依赖声明；禁止隐式跨模块摸对方 DOM/状态
  toggle: "¥ 开关（工具栏）"
  styles: self-injected                # 样式随模块注入，不写全局 main.css
  acceptance: ACC-F-STOCKQ-COSTLINE    # 挂验收单
  handbook: [FEH-KLC-001]              # 挂手册条目
```
- 通信纪律：模块间只允许经 `ctx` 事件总线交互；**禁止跨模块直接改对方 DOM/状态**（防散件重新缠成一坨）。
- 模块废弃：manifest 条目标 `status: deprecated` + 文件保留一个版本周期后删除，全景图同步标"已退役"（编号不回收）。

### 3.3 迁移策略（不一次重写 app1.js）
0. **前置（隐含工作量，勿低估）**：`ctx` 事件总线当前**不存在**——试点第一步先造一个薄发布订阅器（目标 ≤50 行，放 `web/core/`），否则模块间无合规通信通道；
1. 新功能一律模块制；
2. **成本线、事件行先抽出来当样板**（最爱改的两个，验证契约够用不够用）；
3. 样板跑通后再逐步迁其余功能，app1.js 只减不增。

---

## 四、前端全景图（frontend_map，第六全景图）草案

### 4.1 定位
- **索引层真源图**，与作战地图（battle_map）同定位：不 invent 新东西，所有锚点指向已存在的代码/接口/另五图节点。
- 前五图管"后端有什么、怎么连、为什么"；第六图管"**用户看见什么、点哪触发什么、数据从哪来**"。
- 与既有《前端有→后端没有缺口总账》关系：缺口总账是"缺口篇"，frontend_map 是全量正式版；map 建成后总账改为从 map 派生（状态=未建/缺后端的子集视图），两账不再手工双写。
- **与既有 frontend_model.yaml 的关系**（v0.2 第 1 轮盘点新发现）：`architecture_model/frontend/frontend_model.yaml` 已存在，是"前端模块清单+技术栈选型"的 SSoT stub（自标 G0 未激活，与"前端已实际建成"的现实脱节，本身需修正）。分工建议：**frontend_model.yaml 管模块注册（模块 ID/状态/技术栈），frontend_map 管页面→功能点索引**，两者同区并存、互链不重复。

### 4.2 层级与 schema
- 存储：YAML 真源 `architecture_model/frontend/frontend_map.yaml`（与 frontend_model.yaml 同区；机器可读=弱模型防幻觉第一闸），派生人类视图 md。
- 三级：页面 page → 模块 module → 功能点 feature。
```yaml
pages:
  - id: P-STOCKQ
    name: 个股行情页
    route: "#stockq"
    file: pages/stockq.html
    modules:
      - id: M-KLINE-MAIN
        name: K线主图
        features:
          - id: F-STOCKQ-COSTLINE
            name: 持仓成本线
            code_ref: features/cost-line.js        # 或 app1.js#L5934（未模块化前，锚点已核实）
            backend_ref: [chip_distribution]       # blueprint 模块锚点（示例，建map时须核实回填）
            data_flow: df_chip_avg_cost            # dataflowgraph 节点锚点（示例，建map时须核实回填）
            api: /api/chips/avg_cost               # 后端接口（示例，建map时须核实回填；缺口期填 GAP-F-xx）
            interaction: "¥开关控显隐；悬停出成本/数量"
            status: 已建                            # 已建/在建/未建/勿动/已退役
            acceptance: ACC-F-STOCKQ-COSTLINE
            do_not_touch: "plainLine 模板勿换回内置 priceLine（FEH-KLC-001）"
```

### 4.3 六图对齐规则
- **三向锚定**：feature.backend_ref ↔ blueprint 模块 ↔ depgraph 节点，由既有 `panorama_alignment_gate`（commit 门禁）扩一个 frontend 维度巡检。
- **候选池不对齐**：CAND 是未建的点子，无实体可对齐；**对齐发生在转正那一刻**——CAND 转正 commit 若涉前端，必须同 commit 登记 frontend_map 条目，否则门禁拦截（"自动对齐"=门禁强制，不靠自觉）。
- **勿动项字段**（do_not_touch）：防"前脚说完后脚忘"的关键设计，会话接手时读本字段即知雷区。
- **更新触发**：新页面/新功能/改交互/改接口四件事发生时同 commit 更新 map；既有对齐门禁报漂移时修正。

### 4.4 前沿演进方向（2026-08-31 搜索登记，第 4 轮产物）
- 2026 行业主流形态=**组件注册表 + 机器可读单一真源**（shadcn 风格 registry endpoint、design system contracts 设计系统契约、MCP 工具供 AI 查询）——本草案 frontend_map + manifest.yaml 方向与主流吻合，且"机器可读契约防 AI 生成幻觉组件"正是弱模型防漂移的同思路。
- 设计令牌（design tokens）：行业主流=W3C 格式 + Style Dictionary 转换管线——对单人项目过重，维持 CSS variables 单文件即够，不引入。
- 视觉回归：行业主流=Chromatic（商业）——咱们 Playwright 截图+验收单是平替，够用。

---

## 五、施工顺序（已定，五步走）

| 序 | 步 | 产出 | 理由 |
|---|---|---|---|
| 1 | 技术手册骨架+首批条目 | fe_handbook/ 四文件；首批收录本轮实证坑：plainLine 价签、points 只传 {value}、K 线价格域取值、破缓存机制、事件行收展、init 顺序契约（init→setSymbol→setPeriod→setDataLoader，forward/backward 返回空数组） | 零基建成本，下次开发立刻见效 |
| 2 | 验收单模板+样板单 | acceptance/ 目录 + ACC-F-STOCKQ-COSTLINE 样板 + 截图目检纪律写入手册 | 冻结标准，止住返工 |
| 3 | 模块契约+成本线试点 | 薄事件总线（≤50 行）+ manifest.yaml + features/cost-line.js 抽离 | 用最爱改的功能验证契约 |
| 4 | frontend_map 骨架 | YAML schema + 先录 stockq/overview 两页 + 接入对齐门禁 | 把前三件元数据汇成真源 |
| 5 | Playwright 冒烟测试 | 机断条项自动跑（pip 生态，与项目 Python 栈契合） | 图标消失类回归当场拦截 |

## 六、待 Owner 裁定项（附 AI 推荐意见，Owner 点头即定）

> 按项目铁律（不擅自定决策），AI 只给推荐，裁定权属 Owner。

1. 手册命名 `fe_handbook`——**推荐采用**（短、机读友好，与 ruling_registry 风格一致）。
2. 手册分文件粒度——**推荐按库四文件**（实证：AI_review_instructions 单文件 142KB 已超 Read 上限，单文件路线条目多了必撞墙）。
3. frontend_map 真源路径——**推荐 `architecture_model/frontend/frontend_map.yaml`**（v0.2 修正：与既有 frontend_model.yaml 同区并存，不再放 architecture_model/ 根）。
4. 功能点编号规则 F-<页面>-<名>——**推荐采用**（与 BM-/GAP-/CAND- 编号风格一致）。
5. 缺口总账两册去留——**推荐改派生视图**（单一真源防双写漂移；总账曾被误删的教训指向真源集中+git 追踪）。
6. **（v0.2 新增）frontend_model.yaml 漂移处理**：该 stub 自标"G0 前端未建立"，与"前端已建成运营"现实脱节，且多处引用 grep 不到的 frontend_principles.md——**推荐**：建 map 时同 commit 修正其状态（G0→实际档位），并核对其引用的 principles 文件去向；frontend_map 与其并存分工（§4.1）。

## 七、七轮审查日志（v0.1.0→v0.2.0，按 document_review_and_optimization_sop 执行）

| 轮 | 发现 | 处置 |
|---|---|---|
| 1 基础设施盘点 | ✅ 锚点核验通过（app1.js:5934 plainLine 注册、panorama_alignment_gate.py 存在、_domain_frontend/ 在位）；⚠️ 新发现 architecture_model/frontend/frontend_model.yaml G0 stub 与现实脱节 | 修正草案路径建议+新增裁定项 6 |
| 2 内容审查 | 自审 4 点成立（示例锚点未标注/机断过渡空窗/事件总线隐含工作量/库代码表缺失） | §1.2/§2.3/§3.3/§4.2 已修订 |
| 3 缺失环节 | 缺更新触发机制（手册/map）、缺验收单修订权限、缺模块废弃流程 | §1.4/§2.1/§2.3/§3.2/§4.3 已补 |
| 4 前沿搜索 | 2026 行业主流=注册表+机器可读契约，方向吻合 | §4.4 登记 |
| 5 过度工程 | 四件套全过 system_charter §2 硬边界（单人/单机/零外部交付）；Style Dictionary/Chromatic 判定过重不引入 | 无修订，结论留痕 §4.4 |
| 6 一致性 | 草案§四与 frontend_model.yaml 职责重叠 | §4.1 补分工声明 |
| 7 形式规范 | v0.1 缺修订记录节 | 本节即修订记录 |

**修订记录**

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 0.1.0 | 初稿四件套 schema | Owner 指令出草案 |
| 2026-08-31 | 0.2.0 | 七轮审查修订：4 自审点+盘点新发现（frontend_model.yaml）+3 缺失机制+前沿登记+形式补全 | 按新 SOP 狗食审查（dogfooding，用自己定的流程审自己） |
