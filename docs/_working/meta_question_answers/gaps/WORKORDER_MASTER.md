---
ttl: task_bound
completes_when: 各工单施工闭环或 Owner 裁定退役后随总包归档
title: fail 大缺口工单总册（WO-METAQ 系列·转总指挥分派）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-24
---

# fail 大缺口工单总册

> 每单含：缺口/精确配套（缺什么表·什么回填·什么接线）/evidence 链/工作量（S<50 行·M 单模块·L 跨域）/验收判据/门位。详细六向台账见各 gaps/PQ-XXXX_workbook.md。

## WO-001｜PQ-0004 degraded_check 关闸（S-M，代码+登记）
- 缺口：register 事件 283/283 全带 degraded_check 降级桩（evidence 全为"W4_source_line_registry_pending"）。
- 配套：①W4 源线谱 YAML 化落地（02 册→机器可读册）②src/zephyr/governance/meta_question/registry.py L446/L496 无条件降级桩换真检（依赖 0004 批落地）③复考。
- evidence：results/PQ-0004.json（审计 849 行中 283 条 degraded_check 与 283 register 一一配对）+ gaps/PQ-0004_workbook.md。
- 验收：新 register 事件 degraded_check 占比=0（复考 PQ-0004 pass）。

## WO-002｜PQ-0062/0102 JSONL 双轨（M，代码——已建成，待 0004/0006 落地收口）
- 缺口：JSONL 审计账全仓不存在；接线已在位（registry.py _write_audit→_append_jsonl，audit_jsonl_path=.runtime/chain_piling/meta_question_audit.jsonl）；存量已回放（1136 行核平）。
- 配套：①~~接线~~已挂 ②~~存量回放~~已落 ③对账器已建成（check_meta_question_audit_reconcile.py，q-0006 在队）——剩=0004/0006 落 HEAD 后对账器进排班例行化。
- evidence：results/PQ-0062.json、results/PQ-0102.json、gaps/PQ-0062_workbook.md、20_management_policy.md §2.2。
- 验收：JSONL 与 PG 审计逐日事件数差=0（复考 PQ-0062/0102 pass）。

## WO-003｜PQ-0099 状态分布健康带（M，机制——半门位）
- 缺口：283 问一次性应答后 answered=100%，破"单状态≤80%"帽（考后极性反转，已如实改簿）。
- 配套：①监控器已建成（check_meta_question_status_band.py，q-0007 在队；--regime campaign 参数化）②持续入题机制（新问题按批入库）③或 Owner 裁 regime 带宽数值（campaign 带当前占位 95 待裁）。
- evidence：results/PQ-0099.json + gaps/PQ-0099_workbook.md。
- 门位：campaign regime 数值 Owner 裁；选①②已施工。

## WO-004｜PQ-0012/0131 复权链重算（L，跨域管线）
- 缺口：kline_daily_hfq（bdpan_hfq 疑前复权基座）与 raw×adj_factor 系统性不对齐（抽检违例 45.4%；2024-01 复算 416/440 点违例）。
- 配套：①口径裁定=raw×adj_factor 为真源（PQ-0119 等八问已按此口径真算出稳定结论）②重算管线回写 712 万行 hfq 表（CH writer 角色，分片写入）③抽检器例行化（月度 50 只）。
- evidence：results/PQ-0012.json（违例 24,130/53,134）、gaps/PQ-0012_workbook.md。
- 门位：口径二选一与 712 万行重写属数据治理裁定，呈 Owner 批后施工；禁调容差。
- 验收：复权抽检违例率=0（复考 PQ-0012/0131 pass）。

## WO-005｜PQ-0018 板块口径映射（M+门位）
- 缺口：ig_node_company vs TQCENTER 成分 Jaccard 仅 13.5%≪80%（粒度结构性不同）；symbol 级重叠加 97.3%（格式零障碍，卡在名称/聚合规则）。
- 配套：①Owner 裁两口径主从（TQCENTER 为行情准绳）②节点↔板块映射册（名称对图谱词表精确命中仅 10/224，须 symbol 路由）③聚合规则设计。
- evidence：results/PQ-0018.json、gaps/PQ-0018_workbook.md。
- 门位：主从裁定 Owner。

## WO-006｜PQ-0064 链覆盖补挂（L，图谱管线）
- 缺口：A 档链 ig_node_company 覆盖率≥80% 的链占比 33.1%（剔已并入 69.6%）；未挂接活跃节点 1,148/3,335。
- 配套：①同花顺再跑（DS 账号在册）②stock_concept 候选回收 30.7%（(5+348)/1,148）③node_ref 补挂+写入器④2,225 合并节点收敛⑤零覆盖链 115 条（≤2 节点微链）退役提名。
- evidence：results/PQ-0064.json、gaps/PQ-0064_workbook.md。
- 门位：微链退役提名 Owner；其余可施工。

