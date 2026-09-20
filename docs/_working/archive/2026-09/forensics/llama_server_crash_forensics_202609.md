---
ttl: task_bound
completes_when: >-
  Ollama/llama.cpp 升级落地（崩溃签名族归零复测一轮）或 Owner 裁定接受现状；本报告作为
  M4 治理战役终态凭据由工作文档清理批按 GATE-WORKING-DOCS 语义结案。
---

# llama-server 崩溃族溯源诊断报告（治理战役 M4，2026-09-16）

> 会话：st-govops-20260916 ｜ 数据源：Windows 事件日志 Application Id=1000/1001（拉取窗口 2026-08-27 ~ 2026-09-16）+ ollama list + nvidia-smi + config/gguf_vram_budget.yaml

## 1. 结论（TL;DR）

- 崩溃主体=Ollama 0.32.1 内嵌 `llama-server.exe`（版本号字段 0.0.0.0，PE 时间戳
  0x6a586b5d），路径 `%LOCALAPPDATA%\Programs\Ollama\lib\ollama\`。
- 事件日志共 **8 例**崩溃，收敛为 **3 个签名族**；其中 0xc0000005 访问违例 4 例
  **错误偏移完全相同**（libllama.dll +0x2a230）= 确定性缺陷路径，非随机内存翻转。
- 归因主判：**VRAM/内存超订压力下的 llama.cpp 0.32.1 构建缺陷暴露**。9-15 事故日
  （9 孤儿实例 × 按需 2 模型）恰为崩溃密集日（5/8 例），17:14:09→17:14:27→17:15:49
  呈 18s/82s 间隔崩溃-重启循环形态。
- 可执行防护已落：`auto_runtime_core.ensure_running` 孵化前 VRAM 预算门（>21.6GB 拒孵）+
  M1 孵化登记（ledger 可溯）+ M3 超寿收割。版本升级属 Owner 门位（需安装软件），列待裁。

## 2. 崩溃签名族（事件日志实证）

| 签名族 | 异常码 | 出错模块/偏移 | 例数 | 时间点 |
|--------|--------|---------------|-----:|--------|
| AV-LLAMA | 0xc0000005 访问违例 | libllama.dll +0x2a230 | 4 | 08-27 11:57/15:58，09-15 02:45/17:14 |
| FF-UCRT | 0xc0000409 fail-fast（BEX64 栈缓冲安全检查） | ucrtbase.dll +0xa4ace | 3 | 09-15 17:14 / 23:21 / 23:22 |
| CPP-EXC | 0xe06d7363 C++ 异常（未捕获，KERNELBASE RaiseException） | KERNELBASE.dll +0xc804a | 1 | 09-15 17:15 |

签名特征：
- AV-LLAMA 四例同模块同偏移：同一条确定性野指针/越界路径（0.32.1 内嵌 llama.cpp 构建
  的图计算/张量路径），排除随机硬件故障（后者偏移应离散）。
- FF-UCRT（BEX64）= 运行时 fail-fast：栈越界/堆破坏被 /GS 检出后主动终止，与 AV 族
  同日成对出现——先 AV 破坏内存，随后重启实例再触发 fail-fast，符合内存压力型恶化链。
- 全部崩在 Ollama 官方发行二进制（version 字段 0.0.0.0 为其发行惯例），无第三方注入模块。

## 3. 环境取证（2026-09-16 实测）

- ollama 0.32.1；GPU=RTX 3090 24GB（报告时点已用 1147MiB——孤儿清理后基线正常）。
- 已拉模型 9 个（与 gguf_vram_budget.yaml models 登记一致）：qwen3:14b/deepseek-r1:14b/
  qwen2.5-coder:14b 各 9.0GB、qwen3:8b/deepseek-r1:8b 各 5.2GB、qwen3-coder:30b 18GB、
  BGE-M3 1.2GB、Qwen3-Embedding 4.7GB、bge-small 36MB。
- 预算口径：hard_cap 21.6GB（24×90%）；时段配额盘前/盘中 10GB、其余 4GB。
  9-15 事故形态（多实例 × 每实例按需 2 模型，如 14B 9.2+8B 5.4=14.6GB VRAM 需求）
  必然超订：单实例对即破盘中 10GB 配额，9 实例理论需求远超 21.6 硬上限——AV/fail-fast
  即在该超订背景下出现，与"加载/推理路径内存失败"自洽。

## 4. 归因链（第一性原理+量化证据）

1. 触发条件：boot detached spawn 无上限 → 9 实例并存（孤儿不收割，M1 前无登记无闸）。
2. 资源态：每实例按需加载模型 → VRAM 超订（>21.6GB）+ RAM 增至 ≈12GB → commit 触顶。
3. 缺陷暴露：超订下 llama.cpp 0.32.1 的确定性问题路径（AV@0x2a230）被稳定触发；
   部分实例走 fail-fast（BEX64）——两族同源不同 manifestations。
4. 循环放大：崩溃→watchdog/boot 重启→再加载→再崩溃（17:14 三连），直至页面文件扩容
   +孤儿收割（8aaede05cb）后收敛。
5. 8/27 两例 AV：同签名在更早日期出现，说明缺陷固有，9-15 只是压力放大暴露——
   **版本升级建议独立于超订治理成立**。

## 5. 防护落地与待裁

已落（本战役）：
- 孵化前 VRAM 预算门：`auto_runtime_core.ensure_running`（nvidia-smi 实测 > hard_cap
  21.6GB → 拒孵 + error 日志；探测失败 fail-safe 放行）。
- M1 孵化登记 + M3 超寿收割：崩溃-重启循环进程进入 ledger 可溯、超寿即杀（循环放大被断）。
- M2 水位门禁：commit ≥85% 排队/≥90% 拒绝孵化（重任务不再火上浇油）。

待裁（Owner 门位，需安装软件/服务窗口）：
- Ollama 升级（0.32.1 → 最新 stable）：AV 签名为确定性构建缺陷，升级是根因修复路径；
  升级后以本报告 §2 签名族清零为验收（复跑本报告事件日志查询）。
- `qwen3-coder:30b`（19GB，超全部时段配额，登记注仅夜间人工批准）建议核查是否仍需保留。

## 6. 复跑口径（验收用）

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000} -MaxEvents 2000 |
  Where-Object { $_.Message -match 'llama' } |
  ForEach-Object { $_.TimeCreated; ($_.Message -split "`n" | Select-String '异常代码','出错模块') }
