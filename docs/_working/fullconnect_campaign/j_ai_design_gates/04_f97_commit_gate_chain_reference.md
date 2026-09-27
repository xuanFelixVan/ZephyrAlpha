---
ttl: task_bound
title: "F97 commit 侧门禁链（23 环节/115 子环节——引用不重挖）复飞扩卷案卷"
session: st-c7-mine-20260927
---

# F97 · commit 侧门禁链（K 段，总册行 `00_全环节总册.md:172`：—｜提交链｜P2｜G1）

> 本卷为**扩卷**（原 stub 1758 字符 < 2000 判据）。扩卷动因：独立普查测得本环节未达挖干标。
> **扩卷首要结论（黄偏红）**：原 stub §四 记"缺口 G1 无（引用完整）"、§五 自审"挖干"。本卷实测**该自审依据不足**——被引真源四件在盘、五个测量基座（`.runtime/audit/*.jsonl`）在产且今日有写，但**卷宗的时间/拦截榜/过滤盲区结论无法从现存基座复算**：`gate_execution_stats.jsonl` 全部 2060 条记录为同一聚合 schema（`timestamp/n_specs/failed/reused/ms/total_ms`），**不含 per-gate 身份字段**，且窗口 2026-09-15→09-27（total_ms 求和 146,834,700）与 C1 卷宗 :15 的"111,852 秒／现役 102 册名／73.3 秒每链"不同尺（§六 E1/E2）。引用型环节的"引用完整"须含"被引结论可复算"，缺此不得盖挖干 ⇒ 本卷判 **未干**。
> **本卷自纠一条测量错误（留档）**：本卷首跑 §六 E1 时在**工作树内**执行 `test -f .runtime/audit/…`，得 5/5 ABSENT，并据此一度判"基座全缺"。该结论**错**：`.runtime/` 不随 git 走，worktree 的 `.runtime` 与主区 `.runtime` 是两个目录；在主区实测五件全部 PRESENT（行数与 mtime 见 §六 E1b）。此处记录为路径域错（同族先例见本仓 `.git`/`/tmp` 路径域教训），并把"基座存在性"从红判降级为"基座粒度不匹配"。
> 同时本卷**确证**两件好事：①"23 环节/115 子环节"口径可机械复算且逐字吻合（§六 M2）；②被引三件均在 HEAD（非仅在主区暂存面）。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | 被引真源三件 + 卷宗一件，全在 HEAD（`git cat-file -e HEAD:` 四通过，§六 K1）：`docs/_working/commit_speedup_campaign/00_skeleton/S1_stage_inventory.md`、`S2_substage_tree.yaml`、`S3_gaps_and_blindspots.md`、`docs/_working/commit_speedup_campaign/30_gate_census/C1_gate_dossier.md`。整个 `commit_speedup_campaign/` 在 HEAD 有 **46 件**（§六 K2）⇒ 与本次战役的 130 卷不同，**被引侧是真落地面**，不是 index 在途件。 |
| 在册态 | 权威文件册点名：`capability_canonical_file_registry.yaml` 含 `commit_speedup_campaign/00_skeleton` 系条目（§六 R1）；战役侧引用者=`docs/_working/fullflow_mining/m3_governance/01_runtime_guards.md`（引用卷头的边界声明）。门名册在册=`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml:10  total_gates: 182`（字段化计数，符合根宪法 §4.3 计数用字段铁律）。 |
| 消费者 | 无代码消费者（引用型环节，载体为文档）。引用它的战役侧下游=本战役 F98（门引擎运行时）与 K 段各卷，原 stub 已记"其现状漂移（114/102/180）记入 F98 案卷"。⇒ 本卷对该让渡**部分否证**：漂移数字应可由本环节自身复算，让渡给 F98 造成"引用环节的尺在别的环节手里"（§四 缺 3）。 |
| 测试 | 0 件（引用型环节无被测代码；`git ls-tree` 侧无对应测试件，§六 T1）。替代判据=可复算性：本卷 §六 M2 提供两行机械复算（stage 数 / substage 递归数）。 |
| 自动化触发 | 无（本环节=卷宗引用位）。真正的自动触发属被引链路的运行时面（F98 门引擎 / commit 钩子链），本环节不持进程 ⇒ dir6 wide=false/narrow=false 与定性一致。 |
| 真源方向 | **规则数据=YAML/MD 卷宗**（S1/S2/S3/C1 四件），机生名册 `gate_registry.yaml` 为门禁身份真源；两者关系=卷宗描述名册、名册机生自代码（`generate_gate_registry.py` 侧，参 F98 卷）。真源方向**未倒挂**。 |
| 门禁与质量尺 | 本环节即"描述门禁链"的环节，其自身质量尺=口径一致性。实测三处不一致（§三.3）：S2 meta `stage_count: 23`（=声明）｜C1 卷宗 :15 记"现役 102 册名"｜`gate_registry.yaml:10  total_gates: 182`。102 vs 182 的差是"现役名册"与"总门数"两个不同口径，**卷宗未把口径写在同一段**，读者极易误读为漂移。 |
| 当前运行状态 | **黄**：被引四件在 HEAD 且互引自洽；基座五件在主区在产（今日有写）；但基座粒度与被引结论不匹配 ⇒ 卷宗的"门耗时/拦截榜/42-44% 过滤盲区"今日**不可复算**。 |

