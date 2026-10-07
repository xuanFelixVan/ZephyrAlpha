---
campaign: matrix-20261006
version: v2
updated: 2026-10-07
rulings: Owner 2026-10-07 裁定——10 退役候选封存待逐个复核（不执行）；其余全部照总包建议施工
ttl: task_bound
---

# 总施工清单 v2（所有后续工作，一份不落）

> 使用说明：这是全项目"考试战役后续"的唯一施工总账。P0=立即（有时限/解锁价值最大）、P1=本周、P2=排期、P3=等外部条件。每条带验收判据。完成的移入 99_delivery。

## P0 立即执行（0-24 小时）

| # | 事项 | 来源 | 验收判据 | 状态 |
|---|------|------|---------|------|
| P0-1 | **tmp 区代码抢救**：bootstrap_gpu 核 / gpu_ic 核 / exit_sim 仿真器+冻结卡 / grid_adapter 三件套，从 .runtime/tmp（24h TTL）转正到仓内 staging 包（token/翻译/depgraph 全套治理） | E/G/H/I 道产物 24h TTL | 四件在 HEAD+导入自证+对拍脚本随行 | ✅ 已落（6b3426c398，18 件，2026-10-07 st-matrix-20261007 补交；前 3 袋死于 TTL-METADATA/VOCAB-HARDCODE/BARE-SUBPROCESS 三门，逐一修因后过） |
| P0-2 | **78 合格指标入 paper 观察池**（paper_pool_v1.yaml，三个月观察期后复核） | Owner 裁定 | 78 只在册带 IC/覆盖数据 | ✅ 已落 |
| P0-3 | **SMA200 土办法设为默认体制帘子**（J 道 HMM 判不合格；HMM 重训过考前不得回用）；此后一切考试的 regime_source=sma200 | J 道 verdict+Owner 裁定 | 代码默认值变更+册头标注 | 授权=裁定#489②，待车道施工 |
| P0-4 | **MOM-029 direction 注解挂起**——卡面无经济假设文档，禁看分填方向；改立工单"先补 hypothesis 再考" | 纪律刹车 | 工单入本册 P1 | ✅ 已判 |

## P1 本周（高价值/数据已具备）

| # | 事项 | 来源 | 验收判据 |
|---|------|------|---------|
| P1-1 | **指标链行物化向量化**：_build_row 逐格循环（52.9%）→列式批算；GPU 深度后置 | I 道探针（4.03 亿行链，非 IO 瓶颈） | 影子表 143 列 1e-9 双跑+单片耗时对比 |
| P1-2 | **layered spread 核接线**：同签名替换 compute_layer_spread（核已逐位+6.7x） | I 道产物 | governance 引用链全绿+基准留档 |
| P1-3 | **bootstrap 核接线**：walk_forward:274/e2:168/correlation:325 三处内循环换核（API 不动） | H 道（35/35≤1e-9） | 三原函数索引注入对拍回归绿 |
| P1-4 | **MOM-029 补 hypothesis 再考**：读代码写经济假设（事前）→填 direction→冻结 prereg v2→重考 | B 道 0.0517 翻案候选 | 新 prereg 卡+重考 verdict |
| P1-5 | **EMO-体制联动首考**：emotion_index 表 8659 行实测可考（J 道发现），补 prereg 及格线后考"情绪态→forward 收益" | J 道盘点 | 联动考卷+verdict |
| P1-6 | **A06 资金流数据回补申请**：8.5 个月空洞回补后重考 ALT-A06-PERSIST10D（retain 0.60 唯一过线者） | A 道 | 回补到货→重考 verdict |
| P1-7 | **daban 数据回补申请**：daban_engine_load 仅 2026-09 一个月，回补即可考 DABAN-022 | D 道 | 回补→measured verdict |
| P1-8 | **MOM-029 类 direction 字段全册补全勘察**：因子册多少条缺 direction（B 道实证 ICIR 判负源于此）→批量补全工单 | B 道发现 | 勘察册+补全批次表 |

## P2 排期（M 级施工，带规格卡）

| # | 事项 | 前置 |
|---|------|------|
| P2-1 | 离场族其余 12 节点：复制 E 道通道（prereg→双臂→重标定→进册）| E 道 template |
| P2-2 | 板块传导后处理模块（one-hot×查表，M-2）+板块强度四路（M-3）因子接线 | C 道 spec 卡 |
| P2-3 | M-7 二波：data_gap 类 13 因子随数据回补逐个解锁 | P1-6/P1-7 数据到货 |
| P2-4 | M-8 二波：tick 组 5 策略（tick_data 2026-01 起+EDE tick 考道）| tick 回补 |
| P2-5 | EVENT-001 策略：等 event_score 管线闭环（#ARCH-NLP-PIPELINE-001） | NLP 管线 |
| P2-6 | wq_alpha_87 接线（核已就绪，接线日即插） | 装配批 |
| P2-7 | SM 换尺呈批：治标引擎 float64 镜像双跑通道 | Owner 门位 |
| P2-8 | HMM 重训回炉（若 Owner 选 B 路）：重训→重考四表 | Owner 方向 |

## P3 等外部/等 Owner

| # | 事项 | 等什么 |
|---|------|--------|
| P3-1 | 10 退役候选指标逐个复核 | ✅ 裁定#489①（6 退役/CYC 4 留观改条件考场；复活条件=全网调查车道证伪实现或考法） |
| P3-2 | T3a 开闸考点火 | t3a 通道裁定 + GPU 空窗 |
| P3-3 | value_reversal v1_value 因子面通道 | ✅ 裁定#489④（暂不开，T3b 出分后凭考号再裁） |
| P3-4 | t0_material_line 路径并行（23.3h→<2h） | ✅ 裁定#489⑤（已批，P1-1 落地后第二波） |
| P3-5 | R1/R2 地图名实错位定谳 | 裁定#489⑥ 值班队已接管（本会话系），调档中 |
| P3-6 | metaq 逐问回填（36 问 deferred 留痕） | 逐问判据机解器（M-9） |
| P3-7 | 定时器钉死：考试机挂 Windows 计划任务 | 人工再跑 2-3 天确认稳定后 |

## 负结果边界（禁重挖，复活条件在册）

A11 EIA 空壳/B01-B10/C01-C03/G5 等 21 条另类源线；分时破位/条件单/龙虎榜派发等 13 条不可行项——全见 mining/*/99_negative_results.md。
