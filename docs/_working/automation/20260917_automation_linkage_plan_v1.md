---
ttl: task_bound
completes_when: 待批清单全部获 Owner 批复并施工完毕，或本方案被 v2 替代
---

# 交易体系自动化联动方案 v1（会话 st-autolnk-20260917）

> 使命：讨论透→落盘→执行当前可安全执行部分。施工队在飞红线已遵守：未写 docs/03_modules/**、TDM、AGENTS.md、pf_core/backtest；产出全部在本目录+注册表再生（走生成器正门）。
> 证据基线：2026-09-17 凌晨实测（nvidia-smi / Task Scheduler 全量 / 注册表 60→72 实体 / 双探查代理代码级取证）。

## §1 现状盘点（已有资产，勿重复建设）

| 资产 | 现状 | 真源 |
|------|------|------|
| 工厂四段自动 | 周六 10:00 LaneC 挖矿→14:00 C4 考试→intake 自动入库（另有 F06Grid 周六 14:00 周窗） | sch_factory_lane_c / sch_c4_exam / sch_f06_grid（注册表已全收） |
| DataScheduler | 四池 21 槽位全部入注册表（data_slot_*） | src/zephyr/data/config/schedule.yaml |
| 资源排班系统 | 注册表 72 实体×18 字段+冲突闸+周历视图+ops 告警桥 | config/resource_profile_registry.yaml（生成器产出） |
| 进程守护 | reaper（实测 00:37 刚跑）+孵化登记+水位门 10GB | process_reaper |
| 挖矿 LLM | **已经全本地化**（见 §2-Q1 翻案） | OllamaChat+LSG（lane_b/lane_c2/hypothesis_translator） |
| 计划任务全景 | 实测 37 项 ZephyrAlpha/项目任务（含 4 项测试遗留，见 §3） | Task Scheduler（本次全量盘点入注册表） |
| GPU | RTX 3090 24G，利用率 37%≈桌面+Ollama 驻留（1.8G），项目 GPU 计算=0 | nvidia-smi 实测 |
| Ollama | 9 模型在位（qwen3:14b/8b、deepseek-r1:14b/8b、qwen3-coder:30b、qwen2.5-coder:14b、BGE-M3 等）；OllamaServe 计划任务常驻+版本 guard（≤0.32.1 拒注册） | ollama list 实测 |

## §2 四问结论

### Q1 GPU 为什么空转——根因裁定

**第一性原理**：一块算力闲置只有两种可能——(a) 没有 job 指向它（需求侧），(b) 有 job 但调度不到它（调度侧）。本项目两条都占：

1. **需求侧=零**：工厂产线全是 CPU 工种（挖矿=LLM 推理+公式合成、考试=回测、入库=DB 写）。唯一 GPU 工单 Kronos 微调是一次性工单，2026-09-16 已完工——完工后 GPU 需求归零。
2. **调度侧=按时间不按资源**：11→37 个计划任务全部 cron 触发，从未按"GPU 空闲"派工；排班系统昨晚才上线，GPU 工种画像（gpu_default 互斥组）有了架子但没有常驻 job 填进去。
3. 实测 23%~37% 利用率 ≈ Windows 桌面 + Ollama 驻留，**项目份额≈0**——不是"用得少"，是"从未立产线"。

**前提翻案（重要）**：使命书假设"夜间挖矿 LLM 从 API 切本地 Ollama"。代码级取证结论：**挖矿链路已经全本地化**——lane_c2_agentic_miner.py:336/360、hypothesis_translator.py:152、lane_b_idea_generator.py:133 全部走 `OllamaChat`（qwen3:8b 默认，内嵌 LSG 闸 fail-closed）；云 API（GLM/DeepSeek/Kimi）只在 llm_gateway/cost_router 等网关层存在，**不在挖矿路径上**。路径 a 剩余的不是"切换"，是"夜窗扩产+模型档位治理"（→ 工单 GPU-01）。

### Q2 占满性能的三路路径

**路 a——夜间挖矿常态化（工单 GPU-01）**：把 lane_b/lane_c/mcts/假设翻译从"周六一次"扩为夜窗常批（Ollama GPU 推理），qwen3:8b→14b 档位 A/B 一次定版；14b/30b 跑前过 gguf_vram_budget 检查。互斥组 llm_local（qwen3:8b 单实例语义需随档位复核）已在注册表。

**路 b——GPU 常驻工种四张工单**（探查代理代码级就绪度裁定）：

| 工单 | 就绪度 | 缺件 |
|------|--------|------|
| GPU-01 夜间挖矿批+档位 A/B | 高（客户端/LSG/模型全在位） | 夜窗 register ps1+排班实体+一次 A/B |
| GPU-02 Kronos 批量推理打分 | NEEDS-ADAPTER | 推理-only 前瞻模式（现有 --top-n 通道是评估型、输出只 print）+预测落表（无表无写入方）+信号消费 B-007 门 |
| GPU-03 SFT→GGUF→Ollama 回灌链 | READY | 数据集核实+GPU 窗登记即可跑（run_sft_train.py 完整 QLoRA CLI；convert_gguf_ollama.py 端到端默认 dry-run） |
| GPU-04 RL 执行训练 | DESIGN-ONLY | env 骨架无 torch 无 trainer；真训练被 B-007 人工闸锁（宪章 §4.2）——先施工 trainer 再过门 |

**路 c——排班联动（本排班系统的设计初衷）**：全部实体入注册表（本次 60→72，见 §4）→ 夜窗 GPU 时刻表（§6 草案）→ 冲突闸自动拦截（gpu_default/llm_local 互斥组）→ 周历视图人审 → ops 告警桥直达 promotion 页。联动已闭环的证明：本次补注册后 CH 周六凌晨同窗冲突首次变为闸可见（§3-②）。

### Q3 还有哪些该自动化（对账后三件，防重复建设）

1. **自动生成数据因子**：tilib 已有 `tilib_indicator_backfill_nightly`（每日 02:30）+积压池实测 ~40 指标可开工（M-L1/L2/L3/L5 未入库）。建议：tilib 线把"积压池排程化"（每周新指标批+自动回填），非本会话职权，登记建议。
2. **全网搜论文/策略**：定位=对话⑥终局 AI 层的缺失"全网搜索"段。设计红线：**只搜不自动入册**——产出每日候选清单（inbox），LLM 摘要走 Ollama 夜窗（顺带填 GPU），入册走既有 intake+人工确认/门控。外呼边界+LSG 适配需 Owner 点头后才施工（→ 待批）。
3. **自动晨报/周报**：已有件=sim 平台日刊健康三检+ops 告警桥+DataScheduler 对账。缺口=跨链路一页晨报（数据缺口+工厂产出+排班冲突+GPU/内存水位）。建议：只读生成器消费现有注册表/台账/样本 JSONL，产出 markdown，前端挂接等收工（→ 工单级建议，登记待批）。

### Q4 执行分级

| 级 | 项 | 状态 |
|----|----|------|
| 已执行（本次） | ① ops_* 11 实体补注册+F06Grid 覆写+计数追认（72 实体零漂移 8/8 测试绿）② 本方案+四工单落盘 ③ 审计发现六条登记（§3） | ✅ |
| 等施工队收工 | GPU-01 夜窗批接线（scripts/backtest 红线区）、GPU-02 Kronos 打分施工、晨报生成器施工 | ⏸ |
| Owner 门位 | ① 4 个测试遗留任务处置（§3-④）② CH-OptimizeMerge register ps1 化+任务名规范化（改活任务）③ RL 真训练 B-007 ④ 外网搜索 agent 启用 ⑤ F06Grid/C4Exam 同刻错窗处置 | ⏳ 待批 |

## §3 审计发现（六条，全部带证据，只登记不代修）

1. **F06Grid 与 C4Exam 周六 14:00 同刻双重活**：两任务均 weekly Sat 14:00（register_f06_grid_task.ps1 注释只对齐"after LaneC 10:00"，未提 C4Exam）；两实体均 cpu_heavy/heavy 池。建议错窗（如 F06Grid→15:00 或入 mine_vs_exam 串行组——语义归 Owner/资源线裁）。
2. **CH 周六凌晨同窗冲突（本次补注册后闸首次可见）**：data_slot_weekend_calibration（Sat 03:00+180min，ch_bulk_write）vs ZephyrAlpha-CH-OptimizeMerge-Weekly（Sat 03:30，已补注册 ops_ch_optimize_merge_weekly）。治本=给它立 register_*.ps1（现 dash 命名+launch_hidden.vbs 直注册，生成器 I1 正则看不到）——涉改活任务，待批。
3. **nightly_sentiment 疑似双真源**：排班表槽位 cron 08:20（data_slot_nightly_sentiment）vs Windows 任务 ZephyrAlpha_NightlySentiment 实测 22:30。两处都可能真跑。建议数据线核对归一。
4. **4 个测试遗留任务仍在每日重跑整条工厂线**：C4Exam_Full0916 / C4Exam_OneShot0915（每日 17:30）、FactoryLaneC_Full0916 / FactoryLaneC_OneShot0915（每日 15:35），均为 Ready 状态、调 run_c4_exam.ps1 / run_factory_lane_c.ps1 全量脚本。处置（禁用/删除/转正）=Owner 门位，本会话不动。
5. **sch_pattern_mining 有源无任务**：register_pattern_mining_task.ps1 在、注册表实体 active，但 Task Scheduler 无 ZephyrAlpha_PatternMining 任务。图形库线核对是否需重挂。
6. **周六 06:00 备份同刻**：DailyBackup（每日 06:00）与 WeeklyVMBackup（周六 06:00）同刻叠磁盘 I/O（F 盘增量+VHDX）。影响=备份窗口拉长，非致命，登记备查。

## §4 已执行清单（本次三件，全证据留痕）

1. **排班表补注册（生成器正门，未手改 YAML）**：MANUAL_ENTITY_SEED 追加 ops_* 11 实体（CH 周合并/日备份/VHDX 周备份/IO 月检/tilib 夜回填/bdpan tick 守望/板块指数/板块快照/QMT 看门狗/TTL 重判/AI Wrapper）+ PS1_TASK_OVERRIDES 补 F06Grid（cpu_heavy/heavy/240min）。注册表 60→72 实体，`--check` 零漂移，模块测试 8/8 绿（含 test 计数 19→20 追认：register_f06_grid_task.ps1 落地时未再生注册表，本次一并治好）。
2. **方案+工单落盘**：本文件+四张 GPU 工单（同目录 wo_gpu01~04）。
3. **审计发现六条登记**（§3）+ 待批清单（§5）。

## §5 待批清单（Owner 门位/排序建议）

| # | 项 | 门位 | 建议时点 |
|---|----|------|---------|
| 1 | 4 个测试遗留任务处置（§3-④，每日白烧 CPU+Ollama） | Owner | 随时可裁，建议先裁（白烧最实） |
| 2 | F06Grid/C4Exam 周六 14:00 错窗（§3-①） | Owner/资源线 | 下周六 14:00 前 |
| 3 | CH-OptimizeMerge register ps1 化+任务名下划线规范化（§3-②治本） | Owner（改活任务） | 排班线收工后 |
| 4 | GPU-01 夜窗挖矿批接线+模型档位 A/B 定版 | 施工（等收工）+结果报备 | 红线解除后 |
| 5 | GPU-02 Kronos 批量推理打分（含预测表 DDL+B-007 消费门申请） | 施工+B-007 | 红线解除后 |
| 6 | GPU-03 SFT→GGUF 回灌链首跑（数据集核实+窗登记后可跑） | 中风险自动，窗冲突闸拦 | 随时（走闸） |
| 7 | GPU-04 RL trainer 施工+B-007 真训练审批 | B-007 | 排期后 |
| 8 | 外网论文/策略搜索 agent 启用（外呼边界） | Owner | 对话⑥收口时 |
| 9 | 全链晨报生成器施工 | 施工（低风险） | 红线解除后 |
| 10 | tilib 积压池排程化建议 | tilib 线 | 传值即可 |

## §6 GPU 夜窗时刻表草案（待批后由资源线/维护班接线；互斥组已全部在注册表）

```
每日（周一~周五夜窗，双互斥组串行防炸显存）：
  22:30  data_slot_nightly_sentiment（llm_local，20m）        [已有]
  23:00  GPU-01 夜挖批 lane_b/mcts（llm_local，~60m）          [待批#4]
  00:30  GPU-02 kronos 全市场打分（gpu_default，~60m）         [待批#5]
  02:30  tilib_indicator_backfill_nightly（cpu，与 GPU 无冲突） [已有]
  03:00  DataScheduler heavy 槽（nightly_financial 等）        [已有]
周六：10:00 LaneC → 14:00 C4Exam/F06Grid（待批#2 错窗）→ 06:00 备份对齐（§3-⑥）
周日：GPU-03 SFT/回灌链维护窗（gpu_default，双周一次）          [待批#6]
约束：任一时刻 gpu_default 组内至多 1 实体（Kronos/Ollama 大模型/SFT/转换互斥）；
     llm_local 单实例；冲突闸登记时拦截，ops 告警桥兜底。
```

## §7 关联

- 工单：同目录 `20260917_wo_gpu01_night_mining_ollama.md` ~ `wo_gpu04_rl_execution_training.md`
- 排班方案真源：docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md
- 生成器：scripts/governance/generators/generate_resource_profile_registry.py（MOD-RESCHED-PROFILE）
- 会话：st-autolnk-20260917（claim：生成器+注册表两文件）
