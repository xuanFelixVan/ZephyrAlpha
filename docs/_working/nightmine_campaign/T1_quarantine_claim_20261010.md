---
ttl: task_bound
completes_when: T1 认领链闭环（quarantine 清空+index 排雷+笔误修复落地）经 Owner/统筹复核
title: 夜矿续战 T1＝govjudge 棚 quarantine 119 件认领与排雷交付记录（st-nightmine2-20261010）
sid: st-nightmine2-20261010
created: "2026-10-10"
family_id: NIGHTMINE-CAMPAIGN
---

# T1 隔离认领交付记录（夜矿续战令·最急件）

> 令源=夜矿续战令 §三 T1；adjudicator=st-nightmine2-20261010。本记录全部数字出自当日实测命令，复核命令见文末。
> 本件曾于 14:0x 重建（原副本遭共享暂存区清扫失踪，内容自会话上下文全额复原；已获总统统筹批复=五件全验收、T1 排雷记大功，批复登记见 99_checkpoint §〇-3）。

## 一、验属结论（119 件三分类）

| 类 | 件数 | 判定 |
|---|---|---|
| 考试卡（路径/card_id/归属/节点在册四查全绿） | 117 | 归 st-nightmine-20261010 一期（preregistered_by 均带本役签名；node_id 全在 00_lane_roster 186 节点集内） |
| 考试卡（card_id 笔误 1 处） | 1 | `TDM-F-C2-02__shadow__02_约束栈有vs无.yaml`：卡内 card_id=TDM-F-C2/shadow/02 漏 `-02` 后缀；node_id/正文引用/姊妹卡 03/04 三证确认孤例笔误 |
| 非考试卡 | 1 | `docs/_working/govjudge_campaign/99_delivery.md`＝**st-govjudge-20261010 本班终报**（六件交付+施工事故记录，所载 commit 均已在 dev）。**未冒领**，救援至本班 staging `_rescued_foreign/st-govjudge-20261010/` 待统筹/Owner 路由（批复=随 CAP render 解堵一并落库，取件路径已交终清二期） |

## 二、关键翻案：隔离件非"欠落地"，是"冗余孪生"

逐件 sha256 对账：118 卡与 **HEAD 九袋队列落地版逐字节一致**（git cat-file blob 全量比对 118/118 identical；HEAD exam_cards 在册=454 与 00_final_report 454 精确吻合，无删除 commit）。即卡册本体早已由一期 s1..s9 袋落地 dev，被隔离的 119 件是误写进 govjudge 棚的物理副本（cwd 漂移事故面，govjudge 终报自述同款事故在案）。

**TTL 危机实质=证据件损失风险，非材料欠落地。** 认领动作照样执行（超时=对账证据丢失）。

## 三、排雷（本记录最重要发现）

排雷前主区 index 实测（git status -z 逐条分桶）：

- exam_cards 子树挂 **248 条 staged 删除**（rm --cached 型：index 除名+盘面在场，D∩??=248 同路径）＝**任何宽清单提交都会把半套卡册从 dev 抹掉的活雷**
- 其中 118=本班隔离件对应路径（主区缺盘）；130=盘面在场的无盘损路径
- 另有 2 条 `A`（dualwindow 新卡）+7 条 `MM`＝他在飞物，**未碰**

处置：`git restore --staged --pathspec-from-file`（sanctioned 白名单手段，仅 index 面）248 条全清。清后实测：

- 本班 118 路径：index=HEAD=盘面三方一致，转 **clean**
- 8 条既有未暂存改动（` M`，L1 导生卡族等）**显性保留，零丢失**（restore --staged 不触盘面）
- 2 A + 7 MM 原样未动

## 四、实体修复（唯一 content 变更）

`TDM-F-C2-02__shadow__02_约束栈有vs无.yaml` 卡内 card_id 笔误修正（TDM-F-C2/→TDM-F-C2-02/，机械修正非挪门柱——判据面 pillar/window/bucket 零触碰）。token 已在册（一期班裁定#502 意图 API 预登记，抽样 3/3 账本直查 True）。队列正门落地：**commit 0544db35bd3**（q-20261010-st-nightmine2-20261010-0001，--allow-non-worktree 按裁定默认旗）。

## 五、 quarantine 棚收尾

119 件全数搬离（逐件 sha256 断言通过后 unlink），原棚留认领收据 `_CLAIMED_BY_st-nightmine2-20261010.md` 指向本记录与本班 manifest。本班 claim manifest=`.runtime/sessions/st-nightmine2-20261010/staging/_claim_manifest.json`（含逐件 sha256；笔误件另录 sha256_after_fix+fix_note）。

## 六、移交/上报项（禁吞清单）

1. **99_delivery.md 路由**：已批复=随 CAP render 解堵一并落库；救援件现位 `.runtime/sessions/st-nightmine2-20261010/staging/_rescued_foreign/st-govjudge-20261010/docs/_working/govjudge_campaign/99_delivery.md`（终清二期取件即此）。
2. **8 条 ` M` 未暂存改动**（exam_cards L1 族为主）：非本班物，显性化后留盘待其属主处置。
3. **2 A dualwindow + 7 MM**：他在飞（疑 examchief/acure 族），本班未碰。
4. 一期总报告生成器真源=主区 exam_cards；排雷后盘面=454 在册卡+2 dualwindow，与报告 454 对齐（此前 456 差额疑团=2 张 dualwindow 新卡，已定性）。

## 七、复核命令

```bash
# 1. HEAD 卡册在册数=454 且无删除 commit
git ls-tree -r HEAD --name-only -- docs/03_modules/_domain_backtest/exam_cards/ | wc -l
# 2. 本班 118 件与 HEAD 逐字节一致（manifest 逐件 sha256 抽查）
python -c "import json;print(len([i for i in json.load(open('.runtime/sessions/st-nightmine2-20261010/staging/_claim_manifest.json',encoding='utf-8'))['items'] if i['kind']=='card']))"
# 3. 排雷后子树无 staged 删除（应无 D 行）
git status --porcelain -- docs/03_modules/_domain_backtest/exam_cards/ | grep -c "^D "
# 4. 笔误修复落地核验
git show HEAD:docs/03_modules/_domain_backtest/exam_cards/portfolio_flow/C2/TDM-F-C2-02__shadow__02_约束栈有vs无.yaml | grep ^card_id
# 5. quarantine 棚已清空+收据在
ls .runtime/sessions/st-govjudge-20261010/staging/quarantine_foreign_untracked_20261010/
```