## 二、子模块三级枚举（引用面，仅列与本战役交叉的锚）

1. **骨架三件**（真源=`commit_speedup_campaign/00_skeleton/`）
   - S1 阶段清单（23 环节文字面）
   - S2 子环节树：**结构实测** = `meta`（键 `ttl/date/stage_count/source_table/measurement_docks`）+ `stages` 为 **dict**（键 `ST-01`…`ST-23`），非 list；子环节递归计数=**115**（§六 M2）。`meta.date: 2026-09-24`、`meta.ttl: task_bound`、`meta.source_table: s1_stage_inventory.md`
   - 三级=measurement_docks 五件（meta 声明的复算基座）：`.runtime/audit/gate_execution_stats.jsonl`、`preflight_events.jsonl`、`commit_block_events.jsonl`、`worktree_drift_watchdog.jsonl`、`write_audit.jsonl` ⇒ 主区实测**五件全在且今日有写**（§六 E1b 给行数与 mtime），但 `gate_execution_stats.jsonl` 的 schema 为聚合级、**无 per-gate 身份维度**（§六 E2 实算）⇒ 存在但不可用于复算卷宗的门级结论
   - S3 缺口盲区（卷宗侧已知红账）
2. **C1 门禁卷宗**（`30_gate_census/C1_gate_dossier.md`）
   - 二级=CPU 总账：:15 "全部门禁 CPU 111,852 秒＝1,864 分；其中现役 102 册名"
   - 三级=有效拦截榜 / 密钥面"不建议删"清单 / `§3 ms≥1.0 过滤盲区 42-44%`（原 stub 已列，本卷补其**不可复算**定性：过滤盲区依赖 `gate_execution_stats.jsonl`，该件不存在 ⇒ 42-44% 为**历史快照值**，非当前可测值）
3. **交叉欠账登记**：`commit_speedup_campaign/90_verification/`（HEAD 内该战役另有 46 件，含 `decisions_log.md`、`t13_rename_report.md` 等）＝底数出处；本卷不展开（重挖违反总册 K 段边界与根宪法 §4.2 同真源必并）。
4. **战役内对偶件**：F98 门引擎运行时（执法面）／F99 漂移检测（`worktree_drift_watchdog`  dock 的实际产生者）／F100 红蓝对抗——三者共同构成本环节"被引数"的消费端。

## 三、接线四态独立复核

引用型环节的四态口径替换为：**被引件在盘 / 被引结论可复算 / 口径自洽 / 无越界重挖**。

