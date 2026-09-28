---
ttl: task_bound
title: L09 案卷 F89 — 本地模型与嵌入（ollama/嵌入路由/24-7 排程/reranker 四卡面）
session: zc-l09-20260927
---

# F89 本地模型与嵌入（J 段 A4，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 模型源=Ollama 本地推理（ollama_chat 卡：qwen3:8b via /api/chat，6 work types，本日卡头实读）；模型源线归 F95 OBJ_M 设计面 |
| 下游消费 | F86 全族（cleaning washer 等潜在调用方）；F16 车道 B AI 生成；治理面 LSG 拦截（ollama 客户端不在四库 patch 白名单——收口册01 DP-6 点名） |
| 自动化触发 | local_model_scheduler 卡=24/7 排程声明；M5 实测 OllamaServe/RSSHub 为 09-20 一次性拉起**无常驻守护**（05 册 #22 黄）；11434 恢复=仅凭 Owner 显令（wiring_gap §2.3-4，重启提案已封矿勿重提） |
| 真源与注册表 | 四卡全实存：`data/capability_cards/{ollama_chat,embedding_router,local_model_scheduler,reranker}.yaml`；治理锚定 MOD-INF-035（卡头 blueprint 锚实读） |
| 门禁与质量尺 | 调用须经 LSG（F88）；裸 ollama 客户端调用不在运行时 patch 面，仅 GATE-20 静态兜底 |
| 当前运行状态 | **黄**：卡面 built（四卡齐）；服务面无常驻守护+11434 端口状态待 Owner 显令——"built"应读作"卡与排程声明建成，服务体維持性未闭环" |

## 二、子模块三级枚举（四卡逐张）

1. `ollama_chat.yaml`：capability_id=ollama-chat，category=inference，qwen3:8b 本地推理，6 工作类型（卡头 description 实读）。
2. `embedding_router.yaml`：嵌入路由卡（按任务路由嵌入模型）。
3. `local_model_scheduler.yaml`：24/7 本地模型排程卡（骨架"24/7 排程"真源）。
4. `reranker.yaml`：重排卡。
5. 服务侧宿主：OllamaServe 进程（M5：09-20 拉起、无 guard、无 keep-list 证据）——包面无 src 侧 scheduler 实体模块指向（排程逻辑在消费侧/卡声明，本卷如实登记）。

## 三、接线四态独立复核

- **卡面=已接线**：四卡在 data/capability_cards/，capability_lookup 可反查（F91 面消费）。
- **服务面=半接线**：ollama 服务无守护、无探活任务、端口恢复归 Owner 显令——24/7 声明与无常驻守护矛盾（声明≠值守）。
- **调用面=未通水证据**：F86 cleaning_spec 0 行+F16 车道 B partial ⇒ 本地推理生产流量零实证；仓内 ollama 客户端调用若存在则游离于运行时拦截面外（DP-6）。
- **无悬空卡**：四卡均有治理锚定头。

## 骨架勘误

1. 骨架"built"偏乐观：**built 实体=四张能力卡+排程声明；服务维系（守护/探活/端口）与生产流量均为空**——按总册四要素"自动化"判应为黄（建成后未接线=黄）。
2. 新增交叉：ollama 客户端在 LSG DP-6 patch 白名单外（收口册01 点名），F89 与 F88 存在防线协同缺口（当前仓内零此类调用=静态网兜底，扩用时须同步扩面）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | Ollama 无常驻守护、11434 停机待裁 | Owner 显令恢复+决定是否入 guard 族（禁本车道擅动） | P1 |
| 2 | 24/7 排程声明 vs 无值守矛盾 | 排程宿主落位（guard/计划任务）或卡面降格声明 | P2 |
| 3 | 本地推理生产流量零实证 | 随 F86 进化循环点火自然验证 | P2 |

## 五、自审闸三态

**挖干（四卡实读+服务态双源 M5/本日）✅；待裁（缺口#1 全归 Owner，本卷禁动）；待挖（嵌入路由/reranker 的调用方明细——登记 M4 后续面）。**

## 六、复跑命令

```bash
head -14 data/capability_cards/ollama_chat.yaml
ls data/capability_cards/ | grep -E "ollama|embedding|local_model|reranker"
powershell -NoProfile -Command "Get-Process ollama -ErrorAction SilentlyContinue | Select Id,ProcessName"
```
