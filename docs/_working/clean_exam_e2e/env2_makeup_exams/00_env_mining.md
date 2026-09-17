---
ttl: task_bound
title: ENV2 补考线挖干作业簿——16 条 error 策略阻塞链与重考
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918
date: 2026-09-18
status: done
---

# ENV2 补考线 · 挖干作业簿

> **真源**：docs/_working/sharpe2_prep/a_reexam/reexam_results.csv（16 条 error 行）；提交 9322ce6710（数据班补注册+建表）；本班实证。挖矿代理 B 两度撞速率限 [1302] 阵亡，总包亲挖（R1）。
> **事故注记**：本簿随目录两度被 tdchain-sweep 清扫，现件系总包自上下文原样再生（内容零变化）。

## 0. 挖矿日志

- 母节点：16 条 error 策略补考（裁定#329 已入册）。
- 单条冒烟 03:11 实证（3 秒 ok）；批跑经两次清扫杀进程后 04:45 以免疫区运行态 resume。

## 2. 六问逐答

### Q1 阻塞机理
- 抛错点：`src/zephyr/data/table_registry.py:147`——`KeyError: category_id 'market_commodity_futures_main' 未在 business_data_categories.yaml 注册`。
- 传播：16 条策略源文件本身零商品引用（grep 证实）；炸点在 `src/zephyr/data/implementations/akshare_provider.py:333` provider 表清单全局声明+真源存在性校验→任一策略考试实例化该 provider 即全局炸（与策略是否用商品数据无关）。

### Q2 9322ce6710 落了什么
- 真源注册 business_data_categories.yaml:2994（→table=commodity_futures_main）+:3010（commodity_spot_price）；provider 接线 :162/:333/:725/:6385；CH 两表已建（实查 count=1）。

### Q3 缺口清单
- 已被数据班闭环，本班零补动作。实证：单条冒烟 CAND-12286499cb19 3 秒 ok（oos_h2=0.9506）。

### Q4 C1 冲突裁定
- 无冲突：本线零文件编辑；未触碰 C1 三文件。

### Q5 重考机制
- 驱动=.runtime/tmp/cleanexam_makeup_reexam.py（st-sharpe2a 驱动路径重定向副本，算法零改动；R5 后 RESULTS 迁 .runtime/tmp 免疫区）。
- 结果=env2_makeup_exams/makeup_reexam_results.csv（批终自免疫区复制落位）；逐行备份=.runtime/tmp/cleanexam_makeup_backup.csv。
- 口径=WFA 8 折同款+H2 真成本+官方 DSR/门控（N_REEXAM_TRIALS=16）。

### Q6 排期
- tonight 批进行中；完成后结果并入补考结果报告回写本簿 §4。

## 3. 六向台账（摘要）
上游=error 16 行+注册✓+两表✓；下游=结果 CSV→补考报告→a_reexam 勘误附录；依赖=9322ce6710 ✓；阻塞=无；风险=病态慢族耗时（驱动有退避兜底）；验收=16/16 出行。

## 4. 结果回写（批完回填）
ok/error、过严格尺条数、对存活者 17 的影响——（待回填）

## 自审闸三态：**挖干**
