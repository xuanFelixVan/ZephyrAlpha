---
ttl: task_bound
completes_when: 总筹消费完本刷新报后随 commitmap_cure 战役册转归档参考
title: F6 死信分诊刷新（手术后首扫，sid=st-f6-doctorscan-20261004）
---

# F6 死信分诊刷新报告（手术后首扫）

- 会话: st-f6-doctorscan-20261004 ｜ 扫描时刻: 2026-10-04 02:36–02:50 +0800 ｜ 扫描命令: `python scripts/governance/dead_letter_doctor.py --scan`（只读，未落 state/处方）
- 手术批三件在 HEAD 已核实: 影子收敛 5c6b196b36（21:57）｜误伤修复 5611dbf3ca（22:20）｜活性裁决表 1d291d36e5（22:50），均为 2026-10-03 +0800；手术切分点取 **22:50（三件全落地）**
- 红线遵守: 只 --scan 禁 --apply；未碰 sweep/backfill（Owner 手刹）；零提交零判定；写本报告前 claim、写后 release

## 0. 一页结论

1. **队列大盘**: 死袋 1271（F3 时点 1249 → +22）；已重投（有后继袋）252 排除待分诊；**待分诊 1019**。手续五族可治愈 **236**（23.2%）= 自动 145 + 仅处方 91；env requeue 即愈 86；不治（内容归因）697。
2. **任务单"230 只"对当前实测 236**: "230"出自施工清单#8（手术前设计稿评估口径）。doctor 本体今晚随 q-…-cure-0012 落地（13:27 +0800），**手术前无 --scan 落盘快照**，精确逐袋前后差分无基线——本报告以"设计稿 230 vs 当前实测 236"近似 + 手术后真实死亡逐袋分析替代；差值 +6 属设计稿宇宙与实测宇宙差（重投/落地使待分诊集合动态变化），非手术增减。
3. **手术后真实新增死亡 = 19 袋**（22:57–02:19），死因 Top=TAKEOVER-PENDING×6（接管显化新门，旧 Top20 无此族）；手术三件对症的旧基础设施族（NOTHING_TO_COMMIT / GateAutoRegistrationError / WinError233 / approval 误伤假杀）真实新增全部为 0。
4. **23:24 账本回放事件（假信号，已隔离）**: 23:24 +0800 单分钟 1257 条 dead_letter 写入 bottleneck_ledger，死因与各袋前记录逐字相同、session_id 全为旧死会话、dead 文件 dead_at 零移动 → 判读为**账本回放/重发而非真实再死亡**（写入者归属不下判定，留总筹）。本报告所有"手术后"统计均剔除该批。
5. **三向合并族未消灭**: 手术后仍有 1 例真实新增（02:09 mapcensus，ruling_registry.yaml）——能力册/翻译册面收敛后残余转移到裁定册面。

## 1. 产线①：手续五族可治愈清单（当前实测 236）

| 族 | 处置模式 | 袋数 | 判据（doctor 单一标记表） |
|---|---|---|---|
| creation_token | 自动（闸三限 1 次） | 96 | 死因含"无 creation_token" |
| plain_zh | 自动（闸三限 1 次） | 49 | 死因含 TRANSLATION-COVERAGE 翻译真源缺条目 |
| r5_suffix | 仅处方 | 28 | R5-DIGIT-SUFFIX 命名违规（涉改名禁自动） |
| vocab | 仅处方 | 38 | GATE-VOCAB 词表/路径硬编码 |
| depgraph | 仅处方 | 25 | NEW-FILE-DEPGRAPH-ENFORCEMENT 未登记 |
| **合计** |  | **236** | 可治愈率 23.2%（1019 待分诊） |

旁族: env_requeueable 86（requeue 即愈非 doctor 职责）= WinError233 管道×50 + ghost 存活闸拒绝×23 + GateAutoRegistrationError×4 + git reset 瞬态×4 + 其他×5；不治 697（人工排查，内容归因走 session_takeover_ledger）。

### 全量 qid 清单（236，按族）

**creation_token（CREATE-GUARD 缺 creation_token）× 96**

