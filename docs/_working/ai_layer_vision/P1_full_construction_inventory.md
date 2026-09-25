---
ttl: task_bound
title: P1 全量施工清单（11 本 DESIGN 逐项对照 HEAD 实况·通宵全速施工版）
owner: ZephyrAlpha-Owner
session: st-ailayer-final-20260924
date: 2026-09-24
status: construction_inventory
---

# P1 全量施工清单（2026-09-24 凌晨对照定稿）

> 真源=11 本 DESIGN.md + P1_construction_plan.md；实况核验=三路挖矿（09-24 00:1x）+R2 接线批实测。
> **【09-24 晨重建注】本件随主区 untracked 蒸发事件丢失，由接管总包按上下文原样重建（内容与初版一致，末尾补事故一行）。**
> 状态图例：✅已毕 ｜ 🔨本夜施工中 ｜ 📦补丁/母本就绪待落地 ｜ ⛔受阻登记（自裁跳过）｜ ⏸待 Owner 批文（禁代裁）

## L1_perceive（施工项 9）

| 项 | 文件 | 依赖 | 验收标准（DESIGN 要义） | 状态 |
|----|------|------|------------------------|------|
| 1 源注册表 12 源 | config/ai_source_registry.yaml | - | 12 源四闸齐 | ✅（v2 批内） |
| 2 配额同步器 | sync_ai_source_quota.py | 项1 | 配额读数可跑 | ✅ |
| 3 矿脉生成器 | gen_search_veins.py + ai_search_veins.yaml | 地图三真源 | 再生幂等/挂 ROOR | ✅+本夜挂点③ |
| 4 骨架即地图挂接 | depgraph 生成器/align_all/FACTORY-MAP gate | 项3 | 三挂点接通防手工清单退化 | ✅（R2 项5） |
| 5 搜索任务单 | search_orders.py | 项3 | 任务单登记件 | ✅ |
| 6 翻译器 | translator.py + 卡 | 项9 挂起注记 | L0-L3 渐进披露+卡 | ✅卡（R2 项8） |
| 7 外扫节拍宿主 | register_ai_l1_scan_task.ps1 | R1-F2 双前置 | resource_profile 登记+裁定登记 | ⏸（Owner 追认+裁定号） |
| 8 月度体检 | gen_ai_layer_monthly_checkup.py | 项1/3 | 44 tests+本夜 S4 段 | ✅（S4 接线 R2 项7） |
| 9 先验消费接口 | translator.py:18 挂起 | L7 定稿 | L7 priors 消费 | ⏸（待 Owner 翻 L7 状态） |

## L2_intake_library（施工项 9）

| 项 | 状态 |
|----|------|
| T1-T5 表+V1-V3 视图/闸/查重/卡库/KPI/事件/capability 卡 | ✅ 已落 HEAD（批次0/1） |
| ai_cleaning_spec 表并入 DDL | ✅（v2 批内） |
| 机制族 8 族词表口味修正权 | ⏸（Owner；数据操作不阻塞） |
| Phase 2 simhash 分块索引 | ⏸（≥10 万卡解锁，挂起） |
| intake_exam_due 派考边 L2 侧 emit | ⛔（L4 侧已建；L2 侧 emit 属 Owner-3 定向后补——裁不了不造契约） |

## L3_cleaning（C1-C8）

全部 ✅（spec_store/washer/local_prefill/auditor/policy+DDL+测试 61）；C1 判据点头 ⏸（Owner 追认即可，YAML 在 v2 批内）；C8 卡 ✅（R2 项8）。

## L4_compare（C1-C8）

全部 ✅（executor/experiment_store/fairness/too_good/compare_events/四考场/policy+测试）；C1 判据点头 ⏸；C7 独立性 gate ⏸（归 OBJ_R 流水线治理立案）；**EX-R1 引文补核 ✅（销账：作者署名误引修正 Krakovna, V., et al.）**；intake_exam_due L4 侧 ✅ 已建。

## L5_schedule_gate（C1-C10）

