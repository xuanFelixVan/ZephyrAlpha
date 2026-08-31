---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=design_draft · owner=ZephyrAlpha-Owner · status=draft_pending_review · version=0.3.0 · date=2026-08-31 · topic=frontend_governance_four_piece。
>
> **文档性质**：**草案（六项裁定已于 2026-08-31 全部落定，见 §六）**。转正后按性质分流——前端技术手册/模块契约/验收单模板 → `docs/03_modules/_domain_frontend/`；前端全景图定位书 → `docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/`（与另五张全景图定位书同区）。
>
> **背景**：前端（含实盘交易/量化回测/未来 AI 反馈）工作量不亚于后端，AI 会话间出现"前脚做完后脚忘、同一功能反复返工、踩过的坑重复踩"三类实证事故（成本线七返工、图标消失无人发现、priceLine 三小时试错）。本草案定义四件治理件：**技术手册（怎么做）+ 全景图（在哪）+ 模块契约（边界）+ 验收单/冒烟测试（做对没有）**，目标=让弱模型也能"查表代替猜路径、查坑代替试错、对单代替发挥、测试兜底"。
>
> **版本沿革**：v0.1.0 初稿 → v0.2.0 按新《文档审查与优化 SOP》七轮审查修订 → v0.3.0 Owner 六项裁定落地（命名改 frontend_handbook／手册九类分类法／第六图混合制形态／统一对账字段设计／frontend_model.yaml 删除重做）。

# 前端治理四件套草案（v0.3，六项已裁定）

## 〇、四件套关系一句话

| 件 | 管什么 | 类比 | 开源对应物结论 |
|---|---|---|---|
| 前端技术手册 | 怎么做（事实/坑/做法） | 施工手册 | 自建（ADR 工具不合项目，ADR 已全删） |
| 功能验收单 | 什么样子算对（冻结标准） | 质检单 | 单自建 YAML；执行引擎搬 Playwright（Python 版） |
| 前端模块契约 | 边界（散件化、单文件功能） | 零件标准 | 自建薄契约（微前端框架=过度工程，只借 VS Code 插件 manifest 思想） |
| 前端全景图 frontend_map | 在哪（页面→功能→代码→后端）+ 前后端对账 | 地图+自动对账机 | 自建（混合制：git YAML 真源 + 数据库派生副本，同依赖全景图模式） |

---

## 一、前端技术手册（frontend_handbook）草案

### 1.1 定位与边界
- 记"**怎么做**"的**事实库**：内置能不能做、坑是什么、正确做法、代码锚点。**第一读者是 AI（含未来弱模型）**，命名与行文以机器零歧义为先。
- **不是决策记录**：与裁定（ruling_registry，可推翻、superseded_by 链）/设计备忘录（可修订设计）严格分家。手册条目是事实，不存在"推翻"，只有"补充/修正"，**直接改原文**。
- 与 KB 决策记录的关系：手册只收前端施工事实；凡涉及"为什么这么选"的决策归属裁定体系，手册条目可附裁定号引用但不复制内容。

### 1.2 形态与分类法（已裁定：九类预留、按需建文件）
- 目录：`docs/03_modules/_domain_frontend/frontend_handbook/`。
- **分类法一次定死，文件按需创建**：类别按"坑的技术成因"分（不按踩坑历史分——历史只反映做过什么，不反映会踩什么）；哪个领域踩了第一个坑就建哪个文件，**编号段永久预留不回收**。
- **分类对照表**（编号第三段）：

  | 代码 | 类 | 文件 | 管什么 |
  |---|---|---|---|
  | KLC | KLineChart 图表库 | klinecharts.md | K 线/overlay/指标/画线 |
  | DV | Dockview 布局引擎 | dockview.md | 面板/布局/拖拽/锁定 |
  | DAT | 数据层 | data_api.md | 接口对接、数据格式、轮询推送 |
  | STA | 状态与存储 | state_storage.md | localStorage、布局持久化、页面状态 |
  | CSS | 样式系统 | styling.md | CSS 变量、主题、图标、间距 |
  | NB | 浏览器原生 | browser_native.md | 缓存、事件、DPR/canvas、控制台 |
  | LOAD | 加载与依赖 | loading_vendor.md | loader、破缓存、vendor 库管理 |
  | PC | 项目约定 | project_conventions.md | commit、验收、截图目检纪律 |
  | PG | 页面级 | page_\<页面名\>.md | 页面特有复杂逻辑（如 stockq 画线系统），按需生 |

