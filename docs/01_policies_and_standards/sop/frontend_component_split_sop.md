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
| 验收单 | `ACC-F-<PAGE>-<NAME>.yaml` | `ACC-F-STOCKQ-STOCK-HEADER.yaml` |
| 全景图功能点 | `F-<PAGE>-<NAME>` | `F-STOCKQ-STOCK-HEADER` |
| API 接口 | `/api/<name>` | `/api/stock-header` |

---

## 三、施工流程（8 步闭环）

### Step 1：拆分清单规划（_working 临时文档）

- 在 `docs/_working/` 建拆分清单（task_bound，不入持久记忆）
- 列出所有组件：名称/文件/功能语义/数据源/交互行为/验收单
- 按优先级排序（数据就绪度 + 用户痛点）

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

### Step 7：四件套登记

| 文件 | 路径 | 内容 |
|---|---|---|
| manifest | `web/features/manifest.yaml` | 模块 id/name/file/page/depends/acceptance |
| 全景图 | `web/frontend_map.yaml` | 功能点 id/name/page/module_id/file/backend_ref/status |
| 验收单 | `docs/03_modules/_domain_frontend/acceptance/ACC-F-<PAGE>-<NAME>.yaml` | 9 条验收项（目检+机断） |
| 手册 | `frontend_handbook/project_conventions.md` | 踩坑记录（试了两次以上才解决的必入册） |

### Step 8：冒烟测试 + 提交

**测试**：`python -m pytest tests/frontend/test_dashboard_smoke.py -x -q`

**提交**：`python scripts/git_commit.py --session <id> --files ... --message-file ... --allow-promote --allow-overlap --allow-non-worktree --allow-multi-domain`

**门禁逃生通道**（按需）：
- `--allow-overlap`：文件被其他 session 持有
- `--allow-non-worktree`：非 worktree 提交
- `--allow-multi-domain`：跨域提交（前端+测试）
- `[no-lookup:continuation]`：CAPABILITY-LOOKUP-REQUIRED 逃生

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

## 六、已完成组件清单（stockq 页）

| 组件 | 文件 | 状态 | 验收单 |
|---|---|---|---|
| sq-stock-header | features/stockq/sq-stock-header.js | ✅ 已通 | ACC-F-STOCKQ-STOCK-HEADER |
| sq-search-box | features/stockq/sq-search-box.js | ✅ 已通 | ACC-F-STOCKQ-SEARCH-BOX |
| sq-cost-line | features/cost-line.js | ✅ 已通 | ACC-F-STOCKQ-COSTLINE |
| sq-key-data | features/stockq/sq-key-data.js | ⏳ 待建 | - |
| sq-fav-list | features/stockq/sq-fav-list.js | ⏳ 待建 | - |
| sq-order-book | features/stockq/sq-order-book.js | ⏳ 待建 | - |
| ... | ... | ... | ... |

---

## 七、参考文件

- 规则真源：`docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml`
- 拆分清单（临时）：`docs/_working/2026-09-01-stockq-component-split-inventory-v2.md`
- 模块注册表：`src/zephyr/frontend/dashboard/web/features/manifest.yaml`
- 前端全景图：`src/zephyr/frontend/dashboard/web/frontend_map.yaml`
- 冒烟测试：`tests/frontend/test_dashboard_smoke.py`