- q-20260923-st-chainpile-20260922-0063 ｜ q-20260923-st-datatail-20260923-0001 ｜ q-20260923-st-e2e-20260924-0008 ｜ q-20260923-st-nightdata-20260923-0002
- q-20260924-st-audit-fix-20260924-0009 ｜ q-20260924-st-audit-fix-20260924-0016 ｜ q-20260924-st-commitspeed-tbl-20260924-0022 ｜ q-20260924-st-mapbuild-20260924-0015
- q-20260924-st-mapbuild-20260924-0019 ｜ q-20260924-st-metaq-20260923-0003 ｜ q-20260924-st-pipeline-final-20260924-0016 ｜ q-20260924-st-wm1-wave0-20260924-0004
- q-20260925-st-cmd-20260924-0060 ｜ q-20260925-st-cmd-20260924-0083 ｜ q-20260925-st-cmd-20260924-0095 ｜ q-20260925-st-cmd-20260924-0104
- q-20260925-st-cmd-20260924-0116 ｜ q-20260925-st-cmd-20260924-0151 ｜ q-20260925-st-commitspeed-tbl-20260924-0035 ｜ q-20260925-st-commitspeed-tbl-20260924-0077
- q-20260926-st-ailayer-final-20260924-0019 ｜ q-20260926-st-final-build-20260926-0008 ｜ q-20260926-st-mapbuild-20260924-0034 ｜ q-20260926-st-mapbuild-20260924-0041
- q-20260927-st-final-build-20260926-0015 ｜ q-20260928-st-chief7-20260928-0017 ｜ q-20260928-st-chief7-20260928-0029 ｜ q-20260928-st-zcloseout-20260928-0047
- q-20260928-st-zcloseout-20260928-0059 ｜ q-20260928-st-zcloseout-20260928-0061 ｜ q-20260929-st-c9-f02-0002 ｜ q-20260929-st-c9-f73-0001
- q-20260929-st-chief7-20260928-0329 ｜ q-20260929-st-chief7-20260928-0405 ｜ q-20260929-st-chief7-20260928-0563 ｜ q-20260929-st-chief7-20260928-0687
- q-20260929-st-chief7-20260928-0759 ｜ q-20260929-st-chief7-20260928-0767 ｜ q-20260929-st-chief7-20260928-0839 ｜ q-20260929-st-chief7-20260928-0861
- q-20260929-st-chief7-20260928-0901 ｜ q-20260929-st-chief7-20260928-0994 ｜ q-20260929-st-chief7-20260928-1003 ｜ q-20260929-st-chief7-20260928-1030
- q-20260929-st-matrix-revive6-20260928-0001 ｜ q-20260929-st-matrix-revive7-20260928-0001 ｜ q-20260929-st-nightclean-20260929-0004 ｜ q-20260929-st-nightclean-20260929-0026
- q-20260929-st-nightclean-20260929-0033 ｜ q-20260929-st-nightsweep-sw18-20260929-0017 ｜ q-20260929-st-nightsweep-sw18-20260929-0030 ｜ q-20260929-st-nightsweep-sw4-20260929-0002
- q-20260929-st-tailwork4-20260928-0001 ｜ q-20260929-st-tailwork5-20260928-0001 ｜ q-20260929-st-tailwork6-20260928-0001 ｜ q-20260929-st-tailwork7-20260928-0001
- q-20260930-st-c9-close4-0002 ｜ q-20260930-st-c9-final-0006 ｜ q-20260930-st-chief7-20260928-1069 ｜ q-20260930-st-chief7-20260928-1073
- q-20260930-st-chief7-20260928-1077 ｜ q-20260930-st-chief7-20260928-1084 ｜ q-20260930-st-chief7-20260928-1088 ｜ q-20260930-st-menu-t1b5-20260930-0003
- q-20260930-st-menu-t1b6-20260930-0001 ｜ q-20260930-st-nightclean-20260929-0034 ｜ q-20260930-st-nightclean-20260929-0040 ｜ q-20260930-st-zc9-lane-fin-20260930-0010
- q-20261001-st-ffchief-20261001-0015 ｜ q-20261001-st-ffchief-20261001-0017 ｜ q-20261001-st-ffchief-20261001-0038 ｜ q-20261001-st-ffchief-20261001-0065
- q-20261001-st-ffchief-20261001-0070 ｜ q-20261001-st-ffchief-20261001-0073 ｜ q-20261001-st-ffchief-20261001-0075 ｜ q-20261001-st-ffchief-20261001-0076
- q-20261001-st-ffchief-20261001-0077 ｜ q-20261001-st-ffchief-20261001-0086 ｜ q-20261001-st-ffchief-20261001-0090 ｜ q-20261001-st-ffchief-20261001-0101
- q-20261001-st-ffchief-20261001-0103 ｜ q-20261001-st-ffchief-20261001-0108 ｜ q-20261001-st-ffchief-20261001-0111 ｜ q-20261001-st-ffchief-20261001-0113
- q-20261001-st-ffchief-20261001-0116 ｜ q-20261001-st-ffchief-20261001-0117 ｜ q-20261001-st-ffchief-20261001-0118 ｜ q-20261001-st-lanech-main-20261001-0002
- q-20261001-st-lanech-main-20261001-0003 ｜ q-20261001-st-matrix-final-20260930-0026 ｜ q-20261001-st-menu-w3h-20260930-0003 ｜ q-20261001-st-storageswap-20260930-0021
- q-20261002-st-chief7-20260928-2093 ｜ q-20261002-st-ffchief-20261002-0004 ｜ q-20261003-st-sC-surgery-20261003-0002 ｜ q-20261004-st-gomap-f2m-20261003-0001

