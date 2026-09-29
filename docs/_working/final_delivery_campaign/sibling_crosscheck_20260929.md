---
created: 2026-09-29
ttl: task_bound
title: 兄弟施工队 2026-09-29 落地袋交叉验证报告（矿道 M7）
session: st-finaldel-m7-20260929
---

# 兄弟施工队落地袋交叉验证（2026-09-29，M7）

验证者会话：st-finaldel-m7-20260929。只跑测试与只读命令，零文件修改（本报告为唯一产出）。
验证窗口：约 13:05-13:35（本地）。期间 HEAD 由 31c38c5205 移动至 3942796dba（merge train 落袋 CNS-14 增量），已对涉测文件逐一做 disk==HEAD==袋版本 三方核对（见各袋注记）。
环境：Python 3.12.8（RULE-ENV 已修正），pytest 8.4.2，reaper 存活（last_run=2026-09-29 12:57:34，RULE-GUARDIAN 满足）。

## 逐袋结论

| # | commit | 声明 | 实测 | 判定 |
|---|--------|------|------|------|
| 1 | 972c080450 (sw16 词表豁免闭环+探针去手工计数) | 单文件 23 passed；yaml 含 registry_alignment.py:700 豁免 | 23 passed in 61.57s（tests/governance/scripts_governance/test_check_vocab_hardcode.py）；noqa_exempt_registry.yaml 944-946 行 no_vocab_source 豁免在册（file+line:700 分字段）；disk==HEAD==袋内容（纯 CRLF 行尾差异） | PASS |
| 2 | cad41feb2f (sw11/sw12 备份三小件 H04/H06/H08) | 104+75 测试绿 | 触碰面三文件实测 3+29+72=104 passed 全绿（copy_share 3 / restore_drill 29 / reaper 72），零失败；"+75"=reaper 72+copy_share 3 自洽（总数口径一致）；tests/dr+tests/backup 全目录 133P+9F，9 红全在 test_stage3_vault_mtime_and_verdict.py=他会话未跟踪在途 WIP（不在 HEAD），非本袋责任；注：reaper 源盘面含他会话 +52 行纯增量 WIP（session closeout，不动 H08 匹配逻辑） | PASS |
| 3 | cf16fa43fd (st-gpup1 GPU P1+L1 接线) | 121 passed+位证全 PASS | wiring 文件 7 例=5P+2S（skip 原因"cupy/CUDA 不可用"——gpu_core.py 未随袋落地属 conv4 在途资产，本机 torch CUDA 在位但无 cupy，skip 属设计内）；c4 六套件实测 97P+5F：5 红全在 TestRunBatchStageCostWiring（ValueError: not enough values to unpack (expected 9, got 7)）——本袋把 _load_engine 改 9 元组并只同步了 test_factory_grid_executor.py 桩，漏同步 test_factory_grid_stage_cost_tiers.py（其 _stub_engine 仍返 7 元组，盘面==HEAD=落地红）；"parity 11 例"非 HEAD 资产（袋自披露一：conv4 在途），"121 passed 全绿"在 HEAD 不可复现 | PARTIAL |
| 4 | 6d3a221055 (sw16 测试契约漂移治本) | 3 passed | 3 passed in 0.62s（writer fake 注入零 DB，无生产表写入迹象）；disk==HEAD==袋版本 | PASS |
| 5 | 75bdc25470 (nightclean F107 开簿) | 08_f107_rollback_recovery.md 在 HEAD 且双 guard 头注死锚发现记录 | 文件在 HEAD（实际路径 docs/_working/fullflow_mining/m3_governance/08_f107_rollback_recovery.md，非任务书猜测的 governance_sop 下），由本袋提交；双 guard（git_guard.py:5 / post_checkout_guard.py:7）死锚发现记录在 §1 接线向+§2 在册。瑕疵：doc 自审闸勾选"[x] 死引用修复落地（2 锚，随袋提交）"且正文称"已修"，但 HEAD 实测两锚仍指不存在的 zephyr.infrastructure.rollback.concurrency_guard（真身=runtime.concurrency_guard，:64 import 实证）——与袋 commit 自己的拆袋披露（锚修复未随袋，随容量治理批落地）矛盾，doc 面未同步 | PASS（带 doc 一致性瑕疵） |

## 袋 3 红证细节（供修复班直接定位）

- 失败：tests/backtest/test_factory_grid_stage_cost_tiers.py::TestRunBatchStageCostWiring 5 例（test_default_run_no_cost_artifacts_and_no_scan_call / test_t1_two_tier_scan_wired_end_to_end / test_t2_full_five_tier_scan / test_scan_failure_is_gate_negative_not_silent_skip / test_list_input_tiers_accepted_and_normalized）。
- 报错：ValueError: not enough values to unpack (expected 9, got 7)。
- 根因：HEAD scripts/backtest/factory_grid_executor.py:721 对 _load_engine() 做 9 元组解包（cf16fa43fd 改）；test_factory_grid_stage_cost_tiers.py:419 _stub_engine 返 7 元组（:418 注释自证"st-ddup-20260925 适配 7 元组"）。该测试文件最后落地版本停在 5ea9d261a（st-ddup T3 桩适配，27 测试绿），cf16fa43fd 未同步它。
- 判定：修法机械（桩补 2 元素或 *args 吸收，与 test_factory_grid_executor.py 同款），非设计缺陷；但"六套件全绿"声明与 HEAD 事实不符，属袋级质量漏检（兄弟队落袋前回归面没跑全 consumer 桩套件）。

