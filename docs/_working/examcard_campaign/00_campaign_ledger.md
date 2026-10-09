---
ttl: task_bound
title: 考试卡+断言治本双战役作战台账（st-examchief-20261009）
created: "2026-10-09"
sid: st-examchief-20261009
family_id: EXAMCARD-CAMPAIGN
---

# 作战台账（随进展追加）

## 车道状态板（2026-10-09 21:00 快照）

| 车道 | 状态 | 凭据锚点 |
|---|---|---|
| W1 F06 治本 | ✅根因钉死+修复+蓝探针绿；彩排批A 计算中（py-spy 实证 active，非挂起）；正式验收=10-11 周六窗 | 01_w1_f06_root_cause.md + w1_evidence/ |
| W3 骨架生成器 | ✅核心闭环：186/186 覆盖、重跑零 diff、only-add+手工卡保护（10/10 测试）；户口五合一已办 | MOD-BT-241；tests/backtest/test_generate_exam_card_skeleton.py |
| W4 20 卡预注册 | ✅20 张预注册卡落盘（看数前冻结，零数据窥视）；**分数面阻塞**：前置② dexp TI 读侧确定性修复未落 HEAD（argMax 第三路 git log 零命中）——如实登记阻塞非跳过 | exam_cards/entry_flow/L1/*__calibration__0[2-8]*.yaml |
| W5 confidence 闭环 | ✅裁定#501 冻结 v1 判据+回写器落地（13/13 测试）；实弹演示随 W4 首分 | MOD-BT-242；裁定#501 |
| W6 Qoder 云模型 | ✅实弹达成：LLMGateway 增 qwen provider（G1-1 内收零新模块），经 LSG 全链真云调用一次（qwen-flash 1250ms"链路正常"） | src/zephyr/infrastructure/pipeline/llm_gateway.py |
| W7-① fexam 搬家 | ⏸避让延迟：横跨 4 本热册（3 本可能总队在持）——总队队列落地后执行 | 本表 |
| W7-②③ | 候补（dataset_registry 立项/lockfile 钉扎） | 方案 §7.5 净零候补位 |
| F1 lookup state | 🔨子代理施工中 | agent 报告待回 |
| F2 边界登记 | ✅offzone_retrieval_boundary_sop.md 落盘（裁决 b 案） | library_sop/ |
| F3 触发面 | ✅trae_065 v1.1.0+裁定#499 | rules/trae_065 |
| F4 挖矿 SOP | ✅mining_sop_policy v1.7.0 §7.5 | mining_sop/ |
| F5 复盘入册 | ✅CASEBOOK-010 开册+case 0 首录（裁定#500）+prereg 三元组结构落地 | casebook_registry+asset_assertion_cases.yaml |
| W2 GPU 摊销 | ⏳等批A 完成取真全引擎 s/格（热点复测①）；L1 实测已大幅跑赢 L2 设计预期（0.061-0.606s/格纯 pass vs 推演 11.7s），若全引擎 ≤3.5 则按架构册 §六停手条款登记判定，不为饱和而饱和 | p1_wiring_benchmark.md |

## 排队与提交账

- q-20261009-st-examchief-20261009-0001（W1 件 7 文件，含 token 册补 3 条 quant_methodology 修复）已入袋，传送带消化中。
- 待投批次：W3 生成器+186 卡册+2 测试件；W4 20 卡；W5 回写器+裁定#501；W6 llm_gateway；F 文档批（F2/F3/F4/F5+裁定#499/#500）。
- token 工具 HEAD 基底自检在 W1 件落地前会拦（补回 3 条在 W1 批里）——投递序=先等 W1 落地。

## 阻塞与升旗

1. W4 分数面/前置②：dexp argMax(ingest_ts) 第三路未落 HEAD——20 卡分数建立在任意版本指标上的风险未排除，禁开考分数面。
2. W7-① 热册避让：等总队（st-chiefc）队列消化。
3. 批A 时长：全引擎旧路径 ~35s/格推算，census-extend 剩余格数决定收窗时点；不干预（他会在途 CH 负载为 main 因素，reaper keep 在册）。

## 追记（2026-10-10 早）：主袋清障动作账

- st-fig16-20261005（10-05 老会话，零活进程实证）的暂存件 panorama_alignment_gate.py（+25/-13，63 行 `__all__` 缺 Final 触发 MUTABLE-CONST-WITHOUT-FINAL 全局门）封死全仓直落通道。
- 处置=git restore --staged 单文件退栈（**三态验证零丢失**：worktree==index，内容全留工作树，其回来 re-add 即可恢复）；未代改其代码（§3.4）；本条即登记。
