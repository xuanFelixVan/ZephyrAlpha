---
ttl: task_bound
title: L11 案卷 F112 — API server（8890 单端口一体；49 路由记录/47 唯一路径本日实测；契约测试缺位维持）
session: zc-l11-20260927
---

# F112 API server（L 段 F2，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | CH 唯一经 DatabaseService 槽位（api_server.py:77-87 slot=dashboard）；QMT 文件桥 `_QMT_BRIDGE_STOCK_DIR = Path(r"E:\qmt_bridge\Stock")`（本日实取 :126——已由散写收敛为模块常量，盘符仍硬编码）；治理 YAML 三图 mtime 缓存（tdm/factory/govm+threehigh）；ai_layer.scheduling/budget_analyzer/promotion_advisory 投影 |
| 下游消费 | web/services/api.js（BASE=127.0.0.1:8890）40 方法定义（本日 grep 实数）；tdm/govm/factory 直连绝对 API_BASE（裁定模式）；桌面壳 /api/health 探活 |
| 自动化触发 | 导入即启 3 daemon（bt-strategy-warm/data-asset-audit 10min/ops-alert-feed 30s；pytest 在 sys.modules 不启动=测试隔离）；后台回测线程池（backtest-run/framework-backtest-run）；进程由桌面壳 spawn/服务总闸手拉 |
| 真源与注册表 | 头注 INVARIANTS：只读服务+4 获准写端点（backtest-run/framework-backtest-run/services-control/promotion-decide）+1 诚实拒执行（schedulegate-confirm 恒 ok:false 待 C9 批文）；CH 双超时防线（socket 15s+服务端 12s）+`_ch_exec` 全局锁 30s 弃连重建 |
| 门禁与质量尺 | 非法输入 fail-closed ok:false；**契约机检缺位维持**（05 取证册：路由↔api.js↔调用点三面无任何机器校验；tests/frontend/ 涉 TestClient 仅 5 件且非全路由契约） |
| 当前运行状态 | **绿（代码级）**：本日纯导入实测 /api 路由记录 **49 条（GET 44+POST 5）/唯一路径 47**；前端消费侧三红点全清（06 卷 §三）；黄点=契约测试缺位/连接池化/QMT 盘符 |

## 二、子模块三级枚举（8890 API 面路由清单——本日 import 实测 47 唯一路径全列）

1. **健康与行情**：/api/health、/api/kline、/api/stock-header、/api/quote、/api/stock-search、/api/orderbook、/api/position（QMT 桥）、/api/events。
2. **策略与回测**：/api/strategies、/api/battle-map-flow、/api/backtest-list、/api/backtest-detail、GET+POST /api/backtest-run、/api/framework-plans、GET+POST /api/framework-backtest-run。
3. **信号与作战**：/api/signals、/api/signals-overview。
4. **运维三监**：/api/services-status、POST /api/services-control、/api/sources-status、/api/download-status、/api/data-asset、/api/bridge-status。
5. **三图一链**：/api/tdm、/api/tdm/validation、/api/tdm/verdicts、/api/factory、/api/factory/ledger、/api/factory/threehigh、/api/govm。
6. **链图族**：/api/chainmap-galaxy/-cluster/-node/-search/-company/-catalyst、/api/chain-impact-stream。
7. **图形库**：/api/pattern-events、/api/pattern-winrate、/api/pattern-evidence。
8. **审批与通知**：/api/promotion-advisories、POST /api/promotion-decide（Owner 门位数字化，执行器缺位 503）、/api/ops-notifications（通知唯一前端出口）。
9. **AI 层接线批**：/api/budget-advisories、/api/schedulegate-queue、/api/schedulegate-skeletons、POST /api/schedulegate-confirm（诚实拒执行）。
（写端点 5 POST=4 获准+1 拒执行；后台执行链=:873/:1009 线程。）

## 三、接线四态独立复核

- **路由→页面族：已接线**（40 方法+直连族；悬空调用=0，05 册机扫口径维持；budget/schedulegate 消费侧本日实证通）。
- **路由→契约测试：未接线**——49 记录零全路由契约件；05 册 §五 活体案例链（schedulegate 修 2/4 无人知）为无机检代价实证，今两残留虽经后续批次修复，但"修完即验收"的闸仍不存在。
- **CH 通道：半接线（单连接瓶颈）**——全局锁串行+30s 限时+弃连重建；连接池化跨 DatabaseService 域待裁（02 册 §四-2 口径维持）。
- **schedulegate-confirm：诚实拒执行（设计态停用）**——不做假持久化，C9 批文前恒 ok:false。

### 骨架勘误
1. **路由计数口径**：M6 02 册"GET 44+POST 5=47 条 route，47 unique path"算术不成立——本日实测 **49 条路由记录、47 唯一路径**（backtest-run/framework-backtest-run 两路径 GET+POST 双登记）；"47"作为唯一路径口径成立，作为路由记录数少 2。引用建议："49 记录/47 路径"。
2. QMT 桥路径 :115-116→本日 :126（已常量化 `_QMT_BRIDGE_STOCK_DIR`），盘符硬编码病灶仍在——行号漂移+部分修复录勘误。
3. api.js 方法数 43（09-25）→40（本日）：方法面收敛，机检缺位下无变更留痕，佐证缺口#1。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 全路由契约测试缺位 | FastAPI TestClient 契约件（先 5 写端点+高频读端点；tmp_path 隔离） | P1 |
| 2 | 单 CH 连接串行瓶颈 | 连接池化（跨 DatabaseService 域，待裁） | P1 |
| 3 | QMT 盘符硬编码+retire 时间炸弹 | 路径入 shared.io.paths；retire 语义后端出字段 | P2 |
| 4 | schedulegate-queue 每请求全量打分 | 仿 _BMF_CACHE 加 30-60s TTL（0.2 天） | P2 |
| 5 | tdm/govm/factory 直连在机检视野外 | R4 门白名单或 AST 级机检（05 册 §七待裁） | P2 |

## 五、自审闸三态

**挖干（47 路径全列+49/47 双口径实测+写端点授权链+三 daemon 防线+前端消费侧复跑）✅；待裁（连接池化跨域取舍；retire 日语义）；待挖（端点运行态压测=需起服，移交施工批）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "
import sys,types;sys.modules['pytest']=types.SimpleNamespace()
import zephyr.frontend.dashboard.api_server as m
rs=[r for r in m.app.routes if getattr(r,'path','').startswith('/api')]
print('records=',len(rs),'unique_paths=',len({r.path for r in rs}))
from collections import Counter;print(Counter(','.join(sorted(r.methods)) for r in rs))"
grep -n "fetchSchedulegateQueue" src/zephyr/frontend/dashboard/web/services/api.js | head -1
grep -n "_QMT_BRIDGE_STOCK_DIR" src/zephyr/frontend/dashboard/api_server.py | head -1
sed -n '8,10p' src/zephyr/frontend/dashboard/api_server.py   # 写端点授权头注
```
