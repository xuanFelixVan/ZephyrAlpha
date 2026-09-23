---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 血肉编目标准作业规程（SOP）——资产人读描述区必填与质量标准
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-22
topic: blood_flesh_cataloging_sop
scope: library
depends_on:
  - module_translation_registry
  - library_tag_vocabulary
related_issues:
  - "ulib3 T8（千问苦力班指令 B 前置件，指令真源 docs/_working/ultimate_library/12_ulib3_directive.md）"
related_modules:
  - MOD-LIB-001
---

# 血肉编目 SOP——新资产登记必填血肉（BLOOD-FLESH 制度配套）

## §0 一句话

**骨=资产身份证（asset_id/kind/home，机器填）；血肉=人读描述区（中文名+大白话+标准标签，AI 辅填）。**
没有血肉的资产是"有户口没档案"——检索命中了也读不懂，AI 只能开文件重读，图书馆的检索价值被抽空。本规程规定血肉的必填字段、质量标准与违规处置，配套闸=BLOOD-FLESH（提交时）+TAG-VOCAB（标签枚举）。

## §1 血肉字段定义（真源=08 字段词典 §1 人读描述区）

| 血肉 | 模块级落点（module_translation_registry.yaml） | 资产级落点（lib_assets 人读区） | 质量标准 |
|---|---|---|---|
| title_zh（中文标题） | name_zh | title | 非空；实义名词短语，禁止"测试/工具/模块"类空壳词 |
| plain_zh（大白话） | plain_zh | one_liner/ai_contract | CJK≥8；非通用模板；说清"做什么+给谁用"，禁止黑话堆砌 |
| tags（标准标签） | ——（模块不填） | tags[] | 每词必须是 library_tag_vocabulary.yaml 标准词或其登记别名（TAG-VOCAB 闸） |
| 别名 | —— | ext.aliases | 每别名必须挂唯一标准词，别名孤儿=违规 |

## §2 谁在什么时候填（三道出生点）

1. **新建 .py 模块**：`add_module_translation.py --path <file> --domain <D_*> --name-zh <中文名> --plain-zh <大白话>`。BLOOD-FLESH 闸 A 面查 name_zh，TRANSLATION-COVERAGE 硬闸查 plain_zh（两闸分工：59 号管 plain_zh 硬阻断，133 号管血肉双全观察期）。
2. **翻译册新增条目**（改册不建文件的场景）：BLOOD-FLESH 闸 B 面相对 HEAD 新增条目查 name_zh+plain_zh 双全且非通用模板。存量条目不追溯（bootstrap 豁免）。
3. **馆员登记/回填**（lib_assets 直写， librarian.act()）：登记时 title/one_liner/tags 必填，tags 走 §1 枚举。

## §3 tags 选词纪律（只能选不能造）

- 选词顺序：先查标准词 → 查别名（自动解析到标准词）→ 都没有 = **停**。
- 缺词处置：施工 AI **不得自造新词**——在提交说明登记"建议新词+理由"，由馆员/裁定增补词库（REG-TAGVOCAB-001）后再选。
- 过程性噪音（批号/rejected/layer:L0 等）不属业务标签，禁止填入 tags。

## §4 大白话写作标准（plain_zh）

- **合格样例**："把行情快照按交易日切片入库，供回测和模拟盘按日取数。"
- **不合格样例**："提供数据入库功能。"（空壳模板）/ "基于 TSDB 的向量化切片引擎。"（黑话堆砌）
- 判定基准：非开发的 Owner 一遍读懂"这资产是干嘛的、什么时候会用它"。
- 机械检测与 TRANSLATION-COVERAGE 同真源（is_generic_plain_zh/is_generic_plain_suffix），防糊弄。

## §5 违规处置与升硬路径

- BLOOD-FLESH / TAG-VOCAB 观察期 warn-only：违规 WARN+审计留痕（.runtime/gate_audit/）+放行。
- 升硬条件：误报率回评通过+存量噪音清单清偿后，`BLOOD_FLESH_GATE_MODE` / `TAG_VOCAB_GATE_MODE` 翻 "block"（各一行）。
- 千问苦力班（指令 B）按本规程批量补录存量血肉；补录批提交时本闸只看新增/变更条目，不会因存量欠账卡批。

## §6 净零声明

本 SOP 收编"血肉编目"散见纪律（08 词典 §1/§7、TRANSLATION-COVERAGE 写入工具链），不立平行登记表；血肉数据的家=翻译册（模块级）+lib_assets 人读区（资产级），本规程只管"怎么填、填什么标准"。
