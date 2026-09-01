---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 前端组件拆分与数据接通 SOP（stockq 页实证）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-01
topic: frontend_component_split_sop
scope: frontend
depends_on:
  - trae_086_frontend_module_construction
related_issues: []
related_modules:
  - src/zephyr/frontend/dashboard/api_server.py
  - src/zephyr/frontend/dashboard/web/core/loader.js
  - src/zephyr/frontend/dashboard/web/features/manifest.yaml
  - src/zephyr/frontend/dashboard/web/frontend_map.yaml
---

# 前端组件拆分与数据接通 SOP（stockq 页实证）

> **来源**：2026-09-01 stockq 页 sq-stock-header / sq-search-box 拆分实证。
> **核心原则**：单一功能 = 单一组件 = 积木（TRAE-086）。
> **目标**：拆件 → 登记 → 接数据 → 验收 → 提交，四件套闭环。

---

## 〇、开工前必读（AI 冷启动文件清单）

新会话 AI 执行拆件任务前，**必须按顺序读完以下文件**：

| 序 | 文件 | 读什么 | 为什么读 |
|---|---|---|---|
| 1 | `AGENTS.md` | 「新 AI 必读三件套」+ RULE-WORKTREE + 提交规范 | 项目总纲，知道规矩再动手 |
| 2 | `docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml` | 拆件判据 + 命名规则 + 目录归属 + 四件套闭环 | **本 SOP 的上位规则**，拆件铁律真源 |
| 3 | `docs/01_policies_and_standards/sop/construction_workflow_sop.md` | Step 0 必看清单 + 施工流程 15 步 | 知道自己在哪一步 |
| 4 | `src/zephyr/frontend/dashboard/web/frontend_map.yaml` | 现有功能点清单（page → module_id → file → backend_ref） | 避免重复造轮子，看已有组件 |
| 5 | `src/zephyr/frontend/dashboard/web/features/manifest.yaml` | 模块注册表（id/name/file/page/depends/acceptance） | 新组件必须登记 |
| 6 | `src/zephyr/frontend/dashboard/web/core/loader.js` | 加载链顺序（app1→event_bus→api→features→app2） | 新组件挂接到正确位置 |
| 7 | `src/zephyr/frontend/dashboard/web/core/event_bus.js` | ZK.registerFeature 机制 | 组件怎么注册 |
| 8 | `src/zephyr/frontend/dashboard/web/services/api.js` | 现有 fetch 方法 | 新数据接口怎么加 |
| 9 | `src/zephyr/frontend/dashboard/web/pages/<page>.html` | 页面骨架占位符 id | 组件往哪渲染 |
| 10 | `docs/03_modules/_domain_frontend/acceptance/ACC-F-STOCKQ-COSTLINE.yaml` | 验收单模板（9 条格式） | 新验收单照这个写 |
| 11 | `docs/03_modules/_domain_frontend/frontend_handbook/project_conventions.md` | FEH-PC-008 拆件铁律 + 历史踩坑 | 避免重复踩坑 |
| 12 | `tests/frontend/test_dashboard_smoke.py` | 冒烟测试结构断言 | 知道怎么验证 |

**读完标志**：能回答"新组件文件放哪、ID 怎么命、验收单怎么写、loader 怎么挂、测试怎么跑"。

---

## 一、拆分判据（什么时候必须拆）

满足**任一**即拆：

| 判据 | 说明 | 反例 |
|---|---|---|
| 数据源边界 | 两个功能块数据源不同，必须拆 | 自选列表（localStorage）vs 持仓列表（QMT）必须拆 |
| 单一功能 | 一个视觉区块 + 一种交互 + 一个功能语义 = 一个组件 | 股票标题和五档挂单即使同数据源也拆 |
| 经典五信号 | 返工≥2次/独立开关/独立样式/跨页复用/独立数据源 | 成本线（独立开关）必须拆 |

**反向不拆**：一次性初始化、与宿主强耦合、纯布局结构、纯工具函数（进 core/）。

---

## 二、命名规则（一眼定位）

