---
title: "终极图书馆 · 今夜总攻派工单 v1.0（12 对话×12h）"
ttl: task_bound
completes_when: 总攻验收通过或 Owner 叫停；未开工前=禁生效草案
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 今夜总攻派工单 v1.0

> **前提**：Owner 批 03_endgame_blueprint_v1_0.md 后本单生效。模式=多对话并发按写域切零重叠（Owner 结构要求 2026-09-20），执行模型 Flash、终稿评审 Max。

## §0 总令骨架（通宵总包八件）

总包三职责（挖矿封矿+线内流水+红蓝验收）｜线内挖干线间并行流水｜各线自裁原文留痕｜不停不问（堵点走堵点本，维护班清账）｜两轮 0 缺陷+红蓝对抗｜收工清临时｜端到端交付｜成果即入袋。

## §1 波次时序（12h 时间盒，≤6 对话活跃+待命滚动）

| 波 | 时窗 | 内容 | 依赖 |
|---|---|---|---|
| W0 干预窗 | 0-0.5h | token 前置批一次办齐（全部新文件）；新 .py 域 depgraph 设计节点登记；写域分配公示（§2） | Owner 批图 |
| W1 主轴 | 0.5-3h | A 蓝图评审冻结+schema 定签（Max）→ B1/B2 总账 DDL+五采集器 → C1 总闸+C2 总口并行 | **A 签认是 W2 硬门** |
| W2 七馆并发 | 3-9h | D1..D7 每馆一对话（跑采集器→生成 L1/L2→双向自检→供 INDEX 子树）+E 对齐收编 | W1 全绿 |
| W3 验收转正 | 9-12h | F 红蓝两轮（独立对话只读攻击）→G 端到端演示+转正呈批→H 机动补位 | W2 全绿 |

## §2 分包表（写域零重叠；分包只 stage 不 commit，总包统一 --enqueue 入袋）

| 包 | 写域（独占） | 交付物 | 验收门 |
|---|---|---|---|
| A 终稿 | ultimate_library/00、03 | 蓝图批注定稿+schema 冻结签 | 总包签认（Max 评审） |
| B1 总账底座 | src/zephyr/library/（新域：DDL+fs/PG 采集器） | assets/fingerprints/events 三表+2 采集器 | 采集器只读+幂等（两跑零 diff）；新模块登记大白话简介 |
| B2 采集器 | 同域 CH/schtasks/MCP 采集器 | 3 采集器 | 同上 |
| C1 总闸 | gov_enforcement/library_gate + gate 注册表 | LIBRARY-COVERAGE（首周 warn-only） | 注入 ghost/blind 样本全数捕获 |
| C2 总口 | integration/mcp/library_lookup_server + INDEX 生成器 | MCP 工具+docs/library/ INDEX 树 v1 | 冷启动 5 跳达任意馆页 |
| D1 代码馆 | docs/library/code/ | depgraph 12,107 节点+script-manifest 991 目录页 | 双向自检零误报 |
| D2 数据馆 | docs/library/data/ | CH 246 表+数据源/通道+哨兵目录页 | 同上 |
| D3 文档馆 | docs/library/doc/ | docs 全树+十图+sop 九族目录页 | 同上 |
| D4 制度馆 | docs/library/rule/ | 86 规则+裁定 384+议题 761+标准/门位/契约 38/错误码 788/词汇三层目录页+登记骨架（模型验证生命周期/策略生命周期/事故复盘台账/eval set 清单，05 v2 §L） | 同上 |
| D5 管线馆 | docs/library/pipeline/ | tasks/TDM 138/血缘 1,757 jobs/计划任务 45 台账页+LLM 原生资产登记骨架（prompt 清单/agent 卡，05 v2 §K） | 同上 |
| D6 备份馆 | docs/library/backup/ | 盘点（asset_inventory+infrastructure+bdpan）+3 手工任务/Startup .lnk 点名页 | 同上 |
| D7 闸门链馆 | docs/library/gate/ | 门禁全家族（55+113+91+fail_open 1,635+noqa+allowlist）+git 提交链 15 设备台账+LSG/kill_switch 清单页+SBOM/许可证清册+凭证清册（键名+轮换状态，绝不登值，05 v2 §L4/L5） | 同上 |
| E 对齐 | generator_registry.yaml 登记（W0 前置批） | 统一对账窗+指纹回写总账 | regen 两跑幂等 |
| F 红蓝 | 只读+报告 | 两轮缺陷单 | 第二轮 0 |
| G 交付 | 转正材料+端到端脚本 | 验收报告呈 Owner | 蓝图 §8 全绿 |
| H 机动 | —（补位任一空写域） | — | — |

> 05 总目类目表 **v2 终审**（双路外部对标+本地挑刺）新增缺口已全部并入上表 D4/D5/D7 交付物；prompt 版本管理/轨迹数据集/DORA 四指标/数据质量度量四件**实体建设=W+1 批**（今夜只立登记骨架）。

## §3 风险预案（每条都有本仓实证）

1. **队列串行瓶颈**（实证：单件 landing 40min+）→ 分包只 stage 不 commit，总包统一入袋；
2. **热文件 CAS 竞态**（实证：5 连拒+全文件 CRLF 事故）→ token/registry 走 W0 前置批+纯插入 registry_batch_edit.py+显式 newline='\n'；
3. **schema 未冻先施工** → A 签认前 D 包禁开（违者产出作废）；
4. **机器负载**（实证：llama 13.6GB OOM 事故）→ ≤6 对话活跃+6 待命滚动，内存水位 70% 熔断；
5. **门禁误报伤无辜** → LIBRARY-COVERAGE 首周 warn-only；
6. **共享注册表吸收**（实证：token 随他会话 overlap 提交先入 HEAD）→ W2 各包入袋前先查 HEAD 是否已被吸收，冗余单直接放弃不 requeue。

## §4 验收（端到端演示）

①随机 10 资产（跨六馆）经 library_lookup 定位+指纹核验 ≤30s/个；②随机删 1 文件→对齐轮必红；③AGENTS.md 冷启动 5 跳达任意馆页；④红蓝两轮第二轮 0；⑤成果转正入 docs、临时区清零；⑥12 条既有漂移现行全部以 orphan/ghost 入总账留痕。
