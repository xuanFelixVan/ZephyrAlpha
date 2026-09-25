---
ttl: task_bound
---

# M6 前端API链 · 分册 03 · 面板缓存 TTL 全清单（api_server 后端缓存 + 前端 SWR/loader + 旧 Panel 组件 + IBT 面板缓存）

> 挖矿会话 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿。
> 背景：R-022 验收（docs/_working/integrated_backtest/ibt_remedy_a_acceptance.yaml:53）"面板缓存已被 TTL 清空，本次为从 CH 原始数据全量重建（kline_daily_hfq/load_history 路径不变）"——本册穷尽前端/API 链全部缓存及其失效机制，回答"缓存失效/数据断供时前端表现"。

## 一、环节定义与边界
一句话：前端/API 链三层缓存（后端进程内缓存、浏览器 localStorage SWR、IBT 面板 pickle 盘缓存）的 TTL/失效语义台账——失效机制现况=三种范式并存（TTL 计时 / mtime 指纹 / 目录指纹），无统一管理。
- 供料方：api_server 内存态、浏览器 localStorage、.runtime/tmp 盘面。
- 消费方：页面族渲染管线（02 册路由）、IBT 复跑链。

## 二、六向台账
| 向 | 实测证据 |
|---|---|
| 上游输入 | CH 查询结果/YAML 文件 mtime/产物目录指纹/回测面板 DataFrame（pickle） |
| 下游消费 | api_server 响应延迟（缓存命中=毫秒回包，api_server.py:584 注释）、页面首屏（SWR 先渲旧值 api.js:135-148）、IBT 复跑含金量（R-022 :53） |
| 自动化触发 | 无独立缓存守护进程；失效全靠请求路径内联判定；.runtime/tmp 的 TTL 清理由 reconciler 判定（src/zephyr/governance/audit/reconciliation_registry.py:7641"PID 存活 + TTL 双保险"） |
| 真源与注册表 | 缓存实现散在各端点内联（无统一注册表——本册即事实台账）；旧 Panel 组件缓存=components/experiment_history.py:201 lru_cache(maxsize=1) |
| 门禁与质量尺 | 演示诚实纪律：SWR 缓存态渲染须标"上次更新 HH:MM"（api.js:135-137,147-148）；失败/空数据不落缓存不覆盖渲染（api.js:175-179，红队 V6 实证）；测试禁启探针线程防写生产（api_server.py:4457-4459） |
| 当前运行状态 | 绿（语义齐备、降级路径全）；黄点=范式三足鼎立+SWR 无 TTL+缓存不可观测（§四） |

## 三、子模块清单（缓存级穷尽，grep _CACHE/TTL/lru 实测）
### 3.1 api_server 后端进程内缓存（12 处）
| 缓存 | file:line | 失效机制 | 断供表现 |
|---|---|---|---|
| _col_cache（表时间列 DESCRIBE） | :73,:139-153 | 进程生命周期（永不过期） | 表结构变更需重启 api_server |
| _BT_LIST_CACHE（回测列表） | :584,:634-647,:656-688 | 目录指纹 sig（产物目录变化即失效）+ts | 指纹命中=毫秒回包；目录不可达走异常 ok:false |
| _BMF_CACHE（作战地图阶段树） | :585,:596-628 | TTL 600s | 过期后下个请求重读 BattleMapReader |
| _ASSET（库内资产审计） | :1813 `_ASSET_TTL_SEC=600`,:2019-2045 | TTL 600s + refresh=1 后台线程重审（data-asset-audit daemon :2042） | st["ts"] 超期触发 `_asset_maybe_start`，旧值先回 |
| _TDM_CACHE（TDM 一张图） | :2144,:2325-2327,:2414-2415 | **mtime 指纹**（改 config/trading_decision_map.yaml 即失效重算） | YAML 改动秒级生效，无需重启 |
| _TDM_REFNAMES / _TDM_REFDESCS | :2145-2146,:2177;:2294,:2302 | TTL 600s（注册表低频变更口径） | 过期重扫注册表 |
| _FACTORY_CACHE / _FACTORY_LEDGER | :2500,:2607-2649;:2501-2502,:2516-2522 | mtime 指纹 / TTL 300s（台账只增口径） | 同 TDM |
| _GOVM_CACHE | :2664,:2681-2723 | mtime 指纹 | 同 TDM |
| _THREEHIGH_CACHE | :2727,:2745-2777 | mtime 指纹 | 同 TDM |
| _CM_GALAXY_CACHE（链图 L1） | :2784,:3096-3107 | TTL 600s per market | 首算 3-6s（api.js:111 注释），20s 前端兜底 |
| _CM_CLUSTER_CACHE（链图 L2） | :2785,:3217,:3350 | 级联失效：galaxy 刷新即 `.clear()`（:3108） | L1/L2 一致性由级联保证 |
| _CM_NAME_CACHE（symbol→公司名） | :2786,:3113-3134 | TTL 600s | ig_company_edge 覆盖不全"如实用"（:2786 注释） |
| _SCHTASKS_CACHE（服务总闸计划任务态） | services_registry.py:5,:442 | TTL 60s；控制操作主动 pop 失效（:320,:377） | "点了没反应"病灶根治留痕（Owner 实证注释） |

