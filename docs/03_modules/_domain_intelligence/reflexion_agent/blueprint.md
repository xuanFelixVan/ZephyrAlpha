---
blueprint_id: MOD-REFLEXION_AGENT
module_name: reflexion_agent
domain: D_INTELLIGENCE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-REFLEXION_AGENT reflexion_agent 蓝图

> 紧凑版（SOP Step 4 补建，四件合一）。设计真源：12号文 §3.1/§3.2 / §4.2 P0-1~P0-4 + 18号清单 §6 波4-12 + #ARCH-166。
> 代码：`src/zephyr/intelligence/reflexion/`（reflection_schema.py / roles.py / l1_reflector.py / batch_runner.py）

## 0. 定位

自反 Agent Phase 0 地基：失败轨迹 → 归因 → 改进建议的结构化反思机制。三角色是逻辑角色而非三个常驻进程（同一 LLM 会话内可分步扮演）；GP0 手动形态 = 规则化归因 MVP，不调 LLM（12号文 §5-8 不做自由文本感想式反思）。Why 三角色分离而非单角色自问自答：生成与评估共用同一上下文会系统性高估自身产出，Evaluator 独立上下文+结构化量规是廉价的对抗性（§3.2）。避让纪律：feedback_loop 同名运维桩零触碰；L2/L3/PreFlect/ReflCtrl 留 Phase 1+ 不抢。

## 1. 四件职责与接口

| 件 | 职责 | 关键接口 |
|---|---|---|
| reflection_schema（P0-1） | 三级反思共用的结构化记录契约 + 落盘器 | `ReflectionRecord` / `ImprovementSuggestion`（严格校验 fail-closed）；`ReflectionStore.append/read_all` |
| roles（P0-2） | Actor→Evaluator→SelfReflection 三角色协议化骨架（typing.Protocol 结构化子类型） | `ActorProtocol/EvaluatorProtocol/SelfReflectionProtocol`；`run_three_role_flow()`；合成实现 SyntheticActor/RubricEvaluator/L1SelfReflection（骨架跑通/测试用） |
| l1_reflector（P0-3） | L1 单轨迹反思器：规则化归因 + 建议模板（执行层，触发频率最高/成本最低） | `L1Reflector.classify/suggest/reflect`；归因词表六类 config 化可注入 |
| batch_runner（P0-4） | 盘后批量反思入口（手动+计划任务挂点，本件不含调度器） | `BatchReflectionRunner.run_batch(trajectory_dir)`；`load_trajectory(path)` |

## 2. 输出契约

- `ReflectionRecord` 字段（工单冻结）：reflection_id/task_id/trajectory_ref/outcome（success|failure）/failure_category/improvement_suggestions[]/created_at/schema_version=1.0；每条建议锚定归因类别（category 须等于记录 failure_category）且 evidence_ref 追溯轨迹片段（如 step[2]）。落盘 `data/brain/reflections/reflections.jsonl` 追加，from_dict 对称往返可读回（坏行即抛）。
- `EvaluationReport`：score [0,1] + dimensions（非空各 [0,1]，对齐 13号文 §3.5 接口假设）+ defects 清单；字段不完整 → ValueError。
- 归因词表（默认六类，插入序先命中先判）：数据错误/逻辑错误/契约违反/环境问题/需求误解/未知（兜底）；命中证据=首个含关键词的轨迹步，无命中归"未知"并锚定末步。建议模板每类别 ≥1 条恒非空。
- 成功轨迹仅记录成功事实（outcome=success，归因/建议留空）；失败记录归因类别与改进建议恒非空。

## 3. 不变量

- L1 只规则化归因（关键词词表匹配，不调 LLM）；schema 层缺必填字段/未知字段/非法 outcome/failure 缺归因或建议一律 ReflectionSchemaError（ValueError）拒收
- 三角色逻辑分离：Actor 产轨迹 / Evaluator 按量规评估 / SelfReflection 产反思记录；接口协议化，满足协议即可充当
- 盘中零调用：工作日 09:30-15:00（Asia/Shanghai，固定 UTC+8）run_batch 即抛 IntradayReflectionForbidden（RuntimeError），无例外开关——反思全部发生在盘后离线窗口，不进盘中、不进下单热路径（§2.3/§5-5）
- 轨迹目录逐文件 json 读入，坏文件跳过不阻断批量（留痕日志，无有效轨迹不复盘）

## 4. 降级行为

- ERROR_CONTRACT：ReflectionSchemaError fail-closed 上抛；归因规则表为空 → ValueError（至少配置一类关键词）；EvaluationReport 字段不完整 → ValueError
- roles↔reflector 仅 TYPE_CHECKING 类型引用（防循环 import），运行时鸭子类型读字段

## 5. 边界（不做）

- 不做 LLM 自由文本反思（Phase 1 才评估）；不做 L2 同类任务归纳（N=5 累积，Phase 2）/ L3 跨任务（远期）；不做反思触发裁决（归 Phase 1 ReflCtrl 频率闸门）；不做证据链挂接（P2-4）；不做定时自触发

## 6. 测试

tests/intelligence/test_reflexion_phase0.py（28 用例，含同一任务分角色跑通全流程 P0-2 验收 + 盘中守卫）。
