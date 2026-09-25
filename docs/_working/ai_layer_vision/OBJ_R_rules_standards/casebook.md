---
ttl: task_bound
title: OBJ_R 案例库（casebook）——事故归因→缺陷模式→阈值提案 起步件
owner: ZephyrAlpha-Owner
session: st-ailayer-p1-20260923
date: 2026-09-23
status: active
---

# OBJ_R 案例库（casebook）

> **性质**：OBJ_R DESIGN §⑤ 的起步件（施工项 S5）。攒 ≥5 案后由 Owner 裁定是否升格
> catalogs 正式 YAML 注册表（升格时机=OBJ_R-#6 治理立案，未到不议）。
> **词表边界（红蓝 R1-B6 铁律）**：signature/recipe/pattern_norm 三字段与 L7
> `ai_heritage_defect`（H4）同名同义；pattern 词表真源=L7 heritage 词表，本册只引用
> 不扩展——**禁自造新 pattern 值**，模式登记落 L7（机读真源），本册留 case+三字段引用。
> **流程**：事故自动喂（L1 内监）→AI 归因填 root_cause→同 pattern_norm 合案→阈值提案
> （standards_proposal，产出物=proposals/ 目录）→Owner 裁决→ruling_registry 登记→
> 重放验证闭环→回写 L7 传承。

## 案例索引

| case_id | 日期 | 一句话 | pattern_norm | 状态 |
|---------|------|--------|--------------|------|
| CASE-2026-0917-001 | 2026-09-17 | 传送带 serializer pathspec bug（首案） | 编排层路径参数未复用入队侧白名单 | patterned |
| CASE-2026-0922-001 | 2026-09-22 | 翻译册幽灵条目：声称摘除的提交实为纯插入（队列合并器丢删除） | 合并器删除语义缺失致账实脱节回魂 | patterned |

---

## CASE-2026-0917-001

```yaml
case_id: CASE-2026-0917-001
date: '2026-09-17'
source_incident: 传送带 serializer pathspec bug（Owner 口述在案；死因细节已经 OBJ_R-#4 夜批授权按本卡记录登记销项）
root_cause: commit_queue B 段 serializer 落盘的 git pathspec 处理缺陷——路径参数未过白名单语义校验即拼入提交命令（66 号备忘 §6.5 pathspec 白名单语境；enqueue 侧轻检已对 .git/密钥路径 fail-closed，落盘侧未对齐）
defect_pattern: 编排层路径参数未复用入队侧白名单（单侧防御）
signature: 落盘侧 git 命令拼接受态路径参数且该路径未过 enqueue 侧同款白名单校验
recipe: 落盘侧复用 §6.5 白名单校验 + dead_reason 结构化枚举（便于死信归因统计）
pattern_norm: 单侧防御（编排层路径参数）
affected_gates: [commit_queue 入队轻检, FOREIGN-CHANGE, COMMIT-SCOPE]
threshold_proposal: standards_proposal_id 未派（首案为流程起步示例，随体检器产生首批证据后补派）
status: patterned   # Owner-4 补登确认后由 open 转 patterned（夜批授权销项在案）
relapse_verification: 重放用例挂 queue 落地侧回归（test_commit_queue_landing 族）；体检指标=dead_reason 结构化占比
```

## CASE-2026-0922-001

```yaml
case_id: CASE-2026-0922-001
date: '2026-09-22'
source_incident: module_translation_registry.yaml 幽灵 events.py 条目（commit c07568e5f1 声称"摘除幽灵条目"实为纯插入 56 行零删除；2026-09-23 批次1 经 CAS 手术补摘=31dc939f，2026-09-23 夜又见他会话队列死信重放回魂——删除动作在队列链路反复丢失=结构性非偶发）
root_cause: 提交队列合并器删除语义缺失——合并器把"删除行+注记行"的编辑对渲染成"仅注记行插入"，净删语义在 merge 侧无身份表达（与 L55581 声称摘除实未删同构；2026-09-23 夜 nightfix 合并器身份作用域化修复后删除语义仍有回魂波=复合缺陷）
defect_pattern: 合并器净删语义缺失+死信重放不含已落地基（重放侧无"被吸收型 noop"判别）
signature: 提交信息声称删除某注册表条目而该条目 diff 实为纯插入；同一条目在后续会话提交中复活
recipe: 合并器渲染自检加"净删声明↔实际 diff 行数"一致性断言；死信重放前置 grep HEAD 是否已含同 token 条目（被吸收型 noop 判别）
pattern_norm: 合并器删除语义缺失
affected_gates: [REGISTRY-MASS-DELETION, commit_queue 合并器渲染自检]
threshold_proposal: standards_proposal_id 未派（候选尺子=合并器渲染自检断言，随体检器首窗证据补派）
status: patterned
relapse_verification: 体检指标=注册表条目账实一致率（canonical 册/翻译册路径全存在率）；重放用例=test_commit_queue_landing 族删除语义用例
```

---

## 登记纪律（本册自我约束）

1. 新案追加=本文件尾部逐案 YAML 块+索引表加行；禁改历史案块（补登走修订注记行）。
2. pattern_norm 必须引用 L7 heritage 词表现有条目；词表没有=先落 L7 再引用，本册禁首造。
3. threshold_proposal 派号后回填 standards_proposal_id，提案原件=同目录 proposals/<proposal_id>.yaml。
4. status 流转：open（归因未确认）→ patterned（三字段齐+pattern_norm 可引用）→ proposed（提案已派）→ ruled（Owner 裁决入 ruling_registry）。