```
升级验收 = 上查无新增 0xc0000005/0xc0000409 事件。

## 7. Resolution（2026-09-16 升级闭环，会话 st-ollama2-20260916，裁定#269）

- 升级执行：Ollama 0.32.1 → **0.34.1**（GitHub 官方发行 tag v0.34.1，published
  2026-09-14T22:14:03Z；资产 OllamaSetup.exe 1,570,506,608 B，api.github.com
  /releases/latest 当日 15:00/15:03 双时点复核一致）。来源 URL：
  https://github.com/ollama/ollama/releases/download/v0.34.1/OllamaSetup.exe
  接力说明：复用前任会话 st-ollama-20260916 的分段下载断点（9.3/16 段）+脚本，
  续传 49 分钟补齐；装前三道校验全过=大小精确匹配+PE MZ 头+Authenticode Valid
  （CN=Ollama Inc.）。安装包 SHA256=
  a92986c86ab6854675ffd1b725db7c0350d40755895c95c397c58d61014e14d9
  留存 `.runtime/tmp/ollama_upgrade/OllamaSetup.exe`（回滚保险，不入 git）。
- 时间线：15:50:29 正常停服（ollama serve PID 15628=ZephyrAlpha_OllamaServe 编排
  实例，01:01 起运行，cmdline/父链归属核实）→ 15:51 静默安装
  （OllamaSetup.exe /VERYSILENT /NORESTART）→ 16:09:21 服务恢复（新 serve
  PID 24788，绑 127.0.0.1:11434 与旧实例一致）。
- 编排如实记录：安装器尾随托盘链路（ollama app.exe→serve，绑 0.0.0.0）不符项目
  编排，已停；`schtasks /run` 两次触发 0.34.1 均启动阻塞（1 线程挂起不绑端口，
  非瞬态——0.34.1 在非 AtLogOn 触发上下文的启动缺陷），改用与原生产实例同形态
  分离启动（同 exe 同参，输出续写 .runtime/tmp/ollama_serve.log）；
  ZephyrAlpha_OllamaServe 任务定义零改动保留，下次 AtLogOn 真实登录按端口冲突
  自退出幂等设计自然接管（/run 挂起缺陷对 AtLogOn 路径无证据影响，留观察项）。
- 验证四全：① CLI+HTTP version=0.34.1；② GPU 识别正常（RTX 3090 CUDA
  driver 13.3，22.8 GiB 可用，vram-based default ctx 32768）；③ 冒烟 /api/tags
  200（9 模型与本报告 §3 清单逐一吻合）+ /api/generate 真实推理
  response='OK'（qwen3:8b，done_reason=stop，97 tok/s，keep_alive=0 冒烟后卸载）；
  ④ 四层合围零改动（git status config/gguf_vram_budget.yaml=clean）。
- 模型目录 E:\OllamaModels blob 数据零变动：目录 delta +38,500 B 恰为 0.34.1
  新增 9 个 `metadata/*.json` 边车（新版本正常行为，非安装器触碰模型数据）；
  冒烟产生的 2 个孤儿 llama-server runner（服务已报空载但进程不退）已手动收割，
  VRAM 回落 1,852 MiB。
- 升级动机对位：§2 AV-LLAMA 签名族为 0.32.1 内嵌 llama.cpp 构建的确定性缺陷
  路径；0.34.1 底层 llama.cpp 已多轮重建，缺陷根已换，同偏移路径不复存在。
- 被动验收（§6 口径）：升级前后均无新增 llama 崩溃事件（事件日志末次=
  2026-09-15 23:22:31）；**自 2026-09-16 16:09 服务恢复起 7 天（至 2026-09-23）
  无新增 0xc0000005/0xc0000409 llama 事件即正式闭环**，届时本报告按
  GATE-WORKING-DOCS 语义结案。登记：裁定#269（ruling_registry 同 commit）。
- 遗留转办：`qwen3-coder:30b` 保留性核查仍待裁（Owner 门位，与本升级解耦）。

## 8. 转办项核查：qwen3-coder:30b 保留性（2026-09-17，会话 st-qwenchk-20260916，裁定#290）

§5/§7 遗留转办项闭环。核查时点 serve 不在（0.34.1 未随 AtLogOn 自起），按 §7 同形态
分离启动 `ollama serve`（绑 127.0.0.1:11434）后完成核查并保持运行；下次 AtLogOn
ZephyrAlpha_OllamaServe 按幂等设计接管（端口冲突自退出）。

### 8.1 消费方普查（全仓 grep + 运行时实证）

| # | 位置 | 性质 | 生产链自动消费 |
|---|------|------|---------------|
| 1 | config/gguf_vram_budget.yaml §models | 预算门登记（role=backup，vram_gb=19.0，note 夜间人工批准） | 否（管控登记非调用方） |
| 2 | data/brain/passports/qwen3-coder_30b.json | 五轴入职考试护照（2026-06-25，B 级 0.732） | 否（资产档案） |
| 3 | scripts/run_ollama_exam.py | 考试脚本支持列表（非 DEFAULT_MODELS，需 --model 显式） | 否（低频手动） |
| 4 | src/zephyr/governance/ops_governance/cost_router.py:46 | QWEN3_CODER 云端 API 定价枚举（$0.35/$1.40 每千 token，131k ctx） | 否（同族云端 API 项，非本地调用方） |
| 5 | src/zephyr/intelligence/model_profiling/capability_passport.py:372 | 注释（护照文件名编码 bug 历史说明） | 否（文档性） |
| 6 | tests/ 3 件（gguf_model_manager/passport/cost_router） | fixture（mock 注入，不依赖真实在册） | 否（测试） |
| 7 | docs 4 处（03_model_lifecycle_flow/construction_progress_tracker/automation_linkage_plan/本报告） | 登记/快照描述 | 否（文档） |

运行时实证：services_registry/tasks.yaml 零引用；无任何代码路径自动孵化；psutil 无
ollama/runner 进程；data/audit_trail 零使用记录（从未被实际加载）。护照 depth 轴实证
编码核心能力不及格（code_generate P=0.167/F、code_edit_precision P=0.346/F、
refactor P=0.0/F），总分 B 系 breadth 0.97 撑起；编码 backup 角色已由配额内合法的
qwen2.5-coder:14b 承担。

### 8.2 VRAM 成本核算（对照预算口径）

- 实测磁盘 17.28GB（2026-09-17 /api/tags；qwen3moe 30.5B MoE，Q4_K_M——MoE 激活
  3.3B 不减全部专家权重的 VRAM 驻留）。
- 预算口径 vram_gb=19.0 = size×1.1（权重+KV cache 估算，与表头口径吻合）。
- 对照配额：19.0 > 盘前/盘中 10.0 > 午休/盘后/夜间 4.0——超**全部**时段配额，
  任何自动加载必被 check_load 拒绝；19.0 < hard_cap 21.6，唯一理论窗口=突破配额的
  人工特批（原 note"夜间人工批准"实为配额外特批：夜间配额 4GB 亦不可容）。
- 共存风险：19.0+5.4（最小 LLM qwen3:8b）=24.4 > 21.6 硬上限——加载即与任何推理
  模型互斥，系 §4 所述 9-15 超订事故形态的极端单点。

### 8.3 裁定与执行

裁定：**移除**（零真实消费方+超全部配额+能力实证不及格；可逆=re-pull）。

- 重拉口令（如需恢复）：`ollama pull qwen3-coder:30b`（17.28GB，Q4_K_M，30.5B，qwen3moe）。
- `ollama rm qwen3-coder:30b` exit=0；/api/tags 前后对照 9→8，余 8 模型与 §7 升级
  冒烟清单逐一吻合：qwen3:14b 8.38 / BGE-M3 1.08 / bge-small 0.03 / Qwen3-Embedding
  4.36 / qwen3:8b 4.87 / deepseek-r1:8b 4.87 / deepseek-r1:14b 8.37 / qwen2.5-coder:14b 8.37（GB）。
- config/gguf_vram_budget.yaml 同步删行（safe_write_text CAS）+头部计数注记更新——
  避免留行后 registered_but_not_pulled（gguf_model_manager.py 对账差异报告）持续噪音。
- tests/intelligence/test_gguf_model_manager.py::test_real_config_matches_live_inventory
  9→8 同步并锁定"不在册"断言（防 re-pull 不登记回归；原硬编码 9 恰为静态计数写死
  漂移实例）；相关 3 测试文件两轮 125 passed 零失败。
- 护照 data/brain/passports/qwen3-coder_30b.json 留档不移除（历史考试实证资产）。

登记：裁定#290（ruling_registry 同 commit）。