**plain_zh（翻译册缺大白话条目（plain_zh））× 49**

- q-20260923-st-emoreplay-20260923-0002 ｜ q-20260923-st-xhs-full-20260922-0053 ｜ q-20260924-st-mapbuild-20260924-0007 ｜ q-20260924-st-mapbuild-20260924-0008
- q-20260924-st-mapbuild-20260924-0009 ｜ q-20260924-st-mapbuild-20260924-0013 ｜ q-20260924-st-mapbuild-20260924-0014 ｜ q-20260924-st-mapbuild-20260924-0018
- q-20260924-st-metaq-20260923-0020 ｜ q-20260924-st-pipeline-final-20260924-0029 ｜ q-20260925-st-audit-fix-20260924-0037 ｜ q-20260925-st-cmd-20260924-0048
- q-20260925-st-cmd-20260924-0147 ｜ q-20260925-st-commitspeed-tbl-20260924-0034 ｜ q-20260925-st-commitspeed-tbl-20260924-0122 ｜ q-20260926-st-commitspeed-tbl-20260924-0139
- q-20260926-st-final-build-20260926-0002 ｜ q-20260926-st-final-build-20260926-0004 ｜ q-20260926-st-final-build-20260926-0007 ｜ q-20260926-st-mapbuild-20260924-0030
- q-20260926-st-mapbuild-20260924-0031 ｜ q-20260926-st-mapbuild-20260924-0036 ｜ q-20260926-st-mapbuild-20260924-0037 ｜ q-20260926-st-mapbuild-20260924-0038
- q-20260927-st-chief3b-20260926-0008 ｜ q-20260927-st-final-build-20260926-0019 ｜ q-20260927-st-final-build-20260926-0022 ｜ q-20260927-st-final-build-20260926-0027
- q-20260928-chieflease-dispatch-20260928-0001 ｜ q-20260928-chieflease-dispatch-20260928-0002 ｜ q-20260928-st-c8-revive-0021 ｜ q-20260928-st-gpu-conv-20260928-0001
- q-20260928-st-s52-20260928-0001 ｜ q-20260928-st-s52-20260928-0002 ｜ q-20260928-st-secbatch-dispatch-20260928-0001 ｜ q-20260928-st-zcloseout-20260928-0022
- q-20260928-st-zcloseout-20260928-0026 ｜ q-20260929-st-c9-f02-0001 ｜ q-20260929-st-c9-f43-0002 ｜ q-20260929-st-c9-purify-0001
- q-20260930-st-c9-close4-0010 ｜ q-20260930-st-c9-f43-0001 ｜ q-20260930-st-c9-f43-0002 ｜ q-20260930-st-c9-final3-0001
- q-20260930-st-gpu-final7-20260929-0008 ｜ q-20260930-st-matrix-final-20260930-0005 ｜ q-20260930-st-zc9-lane-fin-20260930-0005 ｜ q-20260930-st-zcloseout-20260928-0104
- q-20261001-st-menu-w3h-20260930-0009