## 环境与污染注记（影响解读的现场事实）

1. 共享主区多会话活跃：reaper 报 worktree_changes=761；验证期间目睹 tests/dr/test_backup_copy_share.py 出现"index staged 删除+盘上同名 untracked"形态、两个测试文件 MM 簿记——三方 diff 证实内容均 ==HEAD==袋版本，属 index 陈旧簿记非内容漂移。
2. 未跟踪在途 WIP 会卷入目录级跑测：test_stage3_vault_mtime_and_verdict.py（9 红，ValueError: substring not found 系对 backup.ps1 旧标记子串断言）与 tests/backtest/ 下十余个 ?? 测试文件均为他会话在途件，本报告所有计数已按"文件级三方核对"剥离其影响。
3. 本机 GPU：torch 2.13.0+cu126、CUDA available（RTX 3090 在位）；cupy 未安装。袋 3 GPU 用例的 skip 由 gpu_core 缺件（HEAD 未落）与 cupy 缺失双因构成，属袋内设计内 skip，但意味着 GPU parity 红绿在 HEAD 状态下本机不可测（需 conv4 基座袋落地+cupy 环境）。

## 今日全袋清点（git log --since=2026-09-29T00:00）

截至验证末实测 94 个提交（含 merge train 与 reconciler 自动提交，持续增长中）。已验证 5 袋见上表。未覆盖部分按车道归组，未验证原因一行一条：

- 775ea32b60 (sw16 时序炸弹2件)：未验证——非任务书指派袋；其②与袋4同文件且袋4已绿，①evolution_chain_e2e 留属主矿道。
- 98ce6370c5 (sw4 红五簇撞号修复，声明 134 passed)：未验证——非指派袋，gate 注册簇属执法面专项。
- 81d85b9a77 / 496291460e / ea0b362d0c (sw15 三件)：未验证——非指派袋（G-81 墓碑/W-135 触发面改型/行数核验）。
- ced0f780bf (c9-tzday F62 时区锚)、082d4591e7 / e21ebc03ec (c9-f34 L9 接线，自披露 12F 基线红)：未验证——非指派袋，L9 缺省阈值待 Owner 签批本身即未定态。
- 3b64ce98e2 (ignite AI 点火三件)：未验证——主体为 DB 侧操作（DDL/HT 登记/ps1 DryRun），无测试面可跑。
- 4970433e97 (w173 prereg budget_caps)：未验证——measured 0.53s 需 GPU 车道真跑，非本矿道环境职责。
- aecd7c1a3e (trae032 修正批)、2d34f7b2dc / 65b7c8d9ef (sw1 文档案卷)、16087873ed / c264c426ba / f4a28788c1 / 3436a9e2e4 (载体/册先行)、d094852ffa (R5 改名重投)：未验证——纯登记/载体/文档面，无独立测试断言可复跑。
- f79a88a11e / 3c01517bb2 (zc9 etf_benchmark 源码/测试拆袋)、cc730f6474 (gov_audit 锁 v2 源码件)：未验证——非指派袋（测试件袋自称后继单投）。
- e040583b5e / 233adc3cca (sw2 E13/E09)、35ca1d69cd / 794f16569b (sw5 F62/F125-130 重投)、3cb98bb6f6 (sw9)、609cdceef0 (zcloseout)、31c38c5205 / 1042b6d9e2 (sw11 载体/文案)、2ee8ec84ef (sw12 恒红修)、46063bade4 / 75bdc25470 其余 nightclean 件、3942796dba (SW14 CNS-14)、e15eadc5f3 (日检 ops)、9f220b2e7e / a2881d059e (reconciler 自动提交)：未验证——非任务书指派对象（M7 范围=上表 5 袋），reconciler 自动提交无独立袋声明可验。

## 总体判定

兄弟队今日成果可信度：高（4/5 袋全过，数字声明逐位复现；袋 3 代码主体真、但套件影响面漏检+头条数字在 HEAD 不可复现）。

- 数字诚实度：袋 1/2/4 的 passed 数字与声明精确吻合（23/104/3），无注水迹象；袋 2 在共享区污染环境下仍可完整复现，落地纪律（红绿对拍+三方文件可追溯）扎实。
- 袋 3 教训：改共享签名（_load_engine 9 元组）时对 consumer 桩套件的同步只做了自己名下文件——"121 passed 全绿"是作者工作树态（含 conv4 在途资产）而非 HEAD 态，建议此类跨文件签名变更强制列 consumer 套件清单随袋跑。
- 袋 5 教训：拆袋披露（commit message）诚实，但落袋文档正文/自审闸未随拆袋回改（"已修/随袋提交"在 HEAD 为假），文档面与 git 面出现单袋内自相矛盾。
- 待办移交：①袋 3 的 5 红需修复班补桩（机械修）；②袋 5 的 doc 自审闸两行需回改或在容量治理批落地锚修复后勾选；③他会话在途 WIP（stage3 测试 9 红、reaper +52 行）不属本报告处置范围，留现场归属原会话。