| 类型 | 格式 | 示例 |
|---|---|---|
| 功能模块 ID | `sq-<name>` | `sq-stock-header` |
| 文件路径 | `features/<page>/sq-<name>.js` | `features/stockq/sq-stock-header.js` |
| 纯 UI 件 | `widgets/w-<name>.js` | `widgets/w-price-tag.js` |
| 数据服务 | `services/svc-<domain>.js` | `services/svc-market.js` |
| 验收单 | `ACC-F-<PAGE>-<NAME>.yaml` | `ACC-F-STOCKQ-STOCK-HEADER.yaml` |
| 全景图功能点 | `F-<PAGE>-<NAME>` | `F-STOCKQ-STOCK-HEADER` |
| API 接口 | `/api/<name>` | `/api/stock-header` |

**三类组件区别**：
- **features/**：有数据有交互，页面专属（如 sq-stock-header）
- **widgets/**：无数据无行为，仅渲染样式，全站复用（如 w-price-tag）
- **services/**：数据通道，按域分文件（如 svc-market 管 K线/报价）

---

## 三、施工流程（8 步闭环）

### Step 1：拆分清单规划（_working 临时文档）

- 在 `docs/_working/` 建拆分清单（task_bound，不入持久记忆）
- 列出所有组件：名称/文件/功能语义/数据源/交互行为/验收单
- 按优先级排序（数据就绪度 + 用户痛点）

**参考**：`docs/_working/2026-09-01-stockq-component-split-inventory-v2.md`（stockq 页拆分清单模板）

### Step 2：创建组件文件

**路径**：`src/zephyr/frontend/dashboard/web/features/<page>/sq-<name>.js`

**模板**（必须含 init/render/destroy 契约）：

```javascript
/* 功能模块：<名称>（sq-<name>）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：<CH.table / api:/api/xxx / localStorage / QMT>
 * 验收单：ACC-F-<PAGE>-<NAME>
 */
(function(){
  function injectStyles(){ /* 样式自注入，不写全局 main.css */ }
  var mod = {
    id: 'sq-<name>',
    chart: null,
    init: function(chart, ctx){ /* 初始化：绑定 DOM、注入样式 */ },
    render: function(d){ /* 渲染：从 API 取数或回退演示 */ },
    destroy: function(){ /* 清理：解绑事件、移除 DOM */ }
  };
  ZK.registerFeature(mod);
  /* 竞态兜底：若宿主 init 已执行，注册后主动触发渲染 */
  if(typeof <hostVar> !== 'undefined'){ mod.render(); }
})();
```

**关键坑**：**加载链竞态**——宿主 `sqInit()` 在 app1.js 中执行时，组件可能还没加载。必须加竞态兜底：注册后检查宿主变量是否已存在，存在则主动 `render()`。

**组件类型变体**：

| 类型 | 特点 | 示例 |
|---|---|---|
| 标准组件 | init/render/destroy 三契约 | sq-stock-header |
| 图表组件 | 需接收 chart 实例 | sq-kline-main（init(chart) 拿 KLineChart 实例） |
| 纯展示组件 | 无 chart，只操作 DOM | sq-search-box |
| 交互组件 | 需绑定事件（点击/拖拽/键盘） | sq-draw-tools |
| 聚合组件 | 聚合其他组件状态 | sq-data-source-badge（轮询各组件 mode） |

**图表组件模板**（需 chart 实例）：

```javascript
var mod = {
  id: 'sq-kline-main',
  chart: null,
  init: function(chart, ctx){
    this.chart = chart;  /* 接收宿主传入的 KLineChart 实例 */
    /* 注册指标/覆盖物/事件监听 */
  },
  render: function(d){ /* 用 chart.setData(d) 渲染 */ },
  destroy: function(){ if(this.chart) this.chart.dispose(); }
};
```

**纯 UI 件（widgets/）模板**：

```javascript
/* 纯 UI 件：无数据无行为，仅渲染样式 */
(function(){
  function injectStyles(){ /* 注入 CSS */ }
  window.WPriceTag = { render: function(el, price, direction){ /* 渲染价格标签 */ } };
  injectStyles();
})();
```

**数据服务（services/）模板**：

```javascript
/* 数据服务：按域分文件，导出 fetch 方法 */
window.ZK = window.ZK || {};
ZK.svcMarket = {
  fetchKline: function(symbol, period){ /* ... */ },
  fetchQuote: function(symbol){ /* ... */ }
};
```

### Step 3：API 接口（如需新数据）

**路径**：`src/zephyr/frontend/dashboard/api_server.py`

**模板**：

```python
@app.get("/api/<name>")
def <name>(symbol: str = Query(..., min_length=1)) -> dict[str, Any]:
    """<功能描述>（sq-<name> 组件）"""
    sym = symbol.split(".")[0].strip()
    if not sym.isalnum():
        return {"ok": False, "error": "bad symbol", "data": {}}
    try:
        rows = _ch().execute("SELECT ... FROM <table> WHERE symbol=%(s)s ...", {"s": sym})
        # 注意：先查表结构再写 SQL，避免 Unknown expression identifier
        return {"ok": True, "data": {...}}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": {}}
