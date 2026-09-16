---
ttl: task_bound
completes_when: 夜窗挖矿批上线且模型档位 A/B 定版并报备
---

# 工单 GPU-01：夜间挖矿常态化 + 模型档位治理

> 状态：待施工队收工（scripts/backtest 红线区）｜风险：中｜前置：红线解除
> 使命来源：docs/_working/automation/20260917_automation_linkage_plan_v1.md §2-Q2 路 a

## 1. 事实修正（先纠偏再施工）

挖矿 LLM **已经是本地 Ollama**，不存在"API→Ollama 切换"：
- `scripts/backtest/lane_c2_agentic_miner.py:336` import OllamaChat；`:360` 实例化；`:57` MODEL_DEFAULT="qwen3:8b"
- `scripts/backtest/hypothesis_translator.py:56` 同默认；`scripts/backtest/lane_b_idea_generator.py:133` 同
- LSG 已覆盖本地调用：`src/zephyr/integration/local_model/lsg_gate.py`（fail-closed，默认启用）
- 本工单实际内容=**夜窗扩产+档位治理**，不是切换。

## 2. 施工步骤

1. **档位 A/B（一次定版）**：同一批挖矿种子分别用 qwen3:8b / qwen3:14b / deepseek-r1:14b 跑 lane_c2+lane_b 各一轮，对比假设产出量/入考通过率/幻觉率（`--model` 参数已支持，零代码）。
2. **档位落地**：胜出模型改三处 MODEL_DEFAULT 或统一设 `OLLAMA_INFERENCE_MODEL`（ollama_chat.py:58 已支持）；同步复核 llm_local 互斥组"qwen3:8b 单实例"语义与 VRAM 预算（14b≈9G 盘上/推理峰值对照 config/gguf_vram_budget.yaml）。
3. **夜窗批接线**：新增 register_night_mining_task.ps1（任务名 ZephyrAlpha_NightMining，cron 23:00 周日~周四，跑 lane_b+mcts 候选批进 intake 积压池，**不自动入册**）；跑 `generate_resource_profile_registry.py` 再生→新实体自动挂 llm_local 互斥组。
4. **验收**：冲突闸对夜窗批与 22:30 sentiment 批互斥生效；周六产线不受影响（mine_vs_exam 组回归）；周历视图出现夜窗块。

## 3. 验收标准

- [ ] A/B 报告落盘本目录（含三档位产出对比表）
- [ ] 夜窗任务注册且注册表实体生成（schedule_truth_source=新 ps1）
- [ ] 连续两夜实弹零冲突告警
- [ ] 档位定版报备 Owner（默认胜出档自动生效，除非引 VRAM 超预算）

## 4. 红线与禁区

- scripts/backtest 解冻前不得动 lane_* 源码（A/B 用 --model 参数零改动可做，可先行）。
- 新 .ps1 纯 ASCII（宪法 §9.7）。
