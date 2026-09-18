---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——信号响应三件套（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：信号响应三件套（P23）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM 节点: TDM-E-L2-05-2
- 生产调用方: sector_conduction（P24）/ daily_condition_sensor / strategy_pipeline/daily_gate_snapshot（grep 实证，活件）
- 测试文件: tests/signal_ashare/sector/test_sector_gate.py（合批 68 passed）

## 1 对象快照
MOD-SIG-026 supplement（169 行）：三级准入 gate v2.1 + 水温 5 档响应表 + RRG 象限过滤，纯查表函数。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 水温表 5 档权重/阈值/过滤器与 spec §3.1⑪ 一致；RISK_ON×CONSENSUS_CLIMAX 双重抑制 0.5×0.5=0.25 实现正确；CRASH 用 1.01 阈值实现全拦（score∈[0,1] 不可达）——**防御洞：score>1.01 的上游脏值在 CRASH 反而可放行**（阈值语义倒置） | :82-88,141-150 | P3 | 传 score=1.5 + CRASH 看 gate_pass=True |
| A 边界 | 未知水温 fail-closed ValueError；未知 rrg_filter→False（fail-closed 放行方向正确=拦截）；retained_sectors None/给定两语义分支均有文档（:133-135） | :106-109,169 | 已查无 | 传 "HOT" 应抛 |
| A 语义 | retained_sectors=None 退化分支：level2≤score<level3 即 SECONDARY（不看板块归属）——与给定分支（须 sector∈retained）语义不同，混用时准入口径静默变化（文档已声明但调用方易踩） | :143-147 | P3 | 两种调用形态对拍 |
| B 上游 | score 契约∈[0,1] 由调用方保证（无校验，CRASH 洞同源）；top_sectors/retained 集合注入无来源锁 | :128-134 | P3 | — |
| C 下游 | 三消费方实存；daily_gate_snapshot 消费=盘前闸门快照——水温/门槛错档直接驱动当日准入；爆炸半径=全板块信号准入 | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | RRG_FILTER 字符串常量与 P16 RRGQuadrant 枚举字符串硬耦合（"IMPROVING"/"LEADING" 字面量跨文件）——枚举改名静默失配（str 相等比较绕过类型检查） | :166-168 vs sector_rrg.py:70-77 | P3 | grep "IMPROVING" 字面量计数 |
| E 对抗 | 五问：①无吞异常 ②fail-closed 方向（未知的过滤=拦截）正确 ③无监控面 ④纯函数幂等 ⑤水温档由上游判定（本件不判，分工清晰） | 全文件 | 已查无 | — |
| F 新鲜度 | 受阻/不适用：准入门槛/水温响应为项目 spec 自定义规则表（v2.0→v2.1 阈值演化有 spec 内史），无外部对照对象 | — | — | — |

## 3 SOTA 对照
受阻/不适用（项目自定义规则表）。

## 4 缺陷清单
1. P3 CRASH 阈值 1.01 语义倒置洞（score 越界脏值可放行——建议 CRASH 硬 return False 不走阈值）。
2. P3 retained_sectors 两形态语义分叉（易踩）。
3. P3 RRG 象限字面量跨文件硬耦合。

## 5 挂起疑问
- v2.1 阈值 0.60/0.80 初拟待 G05 回测（自声明）——标定欠账族。

## 6 完备性自评
六轴全查（全文件 169 行逐行）。无长尾。
