---
ttl: task_bound
title: 清洁+补考+E2E冒烟战役·交付报告（终稿）
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918
date: 2026-09-18
status: final
---

# 清洁+补考+E2E 冒烟战役 · 交付报告（终稿）

> 战役令：Owner 2026-09-18 通宵令（第二班）——③清洁三件（三层调查后执行）+⑥16 条补考+端到端模拟盘 100 股桥测试。
> 组织：总包 st-cleanexam-20260918 + 挖矿/施工代理 A/B/C（B 两度撞速率限阵亡由总包亲挖；A/C 三轮再生奋战）。
> 执行模式：先挖矿挖干骨架（六向台账+自审闸三态）→封矿→施工；线内先挖后干、线间并行流水。

## 端到端结论（先行）

1. **ENV1 清洁三件：执行完毕**。10 张空壳 CH 表 DROP（回滚 DDL 快照在案）+125 件 CAS tmp 清除（tar 归档+mtime 守卫）；**三层调查证伪基线 1 件**——db bak b/c"纯重复"前提不成立（md5 实差 14,239 字节），按裁定 #328 自身条款改判**保留留档**。验证链全绿（MV/字典深引用 0、tasks.yaml 零引用、metrics flush、app_panel 导入、data_inventory 重跑零差异）。
2. **ENV2 补考：16/16 全完成（16 ok/0 error），0 放行档**（15 不通过+1 存疑）。存活者 17 名单与 a_reexam 主结论**零变化，经独立复考二次加固**。阻塞机理坐实=akshare_provider 表清单全局校验连坐，非数据缺失；9322ce6710 解除后单条 3 秒冒烟实证。
3. **ENV3 E2E：链路全通（LINK PROVEN）**。09:27 实弹：510300.SH BUY 100 LIMIT@4.07（跌停价）→ orders_sim.csv 双指令行铁证（下单+撤单）→ HTTP 快路径 → 柜台收单 sysid 回填 → SUBMITTED → cancel → **CANCELLED** → Deal 零成交（如设计）→ execution_report 0 行=断点 E4 如实暴露。模拟账户 8886156677 双重断言全程在岗，零实盘接触。
4. **裁定登记闭合**：#327（①②④⑤追认，kimi-audit 执行）+#328（清洁附条件批准）+#329（补考排期执行）全部入册，零撞号。

## 关键数字

| 项 | 值 |
|---|---|
| 清洁删除 | 10 表（全 0 行）+125 tmp（22.1MB，全量 md5 对比） |
| 清洁保留 | db bak b/c（证伪改判）+范围外中风险 8 件/死配置 4 件（待裁） |
| 补考 | 16/16 ok；15 不通过+1 存疑；0 放行档 |
| E2E | 24 环普查/6 断点；段一 7 PASS+1 FAIL（自愈）；段二全生命周期 CANCELLED |
| 提交 | ENV1=6e1804e6cb；ENV2=4e7049752115（message 误贴 ENV3 文案，内容正确如实记录）；ENV3=dc63e8e6bf3b+本批；裁定随 kimi-audit 6baff3162a 入 HEAD |

## 挖矿→施工全过程

- ENV1：作业簿+verdict CSV×2+执行计划（A 代理，自审闸=施工）；总包按计划五环执行（复核→冻结→执行→验证→回写）。
- ENV2：总包亲挖六问（B 代理速率限阵亡）；免疫区批跑+备份种子恢复；结果报告落盘。
- ENV3：C 代理 24 环普查+两段式设计（自审闸=可封矿）；总包执行段一（零委托）+段二（实弹模拟单）。

## 事故与处置（全部如实）

1. **tdchain-sweep 会话多轮物理清扫** docs/_working/clean_exam_e2e/（untracked 直删不进 stash）：A/C 产物三轮再生（字节级自验），ENV2 结果靠 .runtime/tmp 逐行备份零损失；对策 R5=再生即 commit+运行态入免疫区。
2. **账户速率限 [1302]**：三代理并发打满共享额度，A/B 阵亡——R1 降并发+总包亲挖。
3. **提交通道**：直连两度被他会话在途件连坐（VOCAB-CHAIN/SSoT）→队列正门；CREATE-GUARD 三度补 token；瞬态 claim 过期→网关 --claim-only 配方。
4. **诚实瑕疵**：4e7049752115 的 commit message 误贴 ENV3 文案（复制粘贴错误），文件内容正确（ENV2 四件）；smoke_test_design.md 我声称已恢复实际未落地——C 代理自查补齐并报备。

## 红蓝对抗与循环检查（连续两轮 0 问题）

- R1：ENV1 删后独立复验（换查询路径/tzba k 残留=范围内有数据备份按设计保留/tasks.yaml 零引用/tmp 复扫 0/四连接健康）✓
- R2：深引用攻击（MV/字典 0 命中）✓；补考驱动算法零改动实锤（diff --strip-trailing-cr 仅头注）✓；tmp 复查=scripts/ 第四泄漏点 2 件新残留（记长尾）✓
- 红蓝攻击记录：组队检测法缺陷（文件 ack 对 HTTP 失明/Order 导出不含已撤单）——均为检测法问题非链路故障，事后取证补证。

## 遗留清单（诚实，非待裁——均有明确归属）

1. **断点 E4**：execution_report 生产者接线（表/契约/build 全在，缺生产调用方）——编排器"出手"前置工单，下一班。
2. **smoke 检测法升级**：ack 通道分流+Order 导出语义——骨架可复用为回归冒烟（设计 §8 既定）。
3. **长尾 L1-L4**：CAS tmp 治本（metrics.py 补 unlink 等）+scripts/ 第四泄漏点——下一轮清洁批。
4. **范围外保持原状**：中风险 8 件/疑似死配置 4 件/bak 三件/_working TTL/sessions——待 Owner 决赛窗口。
5. 16 条补考的前置缺陷（market_commodity_futures_main 注册）已被数据班 9322ce6710 解决，本班实证——无遗留动作。
