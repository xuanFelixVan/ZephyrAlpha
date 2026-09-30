---
ttl: task_bound
title: "W-M1 双轨 72h 兜底评估卷（F4 车道 · 2026-09-30 实测）"
session: st-nightsweep2-nf-20260930
creation_token: "[CREATION-TOKEN: wm1_evaluation-11_wm1_72h_evaluation]"
---

# W-M1 双轨 72h 兜底评估卷（17 号文 §八 兜底判据）

> 车道=F4（st-nightsweep2-nf-20260930）·总筹=st-nightsweep-chief-20260929
> 评估对象=W-M1 Phase 1 双轨并行窗（起点=2026-09-24 12:3x，旗文件 `.runtime/registry_ledger/dual_track.enabled` 在册）
> 性质=**72h 兜底点（09-27 中午）漏跑补评**，实测时点=2026-09-30 07:1x（窗已 6 天+）。只出材料+翻转判定，判据真源不放松。

## 0. 翻转判定（一句话）

**不翻转**。三判据截至本卷实测无一项具备"全绿"资格（§2），Owner 预批面（本夜 F 组令"F4 已批"）条件不成立，`dual_track.enabled` 摘旗动作**不执行**，双轨观察继续。前置修复（bundle 契约断裂）已本轮治愈并实跑验证（§3）。

## 1. 判据真源与窗坐标

- 判据唯一成文处=`docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` §八：
  24h 点三项全绿→提请 P-3 提前翻转；「72h（09-27 中午）：同判据兜底完全切换」。
- 漂移机械口径=`src/zephyr/governance/registry_ledger/baseline.py` reconcile：`zero_unexplained_drift = content_mismatch==0 and pg_only==0`。
- 窗内自动对账探针样本：`.runtime/registry_ledger/dualtrack_*.json` 共 **613 卷**（2026-09-25 21:30 → 2026-09-30 03:15）。
- 24h 补跑评估卷=`cmd_successor_20260925/WM1_24h_evaluation.md`（LANE-WM1，09-25 21:20，三判据全不绿+bundle 契约断裂定性"翻转前必修"）。

## 2. 三判据实测（72h 兜底口径，本卷取数全只读）

| # | 判据（原句） | 实测（613 卷自动对账+库面快照） | 判定 |
|---|---|---|---|
| ① | 高峰并发期零漂移 | content_mismatch（CAS 真并发冲突）窗内**恒 0**=此半绿；但机械口径另一半 pg_only（PG 有而 YAML 无=未解释）三册长期非零 | **不绿** |
| ② | 对账零异常 | 613 卷自动对账**全绿卷数=0**：REG-MODULE-TRANSLATION-001 613/613 卷非绿（pg_only 持续 2→28）、REG-CAPCAN-001 581/613 非绿（现值 pg_only=33）、REG-ARCH-ISSUE-001 44 卷非绿（现值 pg_only=1）、REG-DOC-001 83 卷、REG-CAND-001 7 卷 | **不绿（决定性）** |
| ③ | 11 读端零改动 | 09-25 21:30 后复测：registry_yaml_parse_gate.py 0 笔；create_guard.py 2 笔（他车道 CREATE-GUARD 面）；其余读端抽查有 1 笔他域提交。读端结构契约零破坏（P0 七册 safe_load+族切分全通，对账探针即依赖该路径） | 不绿（从严口径 X 维持 24h 卷判定） |

**总判：三判据无一全绿 → 不具备"72h 兜底完全切换"的执行条件。**

未解释漂移形态注记：pg_only=Phase 1 insert-only 的结构性产物（YAML 侧删改/身份变体在 PG 留 insert-only 残行），content_mismatch 恒 0 说明真并发零冲突——病灶在**身份口径与吸收规则**，不在并发安全面。治本方向（留卡不在本夜施工）：pg_only 吸收规则 v2（retire 对账/身份变体归并）。

## 3. 前置修复：bundle 契约断裂治愈（WM1_24h_evaluation §3.1 处方执行）

24h 卷定性"投影读端与快照写端 bundle 契约不一致→render 通道物理不可执行，翻转前必修"。本轮 F4 治愈：

1. **写端统一到读端契约**（读端=乙号文设计形态，`pg_source.snapshot_from_bundle`）：`baseline.publish_snapshot` 改发布结构化 bundle（registry_id/header_lines/sections[{root_key,entries=[[k,v]...]}]/trailing_scalars/ledger_revision/snapshot_version/content_sha256；条目=有序对数组，jsonb 数组保序+重复键可表达）；头部/尾部 verbatim 由 `_projection_context_from_disk` 按册 physical_path 从盘上 YAML compose 提取（fail-open 降级空值）；content_sha 仍按 manifest（noop 幂等语义不变）。调用面 `wave0_phase0_gate.py publish` 传 repo_root。
2. **全量重发**：P0 七册 v2 结构化快照发布成功（CAPCAN 12594/TRANSLATION 8730/DOC 300/ARCH-ISSUE 812/ERRCODE 795/CAND 623/RULING 250）。
3. **演练实测**（乙号文 §4 出口判据 3 的"快照 render vs 盘上 YAML"）：render 通道**已可执行**（原 `bundle 结构不符契约: 'sections'` 不再出现）。REG-CAPCAN-001 语义对账：capabilities 族 388↔388 零差；creation_tokens 族 render_only=33（=pg_only 未解释漂移本体）+disk_only=24（YAML 身份变体未吸收）；header 键集相等；字节相等未达（jsonb 键序归一=renderer 自述 cutover 噪音+上列漂移）。
   **结论：通道修复完成；逐字节一致是 Phase 2 cutover 后性质，其前置=pg_only/disk_only 吸收规则治本（§2 注记留卡），不是再修契约。**

## 4. 留卡（按优先级）

1. pg_only/disk_only 吸收规则 v2（retire 对账+身份变体归并）→ 三判据②的治本前置。
2. 判③"零改动"口径 X/Y 裁定（24h 卷已登记案卷瑕疵：LEDGER_wave0 自述与读端名单自相矛盾）。
3. 翻转提请=三判据全绿后按 17 号文 §八走 P-3 面（Owner 门位，届时引用本卷+当期探针数据）。

## 5. 取数命令（复算口）

```bash
python - <<'EOF'  # 613 卷聚合（本卷 §2 表）
import json, glob, collections
files = sorted(glob.glob('.runtime/registry_ledger/dualtrack_*.json'))
drift = collections.Counter(); runs = pass_runs = 0
for f in files:
    regs = json.load(open(f, encoding='utf-8'))
    if not isinstance(regs, list): continue
    runs += 1; ok = True
    for r in regs:
        if isinstance(r, dict) and r.get('zero_unexplained_drift') is False:
            ok = False; drift[r.get('registry_id','?')] += 1
    pass_runs += ok
print(runs, pass_runs, dict(drift))
EOF
# 演练：wave0_phase0_gate.py publish 后 load_latest_snapshot + render 对账（本卷 §3.3）
```