- 参照系说明：量化社区无公开知识分类法可抄（前端大多买现成组件，不是主战场）；本分类参照大厂工程手册/设计系统文档的"按技术域分层"实践，并结合项目实证。

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
- 新功能上线 = 代码 + 验收单 + frontend_map 条目，三件套同 commit。
- **过渡态说明**：Playwright 冒烟（施工第 5 步）落地前，"机断"条款由人工/AI 在浏览器控制台手动执行等价断言；落地后转自动跑。过渡期"机断"不免验，只是手动验。

---

## 三、前端模块契约（fe_module）草案

### 3.1 定位与边界（重要）
- 功能散件化：**代码组织层面的隔离，不是运行时隔离**——KLineChart 是单 canvas 实例，所有模块共享 chart 对象。不引入微前端框架。
- 每个功能=一个独立文件 `web/features/<id>.js`，共享大文件（app1.js）只留一行注册。

### 3.2 契约 schema（manifest 条目）
- 注册表：`web/features/manifest.yaml`（兼作 frontend_map 前端侧清单的生成源之一）
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

## 四、前端全景图（frontend_map，第六全景图）草案（已裁定：混合制 + 统一对账）

### 4.1 定位与第一性原理
- **索引层真源图**，与作战地图（battle_map）同定位：不 invent 新东西，所有锚点指向已存在的代码/接口/另五图节点。
- 前五图管"后端有什么、怎么连、为什么"；第六图管"**用户看见什么、点哪触发什么、数据从哪来**"+ **前后端自动对账**。
- **第一性原理**（Owner 2026-08-31 定调）：缺口问题（前端有后端没有/后端有前端没有）的本质=**两侧各自手工记账、靠人对账**。根治=三条：
  1. **事实只有三种**：前端有什么（页面/功能）、后端有什么（模块）、谁连着谁（引用关系）；
  2. **每种事实只登记一次**：模块在模块注册体系登记，前端功能在前端清单登记，连接关系写成两边的字段；
  3. **账本是派生物不是手工事实**：两本缺口总账 = 机器查询自动生成，**停止手工维护**。

### 4.2 混合制形态（已裁定）
- **前端侧清单**：`architecture_model/frontend/frontend_map.yaml`（页面→模块→功能点三级），**尽量从 manifest.yaml + 页面扫描半自动生成**；手工只维护生成器够不着的部分（交互描述、do_not_touch、状态理由）。
- **模块侧字段**：在既有模块注册体系（module_id_registry / blueprint 注册）上**加字段**，不另建 3000 模块新表（见 §4.3）。
- **派生副本**：governance.db 存同步副本供 SQL 联查（3000 模块级对账）——与依赖全景图同款双态（git YAML 真源 + DB 派生），门禁读文件、联查读库。
- **派生人类视图**：md 视图 + 两本缺口视图全部自动生成。