**r5_suffix（R5 数字后缀命名）× 28**

- q-20260923-st-deepclean-20260923-0001 ｜ q-20260923-st-e2e-20260924-0005 ｜ q-20260923-st-nightfix-20260923-0009 ｜ q-20260925-st-cmd-20260924-0036
- q-20260925-st-cmd-20260924-0038 ｜ q-20260925-st-cmd-20260924-0047 ｜ q-20260925-st-cmd-20260924-0118 ｜ q-20260925-st-cmd-20260924-0123
- q-20260926-st-audit-fix-20260924-0047 ｜ q-20260926-st-ff-chfail-20260926-0001 ｜ q-20260927-st-c7-resc-20260927-0003 ｜ q-20260927-st-pqmine-20260927-0003
- q-20260927-st-pqmine-20260927-0005 ｜ q-20260928-chiefzc-docs2-dispatch-20260928-0001 ｜ q-20260928-chiefzc-surgeon-20260928-0004 ｜ q-20260928-st-zcloseout-20260928-0029
- q-20260928-st-zcloseout-20260928-0050 ｜ q-20260929-st-nightsweep-sw1-20260929-0012 ｜ q-20260929-st-nightsweep-sw1-20260929-0013 ｜ q-20260929-st-tailwork3-20260928-0001
- q-20261001-st-ffchief-20261001-0013 ｜ q-20261001-st-ffchief-20261001-0021 ｜ q-20261001-st-ffchief-20261001-0024 ｜ q-20261001-st-storageswap-20260930-0011
- q-20261001-st-storageswap-20260930-0013 ｜ q-20261002-st-ffchief-20261002-0001 ｜ q-20261002-st-ffchief-20261002-0002 ｜ q-20261003-st-commitmap-chief-20261003-0002

**vocab（GATE-VOCAB 词表/路径硬编码）× 38**

- q-20260923-st-chainpile-20260922-0065 ｜ q-20260923-st-chainpile-20260922-0069 ｜ q-20260924-st-chainpile-20260922-0072 ｜ q-20260924-st-chainpile-20260922-0073
- q-20260924-st-chainpile-20260922-0076 ｜ q-20260924-st-chainpile-20260922-0077 ｜ q-20260924-st-pipeline-final-20260924-0012 ｜ q-20260929-st-zc9-lane-rev-20260929-0001
- q-20260930-st-chief7-20260928-1246 ｜ q-20260930-st-chief7-20260928-1280 ｜ q-20260930-st-chief7-20260928-1286 ｜ q-20260930-st-chief7-20260928-1297
- q-20260930-st-chief7-20260928-1304 ｜ q-20260930-st-chief7-20260928-1310 ｜ q-20260930-st-chief7-20260928-1321 ｜ q-20260930-st-chief7-20260928-1331
- q-20260930-st-chief7-20260928-1356 ｜ q-20260930-st-chief7-20260928-1378 ｜ q-20260930-st-chief7-20260928-1381 ｜ q-20260930-st-chief7-20260928-1382
- q-20260930-st-chief7-20260928-1383 ｜ q-20260930-st-chief7-20260928-1395 ｜ q-20260930-st-chief7-20260928-1398 ｜ q-20260930-st-chief7-20260928-1404
- q-20260930-st-chief7-20260928-1416 ｜ q-20260930-st-chief7-20260928-1545 ｜ q-20260930-st-chief7-20260928-1567 ｜ q-20260930-st-chief7-20260928-1585
- q-20260930-st-chief7-20260928-1597 ｜ q-20260930-st-matrix-revive12-20260929-0001 ｜ q-20260930-st-matrix-revive12-20260929-0002 ｜ q-20261001-st-ffchief-20261001-0088
- q-20261001-st-ffchief-20261001-0098 ｜ q-20261002-st-ffchief-20261001-0126 ｜ q-20261002-st-ffchief-20261001-0130 ｜ q-20261002-st-ffchief-20261001-0137
- q-20261002-st-ffchief-20261001-0138 ｜ q-20261003-st-sC-surgery-20261003-0006

**depgraph（DEPGRAPH 未登记）× 25**

