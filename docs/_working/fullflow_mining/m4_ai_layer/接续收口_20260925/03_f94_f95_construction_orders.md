---
ttl: task_bound
title: 接续收口册03 — F94/F95 设计面→施工单转化清单（七段循环/OBJ 四线·草案级·只列不施工）
lane: m4_ai_layer
session: st-ailayer-fullflow-ai
date: 2026-09-25
status: mined
---

# 03 — F94/F95 施工单转化清单（清单级草案）

> **一句话**：11 本 DESIGN（L1-L7+OBJ_M/T/S/R 全 design_done）中**尚未闭环的施工项**逐条转化为草案级施工单：F94 七段循环 18 单+F95 OBJ 四线 13 单+横切 4 单，共 **35 单**；**本册只列单不施工**。已完成项（✅ 约 46 项）不重复列，真源=P1_full_construction_inventory.md+夜报 Owner 11 项+本日蒸发取证（收口册02）。
> **大前提（前置中的前置）**：v2 117 件批落地（缺①）——过半单的材料在 untracked 盘面/蒸发件里，不落地则无单可施。

## 一、F94 七段循环施工单（L1-L7）

### L1 perceive（2 单+1 重做单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L1-WO-7 | register_ai_l1_scan_task.ps1（**未建**，盘面无此件） | 外扫节拍宿主：计划任务注册+resource_profile_registry 条目+搜索任务单/矿脉再生挂节拍 | **T3 双前置**：Owner 追认+裁定登记（夜报 #9） | resource_profile 登记+裁定号在册；月检外扫段出数 | Owner→施工 |
| L1-WO-9 | translator.py:18 挂起点 | 先验消费接口：接 L7 priors 服务（L7 侧服务已建成） | L7 DESIGN 状态翻转（夜报 #10） | import 通+先验卡可注入翻译器 | Owner 翻状态→施工 |
| L1-WO-R | 矿脉三挂点**重做** | depgraph 生成器尾+align_all 尾 vein 再生子进程钩子+FACTORY-MAP gate 拦截消息携矿脉指引——R2 项5 的三处改动**已不在盘**（三文件 HEAD 干净零 vein 引用，本日实锤） | gen_search_veins.py+ai_search_veins.yaml（在盘 untracked）先行落地 | 三文件含 vein 引用+月检 vein_coverage 段不再显"产物缺失" | 施工（治理层文件改前 claim） |

### L2 intake（3 单，全部挂起/定向态）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L2-WO-E | intake_exam_due 派考边 L2 侧 emit | 二选一：确认不加该边（维持现状 docstring 留痕）or 授权 L2 侧补 emit | Owner 定向（夜报 #3，L4 侧已建不阻塞） | 定向结论落 DESIGN/docstring | Owner |
| L2-WO-C | 机制族 8 族词表口味修正权 | 词表口味修正权限界定 | Owner 批（数据操作不阻塞） | 修正权登记 | Owner |
| L2-WO-P2 | simhash 分块索引（Phase 2） | ≥10 万卡才解锁的分块索引 | 卡库≥10 万（现 6 行） | 挂起，条件触发 | 自动 |

### L3 cleaning（1 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L3-WO-1 | C1 判据追认 | 清洗判据 Owner 点头（YAML 在 v2 批内） | 缺①落地 | 追认记录 | Owner 追认即清 |

### L4 comparator（2 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L4-WO-1 | C1 判据追认 | 对比判据 Owner 点头 | 缺①落地 | 追认记录 | Owner |
| L4-WO-7 | C7 独立性 gate | 立案归 OBJ_R 流水线治理（非 L4 本体施工） | OBJ_R S3 通道（见 F95） | 立案号 | Owner 立案 |

### L5 schedule_gate（4 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L5-WO-C1 | C1 判据追认 | 排产判据 Owner 点头 | 缺①落地 | 追认记录 | Owner |
| L5-WO-C9 | api_server 三路由（queue/skeletons/confirm）+schedulegate.html | **补丁已蒸发**（.runtime staging 空树实测）——重铸或随 v4 批改道直改 | 缺①+他线 api_server drift 清窗 | 三路由 fetch 空态正常+新页渲染 | 施工 |
| L5-WO-CF | confirm 判定落点 | 现为诚实拒执行；需 DESIGN 增补判定落点或永久确认拒态 | Owner/设计定向 | DESIGN 增补行或永久注记 | 设计定向 |
| L5-WO-C8 | C8 排班 --force 再生 | 一行命令 `python scripts/governance/generators/generate_resource_profile_registry.py --force`；生成器混 st-gpu-final 未落地编辑需先分离 | Owner 错峰窗（夜报 #8）+st-gpu-final 件落地 | 资源册再生+OVERRIDES 三条入册 | Owner 排窗 |

