---
module_id: MOD-L28-QMTBH
submodule_path: src/zephyr/frontend/dashboard/components
title: "QMT 文件桥健康监控面板蓝图 — qmt_bridge_health 组件"
doc_type: blueprint
status: Draft
version: "0.1.0"
layer: L2_domain
layer_name: frontend
functional_domain: frontend
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-08-27"
last_updated: "2026-08-27"
last_verified: "2026-08-27"
valid_from: "2026-08-27"
ttl: permanent
actual_disk_path: "src/zephyr/frontend/dashboard/components/"
belongs_to: "MOD-L28-001"
parent_module: "MOD-L28-001"
generation: 2
codification_level: L1
rule_form: structural
scope: module
stability: evolving
verifiability: manual
ssot_yaml: "docs/03_modules/_domain_frontend/blueprint_qmt_bridge_health.md"
summary: "QMT 文件桥健康监控面板——消费 Assembly.health_check() 聚合端点，三级状态（ok/degraded/down）卡片化展示 broker/queue/quote 全组件，3 秒周期刷新，fail-closed 空态降级"
tags: [frontend, dashboard, health-monitor, qmt-file-bridge, panel]
priority: P1
runtime_plane: cold
depends_on:
  - target: "MOD-L06-001-QMTFB"
    at: "QmtFileBridgeAssembly.health_check"
    why: "健康数据唯一真源（b907bfbe 已落地），本面板纯消费不改写"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\07_trading_decision_architecture\\design_memos\\93_qmt_file_bridge_playbook.md"
    section: "§11 反向行情桥"
    why: "文件桥三通道（指令/导出/行情）运行机制与排障语义"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\frontend\\dashboard\\components\\order_book.py"
    section: "全篇"
    why: "组件三段式约定（Data/fetch/render）与 panel 可选导入模式真源"
design_maturity: design
build_status: planned
responsibility_domain: 
---

# QMT 文件桥健康监控面板蓝图 — qmt_bridge_health 组件

> **真源声明**：本蓝图是 qmt_bridge_health 组件的唯一真源。
> **上游衔接**：健康数据 API（`QmtFileBridgeAssembly.health_check()`，commit b907bfbe）→ 本蓝图 → 施工代码。

## 1. 一句话定位

**qmt_bridge_health 是文件桥三通道（指令进口/柜台导出/行情反向）运行态的可视化哨兵——把 `Assembly.health_check()` 的聚合 dict 渲染为三级颜色状态卡片，让"通道是否活着"一眼可见，故障时 detail 字段直给排障入口。**

## 2. 背景与必然性

- 文件桥是 miniQMT 替代主通道（93 playbook 已确立），其可靠性=项目交易能力的可靠性
- 三通道故障模式各异且静默：v14 策略停止（指令堆积）、官方导出中断（状态盲区）、v15 停止（行情断流）——无监控时只能靠人工盯日志
- 健康数据端点已就绪（quote/broker/queue/assembly 四个 health_check，37/37 单测绿），**本面板零数据层施工，纯消费**

## 3. 模块边界

### 3.1 职责（What it does）

1. **数据消费**：调 `assembly.health_check()` 取聚合 dict（含 components 子表）
2. **状态映射**：level(ok/degraded/down) → 颜色(绿/黄/红) + 图标
3. **卡片渲染**：总状态横幅 + 每组件一张卡片（broker_sim/broker_real/queue_*/quote_*）
4. **周期刷新**：`pn.state.add_periodic_callback` 3 秒（与柜台同步间隔对齐）
5. **fail-closed**：assembly 未注入/异常 → 空态卡片"未装配"，不炸面板

### 3.2 非职责（What it does NOT do）

- ❌ 不修改健康判定逻辑（ok/degraded/down 阈值在后端 API，本面板只读）
- ❌ 不做告警通知（告警升级在 alert_center 组件职责内）
- ❌ 不提供控制操作（重启策略/重连是人工或 ops 脚本动作，本面板只读）

## 4. 接口契约

### 4.1 数据模型

```python
@dataclass
class ComponentHealth:
    """单组件健康视图"""
    name: str            # broker_sim / queue_qmt_sim / quote_real ...
    type: str            # broker / order_queue / quote_provider
    level: str           # ok / degraded / down
    detail: str          # 排障提示（空=正常）
    metrics: dict        # 关键指标原样透传（export_age/pending/fresh/running...）

@dataclass
class QmtBridgeHealthData:
    """面板数据（fetch 输出）"""
    assembled: bool              # assembly 是否注入
    overall_level: str           # 聚合等级
    components: list[ComponentHealth]
    checked_at: str              # 渲染时刻（展示用）
```

### 4.2 函数契约（遵循 order_book 三段式）

```python
def fetch_qmt_bridge_health(assembly: object) -> QmtBridgeHealthData:
    """纯函数、依赖注入、fail-closed：assembly None/异常 → QmtBridgeHealthData(assembled=False)"""

def render_qmt_bridge_health(data: QmtBridgeHealthData) -> dict[str, Any]:
    """返回 JSON payload + '_layout' 键挂 Panel 布局；panel 不可导入时仅返回 dict（测试环境零依赖）"""
```

### 4.3 消费的后端契约（已存在，只读）

```python
QmtFileBridgeAssembly.health_check() -> {
    "component": "qmt_file_bridge_assembly", "ok": bool,
    "level": "ok"|"degraded"|"down",
    "components": { "<id>": {level, detail, type 特定指标...} }
}
```

## 5. 五图对齐

### 5.1 依赖图

