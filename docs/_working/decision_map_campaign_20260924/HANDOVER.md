---
ttl: task_bound
title: 总筹交接书（st-cmd-20260924 → 继任者 · 2026-09-25 晚）
---

# 总筹交接书（继任者单入口 · 2026-09-25 晚）

> 继任者只需读完本文件即可接管全部工作。所有数字/路径/配方均经实测，引用文件全部存在。

## 一、你的身份与权限

你是总筹（总包/总负责人），Owner 已全权授权：统筹任务顺序、开子代理、协调验收、裁定无法裁定的内容、整体收尾交付。遇无法裁定的问题，按"客观专业架构师+第一性原理+专业机构实践+量化社区+GitHub 开源"分析后自裁；仍无法裁定→登记+跳过；堵塞→可停。**Owner 在睡，不问问题，做完才汇报。**

## 二、当前在飞的四条线（接手后第一件事：逐线确认还活着）

### 线 1：GPU T1 搜索（Owner 最高优先级交付）
- 运行编号 grid_20260924-213246（目录 data/strategy_intake/grid_20260924-213246/，manifest 期末一次落盘=跑中为空是正常）
- 日志 .runtime/logs/grid_t1_restart2_20260925.log；进程 python.exe ~2.4GB
- 规模 3,700 格全档成本门，闭卷窗 2019-01-04→2025-09-09；启动 09-25 11:15，预计 09-26 23:15 完（36h）
- **备份护甲**：D:\zephyr_t1_backup\strategy_intake\（10 分钟 robocopy 镜像，日志 shield.log）
- **守望器自动化** automation-5f742031（每 30 分钟）：T1 完赛自动验收+发 T2（900 格终审）+自删；正午窗口执行 W-M1 24h 三判据评估+AI 层广播判据+死信自愈重投。**勿删此自动化**
- 完赛验收判据（17 号文§一）：manifest=3,700 行/dead=0/negatives.csv 在/N_eff≥12
- **T1 死过一次**（01:49:57，10 号文元凶=landing clean 打穿主区），EV-01 黑匣子因此上线（.runtime/evaporation_blackbox/blackbox.jsonl 每 5 分钟快照+schtasks ZephyrAlpha_EvaporationBlackbox）——若再蒸发，黑匣子可定位分钟级窗口

### 线 2：落地总执行班（后台子代理，全权死信循环）
- 使命：把主区一批已修复待落文件全部落进 HEAD（enqueue→观察死信→验尸→修复→同步 worktree→重投循环）
- 修复清单 8 项已由前置班完成（BLUEPRINT 头/meta.yaml token/翻译 entries 段/TTL+doc_type/doc_type 迁移/参数对象化/ALGO-NOTE 同步×2），见 15 号文+本轮死信验尸
- 关键配方（血泪换来的，照做）：
  - **代码件入队**必须在会话 worktree 内跑且 export ZEPHYR_COMMIT_QUEUE_DIR="D:\\ZephyrAlpha\\.runtime\\commit_queue"（否则进 worktree 本地队列+WORKTREE-REQUIRED 拒）
  - **文档件**也一律 worktree 内+env（本会话已注册 worktree，所有 commit 都要求 worktree 出身）
  - **修复后重投必须全新 enqueue**（--from-bag 会用修复前的旧快照=白死）
  - **热文件 CAS base 口径**=read_text 归一 LF 后 content_sha256（CRLF 文件先归一再算）
  - 每次 enqueue 后 5-10 分钟查 dead/ 验尸；死因修一项少一项
- 待落批次内容：候选池 7 件/状态轴 9 件/哨兵+黑匣子+导入修复 5 件/材料线 5 件/881xxx 7 件/P1 v2 6 件/桥修复 11 件/双接线 5 件/战役文档+SKEL 26 件/台账

### 线 3：做T多周期引擎班（后台子代理）
- 使命：Owner 主攻方法论——1/5/15/30/60 分钟买卖点规则（34 法规则化 YAML 卡预注册）×全市场全算→六段相位×板块×市值×新闻状态匹配→匹配矩阵
- 容量预检已过：282 万对语料/23.3h<48h
- 已知技术坑：CH 返回 Decimal 列会炸向量算术（已修 astype float64）
- 产出落 docs/_working/decision_map_campaign_20260924/links/L05_t0/

### 线 4：GPU 重写挖矿班（后台子代理）
- 使命：五份文档（计算热点普查/业界 GPU 方案全景/重写架构三层 L1 向量化-L2 批量 GPU-L3 全 GPU/验证框架/迁移路线图）
- 产出落 docs/_working/gpu_rewrite/（若目录已出现即已交付或进行中）
- 交卷后：呈 Owner 裁决 L1/L2/L3 落地顺序

## 三、已落地成果（不必重做）

