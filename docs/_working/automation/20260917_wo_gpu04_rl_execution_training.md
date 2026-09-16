---
ttl: task_bound
completes_when: RL trainer 施工完成并通过 B-007 审批启动真训练，或工单被否决归档
---

# 工单 GPU-04：RL 执行环境训练（B-007 门位工种）

> 状态：DESIGN-ONLY（env 骨架在位，trainer 不存在，真训练被 B-007 人工闸锁）｜风险：高（宪章 §4.2 人工审批域）
> 使命来源：docs/_working/automation/20260917_automation_linkage_plan_v1.md §2-Q2 路 b

## 1. 就绪度证据

- 蓝图：docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md（MOD-XS-008）——"环境+硬边界+契约，不真训"。
- 代码骨架：src/zephyr/ex_sor/core/rl_exec_env.py（gym 式 reset/step，reward=负 implementation shortfall）+rl_exec_boundary.py+rl_exec_contract.py；**无 torch 依赖、无任何调用方**。
- 真训练（PPO/TD3 等）明确属宪章 §4.2 **B-007 人工审批闸门**——本工单只做施工准备，不启动训练。

## 2. 施工步骤（获 B-007 批复后）

1. trainer 施工：torch RL 算法选型（建议先 TD3——连续动作=下单力度，样本效率高于 PPO）；env 包装成 torch兼容向量化环境；checkpoint/早停/种子纪律。
2. 离线预训练数据：replay 流水（local_replay 产物）做 behavior-cloning 预热，再在线微调，防冷启动爆奖励。
3. 训练窗：gpu_default 组登记（建议周日长窗，240min 起步）；reaper 白名单登记。
4. 评估门：训练产物只进影子评估（模拟盘对拍 implementation shortfall vs 现行执行算法），**不直接上实盘**。

## 3. 验收标准

- [ ] B-007 审批记录在案（裁定登记）
- [ ] 训练曲线+checkpoint 治理可复现（种子固定）
- [ ] 影子评估对拍报告产出并报 Owner

## 4. 红线

- 本工单**不含**任何训练启动动作；B-007 未批前只允许 trainer 代码施工与离线评估。
- 执行域边界（rl_exec_boundary）约束不可绕——动作空间越界即 fail-closed。