### 4.3 统一对账字段设计（核心新增）
```yaml
# 模块侧（每个后端模块注册条目加三字段）
has_frontend: yes | no | planned
no_frontend_reason: 纯计算引擎 | 数据管道 | 治理内部件 | 基础设施   # has_frontend=no 时必填（"事出有因"）
frontend_ref: F-STOCKQ-COSTLINE    # has_frontend=yes 时指向具体前端功能点，可多个

# 前端侧（frontend_map 每个功能点条目）
backend_ref: chip_distribution      # 挂空/悬空 = "前端有后端没有"缺口，自动上榜
```
- **为什么没有前端的模块是合法的**：前端的本质是"给人看、给人点的界面"；纯计算引擎/数据管道/治理脚本/内部库是机器调机器，没有人机交互面——**没有前端是正确设计不是缺陷**。所以字段不是"必须都有前端"，而是"**必须都有声明**"。
- **两本缺口总账变成两条自动查询**：
  - 前端有后端没有 = `frontend_ref 有值 但 backend_ref 空/悬空`
  - 后端有前端没有 = `has_frontend=yes/planned 但 frontend_ref 空`
  - 对账异常 = `has_frontend=no 但 no_frontend_reason 空`
- 现有《前端有→后端没有缺口总账》83 项 + 反向账 40 项 = 字段回填的**种子数据**，回填完成后两账改派生视图，停止手工维护（已裁定）。

### 4.4 前端侧清单 schema（三级）
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
            backend_ref: [chip_distribution]       # 模块锚点（示例，建map时须核实回填；缺口期留空即自动上榜）
            data_flow: df_chip_avg_cost            # dataflowgraph 节点锚点（示例，建map时须核实回填）
            interaction: "¥开关控显隐；悬停出成本/数量"
            status: 已建                            # 已建/在建/未建/勿动/已退役
            acceptance: ACC-F-STOCKQ-COSTLINE
            do_not_touch: "plainLine 模板勿换回内置 priceLine（FEH-KLC-001）"
