---
ttl: task_bound
---

# 待 Owner 裁定/定夺项登记——C6 全自动管线班（2026-09-15）

> 按自裁定协议：本班可裁定的已全部裁定并施工（见各模块与裁定书）；以下为**协议允许外**的
> Owner 专属域（渠道选型/资源投入/外部依赖）或长尾登记项。每项含"不裁定的后果"=均为降级运行，
> 不阻塞管线主流程。

| # | 事项 | 现状与降级运行方式 | 建议动作 |
|---|---|---|---|
| ~~1~~ | **告警推送凭据提供——作废（裁定#323，2026-09-17）** | 本条被 09-15 通道裁撤裁定（#255：飞书/SMTP 通道彻底删除，通知=前端 promotion 页）超越却一直未回写——凭据请求与已生效裁定冲突 | ~~Owner 提供凭据即激活~~ → **作废，勿再提供凭据或重建通道**；通道去留如有新变化须另立新裁定 |
| 2 | **LLM 生成策略入口**（方案 §1 长尾） | 登记不施工：等 BacktestBench 级本地评估能力 | 评估器达标（准确率≥95%）后复议；先决=裁定书 ../../../01_policies_and_standards/policies/c3_translation_pipeline_ruling.md 的复认条款 |
| 3 | **wave-2 数据源**（方案长尾） | 登记不施工：等数据到位 | 数据落地后按管线既定事件自动进入现有链路，无需新施工 |
| 4 | **模拟盘 A 阶段 2026-12-14 首评** | 明令勿提前施工；sim_memo_monthly（MOD-BT-193）已按月产出建议书备料 | 12 月首评时以建议书为底稿，Owner 签字即可 |
| 5 | **C1 lane_b/lane_c 生成器自动执行** | 事件扫描+告警已接（scan_c1_c2_backlog）；生成执行留会话（LLM 成本+评估门） | 若 Owner 愿承担 LLM token 成本做无人值守挖矿，授权后按 wq-alpha-pipeline overnight 模式立项 |
| 6 | ~~他会话在途欠账上报~~ **已清偿（2026-09-15 终验）** | c4_fact_*.py 五件缺 D120 哨兵/契约字段——兄弟班已回填（"FACT 知识哨兵回填 git 创建日口径"），test_c4_batch_smoke 终验全绿（183 passed 批次内含） | 无需动作；此行保留作登记闭环留痕 |

## 本班已自裁定的裁定索引（备查）

- FDR 门 sim 不门登记（方案真源 §2.3/§2.5 分工，验收⑥回放 8/8 支撑）→ intake.py + acceptance6-replay.md
- 写入路径开启=fail-closed 存在性门控（Owner 原令"回放达标即视为复核通过"）→ intake.EVIDENCE
- 簇首=批内 p 最小者（"Sharpe 最高"人工先例的 p 值等价）→ intake.cluster_heads
- C3 不全自动（保持会话逐件）→ ../../../01_policies_and_standards/policies/c3_translation_pipeline_ruling.md
- 重资源事件（c4_batch_due）只经显式 drain；调度器唤醒钩子只消费轻 kind → pipeline_events.py
- KillSwitch 探针 fail-closed（全托管后安全优先，推翻旧版 fail-open）→ pipeline_events.kill_switch_clear
