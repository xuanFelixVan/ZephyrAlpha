---
ttl: task_bound
session: st-ailayer-fullflow-frxc
date: 2026-09-25
---

# M6 前端API链 · 补挖波 · 分册 05 · F112"api↔前端契约无机检"取证册

> 挖矿会话 st-ailayer-fullflow-frxc ｜ 2026-09-25 ｜ 只读挖矿+本目录零 commit。
> 命题来源：总筹册 §四 M6 行【黄】"api↔前端契约无机检"+02 册 §四-5"49 端点零自动化契约测试"。本册＝该黄点的**取证收口**：机生差集实测+测试面/门禁面穷尽+活体漂移案例链，供 R4 门立项前的事实基线。只取证不施工。

## 一、命题定义
一句话：api_server.py 47 路由（服务端契约面）、web/services/api.js 43 方法（客户端投影面）、web/features/** 调用点（消费面）三面的一致性**无任何机器校验**——无门禁规则覆盖、无契约测试断言，漂移靠挖矿人肉发现、修复批不完整也无人报警。

## 二、三面机生差集（2026-09-25 实测，复核命令见 §六）
| 面 | 实测 | 机检状态 |
|---|---|---|
| 服务端路由 | app.routes /api 计 47（GET 44+POST 5 含 1 诚实拒执行；与 02 册口径一致） | FastAPI 可机生投影（`m.app.routes` 一行即得）——无人产 |
| api.js 客户端方法 | 43 个定义（`^\s{4}(fetch|post)\w+\s*[:(]` 口径）；字面 `/api/...` 引用 22 处，其余经 fetchJson('/api/xxx') 拼接 | 字符串拼接形态使朴素 path 反解不可靠——需 AST 级 |
| 消费调用点 | `ZK.api.*` 调用 36 个不同方法名；**悬空（调未定义）＝0**；裸 fetch（非 ZK.api）8 处 | 调用点散在 54 页 features 中，无静态闭环 |
| 路由↔方法差集 | api.js 零字面引用的路由 25 条（tdm/govm/factory/chainmap 族经 tdm.js:20 等直连绝对 API_BASE＋backtest 族经方法构造）——其中 tdm/govm/factory 直连=裁定模式（tdm.js:20 注释"app:// 模式下相对 fetch 必断故用绝对 BASE"），**但仍在机检视野外**：路由改名无任何闸拦截 | 无 |

## 三、门禁面穷尽（为什么无机检=结构性，非遗漏）
| 门/工具 | 规则覆盖 | api 契约覆盖 |
|---|---|---|
| FRONTEND-MAP（gate_registry.yaml:1144-1153，priority=137，硬断） | R0 id 重复 fail／R1 backend_ref 五前缀类型化 fail／R2 map↔manifest 双向 warn／R3 file 存在 warn／R4 frontend_map↔depgraph frontend_ref 总线对账（check_frontend_map.py:8-90） | **零**——不读 api_server 路由，不读 api.js 方法面 |
| FRONTEND-TRUTH-SOURCE（:1155-1164，warn-only） | 启发式：staged web/**/*.js 是否出现 fetch 引用（frontend_truth_source_gate.py:204） | **负作用**——裸 fetch 也算"已接线"，拦不住通道违禁（01 册 §四-2 已记 budget.js 实例） |
| 两门 own_scope | **均 false**（gate_registry.yaml:1153,1164）——违宪法 §3.1 own-diff 默认，属 M8 RC-10 连坐面（引用不重裁，归包13 机生补全批） | — |
| test_dashboard_smoke.py | playwright 结构冒烟：①PAGES⊆DOM 注入（modlib 漏挂类回归）②stockq/overview 结构段 | **零 api 契约断言**；且需 playwright+chromium，非提交闸 |

## 四、测试面穷尽
- tests/frontend/ 19 文件中涉 api_server/TestClient 仅 5：test_api_server_ch_timeout.py（CH 防线）、test_api_server_cron_single_source.py、test_ops_alert_feed.py（feed 模块）、test_promotion_advisory_api.py（单域投影）、test_dashboard_smoke.py（结构冒烟）——**均非"路由×客户端方法"契约测试**；无 FastAPI TestClient 全路由契约件（02 册 §四-5 修法"先写 5 写端点+高频读端点"未立项）。
- test_frontend_api_proxy.py 是旧 Panel 的 MOD-FE-011 代理路由表测试，非 api_server 契约。

