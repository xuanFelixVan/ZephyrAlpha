---
ttl: task_bound
title: 接续收口册01 — LSG 拦截死路径取证（双捕防线绕行面全清单）
lane: m4_ai_layer
session: st-ailayer-fullflow-ai
date: 2026-09-25
status: mined
---

# 01 — LSG 拦截死路径取证（F88 收口）

> **一句话**：GATE-20（静态 AST）+运行时拦截器（monkey-patch）双捕防线存在 **15 条死路径**；其中最重一条为本日新实锤——**运行时拦截器在本机全调用模式均未引导（finder 实测 NONE×4），"第二捕"当前整体不在岗**，仅 GATE-20 单网在防。
> 勘误回填：M4 分册03 记"sitecustomize.py 实存 Python 启动即 bootstrap"——文件实存但**引导不生效**，本册纠正（分工册 §三.5 口径回填义务）。

## 一、环节定义与边界

取证对象=LLM 安全网关双捕防线的**绕行面**（死路径=裸调可从两网之间或之外穿过的通道）。真源：`src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py`（537 行，第一捕后备）、`scripts/governance/d7_code/detect_direct_llm_calls.py`（433 行，GATE-20）、`sitecustomize.py`（63 行，引导件）、`scripts/setup_dev_env.py`（usercustomize 安装器）。上游=RULE-LSG-001（拦截器头 INVARIANTS）；下游=全部 LLM 调用方。

## 二、六向台账

| 向 | 实测证据 |
|---|---|
| 上游输入 | 双网输入面：GATE-20=pre-commit AST 扫 staged/全量 .py（detect:308 scan_file）；拦截器=进程内 openai/anthropic/litellm/langchain 四库方法调用（runtime_interceptor:420-425 `_PATCHERS`） |
| 下游消费 | 拦截器 ALLOW 令牌由 gateway 消费（gateway.py:43-48 import grant_allowance/reset_allowance_for_request，**gateway 不调 install()**——引导全靠 sitecustomize/usercustomize）；违规出口=BareLLMCallError（error_code ZA-SC-0022，:86-93） |
| 自动化触发 | GATE-20=pre-commit 事件（.pre-commit-config.yaml:707 gate-20-llm-security-gateway，行号较分册03 记载的 681 漂移）；拦截器=解释器启动引导（sitecustomize:57-59）——**本机实测该触发全模式失效（见 §三 DP-1）** |
| 真源与注册表 | RULE-LSG-001；MOD-LLM_SECURITY；引导链=sitecustomize（仓内）+usercustomize（**仓外全局文件，不在版本控制**，setup_dev_env.py:60-77 生成） |
| 门禁与质量尺 | tests/llm_security/test_runtime_interceptor.py；kill-switch=ZEPHYR_RUNTIME_GATE=0（:81,:505 sitecustomize:47 双重尊重） |
| 当前运行状态 | **红（防线半失位）**：GATE-20 静态网在岗（pre-commit 在案）；运行时网四模式引导全死（`python -c`/脚本/-m/异 cwd 实测 finder 均 NONE，2026-09-25）；gateway 实例化 OK 但其颁令无 patch 面消费 |

## 三、死路径清单（15 条，按严重度降序）

### A 级·防线失位类（当前即可裸穿）

| # | 死路径 | 证据 | 说明 |
|---|--------|------|------|
| DP-1 | **运行时拦截器全模式未引导** | 实测 4 探针全 `finder: NONE`：①`python -c`（仓根）②脚本模式（仓根）③`python -m`④异 cwd `python -c`；根因链=Python 3.11+ site 搜 sitecustomize 不含 cwd/script 目录（sitecustomize.py:17-30 裁定 #ARCH-PYTHON-SITECUSTOMIZE 自述"python -c 下本文件是死代码"）+主机制 usercustomize.py **本机不存在**（`C:\Users\fanzi\AppData\Roaming\Python\Python312\site-packages\usercustomize.py` 实测缺）+user site-packages 无 .pth+PYTHONPATH unset | "第二捕"整体不在岗；30s 令牌/令牌混合存储等机制全部空转 |
| DP-2 | **usercustomize 不在版本控制** | setup_dev_env.py:59-77（模板生成写 USER_SITE）+sitecustomize.py:27-30 自述"由 AI 进项目时一次性配置" | 结构性风险：换机/换用户/重装 Python=运行时网静默消失，无任何告警；冷启动序列（宪法 §0）不含此检查项 |
| DP-3 | **kill-switch 单环境变量全局关闭** | runtime_interceptor.py:81,:505；sitecustomize.py:47 | `set ZEPHYR_RUNTIME_GATE=0` 一条 env 免疫整个运行时网，无审批、无留痕、无告警 |
| DP-4 | **patch 挂载 fail-open** | exec_module 内 patch 失败静默 `pass`（:445-451 注释自述"宁可漏拦也不破坏导入链"）；install() 失败返回 False 不重试不告警（:515-517） | 挂载层失败开放：SDK 版本升级致 patch 目标改名时防线静默蒸发 |
| DP-5 | **allow_llm_call 逃生门无二级审批** | :207-239（sync）/:242-266（async）；拦截器白名单放行该名字 | 设计内逃生；上下文块内任意裸调放行，仅事后审计可追 |

### B 级·patch 面缺口类（SDK 侧绕行）

