---
ttl: task_bound
completes_when: 本线终验红蓝通过
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-V1-LINE-C
---

# 【总包丙·代码文档治理线】施工指令 v1.0（自包含，新对话整贴即用）

# sid：st-code-doc-20260921 ｜ 落盘：docs/_working/code_doc_gov_campaign/ ｜ 模型：Max 总包+Flash 分包（WO-12..16 领单）
# 上位方案：docs/_working/unified_campaign/00_master_plan_v1_0.md（§3 写域/§4 时序/§6 波次）；台账/派工单同目录

## §0 使命
①疑似真 bug 逐条认领修复（14 条）②测试真账清欠（32 条+A14 资产册）③企架两个施工文档目录归置（蓝图或归档二选一，Owner 终极强迫症项）④历史悬账验活核销（D 路四族，v0.1 丢失项）⑤final3 尾巴小件+股权穿透排期出单（含 C-4 reversal.py 尾巴）。终态=测试全绿真账清零、施工文档各归其位、悬账每条有终态。

## §1 冷启动
同甲线配方（PATH/守卫/会话注册+心跳）；裁号 re-find max+1（开工时实测——本方案班已用到 #379）。

## §2 真源读序
1. docs/_working/dataqa_audit/test_health_report.md §2/§3——A17 真账 32 条+A18 疑似 bug 14 条全路径编目（执行日逐条复现验活，报告会陈旧）
2. docs/_working/unified_campaign/p2_backlog_master_ledger_v1_0.md §4——D 路四族悬账+§2 B 路活项
3. docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/ 全目录+09_ai_architecture/implementation_plans/ 全目录——包①归置对象（现场枚举勿背数）
4. docs/03_modules/ 蓝图体系（归置目标态参照）+docs/_working/archive/ 归档区惯例
5. 悬账真源：git status staged（09-20 实测 179 件，本班收编 4 件后余约 175——逐条验活）；判定台账 42 行 pending（PG 查）；backtest backlog 140 条 B0；哨兵 allow_empty 12 表（BRK-046）
6. docs/_working/final3_campaign/p14_final_report.md §四（B 路余项）+a1_campaign_ledger.md §10
7. docs/_working/altdata_line/（W7 股权穿透底座：设计 100/施工 0/原料 60——只读出排期单不施工）
8. CH 实况自查：本线不碰 CH，仅需 df/声明板（归置批大量 git mv 与热文件竞争相关）

## §3 任务波次（对应 WO-12..16）
**W1 疑似 bug 认领（A18，14 条，WO-12）**：逐条复现→真 bug 修复+红证双向（注入红→修→绿）→非 bug 写结论留痕。优先序：SCD2×4（tests/zephyr/data/test_index_constituent_scd2.py，涉 src 数据链与甲协调甲优先）→循环导入（src/zephyr/infrastructure/reliability/）→撮合价×3→子进程挂起（src/zephyr/governance/ops_governance/phase_check_registry.py:77）。全路径在 test_health_report §2 C 类表。
**W2 测试真账（A17，32 条，WO-13，裁定#379③=独立批）**：D38 三未登记库（domain_responsibility_layer_mapping/fail_open_register/standard_family_registry）按内收四判据裁"登记 or 退役"→decision_map R24 复发修复→governance 9 文件真账逐条→battle_map 拓扑 3 条→blueprint 引用 3 条→cron 断言过期 4 条；~9 条测试污染假红修测试隔离；**A14 77 表 data_asset_registry 生成器口径重建（禁手工）**。
**W3 包①企架施工文档归置（WO-14，先挖后干）**：
- **前置铁律**：开工先登记"此前保留裁定翻案"新裁定（Owner 2026-09-20 口头翻案=本 v1.0 指令链，裁定#378 已载背景）
- 逐件三裁：a) 活设计决策→精华晋升 docs/03_modules 蓝图（GATE-12+module_id 锚定）；b) 历史施工记录→git mv 归档（archive/2026-09/design_memos/、implementation_plans 同）；c) 已废弃→salvage 要点后删
- **特判警示（活真源勿归档）**：design_memos/16_technical_indicator_catalog.md（tilib 指标库 138 条终态目录）特判晋升正式资产（甲 W4 批10 更新它——**甲先行，丙避让该单文件**）；technical_indicator_registry.yaml 同理
- 全目录清零判定后两目录本身处置（留壳 or 删+目录契约同步）；引用面 grep 改齐同 commit；归置台账落本战役目录
**W4 历史悬账验活核销（D 路，WO-15，只读先行可即刻）**：staged ~175 件逐条判归属（git log --all --find-renames 验内容是否已落地）→已落地核销/真未落地评估入册；判定台账 42 行 pending 逐行判；backlog 140 条 B0 抽验活死；allow_empty 12 表逐表收口（与甲 W3 对齐口径）。
**W5 final3 尾巴+排期出单（WO-16）**：
- R8 P9 池两小件：.pre-commit-config+gate_registry 的 GATE-21 已知限制文案对（mutation 连环坑配方=拆批+同 shell env+直连正门）；Layer2 无 message 通道治本（gateway precommit 通道 SKIP 保护路径 hook 当 message 带 [ARCH-APPROVAL]——小代码改造+测试）
- R9 死信 q-0040 ALGO-FLOW 锚残留（decisiongraph_adapter.yaml 已删有锚）——清锚或登记豁免
- R10 capability 册旧路径 token 残留清理+**reversal.py 行1 stale 注释修正（C-4，tilib 尾巴归位）**
- R11 W7 股权穿透：读 altdata_line 设计+原料清单，切施工派工单（只出单不施工，交 Owner 点火）

## §4 硬边界
- 写域：tests/**（治理性）、docs/02 归置、注册表清欠、.pre-commit-config/gate_registry（R8 专项）；**禁碰** src/zephyr/data/**（甲线）、CH（乙线）、tasks.yaml 本体、data/strategy_intake、16 号 memo（甲先行期间）
- 翻案前置：包①归置开工前登记翻案裁定；bug 修复禁顺手重构（只修证实的 bug+红证）

## §5 验收与回执
每件红证双向+验收命令实测数字；W3 归置=两目录终态清单（每件去向一行）+引用面零断链（DOC-REF 检查）；W4=悬账逐条终态表（核销/入册/作废三态）。回执六要素；自查两轮 0+红蓝抽 5 条反查编目源。

## §6 共享纪律
同甲线 §6 浓缩段全文适用（00_master_plan_v1_0 §10）；另：staged 大批处置参考 final3 归档三连坑配方（doc_type 剥离/naming skip/危险文本隔字/TTL 补头）；热文件（gate_registry/.pre-commit-config/capability 册）CAS+git add 刷新。
