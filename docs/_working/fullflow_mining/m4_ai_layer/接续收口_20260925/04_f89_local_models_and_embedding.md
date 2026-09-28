---
created: 2026-09-28
ttl: task_bound
volume: 04_f89_local_models_and_embedding
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-f89-localmodel-book-20260926
---

# 04 · F89 本地模型与嵌入（ollama + embedding_router + local_model_scheduler + reranker）

> 车道 W4-B｜worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`｜零提交零入队｜只读取证。
> 派单=`00_skeleton/92_coverage_triage_20260926.md` §三（F89 判"真缺簿·缺上游/下游/门禁向"）。
> 本册状态：**六向齐证**（分诊册点名的三缺向已在 §二 逐向给 file:line），§一 挂 F89 认领锚。
> 对分诊册的一处更正：其 §一 F89 行称"四张 capability_card 是消费画像，未连到 router/reranker 调度码路径"——实测**卡与码同 module_id（MOD-INF-035）且卡即码的机读画像**，缺的是**ROOR 未登记能力卡面**（病灶 1），不是"卡码脱节"。

## 一、环节定义与边界

总册口径（`00_skeleton/00_全环节总册.md:159`）：F89 本地模型与嵌入｜ollama+嵌入路由+24/7 排程+reranker｜上游"F89 模型源"（自指，笔误）｜下游 F86/F16｜真源=`data/capability_cards/{ollama_chat,embedding_router,local_model_scheduler,reranker}.yaml`｜总册标 built、P1、A4（J 段 AI 层）。

本册覆盖 F89
> 实证面=真源代码包 `src/zephyr/integration/local_model/`（8 件）＋ `src/zephyr/intelligence/model_evaluation/reranker.py`＋四张 capability_card＋三处外部消费。

**总册真源列判不全**：总册只列了四张卡（画像面），未列**代码真源**。卡自述 module_id=MOD-INF-035（四卡一致），代码落点=本册 §三。回写建议见 §六末。

边界：`intelligence/model_routing/`（cascade_orchestrator/runtime_assembly，云侧级联路由）与 `infrastructure/pipeline/model_router.py`（管线级路由）**异对象不并**；`integration/vector_memory/`（向量记忆）只作下游消费与内收证据。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | ①**进程内上游=`pipeline_orchestrator`**：`src/zephyr/integration/pipeline_orchestrator.py:4` [DEPENDENCIES] 一字列全 `zephyr.integration.local_model.local_model_scheduler` / `.embedding_router` / `zephyr.intelligence.model_evaluation.reranker`（三件同一消费方）；`:96/:177` 条件 import，`:429-430 self._local_scheduler = LocalModelScheduler() if _LOCAL_SCHEDULER_AVAILABLE else None`；②**模型源=ollama 本地服务**：`embedding_router.py:123-124 OLLAMA_BGE_M3_MODEL="BGE-M3:latest"` / `OLLAMA_BGE_SMALL_MODEL="qllama/bge-small-en-v1.5:latest"`，`:365-366` 按 model_key 选模并构 `OllamaEmbedder(model=...)`；③**外部模型服务面**：`ollama_chat.py:563 requests.get(f"{url}/api/tags")` 探模型清单（ollama 侧注册表即上游真源之一）；④任务入口=scheduler `_task_queue`（`:243`） |
| 下游消费 | ①`integration/pipeline_orchestrator.py:813 "LocalModelScheduler started (L2 24/7)"`（L2 层 24/7 消费者）＋ `:1960 from ...reranker import Reranker`；②`autonomy_core/embedding_provider_adapter.py`、`autonomy_core/skills/skill_router.py`（技能路由取嵌入）；③`integration/llm_runtime_gateway.py`（LLM 运行时网关取 ollama_chat）；④`integration/vector_memory/{hybrid_retriever,in_process_vector_memory,collection_manager,cache_layer}.py`（向量检索取嵌入/缓存）；⑤`intelligence/local_llm_pool.py:26`（自述池化"ollama_chat（单模型客户端）、local_model_scheduler（调度循环）"）；⑥`intelligence/model_profiling/{exam_test_cases,exam_trigger_scheduler}.py`（模型考试消费）；⑦运维面注册：`governance/ops_governance/service_registration.py:81 from ...model_evaluation.reranker import Reranker`——reranker 是**被登记为可运维服务**的 |
| 自动化触发 | ①**24/7 排程=进程内后台线程 + 队列 poll**，非计划任务：`local_model_scheduler.py:179 def start()` → `:198 _log.info("LocalModelScheduler: 后台线程已启动 (poll=%ss)", self._poll_interval)`；`:243 task = self._task_queue.get(timeout=self._poll_interval)`；`:126 poll_interval_s: float = POLL_INTERVAL_S`；`:176/:296 time.sleep(...)`（退避）。**由 pipeline_orchestrator 起停**（:813 start / :818 stop），无独立注册名。②**ollama 服务侧=计划任务**：`docs/_working/fullflow_mining/m5_scheduling/01_windows_schedtasks.md:91` 注册名 **`ZephyrAlpha_OllamaServe`（一次性，ollama.exe serve，09-20 / 0 次运行）**；健康表 `05_master_health_table.md:34` 第 22 行"OllamaServe / RSSHub｜端口/进程活（低频件，09-20 拉起后无守护）｜未逐项验证（黄）"。③**考试触发排程**=`model_profiling/exam_trigger_scheduler.py`（在盘，本册不展开）。④宪法符合性存疑点见 §四病灶 3（poll/sleep 循环 vs §9.3"禁 sleep-loop"红线） |
| 真源与注册表 | ①**能力画像真源=四张卡**：`data/capability_cards/{ollama_chat,embedding_router,local_model_scheduler,reranker}.yaml`，四卡同 `module_id: MOD-INF-035`，`capability_id` 分别 `ollama-chat`(:10)/`embedding-router`(:10)/`local-model-scheduler`/`reranker`(:10)；`status: ACTIVE` 四卡齐；`runtime_plane` = hot/hot/hot/**warm**（reranker 冷一档）；scheduler 卡另记 `priority: P0`、`requires_human: false`、`registered_at: '2026-05-08T20:14:39'`、蓝图锚 `MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`。②**ROOR 面＝半查无**：`docs/registry_of_registries.yaml:97-104` 的 **REG-SKILL-001** 指向 `data/capability_cards/`，但口径是"22 个 **skill_\*.yaml**（entry_count: 22）"——实测该目录 44 张 yaml，其中 `skill_` 前缀恰好 22 张、另 22 张为**能力卡**（`^capability_id:` 命中 44）。⇒ 本环节四张卡所在的能力卡面**在 ROOR 无登记条目**（病灶 1）。③代码模块真源锚：`[BLUEPRINT] MOD-INF-011` 指向 vector_memory 蓝图（shim 件），MOD-INF-035 指 auto_runtime_core 蓝图。④模型清单真源=ollama `/api/tags`（进程外） |
| 门禁与质量尺 | ①**LSG 统一闸门（不是装饰，有 fail-closed 契约）**：`src/zephyr/integration/local_model/lsg_gate.py:19` 自述"local_model 包 LSG 统一注入闸门（09号文 §4.2 P0-1）"、`:24`"必经 LSGSecurityGateway 判决，判决记录落 L6 审计——**三通道同一闸门，无旁路**"、`:28`"fail-closed：LSG 不可用或扫描异常 → 抛 `LSGBlockedError`，不发起 API 调用"（`:69` 异常类、`:77-78` 单例 gateway + 锁）。被 `ollama_chat.py:42` 真 import（同包 `:4` [DEPENDENCIES] 亦列 `lsg_gate`）→ **调用链成立**，且 `ollama_chat.py:473` 的 `requests.post` 前即该闸门。②**开关**：`LSG_ENABLED_ENV = "ZEPHYR_LSG_LOCAL_MODEL_ENABLED"`（`lsg_gate.py:64`，`:31` 口径"（'0'/'false'/'off'/'no' 关闭）**> 默认开**"，`:81 resolve_lsg_enabled(override)`）→ 默认开=好，但**关态无审计**（病灶 2）。③**质量尺**：`embedding_router.py:134 verify_model_checksum(model_dir, expected_sha256)`（模型权重 sha256 校验，嵌入面唯一硬尺）。④**注册在 gate_registry？** 实测 grep `local_model\|ollama\|embedding\|lsg` 于 `gate_registry.yaml` **无本环节条目** → LSG 闸门是**运行时闸门**，不进提交门禁（与宪法 §9.2"GATE-20+运行时拦截器双捕"口径一致，GATE-20 属另一面）。 |
| 当前运行状态 | **黄**（三点定黄，全为实测）：①代码与接线在盘（绿，见上游/下游向 file:line）；②**承载模型的服务无守护**：`m5_scheduling/01_windows_schedtasks.md:91` 记 `ZephyrAlpha_OllamaServe` = "一次性 / 09-20 / 0"，`05_master_health_table.md:34` 判"09-20 拉起后无守护、未逐项验证（黄）"→ 一旦 ollama 掉线，embedding/chat 全链路降级而无人重拉（这与 PolarMem 记忆在案的"LLM 腿无人重启"同型）；③**调度器起停只随 pipeline_orchestrator**（:813/:818），无独立健康探针/看门狗登记。可复跑命令见 §七第 2/3/4 条（第 4 条为状态判据的取数命令）。 |

## 三、子模块清单（`ls`＋`grep`＋注册表三源交叉）

**3.1 `src/zephyr/integration/local_model/`（ls 实测 8 件）**

| 件 | 职责（证据） | 交叉源 |
|---|---|---|
| `__init__.py` | 包 re-export | grep 消费方 20+ 命中 |
| `ollama_chat.py` | ollama 单模型聊天客户端；`:473` post 推理、`:563` `/api/tags` 探清单；`:42` 经 lsg_gate | 卡 `ollama_chat.yaml`（MOD-INF-035）＋`local_llm_pool.py:26` |
| `ollama_embedding.py` | `OllamaEmbedder` 嵌入客户端（182 行，**真源**） | 被 `vector_memory/ollama_embedding.py` shim 再导出 |
| `embedding_router.py` | 双模路由（M3 / bge-small，:123-124/:365-385）、`l2_normalize :127`、`verify_model_checksum :134`、`EmbeddingRouterProtocol :64` | 卡 `embedding_router.yaml` |
| `local_model_scheduler.py` | 24/7 FIFO 任务队列＋后台线程＋退避（:126/:176/:179/:198/:243/:296） | 卡 `local_model_scheduler.yaml`（P0/hot） |
| `cache_layer.py` | 嵌入缓存（162 行，真源） | `vector_memory/cache_layer.py` shim |
| `lsg_gate.py` | LSG 统一注入闸门（fail-closed，:64/:69/:77/:81） | 宪法 §9.2 运维红线对应件 |
| `deepseek_chat.py` | 第二模型源（云端/本地混合） | grep 命中同包 import |

**3.2 环外属件（2）**：`src/zephyr/intelligence/model_evaluation/reranker.py`（`Reranker`，卡 `reranker.yaml` warm/ACTIVE，被 `service_registration.py:81` 与 `pipeline_orchestrator.py:1960` 消费）｜`src/zephyr/integration/vector_memory/ollama_embedding.py`＋`cache_layer.py`（各 19 行 **re-export shim**，头注 `[DEPENDENCIES] zephyr.integration.local_model.*`，真源已在本包——**已内收**，非重复件）

**3.3 邻近但不属本册（防混挖）**：`intelligence/model_routing/{cascade_orchestrator,runtime_assembly}.py`｜`infrastructure/pipeline/model_router.py`｜`infrastructure/model_profiler/`｜`intelligence/model_{evaluation,intel,profiling}/`｜`autonomy_core/embedding_provider_adapter.py`

**3.4 交叉结论**：ls 8+2 件＝本环节全量；grep 得消费方 15 处；注册表侧得 4 卡（MOD-INF-035）＋ROOR REG-SKILL-001 一条（口径不含能力卡，病灶 1）。**未证**：`deepseek_chat.py` 的包外消费方、`cache_layer` 命中率。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | **能力卡面在 ROOR 查无**：REG-SKILL-001 只认领 `skill_*.yaml`（22），另 22 张能力卡（含 F89 四卡）无登记条目 | 目录同名混装两类件（技能声明 + 能力画像），ROOR 登记按其中一类写口径 | 在 ROOR 增一条 `REG-CAP-001 capability 卡目录`（口径=非 skill_ 前缀 22 张，maintenance/generator 注明），或把两类件分目录后各登一条（**只出判据，本车道不改 ROOR**——热册） | 0.3 | 否（ROOR 热册，总筹单点写） |
| 2 | LSG 闸门可被 env 关（`ZEPHYR_LSG_LOCAL_MODEL_ENABLED`），关态是否留痕未证；`resolve_lsg_enabled` 三级优先（override>env>默认开） | 宪法 §9.2 明列"禁裸调 LLM"，但**旁路开关本身无审计**＝可静默关掉唯一防线 | 关态 MUST 写 L6 审计一条（含 reason），并加一条"生产窗口 env 不得为关"的自检 | 0.5 | 否（涉 lsg_gate 生产码，本车道不改） |
| 3 | 宪法 §9.3 红线："reconciler MUST 事件触发，禁 cron/**Timer**/**sleep-loop**"，而 scheduler 卡自述 tags 含 `polling`、实现为 `_task_queue.get(timeout=)`＋`time.sleep(0.5)`（:176）＋退避 sleep（:296） | 该件是"任务队列消费者"，语义上属队列阻塞等待（timeout 取队列）而非忙等 sleep-loop，**与违宪的忙等 loop 有实质区别**；但红线文本未区分"队列 timeout"与"sleep 轮询"，判据口径本身有歧义 | 提请裁定：把 §9.3 精化为"禁忙等 sleep 轮询；queue.get(timeout) 型消费合法"（或反向：要求本件改真事件驱动）。**本车道不自行判其违宪，也不为其开脱** | 0.2（裁定） | 否 |
| 4 | ollama 服务面为"一次性计划任务、09-20 拉起、无守护"（`01_windows_schedtasks.md:91`），F89 全链路依赖它 | 模型服务不在 AutoRuntime 心跳/看门狗覆盖内（已知病灶："LLM 腿无人重启"） | 归 m5 调度车道：给 `ZephyrAlpha_OllamaServe` 加存活探测＋事件重拉，或登记为 keep 名单（`data/runtime/process_reaper_keep.txt`，宪法 §0.2） | 1 | 否（跨车道＋生产配置） |
| 5 | `pipeline_orchestrator.py:177-181` 条件导入失败即 `LocalModelScheduler = None`，静默降级为"无 24/7 排程"，仅 :429 判 None | 降级不留 fail 级审计＝"有 L2 排程"的账面可能在生产上从未成立而无人知 | 导入失败 MUST 记一条 WARN＋健康表面板显式展示"local scheduler 缺席" | 0.3 | 否 |
| 6 | 双嵌入件并存易误判为重复：`local_model/ollama_embedding.py`(182) 与 `vector_memory/ollama_embedding.py`(19) | 实为真源+shim，已收敛；但 shim 头注仍标 `MOD-INF-011`（另一 module_id） | 保留 shim；在 depgraph 里把 shim 标 alias（防 `--force` 重建时把真源判外来） | 0.2 | 可（登记） |

## 五、内收与合并机会（四判据）

- **同真源可派生→必并**：四张 capability_card 与代码是同 module_id 的两视图 → 卡应由代码 docstring/签名派生（现为手工，`maintenance: manual`）；ROOR 的卡计数亦应从目录派生（病灶 1）。
- **零触发零消费→退役**：候选=`deepseek_chat.py`（包外消费未证）与 `cache_layer` 未命中面 → 先跑 §七第 5 条反查，零命中者出退役**判据清单**（不删、不改名，注册表净删=Owner 门位）。
- **同域重复簇→收敛唯一**：**已有一例收敛可作样板**（vector_memory 两 shim 指回 local_model 真源）；剩余簇=三处"模型路由"命名（`integration/local_model/embedding_router`、`intelligence/model_routing/cascade_orchestrator`、`infrastructure/pipeline/model_router`）→ 三者对象不同（嵌入模态路由 / 云边级联 / 管线任务路由），按"跨域不同对象→不并"登记，**但 MUST 在总册各占一格**以免再混。
- **跨域不同对象→不并**：reranker（检索重排）与 embedding_router（表征生成）不并；`model_profiling/exam_*`（模型考试）属 F89 下游但自成环节，不并入本册。

## 六、自审闸三态

**判：挖干可施工**——分诊册点名的三缺向（上游/下游/门禁）均已补 file:line 实证；六向每向有实据。

三项**不随本册闭**（若要宣称 F89 = built 还差这些）：
1. ollama 服务存活与自动重拉无实证（病灶 4）——最小观测量：一次 `ZephyrAlpha_OllamaServe` 拉起后的 `/api/tags` 200 响应记录，或看门狗登记条目。
2. LSG 闸门关态审计无实证（病灶 2）——最小观测量：一条 L6 审计记录含 `ZEPHYR_LSG_LOCAL_MODEL_ENABLED` 取值。
3. `local_model_scheduler` 的 24/7 循环是否**真的在生产在跑**——现证据只有代码 + `pipeline_orchestrator.py:813` 的日志语句，未取到一条生产日志。

**待裁**（已写进 `m4_ai_layer/接续收口_20260925/pending_rulings.md`）：病灶 3（§9.3 sleep-loop 口径精化）、病灶 1（ROOR 能力卡登记）、病灶 2（LSG 关态审计）。

**回写总册建议**：`00_全环节总册.md:159` ①真源列补代码路径 `src/zephyr/integration/local_model/`＋`intelligence/model_evaluation/reranker.py`（现只列四卡＝画像面）；②上游列"F89 模型源"改实指（ollama 服务 + pipeline_orchestrator）；③`built` 改 **`partial`**，备注"承载服务无守护、24/7 循环无生产日志实证"。

## 七、复核命令

```bash
# 1) 四卡与代码同 module_id 自证（本册真源向）
grep -n "module_id\|capability_id\|runtime_plane\|status" data/capability_cards/{ollama_chat,embedding_router,local_model_scheduler,reranker}.yaml | grep -v "^.*#"