## 五、活体漂移案例链（无机检的实证代价，全部 file:line 可复核）
1. **schedulegate 三断点（原 M6 红）→ 0032 接线批修了 2/4，余 2 点至今裸奔**：
   - 已修（本册实证）：api.js:95-101 三方法（fetchSchedulegateQueue/Skeletons/postSchedulegateConfirm）已在——机扫悬空=0 的成因；loader.js:6 PAGES 已含 "budget","schedulegate"（52→54 页），:185-187 loadJs 两 feature 已挂。
   - 未修①：容器 id 失配仍在——pages/schedulegate.html:6 供 `#schedulegate-body`，schedulegate.js:93,118,122,175,177 五处仍操作 `#sg-body`→box 恒 null→静默 return，**页面 wired+方法在+容器空=白板页**，无门无测试报警。
   - 未修②：budget.js:83 仍 `fetch('/api/budget-advisories')` 相对路径裸调——app:// 回退模式必断（tdm.js:20 同坑已注释），FRONTEND-TRUTH-SOURCE 因"有 fetch"照样放行。
   - **取证结论**：修批不完整之所以无人知，正因为三面无一致性机检——修法已在 01 册 §四-1 草案（四点闭合）但缺闸保证"修完即验收"。
2. **调用点别名形态使"朴素 grep 机检"不可靠**：backtest 族 7 方法（fetchBacktestList/postBacktestRun 等）在 bt-engine.js 经别名/解构调用，`ZK.api.<m>` 正则扫不出——任何 R4 机检必须 AST 或运行时级，字符串级会重蹈人肉误判（本册首次机扫即踩，已纠正）。
3. **历史漂移成本**（M6 两册已记，本册归因收口）：schedulegate 三方法缺失=挖矿人肉发现；services_registry 头注"16 启动项"漂移（实际 35）；miniqmt retire 日期语义靠前端本地日期比较（02 册 §四-4 时间炸弹）——三类同根：契约面变更无闸。

## 六、复核命令（10 分钟）
```bash
# 1. 路由面机生（应 47）
python -c "import sys,types;sys.modules['pytest']=types.SimpleNamespace();import zephyr.frontend.dashboard.api_server as m;print(len([r for r in m.app.routes if getattr(r,'path','').startswith('/api')]))"
# 2. 悬空调用复扫（应 0——0032 批已补三方法）
grep -n "fetchSchedulegateQueue" src/zephyr/frontend/dashboard/web/services/api.js | head -1
# 3. 容器 id 失配复现（js 应 4 处 sg-body，html 应 1 处 schedulegate-body）
grep -n "sg-body" src/zephyr/frontend/dashboard/web/features/schedulegate/schedulegate.js | head -4
grep -n "schedulegate-body" src/zephyr/frontend/dashboard/web/pages/schedulegate.html
# 4. budget 裸 fetch 复现（应命中 :83 相对路径）
grep -n "fetch('/api" src/zephyr/frontend/dashboard/web/features/budget/budget.js
# 5. 两门 own_scope=false 复现
sed -n '1153p;1164p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
# 6. R4 现行覆盖面（应只见 frontend_ref 总线对账、无 api 方法投影）
grep -n "R4\|api" scripts/governance/d5_architecture/generators/check_frontend_map.py | head -6
```

## 七、三态
- **取证完备**：三面差集机生可复跑、门禁/测试面穷尽、活体案例 4 例全锚点。
- **可施工（已有登记，引用不重裁）**：R4 门扩展（01 册 §四-3）+机生差集脚本喂门（02 册 §五-3）+TestClient 契约测试（02 册 §四-5）+0032 余量两点闭合（01 册 §四-1）。
- **待裁**：tdm/govm/factory 直连 API_BASE 模式是否纳入机检面（现=裁定豁免模式，纳入则 R4 需白名单）；两门 own-scope 化（随 M8 包13，不独立立案）。