C2/C4/C5/C6/C7/C8(种子 writer)/C10 ✅；C1/C8 判据 ⏸；C3 事件件改名 scheduling_events.py ✅（账实对齐随 31dc939f 摘除记录）；**C9 前端接线 ✅/📦（R2 项4：manifest+html 已 staged，api_server 路由在补丁）**；**confirm 判定落点 ⏸（无 DESIGN 依据，诚实拒执行已实现）**；C8 --force 再生 ⛔（生成器混 st-gpu-final 编辑+Owner 错峰窗）。

## L6_ab_switch（S1-S8）

S1-S5/S7/S8 ✅（两棵树全 staged）；S6 审批分流 ✅/📦（kind=switch 双补丁+WIRING_NOTES 就绪，两硬依赖随批文接）；观察期数值门槛 ⏸（Owner 预注册确认）；墓碑 TTL 清理判据 ⏸（Owner-5）。

## L7_heredity（项 1-9）

项 1-8 ✅；checklist 入册纪律增补行 ⏸（Owner-10 关联：DESIGN 状态翻转）；状态翻转 ⏸。

## OBJ_M_models（C1-C8）

C1/C2/C3/C4/C5/C7 ✅（源码+三表 DDL+测试）；C1/C4/C5 判据 ⏸（追认）；**C6 路由八轨 ⏸（Owner 终批，提案在袋 OBJ_M_models/C6_routing_diff_proposal.md）**；C7 API 端点 📦（补丁就绪）；C8 排班 overrides 盘上就位 ⛔（同 L5 C8 --force）；§3.3 external_missing_remedy ⏸（Owner 定稿，B7）。

## OBJ_R_rules_standards（S1-S5）

S1/S2 ✅ 已落 HEAD（gov 会话 3ac3af3faac）；S4 standard_checkup ✅（v2 批内+本夜挂月检）；S5 casebook ✅（casebook.md 在袋）；**S3 提案 ✅（骨架+76 常量清单落 staging，施工归 gov 车道、批文归 Owner）**；#2 评分裁定追认 ⏸；replays/ 目录=运行态按需。

## OBJ_S_perimeter（S1-S8）

S1-S8 源码+测试全 ✅（staged）；三 gate 挂载 ✅（R2 项2，149/150/151）；S5 阈值/schemas ⏸（v2 批内落地）；软硬线数值 ⏸（Owner）；secret_registry ai_exposure 字段 ⏸（Owner-2，无字段也能拦可缓）。

## OBJ_T_tools（C1-C9）

C1-C4/C9 ✅；**C4 考尺指针 ✅（R2 项1，唯一 skip 消灭）**；C6 配对常量 ⏸（H1 挂起：等 M4 上线+双跑 1 窗；盘上先行产物随批文处置）；C5 沙箱 profile+试用档案卡 ⏸（Owner-11 立案准许）；C7 删除 gate ⏸（归 OBJ_R）；考纲正式化 ⏸（Owner）。

## 横切登记面

| 项 | 状态 |
|----|------|
| capability 卡 ×9（intake 外全部八包） | ✅（蒸发后自 staging 母本恢复） |
| capability 词典条目 ×9 | ✅（canonical 册两次重插，热册覆写事故留痕） |
| creation_token/翻译册/depgraph 节点 | ✅ 已落 HEAD（360468501e）；本夜新增件（卡×9/E2E 测试）收官时 token+翻译补登（token_batch_rows.yaml 预铸 9 行在 staging） |
| api_server 四路由 | 📦 补丁（他线 drift 清后 apply） |
| E2E 链路测试 | ✅ tests/ai_layer/test_evolution_chain_e2e.py（七段全绿+闭环，蒸发后自 staging 恢复） |
| promotion kind=switch | 📦 双补丁+WIRING_NOTES（staging/l6_promotion） |

## 汇总计数

- ✅ 已毕：约 46 项（含前任八批次+v2 修正+R2 接线 6 项+通宵增产 6 件）
- 📦 待落地：3 项（api_server 补丁/promotion 双补丁/C9 前端件）
- ⛔ 受阻登记：3 项（L5 C8 regen/OBJ_M C8 同源/I7 吸入——全因他线在途混编+Owner 错峰窗）
- ⏸ 待 Owner：12 项（全部登记在夜报待批 11 项+R2 增项，禁代裁）
- **🚨 09-24 晨主区 untracked 蒸发事件**：全部恢复（沙盘 126+staging 母本+上下文重建），事故全文见 LEDGER_final.md 事故章。