```

### 4.5 六图对齐规则
- **三向锚定**：feature.backend_ref ↔ blueprint 模块 ↔ depgraph 节点，由既有 `panorama_alignment_gate`（commit 门禁）扩一个 frontend 维度巡检。
- **候选池不对齐**：CAND 是未建的点子，无实体可对齐；**对齐发生在转正那一刻**——CAND 转正 commit 若涉前端，必须同 commit 登记 frontend_map 条目+模块侧字段，否则门禁拦截。
- **勿动项字段**（do_not_touch）：防"前脚说完后脚忘"的关键设计，会话接手时读本字段即知雷区。
- **更新触发**：新页面/新功能/改交互/改接口四件事发生时同 commit 更新；对齐门禁报漂移时修正。
- **新模块注册门禁**：注册新模块必填 has_frontend（+理由/引用），否则门禁拦截。

### 4.6 既有 frontend_model.yaml 处置（已裁定：删除重做）
- 该文件自标"G0 前端未物理建立"，与"前端已建成运营"现实脱节，且多处引用已丢失的 frontend_principles.md——**内容为空壳、状态为假、引用悬空，无保留价值**。
- 处置：建 frontend_map 同 commit **删除旧 stub**，其"前端模块注册+技术栈 SSoT"职责由新体系吸收（模块注册=统一对账字段；技术栈选型=frontend_map 头部 tech_stack 节），历史可从 git 查。

### 4.7 前沿演进方向（2026-08-31 搜索登记，七轮审查第 4 轮产物）
- 2026 行业主流形态=**组件注册表 + 机器可读单一真源**（shadcn 风格 registry endpoint、design system contracts 设计系统契约、MCP 工具供 AI 查询）——本方案"注册表+字段+派生查询"与主流吻合，且"机器可读契约防 AI 生成幻觉组件"正是弱模型防漂移的同思路。
- 设计令牌（design tokens）：行业主流=W3C 格式 + Style Dictionary 转换管线——对单人项目过重，维持 CSS variables 单文件即够，不引入。
- 视觉回归：行业主流=Chromatic（商业）——咱们 Playwright 截图+验收单是平替，够用。

---

## 五、施工顺序（已裁定，六步走）

| 序 | 步 | 产出 | 理由 |
|---|---|---|---|
| 1 | 技术手册骨架+首批条目 | frontend_handbook/（按需建首批文件：klinecharts/browser_native/loading_vendor/project_conventions）；首批收录本轮实证坑：plainLine 价签、points 只传 {value}、K 线价格域取值、破缓存机制、事件行收展、init 顺序契约（init→setSymbol→setPeriod→setDataLoader，forward/backward 返回空数组） | 零基建成本，下次开发立刻见效 |
| 2 | 验收单模板+样板单 | acceptance/ 目录 + ACC-F-STOCKQ-COSTLINE 样板 + 截图目检纪律写入手册 | 冻结标准，止住返工 |
| 3 | 模块契约+成本线试点 | 薄事件总线（≤50 行）+ manifest.yaml + features/cost-line.js 抽离 | 用最爱改的功能验证契约 |
| 4a | frontend_map 骨架 | frontend_map.yaml（先录 stockq/overview 两页）+ 删除旧 frontend_model.yaml（同 commit）+ 接入对齐门禁 | 前端侧清单先立 |
| 4b | 模块侧字段回填 | 模块注册体系加 has_frontend 三字段；用两本缺口总账 83+40 项作种子回填 | 对账机通电 |
| 4c | 缺口视图派生器 | 生成器：从 map+模块字段自动出两本缺口视图；原总账停手工维护 | 手工记账终结 |
| 5 | Playwright 冒烟测试 | 机断条项自动跑（pip 生态，与项目 Python 栈契合） | 图标消失类回归当场拦截 |

## 六、裁定记录（2026-08-31 全部落定）

| # | 裁定项 | 结论 | 第一性原理依据 |
|---|---|---|---|
| 1 | 手册命名 | **frontend_handbook**（弃 fe 缩写） | 第一读者是 AI（含弱模型），零歧义优先于打字长度（Owner 提出，AI 附议） |
| 2 | 手册分类 | **九类预留、按需建文件**（§1.2 表） | 按坑的技术成因分类，不按踩坑历史分类；编号段永预留 |
| 3 | map 存储 | **混合制**：git YAML 真源（architecture_model/frontend/frontend_map.yaml）+ governance.db 派生副本 | 真源要审计链/diff/门禁可读→git；3000 模块联查→DB；同依赖全景图双态模式 |
| 4 | 编号规则 | **F-\<页面\>-\<名\>** | 与 BM-/GAP-/CAND- 同风格，引用可机读解析 |
| 5 | 缺口总账 | **停止手工维护，改自动派生视图**（升级为统一对账字段设计，§4.3） | 账本=事实的派生物，事实只登记一次（Owner 主推） |
| 6 | frontend_model.yaml | **删除重做**（建 map 同 commit 删旧 stub，职责由新体系吸收） | 空壳+假状态+悬空引用，无沉没成本，不留"事实地雷"（Owner 裁定） |

## 七、审查与修订日志

| 版本 | 触发 | 发现 | 处置 |
|---|---|---|---|
| v0.1.0→v0.2.0 | 按新文档审查 SOP 七轮循环 | 4 自审点成立；frontend_model.yaml 漂移新发现；缺更新触发/验收单权限/模块废弃三机制；前沿方向获 2026 行业验证；无过度工程项；缺修订记录节 | 全部修入 v0.2.0 |
| v0.2.0→v0.3.0 | Owner 六项裁定+第一性原理重推 | 命名机器可读性优先；分类法按成因不按历史；存储双态同依赖全景图；缺口总账升级统一对账；model stub 删除重做 | 全部修入 v0.3.0（§六裁定记录） |

**修订记录**

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 0.1.0 | 初稿四件套 schema | Owner 指令出草案 |
| 2026-08-31 | 0.2.0 | 七轮审查修订 | 按新 SOP 狗食审查（dogfooding，用自己定的流程审自己） |
| 2026-08-31 | 0.3.0 | 六项裁定落地：命名/九类分类/混合制存储/编号/统一对账字段/model 删除重做；§六转裁定记录；施工顺序扩为六步 | Owner 裁定收口，草案可转施工 |
