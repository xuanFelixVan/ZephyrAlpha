---
ttl: task_bound
title: "暂存区黑手取证包（两症状一只手假设）"
session: st-commitsys-20260924
---

# ⑤暂存区黑手取证包（总指挥晨会对账素材）

## 症状全录（本班实测）

1. **盘面陈旧快照（案发 00:2x 发现）**：capability 册盘面相对 HEAD 缺 31 条（e2e_20260924×6/secbuild×11/kimi_audit×2/exam_cost_gate 等 09-22~23 token），extra=0。三版本：HEAD=10156 > 盘面=10125 > index=10097。
2. **暂存区缩水版**：index 版 registry -321 行（条目身份消失 61）；翻译册 index 有已被吸收的旧重排残留（-36/+27，nightfix D3 已吸收型）。翻译册 working-vs-HEAD 曾为纯 +32 插入，与 index -36/+27 完全不同源。
3. **盘面二次重置（案发 00:3x-00:4x，现行）**：我 6 条 token+1 条翻译写入盘面并 git add 后，盘面被重置回 HEAD（token 蒸发、翻译蒸发），暂存区快照保留——**重置动作不落 stash（stash list=0）、不留 notice**。
4. **昨日同型案底**：热册蒸发 30 条 lane token（18:20→19:29）；stress 实证 index 里 30 个非其 stage 的 CRLF 快照。
5. **健康对照**：tripwire 期间也观察到他会话正常纯插入（condition_attribution 等 4 条）——并发写本身健康，问题专指"回退型重置"。

## 证据文件

- `.runtime/tmp/commitsys/registry_recon_20260924.json`（缺 31/extra 0 清单）
- `.runtime/tmp/commitsys/registry_head.yaml` / `registry_index.yaml`（三版本对比原始件）
- `.runtime/tmp/commitsys/tripwire.jsonl`（2s 轮询，变更即录 staged/work 双 diff 态）
- batch_creation_tokens 写前守恒闸拦截记录（4 次拒写=31 条缺失的机械实锤，工具 B22 闸首战立功）

## 已排除

- git stash 吞修改（stash list=0、notice 无近期条目）
- auto-sync 产物 restore（`_is_auto_sync_product` 对两册=False 实测）

## 嫌疑面（待晨会对账定性）

1. serializer/landing 的 skipped_dirty 主区同步路径（总指挥 R2 假设同源）
2. 某 reconciler（registry_alignment 再生/自动提交链）整文件重写
3. session_worktree auto-sync restore 的分类误伤面（理论已排除分类，但 restore 动作面未排除）
4. 某会话 promote/cleanup 流整片覆盖

## 治本设计提案（对账定性后施工，候批）

**G1 还原审计闸**：任何 `git restore/checkout --` 触及 `_registry/catalogs/` 的调用点（reconciler/session_worktree/patrol 全查）落 write_audit（who/when/which file/from-to hash）——先全量取证归因。
**G2 热册还原 CAS 化**：还原/覆盖 catalogs/ 文件的代码路径统一走 safe_write_text(expected_base=写前哈希)，基线漂移即 refuse+告警，把"静默重置"变"响亮失败"。红测=模拟并发写后 restore 必须拒；回滚案=开关 feature_flag 一键退回直写。
**G3 指南联动**：黑手案全过程=「盘面被重置→token 蒸发→提交被 CREATE-GUARD 拦→守恒闸拒写」教训入 death_cases（DEATH-021），处方="盘面变更前后跑 recon 对账+守恒闸拒写即停勿强写"。