### L6 ab_switch（3 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L6-WO-S6 | S6 审批分流接线（risk_tier→auto/independent_review/owner_one_click 三道；owner 道接 promotion 页 kind=switch advisory） | **双补丁+WIRING_NOTES 已蒸发**——重铸；两硬依赖 list_switch_advisories/decide 分流随批文接 | 缺①+promotion 页路由落地 | 三道分流机检+promotion 页出 advisory | 施工 |
| L6-WO-O | 观察期数值门槛预注册 | 月度制节拍下的量化门槛值 Owner 确认（DESIGN §C 已有业界下限 14/30 天参照） | Owner 确认 | 预注册记录进 switch_criteria | Owner |
| L6-WO-T | 墓碑 TTL 清理判据+清理提案生成器 | ttl_deadline 仅 schema 字段未消费；判据批后建提案生成器（净删门前置） | Owner（夜报 #5） | 判据入册+生成器产出清理提案走净删门 | Owner→施工 |

### L7 heredity（2 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| L7-WO-ST | DESIGN.md 状态翻转 design_v1→定稿 | 解锁 L1-WO-9；checklist_seed_v0.yaml 在盘 untracked 待随批 | Owner（夜报 #10） | DESIGN frontmatter 翻转+checklist 入册 | Owner |
| L7-WO-CL | checklist 入册纪律增补行 | 与状态翻转关联同批 | 同上 | 纪律行在册 | Owner |

## 二、F95 OBJ 四线施工单（M/T/S/R）

### OBJ_M models（4 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| OM-WO-C6 | model_routing_policy.yaml 增 AI 层轨 8 条+free_window_pref 字段 | 提案在袋（C6_routing_diff_proposal.md，staged）：api_providers 零增删、盘中约束全 inherit、逐条 evidence_ref | **Owner 终批**（夜报 #1）；既有 12 轨零改动 | router 加载不报错+既有测试全绿 | Owner 批→施工 |
| OM-WO-C7 | C7 预算 API（/api/budget-advisories） | **补丁已蒸发**——重铸（compile 过的 api_server_ai_layer_routes.patch） | 缺①+api_server drift 清窗 | 路由 fetch 空态+manifest 条目 | 施工 |
| OM-WO-33 | DESIGN §3.3 external_missing_remedy 定稿 | 三口径互斥（0.7 回流 vs 0.8 归一化，字面 1.1 破 P∈[0,1]）；YAML 现钉 0.8、测试按 0.7 | Owner 定稿（夜报 #7） | DESIGN/YAML/测试三处合流 | Owner |
| OM-WO-A | C1/C4/C5 判据追认 | 模型线三判据点头 | 缺①落地 | 追认记录 | Owner |

### OBJ_T tools（4 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| OT-WO-C6 | C6 配对常量 | H1 挂起：等 M4 上线+双跑 1 窗；盘上先行产物随批文处置 | 双跑窗口数据 | 配对常量入册 | Owner |
| OT-WO-C5 | 沙箱 profile+试用档案卡 | 立案准许后建 | Owner（夜报 #11 内） | profile+档案卡在册 | Owner 立案 |
| OT-WO-K | 考纲正式化 | tool_benchmark_suite_v0.yaml（在盘 untracked）升正式考纲 | Owner 批 | 考纲版本化 | Owner |
| OT-WO-D | ai_tools DDL 部署 | usage_stats `--deploy`（schema 本日实测不存在） | Owner high 门（缺②同源） | information_schema 见 ai_tools | Owner |

### OBJ_S perimeter（2 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| OS-WO-V | 软硬线数值+S5 阈值/schemas 确认 | 数值随 v2 批落地后 Owner 确认 | 缺①落地 | 数值备案 | Owner |
| OS-WO-2 | secret_registry 增 ai_exposure: forbidden 字段 | deny-list 已先行且功能等价，可缓批不阻塞（夜报 #2） | Owner 任意时点 | 字段在册 | Owner |

