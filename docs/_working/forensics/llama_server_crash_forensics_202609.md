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
