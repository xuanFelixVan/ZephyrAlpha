---
ttl: task_bound
title: L11 案卷 F111 — Panel 仪表盘（生产入口=api_server 8890 一体服务；app_panel 弃用未退役；入口口径三方冲突勘误）
session: zc-l11-20260927
---

# F111 Panel 仪表盘（L 段 F1，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | F112 api_server（StaticFiles mount 直出 web/ SPA+47 唯一路径 /api 投影）；页面族=web/pages/*.html **54 片**、features/manifest.yaml 71 模块、loader.js PAGES **54 全 wired**（本日 python 实测 diff=[]） |
| 下游消费 | Owner：桌面壳 tools/desktop/main.js:42 探活 http://127.0.0.1:8890/api/health，断线回退 app:// 磁盘演示态；浏览器直访 8890 |
| 自动化触发 | 桌面壳 spawn api_server 8890+serve_docs 8765（main.js:31 注释锚）；services_registry id=api_server tier=self 可一键重启；`scripts/register_desktop_shell_startup.ps1:32` 桌面壳自启注册 |
| 真源与注册表 | 页面契约真源=web/features/manifest.yaml（71 模块全 active）；功能点全景=web/frontend_map.yaml（361 F-* 行，头注声明旧 architecture_model 副本已降级禁消费）；**旧入口 app_panel.py:19-24 头注实读：DEPRECATED 2026-08-29 Owner 裁定 R22/R23，"保留不删"待新版完全涵盖后净删** |
| 门禁与质量尺 | FRONTEND-MAP 硬断（frontend_map_gate.py:8）+FRONTEND-TRUTH-SOURCE warn-only（own_scope 均=false，gate_registry:1153/:1164——wiring_gap §1.6 连坐面）；test_dashboard_smoke.py playwright 结构冒烟非提交闸 |
| 当前运行状态 | **绿（较 09-25 翻绿）**：M6 01 册红点"AI 层两新页三层接线缺口"+05 册两残留（容器 id 失配/budget 裸 fetch）本日逐一复跑**全部已修**（见 §三）；灰点=app_panel 弃用挂账+services_registry 仍有 id=panel tier=free 启动项（端口 5006） |

## 二、子模块三级枚举（src/zephyr/frontend/ 九子包本日实扫；总册口径括注对照）

**九子包实数（top .py/全 .py）**：dashboard 6/24（api_server+app+app_panel+chainmap_equity_graph+services_registry+init；components/ 17 组件+init）、implementations 6、api 1（壳）、services 2（dashboard_feeds+init）、acceptance 0（仅 baselines 目录）、core 1（壳）、models 1（壳）、infrastructure 1（壳）、_extensions 1（壳）；包根散件 10：五渲染器+compliance_dashboard+frontend_api_proxy+notification_router+interface_base+init；合计 47 .py。
（任务书口径"dashboard 23/implementations 6/api/services 2/acceptance 0"——dashboard 本日实数 24（含 components），差 1=口径时点，录勘误。）

1. **生产壳**：web/index.html+core/loader.js（54 页注入+81 引擎保序）+core/event_bus.js+services/api.js（40 方法定义本日 grep 实数；09-25 口径 43——方法面收敛漂移录勘误）。
2. **页面族**：pages/ 54 html；features/ 71 模块全 active（manifest.yaml）；tdm/govm/factory/schedulegate/budget 等轮询页族。
3. **服务总闸**：services_registry.py SERVICE_CATALOG=**35** 启动项（本日 import 实测；头注"35 个启动项（2026-09-25 实测）"——M6 记录的"16 启动项"陈旧文案已修）；panel 启动项 tier=free 在册。
4. **弃用保留族**：app_panel.py（14 Tab 大屏）+components/ 17 件+app.py（Streamlit v3.1.0 弃用）。
5. **域册**：docs/03_modules/_domain_frontend/（本日 ls：acceptance/alert_center/compliance_dashboard/domain_mapping_view/feishu_bot_sender/frontend_api_proxy/graph_view_renderer/lineage_view_renderer/notification_router/resource_week_view/trace_waterfall_view/value_stream_view/wechat_bot_handler/frontend_handbook/algo_flow+blueprint）。

## 三、接线四态独立复核