### OBJ_R rules_standards（3 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| OR-WO-S3 | S3 阈值外置化（commit gate 硬编码常量→注册表） | **提案已蒸发**（obj_r_s3_proposal.md 202 行全仓零命中）——重铸后走三段通道：提案 ai_layer 起草（全硬编码常量+真源行号，对标 AI-THD-001 统读）→施工 gov 车道（gate 源码=治理层资产）→批文 Owner；建议候 2026-10-15 双窗证据后提包更实 | 提案重铸+30 天 gate_execution_stats | threshold_loader 统读 fail-closed+重放器不再常量覆写 | Owner 批→gov 施工 |
| OR-WO-2 | #2 评分裁定追认 | 评分口径 Owner 点头 | 缺①落地 | 追认记录 | Owner |
| OR-WO-CB | casebook 升格攒 5 案 | casebook.md（staged）攒案至 5 案升格 | 自然积累 | 升格记录 | 按节奏 |

## 三、横切施工单（4 单）

| 单号 | 施工对象 | 内容草案 | 前置 | 验收草案 | 门位 |
|------|---------|---------|------|---------|------|
| XC-WO-1 | v2 117 件批落地 | 四步序列（P1_final_report 要素三）；**一切单的大前提** | 队列畅通广播（Owner） | 主区 pytest≥856+`git log -1 --name-only` 核验 | Owner 触发 |
| XC-WO-2 | token 先行批 9 行 | token_batch_rows.yaml **已蒸发**——重铸后过 CREATE-GUARD | 卡文件落地时序 | 9 卡 token 在册 | 施工 |
| XC-WO-3 | E2E+capability 卡落地批 | test_evolution_chain_e2e.py+卡×9（在盘 untracked）随收官批入 HEAD | XC-WO-1 | HEAD 可 cat-file 命中 | 施工 |
| XC-WO-4 | PG 部署三连+残留清理 | ai_compare/ai_tools/ai_layer_scheduling 三 --deploy+smoke×2 三步验证 DROP（收口册02 缺②全文） | Owner high 门 | information_schema 四进二出 | Owner |

## 四、计数与依赖序

- **35 单**：F94=18（L1×3/L2×3/L3×1/L4×2/L5×4/L6×3/L7×2）；F95=13（M×4/T×4/S×2/R×3）；横切=4。
- 按动作分类：**纯批文/追认/定向单 17**（Owner 点头即清，零代码）｜**重铸单 4**（蒸发件：L5-C9/OM-C7/L6-S6/OR-S3 提案）｜**常规施工单 10**（含 XC-WO-1 落地执行）｜**部署/清理单 2**（OT-WO-D/XC-WO-4）｜**挂起单 2**（L2-P2/OT-C6）。
- 依赖主链：XC-WO-1（落地）→重铸单/常规单并行→XC-WO-4（PG）→缺③触发单（L1-WO-7/L1-WO-9/L7-WO-ST）→进化循环通水。
- 与收口册02 的关系：本册=三缺解锁后的**执行面清单**；02 册=三缺的**证据与门位面**。两册配对使用。

## 五、自审闸三态

**清单级挖干（转化面）+待裁（单的时序与 Owner 批文）**：
- 28 单逐条含对象/内容/前置/验收/门位五要素 ✅；真源可回溯（inventory 行+夜报#+本日蒸发实测）✅
- 只列不施工：本会话零施工动作、零主区写入、零 enqueue ✅
- 待裁：重铸单 4 件是否随 XC-WO-1 同批重铸（建议同批，上下文在终报内新鲜）；L5-WO-CF 判定落点需设计定向。

## 六、复核命令

```bash
ls docs/_working/ai_layer_vision/P1_full_construction_inventory.md   # 转化真源
grep -c "WO-" docs/_working/fullflow_mining/m4_ai_layer/接续收口_20260925/03_f94_f95_construction_orders.md  # 35 处单号行
find . -name "obj_r_s3_proposal*" | wc -l                            # 0=蒸发属实
git status --porcelain docs/_working/ai_layer_vision/ | head         # 报告/清单族 staged 态
```
