---
ttl: task_bound
title: S13 前端转正汇报页+拍板挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S13 前端转正汇报页+拍板（转正建议页+Owner 前端拍板按钮）

> 骨架定位：Owner 指令——**前端做一个专门负责转正建议汇报的页面，Owner 在前端拍板**。
> 拍板后策略进入整装（不是单策略直进实盘）。当前=❌ 未建（后端 OwnerTokenGuard 已有但无
> 执行器）。本环节挖矿核心：①页面怎么挂进前端（新版 web/ 的注册模式）；②页面↔API 契约
> 惯例；③审批/确认类 UI 先例可抄哪件；④FSM 状态怎么透出。
> **【施工班 2026-09-15 回填】C5 已上线：web/pages/promotion.html+features/promotion 引擎（建议卡三态配色 promote 绿·hold 灰·demote 红/need_confirm 两段式拍板/30s 轮询拍板在途暂停/空态诚实文案）+GET /api/promotion-advisories+POST /api/promotion-decide+五登记；api_server [INVARIANTS] 头注扩容留痕（第四写端点，授权=Owner 通宵指令+宪法 §5 拍板门位数字化）。**

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 前端版本地圈——旧 Panel 已废，新页必须进 web/

- `src/zephyr/frontend/dashboard/app_panel.py` L19-22：**DEPRECATED（2026-08-29，Owner 裁定
  R22/R23）**，"新版正式家=src/zephyr/frontend/dashboard/web/（拆分转正，41 页）"——
  C5 新页**禁止**挂 Panel Tab，必须走 web/ 体系。
- web/ 体系结构：`web/index.html`（外壳+侧栏导航）+ `web/pages/<id>.html`（48 个页面片段，
  loader fetch 后注入 #main-root）+ `web/features/<page>/`（页面引擎 JS，2026-09-12 拆件批
  37 件）+ `web/core/app1.js`（宿主 chrome：go() 路由/主题/折叠）+ `web/core/loader.js`
  （加载链）+ `web/services/api.js`（唯一 HTTP 通道）。

### 1.2 新增一页的最小步骤清单（必答②，照 chainmap/factory 先例抄）

1. **建页面片段** `web/pages/promotion.html`（`<div class="page" id="p-promotion">…`）。
2. **loader.js 注册**：`PAGES` 数组（loader.js 头部）追加 `"promotion"`（fetch 片段清单）。
3. **index.html 挂导航**：侧栏加 `nav-item`（`onclick="go('promotion',this)"`，参照
   index.html L21-49 的 A 股组条目格式；顶栏组高亮由 app1.js `GRP_OF` 表兜底，新页需在
   `go()` 的 GRP_OF 映射补一行）。
4. **页面引擎** `web/features/promotion/promotion.js`：新规范=registerFeature 模块
   （契约：init(chart,ctx)/render(d)/destroy()，样式自注入，模块间只经 ZK.bus——
   features/manifest.yaml 头注）；旧惯性=全局函数族+onclick 直绑（ord-ticket.js 模式，
   Tier-2 待契约化）。**新件按 manifest 头注走模块制。**
5. **双登记**：`web/features/manifest.yaml`（模块契约真源）+ `web/frontend_map.yaml`
   （★唯一真源，Owner 2026-09-04 裁定；backend_ref 类型化 module:/api:/table:）——
   `scripts/governance/d5_architecture/generators/scan_frontend_pages.py` 半自动补登。
   （注意 frontend_map 生成器依赖，新页漏登记会被对齐闸拦。）

### 1.3 页面↔API 契约（app:// 不存在，实况=ZK.api 直连 127.0.0.1:8890）

- `web/services/api.js` L4-22：`BASE='http://127.0.0.1:8890'`，`fetchJson(path, timeoutMs,
  opts)` 唯一通道（GET 缺省 5s/POST 15s，AbortController）；失败必 reject，调用方回退演示
  数据并标"演示"（演示诚实纪律）。
- POST 惯例先例（api.js L60/69/84）：`postFrameworkBacktestRun` / `postBacktestRun` /
  `postServicesControl(id,action,confirm)`——**拍板按钮照 postServicesControl 抄**。
- 后端 `src/zephyr/frontend/dashboard/api_server.py`：FastAPI，头注不变量="只读服务（禁
  任何写副作用）"但**已有三个获准写端点**：POST /api/backtest-run（L883）、POST
  /api/framework-backtest-run（L1045，串行线程池 _FW_RUN_POOL L956）、POST
  /api/services-control（L1248，**分级闸门**：confirm 级不带 confirm=true 返回
  `need_confirm` 让前端弹确认框；guard/external/self 级一律拒绝）——拍板端点=第四个
  获准写端点，**需在头注不变量与裁定登记处留痕**（写权限扩张=宪法 §5 门位语义）。
