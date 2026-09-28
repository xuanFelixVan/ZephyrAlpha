---
ttl: task_bound
title: L11 案卷 F113 — 可视化渲染器（五视图库件绿+INVARIANTS 齐；生产消费方=0 零上板——built 须降半接线）
session: zc-l11-20260927
---

# F113 可视化渲染器（L 段 F3，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 五视图纯函数库：图谱/血缘/瀑布/价值流/域映射（总册口径），域映射件消费注入快照（domain_mapping_view.py INVARIANTS"实体须在注入快照内"） |
| 下游消费 | **生产消费方=0**（本日 Python 全仓普查：src/scripts/tools 下 import 命中仅自身；tests/ 各 1 件）——api_server 47 路由零投影、web/ 页面族零调用 |
| 自动化触发 | 零（纯函数库无守护/无计划任务） |
| 真源与注册表 | 五件 BLUEPRINT 锚实读：MOD-FE-006（domain_mapping_view.py:1）、MOD-FE-009（trace_waterfall_view.py:1）等；域册=docs/03_modules/_domain_frontend/ 15 子目录+blueprint+algo_flow+frontend_handbook（本日 ls） |
| 门禁与质量尺 | 五件 INVARIANTS 头注全齐（本日逐一实读）：节点 id 唯一/DAG 闭合环拒绝/重复边幂等/层分配最长路径/barycenter 降交叉/词表闭合/确定性输出"同输入必同输出"——纯函数质量尺为全仓模范面 |
| 当前运行状态 | **库件绿/接线红**：五件有码有测试有不变量；生产装配零——总册"built"系库件级，上板通道空集 |

## 二、子模块三级枚举（src/zephyr/frontend/ 包根渲染器面实扫）

1. **graph_view_renderer.py**：DAG 图谱布局（层分配/降交叉/双向 N 跳钻取子图；INVARIANTS 实读）。
2. **lineage_view_renderer.py**：血缘 DAG+影响着色（changed 优先于 impacted；双向 BFS N 跳闭包）。
3. **trace_waterfall_view.py**：四视图词表（trade_main|data_chain|ai_ops|gpu_infer）瀑布+sha256 确定性采样。
4. **value_stream_view.py**：五段价值流（data|factor|signal|execution|portfolio）仅顺流边+高亮传递闭包。
5. **domain_mapping_view.py**：域映射矩阵=桑基边权重同聚合+孤儿实体识别。
6. **同根邻件**（非五视图但同层面）：compliance_dashboard.py（合规异常严重级/整改状态词表闭合）、frontend_api_proxy.py（MOD-FE-011 代理：路由最长前缀+token Fail-Closed+限流分桶）、interface_base.py（协议基类，implementations/ 5 件+reporting/alert_aggregator 消费其接口）。

## 三、接线四态独立复核（本日 Python 全仓消费普查，patrol=import/ref 双口径）

- **五渲染器：未接线**——生产 import=0、tests 各 1；"图谱/血缘/瀑布/价值流/域映射五视图"在 8890 页面族与 api_server 均无承载（链图族页面实际由 chainmap 专用路由+前端 js 直渲染，未走本渲染器）。
- **compliance_dashboard/frontend_api_proxy：未接线（生产）**——frontend_api_proxy 系旧 Panel 链配套（tests/frontend/test_frontend_api_proxy.py=MOD-FE-011 代理路由表测试），app_panel 弃用后随链冻结。
- **interface_base+implementations：半接线**——接口被 reporting/alert_aggregator、default_approval_gateway/default_notification_manager 实现（库级装配），但装配终端 notification_router 亦零生产消费（见 09 卷），整体未达生产。
- **无停用声明**：五件全 kept、无 deprecated 头注——与 F114 notification_router 头注自认 tests-only 形成对照。

### 骨架勘误
1. **总册 F113"built"降级主张**：实态=库件 built、装配未接线（生产消费方=0）——按总册 §0 四要素判应为 **partial**（③自动化要素：建成后未接线=黄），P2 维持。骨架勘误必录。
2. 总册"五视图"清单成立（五件实存），但须补记：8890 生产页面的图谱渲染实际走 chainmap 专用族+前端 js，本五件为未挂库件——防误读"五件在跑"。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 五渲染器零上板通道 | api_server 增只读投影路由（depgraph/血缘图是天然首客；随 F115 R3 投影同范式） | P2 |
| 2 | 五件与 chainmap 前端渲染职责重叠嫌疑 | 职责界线裁定（内收判据 w5_1 跨域不同对象→不并，需先实证对象差） | P2 |
| 3 | frontend_api_proxy 旧链冻结件归属 | 随 app_panel 净删门同窗处置 | P2 |

## 五、自审闸三态

**挖干（五件 INVARIANTS 逐一实读+全仓消费普查双口径+域册 ls）✅；待裁（缺口#2 职责界线=归总筹内收审计窗）；待挖（五件确定性输出 goldendata 基准=tests 单件覆盖面浅，随上板批扩）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "
from pathlib import Path
mods=['graph_view_renderer','lineage_view_renderer','trace_waterfall_view','value_stream_view','domain_mapping_view','compliance_dashboard','frontend_api_proxy']
files=[p for r in [Path('src'),Path('scripts'),Path('tools')] for p in r.rglob('*.py') if '__pycache__' not in str(p)]
for m in mods:
    hits=[str(p) for p in files if m in p.read_text(encoding='utf-8',errors='ignore') and ('frontend.'+m) in p.read_text(encoding='utf-8',errors='ignore') and not str(p).replace(chr(92),'/').endswith('/'+m+'.py')]
    print(m,'prod_consumers=',len(hits))"
grep -n "INVARIANTS" src/zephyr/frontend/graph_view_renderer.py | head -1
ls docs/03_modules/_domain_frontend/ | head -8
```