### 3.2 前端浏览器缓存（2 处）
| 缓存 | file:line | 失效机制 | 断供表现 |
|---|---|---|---|
| SWR localStorage（各数据页） | api.js:138-146（swrLoad/swrSave）、:164-180（swr 通用） | **无 TTL**：仅被新成功响应覆盖；fetcher 失败/空数据不落缓存不覆盖（:175-179）；缓存态渲染由调用方标"上次更新"（:135-137） | API 断供→页面永远显示最后一次成功数据+时间戳（诚实降级，不白屏不报错） |
| loader 破缓存 | loader.js:3（ZK_BUILD='20260915-1' 版本戳）、:15-16（loadJs 追加 ?v=Date.now()）、:26-29（页面片段 fetch cache:'no-cache'） | 迭代期强制绕过浏览器 HTTP 缓存 | 旧 JS 残留可用页头品牌行 b<版本> 一键定位（:2 注释，2026-09-01 ⚑12 实证） |

### 3.3 旧 Panel 组件（app_panel 链，DEPRECATED 但保留可跑）
| 缓存 | file:line | 失效机制 | 备注 |
|---|---|---|---|
| experiment_history lru_cache(maxsize=1) | components/experiment_history.py:201-209 | 手动 reset_experiment_history_cache（新 run 后调用） | 无 TTL，进程内 |
| QMT 桥健康周期刷新 | app_panel.py:414-434 | 3000ms add_periodic_callback；同文档幂等防重复注册（:429-433） | 全库首例周期回调模式 |
| pn Tabs dynamic=True | app_panel.py:481-486 | Tab 惰性构建 | 单 Tab 失败降级 Alert 不炸（:479-480） |

### 3.4 IBT 面板盘缓存（R-022 锚点，非 api_server 域但在本战役语义内）
| 缓存 | file:line | 失效机制 | 备注 |
|---|---|---|---|
| PANEL_CACHE（15 成员窗口面板 pickle） | scripts/backtest/ibt/ibt_runner.py:45（.runtime/tmp/ibt_panels）、:147-185（build_panels 命中即 read_pickle 毫秒回） | `.runtime/tmp` 24h TTL 卫生域（宪法 §9.4）+ reconciler PID/TTL 双保险判定（reconciliation_registry.py:7641）→R-022 复跑时已被 TTL 清空=从 CH 全量重建 | 池覆盖运行禁用缓存读+独立缓存键防串味（:148-151 `f"{wname}_pooloverride.pkl"`）——缓存键隔离纪律实证 |

