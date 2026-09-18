---
ttl: task_bound
completes_when: Owner 对 flags.alerts.auto_escalation 作出翻或不翻的裁定并留痕
---

# 《翻转前置条件单》—— `config/flags.yaml` §flags.alerts.auto_escalation（T4 交付）

出单方：车道 `st-ff-alarm-20260918`（告警外发通道车道）· 2026-09-18
读单方：Owner / Max。**flag 本体本车道未动**（`config/flags.yaml` 翻转属 Owner 门位，R-022③）。

## 0. 一句话结论

**今天把 `auto_escalation` 从 false 翻成 true，系统行为零变化** —— 因为在本批之前它在**全仓没有任何读者**；
本批已建唯一读者 `zephyr.data.alert_webhook_dispatch.read_auto_escalation_flag`，
所以现在翻 = 开启"未送达告警积压随下一次事件一并外推 + 打 `escalated` 标记"这一条真行为。

**证据**：`grep -rn "auto_escalation" --include=*.py --include=*.yaml src scripts config`
→ 接管前只命中 `config/flags.yaml:60`（定义处），零使用处。
**根因（结构性，非个案）**：`src/zephyr/shared/foundation/flags.py:345-360` 的
`load_flags_from_yaml` 对每个顶层键**只读 `enabled`** 并注册成 FeatureFlag，
嵌套子键（`auto_escalation` / `strict_mode` / `dlq_enabled` / `retention_days`）**根本不进注册表** →
`global_flag_registry.is_enabled("alerts.auto_escalation")` 会抛 `FlagNotFoundError`。
→ 同一把病同时解释 BRK-052 / BRK-054 的"flag 在册但行为不变"。这是 R-021「只写不读」在
**配置层**的形态，建议 Max 考虑升为通用门禁判据（"YAML 里声明的开关，全仓是否存在读方"）。

## 1. 翻转前置条件（逐条：条件 / 怎么验 / 不满足会怎样）

| # | 前置条件 | 验收命令（跑完看什么） | 不满足时的后果 |
|---|---|---|---|
| P1 | **至少一条真实外部接收端点已配** | `PYTHONPATH=src python -m zephyr.data.alert_webhook_dispatch --health` → 期望 `status="available"` 且 `endpoints` 非空；现为 `status="blocked"` | 升级逻辑虽开但每次派发都走 blocked 分支：升级标记无处可去，只是把同一批"不可用"更频繁地投到通知板（噪音） |
| P2 | **凭据已进 secrets 注册表**（四类凭据属 Owner，见 BRK-055） | `config/alert_webhook.yaml` 端点条目的 `secret_key` 所指键在 `zephyr.shared.security.secrets` 可取到非空值；取不到 → 该端点**拒发**（fail-closed，已在 `_headers` 测钉） | 声明了 `secret_key` 却取不到值 = 该端点每轮失败 → 通知板每轮 critical（正确行为，但等于没通道） |
| P3 | **本地回环双验证已过**（不得直接拿公网端点首发） | 见 `ledger_sixway.md` §3-C2（17 passed，含"桩真收到 payload + trail/state 真落盘"） | 未验通道就接公网 = 把凭据发给一个从未收到过东西的接收方，故障时无法区分"没发"与"没收" |
| P4 | **接收方真的在读**（BRK-005 教训：写了没人看 = 假通道） | 在 Owner 侧对收到的 webhook 做一次**回执确认**（例如手机收到后回一条），并核对 `trail` 的 `status=200` 与接收方时间戳一致 | 只验 200 不验"人看到了"= 200 可能来自一个把 body 丢进 /dev/null 的网关 |
| P5 | **升级不会造成风暴**（去重仍按端点×指纹生效） | `python -m pytest tests/data/test_alert_webhook_dispatch.py -q -k "per_endpoint or escalation"` → 3 passed；其中 `test_escalation_off_skips_backlog_on_resends_it` 钉住"false 跳过积压 / true 带积压重发"两态 | 若把去重破坏，升级=每个事件重发全部历史 CRITICAL（实测历史 990 条）→ 接收端被封 + 告警失去信号价值 |
| P6 | **Owner 知情"升级只影响外发面，不影响交易面"** | 读 `alert_webhook_dispatch.py` [INVARIANTS]：本件只读 `data/failures/`，**永不写生产表、不触 KillSwitch、不拦单** | 若误以为它是保命闸的一部分，可能与 `emergency_track_guardian` 的盘内自动拉闸（R-022③ 已冻结待裁）混淆 |

## 2. 翻转与回滚

- **翻**：`config/flags.yaml` §flags.alerts `auto_escalation: true`（改前 `python scripts/lock_files.py acquire config/flags.yaml <sid>`；
  热文件用 `safe_write_text` + 文本口径 CAS；本文件属宪法 §5 high 域"flag 出厂翻转"→ **须 Owner 签**）。
- **验翻生效**（两分钟）：`PYTHONPATH=src python -m zephyr.data.alert_webhook_dispatch --health`
  → `auto_escalation` 字段应从 `"false"` 变 `"true"`；再制造一条 CRITICAL 失败，
  看 `trail` 里 `"escalated": true` 是否出现。
- **回滚**：把该行改回 `false` 即可，**无状态迁移**——升级面只改变 payload 组装与是否带积压，
  `delivered_keys` 语义不变；已发出的告警不撤回。回滚后 `--health` 的 `auto_escalation` 应回到 `"false"`。
- **误翻的代价**：最坏=接收端被重复推送淹（有 P5 的去重钉兜底）+ 通知板多几条 critical。
  **不会**导致下单/撤单/熔断行为变化（本件不接交易面，见 P6）。

## 3. 本车道已做/未做（避免 Owner 误判工作量）

- 已做：唯一读者 + 两态行为 + 3 条测试钉；`channel_health()` 机读面；通知板投影；变异能红证据。
- **未做（不属本车道或属门位）**：`archive`（BRK-053）/ `dlq_enabled`（BRK-054）施工 → 归 z-failopen；
  Multi-Window 告警规则实现 → 归 z-wire-safety（规则族）；实盘/生产流转、凭据提供 → Owner。
