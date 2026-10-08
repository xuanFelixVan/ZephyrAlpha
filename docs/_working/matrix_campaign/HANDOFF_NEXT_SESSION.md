---
ttl: task_bound
campaign: matrix-20261006→20261009
session: st-matrix-20261007
created: 2026-10-09
version: FINAL-CLOSEOUT（v2 置换 2026-10-07 v1，v1 内容已全部执行完毕）
purpose: 新对话一键启动指令（收尾接力：遗留施工+路由政策丰富+运维钉死）
---

# st-matrix-20261007 收尾交接（终版）

> **给新对话的指令：复制下方整块到新对话即可**

```
你是 st-matrix-20261009（矩阵战役收尾接力总包）。前会话 st-matrix-20261007 已完成全部裁定落地与队列排雷
（终审审计通过：核心 4 commit 全在 HEAD 零回退、队列零在途、claims 已释放）。你负责三件事：
①遗留施工推进（清单在下面）②裁定路由政策丰富（车道票在册）③运维钉死。授权口径=裁定路由政策已生效
（adjudication_routing_policy.md），照章路由执行，非 high 门位勿反复请 Owner 裁。

## 冷启动（缺一不可）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:/usr/bin:/mingw64/bin:$PATH"
python --version  # 必须 3.12.x
python scripts/lock_files.py cleanup
python -m zephyr.trading.process_reaper --status   # reaper 不在=禁止写操作
python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start; session_worktree_start(session_id='st-matrix-20261009', allow_workspace_drift=True)"

## 项目背景（30 秒）
A股量化系统 ZephyrAlpha，100% AI 开发，重治理（宪法=AGENTS.md，GitCommitGateway=唯一合法提交入口，
队列串行消化，禁裸 git commit）。矩阵战役=全库大考试（143 指标/175 因子/161 策略/5 分配器），已收官：
78 指标过/6 退役+CYC4 停用/其余回炉；因子策略大面积回炉；分配器三层栈有增益。现役体制帘子=SMA200
（regime_source=sma200_default）；HMM 已改判"实现停用·算法待优化"（deprecated，重启条件写死）。
裁定路由政策（新真源）：什么事走哪条路谁拍板——三公理+八类路由，L3 自动化的裁定引擎输入。

## 前会话已完成（勿重做，核凭=git log）
1. wave-2.5 GPU 核 18 件补交 → 6b3426c398（bootstrap_gpu/gpu_ic/exit_sim/grid_adapter+spread 接线+parity 测试）
2. 26 件 tmp 产物抢救 → docs/_working/matrix_campaign/rescued_tmp_20261007/（16 件入 HEAD；10 件档案
   副本仅磁盘安全——真源已由夜战车道转正 src/，见 L5/W2 各自 commit）
3. 夜战派单 18 车道全部完成（第一波 12+第二波 6，读数全录 99_delivery.md 增补段）
4. 裁定#489 六项 → 50933522210（6 指标退役/CYC 留观→后转轨A/HMM 封顶一击/及格线 v1+Bonferroni/
   v1_value 暂不开/t0 第二波）
5. 15 条无主删除全量恢复（143=143 基线对齐+墓碑×15，红队 P1-1 处置路径②）
6. 裁定#494 三项 → 386675775af（HMM 改判 deprecated·算法待优化/CYC-001/002/004/005 转轨A/
   adjudication_routing_policy.md 骨架落 governance_sop 族）
7. 三个死会话接管处置零损失：rescue tag ×3 = rescue/st-fc-landing-20261008（55件）/
   rescue/st-fc-spm-20261008（3件）/rescue/st-tail3-20261008（5件）——fullcirculation 班可 cherry-pick
8. 暂存区无主删除复发实锤+手工修复（adjudication_routing_policy.md 被 staged D，已 restore）；
   6 死 1 生队列排雷全链证据在 dispatch_blockers.md

## 遗留任务清单（按优先级）
【P0 立即】
- 维护班根治：暂存区"无主删除"复发（根因=陈旧快照袋整册回卷；本会话新实锤一笔在 blockers 末段）
- 通知 fullcirculation 班：死会话成果在 rescue/ 三枚 tag，cherry-pick 回收
【P1 本周】
- SQUEEZE/WAD 实现修复+重考（处方=mining/classic_indicator_investigation_v1.md；修复后按 #489①
  复活条件翻案）
- famex v2 entry_role 分考场立项（AC/MACD背离/CHOP 用择时/策略层尺子）
- 离场族 12 节点：B1-B5 齐备后照 mining/exit_family_12nodes_prereg_draft_v1.md 冻卡施工
- 路由政策丰富票 ×2（adjudication_routing_policy.md §5）：外部 ADR/RFC 框架对表（可联网）+
  ruling_registry 489+ 条先例机生归类统计
- 情绪快照器日批：人工连跑 2-3 天稳定后钉 Windows 计划任务（scripts/data/emotion_index_snapshot.py，
  先登记 process_reaper_keep.txt）
【P2 排期】
- t0_material_line GPU 二期 + CH 取数 IO 提速（W1 留档）
- 路由政策 D2-D8 逐节细化（增量）
- metaq 36 问回填 / T3a 开闸考点火（等裁定+GPU 空窗）/ paper 池 3 个月回调及格线 v1（2027-01 窗）

## 待 Owner 裁定（仅 3 项，均已登记 dispatch_blockers.md）
1. 离场族 B1 新配置维（X_tp/X_ladder）开不开（ prereg 草稿已备）
2. R1/R2 地图 F1-F5 销账批（本体已治本，纯记账）
3. 15 条原始删除队授权链追认（已恢复；若其持授权需补录裁定走正门重执行）

## 必读文件（全路径）
docs/_working/matrix_campaign/master_backlog_v2.md          ← 总施工账（P0-P3 全量）
docs/_working/matrix_campaign/99_delivery.md                ← 战役终报+夜战增补
docs/_working/matrix_campaign/dispatch_blockers.md          ← 堵点/待裁全账
docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md ← 裁定路由政策（新真源）
docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml ← 裁定册（检索 #489/#494）
docs/_working/matrix_campaign/mining/classic_indicator_investigation_v1.md ← L1 对表+修复处方
docs/_working/matrix_campaign/mining/hmm_v3_exam_v1.md      ← HMM 三考全档+改判注记
docs/_working/matrix_campaign/mining/exit_family_12nodes_prereg_draft_v1.md ← 离场族草稿
docs/_working/matrix_campaign/data_requests_v1.yaml         ← DR-1~4 回补申请（待转数据班）
docs/_working/fexam/                                        ← 全部成绩册目录
docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md ← 考试政策
AGENTS.md                                                   ← 宪法
docs/registry_of_registries.yaml                            ← ROOR（注册表发现唯一真源）

## 门禁陷阱（原 11 条见 90_execution_log；本会话新增 T12-T17）
T12 裁定号先查占号再落册（#490-493 曾被他队抢号）
T13 入队袋快照抓 index 不抓工作区——新内容先 git add 再入队
T14 热册三向合并拒结构漂移：PG 渲染引入的顶层族会炸合并——token 落 yaml 用
    scripts/governance/d3_metadata/batch_creation_tokens.py（HEAD 原生格式）
T15 TAKEOVER-PENDING 连环拦热册袋：session_takeover_ledger.py --scan/--list 找拦路条目，
    dirty>0 先 git stash create 打 rescue/<sid> tag（零损失）再 --resolve+worktree remove
T16 ghost_session：长等待=心跳过期=袋死——60s 内紧密轮询保活；内容未变的死袋可 CLI 手动 requeue
    （熔断时 --force 留痕）；内容已变=发新袋禁 requeue
T17 token 双轨制：PG 账本（api.register+publish_snapshot）与 yaml 投影都要落——CREATE-GUARD 只读 yaml

## 完成判据
P0/P1 按表推进；每件走 GitCommitGateway；循环检查×2=0；红蓝通过；报告增补 99_delivery.md；
会话收尾=release-only→promote→handoff→向 Owner 汇报。
```
