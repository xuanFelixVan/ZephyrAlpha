---
ttl: task_bound
title: L6 切换段——A/B 蓝绿（champion/challenger，进化的安全带）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_done   # 真源设计稿=[DESIGN.md](DESIGN.md)（模块级影子运行框架/五态状态机/灰度三档成文）
---

# L6 切换段骨架卡

## 职责一句话
新施工件（B 组/challenger）与老件（A 组/champion）并行运行：影子模式不下真决策，
判据预注册下实测对比，B 赢了才切流量；A 退役不删除（墓碑制）观察 1-3 个月，
全程可一键回切。

## 输入/输出
- 输入：L5 施工完成的新件 + 运行态对比判据（目标常数预注册）
- 输出：切换裁定（升 B 贬 A）→ 正式资产（晋升）+ L7 传承（留档）；回切指令（B 劣化时）

## 业界对应
**Champion/Challenger + Shadow Deployment**（银行模型验证标准动作：挑战者影子运行→胜出→
审批晋升；FICO/DataRobot/监管实务）。MLOps 的蓝绿/金丝雀发布；PDCA 的 Act 环。

## 已有件
模拟盘=策略级 B 组（现成）；flag 系统+回滚=revert；墓碑合并法（deprecated 链不删）；
promotion 前端拍板页（Owner 门位）；OwnerTokenGuard。

## 待挖矿清单
1. 模块级影子运行框架：非策略对象（模块/算法/门禁参数）怎么并行跑双版本不互污染
2. 观察期规则：1-3 个月的定量判据（什么信号触发提前回切）
3. 墓碑制操作规程：退役件的封存位置/复活条件/清理条件（TTL）
4. 切换审批分级：哪些切换全自动（机械债类）、哪些要 Owner 前端一键（骨架/规则类）
5. 回切演练：定时红蓝演练回切通道的可用性（安全带不演练=没有安全带）

## 状态
**design_done（2026-09-17 挖干）**：真源设计稿=[DESIGN.md](DESIGN.md)——模块级影子运行框架
（worktree 双检出+不互染三闸）、五态状态机、观察期 T1-T6 自动回切触发器、墓碑规程、
审批分级（risk_tier 映射）、回切演练挂月度体检、灰度三档成文（EXEMPT-ZONE-FM 先例）。
