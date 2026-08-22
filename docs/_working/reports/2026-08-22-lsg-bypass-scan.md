---
ttl: task_bound
---

# LSG 绕过路径静态扫描报告（18号清单 §4.1 / 09号文 §4.2 P0-2）

- 日期：2026-08-22
- 工单：18号清单 §4.1（09号文 LSG 主链路贯通收尾，GP0 退出项 E0-2）
- 验收口径：09号文 §4.2 P0-2 —— 全仓扫描报告绕过路径数 = 0（豁免项白名单登记）
- 环境：Windows / Python 3.12.8 / Asia/Shanghai

## 一、结论

**绕过路径数 = 0。** 两种扫描模式均零命中，无需新增豁免登记。

| 扫描模式 | 范围 | 命中数 | 退出码 |
|----------|------|:---:|:---:|
| RULE-LSG-001（裸调 LLM API/客户端创建/exec-eval 包裹） | src/zephyr/**/*.py 全量（2919 个 .py） | **0** | 0（PASS） |
| COND-30（业务层直接 import LLM SDK 存量检测） | src/zephyr 业务层（l02-l39_* / B 轨目录） | **0** | 0（PASS） |

## 二、执行方式

```powershell
# 模式 1：RULE-LSG-001 全量扫描（CI 全量口径，等价 pre-commit 去掉 --staged）
python scripts/governance/d7_code/detect_direct_llm_calls.py
# 输出：PASS: 所有 LLM 调用均已通过 LSGSecurityGateway 保护（exit 0）

# 模式 2：COND-30 导入检测
python scripts/governance/d7_code/detect_direct_llm_calls.py --cond30
# 输出：[LLM-CALL] 业务层无直接 LLM 调用（exit 0）
```

pre-commit 链既有调用方式（.pre-commit-config.yaml L679-687，GATE-20）：
`entry: python scripts/governance/d7_code/detect_direct_llm_calls.py`，`args: [--ci, --staged]`，
`files: ^src/zephyr/.*\.py$`，硬阻断模式——变更检测只扫 staged 文件，本次报告用全量口径复核。

## 三、扫描器有效性阴性对照（防空转）

合成探针 `.runtime/_probe_bare_llm.py`（内容：`import openai` + `openai.OpenAI()` + `chat.completions.create()`）
经 `scan_file()` 检出 **2 处违规**（L3 客户端创建、L4 裸调），证明扫描器非空转；探针用后已删除。

## 四、既有豁免机制登记（本次无新增）

扫描器内置豁免（scripts/governance/d7_code/detect_direct_llm_calls.py）：

| 豁免类别 | 机制 | 本次命中 |
|----------|------|:---:|
| 已导入 LSGSecurityGateway / llm_security.gateway 的文件 | `_has_lsg_import` AST 判定（含 importlib 动态导入） | —（未触发违规，无需引用） |
| LSG 模块自身 | `_is_lsg_module`（路径含 llm_security） | — |
| tests/ 目录 | `_is_test_file` | — |
| model_profiling 基础设施（存量待迁移） | `_EXEMPTED_FILES` 4 个路径前缀 | — |

## 五、本工单改动与扫描的交叉确认

本次在 `src/zephyr/integration/local_model/` 新增/改动 5 个文件
（新建 lsg_gate.py；改 ollama_chat.py / deepseek_chat.py / local_model_scheduler.py / embedding_router.py），
全部经 `zephyr.integration.local_model.lsg_gate` 引入 LSG 闸门；4 个客户端底层走 `requests` HTTP 调用
本地 Ollama / DeepSeek API，无 openai/anthropic/litellm/langchain SDK 直连——扫描复核 0 命中，与预期一致。

## 六、残余风险注记

- 扫描口径覆盖 AST 可见的裸调模式（SDK 调用/客户端创建/exec-eval 字符串）；`requests` 直连第三方 LLM HTTP
  端点的语义级识别不在 GATE-20 规则内——该面由运行时拦截器（runtime_interceptor.py，sys.meta_path 拦截
  openai/anthropic/litellm/langchain 裸调）+ 本次 L2/L3 客户端构造点注入（lsg_gate）共同兜底。
- `_EXEMPTED_FILES` 中 model_profiling 4 个路径前缀为既有存量豁免（扫描器注释注明"待迁移后移除"），
  本次全量扫描这些路径下亦无违规命中，豁免未被动用。
