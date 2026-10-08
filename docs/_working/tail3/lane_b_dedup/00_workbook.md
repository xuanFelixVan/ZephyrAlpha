---
created: 2026-10-08
session: st-t3b-dedup
ttl: task_bound
title: 车道B两处重复病收敛作业簿（tasks去重保正身+categories交叉验证+防重门红蓝）
completes_when: tasks.yaml cohort_ledger_daily 去重保正确版+categories 册去重收敛（完全重复并/同 id 异内容收敛胜者）+两防重测试落地+注入攻击红蓝全拦+两轮检查零问题
---

# 车道B·两处重复病收敛 作业簿（st-t3b-dedup）

> **Owner 已批裁定原文**：「立项，机械去重+判重测试钉死」
> **任务**：①tasks.yaml 定位 cohort_ledger_daily 双条目差异→去重保正确版（机械不可判=自裁定留分析过程）；②business_data_categories.yaml 100+ 重复 category_id 全集清单→完全重复直接并；同 id 异内容按「最新 mtime+被引用多者胜」收敛，败者独有字段并入胜者再删；③tests/ 新增两册各一防重门（同键唯一断言，tmp_path 隔离）；④红蓝：构造重复注入攻击→防重门必须拦；两轮循环检查零问题。

## 1. 挖矿台账（六向，每向≥1 发现或"已查无"）

| 向 | 发现/已查无 | 证据锚 |
|---|---|---|
| ①上游（两真源的生成者/写入方） | **两册均手工维护非机生**（tasks.yaml 头注自述"任务清单真源（蓝图 §6.2+§4.4）"无 [GENERATED] 标注；categories 头注"唯一真源…新增品类=加一条YAML记录"）。tasks 双条目成因=平行会话重复登记：residual 55033fd5（09-22 04:22）先登 daily_capital 版→emomine a9818b2e（09-23 02:23）后补登 daily_kline 版，其 recon（emotion_line gap G2"无任务条目"）早于 residual 落地→误判缺失。dup 系已知在案：fig12 WB12-49 点名"全仓唯一重复 task_id"、EXEC1 报告"他会话在途不代修" | `git log --format="%h %ci" -1 55033fd509/a9818b2ef`；docs/_working/emotion_line/gap_list_and_construction_proposal.md:21；docs/_working/map_build/fig12_datachain/00_skeleton.md:93；docs/_working/fullflow_mine/wiring/EXEC1_quickwins_report.md:86 |
| ②下游（消费者/加载器） | tasks.yaml→scheduler.py load_config（list 直载**无判重** :1465-1472）+按 schedule 过滤（:703+）+backfill_checker._load_tasks_yaml（:260）+dashboard api_server.py:1744（展示元数据"首任务为准"）；categories→table_registry.py TableRegistry（真源路径 :66-68，table() fail-closed KeyError，validate_tasks_yaml WARN :183-193） | src/zephyr/data/scheduler.py、src/zephyr/data/table_registry.py、src/zephyr/data/backfill_checker.py、src/zephyr/frontend/dashboard/api_server.py |
| ③算法/机制（去重规则与判重点） | TaskQueue 双语义钉死双触发实锤：未知依赖跳过（task_queue.py:123-124）/跨批依赖视为已满足（:150-162 get_ready_tasks）→daily_kline 变体 16:30 照跑（早于当日资金原料 18:00 落库）、daily_capital 变体 18:00 同批 DAG 等齐 3/4 dep；load_tasks 字典后者覆盖（:97）。trading_day_only 为被消费行为字段（scheduler.py:726 非交易日 skip）。判重规则=同键唯一断言（task_id/category_id） | src/zephyr/data/task_queue.py:97,123-124,150-162；src/zephyr/data/scheduler.py:726 |
| ④后端（YAML→DB 同步面） | categories 无 DB 写回同步器（TableRegistry 只读 YAML→内存，已查无 apply/sync 工具）→去重零 DB 侧动作；cohort 表数据由 cohort_daily_writer 直落 CH，ReplacingMergeTree 同键幂等已吸收双触发的数据面（无双写脏数据，仅双算浪费+16:30 草稿行为） | grep sync/apply 工具=已查无；src/zephyr/alt_data/cohort_daily_writer.py |
| ⑤前端（展示面） | dashboard api_server.py:1744-1748 读 tasks.yaml 建 {全表名:元数据}（"首任务为准"）——去重前 kline 变体居前展示 16:30 档（与实际执行语义不符），去重后展示 daily_capital 正身；categories 前端零直读（grep 已查无） | src/zephyr/frontend/dashboard/api_server.py:1310-1311,1744-1748,1818 |
| ⑥数据字段（重复全集清单/分桶） | tasks：1 组双条目（cohort_ledger_daily），字段级 diff=schedule（daily_kline vs daily_capital）/source 注释/description（互有独有）/trading_day_only（败者 kline 版**无**、正身 capital 版**有**）。categories：HEAD 338 条、116 组重复、**全 116 组完全重复（逐字段 JSON 规范化比对）、0 组同 id 异内容**；每组分桶脚本 .runtime/tmp/tail3/census_categories.py（仓库外，禁入）→census_result.json；staged 工作区 0 残留重复（本车道挖矿时 222 条，挖矿期间 G4 飞行中 +1=223） | .runtime/tmp/tail3/census_result.json；src/zephyr/data/config/tasks.yaml HEAD 3450/3862 |