## 四、堵点与病灶
1. **【黄】失效范式三足鼎立，无统一缓存注册表**：TTL（600s/300s/60s/30s）、mtime 指纹（tdm/factory/govm/threehigh）、目录指纹（backtest-list）三种机制内联散布 12+ 处（§3.1），新增端点靠复制粘贴既有模式——已是同域重复簇（宪法 §4.2 内收判据 w5_1"同域重复簇→收敛唯一"）。修法：抽统一 `_cached(key, ttl_or_mtime, builder)` 助手+缓存清单机生（喂 02 册 §五-1）。1 天，本车道可修。
2. **【黄】SWR localStorage 无 TTL 上限**：api.js:164-180 语义=永久 stale 直到新响应覆盖；跨周打开页面会先渲一周前数据（有"上次更新"标注兜底，诚实纪律成立但可能误导）。修法：swrLoad 读出后 ts 超 N 小时（如 24h）放弃缓存态直接走 loading。0.1 天，本车道可修。
3. **【黄】缓存不可观测**：全部缓存零命中率/年龄暴露面（无 /api/cache-stats 类端点），"改了看不到"类问题只能靠 ZK_BUILD 戳（loader.js:3）定位前端侧，后端侧（如 _col_cache 需重启）无痕。修法：debug 端点或日志暴露各缓存 built_at（多数缓存已存 ts/mtime 字段，只差投影）。0.5 天。
4. **【灰】断供时前端表现矩阵已完备（无病灶，登记为验收基线）**：CH 断连→端点级 ok:false（02 册 ERROR_CONTRACT :14）→前端三型降级：错误卡（budget.js:71-73）、降级徽章（tdm verdicts degraded:true api_server.py:2490，"台账不可达不冒充未验证" :2440）、静默保持缓存态（api.js:175-179）；页面级"API 断开（面板 API 未启动?）"文案（tdm.js:116）。该矩阵是 FRONTEND-TRUTH-SOURCE 之外的第二道演示诚实防线，施工时禁破坏。

## 五、提速与合并机会
1. §四-1 缓存助手合一即提速：四处 mtime 缓存同构逻辑合并后，新端点缓存接入从"复制 30 行"降到"一行装饰"。
2. _CM_CLUSTER_CACHE 级联失效（:3108 clear）是唯一已实现的关联失效——推广给 _TDM_REFNAMES（依赖注册表 mtime 可检测），消灭 600s 盲区。
3. IBT PANEL_CACHE 与 api_server 缓存无共享（不同进程域），勿误合并；.runtime/tmp 24h TTL 与 reconciler 的判定真源已在 reconciliation_registry.py:7502-7641 收敛，保持单点。

## 六、自审闸三态
**挖干可施工**：16 处缓存（12 后端+2 前端+3 旧 Panel+1 IBT）全部 file:line+失效机制+断供表现三列齐；R-022 锚点闭环（ibt_runner.py:45 ↔ acceptance.yaml:53）。
- 挖干可施工：§四-1/2/3 三个修法。
- 待裁：无（缓存语义取舍均已有 Owner 实证留痕，无需新裁）。

## 七、复核命令（10 分钟）
```bash
# 1. 后端缓存清单复现（应见本册 §3.1 全部条目）
grep -n "_CACHE\b\|_CACHE:\|_CACHE =\|TTL" src/zephyr/frontend/dashboard/api_server.py | grep -v "^.*#" | head -40
# 2. SWR 无 TTL 复现（swrLoad 应无时间比较逻辑）
sed -n '138,146p' src/zephyr/frontend/dashboard/web/services/api.js
# 3. IBT 面板缓存锚点复现
sed -n '45p;147,151p' scripts/backtest/ibt/ibt_runner.py
sed -n '53p' docs/_working/integrated_backtest/ibt_remedy_a_acceptance.yaml
# 4. 旧 Panel 组件缓存复现
sed -n '201,209p' src/zephyr/frontend/dashboard/components/experiment_history.py
# 5. 级联失效实证（galaxy 刷新清 cluster）
sed -n '3096,3108p' src/zephyr/frontend/dashboard/api_server.py
```
