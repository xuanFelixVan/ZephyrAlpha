---
ttl: task_bound
created: 2026-10-09
owner: st-chiefc-20261009（A13 车道，总统筹第四号增补令②监视面）
completes_when: "Owner 对复发证据裁定是否立 A-12 后续刀（盘面投影守门）后归档"
token: a13-recurrence-watch-20261009
---

# A-12 复发监视读数（f6b92806c4 落地后 · 09:00 后窗口）

## 判定：**非 0 发作——盘面投影面复发，按处方"有→登记复发证据并停（呈报重修）"**

监视方法：`git log --since="2026-10-09 09:00" --grep="抹|蒸发|回灌"` + dead/ 死因扫描
+ `.runtime/audit/` 痕迹。窗口内命中 2 条蒸发/回灌痕迹：

| 时刻（+0800） | 证据 | 读数 |
|---|---|---|
| 13:09 | commit `45a76ba1a7`（REQUEUE 留痕 v2） | "0083 死因=CREATE-GUARD 读主区盘面 registry 被陈旧快照**再抹**（**HEAD 64726 行有 token 而盘面 0**）；已自 HEAD **回灌**盘面（token 在）后立即重排" |
| 13:32 | commit `dbfb6e4cfc`（D-TOK token 先行袋） | "**陈旧整档快照缺失 HEAD 行**增量回插 1 条（n5-sector-agg-test-20260918，st-tdchain 原条目原样回插）" |

下游连坐（同一窗口）：st-chiefc-20261009 C-4/C-5 两袋（dead/ q-0120/0121，died_at
14:06/14:10）死于 allow_overlap 熔断——重试配额被上述蒸发战烧光（他伤豁免已由 A13①
落地，commit 见本车道交付袋）。

## 复发定性（呈报 Owner 复修的关键读数）

- **HEAD 真源面：未失守**。A-12 治本（f6b92806c4 07:35，落地侧快进守门+直提侧 token
  只增不减）有效——两次事件中 HEAD 册面均完整（token 在、64726 行），丢失只发生在
  **主区盘面投影**；且死因由 CREATE-GUARD 门禁显式拦截（死信可归因），非静默丢失。
- **盘面投影面：仍在发作**。别道陈旧快照直写压盘的行为未被现有门覆盖（门禁只在
  commit/落地时读盘，不拦盘上直写）；每次发作都以"死袋+人工自 HEAD 回灌"收场，
  恢复动作靠人肉不靠系统（违背永久系统四要素"自动维护"）。
- **复修方向（建议下一刀）**：deadcure 台账 08 号处方 B——CREATE-GUARD/同族门禁的
  token 读取源改 PG 意图账本（REG-CAPCAN-001 双轨在册），盘投影滞后/回退不再影响判定；
  或等价物：热册盘面写前读新守门（safe_write_text CAS 强制面）。

## 监视窗声明

本读数覆盖 2026-10-09 09:00 至 14:30（本车道落笔时点）。此前窗口发作（04:35/06:29/
06:33-06:47 三次+09:41 c3d37dee53 记录的第三次压回）已在
`docs/_working/deadcure_campaign/08_hot_registry_eviction_evidence.md` 台账在案，不计入
本监视窗。

## 追记（14:40-14:47 实时发作·蒸发者已验明正身）

本车道登记 token 时被 batch_creation_tokens 写前自检拦下（缺 HEAD 54 条，fail-safe
未落盘）；按手册增量补回（HEAD 基重放，lost_from_HEAD=0/lost_from_disk=0 断言）后
**约 1 分钟内盘面即被再次压回陈旧快照**。safe_write 审计 sha 时间线（778cddf9=陈旧版/
39090ba2=恢复版）：14:01/14:32/14:40(+08) 多次 39090ba2→778cddf9 反转写。

**蒸发者=pid 2040 `python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon`
（队列落地守护进程本体）**，safe_write 留痕 `registry_mass_edit_allowed: true`、
`session: ""`。即：落地侧机械在把某袋携带的陈旧整档注册表写回主区盘面——HEAD 真源
面因 A-12 直提守门无恙（64612+ 行/token 在），但盘面投影被落地侧机械自身周期性污染。
复修焦点从"别道会话陈旧快照直写"收敛为"**belt daemon 落地写盘路径的基底陈旧**"——
A-12 三方合并守门未覆盖该写入面（或其基底选择有洞）。呈报重修优先级应提升：该机制
在持续制造死袋（q-0083 型 CREATE-GUARD 死因）并消耗全车道熔断配额。