- q-20260925-st-cmd-20260924-0149 ｜ q-20260925-st-wm1-wave0-20260924-0031 ｜ q-20260929-st-c9-f02-0005 ｜ q-20260929-st-gpu-final5-20260929-0001
- q-20260929-st-matrix-revive-20260928-0001 ｜ q-20260929-st-secbatch-dispatch5-20260928-0001 ｜ q-20260930-st-chief7-20260928-1363 ｜ q-20261002-st-chief7-20260928-2066
- q-20261002-st-chief7-20260928-2085 ｜ q-20261002-st-chief7-20260928-2117 ｜ q-20261002-st-chief7-20260928-2120 ｜ q-20261002-st-chief7-20260928-2136
- q-20261002-st-chief7-20260928-2139 ｜ q-20261002-st-chief7-20260928-2154 ｜ q-20261002-st-chief7-20260928-2155 ｜ q-20261002-st-chief7-20260928-2158
- q-20261002-st-chief7-20260928-2159 ｜ q-20261002-st-chief7-20260928-2166 ｜ q-20261002-st-chief7-20260928-2170 ｜ q-20261002-st-chief7-20260928-2174
- q-20261002-st-chief7-20260928-2176 ｜ q-20261002-st-chief7-20260928-2180 ｜ q-20261002-st-ffchief-20261001-0136 ｜ q-20261003-st-sC-surgery-20261003-0008
- q-20261004-st-sC-surgery-20261003-0010

## 2. 产线②：死因 Top20 刷新与手术前后对比

**口径警示（必读）**: F3 旧 Top20 = bottleneck_ledger dead_letter **历史累计**（qid 去重 3610，含已重投/已落地袋）；本刷新主表 = **当前死队列待分诊 1019 袋**的现有死因。两宇宙不同，下降≠全部治本（重投落地也带走存量）。故每族配"手术后真实新增"列：只有旧族存量↓ **且** 手术后真实新增=0 才够格称"消灭候选"。

### 表 A：当前死队列归一化死因 Top20（待分诊 1019 袋）

| # | 袋数 | 归一化死因首行 |
|---|---|---|
| 1 | 117 | 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文件的违规（裁定#<n |
| 2 | 49 | 网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: <num> 个新建 .py 文件在翻译真源（module_translat |
| 3 | 45 | 网关落盘失败（COMMIT_FAILED）: 门禁 COMPLEXITY-GUARD 阻断: [NO-HIGH-COMPLEXITY] NO-HIGH-COMPLEXITY：检测到高循环复杂度函数（><num>）， |
| 4 | 44 | landing 异常: OSError: [WinError <num>] 管道的另一端上无任何进程。 |
| 5 | 26 | 网关落盘失败（COMMIT_FAILED）: 门禁 PERMANENT-SYSTEM-TRIGGER 阻断: [MANUAL-ONLY-PERMANENT] 永久系统脚本使用 manual 触发模式（argparse/i |
| 6 | 21 | 网关落盘失败（COMMIT_FAILED）: 门禁 MSG-EXPOSURE 阻断: 错误消息暴露敏感信息（路径/tx_id/凭据/连接串等应放入 details 字段而非消息文本，<num>.<num>.<num> 治 |
| 7 | 19 | 网关落盘失败（COMMIT_FAILED）: 门禁 DEPGRAPH-ENFORCEMENT 阻断: [NEW-FILE-DEPGRAPH-ENFORCEMENT] NEW-FILE-DEPGRAPH-ENFORCEME |
| 8 | 16 | 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-VOCAB 阻断: [VOCAB-CHAIN] 新增 .py 文件含 SSoT 路径硬编码（应通过 capability_canonical_file_reg |
| 9 | 14 | docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml: 自证读回无法判别（docs/01_policies_ |
| 10 | 12 | 网关落盘失败（COMMIT_FAILED）: 门禁 TEST-SOURCE-CONSISTENCY 阻断: TEST-SOURCE-CONSISTENCY (§<num>.<num>)：检测到测试-源码符号漂移 |
| 11 | 12 | 网关落盘失败（COMMIT_FAILED）: 门禁 ALGO-FLOW-LINK 阻断: ALGO-FLOW-LINK：<num> 处 ALGO_FLOW 锚/卡片链接断裂——external 锚指向的 yaml 必须存 |
| 12 | 11 | 网关落盘失败（COMMIT_FAILED）: 门禁 IMPORT-INTEGRITY 阻断: IMPORT-INTEGRITY: 悬空 import（目标模块不可解析，#ARCH-CROSS-COMMIT-ATOMICI |
| 13 | 11 | 网关落盘失败（COMMIT_FAILED）: 门禁 BARE-SUBPROCESS 阻断: BARE-SUBPROCESS：检测到裸 subprocess.run/Popen/check_output/check_cal |
| 14 | 10 | 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-VOCAB 阻断: [VOCAB-HARDCODE] 新增 .py 文件含词表硬编码（应从 *_vocabulary.yaml 动态加载）: .runtime |
| 15 | 10 | landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_standards/_registry/catalogs/rulin |
| 16 | 10 | 网关落盘失败（COMMIT_FAILED）: 门禁 SSOT-REDEFINITION 阻断: SSoT 符号重复定义（硬阻断）： |
| 17 | 10 | 网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 新建 .py 查功能关键词命中在册能力（波13·包13.<num>，判为第二真源）: scripts/governance/d5_ar |
| 18 | 9 | 网关落盘失败（COMMIT_FAILED）: 门禁 DIRECTORY-CONTRACT 阻断: [GATE-DIRECTORY-CONTRACT] <num> 个发现（<num> errors, <num> warni |
| 19 | 9 | 网关落盘失败（COMMIT_FAILED）: 门禁 TTL-METADATA 阻断: FAIL: .runtime\commit_queue\worktree\docs\_working\decision_map_cam |
| 20 | 9 | 网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 新建 .py 查功能关键词命中在册能力（波13·包13.<num>，判为第二真源）: scripts/governance/data_ |