- **web/ 生产链：已接线**——loader 54/54 wired（本日实测 unwired=[]）；api.js schedulegate 三方法在（:95/:101）；**schedulegate.js 本日全用 `schedulegate-body` 与页面容器一致（09-25 的 sg-body 失配 5 处已修）**；**budget.js:84 本日实读已改 ZK.api.fetchJson 并留通道纪律注释（裸 fetch 已修）**——05 取证册两残留全清。
- **app_panel 链：停用（弃用保留）**——R22/R23 保留参考实现；components/warroom.py:490 惰性 import dashboard_feeds=旧链内活但整体弃用态；净删=Owner 门位。
- **桌面壳：已接线**（8890 探活+app:// 回退）。
- **前端三源一致性机检：未接线**——manifest 71×frontend_map 361×loader 54 三源无 R4 门（05 取证册 §三：两门均不读路由与方法面），修批完整性无人报警的根因仍在。

### 骨架勘误（必录：F111 入口口径冲突）
1. **三方口径现场**：①总册 F111 行=核心模块锚 `app_panel.py`、状态 built；②AGENTS.md §7 仪表盘行（本日 sed L110 实读）=**仍指 `app_panel.py`，并未改为 api_server.py 8890**（git log 最近修宪 5fe5f1a5fa=09-23 无此改动）；③盘面实态=生产入口 api_server.py 8890 单端口一体（桌面壳 spawn），app_panel DEPRECATED 2026-08-29。任务书前提"AGENTS §7 已改 api_server.py 8890"与盘面不符，如实录。
2. **勘误主张**：F111 生产真源应记 `src/zephyr/frontend/dashboard/api_server.py:8890`（built 成立性不变），app_panel.py 标注 deprecated-retained；AGENTS §7 行与总册 F111 行的改写=等长替换事项，**归 Owner/总筹**（涉宪法定版文件，本矿道禁改）。
3. wiring_gap 裁-3"F111 入口口径（app_panel vs api_server，随 M6 退役裁）"维持待裁，本卷提供第③方实证补强。
4. 前端接线红点翻绿勘误：M6 01 册 §四-1/2 红黄点与 05 册两残留，本日复跑全清（loader 54/api 方法在/容器 id 一致/ZK.api 通道）——红→绿时点=0032 接线批后至本日之间，总册若引用 M6 红点须同步。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 入口口径三方冲突（总册+AGENTS 均指弃用件） | Owner 门：总册 F111 行+AGENTS §7 行等长改写为 api_server 8890；app_panel 退役时点另裁 | P1 |
| 2 | 三源（manifest/frontend_map/loader）无一致性机检 | FRONTEND-MAP 增 R4（05 取证册 §七既定修法，引用不重裁） | P1 |
| 3 | app_panel+components 17 件+panel 启动项弃用挂账 | Owner 净删门（新版完全涵盖确认后） | P2 |
| 4 | 两门 own_scope=false 连坐面 | 随 M8 包13 机生补全批 | P2 |
| 5 | 54 页运行态冒烟依赖起服 | 移交施工批 playwright 冒烟常态化 | P2 |

## 五、自审闸三态

**挖干（九子包实数+54/54+40 方法+35 启动项实测+弃用头注实读+红线点逐项复跑）✅；待裁（缺口#1 口径改写=Owner 宪法文件门位；app_panel 退役时点）；待挖（71 features 逐模块运行态=随施工冒烟批）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
sed -n '110p' AGENTS.md   # 仪表盘行：实态仍 app_panel.py
sed -n '19,24p' src/zephyr/frontend/dashboard/app_panel.py   # DEPRECATED 2026-08-29 R22/R23
python -c "
import re,sys,types;from pathlib import Path
sys.modules['pytest']=types.SimpleNamespace()
t=Path('src/zephyr/frontend/dashboard/web/core/loader.js').read_text(encoding='utf-8')
pages=re.findall(r'\"([a-z0-9_]+)\"',re.search(r'PAGES\s*=\s*\[(.*?)\]',t,re.S).group(1))
disk={p.stem for p in Path('src/zephyr/frontend/dashboard/web/pages').glob('*.html')}
print('wired=',len(pages),'disk=',len(disk),'unwired=',sorted(disk-set(pages)))"
grep -cE "^\s{4}(fetch|post)\w+\s*[:(]" src/zephyr/frontend/dashboard/web/services/api.js   # 40
grep -n "schedulegate-body" src/zephyr/frontend/dashboard/web/features/schedulegate/schedulegate.js | head -2   # 已统一
grep -n "fetchJson" src/zephyr/frontend/dashboard/web/features/budget/budget.js | head -1   # 已走 ZK.api
python -c "import sys,types;sys.modules['pytest']=types.SimpleNamespace();from zephyr.frontend.dashboard.services_registry import SERVICE_CATALOG;print('n=',len(SERVICE_CATALOG))"   # 35
```