- CORS 已放行 GET/POST（L53）。

### 1.4 审批/确认类 UI 先例（可复用清单）

| 先例 | 位置 | 可抄什么 |
|------|------|---------|
| 服务控制确认流 | `web/features/services/sv-page.js` L150-165 | **need_confirm→window.confirm→带 confirm=true 重发** 的两段式确认交互；badge 三态 class `b-warn/b-na/b-pass`（L131）=现成配色 |
| 盘中下单票据 | `web/features/live/ord-ticket.js` L21-38 | human_gated 二次确认文案+**"提交后进入 Owner 审批队列（演示——真实通道未接）"**——审批队列的前端壳已预留，C5 可将"待审批"状态接真 |
| 作战室决策卡弹层 | `web/features/warroom/wr-scenario-matrix.js`（openDecision/closeDecision） | 详情弹层+决策按钮布局范式 |
| 三态配色体系 | 全站 badge/Alert（web 色系 v7） | 待拍板(amber)/批准(green)/驳回(red) 状态卡 |

### 1.5 FSM/注册表状态在 API 层的透出现状

- `GET /api/strategies`（L549）= **pf_core StrategyRegistry**（kebab 策略，代码注册表），
  不是 strategy_registry.yaml 的 lifecycle_status——**lifecycle 五/八态目前无任何 API 透出**。
- strategy_registry.yaml 在 api_server 仅作中文名翻译源读取（`_tdm_ref_names` L2115）；
  /api/tdm/verdicts（L2395）有"判定类数据透出"的响应形态先例可参照。
- 词表注意：FSM 五态（candidate/sim/production/shelved/retired）vs 注册表八态
  （+backtest/paper/live/monitoring/decayed）分裂（S10 §1.4）——**转正页的状态列显示口径
  必须等 S10 施工 3 词表统一后定稿，本班先按注册表现值显示+标注口径待统一**。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ⑤前端：版本地圈 | app_panel.py L19-22 DEPRECATED 实锤；web/ 48 片段+37 引擎+loader 加载链 | **signal** |
| R2 | ⑤前端：页面注册五步 | loader.js PAGES+go() 路由+GRP_OF+initFn 钩子（app1.js）+index.html nav | **signal** |
| R3 | ⑤前端：API 通道契约 | api.js BASE 8890 fetchJson；POST 三先例 L60/69/84；演示诚实纪律 | **signal** |
| R4 | ④后端：写端点闸门 | api_server 只读不变量+三写端点；services-control need_confirm 分级闸 L1248-1265；CORS L53 | **signal** |
| R5 | ⑤前端：审批 UI 先例 | sv-page.js L150-165 确认流；ord-ticket.js L21-38 审批队列演示壳；wr 决策卡 | **signal** |
| R6 | ⑥数据字段：lifecycle 透出 | /api/strategies=pf_core 注册表；strategy_registry.yaml 仅翻译源 L2115；无 lifecycle 端点 | **signal**（断点） |
| R7 | ③机制（外部）：审批 UX | four-eyes/maker-checker（flagsmith.com、help.sap.com，访问 2026-09）；审批 inbox 三态+理由留痕惯例 | **signal** |

轮次判定：7 signal / 0 noise。封批转施工。

## 3 业界与开源对照

- **审批工作流 UX**：four-eyes/maker-checker（Flagsmith/SAP，URL 见 R7）标准形态=待办
  inbox（列表+详情+双按钮+驳回理由必填+审计留痕）——转正页照此形态：建议卡列表（待拍板
  置顶）→点开证据卷宗→批准/驳回+理由→留痕回执。
- **授权分层对照**：Futu 模拟户免解锁/实盘户 unlock_trade 两层门（openapi.futunn.com，
  访问 2026-09）支持把拍板令牌做成"仅实盘流转动作需要"；ibker 会话级 2FA（见 S12 §3）
  对照下，本站无会话体系，**每动作一次令牌**半径更小。
- **单页应用惯例**：本项目 web/ 自研轻量 SPA（hash 路由+片段注入）与 Grafana/Alertmanager
  的"告警→silence→ack"三态管理同构，拍板页=同款三态（pending/decided/expired）管理面。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | lifecycle 无 API 透出 | /api/strategies 是 pf_core 注册表；无 lifecycle 端点 | 页面无法显示策略当前生命周期 |