### 表 B：F3 旧 Top20 逐族现状对照

| 旧# | 旧累计 | 旧死因族 | 当前存量 | 术后真实新增 | 判读 |
|---|---|---|---|---|---|
| 1 | 370 | GATE-PRECOMMIT-RUN 包装块阻断 | 126 | 0 | 仍活跃（现役头号杀手） |
| 2 | 90 | TRANSLATION-COVERAGE | 49 | 0 | 仍活跃（49 只已入 plain_zh 可治愈） |
| 3 | 80 | landing GateAutoRegistrationError | 4 | 0 | 基本清空（残余 4 全 env 即愈，术后零新增） |
| 4 | 76 | COMPLEXITY-GUARD / NO-HIGH-COMPLEXITY | 52 | 0 | 仍活跃 |
| 5 | 71 | landing WinError 233 管道 | 50 | 0 | 存量全 env 即愈，术后零新增 |
| 6 | 62 | 三向合并失败·capability 册 | 27 | 1 | **未消灭**：术后 1 例真实新增（02:09 ruling_registry.yaml） |
| 7 | 57 | NOTHING_TO_COMMIT 快照未真应用 | 2 | 0 | **消灭候选**（影子收敛 5c6b196b36 对症；残余 2） |
| 8 | 48 | ALGO-NOTE-SYNC | 0 | 0 | Top20 消失（当前队列 0） |
| 9 | 43 | DANGLING-REFERENCE | 0 | 0 | Top20 消失（当前队列 0） |
| 10 | 42 | 三向合并失败·module_translation 册 | 27 | 1 | 并入三向合并族同上 |
| 11 | 40 | IMPORT-INTEGRITY | 11 | 0 | 萎缩 |
| 12 | 35 | NEW-FILE-DEPGRAPH-ENFORCEMENT | 25 | 0 | 萎缩（25 只入 depgraph 可治愈） |
| 13 | 33 | REGISTRY-MASS-DELETION | 0 | 0 | Top20 消失（当前队列 0） |
| 14 | 33 | PERMANENT-SYSTEM-TRIGGER | 32 | 0 | 仍活跃 |
| 15 | 31 | TEST-SOURCE-CONSISTENCY | 12 | 0 | 萎缩 |
| 16 | 29 | PROTECTED-PATHS | 8 | 0 | 萎缩（误伤修复 5611dbf3ca 对症 approval 面；术后零新增） |
| 17 | 29 | SSOT-REDEFINITION | 11 | 0 | 萎缩 |
| 18 | 28 | NO-HIGH-COMPLEXITY（裸名变体） | 52 | 0 | 与旧#4 同族合计口径 |
| 19 | 28 | MSG-EXPOSURE | 21 | 0 | 萎缩 |
| 20 | 27 | MUTABLE-CONST-WITHOUT-FINAL | 7 | 0 | 萎缩 |

