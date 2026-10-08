---
ttl: task_bound
completes_when: 全流通战役交付后归档
---

# 全流通战役工位（fullcirculation_campaign_20261008）

总包=st-gomap-chief 会话（GOMAP chief 延任，Owner 2026-10-08 夜批全权）。
交付目标=业务块+新建任务全链路打通（全流通/全管线/全灌水/全可运行）。

## 目录法
- 00_skeleton/ 主骨架：全链路环节清单（挖矿产物）
- 01_dtable_rulings/ D 表 7 GAP 裁定（tech_stack 吸收+R1-R16+CT-4）
- 02_ctable_encoding/ C 表正典编码裁定（20 unknown+家族形态）
- 03_tdm_matrix/ TDM 182 节点挂载矩阵
- 10_hop_mining/ 每环节子文件夹挖矿文档（环节数由骨架定）
- 90_ledger/ 六向台账+冲突登记+待裁定登记（跳过件汇总）

## 并发纪律（Owner 令）
- 其他大队在编辑的文件：登记 90_ledger/conflicts.yaml 后延后
- 他队已完成任务：交叉验证后记入台账
- 线内先挖后干，线间并行流水，最大并发子代理
