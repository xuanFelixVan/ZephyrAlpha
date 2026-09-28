---
ttl: task_bound
title: L11 案卷 F114 — 通知路由（协议核心+实现件库级齐；头注自认 tests-only 零装配；与撤通道裁定冲突——built 须降）
session: zc-l11-20260927
---

# F114 通知路由（L 段 F4，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 设计面=F81 告警/事件分发（alert 族→路由→前端）；实现面=协议核心纯内存（notification_router.py [DEPENDENCIES] "无（通道发送器/时钟全注入）"） |
| 下游消费 | **生产消费方=0**：本件头注自认"[CONSUMERS] 无装配消费方（tests-only：tests/frontend/test_notification_router.py）"（notification_router.py:6 本日实读）+本日全仓普查复核（src/scripts/tools 零 import，feishu_bot_sender 为被其引用方向非消费方）；实际到达前端的唯一通知通道=api_server /api/ops-notifications→promotion 页横幅（M6 02 册 :4414/:4423 锚，09-15 裁定） |
| 自动化触发 | 零；OpsAlertFeed（api_server 内 daemon）才是在跑的告警投喂链，不经本件 |
| 真源与注册表 | BLUEPRINT=MOD-FE-004（notification_router.py:1）；域册 docs/03_modules/_domain_frontend/{notification_router,feishu_bot_sender,wechat_bot_handler}/ 三卡（本日 ls） |
| 门禁与质量尺 | 协议核心纯内存+注入式设计（密钥仅 secrets 引用不落地——头注）；无专项门 |
| 当前运行状态 | **接线红**：协议核心+实现件库级齐（有码有测试），生产装配零，且"告警/事件分发到前端"的实际职责已由 OpsAlertFeed+ops-notifications 路由另行承载 |

## 二、子模块三级枚举（src/zephyr/frontend/ 通知面实扫）

1. **协议核心**：notification_router.py（路由/分级/注入式通道；MOD-FE-004；tests-only）。
2. **implementations/ 5 实件+init（本日 ls 全读）**：default_notification_manager.py、default_approval_gateway.py、notification_channel_senders.py、feishu_bot_sender.py（唯一反向引用 notification_router 的实件）、wechat_bot_handler.py。
3. **服务面**：services/dashboard_feeds.py（站内数据订阅；frontend_api_proxy.py:26 头注声明"与本件零交集"；唯一生产消费=warroom.py:490 惰性 import query_correlation_netting——旧 Panel 弃用链内）。
4. **在跑替代链**：api_server ops-alert-feed daemon（5s 首跳+30s tick）→ /api/ops-notifications → promotion 页横幅（09-15 裁定：飞书/SMTP 通知通道裁撤，前端=唯一出口）。
5. **接口层**：interface_base.py（协议基类；implementations 双 default 件+reporting/alert_aggregator 实现其接口——库级装配在、生产终端缺）。

## 三、接线四态独立复核

- **notification_router：未接线**——头注自认+普查复核双证；"告警/事件分发到前端"职责实由替代链承载。
- **feishu/wechat 通道发送器：停用态**——2026-09-15 裁定飞书/SMTP 通道裁撤（ops_alert_feed.py:16 锚；M6 02 册在案），两 sender 实件仍在包=与裁定未对齐的遗留实件（同 F115 R4 分发语义悬置同源）。
- **OpsAlertFeed 替代链：已接线**（daemon 在跑+/api/ops-notifications 在 47 路由面+promotion 页消费）。
- **dashboard_feeds：半接线**——生产消费仅 warroom（弃用链内）；新 web/ 链零消费。

### 骨架勘误
1. **总册 F114"built"降级主张**：环节语义"告警/事件分发到前端"在产线上由 OpsAlertFeed+/api/ops-notifications 兜住（该半边绿），但登记锚 notification_router 本身 tests-only 零装配——按四要素③应为 **partial**（建成后未接线=黄），且锚点错位：真源锚应补记 api_server ops-alert-feed 链。P2 维持。骨架勘误必录。
2. 头注"密钥仅 secrets 引用"与 RULE-SECRETS 对齐良好，无勘误；实现件与撤通道裁定的冲突登记为缺口（不自裁）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | notification_router 装配 or 退役二选一 | Owner/总筹裁：接 OpsAlertFeed→router 装配出分级分发，或随净删窗退役（与 F115 R4 分发语义裁定同窗） | P2 |
| 2 | feishu/wechat sender 实件与 09-15 撤通道裁定未对齐 | 停用标注或随净删；禁新增外发通道消费 | P2 |
| 3 | dashboard_feeds 消费面困于弃用链 | 随 app_panel 净删门同窗裁定（warroom 骨架保留参考价值） | P2 |

## 五、自审闸三态

**挖干（头注实读+implementations 5 件 ls+全仓普查+替代链锚）✅；待裁（缺口#1/2 装配 vs 退役=涉撤通道裁定口径对齐，Owner/总筹）；待挖（无——件少面窄已穷举）。**

## 六、复跑命令

```bash
sed -n '1,8p' src/zephyr/frontend/notification_router.py   # [CONSUMERS] 无装配消费方（tests-only）
ls src/zephyr/frontend/implementations/
grep -n "ops-notifications" src/zephyr/frontend/dashboard/api_server.py | head -2   # 替代链在跑
grep -rn "飞书\|SMTP" src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py | head -2
grep -n "dashboard_feeds" src/zephyr/frontend/dashboard/components/warroom.py | head -2
```
