---
ttl: task_bound
title: L11 案卷 F106 — 术语三层翻译体系（术语/域/模块三册+i18n loader+覆盖 gate）
session: zc-l11-20260927
---

# F106 术语三层翻译体系（K 段 G10，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 三册真源：`docs/01_policies_and_standards/_registry/catalogs/{terminology_glossary,functional_domain_registry,module_translation_registry}.yaml`（本日 ls 实存三件）；模块册条目=生成器产出（宪法 §9.5 静态清单禁手工维护） |
| 下游消费 | loader=`scripts/governance/_shared/module_translation_loader.py`（本日 ls 实存；translation_coverage_gate.py:4 头注实证依赖 get_module_translation/is_generic_plain_zh）；生成器族消费（api_server.py、decision_map.py 等 grep module_translation_registry 命中 8+ 文件）；capability_lookup 面间接消费 |
| 自动化触发 | TRANSLATION-COVERAGE 门（gate_registry.yaml:1871，CommitGate priority=59）：staged 新增 .py 无非空非模板 plain_zh 即拦；2026-08-02 观察期结束转 fail-closed；2026-09-23 own-scope 化（外来 staged warn+审计）；对账件=governance/audit/translation_coverage_reconciler.py |
| 真源与注册表 | 模块册 yaml.safe_load 本日实测 **entries=7846**、distinct domain_id=74；术语册 terms=279；域册 domains=94 |
| 门禁与质量尺 | TRANSLATION-COVERAGE（存在性）+可视化模板门互补（gate_registry:511 "存在性 vs 质量"）；loader 只读 YAML（gate 头注 INVARIANTS）；翻译真源不可达 fail-open（环境异常非违规） |
| 当前运行状态 | **绿（库件+门）**：三册+loader+fail-closed 门+own-scope 全实证；黄点=空域条目占比 26.6% 待收编（见勘误） |

## 二、子模块三级枚举（三册 × loader × gate 实扫）

1. **术语册** terminology_glossary.yaml：terms=279 条（本日 yaml 实测）。
2. **域册** functional_domain_registry.yaml：domains=94 条（本日 yaml 实测）。
3. **模块册** module_translation_registry.yaml：entries=7846（本日 yaml 实测；总册 09-25 口径 7686=regex 口径，官方复数命令以 yaml.safe_load 为准——总册 §五-2 自认）。
4. **loader** scripts/governance/_shared/module_translation_loader.py：get_module_translation/is_generic_plain_zh/is_generic_plain_suffix 三函数（gate 头注锚）；只读。
5. **gate** gov_enforcement/commit_gates/translation_coverage_gate.py：[TESTS] tests/governance/commit_gates/test_translation_coverage_gate.py（头注锚）。
6. **对账件** governance/audit/translation_coverage_reconciler.py（grep 实存）。

## 三、接线四态独立复核（四态口径：已接线=生产消费实证｜半接线=库件在链路缺环｜未接线=零生产调用｜停用=裁定保留/撤）

- **三册→loader→gate：已接线**（gate 头注 import 锚+TESTS 锚；priority=59 在册）。
- **三册→生成器输出：已接线**（宪法 §8"生成器输出经 loader 禁硬编码"；api_server/decision_map 等 8+ 文件引用锚）。
- **空域条目收编：半接线**——本日实测 domain_id 空串=**2089/7846（26.6%）**，字面 "UNKNOWN"=0：总册"UNKNOWN 域 2110 条 26.9%"口径已漂移（条目增长+字面实为空串），收编动作未闭环。
- **术语册/域册单点消费：未接线面**——src 下 grep "terminology_glossary" 零命中（loader 只挂模块册路径）；术语/域两层对生成器的实际投影依赖面窄，三册之名与实际消费宽度不对称。

### 骨架勘误
1. 条目计数：总册 7686（09-25 regex）→本日 yaml.safe_load=7846（册在增长，复数一律 yaml 口径）。
2. "UNKNOWN 域 2110/26.9%"实为 **domain_id 空串 2089/26.6%**（字面 UNKNOWN=0）；净零改写时以空串口径入册。
3. 无。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 空域 2089 条（26.6%）待收编 | 域归属批量判建（生成器+人工核），随 M0 普查 29 候选漏项同窗 | P2 |
| 2 | 术语册/域册生产消费面窄 | 与模块册同 loader 面统一投影（随生成器对账批） | P2 |

## 五、自审闸三态

**挖干（三册 yaml 复数+loader/gate 锚+消费方 grep+own-scope/fail-closed 状态实证）✅；待裁（无——本环节无资金/净删门位事项）；待挖（94 域逐域覆盖率透视=P2，随收编批）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "
import yaml;from pathlib import Path;from collections import Counter
d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml').read_text(encoding='utf-8'))
es=d['entries'];dom=Counter(str(e.get('domain_id')) for e in es)
print('entries=',len(es),'empty_domain=',dom.get('',0),'UNKNOWN_literal=',dom.get('UNKNOWN',0))"
ls scripts/governance/_shared/module_translation_loader.py
grep -n "TRANSLATION-COVERAGE" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head -2
```