注: "当前存量"按当前队列死因串含门禁名/特征词聚合；旧#4+旧#18 在新表合并计 52（COMPLEXITY-GUARD 包装名与裸名两形态）。

### 表 C：手术后真实新增死亡 19 袋（22:57–02:19，逐袋）

| 死亡时刻(+0800) | 属主会话 | 袋（尾段） | 死因族 |
|---|---|---|---|
| 2026-10-03 22:57 | st-sC-surgery-20261003 | …-sC-0005 | DOC-HEADER-SUITE [TTL-METADATA]（worktree 内 tests 缺 ttl） |
| 2026-10-03 23:00 | st-tdm-mount-flash-20261003 | …-tdm-0002 | TAKEOVER-PENDING（命中 open 接管条目） |
| 2026-10-03 23:06 | st-sC-surgery-20261003 | …-sC-0006 | GATE-VOCAB [VOCAB-CHAIN] SSoT 路径硬编码 |
| 2026-10-03 23:17 | st-sC-surgery-20261003 | …-sC-0007 | MSG-STYLE 错误消息标点风格 |
| 2026-10-03 23:20 | st-tdm-mount-flash-20261003 | …-tdm-0004 | TAKEOVER-PENDING |
| 2026-10-03 23:23 | st-fig13-chief-20261003 | …-fig13-0001 | TAKEOVER-PENDING |
| 2026-10-03 23:31 | st-sC-surgery-20261003 | …-sC-0008 | DEPGRAPH-PRE-REGISTRATION 滞后 |
| 2026-10-03 23:35 | st-tdm-mount-flash-20261003 | …-tdm-0005 | TAKEOVER-PENDING |
| 2026-10-03 23:38 | st-fig13-chief-20261003 | …-fig13-0002 | TAKEOVER-PENDING |
| 2026-10-04 00:25 | st-sC-surgery-20261003 | …-sC-0009 | IMPORT-INTEGRITY 悬空 import |
| 2026-10-04 00:31 | st-vm12surg-20261003 | …-vm12surg-0001 | ALGO-FLOW-LINK 锚断裂 |
| 2026-10-04 01:10 | st-mapreg-20261003 | …-mapreg-0003 | CLAIM_REQUIRED_VIOLATION 未 claim |
| 2026-10-04 01:14 | st-chief-mount-20261003 | …-chief-mount-0002 | 路径锁等待超时（capability 册同路径在途） |
| 2026-10-04 01:40 | st-vm12e-20261004 | …-vm12e-0001 | CLAIM_REQUIRED_VIOLATION 未 claim |
| 2026-10-04 01:42 | st-sC-surgery-20261003 | …-sC-0010 | DEPGRAPH-PRE-REGISTRATION 滞后 |
| 2026-10-04 01:47 | st-gomap-f1-20261003 | …-gomap-f1-0002 | ghost_session 自动重投被存活闸拒绝（设计内拒绝行为） |
| 2026-10-04 01:52 | st-vm12e-20261004 | …-vm12e-0003 | TAKEOVER-PENDING |
| 2026-10-04 02:09 | st-mapcensus-20260924 | …-mapcensus-0017 | 三向合并失败（ruling_registry.yaml） |
| 2026-10-04 02:19 | st-vm12f2-20261003 | …-vm12f2-0001 | TAKEOVER-PENDING |

术后 19 袋族构成: TAKEOVER-PENDING×6 ＞ sC-surgery 施工迭代×6（六种不同门，逐袋修进）＞ CLAIM_REQUIRED×2 ＞ ghost 存活闸×1 / 路径锁×1 / 三向合并×1 / ALGO-FLOW-LINK×1。**无一例命中手术三件对症的旧基础设施族**——手术对症面术后零复发，新死亡全部来自内容/手续/新门位。

### 23:24 账本回放事件档案（不计入统计）