# 2) 24/7 调度循环实现与起停（黄判据 3）
sed -n '120,135p;170,200p;240,250p;290,300p' src/zephyr/integration/local_model/local_model_scheduler.py
sed -n '175,185p;425,435p;810,820p' src/zephyr/integration/pipeline_orchestrator.py

# 3) LSG 闸门 fail-closed 契约与开关（门禁向）
sed -n '19,35p;60,90p' src/zephyr/integration/local_model/lsg_gate.py
sed -n '40,48p;470,476p' src/zephyr/integration/local_model/ollama_chat.py

# 4) 服务面与守护状态（状态向，取数即判黄）
schtasks /query /tn ZephyrAlpha_OllamaServe /fo LIST /v | grep -i "Task To Run\|Last Run Time\|Status"

# 5) 退役候选反查（deepseek_chat / cache_layer 包外消费）
grep -rn "local_model.deepseek_chat\|local_model.cache_layer\|import cache_layer" --include=*.py src/ scripts/ tests/ | grep -v "^src/zephyr/integration/local_model/"

# 6) ROOR 能力卡查无自证（病灶 1：22 skill vs 44 总数）
sed -n '97,104p' docs/registry_of_registries.yaml
ls data/capability_cards/*.yaml | wc -l ; ls data/capability_cards/ | grep -c "^skill_"

# 7) shim 已内收自证（防误判重复簇）
cat src/zephyr/integration/vector_memory/ollama_embedding.py
```
