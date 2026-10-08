---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: 审计闭合夜战 W2 五车道按本表全部挖干施工并经 W3 循环检查两轮零失败后归档
---

# 审计闭合夜战 · 挖矿工作项总表（车道 M / st-acure-m1）

> 输入=`docs/_working/external_audit_mastertc/`（00_audit_report.md + lane_a~h 八份）。
> 审计基线 HEAD=`649a8c93c7`（2026-10-07 20:47）；**挖矿基线 HEAD=`f82008eb25`（2026-10-08 00:53，新鲜复跑时点）**。
> 挖干判据=每卡六向台账（①卡面处方②HEAD 现状实证③上游依赖④下游消费者⑤冲突面⑥残余移交）+自审闸三态（GREEN 挖干/WAIT 依赖/RED 登记）。
> 挖矿复用既有真源（132 环节表/fullflow 总册/00_环节总表挂接视图/126 卡体系），零新建 taxonomy（内收判据：可派生必并）。

## 一、新鲜度核查五项结论（审计结论 vs 挖矿时点 HEAD）

| # | 核查项 | 结论 |
|---|---|---|
| (a) | 死袋簇 8 卡字节 | **审计结论成立**：event_axis/swing_sequence/resonance_pair/tech_factor 全树零命中；`_PaperFillJsonlWriter` 在 start_paper_session.py 零命中；红证尺测试全史零 A 落地；entity_graph_uscc_bridge 全史零 A 落地；quant_methodology 仍仅 01-06+README+三附录。六袋（recover-0002/0003/0005、mini-0002/0003）+final-0001（C122）全部仍在 `.runtime/commit_queue/dead/` |
| (b) | l8 分支 | **成立**：`session/st-mastertc-l8` 在，tip=`cf5b6ddcf7`，merge-base `--is-ancestor`=NOT-MERGED；差异面仍=6 文件 +242/-1 |
| (c) | 裁定#490 | **部分成立（工作区已落、HEAD 未落）**：工作区 ruling_registry.yaml L4312 已载 #490（A 段授权+B 段 C19/C18 对调+C 段 C441 撤回翻转），git 态=` M` 未 staged——属总包 chief 在途面，落 HEAD 归 chief；**P0-4/P0-5 的裁定侧处方文本已就位**，M 道不代提交 |
| (d) | 交付链三件 | **成立（未被他会话更新）**：交付报告末触=de50314561（10-07 18:03 v2）、00_环节总表末触=6072df11ef（09:10）、close_lane 末触=0d1d6d29a6（10:33）——E 道勘误卡所引行号全部有效 |
| (e) | 桌面两清单 | **成立（内容与 mtime 双未变）**：主清单 `C:\Users\fanzi\Desktop\未完成任务施工清单_2026-09-29.md` mtime=10-07 19:24:25（53 卡头、9 张假销户仍缺、X01 缺、"在途袋 3+3 件传送带消化中"失真叙事在）；总清单 `遗留任务全量核验总清单_2026-09-29.md` mtime=10-07 19:31:47（63 行、C61 行仍写"token 批落地"） |

附：今夜新落地提交（895b535843 G2 队列基建、d553b160eb G6 P12A、f82008eb25 G4 误伤面治理、a92886e31d st-mx07-L3 等）均未触及审计 P0 面文件；module_translation_registry 被两笔今夜提交触及其他区段，但 4 条幽灵条目仍在 L67723/67731/67739/67747 原位。

## 二、P0 必修 10 项总表

| 项 | 来源审计条 | 负责车道 | 挖干态 | 依赖关系 | 执行序 |
|---|---|---|---|---|---|
| P0-1 死袋假完成簇（8 卡：C232/C234/C235/C75/C107/C233/C122/C452） | 总报告§三 P0-1；lane_a P0-1~4；lane_c P0-1；lane_d P0-1；lane_g P0-1 | R 恢复（st-acure-r1） | GREEN | 上游=六袋+final-0001 在 dead/（已核实）；下游=P0-7/P0-10/G 道注记 | W2 第一波 |
| P0-2 close_lane L35 错哈希假落地行 | 总报告§三 P0-2；lane_h H-P0-1 | E 勘误（st-acure-e1） | GREEN | 无上游；下游=晨会移交凭据更正 | W2 第一波 |
| P0-3 循环检查终判定失真（conftest 未入库+rule_red_blue 表述失实） | 总报告§三 P0-3；lane_b P0-B1 | E 勘误 | GREEN | conftest 正门入库无上游；表述更正无上游 | W2 第一波 |
| P0-4 C441 授权锚断链+机制互串 | 总报告§三 P0-4；lane_e P0-E1；lane_g P0-5 | E 勘误（裁定侧=chief #490 C 段） | GREEN（报告侧）/WAIT（裁定册落 HEAD=chief） | 上游=#490 C 段落 HEAD | W2 第一波（报告侧即行） |
| P0-5 #488 C19/C18 张冠李戴 | 总报告§三 P0-5；lane_g P0-3 | E 勘误（裁定侧=chief #490 B 段） | GREEN（注记侧）/WAIT（裁定册落 HEAD=chief） | 上游=#490 B 段落 HEAD | W2 第一波（注记侧即行） |
| P0-6 桌面清单 9 张假销户/漏收（C232/C234/C235/C75/C122/C56/C155/C267+X01） | 总报告§三 P0-6；lane_g P0-1/P0-4 | G 桌面（st-acure-g1，二波） | GREEN | 上游=R 道终态（注记写"已落地"或"死袋待取回"）+R 道文件 cp 备份 | W2 第二波 |
| P0-7 HEAD 注册表完整性（翻译册 4 幽灵条目+token 册 3 悬空 token） | 总报告§三 P0-7；lane_c P0-1.2；lane_h H-P0-2；lane_a E3 | R 恢复（随死袋清偿自然消除）+撤号面呈报 | GREEN（清偿面）/RED（C452 撤号 vs 落册=Owner 择一，登记呈报） | 上游=P0-1 落地 | 随 P0-1 |
| P0-8 C129 原件 object DB 可捞回而未捞回 | 总报告§三 P0-8；lane_f P0-F1 | E 勘误 | GREEN | 三悬挂 blob 已核实现存（52013B/51834B/51820B） | W2 第一波 |
| P0-9 "在途袋"叙事失真（桌面两清单头部） | 总报告§三 P0-9；lane_g P0-2 | G 桌面（二波） | GREEN | 与 P0-6 同窗同文件 | W2 第二波 |
| P0-10 HEAD 结构性红测试钉（fill 验收钉） | 总报告§三 P0-10；lane_d P0-2 | R 恢复 | WAIT（依赖 C107 写者腿落地转绿） | 上游=P0-1 中 C107 清偿 | 随 P0-1 |

