---
ttl: task_bound
title: 条件轴总包·终账收口册——四域全生命周期账（P0→P3→晨令→追加令，战役闭卷）
created: '2026-10-14'
session: st-condaxis-20261013
status: campaign_final_ledger
family_id: CONDAXIS-CAMPAIGN
completes_when: Owner 阅毕归档（战役终态闭卷）
---

# 条件轴总包终账（st-condaxis-20261013→14，Owner 全授权令·晨令·追加令全执行）

## §1 终态一句话

**四域产出全部落 dev、两裁定在册（PG＋YAML 双尺）、38 项呈批全闭环、C1/C2 对拍同尺回执考试线、五 worktree 归档、无 pending/dead 残项**——条件轴战役按令闭卷；后续开工面（两态 TDM 接线／板块验证班跑数／daban 深史重放／infoaxis 对齐）全部有锚有主。

## §2 落地总账（dev 面，全部 git cat-file 验证）

| 类 | 内容 | 锚 |
|---|---|---|
| 文档面 | 四研究档＋68 断言核验五组更正＋P1 呈批包（§5 回执）＋30 作业簿＋P3 设计/结果＋战役总结＋对拍册＋深史评估/施工记录 | 99a8fcaf…175a6e54/36883ea9/668c859c/3adc34d1/777db6e3/215e2da12b/0089-0090 系列 |
| 码面 | formreg 引擎 5 模块＋4 测试（31 用例）＋5 algo_flow 卡；sector 路由器＋16 测试＋配置＋algo_flow 册；sentiment 日批挂接＋9 测试；capital card_binding 算子＋74 测试＋考试卡＋分数行 | formreg 袋 0107→34c9205c72；sector 袋 0110→d19832cc1f；sentiment/capital 0058/0060/0089/0090 系列 |
| 裁定面 | **裁定#518**（形态向职责/#229 扩界/F8 D 族接管/锚语义=叙事尺/X2 不入格）；**裁定#519**（温度计≠档位计/#400 撞号修正） | PG 账本 v27＋YAML 投影（两把尺都过）；#517 占号被 VM 裁定并发挤占顺延 #519 |
| 数据面 | daban 双表补齐 22→24 交易日；词表册 v1.0.1 纠偏；挂图申报 15 条（账本 v538）；depgraph 六节点 production（六态合法链） | 各自袋留痕 |
| 归档面 | 五 worktree 归档（integ 分支 retire patch＝.runtime/quarantine/st-cdx-integ-…-retire-…patch；sent/capital 真 ahead 白名单台账） | session_worktree archive |

## §3 门链战损实录（九层，全部留下修法）

ruff 风格→`__all__: Final`→ALGO_FLOW 锚须在 docstring→MSG-EXPOSURE 去插值→MAP-MOUNTS no_mount_reason（账本 api.update，表名 registry_ledger.**registry_entry**）→DEPGRAPH 六态链（跳态非法且报错在 stderr）→翻译/token 陈读（PG render 治）→ghost_session（心跳 daemon idle 30 分自退，重注册+重启治）→热文件 stale-base（checkout dev 重基本/pool-regression-ack）。**队列合并袋机制**（单域快速连投→同签名合并→落地侧认 [allow-multi-domain] 标记）为本役打通多域袋的关键发现。

## §4 诚实账（负结果与自犯，零粉饰）

1. 轮一锚打靶 FAIL（上证锚 vs 000300，9 月差）按预注册存档；轮二叙事尺 4/4（裁定采纳），argmin 尺平底敏感（三腿极差 0.31%）留证。
2. A1 获利盘考试 fail（ic 0.0139<0.02/OOS 反号）——负结果有效，卡面 examined。
3. 自犯两笔：safe_write 缩进笔误致注册表短暂不可解析（即修留痕）；depgraph 跳态报错被 stderr 吞致误判"regen 覆盖"（读码后正名）。
4. 域外遗留（非本役件）：docs/03_modules/_domain_signal/algo_flow/{core,source_line}/index.md 两个无主 untracked（落袋代理留报待查）。

## §5 待 Owner/他班的后续开工面（全部有锚）

| 事项 | 锚/前置 |
|---|---|
| 两态层 TDM 挂接＋condition_package 大盘腿转正式 | 裁定#518 已解锁；数值冻结=formreg 8_prereg |
| 板块验证班开考 | 判据=sector 8_prereg_validation 六组；RRG 口径=10/26 式（D10 甲） |
| daban 深史重放（Owner 夜间窗，月块分片） | 对拍同尺已立（sentiment/9 号册）；重考 A 卡须整体重放统一面 |
| 分析师预期采购／分钟流外购／L2 | 报价单到位再呈（S2/S3/C4） |
| ETF 申赎差分 | 快照管线修复后（capital/10 号册四项呈批） |
| infoaxis 判据对齐 | 本包 §5 回执双锚（prereg 四处真源＋行号） |

## §6 闭卷判定

完工判据六条对账：①四域产出经验证 ✓（测试 139×2 绿＋考试如实判读）②端到端回测按预注册判据执行 ✓（02_p3_design §2 口径）③循环自检两轮零失败 ✓ ④红蓝对抗四项全拦 ✓ ⑤落地完整性 ✓（本册 §2）＋临时面已清 ⑥呈批项全闭环 ✓（38 项＋追加令回执）。**战役闭卷。**
