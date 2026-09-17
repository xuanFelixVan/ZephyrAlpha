---
ttl: task_bound
completeness: draft
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-E1G-001（暂编号）车道G-全网搜索进货蓝图（⑥号车道）

## 定位

骨架 §1 工段⑥（策略合成）的点菜窗口之二：E1 第六车道。AI 层胃（L3 intel_harvester，
MOD-AUTO-L3-001）"只搜不入册"；本件把胃的收件箱消化产物转成带出生证的策略假说卸进货台账，
交 E2 预审把关。业务层消费 AI 层产出、不重建搜索能力——分工边界=骨架 §5。

## ALGO_FLOW

- I1: docs/_working/automation/inbox/intel-*.md（胃收件箱，文件名排序保确定性）
- A1: parse_inbox_entries（markdown→条目 dict；无链接畸形块跳过）
- A2: seen log 过滤（url_md5 级；LLM 失败/无 JSON 回包条目不标 seen=下一班自愈重试）
- A3: build_extraction_prompt（确定性：同条目必同 prompt，prompt_md5 进出生证）
- A4: OllamaChat 抽取 0-2 条/篇可检验假说（经 LSG；空数组=诚实无货，同样记账不重考）
- A5: 内容寻址去重（candidate_id=CAND-md5_12('E1G:'+假说全文)，跨批稳定）
- O1: data/strategy_intake/lane_g_candidates.csv（追加式台账）+ lane_g_seen_urls.csv

## 不变量

出生证机器写入（channel=G/batch=E1G-<ts>/birth_source 含原文 url）；进货不打分（判定权 E2/E4）；
本件不联网不抓取（抓取真源=L3）；台账只追加。

## 消费方

factory_intake_pipeline E2 幂等预审循环（intake_sources["G"]）；工厂图 FAC-E1G 节点；
E3 构造排产（passed 清单下游）。

## 欠账与扩展位

- 事件接线（收件箱落新班→自动触发消化）未挂=partial，挂 E1⑤"新数据入库自动触发"同批事件轨。
- 车道字母 F 被 F06 网格占用（仅代码车道），图节点补挂=2.4 接线跨线欠账，本件跳号取 G。
- 首班实弹观察：方法论论文多回"[]">0 产出是设计内诚实行为；扩量靠胃侧关键词与源注册表化（L3 扩展位）。
