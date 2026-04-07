---
version: 1.0.0
standard_type: тиЦтЁиТїЄтЇЌ
responsibility:
  - 实施指南、部署文档
applicable_scope: тЁЃТЋ░ТЇ«у«Ауљ?compliance_level: ТГБт╝ЈТаЄтЄє
parent_document: ../README.md
implementation_status: ти▓т«їТѕ?owner: ТќЄТАБу«АуљєтЉ?version: 1.0.0
module_id: METADATA_ENHANCER_GUIDE
created_date: 2026-04-02
last_updated: 2026-04-02
tags: ["тиЦтЁиТїЄтЇЌ", "тЁЃТЋ░ТЇ?, "УЄфтіетї?, "Сй┐ућеТЅІтєї"]
---
---

# тЁЃТЋ░ТЇ«тбът╝║тиЦтЁиСй┐ућеТїЄтЇ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

**ТќЄТАБуЅѕТюг**: 1.0.0
**ТюђтљјТЏ┤Тќ?*: 2026-04-02
**ТќЄТАБТЅђТюЅУђ?*: ТќЄТАБу«АуљєтЉ?
---

## 1. тиЦтЁиТдѓУ┐░

### 1.1 тиЦтЁиу«ђС╗?
тЁЃТЋ░ТЇ«тбът╝║тиЦтЁиућеС║јУЄфтіеТјеТќГтњїУАЦтЁЁТќЄТАБтЁЃТЋ░ТЇ«№╝їуА«С┐ЮТќЄТАБтЁЃТЋ░ТЇ«т«їТЋ┤ТђДтњїУДёУїЃТђДсђ?
### 1.2 СИ╗УдЂтіЪУЃй

- Рю?УЄфтіеТјеТќГтЁЃТЋ░ТЇ?- Рю?ТЅ╣жЄЈТи╗тіатЁЃТЋ░ТЇ?- Рю?жфїУ»ЂтЁЃТЋ░ТЇ«т«їТЋ┤Тђ?- Рю?ућЪТѕљтбът╝║ТіЦтЉі

---

## 2. т┐ФжђЪт╝ђтД?
### 2.1 тЪ║ТюгСй┐уће

**тбът╝║тЁЃТЋ░ТЇ?*:
```bash
python scripts/metadata_enhancer.py
```

**жфїУ»ЂтЁЃТЋ░ТЇ?*:
```bash
python scripts/metadata_enhancer.py --validate
```

---

## 3. тіЪУЃйУ»дУДБ

### 3.1 тЁЃТЋ░ТЇ«ТјеТќ?
**ТјеТќГУДётѕЎ**:
- С╗јТќЄС╗ХУи»тЙёТјеТќГmodule_id
- С╗јТќЄС╗ХтљЇТјеТќГТаЄжбў
- С╗јуЏ«тйЋу╗ЊТъёТјеТќГтѕєу▒?
**уц║СЙІ**:
```
ТќЄС╗ХУи»тЙё: docs/02_FACTOR_LIBRARY/01_FACTORS/MOMENTUM_FACTOR.md
ТјеТќГу╗ЊТъю:
  - module_id: MOMENTUM_FACTOR
  - category: 02_FACTOR_LIBRARY
  - title: тіежЄЈтЏатГљ
```

### 3.2 тЁЃТЋ░ТЇ«жфїУ»?
**т┐ЁжюђтГЌТ«х**:
- owner
- version
- module_id
- created_date
- last_updated

**ТјеУЇљтГЌТ«х**:
- standard_type
- applicable_scope
- compliance_level
- parent_document

---

## 4. жЁЇуй«жђЅжА╣

### 4.1 ТјеТќГУДётѕЎжЁЇуй«

```yaml
inference_rules:
  module_id:
    source: "filename"
    pattern: "([A-Z_]+)\\.md"
  
  category:
    source: "directory"
    mapping:
      "01_FRAMEWORK": "ТАєТъХТќЄТАБ"
      "02_FACTOR_LIBRARY": "тЏатГљт║?
```

---

## 5. ТюђСй│т«ъУи?
### 5.1 Сй┐ућеТеАТЮ┐

**тѕЏт╗║ТќЄТАБТЌХСй┐ућеТеАТЮ?*:
```bash
# Сй┐ућеТќЄТАБТеАТЮ┐
cp docs/09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md new_document.md
```

### 5.2 т«џТюЪжфїУ»Ђ

**Т»ЈТюѕжфїУ»ЂтЁЃТЋ░ТЇ«т«їТЋ┤Тђ?*:
```bash
python scripts/metadata_enhancer.py --validate
```

---

## 6. тЈѓУђЃТќЄТА?
- [тЁЃТЋ░ТЇ«тбът╝║тиЦтЁиТіђТю»УДёУїЃ](05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/METADATA_ENHANCER_SPECIFICATION.md)
- [ТќЄТАБТеАТЮ┐](09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md)

---

**ТќЄТАБуіХТђ?*: ТГБт╝ЈТаЄтЄє
**СИІТгАТЏ┤Тќ░**: 2026-07-02