## WO-007｜PQ-0067/0078 io_edge 挂接+行业聚合（L，DDL+映射册，合批；含 0065 并案）
- 缺口：ig_io_edge 16,859 边 100% 挂零（表无 node 挂接字段，名称重放可挂率仅 4.1%/部门级 19.7%）；CKG supplies_to 聚合跨行业对不足。
- 配套：①DDL 二选一（ig_io_edge 加列 vs 旁挂册——Owner 选型）②153 部门两级映射册（95% 需人工确认，配豁免条款）③PQ-0065 已审计改判 infra 并入本单（一致率 1.23%≪70%，题面自带『低于则 CKG 降级为结构先验』条款——降级/换源/补救三选一裁）。
- evidence：results/PQ-0067.json、results/PQ-0078.json、results/PQ-0065.json、三 workbook。
- 门位：DDL 选型+人工映射确认窗+CKG 降级裁定。

## WO-008｜PQ-0068 产品同义词册（M，结构性预警）
- 缺口：CKG 产品边双端对齐率 0.15%≪30%；symbol 路由机械锚定 2,218 产品（4.6%，约 30 倍于现状）但机械上限约 5%≪30%。
- 配套：①产品同义词册（M）②PIT 语义写入规则③结构性结论：30% 阈值在该天花板下不可达，建议随 WO-007 并案裁（降阈值/退役/换源）。
- evidence：results/PQ-0068.json、gaps/PQ-0068_workbook.md。
- 门位：阈值或路线裁定。

## WO-009｜PQ-0072 质押事件版本载体（L，DDL+回填）
- 缺口：质押公告 vs edge_holding 报告期快照时序违规 5,238/110,690=4.73%≠0；同公告日版本命中仅 1.2%，换 pledge_start_date 口径后 44% 违规仍存（换口径无效实证）。
- 配套：①事件版本载体选型（新增 event_version 表 vs edge_holding 加 as_of 链）②DDL③回填 11.3 万条④与 equity_penetration 现行"质押按设计排除"口径（equity_penetration.py L50-51）的关系裁定。
- evidence：results/PQ-0072.json、gaps/PQ-0072_workbook.md。
- 门位：载体选型+口径关系裁定 Owner。

## WO-010｜PQ-0172 DS 册 coverage 补注（S，单行——待审批）
- 缺口：DS-AKSHARE-ALT coverage 未登记两断供子指数（known_data_gaps 两条已随 q-0001 落地 hash=0cd098e56b）。
- 配套：architecture_model/ 为保护路径（重大修改须 Owner 审批，无 CLI 逃生旗）；一行 coverage 补注已备好在工作区，Owner 批后单独一行批落地（或随任何获批批捎带）。时序依赖：须后于 q-0001（已满足）。
- evidence：gaps/PQ-0172_workbook.md §4。
- 门位：PROTECTED-PATHS Owner 审批（本批已按自裁拆出，不硬闯）。

## WO-011｜PQ-0025/0026/0125/0126/0127/0163 A06 资金流历史回补（M，数据管线）
- 缺口：c1_market.money_flow 仅 2026-06-01 起（533,575 行@23:09 时点，活库漂移），闭卷窗内零样本（sector_fund_flow 2026-09-15/market_fund_flow_daily 2026-03-27/block_trade 2026-08-07 同）。回填后可解 A06 族 6 条 insufficient。
- 配套：①tushare pro money_flow 接口全A 日频回补 2021-01-04~2025-09-09（窗内约 1,137 交易日（kline_daily 实测），全量约 560-600 万行）②入 c1_market.money_flow（writer 角色，分片）③哨兵+断档登记④复考 6 问（PQ-0025 事件研究/0125-0127 IC/0026 Chow/0163 U6 重放）。注：PQ-0161（口径版本存证）系 B 类载体问，回补数据不产生历史版本事件，其复考走建设需求清单同类载体，不由本工单解锁。
- evidence：results/PQ-0025.json、01_phase2_plan.md 数据清单#1、源线谱 SL-A06（DS-TUSHARE 在册）。
- 验收：money_flow 切点前覆盖 2021-01-04 起≥98% 交易日；6 问复考出 outcome。
- 门位：回补通道（tushare 积分）已运营在册，无新增门位；CH 写入走既有管线规范。