| 2 | 无拍板写端点 | api_server 仅三写端点均非审批 | 拍板无后端承接 |
| 3 | api_server"只读"不变量需第四次裁定扩张 | 头注 L8/L52 | 不留痕扩张=违反自家契约 |
| 4 | owner_token 前端怎么合法带 | S12 §1.3：token 尚无签发 | 无凭据体系前拍板按钮是空的 |
| 5 | FSM/注册表词表分裂 | lifecycle_fsm 五态 vs 注册表八态 | 页面状态口径未定 |
| 6 | 审批台账无处落 | 无 decision 存储 | 拍板留痕断链 |
| 7 | 前端双登记易漏 | frontend_map.yaml 唯一真源+生成器校验 | 漏登记被对齐闸拦回 |

## 5 施工项建议（C5 前端转正页+拍板方案雏形）

1. **GET /api/promotion-advisories**（api_server 新增，只读）：扫描
   `docs/_working/pipeline-research/promotion-advisories/advisory-*.json`（C4 产物），
   合并 strategy_registry.yaml 当前 lifecycle_status，返回
   {advisory_id, strategy_id, name_zh, recommendation, evidence:{screen_batch, memo_ref,
   fw_artifact}, lifecycle_status, created_at}。验收=与盘上 advisory 文件零 diff；空目录
   返回空列表不报错。
2. **POST /api/promotion-decide**（api_server 第四写端点，头注不变量同步修订+裁定留痕）：
   body={advisory_id, strategy_id, decision: approve|reject, owner_token, reason}；流程=
   owner_token.verify（S12 §5.3，常量时间比对，指纹留痕）→ `build_strategy_fsm(sid).
   transition(PRODUCTION, {"owner_token": token})`（FSM 执行器首落地）→ registry_writer
   更新 lifecycle_status → decision 台账落
   `docs/_working/pipeline-research/promotion-advisories/decisions/`（json：令牌指纹/时刻/
   理由）→ Alerter 回执 Owner。验收=错 token 401 语义+FSM 非法转换拒+重放同 advisory 拒
   （已决幂等）；approve 后注册表状态变化可查。
3. **页面五步**（§1.2 清单）：pages/promotion.html（建议卡列表：策略名/当前态/建议/两月
   判定缩略/证据链接）+ features/promotion/promotion.js（registerFeature 模块制）；
   拍板交互抄 sv-page：批准→输入 owner_token（粘贴一次令牌）+reason→window.confirm
   二次确认→POST；响应 need_token/invalid_token 就地提示。三态配色复用 b-pass/b-warn/
   b-na。
4. **双登记**：features/manifest.yaml + frontend_map.yaml（backend_ref=api:/api/
   promotion-advisories）+ scan_frontend_pages.py 补登。
5. **整装语义锚定**：页面文案与拍板后流转写明"批准=进入整装组合（TDM sleeve 权重已挂），
   非单策略直进实盘"——与 Owner 口述流程（骨架 §2）一致；实盘下单仍由 S14/C6 通道承载。
6. **远期登记（不在 C5）**：拍板后自动触发整装回测重跑回执（依赖 C3）；多策略批量拍板；
   拍板页接 NotificationRouter ack 状态。

## 6 封矿结论

- 矿脉层面：7 signal/0 noise，注册模式、API 契约、UI 先例、状态透出断点全部挖透，封批。
- 方案层面：C5 = 一读一写两端点+一页一引擎+双登记，先例四件全齐（services-control/
  ord-ticket/wr 决策卡/三态 badge），无新框架引入；消灭"Owner 无界面可看建议、拍板靠
  口头/工单"人工位，**施工**。
- 一句话结论：**新页照 chainmap/factory 先例五步挂进 web/（旧 Panel 已废禁用）；拍板按钮
  抄 sv-page 的 need_confirm 两段式；最大断点不是前端而是后端——lifecycle 无透出 API、
  拍板无写端点、token 无签发，三件后端补齐则前端两天可落。**

## 7 施工班状态回填（2026-09-15）

- C5 全量落地（6df0e6b898）：页面+引擎按 §5 方案执行；拍板交互=sv-page 同款 need_confirm 两段式；三态配色复用站点 badge 体系；五登记（loader.js PAGES/index.html nav-item/app1.js GRP_OF/manifest.yaml/frontend_map.yaml F-PROMO-BOARD·F-PROMO-DECIDE）+scan_frontend_pages 在册核验。
- 端点健壮性：执行器缺位降级 200 ok:false（空态不 500）；400 非法输入/503 执行器缺位/500 意外；FileNotFoundError→业务拒绝 not_found（红蓝发现#2 修复）；TestClient 12 例+前端门禁 49 例全绿。
- §4 堵点状态：1/2/3/4/6 已解（lifecycle 透出经 /api/promotion-advisories 合并注册表现值；拍板写端点已上；头注不变量扩张已留痕；token 签发体系已建；decision 台账=decide 链内落档）；5（词表分裂）维持挂起——页面按注册表现值显示；7（双登记）由生成器核验兜住。
