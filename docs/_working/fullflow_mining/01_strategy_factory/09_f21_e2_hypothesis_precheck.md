---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F21 E2 假说预审逻辑门（防噪音总闸）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-091
map_node: FAC-E2
---

# F21 · E2 假说预审逻辑门

## 一、环节定义与边界
一句话：全厂防噪音总闸——候选想法→本地 qwen3:8b（经 OllamaChat/LSG）机制六问是非题预审（机制/前视/成本/可证伪/同义反复/边界）→verdict 三态落 c1_backtest.hypothesis_precheck（只追加）；讲不通的想法在此死，不花回测算力。
上游供料=D/B/C/C2/G/I 六车道进货台账；下游消费=E3 构造（auto_construct 只认 precheck_passed 的 C/C2；hypothesis_translator 只认 D/B 的 passed）+race 计分板+E9 归因回灌（法定反馈边 FL1 终点）。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | 六源 csv（load_candidates 校验 birth 四列 :170-180）；CH 实测各渠道存量：D 40（唯一 22）/B 4（蒸发前 15）/C 16/C2 8/G 0/I 10 |
| 下游消费 | **c1_backtest.hypothesis_precheck 实测 58 行**（14 批，09-14~09-19）：13 passed/26 rejected/19 deferred（全 defer_llm_unreachable）；E3 侧 consumed=6（translated 5+constructed 1）；DDL-as-Code 真源=schemas/categories/backtest/backtest_hypothesis_precheck.py |
| 自动化触发 | 无常驻（manual；factory run 自动接续=唯一自动面）；deferred 重审无任何通道（见堵点①） |
| 真源与注册表 | MOD-BT-091 在 path_ownership_map.yaml:15963,16222；tests/backtest/test_hypothesis_precheck.py 在盘；图9 FAC-E2 build_status=partial；方法论底座=FaVOR+Harvey-Liu-Zhu t≥3.0+Owner 先验过滤器笔记（algo_note） |
| 门禁与质量尺 | verdict/verdict_reason 代码生成禁手填（INVARIANTS）；理由码封闭枚举（6 reject+3 defer）；reject 理由码不可映射→转 defer_low_confidence 不落脏码（:121-123）；LLM 异常→defer_llm_unreachable 不冤枉想法；低置信阈值 0.6；台账只追加；考试权留 E4（本门只做经济学预审） |
| 当前运行状态 | **绿（判定通路）/红（滞留面）**。最近一次真实运行=**2026-09-19 10:00（E2-20260919-100054：I 渠道 10 条全 defer_llm_unreachable）**；09-19 后零新判定；E2 漏斗总览：D 8 pass/15 审、B 4 pass/15 审、C 1 pass/10 审、C2 0 pass/8 审、I 0 pass/10 审 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 六问 prompt build_prompt（确定性） | scripts/backtest/hypothesis_precheck.py:80-95 | built |
| 强解析 parse_reply（JSON→关键词兜底→defer） | 同上:98-145 | built |
| 单条预审 precheck_one（异常→defer_llm_unreachable） | 同上:156-167 | built |
| 幂等过滤 fetch_prechecked_ids | 同上:183-191 | **built 但有语义缺陷**（全表 DISTINCT 含 deferred→滞留） |
| 落台账 insert_verdicts（writer 通道） | 同上:194-211 | built（58 行实证） |
| 主流程 run（读→过滤→审→落→汇总） | 同上:214-254 | built |
| 台账分布 cmd_status（只读） | 同上:257-269 | built（本次挖矿即用其复核） |
| deferred 重审通道 | — | **missing** |
| E2 结果看板/滞留告警 | — | missing（过审≠排产无可见性） |

## 四、堵点与病灶
1. **【P0】deferred 19 条永久滞留**：现象=I 渠道 10 条（09-19）+D 5+C 2+C2 2（09-15 LLM 不可达期）全 defer；fetch_prechecked_ids 用 `SELECT DISTINCT candidate_id`（全 verdict）幂等跳过→deferred 行永不再审，与 :190 注释"deferred 可重跑语义"不符（仅 CH 不可达全量重审时才意外达成）；修法=幂等 SQL 改 `WHERE verdict != 'precheck_deferred'`（1 行+测试）；0.5 天；本车道可修。
2. **head(limit) 截取语义**：load_candidates `df.head(limit)` 取文件头非新增——编排默认 limit 10 时，堆积批行（D 40 行唯一 22）挤占名额；head 语义与"消费**新增**候选"（factory 编排 :126 注释）不符；修法=过滤已审 id 后再截断（顺序对调）+去重；0.5 天；本车道可修。
3. **LLM 不可达窗口无告警**：09-15/09-19 两波 defer_llm_unreachable 共 19 条，无告警无重试——Ollama 服务健康检查不进任何巡检（M5 健康总表无此项）；修法=defer 率超阈值夜批告警；0.5 天；跨 M5。
4. **判定权单点（qwen3:8b 一票制）**：E2 是"讲不通在此死"的生杀门，但单小模型单温（0.0）判定——reject 无复核、pass 无第二意见；图9 FaVOR 参照未落地（假说拆可观测条件+分布证据先验检查）；修法=P2：低置信带双模型复核（qwen3+deepseek-r1 消融档已在 158 验证可行）；2-3 天；待裁（涉及判定权设计）。
5. **拒绝质量未标定**：26 reject 无抽样复核记录（误杀率未知）；修法=Owner/人工抽 10% reject 复核一轮并留档（与 E6 判死行同构）；0.5 天/轮。

## 五、提速与合并机会
- cmd_status 已是单命令复核面；race 计分板复用同表——无重复。
- E2 六问与 C2 两段式机制门（build_mechanism_prompt 三问）语义重叠面大：机制三问是六问第 1 问的深化版——可把三问文本升格为共享真源（一处改两边生效）；0.5 天；防漂移建议。

## 六、自审闸三态
- **三态结论：partial**（判定通路 built 且 58 行实战；deferred 滞留+limit 语义+无告警三伤）。
- **差什么才算 built**：①deferred 重审通道修复+19 条重审完成；②幂等/limit 语义修正；③（口径裁后）reject 抽检一轮留档。①②完成即可升 built。

## 七、复核命令
```bash
python scripts/backtest/hypothesis_precheck.py status     # 58 行分布（本册核心证据）
# 批次史：SELECT precheck_batch,birth_channel,verdict,count() FROM c1_backtest.hypothesis_precheck GROUP BY 1,2,3 ORDER BY 1
sed -n '183,191p' scripts/backtest/hypothesis_precheck.py  # 幂等缺陷现场
python -m pytest tests/backtest/test_hypothesis_precheck.py -q
```
