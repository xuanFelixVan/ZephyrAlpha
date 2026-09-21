---
ttl: task_bound
title: 深度审查报告——策略intake准入（T02）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：策略intake准入（T02）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/strategy_pipeline/intake.py:263(run_intake)/:80(fdr_gate)/:164(promote_to_sim)`
- 生产调用方: pipeline_events.py:226-228（c4_batch_completed→run_intake_auto，dry_run=False，事件驱动）；验收⑥回放/测试为其余调用面
- 测试文件: tests/strategy_pipeline/test_intake.py（15 用例）
- F/I 车道演进注意项：scripts/backtest/lane_g_stomach_intake.py:163 存在同名 `run_intake`（G 车道，语义不同）——与本对象无调用关系，D 轴登记命名撞车
- 材料包缺项: screen_source（p 值/ρ 矩阵生产者）深审归后续对象；近 N 天 pipeline 报告落盘目录未取样

## 1 对象快照

- 范围：intake.py 全文件（FDR 门/聚类/差异化/编号/FSM 预授权/注册表写入/挂图/报告/自愈补挂）+ 直接依赖 bh_fdr.py 与 registry_writer.append_entries 的契约面。排除：screen_source、auto_mount、lifecycle_fsm（各自对象）。
- 变更热力：2026-09-15 一日内 4 commit 建成（6c3bf86b40→d8dae11db8），单日速成型模块=高风险区。
- 测试覆盖概况：15 用例覆盖聚类确定性/差异化/FDR 管流转不管登记/幂等/KillSwitch/写入授权；**decay=None 与空 segments 的衰减条件无专测**（见 §4-1）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **衰减证据缺失 fail-open**：`s.get("decay") is None → 计为无预警`；`segments` 为空表 → `all(())=True`。衰减计算断供/漏算时三条件之三静默通过，sim 流转在零衰减证据下发生 | intake.py:313-316 | **P1** | 构造 items=[{key,segments:[{decay:None,sharpe:0.5}]}]+p 全 0.001 跑 run_intake(dry_run=True)，看 sim_promoted 非空 |
| A | 差异化指纹空集穿透：三轴全同的既有条目若 `entry_tokens_fn` 返回空集（代码不可解析/无指标），`if e_tokens and ...` 短路 continue → 判"差异化成立"，且返回语"三轴存在差异"与事实不符 | intake.py:147-153 | **P2** | differentiation_ok(axes,[同三轴条目],cand_tokens={"x"},entry_tokens_fn=lambda e: frozenset()) → (True,"三轴存在差异") |
| A | 聚类=single-linkage 贪心（ρ>0.6 严格大于）：链式效应 A-B/B-C 各 0.61 而 A-C 低也同簇——族吸收偏宽（保守向，登记候选变少），阈值边界 ρ=0.6 不聚。隐含假设=corr 为皮尔逊相关且样本充分，契约未在本模块文档化 | intake.py:104-109 | P3 | 造三键 corr 链式数据跑 cluster_heads 看同簇 |
| A | `strength` 语义"越小越强"（传 p 值=簇首证据最强）与 C5 人工先例"Sharpe 最高"等价性依赖 p 单调假设——docstring 已自白，口径一致 | intake.py:89-94 | 已查无 | — |
| A | 编号 `max+1` 扫描含本批已建条目（:325 追加进 entries）→ 批内唯一；跨会话竞态由整文件 CAS（registry_writer.py:188-192）兜住 fail-closed | intake.py:156-160, :308-309, :325 | 已查无 | — |
| A.3 | 测试：promote_to_sim 四态（全真/各假一）已测（test_intake.py:77-92）；decay=None 分支未测——正是 P1 漏测点 | test_intake.py:77-92 | P2 | 跑 `pytest tests/strategy_pipeline/test_intake.py -k decay` 无 None 用例 |
| B | passed_p 为调用方注入裸 dict：无 p∈[0,1]/有限性前置校验于 intake 层（bh_fdr 层拦 NaN/非有限，bh_fdr.py:42-46），负 p/越界 p 行为取决于 canonical bhy_fdr——隐式契约"p 合法"未在 intake 签名声明 | intake.py:263-274; bh_fdr.py:42-46 | P3 | run_intake(passed_p={"a":-0.5}) 看 canonical 拒绝或静默 |
| B | 手动模式 FDR 可绕过面：run_intake 直接喂 p 字典即判门——p 值与台账无对账（auto 模式 :470 自台账取数才有对账）。上游 bug/误用伪造 p=0.001 全过门即达 sim；属代码级动作非运行时漏洞，但"门的对账锚"缺失 | intake.py:263-266 vs :466-472 | **P2** | 对比两模式：手动传自造 p 即过（设计契约如此，建议生产强制走 auto 模式） |
| B | 空 passed_p → bh_filter ValueError("空假设族") → drain 重试 3 次 → 毒丸+ERROR 告警：批内全灭时事件以毒丸收场（可见但非优雅零工回执） | intake.py:273; bh_fdr.py:40-41; pipeline_events.py:294-305 | P3 | run_intake(trigger,"x",{}) 复现 ValueError |
| C | 下游消费：注册表→TDM 校验 R3/R12；sim_promoted→sim_wallet_due 开户钩子；报告→面板。失败链：注册表 CAS 成功后挂图失败不回滚（only-add 自愈下批补挂，:344-357）+ 开户钩子异常仅 warning（:387-394，事件留 journal 重放）——静默吞掉点两处均有告警/重放通道，判定可接受 | intake.py:344-357, :387-394 | 已查无 | — |
| C | 孤儿检查：本模块生产调用方≥1（pipeline_events 事件链实链）；非死码 | pipeline_events.py:226-228 | 已查无 | — |
| D | 同名 `run_intake` 撞车：strategy_pipeline.intake:263 vs scripts/backtest/lane_g_stomach_intake.py:163（G 车道）——语义不同易混 import | 两文件锚点 | P3 | grep -rn "def run_intake" src scripts |
| D | FDR 决策核单源委托 canonical bhy_fdr（对账 28a7403e86 裁定），intake 无自有统计实现——双份承载已治理 | bh_fdr.py:20-24 | 已查无（正面） | — |
| E | KillSwitch 探针 fail-closed（不可达=不清除，:69-76 注释明示与旧版 fail-open 相反）；写入路径 EVIDENCE 文件钥匙 fail-closed（:335-336） | intake.py:69-76, :335-336 | 已查无（正面） | — |
| E | 重放幂等：code_path 键优先/sid 兜底（:291-295）；整批重放零 diff 有测试（test:94）。但**文件改名绕过 code_path 幂等**：同一策略翻译件 rename 后 code_path 变 → 二次入库新 sid（checklist #14 同族） | intake.py:291-295 | P3 | 同 items 改 source_file 文件名重放 dry_run，出两个新 sid |
| E | registry_writer 写后复核 only-add+磁盘回读（registry_writer.py:184-197）+CAS fail-closed——假完成状态（checklist #12）已防 | registry_writer.py:184-197 | 已查无（正面） | — |
| E | `assert` 校验（intake.py:452 挂图 38 规则；registry_writer.py:184-185）在 `python -O` 下被剥离=校验静默失效——当前运行方式未用 -O，属纵深防御缺口 | intake.py:452; registry_writer.py:184-185 | P3 | python -O -c "assert False" 观察不抛 |

## 3 SOTA 对照

1. **BH-FDR+BHY 保守校正（对等已有）**：canonical 核启用 BHY 依赖稳健校正（c(m)=Σ1/i），与多重检验文献主流一致——Harvey, Liu & Zhu《…and the Cross-Section of Expected Returns》（Review of Financial Studies 29(1)，2016，https://academic.oup.com/rfs/article-abstract/29/1/5/1843824；SSRN 2249314）；Harvey & Liu《Backtesting》（JPM，2015）haircut Sharpe 同族口径（Witzany 2021《A Bayesian Approach to Measurement of Backtest Overfitting》Risks 9(1):18 综述引：https://www.mdpi.com/2227-9091/9/1/18）。步进单调通过集（防挑尾）为正确实现细节。
2. **聚类去重与多重检验的顺序（立卡候选）**：当前 FDR 假设族=当批全集、簇首才入库；学界做法是先筛代表再入族（Feng, Giglio & Xiu《Taming the Factor Zoo》，QJE，2020）。现状"聚类后族仍全量入 FDR"偏保守向（门槛更严），无需急改，登记挖矿候选。
3. 结论：FDR 门数学面**对等已有**，无立卡即改项。

## 4 缺陷清单

1. **[P1] 衰减证据缺失=静默视为无预警（FSM 预授权第三条件 fail-open）**
   - 现状：`no_decay = all(s.get("decay") is None or float(s["decay"]) < 0.5 ...)`，且空 segments 同判 True。
   - 证据：intake.py:313-316；docstring 只豁免"无 items 注入模式"（:311），未豁免"有 items 但 decay 字段缺"路径。
   - 影响：上游衰减计算断供（checklist #6 同族）时，策略在零衰减证据下自动进 sim——预授权三条件形同二条件。爆炸半径：sim 账本与后续晋升链输入（非真金；sim→paper 晋升另有 T04/T06 闸）。
   - 建议修法：decay is None 计为"有未决预警"（fail-closed）或显式告警计数；空 segments 视为证据缺失拒绝 sim。
   - 验证法：`run_intake("t", {"k":0.001}, {}, dry_run=True, items=[{"key":"k","source_file":"x.py","segments":[{"batch":"b","sharpe":1.0,"decay":None}]}])` → sim_promoted 非空即复现。
2. **[P2] 差异化指纹空集穿透+返回语失真**——证据 intake.py:147-153；影响：不可解析代码的既有条目挡不住三轴全同的重复入库（注册表 only-add 膨胀+重复占编号）；建议空 e_tokens 判"证据不足拒收"或至少改返回语；验证法见 §2。
3. **[P2] 手动模式 FDR 无台账对账锚**——证据 intake.py:263-266 vs :466-472；影响：p 值注入面绕过统计门（需代码动作，属纵深缺失）；建议手动模式收窄为仅测试可用；验证法：对账两模式入参来源。
4. **[P3] 空 passed_p 毒丸收场**（intake.py:273+bh_fdr.py:40）——建议空族短路返回零工回执；验证法见 §2。
5. **[P3] assert 承载校验逻辑**（intake.py:452；registry_writer.py:184-185）——建议改显式 raise；验证法 python -O。
6. **[P3] 报告文件名分钟级碰撞**（intake.py:236, :339 同分钟两批互覆）；验证法：同分钟两次落盘比对。
7. **[P3] 文件改名绕过 code_path 幂等**（intake.py:291）；验证法：改源文件名重放 dry_run。
8. **[P3] `run_intake` 跨模块同名**（lane_g_stomach_intake.py:163）；建议 lane 侧改名。

## 5 挂起疑问

1. decay 阈值 0.5（:314）硬编码于本模块——lifecycle/promotion 侧若另有衰减阈值即 checklist #4 双承载，需 Owner 确认真源归属。
2. 簇首"吸收"的 redundant 候选无复活重检通道（后续批次 ρ 下降时）——是否符合 Owner 意图？
3. EVIDENCE 文件（:58, :335）为一次性全局钥匙，验收⑥后永久开启写入路径，无按批撤销机制——是否需要钥匙轮换？

## 6 完备性自评

- 六轴全查：是。A（三算法逐个四问+边界构造）、A.3（15 用例逐一对发现映射）、B（passed_p/corr/items/segments 四输入逐条追源）、C（事件链/开户钩子/报告/挂图四输出全列）、D（canonical 委托+同名撞车+阈值常量）、E（五问：幂等/重放/KillSwitch/毒丸/改名绕过）。
- 长尾：①screen_source.passing_with_p/corr_matrix 内部数学未深审（p 值与 ρ 生产者，建议单列对象）；②canonical bhy_fdr 实现细节信任对账裁定未复算（P0 战役覆盖四闸/FDR，按分工不复算）；③auto_mount 五步管线只审调用面。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
