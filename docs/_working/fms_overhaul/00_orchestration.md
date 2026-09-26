---
ttl: task_bound
title: FMS 大改造战役总骨架 · 十年级文件管理体系（全环节地图/波次/避让图/判据）
created: 2026-09-27
sid: st-fms-chief-20260927
status: 骨架定版，S1-S8 并行挖矿中
---

# FMS 大改造总骨架（Owner 总筹令 2026-09-27）

**使命**：按"100% AI 施工的长远期项目"标准，对全套文件/文件夹管理体系大改造，六个维度全部达到模拟外部审查 + 红蓝极限对抗满分。

## 一、交付目标（评分卡基线 → 目标）

| 维度 | 基线 | 目标 | 主抓手 |
|------|:---:|:---:|--------|
| 引用完整性 | 3/10（10,683 引用 2,498 死=23.4%） | 10/10 | FMS-HYGIENE 门（棘轮）+ 基线清偿 |
| 生命周期 | 4/10 | 10/10 | 永久/临时隔离条款 + CAS 残渣清零 + 根目录净化 |
| 分类学与导航 | 6/10 | 10/10 | FRONT-DOOR + 嵌套 AGENTS.md + lookup 单口立法 |
| 元数据机器自身治理 | 4/10 | 10/10 | 计数回填机械化 + ROOR 收敛 + 口径统一 |
| 写侧执法 | 9/10 | 10/10 | 保持 + 新门以退役旧门配对（净零） |
| 真源层完整性 | 8/10 | 10/10 | 图书馆三层对账（总账↔视图↔盘面） |

## 二、十年机制五支柱（设计公理，一切施工服从）

1. **棘轮（Ratchet）**：坏指标只许降不许升——存量违规进生成基线豁免（只减不增），新增违规一律硬拦。10 年后基线趋零。
2. **单写者（Single Writer）**：每类事实一个真源平面；读侧唯一入口=图书馆 lookup；路径禁凭记忆书写（宪法立法）。
3. **生成闭环（Regen-Clean）**：凡生成物必有 `regenerate && diff --exit-code` 机械验证；手写即漂移。
4. **生命周期隔离（Lifecycle Isolation）**：永久区（ttl: permanent）禁止引用临时区（_working/.runtime）；临时真源必须先 promote 才能被永久件引用。
5. **墓碑去向（Tombstone Successor）**：资产死亡必须留 `successor_of` 去向指针，死引用报错从"不存在"升级为"迁往何处"。

## 三、环节骨架（S1-S8，每线一簿，挖干封矿后进施工）

| 线 | 名称 | 施工批映射 | 主交付 |
|----|------|-----------|--------|
| S1 | 引用完整性 | B1+B2 | FMS-HYGIENE 门（死引用棘轮/ASCII 新路径/永久引临时/CAS 残渣四查类）+ 基线清偿首批 |
| S2 | 生命周期与临时区 | B7+B8 | 根目录净化（nul/30/ZephyrAlpha/test_dir）+ catalogs 残渣清零 + _working 陈化处置方案 |
| S3 | 分类学与命名 | B9（方案批） | 分类学 v2 规格（镜像树/ASCII 政策/命名收敛），大规模迁移列队后波 |
| S4 | 注册表机器自身治理 | B5+B10 | ROOR FRONT-DOOR 瘤切 + 计数回填机械化 + 三口径统一 |
| S5 | 图书馆接线 | B3 | successor_of 墓碑 + lookup 立法 + 三层对账 |
| S6 | 导航与上下文经济学 | B5+B6 | 嵌套 AGENTS.md×5 + llms.txt + 检索阶梯缩短 |
| S7 | 生成器与 regen-clean | B4 | 生成器清单 + regen-clean 检查器 + 门挂接 |
| S8 | 并发与冲突面 | 总筹自留 | 避让图 + claim 纪律 + 施工序列 |
| S9 | 模块退役自动化（Owner 09-27 增补令） | B10 | MLC-003 退役七步执行器 + 退役候选机械判定 + IFC-007 契约级联 + 生命周期转换门 |

## 四、挖干判据（每簿六向台账 + 自审闸三态）

- **六向台账**：真源 / 写者 / 消费者 / 漂移史 / 冲突面 / 净零方案（全部带 file:line 证据）。
- **自审闸三态**：`挖干`（施工代理拿簿可直接开工）｜`未干`（列缺口）｜`受阻`（列阻塞与绕行）。
- **封矿**：自审=挖干 且 总筹复核通过 → 该线进入施工，簿不再改。

## 五、冲突避让图（多队并发，铁律）

