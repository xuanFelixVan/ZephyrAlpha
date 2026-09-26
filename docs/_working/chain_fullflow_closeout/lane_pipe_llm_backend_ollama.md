---
ttl: task_bound
---

# lane_pipe · llm_backend_ollama（本地大模型推理后端 → LSG 下游链）— 判定：不通 ❌

## 六向台账

### 1 做什么
`ollama serve` 提供本地 LLM/嵌入/重排算力，`OllamaServe` 计划任务开机拉起；LSG 网关把系统内所有 LLM 调用路由到该后端（宪法 §7、§9.2），下游含夜间情绪打分、AI 清洗/感知/调度/比价、嵌入路由。

### 2 依据
- 计划任务在册：`ZephyrAlpha_OllamaServe` → `C:\...\Ollama\ollama.exe serve`，State=Ready，LastRun=2026-09-25 01:51:28，**NextRunTime 为空**（boot/手工触发型，无常备再拉起）。
- 网关在册：`zephyr.security.llm_defense.llm_security.gateway`（所有 LLM 必经）。
- 卡面在册：`data/capability_cards/ollama_chat.yaml`、`embedding_router.yaml`、`reranker.yaml`、`local_model_scheduler.yaml`、`ai_perceive_l1/ai_intake_l2/…`。
- 连带链：#55 NightlySentiment（新闻情绪打分）依赖之。

### 3 改动点（本轮不改，运维/门位面）
- 后端进程缺失：实测 `11434` 端口**未监听**、无 `ollama` 进程 → 所有 LLM 腿取不到算力。
- 缺"后端存活→业务尺"联动：探针/告警未把 Ollama down 归到情绪/AI 链失败（与 news_sentiment_score 冻结互为表里）。

### 4 判据
`11434` LISTEN + 一次 LSG 健康回环成功 + 下游情绪打分恢复推进。

### 5 读数（实测·只读）
- `Get-NetTCPConnection -LocalPort 11434 -State Listen` → **空**（未监听）。
- `Get-CimInstance Win32_Process` 过滤 `ollama` → **无**。
- 兄弟：RSSHub(`node …/RSSHub/dist/index.mjs`) 经 pm2 **在跑**（新闻采集上游未受此灾），但打分链的 LLM 依赖断。
- 佐证冻结：`c1_market.news_sentiment_score` max=2025-09-09（见对应 lane）。

### 6 风险
- "全部能运行"直接受阻：AI/情绪/嵌入三簇链在此单点卡死；开机未命中 boot 触发即长期空窗（NextRun 为空）。

## 自审三态
- **PASS**：端口/进程/计划任务三态独立只读核实；下游冻结证据交叉。
- **FAIL（未做）**：未主动拉起 `ollama serve`（属启停生产进程，越"禁重启/只读"红线）。
- **待裁**：是否把 Ollama 纳入常备守护（加自动再拉起 + 存活入业务尺）涉及常驻守护拓扑与 flag，交 owner 车道，不臆造裁定。

## 处方与复现命令（全部只读）
```
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue | Select LocalPort,OwningProcess"
powershell -NoProfile -Command "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'ollama' } | Select CommandLine"
powershell -NoProfile -Command "(Get-ScheduledTask ZephyrAlpha_OllamaServe|Get-ScheduledTaskInfo).LastRunTime; (Get-ScheduledTask ZephyrAlpha_OllamaServe|Get-ScheduledTaskInfo).NextRunTime"
```
处方（待授权）：① 给 Ollama 加"死即再拉起"守护或改常备计划任务（触发器从 boot-only 改为周期自检）；② LSG 调用失败计入 AI 链健康尺并对情绪链告警；拉起动作需 Owner/运维在正式通道执行。