| # | 死路径 | 证据 | 说明 |
|---|--------|------|------|
| DP-6 | **白名单仅 4 顶层库** | `_PATCHERS`={openai, anthropic, litellm, langchain}（:420-425） | google-genai/mistralai/cohere/zhipuai/dashscope/groq/together/ollama 客户端/llama_index/autogen/dspy 等全部不拦（仓内现无此类调用=GATE-20 兜底，扩库即漏） |
| DP-7 | **openai v2.36.0 Responses API 未 patch** | 本机 openai=2.36.0（pip show 实测）；`_patch_openai` 仅 patch `chat.completions.create` 同步+异步（:317-326，import 限 `openai.resources.chat.completions`） | v2 主推入口 `client.responses.create()` 完全在 patch 面外；GATE-20 签名清单亦无 responses.create（detect:85-95）——**双网同漏** |
| DP-8 | **openai 其他方法面未 patch** | 同 :317-326 | embeddings.create/completions.create(legacy)/batches/files 等不拦（embeddings 算 LLM API 消费面） |
| DP-9 | **anthropic 仅 messages.create** | :329-341（import 限 `anthropic.resources.messages` 的 Messages/AsyncMessages.create） | `messages.stream()`/`count_tokens()` 等独立方法不拦 |
| DP-10 | **litellm 仅模块级 completion/acompletion** | :344-367 | `litellm.Router` 实例方法/text_completion/batch_completion 不拦 |
| DP-11 | **langchain patch 面三重窄** | :370-416（_import_chat_classes 仅试 `langchain.chat_models` 与 `langchain_community.chat_models` 两路径的 ChatOpenAI/ChatAnthropic，仅 patch `.invoke`） | 新标准包 `langchain_openai.ChatOpenAI` 直接导入不拦；`.ainvoke/.generate/.batch` 等方法不拦；其他 Chat* 类（Google/Mistral/…）不拦 |

### C 级·静态网盲区类（GATE-20 侧）

| # | 死路径 | 证据 | 说明 |
|---|--------|------|------|
| DP-12 | **原生 HTTP 调用双网同漏** | GATE-20 签名=SDK 方法链+客户端构造+字符串常量（detect:85-95,:236-276），无 URL/host 字符串扫描；运行时无代理层 | `requests.post("https://api.openai.com/v1/chat/completions",…)`/httpx/aiohttp 直连不设防 |
| DP-13 | **非 Python 运行时不设防** | 双网均为 Python 生态内（AST+meta_path） | node/claude CLI/curl/PowerShell Invoke-RestMethod 等 LLM 调用完全出网 |
| DP-14 | **exec/eval 变量拼接运行时才可见** | detect 头注自述+仅扫字符串常量字面量与简单 BinOp 拼接（_get_string_value detect:179）；base64/编码后 exec 不可见 | 文件头已声明的"不可修复静态上限"；运行时网在岗时可兜，但见 DP-1 |
| DP-15 | **GATE-20 三重豁免面** | tests/ 全目录（detect:312-313）+LSG 模块自身（:313-314）+model_profiling 存量清单（:115-119）+**单行 LSG import 全文件免检**（_has_lsg_import detect:191；scan_file:325-326 "已导入 LSG → 放行"） | 文件头 import 一次 LSGSecurityGateway 即可让同文件后续全部裸调免静态检——绕过成本=一行合法 import |

### 附：令牌机制边界（非死路径但记录）

令牌 TTL 30s 粗粒度（:83,:146-168）：grant 后 30s 内同线程/同任务任意调用放行，非 per-call 授权；`reset_allowance_for_request`（:193-204）防线程池令牌残留但依赖消费方中间件主动调用（纪律性防线）。

## 四、修法草案（按性价比排序，供施工立项）

1. **引导链修复（解 DP-1/2，最高优先）**：跑 `python scripts/setup_dev_env.py` 落 usercustomize.py+①宪法 §0 冷启动序列增一行 usercustomize 存在性校验②AutoRuntime Core 启动链增 `is_installed()` 自证告警（可观测性兜底）③usercustomize 内容哈希入某注册表防漂移。工作量=配置级+一处告警埋点。
2. **GATE-20 签名扩面（解 DP-7 前半）**：`_BARE_LLM_SIGNATURES` 增 `responses.create`（detect:85）；`_BARE_LLM_CLIENTS` 视需扩。工作量=清单行级。
3. **patch 面扩 responses.create（解 DP-7 后半）**：`_patch_openai` 增 `openai.resources.responses.Responses.create` patch。工作量=单函数级，tests/llm_security 同步。
4. **LSG-import 豁免收紧（解 DP-15 后半）**：已导入 LSG 的文件改为"逐调用点校验"或至少告警非阻断。工作量=中，可缓。
5. **扩库白名单（解 DP-6）**：按引入新 SDK 同步扩 `_PATCHERS`，登记为"扩库检查单"条目即可（当前零此类调用，不急）。
6. DP-3/4/5 属设计取舍（fail-open 换稳定、逃生门换可用性），建议仅在 kill-switch 处加审计留痕，其余维持。

## 五、自审闸三态

**挖干可施工**：15 条死路径逐条带 file:line 或可复跑命令；DP-1/DP-2 为本日新实锤（四模式探针+usercustomize 缺席+user site-packages 清单），纠正分册03 一处"绿"判；修法草案逐条列。零 LLM 外呼，全部证据=静态读取+解释器内省+进程探针。

## 六、复核命令

```bash
# DP-1 四模式探针（任一返回 NONE 即引导死）
python -c "import sys; print([type(f).__name__ for f in sys.meta_path if 'LLMGuard' in type(f).__name__] or 'NONE')"
python -c "import site,os; print(os.path.exists(os.path.join(site.getusersitepackages(),'usercustomize.py')))"
# DP-7 双网签名
sed -n '317,326p' src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py
sed -n '85,95p' scripts/governance/d7_code/detect_direct_llm_calls.py
# 令牌/kill-switch
sed -n '81,83p;505,517p' src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py
```