## 三、P1 建议 10 项总表

| 项 | 来源 | 负责车道 | 挖干态 | 依赖 | 执行序 |
|---|---|---|---|---|---|
| ① C02 死信 44 封属主面接手（chainpile-0066 内表矛盾并案） | 总报告§四 P1①；lane_c §1 | 登记移交（维护班窗） | GREEN（登记） | 租约窗口+属主认领 | W2 登记即行 |
| ② l8 分支 6 文件 +242/-1 落 dev | 总报告§四 P1②；lane_e §5；lane_h E14 | B 分支（st-acure-b1） | GREEN | 队列袋+干净暂存区；落地后 branch 归档 | W2 并行 |
| ③ C136/C394 卡面补"在分支"披露 | 总报告§四 P1③；lane_e §5 | B 分支（随②落地后披露自然消解） | GREEN | 上游=P1② | 随 P1② |
| ④ C61 GREEN 残留回改（05_block_governance_gates.md L113） | 总报告§四 P1④；lane_f P1-F2/E4 | E 勘误 | GREEN | 无（L113 已复核原位） | W2 第一波 |
| ⑤ C61 升 ⏳+C78 转 ❌ | 总报告§四 P1⑤；§五；lane_g 重点 13 卡 | E 勘误（台账面） | GREEN | C61 升级已有交付报告 L47 OWNER 背书 | W2 第一波 |
| ⑥ C27/C441 注记更正 | 总报告§四 P1⑥；lane_g P0-5 | E 勘误 | GREEN | 与 P0-4 同一注记面 | W2 第一波 |
| ⑦ F096/F033 双处置总裁定归一 | 总报告§四 P1⑦；lane_h §5 | Owner 项——RED 登记呈报 | RED（登记） | Owner 裁定后才能排产 | 呈报 |
| ⑧ C24 净删执行前回 Owner 单项确认+C65 逐条回填 | 总报告§四 P1⑧；lane_e §7 | Owner 项——RED 登记呈报 | RED（登记） | §5 门位不代裁 | 呈报 |
| ⑨ C128 hook 挂册+升硬前置登记 | 总报告§四 P1⑨；lane_b §3 | 登记移交（施工项） | GREEN（登记） | 存量清零+Owner 批=升硬前置 | W2 登记即行 |
| ⑩ Owner 对话令授权补正式通道留痕 | 总报告§四 P1⑩；lane_g §4 | **已由裁定#490 A 段闭合**（工作区在册，落 HEAD=chief） | 已闭合（待 #490 落 HEAD） | 上游=#490 落 HEAD | 随 chief |

## 四、❓开口项与 P2 择要

| 项 | 来源 | 车道 | 挖干态 |
|---|---|---|---|
| ❓C312（T13 flag 读失败按 OFF 静默拒投判据修正） | lane_g §❓ | Q 开口（st-acure-q1） | GREEN 可施工（工程判据面；出厂翻转面禁触） |
| ❓C271（gate 自洽面 --diff 复跑对账，AI 只读） | lane_g §❓ | Q 开口 | GREEN 可施工 |
| ❓C315（35 红复跑对账） | lane_g §❓ | Q 开口 | GREEN 可施工 |
| ❓C411（幽灵户口净删）等 Owner 菜单漏登记 | lane_g §❓ | 呈报（#490 已声明 C411 仅呈报） | RED 登记 |
| P2 择要（计数勘误三处/snapshot 哈希/C85 时钟/C320 实体行/C192 三修/C61 分母附录/归档批补 completes_when/蒸发族机械前置等） | 总报告§四 P2 | Q 开口+各道顺带 | 见 open_questions/p2_digest.md |

## 五、真源挂接声明（内收）

本总表与全部施工卡**零新建 taxonomy**：卡号体系沿用 126 卡（C 系）+队列袋 qid 系；环节挂接沿用 132 表/00_环节总表挂接视图；状态轴真源=各 lane workbook+交付报告（勘误后）；本目录 01_mining/ 为施工卡编译层（task_bound），W5 归档时随战役树处置，不新增常驻清单。
