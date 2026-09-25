---
ttl: task_bound
---

# M6 前端API链 · 分册 01 · 仪表盘与页面族（dashboard 壳/入口/页面族/门禁/挂接点）

> 挖矿会话 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿，零 commit/零 enqueue。
> 上游分册：02_api_server.md（数据通道）、03_panel_caches.md（缓存 TTL）。

## 一、环节定义与边界
一句话：把 8890 单端口一体服务（api_server）直出的 SPA 页面族（web/ 54 片段）经桌面壳（Electron）交付给 Owner，页面族经 loader 注入 + features 模块制渲染 + ZK.api 取数，前端真源接通由 FRONTEND-MAP / FRONTEND-TRUTH-SOURCE 双门看守。
- 供料方：02 册 api_server（页面 StaticFiles + 全部 /api 数据）；M5 调度链（计划任务四态灯数据源）。
- 消费方：Owner（桌面壳/浏览器）；frontend_map 六图对齐体系；depgraph frontend_ref 闭合。

## 二、六向台账
| 向 | 实测证据 |
|---|---|
| 上游输入 | api_server StaticFiles mount `src/zephyr/frontend/dashboard/api_server.py:4468-4474`（web/ 目录 html=True）；页面片段 `web/pages/*.html` 54 个；页面引擎 `web/features/**`（features/manifest.yaml 登记 71 模块全 active）；全局宿主 `web/core/app1.js` + loader 保序加载链 `web/core/loader.js:29-81`（81 处 loadJs） |
| 下游消费 | 桌面壳 `tools/desktop/main.js:42`（API_HEALTH=http://127.0.0.1:8890/api/health，生产入口 8890，断线回退 app:// 直读磁盘演示态，`main.js:44-48` 注册 app:// 特权 scheme）；浏览器直访 8890；frontend_map.yaml（361 功能点行，v2.3.3）供六图对齐 |
| 自动化触发 | 无 cron/计划任务直属前端；api_server 由桌面壳 spawn（`tools/desktop/main.js:31` 注释：auto-spawns api_server 8890 + serve_docs 8765）或服务总闸手拉（services_registry id=api_server tier=self 可一键重启）；`scripts/register_desktop_shell_startup.ps1:32` 桌面壳快捷方式注册 |
| 真源与注册表 | 页面模块契约真源=`web/features/manifest.yaml`（71 模块，全 status: active）；功能点全景真源=`web/frontend_map.yaml`（v2.3.3, 361 行 F-*；头注：architecture_model/frontend/frontend_map.yaml 已降级派生副本禁消费）；旧 Panel 入口=`app_panel.py`（DEPRECATED 2026-08-29 R22/R23，`app_panel.py:19-22`，保留不删）；Streamlit 入口=`app.py:22-30` 已弃用 v3.1.0 |
| 门禁与质量尺 | FRONTEND-MAP 硬阻断（`src/zephyr/gov_enforcement/commit_gates/frontend_map_gate.py:8`——id 重复/backend_ref 非类型化/悬空即断，YAML 损坏 fail-closed，校验单一真源=scripts check_frontend_map.py）；FRONTEND-TRUTH-SOURCE warn-only（`frontend_truth_source_gate.py:8,204`——staged web/**/*.js 零 ZK.api/fetch 引用=自建数据世界嫌疑，审计落盘 .runtime/gate_audit/frontend_truth_source.jsonl:213-215，own-scope 化 2026-09-23） |
| 当前运行状态 | 黄。壳/页面族主体绿（loader 52 页 wired，81 引擎文件保序，导入级验证 COMPILE_OK/IMPORT_OK）；黄点=AI 层两新页（budget/schedulegate）三层接线缺口未闭合（见 §四-1）；app_panel.py 弃用未退役（Owner 指令：新版完全涵盖旧版后才可删，`app_panel.py:20-21`） |

