---
ttl: task_bound
title: 深度审查作业簿——面板API服务
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：面板API服务（I26）

- 状态: **已审**
- 级别: P2｜类型: 前端
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/frontend/dashboard/api_server.py:56`（FastAPI app；CORS 中间件 :57；_ch_exec :91；main :4441）
- 生产调用方: 前端面板（app_panel/app 静态页）+ 运维轮询；HTTP 127.0.0.1:8890
- 测试文件: 分散（pytest 守卫 :4435 防测试启探针线程）；无系统级 API 测试
- 备注: 4453 行单文件/72 次提交=全仓最高变更热力之一；审查为"结构+高危点抽样"，非逐端点全审（长尾见 §6）

## 1 对象快照

- 审查范围：服务装配（FastAPI+CORS）、CH 单连接锁体系（_ch/_ch_exec + 弃连自愈 + 双道超时）、4 个 POST 控制端点（backtest-run/framework-backtest-run/services-control/promotion-decide）、数据源监管真源端点（sources-status 读 source_health 日志+data/failures）、ops 通知线程、启动防弹（SEM_FAILCRITICALERRORS）。
- 排除项：~40 个只读 GET 数据端点的逐个 SQL 审（抽查 kline/stock-header/sources-status 三个代表）；services_registry/promotion_advisory 执行器内部（下游对象）；app_panel/app.py 前端渲染（I27/I28）。
- 测试覆盖概况：有 pytest 进程守卫（防测试启生产线程）；端点级契约测试未见系统性覆盖。
- 材料包缺项：无近 N 天 API 错误率/锁等待超时频次（运行时证据包缺）。
- 变更热力：72 次提交，**全仓最高热区**（2026-09-01/09-03/09-10 三轮锁与超时加固注释在案）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗 | **P0 候选：Owner 门位端点无鉴权 + CORS 全源放行**：`allow_origins=["*"]`（:57）使任意网页可跨域调用本机 8890 全部 API 并**读取响应**（GET /api/position 持仓、订单、策略、服务状态= drive-by 数据外泄）；`POST /api/promotion-decide`（:4350-4360）执行 Owner 拍板（approve=进整装组合）且 token=None 服务端自取——HTTP 层即唯一门禁，confirm 闸只防误点不防攻击者（攻击者直接带 confirm/decision）；services-control 可被外部网页停服务（断供）。DNS rebinding 可进一步绕过同源策略直读 | api_server.py:57（CORS *）+ :4350-4377（promotion-decide 无鉴权链）+ :1294-1307（services-control）+ :4447（127.0.0.1 绑定=仅减远程直连面） | **P0** | 在同机浏览器任意测试页发 `fetch('http://127.0.0.1:8890/api/position').then(r=>r.text()).then(console.log)`——返回持仓 JSON 即实证（CORS 反射 ACAO:*）；再发 promotion-decide POST 验证 200 |
| E 对抗 | 半开连接防线质量高（正面确认）：锁获取 30s 限时防线程池耗尽、查询级 max_execution_time=12s、异常即弃连重建（:109-126 注释三轮实证驱动）——单连接锁风险已被三层缓解 | api_server.py:87-126 | — | — |
| A 深度 | 全部 CH 查询单连接串行：4453 行 ~45 端点共用一把 _ch_lock+一条 admin 连接——慢端点（12s 上限）最长阻塞全面板 30s×N；slot 机制（dashboard 独立槽）已隔离 writer 流量，残余=面板自竞 | api_server.py:79-126（单锁单连接） | P3 | 压测：并发请求两个 12s 级慢端点测第二响应延迟 |
| B 上游 | 连接角色=**admin（base 全权账号）**：面板查询持有 DDL 级账号（database_service.py:168-170），RBAC 治理残留例外（详见 I24 D-2）；当前端点 SQL 均为 SELECT，账号收敛无功能阻塞 | api_server.py:82-89 | P2 | 切 reader 槽回归全端点 |
| A 深度 | 端点 SQL 卫生（抽查 kline/stock-header）：表名白名单 _PERIOD_TABLE、tc 来自 DESCRIBE、symbol isalnum 校验、参数化 %(s)s——无内插漏洞面（正面确认）；_time_col 无表名白名单校验但调用方全传常量 | api_server.py:167-190, 137-152 | — | grep _time_col 调用点核参数来源 |
| E 对抗 | errors 直通前端：`{"ok":False,"error":str(exc)[:200]}`（kline 等）与 500 detail str(exc)[:300]——CH 错误文本（含表名/账号线索）对外暴露；本地绑定下降级为 P3 | api_server.py:192, 4377 | P3 | 触发一次 CH 错误看响应体 |
| C 下游 | sources-status 读 source_health 日志+failures JSON 有逐文件 try 容错（脏文件跳过）；`datetime.now()` 本地时区做 generated_at 戳（:1399）——展示层时间戳无时区后缀，跨时区读取歧义 | api_server.py:1362-1377, 1399 | P3 | 观察端点输出 |
| A 深度 | promotion-decide 依赖 promotion_advisory.decide 存在性检查+异常映射（400/503/500）规范；FileNotFoundError→业务拒绝设计正确（:4374-4375） | api_server.py:4366-4379 | — | — |
| D 旁系 | 4453 行单文件：路由/CH 访问层/QMT 桥读取/策略快照/ops feed 五类职责同居——72 次提交的高热与三轮锁加固史表明改动集中度高，回归风险随行数增长；已有拆分先例（services_registry 已外置） | api_server.py 全文 + git log --oneline 72 次 | P3 | 收口方裁拆分节奏（属施工决策） |
| E 对抗 | ops feed 线程 broad except 静默（:4427-4429）——通知板死了前端横幅静默空态（fail-safe 有意），但"通知通道死亡"本身无通知（同 I20 结构性盲区） | api_server.py:4419-4431 | P3 | 注入 tick 异常观察无任何告警 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| localhost API 的 CORS/CSRF/DNS-rebinding 暴露面 | **驳回现状（业界明确反模式）**：GitHub 安全博客专文论述 localhost 服务的 CORS 配置错误与 DNS rebinding 危险，建议服务端校验 Origin、不因"来自 localhost"而信任请求；OWASP WSTG 有 CORS 测试专章——本项目 allow_origins=["*"]+无鉴权控制端点正踩两书红线 | GitHub Blog: Localhost dangers — CORS and DNS rebinding, github.blog, 2021 存档（2025 仍为权威论述）：https://github.blog/security/application-security/localhost-dangers-cors-and-dns-rebinding/ ；OWASP WSTG CORS 测试指南, owasp.org, v4.1：https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/11-Client_Side_Testing/07-Testing_Cross_Origin_Resource_Sharing |
| 人机门位数字化的最小鉴权（even MVP） | **立卡候选**：最小半径做法=Loopback token（启动时生成一次性 token 写本机文件，前端同机读取附带）或 Host/Origin 白名单校验；token=None+全源 CORS 连 MVP 线都不达 | FastAPI CORS 官方文档（allow_origins 应为显式清单）, fastapi.tiangolo.com, 2025：https://fastapi.tiangolo.com/tutorial/cors/ ；MDN CORS, developer.mozilla.org, 2025 |
| 只读数据面板单一 CH 连接+锁串行 | 对等已有：单连接+应用层锁是小规模 dashboard 常见务实解（vs 连接池），且有超时防线；规模增长再立卡池化 | 受限流与前述检索批次覆盖（clickhouse-pool 等已在 I24 引） |

## 4 缺陷清单

1. **D-1（P0）Owner 门位+持仓数据经浏览器任意网页可达**
   - 现状→证据：CORS `allow_origins=["*"]`（:57）+ 4 个无鉴权 POST（含 promotion-decide=宪法 §5 high 域 Owner 门位的数字化承载，:4350-4377）+ GET 全量账户/策略数据可读（:57 ACAO 反射使响应可被外部源 JS 读取）。
   - 影响：Owner 浏览任意网页时，该网页可 ①静默读持仓/订单/策略（信息外泄）②approve/reject promotion advisory（**人机门位被绕过**=闸门失效，production 流转不经 Owner）③停停启启服务（断供）。爆炸半径=全账户决策链信任根。
   - 前置条件：api_server 运行中（schtasks 常驻即满足）+ Owner 浏览器访问恶意页（或任何带外链广告的页面）；DNS rebinding 可免于 CORS 读取限制。
   - 建议修法（最小半径三件套）：①`allow_origins` 改显式 `["http://127.0.0.1:8890"]`（同源页面本不受 CORS 约束，此配置只服务外部调试时收紧）；②控制类 POST 校验 `Origin`/`Host` 头必为 127.0.0.1:8890；③promotion-decide/services-control 加 loopback token（启动生成写 .runtime，前端加载时取）。三者皆小改，不影响功能。
   - 验证法：轴 E 行 fetch 实证；修后同 fetch 被拒（CORS/403）。
2. **D-2（P2）admin（base）账号作面板查询连接**（详见 I24 D-2）：切 reader 槽；若 DESCRIBE/系统表查询需要，开 reader 权限的专用槽而非 base。
3. **D-3（P3）单锁单连接全端点串行**：12s 慢查询阻塞全面板；已有 30s 锁超时+12s 查询超时兜底，规模再涨立卡池化（I24 SOTA 行）。
4. **D-4（P3）CH 错误文本直通前端**：截断+归一化 error code。
5. **D-5（P3）4453 行单文件/72 次提交**：按职责拆模块（路由层/CH层/桥层/feed层），先从 QMT 桥与 ops feed 切出。
6. **D-6（P3）展示时间戳 naive datetime.now()** + ops feed 死亡无自告。

## 5 挂起疑问

- promotion_advisory.decide 内部是否有第二道确认（如 advisory 状态机要求前置 review 完成）能部分缓冲 D-1 的门位绕过——需审 promotion_advisory（策略域对象）后定 D-1 最终严重级；**在未证实前按 P0 报**。
- 8890 是否有防火墙/本机访问控制缓解（Windows 防火墙默认拦外部入站 127.0.0.1 无关，远程面已由绑定限制）。
- backtest-run POST 的资源限额（无鉴权触发重算的 DoS 面，D-1 修后自然收敛）。

## 6 完备性自评

- 六轴全查：A（锁体系/超时防线/SQL 卫生）、B（admin 账号+DESCRIBE 缓存）、C（前端+运维轮询消费方、failures 读取容错）、D（services_registry 拆分先例+单文件热区）、E（五问：静默失败=feed 死亡、假阳性=confirm 只防误点、断了没人知道=D-6、重复触发=POST 幂等性未证（backtest-run 重复提交会双跑?见长尾）、时序=锁队列）、F（GitHub/OWASP/FastAPI 三源带 URL）。
- 长尾（未逐项审，收口方知悉）：~40 个 GET 端点逐个 SQL 与数据口径；backtest-run/framework-run 后台线程的状态机与并发重入；services_registry.control_service 的实现（stop 命令对保命进程的保护边界）；promotion_advisory.decide 内部门位链。
- 总评：工程韧性（锁/超时/自愈/启动防弹）是全仓最佳实践区；安全边界（鉴权/CORS）与之严重不匹配，一票拉回。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P0 CORS */无鉴权 promotion-decide（Owner 门位）/持仓 drive-by 读取: 挂起登记（晨报置顶；本机绑定但浏览器网页可驱动 localhost）。修复=token 鉴权+收 CORS，需与前端联动裁定。