- 23:24:05 +0800 单分钟写入 1257 条 dead_letter（bottleneck_ledger），加零星 9 条后账本停更于 23:38（此后 00:25–02:19 的真实死亡只落 dead 文件、未进账本——**账本写入疑似停更，附观察**）。
- 证据: 1257 条与各袋前记录死因逐字相同（同袋前后对比 same=1251 / changed=0）；session_id 全为旧死会话原值；1271 个 dead 文件中仅 19 个 dead_at 在术后。
- 判读: 账本回放/重发（如 ledger 重演验证），非真实再死亡；写入者归属**不下判定**，留总筹。

## 3. 产线③：八袋逐袋诊断（q-20261003-st-deadletter-cure-20261003-0004..0011）

总判: 八袋=**一条重投链的中段**，属主会话 st-deadletter-cure-20261003（doctor 立法会话）。当前 doctor 分诊全部为"已重投（有后继）"=排除待分诊；链尾 **-0012（doctor 本体+车道BCD合流批）与 -0013（测试改名补丁）均已 done 落地**，八袋内容全部被后继袋收编，**当前无需任何处方或重投**。

| 袋 | 死亡(+0800) | ledger 族 | 复发计数 | 死因 | 重投去向 | 当前诊断 |
|---|---|---|---|---|---|---|
| -0004 | 12:50 | env | 23 | ghost_session：属主会话已死，自动重投被存活闸拒绝（裁定#459） | → -0005（12:51） | 已重投；doctor 族=env_requeueable；内容经后继链于 -0012/-0013 落地 |
| -0005 | 12:58 | item | 61 | DOC-HEADER-SUITE [MODULE-ID-CONSISTENCY] MOD-GOV-046 多文件碰撞 | → -0006（13:01） | 已重投；doctor 族=untreatable（内容）；内容经后继链于 -0012/-0013 落地 |
| -0006 | 13:01 | env | 24 | ghost_session（同 -0004） | → -0007（13:02） | 已重投；doctor 族=env_requeueable；内容经后继链于 -0012/-0013 落地 |
| -0007 | 13:02 | env | 25 | ghost_session（同 -0004） | → -0008（13:03） | 已重投；doctor 族=env_requeueable；内容经后继链于 -0012/-0013 落地 |
| -0008 | 13:03 | env | 26 | ghost_session（同 -0004） | → -0009（13:04） | 已重投；doctor 族=env_requeueable；内容经后继链于 -0012/-0013 落地 |
| -0009 | 13:11 | item | 62 | MODULE-ID-CONSISTENCY 同碰撞复发 | → -0010（13:12） | 已重投；doctor 族=untreatable（内容）；内容经后继链于 -0012/-0013 落地 |
| -0010 | 13:18 | item | 63 | NEW-FILE-DEPGRAPH-ENFORCEMENT：dead_letter_doctor.py 无 depgraph 登记 | → -0011（13:19） | 已重投；doctor 族=depgraph（可治愈族）；内容经后继链于 -0012/-0013 落地 |
| -0011 | 13:26 | item | 64 | NO-SECRET-HARDCODE：doctor 源码 TOKEN="creation_token" 测试值文本误伤（-0013 已改名绕行） | → -0012（13:27） | 已重投；doctor 族=untreatable（内容·文本误伤）；内容经后继链于 -0012/-0013 落地 |

链形态判读（供总筹参考，不下判定）: ghost 三连（-0006/07/08 约一分钟一死）正是 8 套活性机制互斗的实弹样本=活性裁决表（1d291d36e5）的立法病灶；-0010/-0011（depgraph 未登记 + 源码测试值被密钥门文本误杀）正是 doctor 五族与 NO-SECRET 误伤面的立法病灶——八袋即 doctor/活性表两件治本的"病历本"。链从 -0004（ghost 族，recurrence=23）到链尾 -0012 落地共用约 37 分钟。

## 4. 留给总筹的观察项（零判定）

1. 23:24 账本回放写入者与动机；账本 23:38 后停更（真实死亡未进账本）需确认是否轮换/写入器下岗。
2. TAKEOVER-PENDING 成术后头号新杀手（×6）：open 接管条目与活跃会话提交的冲突面是否需要豁免通道，属政策门位。
3. 三向合并族残余（ruling_registry 面）与 chief-mount 的 capability 册路径锁等待，同指"热册单点串行"未解。
4. doctor --apply 未执行（Owner 手刹范围）：236 只可治愈的受控执行时机待总筹/Owner 定。

---

判定权归总筹。
