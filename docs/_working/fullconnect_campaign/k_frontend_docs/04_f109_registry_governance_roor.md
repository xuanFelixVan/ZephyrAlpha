---
ttl: task_bound
title: L11 案卷 F109 — 注册表族治理（ROOR 注册表的注册表+master_index 机生+一致性契约）
session: zc-l11-20260927
---

# F109 注册表族治理（K 段 G13，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 全体 REG-* 注册表（ROOR 逐条登记 physical_path/maintenance）；master_index 机生源=`generate_registry_master_index.py`（ROOR:153 maintenance:auto 锚） |
| 下游消费 | 全链发现面：宪法 §0 RULE-REGISTRY"查注册表先读 ROOR 勿背数"；capability_canonical_file_registry、capability_lookup 发现链 |
| 自动化触发 | master_index=生成器产出（auto 维护）；一致性契约+净零审计=季度窗（宪法 §4.2）；无独立守护进程 |
| 真源与注册表 | `docs/registry_of_registries.yaml` 本日双计数：grep "registry_id: REG-"=**77** vs summary.total_registries=**76**（:881）——总册 §五-3 预言的漂移本日现场复现（REG-METAQ-001 PG 快照双计或新增未刷新 summary，裁-1 待裁） |
| 门禁与质量尺 | 无 ROOR 专项 gate（发现面靠纪律+复核命令）；wiring_gap §1.3：15 项 REG 册无环节落位+40 项"环节在册内未点 REG 号"=机检不可达欠账 |
| 当前运行状态 | **黄**：册体绿（77 条在管+master_index 机生）；黄点=summary 漂移 76≠77 未收敛、登记面欠账 40 项 |

## 二、子模块三级枚举

1. **ROOR 本册**：registry_of_registries.yaml（本日 77 REG- 条目；summary:881=76 漂移位）。
2. **master_index**：docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml（physical_path ROOR:151 锚；generate_registry_master_index.py 机生）。
3. **机生器**：scripts/governance/ generate_registry_master_index.py（maintenance:auto 字段锚）。
4. **一致性契约**：宪法 §4 净零+内收判据（w5_1）+文档矛盾=事故（§4.3）——规则面非代码件。
5. **欠账面**：wiring_gap §1.3 B-1..B-15（15 项无环节落位；P0 两项=B-9 迁移册/B-12 状态词表册）。

## 三、接线四态独立复核

- **ROOR→发现链：已接线**（宪法 L0 冷启动第 6 步强制；capability_lookup 链）。
- **master_index 机生：已接线**（maintenance:auto+生成器在仓）。
- **summary↔条目自洽：半接线（漂移在飞）**——76≠77 本日复现；无门禁拦 summary 漂移（机检缺位=同"静态清单禁手工维护"精神的执行盲区）。
- **15+40 登记欠账：未接线**——B-12 GATE-VOCAB"真在拦却无环节"为最痛样本（wiring_gap P0）。

### 骨架勘误
1. 总册 F109 行"ROOR 76 册"→本日实测 grep=77、summary=76：**双口径并存**，收敛前引用一律"grep 77/summary 76"双写，禁单写。
2. 总册 §五-3 的猜测（METAQ 双计/新增未刷新）本日未能定谳——保持待裁（裁-1），不采信任何单边解释。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | summary 76≠77 漂移 | 裁-1 收敛（建议补 summary=77 或 METAQ 双计修正）+机生 summary 字段 | P1 |
| 2 | B-9 迁移册/B-12 状态词表册 P0 落位 | 挂环节（环节层 41 未接线清单同窗） | P0（wiring_gap §1.3 已定级） |
| 3 | 40 项"环节在册未点 REG 号" | 机生对账批补点号（90 普查同窗） | P1 |

## 五、自审闸三态

**挖干（双计数现场复现+master_index 锚+欠账面引用）✅；待裁（裁-1 漂移归因=Owner/总筹，本卷不代裁）；待挖（77 册逐册 maintenance 四态透视=P2，master_index 已机生可查）。**

## 六、复跑命令

```bash
grep -c "registry_id: REG-" docs/registry_of_registries.yaml                    # 77
grep -n "total_registries" docs/registry_of_registries.yaml                     # :881 = 76
grep -n "master_index" docs/registry_of_registries.yaml | head -2               # :151-153 auto
ls docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml
```
