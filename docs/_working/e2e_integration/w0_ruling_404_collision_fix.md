---
ttl: task_bound
title: 取证·裁定#404 撞号修数（Owner 2026-09-23 夜裁定 R1）
created: 2026-09-23
sid: st-e2e-20260924
lane: e2e_integration
---

# W0 裁定#404 撞号修数（本班首件）

## 一、事实（全部实测，非推演）

`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 在 HEAD 面
`979091ad08` **同时存在两条 `ruling_id: 裁定#404` 的异体条目**（非逐字重复）：

| 行号 | 条目 | 登记车道 | 外部引用面 |
|---|---|---|---|
| 5521 | 批次排序代裁=IBT 整改批C→F 按方案时间线 | st-ibt-remedy-cf-20260923 | **零**（HEAD 面除本册自身外无任何文件引用） |
| 5567 | TC-06 四卡代裁定版（Max 代裁 Owner 全批） | st-oddjobs-20260923 件7 | **6 处**：max_remediation_plan §R2/§R3、experiments_ledger 修正案#2（2 行）、known_data_gaps `etf_minute_tz_split_pre_202607` 结案行、oddjobs_shift_ledger 件7、08_gate_safety_recheck REFERENCE-INTEGRITY 样本行 |

**后果链**：落地侧注册表三向合并判身份键不唯一 → 凡携带裁定册的队列批结构性必死。
实证死信=`.runtime/commit_queue/dead/q-20260923-st-ibt-remedy-cf-20260923-0023.json`，
`dead_reason` 原文："landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）:
ruling_registry.yaml: ours 同侧身份键重复: ruling_id=裁定#404——身份不唯一，死信回人工"。
同件第一道死信 `-0013` 的真死因（TRANSLATION-COVERAGE 缺 plain_zh）已由原道拆册直连批次自行解除
（本班实测两条翻译条目 + 四条 capability token 均已在 HEAD）。

## 二、取号（禁默认顺取，实测所得）

扫描口径=HEAD 册 + 工作区册 + **全队列袋四态**（pending/processing/dead/done 内所有携带
ruling_registry.yaml blob 的快照）的 `裁定#(\d+)` 并集：

- HEAD 册实测 max=**406**（去重后 213 个号位，含带字母后缀子裁定不计入主号 max）
- 工作区册 vs HEAD 册：无新增号
- 全队列袋：无任何袋携带 ≥407 号
⇒ 新号取 **407**（迁号目标）与 **408**（tombstone 位）。

## 三、处置（Owner 2026-09-23 夜裁定，本班执行）

1. ②（TC-06 四卡）系引用链主体，**原地不动**，保留 #404。
2. ①（IBT 批次排序）零外部引用，**让位迁 #407**，条目 summary 追加让位留痕两行。
3. 新立 **#408 `status: void` tombstone**（样式先例=裁定#265"编号让位空号保留"）记录撞号双方、
   取号口径、引用链清单与实证死信号，堵住"改号后有人以为 #404 空了再占一次"的复用缺口。
4. 册顶 `last_updated` 同步 2026-09-23。
5. 写法：热文件走 `safe_write_text` CAS（宪法 §13），禁裸 Edit；外科脚本
   `.runtime/tmp/e2e_20260924/fix_ruling_404.py`，四道前置拒绝（双挂前提不成立/
   待迁锚点不唯一/目标号已被占/改后仍有重复），任一不满足即零写入。

## 四、改后自检（实测输出）

```
entries= 226 unique= 226
dupes: none
404 owner: ['TC-06 四卡代裁定版（Max 代裁 Owner 全批，随批登记）']
407 owner: ['批次排序代裁=IBT 整改批C→F 按方案时间线（st-ibt-remedy-c']
408 status: ['void']
```

外科脚本自身输出：`WRITTEN cas_ok=True base=d39cbb1149ef`（base 与 HEAD 册逐位相符）
`条目数 225 -> 226；#404 计数 1；新增 裁定#408`；`dupes: none`。

## 五、复核命令（任何人可复跑）

```bash
# 撞号双挂取证（改前基线）
git show 979091ad08:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml \
  | grep -n '裁定#404'
# 唯一性复测（改后）
python -c "import yaml,collections;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml',encoding='utf-8'));i=[x.get('ruling_id') for x in d['entries']];print(len(i),len(set(i)),[k for k,v in collections.Counter(i).items() if v>1])"
# 取号面复测（HEAD+全队列袋并集 max）
python -c "import re,subprocess,glob,json;ids=set(re.findall(r'裁定#(\d+)',subprocess.run(['git','show','HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml'],capture_output=True,text=True).stdout));print(max(map(int,ids)))"
# 死信原文
python -c "import json;print(json.load(open('.runtime/commit_queue/dead/q-20260923-st-ibt-remedy-cf-20260923-0023.json',encoding='utf-8'))['dead_reason'])"
```

## 六、本件未做（划清边界）

- 未动 TC-06 条目一字；未动任何引用 #404 的 6 处他班文档（改号方向已选零引用侧，无引用链需回写）。
- 未做数据回补、未点火 GPU、未重启调度器（各归其位，见本班总台账）。
