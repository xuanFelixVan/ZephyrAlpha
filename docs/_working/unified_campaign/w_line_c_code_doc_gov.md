---
ttl: task_bound
completes_when: 本线终验红蓝通过
---

# 【总包丙·代码文档治理线】施工指令（自包含，新对话整贴即用）

# sid：st-code-doc-20260921 ｜ 落盘：docs/_working/code_doc_gov_campaign/ ｜ 模型：Max 总包+Flash 分包
# 上位方案：docs/_working/unified_campaign/00_master_plan.md（§2 写域/§8 纪律）

## §0 使命
①疑似真 bug 逐条认领修复（14 条）②测试真账清欠（32 条）③企架两个施工文档目录归置（蓝图或归档二选一，Owner 终极强迫症项）④历史悬账验活核销 ⑤final3 尾巴小件+股权穿透线排期出单。终态=测试全绿真账清零、施工文档各归其位、悬账每条有终态。

## §1 冷启动
同甲线配方（PATH/守卫/session_worktree_start+心跳）；裁号 re-find max+1（当前 max=#377）。

## §2 真源读序
1. docs/_working/dataqa_audit/test_health_report.md §2/§3——A17 真账 32 条+A18 疑似 bug 14 条全路径编目（执行日逐条复现验活，报告会陈旧）
2. docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/ 全目录+09_ai_architecture/implementation_plans/ 全目录——包①归置对象（现场枚举勿背数）
3. docs/03_modules/ 蓝图体系（归置目标态参照）+docs/_working/archive/ 归档区惯例
4. 悬账真源：git status staged 现状（原记录 189 件，2026-09-20 汚编时实测 167——逐条验活）；判定台账 42 行 pending（PG 查）；backtest backlog 140 条 B0；哨兵 allow_empty 白名单 12 表（BRK-046）
5. docs/_working/final3_campaign/p14_final_report.md §四（B 路余项清单）+a1_campaign_ledger.md §10
6. docs/_working/altdata_line/（W7 股权穿透底座：设计 100/施工 0/原料 60——只读出排期单不施工）

## §3 任务波次

**W1 疑似 bug 认领（A18，14 条）**：逐条复现→真 bug 修复+红证双向（注入红→修→绿）→非 bug 写结论留痕。优先序：SCD2×4（tests/zephyr/data/test_index_constituent_scd2.py）→循环导入（src/zephyr/infrastructure/reliability/）→撮合价×3→子进程挂起（src/zephyr/governance/ops_governance/phase_check_registry.py:77）。全路径在 test_health_report §2 C 类表。
**W2 测试真账（A17，32 条）**：3 个未登记库（domain_responsibility_layer_mapping/fail_open_register/standard_family_registry）按内收四判据裁"登记 or 退役"→decision_map R24 复发修复→governance 9 文件真账逐条处置（全路径 R3 §2）。
**W3 包①企架施工文档归置**（Owner 强迫症项，先挖后干）：
- 逐件三裁：a) 内容描述**活设计决策**且无蓝图承载→精华晋升进 docs/03_modules 对应蓝图（走 GATE-12/BLUEPRINT 门禁+module_id 锚定）；b) **历史施工记录**→git mv 归档（design_memos→archive/2026-09/design_memos/，implementation_plans 同）；c) 设计已废弃→salvage 要点后删
- **特判警示（活真源勿归档）**：design_memos/16_technical_indicator_catalog.md（v1.10.0，tilib 指标库 138 条终态目录）是 tilib 线活真源——归置时必须特判为"晋升正式资产"（建议挪 data/ 或 03_modules 蓝图区+引用面改齐），严禁顺手归档（归档误埋活件红蓝前科在案）
- 全目录清零判定后两目录本身处置（留空壳 or 删除+目录契约同步）；引用面 grep 改齐同 commit；归置台账落本战役目录
- 前置铁律：此前有"必须保留"裁定在案——本任务=Owner 2026-09-20 口头翻案（"要么蓝图要么归档"），开工先登记翻案裁定号再动
**W4 历史悬账验活核销**：staged 167/189 件逐条判归属（git log --all --find-renames 验内容是否已落地）→已落地核销/真未落地评估入册；判定台账 42 行 pending 逐行判；backlog 140 条 B0 抽验活死；allow_empty 12 表逐表收口（BRK-046）
**W5 final3 尾巴+排期出单**：
- R8 P9 池两小件：.pre-commit-config+gate_registry 的 GATE-21 已知限制文案对（mutation 连环坑——配方：拆批+同 shell env+直连）；Layer2 无 message 通道治本（gateway precommit 通道 SKIP 保护路径 hook 当 message 带 [ARCH-APPROVAL]——小代码改造+测试）
- R9 死信-0040 ALGO-FLOW 锚残留（decisiongraph_adapter.yaml 已删有锚）——清锚或登记豁免
- R10 capability 册旧路径 token 残留清理（归档迁移产生的 stale 路径，无害顺手清）+reversal.py 行1 stale 注释修正（tilib 尾巴⑥）
- R11 W7 股权穿透：读 altdata_line 设计+原料清单，切施工派工单（只出单不施工，交 Owner 决定何时点火）

## §4 硬边界
- 写域：tests/**（治理性）、docs/02 归置、注册表清欠、.pre-commit-config/gate_registry（R8 专项）；**禁碰** src/zephyr/data/**（甲线）、CH（乙线）、tasks.yaml 本体、data/strategy_intake
- 翻案前置：包① 归置开工前登记"此前保留裁定翻案"新裁定（Owner 口令=本指令）
- bug 修复禁顺手重构（只修证实的 bug+红证）

## §5 验收与回执
每件红证双向+验收命令实测数字；W3 归置=两目录终态清单（每件去向一行）+引用面零断链（DOC-REF 检查）；回执六要素；自查两轮 0+红蓝抽 5 条反查编目源。

## §6 共享纪律
同甲线 §6 浓缩段全文适用（00_master_plan §8）；另：staged 大批处置参考 final3 归档三连坑配方（doc_type 剥离/naming skip/危险文本隔字/TTL 补头）。