```

**坑**：ClickHouse 表结构必须先 `DESCRIBE TABLE` 确认列名，不要假设。

**数据源类型变体**：

| 数据源 | 组件示例 | API 接口 | 备注 |
|---|---|---|---|
| CH 表 | sq-stock-header / sq-key-data | `/api/stock-header` | 查 stock_basic/daily_valuation 等 |
| QMT 接口 | sq-position-list / sq-order-book | 需 QMT 桥接服务 | 实盘数据，延后开发 |
| localStorage | sq-fav-list | 无（纯前端） | 自选列表本地存储 |
| 纯前端 | sq-draw-tools / sq-timeline | 无 | 画线工具/时间轴 |
| 后端接口 | sq-financial-read / sq-news | `/api/finance` / `/api/news` | 财务/新闻数据 |
| 聚合状态 | sq-data-source-badge | 无（读各组件状态） | 轮询 ZK.features 各组件 mode |

### Step 4：前端数据服务

**路径**：`src/zephyr/frontend/dashboard/web/services/api.js`

```javascript
fetch<Name>: function(symbol){
  return fetchJson('/api/<name>?symbol='+encodeURIComponent(symbol));
}
```

### Step 5：宿主集成（app1.js）

**初始化**：在 `sqInit()` 中调用组件 init：

```javascript
if(window.ZK && ZK.features && ZK.features['sq-<name>']){ ZK.features['sq-<name>'].init(); }
```

**渲染替换**：原内联渲染函数改为调用组件：

```javascript
function sqRender<Name>(){
  if(window.ZK && ZK.features && ZK.features['sq-<name>']){
    ZK.features['sq-<name>'].render();
    return;
  }
  /* 回退：老代码路径（兼容旧加载链） */
  ...原代码...
}
```

**关键**：必须保留回退路径，防止组件未加载时页面崩溃。

### Step 6：loader.js 加载链挂接

在 `core/loader.js` 中按顺序挂接：

```javascript
.then(function(){
  return loadJs('features/<page>/sq-<name>.js');   /* <名称>功能模块 */
})
```

**顺序**：app1.js → event_bus.js → api.js → **features/** → app2.js

**参考**：`src/zephyr/frontend/dashboard/web/core/loader.js`（现有加载链）

### Step 7：四件套登记

| 文件 | 路径 | 内容 |
|---|---|---|
| manifest | `web/features/manifest.yaml` | 模块 id/name/file/page/depends/acceptance |
| 全景图 | `web/frontend_map.yaml` | 功能点 id/name/page/module_id/file/backend_ref/status |
| 验收单 | `docs/03_modules/_domain_frontend/acceptance/ACC-F-<PAGE>-<NAME>.yaml` | 9 条验收项（目检+机断） |
| 手册 | `frontend_handbook/project_conventions.md` | 踩坑记录（试了两次以上才解决的必入册） |

**widgets/ 登记**：widgets 是全局复用件，不进 frontend_map（无 page 归属），但需在 `widgets/manifest.yaml` 登记：

```yaml
widgets:
  - id: w-price-tag
    name: 价格标签
    file: widgets/w-price-tag.js
    scope: global
    usage: "所有显示价格的地方"
```

**services/ 登记**：services 是数据通道，在 `services/manifest.yaml` 登记域和方法：

```yaml
services:
  - id: svc-market
    name: 行情数据服务
    file: services/svc-market.js
    domain: market
    methods: [fetchKline, fetchQuote]