```
qmt_bridge_health (components/)
    ├── QmtFileBridgeAssembly.health_check [消费，DI 注入]
    ├── chart_factory [复用：状态卡片/指标条统一工厂]
    ├── panel (pn) [可选导入，测试环境 None]
    └── components/__init__.py [守卫式单行 import 注册]
```

### 5.2 数据流图

```
QMT 终端文件区 (E:\qmt_bridge{,_sim}\)
    ▼ (后端 3 秒轮询，已存在)
health_check() APIs (broker/quote/queue/assembly)
    ▼ fetch_qmt_bridge_health（面板构建时调用）
QmtBridgeHealthData
    ▼ render_qmt_bridge_health
Panel 布局 (_layout) ──[Bokeh WebSocket]──▶ 浏览器卡片
    ▲ pn.state.add_periodic_callback(3s) 周期重取
```

### 5.3 状态映射图（level → 视觉）

| level | 颜色 | 图标 | 含义（直给用户的排障语义） |
|---|---|---|---|
| ok | 绿 #22c55e | ● | 通道活着 |
| degraded | 黄 #eab308 | ▲ | detail 直给原因（导出>60s 未更新/行情 10s-5min 未更新/同步线程停） |
| down | 红 #ef4444 | ■ | detail 直给原因（未连接/文件不存在/行情中断>5min） |

### 5.4 布局图

```
┌────────────────────────────────────────────┐
│ 总状态横幅: ● 文件桥整体 ok（检查于 12:30:05） │
├──────────────┬──────────────┬──────────────┤
│ broker_sim   │ broker_real  │ queue_qmt_sim│
│ ● ok         │ ▲ degraded   │ ● ok         │
│ 导出 2.1s    │ 导出 75s     │ 待发 2/已发 8│
├──────────────┼──────────────┼──────────────┤
│ quote_sim    │ quote_real   │              │
│ ● ok         │ ■ down       │              │
│ 新鲜 1.2s    │ 文件不存在    │              │
└──────────────┴──────────────┴──────────────┘
```

### 5.5 集成序列图（注册步骤，4 处改动）

```
① components/qmt_bridge_health.py        新建（本蓝图 §4）
② components/__init__.py                 守卫式 import + __all__
③ app_panel.py
   ├─ import fetch/render（仿 order_book L112-115）
   ├─ __init__ 增加 DI: qmt_assembly: object | None = None
   ├─ _tab_qmt_bridge_health() builder（仿 L308-311）
   └─ build_tabs() tabs_spec 追加 ("QMT桥健康", builder)
④ 周期刷新：builder 内 pn.state.add_periodic_callback(3000ms)
   ※ 全库首例周期刷新模式，本蓝图确立为先例
```

## 6. 关键设计决策

### 6.1 为什么周期刷新选 3 秒而非 1 秒/5 秒？

- 与柜台同步间隔（sync_interval=3.0s）对齐：后端状态最快 3 秒一变，更快刷新无新增信息
- Bokeh WebSocket 推送成本与刷新频率正相关，3 秒对本地单用户面板零压力
- 93 playbook 裁定"做T场景 3 秒知道状态完全不影响决策"同一逻辑

### 6.2 为什么健康判定阈值不前端化？

- 阈值（fresh=10s/导出 60s/degraded 300s）是**后端运维语义**，前端硬编码会造成第二真源
- 面板只读 level+detail 展示，阈值调整只改后端 API 单测覆盖处，前端零改动

### 6.3 为什么 fail-closed 空态而非隐藏 Tab？

- assembly 未注入时隐藏 Tab 会让用户以为"没有文件桥功能"，空态卡片"未装配"才是诚实 UI
- 与 order_book/position_monitor 现有 fail-closed 约定一致

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| add_periodic_callback 无先例引入新模式 | 中 | 模式风险 | 本蓝图即先例文档；回调内 try/except 全捕获，异常仅记日志不炸 server |
| 健康端点在交易时段高频调用竞争文件句柄 | 低 | 读取失败 | health_check 全部只读 stat/尾读，OSError 容错已内置 |
| 用户把 degraded 误读为故障 | 中 | 误操作 | detail 文案直给原因+正常场景（午休/收盘后行情不新鲜属预期） |

## 8. 测试策略

- `fetch` 单测：assembly None → assembled=False；mock assembly 返回聚合 dict → 字段映射正确；assembly 抛异常 → fail-closed
- `render` 单测：panel=None 环境返回 dict payload（无 _layout 键报错）；三级 level 映射到预期颜色键
- 集成：真实 Assembly（temp dir 构造）→ fetch → data.components 非空

## 9. 施工清单

| # | 任务 | 产出 | 依赖 |
|---|---|---|---|
| 1 | qmt_bridge_health.py 组件 | `src/zephyr/frontend/dashboard/components/qmt_bridge_health.py` | 本蓝图 |
| 2 | 组件注册 | `components/__init__.py` 追加 | #1 |
| 3 | Tab 接线 + DI | `app_panel.py` 四处改动 | #1 |
| 4 | 周期回调刷新 | 同 #3（builder 内） | #3 |
| 5 | 单测 | `tests/frontend/dashboard/components/test_qmt_bridge_health.py` | #1 |
| 6 | 手工验收 | 起 panel serve 肉眼验证三色卡片+3秒刷新 | #3 |

## 10. 修订记录

| 版本 | 日期 | 内容 |
|---|---|---|
| 0.1.0 | 2026-08-27 | 初版：基于已落地 health_check API（b907bfbe）定义监控面板组件，确立 add_periodic_callback 周期刷新先例 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L28-QMTBH`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L28-QMTBH` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-L28-QMTBH` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L28-QMTBH | MOD-L28-QMTBH | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | planned | ❌ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
