---
ttl: task_bound
completes_when: 总包对本单四项作出裁定并回写待裁表
---

# 车道申请书 req_alarm_01（st-ff-alarm-20260918 · 告警外发通道）

按 `COORDINATION_LEDGER.md` §4：车道不自取裁定号，只交申请书 + 回写待裁表，然后继续施工（未停等）。

## A1 · 已停车道遗留 untracked 成件代码的归属与"假消费者声明"（R-021 新实例）

- **背景**：接管 FF-16 外发通道时实测发现 `src/zephyr/data/alert_webhook_dispatch.py` +
  `config/alert_webhook.yaml` **已在盘但 untracked**，其头注释 `[CONSUMERS]` 声称
  "zephyr.strategy_pipeline.pipeline_events(maybe_dispatch_alerts 唤醒钩子)"。
- **实测**：`grep -rn "maybe_dispatch_alerts\|alert_webhook_dispatch" --include=*.py src tests scripts`
  → **0 命中**（模块自身除外）。`pipeline_events.py` 从未 import 它。且 `tests/data/test_alert_webhook_dispatch.py`
  （[TESTS] 所指）不存在 → **零测试**。
- **选项**：甲=本车道接管并补齐（已选，理由：任务书 T1 即此件，另建=造 R-015 式"六套并存"）；
  乙=判为无主件由总包另行指派。
- **建议**：确认甲，并把 **"头注释 [CONSUMERS] 声称的消费方与实测 import 面不符"** 升为门禁判据
  （现 ORPHAN-MODULE 只查"零入度"，查不出"声称有消费方其实没有"）。
- **影响面**：`alert_webhook_dispatch.py`（已改）；判据若立则全仓 4000+ 件带 [CONSUMERS] 的 .py 受益。

## A2 · `flags.yaml` 嵌套子键结构性不可读（BRK-052/054 共同根因）

- **背景**：普查把 `auto_escalation: false` / `strict_mode: false` / `dlq_enabled: false` 记成"功能未开"。
- **实测**：`src/zephyr/shared/foundation/flags.py:345-360` 的 `load_flags_from_yaml` 对每个顶层键
  **只取 `spec["enabled"]`** 注册 FeatureFlag；嵌套子键不进注册表 → 翻它们**零效果**（翻转前全仓零读者）。
- **选项**：甲=每处消费方各自直读 YAML（本车道已为 `alerts.auto_escalation` 这么做，代价=多读者口径分散）；
  乙=给 `FlagRegistry` 加嵌套键支持（治本，但改的是全仓共用件，风险面=所有 flag 读方）；
  丙=把"嵌套子键"从 flags.yaml 迁出为各自配置册（SSOT 方向最干净，动的是文件结构）。
- **建议**：本轮维持甲（局部、可测、不碰共用件）；请 Max 裁乙/丙是否立项。
- **影响面**：`config/flags.yaml` 全部嵌套子键（含 z-failopen 的 `schema_validation.*`、archive 的
  `retention_days/compression`）。**提醒 z-failopen**：只翻 flag 不建读方 = 造第二个假通道。

## A3 · risk 侧触发点需求（登记需求，未改文件）

- **背景**：任务书要求"机器侧告警在危机判定 breach 时真能出声"。现出口已挂在
  `Alerter._write_failure_file`（CRITICAL）与 kill_switch 探针两条腿上。
- **需求**：`src/zephyr/risk/**`（z-land2 独占）若在危机闸/对冲腿触发处希望外发，
  **只需调 `zephyr.data.alerter.Alerter.notify(..., level=LEVEL_CRITICAL)`**，无需直连本通道；
  若需"绕过 alerter 直发"，请提出，本车道再开显式 seam（禁自行 import 派发器，防多入口漂移）。
- **建议**：总包把"CRITICAL 一律经 Alerter.notify 出声"写进战役惯例（与 OpsAlertFeed 的
  "唯一出口"纪律同族）。

## A4 · 通知板可见性副作用（请 Owner 确认是否接受）

- **实测**：fail-closed 投影使 `.runtime/ops_notifications/notifications.jsonl` 出现
  `key=alert-webhook/channel-unavailable, severity=critical, title=告警外发通道不可用（fail-closed）`
  → promotion 页会挂红条，直到 Owner 提供凭据并配端点。
- **选项**：甲=保留（"通道没通"就该天天看见，这是 R-021 的正解）；乙=降为 warning；丙=首次挂条、后续静默窗口拉长。
- **建议**：甲。当前 `OpsAlertFeed.publish` 已自带 300s 静默窗（同 key 不重复堆条目），噪音可控。

## A5 · 交工连带面如实登记

- 本批 `src/zephyr/data/alerter.py` 提交**吸收**了他车道（z-failopen）已 staged 的 7 行
  BRK-049 兜底日志改动（非本车道产物，按 §2.5 核归属后如实登记，不代修不回退）。
- `capability_canonical_file_registry.yaml` / `module_translation_registry.yaml` 为热文件，
  本批同样带入了他会话已 staged 的 token 条目（60 + 40 行），属正常吸收（§3 协议第 1 条）。