```

### Step 8：冒烟测试 + 提交

**测试**：`python -m pytest tests/frontend/test_dashboard_smoke.py -x -q`

**提交**：`python scripts/git_commit.py --session <id> --files ... --message-file ... --allow-promote --allow-overlap --allow-non-worktree --allow-multi-domain`

**门禁逃生通道**（按需）：
- `--allow-overlap`：文件被其他 session 持有
- `--allow-non-worktree`：非 worktree 提交
- `--allow-multi-domain`：跨域提交（前端+测试）
- `[no-lookup:continuation]`：CAPABILITY-LOOKUP-REQUIRED 逃生

**参考**：
- 冒烟测试：`tests/frontend/test_dashboard_smoke.py`
- 提交网关：`scripts/git_commit.py`
- 施工流程 SOP：`docs/01_policies_and_standards/sop/construction_workflow_sop.md`

---

## 四、常见坑与对策

| 坑 | 现象 | 对策 |
|---|---|---|
| 加载链竞态 | 组件已注册但页面没渲染 | 注册后主动 `mod.render()` 兜底 |
| 表结构假设 | SQL 报 Unknown identifier | 先 `DESCRIBE TABLE` 确认列名 |
| symbol 重复 | 查询返回多行相同数据 | SQL 加 `DISTINCT` |
| 中文乱码 | PowerShell 显示 æ¢¦å¤©å®¶å± | 用 Python `json.loads` 验证真实数据 |
| 门禁阻断 | CLAIM_REQUIRED / MULTI_DOMAIN | 加对应逃生通道标记 |

---

## 五、验收标准（四态灯）

| 状态 | 含义 | 处理 |
|---|---|---|
| 绿 | 真源正常 | 正常显示 |
| 黄 | 数据延迟 | 提示延迟，仍显示 |
| 红 | 断线（回退演示） | 标"断线·演示"，显示演示数据 |
| 灰 | 服务未启动 | 标"未启动"，显示演示数据 |

**演示诚实纪律**：回退演示数据必须明示（状态灯或文本），禁止冒充真源。

---

## 六、stockq 页组件全清单（26 features + 6 widgets + 8 services）

### features/stockq/（26 个）

| # | 组件 | 文件 | 数据源 | 状态 |
|---|---|---|---|---|
| 1 | sq-fav-list | features/stockq/sq-fav-list.js | localStorage + 价格推送 | ⏳ 待建 |
| 2 | sq-position-list | features/stockq/sq-position-list.js | QMT 持仓接口 | ⏳ 待建（QMT 延后） |
| 3 | sq-search-box | features/stockq/sq-search-box.js | /api/stock-search | ✅ 已通 |
| 4 | sq-kline-main | features/stockq/sq-kline-main.js | CH.kline_* | ⏳ 待建 |
| 5 | sq-kline-volume | features/stockq/sq-kline-volume.js | CH.kline_* | ⏳ 待建 |
| 6 | sq-kline-macd | features/stockq/sq-kline-macd.js | CH.kline_* | ⏳ 待建 |
| 7 | sq-kline-kdj | features/stockq/sq-kline-kdj.js | CH.kline_* | ⏳ 待建 |
| 8 | sq-draw-tools | features/stockq/sq-draw-tools.js | 无（纯前端） | ⏳ 待建 |
| 9 | sq-marks-bs | features/stockq/sq-marks-bs.js | 后端信号接口 | ⏳ 待建 |
| 10 | sq-marks-trade | features/stockq/sq-marks-trade.js | QMT 成交接口 | ⏳ 待建（QMT 延后） |
| 11 | sq-marks-chip | features/stockq/sq-marks-chip.js | CH.chip_distribution | ⏳ 待建 |
| 12 | sq-cost-line | features/cost-line.js | chip-peak.avgCost | ✅ 已通 |
| 13 | sq-event-row | features/stockq/sq-event-row.js | CH.calendar_event | ⏳ 待建 |
| 14 | sq-timeline | features/stockq/sq-timeline.js | 无（纯前端） | ⏳ 待建 |
| 15 | sq-chip-peak | features/stockq/sq-chip-peak.js | CH.chip_distribution | ⏳ 待建 |
| 16 | sq-stock-header | features/stockq/sq-stock-header.js | /api/stock-header | ✅ 已通 |
| 17 | sq-sector-tags | features/stockq/sq-sector-tags.js | stock_basic.sector | ⏳ 待建 |
| 18 | sq-company-intro | features/stockq/sq-company-intro.js | stock_basic.intro | ⏳ 待建 |
| 19 | sq-order-book | features/stockq/sq-order-book.js | QMT l2_tick | ⏳ 待建（QMT 延后） |
| 20 | sq-key-data | features/stockq/sq-key-data.js | CH.daily_valuation | ⏳ 待建 |
| 21 | sq-financial-read | features/stockq/sq-financial-read.js | CH.finance | ⏳ 待建 |
| 22 | sq-related-news | features/stockq/sq-related-news.js | CH.news | ⏳ 待建 |
| 23 | sq-quant-analysis | features/stockq/sq-quant-analysis.js | 后端量化接口 | ⏳ 待建 |
| 24 | sq-fair-value | features/stockq/sq-fair-value.js | 后端估值接口 | ⏳ 待建 |
| 25 | sq-limit-up-gene | features/stockq/sq-limit-up-gene.js | CH.limit_up_pool | ⏳ 待建 |
| 26 | sq-data-source-badge | features/stockq/sq-data-source-badge.js | 各组件状态聚合 | ⏳ 待建 |

### widgets/（6 个，全站复用）

| # | 组件 | 文件 | 用途 |
|---|---|---|---|
| 1 | w-price-tag | widgets/w-price-tag.js | 价格标签（红涨绿跌） |
| 2 | w-pct-badge | widgets/w-pct-badge.js | 涨跌幅徽章 |
| 3 | w-data-table | widgets/w-data-table.js | 键值对数据表格 |
| 4 | w-mini-chart | widgets/w-mini-chart.js | 迷你走势图 |
| 5 | w-icon-toggle | widgets/w-icon-toggle.js | 图标开关（¥/⇅/◍/▤/⚑） |
| 6 | w-status-light | widgets/w-status-light.js | 状态灯（DS-12 四态） |

### services/（8 个，按域分）

| # | 服务 | 文件 | 职责 |
|---|---|---|---|
| 1 | svc-market | services/svc-market.js | K线/分时/报价/五档 |
| 2 | svc-stock-info | services/svc-stock-info.js | 公司资料/财务/关键数据 |
| 3 | svc-events | services/svc-events.js | 日历事件/财报/解禁 |
| 4 | svc-chip | services/svc-chip.js | 筹码分布/成本/获利比例 |
| 5 | svc-fav | services/svc-fav.js | 自选增删改/排序 |
| 6 | svc-position | services/svc-position.js | 持仓查询/盈亏计算 |
| 7 | svc-news | services/svc-news.js | 新闻列表/详情 |
| 8 | svc-quant | services/svc-quant.js | 量化信号/因子/模型 |

---

## 七、参考文件（完整引用链）

**规则真源**：
- `AGENTS.md` — 项目总纲（新 AI 必读三件套 + RULE-WORKTREE + 提交规范）
- `docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml` — 拆件铁律（数据源边界/单一功能/命名/目录归属/四件套闭环）
- `docs/01_policies_and_standards/sop/construction_workflow_sop.md` — 施工流程 15 步（Step 0 必看清单）

**前端真源**：
- `src/zephyr/frontend/dashboard/web/frontend_map.yaml` — 前端全景图（page → module → file → backend_ref）
- `src/zephyr/frontend/dashboard/web/features/manifest.yaml` — 模块注册表（depends 显式声明）
- `src/zephyr/frontend/dashboard/web/core/loader.js` — 加载链（app1→event_bus→api→features→app2）
- `src/zephyr/frontend/dashboard/web/core/event_bus.js` — ZK.registerFeature 机制
- `src/zephyr/frontend/dashboard/web/services/api.js` — 数据服务通道

**模板与范例**：
- `docs/03_modules/_domain_frontend/acceptance/ACC-F-STOCKQ-COSTLINE.yaml` — 验收单模板
- `docs/03_modules/_domain_frontend/frontend_handbook/project_conventions.md` — 手册（FEH-PC-008 拆件铁律 + 历史踩坑）
- `docs/_working/2026-09-01-stockq-component-split-inventory-v2.md` — 拆分清单模板（task_bound）

**测试与提交**：
- `tests/frontend/test_dashboard_smoke.py` — 冒烟测试
- `scripts/git_commit.py` — GitCommitGateway 提交入口