挖干裁定（自审闸三态）：**干**——去重属同键收敛非退役语义，116 组 categories 重复与 tasks 双条目均无整段功能废弃；无 OPEN_QUESTIONS 级退役组。

## 2. 施工记录

- [x] tasks.yaml cohort_ledger_daily 去重（差异分析：schedule/注释/description/trading_day_only 四处；**正确版=daily_capital 变体**）
  - **裁定过程（机械判据三轴）**：①消费方兼容性——Owner 批 wiring_proposals §A 明文"挂 daily_capital 尾部"+cohort_daily_writer.py:6 代码头注"daily_capital 档"+四 dep 三条同批 DAG（kline 版 dep 全跨批=16:30 抢跑当日未落库原料）→capital 胜；②最新 mtime——两变体同commit(a9818b2e)打平，但最后有意维护（dloop 收敛+trading_day_only 补齐）落 capital 版→capital 胜；③被引用多者——代码头注+Owner 批提案引 capital 档 vs 仅 data_acquisition_flow.md 镜像行引 kline→capital 胜。三轴全指向 daily_capital。
  - **staged 在途改动（01:26 无主）保错变体**（删 capital 留 kline）→本车道**反转换保**：删 kline 重条（含其 section header），恢复 capital 正身于原位（含 residual TC-08+dloop 收敛注释块全须），并恢复被误删的 option_daily_stats 7 行注释块；败者独有信息并入（description 追加 WORK-ORDER-5 留位/行语义/防双写；schedule 行补 PIT 注记；source 行补本地结算注记；symbols 行补聚合注记）+去重注记 5 行留痕。
  - before=276 行任务（1 组重复）/after=275 行任务 0 重复（yaml.safe_load+Counter 断言过）。
- [x] categories 全集清单（**完全重复=116 组/同 id 异内容=0 组**；HEAD 338 条→收敛 222 条）
  - staged 在途改动（G4 st-datasop-20260930 活跃在飞：claim 02:20+写盘 03:11，心跳 exited 系旧进程、新写盘实锤存活）=去重+规范化重排，**经本车道逐组交叉验证 116/116 全部正确**（完全重复组保任一 occurrence 等价）→本车道对 categories **零编辑**（禁碰飞行中队列 staged 面，RULE-WORKTREE HELD-OVERLAP 不硬闯），收敛由其 staged 态承载。
- [x] categories 收敛（胜者/败者合并明细：无涉——0 组异内容，无败者字段可并）
- [x] 防重测试×2（tests/data/data/test_tasks_yaml_task_id_unique.py + tests/data/data/test_business_data_categories_unique.py，先 grep 确认无同名；真实册只读钉回归+tmp_path 注入攻击面；tests/ 豁免 token）
- [x] 红蓝注入攻击（见 §3）
- [x] 两轮循环检查零问题（见 §3）

