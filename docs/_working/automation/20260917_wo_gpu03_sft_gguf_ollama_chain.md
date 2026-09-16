---
ttl: task_bound
completes_when: 情绪 SFT 模型回灌 Ollama 且夜窗情绪批切换自模型验证一轮
---

# 工单 GPU-03：SFT→GGUF→Ollama 回灌链常态化

> 状态：READY（唯一缺"窗"与"数据集核实"）｜风险：低中｜前置：无硬前置（走冲突闸）
> 使命来源：docs/_working/automation/20260917_automation_linkage_plan_v1.md §2-Q2 路 b

## 1. 就绪度证据

- `scripts/ml/run_sft_train.py`：完整 QLoRA 4-bit 训练 CLI（Qwen2.5-7B，smoke+full 两档），产出 adapter 至 models/qwen25-7b-sft-v1/，Macro-F1 评估在环。
- `scripts/ml/convert_gguf_ollama.py`：adapter→GGUF→Q4_K_M→`ollama create` 端到端，默认 --dry-run（交付态），需 --llama-cpp-dir 指向本机 llama.cpp 工具。
- 注册表两实体已挂：manual_run_sft_train / manual_convert_gguf（gpu_default 互斥组）。
- 闭环价值：夜窗情绪批（manual_run_sentiment_batch，llm_local 180m）从通用 qwen3 切**自研情绪模型**——单一推理源+零 API 成本。

## 2. 施工步骤

1. 核实训练数据集在位：`data/sft/train.jsonl`（build_sft_dataset.py 可再生）+ 评估集 news_sentiment_200。
2. GPU 窗登记：双周周日日间窗（gpu_default 空档，冲突闸拦截兜底）；跑 run_sft_train full 档。
3. convert_gguf_ollama 真跑（去掉 dry-run，指 llama.cpp 目录）→ `ollama list` 出现自模型。
4. 情绪批 A/B：run_sentiment_batch 小样本分别用 qwen3:8b vs 自模型，对齐标注口径后切换。

## 3. 验收标准

- [ ] 自模型在 Ollama 注册且 `ollama_version_guard` 版本约束通过
- [ ] 情绪批切换后 Macro-F1 不低于通用模型基线-2%
- [ ] 全程 gpu_default 互斥无违例（冲突闸/告警桥零红）

## 4. 备注

- 训练属资源重活：跑前在 process_reaper_keep.txt 登记白名单防误杀。
- llama.cpp 目录若缺→本工单挂起，登记缺件，不代装（软件安装=Owner 门位）。