## 三、子模块清单（ls+grep 穷尽，两源交叉=ls 目录 × manifest.yaml × frontend_map.yaml）
| 模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| 桌面壳（Electron） | 生产入口 8890；断线回退 app:// 磁盘演示态；单实例锁 | tools/desktop/main.js:5-13,42-48 | 绿 |
| SPA 壳 | index.html 骨架 + loader 注入 52 页片段 + 保序加载 81 个 JS | web/index.html:1-10；web/core/loader.js:3,6,26-29 | 绿 |
| 页面片段族 | pages/*.html 54 个（loader PAGES 52 个 wired；budget/schedulegate 未 wired，见 §四-1） | web/pages/（54 文件，python 实测 diff） | 黄 |
| features 模块制 | 契约 init(chart,ctx)/render(d)/destroy()，ZK.registerFeature 登记，模块间只走 ZK.bus | web/features/manifest.yaml:3-5（71 模块）；web/core/event_bus.js | 绿 |
| 数据通道 | ZK.api 唯一接触点（fetchJson/47 方法+SWR），失败必 reject 回退演示 | web/services/api.js:1-7,164-180 | 黄（schedulegate 三方法缺失，见 §四-1） |
| 旧 Panel 大屏（Panel/HoloViz） | 14 Tab（作战室/治理6/交易回测7），DEPRECATED 保留 | app_panel.py:19-27,457-486 | 冻结（保留参考实现） |
| 旧 Streamlit | 已弃用 v3.1.0，编程式 API 保留 | app.py:22-30,74-125 | 冻结 |
| components/（17 件） | 旧 Panel 的 Tab 组件（warroom/task_progress/…/tick_replay）；experiment_history 带 lru_cache+reset | src/zephyr/frontend/dashboard/components/（ls 17 文件）；experiment_history.py:201-209 | 冻结（warroom 消费链仍活：app_panel.py:153-156） |
| services_registry | 服务总闸唯一真源：**35 启动项**四态灯+分级启停（free/confirm/guard/external/self）+审计日志 tmp/services_control_log.jsonl | services_registry.py:33（SERVICE_CATALOG），实例测 len=35；tier 分级 :29-31 | 绿（头注"16 个启动项"(:4) 已漂移为陈旧文案） |
| TDM 一张图挂接 | 交易决策地图：真源 config/trading_decision_map.yaml → /api/tdm（mtime 缓存）→ tdm.js 原生渲染 30s 轮询（页面可见才 fetch） | api_server.py:2315-2332；web/features/tdm.js:1-20,646 | 绿（validation/verdicts 子通道降级语义齐备 api_server.py:2419,2475） |
| 排班一张图挂接 | L5 排产门闸：zephyr.ai_layer.scheduling（seed_writer.load_seeds+dispatcher.rank_pending，导入实测 callable）→ /api/schedulegate-queue/-skeletons/-confirm → schedulegate.js | api_server.py:4513-4561；web/features/schedulegate/schedulegate.js:1-16 | 红（前端三层接线缺口，见 §四-1） |
| 预算页挂接 | zephyr.intelligence.budget_analyzer（导入实测 callable）→ /api/budget-advisories → budget.js 60s 轮询 | api_server.py:4497-4510；web/features/budget/budget.js:81-118 | 黄（页未 wired+相对路径 fetch，见 §四-2） |
| 门禁双闸 | FRONTEND-MAP（硬断）+ FRONTEND-TRUTH-SOURCE（warn） | frontend_map_gate.py:8；frontend_truth_source_gate.py:8,136,221-277 | 绿 |

## 四、堵点与病灶
1. **【红】AI 层两新页三层接线缺口（st-ailayer-final-20260924 件先落位、接线批未补齐）**
   - 现象：budget/schedulegate 页在桌面壳中不可达且排产页即使可达也不出数据。
   - 根因（三层各自独立成立，任一即断）：
     a) loader 未 wiring：`core/loader.js:6` PAGES 52 项无 "budget"/"schedulegate"，python 实测 diff=`['budget','schedulegate']`——页面片段永不注入 DOM，budget.js:113 / schedulegate.js:175 的容器自举永不触发；
     b) api.js 客户端方法缺失：schedulegate.js:111-112,142 调 `ZK.api.fetchSchedulegateQueue/fetchSchedulegateSkeletons/postSchedulegateConfirm`，`services/api.js`（全 182 行通读）零定义——防御式三元使其静默回退 `{orders:[]}`，页面永远显示"暂无进化工单"；拍板按钮点击即 TypeError（undefined is not a function）；
     c) 容器 id 不匹配：pages/schedulegate.html:6 供 `#schedulegate-body`，schedulegate.js:93,175 全程操作 `#sg-body`——5 处引用全落空。
   - 修法草案：单批四点闭合——loader.js PAGES 追加两页 + 页尾按 promotion.js:183 先例 loadJs 两个 feature + api.js 补三方法（对齐 api_server.py:4513-4561 契约）+ schedulegate.js 改 `#schedulegate-body`（或页面改 id，单点即可）。预估 0.5 天，属本车道可修。
   - 佐证：schedulegate.js:14-15 自述"接线缺口（在册，施工另行单派——本班禁改既有文件）"——已知在册未还。
2. **【黄】budget.js 违反通道纪律（相对路径裸 fetch）**：budget.js:83 `fetch('/api/budget-advisories')` 绕过 ZK.api 且用相对路径——桌面壳断线回退 app:// 模式下会打到 `app://api/...` 必断（tdm.js:20 注释明文该坑："app:// 模式下相对 fetch 会打到 app://api/tdm 必断"故用绝对 BASE）。修法：改走 ZK.api.fetchJson（绝对 BASE）。0.1 天，本车道可修。附：FRONTEND-TRUTH-SOURCE 启发式只查"有无 fetch 引用"(:204)，裸 fetch 也算接线，拦不住该类漂移。
3. **【黄】frontend_map 与 manifest 双源登记、与 loader 三源无一致性门**：manifest.yaml 71 模块、frontend_map.yaml 361 功能点、loader PAGES 52 页——三源各自维护，FRONTEND-MAP 门只校验 frontend_map 自身 R0-R3（frontend_map_gate.py:8），"页面是否可达（loader wired）"与"api 方法是否存在"无门看守（本册 §四-1 即漏网实例）。修法草案：FRONTEND-MAP 增 R4=loader PAGES ⊇ pages/ 目录、manifest.file 存在性、api.js 方法名 ⊆ api_server 路由投影（可机生校验）。1-2 天，本车道可修。
4. **【黄】services_registry 头注陈旧**：services_registry.py:4 写"16 个启动项"，实测 SERVICE_CATALOG len=35（分组 services6/data5/trading6/infra6/guard12；tier free6/confirm5/guard13/external10/self1）。文档矛盾=事故级病灶（宪法 §4.3），修法=头注改字段引用禁写死。0.05 天。
5. **【灰】app_panel.py 弃用挂账**：R22/R23 裁定保留（app_panel.py:19-22），保留价值=Tick 回放参考+作战室骨架+hover 交互参考；services_registry 仍有 id=panel 启动项（services_registry.py:38-42，端口 5006）。属 Owner 净删门位事项（§5 high 域），非本车道擅动。

## 五、提速与合并机会
1. budget/schedulegate 接线批（§四-1）与 §四-2 通道修正天然同批，一次 commit 闭合红+黄。
2. 前端三源（manifest/frontend_map/loader）可派生校验器合一：一个机生脚本产出三源一致性报告，FRONTEND-MAP 门复用——同真源多消费合并，防再添第四源。
3. services_registry 头注计数漂移与宪法 §4.3"计数用字段"同治：目录项数从 len(SERVICE_CATALOG) 注入，禁手写。
4. 页面轮询生态（tdm 30s/govm 30s/factory 30s/schedulegate 30s/budget 60s/promotion timer）可抽公共 visible-guard 轮询器（tdm.js:646 模式），减少每页自写 setInterval 漂移。

## 六、自审闸三态
**待挖→挖干可施工（本册）**：六向全实证（file:line + python 导入/实测输出）；子模块两源交叉（ls × manifest × frontend_map × python len 实测）；堵点有根因+修法。
- 挖干可施工：§四-1/2/4 三个修法（前端接线批）。
- 待裁：§四-5 app_panel 退役时点（Owner 净删门位）。
- 缺口移交：页面族 54 页逐页运行态验证需起服务器（本车道禁启动服务进程），移交施工批冒烟。

## 七、复核命令（10 分钟）
```bash
# 1. 页面 wiring 缺口复现（应输出 ['budget','schedulegate']）
python -c "from pathlib import Path;import re;l=Path('src/zephyr/frontend/dashboard/web/core/loader.js').read_text(encoding='utf-8').splitlines()[5];m=set(re.findall(r'\"([a-z0-9]+)\"',l));p={f.stem for f in Path('src/zephyr/frontend/dashboard/web/pages').glob('*.html')};print(sorted(p-m))"
# 2. api.js 方法缺口复现（应无输出=零定义）
grep -n "fetchSchedulegateQueue\|postSchedulegateConfirm" src/zephyr/frontend/dashboard/web/services/api.js
# 3. 容器 id 不匹配复现
grep -n "sg-body\|schedulegate-body" src/zephyr/frontend/dashboard/web/features/schedulegate/schedulegate.js src/zephyr/frontend/dashboard/web/pages/schedulegate.html
# 4. 服务目录计数复现（应 n= 35）
python -c "import sys,types;sys.modules['pytest']=types.SimpleNamespace();from zephyr.frontend.dashboard.services_registry import SERVICE_CATALOG;print('n=',len(SERVICE_CATALOG))"
# 5. 门禁在册复核
grep -n "FRONTEND-TRUTH-SOURCE\|FRONTEND-MAP" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head -4
```