1. **在盘=通**：四件 `git cat-file -e HEAD:` 全通过，且战役目录整体 46 件已入库 ⇒ 不是"引用了一份未落地的工作区草稿"（对照：本次战役自己的 130 卷在本卷测量时点**只存在于主区 index、不在 HEAD**——HEAD 内 5 件 vs 主区 index 内 135 件，§六 X1 一测即现；本道 bag1 随后落地 10 卷会使该计数上移，故**读法比数值重要**）。"引用未落地件"在本仓是真实风险形态，必须每轮重测。
2. **可复算=红（本卷改判主因）**：S2 的 stage/substage 数可复算（23/115 ✓），但 C1 卷宗的一切**时间/拦截/盲区类结论今日不可复算**——基座五件虽在（§六 E1b），`gate_execution_stats.jsonl` 却只有聚合 schema（2060 条同构记录，字段 `timestamp/n_specs/failed/reused/ms/total_ms`，**无 gate 身份列**，§六 E2），窗口亦与卷宗不同（09-15→09-27 vs 卷宗的"现役 102 册名 97,476 秒"）。⇒ 按"引用完整 = 被引结论可复算"的判据，本环节只能是**半接线（描述面通、测量面粒度不匹配）**。stub 把"三件 ls 命中"当成"引用完整"，属把**存在性判据**当**内容判据**的同一失效模式；本卷首跑另加一条同源错误的自纠（把 worktree 的 `.runtime` 当主区的 `.runtime`，见卷头留档段）——两次错同一族：**没验数据源的作用域就下结论**。
3. **口径自洽=黄**：23/115 与声明吻合（好）；但 `102`（现役册名）与 `total_gates: 182` 并存于不同件且未在同一段解释口径（§一 门禁与质量尺行）。⇒ 数字无错、口径易误读，登记为可读性缺口而非事实缺口（§四 缺 2），刻意不上升为"漂移事故"。
4. **无越界重挖=通**：本卷未重做 S1/S2/S3 内容挖矿（总册 K 段标题 :168 明示"commit 侧 23 环节引用 commit_speedup 战役不重挖"），只做引用完整性复核与可复算性证伪——这正是引用型环节应挖的那部分。
5. **让渡判据的反向检验**：stub 把底数漂移让渡给 F98。本卷反向问"谁有资格让渡"——引用环节把自己的核心尺让给别人，导致**本环节自审时手上无尺**，于是"缺口 G1 无"必然被盖出来（结构性自证绿）。⇒ 登记为机制教训（§四 缺 3）。

## 骨架勘误

对骨架无否证：总册 :172 判 `built`、P2、G1，与"引用件在盘、战役已落地"一致。补两处细化：①总册 F97 实现件列"提交链战役 00_skeleton"，未列 `30_gate_census/C1_gate_dossier.md`（本卷实测被引面为**四件**而非三件）；②"115 子环节"的可复算口径是 `stages` 为 dict + 递归计数，若下一个人按 list 遍历会得到 0（本卷首跑即踩此坑，已把正确写法固化进 §六 M2）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | `gate_execution_stats.jsonl` 只有聚合 schema（无 per-gate 身份列），故 C1 卷宗的门级结论（现役 102 册名 97,476 秒／73.3 秒每链／ms≥1.0 过滤盲区 42-44%）今日**无从复算** | 施工：dock 生产者补 gate 身份维度（或另立门级明细流），补齐后回填卷宗并重算；在补齐前，引用面须逐处标"历史快照值、当日不可复算" | P1 |
| 2 | `102 现役册名` 与 `gate_registry.yaml:10 total_gates: 182` 的口径差未在卷宗同段解释 | 施工：C1 卷宗补一行口径注（现役/总数分列）；机械改注，不动数字 | P2 |
| 3 | 引用环节把核心尺让渡给 F98，造成本环节自证无尺（结构性假绿机制） | 施工：本环节自留"可复算性"这一把尺（即 §六 M2/E1 两条），其余让渡维持不变 | P1 |
| 4 | 测试面为 0 且无替代机检（§六 T1） | 挂起：引用型卷宗是否强制配可复算断言，属判据立法面；本卷不自立尺 | P2 |
| 5 | dock 在 `.runtime/audit/`（由清理策略回收、且**不随 git 走**——worktree 与主区各有一份，本卷自纠即源于此），卷宗在 `docs/_working/`（由 completes_when 归档）⇒ 两套生命周期不同步，且 dock 无版本锚：换机/开 worktree 即"基座消失"错觉 | 施工：卷宗侧为每条 dock 结论标注"采集窗口 + 主机/工作树作用域"；挂起：跨区生命周期同步属治理侧（根宪法 §9.4 延伸面） | P2 |
| 6 | dock 路径的作用域陷阱（`.runtime` 非 git 管辖，worktree≠主区）已在 §六 E1b/E1c 固化为必带 `cd` 的读法 | 施工：本卷已在 §六 写死；建议同类卷宗统一采用"先 cd 主区再测"模板 | P2 |

## 五、自审闸三态