全部经 GitCommitGateway 正门入 HEAD，git log 可验：
- 九环节骨架 SKEL×9+五车道审计（10-14 号文）+15 治本方案+16 件案结案+17 量化判据+18 专业对表
- P1 条件概率表 v1（data/strategy_intake/conditional_tables/，469 板块版；v2 729 板块在队）
- 决策链哨兵（v10 已落，schtasks 09:40 值班）+蒸发黑匣子（v8 已落，5 分钟快照值班）
- 881xxx 行业族补采 v5（469→728 板块）+决策链/黑匣子翻译
- 状态轴合并批/六段温度统一/候选池 M-41/L2 门三态/D13 mock 退役/T4 核对实体化——部分已落部分在队
- 上岗规则 v1 立法稿+风控仲裁序 v1 立法稿（两份 design 文档）
- 方法论十册（quant_methodology/）+十七号文量化判据+十八号文专业对表

## 四、剩余工作全量清单（优先级序，详版=07 号文）

### GPU 战役收尾（本周末）
1. 红蓝标定达标线：Spearman≥0.99+top50 重合≥90%→达标即切两轮制（prereg 重签裁定触发）
2. T1→T2→成绩单→17 号文六线垃圾判据检查
3. 成绩单解读（考尺口径相对排名；口径对照 IBT-D01 先行）
4. L06-C01 上岗规则 v1 激活（填 state_matrix；前置=euphoria/distribution 无 r 态来源的结构性问题）
5. GPU 重写挖矿班交卷→呈 Owner 裁 L1/L2/L3 路线

### W-M1 账本线
6. 24h 评估点：守望器正午窗口自动跑三判据，全绿→提请 Owner 按 P-3 提前翻转
7. 72h 兜底 09-27 中午

### 施工项池 P0（资金安全/成绩单可信度）
8. IBT-D01 双引擎成本口径对照（考尺 vs 整装）
9. TRD-A10 桥客户端两缺陷修复（隔夜单静默丢弃+撤单竞态）
10. TRD-A12 熔断 HALT 首次演练（Owner 门位）
11. L04-C03 DU-11 daily_valuation 部分写入病根治
12. AI 层 245 件批落地（三 AI 门暂禁用待翻回——in_process_gate_registry.yaml 三条 enabled:false，AI 批落地同批翻回）

### 施工项池 P1（链路通电）
13. L09-C01 编排器收拢（蓝图版 vs 双轨二选一）
14. L09-C03 双账合流；L04 候选池三来源接线；L07-C03 算法层收口（Owner 一句话）；L03-C06 v2 卡判档；L01-C03 口径治理；六段收编剩余三步

### 消费面与战略
15. CNS-01~14 消费面接线；L08-C03 MOD-RK-049 三选一；退役策略重考预注册（聚宽 322/潘潘 159，CPCV 框架，同卷同纪）；假设引擎；ETF 做T线；bandit v2；tick 盘口信号

### 假期/日历（不挡 GPU）
10-05 F 盘链摘除（日检 1/14 天）/vhdx 压缩/flags 轮转/266 件月批/10-18~21 删链/DU-16 复盘/881 深度缺口/live 准入/C2

## 五、Owner 待裁清单（全部有建议，见 07 号文 C2）

1. t0 甲位（三版本分叉待确认）2. 清道三袋 ARCH 议题注册 3. L09-C01 编排器收拢 4. emoreplay 交接确认 5. 方案① prereg 重签（红蓝达标触发）6. AI 层批文 7. 修宪入口 8. DU-07 consensus 补齐已批待执行

## 六、血泪配方（违反即重蹈）

1. 代码件入队=会话 worktree 内+ZEPHYR_COMMIT_QUEUE_DIR 指主队列；文档件同
2. 跨调用 cd 后必须 pwd 自检（跑丢 cwd 会把整条队列卷进嵌套 worktree 死亡）
3. 修复后重投=全新 enqueue；--from-bag=旧快照白死
4. 热文件 CAS base=content_sha256(归一 LF 文本)；CRLF 文件写时 newline 参数保风格
5. .md 在 docs/_working 需 ttl+doc_type 双字段（strict-doctype 已启）；doc_type 从词表取（readme 已 deprecated→index）
6. 新 .py=CREATE-GUARD token+add_module_translation 大白话（翻译条目必须落 entries: 段，落错段=gate 判缺失）
7. git checkout HEAD -- <热册>=第二次蒸发（会抹他会话未落条目）；增量补回才正解
8. ALGO-NOTE-SYNC：碰实现代码必须同批同步 TDM algo_note_zh+algo_flow yaml
9. 落地环境 GateAutoRegistrationError fail-closed=名册引用了未落 HEAD 的模块（同源断裂）——暂禁用该门待模块落地翻回
10. 队列重整/清算会重置计数器并可能清 pending——入队后必须核实在队（ENQUEUED 回执+glob pending）

## 七、纪律

禁裸 git commit；禁实盘四禁；禁向 .runtime 根直写；主区改动 CAS；临时文件 .runtime/tmp（24h 清理）；禁跑 T1 冲突 GPU 作业（单卡独占）；红蓝未过禁上岗；全部交付走 GitCommitGateway。