## 3. 红蓝战果

**7 用例全绿（两册 7 例：真册钉 3+注入红 2+合法绿 2），两轮零问题**：

| # | 用例 | 面 | 结果 |
|---|---|---|---|
| 1 | 真册 tasks.yaml task_id 全仓唯一断言（275 任务） | 只读回归钉 | 绿（去重后 0 重复） |
| 2 | 真册 cohort 正身字段锚（schedule=daily_capital+trading_day_only=True） | 只读回归钉（裁定防翻案） | 绿 |
| 3 | 真册 categories category_id 全集唯一断言 | 只读回归钉 | 绿 |
| 4 | 重复 task_id 注入（tmp_path，同键双条异表）→必拦 | 红攻 | **拦**（捕获 ["dup_task"]） |
| 5 | 重复 category_id 注入（tmp_path）→必拦 | 红攻 | **拦**（捕获 ["dup_cat"]） |
| 6 | 合法唯一键注入 tasks 形态→放行 | 绿 | 放行 |
| 7 | 合法唯一键注入 categories 形态→放行 | 绿 | 放行 |

**第二轮循环检查（更深红证+生产消费器交叉）零问题**：①反向红证——判重器对 HEAD 重复态咬合：tasks 捕获 cohort_ledger_daily、categories 捕获 116 组（证明门真咬非恒绿）；②TableRegistry.validate_tasks_yaml（生产交叉校验器）对去重后真册 2 警告=HEAD 基线同款既存（cftc_positioning/gold_etf_holdings 未注册，非本批引入，录观察）；③ruff check/format 过闸，格式化后复跑 7/7 绿。

## 4. OPEN_QUESTIONS

1. categories 册当前 staged 面（去重+规范化）属 G4 队列（st-datasop-20260930 [G4 次优先三项消费接线]）在飞工作，其落地归属与提交时机由总包/G4 裁定；本车道防重测试已对其收敛态钉死回归（0 重复断言），G4 若再叠加新条目须保同键唯一。
2. margin_trading_incremental 在 nightly_financial(22:00) 档、cohort 四 dep 中三条在 daily_capital(18:00) 档——跨批依赖"视为已满足"口径下 cohort 结算不等 margin 当日数据（§A deps 照抄的既知设计），如需强一致可另立单项（非本裁定范围）。
3. 观察项（非本批引入，呈总包）：tasks.yaml 有 2 任务表未在 categories 册注册（cftc_positioning_refresh→c1_market.cftc_positioning、gold_etf_holdings_refresh→c1_market.gold_etf_holdings，TableRegistry 双真源漂移 WARN，HEAD 基线同款）——若 Owner 认为应补注册可另立小单。
4. **本簿 git 落地阻塞登记（15+ 次尝试后按升级协议跳过）**：CREATE-GUARD 判「无 creation_token」但 token 实况=worktree+index 双层持久在场（CAS 落盘 OK+git add 后 `git show :<registry>` 可见）。白盒诊断：anchor_main_root/解析/匹配三环节全绿（`yaml.safe_load` 见条目、路径精确匹配）。根因判定=git_commit.py 锁外预检的 CREATE-GUARD 读 HEAD/沙箱树版本注册表（不含未落地 token），而门指路自述「token 批与内容同批或**先行落地**」=设计上 token 须经注册表 commit 落地；capability_canonical_file_registry.yaml 现被 st-acure-20261008-chief 活跃 claim（MM 面），本车道不硬闯代投。**解堵路径**：待 st-acure（或总包收官批）下次落地注册表（将携带本簿 token=tail3-lane-b-00-workbook-20261007，已在 index 层待携），随后任一会话以 `--files docs/_working/tail3/lane_b_dedup/00_workbook.md` 补投本簿即可过闸；簿内容已全量在盘（本文件），24h TTL 暂存面不受影响。
5. 提交袋战果：主袋（tasks.yaml+两防重测试）已入队列 **q-20261008-st-t3b-dedup-0001**（快照入袋即完成）；本簿单独补投（消息文件 .runtime/tmp/tail3/msg_laneb_workbook.txt 已备）。