- **本队命名**：`st-fms-chief-20260927`；作业区 `docs/_working/fms_overhaul/`（他队勿入）。
- **st-p15-phantom**（幻影引用治疗）：作业面=`docs/_working/decision_map_campaign_20260924/links/**` + `docs/_working/three_piece_infra/phantom_cure/`。**本队不碰**；其"幻影引用"语义与 S1 死引用相邻但平面不同（它治挖矿簿引用，本队治全仓文档→文件引用），已错峰。
- **st-p1b-libr**（图书馆 reconcilers）：在改 `library_regen_reconciler.py` / `reconciliation_registry.py` / `library_new_module_reconciler.py` + project_handbook 族 + capability_canonical/module_translation 两册。**本队 B3/B4 避开上述文件**：successor_of 落 `ledger_schema.py`+`lookup.py`（其未触碰），regen-clean 落独立检查器不碰 library reconciler。
- **主区在途脏文件（511 个）**：candidate_module_registry / capability_canonical_file_registry / module_translation_registry / rule_catalog_registry / trial_ledger_registry / project_handbook 族 / architecture_model/index.yaml / config 两册 / data 三件——**全部不 claim 不修改**。
- 所有既有文件改动前 `lock_files.py acquire <file> st-fms-chief-20260927`；改毕 release；提交必经 `scripts/git_commit.py --session st-fms-chief-20260927`。

## 六、仪式链 checklist（每个施工批过一遍）

1. 新文件命名：ASCII、禁空格禁中文路径；目录/文件遵循 TRAE-028 既有命名规则（S3 线修正：禁 kebab-case，Python 域 snake_case）。
2. 新 .py：头部 30 行内 14 字段标注（BLUEPRINT/MODULE/DOMAIN/DEPENDENCIES/CONSUMERS/STARTUP/MATURITY/INVARIANTS/MODIFY-GUARD/STABILITY/SAFETY/AI_AUTONOMY/ERROR_CONTRACT/TESTS）。
3. 新 .py/.yaml/.md/.json：creation_token 先行独立批（`scripts/governance/d3_metadata/batch_creation_tokens.py`，token 批先落地，文件批后落）。
4. 新 .py 模块：`add_module_translation.py` 登记大白话简介（同批或先行）。
5. 新模块：`apply_depgraph.py --add-design-node` 登记。
6. 新门：`.pre-commit-config.yaml` 加 entry（gate_registry.yaml 由 reconciler 自动再生，禁手改）。
7. 新注册表/目录：ROOR 登记（RULE-FOUR）+ 净零声明（替代/合并了什么，或为何属新生成物非新真源）。
8. 热文件（宪法/ROOR/注册表）写入用 `safe_write_text` CAS，写后进程外复核。
9. 提交：`git_commit.py --session st-fms-chief-20260927 --files <清单>`；提交后 `git log -1 --name-only` 核实归属。

## 七、波次与验收

- **波1 挖矿**：S1-S7 七路代理并行 + S8 总筹自挖 → 八簿齐 + 三态全`挖干`。
- **波2 施工**：B1→B2 串行（门先立再清偿）；B3/B4/B5/B6/B7/B8 线间并行流水，谁挖干谁开工。
- **波3 循环检查**：全部新门自测 + 全链 git_commit 实投，连续两轮问题=0 才过。
- **波4 红蓝对抗**：90_red_blue/ 记录；红=对抗夹具（伪装死链/unicode 路径/模板占位/noqa 逃逸/生成物篡改），蓝=合法提交必过；两轮零 FAIL。
- **波5 收尾**：claim 全 release、临时文件清理、晨报（含评分卡终评 + 登记跳过清单——按 Owner 令尽量零遗留零待裁定）。

## 八、数据附件

- `_data/deadref_missing_2498.csv`：全量死引用清单（S1 挖矿输入）。
- `_data/deadref_refs_unique.csv`：10,683 条唯一引用全集。
- `_data/deadref_refcounts.csv`：引用频次。
- 审查方法与基线数据出处：本战役晨间审查（2026-09-27，总筹会话实测）。

## 九、增补令（Owner 2026-09-27 深夜）：S9 模块退役自动化

Owner 令：模块退役目前零自动化——检测、标准、流程、接线全缺。已并入本战役为 S9 挖矿线 + B10 施工批。他队 AI 情报（MLC-003 七步从未实现/账本 module-id-registry.json 不存在/IFC-007 零触发/ORPHAN-MODULE 存根）按数据处理，S9 全量复审取证后定方案。与其他线的接线：退役即生命周期终点，与五支柱的墓碑去向（S5 successor_of）、生命周期隔离、净零判据（§4）同构；MLC-003 的机械判定优先复用 depgraph 消费者计数 + git 活动度 + 图书馆 potential_consumers。