**未干。** 已做到且可复算：四件在 HEAD 的存在性、战役 46 件落地面、23/115 两口径的机械复算（含 `stages` 为 dict 的正确遍历法）、五个 dock 的**存在性正证**（主区实测 5/5 PRESENT，行数 2060/5452/2326/12057/2813、mtime 均为今日）与**粒度否证**（聚合 schema、无 per-gate 列、窗口 09-15→09-27）、102 vs 182 的口径定位、stub"引用完整"的判据错型（存在性当内容），以及本卷自身一次路径域测量错的公开自纠（卷头留档段 + §六 E1c）。
未干的原因：①**未读 S1/S2/S3/C1 四件的实质内容**（本卷刻意遵守 K 段"不重挖"边界，但"不重挖"与"已挖干引用面"不等价——引用面还应含"哪条战役结论依赖哪个 dock 的哪个字段"的正向映射表，本卷只做了 dock 粒度不匹配这一条否证）；②缺 1 的 dock 生产者未定位（需读 F98/F99 面），因此"能否补出 per-gate 维度"只是需求陈述、不是可行方案；③缺 5 属跨区生命周期立法面。
⇒ 本卷交"半接线黄判 + 未干"，并**明确撤销原 stub 的"挖干"自审章**（撤销理由=§三.2 的可复算性判据，非口径之争）。同时本卷不因首跑的假红而反向盖章：dock 存在≠引用完整，两者都要测。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# K1 被引四件在 HEAD
for p in docs/_working/commit_speedup_campaign/00_skeleton/S1_stage_inventory.md \
         docs/_working/commit_speedup_campaign/00_skeleton/S2_substage_tree.yaml \
         docs/_working/commit_speedup_campaign/00_skeleton/S3_gaps_and_blindspots.md \
         docs/_working/commit_speedup_campaign/30_gate_census/C1_gate_dossier.md; do git cat-file -e HEAD:$p && echo "OK $p"; done
# K2 战役落地面件数（期望 46）
git ls-tree -r --name-only HEAD docs/_working/commit_speedup_campaign/ | wc -l
# M2 口径机械复算（期望 stages=23 / sub_total=115，与册面声明逐字吻合）
python -c "
import yaml,io
d=yaml.safe_load(io.open('docs/_working/commit_speedup_campaign/00_skeleton/S2_substage_tree.yaml',encoding='utf-8'))
st=d['stages']
def cnt(o):
    if isinstance(o,dict):
        return sum((len(v) if k in ('substages','sub_stages','nodes','children') and isinstance(v,(list,dict)) else 0)+cnt(v) for k,v in o.items())
    if isinstance(o,list): return sum(cnt(x) for x in o)
    return 0
print('type',type(st).__name__,'stages',len(st),'sub_total',cnt(st))
print('meta',d['meta'])"
# E1b 测量基座存在性——必须 cd 主区（`.runtime` 不随 git 走；期望 5/5 PRESENT）
for d in gate_execution_stats preflight_events commit_block_events worktree_drift_watchdog write_audit; do printf "%-26s lines=%-7s mtime=%s\n" "$d" "$(wc -l < .runtime/audit/$d.jsonl 2>/dev/null)" "$(date -r .runtime/audit/$d.jsonl +%F_%H:%M 2>/dev/null)"; done
# E1c 作用域陷阱复现（本卷假红来源：在任一 worktree 里跑同一命令会得到 5/5 ABSENT）
#   for d in gate_execution_stats preflight_events commit_block_events worktree_drift_watchdog write_audit; do test -f .runtime/audit/$d.jsonl && echo "PRESENT $d" || echo "ABSENT $d"; done
# E2 粒度否证（本卷真红点）：期望 distinct_gate_fields=0、单一 schema、窗口跨 09-15→09-27
python -c "
import json,io,collections
L=io.open('.runtime/audit/gate_execution_stats.jsonl',encoding='utf-8',errors='replace').read().splitlines()
r=[json.loads(x) for x in L if x.strip()]
print('n',len(r))
print('schemas',collections.Counter(tuple(sorted(e)) for e in r).most_common(2))
ts=[e['timestamp'] for e in r if e.get('timestamp')]
print('window',min(ts)[:10],'->',max(ts)[:10])
print('per_gate_identity_fields',sum(1 for e in r for k in e if 'gate' in k or 'name' in k))"
# X1 对照：本战役 130 卷不在 HEAD（引用面与在途面的区别，一测即现）
git ls-tree -r --name-only HEAD docs/_working/fullconnect_campaign/ | wc -l
git ls-files docs/_working/fullconnect_campaign/ | wc -l
# R1 权威册点名 + 门数口径两处
git grep -ln "commit_speedup_campaign/00_skeleton" HEAD
grep -n "^total_gates:" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
sed -n '13,17p' docs/_working/commit_speedup_campaign/30_gate_census/C1_gate_dossier.md
# T1 测试面（期望 0）
git ls-tree -r --name-only HEAD | grep -iE "test.*(substage|gate_census|commit_speedup)" | wc -l
```
